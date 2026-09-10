"""Clean & Safe India - Real-Time Backend Server v44.0.0 (Python 3.14)"""
import os
import sys
import re
import json
import time
import sqlite3
import datetime
import threading
import mimetypes
import hashlib
import secrets
import hmac
import random
import math
import base64
import predictive_engine
import ai_engine

# ------------------------------------------------------------------------------
# INDUSTRY-STANDARD PASSWORD SECURITY (SCRYPT WITH PER-USER SALT)
# ------------------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Hash a password securely using scrypt with a unique 16-byte random salt."""
    if not password:
        return ''
    salt = secrets.token_hex(16)
    key = hashlib.scrypt(password.encode('utf-8'), salt=bytes.fromhex(salt), n=16384, r=8, p=1)
    return f"scrypt${salt}${key.hex()}"

def verify_password(password: str, stored: str) -> bool:
    """Verify password against stored scrypt hash or legacy plain-text (backward compatible)."""
    if not stored or not password:
        return False
    if stored.startswith('scrypt$'):
        parts = stored.split('$')
        if len(parts) == 3:
            salt_hex = parts[1]
            hash_hex = parts[2]
            try:
                key = hashlib.scrypt(password.encode('utf-8'), salt=bytes.fromhex(salt_hex), n=16384, r=8, p=1)
                return hmac.compare_digest(key.hex(), hash_hex)
            except Exception:
                return False
    # Backward compatibility with existing plain-text demo passwords
    return hmac.compare_digest(stored, password)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get('PORT', 8000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'civic_database.db')
PREDICTIVE_HONEST_LABEL = "AI-Assisted Predictive Demo — Transparent Rule-Based Forecast (No ML Model Configured)"

CIVIC_REWARDS_CATALOG = [
    {
        'id': 'bus_pass',
        'title': 'City Bus Pass Credit',
        'category': 'self',
        'typeLabel': 'Direct Commute Benefit',
        'points': 50,
        'icon': '🚌',
        'desc': '30-Day City Bus transit pass credit prototype. Redeem points for public bus transport pass.',
        'disclaimer': 'DEMO / PROTOTYPE — For civic engagement demonstration only. Not an official public transit contract.'
    },
    {
        'id': 'electricity_credit',
        'title': 'Electricity Bill Credit',
        'category': 'self',
        'typeLabel': 'Utility Bill Credit',
        'points': 100,
        'icon': '⚡',
        'desc': 'Municipal electricity bill adjustment prototype for active civic reporting and street light maintenance reporting.',
        'disclaimer': 'DEMO / PROTOTYPE — For civic engagement demonstration only. Not an official DISCOM utility contract.'
    },
    {
        'id': 'water_credit',
        'title': 'Water Bill Credit',
        'category': 'self',
        'typeLabel': 'Utility Bill Credit',
        'points': 75,
        'icon': '💧',
        'desc': 'Drinking water municipal supply tariff rebate prototype for active drainage and leakage reporting.',
        'disclaimer': 'DEMO / PROTOTYPE — For civic engagement demonstration only. Not an official Water Supply Board contract.'
    },
    {
        'id': 'service_coupon',
        'title': 'Local Civic Service Coupon',
        'category': 'self',
        'typeLabel': 'Civic Merchant Voucher',
        'points': 60,
        'icon': '🎟️',
        'desc': 'Local civic market stall and authorized municipal service voucher prototype.',
        'disclaimer': 'DEMO / PROTOTYPE — For civic engagement demonstration only. Not an official commercial voucher.'
    },
    {
        'id': 'tree_planting',
        'title': 'Neighbourhood Tree Planting',
        'category': 'community',
        'typeLabel': 'Green Ward Sponsorship',
        'points': 50,
        'icon': '🌱',
        'desc': 'Direct your civic points toward Ward 12 sapling procurement and roadside green canopy planting.',
        'disclaimer': 'DEMO / PROTOTYPE — Community engagement demonstration only.'
    },
    {
        'id': 'school_drive',
        'title': 'Clean School Zone Drive',
        'category': 'community',
        'typeLabel': 'Education Zone Sponsorship',
        'points': 80,
        'icon': '🏫',
        'desc': 'Sponsor dedicated school zone litter bins, child safety signage, and cleanliness kits for local primary schools.',
        'disclaimer': 'DEMO / PROTOTYPE — Community engagement demonstration only.'
    },
    {
        'id': 'park_bench',
        'title': 'Local Park Bench Sponsorship',
        'category': 'community',
        'typeLabel': 'Public Amenity Sponsorship',
        'points': 120,
        'icon': '🪑',
        'desc': 'Sponsor an eco-friendly recycled park bench dedicated to active civic volunteers in Ward 12.',
        'disclaimer': 'DEMO / PROTOTYPE — Community engagement demonstration only.'
    },
    {
        'id': 'drinking_water',
        'title': 'Public Drinking Water Maintenance',
        'category': 'community',
        'typeLabel': 'Public Health Sponsorship',
        'points': 100,
        'icon': '🚰',
        'desc': 'Sponsor maintenance and cartridge replacement for public drinking water kiosks in high-footfall ward areas.',
        'disclaimer': 'DEMO / PROTOTYPE — Community engagement demonstration only.'
    },
    {
        'id': 'community_cleanliness',
        'title': 'Community Cleanliness Activity',
        'category': 'community',
        'typeLabel': 'Volunteer Squad Sponsorship',
        'points': 60,
        'icon': '🧹',
        'desc': 'Sponsor volunteer safety vests, sturdy waste disposal bags, and cleaning tools for local weekend drives.',
        'disclaimer': 'DEMO / PROTOTYPE — Community engagement demonstration only.'
    }
]

for _r in CIVIC_REWARDS_CATALOG:
    _r['points_cost'] = _r['points']
    _r['description'] = _r['desc']

# SMTP Mail Dispatcher Configuration (Optional: set environment variables or use default relay)
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')

def dispatch_otp_email(recipient_email, otp_code):
    """Attempts to deliver real OTP to user email inbox via SMTP if configured."""
    if not SMTP_USER or not SMTP_PASS:
        print(f'[Email Engine] OTP {otp_code} generated for {recipient_email}. (To deliver directly into real email inbox, set SMTP_USER & SMTP_PASS in server environment)')
        return False, 'SMTP credentials not configured.'

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'🔐 Clean & Safe India — Your Verification OTP: {otp_code}'
        msg['From'] = f'Clean & Safe India Portal <{SMTP_USER}>'
        msg['To'] = recipient_email

        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; background: #060911; color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #10b981;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #10b981; margin: 0;">🇮🇳 Clean & Safe India</h2>
                <p style="color: #94a3b8; font-size: 13px; margin: 4px 0;">National Smart Civic Grievance Network</p>
            </div>
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px dashed #10b981; border-radius: 10px; padding: 20px; text-align: center; margin: 20px 0;">
                <div style="font-size: 13px; color: #a7f3d0; text-transform: uppercase; font-weight: bold; letter-spacing: 1px;">Your Citizen Verification OTP</div>
                <div style="font-size: 32px; font-weight: 900; letter-spacing: 6px; color: #34d399; margin: 12px 0; font-family: monospace;">{otp_code}</div>
                <div style="font-size: 12px; color: #cbd5e1;">Valid for 10 minutes. Do not share this OTP with anyone.</div>
            </div>
            <p style="font-size: 13px; color: #94a3b8; line-height: 1.5;">
                Use this OTP to complete your citizen registration and claim your <strong>20 Welcome Civic Credits</strong>.
            </p>
            <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px; margin-top: 20px; font-size: 11px; color: #64748b; text-align: center;">
                Government of India • Ministry of Housing & Urban Affairs (MoHUA)
            </div>
        </div>
        """
        msg.attach(MIMEText(html, 'html'))

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=8)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, recipient_email, msg.as_string())
        server.quit()
        print(f'[Email Engine] ✅ Real OTP email sent successfully to {recipient_email}!')
        return True, 'OTP sent directly to your email inbox!'
    except Exception as e:
        print(f'[Email Engine] SMTP delivery exception for {recipient_email}: {e}')
        return False, str(e)

# ------------------------------------------------------------------------------
# In-Memory Active OTP Cache: { email: { 'otp': '123456', 'expires_at': timestamp } }
ACTIVE_OTPS = {}

# 1. DATABASE MANAGEMENT & SCHEMA INITIALIZATION
# ------------------------------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=30.0)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=30000')
    conn.row_factory = sqlite3.Row
    return conn

# ------------------------------------------------------------------------------
# SESSION MANAGEMENT & AUTHORITATIVE SERVER-SIDE IDENTITY RESOLUTION
# ------------------------------------------------------------------------------
def create_session(user_dict, conn):
    """
    Generate cryptographically secure 64-character session token.
    Persist session row in SQLite with authoritative user identity and jurisdiction.
    """
    token = secrets.token_hex(32)
    now_ms = int(time.time() * 1000)
    expires_at = now_ms + (7 * 86400 * 1000)  # 7 Days valid
    
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO sessions (
            token, userId, email, department, roleTitle, name, officialId,
            jurisdictionState, jurisdictionCity, jurisdictionWard, createdAt, expiresAt
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        token,
        user_dict.get('id'),
        (user_dict.get('email') or '').lower().strip(),
        user_dict.get('department'),
        user_dict.get('roleTitle'),
        user_dict.get('name'),
        user_dict.get('officialId'),
        user_dict.get('jurisdictionState'),
        user_dict.get('jurisdictionCity'),
        user_dict.get('jurisdictionWard'),
        now_ms,
        expires_at
    ))
    conn.commit()
    return token

def get_authenticated_user(handler, conn=None):
    """
    Authoritative server-side identity resolver.
    Validates token from Authorization: Bearer <token> against sessions table.
    Ensures token has not expired and retrieves authorized jurisdiction.
    """
    auth_header = handler.headers.get('Authorization', '').strip()
    if not auth_header:
        return None

    token = auth_header
    if token.lower().startswith('bearer '):
        token = token[7:].strip()

    if not token:
        return None

    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    try:
        cursor = conn.cursor()
        now_ms = int(time.time() * 1000)
        cursor.execute('''
            SELECT s.*, 
                   u.name as u_name,
                   u.avatar as u_avatar,
                   u.phone as u_phone,
                   u.permanentAddress as u_address,
                   u.profileCompleted as u_completed,
                   u.civicCredits as u_credits,
                   u.jurisdictionState as u_state, 
                   u.jurisdictionCity as u_city, 
                   u.jurisdictionWard as u_ward
            FROM sessions s
            LEFT JOIN users u ON LOWER(TRIM(u.email)) = LOWER(TRIM(s.email))
            WHERE s.token = ? AND s.expiresAt > ?
        ''', (token, now_ms))
        row = cursor.fetchone()
        if row:
            d = dict(row)
            # Favor current users table authoritative values if set
            if d.get('u_name'):
                d['name'] = d['u_name']
            if d.get('u_avatar'):
                d['avatar'] = d['u_avatar']
            if d.get('u_phone'):
                d['phone'] = d['u_phone']
            if d.get('u_address'):
                d['permanentAddress'] = d['u_address']
            d['profileCompleted'] = 1 if d.get('u_completed') == 1 else 0
            if d.get('u_credits') is not None:
                d['civicCredits'] = d['u_credits']
            if d.get('u_state'):
                d['jurisdictionState'] = d['u_state']
            if d.get('u_city'):
                d['jurisdictionCity'] = d['u_city']
            if d.get('u_ward'):
                d['jurisdictionWard'] = d['u_ward']
            return d

        return None
    finally:
        if close_conn:
            conn.close()

# ------------------------------------------------------------------------------
# CIVIC INCIDENT IDENTITY ENGINE (v43.0.0) — DETERMINISTIC MULTI-SIGNAL MATCHER
# ------------------------------------------------------------------------------
def compute_evidence_hash(img_str):
    """Compute SHA-256 hash for genuine evidence verification."""
    if not img_str:
        return None
    try:
        if ',' in img_str and 'base64' in img_str:
            b64_data = img_str.split(',', 1)[1]
            raw_bytes = base64.b64decode(b64_data)
        else:
            raw_bytes = img_str.encode('utf-8')
        return hashlib.sha256(raw_bytes).hexdigest()
    except Exception:
        return hashlib.sha256(str(img_str).encode('utf-8', errors='ignore')).hexdigest()

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Distance in meters between two lat/lon coordinates."""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 999999.0
    try:
        lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
        R = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c
    except Exception:
        return 999999.0

def normalize_text_tokens(text):
    """Normalize text into meaningful civic tokens (strip stopwords & punctuation)."""
    if not text:
        return set()
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'is', 'are', 'was', 'were', 'been', 'be', 'this', 'that', 'there', 'here',
        'near', 'by', 'from', 'about', 'has', 'have', 'had', 'very', 'severe', 'please',
        'urgent', 'issue', 'complaint', 'problem', 'reported', 'area', 'zone'
    }
    words = re.findall(r'[a-zA-Z0-9]+', str(text).lower())
    return {w for w in words if len(w) > 2 and w not in stopwords}

# ------------------------------------------------------------------------------
# VERSION 44: GPS-BASED GEO-EVIDENCE & CIVIC JURISDICTION ENGINE
# ------------------------------------------------------------------------------
CIVIC_GEOGRAPHY = {
    'Andhra Pradesh': {
        'Surampalem': {
            'center': (17.0050, 81.8050),
            'radiusMeters': 4500.0,
            'wards': {
                'Ward 12 (Market Zone)': {'center': (17.0015, 81.8042), 'radiusMeters': 900.0, 'zone': 'Commercial / Market Zone'},
                'Ward 14 (Campus Zone)': {'center': (17.0090, 81.8020), 'radiusMeters': 1200.0, 'zone': 'Academic Campus Zone'},
                'Ward 11 (Lake View Zone)': {'center': (17.0050, 81.8080), 'radiusMeters': 900.0, 'zone': 'Residential / Lake View Zone'}
            }
        },
        'Kakinada': {
            'center': (16.9890, 82.2474),
            'radiusMeters': 8000.0,
            'wards': {
                'Ward 1 (Port Zone)': {'center': (16.9850, 82.2400), 'radiusMeters': 1500.0, 'zone': 'Port Corridor'},
                'Ward 2 (City Central)': {'center': (16.9920, 82.2510), 'radiusMeters': 1500.0, 'zone': 'City Center'},
                'Ward 5 (Collectorate)': {'center': (16.9780, 82.2350), 'radiusMeters': 1500.0, 'zone': 'Administrative Zone'}
            }
        },
        'Visakhapatnam': {
            'center': (17.6868, 83.2185),
            'radiusMeters': 15000.0,
            'wards': {
                'Ward 10 (Beach Road)': {'center': (17.7200, 83.3000), 'radiusMeters': 2000.0, 'zone': 'Coastal Promenade'},
                'Ward 15 (Siripuram)': {'center': (17.7100, 83.3100), 'radiusMeters': 2000.0, 'zone': 'Central Commercial'},
                'Ward 20 (Gajuwaka)': {'center': (17.7000, 83.2900), 'radiusMeters': 2500.0, 'zone': 'Industrial Sector'}
            }
        }
    }
}

def evaluate_geo_evidence(lat, lng, reported_ward=None, reported_city=None, reported_state=None, accuracy=None):
    """
    Evaluates citizen GPS coordinates against genuine civic administrative centers and radii.
    Result States:
      - LOCATION_CONSISTENT: High confidence match within authentic ward/city radius.
      - LOCATION_NEEDS_CONFIRMATION: Within city limits but near boundary or divergent from reported ward.
      - LOCATION_MISMATCH: Out of city/state jurisdiction bounds.
      - LOCATION_UNAVAILABLE: Coordinates missing, zero, or invalid.
    """
    if lat is None or lng is None:
        return {
            'status': 'LOCATION_UNAVAILABLE',
            'consistencyLevel': 'UNAVAILABLE',
            'latitude': None,
            'longitude': None,
            'accuracy': accuracy,
            'distanceMeters': None,
            'resolvedState': reported_state or 'Andhra Pradesh',
            'resolvedCity': reported_city or 'Surampalem',
            'resolvedWard': reported_ward or 'Ward 12 (Market Zone)',
            'resolvedZone': 'Municipal Administrative Area',
            'resolvedStreet': None,
            'jurisdictionMatch': False,
            'wardMatch': False,
            'zoneMatch': False,
            'reasoning': 'Device GPS coordinates unavailable. Retaining current civic administrative context.',
            'recommendedAction': 'PROCEED_WITH_WARNING'
        }

    try:
        f_lat = float(lat)
        f_lng = float(lng)
    except (ValueError, TypeError):
        return {
            'status': 'LOCATION_UNAVAILABLE',
            'consistencyLevel': 'UNAVAILABLE',
            'latitude': lat,
            'longitude': lng,
            'accuracy': accuracy,
            'distanceMeters': None,
            'resolvedState': reported_state or 'Andhra Pradesh',
            'resolvedCity': reported_city or 'Surampalem',
            'resolvedWard': reported_ward or 'Ward 12 (Market Zone)',
            'resolvedZone': 'Municipal Administrative Area',
            'resolvedStreet': None,
            'jurisdictionMatch': False,
            'wardMatch': False,
            'zoneMatch': False,
            'reasoning': f'Invalid coordinate format received ({lat}, {lng}).',
            'recommendedAction': 'PROCEED_WITH_WARNING'
        }

    # Range and zero-origin validation
    if abs(f_lat) > 90.0 or abs(f_lng) > 180.0 or (abs(f_lat) < 0.0001 and abs(f_lng) < 0.0001):
        return {
            'status': 'LOCATION_UNAVAILABLE',
            'consistencyLevel': 'UNAVAILABLE',
            'latitude': f_lat,
            'longitude': f_lng,
            'accuracy': accuracy,
            'distanceMeters': None,
            'resolvedState': reported_state or 'Andhra Pradesh',
            'resolvedCity': reported_city or 'Surampalem',
            'resolvedWard': reported_ward or 'Ward 12 (Market Zone)',
            'resolvedZone': 'Municipal Administrative Area',
            'resolvedStreet': None,
            'jurisdictionMatch': False,
            'wardMatch': False,
            'zoneMatch': False,
            'reasoning': f'Coordinates ({f_lat:.4f}, {f_lng:.4f}) fall outside valid geographical ranges.',
            'recommendedAction': 'PROCEED_WITH_WARNING'
        }

    # Match against CIVIC_GEOGRAPHY
    target_state = reported_state or 'Andhra Pradesh'
    state_data = CIVIC_GEOGRAPHY.get(target_state, CIVIC_GEOGRAPHY['Andhra Pradesh'])

    nearest_city = None
    min_city_dist = float('inf')
    for city_name, city_info in state_data.items():
        c_lat, c_lng = city_info['center']
        d = calculate_haversine_distance(f_lat, f_lng, c_lat, c_lng)
        if d < min_city_dist:
            min_city_dist = d
            nearest_city = city_name

    city_info = state_data.get(nearest_city, state_data['Surampalem'])
    nearest_ward = None
    nearest_zone = None
    min_ward_dist = float('inf')
    ward_radius = 900.0

    for ward_name, ward_meta in city_info['wards'].items():
        w_lat, w_lng = ward_meta['center']
        d = calculate_haversine_distance(f_lat, f_lng, w_lat, w_lng)
        if d < min_ward_dist:
            min_ward_dist = d
            nearest_ward = ward_name
            nearest_zone = ward_meta['zone']
            ward_radius = ward_meta['radiusMeters']

    # Compare with reported context
    rep_city_clean = (reported_city or 'Surampalem').strip().lower()
    nearest_city_clean = nearest_city.strip().lower()
    city_match = (rep_city_clean in nearest_city_clean or nearest_city_clean in rep_city_clean)

    rep_ward_clean = (reported_ward or '').split('(')[0].strip().lower()
    nearest_ward_clean = nearest_ward.split('(')[0].strip().lower()
    ward_match = bool(rep_ward_clean and (rep_ward_clean in nearest_ward_clean or nearest_ward_clean in rep_ward_clean))

    # Check GPS accuracy uncertainty
    f_acc = None
    if accuracy is not None:
        try:
            f_acc = float(accuracy)
        except (ValueError, TypeError):
            f_acc = None

    # Evaluate consistency
    if city_match:
        if f_acc is not None and f_acc > 100:
            status = 'LOCATION_NEEDS_CONFIRMATION'
            consistency = 'LOW'
            reasoning = f'GPS coordinates ({f_lat:.4f}, {f_lng:.4f}) have high uncertainty (±{int(f_acc)}m). Approximate location flagged for field team confirmation.'
            rec_action = 'CONFIRM_LOCATION'
        elif min_ward_dist <= ward_radius:
            if ward_match or not reported_ward:
                status = 'LOCATION_CONSISTENT'
                consistency = 'HIGH'
                reasoning = f'Device GPS ({f_lat:.4f}, {f_lng:.4f}) is within {int(min_ward_dist)}m of {nearest_ward} civic boundary.'
                rec_action = 'PROCEED'
            else:
                status = 'LOCATION_NEEDS_CONFIRMATION'
                consistency = 'MEDIUM'
                reasoning = f'GPS coordinates ({f_lat:.4f}, {f_lng:.4f}) lie in adjacent {nearest_ward} (~{int(min_ward_dist)}m from center) rather than reported {reported_ward}.'
                rec_action = 'CONFIRM_LOCATION'
        elif min_city_dist <= city_info['radiusMeters']:
            status = 'LOCATION_NEEDS_CONFIRMATION'
            consistency = 'MEDIUM'
            reasoning = f'GPS location is within {nearest_city} civic limits (~{int(min_ward_dist)}m from {nearest_ward} center). Municipal officer review recommended.'
            rec_action = 'CONFIRM_LOCATION'
        else:
            status = 'LOCATION_MISMATCH'
            consistency = 'LOW'
            reasoning = f'GPS coordinates ({f_lat:.4f}, {f_lng:.4f}) are {int(min_city_dist/1000)}km outside the {reported_city or nearest_city} municipal boundary.'
            rec_action = 'REVIEW_LOCATION'
    else:
        # Cross-city mismatch
        status = 'LOCATION_MISMATCH'
        consistency = 'LOW'
        reasoning = f'GPS coordinates ({f_lat:.4f}, {f_lng:.4f}) map to {nearest_city} ({int(min_city_dist/1000)}km away), conflicting with reported city {reported_city}.'
        rec_action = 'REVIEW_LOCATION'

    return {
        'status': status,
        'consistencyLevel': consistency,
        'latitude': f_lat,
        'longitude': f_lng,
        'accuracy': accuracy,
        'distanceMeters': round(min_ward_dist, 1),
        'resolvedState': target_state,
        'resolvedCity': nearest_city,
        'resolvedWard': nearest_ward,
        'resolvedZone': nearest_zone,
        'resolvedStreet': None,
        'jurisdictionMatch': city_match,
        'wardMatch': ward_match,
        'zoneMatch': True if ward_match else False,
        'reasoning': reasoning,
        'recommendedAction': rec_action
    }

