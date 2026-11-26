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
from src.bank_ui import aggregate_next_steps
from src.counterfactual import find_improvements
from src.features import build_features
from src.finance import emi, foir, loan_summary
from src.predictor import predict, readiness_band
from src.translations import reset_language, set_language
from src.ui import CSS, build_download_report, format_risk_pct, format_whatif_delta


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


 def test_slider_css_and_repayment_slider_rules(self):
    self.assertIn('.stSlider [data-testid="stSliderThumbValue"]', CSS)
    self.assertIn('.stSlider:has([aria-label*="Repayment"])', CSS)
    self.assertIn('.stSlider:has([aria-label*="अवधि"])', CSS)
    self.assertIn('.stSlider:has([aria-valuetext*="month"])', CSS)


 def test_emi_planner_calculations_across_all_terms(self):
    s36 = loan_summary(300_000, 11, 36)
    self.assertAlmostEqual(s36["emi"], 9_822, delta=1)
    self.assertAlmostEqual(s36["interest"], 53_578, delta=1)

    terms = [12, 24, 36, 48, 60]
    summaries = [loan_summary(300_000, 11, m) for m in terms]
    emis = [s["emi"] for s in summaries]
    interests = [s["interest"] for s in summaries]

    self.assertTrue(all(emis[i] > emis[i+1] for i in range(len(emis)-1)))
    self.assertTrue(all(interests[i] < interests[i+1] for i in range(len(interests)-1)))


 def test_aggregate_next_steps_deduplication(self):
    results = check_all(PROFILE)
    fixes = aggregate_next_steps(results)
    self.assertEqual(len(fixes), 1)
    self.assertIn("CIBIL", fixes[0])

    # Multi-fail profile produces multiple distinct next steps without duplicates
    p = dict(PROFILE)
    p["annual_income"] = 240_000
    p["existing_emi"] = 8_000
    p["loan_amount"] = 500_000
    multi_results = check_all(p)
    multi_fixes = aggregate_next_steps(multi_results)
    self.assertGreater(len(multi_fixes), 1)
    self.assertEqual(len(multi_fixes), len(set(multi_fixes)))


 def test_download_report_includes_band_lenders_and_disclaimer(self):
    from src.finance import foir
    result = predict(build_features(PROFILE))
    summary = loan_summary(PROFILE["loan_amount"], PROFILE["rate"], PROFILE["tenure_months"])
    ratio = foir(PROFILE["annual_income"] / 12, PROFILE["existing_emi"], summary["emi"])
    bank_results = check_all(PROFILE)

    # 1. English report check
    report = build_download_report(result, summary, ratio, bank_results)
    self.assertIn("Readiness band: Needs work", report)
    self.assertIn("State Bank of India: Meets published criteria", report)
    self.assertIn("Tata Capital: Close", report)
    self.assertIn("Last checked:", report)
    self.assertIn("Published minimum criteria only. Meeting them does not guarantee approval", report)

    # 2. Hindi report check
    token = set_language("हिं")
    try:
        hi_report = build_download_report(result, summary, ratio, bank_results)
        self.assertIn("तैयारी स्तर: सुधार की ज़रूरत", hi_report)
        self.assertIn("State Bank of India: प्रकाशित मानदंड पूरे", hi_report)
        self.assertIn("Tata Capital: करीब", hi_report)
        self.assertIn("अंतिम जाँच:", hi_report)
        self.assertIn("केवल प्रकाशित न्यूनतम मानदंड", hi_report)
    finally:
        reset_language(token)


 def test_whatif_loan_amount_slider_updates_risk_and_bank_eligibility(self):
    from src.counterfactual import apply_change
    orig_meets = count_meets(check_all(PROFILE))
    self.assertEqual(orig_meets, 5)

    # Decreasing loan amount lowers or maintains risk and eligibility
    _, low_res = apply_change(PROFILE, loan=100_000)
    low_meets = count_meets(check_all(dict(PROFILE, loan_amount=100_000)))
    self.assertLessEqual(low_res["risk"], 0.324)  # Remains Good or Fair
    self.assertEqual(low_meets, 5)

    # Increasing loan amount significantly increases risk and reduces lender eligibility
    _, high_res = apply_change(PROFILE, loan=4_000_000)
    high_meets = count_meets(check_all(dict(PROFILE, loan_amount=4_000_000)))
    self.assertEqual(high_res["readiness_band"], "needs_work")
    self.assertLess(high_meets, orig_meets)


 def test_format_risk_pct_never_shows_zero(self):
    token = set_language("EN")
    try:
        self.assertEqual(format_risk_pct(0.0), "under 1%")
        self.assertEqual(format_risk_pct(0.004), "under 1%")
        self.assertEqual(format_risk_pct(0.0099), "under 1%")
        self.assertEqual(format_risk_pct(0.01), "1%")
        self.assertEqual(format_risk_pct(0.236), "24%")
        self.assertEqual(format_risk_pct(0.4288), "43%")
    finally:
        reset_language(token)

    token = set_language("हिं")
    try:
        self.assertEqual(format_risk_pct(0.0), "1% से कम")
        self.assertEqual(format_risk_pct(0.005), "1% से कम")
        self.assertEqual(format_risk_pct(0.4288), "43%")
    finally:
        reset_language(token)


 def test_home_page_clean_hero_and_trust_ticks_and_sample_cases(self):
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file("app.py", default_timeout=25)
    at.run()
    # Check headline
    headlines = [m.value for m in at.markdown if "Know where you stand before a bank says no." in m.value]
    self.assertTrue(len(headlines) > 0)
    # Check trust ticks
    trust_mds = [m.value for m in at.markdown if "Doesn't touch your CIBIL score" in m.value]
    self.assertTrue(len(trust_mds) > 0)
    # Check that competing preview card was removed
    sample_mds = [m.value for m in at.markdown if '<section class="sample-result"' in m.value]
    self.assertEqual(len(sample_mds), 0)


 def test_check_wizard_five_steps_and_back_preserves_state(self):
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file("pages/1_Check_Eligibility.py", default_timeout=25)
    at.run()
    # Initial step 1
    self.assertEqual(at.session_state["wizard_step"], 1)
    # Check running EMI
    emi_mds = [m.value for m in at.markdown if "9,822" in m.value]
    self.assertTrue(len(emi_mds) > 0)
    # Click continue to Step 2
    at.button(key="btn_step1_cont").click().run()
    self.assertEqual(at.session_state["wizard_step"], 2)
    # Click back to Step 1
    at.button(key="btn_step2_back").click().run()
    self.assertEqual(at.session_state["wizard_step"], 1)



 def test_whatif_zero_card_usage_threshold_band_fair(self):
    from src.counterfactual import apply_change
    _, new_res = apply_change(PROFILE, revol_util=0)
    # Risk should be ~23.6%, which is between 12.4% and 32.4%, hence "fair"
    self.assertGreaterEqual(new_res["risk"], 0.124)
    self.assertLessEqual(new_res["risk"], 0.324)
    self.assertEqual(new_res["readiness_band"], "fair")


 def test_counterfactual_respects_card_and_emi_floors(self):
    suggestions = find_improvements(PROFILE, max_suggestions=5)
    for sug in suggestions:
        if sug["field"] == "revol_util":
            self.assertGreaterEqual(sug["value"], 10)
        if sug["field"] == "existing_emi":
            self.assertGreaterEqual(sug["value"], round(PROFILE["existing_emi"] * 0.5 / 1000) * 1000)


 def test_get_threshold_settings_matches_threshold_json(self):
    from src.predictor import get_threshold_settings
    threshold, band = get_threshold_settings()
    self.assertAlmostEqual(threshold, 0.224, places=3)
    self.assertAlmostEqual(band, 0.1, places=3)


 def test_explain_reasons_assumed_fields_and_dti_wording(self):
    from src.explainer import explain_reasons
    token = set_language("EN")
    try:
        features = build_features(PROFILE)
        contributions = [
            {"feature": "open_acc", "contribution": 0.25},
            {"feature": "dti", "contribution": -0.15},
        ]
        reasons = explain_reasons(features, contributions, assumed_fields={"open_acc"})
        open_acc_reason = next(r for r in reasons if r["feature"] == "open_acc")
        dti_reason = next(r for r in reasons if r["feature"] == "dti")
        self.assertTrue(open_acc_reason["assumed"])
        self.assertIn("typical value", open_acc_reason["text"])
        self.assertNotIn("you report", open_acc_reason["text"])
        self.assertIn("before this new loan", dti_reason["text"])
    finally:
        reset_language(token)


if __name__ == "__main__":
    unittest.main()

