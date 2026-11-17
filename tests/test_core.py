import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib"))

from src.bank_checker import check_all, count_meets
from src.counterfactual import find_improvements
from src.features import build_features
from src.finance import emi, foir
from src.predictor import predict, readiness_band
from src.translations import reset_language, set_language
from src.ui import format_whatif_delta


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
    self.assertLess(result["risk"], 0.5, "The specified strong example stays below the accepted 50% risk target.")
    self.assertIn(result["readiness_band"], {"good", "fair", "needs_work"})


 def test_readiness_band_thresholds(self):
    self.assertEqual(readiness_band(0.10), "good")
    self.assertEqual(readiness_band(0.236), "fair")
    self.assertEqual(readiness_band(0.43), "needs_work")
    # Exact threshold cutoffs (<0.124 good, 0.124-0.324 fair, >0.324 needs work)
    self.assertEqual(readiness_band(0.123), "good")
    self.assertEqual(readiness_band(0.124), "fair")
    self.assertEqual(readiness_band(0.324), "fair")
    self.assertEqual(readiness_band(0.325), "needs_work")


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


 def test_language_toggle_switches_home_page_to_hindi(self):
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file("app.py", default_timeout=25)
    at.run()
    self.assertEqual(at.session_state["language"], "EN")
    en_titles = [m.value for m in at.markdown if "Know where you stand before a bank says no." in m.value]
    self.assertTrue(len(en_titles) > 0)

    # Click toggle button
    at.button(key="toggle_language").click().run()
    self.assertEqual(at.session_state["language"], "हिं")
    hi_titles = [m.value for m in at.markdown if "बैंक के मना करने से पहले अपनी स्थिति समझें।" in m.value]
    self.assertTrue(len(hi_titles) > 0)

    # Toggle back to English
    at.button(key="toggle_language").click().run()
    self.assertEqual(at.session_state["language"], "EN")
    en_titles_restored = [m.value for m in at.markdown if "Know where you stand before a bank says no." in m.value]
    self.assertTrue(len(en_titles_restored) > 0)


 def test_whatif_delta_wording_points_not_percentage(self):
    token = set_language("EN")
    try:
        self.assertEqual(format_whatif_delta(-0.19), "↓ 19 points lower")
        self.assertEqual(format_whatif_delta(0.05), "↑ 5 points higher")
        self.assertEqual(format_whatif_delta(0.001), "No change")
        self.assertEqual(format_whatif_delta(-0.01), "↓ 1 point lower")
    finally:
        reset_language(token)

    token = set_language("हिं")
    try:
        self.assertEqual(format_whatif_delta(-0.19), "↓ 19 अंक कम")
        self.assertEqual(format_whatif_delta(0.05), "↑ 5 अंक अधिक")
        self.assertEqual(format_whatif_delta(0.001), "कोई बदलाव नहीं")
    finally:
        reset_language(token)


if __name__ == "__main__":
    unittest.main()

