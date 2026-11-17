import json
from pathlib import Path

import unittest

from src.bank_checker import check_all, count_meets
from src.counterfactual import find_improvements
from src.features import build_features
from src.finance import emi, foir
from src.predictor import predict, readiness_band


PROFILE = {
    "age": 30,
    "employment": "Salaried",
    "job_years": 5,
    "home": "Rented",
    "credit_year": 2015,
    "annual_income": 800_000,
    "existing_emi": 4_844,
    "card_bill": 12_000,
    "revol_util": 30,
    "open_acc": 3,
    "total_acc": 8,
    "mort_acc": 0,
    "pub_rec": 0,
    "bankruptcies": 0,
    "cibil": "Good · 700–749",
    "cibil_index": 1,
    "loan_amount": 300_000,
    "tenure_months": 36,
    "purpose": "Other",
    "rate": 11.0,
}


class TestCore(unittest.TestCase):
 def test_emi_formula_for_example_loan(self):
    self.assertAlmostEqual(emi(300_000, 11, 36), 9_822, delta=1)


 def test_foir_includes_existing_and_new_emi(self):
    monthly_income = 800_000 / 12
    self.assertAlmostEqual(foir(monthly_income, 4_844, emi(300_000, 11, 36)), 22, delta=0.1)


 def test_calibrated_prediction_is_a_valid_probability(self):
    result = predict(build_features(PROFILE))
    self.assertGreaterEqual(result["risk"], 0)
    self.assertLessEqual(result["risk"], 1)
    self.assertIn(result["readiness_band"], {"good", "fair", "needs_work"})


 def test_readiness_band_uses_saved_validation_quantiles(self):
    config = json.loads((Path(__file__).parents[1] / "models" / "readiness.json").read_text(encoding="utf-8"))
    self.assertEqual(readiness_band(config["good_max"]), "good")
    self.assertEqual(readiness_band((config["good_max"] + config["fair_max"]) / 2), "fair")
    self.assertEqual(readiness_band(config["fair_max"] + 1e-5), "needs_work")


 def test_suggestions_use_distinct_helpful_levers(self):
    suggestions = find_improvements(PROFILE)
    fields = [item["field"] for item in suggestions]
    self.assertEqual(len(fields), len(set(fields)))
    self.assertTrue(all(item["risk_reduction"] > 0 for item in suggestions))


 def test_example_profile_meets_five_lenders_and_tata_is_close(self):
    results = check_all(PROFILE)
    self.assertEqual(count_meets(results), 5)
    tata = next(item for item in results if item["id"] == "tata")
    self.assertEqual(tata["status"], "close")
    cibil = next(item for item in tata["rules"] if item["key"] == "min_cibil")
    self.assertEqual(cibil["status"], "warn")


if __name__ == "__main__":
    unittest.main()

