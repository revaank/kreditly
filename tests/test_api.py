"""API contract tests; install requirements-api.txt and pytest to run them."""
import unittest

try:
    from fastapi.testclient import TestClient
    from api.main import app
except ImportError:
    TestClient = None
    app = None


@unittest.skipIf(TestClient is None, "Install requirements-api.txt to run API tests")
class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_context = TestClient(app)
        cls.client = cls.client_context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client_context.__exit__(None, None, None)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_emi_table_uses_shared_finance_formula(self):
        response = self.client.get("/emi-table", params={"amount": 300_000, "rate": 11})
        self.assertEqual(response.status_code, 200)
        terms = response.json()["terms"]
        term_36 = next(row for row in terms if row["months"] == 36)
        self.assertEqual(round(term_36["emi"]), 9_822)
        self.assertEqual(len(terms), 5)

    def test_profile_rejects_values_outside_indian_input_ranges(self):
        response = self.client.post("/predict", json={"age": 18, "annual_income": 500_000, "loan_amount": 200_000})
        self.assertEqual(response.status_code, 422)
        self.assertTrue(response.json()["error"])

    def test_lenders_uses_existing_matcher_and_status_vocabulary(self):
        profile = {
            "age": 30, "employment": "Salaried", "job_years": 5,
            "annual_income": 800_000, "existing_emi": 4_844, "card_bill": 12_000,
            "revol_util": 30, "open_acc": 3, "total_acc": 8, "cibil_index": 1,
            "cibil": "Good · 700–749", "credit_year": 2015,
            "loan_amount": 300_000, "tenure_months": 36, "purpose": "other",
            "rate": 11,
        }
        response = self.client.post("/lenders", json=profile)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 6)
        self.assertEqual(data["qualify_count"], 5)
        tata = next(row for row in data["lenders"] if "Tata" in row["name"])
        self.assertEqual(tata["status"], "close")

    def test_prediction_and_whatif_return_band_and_finance(self):
        profile = {
            "age": 30, "employment": "Salaried", "job_years": 5,
            "annual_income": 800_000, "existing_emi": 4_844, "card_bill": 12_000,
            "revol_util": 30, "open_acc": 3, "total_acc": 8, "cibil_index": 1,
            "cibil": "Good · 700–749", "credit_year": 2015,
            "loan_amount": 300_000, "tenure_months": 36, "purpose": "other",
            "rate": 11,
        }
        response = self.client.post("/predict", json=profile)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertGreaterEqual(result["probability"], 0)
        self.assertLessEqual(result["probability"], 1)
        self.assertIn(result["readiness_band"], {"good", "fair", "needs_work"})
        self.assertAlmostEqual(result["finance"]["emi"], 9_822, delta=1)
        changed = self.client.post("/whatif", json={"profile": profile, "changes": {"loan_amount": 250_000}})
        self.assertEqual(changed.status_code, 200)
        self.assertIn("delta", changed.json())
