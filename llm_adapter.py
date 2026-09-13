"""
Smart Civic Connect — Open-Source Civic LLM Intelligence Layer
Module: llm_adapter.py
Version: 44.0.0

Provides modular, pluggable abstraction for open-source LLM integration:
- OpenSourceLLMProvider (Ollama, vLLM, LocalAI, OpenAI-compatible open-source servers)
- DeterministicFallbackProvider (Rule-based zero-GPU fallback supporting EN/TE/HI)
- Strict Schema Validation & Canonical Civic Taxonomy Mapping
- PII Sanitization and Advisory Guardrails ("AI recommends. Government decides.")
"""

import os
import re
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple

# ------------------------------------------------------------------------------
# CANONICAL CIVIC TAXONOMY (SMART CIVIC CONNECT AUTHORITATIVE ENUMS)
# ------------------------------------------------------------------------------
VALID_DEPARTMENTS = {
    'sanitation': 'Sanitation & Waste Management',
    'roads': 'Infrastructure / Roads',
    'electricity': 'Smart Electricity Department',
    'water_supply': 'Water Supply',
    'food_safety': 'Food Safety Department'
}

VALID_CATEGORIES = {
    'garbage_overflow': ('sanitation', 'Garbage Overflow', '🗑️'),
    'drain_blockage': ('sanitation', 'Drain Blockage', '🌊'),
    'pothole': ('roads', 'Pothole', '🕳️'),
    'road_damage': ('roads', 'Road Damage', '🚧'),
    'broken_footpath': ('roads', 'Broken Footpath', '🚶'),
    'sparking_wire': ('electricity', 'Sparking Wire', '⚡'),
    'power_outage': ('electricity', 'Power Outage', '🔌'),
    'water_leakage': ('water_supply', 'Water Leakage', '🚰'),
    'food_hygiene': ('food_safety', 'Food Hygiene Violation', '🍱')
}

VALID_URGENCIES = {'low', 'medium', 'high', 'critical'}
VALID_LANGUAGES = {'en', 'te', 'hi', 'other'}

# Taxonomy Synonyms Mapping (Maps arbitrary LLM generated tokens to canonical enums)
DEPARTMENT_SYNONYMS = {
    'sanitation': 'sanitation',
    'waste': 'sanitation',
    'solid_waste': 'sanitation',
    'cleanliness': 'sanitation',
    'drainage': 'sanitation',
    'roads': 'roads',
    'road': 'roads',
    'infrastructure': 'roads',
    'pwd': 'roads',
    'transport': 'roads',
    'electricity': 'electricity',
    'electrical': 'electricity',
    'power': 'electricity',
    'energy': 'electricity',
    'water': 'water_supply',
    'water_supply': 'water_supply',
    'water_works': 'water_supply',
    'food': 'food_safety',
    'food_safety': 'food_safety',
    'fssai': 'food_safety',
    'health': 'food_safety'
}

CATEGORY_SYNONYMS = {
    'garbage': 'garbage_overflow',
    'garbage_overflow': 'garbage_overflow',
    'trash': 'garbage_overflow',
    'waste_dump': 'garbage_overflow',
    'litter': 'garbage_overflow',
    'bin_overflow': 'garbage_overflow',
    'drain': 'drain_blockage',
    'drain_blockage': 'drain_blockage',
    'gutter': 'drain_blockage',
    'clogged_drain': 'drain_blockage',
    'sewage': 'drain_blockage',
    'waterlogging': 'drain_blockage',
    'pothole': 'pothole',
    'potholes': 'pothole',
    'road_crater': 'pothole',
    'road_damage': 'road_damage',
    'broken_road': 'road_damage',
    'asphalt_damage': 'road_damage',
    'footpath': 'broken_footpath',
    'broken_footpath': 'broken_footpath',
    'pavement': 'broken_footpath',
    'sparking_wire': 'sparking_wire',
    'sparking': 'sparking_wire',
    'hanging_wire': 'sparking_wire',
    'electric_hazard': 'sparking_wire',
    'short_circuit': 'sparking_wire',
    'power_outage': 'power_outage',
    'blackout': 'power_outage',
    'no_power': 'power_outage',
    'power_cut': 'power_outage',
    'water_leak': 'water_leakage',
    'water_leakage': 'water_leakage',
    'burst_pipe': 'water_leakage',
    'pipe_leak': 'water_leakage',
    'food_hygiene': 'food_hygiene',
    'unhygienic_food': 'food_hygiene',
    'stale_food': 'food_hygiene',
    'food_safety_violation': 'food_hygiene',
    'spoilage': 'food_hygiene'
}

