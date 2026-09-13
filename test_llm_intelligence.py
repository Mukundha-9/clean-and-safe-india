"""
Smart Civic Connect — Phase 1 Open-Source Civic LLM Intelligence Test Suite
Tests 10 mandatory LLM scenarios + Integration with Operational Core.
"""

import os
import sys
import json
import time
import sqlite3
import unittest
from unittest.mock import patch, MagicMock
import urllib.request
import urllib.error

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm_adapter
from llm_adapter import (
    get_llm_adapter,
    reset_llm_adapter,
    DeterministicFallbackProvider,
    OpenSourceLLMProvider,
    sanitize_pii,
    VALID_DEPARTMENTS,
    VALID_CATEGORIES,
    VALID_URGENCIES,
    VALID_LANGUAGES
)


class TestCivicLLMIntelligence(unittest.TestCase):
    """Unit and integration tests for Phase 1 Open-Source Civic LLM Intelligence Foundation."""

    def setUp(self):
        reset_llm_adapter(None)

    def tearDown(self):
        reset_llm_adapter(None)

    # --------------------------------------------------------------------------
    # 1. English Garbage Complaint
    # --------------------------------------------------------------------------
    def test_01_english_garbage_complaint(self):
        adapter = DeterministicFallbackProvider()
        text = "There has been garbage piling up near the college gate for the last three days. The smell is becoming unbearable and people are throwing more waste there."
        res = adapter.understand_civic_complaint(text)

        self.assertEqual(res['language'], 'en')
        self.assertEqual(res['department'], 'sanitation')
        self.assertEqual(res['category'], 'garbage_overflow')
        self.assertIn(res['urgency'], ['high', 'critical'])
        self.assertTrue(res['is_advisory'])
        self.assertEqual(res['validation_status'], 'PASSED')
        self.assertTrue(len(res['normalized_summary']) > 0)
        self.assertTrue(len(res['recommended_action']) > 0)

    # --------------------------------------------------------------------------
    # 2. Telugu Garbage Complaint
    # --------------------------------------------------------------------------
    def test_02_telugu_garbage_complaint(self):
        adapter = DeterministicFallbackProvider()
        text = "కాలేజ్ గేట్ దగ్గర మూడు రోజులుగా చెత్త పేరుకుపోయింది. చాలా దుర్వాసన వస్తోంది."
        res = adapter.understand_civic_complaint(text)

        self.assertEqual(res['language'], 'te')
        self.assertEqual(res['department'], 'sanitation')
        self.assertEqual(res['category'], 'garbage_overflow')
        self.assertIn(res['urgency'], ['high', 'critical'])
        self.assertTrue(res['is_advisory'])
        self.assertIn("Garbage", res['normalized_summary'])

    # --------------------------------------------------------------------------
    # 3. Telugu Road / Pothole Complaint
    # --------------------------------------------------------------------------
    def test_03_telugu_road_pothole_complaint(self):
        adapter = DeterministicFallbackProvider()
        text = "మార్కెట్ రోడ్డుపై పెద్ద గుంతలు పడ్డాయి, ప్రమాదాలు జరుగుతున్నాయి."
        res = adapter.understand_civic_complaint(text)

        self.assertEqual(res['language'], 'te')
        self.assertEqual(res['department'], 'roads')
        self.assertEqual(res['category'], 'pothole')
        self.assertTrue(res['is_advisory'])
        self.assertIn("pothole", res['normalized_summary'].lower())

    # --------------------------------------------------------------------------
    # 4. Hindi Complaint
    # --------------------------------------------------------------------------
    def test_04_hindi_complaint(self):
        adapter = DeterministicFallbackProvider()
        text = "कॉलेज के गेट के पास तीन दिनों से कचरा जमा है और बहुत बदबू आ रही है।"
        res = adapter.understand_civic_complaint(text)

        self.assertEqual(res['language'], 'hi')
        self.assertEqual(res['department'], 'sanitation')
        self.assertEqual(res['category'], 'garbage_overflow')
        self.assertTrue(res['is_advisory'])
        self.assertIn("Garbage", res['normalized_summary'])

    # --------------------------------------------------------------------------
    # 5. Ambiguous Complaint
    # --------------------------------------------------------------------------
    def test_05_ambiguous_complaint(self):
        adapter = DeterministicFallbackProvider()
        text = "Something looks unusual and concerning near the corner of the cross street."
        res = adapter.understand_civic_complaint(text)

        self.assertIn(res['department'], VALID_DEPARTMENTS)
        self.assertIn(res['category'], VALID_CATEGORIES)
        self.assertIn(res['urgency'], VALID_URGENCIES)
        self.assertTrue(res['is_advisory'])
        self.assertEqual(res['validation_status'], 'PASSED')

    # --------------------------------------------------------------------------
    # 6. Empty Complaint
    # --------------------------------------------------------------------------
    def test_06_empty_complaint(self):
        adapter = DeterministicFallbackProvider()
        res = adapter.understand_civic_complaint("")

        self.assertIn(res['department'], VALID_DEPARTMENTS)
        self.assertIn(res['category'], VALID_CATEGORIES)
        self.assertIn(res['urgency'], VALID_URGENCIES)
        self.assertTrue(res['is_advisory'])

    # --------------------------------------------------------------------------
    # 7. Malformed LLM JSON Response
    # --------------------------------------------------------------------------
    def test_07_malformed_llm_json(self):
        provider = OpenSourceLLMProvider(base_url="http://mock-llm:11434", model="llama3.2")
        # Simulate model returning broken JSON
        bad_json = "This is not json { 'broken': true "
        normalized, status = provider._validate_and_normalize_schema(bad_json, "Garbage at gate", None)

        self.assertEqual(status, 'FALLBACK_MALFORMED_JSON')
        self.assertIn(normalized['department'], VALID_DEPARTMENTS)
        self.assertIn(normalized['category'], VALID_CATEGORIES)
        self.assertTrue(normalized['is_advisory'])

    # --------------------------------------------------------------------------
    # 8. LLM Timeout Simulation
    # --------------------------------------------------------------------------
    def test_08_llm_timeout(self):
        provider = OpenSourceLLMProvider(base_url="http://mock-llm:11434", model="llama3.2", timeout=0.001)
        with patch('urllib.request.urlopen', side_effect=TimeoutError("Connection timed out")):
            res = provider.understand_civic_complaint("Pothole on Main Road")

            self.assertIn(res['department'], VALID_DEPARTMENTS)
            self.assertEqual(res['department'], 'roads')
            self.assertIn('fallback_due_to_error', res['provider'])
            self.assertTrue(res['is_advisory'])

    # --------------------------------------------------------------------------
    # 9. LLM Unavailable / Connection Refused
    # --------------------------------------------------------------------------
    def test_09_llm_unavailable(self):
        # Point to an unallocated high port
        provider = OpenSourceLLMProvider(base_url="http://127.0.0.1:59999", model="llama3.2", timeout=0.5)
        res = provider.understand_civic_complaint("Water pipe burst wasting drinking water")

        self.assertIn(res['department'], VALID_DEPARTMENTS)
        self.assertEqual(res['department'], 'water_supply')
        self.assertEqual(res['category'], 'water_leakage')
        self.assertIn('fallback_due_to_error', res['provider'])
        self.assertTrue(res['is_advisory'])

    # --------------------------------------------------------------------------
    # 10. Unsupported Department / Category / Urgency Fallbacks (Phase 1A Hardened)
    # --------------------------------------------------------------------------
    def test_10a_unsupported_department_triggers_fallback(self):
        provider = OpenSourceLLMProvider(base_url="http://mock-llm:11434", model="llama3.2")
        weird_output = json.dumps({
            "language": "en",
            "normalized_summary": "Alien spaceship landed in the road",
            "department": "intergalactic_defense",
            "category": "ufo_landing",
            "urgency": "medium"
        })
        normalized, status = provider._validate_and_normalize_schema(weird_output, "Garbage at gate", None)
        self.assertEqual(status, 'FALLBACK_UNSUPPORTED_DEPARTMENT')
        self.assertIn(normalized['department'], VALID_DEPARTMENTS)
        self.assertIn(normalized['category'], VALID_CATEGORIES)

    def test_10b_unsupported_category_triggers_fallback(self):
        provider = OpenSourceLLMProvider(base_url="http://mock-llm:11434", model="llama3.2")
        weird_output = json.dumps({
            "language": "en",
            "normalized_summary": "Garbage issue",
            "department": "sanitation",
            "category": "quantum_singularity_dump",
            "urgency": "medium"
        })
        normalized, status = provider._validate_and_normalize_schema(weird_output, "Garbage at gate", None)
        self.assertEqual(status, 'FALLBACK_UNSUPPORTED_CATEGORY')
        self.assertIn(normalized['department'], VALID_DEPARTMENTS)
        self.assertIn(normalized['category'], VALID_CATEGORIES)

    def test_10c_category_department_mismatch_triggers_fallback(self):
        provider = OpenSourceLLMProvider(base_url="http://mock-llm:11434", model="llama3.2")
        weird_output = json.dumps({
            "language": "en",
            "normalized_summary": "Pothole on the road",
            "department": "sanitation",
            "category": "pothole",  # Pothole belongs to roads, not sanitation!
            "urgency": "medium"
        })
        normalized, status = provider._validate_and_normalize_schema(weird_output, "Pothole on Main road", None)
        self.assertEqual(status, 'FALLBACK_CATEGORY_DEPARTMENT_MISMATCH')
        self.assertIn(normalized['department'], VALID_DEPARTMENTS)
        self.assertIn(normalized['category'], VALID_CATEGORIES)

    def test_10d_unsupported_urgency_triggers_fallback(self):
        provider = OpenSourceLLMProvider(base_url="http://mock-llm:11434", model="llama3.2")
        weird_output = json.dumps({
            "language": "en",
            "normalized_summary": "Pothole on the road",
            "department": "roads",
            "category": "pothole",
            "urgency": "apocalyptic_catastrophe"
        })
        normalized, status = provider._validate_and_normalize_schema(weird_output, "Pothole on Main road", None)
        self.assertEqual(status, 'FALLBACK_UNSUPPORTED_URGENCY')
        self.assertIn(normalized['department'], VALID_DEPARTMENTS)
        self.assertIn(normalized['category'], VALID_CATEGORIES)
        self.assertIn(normalized['urgency'], VALID_URGENCIES)

    # --------------------------------------------------------------------------
    # 11. PII Sanitization Guardrail & Outbound Transmission Privacy
    # --------------------------------------------------------------------------
    def test_11_pii_sanitization(self):
        raw_text = "Citizen Ravi phone +91 98480 12345 reported garbage. Contact him at ravi.kumar@gmail.com, Aadhaar 2345 6789 0123."
        sanitized = sanitize_pii(raw_text)

        self.assertNotIn("98480", sanitized)
        self.assertNotIn("ravi.kumar@gmail.com", sanitized)
        self.assertNotIn("2345 6789 0123", sanitized)
        self.assertIn("[REDACTED_PHONE]", sanitized)
        self.assertIn("[REDACTED_EMAIL]", sanitized)
        self.assertIn("[REDACTED_UID]", sanitized)

    def test_11b_outbound_pii_sanitization_before_http_dispatch(self):
        """Verifies that PII is redacted in the outgoing HTTP payload BEFORE external dispatch."""
        provider = OpenSourceLLMProvider(base_url="https://api.groq.com/openai", model="openai/gpt-oss-20b", api_key="test-key")
        captured_payloads = []

        def mock_urlopen(req, timeout=None):
            captured_payloads.append((req.full_url, req.headers, req.data.decode('utf-8') if req.data else ''))
            raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, None)

        with patch('urllib.request.urlopen', side_effect=mock_urlopen):
            res = provider.understand_civic_complaint(
                "Garbage dump at gate. Citizen phone +91 98480 12345, email citizen@civic.gov.in, UID 4455 6677 8899."
            )

        self.assertTrue(len(captured_payloads) > 0)
        outbound_url, outbound_headers, outbound_body = captured_payloads[0]
        # Verify outgoing headers contain User-Agent
        self.assertEqual(outbound_headers.get('User-agent'), 'SmartCivicConnect/44.0')
        # Verify outbound body does not leak raw PII
        self.assertNotIn("98480", outbound_body)
        self.assertNotIn("citizen@civic.gov.in", outbound_body)
        self.assertNotIn("4455 6677 8899", outbound_body)
        self.assertIn("[REDACTED_PHONE]", outbound_body)
        self.assertIn("[REDACTED_EMAIL]", outbound_body)
        self.assertIn("[REDACTED_UID]", outbound_body)

    def test_11c_deterministic_interpretation_basis_no_fake_confidence(self):
        """Verifies deterministic fallback provides interpretation_basis and no fake numeric confidence."""
        adapter = DeterministicFallbackProvider()
        res = adapter.understand_civic_complaint("Pothole on Main Road near Bus Stand")

        self.assertNotIn('confidence', res)
        self.assertIn('interpretation_basis', res)
        self.assertEqual(res['interpretation_basis'], 'Deterministic civic rules/pattern matching')

    def test_11d_live_llm_advisory_distinct_basis_from_deterministic(self):
        """Verifies successful live LLM sets transparent Open-source basis distinct from deterministic decision."""
        provider = OpenSourceLLMProvider(base_url="http://127.0.0.1:11434", model="qwen2.5:3b")
        fake_llm_output = json.dumps({
            "language": "en",
            "normalized_summary": "Garbage overflow near college gate",
            "department": "sanitation",
            "category": "garbage_overflow",
            "urgency": "medium"
        })
        with patch.object(provider, '_validate_and_normalize_schema', return_value=({
            'language': 'en',
            'normalized_summary': 'Garbage overflow near college gate',
            'department': 'sanitation',
            'category': 'garbage_overflow',
            'subcategory': '',
            'landmark': 'college gate',
            'duration': '3 days',
            'impact': 'smell',
            'urgency': 'medium',
            'recommended_action': 'Clear garbage',
            'is_advisory': True
        }, 'PASSED')):
            with patch('urllib.request.urlopen') as mock_url:
                mock_resp = MagicMock()
                mock_resp.read.return_value = json.dumps({
                    'message': {'content': fake_llm_output}
                }).encode('utf-8')
                mock_url.return_value.__enter__.return_value = mock_resp

                res = provider.understand_civic_complaint("Garbage overflow near college gate")
                self.assertIn("Open-source LLM inference", res['interpretation_basis'])
                self.assertIn("qwen2.5:3b", res['interpretation_basis'])
                self.assertIn("via Ollama", res['interpretation_basis'])
                self.assertFalse(res['fallback_triggered'])


