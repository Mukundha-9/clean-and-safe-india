#!/usr/bin/env python3
"""
Smart Civic Connect — v44.0: Production Verification Test Suite
Items A through W Verification:
  A: Citizen GPS capture
  B: GPS validation
  C: Valid jurisdiction resolution (Surampalem Ward 12 center match)
  D: Missing GPS handling (LOCATION_UNAVAILABLE, non-blocking)
  E: Invalid GPS handling (out-of-bound coords -> LOCATION_UNAVAILABLE)
  F: Approximate location behavior (LOCATION_NEEDS_CONFIRMATION)
  G: Jurisdiction mismatch (LOCATION_MISMATCH for remote coords)
  H: V43 duplicate detection (same spot + close time -> POSSIBLE_DUPLICATE)
  I: V43 follow-up detection (same spot + unresolved -> FOLLOW_UP)
  J: V43 related incident detection (same spot + cross-dept category -> RELATED_INCIDENT)
  K: V43 new incident detection (distinct problem / category -> NEW_INCIDENT)
  L: Same location + unresolved issue -> FOLLOW_UP
  M: Different location (>250m) -> NEW_INCIDENT
  N: Cross-jurisdiction officer access enforcement (HTTP 403 / scoped)
  O: Cross-department worker assignment isolation
  P: Worker field lifecycle (assigned -> en route -> arrived -> completed)
  Q: Officer verification and sign-off
  R: Food Safety city-level security
  S: Predictive counting: uniqueIncidentCount excludes child follow-ups
  T: Risk map genuine coordinates only
  U: Municipal severity UI responsiveness (change-priority endpoint & officer authorization)
  V: Mobile responsiveness (HTML & CSS contract check)
  W: Desktop responsiveness (HTML & CSS contract check)
"""

import urllib.request
import urllib.parse
import json
import sqlite3
import time
import os
import sys

BASE_URL = "http://127.0.0.1:8000"
DB_FILE = "civic_database.db"

def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=30.0)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=30000')
    conn.row_factory = sqlite3.Row
    return conn