# Urgency Synonyms Mapping (Maps arbitrary LLM generated tokens to canonical enums)
URGENCY_SYNONYMS = {
    'low': 'low',
    'minor': 'low',
    'trivial': 'low',
    'slight': 'low',
    'minimal': 'low',
    'medium': 'medium',
    'moderate': 'medium',
    'normal': 'medium',
    'standard': 'medium',
    'regular': 'medium',
    'average': 'medium',
    'high': 'high',
    'urgent': 'high',
    'severe': 'high',
    'elevated': 'high',
    'important': 'high',
    'high_priority': 'high',
    'critical': 'critical',
    'emergency': 'critical',
    'fatal': 'critical',
    'immediate': 'critical',
    'danger': 'critical',
    'dangerous': 'critical',
    'life-threatening': 'critical',
    'life_threatening': 'critical'
}

# ------------------------------------------------------------------------------
# SECURITY & PII SANITIZATION
# ------------------------------------------------------------------------------
def sanitize_pii(text: str) -> str:
    """Sanitizes sensitive citizen identifiers before audit logging."""
    if not text:
        return ''
    # Mask Indian phone numbers: +91 xxxxx xxxxx or 10 digits
    sanitized = re.sub(r'(\+?91[-.\s]?)?[6-9]\d{4}[\s.-]?\d{5}\b|(\+?91[-.\s]?)?[6-9]\d{9}\b', '[REDACTED_PHONE]', text)
    # Mask email addresses
    sanitized = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', sanitized)
    # Mask 12-digit Aadhaar-like numbers
    sanitized = re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b', '[REDACTED_UID]', sanitized)
    return sanitized

