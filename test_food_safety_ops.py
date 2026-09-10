import unittest
import json
import threading
import time
import urllib.request
import urllib.error
import http.server
import server
import sqlite3

PORT = 8092

class FoodSafetyOpsE2ETest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.PORT = PORT
        cls.httpd = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), server.CivicAppRequestHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.5)

        conn = server.get_db_connection()
        cls.fso_token = server.create_session({
            'id': 'user-103', 'name': 'Dr. Lakshmi Prasad (FSO)', 'email': 'foodsafety@surampalem.gov.in',
            'department': 'food_safety', 'roleTitle': 'Food Safety Officer', 'officialId': 'FSO-AP-2026-003',
            'jurisdictionState': 'Andhra Pradesh', 'jurisdictionCity': 'Surampalem', 'jurisdictionWard': 'Ward 12'
        }, conn)
        cls.citizen_token = server.create_session({
            'id': 'user-101', 'name': 'Krish Varma', 'email': 'citizen@surampalem.gov.in',
            'department': 'citizen', 'roleTitle': 'Resident', 'officialId': 'CIT-2026-001',
            'jurisdictionState': 'Andhra Pradesh', 'jurisdictionCity': 'Surampalem', 'jurisdictionWard': 'Ward 12'
        }, conn)
        cls.worker_token = server.create_session({
            'id': 'user-104', 'name': 'Ramesh Kumar', 'email': 'worker@surampalem.gov.in',
            'department': 'sanitation', 'roleTitle': 'Field Squad Lead', 'officialId': 'WRK-2026-004',
            'jurisdictionState': 'Andhra Pradesh', 'jurisdictionCity': 'Surampalem', 'jurisdictionWard': 'Ward 12'
        }, conn)
        cls.out_of_jur_token = server.create_session({
            'id': 'user-999', 'name': 'Other FSO', 'email': 'fso@bengaluru.gov.in',
            'department': 'food_safety', 'roleTitle': 'Food Safety Officer', 'officialId': 'FSO-KA-2026-999',
            'jurisdictionState': 'Karnataka', 'jurisdictionCity': 'Bengaluru', 'jurisdictionWard': 'Ward 1'
        }, conn)
        conn.close()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def make_req(self, path, method='GET', data=None, token=None):
        url = f'http://127.0.0.1:{PORT}{path}'
        headers = {'Connection': 'close'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        body = None
        if data is not None:
            headers['Content-Type'] = 'application/json'
            body = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                resp_body = resp.read().decode('utf-8')
                return resp.status, json.loads(resp_body) if resp_body else {}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8')
            try:
                parsed = json.loads(err_body)
            except:
                parsed = {'error': err_body}
            return e.code, parsed

    # 1. SECURITY & RBAC TESTS
    def test_01_fso_overview_unauthorized(self):
        status, res = self.make_req('/api/food/overview')
        self.assertEqual(status, 401)

    def test_02_fso_overview_citizen_forbidden(self):
        status, res = self.make_req('/api/food/overview', token=self.citizen_token)
        self.assertEqual(status, 403)

    def test_03_fso_overview_worker_forbidden(self):
        status, res = self.make_req('/api/food/overview', token=self.worker_token)
        self.assertEqual(status, 403)

    def test_04_fso_overview_out_of_jurisdiction_blocked(self):
        status, res = self.make_req('/api/food/overview', token=self.out_of_jur_token)
        self.assertEqual(status, 403)

    def test_05_fso_overview_authorized(self):
        status, res = self.make_req('/api/food/overview', token=self.fso_token)
        self.assertEqual(status, 200)
        self.assertIn('metrics', res)
        metrics = res['metrics']
        self.assertIn('urgentReviewsCount', metrics)
        self.assertIn('activeInspectionsCount', metrics)
        self.assertIn('pendingCorrectiveActionsCount', metrics)
        self.assertIn('reinspectionsDueCount', metrics)
        self.assertIn('highRiskEstablishmentsCount', metrics)
        self.assertIn('hotspotsCount', metrics)

    # 2. INSPECTIONS LIST & DETAILS
    def test_06_get_inspections(self):
        status, res = self.make_req('/api/food/inspections', token=self.fso_token)
        self.assertEqual(status, 200)
        self.assertIn('inspections', res)
        self.assertGreaterEqual(len(res['inspections']), 5)
        insp = res['inspections'][0]
        self.assertIn('inspectionId', insp)
        self.assertIn('vendorName', insp)

    # 3. VENDORS / ESTABLISHMENT COMPLIANCE REGISTRY
    def test_07_get_vendors(self):
        status, res = self.make_req('/api/food/vendors', token=self.fso_token)
        self.assertEqual(status, 200)
        self.assertIn('vendors', res)
        self.assertGreaterEqual(len(res['vendors']), 5)
        v = res['vendors'][0]
        self.assertIn('establishmentType', v)
        self.assertIn('monitoringStatus', v)

    # 4. HOTSPOTS & PREDICTIVE FORECASTING (HONEST ADVISORY)
    def test_08_get_hotspots(self):
        status, res = self.make_req('/api/food/hotspots', token=self.fso_token)
        self.assertEqual(status, 200)
        self.assertIn('hotspots', res)
        self.assertGreaterEqual(len(res['hotspots']), 3)

    def test_09_get_predictive_monitoring(self):
        status, res = self.make_req('/api/food/monitoring', token=self.fso_token)
        self.assertEqual(status, 200)
        self.assertIn('disclaimer', res)
        self.assertIn('Transparent Rule-Based Forecast', res['disclaimer'])
        self.assertIn('monitoring', res)
        self.assertGreaterEqual(len(res['monitoring']), 2)

    # 5. ON-SITE 6-SECTION INSPECTION SUBMISSION
    def test_10_post_inspection(self):
        payload = {
            'inspectionId': 'INSP-TEST-001',
            'issueId': 'ISS-2026-FS-001',
            'vendorId': 'FSSAI-AP-2026-V11',
            'vendorName': 'Sri Sai Street Food Stall',
            'officerId': 'user-103',
            'officerName': 'Dr. Lakshmi Prasad (FSO)',
            'jurisdictionState': 'Andhra Pradesh',
            'jurisdictionCity': 'Surampalem',
            'ward': 'Ward 12 (Market Zone)',
            'scheduledAt': int(time.time() * 1000),
            'startedAt': int(time.time() * 1000) - 1800000,
            'completedAt': int(time.time() * 1000),
            'inspectionStatus': 'completed',
            'inspectionResult': 'compliant_with_corrective_action',
            'inspectionNotes': 'Test audit: acrylic sneeze guard mandated; verified food grade tongs.',
            'checklistData': {
                'food_handling': {'safe_handling_observed': True, 'protected_from_exposure': False, 'utensils_used': True},
                'food_storage': {'appropriate_storage': True, 'temp_controlled': True, 'separation': True},
                'personal_hygiene': {'hand_hygiene': True, 'protective_clothing': False, 'medical_clearance': True},
                'premises_hygiene': {'clean_surfaces': True, 'waste_containment': True, 'pest_control': True},
                'water_cleaning': {'potable_water': True, 'grease_trap': True},
                'labelling_display': {'display_board': True, 'medical_certs': True}
            },
            'evidence': ['https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80'],
            'correctiveActionRequired': 1,
            'nextInspectionAt': int(time.time() * 1000) + 48 * 3600000
        }
        status, res = self.make_req('/api/food/inspect', method='POST', data=payload, token=self.fso_token)
        self.assertEqual(status, 200)
        self.assertTrue(res.get('success'))

    # 6. FORMAL CORRECTIVE ACTION ORDER & VERIFICATION
    def test_11_post_corrective_action_and_verify(self):
        ca_payload = {
            'actionId': 'CA-TEST-001',
            'inspectionId': 'INSP-TEST-001',
            'issueId': 'ISS-2026-FS-001',
            'vendorId': 'FSSAI-AP-2026-V11',
            'vendorName': 'Sri Sai Street Food Stall',
            'description': 'Install acrylic transparent sneeze shield over prep counter.',
            'status': 'pending',
            'assignedAt': int(time.time() * 1000),
            'deadline': '48 Hours SLA'
        }
        status, res = self.make_req('/api/food/corrective-action', method='POST', data=ca_payload, token=self.fso_token)
        self.assertEqual(status, 200)
        self.assertTrue(res.get('success'))

        verify_payload = {
            'actionId': 'CA-TEST-001',
            'notes': 'Physical inspection confirmed shield installed.'
        }
        v_status, v_res = self.make_req('/api/food/corrective-action/verify', method='POST', data=verify_payload, token=self.fso_token)
        self.assertEqual(v_status, 200)
        self.assertTrue(v_res.get('success'))

    # 7. RE-INSPECTION VERIFICATION
    def test_12_post_reinspection(self):
        reinsp_payload = {
            'inspectionId': 'INSP-TEST-001',
            'notes': 'Re-inspection confirmed compliant hygiene.',
            'score': 95,
            'complianceStatus': 'COMPLIANCE_CONFIRMED'
        }
        status, res = self.make_req('/api/food/reinspection', method='POST', data=reinsp_payload, token=self.fso_token)
        self.assertEqual(status, 200)
        self.assertTrue(res.get('success'))

    # 8. FSO REVIEW DECISION
    def test_13_post_review_decision(self):
        dec_payload = {
            'issueId': 'ISS-2026-FS-001',
            'decision': 'confirmed_violation',
            'notes': 'On-site audit confirmed violation; corrective order issued.'
        }
        status, res = self.make_req('/api/food/review-decision', method='POST', data=dec_payload, token=self.fso_token)
        self.assertEqual(status, 200)
        self.assertTrue(res.get('success'))

    # 9. CITIZEN RESOLUTION FEEDBACK
    def test_14_citizen_resolution_feedback(self):
        fb_payload = {
            'isSatisfied': True,
            'feedbackNotes': 'Street food counter now has proper sneeze guard. Satisfied.'
        }
        status, res = self.make_req('/api/issues/ISS-2026-FS-004/citizen-verify', method='POST', data=fb_payload, token=self.citizen_token)
        self.assertEqual(status, 200)
        self.assertTrue(res.get('success'))

    # 10. REGRESSION CHECK: FOOD SAFETY INCIDENTS IN DB
    def test_15_citizen_reports_regression(self):
        conn = server.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM issues WHERE department = 'food_safety'")
        food_count = cursor.fetchone()[0]
        self.assertGreaterEqual(food_count, 5, "Food safety must have at least 5 realistic seeded issues")
        conn.close()

if __name__ == '__main__':
    unittest.main()