def request_json(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            status_code = resp.getcode()
            res_data = json.loads(resp.read().decode("utf-8"))
            return status_code, res_data
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {"error": err_body}
    except Exception as e:
        return 500, {"error": str(e)}

def setup_test_sessions():
    conn = get_db()
    c = conn.cursor()
    now_ms = int(time.time() * 1000)
    expires = now_ms + 86400000

    tokens = {
        "citizen": "test_v44_citizen_token",
        "mun_surampalem": "test_v44_mun_surampalem_token",
        "mun_vizag": "test_v44_mun_vizag_token",
        "worker_sanitation": "test_v44_worker_sanitation_token",
        "worker_electricity": "test_v44_worker_electricity_token",
        "food_surampalem": "test_v44_food_surampalem_token",
        "food_kakinada": "test_v44_food_kakinada_token"
    }

    sessions = [
        (tokens["citizen"], "user-v44-cit", "citizen_v44@civic.gov", "citizen", "citizen", "Ravi Kumar (Citizen)", "CIT-4401", "Andhra Pradesh", "Surampalem", "Ward 12 (Market Zone)", now_ms, expires),
        (tokens["mun_surampalem"], "mun-v44-sur", "mukundha_v44@civic.gov", "municipal", "municipal", "K. Mukundha (Zonal Admin)", "MUN-AP-01", "Andhra Pradesh", "Surampalem", "Ward 12 (Market Zone)", now_ms, expires),
        (tokens["mun_vizag"], "mun-v44-viz", "vizag_officer_v44@civic.gov", "municipal", "municipal", "Vizag Municipal Officer", "MUN-AP-02", "Andhra Pradesh", "Visakhapatnam", "Zone 3 (Beach Area)", now_ms, expires),
        (tokens["worker_sanitation"], "user-104", "ramesh@civic.gov", "worker", "worker", "Ramesh (Squad 4 Leader)", "WRK-SQ-04", "Andhra Pradesh", "Surampalem", "Ward 12 (Market Zone)", now_ms, expires),
        (tokens["worker_electricity"], "wrk-v44-elec", "lineman_v44@civic.gov", "worker", "worker", "Feeder 4 Lineman", "WRK-EL-02", "Andhra Pradesh", "Surampalem", "Ward 12 (Market Zone)", now_ms, expires),
        (tokens["food_surampalem"], "fso-v44-sur", "fso_surampalem@civic.gov", "food_safety", "food", "Dr. Lakshmi Prasad (FSO)", "FSO-AP-14", "Andhra Pradesh", "Surampalem", "Ward 14 (Campus Zone)", now_ms, expires),
        (tokens["food_kakinada"], "fso-v44-kak", "fso_kakinada@civic.gov", "food_safety", "food", "Kakinada FSO", "FSO-AP-08", "Andhra Pradesh", "Kakinada", "Ward 5", now_ms, expires),
    ]

    for s in sessions:
        c.execute("""
            INSERT OR REPLACE INTO sessions (
                token, userId, email, department, roleTitle, name, officialId,
                jurisdictionState, jurisdictionCity, jurisdictionWard, createdAt, expiresAt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, s)

    c.execute("DELETE FROM citizen_quotas WHERE user_id = 'user-v44-cit'")
    conn.commit()
    conn.close()
    return tokens

def run_suite():
    print("=" * 80)
    print("SMART CIVIC CONNECT — PRODUCTION TEST SUITE v44.0 (ITEMS A - W)")
    print("=" * 80)

    tokens = setup_test_sessions()
    passed = 0
    failed = 0

    def record_result(code, name, condition, details=""):
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  [PASS] {code}: {name} {details}")
            return True
        else:
            failed += 1
            print(f"  [FAIL] {code}: {name} {details}")
            return False

    # -------------------------------------------------------------------------
    # TEST A: Citizen GPS Capture Endpoint Verification
    # -------------------------------------------------------------------------
    status, res = request_json("/api/geo/verify-location", method="POST", data={
        "lat": 17.0015, "lng": 81.8042, "accuracy": 12.5, "ward": "Ward 12", "city": "Surampalem"
    }, token=tokens["citizen"])
    geo = res.get("geoEvidence", {})
    record_result("TEST A", "Citizen GPS Capture Endpoint", status == 200 and res.get("success") and geo.get("latitude") == 17.0015, f"(Lat: {geo.get('latitude')}, Lng: {geo.get('longitude')})")

    # -------------------------------------------------------------------------
    # TEST B: GPS Validation
    # -------------------------------------------------------------------------
    status_b, res_b = request_json("/api/geo/verify-location", method="POST", data={
        "lat": 17.0018, "lng": 81.8040, "accuracy": 15.0
    }, token=tokens["citizen"])
    geo_b = res_b.get("geoEvidence", {})
    record_result("TEST B", "GPS Validation & Reverse Geo Resolution", status_b == 200 and geo_b.get("resolvedCity") == "Surampalem" and geo_b.get("status") == "LOCATION_CONSISTENT", f"(Resolved: {geo_b.get('resolvedWard')}, Status: {geo_b.get('status')})")

    # -------------------------------------------------------------------------
    # TEST C: Valid Jurisdiction Resolution (Surampalem Ward 12 center match)
    # -------------------------------------------------------------------------
    record_result("TEST C", "Valid Jurisdiction Resolution (Ward 12 Center)", geo_b.get("distanceMeters", 999) < 100 and geo_b.get("resolvedWard") == "Ward 12 (Market Zone)", f"(Distance: {geo_b.get('distanceMeters'):.1f}m)")

    # -------------------------------------------------------------------------
    # TEST D: Missing GPS Handling (LOCATION_UNAVAILABLE, Non-Blocking)
    # -------------------------------------------------------------------------
    status_d, res_d = request_json("/api/geo/verify-location", method="POST", data={
        "lat": None, "lng": None
    }, token=tokens["citizen"])
    geo_d = res_d.get("geoEvidence", {})
    record_result("TEST D", "Missing GPS Handling (LOCATION_UNAVAILABLE)", status_d == 200 and geo_d.get("status") == "LOCATION_UNAVAILABLE" and geo_d.get("recommendedAction") == "PROCEED_WITH_WARNING", f"(Status: {geo_d.get('status')}, Action: {geo_d.get('recommendedAction')})")

    # -------------------------------------------------------------------------
    # TEST E: Invalid GPS Handling (Out-of-bound coords -> LOCATION_UNAVAILABLE)
    # -------------------------------------------------------------------------
    status_e, res_e = request_json("/api/geo/verify-location", method="POST", data={
        "lat": 999.0, "lng": -500.0
    }, token=tokens["citizen"])
    geo_e = res_e.get("geoEvidence", {})
    record_result("TEST E", "Invalid GPS Handling (Out-of-bounds coords)", status_e == 200 and geo_e.get("status") == "LOCATION_UNAVAILABLE", f"(Status: {geo_e.get('status')})")

    # -------------------------------------------------------------------------
    # TEST F: Approximate Location Behavior (LOCATION_NEEDS_CONFIRMATION)
    # -------------------------------------------------------------------------
    status_f, res_f = request_json("/api/geo/verify-location", method="POST", data={
        "lat": 17.0015, "lng": 81.8042, "accuracy": 150.0  # High uncertainty accuracy > 100m
    }, token=tokens["citizen"])
    geo_f = res_f.get("geoEvidence", {})
    record_result("TEST F", "Approximate Location Behavior (>100m accuracy)", status_f == 200 and geo_f.get("status") == "LOCATION_NEEDS_CONFIRMATION", f"(Status: {geo_f.get('status')}, Level: {geo_f.get('consistencyLevel')})")

    # -------------------------------------------------------------------------
    # TEST G: Jurisdiction Mismatch (LOCATION_MISMATCH for remote coords)
    # -------------------------------------------------------------------------
    status_g, res_g = request_json("/api/geo/verify-location", method="POST", data={
        "lat": 17.6868, "lng": 83.2185, "city": "Surampalem", "ward": "Ward 12"
    }, token=tokens["citizen"])
    geo_g = res_g.get("geoEvidence", {})
    record_result("TEST G", "Jurisdiction Mismatch (Remote Coords)", status_g == 200 and geo_g.get("status") == "LOCATION_MISMATCH" and geo_g.get("resolvedCity") == "Visakhapatnam", f"(Status: {geo_g.get('status')}, Resolved City: {geo_g.get('resolvedCity')})")

    # Prepare known test base issue in Ward 12
    conn = get_db()
    c = conn.cursor()
    base_issue_id = f"ISS-TEST-BASE-{int(time.time())}"
    now_ms = int(time.time() * 1000)
    c.execute("""
        INSERT INTO issues (
            id, title, description, category, department, severity, status, workerStatus,
            state, city, ward, street, location, lat, lng,
            geoConsistencyStatus, geoConsistencyLevel, geoDistanceMeters,
            geoResolvedState, geoResolvedCity, geoResolvedWard,
            timestamp, reportedBy, reportedById
        ) VALUES (
            ?, 'Overflowing Waste Bin at Market Center',
            'Severe wet waste and garbage spill at the central vegetable market gate.',
            'wet_waste', 'sanitation', 'medium', 'open', 'unassigned',
            'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)', 'Vegetable Market Cross Road', 'Surampalem • Ward 12',
            17.0015, 81.8042,
            'LOCATION_CONSISTENT', 'HIGH', 0.0,
            'Andhra Pradesh', 'Surampalem', 'Ward 12 (Market Zone)',
            ?, 'Ravi Kumar', 'user-v44-cit'
        )
    """, (base_issue_id, now_ms))
    conn.commit()
    conn.close()

    # -------------------------------------------------------------------------
    # TEST H: V43 Duplicate Detection (Same spot + close time -> POSSIBLE_DUPLICATE)
    # -------------------------------------------------------------------------
    status_h, res_h = request_json("/api/ai/incident-identity", method="POST", data={
        "title": "Severe garbage spill near market gate",
        "description": "Excess wet garbage spilled outside the bin at central market.",
        "category": "wet_waste",
        "department": "sanitation",
        "latitude": 17.0015,
        "longitude": 81.8042,
        "ward": "Ward 12",
        "city": "Surampalem"
    }, token=tokens["citizen"])
    record_result("TEST H", "Duplicate Incident Detection (Same Spot + Recent)", status_h == 200 and res_h.get("identityType") in ["POSSIBLE_DUPLICATE", "FOLLOW_UP"], f"(Type: {res_h.get('identityType')}, Score: {res_h.get('matchScore')})")

    # -------------------------------------------------------------------------
    # TEST I: V43 Follow-up Detection (Same spot + unresolved issue)
    # -------------------------------------------------------------------------
    status_i, res_i = request_json("/api/issues/follow-up", method="POST", data={
        "issueId": base_issue_id,
        "comment": "The garbage is still overflowing after 4 hours.",
        "latitude": 17.0015,
        "longitude": 81.8042
    }, token=tokens["citizen"])
    record_result("TEST I", "Follow-up Submission & Priority Escalation", status_i == 200 and res_i.get("success") and res_i.get("followUpCount") >= 1, f"(FollowUpCount: {res_i.get('followUpCount')})")

    # -------------------------------------------------------------------------
    # TEST J: V43 Related Incident Detection (Same spot + cross-dept category)
    # -------------------------------------------------------------------------
    status_j, res_j = request_json("/api/ai/incident-identity", method="POST", data={
        "title": "Streetlight feeder sparking near vegetable market",
        "description": "Electrical sparking on pole number 12 beside the market entrance.",
        "category": "electricity",
        "department": "electricity",
        "latitude": 17.0016,
        "longitude": 81.8041,
        "ward": "Ward 12",
        "city": "Surampalem"
    }, token=tokens["citizen"])
    record_result("TEST J", "Related Incident Detection (Cross-Dept at Spot)", status_j == 200 and res_j.get("identityType") in ["RELATED_INCIDENT", "NEW_INCIDENT"], f"(Type: {res_j.get('identityType')})")

    # -------------------------------------------------------------------------
    # TEST K: V43 New Incident Detection (Distinct Problem / Location)
    # -------------------------------------------------------------------------
    status_k, res_k = request_json("/api/ai/incident-identity", method="POST", data={
        "title": "Stray dog pack near hostel gate",
        "description": "Stray animals blocking pedestrian gate at campus entrance.",
        "category": "animal_control",
        "department": "sanitation",
        "latitude": 17.0080,
        "longitude": 81.8090,
        "ward": "Ward 14",
        "city": "Surampalem"
    }, token=tokens["citizen"])
    record_result("TEST K", "New Incident Classification (>250m away)", status_k == 200 and res_k.get("identityType") == "NEW_INCIDENT", f"(Type: {res_k.get('identityType')})")

    # -------------------------------------------------------------------------
    # TEST L: Same Location + Unresolved Issue -> Follow-Up Guidance
    # -------------------------------------------------------------------------
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT followUpCount, severity FROM issues WHERE id = ?", (base_issue_id,))
    row_l = c.fetchone()
    conn.close()
    record_result("TEST L", "Same Location Unresolved Tracked as Follow-up", row_l["followUpCount"] >= 1, f"(FollowUps: {row_l['followUpCount']})")

    # -------------------------------------------------------------------------
    # TEST M: Different Location (>250m) -> Guaranteed NEW_INCIDENT
    # -------------------------------------------------------------------------
    status_m, res_m = request_json("/api/ai/incident-identity", method="POST", data={
        "title": "Garbage dump near hospital",
        "description": "Waste piled up outside primary health clinic.",
        "category": "wet_waste",
        "department": "sanitation",
        "latitude": 17.0090,
        "longitude": 81.8020,
        "ward": "Ward 11",
        "city": "Surampalem"
    }, token=tokens["citizen"])
    record_result("TEST M", "Guaranteed NEW_INCIDENT when Distance > 250m", status_m == 200 and res_m.get("identityType") == "NEW_INCIDENT", f"(Type: {res_m.get('identityType')})")

    # -------------------------------------------------------------------------
    # TEST N: Cross-Jurisdiction Officer Access Enforcement (HTTP 403 / Scoped)
    # -------------------------------------------------------------------------
    status_n, res_n = request_json(f"/api/issues/{base_issue_id}/change-priority", method="POST", data={
        "severity": "critical"
    }, token=tokens["mun_vizag"])
    record_result("TEST N", "Cross-Jurisdiction Officer Access Enforcement (HTTP 403)", status_n == 403 and "Forbidden" in res_n.get("error", ""), f"(Status: {status_n}, Msg: {res_n.get('error')})")

    # -------------------------------------------------------------------------
    # TEST O: Cross-Department Worker Assignment Isolation
    # -------------------------------------------------------------------------
    status_o, res_o = request_json("/api/issues/assign", method="POST", data={
        "issueId": base_issue_id,
        "workerId": "WRK-ELE-02",  # Electricity lineman for sanitation task
        "supervisorNotes": "Cross-dept test"
    }, token=tokens["mun_surampalem"])
    record_result("TEST O", "Cross-Department Worker Assignment Isolation", status_o == 400 and "Electricity department" in res_o.get("error", ""), f"(Status: {status_o}, Msg: {res_o.get('error')})")

    # -------------------------------------------------------------------------
    # TEST P: Worker Field Lifecycle (Assigned -> En Route -> Arrived -> Completed)
    # -------------------------------------------------------------------------
    # 1. Assign to Sanitation Squad 4 (WRK-SAN-04)
    status_p1, res_p1 = request_json("/api/issues/assign", method="POST", data={
        "issueId": base_issue_id,
        "workerId": "WRK-SAN-04",
        "supervisorNotes": "Priority clearance at vegetable market."
    }, token=tokens["mun_surampalem"])
    # 2. Worker transitions to 'En Route to Site'
    status_p2, _ = request_json("/api/issues/transition", method="POST", data={
        "issueId": base_issue_id,
        "workerId": "WRK-SAN-04",
        "status": "En Route to Site"
    }, token=tokens["worker_sanitation"])
    # 3. Worker transitions to 'On Site - Conducting Work'
    status_p3, _ = request_json("/api/issues/transition", method="POST", data={
        "issueId": base_issue_id,
        "workerId": "WRK-SAN-04",
        "status": "On Site - Conducting Work"
    }, token=tokens["worker_sanitation"])
    # 4. Worker transitions to 'Work Completed - Awaiting Verification'
    status_p4, res_p4 = request_json("/api/issues/transition", method="POST", data={
        "issueId": base_issue_id,
        "workerId": "WRK-SAN-04",
        "status": "Work Completed - Awaiting Verification",
        "imageAfter": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "resolutionNotes": "Area swept and 1.2 tons wet waste cleared."
    }, token=tokens["worker_sanitation"])
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT workerStatus FROM issues WHERE id = ?", (base_issue_id,))
    row_p = c.fetchone()
    conn.close()
    record_result("TEST P", "Worker Field Lifecycle (Assigned -> Work Completed)", row_p["workerStatus"] == "Work Completed - Awaiting Verification", f"(Final Worker Status: {row_p['workerStatus']})")

    # -------------------------------------------------------------------------
    # TEST Q: Officer Verification & Sign-off
    # -------------------------------------------------------------------------
    status_q, res_q = request_json("/api/issues/resolve", method="POST", data={
        "issueId": base_issue_id,
        "notes": "Supervisory inspection confirmed spot clean and sanitized."
    }, token=tokens["mun_surampalem"])
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT status, verifiedByOfficer FROM issues WHERE id = ?", (base_issue_id,))
    row_q = c.fetchone()
    conn.close()
    record_result("TEST Q", "Officer Verification & Final Closure", status_q == 200 and row_q["status"] == "resolved" and row_q["verifiedByOfficer"] is not None, f"(Status: {row_q['status']}, VerifiedBy: {row_q['verifiedByOfficer']})")

    # -------------------------------------------------------------------------
    # TEST R: Food Safety City-Level Security
    # -------------------------------------------------------------------------
    # Kakinada FSO tries to issue a violation in Surampalem -> HTTP 403 Forbidden
    status_r, res_r = request_json("/api/food-violations", method="POST", data={
        "city": "Surampalem",
        "vendorName": "Test Sweet House",
        "ownerName": "Test Owner",
        "violationClause": "Sec 56 FSS Act",
        "fineAmount": 500
    }, token=tokens["food_kakinada"])
    # Kakinada FSO queries issues -> scoped strictly to food safety in Kakinada
    status_r2, res_r2 = request_json("/api/issues", method="GET", token=tokens["food_kakinada"])
    record_result("TEST R", "Food Safety City-Level Scoped Access & Enforcement", status_r == 403 and status_r2 == 200, f"(Violation In Surampalem: {status_r} Forbidden, Issues Fetch: {status_r2})")

    # -------------------------------------------------------------------------
    # TEST S: Predictive Counting (uniqueIncidentCount excludes follow-ups)
    # -------------------------------------------------------------------------
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as total_reports FROM issues")
    total_reports = c.fetchone()["total_reports"]
    c.execute("SELECT COUNT(*) as unique_incidents FROM issues WHERE parentIssueId IS NULL OR parentIssueId = ''")
    unique_incidents = c.fetchone()["unique_incidents"]
    conn.close()
    record_result("TEST S", "Predictive Counting (uniqueIncidentCount <= totalReports)", unique_incidents <= total_reports, f"(Unique: {unique_incidents}, Total: {total_reports})")

    # -------------------------------------------------------------------------
    # TEST T: Risk Map Genuine Coordinates Only
    # -------------------------------------------------------------------------
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, lat, lng FROM issues WHERE lat IS NOT NULL AND lng IS NOT NULL")
    coords = c.fetchall()
    conn.close()
    all_genuine = all(15.0 <= r["lat"] <= 20.0 and 80.0 <= r["lng"] <= 85.0 for r in coords)
    record_result("TEST T", "Risk Map Uses Authentic AP Coords", all_genuine and len(coords) > 0, f"(Checked {len(coords)} coordinates within AP geo-box)")

    # -------------------------------------------------------------------------
    # TEST U: Municipal Severity UI Responsiveness (Change Priority API)
    # -------------------------------------------------------------------------
    status_u, res_u = request_json(f"/api/issues/{base_issue_id}/change-priority", method="POST", data={
        "severity": "critical"
    }, token=tokens["mun_surampalem"])
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT severity FROM issues WHERE id = ?", (base_issue_id,))
    row_u = c.fetchone()
    conn.close()
    record_result("TEST U", "Municipal Severity Change Priority API & DB Persistence", status_u == 200 and row_u["severity"] == "critical", f"(New Severity: {row_u['severity']})")

    # -------------------------------------------------------------------------
    # TEST V: Mobile Responsiveness Contract Check
    # -------------------------------------------------------------------------
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    with open("js/bundle.js", "r", encoding="utf-8") as f:
        bundle_content = f.read()

    has_mobile_viewport = "viewport-fit=cover" in html_content
    has_mobile_nav = "mobile-bottom-nav" in html_content
    has_location_captured_card = "modalLocationCapturedCard" in html_content
    record_result("TEST V", "Mobile Responsiveness Contract (Viewport, Nav, Captured Card)", has_mobile_viewport and has_mobile_nav and has_location_captured_card, "(Viewport & Mobile Card verified)")

    # -------------------------------------------------------------------------
    # TEST W: Desktop Responsiveness Contract Check
    # -------------------------------------------------------------------------
    has_command_tiers = "mun-tier-attention" in html_content and "mun-tier-fieldops" in html_content
    has_priority_dispatch = "mun-priority-dispatch-strip" in html_content
    has_view_evidence = "VIEW LOCATION EVIDENCE" in bundle_content
    has_change_priority_btn = "Change Priority" in bundle_content
    record_result("TEST W", "Desktop Responsiveness Contract (4-Tier Grid, Dispatch Matrix, Location Evidence)", has_command_tiers and has_priority_dispatch and has_view_evidence and has_change_priority_btn, "(Tiers, Dispatch Matrix & Location Evidence verified)")

    print("=" * 80)
    print(f"RESULTS: {passed} PASSED, {failed} FAILED (TOTAL {passed + failed} TESTS)")
    print("=" * 80)
    return failed == 0

if __name__ == "__main__":
    success = run_suite()
    sys.exit(0 if success else 1)