# ------------------------------------------------------------------------------
# BASE INTERFACE
# ------------------------------------------------------------------------------
class LLMProviderInterface:
    """Abstract interface for Civic LLM Intelligence providers."""

    def understand_civic_complaint(self, text: str, location_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Interprets natural-language complaint into validated structured JSON.
        Returns a dictionary containing 'llm_advisory' metadata.
        """
        raise NotImplementedError

    def health_check(self) -> Tuple[bool, str]:
        """Returns (is_healthy, status_message)."""
        raise NotImplementedError


# ------------------------------------------------------------------------------
# DETERMINISTIC LOCAL FALLBACK PROVIDER (ZERO GPU / OFFLINE)
# ------------------------------------------------------------------------------
class DeterministicFallbackProvider(LLMProviderInterface):
    """
    High-precision deterministic rule-based extractor supporting English,
    Telugu (తెలుగు), and Hindi (हिन्दी).
    Ensures zero failure rate when open-source LLM runtime is offline or unreachable.
    """

    def health_check(self) -> Tuple[bool, str]:
        return True, "Deterministic Fallback Engine Active (Rule-Based)"

    def understand_civic_complaint(self, text: str, location_hint: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        raw_text = (text or '').strip()
        q_lower = raw_text.lower()

        # 1. Detect Language
        lang = 'en'
        # Telugu script unicode range: 0C00-0C7F
        if re.search(r'[\u0C00-\u0C7F]', raw_text):
            lang = 'te'
        # Devanagari (Hindi) script unicode range: 0900-097F
        elif re.search(r'[\u0900-\u097F]', raw_text):
            lang = 'hi'

        # 2. Extract Landmark & Location Context
        landmark = (location_hint or '').strip()
        loc_patterns = [
            r'near\s+(?:the\s+)?([a-zA-Z0-9\s]{3,35}?)(?:\s+for|\s+since|\s+causing|\.|\,|$)',
            r'at\s+(?:the\s+)?([a-zA-Z0-9\s]{3,35}?)(?:\s+for|\s+since|\s+causing|\.|\,|$)',
            r'opposite\s+(?:to\s+)?([a-zA-Z0-9\s]{3,35}?)(?:\s+for|\s+since|\.|\,|$)',
            r'దగ్గర\s*([a-zA-Z0-9\u0C00-\u0C7F\s]{3,30})',
            r'([a-zA-Z0-9\u0C00-\u0C7F\s]{3,30})\s*దగ్గర',
            r'के\s*पास\s*([a-zA-Z0-9\u0900-\u097F\s]{3,30})',
            r'([a-zA-Z0-9\u0900-\u097F\s]{3,30})\s*के\s*पास'
        ]
        if not landmark:
            for pat in loc_patterns:
                m = re.search(pat, raw_text, re.IGNORECASE)
                if m:
                    candidate = m.group(1).strip()
                    if len(candidate) > 2 and candidate.lower() not in ['the', 'this', 'that']:
                        landmark = candidate[:60]
                        break

        if not landmark:
            if any(w in q_lower or w in raw_text for w in ['college', 'కాలేజ్', 'कॉलेज', 'school', 'స్కూల్']):
                landmark = 'College / School Area'
            elif any(w in q_lower or w in raw_text for w in ['market', 'మార్కెట్', 'मार्केट', 'bazaar']):
                landmark = 'Market Zone'
            elif any(w in q_lower or w in raw_text for w in ['hospital', 'ఆసుపత్రి', 'अस्पताल']):
                landmark = 'Hospital Area'
            else:
                landmark = 'Main Road / Ward Vicinity'

        # 3. Extract Duration
        duration = 'Unknown duration'
        if any(w in q_lower for w in ['3 days', 'three days', 'మూడు రోజులు', 'तीन दिन', '3 రోజులు', '3 दिन']):
            duration = '3 days'
        elif any(w in q_lower for w in ['2 days', 'two days', 'రెండు రోజులు', 'दो दिन', '2 రోజులు']):
            duration = '2 days'
        elif any(w in q_lower for w in ['week', 'వారం', 'हफ्ते', 'हफ़्ते']):
            duration = '1 week'
        elif any(w in q_lower for w in ['today', 'ఈరోజు', 'आज', 'morning', 'ఉదయం', 'सुबह']):
            duration = 'Since morning / Today'

        # 4. Extract Impact
        impact = 'General public inconvenience'
        if any(w in q_lower or w in raw_text for w in ['smell', 'odor', 'stench', 'దుర్వాసన', 'बदबू', 'foul']):
            impact = 'Severe foul smell and public health hazard'
        elif any(w in q_lower or w in raw_text for w in ['accident', 'accidents', 'ప్రమాదం', 'हादसा', 'fall', 'injury']):
            impact = 'Imminent risk of vehicular accidents or pedestrian injury'
        elif any(w in q_lower or w in raw_text for w in ['shock', 'spark', 'షాక్', 'करंट']):
            impact = 'Critical electrocution and public safety hazard'
        elif any(w in q_lower or w in raw_text for w in ['flood', 'waterlogging', 'ముంపు', 'जलभराव']):
            impact = 'Road impassability and stormwater conduit stagnation'

        # 5. Multilingual Keyword Mapping for Department & Category
        # Electricity
        if any(w in q_lower or w in raw_text for w in [
            'spark', 'wire', 'transformer', 'shock', 'electric', 'current', 'cable', 'pole', 'power',
            'కరెంట్', 'వైర్', 'ట్రాన్స్ఫార్మర్', 'షాక్', 'స్పార్క్', 'విద్యుత్',
            'बिजली', 'तार', 'ट्रांसफार्मर', 'करंट', 'शॉर्ट सर्किट'
        ]):
            dept = 'electricity'
            if any(w in q_lower or w in raw_text for w in ['outage', 'blackout', 'no power', 'power cut', 'కరెంట్ లేదు', 'बिजली गुल']):
                cat = 'power_outage'
                subcat = 'unscheduled_feeder_trip'
                urgency = 'high'
                action = 'Deploy Lineman Squad for substation breaker check and restoration'
                summary = f"Power outage reported in {landmark} ({duration})"
            else:
                cat = 'sparking_wire'
                subcat = 'loose_conductor_spark'
                urgency = 'critical'
                action = 'Immediate feeder shutdown and emergency Lineman repair squad dispatch'
                summary = f"Dangerous sparking wire / electrical hazard at {landmark}"

        # Sanitation / Waste
        elif any(w in q_lower or w in raw_text for w in [
            'garbage', 'waste', 'trash', 'dump', 'litter', 'debris', 'rubbish', 'dustbin', 'overflow',
            'చెత్త', 'చెత్తకుండీ', 'వ్యర్థాలు', 'కాలువ',
            'कचरा', 'कूड़ा', 'डस्टबिन', 'गंदगी', 'नाली'
        ]):
            dept = 'sanitation'
            if any(w in q_lower or w in raw_text for w in ['drain', 'sewage', 'clog', 'gutter', 'కాలువ', 'नाली']):
                cat = 'drain_blockage'
                subcat = 'stormwater_clog'
                urgency = 'high' if duration in ['3 days', '1 week'] else 'medium'
                action = 'Dispatch Suction Machine Squad to unblock municipal stormwater conduit'
                summary = f"Drainage blockage causing stagnant overflow near {landmark}"
            else:
                cat = 'garbage_overflow'
                subcat = 'bin_overflow'
                urgency = 'high' if duration in ['3 days', '1 week'] or 'smell' in impact.lower() else 'medium'
                action = 'Deploy municipal waste collection truck and sanitize area with bleaching powder'
                summary = f"Garbage accumulation and overflow near {landmark} ({duration})"

        # Roads
        elif any(w in q_lower or w in raw_text for w in [
            'pothole', 'road', 'crater', 'asphalt', 'tar', 'footpath', 'pavement',
            'గుంత', 'గుంతలు', 'రోడ్డు', 'రహదారి', 'ఫుట్‌పాత్',
            'गड्ढा', 'गड्ढे', 'सड़क', 'फुटपाथ'
        ]):
            dept = 'roads'
            if any(w in q_lower or w in raw_text for w in ['footpath', 'pavement', 'ఫుట్‌పాత్', 'फुटपाथ']):
                cat = 'broken_footpath'
                subcat = 'curb_damage'
                urgency = 'medium'
                action = 'Deploy PWD Masonry Unit to realign and repave damaged footpath slabs'
                summary = f"Damaged pedestrian footpath near {landmark}"
            elif any(w in q_lower or w in raw_text for w in ['pothole', 'crater', 'గుంత', 'गड्ढा']):
                cat = 'pothole'
                subcat = 'deep_asphalt_crater'
                urgency = 'high' if 'accident' in impact.lower() else 'medium'
                action = 'Deploy Road Repair Squad for rapid cold-mix bitumen patching'
                summary = f"Dangerous pothole impacting transit near {landmark}"
            else:
                cat = 'road_damage'
                subcat = 'surface_deterioration'
                urgency = 'medium'
                action = 'Inspect road sub-base and schedule asphalt resurfacing'
                summary = f"Road surface deterioration near {landmark}"

        # Water Supply
        elif any(w in q_lower or w in raw_text for w in [
            'water leak', 'leakage', 'pipe', 'burst', 'drinking water',
            'నీటి లీకేజీ', 'పైప్ లీక్', 'తాగునీరు',
            'पानी का पाइप', 'पानी की लीकेज', 'पाइप फटा'
        ]):
            dept = 'water_supply'
            cat = 'water_leakage'
            subcat = 'main_pipeline_rupture'
            urgency = 'high'
            action = 'Deploy Water Utility Squad for isolation valve shutdown and pipe collar welding'
            summary = f"Drinking water pipeline leakage wasting potable water near {landmark}"

        # Food Safety
        elif any(w in q_lower or w in raw_text for w in [
            'food', 'hotel', 'restaurant', 'dhaba', 'stall', 'stale', 'rotten', 'hygiene', 'fssai',
            'ఆహారం', 'హోటల్', 'రెస్టారెంట్', 'బాగోలేదు', 'వాసన',
            'खाना', 'होटल', 'सड़ा', 'बासी', 'दुकान'
        ]):
            dept = 'food_safety'
            cat = 'food_hygiene'
            subcat = 'commercial_spoilage'
            urgency = 'high'
            action = 'Dispatch Food Safety Officer for statutory inspection and hygiene sampling'
            summary = f"Food hygiene and spoilage concern reported at {landmark}"

        else:
            # Safe civic default
            dept = 'sanitation'
            cat = 'garbage_overflow'
            subcat = 'general_civic_complaint'
            urgency = 'medium'
            action = 'Assign Ward Sanitary Inspector for initial site inspection'
            summary = f"Civic grievance reported in {landmark}: {raw_text[:60]}"

        latency_ms = round((time.time() - start_time) * 1000, 2)

        return {
            'language': lang,
            'normalized_summary': summary[:200],
            'department': dept,
            'category': cat,
            'subcategory': subcat,
            'landmark': landmark[:100],
            'duration': duration,
            'impact': impact,
            'urgency': urgency,
            'recommended_action': action[:200],
            'is_advisory': True,
            'provider': 'deterministic_fallback',
            'model': 'regex_indic_taxonomy_v44',
            'latency_ms': latency_ms,
            'validation_status': 'PASSED',
            'interpretation_basis': 'Deterministic civic rules/pattern matching'
        }


# ------------------------------------------------------------------------------
# OPEN-SOURCE LLM PROVIDER (OLLAMA / VLLM / OPENAI-COMPATIBLE RUNTIMES)
# ------------------------------------------------------------------------------
class OpenSourceLLMProvider(LLMProviderInterface):
    """
    Connects to an actual Open-Source LLM running locally or self-hosted:
    - Ollama API (e.g. http://localhost:11434)
    - vLLM / LocalAI / HuggingFace TGI (OpenAI-compatible /v1/chat/completions)
    - Fallback: Automatically delegates to DeterministicFallbackProvider upon error.
    """

    def __init__(self, base_url: str, model: str, api_key: str = '', timeout: float = 8.0):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.api_key = api_key.strip()
        self.timeout = timeout
        self.fallback_engine = DeterministicFallbackProvider()

    def health_check(self) -> Tuple[bool, str]:
        """Checks connectivity to the open-source LLM runtime."""
        clean_base = self.base_url.rstrip('/')
        if clean_base.endswith('/v1'):
            clean_base = clean_base[:-3]
        test_urls = [
            f"{clean_base}/api/tags",
            f"{clean_base}/v1/models",
            f"{clean_base}/api/version"
        ]
        for url in test_urls:
            try:
                headers = {'User-Agent': 'SmartCivicConnect/44.0'}
                if self.api_key:
                    headers['Authorization'] = f"Bearer {self.api_key}"
                req = urllib.request.Request(url, headers=headers, method='GET')
                with urllib.request.urlopen(req, timeout=2.0) as resp:
                    if resp.status in (200, 204):
                        return True, f"Open-source LLM server responsive at {self.base_url}"
            except Exception:
                continue
        return False, f"Open-source LLM server unreachable at {self.base_url}"

    def understand_civic_complaint(self, text: str, location_hint: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        clean_text = (text or '').strip()

        if not clean_text:
            return self.fallback_engine.understand_civic_complaint('', location_hint)

        # 1. PII Sanitization Guardrail (Prior to Outbound Model Transmission)
        sanitized_text = sanitize_pii(clean_text)

        # Build strict civic schema system prompt with faithful semantic grounding
        system_prompt = (
            "You are an advisory civic complaint intelligence assistant for Smart Civic Connect.\n"
            "Analyze the citizen's grievance faithfully and extract STRICT JSON matching this exact schema:\n"
            "{\n"
            '  "language": "en | te | hi | other",\n'
            '  "normalized_summary": "Concise 1-sentence English summary faithfully preserving original meaning",\n'
            '  "department": "sanitation | roads | electricity | water_supply | food_safety",\n'
            '  "category": "garbage_overflow | drain_blockage | pothole | road_damage | broken_footpath | sparking_wire | power_outage | water_leakage | food_hygiene",\n'
            '  "subcategory": "specific issue described or empty string",\n'
            '  "landmark": "specific physical landmark stated by citizen or empty string",\n'
            '  "duration": "stated timeframe/duration or empty string",\n'
            '  "impact": "civic, health, or safety impact stated or empty string",\n'
            '  "urgency": "low | medium | high | critical",\n'
            '  "recommended_action": "actionable field squad recommendation"\n'
            "}\n"
            "STRICT RULES:\n"
            "1. Output valid JSON ONLY. No markdown ticks, no commentary.\n"
            "2. PRESERVE MEANING: Faithfully capture the citizen's original meaning in English, Telugu (తెలుగు), or Hindi (हिन्दी).\n"
            "3. NEVER INVENT: Never invent landmarks, streets, wards, incidents, durations, or impacts not described by the citizen.\n"
            "4. NO FALSE INFERENCE: Do NOT infer a water leak, road damage, or electrical hazard unless the citizen actually describes it. Garbage/waste (చెత్త / कचरा) is sanitation/garbage_overflow. Foul odor (దుర్వాసన / बदबू) is sanitation.\n"
            "5. LOCATION CONTEXT: Location hints provided by the system are NOT evidence that an incident occurred there.\n"
            "6. UNKNOWN FIELDS: If a field cannot be safely determined, use an empty string rather than inventing information.\n"
            "7. ADVISORY ONLY: Output is advisory metadata only. Never claim certainty, official verification, or government approval.\n"
            "8. CANONICAL ENUMS: 'department' must be exactly one of: sanitation, roads, electricity, water_supply, food_safety. 'category' must be one of the listed 9 categories. 'urgency' must be: low, medium, high, critical."
        )

        user_content = f"Citizen Complaint Text:\n\"\"\"{sanitized_text}\"\"\""
        if location_hint:
            user_content += f"\nReported Location Hint: {location_hint}"

        clean_base = self.base_url.rstrip('/')
        if clean_base.endswith('/v1'):
            clean_base = clean_base[:-3]

        # Determine primary endpoint strategy:
        # If Ollama endpoint (:11434 or 'ollama' in url), prioritize native /api/chat with format: json.
        # Otherwise, prioritize standard OpenAI-compatible /v1/chat/completions.
        is_ollama = (':11434' in clean_base or 'ollama' in clean_base.lower())
        raw_json_str = None
        error_msg = None

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'SmartCivicConnect/44.0'
        }
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"

        def _try_ollama_chat() -> Optional[str]:
            nonlocal error_msg
            endpoint = f"{clean_base}/api/chat"
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.1
                }
            }
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=json.dumps(payload).encode('utf-8'),
                    headers=headers,
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    res_dict = json.loads(resp.read().decode('utf-8'))
                    return res_dict.get('message', {}).get('content', '')
            except Exception as e:
                error_msg = f"Ollama native /api/chat failed: {e}"
                return None

        def _try_openai_chat() -> Optional[str]:
            nonlocal error_msg
            endpoint = f"{clean_base}/v1/chat/completions"
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "temperature": 0.1,
                "max_tokens": 512,
                "response_format": {"type": "json_object"}
            }
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=json.dumps(payload).encode('utf-8'),
                    headers=headers,
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    res_dict = json.loads(resp.read().decode('utf-8'))
                    choices = res_dict.get('choices', [])
                    if choices:
                        return choices[0].get('message', {}).get('content', '')
            except urllib.error.HTTPError as e:
                error_msg = f"HTTP {e.code}"
            except Exception as e:
                error_msg = str(e)
            return None

        if is_ollama:
            raw_json_str = _try_ollama_chat()
            if not raw_json_str:
                raw_json_str = _try_openai_chat()
        else:
            raw_json_str = _try_openai_chat()
            if not raw_json_str:
                raw_json_str = _try_ollama_chat()

        # If both failed or returned empty, execute Deterministic Fallback
        if not raw_json_str:
            fallback_res = self.fallback_engine.understand_civic_complaint(sanitized_text, location_hint)
            fallback_res['provider'] = f"fallback_due_to_error:{self.model}"
            fallback_res['fallback_reason'] = error_msg or 'No response from open-source model'
            fallback_res['interpretation_basis'] = 'Deterministic civic rules/pattern matching (fallback triggered)'
            return fallback_res

        # Validate and normalize model output
        validated, val_status = self._validate_and_normalize_schema(raw_json_str, sanitized_text, location_hint)
        latency_ms = round((time.time() - start_time) * 1000, 2)
        validated['latency_ms'] = latency_ms
        if val_status != 'PASSED':
            validated['provider'] = f"open_source_fallback:{self.model}"
            validated['fallback_triggered'] = True
            validated['interpretation_basis'] = 'Deterministic civic rules/pattern matching (fallback triggered)'
        else:
            validated['provider'] = f"open_source:{self.model}"
            validated['fallback_triggered'] = False
            is_local = (':11434' in self.base_url or '127.0.0.1' in self.base_url or 'localhost' in self.base_url or 'ollama' in self.base_url.lower())
            if is_local:
                validated['interpretation_basis'] = f"Open-source LLM inference ({self.model} via Ollama)"
            else:
                validated['interpretation_basis'] = f"Open-source LLM inference ({self.model})"
        validated['model'] = self.model
        validated['validation_status'] = val_status
        validated['is_advisory'] = True

        return validated

    def _validate_and_normalize_schema(self, raw_output: str, original_text: str, location_hint: Optional[str]) -> Tuple[Dict[str, Any], str]:
        """
        Parses JSON, validates required fields, maps synonyms to canonical enums,
        and applies length restrictions.
        """
        cleaned = raw_output.strip()
        # Strip markdown codeblocks ```json ... ```
        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)

        try:
            data = json.loads(cleaned)
        except Exception:
            fallback_res = self.fallback_engine.understand_civic_complaint(original_text, location_hint)
            return fallback_res, 'FALLBACK_MALFORMED_JSON'

        if not isinstance(data, dict):
            fallback_res = self.fallback_engine.understand_civic_complaint(original_text, location_hint)
            fallback_res['fallback_reason'] = 'LLM response is not a valid JSON object'
            return fallback_res, 'FALLBACK_NOT_A_DICT'

        # 1. Department Validation (Strict: Unsupported -> Deterministic Fallback)
        raw_dept = str(data.get('department', '')).lower().strip().replace(' ', '_')
        dept = DEPARTMENT_SYNONYMS.get(raw_dept)
        if not dept or dept not in VALID_DEPARTMENTS:
            fallback_res = self.fallback_engine.understand_civic_complaint(original_text, location_hint)
            fallback_res['fallback_reason'] = f"Unsupported LLM department '{raw_dept}'"
            return fallback_res, 'FALLBACK_UNSUPPORTED_DEPARTMENT'

        # 2. Category Validation (Strict: Unsupported -> Deterministic Fallback)
        raw_cat = str(data.get('category', '')).lower().strip().replace(' ', '_')
        cat = CATEGORY_SYNONYMS.get(raw_cat)
        if not cat or cat not in VALID_CATEGORIES:
            fallback_res = self.fallback_engine.understand_civic_complaint(original_text, location_hint)
            fallback_res['fallback_reason'] = f"Unsupported LLM category '{raw_cat}'"
            return fallback_res, 'FALLBACK_UNSUPPORTED_CATEGORY'

        # 3. Department-Category Alignment Validation
        expected_dept = VALID_CATEGORIES[cat][0]
        if expected_dept != dept:
            fallback_res = self.fallback_engine.understand_civic_complaint(original_text, location_hint)
            fallback_res['fallback_reason'] = f"Category '{cat}' belongs to '{expected_dept}', not '{dept}'"
            return fallback_res, 'FALLBACK_CATEGORY_DEPARTMENT_MISMATCH'

        # 4. Urgency Validation (Maps synonyms to canonical enums, strict fallback on invalid)
        raw_urg = str(data.get('urgency', '')).lower().strip().replace(' ', '_').replace('-', '_')
        urgency = URGENCY_SYNONYMS.get(raw_urg)
        if not urgency:
            for k, v in URGENCY_SYNONYMS.items():
                if k in raw_urg:
                    urgency = v
                    break
        if not urgency or urgency not in VALID_URGENCIES:
            fallback_res = self.fallback_engine.understand_civic_complaint(original_text, location_hint)
            fallback_res['fallback_reason'] = f"Unsupported LLM urgency '{raw_urg}'"
            return fallback_res, 'FALLBACK_UNSUPPORTED_URGENCY'

        # 5. Required Summary Validation
        summary = str(data.get('normalized_summary') or '').strip()
        if not summary:
            fallback_res = self.fallback_engine.understand_civic_complaint(original_text, location_hint)
            fallback_res['fallback_reason'] = "Missing required 'normalized_summary' field"
            return fallback_res, 'FALLBACK_MALFORMED_OUTPUT'

        # 6. Language Normalization
        raw_lang = str(data.get('language', '')).lower().strip()
        lang = raw_lang if raw_lang in VALID_LANGUAGES else 'other'

        # 7. Strings & length clamping (do not invent missing details)
        summary = summary[:200]
        landmark = str(data.get('landmark') or location_hint or '').strip()[:100]
        duration = str(data.get('duration') or '').strip()[:60]
        impact = str(data.get('impact') or '').strip()[:150]
        subcat = str(data.get('subcategory') or '').strip()[:80]
        action = str(data.get('recommended_action') or 'Deploy field inspection squad').strip()[:200]

        normalized = {
            'language': lang,
            'normalized_summary': summary,
            'department': dept,
            'category': cat,
            'subcategory': subcat,
            'landmark': landmark,
            'duration': duration,
            'impact': impact,
            'urgency': urgency,
            'recommended_action': action,
            'is_advisory': True
        }
        return normalized, 'PASSED'


# ------------------------------------------------------------------------------
# FACTORY: GET ACTIVE LLM ADAPTER
# ------------------------------------------------------------------------------
_GLOBAL_ADAPTER: Optional[LLMProviderInterface] = None

def get_llm_adapter() -> LLMProviderInterface:
    """
    Returns the configured LLM provider instance based on environment variables:
    - LLM_ENABLED: 'true' / 'false' (Default: 'false' unless LLM_BASE_URL is provided)
    - LLM_BASE_URL: Open-source server URL (Default: http://127.0.0.1:11434)
    - LLM_MODEL: Model tag (Default: qwen2.5:3b)
    - LLM_API_KEY: Optional token (e.g. for vLLM proxy)
    - LLM_TIMEOUT_SECONDS: Timeout in seconds (Default: 30.0)
    """
    global _GLOBAL_ADAPTER
    if _GLOBAL_ADAPTER is not None:
        return _GLOBAL_ADAPTER

    enabled_str = os.environ.get('LLM_ENABLED', '').strip().lower()
    base_url = os.environ.get('LLM_BASE_URL', '').strip()
    model = os.environ.get('LLM_MODEL', 'qwen2.5:3b').strip()
    api_key = os.environ.get('LLM_API_KEY', '').strip()
    try:
        timeout = float(os.environ.get('LLM_TIMEOUT_SECONDS', '30.0'))
    except ValueError:
        timeout = 30.0

    if enabled_str in ('true', '1', 'yes') or (base_url and enabled_str != 'false'):
        active_url = base_url or 'http://127.0.0.1:11434'
        _GLOBAL_ADAPTER = OpenSourceLLMProvider(
            base_url=active_url,
            model=model,
            api_key=api_key,
            timeout=timeout
        )
    else:
        _GLOBAL_ADAPTER = DeterministicFallbackProvider()

    return _GLOBAL_ADAPTER

def reset_llm_adapter(adapter: Optional[LLMProviderInterface] = None):
    """Allows testing harnesses to inject mock adapters or reset state."""
    global _GLOBAL_ADAPTER
    _GLOBAL_ADAPTER = adapter
