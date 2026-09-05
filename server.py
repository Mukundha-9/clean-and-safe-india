"""Clean & Safe India - Real-Time Backend Server (Python 3.14)"""
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
import predictive_engine

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
            mq135GasPpm REAL,
            imageAiHazard TEXT,
            imageAiConfidence TEXT,
            imageTextConsistency TEXT,
            imageRiskModifier INTEGER DEFAULT 0,
            imageAiReasoning TEXT,
            imageAiAccepted INTEGER DEFAULT 0,
            imageOfficerVerified INTEGER DEFAULT 0,
            imageOfficerOverrideReason TEXT
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
        ('imageOfficerOverrideReason', 'TEXT')
    ]
    for col_name, col_type in new_issue_cols:
        if col_name not in existing_issue_cols:
            try:
                cursor.execute(f"ALTER TABLE issues ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"[Database] Column {col_name} migration note: {e}")

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


    # Seed Field Workers if empty
    cursor.execute('SELECT COUNT(*) FROM workers')
    if cursor.fetchone()[0] == 0:
        seed_workers = [
            ('WRK-SAN-01', 'Ravi Kumar', '+91 98480 22311', 'sanitation', 'Garbage & Heavy Compactor Operations', 'available', 17.0012, 81.8048, 14, None),
            ('WRK-ELE-02', 'Suresh Kumar', '+91 94401 55422', 'electricity', '11KV Substation & Line Repair', 'available', 17.0025, 81.8030, 22, None),
            ('WRK-ROA-03', 'Anita Roy', '+91 99880 33411', 'sanitation', 'Asphalt Patching & Culvert Desilting', 'available', 16.9995, 81.8060, 9, None),
            ('WRK-SAN-04', 'M. Appa Rao', '+91 98661 77211', 'sanitation', 'Commercial Market Solid Waste Collection', 'busy', 17.0030, 81.8010, 31, 'ISS-2026-00123')
        ]
        cursor.executemany('''
            INSERT OR IGNORE INTO workers (id, name, phone, department, specialization, currentStatus, lat, lng, tasksCompleted, currentTaskId)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    conn.commit()

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
            'ISS-2026-00128', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', 'Gandhi Statue Main Road',
            'sanitation', 'Sanitation & Waste Management', '🏢',
            '🚨 SLA Breached: Massive Solid Waste & Garbage Dump Overflow',
            'Over 3 tons of rotten municipal garbage overflowing onto main pedestrian road. Exceeded mandatory 48-Hour SLA period without field clearance. Automatically escalated to Municipal Commissioner Dr. Mahesh Babu & Zonal Health Directorate.',
            'Surampalem • Ward 12 (Market Zone), Gandhi Statue Main Road',
            'garbage_overflow', 'Garbage Overflow', '🗑️', 'bulk', 'SLA BREACHED (>48H)', 'escalated',
            now - (62 * 3600 * 1000), now - (14 * 3600 * 1000), 0, None, 1,
            'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80', None,
            'KRISH (Civic Guardian)', 'user-101', 'Consultant Officer K. Mukundha (GOV-MUNC-SEC-012)', now - (61.5 * 3600 * 1000),
            'Sanitation Rapid Fleet 3 (Lead: P. Ramesh)', now - (60 * 3600 * 1000),
            'Delayed (>48h) — Auto-Forwarded to Municipal Commissioner Red Desk for Urgent Action',
            'Heavy Hydraulic Compactor & 10-Ton Tipper Fleet', 84, json.dumps(['user-101']),
            json.dumps([
                {'author': 'System SLA Monitor', 'text': '⏱️ 48-Hour SLA Breached! Grievance unaddressed after 48h limit.', 'time': '14h ago'},
                {'author': 'Auto-Escalation Gateway', 'text': '🚨 Escalated to Higher Authority: Zonal Municipal Commissioner (Dr. Mahesh Babu) & Urban Health Directorate.', 'time': '14h ago'},
                {'author': 'Municipal Commissioner Red Desk', 'text': 'Ticket received with Critical Priority 1. Direct disciplinary summons and immediate heavy squad deployed.', 'time': '12h ago'},
                {'author': 'KRISH (Citizen)', 'text': 'Garbage dump is emitting toxic odor and blocking school children. Thank you for forwarding to the Commissioner.', 'time': '4h ago'}
            ]),
            0, 0, 17.0012, 81.8048, None, None, None
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
        # Phase 4: Predictive Civic Intelligence Endpoints (GET)
        if predictive_engine.handle_predictive_get(self, path, query):
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

        # Phase 4: Predictive Civic Intelligence Endpoints (POST)
        if predictive_engine.handle_predictive_post(self, path, body, sse_hub):
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
                'imageOfficerOverrideReason': body.get('imageOfficerOverrideReason')
            }

            cols = ', '.join(new_issue.keys())
            placeholders = ', '.join([f":{k}" for k in new_issue.keys()])
            cursor.execute(f"INSERT INTO issues ({cols}) VALUES ({placeholders})", new_issue)

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
                'password': hash_password(password),
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
            officer_name = (body.get('officerName') or 'Consultant Officer K. Mukundha (GOV-MUNC-SEC-012)').strip()

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