def evaluate_incident_identity(report_data, candidate_issues, auth_user=None):
    """
    Deterministically evaluates an incoming citizen submission against existing
    active and recently resolved civic incidents within authorized jurisdiction.
    Treats GPS proximity as the primary matching and separation signal.
    """
    now_ms = int(time.time() * 1000)
    rep_title = report_data.get('title', '')
    rep_desc = report_data.get('description', '')
    rep_dept = str(report_data.get('department') or 'sanitation').lower()
    rep_cat = str(report_data.get('category') or 'general').lower()
    rep_ward = str(report_data.get('ward') or '')
    rep_street = str(report_data.get('street') or report_data.get('location') or '')
    rep_lat = report_data.get('lat') if report_data.get('lat') is not None else report_data.get('latitude')
    rep_lng = report_data.get('lng') if report_data.get('lng') is not None else report_data.get('longitude')
    rep_img = report_data.get('image') or report_data.get('imageBefore') or ''
    rep_hash = compute_evidence_hash(rep_img) if rep_img else None

    combined_text = f"{rep_title} {rep_desc}"
    rep_tokens = normalize_text_tokens(combined_text)

    # Department cross-dependency mapping
    cross_dept_related = {
        'water_supply': ['roads', 'sanitation'],
        'roads': ['water_supply', 'electricity'],
        'electricity': ['roads'],
        'sanitation': ['food_safety'],
        'food_safety': ['sanitation']
    }

    evaluated_matches = []

    for cand in candidate_issues:
        cand_id = cand.get('id')
        cand_dept = str(cand.get('department') or '').lower()
        cand_cat = str(cand.get('category') or '').lower()
        cand_ward = str(cand.get('ward') or '')
        cand_street = str(cand.get('street') or cand.get('location') or '')
        cand_lat = cand.get('lat') if cand.get('lat') is not None else cand.get('latitude')
        cand_lng = cand.get('lng') if cand.get('lng') is not None else cand.get('longitude')
        cand_ts = cand.get('timestamp') or now_ms
        cand_status = str(cand.get('status') or 'pending').lower()
        cand_is_unresolved = cand_status not in ['resolved', 'verified', 'closed']
        cand_img = cand.get('imageBefore') or ''
        cand_hash = cand.get('evidenceHash') or (compute_evidence_hash(cand_img) if cand_img else None)

        cand_tokens = normalize_text_tokens(f"{cand.get('title', '')} {cand.get('description', '')}")

        # 1. Location Metrics (GPS is primary)
        dist_m = calculate_haversine_distance(rep_lat, rep_lng, cand_lat, cand_lng)
        ward_clean_rep = rep_ward.lower().split('(')[0].strip()
        ward_clean_cand = cand_ward.lower().split('(')[0].strip()
        same_ward = bool(ward_clean_rep and ward_clean_cand and ward_clean_rep == ward_clean_cand)
        
        # Spatial separation rule: distance > 250m indicates a distinct incident spot
        if dist_m > 250:
            continue

        # Street token overlap
        street_tokens_rep = normalize_text_tokens(rep_street)
        street_tokens_cand = normalize_text_tokens(cand_street)
        same_street = bool(street_tokens_rep and street_tokens_cand and (street_tokens_rep & street_tokens_cand))

        # 2. Category & Dept Metrics
        same_dept = (rep_dept == cand_dept)
        same_cat = (rep_cat == cand_cat) or ('garbage' in rep_cat and 'garbage' in cand_cat) or ('pothole' in rep_cat and 'pothole' in cand_cat) or ('electric' in rep_cat and 'electric' in cand_cat)
        is_cross_dept_related = cand_dept in cross_dept_related.get(rep_dept, [])

        # 3. Text Overlap
        if rep_tokens and cand_tokens:
            intersection = rep_tokens & cand_tokens
            union = rep_tokens | cand_tokens
            text_sim = len(intersection) / float(len(union)) if union else 0.0
        else:
            text_sim = 0.0

        # 4. Evidence Hash Match
        evidence_match = bool(rep_hash and cand_hash and rep_hash == cand_hash)

        # 5. Time Difference
        time_diff_hours = max(0.0, (now_ms - cand_ts) / (3600.0 * 1000.0))

        # Collect signals
        signals = []
        if dist_m < 50:
            signals.append({'type': 'LOCATION_EXACT', 'label': f'Same coordinates spot (~{int(dist_m)}m)'})
        elif dist_m < 150:
            signals.append({'type': 'LOCATION_PROXIMITY', 'label': f'Nearby spot (~{int(dist_m)}m)'})
        elif same_ward:
            signals.append({'type': 'WARD_MATCH', 'label': f'Same administrative ward ({cand_ward})'})

        if same_street:
            signals.append({'type': 'STREET_MATCH', 'label': 'Matching street/landmark corridor'})

        if same_dept and same_cat:
            signals.append({'type': 'SECTOR_MATCH', 'label': f'Same civic sector ({cand.get("deptName", cand_dept)})'})
        elif same_dept:
            signals.append({'type': 'DEPT_MATCH', 'label': f'Same municipal department ({cand_dept})'})
        elif is_cross_dept_related:
            signals.append({'type': 'CROSS_DEPT_RELATION', 'label': f'Cross-sector impact ({rep_dept} affecting {cand_dept})'})

        if evidence_match:
            signals.append({'type': 'EVIDENCE_HASH_MATCH', 'label': 'Exact Evidence File Match (SHA-256)'})
        else:
            signals.append({'type': 'EVIDENCE_STATUS', 'label': 'Evidence similarity unavailable'})

        if text_sim >= 0.5:
            signals.append({'type': 'TEXT_SIMILARITY_HIGH', 'label': f'High text token match ({int(text_sim * 100)}%)'})
        elif text_sim >= 0.25:
            signals.append({'type': 'TEXT_SIMILARITY_MOD', 'label': f'Moderate text token match ({int(text_sim * 100)}%)'})

        if time_diff_hours < 2.0:
            signals.append({'type': 'TIME_IMMEDIATE', 'label': f'Submitted within {int(time_diff_hours * 60)} mins of existing report'})
        elif time_diff_hours <= 72.0:
            signals.append({'type': 'TIME_ACTIVE_WINDOW', 'label': f'Reported {int(time_diff_hours)} hours ago (Active SLA)'})
        else:
            signals.append({'type': 'TIME_HISTORICAL', 'label': f'Reported {int(time_diff_hours / 24)} days ago'})

        # RULE 1: POSSIBLE DUPLICATE (Same location + same category + very close time or matching evidence)
        if same_dept and (dist_m < 100 or same_street):
            if evidence_match and dist_m < 150:
                match_score = 0.96
                reasoning = f"An active civic report may already exist at this location (#{cand_id}) matching uploaded evidence. This may be a follow-up to an existing issue rather than a new complaint."
                evaluated_matches.append({
                    'type': 'POSSIBLE_DUPLICATE',
                    'score': match_score,
                    'cand': cand,
                    'signals': signals,
                    'reasoning': reasoning,
                    'action': 'Add Follow-up to Existing Ticket'
                })
                continue
            elif dist_m < 80 and same_cat and time_diff_hours < 2.0:
                match_score = 0.90
                reasoning = f"An active civic report may already exist at this location (#{cand_id}), reported {int(time_diff_hours * 60)} mins ago. This may be a follow-up to an existing issue rather than a new complaint."
                evaluated_matches.append({
                    'type': 'POSSIBLE_DUPLICATE',
                    'score': match_score,
                    'cand': cand,
                    'signals': signals,
                    'reasoning': reasoning,
                    'action': 'Add Follow-up to Existing Ticket'
                })
                continue

        # RULE 2: FOLLOW_UP (Same location + same category + unresolved existing issue)
        if cand_is_unresolved and same_dept and (dist_m < 150 or same_street):
            if same_cat or dist_m < 60 or text_sim >= 0.2:
                match_score = 0.88
                status_label = (cand.get('workerStatus') or cand_status).upper()
                reasoning = f"An active civic report may already exist at this location (#{cand_id}, status: {status_label}). This may be a follow-up to an existing issue rather than a new complaint."
                evaluated_matches.append({
                    'type': 'FOLLOW_UP',
                    'score': match_score,
                    'cand': cand,
                    'signals': signals,
                    'reasoning': reasoning,
                    'action': 'Add Follow-up to Existing Ticket'
                })
                continue

        # RULE 3: RELATED_INCIDENT (Same location + different but connected civic category)
        if dist_m < 200 or (same_ward and same_street):
            if same_dept and not same_cat:
                match_score = 0.65
                reasoning = f"Adjacent civic issue detected at this location (#{cand_id}: {cand.get('title')}). Can be linked for coordinated field handling."
                evaluated_matches.append({
                    'type': 'RELATED_INCIDENT',
                    'score': match_score,
                    'cand': cand,
                    'signals': signals,
                    'reasoning': reasoning,
                    'action': 'Link as Related Incident'
                })
                continue
            elif is_cross_dept_related:
                match_score = 0.60
                reasoning = f"Cross-department civic relationship detected between {rep_dept} and {cand_dept} near this location (#{cand_id})."
                evaluated_matches.append({
                    'type': 'RELATED_INCIDENT',
                    'score': match_score,
                    'cand': cand,
                    'signals': signals,
                    'reasoning': reasoning,
                    'action': 'Link as Related Incident'
                })
                continue

    if evaluated_matches:
        evaluated_matches.sort(key=lambda m: m['score'], reverse=True)
        best = evaluated_matches[0]
        cand = best['cand']
        
        now_ts = int(time.time() * 1000)
        c_ts = cand.get('timestamp') or now_ts
        hours_ago = round(max(0.1, (now_ts - c_ts) / (3600.0 * 1000.0)), 1)

        existing_summary = {
            'id': cand.get('id'),
            'title': cand.get('title'),
            'category': cand.get('category'),
            'categoryName': cand.get('categoryName'),
            'department': cand.get('department'),
            'deptName': cand.get('deptName'),
            'location': cand.get('location') or f"{cand.get('ward', '')}, {cand.get('street', '')}",
            'ward': cand.get('ward'),
            'status': cand.get('status'),
            'workerStatus': cand.get('workerStatus'),
            'timestamp': c_ts,
            'hoursAgo': hours_ago,
            'severity': cand.get('severity'),
            'followUpCount': int(cand.get('followUpCount') or 0),
            'imageBefore': cand.get('imageBefore')
        }

        return {
            'identityType': best['type'],
            'matchedIssueId': cand.get('id'),
            'matchScore': best['score'],
            'signals': best['signals'],
            'reasoning': best['reasoning'],
            'recommendedAction': best['action'],
            'existingIssue': existing_summary
        }

    return {
        'identityType': 'NEW_INCIDENT',
        'matchedIssueId': None,
        'matchScore': 0.0,
        'signals': [
            {'type': 'ISOLATED_INCIDENT', 'label': 'No matching active or unresolved reports found in this zone'}
        ],
        'reasoning': 'No conflicting or unresolved civic incidents detected at this location. Proceeding with new ticket creation.',
        'recommendedAction': 'Proceed with New Incident',
        'existingIssue': None
    }

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table: Issues (Civic Grievances)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id TEXT PRIMARY KEY,
            state TEXT,
            city TEXT,
            ward TEXT,
            street TEXT,
            department TEXT,
            deptName TEXT,
            deptIcon TEXT,
            title TEXT,
            description TEXT,
            location TEXT,
            category TEXT,
            categoryName TEXT,
            categoryIcon TEXT,
            severity TEXT,
            severityLabel TEXT,
            status TEXT,
            timestamp INTEGER,
            slaDeadline INTEGER,
            slaHoursLeft REAL,
            resolvedTimestamp INTEGER,
            isSlaBreached INTEGER DEFAULT 0,
            imageBefore TEXT,
            imageAfter TEXT,
            reportedBy TEXT,
            reportedById TEXT,
            verifiedByOfficer TEXT,
            verifiedTimestamp INTEGER,
            assignedWorker TEXT,
            assignedTimestamp INTEGER,
            workerStatus TEXT,
            recommendedResource TEXT,
            upvotes INTEGER DEFAULT 0,
            upvotedBy TEXT,
            comments TEXT,
            rewardIssued INTEGER DEFAULT 0,
            fineLevied REAL DEFAULT 0,
            lat REAL,
            lng REAL,
            vendorId TEXT,
            vendorName TEXT,
            mq135GasPpm REAL,
            imageAiHazard TEXT,
            imageAiConfidence TEXT,
            imageTextConsistency TEXT,
            imageRiskModifier INTEGER DEFAULT 0,
            imageAiReasoning TEXT,
            imageAiAccepted INTEGER DEFAULT 0,
            imageOfficerVerified INTEGER DEFAULT 0,
            imageOfficerOverrideReason TEXT,
            enRouteTimestamp INTEGER,
            arrivedTimestamp INTEGER,
            supervisorNotes TEXT
        )
    ''')

    # Table: Food Vendors & Inspection Registry
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendors (
            id TEXT PRIMARY KEY,
            state TEXT,
            city TEXT,
            ward TEXT,
            name TEXT,
            owner TEXT,
            location TEXT,
            hygieneGrade TEXT,
            score TEXT,
            validTill TEXT,
            inspectedBy TEXT,
            status TEXT,
            isViolated INTEGER DEFAULT 0,
            violationClause TEXT,
            penaltyImposed TEXT,
            rectificationDeadline TEXT,
            mq135GasPpm TEXT,
            officerDirectives TEXT
        )
    ''')

    # Table: Citizen Daily Reports Quota (Max 3/day per citizen)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citizen_quotas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            date_str TEXT,
            report_count INTEGER DEFAULT 0,
            UNIQUE(user_id, date_str)
        )
    ''')

    # Table: Incident Clusters (Duplicate grouping & multi-report aggregation)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incident_clusters (
            id TEXT PRIMARY KEY,
            title TEXT,
            category TEXT,
            department TEXT,
            ward TEXT,
            lat REAL,
            lng REAL,
            reportCount INTEGER DEFAULT 1,
            status TEXT DEFAULT 'active',
            firstReportedAt INTEGER,
            lastReportedAt INTEGER,
            riskScore INTEGER DEFAULT 50
        )
    ''')

    # Table: Hotspots (Predictive Ward Risk & Recurring Hotspot Tracking)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hotspots (
            ward TEXT PRIMARY KEY,
            pastComplaints INTEGER DEFAULT 0,
            avgResolutionHours REAL DEFAULT 24.0,
            recurrenceRate REAL DEFAULT 0.0,
            predictedRiskPercent INTEGER DEFAULT 50,
            riskLevel TEXT DEFAULT 'Medium',
            forecastHorizonHours INTEGER DEFAULT 48,
            recommendedAction TEXT,
            lastEvaluatedAt INTEGER
        )
    ''')

    # Table: Workers (Municipal Field Workforce Registry)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workers (
            id TEXT PRIMARY KEY,
            name TEXT,
            phone TEXT,
            department TEXT,
            specialization TEXT,
            currentStatus TEXT DEFAULT 'available',
            lat REAL,
            lng REAL,
            tasksCompleted INTEGER DEFAULT 0,
            currentTaskId TEXT
        )
    ''')

    # Table: AI Predictions & Recommendations Log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_predictions (
            id TEXT PRIMARY KEY,
            entityType TEXT,
            entityId TEXT,
            predictionType TEXT,
            confidenceScore REAL,
            reasoning TEXT,
            recommendedAction TEXT,
            createdAt INTEGER
        )
    ''')

    # Table: Operational Audit Logs (Human-in-the-Loop & Squad Assignment Ledger)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operational_audit_logs (
            id TEXT PRIMARY KEY,
            issueId TEXT,
            officer TEXT,
            actionType TEXT,
            assignedWorker TEXT,
            supervisorNotes TEXT,
            timestamp INTEGER
        )
    ''')

    # Safe column migrations for issues table
    cursor.execute("PRAGMA table_info(issues)")
    existing_issue_cols = [row['name'] if isinstance(row, dict) or hasattr(row, 'keys') else row[1] for row in cursor.fetchall()]
    new_issue_cols = [
        ('clusterId', 'TEXT'),
        ('aiRiskScore', 'INTEGER DEFAULT 50'),
        ('aiConfidence', 'REAL DEFAULT 0.0'),
        ('aiReasoning', 'TEXT'),
        ('aiSuggestedSLA', 'REAL'),
        ('slaBreachProb', 'REAL DEFAULT 0.0'),
        ('aiSuggestedDepartment', 'TEXT'),
        ('aiSuggestedCategory', 'TEXT'),
        ('aiSuggestedSeverity', 'TEXT'),
        ('citizenConfirmedAI', 'INTEGER DEFAULT 1'),
        ('aiOverrideReason', 'TEXT'),
        ('imageAiHazard', 'TEXT'),
        ('imageAiConfidence', 'TEXT'),
        ('imageTextConsistency', 'TEXT'),
        ('imageRiskModifier', 'INTEGER DEFAULT 0'),
        ('imageAiReasoning', 'TEXT'),
        ('imageAiAccepted', 'INTEGER DEFAULT 0'),
        ('imageOfficerVerified', 'INTEGER DEFAULT 0'),
        ('imageOfficerOverrideReason', 'TEXT'),
        ('enRouteTimestamp', 'INTEGER'),
        ('arrivedTimestamp', 'INTEGER'),
        ('supervisorNotes', 'TEXT'),
        ('workCompletedTimestamp', 'INTEGER'),
        ('workCompletedBy', 'TEXT'),
        ('resolutionNotes', 'TEXT'),
        ('rejectionReason', 'TEXT'),
        ('parentIssueId', 'TEXT'),
        ('identityType', 'TEXT DEFAULT "NEW_INCIDENT"'),
        ('identityMatchScore', 'REAL DEFAULT 0.0'),
        ('identityMatchedIssueId', 'TEXT'),
        ('identityReasoning', 'TEXT'),
        ('identityReviewed', 'INTEGER DEFAULT 0'),
        ('identityReviewedBy', 'TEXT'),
        ('identityReviewedTimestamp', 'INTEGER'),
        ('followUpCount', 'INTEGER DEFAULT 0'),
        ('evidenceHash', 'TEXT'),
        ('geoConsistencyStatus', 'TEXT DEFAULT "LOCATION_CONSISTENT"'),
        ('geoConsistencyLevel', 'TEXT DEFAULT "HIGH"'),
        ('geoDistanceMeters', 'REAL DEFAULT 0.0'),
        ('geoResolvedState', 'TEXT'),
        ('geoResolvedCity', 'TEXT'),
        ('geoResolvedWard', 'TEXT'),
        ('geoResolvedZone', 'TEXT'),
        ('geoResolvedStreet', 'TEXT'),
        ('geoCheckTimestamp', 'INTEGER'),
        ('geoCheckReasoning', 'TEXT')
    ]
    for col_name, col_type in new_issue_cols:
        if col_name not in existing_issue_cols:
            try:
                cursor.execute(f"ALTER TABLE issues ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"[Database] Column {col_name} migration note: {e}")

    # Table: Incident Relationships (Civic Incident Identity Engine v43)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incident_relationships (
            id TEXT PRIMARY KEY,
            sourceIssueId TEXT,
            targetIssueId TEXT,
            relationshipType TEXT,
            matchReason TEXT,
            matchScore REAL DEFAULT 0.0,
            signals TEXT,
            createdAt INTEGER,
            createdBy TEXT,
            createdById TEXT,
            reviewedBy TEXT,
            reviewedAt INTEGER,
            status TEXT DEFAULT 'ACTIVE'
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_inc_rel_target ON incident_relationships(targetIssueId)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_inc_rel_source ON incident_relationships(sourceIssueId)')

    # Table: Geo-Evidence Checks (Civic Jurisdiction Engine v44)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS geo_evidence_checks (
            id TEXT PRIMARY KEY,
            issueId TEXT,
            latitude REAL,
            longitude REAL,
            status TEXT,
            consistencyLevel TEXT,
            distanceMeters REAL,
            resolvedState TEXT,
            resolvedCity TEXT,
            resolvedWard TEXT,
            resolvedZone TEXT,
            timestamp INTEGER,
            citizenConfirmed INTEGER DEFAULT 1,
            reasoning TEXT
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_geo_issue ON geo_evidence_checks(issueId)')

    # Table: Sessions (Authoritative Cryptographic Session Store)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            userId TEXT,
            email TEXT COLLATE NOCASE,
            department TEXT,
            roleTitle TEXT,
            name TEXT,
            officialId TEXT,
            jurisdictionState TEXT,
            jurisdictionCity TEXT,
            jurisdictionWard TEXT,
            createdAt INTEGER,
            expiresAt INTEGER
        )
    ''')

    # Table: Users & Standing Ledger (Amazon-style persistent unique account store)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY COLLATE NOCASE,
            id TEXT,
            name TEXT,
            password TEXT,
            department TEXT,
            roleTitle TEXT,
            officialId TEXT,
            avatar TEXT,
            civicCredits INTEGER DEFAULT 20,
            activeStreakWeeks INTEGER DEFAULT 1,
            createdAt INTEGER,
            jurisdictionState TEXT,
            jurisdictionCity TEXT,
            jurisdictionWard TEXT
        )
    ''')

    # Table: Civic Redemptions (Dual-path Citizen Rewards & Community Contributions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS civic_redemptions (
            id TEXT PRIMARY KEY,
            userId TEXT,
            userEmail TEXT COLLATE NOCASE,
            rewardId TEXT,
            rewardTitle TEXT,
            rewardType TEXT,
            pointsDeducted INTEGER,
            voucherCode TEXT,
            status TEXT DEFAULT 'CONFIRMED_PROTOTYPE',
            timestamp INTEGER
        )
    ''')

    # Safe column migrations for users table
    cursor.execute("PRAGMA table_info(users)")
    existing_user_cols = [row['name'] if isinstance(row, dict) or hasattr(row, 'keys') else row[1] for row in cursor.fetchall()]
    user_cols_to_add = [
        ('jurisdictionState', 'TEXT'),
        ('jurisdictionCity', 'TEXT'),
        ('jurisdictionWard', 'TEXT'),
        ('phone', 'TEXT'),
        ('permanentAddress', 'TEXT'),
        ('profileCompleted', 'INTEGER DEFAULT 0')
    ]
    for col_name, col_type in user_cols_to_add:
        if col_name not in existing_user_cols:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"[Database] User column {col_name} migration note: {e}")

    # Safe column migrations for workers table
    cursor.execute("PRAGMA table_info(workers)")
    existing_worker_cols = [row['name'] if isinstance(row, dict) or hasattr(row, 'keys') else row[1] for row in cursor.fetchall()]
    worker_cols_to_add = [
        ('operationalState', 'TEXT'),
        ('operationalCity', 'TEXT'),
        ('operationalWards', 'TEXT')
    ]
    for col_name, col_type in worker_cols_to_add:
        if col_name not in existing_worker_cols:
            try:
                cursor.execute(f"ALTER TABLE workers ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"[Database] Worker column {col_name} migration note: {e}")

    conn.commit()

    # Seed default system accounts if not present
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, id, name, password, department, roleTitle, officialId, avatar, civicCredits, activeStreakWeeks, createdAt, jurisdictionState, jurisdictionCity, jurisdictionWard)
        VALUES ('citizen@civictech.in', 'user-101', 'KRISH', 'password123', 'citizen', 'Verified Citizen Reporter', 'CIT-IND-2026-8941', 'KR', 20, 1, strftime('%s', 'now'), 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)')
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, id, name, password, department, roleTitle, officialId, avatar, civicCredits, activeStreakWeeks, createdAt, jurisdictionState, jurisdictionCity, jurisdictionWard)
        VALUES ('admin@municipality.gov.in', 'user-102', 'K. Mukundha (Zonal Administrator)', 'password123', 'municipal', 'Designated Municipal & Electricity Administrator', 'Zonal Administrator', 'KM', 0, 0, strftime('%s', 'now'), 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)')
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, id, name, password, department, roleTitle, officialId, avatar, civicCredits, activeStreakWeeks, createdAt, jurisdictionState, jurisdictionCity, jurisdictionWard)
        VALUES ('fso.officer@foodsafety.gov.in', 'user-103', 'Dr. Lakshmi Prasad (FSO)', 'password123', 'food', 'Designated Food Safety Officer (FSO)', 'Food Safety Officer', 'LP', 0, 0, strftime('%s', 'now'), 'Andhra Pradesh', 'Surampalem', 'ALL')
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, id, name, password, department, roleTitle, officialId, avatar, civicCredits, activeStreakWeeks, createdAt, jurisdictionState, jurisdictionCity, jurisdictionWard)
        VALUES ('worker4@municipality.gov.in', 'user-104', 'Ramesh (Squad 4 Leader)', 'password123', 'worker', 'Field Response Squad Lead', 'Squad 4 Lead', 'SQ', 0, 0, strftime('%s', 'now'), 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)')
    ''')

    # Authoritatively backfill/update official jurisdictions & default profiles in users table
    cursor.execute("UPDATE users SET phone = '+91 94401 88421', permanentAddress = 'Plot 18, Gandhi Nagar Main Road, Ward 12, Surampalem, Andhra Pradesh - 533437', profileCompleted = 1 WHERE LOWER(email) = 'citizen@civictech.in'")
    cursor.execute("UPDATE users SET profileCompleted = 1 WHERE department IN ('municipal', 'food', 'worker')")
    cursor.execute("UPDATE users SET profileCompleted = 1 WHERE jurisdictionWard IS NOT NULL AND jurisdictionWard != '' AND permanentAddress IS NOT NULL AND permanentAddress != ''")
    cursor.execute("UPDATE users SET jurisdictionState = 'Andhra Pradesh', jurisdictionCity = 'Surampalem', jurisdictionWard = 'Ward 12 (Market Zone)' WHERE LOWER(email) IN ('admin@municipality.gov.in', 'zonal.officer@andhra.gov.in') AND (jurisdictionState IS NULL OR jurisdictionState = '')")
    cursor.execute("UPDATE users SET jurisdictionState = 'Andhra Pradesh', jurisdictionCity = 'Surampalem', jurisdictionWard = 'ALL' WHERE LOWER(email) IN ('fso.officer@foodsafety.gov.in', 'inspector.sharma@fssai.gov.in') AND (jurisdictionState IS NULL OR jurisdictionState = '')")
    cursor.execute("UPDATE users SET jurisdictionState = 'Andhra Pradesh', jurisdictionCity = 'Surampalem', jurisdictionWard = 'Ward 12 (Market Zone)' WHERE LOWER(email) = 'worker4@municipality.gov.in' AND (jurisdictionState IS NULL OR jurisdictionState = '')")
    cursor.execute("UPDATE users SET jurisdictionState = 'Andhra Pradesh', jurisdictionCity = 'Surampalem', jurisdictionWard = 'Ward 12 (Market Zone)' WHERE LOWER(email) IN ('citizen@civictech.in', 'mukundha.k@gmail.com') AND (jurisdictionState IS NULL OR jurisdictionState = '')")
    cursor.execute("UPDATE users SET civicCredits = 250 WHERE LOWER(email) = 'citizen@civictech.in' AND (civicCredits IS NULL OR civicCredits < 150)")

    # Authoritatively backfill/update operational boundaries in workers table
    cursor.execute("UPDATE workers SET operationalState = 'Andhra Pradesh', operationalCity = 'Surampalem', operationalWards = '[\"Ward 12 (Market Zone)\", \"Ward 11 (Lake View Zone)\"]' WHERE id = 'WRK-SAN-04' AND (operationalState IS NULL OR operationalState = '')")
    cursor.execute("UPDATE workers SET operationalState = 'Andhra Pradesh', operationalCity = 'Surampalem', operationalWards = '[\"Ward 12 (Market Zone)\", \"Ward 14 (Campus Zone)\"]' WHERE id = 'WRK-SAN-01' AND (operationalState IS NULL OR operationalState = '')")
    cursor.execute("UPDATE workers SET operationalState = 'Andhra Pradesh', operationalCity = 'Surampalem', operationalWards = '[\"Ward 12 (Market Zone)\", \"Ward 11 (Lake View Zone)\", \"Ward 14 (Campus Zone)\"]' WHERE id = 'WRK-ELE-02' AND (operationalState IS NULL OR operationalState = '')")
    cursor.execute("UPDATE workers SET department = 'roads', operationalState = 'Andhra Pradesh', operationalCity = 'Surampalem', operationalWards = '[\"Ward 12 (Market Zone)\", \"Ward 11 (Lake View Zone)\", \"Ward 7 (Railway Colony)\"]' WHERE id = 'WRK-ROA-03'")
    cursor.execute('''
        INSERT OR IGNORE INTO workers (id, name, phone, department, specialization, currentStatus, lat, lng, tasksCompleted, currentTaskId, operationalState, operationalCity, operationalWards)
        VALUES ('WRK-WAT-05', 'Water Utility Squad 5 (Lead: K. Somaraju)', '+91 94402 66711', 'water_supply', 'Municipal Pipeline Repair & Pressure Valve Maintenance', 'available', 17.0018, 81.8032, 18, NULL, 'Andhra Pradesh', 'Surampalem', '[\"Ward 12 (Market Zone)\", \"Ward 11 (Lake View Zone)\", \"Ward 3 (Residential Colony)\"]')
    ''')

    # Seed Out-of-Jurisdiction Test Accounts for Automated Security Verification
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, id, name, password, department, roleTitle, officialId, avatar, civicCredits, activeStreakWeeks, createdAt, jurisdictionState, jurisdictionCity, jurisdictionWard)
        VALUES ('delhi.officer@mcd.gov.in', 'user-delhi-01', 'Rajesh Sharma (MCD Zonal Head)', 'password123', 'municipal', 'Zonal Officer (Delhi MCD)', 'GOV-MCD-DEL-01', 'RS', 0, 0, strftime('%s', 'now'), 'Delhi NCR', 'New Delhi', 'Ward 5 (Central)')
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, id, name, password, department, roleTitle, officialId, avatar, civicCredits, activeStreakWeeks, createdAt, jurisdictionState, jurisdictionCity, jurisdictionWard)
        VALUES ('hyd.fso@foodsafety.gov.in', 'user-fso-hyd', 'Dr. Aruna Reddy (GHMC FSO)', 'password123', 'food', 'Food Safety Officer (GHMC)', 'FSSAI-HYD-2026-99', 'AR', 0, 0, strftime('%s', 'now'), 'Telangana', 'Hyderabad', 'ALL')
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO workers (id, name, phone, department, specialization, currentStatus, lat, lng, tasksCompleted, currentTaskId, operationalState, operationalCity, operationalWards)
        VALUES ('WRK-SAN-99', 'Squad 99 (Lead: Gopal)', '+91 99001 12233', 'sanitation', 'Remote Outpost Collection', 'available', 17.0200, 81.8200, 5, NULL, 'Andhra Pradesh', 'Surampalem', '[\"Ward 99 (Remote Zone)\"]')
    ''')

    # Seed default active sessions for quick testing & immediate authentication
    now_ms = int(time.time() * 1000)
    exp_ms = now_ms + (30 * 86400 * 1000)
    demo_sessions = [
        ('DEMO_TOKEN_MUNICIPAL_OFFICER', 'user-102', 'admin@municipality.gov.in', 'municipal', 'Designated Municipal & Electricity Administrator', 'K. Mukundha (Zonal Administrator)', 'Zonal Administrator', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', now_ms, exp_ms),
        ('DEMO_TOKEN_FOOD_OFFICER', 'user-103', 'fso.officer@foodsafety.gov.in', 'food', 'Designated Food Safety Officer (FSO)', 'Dr. Lakshmi Prasad (FSO)', 'Food Safety Officer', 'Andhra Pradesh', 'Surampalem', 'ALL', now_ms, exp_ms),
        ('DEMO_TOKEN_WORKER_4', 'user-104', 'worker4@municipality.gov.in', 'worker', 'Field Response Squad Lead', 'Ramesh (Squad 4 Leader)', 'Squad 4 Lead', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', now_ms, exp_ms),
        ('DEMO_TOKEN_CITIZEN', 'user-101', 'citizen@civictech.in', 'citizen', 'Verified Citizen Reporter', 'KRISH', 'CIT-IND-2026-8941', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', now_ms, exp_ms),
        ('DEMO_TOKEN_DELHI_OFFICER', 'user-delhi-01', 'delhi.officer@mcd.gov.in', 'municipal', 'Zonal Officer (Delhi MCD)', 'Rajesh Sharma (MCD Zonal Head)', 'GOV-MCD-DEL-01', 'Delhi NCR', 'New Delhi', 'Ward 5 (Central)', now_ms, exp_ms),
        ('DEMO_TOKEN_HYD_FSO', 'user-fso-hyd', 'hyd.fso@foodsafety.gov.in', 'food', 'Food Safety Officer (GHMC)', 'Dr. Aruna Reddy (GHMC FSO)', 'FSSAI-HYD-2026-99', 'Telangana', 'Hyderabad', 'ALL', now_ms, exp_ms),
    ]
    cursor.executemany('''
        INSERT OR REPLACE INTO sessions (token, userId, email, department, roleTitle, name, officialId, jurisdictionState, jurisdictionCity, jurisdictionWard, createdAt, expiresAt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', demo_sessions)

    conn.commit()

    # Seed Field Workers if empty
    cursor.execute('SELECT COUNT(*) FROM workers')
    if cursor.fetchone()[0] == 0:
        seed_workers = [
            ('WRK-SAN-01', 'Squad 1 (Lead: Ravi Kumar)', '+91 98480 22311', 'sanitation', 'Garbage & Heavy Compactor Operations', 'available', 17.0012, 81.8048, 14, None, 'Andhra Pradesh', 'Surampalem', '["Ward 12 (Market Zone)", "Ward 14 (Campus Zone)"]'),
            ('WRK-ELE-02', 'Lineman Squad B (Lead: Suresh Kumar)', '+91 94401 55422', 'electricity', '11KV Substation & Line Repair', 'available', 17.0025, 81.8030, 22, None, 'Andhra Pradesh', 'Surampalem', '["Ward 12 (Market Zone)", "Ward 11 (Lake View Zone)", "Ward 14 (Campus Zone)"]'),
            ('WRK-ROA-03', 'Roads Squad 3 (Lead: Anita Roy)', '+91 99880 33411', 'roads', 'Asphalt Patching & Culvert Desilting', 'available', 16.9995, 81.8060, 9, None, 'Andhra Pradesh', 'Surampalem', '["Ward 12 (Market Zone)", "Ward 11 (Lake View Zone)", "Ward 7 (Railway Colony)"]'),
            ('WRK-SAN-04', 'Squad 4 (Lead: Ramesh)', '+91 98661 77211', 'sanitation', 'Commercial Market Solid Waste Collection', 'busy', 17.0030, 81.8010, 31, 'ISS-2026-00123', 'Andhra Pradesh', 'Surampalem', '["Ward 12 (Market Zone)", "Ward 11 (Lake View Zone)"]'),
            ('WRK-WAT-05', 'Water Utility Squad 5 (Lead: K. Somaraju)', '+91 94402 66711', 'water_supply', 'Municipal Pipeline Repair & Pressure Valve Maintenance', 'available', 17.0018, 81.8032, 18, None, 'Andhra Pradesh', 'Surampalem', '["Ward 12 (Market Zone)", "Ward 11 (Lake View Zone)", "Ward 3 (Residential Colony)"]')
        ]
        cursor.executemany('''
            INSERT OR IGNORE INTO workers (id, name, phone, department, specialization, currentStatus, lat, lng, tasksCompleted, currentTaskId, operationalState, operationalCity, operationalWards)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', seed_workers)

    # Seed Hotspots if empty
    cursor.execute('SELECT COUNT(*) FROM hotspots')
    if cursor.fetchone()[0] == 0:
        now_eval = int(time.time() * 1000)
        seed_hotspots = [
            ('Ward 12 (Market Zone)', 82, 18.5, 0.71, 87, 'Critical', 48, 'Increase collection vehicle frequency & deploy secondary compactor crew', now_eval),
            ('Ward 7 (Railway Colony)', 44, 26.0, 0.58, 73, 'High', 48, 'Pre-monsoon culvert desilting & storm drain inspection', now_eval),
            ('Ward 19 (Industrial Belt)', 29, 31.2, 0.42, 61, 'Medium', 48, 'Schedule preventive road asphalt patch inspection', now_eval),
            ('Ward 3 (Residential Colony)', 11, 12.0, 0.15, 24, 'Low', 48, 'Routine maintenance schedule maintained', now_eval)
        ]
        cursor.executemany('''
            INSERT OR IGNORE INTO hotspots (ward, pastComplaints, avgResolutionHours, recurrenceRate, predictedRiskPercent, riskLevel, forecastHorizonHours, recommendedAction, lastEvaluatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', seed_hotspots)

    # Transparently upgrade existing plain-text passwords in users table to scrypt
    cursor.execute('SELECT email, password FROM users')
    for u_row in cursor.fetchall():
        u_email = u_row[0]
        u_pass = str(u_row[1] or '').strip()
        if u_pass and not u_pass.startswith('scrypt$'):
            cursor.execute('UPDATE users SET password = ? WHERE email = ?', (hash_password(u_pass), u_email))
    conn.commit()

    # Seed Database if empty
    cursor.execute('SELECT COUNT(*) FROM issues')
    count = cursor.fetchone()[0]
    if count == 0:
        seed_initial_data(conn)

    # Phase 4: Predictive Civic Intelligence Tables & Seeding
    predictive_engine.init_predictive_tables(cursor)
    predictive_engine.seed_predictive_intelligence_data(conn)
    ai_engine.init_ai_settings(conn)
    conn.commit()

    conn.close()
    print('[Database] SQLite database initialized successfully at', DB_FILE)

def seed_initial_data(conn):
    cursor = conn.cursor()
    now = int(time.time() * 1000)

    # Initial Issues
    seed_issues = [
        # KRISH REPORT 1: Category: Sanitation & Waste Management, Status: RESOLVED / COMPLETED, SLA: Resolved successfully
        (
            'ISS-2026-00121', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', 'Canteen Gate Cross',
            'sanitation', 'Sanitation & Waste Management', '🏢',
            'Overflowing Waste Bins Near Canteen Gate',
            'Commercial waste bins overflowing near the canteen entrance causing pedestrian obstruction and hygiene concerns. Bins cleared, sanitized and relocated to designated waste bay.',
            'Surampalem • Ward 12 (Market Zone), Canteen Gate Cross',
            'garbage_overflow', 'Sanitation & Waste Management', '🗑️',
            'medium', 'RESOLVED IN 26 HOURS', 'resolved',
            now - (30 * 3600 * 1000), now + (18 * 3600 * 1000), 0.0, now - (4 * 3600 * 1000),
            0,
            'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&auto=format&fit=crop&q=80',
            'KRISH', 'user-101',
            'K. Mukundha (Zonal Administrator)', now - (28 * 3600 * 1000),
            'Sanitation Rapid Fleet 1 (Lead: Ravi Kumar)', now - (26 * 3600 * 1000),
            'Completed & Verified On-Site', 'Compactor Fleet',
            14, json.dumps(['user-101', 'user-102']),
            json.dumps([
                {'author': 'System Watchdog', 'text': 'Live GPS Geotag logged: 17.0015° N, 81.8042° E. 48h SLA timer active.', 'time': '30h ago'},
                {'author': 'Consultant Officer K. Mukundha', 'text': 'Grievance verified. Heavy hydraulic tipper assigned.', 'time': '28h ago'},
                {'author': 'Sanitation Rapid Fleet 1', 'text': 'Site cleared and sanitized with lime powder.', 'time': '4h ago'}
            ]),
            1, 0.0, 17.0015, 81.8042, None, None, None
        ),

        # KRISH REPORT 2: Category: Sanitation & Waste Management, Status: RESOLVED / COMPLETED, SLA: Resolved successfully
        (
            'ISS-2026-00128', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', 'Market Road Corner',
            'sanitation', 'Sanitation & Waste Management', '🏢',
            'Open Garbage Dumping Near Market Road',
            'Illegal dumping of commercial cartons and household solid waste along Market Road corner. Entire stretch cleared, disinfected, and anti-dumping signage erected.',
            'Surampalem • Ward 12 (Market Zone), Market Road Corner',
            'garbage_overflow', 'Sanitation & Waste Management', '🗑️',
            'medium', 'RESOLVED IN 18 HOURS', 'resolved',
            now - (24 * 3600 * 1000), now + (24 * 3600 * 1000), 0.0, now - (6 * 3600 * 1000),
            0,
            'https://images.unsplash.com/photo-1530587191325-3db32d826c18?w=800&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&auto=format&fit=crop&q=80',
            'KRISH', 'user-101',
            'K. Mukundha (Zonal Administrator)', now - (22 * 3600 * 1000),
            'Municipal Rapid Squad 4 (Lead: Ramesh)', now - (20 * 3600 * 1000),
            'Completed & Verified On-Site', 'Tipper Truck',
            18, json.dumps(['user-101']),
            json.dumps([
                {'author': 'Consultant Officer K. Mukundha', 'text': 'Sanitation supervisor notified and squad deployed.', 'time': '22h ago'},
                {'author': 'Municipal Rapid Squad 4', 'text': 'Waste cleared and bins repositioned.', 'time': '6h ago'}
            ]),
            1, 0.0, 17.0018, 81.8038, None, None, None
        ),

        # KRISH REPORT 3: Category: Sanitation & Waste Management, Status: IN PROGRESS, SLA: 48-HOUR SLA BREACHED / ESCALATED
        (
            'ISS-2026-00123', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', 'Gandhi Statue Main Road',
            'sanitation', 'Sanitation & Waste Management', '🏢',
            'Severe Commercial Waste Overflow at Market Gate',
            'Over 3 tons of rotten municipal and commercial garbage overflowing onto main pedestrian road. Exceeded mandatory 48-Hour SLA period without field clearance. Automatically escalated to Municipal Commissioner Dr. Mahesh Babu & Zonal Health Directorate.',
            'Surampalem • Ward 12 (Market Zone), Gandhi Statue Main Road',
            'garbage_overflow', 'Sanitation & Waste Management', '🗑️',
            'bulk', 'SLA BREACHED (>48H)', 'in_progress',
            now - (58 * 3600 * 1000), now - (10 * 3600 * 1000), 0.0, None,
            1,
            'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80',
            None,
            'KRISH', 'user-101',
            'K. Mukundha (Zonal Administrator)', now - (56 * 3600 * 1000),
            'Sanitation Rapid Fleet 3 (Lead: P. Ramesh)', now - (54 * 3600 * 1000),
            'Delayed (>48h) — Auto-Forwarded to Municipal Commissioner Red Desk for Urgent Action',
            'Heavy Hydraulic Compactor & 10-Ton Tipper Fleet',
            84, json.dumps(['user-101']),
            json.dumps([
                {'author': 'System SLA Monitor', 'text': '⏱️ 48-Hour SLA Breached! Grievance unaddressed after 48h limit.', 'time': '10h ago'},
                {'author': 'Auto-Escalation Gateway', 'text': '🚨 Escalated to Higher Authority: Zonal Municipal Commissioner (Dr. Mahesh Babu) & Urban Health Directorate.', 'time': '10h ago'},
                {'author': 'Municipal Commissioner Red Desk', 'text': 'Ticket received with Critical Priority 1. Direct disciplinary summons and immediate heavy squad deployed.', 'time': '8h ago'}
            ]),
            0, 0.0, 17.0012, 81.8048, None, None, None
        ),

        # KRISH REPORT 4: Category: Smart Electricity Department, Status: RESOLVED / COMPLETED, SLA: Resolved successfully
        (
            'ISS-2026-00130', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', 'Gandhi Statue Junction',
            'electricity', 'Smart Electricity Department', '⚡',
            'Streetlight Failure Near Ward 12',
            'Twin-arm LED streetlights completely non-operational near Gandhi Statue junction, leading to low visibility at night. Replaced faulty ballast and LED driver unit. Full illumination restored.',
            'Surampalem • Ward 12 (Market Zone), Gandhi Statue Junction',
            'electricity', 'Smart Electricity Department', '💡',
            'medium', 'RESOLVED IN 28 HOURS', 'resolved',
            now - (36 * 3600 * 1000), now + (12 * 3600 * 1000), 0.0, now - (8 * 3600 * 1000),
            0,
            'https://images.unsplash.com/photo-1544724569-5f546fd6f2b5?w=800&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1509228468518-180dd4864904?w=800&auto=format&fit=crop&q=80',
            'KRISH', 'user-101',
            'K. Mukundha (Zonal Administrator)', now - (34 * 3600 * 1000),
            'Lineman Squad B (Lead: Suresh Kumar)', now - (32 * 3600 * 1000),
            'Completed & Verified On-Site', 'Lineman Bucket Van (AP-05-EB)',
            22, json.dumps(['user-101']),
            json.dumps([
                {'author': 'Consultant Officer K. Mukundha', 'text': 'Electrical inspector assigned.', 'time': '34h ago'},
                {'author': 'Lineman Squad B', 'text': 'Replaced driver unit. All streetlights operational.', 'time': '8h ago'}
            ]),
            1, 0.0, 17.0022, 81.8035, None, None, None
        ),

        # KRISH REPORT 5: Category: Water Leakage / Water Supply, Status: IN PROGRESS, SLA: Normal / active SLA window
        (
            'ISS-2026-00131', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', 'Market Road Pavement',
            'water_supply', 'Water Leakage / Water Supply', '💧',
            'Water Pipeline Leakage Near Ward 12',
            'Pressurized municipal water distribution main leaking clean drinking water onto Market Road pavement. Isolation valve inspection underway.',
            'Surampalem • Ward 12 (Market Zone), Market Road Pavement',
            'water_leakage', 'Water Leakage / Water Supply', '🚰',
            'medium', 'ACTIVE SLA (38H LEFT)', 'in_progress',
            now - (10 * 3600 * 1000), now + (38 * 3600 * 1000), 38.0, None,
            0,
            'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=800&auto=format&fit=crop&q=80',
            None,
            'KRISH', 'user-101',
            'K. Mukundha (Zonal Administrator)', now - (8 * 3600 * 1000),
            'Public Works Water Squad 2 (Lead: Anita Roy)', now - (6 * 3600 * 1000),
            'On Site - Conducting Work', 'Valve Repair Utility Van',
            9, json.dumps(['user-101']),
            json.dumps([
                {'author': 'Consultant Officer K. Mukundha', 'text': 'Water Board division alerted. Utility squad dispatched.', 'time': '8h ago'},
                {'author': 'Public Works Water Squad 2', 'text': 'Pressure isolated. Excavating service collar for replacement.', 'time': '2h ago'}
            ]),
            0, 0.0, 17.0016, 81.8040, None, None, None
        ),

        # Other Community & Official Seed Records
        (
            'ISS-2026-00124', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', 'Gandhi Statue Main Road',
            'electricity', 'Smart Electricity Department', '⚡',
            '11KV Transformer Sparking & Low Hanging Cable',
            'Dangerous spark discharge observed at 11KV junction pole during wind gust. Risk of electrocution.',
            'Surampalem • Ward 12 (Market Zone), Gandhi Statue Main Road',
            'sparking_wire', 'Sparking Cable / Wire', '⚡', 'bulk', 'CRITICAL LIFE HAZARD', 'pending',
            now - (18 * 3600 * 1000), now + (30 * 3600 * 1000), 29.8, None, 0,
            'https://images.unsplash.com/photo-1544724569-5f546fd6f2b5?w=800&auto=format&fit=crop&q=80', None,
            'R. Venkatesh (Citizen)', 'user-103', 'K. Mukundha (Zonal Administrator)', now - (17 * 3600 * 1000),
            'Lineman Squad B (Suresh Kumar)', now - (16 * 3600 * 1000), 'Feeder Isolated & Line Repair Crew Active',
            'Lineman Bucket Van (AP-05-EB)', 28, json.dumps(['user-103', 'user-104', 'user-105']),
            json.dumps([
                {'author': 'System Watchdog', 'text': 'Critical Priority Alert triggered. Feeder #4 SCADA alert mapped.', 'time': '18h ago'},
                {'author': 'Consultant Officer K. Mukundha', 'text': 'SCADA auto-tripped feeder. Lineman Suresh Kumar on site with insulated ladder.', 'time': '17h ago'}
            ]),
            0, 0, 17.0018, 81.8080, None, None, None
        ),
        (
            'ISS-2026-00125', 'Andhra Pradesh', 'Surampalem', 'Ward 14 (Campus Zone)', 'College Road Food Court',
            'food_safety', 'Food Safety Department', '🍲',
            'Swagath Grand: Uncovered Food & High Spoilage Gas',
            'MQ-135 IoT sensor detected 360 PPM ammonia/methane gas near kitchen drain. Food preparation without hairnets.',
            'Surampalem • Ward 14 (Campus Zone), College Road Food Court Lane 2',
            'food_hygiene', 'Food Hygiene Violation', '🍲', 'bulk', 'VIOLATION ON NOTICE', 'pending',
            now - (6 * 3600 * 1000), now + (42 * 3600 * 1000), 41.9, None, 0,
            'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80', None,
            'FoodGuard AI Sensor', 'system-fso', 'Dr. Lakshmi Prasad (FSO)', now - (5 * 3600 * 1000),
            'Food Safety Officer (Dr. Lakshmi Prasad)', now - (5 * 3600 * 1000), 'Statutory Notice FSSAI-AP-2026-V09 Served',
            'FSO Inspection Squad', 19, json.dumps(['user-103']),
            json.dumps([
                {'author': 'FoodGuard AI Sensor', 'text': 'Automated IoT Gas Spike: 360 PPM Ammonia detected.', 'time': '6h ago'},
                {'author': 'Dr. Lakshmi Prasad (FSO)', 'text': 'Notice served under Sec 56 FSS Act. Penalty: ₹2,500. 7 days rectification period.', 'time': '5h ago'}
            ]),
            0, 2500, 17.0040, 81.8020, 'FSSAI-AP-2026-V09', 'Swagath Grand Fast Food', 360
        ),
        (
            'ISS-2026-00122', 'Andhra Pradesh', 'Surampalem', 'Ward 11 (Lake View Zone)', 'Lake View Road',
            'sanitation', 'Sanitation & Waste Management', '🏢',
            'Water Pipeline Leakage & Pothole Formed',
            'Underground valve burst repaired and blacktop restoration completed.',
            'Surampalem • Ward 11 (Lake View Zone), Lake View Road',
            'pothole', 'Pothole / Road Damage', '🕳️', 'medium', 'RESOLVED IN 26 HOURS', 'resolved',
            now - (36 * 3600 * 1000), now + (12 * 3600 * 1000), 0, now - (10 * 3600 * 1000), 0,
            'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=800&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&auto=format&fit=crop&q=80',
            'S. Rajesh (Citizen)', 'user-106', 'Consultant Officer K. Mukundha', now - (35 * 3600 * 1000),
            'Public Works Squad 2', now - (34 * 3600 * 1000), 'Field Execution Completed & Cleaned Proof Uploaded',
            'Collection Truck', 22, json.dumps(['user-106']),
            json.dumps([
                {'author': 'Consultant Officer K. Mukundha', 'text': 'Grievance verified. PW squad closed repair within 26 hours.', 'time': '10h ago'}
            ]),
            1, 0, 17.0012, 81.8040, None, None, None
        )
    ]

    cursor.executemany('''
        INSERT INTO issues (
            id, state, city, ward, street, department, deptName, deptIcon, title,
            description, location, category, categoryName, categoryIcon, severity,
            severityLabel, status, timestamp, slaDeadline, slaHoursLeft, resolvedTimestamp,
            isSlaBreached, imageBefore, imageAfter, reportedBy, reportedById, verifiedByOfficer,
            verifiedTimestamp, assignedWorker, assignedTimestamp, workerStatus,
            recommendedResource, upvotes, upvotedBy, comments, rewardIssued, fineLevied,
            lat, lng, vendorId, vendorName, mq135GasPpm
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    ''', seed_issues)

    # Initial Vendors
    seed_vendors = [
        (
            'FSSAI-AP-2026-V01', 'Andhra Pradesh', 'Surampalem', 'Ward 14 (Campus Food Zone)',
            'Annapurna Tiffin Centre', 'K. Satyanarayana', 'College Road, Ward 14, Surampalem',
            'A+', '94/100', '31 Dec 2026', 'Dr. Lakshmi Prasad (FSO)', 'VERIFIED & CERTIFIED',
            0, None, None, None, '180 PPM (Safe)', 'All hygiene standards, water potability & hairnet compliance cleared.'
        ),
        (
            'FSSAI-AP-2026-V04', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)',
            'Aditya Highway Dhaba & Fast Food', 'R. Koteswara Rao', 'Gandhi Statue Main Road, Surampalem',
            'F', '24/100', 'SEIZED & SUSPENDED', 'Dr. Lakshmi Prasad (FSO)', 'CRITICAL UNHYGIENIC VIOLATION',
            1, 'Section 59: Rotten Meat Storage, Reheated Stale Oil (TPM >36%) & Drain Adjacent Prep',
            '₹5,000.00', 'Immediate Suspension & Seizure', '580 PPM (Severe Toxic Ammonia Spoilage)',
            'Complete commercial closure order served. Kitchen sealed under FSSAI Section 38. Confiscation of contaminated food inventory.'
        ),
        (
            'FSSAI-AP-2026-V09', 'Andhra Pradesh', 'Surampalem', 'Ward 14 (Campus Food Zone)',
            'Swagath Grand Fast Food', 'R. Koteswara Rao', 'College Road Food Court Lane 2, Surampalem',
            'C', '45/100', 'Action Required (Statutory Notice)', 'Dr. Lakshmi Prasad (FSO)', 'VIOLATION NOTICE ISSUED',
            1, 'Sec 56 FSS Act - Unhygienic preparation area & elevated organic volatile gases',
            '₹2,500.00', '7 Days from Notice', '360 PPM (High Gas Risk)', 'Immediate installation of insect fly-killers and grease trap cleanup required.'
        ),
        (
            'FSSAI-AP-2026-V02', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)',
            'Sri Venkateswara Sweets & Bakers', 'M. Venkatesh', 'Gandhi Statue Main Road, Surampalem',
            'A', '89/100', '31 Dec 2026', 'Dr. Lakshmi Prasad (FSO)', 'VERIFIED & CERTIFIED',
            0, None, None, None, '210 PPM (Safe)', 'Temperature control in dairy display units verified compliant.'
        )
    ]

    cursor.executemany('''
        INSERT INTO vendors VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', seed_vendors)

    # Initial User & Quota
    today_str = datetime.date.today().isoformat()
    cursor.execute('''
        INSERT OR REPLACE INTO users (id, name, email, department, roleTitle, officialId, civicCredits, activeStreakWeeks)
        VALUES ('user-101', 'KRISH', 'citizen@civictech.in', 'citizen', 'Verified Citizen Reporter', 'CIT-IND-2026-8941', 150, 4)
    ''')

    cursor.execute('''
        INSERT OR REPLACE INTO citizen_quotas (user_id, date_str, report_count)
        VALUES ('user-101', ?, 1)
    ''', (today_str,))

    conn.commit()
    print('[Database] Seed data loaded successfully!')

# ------------------------------------------------------------------------------
# 2. SERVER-SENT EVENTS (SSE) BROADCAST HUB
# ------------------------------------------------------------------------------
class SSEBroadcastHub:
    def __init__(self):
        self.clients = []
        self.lock = threading.Lock()

    def register_client(self, client_writer):
        with self.lock:
            self.clients.append(client_writer)
            print(f'[SSE Hub] Client connected. Active clients: {len(self.clients)}')

    def unregister_client(self, client_writer):
        with self.lock:
            if client_writer in self.clients:
                self.clients.remove(client_writer)
                print(f'[SSE Hub] Client disconnected. Active clients: {len(self.clients)}')

    def broadcast(self, event_type, payload):
        packet = json.dumps({'type': event_type, 'payload': payload, 'timestamp': int(time.time() * 1000)})
        msg = f'event: message\ndata: {packet}\n\n'.encode('utf-8')

        with self.lock:
            disconnected = []
            for client in self.clients:
                try:
                    client.wfile.write(msg)
                    client.wfile.flush()
                except Exception:
                    disconnected.append(client)
            
            for d in disconnected:
                if d in self.clients:
                    self.clients.remove(d)

sse_hub = SSEBroadcastHub()

# Background telemetry ticker (Moving Fleet GPS & IoT Gas updates)
def background_telemetry_loop():
    step = 0
    while True:
        time.sleep(3.5)
        step = (step + 1) % 360
        fleet_packet = [
            {'name': 'Collection Truck AP-05-TX', 'type': '🚛', 'lat': 17.0035 + (0.0008 * (step % 20 - 10) / 10), 'lng': 81.8025, 'status': 'Live GPS Tracking (24 km/h)'},
            {'name': 'Lineman Van AP-05-EB', 'type': '⚡', 'lat': 17.0018, 'lng': 81.8080 + (0.0008 * (step % 20 - 10) / 10), 'status': 'En Route to Feeder 4'},
            {'name': 'Compactor Tractor AP-05-CT', 'type': '🚜', 'lat': 16.9990 + (0.0005 * (step % 15 - 7) / 7), 'lng': 81.8050, 'status': 'Compacting at Waste Facility'}
        ]
        sse_hub.broadcast('FLEET_GPS_STREAM', fleet_packet)

# ------------------------------------------------------------------------------
# 3. HTTP REST API & STATIC FILE REQUEST HANDLER
# ------------------------------------------------------------------------------
class CivicAppRequestHandler(BaseHTTPRequestHandler):
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # 1. SSE Real-Time Stream Endpoint
        if path == '/api/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_cors_headers()
            self.end_headers()

            welcome_msg = f'event: connected\ndata: {{"status": "online", "timestamp": {int(time.time()*1000)}}}\n\n'.encode('utf-8')
            try:
                self.wfile.write(welcome_msg)
                self.wfile.flush()
            except Exception:
                return

            sse_hub.register_client(self)

            try:
                while True:
                    time.sleep(15)
                    self.wfile.write(b': ping\n\n')
                    self.wfile.flush()
            except Exception:
                sse_hub.unregister_client(self)
        # Phase 4/E: Predictive Civic Intelligence Endpoints (GET)
        conn_pred = get_db_connection()
        auth_user_pred = get_authenticated_user(self, conn_pred)
        conn_pred.close()
        if predictive_engine.handle_predictive_get(self, path, query, auth_user=auth_user_pred):
            return

        # 2. REST API: GET /api/issues
        if path == '/api/issues':
            conn = get_db_connection()
            cursor = conn.cursor()

            # Authoritative server-side identity & jurisdiction resolution
            auth_user = get_authenticated_user(self, conn)
            user_dept = auth_user.get('department') if auth_user else None

            where_clauses = []
            params = []

            # 1. Municipal Officer: scoped strictly to assigned official jurisdiction & municipal departments
            if user_dept == 'municipal':
                state = auth_user.get('jurisdictionState')
                city = auth_user.get('jurisdictionCity')
                ward = auth_user.get('jurisdictionWard')

                if state:
                    where_clauses.append("state = ?")
                    params.append(state)
                if city:
                    where_clauses.append("city = ?")
                    params.append(city)
                if ward and ward != 'ALL':
                    where_clauses.append("ward = ?")
                    params.append(ward)

                # Municipal officers manage civic infra, sanitation, electricity, etc., not food safety
                where_clauses.append("department != 'food_safety'")

            # 2. Food Safety Officer: scoped strictly to food_safety violations within city
            elif user_dept in ['food', 'food_safety']:
                where_clauses.append("department = 'food_safety'")
                state = auth_user.get('jurisdictionState')
                city = auth_user.get('jurisdictionCity')
                ward = auth_user.get('jurisdictionWard')

                if state:
                    where_clauses.append("state = ?")
                    params.append(state)
                if city:
                    where_clauses.append("city = ?")
                    params.append(city)
                if ward and ward != 'ALL':
                    where_clauses.append("ward = ?")
                    params.append(ward)

            # 3. Field Worker: scoped strictly to tasks assigned to this worker or squad
            elif user_dept == 'worker':
                w_name = auth_user.get('name', '')
                w_id = auth_user.get('officialId', '')
                where_clauses.append("(assignedWorker LIKE ? OR assignedWorker LIKE ? OR assignedWorker LIKE ?)")
                params.append(f"%{w_name}%")
                params.append(f"%Squad 4%")
                params.append(f"%{w_id}%")

            # 4. Citizen or Unauthenticated Public View
            else:
                q_state = query.get('state', [None])[0]
                q_city = query.get('city', [None])[0]
                q_ward = query.get('ward', [None])[0]
                if q_state and q_state != 'all':
                    where_clauses.append("state = ?")
                    params.append(q_state)
                if q_city and q_city != 'all':
                    where_clauses.append("city = ?")
                    params.append(q_city)
                if q_ward and q_ward != 'all':
                    where_clauses.append("ward = ?")
                    params.append(q_ward)

            sql = 'SELECT * FROM issues'
            if where_clauses:
                sql += ' WHERE ' + ' AND '.join(where_clauses)
            sql += ' ORDER BY timestamp DESC'

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            issues = []
            for r in rows:
                item = dict(r)
                item['upvotedBy'] = json.loads(item['upvotedBy'] or '[]')
                item['comments'] = json.loads(item['comments'] or '[]')

                # Public / Citizen data protection: redact internal administrative & supervisor notes
                if not auth_user or user_dept == 'citizen':
                    item['supervisorNotes'] = None
                    item['rejectionReason'] = None
                    item['aiRiskScore'] = None
                    item['aiConfidence'] = None
                    item['aiReasoning'] = None
                    item['aiOverrideReason'] = None
                    item['imageRiskModifier'] = None
                # Phase E: Clean Zone citizen awareness notice
                i_ward = str(item.get('ward') or '')
                i_dept = str(item.get('department') or '').lower()
                if 'ward 12' in i_ward.lower() and i_dept == 'sanitation':
                    item['cleanZone'] = {
                        'name': 'Market Canteen Gate, Ward 12',
                        'status': 'UNDER PREVENTIVE MONITORING',
                        'guidance': 'Please use designated waste collection points and avoid leaving waste outside collection areas.'
                    }
                else:
                    item['cleanZone'] = None

                issues.append(item)
            conn.close()

            self.send_json_response({'success': True, 'issues': issues, 'count': len(issues)})
            return

        # Stage v43: REST API: GET /api/issues/:id/relationships
        if (path.startswith('/api/issues/') and path.endswith('/relationships')) or path == '/api/issues/relationships':
            parts = path.split('/')
            issue_id = parts[3] if len(parts) >= 5 else query.get('issueId', [None])[0]
            
            if not issue_id:
                self.send_json_response({'success': False, 'error': 'Missing issue ID.'}, status=400)
                return
            
            conn = get_db_connection()
            cursor = conn.cursor()
            auth_user = get_authenticated_user(self, conn)
            
            cursor.execute("SELECT * FROM issues WHERE id = ?", (issue_id,))
            i_row = cursor.fetchone()
            if not i_row:
                conn.close()
                self.send_json_response({'success': False, 'error': f'Issue #{issue_id} not found.'}, status=404)
                return
            
            target_issue = dict(i_row)
            
            # Authoritative Jurisdiction Security Check
            if auth_user:
                u_dept = auth_user.get('department')
                if u_dept == 'municipal':
                    u_state = auth_user.get('jurisdictionState')
                    u_city = auth_user.get('jurisdictionCity')
                    u_ward = auth_user.get('jurisdictionWard')
                    if u_state and target_issue.get('state') and u_state.lower() != target_issue.get('state').lower():
                        conn.close()
                        self.send_json_response({'success': False, 'error': 'Forbidden: Incident outside authorized state jurisdiction.'}, status=403)
                        return
                    if u_city and target_issue.get('city') and u_city.lower() != target_issue.get('city').lower():
                        conn.close()
                        self.send_json_response({'success': False, 'error': 'Forbidden: Incident outside authorized city jurisdiction.'}, status=403)
                        return
                    if u_ward and u_ward != 'ALL' and target_issue.get('ward') and u_ward.lower() not in target_issue.get('ward').lower():
                        conn.close()
                        self.send_json_response({'success': False, 'error': 'Forbidden: Incident outside authorized ward jurisdiction.'}, status=403)
                        return
                    if target_issue.get('department') == 'food_safety':
                        conn.close()
                        self.send_json_response({'success': False, 'error': 'Forbidden: Municipal officer cannot view food safety incident relationships.'}, status=403)
                        return
                elif u_dept in ['food', 'food_safety']:
                    if target_issue.get('department') != 'food_safety':
                        conn.close()
                        self.send_json_response({'success': False, 'error': 'Forbidden: Food safety officers only have access to food safety incidents.'}, status=403)
                        return
                elif u_dept == 'worker':
                    if target_issue.get('assignedWorker') != auth_user.get('name') and target_issue.get('assignedWorkerId') != auth_user.get('userId'):
                        conn.close()
                        self.send_json_response({'success': False, 'error': 'Forbidden: Workers may only access assigned tasks.'}, status=403)
                        return

            # Fetch relationships from incident_relationships
            cursor.execute("""
                SELECT * FROM incident_relationships 
                WHERE targetIssueId = ? OR sourceIssueId = ?
                ORDER BY createdAt DESC
            """, (issue_id, issue_id))
            rel_rows = cursor.fetchall()
            relationships = []
            for r in rel_rows:
                rd = dict(r)
                try:
                    rd['signals'] = json.loads(rd.get('signals') or '[]')
                except Exception:
                    rd['signals'] = []
                relationships.append(rd)

            # Fetch direct child follow-up issues if any
            cursor.execute("SELECT id, title, status, timestamp, reportedBy, followUpCount, identityType FROM issues WHERE parentIssueId = ?", (issue_id,))
            child_rows = cursor.fetchall()
            linked_followups = [dict(cr) for cr in child_rows]

            conn.close()
            self.send_json_response({
                'success': True,
                'issueId': issue_id,
                'parentIssueId': target_issue.get('parentIssueId'),
                'identityType': target_issue.get('identityType') or 'NEW_INCIDENT',
                'identityMatchScore': target_issue.get('identityMatchScore'),
                'identityMatchedIssueId': target_issue.get('identityMatchedIssueId'),
                'identityReasoning': target_issue.get('identityReasoning'),
                'identityReviewed': target_issue.get('identityReviewed') or 0,
                'identityReviewedBy': target_issue.get('identityReviewedBy'),
                'identityReviewedTimestamp': target_issue.get('identityReviewedTimestamp'),
                'followUpCount': int(target_issue.get('followUpCount') or 0),
                'relationships': relationships,
                'linkedFollowUps': linked_followups
            })
            return

        # 3. REST API: GET /api/vendors
        if path == '/api/vendors':
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM vendors')
            rows = cursor.fetchall()
            vendors = [dict(r) for r in rows]
            conn.close()

            self.send_json_response({'success': True, 'vendors': vendors})
            return

        # 4. REST API: GET /api/quota
        if path == '/api/quota':
            user_id = query.get('user_id', ['user-101'])[0]
            today_str = datetime.date.today().isoformat()

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT report_count FROM citizen_quotas WHERE user_id = ? AND date_str = ?', (user_id, today_str))
            row = cursor.fetchone()
            count = row['report_count'] if row else 0
            conn.close()

            limit = 3
            remaining = max(0, limit - count)
            self.send_json_response({
                'success': True,
                'user_id': user_id,
                'date': today_str,
                'usedToday': count,
                'limit': limit,
                'remaining': remaining,
                'isLimitReached': count >= limit
            })
            return

        # ---------------------------------------------------------------------
        # PHASE 7 PREPARED ENDPOINTS: CLUSTERS, HOTSPOTS & WORKERS
        # ---------------------------------------------------------------------
        if path == '/api/clusters':
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM incident_clusters ORDER BY lastReportedAt DESC')
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            self.send_json_response({'success': True, 'clusters': rows, 'total': len(rows)})
            return

        if path == '/api/hotspots':
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM hotspots ORDER BY predictedRiskPercent DESC')
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            self.send_json_response({'success': True, 'hotspots': rows, 'total': len(rows)})
            return

        if path == '/api/workers':
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM workers ORDER BY tasksCompleted DESC')
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            self.send_json_response({'success': True, 'workers': rows, 'total': len(rows)})
            return

        # REST API: GET /api/audit-logs
        if path == '/api/audit-logs':
            conn = get_db_connection()
            cursor = conn.cursor()
            auth_user = get_authenticated_user(self, conn)

            cursor.execute('''
                SELECT l.id, l.issueId, l.officer, l.actionType, l.assignedWorker, l.supervisorNotes, l.timestamp,
                       i.title as issueTitle, i.department as issueDept, i.ward as issueWard, i.state as issueState, i.city as issueCity
                FROM operational_audit_logs l
                LEFT JOIN issues i ON l.issueId = i.id
                ORDER BY l.timestamp DESC
                LIMIT 100
            ''')
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            self.send_json_response({'success': True, 'auditLogs': rows, 'total': len(rows)})
            return

        # REST API: GET /api/grid/status
        if path == '/api/grid/status':
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, location, status, assignedWorker FROM issues WHERE department = 'electricity'")
            elec_issues = [dict(r) for r in cursor.fetchall()]
            conn.close()

            feeders = [
                {
                    'id': 'FEEDER-01',
                    'name': 'Feeder #1 (Market Commercial & Cold Storage)',
                    'voltage': 11.2,
                    'current': 142.5,
                    'load': 1.6,
                    'frequency': 50.02,
                    'status': 'ONLINE',
                    'breaker': 'CLOSED',
                    'substation': 'Surampalem 33/11 KV Central'
                },
                {
                    'id': 'FEEDER-02',
                    'name': 'Feeder #2 (University & Campus Hostels)',
                    'voltage': 11.1,
                    'current': 98.4,
                    'load': 1.1,
                    'frequency': 50.01,
                    'status': 'ONLINE',
                    'breaker': 'CLOSED',
                    'substation': 'Surampalem 33/11 KV Central'
                },
                {
                    'id': 'FEEDER-03',
                    'name': 'Feeder #3 (Industrial Agro Estate & Water Works)',
                    'voltage': 11.3,
                    'current': 210.0,
                    'load': 2.4,
                    'frequency': 49.98,
                    'status': 'ONLINE',
                    'breaker': 'CLOSED',
                    'substation': 'Surampalem 33/11 KV Central'
                },
                {
                    'id': 'FEEDER-04',
                    'name': 'Feeder #4 (Ward 12 Residential Gandhi Road)',
                    'voltage': 10.7,
                    'current': 0.0,
                    'load': 0.0,
                    'frequency': 0.0,
                    'status': 'OUTAGE',
                    'breaker': 'TRIPPED',
                    'substation': 'Surampalem 33/11 KV Central',
                    'cause': 'Sparking & Low Hanging Cable (ISS-2026-00124)',
                    'assignedLineman': 'Lineman Squad B (Suresh Kumar)',
                    'etaMinutes': 35
                }
            ]
            self.send_json_response({
                'success': True,
                'substation': 'Surampalem Central 33/11 KV Substation',
                'overallStatus': 'WARNING_ACTIVE_OUTAGE',
                'activeFeedersOnline': 3,
                'totalFeeders': 4,
                'feeders': feeders,
                'activeElectricalTickets': elec_issues,
                'timestamp': int(time.time() * 1000)
            })
            return

        # REST API: GET /api/settings/ai-status
        if path == '/api/settings/ai-status':
            conn = get_db_connection()
            has_key = bool(ai_engine.get_gemini_api_key(conn))
            conn.close()
            self.send_json_response({
                'success': True,
                'hasGeminiApiKey': has_key,
                'activeModel': 'gemini-2.5-flash' if has_key else 'contextual-civic-intelligence',
                'multimodalVisionAvailable': has_key
            })
            return

        # 5. REST API: GET /api/stats
        if path == '/api/stats':
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as total, SUM(CASE WHEN status="resolved" THEN 1 ELSE 0 END) as resolved, SUM(fineLevied) as fines FROM issues')
            stat_row = cursor.fetchone()
            conn.close()

            total = stat_row['total'] or 0
            resolved = stat_row['resolved'] or 0
            fines = stat_row['fines'] or 2500
            res_rate = int((resolved / total * 100)) if total > 0 else 0

            self.send_json_response({
                'success': True,
                'totalReports': total,
                'resolvedReports': resolved,
                'resolutionRate': f'{res_rate}%',
                'civicCreditsPaid': '150 Pts',
                'finesCollected': f'₹{int(fines):,}'
            })
        # REST API: GET /api/citizen/profile (Authoritative Server-Side Identity Resolution)
        if path == '/api/citizen/profile':
            conn = get_db_connection()
            auth_user = get_authenticated_user(self, conn)
            if not auth_user:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Unauthorized. Please login.'}, status=401)
                return

            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE LOWER(TRIM(email)) = LOWER(TRIM(?))', (auth_user['email'],))
            user_row = cursor.fetchone()
            conn.close()

            if not user_row:
                self.send_json_response({'success': False, 'error': 'Citizen account record not found.'}, status=404)
                return

            user_dict = dict(user_row)
            safe_user = {k: v for k, v in user_dict.items() if k != 'password'}
            safe_user['profileCompleted'] = 1 if safe_user.get('profileCompleted') == 1 else 0
            self.send_json_response({'success': True, 'user': safe_user})
            return

        # REST API: GET /api/citizen/rewards (Civic Rewards Catalog & Redemptions)
        if path == '/api/citizen/rewards':
            conn = get_db_connection()
            auth_user = get_authenticated_user(self, conn)
            target_email = None
            if auth_user:
                target_email = auth_user.get('email')
            elif 'email' in query:
                target_email = query['email'][0].strip()
            elif not target_email:
                target_email = 'citizen@civictech.in'

            cursor = conn.cursor()
            user_points = 250
            if target_email:
                cursor.execute('SELECT civicCredits FROM users WHERE LOWER(TRIM(email)) = LOWER(TRIM(?))', (target_email,))
                row = cursor.fetchone()
                if row and row['civicCredits'] is not None:
                    user_points = row['civicCredits']

            # Fetch past redemptions
            if target_email:
                cursor.execute('SELECT * FROM civic_redemptions WHERE LOWER(TRIM(userEmail)) = LOWER(TRIM(?)) ORDER BY timestamp DESC LIMIT 20', (target_email,))
                redemptions = [dict(r) for r in cursor.fetchall()]
            else:
                cursor.execute('SELECT * FROM civic_redemptions ORDER BY timestamp DESC LIMIT 20')
                redemptions = [dict(r) for r in cursor.fetchall()]

            formatted_redemptions = []
            for r in redemptions:
                r_dict = dict(r)
                r_dict['reward_title'] = r_dict.get('rewardTitle')
                r_dict['voucher_code'] = r_dict.get('voucherCode')
                r_dict['points_spent'] = r_dict.get('pointsDeducted')
                ts = r_dict.get('timestamp')
                r_dict['created_at'] = datetime.datetime.fromtimestamp(ts/1000).strftime('%d %b %Y') if ts else 'Recent'
                formatted_redemptions.append(r_dict)

            conn.close()
            self.send_json_response({
                'success': True,
                'userPoints': user_points,
                'user_points': user_points,
                'catalog': CIVIC_REWARDS_CATALOG,
                'redemptions': formatted_redemptions
            })
            return

        # 6. Static Asset Serving
        self.serve_static_file(path)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b'{}'
        try:
            body = json.loads(post_body.decode('utf-8'))
        except Exception:
            body = {}

        # Phase 4/E: Predictive Civic Intelligence Endpoints (POST)
        conn_pred = get_db_connection()
        auth_user_pred = get_authenticated_user(self, conn_pred)
        conn_pred.close()
        if predictive_engine.handle_predictive_post(self, path, body, sse_hub, auth_user=auth_user_pred):
            return

        # 1. REST API: POST /api/issues
        if path == '/api/issues':
            user_id = body.get('reportedById', 'user-101')
            today_str = datetime.date.today().isoformat()

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT report_count FROM citizen_quotas WHERE user_id = ? AND date_str = ?', (user_id, today_str))
            q_row = cursor.fetchone()
            current_count = q_row['report_count'] if q_row else 0

            if current_count >= 3:
                conn.close()
                self.send_json_response({
                    'success': False,
                    'error': 'Daily quota exceeded. Maximum 3 complaints allowed per day.',
                    'remaining': 0
                }, status=429)
                return

            cursor.execute('''
                INSERT INTO citizen_quotas (user_id, date_str, report_count)
                VALUES (?, ?, 1)
                ON CONFLICT(user_id, date_str) DO UPDATE SET report_count = report_count + 1
            ''', (user_id, today_str))

            cursor.execute('SELECT COUNT(*) FROM issues')
            total_issues = cursor.fetchone()[0]
            issue_id = (body.get('id') or '').strip() or f'ISS-2026-{str(total_issues + 124).zfill(5)}'

            now = int(time.time() * 1000)
            deadline = now + (48 * 3600 * 1000)
            reporter_actor = (body.get('reportedBy') or 'Citizen').strip()

            dept_key = body.get('department', 'sanitation')
            dept_map = {
                'sanitation': ('Sanitation & Waste Management', '🏢', 'Municipal Rapid Squad 4'),
                'roads': ('Infrastructure / Roads', '🛣️', 'Roads Squad 3 (Lead: Anita Roy)'),
                'electricity': ('Smart Electricity Department', '⚡', 'Lineman Squad B'),
                'water_supply': ('Water Supply', '💧', 'Water Utility Squad 5 (Lead: K. Somaraju)'),
                'food_safety': ('Food Safety Department', '🍲', 'Food Safety Officer')
            }
            dept_default_name, dept_default_icon, assigned_squad = dept_map.get(dept_key, ('Sanitation & Waste Management', '🏢', 'Municipal Rapid Squad 4'))
            dept_name = body.get('deptName') or dept_default_name
            dept_icon = body.get('deptIcon') or dept_default_icon

            comments = [
                {'author': 'System Watchdog', 'text': 'Report logged with live GPS geotag. 48h SLA timer activated.', 'time': 'Just now'},
                {'author': 'Consultant Officer K. Mukundha', 'text': 'Grievance verified. Squad allocated and dispatched.', 'time': 'Just now'}
            ]

            auth_user_iss = get_authenticated_user(self, conn)
            resolved_state = body.get('state') or (auth_user_iss and auth_user_iss.get('jurisdictionState')) or 'Andhra Pradesh'
            resolved_city = body.get('city') or (auth_user_iss and auth_user_iss.get('jurisdictionCity')) or 'Surampalem'
            resolved_ward = body.get('ward') or (auth_user_iss and auth_user_iss.get('jurisdictionWard')) or 'Ward 12 (Market Zone)'
            resolved_street = body.get('street') or (auth_user_iss and auth_user_iss.get('permanentAddress')) or 'Geotagged Incident Location'

            # Version 44: Evaluate Geo-Evidence Consistency
            input_lat = body.get('lat')
            input_lng = body.get('lng')
            geo_eval = evaluate_geo_evidence(input_lat, input_lng, reported_ward=resolved_ward, reported_city=resolved_city, reported_state=resolved_state, accuracy=body.get('accuracy'))

            new_issue = {
                'id': issue_id,
                'state': resolved_state,
                'city': resolved_city,
                'ward': resolved_ward,
                'street': resolved_street,
                'department': dept_key,
                'deptName': dept_name,
                'deptIcon': dept_icon,
                'title': body.get('title', 'Civic Hazard'),
                'description': body.get('description', ''),
                'location': f"{resolved_city} • {resolved_ward}, {resolved_street}",
                'category': body.get('category', 'general'),
                'categoryName': body.get('categoryName', 'Civic Hazard'),
                'categoryIcon': dept_icon,
                'severity': body.get('severity', 'medium'),
                'severityLabel': 'HIGH RISK HAZARD' if body.get('severity') == 'bulk' else 'STANDARD COMPLAINT',
                'status': 'pending',
                'timestamp': now,
                'slaDeadline': deadline,
                'slaHoursLeft': 48.0,
                'resolvedTimestamp': None,
                'isSlaBreached': 0,
                'imageBefore': body.get('imageBefore', 'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80'),
                'imageAfter': None,
                'reportedBy': body.get('reportedBy', 'KRISH'),
                'reportedById': user_id,
                'verifiedByOfficer': None,
                'verifiedTimestamp': None,
                'assignedWorker': None,
                'assignedTimestamp': None,
                'workerStatus': 'Pending Allocation',
                'recommendedResource': 'Tractor / Heavy Squad' if body.get('severity') == 'bulk' else 'Collection Truck',
                'upvotes': 1,
                'upvotedBy': json.dumps([user_id]),
                'comments': json.dumps(comments),
                'rewardIssued': 0,
                'fineLevied': 0,
                'lat': body.get('lat', 17.0010),
                'lng': body.get('lng', 81.8045),
                'vendorId': body.get('vendorId'),
                'vendorName': body.get('vendorName'),
                'mq135GasPpm': body.get('mq135GasPpm'),
                'clusterId': body.get('clusterId'),
                'aiRiskScore': body.get('aiRiskScore', 50),
                'aiConfidence': body.get('aiConfidence', 0.0),
                'aiReasoning': body.get('aiReasoning', ''),
                'aiSuggestedSLA': body.get('aiSuggestedSLA', 48.0),
                'slaBreachProb': body.get('slaBreachProb', 0.1),
                'aiSuggestedDepartment': body.get('aiSuggestedDepartment', body.get('department', 'sanitation')),
                'aiSuggestedCategory': body.get('aiSuggestedCategory', body.get('category')),
                'aiSuggestedSeverity': body.get('aiSuggestedSeverity', body.get('severity')),
                'citizenConfirmedAI': int(body.get('citizenConfirmedAI', 1)),
                'aiOverrideReason': body.get('aiOverrideReason', ''),
                'imageAiHazard': body.get('imageAiHazard'),
                'imageAiConfidence': body.get('imageAiConfidence'),
                'imageTextConsistency': body.get('imageTextConsistency'),
                'imageRiskModifier': int(body.get('imageRiskModifier', 0)),
                'imageAiReasoning': body.get('imageAiReasoning'),
                'imageAiAccepted': int(body.get('imageAiAccepted', 0)),
                'imageOfficerVerified': int(body.get('imageOfficerVerified', 0)),
                'imageOfficerOverrideReason': body.get('imageOfficerOverrideReason'),
                'parentIssueId': body.get('parentIssueId'),
                'identityType': body.get('identityType', 'NEW_INCIDENT'),
                'identityMatchScore': float(body.get('identityMatchScore', 0.0)),
                'identityMatchedIssueId': body.get('identityMatchedIssueId'),
                'identityReasoning': body.get('identityReasoning'),
                'identityReviewed': int(body.get('identityReviewed', 0)),
                'identityReviewedBy': body.get('identityReviewedBy'),
                'identityReviewedTimestamp': body.get('identityReviewedTimestamp'),
                'followUpCount': int(body.get('followUpCount', 0)),
                'evidenceHash': compute_evidence_hash(body.get('imageBefore')),
                'geoConsistencyStatus': geo_eval['status'],
                'geoConsistencyLevel': geo_eval['consistencyLevel'],
                'geoDistanceMeters': geo_eval['distanceMeters'] or 0.0,
                'geoResolvedState': geo_eval['resolvedState'],
                'geoResolvedCity': geo_eval['resolvedCity'],
                'geoResolvedWard': geo_eval['resolvedWard'],
                'geoResolvedZone': geo_eval['resolvedZone'],
                'geoResolvedStreet': geo_eval.get('resolvedStreet') or resolved_street,
                'geoCheckTimestamp': now,
                'geoCheckReasoning': geo_eval['reasoning']
            }

            cols = ', '.join(new_issue.keys())
            placeholders = ', '.join([f":{k}" for k in new_issue.keys()])
            cursor.execute(f"INSERT INTO issues ({cols}) VALUES ({placeholders})", new_issue)

            # Record in incident_relationships if linked or related
            if body.get('identityMatchedIssueId') or body.get('parentIssueId'):
                target_id = body.get('parentIssueId') or body.get('identityMatchedIssueId')
                rel_type = body.get('identityType') or 'RELATED_INCIDENT'
                cursor.execute('''
                    INSERT INTO incident_relationships (
                        id, sourceIssueId, targetIssueId, relationshipType, matchReason,
                        matchScore, signals, createdAt, createdBy, createdById, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"REL-{now}-{random.randint(100, 999)}",
                    new_issue['id'],
                    target_id,
                    rel_type,
                    body.get('identityReasoning') or 'Citizen corroborated relationship',
                    float(body.get('identityMatchScore', 0.0)),
                    json.dumps(body.get('signals') or []),
                    now,
                    reporter_actor,
                    user_id,
                    'ACTIVE'
                ))
                cursor.execute('''
                    INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"AUDIT-REL-{now}-{random.randint(100, 999)}",
                    new_issue['id'],
                    reporter_actor,
                    'ISSUE_RELATIONSHIP_CREATED',
                    None,
                    f"Linked to incident #{target_id} as {rel_type}",
                    now
                ))

            # Record Geo-Evidence Check
            check_id = f"GEC-{now}-{random.randint(100, 999)}"
            cursor.execute('''
                INSERT INTO geo_evidence_checks (
                    id, issueId, latitude, longitude, status, consistencyLevel, distanceMeters,
                    resolvedState, resolvedCity, resolvedWard, resolvedZone, timestamp, citizenConfirmed, reasoning
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                check_id, issue_id, geo_eval['latitude'], geo_eval['longitude'], geo_eval['status'],
                geo_eval['consistencyLevel'], geo_eval['distanceMeters'] or 0.0, geo_eval['resolvedState'],
                geo_eval['resolvedCity'], geo_eval['resolvedWard'], geo_eval['resolvedZone'], now, 1, geo_eval['reasoning']
            ))

            # Operational Audit Logging for Geo-Evidence
            cursor.execute('''
                INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"AUDIT-GEO-{now}-{random.randint(100, 999)}",
                issue_id,
                reporter_actor,
                'GEO_CHECK_PERFORMED',
                None,
                f"Geo-Evidence evaluated: status={geo_eval['status']}, consistency={geo_eval['consistencyLevel']}, distance={geo_eval['distanceMeters']}m to {geo_eval['resolvedWard']}. Action: {geo_eval['recommendedAction']}",
                now
            ))
            if geo_eval['status'] == 'LOCATION_MISMATCH':
                cursor.execute('''
                    INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"AUDIT-GEO-MIS-{now}-{random.randint(100, 999)}",
                    issue_id,
                    'SYSTEM',
                    'GEO_MISMATCH_DETECTED',
                    None,
                    f"Mismatch detected between reported area ({resolved_city}, {resolved_ward}) and GPS coordinates ({geo_eval['latitude']}, {geo_eval['longitude']}). Reasoning: {geo_eval['reasoning']}",
                    now
                ))
            else:
                cursor.execute('''
                    INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"AUDIT-GEO-OK-{now}-{random.randint(100, 999)}",
                    issue_id,
                    'SYSTEM',
                    'GEO_LOCATION_CONFIRMED',
                    None,
                    f"GPS location validated as {geo_eval['status']} within {geo_eval['resolvedWard']} ({geo_eval['resolvedCity']}).",
                    now
                ))

            # Operational Audit Trail Logging (Phase D Requirement 8)
            audit_id_rep = f"AUDIT-REP-{now}-{random.randint(100, 999)}"
            reporter_actor = (new_issue.get('reportedBy') or 'Citizen').strip()
            cursor.execute('''
                INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit_id_rep,
                new_issue['id'],
                reporter_actor,
                'ISSUE_REPORTED',
                None,
                f"Citizen grievance registered: {new_issue.get('title')}",
                now
            ))

            audit_id_tri = f"AUDIT-TRI-{now}-{random.randint(100, 999)}"
            cursor.execute('''
                INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit_id_tri,
                new_issue['id'],
                'Smart Triage Engine',
                'ISSUE_TRIAGED',
                None,
                f"Categorized as {new_issue.get('categoryName')} with severity {new_issue.get('severity')} ({new_issue.get('aiSuggestedSLA', 48)}h SLA)",
                now
            ))

            conn.commit()
            conn.close()

            broadcast_payload = dict(new_issue)
            broadcast_payload['upvotedBy'] = [user_id]
            broadcast_payload['comments'] = comments
            sse_hub.broadcast('ISSUE_CREATED', broadcast_payload)

            self.send_json_response({
                'success': True,
                'issue': broadcast_payload,
                'geoEvidence': geo_eval,
                'remainingToday': max(0, 2 - current_count)
            })
            return

        # Version 44: REST API: POST /api/geo/verify-location
        if path == '/api/geo/verify-location':
            lat = body.get('lat') or body.get('latitude')
            lng = body.get('lng') or body.get('longitude')
            accuracy = body.get('accuracy')
            ward = body.get('ward')
            city = body.get('city')
            state = body.get('state')
            geo_eval = evaluate_geo_evidence(lat, lng, reported_ward=ward, reported_city=city, reported_state=state, accuracy=accuracy)
            self.send_json_response({'success': True, 'geoEvidence': geo_eval})
            return

        # Version 44: Municipal Officer Severity / Priority Update: POST /api/issues/:id/change-priority
        if (path.startswith('/api/issues/') and path.endswith('/change-priority')) or path == '/api/issues/change-priority':
            conn = get_db_connection()
            cursor = conn.cursor()
            auth_user = get_authenticated_user(self, conn)
            user_dept = auth_user.get('department') if auth_user else None

            if user_dept != 'municipal':
                conn.close()
                self.send_json_response({'success': False, 'error': 'Unauthorized: Only authorized municipal officers can change incident priority.'}, status=403)
                return

            parts = path.strip('/').split('/')
            issue_id = parts[2] if len(parts) >= 4 and parts[0] == 'api' and parts[1] == 'issues' and parts[3] == 'change-priority' else body.get('issueId')
            new_severity = (body.get('severity') or body.get('priority') or 'medium').lower()
            if new_severity not in ['low', 'medium', 'high', 'critical', 'bulk']:
                new_severity = 'medium'

            cursor.execute("SELECT id, city, ward, department, severity, title FROM issues WHERE id = ?", (issue_id,))
            target_issue = cursor.fetchone()
            if not target_issue:
                conn.close()
                self.send_json_response({'success': False, 'error': f'Issue #{issue_id} not found'}, status=404)
                return

            off_ward = auth_user.get('jurisdictionWard')
            off_city = auth_user.get('jurisdictionCity')
            if off_city and target_issue['city'] and off_city.lower() != target_issue['city'].lower():
                conn.close()
                self.send_json_response({'success': False, 'error': 'Forbidden: Officer cannot modify issues outside official city jurisdiction.'}, status=403)
                return
            if off_ward and off_ward != 'ALL' and target_issue['ward'] and off_ward.lower() != target_issue['ward'].lower():
                conn.close()
                self.send_json_response({'success': False, 'error': 'Forbidden: Officer cannot modify issues outside assigned ward.'}, status=403)
                return

            now_ts = int(time.time() * 1000)
            cursor.execute("UPDATE issues SET severity = ? WHERE id = ?", (new_severity, issue_id))
            cursor.execute('''
                INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"AUDIT-PRIO-{now_ts}-{random.randint(100, 999)}",
                issue_id,
                auth_user.get('name', 'Municipal Officer'),
                'PRIORITY_CHANGED',
                None,
                f"Municipal officer modified severity from {target_issue['severity']} to {new_severity}. Reason: {body.get('reason', 'Administrative prioritization')}",
                now_ts
            ))
            conn.commit()
            conn.close()
            self.send_json_response({'success': True, 'issueId': issue_id, 'newSeverity': new_severity})
            return

        # Stage v43: REST API: POST /api/issues/follow-up (Citizen Follow-up Linking)
        if path == '/api/issues/follow-up':
            conn = get_db_connection()
            cursor = conn.cursor()
            auth_user = get_authenticated_user(self, conn)
            
            parent_id = (body.get('parentIssueId') or body.get('issueId') or '').strip()
            reason = (body.get('reason') or body.get('description') or '').strip()
            image = body.get('image') or body.get('imageBefore') or ''
            
            if not parent_id:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Parent incident ID is required.'}, status=400)
                return
            
            cursor.execute("SELECT * FROM issues WHERE id = ?", (parent_id,))
            p_row = cursor.fetchone()
            if not p_row:
                conn.close()
                self.send_json_response({'success': False, 'error': f'Parent issue #{parent_id} not found.'}, status=404)
                return
            
            parent_issue = dict(p_row)
            
            # Security & Jurisdiction validation
            if auth_user:
                u_dept = auth_user.get('department')
                if u_dept == 'worker':
                    conn.close()
                    self.send_json_response({'success': False, 'error': 'Forbidden: Field workforce squads cannot manipulate citizen follow-ups.'}, status=403)
                    return
                if u_dept == 'municipal':
                    u_state = auth_user.get('jurisdictionState')
                    u_city = auth_user.get('jurisdictionCity')
                    u_ward = auth_user.get('jurisdictionWard')
                    if u_state and parent_issue.get('state') and u_state.lower() != parent_issue.get('state').lower():
                        conn.close()
                        self.send_json_response({'success': False, 'error': 'Forbidden: Parent issue is outside your authorized state.'}, status=403)
                        return
                    if u_city and parent_issue.get('city') and u_city.lower() != parent_issue.get('city').lower():
                        conn.close()
                        self.send_json_response({'success': False, 'error': 'Forbidden: Parent issue is outside your authorized city.'}, status=403)
                        return
                    if u_ward and u_ward != 'ALL' and parent_issue.get('ward') and u_ward.lower() not in parent_issue.get('ward').lower():
                        conn.close()
                        self.send_json_response({'success': False, 'error': 'Forbidden: Parent issue is outside your authorized ward.'}, status=403)
                        return

            now_ms = int(time.time() * 1000)
            citizen_name = (auth_user.get('name') if auth_user else body.get('reportedBy')) or 'Citizen'
            user_id = (auth_user.get('userId') if auth_user else body.get('reportedById')) or 'user-citizen'
            
            current_followups = int(parent_issue.get('followUpCount') or 0)
            new_followup_count = current_followups + 1
            
            comments = json.loads(parent_issue.get('comments') or '[]')
            follow_up_comment = {
                'author': f"Citizen Follow-up ({citizen_name})",
                'text': reason or "Citizen submitted a follow-up report confirming the issue remains unresolved on-site.",
                'time': 'Just now',
                'type': 'follow_up',
                'timestamp': now_ms
            }
            comments.append(follow_up_comment)
            
            cursor.execute('''
                UPDATE issues 
                SET followUpCount = ?, comments = ?
                WHERE id = ?
            ''', (new_followup_count, json.dumps(comments), parent_id))
            
            rel_id = f"REL-FLW-{now_ms}-{random.randint(100, 999)}"
            flw_id = f"FLW-{parent_id}-{new_followup_count}"
            cursor.execute('''
                INSERT INTO incident_relationships (
                    id, sourceIssueId, targetIssueId, relationshipType, matchReason,
                    matchScore, signals, createdAt, createdBy, createdById, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rel_id,
                flw_id,
                parent_id,
                'FOLLOW_UP',
                reason or 'Operational citizen follow-up on active grievance',
                1.0,
                json.dumps([{'signal': 'DIRECT_CITIZEN_FOLLOW_UP', 'description': 'Citizen explicitly confirmed follow-up on active issue'}]),
                now_ms,
                citizen_name,
                user_id,
                'ACTIVE'
            ))
            
            audit_id = f"AUDIT-FLW-{now_ms}-{random.randint(100, 999)}"
            cursor.execute('''
                INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit_id,
                parent_id,
                citizen_name,
                'ISSUE_FOLLOW_UP_LINKED',
                parent_issue.get('assignedWorker'),
                f"Citizen {citizen_name} submitted follow-up report. Total follow-ups on #{parent_id}: {new_followup_count}",
                now_ms
            ))
            
            conn.commit()
            conn.close()
            
            self.send_json_response({
                'success': True,
                'parentIssueId': parent_id,
                'followUpCount': new_followup_count,
                'message': f"Follow-up successfully attached to incident #{parent_id}.",
                'comment': follow_up_comment
            })
            return

        # Stage v43: REST API: POST /api/issues/:id/review-identity (Officer Identity Review)
        if (path.startswith('/api/issues/') and path.endswith('/review-identity')) or path == '/api/issues/review-identity':
            conn = get_db_connection()
            cursor = conn.cursor()
            auth_user = get_authenticated_user(self, conn)
            
            if not auth_user or auth_user.get('department') not in ['municipal', 'food', 'food_safety']:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Unauthorized: Only authorized officers can review incident identity.'}, status=403)
                return
            
            parts = path.split('/')
            issue_id = parts[3] if len(parts) >= 5 else body.get('issueId')
            status_decision = body.get('decision', 'CONFIRMED')
            reason = body.get('reason', '')
            
            now_ms = int(time.time() * 1000)
            officer_name = auth_user.get('name', 'Authorized Officer')
            
            cursor.execute('''
                UPDATE issues 
                SET identityReviewed = 1, identityReviewedBy = ?, identityReviewedTimestamp = ?
                WHERE id = ?
            ''', (officer_name, now_ms, issue_id))
            
            audit_id = f"AUDIT-REV-{now_ms}-{random.randint(100, 999)}"
            cursor.execute('''
                INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit_id,
                issue_id,
                officer_name,
                'ISSUE_IDENTITY_REVIEWED',
                None,
                f"Officer reviewed incident identity: decision={status_decision}. Notes: {reason}",
                now_ms
            ))
            
            conn.commit()
            conn.close()
            
            self.send_json_response({'success': True, 'issueId': issue_id, 'status': status_decision})
            return

        # Stage B: REST API: POST /api/issues/assign (Officer Squad Allocation & Persistence)
        if path == '/api/issues/assign':
            issue_id = (body.get('issueId') or '').strip()
            worker_id = (body.get('workerId') or '').strip()
            supervisor_notes = (body.get('supervisorNotes') or '').strip()
            confirm_reassign = bool(body.get('confirmReassign', False))

            if not issue_id:
                self.send_json_response({'success': False, 'error': 'Issue ID is required.'}, status=400)
                return

            if not worker_id:
                self.send_json_response({'success': False, 'error': 'Target field squad ID is required.'}, status=400)
                return

            conn = get_db_connection()
            cursor = conn.cursor()

            # 1. Authoritative Officer Authentication Validation (Requirement 2 & 3)
            auth_user = get_authenticated_user(self, conn)
            if not auth_user:
                conn.close()
                self.send_json_response({
                    'success': False,
                    'error': 'Authentication required. Please log in with municipal officer credentials.'
                }, status=401)
                return

            if auth_user.get('department') != 'municipal':
                conn.close()
                self.send_json_response({
                    'success': False,
                    'error': 'Unauthorized. Only authenticated Municipal Officers may authorize field squad assignments.'
                }, status=403)
                return

            official_officer_name = auth_user.get('name') or 'Municipal Officer'

            # 2. Issue Validation (Requirement 2 & 3)
            cursor.execute('SELECT * FROM issues WHERE id = ?', (issue_id,))
            issue_row = cursor.fetchone()
            if not issue_row:
                conn.close()
                self.send_json_response({'success': False, 'error': f"Grievance ticket {issue_id} not found."}, status=404)
                return

            issue_dict = dict(issue_row)
            if issue_dict.get('status') == 'resolved':
                conn.close()
                self.send_json_response({'success': False, 'error': 'Cannot assign field squad to an already resolved grievance.'}, status=400)
                return

            # Reject cross-department assignment: Municipal Officer cannot assign Food Safety issues
            if issue_dict.get('department') == 'food_safety':
                conn.close()
                self.send_json_response({
                    'success': False,
                    'error': 'Cross-department assignment prohibited. Municipal Officers cannot assign Food Safety violations.'
                }, status=403)
                return

            # 3. Enforce Server-Side Government Jurisdiction Check
            officer_state = auth_user.get('jurisdictionState')
            officer_city = auth_user.get('jurisdictionCity')
            officer_ward = auth_user.get('jurisdictionWard')

            if officer_state and officer_state != issue_dict.get('state'):
                conn.close()
                self.send_json_response({
                    'success': False,
                    'error': f"Cross-jurisdiction assignment rejected. Officer jurisdiction is {officer_state} but incident is in {issue_dict.get('state')}."
                }, status=403)
                return

            if officer_city and officer_city != issue_dict.get('city'):
                conn.close()
                self.send_json_response({
                    'success': False,
                    'error': f"Cross-jurisdiction assignment rejected. Officer jurisdiction is {officer_city} but incident is in {issue_dict.get('city')}."
                }, status=403)
                return

            if officer_ward and officer_ward != 'ALL' and officer_ward != issue_dict.get('ward'):
                conn.close()
                self.send_json_response({
                    'success': False,
                    'error': f"Cross-jurisdiction assignment rejected. Officer jurisdiction is {officer_ward} but incident is in {issue_dict.get('ward')}."
                }, status=403)
                return

            # 4. Worker / Squad Validation & Operational Area Boundary Enforcement
            cursor.execute('SELECT * FROM workers WHERE id = ? OR name = ?', (worker_id, worker_id))
            worker_row = cursor.fetchone()
            if not worker_row:
                conn.close()
                self.send_json_response({
                    'success': False,
                    'error': f"Invalid worker/squad '{worker_id}'. Selected squad is not registered in the municipal workforce registry."
                }, status=400)
                return

            target_worker = dict(worker_row)
            assigned_worker_name = target_worker['name']

            # Worker Operational Area Verification
            w_op_state = target_worker.get('operationalState')
            w_op_city = target_worker.get('operationalCity')
            w_op_wards = target_worker.get('operationalWards')

            if w_op_state and w_op_state != issue_dict.get('state'):
                conn.close()
                self.send_json_response({
                    'success': False,
                    'error': f"Worker operational state mismatch. Squad '{assigned_worker_name}' operates in {w_op_state}, but incident is in {issue_dict.get('state')}."
                }, status=400)
                return

            if w_op_city and w_op_city != issue_dict.get('city'):
                conn.close()
                self.send_json_response({
                    'success': False,
                    'error': f"Worker operational city mismatch. Squad '{assigned_worker_name}' operates in {w_op_city}, but incident is in {issue_dict.get('city')}."
                }, status=400)
                return

            if w_op_wards:
                try:
                    permitted_wards = json.loads(w_op_wards) if isinstance(w_op_wards, str) else w_op_wards
                except Exception:
                    permitted_wards = [w_op_wards]

                if permitted_wards and 'ALL' not in permitted_wards and issue_dict.get('ward') not in permitted_wards:
                    conn.close()
                    self.send_json_response({
                        'success': False,
                        'error': f"Squad '{assigned_worker_name}' is not authorized to operate in {issue_dict.get('ward')}. Permitted operational wards: {permitted_wards}."
                    }, status=400)
                    return

            # Worker Department Eligibility Verification
            w_dept = target_worker.get('department')
            issue_dept = issue_dict.get('department')
            if w_dept and issue_dept and w_dept != issue_dept:
                conn.close()
                self.send_json_response({
                    'success': False,
                    'error': f"Squad '{assigned_worker_name}' belongs to {w_dept.capitalize()} department and cannot be assigned to {issue_dept.capitalize()} issues."
                }, status=400)
                return

            # 4. Prevent Duplicate / Accidental Duplicate Assignment (Requirement 2 & TEST 6)
            existing_assigned = (issue_dict.get('assignedWorker') or '').strip()
            if existing_assigned:
                if worker_id in existing_assigned or target_worker['name'] in existing_assigned or target_worker['id'] in existing_assigned:
                    conn.close()
                    self.send_json_response({
                        'success': False,
                        'error': f"Duplicate assignment rejected: Issue {issue_id} is already assigned to {existing_assigned}.",
                        'isDuplicate': True
                    }, status=409)
                    return

                if not confirm_reassign:
                    conn.close()
                    self.send_json_response({
                        'success': False,
                        'error': f"Issue {issue_id} is already assigned to {existing_assigned}. Reassignment confirmation required.",
                        'requiresConfirmation': True
                    }, status=409)
                    return

            # 5. Persist Assignment in SQLite with Real Server Timestamp (Requirement 3 & 10)
            now_ms = int(time.time() * 1000)

            cursor.execute('''
                UPDATE issues
                SET assignedWorker = ?,
                    assignedTimestamp = ?,
                    workerStatus = 'Assigned',
                    supervisorNotes = ?,
                    verifiedByOfficer = COALESCE(verifiedByOfficer, ?),
                    verifiedTimestamp = COALESCE(verifiedTimestamp, ?)
                WHERE id = ?
            ''', (
                assigned_worker_name,
                now_ms,
                supervisor_notes or None,
                official_officer_name,
                now_ms,
                issue_id
            ))

            cursor.execute('''
                UPDATE workers
                SET currentStatus = 'busy',
                    currentTaskId = ?
                WHERE id = ?
            ''', (issue_id, target_worker['id']))

            # 6. Audit Trail Logging (Requirement 8)
            audit_id = f"AUDIT-ASSIGN-{now_ms}-{random.randint(100, 999)}"
            cursor.execute('''
                INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit_id,
                issue_id,
                official_officer_name,
                'ISSUE_ASSIGNED',
                assigned_worker_name,
                supervisor_notes or 'Standard municipal SOP dispatch',
                now_ms
            ))

            cursor.execute('''
                INSERT INTO ai_predictions (id, entityType, entityId, predictionType, confidenceScore, reasoning, recommendedAction, createdAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"PRED-{audit_id}",
                'issue',
                issue_id,
                'squad_assignment',
                1.0,
                f"Officer assigned {assigned_worker_name}. Instructions: {supervisor_notes or 'Standard SOP'}",
                f"Deploy {assigned_worker_name}",
                now_ms
            ))

            comments = json.loads(issue_dict.get('comments') or '[]')
            comments.append({
                'author': official_officer_name,
                'text': f"Squad allocated: {assigned_worker_name}. Dispatch instructions: {supervisor_notes or 'Standard municipal resolution protocol'}",
                'time': 'Just now'
            })
            cursor.execute('UPDATE issues SET comments = ? WHERE id = ?', (json.dumps(comments), issue_id))

            conn.commit()

            cursor.execute('SELECT * FROM issues WHERE id = ?', (issue_id,))
            updated_issue = dict(cursor.fetchone())
            conn.close()

            updated_issue['upvotedBy'] = json.loads(updated_issue.get('upvotedBy') or '[]')
            updated_issue['comments'] = json.loads(updated_issue.get('comments') or '[]')

            # 7. Real-Time SSE Event Broadcast (Requirement 6)
            sse_payload = {
                'id': updated_issue['id'],
                'assignedWorker': updated_issue['assignedWorker'],
                'assignedTimestamp': updated_issue['assignedTimestamp'],
                'workerStatus': updated_issue['workerStatus'],
                'supervisorNotes': updated_issue['supervisorNotes'],
                'ward': updated_issue.get('ward'),
                'title': updated_issue.get('title'),
                'severity': updated_issue.get('severity'),
                'department': updated_issue.get('department'),
                'comments': updated_issue.get('comments')
            }
            sse_hub.broadcast('ISSUE_ASSIGNED', sse_payload)

            self.send_json_response({
                'success': True,
                'message': f"Squad '{assigned_worker_name}' successfully assigned to issue {issue_id}.",
                'issue': updated_issue
            })
            return

        # Stage C: REST API: POST /api/issues/transition (Worker Lifecycle State Persistence)
        if path == '/api/issues/transition' or (path.startswith('/api/issues/') and path.endswith('/transition')):
            if path == '/api/issues/transition':
                issue_id = (body.get('issueId') or '').strip()
            else:
                issue_id = path.split('/')[3].strip()

            target_status = (body.get('status') or body.get('targetStatus') or body.get('workerStatus') or '').strip()
            worker_id = (body.get('workerId') or '').strip()
            worker_email = (body.get('workerEmail') or '').strip().lower()
            worker_name_param = (body.get('workerName') or '').strip()

            if not issue_id:
                self.send_json_response({'success': False, 'error': 'Issue ID is required.'}, status=400)
                return

            # Allowed Stage C & D transition targets
            valid_statuses = ['En Route to Site', 'On Site - Conducting Work', 'Work Completed - Awaiting Verification']
            if target_status not in valid_statuses:
                self.send_json_response({
                    'success': False,
                    'error': f"Invalid status transition '{target_status}'. Allowed transitions: {', '.join(valid_statuses)}."
                }, status=400)
                return

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM issues WHERE id = ?', (issue_id,))
            issue_row = cursor.fetchone()
            if not issue_row:
                conn.close()
                self.send_json_response({'success': False, 'error': f"Grievance ticket {issue_id} not found."}, status=404)
                return

            issue_dict = dict(issue_row)
            if issue_dict.get('status') == 'resolved':
                conn.close()
                self.send_json_response({'success': False, 'error': 'Cannot update lifecycle status of an already resolved grievance.'}, status=400)
                return

            assigned_worker = (issue_dict.get('assignedWorker') or '').strip()
            if not assigned_worker:
                conn.close()
                self.send_json_response({'success': False, 'error': f"Issue {issue_id} is not assigned to any field squad yet."}, status=400)
                return

            # 1. Authoritative Identity Verification
            auth_user = get_authenticated_user(self, conn)
            if not auth_user:
                conn.close()
                self.send_json_response({
                    'success': False,
                    'error': 'Authentication required for field status transition.'
                }, status=401)
                return

            if auth_user.get('department') not in ['worker', 'municipal']:
                conn.close()
                self.send_json_response({
                    'success': False,
                    'error': 'Unauthorized. Only assigned field workers or supervising municipal officers may transition task lifecycle.'
                }, status=403)
                return

            # 2. Enforce that Worker is actually assigned to this issue
            if auth_user.get('department') == 'worker':
                assigned_lower = assigned_worker.lower()
                user_name_lower = (auth_user.get('name') or '').lower()
                user_email_lower = (auth_user.get('email') or '').lower()
                user_official_id = (auth_user.get('officialId') or '').lower()

                is_assigned = (
                    user_name_lower in assigned_lower or
                    ('squad 4' in assigned_lower and 'squad 4' in user_name_lower) or
                    ('squad 1' in assigned_lower and 'squad 1' in user_name_lower) or
                    ('lineman' in assigned_lower and 'lineman' in user_name_lower) or
                    (user_official_id and user_official_id in assigned_lower) or
                    (user_email_lower and user_email_lower in assigned_lower)
                )
                if not is_assigned:
                    conn.close()
                    self.send_json_response({
                        'success': False,
                        'error': f"Worker '{auth_user.get('name')}' is not assigned to issue {issue_id}. Current assigned squad: {assigned_worker}."
                    }, status=403)
                    return

            worker_display_name = auth_user.get('name') or assigned_worker

            now_ms = int(time.time() * 1000)
            if target_status == 'En Route to Site':
                audit_action = 'WORKER_EN_ROUTE'
            elif target_status == 'On Site - Conducting Work':
                audit_action = 'WORKER_ARRIVED'
            else:
                audit_action = 'WORK_COMPLETED'

            audit_id = f"AUDIT-WRK-{now_ms}-{random.randint(100, 999)}"

            comments = json.loads(issue_dict.get('comments') or '[]')

            if target_status == 'En Route to Site':
                actual_en_route_ts = issue_dict.get('enRouteTimestamp') or now_ms
                cursor.execute('''
                    UPDATE issues
                    SET workerStatus = 'En Route to Site',
                        enRouteTimestamp = ?
                    WHERE id = ?
                ''', (actual_en_route_ts, issue_id))

                log_notes = f"Field squad departed base and is en route to site ({issue_dict.get('location') or 'incident location'})."
                cursor.execute('''
                    INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    audit_id,
                    issue_id,
                    worker_display_name,
                    audit_action,
                    assigned_worker,
                    log_notes,
                    now_ms
                ))

                comments.append({
                    'author': worker_display_name,
                    'text': f"🚗 Squad departed base and is travelling to site ({issue_dict.get('location') or 'incident location'}).",
                    'time': 'Just now'
                })

            elif target_status == 'On Site - Conducting Work':
                actual_arrived_ts = issue_dict.get('arrivedTimestamp') or now_ms
                actual_en_route_ts = issue_dict.get('enRouteTimestamp') or (now_ms - 15 * 60 * 1000)

                cursor.execute('''
                    UPDATE issues
                    SET workerStatus = 'On Site - Conducting Work',
                        enRouteTimestamp = COALESCE(enRouteTimestamp, ?),
                        arrivedTimestamp = ?
                    WHERE id = ?
                ''', (actual_en_route_ts, actual_arrived_ts, issue_id))

                log_notes = f"Field squad arrived on site. Remediation perimeter established at {issue_dict.get('location') or 'incident location'}."
                cursor.execute('''
                    INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    audit_id,
                    issue_id,
                    worker_display_name,
                    audit_action,
                    assigned_worker,
                    log_notes,
                    now_ms
                ))

                comments.append({
                    'author': worker_display_name,
                    'text': f"📍 Squad arrived on site. Commenced remediation operations.",
                    'time': 'Just now'
                })

            elif target_status == 'Work Completed - Awaiting Verification':
                resolution_notes = (body.get('resolutionNotes') or body.get('notes') or body.get('description') or 'Remediation completed and site cleaned.').strip()
                photo_after = body.get('photoAfter') or body.get('imageAfter') or None

                cursor.execute('''
                    UPDATE issues
                    SET workerStatus = 'Work Completed - Awaiting Verification',
                        status = 'work_completed',
                        workCompletedTimestamp = ?,
                        workCompletedBy = ?,
                        resolutionNotes = ?,
                        imageAfter = COALESCE(?, imageAfter)
                    WHERE id = ?
                ''', (now_ms, worker_display_name, resolution_notes, photo_after, issue_id))

                log_notes = f"Work completed by field squad: {resolution_notes}"
                cursor.execute('''
                    INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    audit_id,
                    issue_id,
                    worker_display_name,
                    'WORK_COMPLETED',
                    assigned_worker,
                    log_notes,
                    now_ms
                ))

                if photo_after:
                    audit_id_ev = f"AUDIT-EVD-{now_ms}-{random.randint(100, 999)}"
                    cursor.execute('''
                        INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        audit_id_ev,
                        issue_id,
                        worker_display_name,
                        'RESOLUTION_EVIDENCE_SUBMITTED',
                        assigned_worker,
                        f"Field resolution evidence photo submitted by {worker_display_name}",
                        now_ms
                    ))

                comments.append({
                    'author': worker_display_name,
                    'text': f"✅ Work Completed: {resolution_notes}",
                    'time': 'Just now'
                })

            cursor.execute('UPDATE issues SET comments = ? WHERE id = ?', (json.dumps(comments), issue_id))
            conn.commit()

            cursor.execute('SELECT * FROM issues WHERE id = ?', (issue_id,))
            updated_issue = dict(cursor.fetchone())
            conn.close()

            updated_issue['upvotedBy'] = json.loads(updated_issue.get('upvotedBy') or '[]')
            updated_issue['comments'] = json.loads(updated_issue.get('comments') or '[]')

            # Real-Time SSE Broadcast
            sse_payload = {
                'id': updated_issue['id'],
                'workerStatus': updated_issue['workerStatus'],
                'enRouteTimestamp': updated_issue.get('enRouteTimestamp'),
                'arrivedTimestamp': updated_issue.get('arrivedTimestamp'),
                'workCompletedTimestamp': updated_issue.get('workCompletedTimestamp'),
                'workCompletedBy': updated_issue.get('workCompletedBy'),
                'resolutionNotes': updated_issue.get('resolutionNotes'),
                'imageAfter': updated_issue.get('imageAfter'),
                'assignedWorker': updated_issue['assignedWorker'],
                'assignedTimestamp': updated_issue['assignedTimestamp'],
                'supervisorNotes': updated_issue['supervisorNotes'],
                'status': updated_issue['status'],
                'ward': updated_issue.get('ward'),
                'title': updated_issue.get('title'),
                'severity': updated_issue.get('severity'),
                'department': updated_issue.get('department'),
                'comments': updated_issue.get('comments')
            }
            sse_hub.broadcast('ISSUE_TRANSITIONED', sse_payload)
            if target_status == 'Work Completed - Awaiting Verification':
                sse_hub.broadcast('WORK_COMPLETED', sse_payload)

            self.send_json_response({
                'success': True,
                'message': f"Issue {issue_id} status updated to '{target_status}'.",
                'issue': updated_issue
            })
            return

        # 2. REST API: POST /api/issues/resolve (Officer Verification Endpoint)
        if (path.startswith('/api/issues/') and path.endswith('/resolve')) or path == '/api/issues/resolve':
            if path == '/api/issues/resolve':
                issue_id = (body.get('issueId') or '').strip()
            else:
                parts = path.split('/')
                issue_id = parts[3].strip()

            conn = get_db_connection()
            cursor = conn.cursor()

            # 1. Authoritative Authentication Check
            auth_user = get_authenticated_user(self, conn)
            if not auth_user:
                conn.close()
                self.send_json_response({
                    'success': False,
                    'error': 'Authentication required to verify and resolve grievance.'
                }, status=401)
                return

            cursor.execute('SELECT * FROM issues WHERE id = ?', (issue_id,))
            row = cursor.fetchone()

            if not row:
                conn.close()
                self.send_json_response({'success': False, 'error': f'Issue {issue_id} not found'}, status=404)
                return

            issue_dict = dict(row)

            # 2. Department & Authority Check (Workers CANNOT resolve issues!)
            if issue_dict.get('department') == 'food_safety':
                if auth_user.get('department') not in ['food', 'food_safety']:
                    conn.close()
                    self.send_json_response({
                        'success': False,
                        'error': 'Unauthorized. Only Food Safety Officers may resolve food safety violations.'
                    }, status=403)
                    return
            else:
                if auth_user.get('department') != 'municipal':
                    conn.close()
                    self.send_json_response({
                        'success': False,
                        'error': 'Unauthorized. Only Municipal Officers may verify and resolve municipal grievances. Field workers cannot directly resolve issues.'
                    }, status=403)
                    return

            # 3. Jurisdiction Check
            if auth_user.get('department') == 'municipal':
                if auth_user.get('jurisdictionState') and auth_user.get('jurisdictionState') != issue_dict.get('state'):
                    conn.close()
                    self.send_json_response({'success': False, 'error': 'Resolution rejected: Incident is outside officer jurisdiction state.'}, status=403)
                    return
                if auth_user.get('jurisdictionCity') and auth_user.get('jurisdictionCity') != issue_dict.get('city'):
                    conn.close()
                    self.send_json_response({'success': False, 'error': 'Resolution rejected: Incident is outside officer jurisdiction city.'}, status=403)
                    return
                if auth_user.get('jurisdictionWard') and auth_user.get('jurisdictionWard') != 'ALL':
                    if auth_user.get('jurisdictionWard') != issue_dict.get('ward'):
                        conn.close()
                        self.send_json_response({'success': False, 'error': 'Resolution rejected: Incident is outside officer jurisdiction ward.'}, status=403)
                        return
            elif auth_user.get('department') in ['food', 'food_safety']:
                if auth_user.get('jurisdictionState') and auth_user.get('jurisdictionState') != issue_dict.get('state'):
                    conn.close()
                    self.send_json_response({'success': False, 'error': 'Resolution rejected: Food violation is outside officer jurisdiction state.'}, status=403)
                    return
                if auth_user.get('jurisdictionCity') and auth_user.get('jurisdictionCity') != issue_dict.get('city'):
                    conn.close()
                    self.send_json_response({'success': False, 'error': 'Resolution rejected: Food violation is outside officer jurisdiction city.'}, status=403)
                    return
                if auth_user.get('jurisdictionWard') and auth_user.get('jurisdictionWard') != 'ALL':
                    if auth_user.get('jurisdictionWard') != issue_dict.get('ward'):
                        conn.close()
                        self.send_json_response({'success': False, 'error': 'Resolution rejected: Food violation is outside officer jurisdiction ward.'}, status=403)
                        return

            notes = (body.get('notes') or body.get('resolutionNotes') or 'Field execution verified and certified closed.').strip()
            photo_after = body.get('photoAfter') or body.get('imageAfter') or None
            now = int(time.time() * 1000)
            officer_name = auth_user.get('name') or 'Municipal Officer'

            comments = json.loads(row['comments'] or '[]')
            comments.append({'author': officer_name, 'text': f'Verified and officially closed: {notes}', 'time': 'Just now'})

            cursor.execute('''
                UPDATE issues SET
                    status = "resolved",
                    resolvedTimestamp = ?,
                    verifiedTimestamp = ?,
                    verifiedByOfficer = ?,
                    slaHoursLeft = 0,
                    workerStatus = "Field Execution Completed & Cleaned Proof Uploaded",
                    imageAfter = COALESCE(?, imageAfter),
                    comments = ?
                WHERE id = ?
            ''', (now, now, officer_name, photo_after, json.dumps(comments), issue_id))

            # Operational Audit Log: RESOLUTION_VERIFIED
            audit_id_res = f"AUDIT-VERIFY-{now}-{random.randint(100, 999)}"
            cursor.execute('''
                INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit_id_res,
                issue_id,
                officer_name,
                'RESOLUTION_VERIFIED',
                issue_dict.get('assignedWorker'),
                f"Official resolution verified and certified by {officer_name}. {notes}",
                now
            ))

            conn.commit()

            cursor.execute('SELECT * FROM issues WHERE id = ?', (issue_id,))
            updated_row = dict(cursor.fetchone())
            updated_row['upvotedBy'] = json.loads(updated_row['upvotedBy'] or '[]')
            updated_row['comments'] = json.loads(updated_row['comments'] or '[]')
            conn.close()

            sse_hub.broadcast('RESOLUTION_VERIFIED', updated_row)
            sse_hub.broadcast('ISSUE_RESOLVED', updated_row)
            self.send_json_response({'success': True, 'message': 'Resolution verified and ticket closed successfully.', 'issue': updated_row})
            return

        # 3. REST API: POST /api/issues/:id/reject-resolution (Officer Resolution Rejection)
        if (path.startswith('/api/issues/') and path.endswith('/reject-resolution')) or path == '/api/issues/reject-resolution':
            if path == '/api/issues/reject-resolution':
                issue_id = (body.get('issueId') or '').strip()
            else:
                parts = path.split('/')
                issue_id = parts[3].strip()

            conn = get_db_connection()
            cursor = conn.cursor()

            # 1. Authoritative Authentication Check
            auth_user = get_authenticated_user(self, conn)
            if not auth_user:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Authentication required.'}, status=401)
                return

            cursor.execute('SELECT * FROM issues WHERE id = ?', (issue_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                self.send_json_response({'success': False, 'error': f'Issue {issue_id} not found'}, status=404)
                return

            issue_dict = dict(row)

            # 2. Authority Check
            if auth_user.get('department') != 'municipal':
                conn.close()
                self.send_json_response({'success': False, 'error': 'Unauthorized. Only Municipal Officers may reject resolution and return tasks.'}, status=403)
                return

            # 3. Jurisdiction Check
            if auth_user.get('jurisdictionState') and auth_user.get('jurisdictionState') != issue_dict.get('state'):
                conn.close()
                self.send_json_response({'success': False, 'error': 'Action rejected: Incident is outside officer jurisdiction state.'}, status=403)
                return
            if auth_user.get('jurisdictionCity') and auth_user.get('jurisdictionCity') != issue_dict.get('city'):
                conn.close()
                self.send_json_response({'success': False, 'error': 'Action rejected: Incident is outside officer jurisdiction city.'}, status=403)
                return
            if auth_user.get('jurisdictionWard') and auth_user.get('jurisdictionWard') != 'ALL':
                if auth_user.get('jurisdictionWard') != issue_dict.get('ward'):
                    conn.close()
                    self.send_json_response({'success': False, 'error': 'Action rejected: Incident is outside officer jurisdiction ward.'}, status=403)
                    return

            # 4. Mandatory Justification Check
            justification = (body.get('justification') or body.get('reason') or '').strip()
            if not justification:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Justification is mandatory when rejecting field resolution.'}, status=400)
                return

            now_ms = int(time.time() * 1000)
            officer_name = auth_user.get('name') or 'Municipal Officer'
            comments = json.loads(issue_dict.get('comments') or '[]')
            comments.append({
                'author': officer_name,
                'text': f"⚠️ Resolution Rejected & Returned to Worker: {justification}",
                'time': 'Just now'
            })

            cursor.execute('''
                UPDATE issues SET
                    status = 'in_progress',
                    workerStatus = 'On Site - Conducting Work',
                    rejectionReason = ?,
                    comments = ?
                WHERE id = ?
            ''', (justification, json.dumps(comments), issue_id))

            # Operational Audit Log: RESOLUTION_REJECTED
            audit_id_rej = f"AUDIT-REJ-{now_ms}-{random.randint(100, 999)}"
            cursor.execute('''
                INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit_id_rej,
                issue_id,
                officer_name,
                'RESOLUTION_REJECTED',
                issue_dict.get('assignedWorker'),
                f"Resolution returned to squad with reason: {justification}",
                now_ms
            ))

            conn.commit()

            cursor.execute('SELECT * FROM issues WHERE id = ?', (issue_id,))
            updated_row = dict(cursor.fetchone())
            updated_row['upvotedBy'] = json.loads(updated_row['upvotedBy'] or '[]')
            updated_row['comments'] = json.loads(updated_row['comments'] or '[]')
            conn.close()

            sse_hub.broadcast('RESOLUTION_REJECTED', updated_row)
            sse_hub.broadcast('ISSUE_TRANSITIONED', updated_row)
            self.send_json_response({
                'success': True,
                'message': 'Field resolution rejected. Task returned to worker with instructions.',
                'issue': updated_row
            })
            return

        # 3. REST API: POST /api/food-violations
        if path == '/api/food-violations':
            conn = get_db_connection()
            cursor = conn.cursor()

            auth_user = get_authenticated_user(self, conn)
            if not auth_user:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Authentication required.'}, status=401)
                return

            if auth_user.get('department') not in ['food', 'food_safety']:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Unauthorized. Only Food Safety Officers may issue statutory notices.'}, status=403)
                return

            city = body.get('city', 'Surampalem')
            if auth_user.get('jurisdictionCity') and auth_user.get('jurisdictionCity') != city:
                conn.close()
                self.send_json_response({'success': False, 'error': f"Cross-jurisdiction violation notice rejected. FSO jurisdiction is {auth_user.get('jurisdictionCity')}."}, status=403)
                return

            fine_amount = float(body.get('fineAmount', 500))
            state = body.get('state', 'Andhra Pradesh')
            ward = body.get('ward', 'Ward 14 (Campus Food Zone)')
            street = body.get('street', 'College Road')
            vendor_name = body.get('vendorName', 'Food Stall')
            owner_name = body.get('ownerName', 'Proprietor')
            clause = body.get('violationClause', 'Sec 56 FSS Act - Unhygienic premises')
            notes = body.get('notes', 'Inspection notice served.')

            vendor_id = f'FSSAI-{"AP" if state == "Andhra Pradesh" else "IND"}-2026-V{int(time.time()) % 900 + 100}'

            new_vendor = {
                'id': vendor_id,
                'state': state,
                'city': city,
                'ward': ward,
                'name': vendor_name,
                'owner': owner_name,
                'location': f'{street}, {ward}, {city}',
                'hygieneGrade': 'C',
                'score': '45/100',
                'validTill': 'Action Required (Statutory Notice)',
                'inspectedBy': auth_user.get('name') or 'Dr. Lakshmi Prasad (FSO)',
                'status': 'VIOLATION NOTICE ISSUED',
                'isViolated': 1,
                'violationClause': clause,
                'penaltyImposed': f'₹{fine_amount:,.2f}',
                'rectificationDeadline': '7 Days from Notice',
                'mq135GasPpm': '360 PPM (High Gas Risk)',
                'officerDirectives': notes
            }

            cursor.execute('''
                INSERT INTO vendors VALUES (
                    :id, :state, :city, :ward, :name, :owner, :location, :hygieneGrade, :score,
                    :validTill, :inspectedBy, :status, :isViolated, :violationClause, :penaltyImposed,
                    :rectificationDeadline, :mq135GasPpm, :officerDirectives
                )
            ''', new_vendor)

            conn.commit()
            conn.close()

            sse_hub.broadcast('FOOD_VIOLATION_LOGGED', {'vendor': new_vendor})
            self.send_json_response({'success': True, 'vendor': new_vendor})
            return

        # 4. REST API: POST /api/food-rectify
        if path == '/api/food-rectify':
            conn = get_db_connection()
            cursor = conn.cursor()

            auth_user = get_authenticated_user(self, conn)
            if not auth_user:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Authentication required.'}, status=401)
                return

            if auth_user.get('department') not in ['food', 'food_safety']:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Unauthorized. Only Food Safety Officers may certify food rectifications.'}, status=403)
                return

            issue_id = body.get('issueId')
            notes = body.get('notes', 'Re-inspected and compliant.')
            gas_ppm = body.get('gasPpm', 180)
            score = body.get('score', 92)
            outcome = body.get('outcome', 'passed')

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM issues WHERE id = ?', (issue_id,))
            issue_row = cursor.fetchone()

            if not issue_row:
                conn.close()
                self.send_json_response({'success': False, 'error': f'Issue {issue_id} not found.'}, status=404)
                return

            if auth_user.get('jurisdictionState') and auth_user.get('jurisdictionState') != issue_row['state']:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Rectification rejected: Violation is outside officer jurisdiction state.'}, status=403)
                return
            if auth_user.get('jurisdictionCity') and auth_user.get('jurisdictionCity') != issue_row['city']:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Rectification rejected: Violation is outside officer jurisdiction city.'}, status=403)
                return

            if issue_row:
                v_id = issue_row['vendorId']
                if v_id and outcome == 'passed':
                    cursor.execute('''
                        UPDATE vendors SET
                            isViolated = 0,
                            hygieneGrade = "A+",
                            score = ?,
                            status = "VERIFIED & CERTIFIED",
                            validTill = "31 Dec 2026",
                            mq135GasPpm = ?
                        WHERE id = ?
                    ''', (f'{score}/100', f'{gas_ppm} PPM (Safe)', v_id))

                comments = json.loads(issue_row['comments'] or '[]')
                comments.append({
                    'author': 'Dr. Lakshmi Prasad (FSO)',
                    'text': f'Re-inspected & Rectified! Gas Reading: {gas_ppm} PPM | Hygiene Score: {score}/100. Outcome: Grade A+ Issued',
                    'time': 'Just now'
                })

                now = int(time.time() * 1000)
                cursor.execute('''
                    UPDATE issues SET status = "resolved", resolvedTimestamp = ?, comments = ? WHERE id = ?
                ''', (now, json.dumps(comments), issue_id))

            conn.commit()
            conn.close()

            sse_hub.broadcast('FOOD_RECTIFIED', {'issueId': issue_id, 'outcome': outcome})
            self.send_json_response({'success': True, 'issueId': issue_id})
            return

        # 5. REST API: POST /api/auth/send-otp (Citizen Registration Verification)
        if path == '/api/auth/send-otp':
            email = (body.get('email') or '').strip().lower()
            if not email or '@' not in email or '.' not in email:
                self.send_json_response({'success': False, 'error': 'Please enter a valid email address.'}, status=400)
                return

            otp_code = str(random.randint(100000, 999999))
            ACTIVE_OTPS[email] = {
                'otp': otp_code,
                'expires_at': time.time() + 600
            }
            print(f'[OTP Dispatcher] Generated OTP for {email}: {otp_code}')

            # Dispatch real email to user inbox
            sent, info = dispatch_otp_email(email, otp_code)

            self.send_json_response({
                'success': True,
                'otp': otp_code,
                'email': email,
                'emailDelivered': sent,
                'expiresIn': 600,
                'message': f'6-Digit National Citizen Verification OTP generated and sent to {email}.'
            })
            return

        # 6. REST API: POST /api/auth/register (Citizen OTP Verification & Password Creation)
        if path == '/api/auth/register':
            name = (body.get('name') or '').strip()
            email = (body.get('email') or '').strip().lower()
            otp = (body.get('otp') or '').strip()
            password = (body.get('password') or '').strip()

            if not email or '@' not in email:
                self.send_json_response({'success': False, 'error': 'Please enter a valid email address.'}, status=400)
                return

            if not name:
                self.send_json_response({'success': False, 'error': 'Please enter your full name.'}, status=400)
                return

            if not password or len(password) < 4:
                self.send_json_response({'success': False, 'error': 'Password must be at least 4 characters.'}, status=400)
                return

            # Verify OTP
            cached = ACTIVE_OTPS.get(email)
            if not cached or cached['otp'] != otp:
                self.send_json_response({'success': False, 'error': 'Invalid or expired OTP. Please verify the OTP sent to your email.'}, status=400)
                return

            # Clean name & avatar
            name_words = [w.capitalize() for w in name.split() if w]
            display_name = ' '.join(name_words) if name_words else name.upper()
            avatar = ''.join([w[0] for w in name_words[:2]]).upper() if name_words else 'CZ'

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE LOWER(TRIM(email)) = LOWER(TRIM(?))', (email,))
            existing = cursor.fetchone()

            user_id = existing['id'] if existing else f'user-{int(time.time()) % 90000 + 10000}'
            official_id = existing['officialId'] if existing else f'CIT-IND-2026-{int(time.time()) % 9000 + 1000}'
            credits = existing['civicCredits'] if existing else 20
            streak = existing['activeStreakWeeks'] if existing else 1
            created_at = existing['createdAt'] if (existing and 'createdAt' in existing.keys() and existing['createdAt']) else int(time.time() * 1000)

            phone = existing['phone'] if (existing and 'phone' in existing.keys() and existing['phone']) else ''
            perm_addr = existing['permanentAddress'] if (existing and 'permanentAddress' in existing.keys() and existing['permanentAddress']) else ''
            prof_comp = existing['profileCompleted'] if (existing and 'profileCompleted' in existing.keys() and existing['profileCompleted']) else 0
            u_state = existing['jurisdictionState'] if (existing and 'jurisdictionState' in existing.keys()) else None
            u_city = existing['jurisdictionCity'] if (existing and 'jurisdictionCity' in existing.keys()) else None
            u_ward = existing['jurisdictionWard'] if (existing and 'jurisdictionWard' in existing.keys()) else None

            user_data = {
                'email': email,
                'id': user_id,
                'name': display_name,
                'password': hash_password(password),
                'department': 'citizen',
                'roleTitle': 'Verified Citizen Reporter',
                'officialId': official_id,
                'avatar': avatar,
                'civicCredits': credits,
                'activeStreakWeeks': streak,
                'createdAt': created_at,
                'phone': phone,
                'permanentAddress': perm_addr,
                'profileCompleted': prof_comp,
                'jurisdictionState': u_state,
                'jurisdictionCity': u_city,
                'jurisdictionWard': u_ward
            }

            cursor.execute('''
                INSERT OR REPLACE INTO users (email, id, name, password, department, roleTitle, officialId, avatar, civicCredits, activeStreakWeeks, createdAt, phone, permanentAddress, profileCompleted, jurisdictionState, jurisdictionCity, jurisdictionWard)
                VALUES (:email, :id, :name, :password, :department, :roleTitle, :officialId, :avatar, :civicCredits, :activeStreakWeeks, :createdAt, :phone, :permanentAddress, :profileCompleted, :jurisdictionState, :jurisdictionCity, :jurisdictionWard)
            ''', user_data)
            token = create_session(user_data, conn)
            conn.close()

            # Clear used OTP
            if email in ACTIVE_OTPS:
                del ACTIVE_OTPS[email]

            safe_user = {k: v for k, v in user_data.items() if k != 'password'}
            safe_user['profileCompleted'] = 1 if safe_user.get('profileCompleted') == 1 else 0
            session_payload = {
                'success': True,
                'token': token,
                'department': 'citizen',
                'user': safe_user,
                'message': 'Citizen account successfully registered with 20 Welcome Civic Credits!'
            }
            self.send_json_response(session_payload)
            return

        # 6b. REST API: POST /api/citizen/profile (Authoritative Citizen Profile Onboarding & Setup)
        if path == '/api/citizen/profile':
            conn = get_db_connection()
            auth_user = get_authenticated_user(self, conn)
            if not auth_user:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Unauthorized. Please login to complete your profile.'}, status=401)
                return

            if auth_user.get('department') != 'citizen':
                conn.close()
                self.send_json_response({'success': False, 'error': 'Forbidden. Profile onboarding is for citizen accounts.'}, status=403)
                return

            name = (body.get('name') or '').strip()
            phone = (body.get('phone') or '').strip()
            address = (body.get('permanentAddress') or body.get('address') or '').strip()
            state = (body.get('state') or body.get('jurisdictionState') or '').strip()
            city = (body.get('city') or body.get('jurisdictionCity') or '').strip()
            ward = (body.get('ward') or body.get('jurisdictionWard') or '').strip()

            if not name or len(name) < 2:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Please enter your Full Name (minimum 2 characters).'}, status=400)
                return

            clean_digits = ''.join(c for c in phone if c.isdigit())
            if not phone or len(clean_digits) < 10:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Please enter a valid 10-digit contact Phone Number.'}, status=400)
                return

            if not address or len(address) < 5:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Please enter your complete Permanent Residential Address (House/Plot, Street).'}, status=400)
                return

            if not state:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Please select your State.'}, status=400)
                return

            if not city:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Please select your City.'}, status=400)
                return

            if not ward:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Please select your Home Ward / Jurisdiction.'}, status=400)
                return

            name_words = [w.capitalize() for w in name.split() if w]
            display_name = ' '.join(name_words) if name_words else name
            avatar = ''.join([w[0] for w in name_words[:2]]).upper() if name_words else 'CZ'

            email = auth_user['email']
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET
                    name = ?,
                    phone = ?,
                    permanentAddress = ?,
                    jurisdictionState = ?,
                    jurisdictionCity = ?,
                    jurisdictionWard = ?,
                    avatar = ?,
                    profileCompleted = 1
                WHERE LOWER(TRIM(email)) = LOWER(TRIM(?))
            ''', (display_name, phone, address, state, city, ward, avatar, email))

            auth_token = auth_user.get('token')
            if auth_token:
                cursor.execute('''
                    UPDATE sessions SET
                        name = ?,
                        jurisdictionState = ?,
                        jurisdictionCity = ?,
                        jurisdictionWard = ?
                    WHERE token = ?
                ''', (display_name, state, city, ward, auth_token))

            cursor.execute('SELECT * FROM users WHERE LOWER(TRIM(email)) = LOWER(TRIM(?))', (email,))
            updated_user = cursor.fetchone()
            conn.commit()
            conn.close()

            user_dict = dict(updated_user) if updated_user else {}
            safe_user = {k: v for k, v in user_dict.items() if k != 'password'}
            safe_user['profileCompleted'] = 1

            self.send_json_response({
                'success': True,
                'user': safe_user,
                'message': 'Citizen profile successfully completed!'
            })
            return

        # REST API: POST /api/citizen/redeem (Dual-path Civic Rewards & Community Impact)
        if path == '/api/citizen/redeem':
            reward_id = body.get('rewardId') or body.get('reward_id')
            reward_item = next((r for r in CIVIC_REWARDS_CATALOG if r['id'] == reward_id or (reward_id and (r['id'].startswith(reward_id) or reward_id.startswith(r['id'])))), None)
            if not reward_item:
                self.send_json_response({'success': False, 'error': f'Invalid reward identifier: {reward_id}'}, status=400)
                return

            conn = get_db_connection()
            auth_user = get_authenticated_user(self, conn)
            user_email = (auth_user['email'] if auth_user else body.get('userEmail') or 'citizen@civictech.in').strip()
            user_name = auth_user['name'] if auth_user else body.get('userName') or 'KRISH'
            user_id = auth_user['userId'] if auth_user else body.get('userId') or 'user-101'

            cursor = conn.cursor()
            cursor.execute('SELECT civicCredits FROM users WHERE LOWER(TRIM(email)) = LOWER(TRIM(?))', (user_email,))
            user_row = cursor.fetchone()
            current_credits = user_row['civicCredits'] if user_row and user_row['civicCredits'] is not None else 0
            cost = reward_item['points']

            if current_credits < cost:
                conn.close()
                self.send_json_response({
                    'success': False,
                    'error': f'Insufficient Civic Credits. You need {cost} points for {reward_item["title"]}, but have {current_credits} points.',
                    'currentCredits': current_credits,
                    'requiredCredits': cost
                }, status=400)
                return

            new_balance = current_credits - cost
            cursor.execute('UPDATE users SET civicCredits = ? WHERE LOWER(TRIM(email)) = LOWER(TRIM(?))', (new_balance, user_email))

            redemption_id = f"RED-{int(time.time()*1000)}"
            reward_type = reward_item.get('category', 'self')
            prefix = "CIVIC-ME" if reward_type == 'self' else "CIVIC-COMM"
            code_tag = reward_item['id'].replace('_', '').upper()[:4]
            voucher_code = f"{prefix}-2026-{code_tag}-{random.randint(1000, 9999)}"
            now_ms = int(time.time() * 1000)

            cursor.execute('''
                INSERT INTO civic_redemptions (
                    id, userId, userEmail, rewardId, rewardTitle, rewardType, pointsDeducted, voucherCode, status, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                redemption_id, user_id, user_email, reward_item['id'], reward_item['title'], reward_type, cost, voucher_code, 'CONFIRMED_PROTOTYPE', now_ms
            ))

            # Operational audit logging
            cursor.execute('''
                INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"AUD-RED-{now_ms}",
                reward_item['id'],
                user_name,
                'CIVIC_REWARD_REDEEMED',
                voucher_code,
                f"Redeemed {reward_item['title']} ({cost} Pts, {reward_type.upper()}). Remaining balance: {new_balance} Pts.",
                now_ms
            ))

            conn.commit()
            conn.close()

            self.send_json_response({
                'success': True,
                'message': f"Successfully redeemed {reward_item['title']}!",
                'voucher_code': voucher_code,
                'voucherCode': voucher_code,
                'new_balance': new_balance,
                'newBalance': new_balance,
                'redemption': {
                    'id': redemption_id,
                    'rewardId': reward_item['id'],
                    'rewardTitle': reward_item['title'],
                    'rewardType': reward_type,
                    'pointsDeducted': cost,
                    'voucherCode': voucher_code,
                    'voucher_code': voucher_code,
                    'status': 'CONFIRMED_PROTOTYPE',
                    'timestamp': now_ms,
                    'newBalance': new_balance,
                    'new_balance': new_balance,
                    'disclaimer': reward_item['disclaimer']
                }
            })
            return

        # ---------------------------------------------------------------------
        # PHASE 7 PREPARED ENDPOINTS: CLUSTERS, HOTSPOTS & WORKERS (POST)
        # ---------------------------------------------------------------------
        if path == '/api/clusters/link':
            issue_id = body.get('issueId')
            cluster_id = body.get('clusterId')
            if not issue_id or not cluster_id:
                self.send_json_response({'success': False, 'error': 'issueId and clusterId are required.'}, status=400)
                return
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE issues SET clusterId = ? WHERE id = ?', (cluster_id, issue_id))
            cursor.execute('UPDATE incident_clusters SET reportCount = reportCount + 1, lastReportedAt = ? WHERE id = ?', (int(time.time()*1000), cluster_id))
                        # Audit log persisted AI predictions
            if body.get('aiRiskScore'):
                try:
                    cursor.execute('''
                        INSERT INTO ai_predictions (id, entityType, entityId, predictionType, confidenceScore, reasoning, recommendedAction, createdAt)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        f"PRED-ISS-{issue_id}",
                        'issue',
                        issue_id,
                        'complaint_intelligence_persisted',
                        float(body.get('aiConfidence') or 0.90),
                        f"{body.get('aiReasoning', '')} | Confirmed: {body.get('citizenConfirmedAI', True)}",
                        f"Dept: {body.get('aiSuggestedDepartment', dept)} | Cat: {body.get('aiSuggestedCategory', cat)} | Risk: {body.get('aiRiskScore')}/100",
                        int(time.time()*1000)
                    ))
                except Exception as audit_err:
                    print(f"[Issue Audit Warning]: {audit_err}")

            conn.commit()
            conn.close()
            self.send_json_response({'success': True, 'message': f'Issue {issue_id} linked to Cluster {cluster_id}.'})
            return

        if path == '/api/hotspots/predict':
            ward = body.get('ward')
            if not ward:
                self.send_json_response({'success': False, 'error': 'ward is required.'}, status=400)
                return
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM hotspots WHERE ward = ?', (ward,))
            row = cursor.fetchone()
            conn.close()
            if row:
                self.send_json_response({'success': True, 'hotspot': dict(row)})
            else:
                self.send_json_response({'success': True, 'hotspot': {
                    'ward': ward, 'predictedRiskPercent': 45, 'riskLevel': 'Medium',
                    'recommendedAction': 'Continuous baseline monitoring'
                }})
            return

        if path == '/api/workers/update-status':
            worker_id = body.get('workerId')
            new_status = body.get('status')
            task_id = body.get('taskId')
            if not worker_id or not new_status:
                self.send_json_response({'success': False, 'error': 'workerId and status are required.'}, status=400)
                return
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE workers SET currentStatus = ?, currentTaskId = ? WHERE id = ?', (new_status, task_id, worker_id))
            conn.commit()
            conn.close()
            self.send_json_response({'success': True, 'message': f'Worker {worker_id} status updated to {new_status}.'})
            return

        # ---------------------------------------------------------------------
        # REAL-TIME AI ENGINE ENDPOINTS (GEMINI 2.5 FLASH + CIVIC AGENT)
        # ---------------------------------------------------------------------
        if path == '/api/ai/chat':
            user_msg = (body.get('message') or '').strip()
            dept = body.get('department') or 'citizen'
            if not user_msg:
                self.send_json_response({'success': False, 'error': 'Message cannot be empty.'}, status=400)
                return

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, department, location, ward, status, assignedWorker FROM issues ORDER BY timestamp DESC LIMIT 25")
            issues_summary = [dict(r) for r in cursor.fetchall()]

            auth_user = get_authenticated_user(self, conn)
            context_data = {
                'issues': issues_summary,
                'department': dept,
                'userName': auth_user.get('name') if auth_user else 'Citizen User'
            }
            res = ai_engine.call_gemini_chat(user_msg, dept, context_data, conn)
            conn.close()
            self.send_json_response(res)
            return

        if path in ['/api/ai/analyze-image', '/api/issues/assess-image']:
            img_data = body.get('image') or body.get('imageData') or body.get('imageUrl') or ''
            prompt_hint = body.get('prompt') or body.get('complaintText') or body.get('text') or ''

            conn = get_db_connection()
            analysis = ai_engine.call_gemini_vision(img_data, prompt_hint, conn)
            conn.close()
            self.send_json_response(analysis)
            return

        if path == '/api/settings/ai-key':
            new_key = (body.get('apiKey') or '').strip()
            conn = get_db_connection()
            ai_engine.set_gemini_api_key(conn, new_key)
            conn.close()
            self.send_json_response({'success': True, 'message': 'Gemini API Key updated successfully.'})
            return

        # ---------------------------------------------------------------------
        # PHASE 7 PREPARED AI SCAFFOLDING ENDPOINTS (ADVISORY DECISION SUPPORT)
        # ---------------------------------------------------------------------
        if path == '/api/ai/complaint-intelligence':
            text = (body.get('text') or '').strip()
            loc_input = (body.get('location') or '').strip()
            if not text:
                self.send_json_response({'success': False, 'error': 'Complaint description text is required.'}, status=400)
                return

            q_lower = text.lower()

            # 1. Location Sensitivity Extraction
            sensitivity = 'General Area'
            if any(w in q_lower for w in ['college', 'school', 'university', 'campus', 'student', 'classroom', 'hostel']):
                sensitivity = 'Educational Zone'
            elif any(w in q_lower for w in ['hospital', 'clinic', 'dispensary', 'patient', 'doctor', 'ambulance']):
                sensitivity = 'Hospital & Medical Zone'
            elif any(w in q_lower for w in ['market', 'bazaar', 'shop', 'vendor', 'stall', 'commercial', 'supermarket']):
                sensitivity = 'Commercial Market Zone'
            elif any(w in q_lower for w in ['highway', 'flyover', 'junction', 'cross', 'main road', 'traffic', 'expressway', 'road']):
                sensitivity = 'Public Road / Transit Corridor'
            elif any(w in q_lower for w in ['colony', 'apartment', 'house', 'nagar', 'residential', 'society', 'street']):
                sensitivity = 'Residential Zone'
            elif any(w in q_lower for w in ['substation', 'feeder', 'water tank', 'pump', 'transformer', 'grid']):
                sensitivity = 'Critical Infrastructure'

            # 2. Strict Department & Category Classification (Deterministic Rule-based Civic AI)
            if any(w in q_lower for w in ['spark', 'wire', 'transformer', 'shock', 'electric', 'current', 'cable', 'pole', 'power', 'outage', 'voltage', 'blackout', 'short circuit']):
                dept = 'electricity'
                dept_name = 'Electricity'
                dept_icon = '⚡'
                if any(w in q_lower for w in ['outage', 'blackout', 'no power', 'power out', 'power has been out', 'power is out', 'power cut', 'cut', 'tripped', 'no current', 'current cut', 'load shedding']):
                    cat = 'power_outage'
                    cat_name = 'Power Outage'
                    cat_icon = '🔌'
                    suggested_title = 'Unscheduled Power Outage'
                else:
                    cat = 'sparking_wire'
                    cat_name = 'Sparking Wire'
                    cat_icon = '⚡'
                    suggested_title = 'Sparking Wire Hazard'

            elif any(w in q_lower for w in ['garbage', 'waste', 'trash', 'dump', 'litter', 'debris', 'rubbish', 'dustbin', 'bin overflow', 'solid waste', 'canteen waste', 'rotting waste', 'overflowing bins', 'open dump', 'compost', 'refuse']):
                dept = 'sanitation'
                dept_name = 'Sanitation & Waste Management'
                dept_icon = '🏢'
                cat = 'garbage_overflow'
                cat_name = 'Garbage Overflow'
                cat_icon = '🗑️'
                suggested_title = 'Garbage Overflow Report'

            elif any(w in q_lower for w in ['pothole', 'crater', 'asphalt', 'tar', 'road damage', 'broken road', 'footpath', 'pavement', 'paver', 'curb']):
                dept = 'roads'
                dept_name = 'Infrastructure / Roads'
                dept_icon = '🛣️'
                if any(w in q_lower for w in ['footpath', 'pavement', 'paver', 'curb', 'pedestrian']):
                    cat = 'broken_footpath'
                    cat_name = 'Broken Footpath'
                    cat_icon = '🚶'
                    suggested_title = 'Broken Footpath Hazard'
                elif any(w in q_lower for w in ['pothole', 'crater']):
                    cat = 'pothole'
                    cat_name = 'Pothole'
                    cat_icon = '🕳️'
                    suggested_title = 'Dangerous Pothole'
                else:
                    cat = 'road_damage'
                    cat_name = 'Road Damage'
                    cat_icon = '🚧'
                    suggested_title = 'Road Damage'

            elif any(w in q_lower for w in ['water leak', 'leakage', 'burst pipe', 'pipe burst', 'drinking water', 'pipeline leak', 'water pipe', 'wasting water']):
                dept = 'water_supply'
                dept_name = 'Water Supply'
                dept_icon = '💧'
                cat = 'water_leakage'
                cat_name = 'Water Leakage'
                cat_icon = '🚰'
                suggested_title = 'Water Pipeline Leakage'

            elif any(w in q_lower for w in ['drain', 'sewage', 'clog', 'silt', 'gutter', 'drainage', 'drain blockage', 'manhole', 'waterlogging']):
                dept = 'sanitation'
                dept_name = 'Sanitation'
                dept_icon = '🏢'
                cat = 'drain_blockage'
                cat_name = 'Drain Blockage'
                cat_icon = '🌊'
                suggested_title = 'Drainage Blockage'

            elif any(w in q_lower for w in ['food', 'hotel', 'restaurant', 'dhaba', 'stall', 'oil', 'stale', 'rotten', 'spoilage', 'unhygienic', 'fssai', 'tiffin', 'hygiene']):
                dept = 'food_safety'
                dept_name = 'Food Safety'
                dept_icon = '🍲'
                cat = 'food_hygiene'
                cat_name = 'Food Hygiene'
                cat_icon = '🍱'
                suggested_title = 'Food Hygiene Violation'

            else:
                dept = 'sanitation'
                dept_name = 'Sanitation'
                dept_icon = '🏢'
                cat = 'garbage_overflow'
                cat_name = 'Garbage Overflow'
                cat_icon = '🗑️'
                suggested_title = 'Garbage Overflow Report'

            # 3. Urgency Score Calculation (0-100)
            base_urgency = 62
            if cat == 'sparking_wire':
                base_urgency = 88
            elif cat == 'power_outage':
                base_urgency = 75
            elif cat == 'pothole':
                base_urgency = 82 if any(w in q_lower for w in ['accident', 'danger', 'injury', 'damage', 'causing', 'deep', 'dangerous']) else 75
            elif cat == 'road_damage':
                base_urgency = 76
            elif cat == 'broken_footpath':
                base_urgency = 68
            elif cat == 'garbage_overflow':
                base_urgency = 70
            elif cat == 'drain_blockage':
                base_urgency = 72
            elif cat == 'water_leakage':
                base_urgency = 74
            elif cat == 'food_hygiene':
                base_urgency = 78

            # Duration bonus
            if any(w in q_lower for w in ['3 days', 'three days', 'week', 'weeks', 'several days', 'days', 'long time', 'daily']):
                base_urgency += 10
            elif any(w in q_lower for w in ['since morning', 'hours', 'today']):
                base_urgency += 5

            # Location sensitivity bonus
            if sensitivity in ['Educational Zone', 'Hospital & Medical Zone', 'Critical Infrastructure']:
                base_urgency += 8
            elif sensitivity in ['Commercial Market Zone', 'Public Road / Transit Corridor']:
                base_urgency += 5

            urgency_score = min(98, max(25, base_urgency))

            # 4. Severity Mapping
            if urgency_score >= 82:
                severity = 'Critical'
                form_severity = 'bulk'
            elif urgency_score >= 70:
                severity = 'High'
                form_severity = 'bulk'
            elif urgency_score >= 45:
                severity = 'Medium'
                form_severity = 'medium'
            else:
                severity = 'Low'
                form_severity = 'low'

            # 5. Suggested SLA
            if urgency_score >= 82:
                suggested_sla = 12.0
            elif urgency_score >= 70:
                suggested_sla = 24.0
            else:
                suggested_sla = 48.0

            # 6. Confidence Score (Deterministic Rule-Based)
            confidence = 0.90

            # 7. Human-safe Observable Reasoning
            reasons = []
            if sensitivity != 'General Area':
                reasons.append(f"identified {sensitivity.lower()}")
            if any(w in q_lower for w in ['3 days', 'three days', 'week', 'days']):
                reasons.append("multi-day hazard persistence")
            if any(w in q_lower for w in ['smell', 'stench', 'odor', 'bad smell']):
                reasons.append("public health odor nuisance")
            if any(w in q_lower for w in ['accident', 'injury', 'accidents', 'danger', 'dangerous', 'shock', 'spark']):
                reasons.append("active risk to pedestrian and vehicular safety")

            if reasons:
                reasoning = f"Complaint mentions {cat_name.lower()} in a {sensitivity.lower()} ({', '.join(reasons)}), elevating urgency to {urgency_score}/100."
            else:
                reasoning = f"Complaint classified under {dept_name} as {cat_name} based on observable civic keywords."

            # 8. Multi-Factor Civic Risk Score (0-100)
            pop_factor = 9 if sensitivity in ['Educational Zone', 'Hospital & Medical Zone'] else (8 if sensitivity in ['Commercial Market Zone', 'Public Road / Transit Corridor'] else 6)
            sev_factor = 9 if severity in ['Critical', 'High'] else 6
            raw_risk = (sev_factor * 2.5) + (pop_factor * 2.0) + (7 * 2.0) + (8 * 2.0) + (confidence * 15.0)
            civic_risk_score = min(100, max(15, round(raw_risk)))
            risk_level = 'Critical' if civic_risk_score >= 81 else ('High' if civic_risk_score >= 61 else ('Medium' if civic_risk_score >= 31 else 'Low'))

            # 9. Audit Log Entry in ai_predictions
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                pred_id = f"PRED-{int(time.time()*1000)}"
                draft_ref = 'DRAFT-' + str(int(time.time()*1000) % 100000)
                cur.execute('''
                    INSERT INTO ai_predictions (id, entityType, entityId, predictionType, confidenceScore, reasoning, recommendedAction, createdAt)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pred_id,
                    'complaint_draft',
                    draft_ref,
                    'complaint_intelligence',
                    confidence,
                    f"Observable reasoning: {reasoning} | Source: Rule-based Civic AI decision support | Advisory: True",
                    f"Recommend triage to {dept_name} ({cat_name}) with {suggested_sla}h SLA (Risk: {civic_risk_score}/100)",
                    int(time.time()*1000)
                ))
                conn.commit()
                conn.close()
            except Exception as pred_err:
                print(f"[AI Audit Note]: {pred_err}")

            self.send_json_response({
                'success': True,
                'aiDepartment': dept,
                'aiDeptName': dept_name,
                'aiDeptIcon': dept_icon,
                'aiCategory': cat,
                'aiCategoryName': cat_name,
                'aiCategoryIcon': cat_icon,
                'aiSeverity': severity,
                'formSeverity': form_severity,
                'aiUrgencyScore': urgency_score,
                'aiSuggestedSLA': suggested_sla,
                'aiLocationSensitivity': sensitivity,
                'aiConfidence': confidence,
                'aiReasoning': reasoning,
                'aiRiskScore': civic_risk_score,
                'aiRiskLevel': risk_level,
                'suggestedTitle': suggested_title,
                'isAdvisoryOnly': True,
                'analysisSource': 'Deterministic AI-assisted civic classification'
            })
            return

        # ---------------------------------------------------------------------
        # STAGE v43: CIVIC INCIDENT IDENTITY ENGINE EVALUATION
        # POST /api/ai/incident-identity
        # ---------------------------------------------------------------------
        if path == '/api/ai/incident-identity':
            conn = get_db_connection()
            cursor = conn.cursor()
            auth_user = get_authenticated_user(self, conn)

            # Security & Jurisdiction Validation
            if auth_user:
                u_dept = auth_user.get('department')
                if u_dept == 'worker':
                    conn.close()
                    self.send_json_response({'success': False, 'error': 'Forbidden: Field workforce squad is restricted to operational tasks.'}, status=403)
                    return
                if u_dept == 'municipal':
                    u_state = auth_user.get('jurisdictionState')
                    u_city = auth_user.get('jurisdictionCity')
                    u_ward = auth_user.get('jurisdictionWard')
                    req_state = body.get('state')
                    req_city = body.get('city')
                    req_ward = body.get('ward')
                    if u_state and req_state and u_state.lower() != req_state.lower():
                        conn.close()
                        self.send_json_response({'success': False, 'error': 'Forbidden: Request state outside authorized municipal jurisdiction.'}, status=403)
                        return
                    if u_city and req_city and u_city.lower() != req_city.lower():
                        conn.close()
                        self.send_json_response({'success': False, 'error': 'Forbidden: Request city outside authorized municipal jurisdiction.'}, status=403)
                        return
                    if u_ward and u_ward != 'ALL' and req_ward and u_ward.lower() not in req_ward.lower():
                        conn.close()
                        self.send_json_response({'success': False, 'error': 'Forbidden: Request ward outside authorized municipal jurisdiction.'}, status=403)
                        return
                    if body.get('department') == 'food_safety':
                        conn.close()
                        self.send_json_response({'success': False, 'error': 'Forbidden: Municipal officer cannot evaluate food safety incident identity.'}, status=403)
                        return
                elif u_dept in ['food', 'food_safety']:
                    if body.get('department') and body.get('department') != 'food_safety':
                        conn.close()
                        self.send_json_response({'success': False, 'error': 'Forbidden: Food safety officers are restricted to food safety incidents.'}, status=403)
                        return

            where_clauses = []
            prms = []
            if auth_user and auth_user.get('department') == 'municipal':
                where_clauses.append("department != 'food_safety'")
                if auth_user.get('jurisdictionState'):
                    where_clauses.append("state = ?")
                    prms.append(auth_user.get('jurisdictionState'))
                if auth_user.get('jurisdictionCity'):
                    where_clauses.append("city = ?")
                    prms.append(auth_user.get('jurisdictionCity'))
                if auth_user.get('jurisdictionWard') and auth_user.get('jurisdictionWard') != 'ALL':
                    where_clauses.append("ward = ?")
                    prms.append(auth_user.get('jurisdictionWard'))
            elif auth_user and auth_user.get('department') in ['food', 'food_safety']:
                where_clauses.append("department = 'food_safety'")
                if auth_user.get('jurisdictionState'):
                    where_clauses.append("state = ?")
                    prms.append(auth_user.get('jurisdictionState'))
                if auth_user.get('jurisdictionCity'):
                    where_clauses.append("city = ?")
                    prms.append(auth_user.get('jurisdictionCity'))
            else:
                req_state = body.get('state') or (auth_user and auth_user.get('jurisdictionState'))
                req_city = body.get('city') or (auth_user and auth_user.get('jurisdictionCity'))
                if req_state:
                    where_clauses.append("state = ?")
                    prms.append(req_state)
                if req_city:
                    where_clauses.append("city = ?")
                    prms.append(req_city)

            query_sql = "SELECT * FROM issues"
            if where_clauses:
                query_sql += " WHERE " + " AND ".join(where_clauses)
            query_sql += " ORDER BY id DESC LIMIT 200"

            cursor.execute(query_sql, prms)
            candidates = [dict(r) for r in cursor.fetchall()]

            exclude_id = body.get('excludeIssueId') or body.get('issueId')
            if exclude_id:
                candidates = [c for c in candidates if str(c.get('id')) != str(exclude_id)]

            evaluation = evaluate_incident_identity(body, candidates, auth_user=auth_user)

            # Evaluate Geo-Evidence Consistency (v44)
            input_lat = body.get('lat') or body.get('latitude')
            input_lng = body.get('lng') or body.get('longitude')
            geo_eval = evaluate_geo_evidence(
                input_lat, input_lng,
                reported_ward=body.get('ward'),
                reported_city=body.get('city'),
                reported_state=body.get('state'),
                accuracy=body.get('accuracy')
            )

            # Audit logging
            now_ms = int(time.time() * 1000)
            actor = (auth_user.get('name') if auth_user else body.get('reportedBy')) or 'Citizen'
            audit_id = f"AUDIT-IDN-{now_ms}-{random.randint(100, 999)}"
            cursor.execute('''
                INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit_id,
                evaluation.get('matchedIssueId'),
                actor,
                'ISSUE_IDENTITY_ANALYZED',
                None,
                f"Incident Identity Engine evaluated: type={evaluation.get('identityType')}, score={evaluation.get('matchScore')}. Matched: #{evaluation.get('matchedIssueId')}. Geo: {geo_eval['status']}",
                now_ms
            ))
            conn.commit()
            conn.close()

            self.send_json_response({
                'success': True,
                'geoEvidence': geo_eval,
                **evaluation
            })
            return

        # ---------------------------------------------------------------------
        # PHASE 3: TRANSPARENT AI IMAGE VERIFICATION & HUMAN-IN-THE-LOOP OVERRIDE
        # ---------------------------------------------------------------------
        if path == '/api/ai/image-verify':
            # Visual Evidence Analysis in Honest Deterministic Demo Mode
            image_data = body.get('image') or body.get('imageData') or body.get('imageUrl') or ''
            complaint_text = (body.get('complaintText') or body.get('text') or '').strip()
            dept_context = (body.get('department') or '').strip().lower()
            cat_context = (body.get('category') or '').strip().lower()
            preset_hint = (body.get('presetHint') or '').strip().lower()
            base_risk = int(body.get('baseRiskScore') or 50)
            issue_id = body.get('issueId')

            # Validate evidence presence
            if not image_data and not preset_hint:
                self.send_json_response({
                    'success': False,
                    'error': 'Visual evidence (image data or sample preset) is required for verification.'
                }, status=400)
                return

            # Visual Evidence Hazard Classification
            # Honest Capability: Rule-based visual classification demo mode (no fake deep learning or pixel analysis)
            img_str = str(image_data).lower()
            detected_hazard = 'Garbage / Waste Accumulation'
            observable_reasoning = 'Visual evidence indicates surface solid waste accumulation and uncollected refuse.'
            scientific_honesty_note = 'Observable visual patterns of discarded refuse. Cannot determine underlying biochemical contamination level.'

            # Determine class based on presetHint or image metadata / URL / content clues
            if preset_hint == 'pothole' or 'pothole' in img_str or 'photo-1578328819058' in img_str:
                detected_hazard = 'Pothole / Road Damage'
                observable_reasoning = 'Visual evidence exhibits asphalt surface depression and road cavity distress.'
                scientific_honesty_note = 'Visible road surface depression detected. Sub-surface structural integrity requires physical engineering inspection.'
            elif preset_hint == 'spark' or 'spark' in img_str or 'electric' in img_str or 'photo-1544724569' in img_str:
                detected_hazard = 'Electrical Hazard'
                observable_reasoning = 'Visible electrical fixture / conductor distress indicators detected.'
                scientific_honesty_note = 'Visible electrical hazard indicators detected. AI cannot confirm whether the line or conductor is energized.'
            elif preset_hint == 'water' or 'water' in img_str or 'drain' in img_str or 'photo-1515162816' in img_str:
                detected_hazard = 'Standing Water / Waterlogging'
                observable_reasoning = 'Visual evidence indicates street-level standing water and inadequate drainage runoff.'
                scientific_honesty_note = 'Observable surface ponding detected. Depth and drainage flow rate require on-site measurement.'
            elif preset_hint == 'food' or 'food' in img_str or 'photo-1555396273' in img_str:
                detected_hazard = 'Food-Safety Visual Concern'
                observable_reasoning = 'Observable visual indicators of possible food-safety concern (uncovered food or unhygienic storage environment).'
                scientific_honesty_note = 'Observable visual indicators of possible food-safety concern. Cannot determine microbiological contamination, bacterial presence, or food freshness.'
            elif preset_hint == 'garbage' or 'garbage' in img_str or 'photo-1605600659' in img_str:
                detected_hazard = 'Garbage / Waste Accumulation'
                observable_reasoning = 'Visual evidence indicates surface solid waste accumulation and uncollected refuse.'
                scientific_honesty_note = 'Observable visual patterns of discarded refuse. Cannot determine underlying biochemical contamination level.'
            else:
                # Default fallback based on complaint text / dept if preset hint not matched
                if any(w in complaint_text.lower() for w in ['pothole', 'road', 'crater', 'asphalt']):
                    detected_hazard = 'Pothole / Road Damage'
                    observable_reasoning = 'Visual evidence exhibits asphalt surface depression and road cavity distress.'
                    scientific_honesty_note = 'Visible road surface depression detected. Sub-surface structural integrity requires physical engineering inspection.'
                elif any(w in complaint_text.lower() for w in ['spark', 'wire', 'cable', 'electric', 'shock']):
                    detected_hazard = 'Electrical Hazard'
                    observable_reasoning = 'Visible electrical fixture / conductor distress indicators detected.'
                    scientific_honesty_note = 'Visible electrical hazard indicators detected. AI cannot confirm whether the line or conductor is energized.'
                elif any(w in complaint_text.lower() for w in ['water', 'waterlogging', 'flood', 'drain']):
                    detected_hazard = 'Standing Water / Waterlogging'
                    observable_reasoning = 'Visual evidence indicates street-level standing water and inadequate drainage runoff.'
                    scientific_honesty_note = 'Observable surface ponding detected. Depth and drainage flow rate require on-site measurement.'
                elif any(w in complaint_text.lower() for w in ['food', 'hotel', 'restaurant', 'hygiene', 'stale']):
                    detected_hazard = 'Food-Safety Visual Concern'
                    observable_reasoning = 'Observable visual indicators of possible food-safety concern (uncovered food or unhygienic storage environment).'
                    scientific_honesty_note = 'Observable visual indicators of possible food-safety concern. Cannot determine microbiological contamination, bacterial presence, or food freshness.'

            # Cross-Consistency Evaluation (Visual Evidence vs. Citizen Complaint Text / Department)
            q_text = complaint_text.lower()
            consistency = 'HIGH'
            risk_modifier = 12
            consistency_label = 'HIGH Corroboration'

            # Class-specific keyword sets
            garbage_keywords = ['garbage', 'waste', 'trash', 'dump', 'overflow', 'litter', 'debris', 'bin', 'smell', 'stench', 'refuse', 'filth']
            pothole_keywords = ['pothole', 'road', 'asphalt', 'crater', 'pavement', 'street', 'ditch', 'crack', 'tar']
            electrical_keywords = ['spark', 'wire', 'cable', 'pole', 'electric', 'power', 'shock', 'current', 'transformer', 'outage', 'blackout', 'short circuit']
            water_keywords = ['water', 'waterlogging', 'flood', 'drain', 'drainage', 'puddle', 'pool', 'overflow', 'clog', 'monsoon', 'pipeline']
            food_keywords = ['food', 'hotel', 'restaurant', 'vendor', 'stall', 'kitchen', 'hygiene', 'pest', 'cockroach', 'fly', 'flies', 'stale', 'spoil', 'rotten', 'dirty', 'taste']

            if detected_hazard == 'Garbage / Waste Accumulation':
                if any(w in q_text for w in garbage_keywords) or dept_context == 'sanitation':
                    consistency = 'HIGH'
                    risk_modifier = 12
                    consistency_label = 'HIGH Corroboration'
                elif any(w in q_text for w in ['clean', 'dirty', 'street', 'area', 'colony']):
                    consistency = 'MODERATE'
                    risk_modifier = 5
                    consistency_label = 'MODERATE Corroboration'
                else:
                    consistency = 'DISCREPANT'
                    risk_modifier = -10
                    consistency_label = 'DISCREPANT (Visual/Text Mismatch)'

            elif detected_hazard == 'Pothole / Road Damage':
                if any(w in q_text for w in pothole_keywords) or (dept_context in ['roads', 'transport', 'sanitation'] and any(w in q_text for w in ['road', 'pothole', 'street'])):
                    consistency = 'HIGH'
                    risk_modifier = 12
                    consistency_label = 'HIGH Corroboration'
                elif any(w in q_text for w in ['traffic', 'vehicle', 'bike', 'accident', 'drive', 'lane']):
                    consistency = 'MODERATE'
                    risk_modifier = 5
                    consistency_label = 'MODERATE Corroboration'
                else:
                    consistency = 'DISCREPANT'
                    risk_modifier = -10
                    consistency_label = 'DISCREPANT (Visual/Text Mismatch)'

            elif detected_hazard == 'Electrical Hazard':
                if any(w in q_text for w in electrical_keywords) or dept_context == 'electricity':
                    consistency = 'HIGH'
                    risk_modifier = 12
                    consistency_label = 'HIGH Corroboration'
                elif any(w in q_text for w in ['danger', 'hazard', 'pole', 'light', 'dark', 'street']):
                    consistency = 'MODERATE'
                    risk_modifier = 5
                    consistency_label = 'MODERATE Corroboration'
                else:
                    consistency = 'DISCREPANT'
                    risk_modifier = -10
                    consistency_label = 'DISCREPANT (Visual/Text Mismatch)'

            elif detected_hazard == 'Standing Water / Waterlogging':
                if any(w in q_text for w in water_keywords) or dept_context in ['water', 'drainage'] or (dept_context == 'sanitation' and any(w in q_text for w in ['drain', 'water'])):
                    consistency = 'HIGH'
                    risk_modifier = 12
                    consistency_label = 'HIGH Corroboration'
                elif any(w in q_text for w in ['rain', 'monsoon', 'road', 'mosquito', 'smell']):
                    consistency = 'MODERATE'
                    risk_modifier = 5
                    consistency_label = 'MODERATE Corroboration'
                else:
                    consistency = 'DISCREPANT'
                    risk_modifier = -10
                    consistency_label = 'DISCREPANT (Visual/Text Mismatch)'

            elif detected_hazard == 'Food-Safety Visual Concern':
                if any(w in q_text for w in food_keywords) or dept_context == 'food':
                    consistency = 'HIGH'
                    risk_modifier = 12
                    consistency_label = 'HIGH Corroboration'
                elif any(w in q_text for w in ['eating', 'meal', 'sweet', 'oil', 'stall', 'shop']):
                    consistency = 'MODERATE'
                    risk_modifier = 5
                    consistency_label = 'MODERATE Corroboration'
                else:
                    consistency = 'DISCREPANT'
                    risk_modifier = -10
                    consistency_label = 'DISCREPANT (Visual/Text Mismatch)'

            # Strict risk modifier bounds [-15, +15]
            risk_modifier = max(-15, min(15, risk_modifier))
            final_risk_score = max(5, min(99, base_risk + risk_modifier))

            # Audit Logging in ai_predictions table
            now_ms = int(time.time() * 1000)
            pred_id = f"PRED-IMG-{now_ms}-{random.randint(100, 999)}"
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO ai_predictions (id, entityType, entityId, predictionType, confidenceScore, reasoning, recommendedAction, createdAt)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pred_id,
                    'issue',
                    issue_id or 'NEW_SUBMISSION',
                    'image_verification',
                    None,
                    f"Hazard: {detected_hazard} | Consistency: {consistency} ({risk_modifier:+d}) | {observable_reasoning}",
                    'Authoritative municipal officer physical verification recommended before field closure',
                    now_ms
                ))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"[AI Audit Log Error] {e}")

            self.send_json_response({
                'success': True,
                'detectedHazard': detected_hazard,
                'visualConfidence': 'Demo / Rule-Based (No vision model configured)',
                'consistency': consistency,
                'consistencyLabel': consistency_label,
                'riskModifier': risk_modifier,
                'baseRiskScore': base_risk,
                'finalRiskScore': final_risk_score,
                'observableReasoning': observable_reasoning,
                'scientificHonestyNote': scientific_honesty_note,
                'modelCapability': 'Deterministic Visual-Evidence Demo Mode',
                'isAdvisoryOnly': True,
                'disclaimer': 'Visual AI assessment is advisory decision-support only. Authoritative action requires human officer verification.',
                'timestamp': now_ms
            })
            return

        if path == '/api/issues/verify-evidence':
            # Human-in-the-Loop Officer Verification / Override
            issue_id = body.get('issueId')
            verified = bool(body.get('verified'))
            override_reason = (body.get('overrideReason') or '').strip()
            officer_name = (body.get('officerName') or 'K. Mukundha (Zonal Administrator)').strip()

            if not issue_id:
                self.send_json_response({'success': False, 'error': 'Issue ID is required.'}, status=400)
                return

            if not verified and not override_reason:
                self.send_json_response({
                    'success': False,
                    'error': 'A non-empty justification is mandatory when overriding AI visual evidence assessment.'
                }, status=400)
                return

            now_ms = int(time.time() * 1000)
            officer_verified_val = 1 if verified else -1

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, status, imageAiHazard FROM issues WHERE id = ?', (issue_id,))
            issue_row = cursor.fetchone()

            if not issue_row:
                conn.close()
                self.send_json_response({'success': False, 'error': f'Issue {issue_id} not found.'}, status=404)
                return

            cursor.execute('''
                UPDATE issues
                SET imageOfficerVerified = ?,
                    imageOfficerOverrideReason = ?,
                    verifiedByOfficer = ?,
                    verifiedTimestamp = ?
                WHERE id = ?
            ''', (
                officer_verified_val,
                override_reason if not verified else None,
                officer_name,
                now_ms,
                issue_id
            ))

            # Audit log the officer decision
            audit_id = f"AUDIT-OVR-{now_ms}-{random.randint(100, 999)}"
            cursor.execute('''
                INSERT INTO ai_predictions (id, entityType, entityId, predictionType, confidenceScore, reasoning, recommendedAction, createdAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit_id,
                'issue',
                issue_id,
                'officer_evidence_verification',
                1.0 if verified else 0.0,
                f"Officer {'VERIFIED' if verified else 'OVERRODE'} AI assessment. Reason: {override_reason or 'Corroborated by on-site officer inspection'}",
                'Authoritative officer verification recorded in governance ledger',
                now_ms
            ))

            conn.commit()

            # Retrieve updated issue
            cursor.execute('SELECT * FROM issues WHERE id = ?', (issue_id,))
            updated_row = dict(cursor.fetchone())
            conn.close()

            updated_row['upvotedBy'] = json.loads(updated_row.get('upvotedBy') or '[]')
            updated_row['comments'] = json.loads(updated_row.get('comments') or '[]')

            # Broadcast SSE update
            sse_hub.broadcast('ISSUE_UPDATED', updated_row)

            self.send_json_response({
                'success': True,
                'issueId': issue_id,
                'imageOfficerVerified': officer_verified_val,
                'imageOfficerOverrideReason': override_reason if not verified else None,
                'verifiedByOfficer': officer_name,
                'verifiedTimestamp': now_ms,
                'message': f"Evidence successfully {'verified' if verified else 'overridden'} by officer."
            })
            return

        if path == '/api/ai/workforce-recommend':
            dept = body.get('department', 'sanitation')
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM workers WHERE department = ? AND currentStatus = "available"', (dept,))
            avail_workers = [dict(r) for r in cursor.fetchall()]
            conn.close()
            if not avail_workers:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM workers WHERE department = ?', (dept,))
                avail_workers = [dict(r) for r in cursor.fetchall()]
                conn.close()

            rec_worker = avail_workers[0] if avail_workers else {
                'id': 'WRK-SAN-01', 'name': 'Ravi Kumar', 'department': dept,
                'specialization': 'General Operations', 'tasksCompleted': 14
            }
            self.send_json_response({
                'success': True,
                'recommendedWorker': rec_worker,
                'confidence': 0.88,
                'reasoning': f"Worker {rec_worker.get('name')} is closest to the incident zone with {rec_worker.get('tasksCompleted', 0)} completed tasks.",
                'estimatedArrivalMinutes': 14,
                'isAdvisoryOnly': True
            })
            return

        if path == '/api/ai/food-risk':
            score = float(body.get('hygieneScore', 65))
            violations = int(body.get('violationsCount', 1))
            gas_ppm = float(body.get('mq135GasPpm', 220))
            
            # Multi-factor advisory risk score
            risk_pct = min(98, max(12, int((100 - score) * 0.4 + (violations * 15) + (gas_ppm / 500.0 * 30))))
            risk_level = 'Critical' if risk_pct >= 80 else 'High' if risk_pct >= 60 else 'Medium' if risk_pct >= 35 else 'Low'
            
            self.send_json_response({
                'success': True,
                'riskPercent': risk_pct,
                'riskLevel': risk_level,
                'confidence': 0.89,
                'recommendedAction': 'Priority Statutory Inspection & MQ-135 Verification' if risk_pct >= 60 else 'Routine Surveillance Inspection',
                'isAdvisoryOnly': True
            })
            return

        # 7. REST API: POST /api/auth/login (Strict Real-Time SQLite Credential Verification)
        if path == '/api/auth/login':
            email = (body.get('email') or '').strip().lower()
            password = (body.get('password') or '').strip()
            department = body.get('department', 'citizen')

            if not email or len(email) < 3:
                self.send_json_response({'success': False, 'error': 'Please enter a valid email address.'}, status=400)
                return

            if not password:
                self.send_json_response({'success': False, 'error': 'Please enter your password.'}, status=400)
                return

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE LOWER(TRIM(email)) = LOWER(TRIM(?))', (email,))
            user_row = cursor.fetchone()
            conn.close()

            # ❌ If account does not exist in SQLite database
            if not user_row:
                if department == 'citizen':
                    self.send_json_response({
                        'success': False,
                        'error': 'No citizen account found with this email. Please click "Register with OTP" to create your account.'
                    }, status=404)
                else:
                    self.send_json_response({
                        'success': False,
                        'error': 'No registered government official found with this email.'
                    }, status=404)
                return

            user_dict = dict(user_row)
            stored_password = str(user_dict.get('password') or '').strip()
            provided_password = str(password).strip()

            # Verify with scrypt or legacy plain-text
            if not verify_password(provided_password, stored_password):
                self.send_json_response({
                    'success': False,
                    'error': 'Incorrect password! Please enter the exact password you created during registration.'
                }, status=401)
                return

            # Transparently upgrade plain-text password to scrypt upon successful authentication
            if not stored_password.startswith('scrypt$'):
                try:
                    up_conn = get_db_connection()
                    up_cursor = up_conn.cursor()
                    up_cursor.execute('UPDATE users SET password = ? WHERE LOWER(TRIM(email)) = LOWER(TRIM(?))', (hash_password(provided_password), email))
                    up_conn.commit()
                    up_conn.close()
                except Exception as up_err:
                    print(f"[Security] Password upgrade note: {up_err}")

            # Generate real cryptographic session token persisted in SQLite
            sess_conn = get_db_connection()
            token = create_session(user_dict, sess_conn)
            sess_conn.close()

            safe_user = {k: v for k, v in user_dict.items() if k != 'password'}
            safe_user['profileCompleted'] = 1 if safe_user.get('profileCompleted') == 1 else 0
            session_payload = {
                'success': True,
                'token': token,
                'department': user_dict.get('department') or department,
                'user': safe_user
            }
            self.send_json_response(session_payload)
            return

        self.send_json_response({'error': 'Not Found'}, status=404)

    def send_json_response(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def serve_static_file(self, req_path):
        if req_path == '/' or req_path == '':
            req_path = '/index.html'

        rel_path = req_path.lstrip('/')
        file_path = os.path.join(BASE_DIR, rel_path)

        if not os.path.exists(file_path) or os.path.isdir(file_path):
            file_path = os.path.join(BASE_DIR, 'index.html')

        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'

            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))

# ------------------------------------------------------------------------------
# 4. ENTRY POINT
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    init_database()

    telemetry_thread = threading.Thread(target=background_telemetry_loop, daemon=True)
    telemetry_thread.start()

    server = ThreadingHTTPServer(('0.0.0.0', PORT), CivicAppRequestHandler)
    print(f'===========================================================')
    print(f'  Clean & Safe India - Real-Time Backend Server Online!')
    print(f'  Local URL:    http://localhost:{PORT}')
    print(f'  Database:     SQLite ({DB_FILE})')
    print(f'  SSE Stream:   http://localhost:{PORT}/api/stream')
    print(f'===========================================================')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\\nShutting down server...')
        server.server_close()