class TestLiveServerIntegration(unittest.TestCase):
    """Integration tests running against active ThreadingHTTPServer instance."""

    server_thread = None
    httpd = None
    port = 8008
    base_url = f"http://127.0.0.1:{port}"

    @classmethod
    def setUpClass(cls):
        import threading
        import server
        server.PORT = cls.port
        server.init_database()
        cls.httpd = server.ThreadingHTTPServer(('127.0.0.1', cls.port), server.CivicAppRequestHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        if cls.httpd:
            cls.httpd.shutdown()
            cls.httpd.server_close()

    def _post(self, path, data, headers=None):
        url = f"{self.base_url}{path}"
        req_headers = {'Content-Type': 'application/json'}
        if headers:
            req_headers.update(headers)
        body = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=body, headers=req_headers, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status, json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode('utf-8'))

    def test_12_http_complaint_intelligence_en(self):
        code, res = self._post('/api/ai/complaint-intelligence', {
            'text': 'There has been garbage piling up near the college gate for the last three days. The smell is becoming unbearable.',
            'location': 'Ward 12 (Market Zone)'
        })
        self.assertEqual(code, 200)
        self.assertTrue(res['success'])

        # Verify separation: llm_advisory and deterministic_decision
        self.assertIn('llm_advisory', res)
        self.assertIn('deterministic_decision', res)

        advisory = res['llm_advisory']
        decision = res['deterministic_decision']

        self.assertEqual(advisory['language'], 'en')
        self.assertEqual(advisory['department'], 'sanitation')
        self.assertEqual(advisory['category'], 'garbage_overflow')
        self.assertTrue(advisory['is_advisory'])
        self.assertIn('interpretation_basis', advisory)
        self.assertEqual(advisory['interpretation_basis'], 'Deterministic civic rules/pattern matching')
        self.assertNotIn('confidence', advisory)

        self.assertEqual(decision['department'], 'sanitation')
        self.assertEqual(decision['category'], 'garbage_overflow')
        self.assertTrue(decision['isAuthoritative'])
        self.assertEqual(decision['interpretation_basis'], 'Deterministic civic rules/pattern matching')

        # Verify audit event in operational_audit_logs
        import server
        conn = server.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM operational_audit_logs WHERE actionType = 'CIVIC_LLM_COMPLAINT_UNDERSTANDING' ORDER BY timestamp DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row['officer'], 'Civic LLM Advisory Engine')
        self.assertEqual(row['assignedWorker'], 'N/A (Advisory Inference)')
        audit_notes = json.loads(row['supervisorNotes'])
        self.assertIn('provider', audit_notes)
        self.assertIn('validation_status', audit_notes)

    def test_13_http_complaint_intelligence_telugu(self):
        code, res = self._post('/api/ai/complaint-intelligence', {
            'text': 'కాలేజ్ గేట్ దగ్గర మూడు రోజులుగా చెత్త పేరుకుపోయింది. చాలా దుర్వాసన వస్తోంది.',
            'location': 'Ward 12 (Market Zone)'
        })
        self.assertEqual(code, 200)
        self.assertTrue(res['success'])

        advisory = res['llm_advisory']
        decision = res['deterministic_decision']

        self.assertEqual(advisory['language'], 'te')
        self.assertEqual(advisory['department'], 'sanitation')
        self.assertEqual(decision['department'], 'sanitation')
        self.assertTrue(advisory['is_advisory'])
        self.assertTrue(decision['isAuthoritative'])

    def test_14_http_complaint_intelligence_empty_rejected(self):
        code, res = self._post('/api/ai/complaint-intelligence', {
            'text': '',
            'location': ''
        })
        self.assertEqual(code, 400)
        self.assertFalse(res['success'])

    def test_15_authoritative_issue_submission(self):
        ts = int(time.time() * 1000)
        issue_id = f"ISS-TEST-{ts % 100000}"
        code, res = self._post('/api/issues', {
            'id': issue_id,
            'title': 'College Gate Garbage Accumulation',
            'description': 'Garbage has been overflowing for 3 days near college gate',
            'department': 'sanitation',
            'category': 'garbage_overflow',
            'severity': 'bulk',
            'state': 'Andhra Pradesh',
            'city': 'Surampalem',
            'ward': 'Ward 12 (Market Zone)',
            'reportedBy': 'KRISH',
            'reportedById': f'user-test-{ts}'
        })
        self.assertEqual(code, 200)
        self.assertTrue(res['success'])

        # Verify database record
        import server
        conn = server.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, department, category, slaDeadline, evidenceHash FROM issues WHERE id = ?", (issue_id,))
        row = cur.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row['department'], 'sanitation')
        self.assertIsNotNone(row['slaDeadline'])

    def test_16_worker_cannot_self_resolve(self):
        import server
        conn = server.get_db_connection()
        cur = conn.cursor()
        token = f"test-worker-token-{int(time.time())}"
        cur.execute("SELECT id FROM issues LIMIT 1")
        existing_issue_row = cur.fetchone()
        existing_issue_id = existing_issue_row['id'] if existing_issue_row else 'ISS-2026-00001'

        cur.execute("""
            INSERT OR REPLACE INTO sessions (token, userId, email, department, roleTitle, name, officialId, jurisdictionState, jurisdictionCity, jurisdictionWard, createdAt, expiresAt)
            VALUES (?, 'user-104', 'worker4@municipality.gov.in', 'worker', 'Field Response Squad Lead', 'Ramesh', 'Squad 4 Lead', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', ?, ?)
        """, (token, int(time.time()*1000), int(time.time()*1000) + 3600000))
        conn.commit()
        conn.close()

        code, res = self._post('/api/issues/resolve', {
            'issueId': existing_issue_id,
            'resolutionNotes': 'Worker attempting unauthorized closure'
        }, headers={'Authorization': f"Bearer {token}"})

        # Worker must be blocked from self-resolving (403 Forbidden)
        self.assertEqual(code, 403)
        self.assertFalse(res.get('success', False))


if __name__ == '__main__':
    unittest.main(verbosity=2)

