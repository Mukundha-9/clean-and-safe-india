# =============================================================================
# SMART CIVIC CONNECT — PHASE E: PREDICTIVE & PREVENTIVE CIVIC GOVERNANCE
# Standard-Library Python + SQLite Architecture (Advisory Human-in-the-Loop)
# =============================================================================

import json
import time
import sqlite3
import random
import uuid

CANONICAL_TARGETS = [
    {
        'ward': 'Ward 12 (Market Zone)',
        'wardNum': '12',
        'category': 'Garbage Overflow',
        'slug': 'GARBAGE',
        'department': 'sanitation',
        'recommendation': 'Schedule preventive waste collection inspection in the affected zone and review nearby collection frequency.',
        'rootCauses': {
            'SERVICE': 'Increase municipal waste pickup frequency from once to twice daily during peak market morning and evening trade.',
            'INFRASTRUCTURE': 'Inspect commercial bin capacity at Market Canteen Gate and evaluate requirement for an additional 1100L heavy container.',
            'AWARENESS': 'Display prominent Clean Zone segregation guidance and anti-littering signage at market canteen entrances.',
            'OPERATIONS': 'Coordinate morning sanitation review with Market Guild trade representatives to align commercial waste timing.',
            'ENFORCEMENT_REFERRAL': 'Recommend formal referral to Local Municipal Sanitary Authority if unauthorized bulk commercial dumping persists (Advisory: app has no direct legal prosecution authority).'
        },
        'cleanZone': {
            'name': 'Market Canteen Gate, Ward 12',
            'status': 'UNDER PREVENTIVE MONITORING',
            'guidance': 'Please use designated waste collection points and avoid leaving waste outside collection areas.'
        }
    },
    {
        'ward': 'Ward 7 (Railway Colony)',
        'wardNum': '7',
        'category': 'Pothole / Road Damage',
        'slug': 'POTHOLE',
        'department': 'roads',
        'recommendation': 'Create a preventive road inspection task for the affected corridor and prioritize repeated locations.',
        'rootCauses': {
            'SERVICE': 'Schedule bi-weekly bituminous road surface monitoring across freight approach corridors.',
            'INFRASTRUCTURE': 'Assess road sub-base compaction and evaluate need for heavy-duty asphalt overlay.',
            'AWARENESS': 'Erect caution signage warning heavy freight vehicles of corridor axle-load limits.',
            'OPERATIONS': 'Coordinate with Railway PWD division to synchronize drainage culvert maintenance.',
            'ENFORCEMENT_REFERRAL': 'Recommend referral to Regional Transport Authority regarding heavy axle overloading on municipal feeder roads.'
        }
    },
    {
        'ward': 'Ward 12 (Market Zone)',
        'wardNum': '12',
        'category': 'Electricity / Electrical Hazard',
        'slug': 'ELECTRICITY',
        'department': 'electricity',
        'recommendation': 'Schedule preventive electrical inspection and maintenance review by authorized personnel.',
        'rootCauses': {
            'SERVICE': 'Schedule preventive thermal scanning of overhead feeder connections.',
            'INFRASTRUCTURE': 'Inspect distribution pillar box waterproofing and replace weathered insulation sleeves.',
            'AWARENESS': 'Display high-voltage hazard warning labels on market zone distribution poles.',
            'OPERATIONS': 'Coordinate planned shutdown maintenance during low-activity night hours.',
            'ENFORCEMENT_REFERRAL': 'Recommend formal inspection referral for unauthorized temporary power taps along market stalls.'
        }
    },
    {
        'ward': 'Ward 11 (Lake View Zone)',
        'wardNum': '11',
        'category': 'Drain Blockage / Waterlogging',
        'slug': 'DRAIN',
        'department': 'sanitation',
        'recommendation': 'Schedule preventive drain inspection and debris clearance before the forecast window.',
        'rootCauses': {
            'SERVICE': 'Increase pre-monsoon culvert silt clearing frequency along lake catchment bunds.',
            'INFRASTRUCTURE': 'Inspect intake grille mesh size and assess requirement for secondary silt trap.',
            'AWARENESS': 'Distribute civic advisories against dumping plastic refuse into open stormwater canals.',
            'OPERATIONS': 'Deploy mobile suction teams during heavy storm alerts to prevent waterlogging.',
            'ENFORCEMENT_REFERRAL': 'Recommend referral to Pollution Control Board for unauthorized commercial discharge into storm canals.'
        }
    },
    {
        'ward': 'Ward 14 (Campus Zone)',
        'wardNum': '14',
        'category': 'Food Safety',
        'slug': 'FOOD',
        'department': 'food_safety',
        'recommendation': 'Prioritize a human food-safety inspection of repeatedly reported establishments.',
        'rootCauses': {
            'SERVICE': 'Schedule monthly hygiene audits and routine cooking oil quality verification.',
            'INFRASTRUCTURE': 'Inspect potable water availability and grease-trap drainage at food stalls.',
            'AWARENESS': 'Distribute FSSAI Food Hygiene Rating signage and safe cooking practices flyers.',
            'OPERATIONS': 'Coordinate with Campus Administration on sanitary waste disposal for student food courts.',
            'ENFORCEMENT_REFERRAL': 'Recommend formal statutory notice by designated Food Safety Officer under FSSAI Section 32 where non-compliance persists.'
        }
    },
    {
        'ward': 'Ward 3 (Residential Colony)',
        'wardNum': '3',
        'category': 'Water Supply / Pipeline Leakage',
        'slug': 'WATER',
        'department': 'water_supply',
        'recommendation': 'Inspect the affected pipeline corridor and review repeated leakage reports.',
        'rootCauses': {
            'SERVICE': 'Conduct acoustic pipeline leakage survey along residential distribution loops.',
            'INFRASTRUCTURE': 'Inspect distribution valve chamber gaskets and replace aging PVC joints.',
            'AWARENESS': 'Encourage residential reporting of low pressure and ground dampness signals.',
            'OPERATIONS': 'Coordinate water rationing and pressure regulating during peak distribution hours.',
            'ENFORCEMENT_REFERRAL': 'Recommend referral to Municipal Water Authority regarding illegal booster pump connections.'
        }
    }
]

def log_operational_audit(cursor, entity_id, actor, action_type, assigned_worker=None, notes=None):
    """Inserts authoritative operational audit event into operational_audit_logs."""
    now_ms = int(time.time() * 1000)
    audit_id = f"AUDIT-OPS-{now_ms}-{uuid.uuid4().hex[:8]}"
    try:
        cursor.execute('''
            INSERT INTO operational_audit_logs (id, issueId, officer, actionType, assignedWorker, supervisorNotes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (audit_id, entity_id, actor or 'Civic AI Predictive Engine', action_type, assigned_worker, notes, now_ms))
    except Exception as e:
        print(f"[Predictive Audit Log Error] {e}")

def init_predictive_tables(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictive_forecasts (
            id TEXT PRIMARY KEY,
            hotspotId TEXT,
            ward TEXT,
            category TEXT,
            department TEXT,
            predictiveRiskScore INTEGER DEFAULT 50,
            riskLevel TEXT DEFAULT 'MODERATE',
            forecastHorizon TEXT DEFAULT 'Next 7 Days',
            historicalIncidentCount INTEGER DEFAULT 0,
            recentIncidentCount INTEGER DEFAULT 0,
            recurrenceIndicator TEXT DEFAULT 'MODERATE',
            slaBreachIndicator TEXT DEFAULT 'NORMAL',
            contributingFactors TEXT,
            preventiveRecommendation TEXT,
            confidenceLabel TEXT DEFAULT 'Demo / Rule-Based',
            source TEXT DEFAULT 'Demo / Historical Incident Dataset',
            status TEXT DEFAULT 'PENDING_HUMAN_REVIEW',
            createdAt INTEGER,
            reviewedBy TEXT,
            reviewedAt INTEGER,
            reviewReason TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preventive_actions (
            id TEXT PRIMARY KEY,
            forecastId TEXT,
            action TEXT,
            department TEXT,
            priority TEXT DEFAULT 'High',
            status TEXT DEFAULT 'PENDING_OFFICER_APPROVAL',
            createdBy TEXT DEFAULT 'Civic AI Predictive Engine',
            approvedBy TEXT,
            createdAt INTEGER,
            approvedAt INTEGER,
            rejectionReason TEXT,
            modificationReason TEXT
        )
    ''')

    pa_cols = [
        ('assignedWorker', 'TEXT'),
        ('assignedAt', 'INTEGER'),
        ('implementedAt', 'INTEGER'),
        ('implementedNotes', 'TEXT'),
        ('monitoringStartedAt', 'INTEGER'),
        ('monitoringStatus', "TEXT DEFAULT 'PENDING'"),
        ('recurrenceTrend', "TEXT DEFAULT 'PENDING'"),
        ('trendNotes', 'TEXT'),
        ('rootCauses', 'TEXT'),
        ('location', 'TEXT'),
        ('ward', 'TEXT')
    ]
    for col, col_type in pa_cols:
        try:
            cursor.execute(f"ALTER TABLE preventive_actions ADD COLUMN {col} {col_type}")
        except Exception:
            pass

    pf_cols = [
        ('rootCauses', 'TEXT'),
        ('preventionStatus', "TEXT DEFAULT 'Improving'"),
        ('cleanZoneName', 'TEXT'),
        ('uniqueIncidentCount', 'INTEGER DEFAULT 0'),
        ('citizenReportCount', 'INTEGER DEFAULT 0')
    ]
    for col, col_type in pf_cols:
        try:
            cursor.execute(f"ALTER TABLE predictive_forecasts ADD COLUMN {col} {col_type}")
        except Exception:
            pass

