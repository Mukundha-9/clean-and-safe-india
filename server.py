"""Clean & Safe India - Real-Time Backend Server (Python 3.14)"""
import os
import sys
import json
import time
import sqlite3
import datetime
import threading
import mimetypes
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get('PORT', 8000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'civic_database.db')

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
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

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
            mq135GasPpm REAL
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
            createdAt INTEGER
        )
    ''')

    conn.commit()

    # Seed default system accounts if not present
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, id, name, password, department, roleTitle, officialId, avatar, civicCredits, activeStreakWeeks, createdAt)
        VALUES ('citizen@civictech.in', 'user-101', 'KRISH', 'password123', 'citizen', 'Verified Citizen Reporter', 'CIT-IND-2026-8941', 'KR', 20, 1, strftime('%s', 'now'))
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, id, name, password, department, roleTitle, officialId, avatar, civicCredits, activeStreakWeeks, createdAt)
        VALUES ('admin@municipality.gov.in', 'user-102', 'K. Mukundha (Zonal Administrator)', 'password123', 'municipal', 'Designated Municipal & Electricity Administrator', 'GOV-MUNC-SEC-012', 'KM', 0, 0, strftime('%s', 'now'))
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, id, name, password, department, roleTitle, officialId, avatar, civicCredits, activeStreakWeeks, createdAt)
        VALUES ('fso.officer@foodsafety.gov.in', 'user-103', 'Dr. Lakshmi Prasad (FSO)', 'password123', 'food', 'Designated Food Safety Officer (FSO)', 'FSSAI-INSP-2026-44', 'LP', 0, 0, strftime('%s', 'now'))
    ''')
    conn.commit()

    # Seed Database if empty
    cursor.execute('SELECT COUNT(*) FROM issues')
    count = cursor.fetchone()[0]
    if count == 0:
        seed_initial_data(conn)
    
    conn.close()
    print('[Database] SQLite database initialized successfully at', DB_FILE)

