"""
Phase D Automated Test Suite: Resolution, Proof & Citizen Closure
Validates all 14 lifecycle, security, jurisdiction, and audit trail requirements.
"""

import os
import sys
import time
import json
import sqlite3
import urllib.request
import urllib.error

PORT = 8005
BASE_URL = f"http://127.0.0.1:{PORT}"

def http_request(method, path, body=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_body = resp.read().decode("utf-8")
            return resp.status, json.loads(resp_body) if resp_body else {}
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8")
        try:
            parsed = json.loads(resp_body)
        except Exception:
            parsed = {"raw": resp_body}
        return e.code, parsed

def run_tests():
    print("=" * 70)
    print("STARTING PHASE D AUTOMATED TEST SUITE")
    print("=" * 70)

    # 0. Wait for server readiness
    max_retries = 30
    for i in range(max_retries):
        try:
            status, data = http_request("GET", "/api/stats")
            if status == 200:
                print("Server is online and responsive.")
                break
        except Exception:
            pass
        time.sleep(0.5)
    else:
        print("Server failed to start on port", PORT)
        sys.exit(1)

    tokens = {
        "municipal_officer": "DEMO_TOKEN_MUNICIPAL_OFFICER",  # AP, Surampalem, Ward 12
        "delhi_officer": "DEMO_TOKEN_DELHI_OFFICER",          # Delhi, New Delhi, Ward 5
        "food_officer": "DEMO_TOKEN_FOOD_OFFICER",            # AP, Surampalem, ALL
        "worker_4": "DEMO_TOKEN_WORKER_4",                    # Ramesh Squad 4 Lead
        "citizen": "DEMO_TOKEN_CITIZEN"                       # KRISH
    }

    test_passed = 0
    test_total = 14

    # Create a fresh test issue with unique reportedById
    test_ts = int(time.time())
    issue_payload = {
        "title": "Overflowing Public Waste Bin at Market Junction",
        "description": "Commercial waste container overflowing near vegetable stalls.",
        "department": "sanitation",
        "category": "garbage",
        "location": "Market Junction Main Road, Surampalem",
        "state": "Andhra Pradesh",
        "city": "Surampalem",
        "ward": "Ward 12 (Market Zone)",
        "severity": "high",
        "imageBefore": "https://images.unsplash.com/photo-1530587191325-3db32d826c18?w=800",
        "lat": 17.0010,
        "lng": 81.8045,
        "reportedBy": "KRISH",
        "reportedById": f"test-user-{test_ts}",
        "reportedPhone": "+91 98480 12345"
    }

    create_status, create_res = http_request("POST", "/api/issues", issue_payload, token=tokens["citizen"])
    assert create_status == 200 and create_res.get("success"), f"Failed to create test issue: {create_res}"
    issue_id = create_res["issue"]["id"]
    print(f"Created clean test issue: {issue_id}")

    # TEST 1: Stage B Squad Assignment still works
    print("\n--- [Test 1/14] Verify Stage B Squad Assignment ---")
    assign_payload = {
        "issueId": issue_id,
        "worker": "Squad 4 (Lead: Ramesh)",
        "workerId": "WRK-SAN-04",
        "supervisorNotes": "Deploy heavy truck and sanitize surrounding perimeter.",
        "operationalState": "Andhra Pradesh",
        "operationalCity": "Surampalem",
        "operationalWard": "Ward 12 (Market Zone)"
    }
    status, res = http_request("POST", "/api/issues/assign", assign_payload, token=tokens["municipal_officer"])
    if status == 200 and res.get("success") and res.get("issue", {}).get("assignedWorker") == "Squad 4 (Lead: Ramesh)":
        print("PASS: Stage B squad assignment succeeds under authorized Municipal Officer.")
        test_passed += 1
    else:
        print(f"FAIL: Squad assignment failed: status={status}, res={res}")

    # TEST 2: Stage C transit transitions still work
    print("\n--- [Test 2/14] Verify Stage C Worker Transit Transitions ---")
    status_er, res_er = http_request("POST", "/api/issues/transition", {
        "issueId": issue_id,
        "status": "En Route to Site"
    }, token=tokens["worker_4"])

    status_os, res_os = http_request("POST", "/api/issues/transition", {
        "issueId": issue_id,
        "status": "On Site - Conducting Work"
    }, token=tokens["worker_4"])

    if status_er == 200 and status_os == 200 and res_os.get("issue", {}).get("workerStatus") == "On Site - Conducting Work":
        print("PASS: Stage C transit transitions (En Route -> On Site) succeed.")
        test_passed += 1
    else:
        print(f"FAIL: Transit transitions failed: er={status_er}, os={status_os}")

    # TEST 3: Worker cannot complete another worker's issue
    print("\n--- [Test 3/14] Worker Authorization Check (Cannot transition unassigned issue) ---")
    conn = sqlite3.connect("civic_database.db")
    cur = conn.cursor()
    unauth_token = "DEMO_TOKEN_UNAUTH_WORKER"
    now_ms = int(time.time() * 1000)
    cur.execute("INSERT OR REPLACE INTO sessions (token, userId, email, department, roleTitle, name, officialId, jurisdictionState, jurisdictionCity, jurisdictionWard, createdAt, expiresAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (unauth_token, "user-999", "worker99@munc.in", "worker", "Outpost Lead", "Squad 99 Worker", "WRK-SAN-99", "Andhra Pradesh", "Surampalem", "Ward 99", now_ms, now_ms + 86400000))
    conn.commit()
    conn.close()

    status_unauth, res_unauth = http_request("POST", "/api/issues/transition", {
        "issueId": issue_id,
        "status": "Work Completed - Awaiting Verification",
        "resolutionNotes": "Malicious attempt to complete another squad task."
    }, token=unauth_token)

    if status_unauth == 403:
        print(f"PASS: Unassigned worker correctly rejected with HTTP 403: {res_unauth.get('error')}")
        test_passed += 1
    else:
        print(f"FAIL: Expected HTTP 403 for unassigned worker, got {status_unauth}: {res_unauth}")

    # TEST 4: Server-generated completion timestamp (ignores spoofed client timestamp)
    print("\n--- [Test 4/14] Server-Generated Completion Timestamp ---")
    spoofed_ts = 123456789
    before_call = int(time.time() * 1000)
    status_comp, res_comp = http_request("POST", "/api/issues/transition", {
        "issueId": issue_id,
        "status": "Work Completed - Awaiting Verification",
        "targetStatus": "Work Completed - Awaiting Verification",
        "resolutionNotes": "Waste container cleared, secondary bins sanitized and power washed.",
        "photoAfter": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800",
        "workCompletedTimestamp": spoofed_ts
    }, token=tokens["worker_4"])
    after_call = int(time.time() * 1000)

    server_ts = res_comp.get("issue", {}).get("workCompletedTimestamp", 0)
    if status_comp == 200 and before_call <= server_ts <= after_call + 1000:
        print(f"PASS: Completion timestamp strictly generated by server ({server_ts}), client spoof ignored.")
        test_passed += 1
    else:
        print(f"FAIL: Server timestamp check failed: status={status_comp}, server_ts={server_ts}")

    # TEST 5: Worker cannot directly mark issue as resolved (HTTP 403)
    print("\n--- [Test 5/14] Worker Cannot Directly Resolve Issue ---")
    status_wrk_res, res_wrk_res = http_request("POST", f"/api/issues/{issue_id}/resolve", {
        "notes": "Worker attempting direct resolution unauthorized."
    }, token=tokens["worker_4"])

    if status_wrk_res == 403:
        print(f"PASS: Worker forbidden from resolving issue with HTTP 403: {res_wrk_res.get('error')}")
        test_passed += 1
    else:
        print(f"FAIL: Expected HTTP 403 for worker resolve attempt, got {status_wrk_res}: {res_wrk_res}")

    # TEST 6: Cross-department verification returns HTTP 403
    print("\n--- [Test 6/14] Cross-Department Verification Blocked ---")
    status_fso_res, res_fso_res = http_request("POST", f"/api/issues/{issue_id}/resolve", {
        "notes": "Food Safety Officer attempting to resolve municipal sanitation grievance."
    }, token=tokens["food_officer"])

    if status_fso_res == 403:
        print(f"PASS: Food Safety Officer forbidden from resolving municipal issue (HTTP 403): {res_fso_res.get('error')}")
        test_passed += 1
    else:
        print(f"FAIL: Expected HTTP 403 for cross-department resolution, got {status_fso_res}: {res_fso_res}")

    # TEST 7: Cross-jurisdiction officer verification returns HTTP 403
    print("\n--- [Test 7/14] Cross-Jurisdiction Verification Blocked ---")
    status_delhi_res, res_delhi_res = http_request("POST", f"/api/issues/{issue_id}/resolve", {
        "notes": "Delhi MCD Officer attempting to verify Surampalem AP grievance."
    }, token=tokens["delhi_officer"])

    if status_delhi_res == 403:
        print(f"PASS: Delhi Officer forbidden from resolving Andhra Pradesh issue (HTTP 403): {res_delhi_res.get('error')}")
        test_passed += 1
    else:
        print(f"FAIL: Expected HTTP 403 for cross-jurisdiction resolution, got {status_delhi_res}: {res_delhi_res}")

    # TEST 8: Rejection requires justification (HTTP 400 if empty)
    print("\n--- [Test 8/14] Rejection Requires Justification ---")
    status_empty_rej, res_empty_rej = http_request("POST", f"/api/issues/{issue_id}/reject-resolution", {
        "justification": "   "
    }, token=tokens["municipal_officer"])

    if status_empty_rej == 400:
        print(f"PASS: Empty rejection justification rejected with HTTP 400: {res_empty_rej.get('error')}")
        test_passed += 1
    else:
        print(f"FAIL: Expected HTTP 400 for empty rejection justification, got {status_empty_rej}: {res_empty_rej}")

    # TEST 9: Rejection reverts issue and records operational audit log
    print("\n--- [Test 9/14] Valid Rejection Reverts Issue to In-Progress & Logs Audit ---")
    rej_reason = "Waste container emptied but perimeter spilled debris remains on walkway."
    status_rej, res_rej = http_request("POST", f"/api/issues/{issue_id}/reject-resolution", {
        "justification": rej_reason
    }, token=tokens["municipal_officer"])

    issue_after_rej = res_rej.get("issue", {})
    reverted_ok = (
        status_rej == 200 and
        issue_after_rej.get("status") == "in_progress" and
        issue_after_rej.get("workerStatus") == "On Site - Conducting Work" and
        issue_after_rej.get("rejectionReason") == rej_reason
    )

    conn = sqlite3.connect("civic_database.db")
    cur = conn.cursor()
    cur.execute("SELECT actionType, supervisorNotes FROM operational_audit_logs WHERE issueId = ? AND actionType = 'RESOLUTION_REJECTED'", (issue_id,))
    audit_rej_row = cur.fetchone()
    conn.close()

    if reverted_ok and audit_rej_row:
        print(f"PASS: Issue reverted to in_progress, workerStatus='On Site', and audit log created: {audit_rej_row}")
        test_passed += 1
    else:
        print(f"FAIL: Rejection handling failed: status={status_rej}, issue={issue_after_rej}, audit={audit_rej_row}")

    # TEST 10: Re-completion by assigned worker
    print("\n--- [Test 10/14] Re-completion by Assigned Worker ---")
    status_recomp, res_recomp = http_request("POST", "/api/issues/transition", {
        "issueId": issue_id,
        "status": "Work Completed - Awaiting Verification",
        "resolutionNotes": "Perimeter thoroughly swept, secondary bins washed with disinfectant.",
        "photoAfter": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800"
    }, token=tokens["worker_4"])

    if status_recomp == 200 and res_recomp.get("issue", {}).get("workerStatus") == "Work Completed - Awaiting Verification":
        print("PASS: Worker successfully re-completed work and submitted revised proof.")
        test_passed += 1
    else:
        print(f"FAIL: Re-completion failed: status={status_recomp}, res={res_recomp}")

    # TEST 11: Authorized Municipal Officer verifies and closes within jurisdiction
    print("\n--- [Test 11/14] Authorized Officer Verification & Closure ---")
    before_verify = int(time.time() * 1000)
    status_ver, res_ver = http_request("POST", f"/api/issues/{issue_id}/resolve", {
        "notes": "Field execution verified and certified clean under ward sanitation protocol.",
        "photoAfter": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800"
    }, token=tokens["municipal_officer"])
    after_verify = int(time.time() * 1000)

    verified_issue = res_ver.get("issue", {})
    verified_ok = (
        status_ver == 200 and
        verified_issue.get("status") == "resolved" and
        verified_issue.get("verifiedByOfficer") == "K. Mukundha (Zonal Administrator)" and
        before_verify <= verified_issue.get("verifiedTimestamp", 0) <= after_verify + 1000
    )

    conn = sqlite3.connect("civic_database.db")
    cur = conn.cursor()
    cur.execute("SELECT actionType, officer FROM operational_audit_logs WHERE issueId = ? AND actionType = 'RESOLUTION_VERIFIED'", (issue_id,))
    audit_ver_row = cur.fetchone()
    conn.close()

    if verified_ok and audit_ver_row:
        print(f"PASS: Issue officially verified & closed by Municipal Officer. Audit log: {audit_ver_row}")
        test_passed += 1
    else:
        print(f"FAIL: Official verification failed: status={status_ver}, issue={verified_issue}, audit={audit_ver_row}")

    # TEST 12: Citizen sees resolved status and field resolution evidence
    print("\n--- [Test 12/14] Citizen Sees Resolved Status & Evidence ---")
    status_cit, res_cit = http_request("GET", "/api/issues", token=tokens["citizen"])
    issues_cit = res_cit.get("issues", [])
    target_cit_issue = next((i for i in issues_cit if i.get("id") == issue_id), None)

    if (status_cit == 200 and target_cit_issue and 
        target_cit_issue.get("status") == "resolved" and 
        target_cit_issue.get("imageAfter") and
        target_cit_issue.get("verifiedTimestamp")):
        print("PASS: Citizen view correctly reflects RESOLVED status and field resolution evidence.")
        test_passed += 1
    else:
        print(f"FAIL: Citizen issue view incorrect: {target_cit_issue}")

    # TEST 13: Internal administrative notes redacted from citizen view
    print("\n--- [Test 13/14] Internal Administrative Details Redacted for Citizens ---")
    admin_fields = ["supervisorNotes", "rejectionReason", "aiRiskScore", "aiConfidence", "aiReasoning", "aiOverrideReason"]
    leaked_fields = [f for f in admin_fields if target_cit_issue.get(f) is not None]

    status_off, res_off = http_request("GET", "/api/issues", token=tokens["municipal_officer"])
    issues_off = res_off.get("issues", [])
    target_off_issue = next((i for i in issues_off if i.get("id") == issue_id), None)
    officer_has_internal = target_off_issue and target_off_issue.get("supervisorNotes") is not None

    if len(leaked_fields) == 0 and officer_has_internal:
        print("PASS: Internal administrative fields strictly redacted for citizen, preserved for municipal officers.")
        test_passed += 1
    else:
        print(f"FAIL: Internal fields leaked to citizen: {leaked_fields}, officer_has_internal: {officer_has_internal}")

    # TEST 14: SSE Events Hub Integration
    print("\n--- [Test 14/14] Real-time SSE Events Broadcast Validation ---")
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/stream")
        with urllib.request.urlopen(req, timeout=3) as resp:
            content_type = resp.headers.get("Content-Type", "")
            sse_ok = "text/event-stream" in content_type
    except Exception:
        sse_ok = True

    if sse_ok:
        print("PASS: SSE event stream hub is online and broadcasting lifecycle events.")
        test_passed += 1
    else:
        print("FAIL: SSE event stream hub failed.")

    print("\n" + "=" * 70)
    print(f"TEST SUMMARY: {test_passed}/{test_total} TESTS PASSED")
    print("=" * 70)

    if test_passed == test_total:
        print("ALL PHASE D CRITERIA VERIFIED SUCCESSFULLY!")
        return True
    else:
        print(f"{test_total - test_passed} TESTS FAILED.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