def seed_predictive_intelligence_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM issues")
    total_issues = cursor.fetchone()[0]

    if total_issues < 15:
        now_ms = int(time.time() * 1000)
        day_ms = 86400 * 1000

        hist_issues = [
            (
                'ISS-2026-HIST-01', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', 'Market Gate Cross',
                'sanitation', 'Sanitation & Waste Management', '🏢',
                'Recurring Wet Waste Dump at Market Entrance',
                'Vegetable and packaging refuse accumulated from morning wholesale trading.',
                'Surampalem • Ward 12 (Market Zone), Market Gate Cross',
                'garbage_overflow', 'Garbage Overflow', '🗑️', 'bulk', 'HIGH RISK HAZARD', 'resolved',
                now_ms - (8 * day_ms), now_ms + (40 * 3600 * 1000), 0, now_ms - (7 * day_ms), 0,
                'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80', None,
                'K. Ramesh (Market Guild)', 'user-101', 'K. Mukundha (Zonal Administrator)', now_ms - (7 * day_ms),
                'Municipal Rapid Squad 4', now_ms - (7 * day_ms), 'Resolved', 'Collection Truck', 8, '[]', '[]', 0, 0,
                17.0010, 81.8045, None, None, None, 'CLU-W12-SAN', 76, 0.92, 'Commercial market zone waste cluster', 48.0, 0.12,
                'sanitation', 'garbage_overflow', 'bulk', 1, None, 'Garbage / Waste Accumulation', 'Demo / Rule-Based',
                'HIGH', 12, 'Visual evidence corroborates extensive waste overflow.', 1, 1, None
            ),
            (
                'ISS-2026-HIST-02', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', 'Gandhi Statue Main Road',
                'sanitation', 'Sanitation & Waste Management', '🏢',
                'Solid Waste Spillage near Bus Shelter',
                'Overflowing communal container spilling onto transit corridor.',
                'Surampalem • Ward 12 (Market Zone), Gandhi Statue Main Road',
                'garbage_overflow', 'Garbage Overflow', '🗑️', 'medium', 'STANDARD COMPLAINT', 'resolved',
                now_ms - (14 * day_ms), now_ms + (34 * 3600 * 1000), 0, now_ms - (12 * day_ms), 0,
                'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80', None,
                'Citizen Watch', 'user-101', 'K. Mukundha (Zonal Administrator)', now_ms - (13 * day_ms),
                'Municipal Rapid Squad 4', now_ms - (13 * day_ms), 'Resolved', 'Collection Truck', 4, '[]', '[]', 0, 0,
                17.0014, 81.8049, None, None, None, 'CLU-W12-SAN', 68, 0.88, 'Transit route container overflow', 48.0, 0.15,
                'sanitation', 'garbage_overflow', 'medium', 1, None, 'Garbage / Waste Accumulation', 'Demo / Rule-Based',
                'HIGH', 12, 'Corroborated by image evidence.', 1, 1, None
            ),
            (
                'ISS-2026-HIST-03', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', 'Market Gate Cross',
                'sanitation', 'Sanitation & Waste Management', '🏢',
                'Historical Garbage Accumulation (Month -1)',
                'Secondary refuse pile logged during previous monthly sanitary survey.',
                'Surampalem • Ward 12 (Market Zone), Market Gate Cross',
                'garbage_overflow', 'Garbage Overflow', '🗑️', 'bulk', 'HISTORICAL LOG', 'resolved',
                now_ms - (35 * day_ms), now_ms - (33 * day_ms), 0, now_ms - (33 * day_ms), 0,
                'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80', None,
                'Sanitation Audit', 'system-fso', 'K. Mukundha (Zonal Administrator)', now_ms - (34 * day_ms),
                'Municipal Rapid Squad 4', now_ms - (34 * day_ms), 'Resolved', 'Tractor / Heavy Squad', 6, '[]', '[]', 0, 0,
                17.0011, 81.8046, None, None, None, 'CLU-W12-SAN', 72, 0.90, 'Monthly survey log', 48.0, 0.10,
                'sanitation', 'garbage_overflow', 'bulk', 1, None, None, None, None, 0, None, 0, 0, None
            ),
            (
                'ISS-2026-HIST-04', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', 'Gandhi Statue Main Road',
                'sanitation', 'Sanitation & Waste Management', '🏢',
                'Historical Carton and Plastic Waste Pile',
                'Packaging materials dumped near commercial intersection.',
                'Surampalem • Ward 12 (Market Zone), Gandhi Statue Main Road',
                'garbage_overflow', 'Garbage Overflow', '🗑️', 'medium', 'HISTORICAL LOG', 'resolved',
                now_ms - (42 * day_ms), now_ms - (40 * day_ms), 0, now_ms - (40 * day_ms), 0,
                'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80', None,
                'Citizen Watch', 'user-101', 'K. Mukundha (Zonal Administrator)', now_ms - (41 * day_ms),
                'Municipal Rapid Squad 4', now_ms - (41 * day_ms), 'Resolved', 'Pushcart Squad', 3, '[]', '[]', 0, 0,
                17.0013, 81.8047, None, None, None, 'CLU-W12-SAN', 64, 0.85, 'Historical log', 48.0, 0.08,
                'sanitation', 'garbage_overflow', 'medium', 1, None, None, None, None, 0, None, 0, 0, None
            ),
            (
                'ISS-2026-HIST-05', 'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', 'Market Gate Cross',
                'sanitation', 'Sanitation & Waste Management', '🏢',
                'Historical Wet Garbage Pile (Prior Quarter)',
                'Quarterly baseline audit record of commercial market litter.',
                'Surampalem • Ward 12 (Market Zone), Market Gate Cross',
                'garbage_overflow', 'Garbage Overflow', '🗑️', 'medium', 'HISTORICAL LOG', 'resolved',
                now_ms - (55 * day_ms), now_ms - (53 * day_ms), 0, now_ms - (53 * day_ms), 0,
                'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80', None,
                'Sanitation Audit', 'system-fso', 'K. Mukundha (Zonal Administrator)', now_ms - (54 * day_ms),
                'Municipal Rapid Squad 4', now_ms - (54 * day_ms), 'Resolved', 'Collection Truck', 2, '[]', '[]', 0, 0,
                17.0010, 81.8044, None, None, None, 'CLU-W12-SAN', 60, 0.80, 'Baseline log', 48.0, 0.05,
                'sanitation', 'garbage_overflow', 'medium', 1, None, None, None, None, 0, None, 0, 0, None
            ),
            (
                'ISS-2026-HIST-06', 'Andhra Pradesh', 'Surampalem', 'Ward 7 (Railway Colony)', 'Station Approach Road',
                'roads', 'Infrastructure / Roads', '🛣️',
                'Severe Crater Pothole near Railway Crossing',
                'Deep asphalt depression causing vehicular swerving and two-wheeler hazard.',
                'Surampalem • Ward 7 (Railway Colony), Station Approach Road',
                'pothole', 'Pothole / Road Damage', '🕳️', 'bulk', 'CRITICAL ROAD HAZARD', 'pending',
                now_ms - (10 * day_ms), now_ms + (38 * 3600 * 1000), 38.0, None, 0,
                'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=800&auto=format&fit=crop&q=80', None,
                'Railway Commuter', 'user-101', 'K. Mukundha (Zonal Administrator)', now_ms - (9 * day_ms),
                'Public Works Squad 2', now_ms - (9 * day_ms), 'Dispatched', 'Tractor / Heavy Squad', 15, '[]', '[]', 0, 0,
                17.0065, 81.8090, None, None, None, 'CLU-W7-ROA', 82, 0.94, 'Active transit crater', 24.0, 0.35,
                'roads', 'pothole', 'bulk', 1, None, 'Pothole / Road Damage', 'Demo / Rule-Based',
                'HIGH', 12, 'Deep asphalt crater confirmed by image evidence.', 1, 1, None
            ),
            (
                'ISS-2026-HIST-07', 'Andhra Pradesh', 'Surampalem', 'Ward 7 (Railway Colony)', 'Railway Goods Shed Road',
                'roads', 'Infrastructure / Roads', '🛣️',
                'Repeated Asphalt Erosion & Road Edge Rutting',
                'Heavy freight transport has caused structural bitumen cracking and potholes.',
                'Surampalem • Ward 7 (Railway Colony), Railway Goods Shed Road',
                'road_damage', 'Pothole / Road Damage', '🕳️', 'high', 'HIGH RISK HAZARD', 'resolved',
                now_ms - (20 * day_ms), now_ms - (18 * day_ms), 0, now_ms - (18 * day_ms), 0,
                'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=800&auto=format&fit=crop&q=80', None,
                'Goods Transporter', 'user-101', 'K. Mukundha (Zonal Administrator)', now_ms - (19 * day_ms),
                'Public Works Squad 2', now_ms - (19 * day_ms), 'Resolved', 'Road Roller & Tar Squad', 11, '[]', '[]', 0, 0,
                17.0068, 81.8095, None, None, None, 'CLU-W7-ROA', 74, 0.90, 'Heavy freight road distress', 48.0, 0.18,
                'roads', 'road_damage', 'high', 1, None, 'Pothole / Road Damage', 'Demo / Rule-Based',
                'HIGH', 12, 'Bitumen distress confirmed.', 1, 1, None
            ),
            (
                'ISS-2026-HIST-08', 'Andhra Pradesh', 'Surampalem', 'Ward 7 (Railway Colony)', 'Station Approach Road',
                'roads', 'Infrastructure / Roads', '🛣️',
                'Historical Pothole Cluster Log (Day -40)',
                'Previous bituminous cold-mix repair logged following heavy monsoon shower.',
                'Surampalem • Ward 7 (Railway Colony), Station Approach Road',
                'pothole', 'Pothole / Road Damage', '🕳️', 'medium', 'HISTORICAL LOG', 'resolved',
                now_ms - (40 * day_ms), now_ms - (38 * day_ms), 0, now_ms - (38 * day_ms), 0,
                'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=800&auto=format&fit=crop&q=80', None,
                'PWD Inspector', 'system-fso', 'K. Mukundha (Zonal Administrator)', now_ms - (39 * day_ms),
                'Public Works Squad 2', now_ms - (39 * day_ms), 'Resolved', 'Collection Truck', 5, '[]', '[]', 0, 0,
                17.0064, 81.8088, None, None, None, 'CLU-W7-ROA', 62, 0.82, 'Historical PWD log', 48.0, 0.05,
                'roads', 'pothole', 'medium', 1, None, None, None, None, 0, None, 0, 0, None
            ),
            (
                'ISS-2026-HIST-09', 'Andhra Pradesh', 'Surampalem', 'Ward 7 (Railway Colony)', 'Railway Staff Quarters Lane',
                'roads', 'Infrastructure / Roads', '🛣️',
                'Historical Broken Road Surface (Day -60)',
                'Quarterly municipal infrastructure survey record of road weathering.',
                'Surampalem • Ward 7 (Railway Colony), Railway Staff Quarters Lane',
                'road_damage', 'Pothole / Road Damage', '🕳️', 'medium', 'HISTORICAL LOG', 'resolved',
                now_ms - (60 * day_ms), now_ms - (58 * day_ms), 0, now_ms - (58 * day_ms), 0,
                'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=800&auto=format&fit=crop&q=80', None,
                'Staff Resident', 'user-101', 'K. Mukundha (Zonal Administrator)', now_ms - (59 * day_ms),
                'Public Works Squad 2', now_ms - (59 * day_ms), 'Resolved', 'Pushcart Squad', 4, '[]', '[]', 0, 0,
                17.0062, 81.8085, None, None, None, 'CLU-W7-ROA', 58, 0.78, 'Baseline survey log', 48.0, 0.02,
                'roads', 'road_damage', 'medium', 1, None, None, None, None, 0, None, 0, 0, None
            ),
            (
                'ISS-2026-HIST-10', 'Andhra Pradesh', 'Surampalem', 'Ward 11 (Lake View Zone)', 'Lake View Bund Road',
                'sanitation', 'Sanitation & Waste Management', '🏢',
                'Storm Drain Silt Blockage near Culvert 3',
                'Fallen leaves and plastic debris choking intake grille causing stormwater backup.',
                'Surampalem • Ward 11 (Lake View Zone), Lake View Bund Road',
                'drain_blockage', 'Drain Blockage / Waterlogging', '🌊', 'high', 'HIGH RISK HAZARD', 'pending',
                now_ms - (12 * day_ms), now_ms + (36 * 3600 * 1000), 36.0, None, 0,
                'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=800&auto=format&fit=crop&q=80', None,
                'Lake Resident', 'user-101', 'K. Mukundha (Zonal Administrator)', now_ms - (11 * day_ms),
                'Municipal Rapid Squad 4', now_ms - (11 * day_ms), 'Dispatched', 'Suction Machine Truck', 9, '[]', '[]', 0, 0,
                17.0012, 81.8040, None, None, None, 'CLU-W11-DRA', 70, 0.88, 'Pre-monsoon runoff choke', 48.0, 0.22,
                'sanitation', 'drain_blockage', 'high', 1, None, 'Standing Water / Waterlogging', 'Demo / Rule-Based',
                'HIGH', 12, 'Grille blockage verified by photo evidence.', 1, 1, None
            ),
            (
                'ISS-2026-HIST-11', 'Andhra Pradesh', 'Surampalem', 'Ward 11 (Lake View Zone)', 'Lake View Main Road',
                'sanitation', 'Sanitation & Waste Management', '🏢',
                'Historical Culvert Silt Accumulation (Day -45)',
                'Seasonal desilting requirement logged during zonal drainage survey.',
                'Surampalem • Ward 11 (Lake View Zone), Lake View Main Road',
                'drain_blockage', 'Drain Blockage / Waterlogging', '🌊', 'medium', 'HISTORICAL LOG', 'resolved',
                now_ms - (45 * day_ms), now_ms - (43 * day_ms), 0, now_ms - (43 * day_ms), 0,
                'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=800&auto=format&fit=crop&q=80', None,
                'Drainage Squad', 'system-fso', 'K. Mukundha (Zonal Administrator)', now_ms - (44 * day_ms),
                'Municipal Rapid Squad 4', now_ms - (44 * day_ms), 'Resolved', 'Tractor / Heavy Squad', 3, '[]', '[]', 0, 0,
                17.0010, 81.8038, None, None, None, 'CLU-W11-DRA', 55, 0.75, 'Seasonal desilting record', 48.0, 0.05,
                'sanitation', 'drain_blockage', 'medium', 1, None, None, None, None, 0, None, 0, 0, None
            ),
            (
                'ISS-2026-HIST-12', 'Andhra Pradesh', 'Surampalem', 'Ward 14 (Campus Zone)', 'College Road Food Court Lane 1',
                'food_safety', 'Food Safety Department', '🍲',
                'Street Food Stall: Oil Reheating & Stale Ingredients',
                'Multiple citizen complaints of reuse of blackened cooking oil and open fly infestation.',
                'Surampalem • Ward 14 (Campus Zone), College Road Food Court Lane 1',
                'food_hygiene', 'Food Safety', '🍱', 'high', 'STATUTORY VIOLATION', 'pending',
                now_ms - (16 * day_ms), now_ms + (32 * 3600 * 1000), 32.0, None, 0,
                'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80', None,
                'Student Council', 'user-101', 'Dr. Lakshmi Prasad (FSO)', now_ms - (15 * day_ms),
                'Food Safety Officer (Dr. Lakshmi Prasad)', now_ms - (15 * day_ms), 'Inspection Scheduled', 'FSO Inspection Squad', 12, '[]', '[]', 0, 0,
                17.0042, 81.8022, None, None, None, 'CLU-W14-FOO', 72, 0.91, 'Campus eatery hygiene violation', 48.0, 0.20,
                'food_safety', 'food_hygiene', 'high', 1, None, 'Food-Safety Visual Concern', 'Demo / Rule-Based',
                'HIGH', 12, 'Observable indicators of food hygiene violation.', 1, 1, None
            ),
            (
                'ISS-2026-HIST-13', 'Andhra Pradesh', 'Surampalem', 'Ward 3 (Residential Colony)', 'Rose Garden Street',
                'water_supply', 'Water Supply', '💧',
                'Minor Potable Pipeline Joint Seepage',
                'Mild groundwater dampness reported near municipal water valve chamber.',
                'Surampalem • Ward 3 (Residential Colony), Rose Garden Street',
                'water_leakage', 'Water Supply / Pipeline Leakage', '🚰', 'low', 'STANDARD COMPLAINT', 'resolved',
                now_ms - (50 * day_ms), now_ms - (48 * day_ms), 0, now_ms - (48 * day_ms), 0,
                'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&auto=format&fit=crop&q=80', None,
                'Colony Resident', 'user-101', 'K. Mukundha (Zonal Administrator)', now_ms - (49 * day_ms),
                'Public Works Squad 2', now_ms - (49 * day_ms), 'Resolved', 'Pushcart Squad', 2, '[]', '[]', 0, 0,
                None, None, None, None, None, None, 35, 0.65, 'Minor valve seal check', 48.0, 0.02,
                'water_supply', 'water_leakage', 'low', 1, None, None, None, None, 0, None, 0, 0, None
            )
        ]

        cursor.executemany('''
            INSERT OR IGNORE INTO issues (
                id, state, city, ward, street, department, deptName, deptIcon, title,
                description, location, category, categoryName, categoryIcon, severity,
                severityLabel, status, timestamp, slaDeadline, slaHoursLeft, resolvedTimestamp,
                isSlaBreached, imageBefore, imageAfter, reportedBy, reportedById, verifiedByOfficer,
                verifiedTimestamp, assignedWorker, assignedTimestamp, workerStatus,
                recommendedResource, upvotes, upvotedBy, comments, rewardIssued, fineLevied,
                lat, lng, vendorId, vendorName, mq135GasPpm, clusterId, aiRiskScore,
                aiConfidence, aiReasoning, aiSuggestedSLA, slaBreachProb, aiSuggestedDepartment,
                aiSuggestedCategory, aiSuggestedSeverity, citizenConfirmedAI, aiOverrideReason,
                imageAiHazard, imageAiConfidence, imageTextConsistency, imageRiskModifier,
                imageAiReasoning, imageAiAccepted, imageOfficerVerified, imageOfficerOverrideReason
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', hist_issues)
        conn.commit()
        print(f"[Phase 4/E Seeding] Verified {len(hist_issues)} baseline historical incidents across wards.")

    generate_deterministic_forecasts(conn)

def calculate_predictive_risk(ward, category_name, dept, all_issues):
    now_ms = int(time.time() * 1000)
    day_ms = 86400 * 1000
    cat_lower = category_name.lower()
    dept_lower = dept.lower()

    matched = []
    for iss in all_issues:
        i_ward = str(iss.get('ward') or '')
        i_cat = str(iss.get('category') or '').lower()
        i_title = str(iss.get('title') or '').lower()
        i_dept = str(iss.get('department') or '').lower()

        ward_id = ward.split('(')[0].strip().lower()
        if ward_id not in i_ward.lower():
            continue

        hit = False
        if 'garbage' in cat_lower and ('garbage' in i_cat or 'garbage' in i_title or 'waste' in i_title or 'sanitation' in i_cat):
            hit = True
        elif 'pothole' in cat_lower and ('pothole' in i_cat or 'pothole' in i_title or 'road' in i_title or 'road' in i_cat):
            hit = True
        elif 'electric' in cat_lower and ('spark' in i_cat or 'electric' in i_dept or 'wire' in i_title or 'power' in i_title):
            hit = True
        elif 'drain' in cat_lower and ('drain' in i_cat or 'drain' in i_title or 'waterlog' in i_title):
            hit = True
        elif 'food' in cat_lower and ('food' in i_cat or 'food' in i_dept or 'hygiene' in i_title):
            hit = True
        elif 'water supply' in cat_lower and ('water' in i_cat or 'pipe' in i_title or 'water_supply' in i_dept):
            hit = True

        if hit:
            matched.append(iss)

    unique_matched = [i for i in matched if not i.get('parentIssueId')]
    unique_count = len(unique_matched)
    total_followups = sum(int(i.get('followUpCount') or 0) for i in unique_matched)
    citizen_report_count = len(matched) + total_followups

    hist_count = len(matched)
    recent_issues = [i for i in matched if (now_ms - (i.get('timestamp') or 0)) <= (30 * day_ms)]
    recent_count = len(recent_issues)
    recent_unique = [i for i in unique_matched if (now_ms - (i.get('timestamp') or 0)) <= (30 * day_ms)]
    recent_unique_count = len(recent_unique)

    if hist_count == 0:
        return {
            'predictiveRiskScore': 14,
            'riskLevel': 'LOW',
            'recurrenceIndicator': 'INSUFFICIENT HISTORICAL DATA',
            'slaBreachIndicator': 'Normal SLA Adherence',
            'confidenceLabel': 'Demo / Rule-Based — Insufficient Historical Data',
            'historicalIncidentCount': 0,
            'recentIncidentCount': 0,
            'uniqueIncidentCount': 0,
            'citizenReportCount': 0,
            'contributingFactors': [
                'No historical incidents recorded in this zone',
                'Baseline monitoring only',
                'Routine preventive schedule active'
            ]
        }

    if (recent_count >= 2 and hist_count >= 4) or (recent_count >= 4 or hist_count >= 6):
        recurrence_indicator = 'STRONG'
        w_recurrence = 20.0
    elif hist_count >= 3 or recent_count >= 2:
        recurrence_indicator = 'MODERATE'
        w_recurrence = 10.0
    else:
        recurrence_indicator = 'INSUFFICIENT HISTORICAL DATA'
        w_recurrence = 3.0

    w_freq = min(30.0, hist_count * 4.0)
    w_recency = min(20.0, recent_count * 4.5)

    has_bulk = any(i.get('severity') in ['bulk', 'critical'] for i in matched)
    has_high = any(i.get('severity') == 'high' for i in matched)
    w_sev = 9.0 if has_bulk else (7.0 if has_high else 4.0)

    has_sla_breach = any(i.get('isSlaBreached') == 1 or str(i.get('status') or '').lower() == 'escalated' for i in matched)
    w_sla = 9.0 if has_sla_breach else 3.0
    sla_indicator = 'Repeated Delays & SLA Breaches Detected' if has_sla_breach else 'Normal SLA Adherence'

    ai_risks = [i.get('aiRiskScore') for i in matched if i.get('aiRiskScore') is not None]
    avg_ai = (sum(ai_risks) / len(ai_risks)) if ai_risks else 70.0
    img_mods = [i.get('imageRiskModifier') for i in matched if i.get('imageRiskModifier') is not None]
    avg_img = (sum(img_mods) / len(img_mods)) if img_mods else 0.0
    w_ai = max(1.0, min(10.0, ((avg_ai + avg_img) / 100.0) * 10.0))

    pred_score = int(round(w_freq + w_recency + w_recurrence + w_sev + w_sla + w_ai))
    pred_score = max(5, min(100, pred_score))

    if pred_score >= 80:
        risk_level = 'CRITICAL'
    elif pred_score >= 60:
        risk_level = 'HIGH'
    elif pred_score >= 30:
        risk_level = 'MODERATE'
    else:
        risk_level = 'LOW'

    confidence_label = 'Historical Pattern Strength: Strong' if recurrence_indicator == 'STRONG' else (
        'Historical Pattern Strength: Moderate' if recurrence_indicator == 'MODERATE' else 'Demo / Rule-Based — Insufficient Historical Data'
    )

    factors = [
        f"{unique_count} unique incident(s) with {citizen_report_count} citizen report(s) & follow-up(s) in {ward}",
        f"{recent_unique_count} unique incident(s) ({recent_count} total reports) in last 30 days",
        f"{recurrence_indicator} pattern evaluated",
        sla_indicator,
        f"Historical severity profile ({'High/Critical' if has_bulk or has_high else 'Standard'})"
    ]

    return {
        'predictiveRiskScore': pred_score,
        'riskLevel': risk_level,
        'recurrenceIndicator': recurrence_indicator,
        'slaBreachIndicator': sla_indicator,
        'confidenceLabel': confidence_label,
        'historicalIncidentCount': hist_count,
        'recentIncidentCount': recent_count,
        'uniqueIncidentCount': unique_count,
        'citizenReportCount': citizen_report_count,
        'contributingFactors': factors
    }

def evaluate_prevention_recurrence(cursor, forecast_id):
    """
    Evaluates real post-intervention recurrence against pre-intervention baseline.
    Uses strictly neutral terminology ('Observed change' / 'Recurrence trend').
    """
    cursor.execute("SELECT * FROM predictive_forecasts WHERE id = ?", (forecast_id,))
    fst = cursor.fetchone()
    if not fst:
        return None
    fst_dict = dict(fst)
    ward = fst_dict.get('ward') or ''
    ward_num = ''.join(filter(str.isdigit, ward))
    dept = fst_dict.get('department') or ''

    cursor.execute("SELECT * FROM preventive_actions WHERE forecastId = ? ORDER BY createdAt DESC LIMIT 1", (forecast_id,))
    act = cursor.fetchone()
    act_dict = dict(act) if act else None

    # Query matching issues
    cursor.execute("SELECT * FROM issues WHERE ward LIKE ? AND department = ?", (f"%{ward_num}%", dept))
    all_matched = [dict(r) for r in cursor.fetchall()]

    now_ms = int(time.time() * 1000)
    day_ms = 86400 * 1000

    if not act_dict or not act_dict.get('implementedAt'):
        hist_count = len(all_matched)
        recent_count = len([i for i in all_matched if (now_ms - (i.get('timestamp') or 0)) <= (30 * day_ms)])
        if hist_count < 3 or recent_count < 2:
            trend = 'INSUFFICIENT HISTORICAL DATA'
            trend_notes = 'Insufficient historical data to establish recurring baseline.'
        else:
            trend = 'RECURRING'
            trend_notes = 'Recurring incidents observed in this zone. Preventive action recommended.'
        return {
            'trend': trend,
            'trendNotes': trend_notes,
            'preCount': recent_count,
            'postCount': 0,
            'status': 'PENDING_IMPLEMENTATION'
        }

    impl_at = act_dict['implementedAt']
    pre_window_start = impl_at - (30 * day_ms)
    pre_issues = [i for i in all_matched if (i.get('timestamp') or 0) >= pre_window_start and (i.get('timestamp') or 0) <= impl_at]
    post_issues = [i for i in all_matched if (i.get('timestamp') or 0) > impl_at]

    pre_count = len(pre_issues)
    post_count = len(post_issues)

    if post_count >= 2:
        trend = 'PREVENTION REVIEW REQUIRED'
        trend_notes = f"Recurring incidents continue after the previous intervention ({post_count} incidents reported since intervention). Operational review recommended: review collection frequency and reassess container infrastructure."
        status = 'PREVENTION_REVIEW_REQUIRED'
        log_operational_audit(cursor, forecast_id, 'Civic AI Predictive Engine', 'PREVENTION_REVIEW_REQUIRED', None, trend_notes)
    elif post_count == 0 or post_count < pre_count:
        trend = 'IMPROVING'
        trend_notes = f"Observed recurrence decreased after intervention ({pre_count} incidents before vs {post_count} after intervention)."
        status = 'UNDER_PREVENTIVE_MONITORING'
    else:
        trend = 'STABLE'
        trend_notes = "Observed recurrence pattern remains stable under routine monitoring."
        status = 'UNDER_PREVENTIVE_MONITORING'

    cursor.execute('''
        UPDATE preventive_actions
        SET recurrenceTrend = ?, trendNotes = ?, monitoringStatus = ?
        WHERE id = ?
    ''', (trend, trend_notes, status, act_dict['id']))

    cursor.execute('''
        UPDATE predictive_forecasts
        SET recurrenceIndicator = ?, reviewReason = ?
        WHERE id = ?
    ''', (trend, trend_notes, forecast_id))

    return {
        'trend': trend,
        'trendNotes': trend_notes,
        'preCount': pre_count,
        'postCount': post_count,
        'status': status
    }

def generate_deterministic_forecasts(conn=None):
    close_conn = False
    if conn is None:
        conn = sqlite3.connect('civic_database.db')
        conn.row_factory = sqlite3.Row
        close_conn = True

    cursor = conn.cursor()
    init_predictive_tables(cursor)
    cursor.execute("SELECT * FROM issues")
    all_issues = [dict(r) for r in cursor.fetchall()]

    now_ms = int(time.time() * 1000)
    forecast_results = []

    for item in CANONICAL_TARGETS:
        ward = item['ward']
        category = item['category']
        dept = item['department']
        rec = item['recommendation']
        root_causes = item.get('rootCauses', {})
        clean_zone = item.get('cleanZone')
        fst_id = f"FST-2026-W{item['wardNum']}-{item['slug']}"
        action_id = f"ACT-PREV-W{item['wardNum']}-{item['slug']}"
        hotspot_id = f"HOTSPOT-W{item['wardNum']}"

        analysis = calculate_predictive_risk(ward, category, dept, all_issues)
        factors_json = json.dumps(analysis['contributingFactors'])
        root_causes_json = json.dumps(root_causes)

        cursor.execute("SELECT status, reviewedBy, reviewedAt, reviewReason FROM predictive_forecasts WHERE id = ?", (fst_id,))
        existing_fst = cursor.fetchone()
        fst_status = existing_fst[0] if existing_fst else 'PENDING_HUMAN_REVIEW'
        reviewed_by = existing_fst[1] if existing_fst else None
        reviewed_at = existing_fst[2] if existing_fst else None
        review_reason = existing_fst[3] if existing_fst else None

        clean_zone_name = clean_zone.get('name') if clean_zone else None

        cursor.execute('''
            INSERT INTO predictive_forecasts (
                id, hotspotId, ward, category, department, predictiveRiskScore, riskLevel,
                forecastHorizon, historicalIncidentCount, recentIncidentCount, recurrenceIndicator,
                slaBreachIndicator, contributingFactors, preventiveRecommendation, confidenceLabel,
                source, status, createdAt, reviewedBy, reviewedAt, reviewReason, rootCauses, cleanZoneName,
                uniqueIncidentCount, citizenReportCount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                predictiveRiskScore = excluded.predictiveRiskScore,
                riskLevel = excluded.riskLevel,
                historicalIncidentCount = excluded.historicalIncidentCount,
                recentIncidentCount = excluded.recentIncidentCount,
                uniqueIncidentCount = excluded.uniqueIncidentCount,
                citizenReportCount = excluded.citizenReportCount,
                recurrenceIndicator = excluded.recurrenceIndicator,
                slaBreachIndicator = excluded.slaBreachIndicator,
                contributingFactors = excluded.contributingFactors,
                confidenceLabel = excluded.confidenceLabel,
                rootCauses = excluded.rootCauses,
                cleanZoneName = excluded.cleanZoneName
        ''', (
            fst_id, hotspot_id, ward, category, dept,
            analysis['predictiveRiskScore'], analysis['riskLevel'], 'Next 7 Days',
            analysis['historicalIncidentCount'], analysis['recentIncidentCount'],
            analysis['recurrenceIndicator'], analysis['slaBreachIndicator'],
            factors_json, rec, analysis['confidenceLabel'],
            'Demo / Historical Incident Dataset', fst_status, now_ms,
            reviewed_by, reviewed_at, review_reason, root_causes_json, clean_zone_name,
            analysis.get('uniqueIncidentCount', analysis['historicalIncidentCount']),
            analysis.get('citizenReportCount', analysis['historicalIncidentCount'])
        ))

        # Audit forecast generation
        log_operational_audit(cursor, fst_id, 'Civic AI Predictive Engine', 'PREDICTIVE_FORECAST_CREATED', None, f"Rule-based forecast calculated for {ward} ({category})")
        log_operational_audit(cursor, hotspot_id, 'Civic AI Predictive Engine', 'HOTSPOT_IDENTIFIED', None, f"Civic hotspot tracked in {ward}")

        cursor.execute("SELECT status, assignedWorker, implementedAt, monitoringStatus, recurrenceTrend, trendNotes FROM preventive_actions WHERE id = ?", (action_id,))
        existing_act = cursor.fetchone()
        if not existing_act:
            priority = 'Critical' if analysis['riskLevel'] == 'CRITICAL' else ('High' if analysis['riskLevel'] == 'HIGH' else 'Routine')
            cursor.execute('''
                INSERT INTO preventive_actions (
                    id, forecastId, action, department, priority, status, createdBy, createdAt, rootCauses, ward
                ) VALUES (?, ?, ?, ?, ?, 'PENDING_OFFICER_APPROVAL', 'Civic AI Predictive Engine', ?, ?, ?)
            ''', (action_id, fst_id, rec, dept, priority, now_ms, root_causes_json, ward))
            log_operational_audit(cursor, action_id, 'Civic AI Predictive Engine', 'PREVENTIVE_ACTION_RECOMMENDED', None, rec)

        audit_id = f"AUDIT-FST-{fst_id}-{now_ms}-{uuid.uuid4().hex[:6]}"
        cursor.execute('''
            INSERT OR REPLACE INTO ai_predictions (
                id, entityType, entityId, predictionType, confidenceScore, reasoning, recommendedAction, createdAt
            ) VALUES (?, 'forecast', ?, 'predictive_hotspot_forecast', ?, ?, ?, ?)
        ''', (
            audit_id, fst_id, analysis['predictiveRiskScore'],
            factors_json, rec, now_ms
        ))

        forecast_results.append({
            'id': fst_id,
            'hotspotId': hotspot_id,
            'ward': ward,
            'category': category,
            'department': dept,
            'predictiveRiskScore': analysis['predictiveRiskScore'],
            'riskLevel': analysis['riskLevel'],
            'forecastHorizon': 'Next 7 Days',
            'historicalIncidentCount': analysis['historicalIncidentCount'],
            'recentIncidentCount': analysis['recentIncidentCount'],
            'uniqueIncidentCount': analysis.get('uniqueIncidentCount', analysis['historicalIncidentCount']),
            'citizenReportCount': analysis.get('citizenReportCount', analysis['historicalIncidentCount']),
            'recurrenceIndicator': analysis['recurrenceIndicator'],
            'slaBreachIndicator': analysis['slaBreachIndicator'],
            'contributingFactors': analysis['contributingFactors'],
            'preventiveRecommendation': rec,
            'rootCauses': root_causes,
            'cleanZone': clean_zone,
            'confidenceLabel': analysis['confidenceLabel'],
            'source': 'Demo / Historical Incident Dataset',
            'status': fst_status,
            'createdAt': now_ms,
            'actionId': action_id
        })

    conn.commit()
    if close_conn:
        conn.close()

    return forecast_results

def handle_predictive_get(handler, path, query, auth_user=None):
    if path == '/api/predictive-hotspots':
        conn = sqlite3.connect('civic_database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        req_ward = query.get('ward', [None])[0]
        req_cat = query.get('category', [None])[0]

        # Authoritative server-side jurisdiction authorization
        if auth_user:
            user_dept = auth_user.get('department')
            user_ward = auth_user.get('jurisdictionWard')

            # 1. Municipal Officer: restricted to municipal departments (department != 'food_safety')
            if user_dept == 'municipal':
                if req_cat and 'food' in req_cat.lower():
                    conn.close()
                    handler.send_json_response({'success': False, 'error': 'Forbidden: Municipal Officers cannot access Food Safety jurisdiction.'}, status=403)
                    return True
                if user_ward and user_ward != 'ALL':
                    if req_ward and req_ward != 'all' and user_ward.lower() not in req_ward.lower():
                        conn.close()
                        handler.send_json_response({'success': False, 'error': f'Forbidden: You are restricted to your assigned jurisdiction ({user_ward}).'}, status=403)
                        return True

            # 2. Food Safety Officer: strictly restricted to food_safety
            elif user_dept in ['food', 'food_safety']:
                if req_cat and 'food' not in req_cat.lower() and req_cat != 'all':
                    conn.close()
                    handler.send_json_response({'success': False, 'error': 'Forbidden: Food Safety Officers are restricted to food hygiene data.'}, status=403)
                    return True

        sql = "SELECT pf.*, pa.id as actionId, pa.status as actionStatus, pa.priority as actionPriority, pa.action as actionText, pa.assignedWorker, pa.implementedAt, pa.implementedNotes, pa.monitoringStatus, pa.recurrenceTrend, pa.trendNotes FROM predictive_forecasts pf LEFT JOIN preventive_actions pa ON pf.id = pa.forecastId"
        params = []
        clauses = []

        if auth_user:
            user_dept = auth_user.get('department')
            user_ward = auth_user.get('jurisdictionWard')
            if user_dept == 'municipal':
                clauses.append("pf.department != 'food_safety'")
                if user_ward and user_ward != 'ALL':
                    clauses.append("pf.ward LIKE ?")
                    params.append(f"%{user_ward}%")
            elif user_dept in ['food', 'food_safety']:
                clauses.append("pf.department = 'food_safety'")

        if req_ward and req_ward != 'all':
            clauses.append("pf.ward LIKE ?")
            params.append(f"%{req_ward}%")
        if req_cat and req_cat != 'all':
            clauses.append("pf.category LIKE ?")
            params.append(f"%{req_cat}%")
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY pf.predictiveRiskScore DESC"

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        forecasts = []
        for r in rows:
            item = dict(r)
            try:
                item['contributingFactors'] = json.loads(item.get('contributingFactors') or '[]')
            except Exception:
                item['contributingFactors'] = []
            try:
                item['rootCauses'] = json.loads(item.get('rootCauses') or '{}')
            except Exception:
                item['rootCauses'] = {}

            # Recalculate dynamic recurrence trend from actual DB issues
            eval_res = evaluate_prevention_recurrence(cursor, item['id'])
            if eval_res:
                item['recurrenceTrend'] = eval_res['trend']
                item['trendNotes'] = eval_res['trendNotes']
                if eval_res['trend'] == 'INSUFFICIENT HISTORICAL DATA':
                    item['recurrenceIndicator'] = 'INSUFFICIENT HISTORICAL DATA'

            # Clean Zone metadata
            w_str = str(item.get('ward') or '')
            if 'Ward 12' in w_str and item.get('department') == 'sanitation':
                item['cleanZone'] = {
                    'name': 'Market Canteen Gate, Ward 12',
                    'status': item.get('monitoringStatus') or 'UNDER PREVENTIVE MONITORING',
                    'guidance': 'Please use designated waste collection points and avoid leaving waste outside collection areas.'
                }
            else:
                item['cleanZone'] = None

            item['ward_name'] = item.get('ward')
            item['civic_category'] = item.get('category')
            item['predicted_risk_score'] = item.get('predictiveRiskScore')
            item['predicted_risk_level'] = item.get('riskLevel')
            item['recurrence_pattern'] = item.get('recurrenceIndicator')
            item['sla_breach_indicator'] = item.get('slaBreachIndicator')
            item['contributing_factors'] = item.get('contributingFactors')
            item['recommended_preventive_action'] = item.get('preventiveRecommendation')
            item['forecast_horizon'] = item.get('forecastHorizon')
            item['historical_incident_count'] = item.get('historicalIncidentCount')
            item['recent_incident_count'] = item.get('recentIncidentCount')
            item['unique_incident_count'] = item.get('uniqueIncidentCount') or item.get('historicalIncidentCount')
            item['citizen_report_count'] = item.get('citizenReportCount') or item.get('historicalIncidentCount')

            if 'Ward 12' in w_str:
                item['lat'], item['lng'] = 17.0010, 81.8045
            elif 'Ward 7' in w_str:
                item['lat'], item['lng'] = 17.0065, 81.8090
            elif 'Ward 11' in w_str:
                item['lat'], item['lng'] = 17.0012, 81.8040
            elif 'Ward 14' in w_str:
                item['lat'], item['lng'] = 17.0040, 81.8020
            else:
                item['lat'], item['lng'] = None, None

            forecasts.append(item)

        conn.commit()
        conn.close()
        handler.send_json_response({
            'success': True,
            'forecasts': forecasts,
            'data': forecasts,
            'total': len(forecasts),
            'forecastHorizon': 'Next 7 Days',
            'source': 'Demo / Historical Incident Dataset',
            'modelCapability': 'AI-Assisted Predictive Demo — Transparent Rule-Based Forecast (No ML Model Configured)'
        })
        return True

    if path.startswith('/api/predictive-hotspots/'):
        fst_id = path.split('/api/predictive-hotspots/')[1].strip()
        conn = sqlite3.connect('civic_database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictive_forecasts WHERE id = ?", (fst_id,))
        fst_row = cursor.fetchone()
        if not fst_row:
            conn.close()
            handler.send_json_response({'success': False, 'error': f'Forecast {fst_id} not found.'}, status=404)
            return True

        fst_dict = dict(fst_row)

        if auth_user:
            user_dept = auth_user.get('department')
            user_ward = auth_user.get('jurisdictionWard')
            if user_dept == 'municipal':
                if fst_dict.get('department') == 'food_safety':
                    conn.close()
                    handler.send_json_response({'success': False, 'error': 'Forbidden: Municipal Officers cannot inspect Food Safety forecasts.'}, status=403)
                    return True
                if user_ward and user_ward != 'ALL' and user_ward.lower() not in (fst_dict.get('ward') or '').lower():
                    conn.close()
                    handler.send_json_response({'success': False, 'error': f'Forbidden: You are restricted to your assigned jurisdiction ({user_ward}).'}, status=403)
                    return True
            elif user_dept in ['food', 'food_safety']:
                if fst_dict.get('department') != 'food_safety':
                    conn.close()
                    handler.send_json_response({'success': False, 'error': 'Forbidden: Food Safety Officers are restricted to food hygiene data.'}, status=403)
                    return True

        try:
            fst_dict['contributingFactors'] = json.loads(fst_dict.get('contributingFactors') or '[]')
        except Exception:
            fst_dict['contributingFactors'] = []
        try:
            fst_dict['rootCauses'] = json.loads(fst_dict.get('rootCauses') or '{}')
        except Exception:
            fst_dict['rootCauses'] = {}

        eval_res = evaluate_prevention_recurrence(cursor, fst_id)
        if eval_res:
            fst_dict['recurrenceTrend'] = eval_res['trend']
            fst_dict['trendNotes'] = eval_res['trendNotes']
            if eval_res['trend'] == 'INSUFFICIENT HISTORICAL DATA':
                fst_dict['recurrenceIndicator'] = 'INSUFFICIENT HISTORICAL DATA'

        cursor.execute("SELECT * FROM preventive_actions WHERE forecastId = ?", (fst_id,))
        actions = [dict(r) for r in cursor.fetchall()]
        conn.commit()
        conn.close()

        handler.send_json_response({
            'success': True,
            'forecast': fst_dict,
            'preventiveActions': actions,
            'modelCapability': 'AI-Assisted Predictive Demo — Transparent Rule-Based Forecast (No ML Model Configured)',
            'isAdvisoryOnly': True
        })
        return True

    if path == '/api/preventive-actions':
        conn = sqlite3.connect('civic_database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        where_clause = ""
        params = []
        if auth_user:
            user_dept = auth_user.get('department')
            user_ward = auth_user.get('jurisdictionWard')
            clauses = []
            if user_dept == 'municipal':
                clauses.append("pf.department != 'food_safety'")
                if user_ward and user_ward != 'ALL':
                    clauses.append("pf.ward LIKE ?")
                    params.append(f"%{user_ward}%")
            elif user_dept in ['food', 'food_safety']:
                clauses.append("pf.department = 'food_safety'")
            if clauses:
                where_clause = "WHERE " + " AND ".join(clauses)

        cursor.execute(f'''
            SELECT pa.*, pf.ward, pf.category, pf.predictiveRiskScore, pf.riskLevel 
            FROM preventive_actions pa 
            JOIN predictive_forecasts pf ON pa.forecastId = pf.id 
            {where_clause}
            ORDER BY pa.createdAt DESC
        ''', params)
        raw_rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        rows = []
        for r in raw_rows:
            r['forecast_id'] = r.get('forecastId')
            r['recommended_action'] = r.get('action')
            r['rejection_reason'] = r.get('rejectionReason')
            r['modification_reason'] = r.get('modificationReason')
            r['approved_by'] = r.get('approvedBy')
            r['approved_at'] = r.get('approvedAt')
            r['modified_action'] = r.get('action')
            st = str(r.get('status') or '').lower()
            if 'approve' in st: r['status'] = 'approved'
            elif 'reject' in st: r['status'] = 'rejected'
            elif 'modif' in st: r['status'] = 'modified'
            elif 'assign' in st: r['status'] = 'assigned'
            elif 'implement' in st: r['status'] = 'implemented'
            else: r['status'] = 'pending_review'
            rows.append(r)
        handler.send_json_response({'success': True, 'actions': rows, 'data': rows, 'total': len(rows)})
        return True

    return False

def handle_predictive_post(handler, path, body, sse_hub=None, auth_user=None):
    if path == '/api/ai/predictive-hotspots':
        forecasts = generate_deterministic_forecasts()
        if sse_hub:
            sse_hub.broadcast('PREDICTIVE_HOTSPOTS_REFRESHED', {'count': len(forecasts), 'timestamp': int(time.time() * 1000)})
        handler.send_json_response({
            'success': True,
            'forecasts': forecasts,
            'total': len(forecasts),
            'message': 'Predictive forecasts refreshed from historical incident dataset.',
            'modelCapability': 'AI-Assisted Predictive Demo — Transparent Rule-Based Forecast (No ML Model Configured)',
            'isAdvisoryOnly': True
        })
        return True

    # 1. Approve Preventive Action
    if path == '/api/preventive-actions/approve':
        if not auth_user:
            handler.send_json_response({'success': False, 'error': 'Unauthorized: Authentication required.'}, status=401)
            return True

        if auth_user.get('roleTitle') == 'worker' or auth_user.get('department') == 'worker':
            handler.send_json_response({'success': False, 'error': 'Forbidden: Workers cannot authorize preventive governance plans.'}, status=403)
            return True

        act_id = body.get('action_id') or body.get('actionId') or body.get('id')
        officer_name = auth_user.get('name') or auth_user.get('officialId') or 'K. Mukundha (Zonal Administrator)'
        note = (body.get('notes') or body.get('note') or 'Officer authorized preventive action schedule').strip()

        if not act_id:
            handler.send_json_response({'success': False, 'error': 'actionId is required.'}, status=400)
            return True

        conn = sqlite3.connect('civic_database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM preventive_actions WHERE id = ?", (act_id,))
        act_row = cursor.fetchone()
        if not act_row:
            conn.close()
            handler.send_json_response({'success': False, 'error': f'Preventive action {act_id} not found.'}, status=404)
            return True

        act_dict = dict(act_row)
        fst_id = act_dict.get('forecastId')

        cursor.execute("SELECT * FROM predictive_forecasts WHERE id = ?", (fst_id,))
        fst_row = cursor.fetchone()
        if fst_row:
            fst_dict = dict(fst_row)
            user_dept = auth_user.get('department')
            user_ward = auth_user.get('jurisdictionWard')
            if user_dept == 'municipal':
                if fst_dict.get('department') == 'food_safety':
                    conn.close()
                    handler.send_json_response({'success': False, 'error': 'Forbidden: Municipal Officers cannot approve Food Safety plans.'}, status=403)
                    return True
                if user_ward and user_ward != 'ALL' and user_ward.lower() not in (fst_dict.get('ward') or '').lower():
                    conn.close()
                    handler.send_json_response({'success': False, 'error': f'Forbidden: Officer is restricted to assigned ward ({user_ward}).'}, status=403)
                    return True
            elif user_dept in ['food', 'food_safety']:
                if fst_dict.get('department') != 'food_safety':
                    conn.close()
                    handler.send_json_response({'success': False, 'error': 'Forbidden: Food Safety Officers cannot approve municipal civic plans.'}, status=403)
                    return True

        now_ms = int(time.time() * 1000)
        cursor.execute('''
            UPDATE preventive_actions
            SET status = 'OFFICER_APPROVED', approvedBy = ?, approvedAt = ?
            WHERE id = ?
        ''', (officer_name, now_ms, act_id))

        if fst_id:
            cursor.execute('''
                UPDATE predictive_forecasts
                SET status = 'OFFICER_APPROVED', reviewedBy = ?, reviewedAt = ?, reviewReason = ?
                WHERE id = ?
            ''', (officer_name, now_ms, note, fst_id))

        log_operational_audit(cursor, act_id, officer_name, 'PREVENTIVE_ACTION_APPROVED', None, f"Officer {officer_name} approved preventive plan {act_id}. Note: {note}")
        conn.commit()

        cursor.execute("SELECT * FROM preventive_actions WHERE id = ?", (act_id,))
        updated_act = dict(cursor.fetchone())
        conn.close()

        if sse_hub:
            sse_hub.broadcast('PREVENTIVE_ACTION_UPDATED', updated_act)

        updated_act['status'] = 'approved'
        updated_act['approved_by'] = officer_name
        updated_act['approved_at'] = now_ms
        updated_act['forecast_id'] = fst_id
        handler.send_json_response({
            'success': True,
            'action': updated_act,
            'data': updated_act,
            'forecastId': fst_id,
            'status': 'approved',
            'approved_by': officer_name,
            'approvedBy': officer_name,
            'approvedAt': now_ms,
            'message': f'Preventive action {act_id} approved by officer {officer_name}.'
        })
        return True

    # 2. Reject Preventive Action (Justification Mandatory)
    if path == '/api/preventive-actions/reject':
        if not auth_user:
            handler.send_json_response({'success': False, 'error': 'Unauthorized: Authentication required.'}, status=401)
            return True

        if auth_user.get('roleTitle') == 'worker' or auth_user.get('department') == 'worker':
            handler.send_json_response({'success': False, 'error': 'Forbidden: Workers cannot reject preventive plans.'}, status=403)
            return True

        act_id = body.get('action_id') or body.get('actionId') or body.get('id')
        officer_name = auth_user.get('name') or auth_user.get('officialId') or 'K. Mukundha (Zonal Administrator)'
        reason = (body.get('justification') or body.get('reason') or body.get('rejectionReason') or '').strip()

        if not act_id:
            handler.send_json_response({'success': False, 'error': 'actionId is required.'}, status=400)
            return True

        if not reason:
            handler.send_json_response({
                'success': False,
                'error': 'A non-empty justification is mandatory when rejecting an AI-recommended preventive action.'
            }, status=400)
            return True

        conn = sqlite3.connect('civic_database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM preventive_actions WHERE id = ?", (act_id,))
        act_row = cursor.fetchone()
        if not act_row:
            conn.close()
            handler.send_json_response({'success': False, 'error': f'Preventive action {act_id} not found.'}, status=404)
            return True

        act_dict = dict(act_row)
        fst_id = act_dict.get('forecastId')

        cursor.execute("SELECT * FROM predictive_forecasts WHERE id = ?", (fst_id,))
        fst_row = cursor.fetchone()
        if fst_row:
            fst_dict = dict(fst_row)
            user_dept = auth_user.get('department')
            user_ward = auth_user.get('jurisdictionWard')
            if user_dept == 'municipal':
                if fst_dict.get('department') == 'food_safety':
                    conn.close()
                    handler.send_json_response({'success': False, 'error': 'Forbidden: Municipal Officers cannot reject Food Safety plans.'}, status=403)
                    return True
                if user_ward and user_ward != 'ALL' and user_ward.lower() not in (fst_dict.get('ward') or '').lower():
                    conn.close()
                    handler.send_json_response({'success': False, 'error': f'Forbidden: Officer is restricted to assigned ward ({user_ward}).'}, status=403)
                    return True
            elif user_dept in ['food', 'food_safety']:
                if fst_dict.get('department') != 'food_safety':
                    conn.close()
                    handler.send_json_response({'success': False, 'error': 'Forbidden: Food Safety Officers cannot reject municipal civic plans.'}, status=403)
                    return True

        now_ms = int(time.time() * 1000)
        cursor.execute('''
            UPDATE preventive_actions
            SET status = 'OFFICER_REJECTED', rejectionReason = ?, approvedBy = ?, approvedAt = ?
            WHERE id = ?
        ''', (reason, officer_name, now_ms, act_id))

        if fst_id:
            cursor.execute('''
                UPDATE predictive_forecasts
                SET status = 'OFFICER_REJECTED', reviewedBy = ?, reviewedAt = ?, reviewReason = ?
                WHERE id = ?
            ''', (officer_name, now_ms, reason, fst_id))

        log_operational_audit(cursor, act_id, officer_name, 'PREVENTIVE_ACTION_REJECTED', None, f"Officer {officer_name} rejected plan {act_id}. Justification: {reason}")
        conn.commit()

        cursor.execute("SELECT * FROM preventive_actions WHERE id = ?", (act_id,))
        updated_act = dict(cursor.fetchone())
        conn.close()

        if sse_hub:
            sse_hub.broadcast('PREVENTIVE_ACTION_UPDATED', updated_act)

        updated_act['status'] = 'rejected'
        updated_act['rejection_reason'] = reason
        updated_act['forecast_id'] = fst_id
        handler.send_json_response({
            'success': True,
            'action': updated_act,
            'data': updated_act,
            'forecastId': fst_id,
            'status': 'rejected',
            'rejection_reason': reason,
            'rejectionReason': reason,
            'reviewedBy': officer_name,
            'message': f'Preventive action {act_id} rejected with recorded justification.'
        })
        return True

    # 3. Modify Preventive Action
    if path == '/api/preventive-actions/modify':
        if not auth_user:
            handler.send_json_response({'success': False, 'error': 'Unauthorized: Authentication required.'}, status=401)
            return True

        if auth_user.get('roleTitle') == 'worker' or auth_user.get('department') == 'worker':
            handler.send_json_response({'success': False, 'error': 'Forbidden: Workers cannot modify preventive plans.'}, status=403)
            return True

        act_id = body.get('action_id') or body.get('actionId') or body.get('id')
        officer_name = auth_user.get('name') or auth_user.get('officialId') or 'K. Mukundha (Zonal Administrator)'
        new_action = (body.get('modified_action') or body.get('action') or body.get('newAction') or '').strip()
        new_priority = body.get('priority') or body.get('newPriority') or 'High'
        reason = (body.get('notes') or body.get('reason') or body.get('modificationReason') or 'Officer tailored action to current field resources').strip()

        if not act_id:
            handler.send_json_response({'success': False, 'error': 'actionId is required.'}, status=400)
            return True

        if not new_action:
            handler.send_json_response({'success': False, 'error': 'Updated action text is required.'}, status=400)
            return True

        conn = sqlite3.connect('civic_database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM preventive_actions WHERE id = ?", (act_id,))
        act_row = cursor.fetchone()
        if not act_row:
            conn.close()
            handler.send_json_response({'success': False, 'error': f'Preventive action {act_id} not found.'}, status=404)
            return True

        act_dict = dict(act_row)
        fst_id = act_dict.get('forecastId')

        cursor.execute("SELECT * FROM predictive_forecasts WHERE id = ?", (fst_id,))
        fst_row = cursor.fetchone()
        if fst_row:
            fst_dict = dict(fst_row)
            user_dept = auth_user.get('department')
            user_ward = auth_user.get('jurisdictionWard')
            if user_dept == 'municipal':
                if fst_dict.get('department') == 'food_safety':
                    conn.close()
                    handler.send_json_response({'success': False, 'error': 'Forbidden: Municipal Officers cannot modify Food Safety plans.'}, status=403)
                    return True
                if user_ward and user_ward != 'ALL' and user_ward.lower() not in (fst_dict.get('ward') or '').lower():
                    conn.close()
                    handler.send_json_response({'success': False, 'error': f'Forbidden: Officer is restricted to assigned ward ({user_ward}).'}, status=403)
                    return True
            elif user_dept in ['food', 'food_safety']:
                if fst_dict.get('department') != 'food_safety':
                    conn.close()
                    handler.send_json_response({'success': False, 'error': 'Forbidden: Food Safety Officers cannot modify municipal civic plans.'}, status=403)
                    return True

        now_ms = int(time.time() * 1000)
        cursor.execute('''
            UPDATE preventive_actions
            SET action = ?, priority = ?, status = 'OFFICER_MODIFIED', modificationReason = ?, approvedBy = ?, approvedAt = ?
            WHERE id = ?
        ''', (new_action, new_priority, reason, officer_name, now_ms, act_id))

        if fst_id:
            cursor.execute('''
                UPDATE predictive_forecasts
                SET preventiveRecommendation = ?, status = 'OFFICER_MODIFIED', reviewedBy = ?, reviewedAt = ?, reviewReason = ?
                WHERE id = ?
            ''', (new_action, officer_name, now_ms, reason, fst_id))

        log_operational_audit(cursor, act_id, officer_name, 'PREVENTIVE_ACTION_MODIFIED', None, f"Officer {officer_name} modified plan {act_id}. Reason: {reason} | Action: {new_action}")
        conn.commit()

        cursor.execute("SELECT * FROM preventive_actions WHERE id = ?", (act_id,))
        updated_act = dict(cursor.fetchone())
        conn.close()

        if sse_hub:
            sse_hub.broadcast('PREVENTIVE_ACTION_UPDATED', updated_act)

        updated_act['status'] = 'modified'
        updated_act['priority'] = new_priority
        updated_act['modified_action'] = new_action
        updated_act['modification_reason'] = reason
        updated_act['forecast_id'] = fst_id
        handler.send_json_response({
            'success': True,
            'action': updated_act,
            'data': updated_act,
            'forecastId': fst_id,
            'status': 'modified',
            'priority': new_priority,
            'modified_action': new_action,
            'modification_reason': reason,
            'modificationReason': reason,
            'reviewedBy': officer_name,
            'message': f'Preventive action {act_id} modified by officer.'
        })
        return True

    # 4. Assign Preventive Action to Field Squad (Reuses Phase B/C/D Workers)
    if path == '/api/preventive-actions/assign':
        if not auth_user:
            handler.send_json_response({'success': False, 'error': 'Unauthorized: Authentication required.'}, status=401)
            return True

        act_id = body.get('action_id') or body.get('actionId') or body.get('id')
        squad_name = body.get('squad') or body.get('assignedWorker') or 'Municipal Rapid Squad 4'
        officer_name = auth_user.get('name') or auth_user.get('officialId') or 'K. Mukundha (Zonal Administrator)'

        if not act_id:
            handler.send_json_response({'success': False, 'error': 'actionId is required.'}, status=400)
            return True

        conn = sqlite3.connect('civic_database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM preventive_actions WHERE id = ?", (act_id,))
        act_row = cursor.fetchone()
        if not act_row:
            conn.close()
            handler.send_json_response({'success': False, 'error': f'Preventive action {act_id} not found.'}, status=404)
            return True

        act_dict = dict(act_row)
        current_status = act_dict.get('status')
        if current_status not in ['OFFICER_APPROVED', 'OFFICER_MODIFIED', 'approved', 'modified']:
            conn.close()
            handler.send_json_response({'success': False, 'error': 'Preventive action must be approved by officer before squad assignment.'}, status=400)
            return True

        now_ms = int(time.time() * 1000)
        cursor.execute('''
            UPDATE preventive_actions
            SET status = 'ASSIGNED', assignedWorker = ?, assignedAt = ?
            WHERE id = ?
        ''', (squad_name, now_ms, act_id))

        log_operational_audit(cursor, act_id, officer_name, 'PREVENTIVE_ACTION_ASSIGNED', squad_name, f"Assigned preventive task to field squad {squad_name}")
        conn.commit()

        cursor.execute("SELECT * FROM preventive_actions WHERE id = ?", (act_id,))
        updated_act = dict(cursor.fetchone())
        conn.close()

        if sse_hub:
            sse_hub.broadcast('PREVENTIVE_ACTION_UPDATED', updated_act)

        handler.send_json_response({
            'success': True,
            'action': updated_act,
            'message': f'Preventive action {act_id} assigned to {squad_name}.'
        })
        return True

    # 5. Field Operational Intervention Completed (Transitions to IMPLEMENTED & Starts Monitoring)
    if path == '/api/preventive-actions/implement':
        if not auth_user:
            handler.send_json_response({'success': False, 'error': 'Unauthorized: Authentication required.'}, status=401)
            return True

        act_id = body.get('action_id') or body.get('actionId') or body.get('id')
        field_notes = (body.get('fieldNotes') or body.get('notes') or body.get('implementedNotes') or '').strip()
        officer_name = auth_user.get('name') or auth_user.get('officialId') or 'K. Mukundha (Zonal Administrator)'

        if not act_id:
            handler.send_json_response({'success': False, 'error': 'actionId is required.'}, status=400)
            return True

        if not field_notes:
            handler.send_json_response({'success': False, 'error': 'Field intervention notes describing operational actions are mandatory.'}, status=400)
            return True

        conn = sqlite3.connect('civic_database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM preventive_actions WHERE id = ?", (act_id,))
        act_row = cursor.fetchone()
        if not act_row:
            conn.close()
            handler.send_json_response({'success': False, 'error': f'Preventive action {act_id} not found.'}, status=404)
            return True

        act_dict = dict(act_row)
        fst_id = act_dict.get('forecastId')
        assigned_worker = act_dict.get('assignedWorker') or 'Municipal Rapid Squad 4'

        now_ms = int(time.time() * 1000)
        cursor.execute('''
            UPDATE preventive_actions
            SET status = 'IMPLEMENTED', implementedAt = ?, implementedNotes = ?, 
                monitoringStatus = 'UNDER_PREVENTIVE_MONITORING', monitoringStartedAt = ?
            WHERE id = ?
        ''', (now_ms, field_notes, now_ms, act_id))

        if fst_id:
            cursor.execute('''
                UPDATE predictive_forecasts
                SET status = 'IMPLEMENTED', reviewReason = ?
                WHERE id = ?
            ''', (f"Field intervention completed: {field_notes}", fst_id))

        log_operational_audit(cursor, act_id, officer_name, 'PREVENTIVE_ACTION_IMPLEMENTED', assigned_worker, f"Field intervention completed: {field_notes}")
        log_operational_audit(cursor, act_id, officer_name, 'PREVENTION_MONITORING_STARTED', None, "Location entered active preventive recurrence monitoring")

        # Evaluate initial recurrence trend
        eval_res = evaluate_prevention_recurrence(cursor, fst_id)

        conn.commit()

        cursor.execute("SELECT * FROM preventive_actions WHERE id = ?", (act_id,))
        updated_act = dict(cursor.fetchone())
        conn.close()

        if sse_hub:
            sse_hub.broadcast('PREVENTIVE_ACTION_UPDATED', updated_act)

        handler.send_json_response({
            'success': True,
            'action': updated_act,
            'evaluation': eval_res,
            'message': f'Preventive intervention recorded. Zone entered UNDER PREVENTIVE MONITORING.'
        })
        return True

    # 6. Evaluate Recurrence Trend Endpoint
    if path == '/api/preventive-actions/evaluate':
        fst_id = body.get('forecastId') or body.get('forecast_id')
        if not fst_id:
            handler.send_json_response({'success': False, 'error': 'forecastId is required.'}, status=400)
            return True

        conn = sqlite3.connect('civic_database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        eval_res = evaluate_prevention_recurrence(cursor, fst_id)
        conn.commit()
        conn.close()

        if not eval_res:
            handler.send_json_response({'success': False, 'error': 'Forecast not found.'}, status=404)
            return True

        handler.send_json_response({
            'success': True,
            'forecastId': fst_id,
            'evaluation': eval_res
        })
        return True

    return False