def seed_initial_data(conn):
    cursor = conn.cursor()
    now = int(time.time() * 1000)

    # Initial Issues
    seed_issues = [
        (
            'ISS-2026-00123', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', 'Market Gate Cross',
            'sanitation', 'Sanitation & Waste Management', '🏢',
            'Overflowing Commercial Waste at Market Gate',
            'High volume wet & dry waste pile obstructing market walkway. Threat of vector-borne contamination.',
            'Surampalem • Ward 12 (Market Zone), Market Gate Cross',
            'garbage_overflow', 'Garbage Overflow', '🗑️', 'bulk', 'HIGH RISK BULK HAZARD', 'pending',
            now - (8 * 3600 * 1000), now + (40 * 3600 * 1000), 39.9, None, 0,
            'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80', None,
            'Krish (Civic Guardian)', 'user-101', 'Consultant Officer K. Mukundha (GOV-MUNC-SEC-012)', now - (7 * 3600 * 1000),
            'Municipal Rapid Squad 4', now - (6 * 3600 * 1000), 'Squad Dispatched with Hydraulic Compactor',
            'Tractor / Heavy Squad', 14, json.dumps(['user-101', 'user-102']),
            json.dumps([
                {'author': 'System Watchdog', 'text': 'Live GPS Geotag logged: 17.0010° N, 81.8045° E (±4m). 48h SLA timer active.', 'time': '8h ago'},
                {'author': 'Consultant Officer K. Mukundha', 'text': 'Grievance verified. Heavy hydraulic tipper assigned.', 'time': '7h ago'}
            ]),
            0, 0, 17.0010, 81.8045, None, None, None
        ),
        (
            'ISS-2026-00124', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', 'Gandhi Statue Main Road',
            'electricity', 'Smart Electricity Department', '⚡',
            '11KV Transformer Sparking & Low Hanging Cable',
            'Dangerous spark discharge observed at 11KV junction pole during wind gust. Risk of electrocution.',
            'Surampalem • Ward 12 (Market Zone), Gandhi Statue Main Road',
            'sparking_wire', 'Sparking Cable / Wire', '⚡', 'bulk', 'CRITICAL LIFE HAZARD', 'pending',
            now - (18 * 3600 * 1000), now + (30 * 3600 * 1000), 29.8, None, 0,
            'https://images.unsplash.com/photo-1544724569-5f546fd6f2b5?w=800&auto=format&fit=crop&q=80', None,
            'R. Venkatesh (Citizen)', 'user-103', 'Consultant Officer K. Mukundha (GOV-MUNC-SEC-012)', now - (17 * 3600 * 1000),
            'Lineman Squad B (Suresh Kumar)', now - (16 * 3600 * 1000), 'Feeder Isolated & Line Repair Crew Active',
            'Lineman Bucket Van (AP-05-EB)', 28, json.dumps(['user-101', 'user-104', 'user-105']),
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
            'FSO Inspection Squad', 19, json.dumps(['user-101']),
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
            'Collection Truck', 22, json.dumps(['user-101', 'user-106']),
            json.dumps([
                {'author': 'Consultant Officer K. Mukundha', 'text': 'Grievance verified. PW squad closed repair within 26 hours.', 'time': '10h ago'}
            ]),
            1, 0, 17.0012, 81.8040, None, None, None
        )
    ]

    cursor.executemany('''
        INSERT INTO issues VALUES (
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
            return

        # 2. REST API: GET /api/issues
        if path == '/api/issues':
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM issues ORDER BY timestamp DESC')
            rows = cursor.fetchall()
            issues = []
            for r in rows:
                item = dict(r)
                item['upvotedBy'] = json.loads(item['upvotedBy'] or '[]')
                item['comments'] = json.loads(item['comments'] or '[]')
                issues.append(item)
            conn.close()

            self.send_json_response({'success': True, 'issues': issues})
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
            issue_id = f'ISS-2026-{str(total_issues + 124).zfill(5)}'

            now = int(time.time() * 1000)
            deadline = now + (48 * 3600 * 1000)

            assigned_squad = 'Municipal Rapid Squad 4' if body.get('department') == 'sanitation' else 'Lineman Squad B' if body.get('department') == 'electricity' else 'Food Safety Officer'
            dept_icon = '🏢' if body.get('department') == 'sanitation' else '⚡' if body.get('department') == 'electricity' else '🍲'
            dept_name = 'Sanitation & Waste Management' if body.get('department') == 'sanitation' else 'Smart Electricity Department' if body.get('department') == 'electricity' else 'Food Safety Department'

            comments = [
                {'author': 'System Watchdog', 'text': 'Report logged with live GPS geotag. 48h SLA timer activated.', 'time': 'Just now'},
                {'author': 'Consultant Officer K. Mukundha', 'text': 'Grievance verified. Squad allocated and dispatched.', 'time': 'Just now'}
            ]

            new_issue = {
                'id': issue_id,
                'state': body.get('state', 'Andhra Pradesh'),
                'city': body.get('city', 'Surampalem'),
                'ward': body.get('ward', 'Ward 12 (Market Zone)'),
                'street': body.get('street', 'Main Road'),
                'department': body.get('department', 'sanitation'),
                'deptName': dept_name,
                'deptIcon': dept_icon,
                'title': body.get('title', 'Civic Hazard'),
                'description': body.get('description', ''),
                'location': f"{body.get('city', 'Surampalem')} • {body.get('ward', 'Ward 12')}, {body.get('street', '')}",
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
                'verifiedByOfficer': 'Consultant Officer K. Mukundha (GOV-MUNC-SEC-012)',
                'verifiedTimestamp': now + 900000,
                'assignedWorker': assigned_squad,
                'assignedTimestamp': now + 1800000,
                'workerStatus': 'Dispatched & En Route to Site',
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
                'mq135GasPpm': body.get('mq135GasPpm')
            }

            cursor.execute('''
                INSERT INTO issues VALUES (
                    :id, :state, :city, :ward, :street, :department, :deptName, :deptIcon, :title,
                    :description, :location, :category, :categoryName, :categoryIcon, :severity,
                    :severityLabel, :status, :timestamp, :slaDeadline, :slaHoursLeft, :resolvedTimestamp,
                    :isSlaBreached, :imageBefore, :imageAfter, :reportedBy, :reportedById, :verifiedByOfficer,
                    :verifiedTimestamp, :assignedWorker, :assignedTimestamp, :workerStatus,
                    :recommendedResource, :upvotes, :upvotedBy, :comments, :rewardIssued, :fineLevied,
                    :lat, :lng, :vendorId, :vendorName, :mq135GasPpm
                )
            ''', new_issue)

            conn.commit()
            conn.close()

            broadcast_payload = dict(new_issue)
            broadcast_payload['upvotedBy'] = [user_id]
            broadcast_payload['comments'] = comments
            sse_hub.broadcast('ISSUE_CREATED', broadcast_payload)

            self.send_json_response({
                'success': True,
                'issue': broadcast_payload,
                'remainingToday': max(0, 2 - current_count)
            })
            return

        # 2. REST API: POST /api/issues/resolve
        if path.startswith('/api/issues/') and path.endswith('/resolve'):
            parts = path.split('/')
            issue_id = parts[3]

            notes = body.get('notes', 'Field execution verified and site cleaned.')
            photo_after = body.get('photoAfter', 'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&auto=format&fit=crop&q=80')
            now = int(time.time() * 1000)

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM issues WHERE id = ?', (issue_id,))
            row = cursor.fetchone()

            if not row:
                conn.close()
                self.send_json_response({'success': False, 'error': 'Issue not found'}, status=404)
                return

            comments = json.loads(row['comments'] or '[]')
            comments.append({'author': body.get('officerName', 'Field Officer'), 'text': f'Issue resolved: {notes}', 'time': 'Just now'})

            cursor.execute('''
                UPDATE issues SET
                    status = "resolved",
                    resolvedTimestamp = ?,
                    slaHoursLeft = 0,
                    imageAfter = ?,
                    workerStatus = "Field Execution Completed & Cleaned Proof Uploaded",
                    rewardIssued = 1,
                    comments = ?
                WHERE id = ?
            ''', (now, photo_after, json.dumps(comments), issue_id))

            cursor.execute('''
                UPDATE users SET civicCredits = civicCredits + 50 
                WHERE id = ? OR LOWER(name) = LOWER(?) OR LOWER(email) = LOWER(?)
            ''', (row['reportedById'] or '', row['reportedBy'] or '', row['reportedById'] or ''))

            conn.commit()

            cursor.execute('SELECT * FROM issues WHERE id = ?', (issue_id,))
            updated_row = dict(cursor.fetchone())
            updated_row['upvotedBy'] = json.loads(updated_row['upvotedBy'] or '[]')
            updated_row['comments'] = json.loads(updated_row['comments'] or '[]')
            conn.close()

            sse_hub.broadcast('ISSUE_RESOLVED', updated_row)
            self.send_json_response({'success': True, 'issue': updated_row})
            return

        # 3. REST API: POST /api/food-violations
        if path == '/api/food-violations':
            fine_amount = float(body.get('fineAmount', 500))
            state = body.get('state', 'Andhra Pradesh')
            city = body.get('city', 'Surampalem')
            ward = body.get('ward', 'Ward 14 (Campus Food Zone)')
            street = body.get('street', 'College Road')
            vendor_name = body.get('vendorName', 'Food Stall')
            owner_name = body.get('ownerName', 'Proprietor')
            clause = body.get('violationClause', 'Sec 56 FSS Act - Unhygienic premises')
            notes = body.get('notes', 'Inspection notice served.')

            vendor_id = f'FSSAI-{"AP" if state == "Andhra Pradesh" else "IND"}-2026-V{int(time.time()) % 900 + 100}'

            conn = get_db_connection()
            cursor = conn.cursor()

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
                'inspectedBy': 'Dr. Lakshmi Prasad (FSO)',
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
            issue_id = body.get('issueId')
            notes = body.get('notes', 'Re-inspected and compliant.')
            gas_ppm = body.get('gasPpm', 180)
            score = body.get('score', 92)
            outcome = body.get('outcome', 'passed')

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM issues WHERE id = ?', (issue_id,))
            issue_row = cursor.fetchone()

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

            import random
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

            user_data = {
                'email': email,
                'id': user_id,
                'name': display_name,
                'password': password,
                'department': 'citizen',
                'roleTitle': 'Verified Citizen Reporter',
                'officialId': official_id,
                'avatar': avatar,
                'civicCredits': credits,
                'activeStreakWeeks': streak,
                'createdAt': created_at
            }

            cursor.execute('''
                INSERT OR REPLACE INTO users (email, id, name, password, department, roleTitle, officialId, avatar, civicCredits, activeStreakWeeks, createdAt)
                VALUES (:email, :id, :name, :password, :department, :roleTitle, :officialId, :avatar, :civicCredits, :activeStreakWeeks, :createdAt)
            ''', user_data)
            conn.commit()
            conn.close()

            # Clear used OTP
            if email in ACTIVE_OTPS:
                del ACTIVE_OTPS[email]

            safe_user = {k: v for k, v in user_data.items() if k != 'password'}
            session_payload = {
                'success': True,
                'token': f'CIVIC_JWT_{int(time.time()*1000)}',
                'department': 'citizen',
                'user': safe_user,
                'message': 'Citizen account successfully registered with 20 Welcome Civic Credits!'
            }
            self.send_json_response(session_payload)
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

            # ❌ If password does NOT match the password saved in SQLite
            if stored_password != provided_password:
                self.send_json_response({
                    'success': False,
                    'error': 'Incorrect password! Please enter the exact password you created during registration.'
                }, status=401)
                return

            safe_user = {k: v for k, v in user_dict.items() if k != 'password'}
            session_payload = {
                'success': True,
                'token': f'CIVIC_JWT_{int(time.time()*1000)}',
                'department': department,
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

    server = HTTPServer(('0.0.0.0', PORT), CivicAppRequestHandler)
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
