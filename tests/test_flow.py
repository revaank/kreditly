import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib"))

from streamlit.testing.v1 import AppTest
from src.bank_checker import check_all, count_meets
from src.counterfactual import apply_change
from src.features import build_features
from src.finance import emi, foir, loan_summary
from src.predictor import predict, readiness_band
from src.translations import set_language, reset_language, t
from src.ui import format_risk_pct

class TestFlow(unittest.TestCase):
    def test_app_home_page_loads_and_has_no_errors(self):
        at = AppTest.from_file("app.py", default_timeout=25)
        at.run()
        self.assertFalse(at.exception)
        self.assertTrue(len(at.markdown) > 0)

    def test_samples_page_loads_and_has_no_errors(self):
        at = AppTest.from_file("pages/2_Sample_Cases.py", default_timeout=25)
        at.run()
        self.assertFalse(at.exception)

    def test_insights_page_loads_and_has_no_errors(self):
        at = AppTest.from_file("pages/3_Model_Insights.py", default_timeout=25)
        at.run()
        self.assertFalse(at.exception)

    def test_tools_page_loads_and_has_no_errors(self):
        at = AppTest.from_file("pages/4_Tools.py", default_timeout=25)
        at.run()
        self.assertFalse(at.exception)

    def test_guide_page_loads_and_has_no_errors(self):
        at = AppTest.from_file("pages/5_Guide.py", default_timeout=25)
        at.run()
        self.assertFalse(at.exception)

    def test_about_page_loads_and_has_no_errors(self):
        at = AppTest.from_file("pages/6_About.py", default_timeout=25)
        at.run()
        self.assertFalse(at.exception)

    def test_check_wizard_flow_and_results_sections(self):
        at = AppTest.from_file("pages/1_Check_Eligibility.py", default_timeout=25)
        at.run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["wizard_step"], 1)

        # Step 1: Click Continue
        at.button(key="btn_step1_cont").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["wizard_step"], 2)

        # Step 2: Click Continue
        at.button(key="btn_step2_cont").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["wizard_step"], 3)

        # Step 3: Click Continue
        at.button(key="btn_step3_cont").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["wizard_step"], 4)

        # Step 4: Click Continue
        at.button(key="btn_step4_cont").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["wizard_step"], 5)

        # Step 5: Click Run Check -> Triggers prediction and shows results
        at.button(key="btn_run_check").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["view_mode"], "results")
        self.assertEqual(at.session_state["results_section"], "result")
        self.assertIn("estimate", at.session_state)

        # Check default profile numbers: EMI ₹9,822
        summary = loan_summary(300000, 11.0, 36)
        self.assertEqual(round(summary["emi"]), 9822)

        # Result section: Next to banks
        at.button(key="btn_next_banks").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["results_section"], "banks")

        # Banks section: Next to fixes
        at.button(key="btn_next_fixes").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["results_section"], "fixes")

        # Fixes section: Next to plan
        at.button(key="btn_next_plan").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["results_section"], "plan")
        self.assertIn("whatif_monthly_income", at.session_state)
        self.assertEqual(at.session_state["whatif_monthly_income"], 65000)

        # Plan section: Next to save
        at.button(key="btn_next_save").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["results_section"], "save")

        # Save section: Test edit answers preserves state and returns to wizard
        at.button(key="btn_edit_answers").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["view_mode"], "wizard")
        self.assertEqual(at.session_state["wizard_step"], 1)
        self.assertEqual(at.session_state["profile"]["loan_amount"], 300000)
        self.assertEqual(at.session_state["profile"]["monthly_income"], 65000)

    def test_results_pills_navigation(self):
        """Test that results section chips switch on the first click, stay on re-click, and survive language toggle."""
        at = AppTest.from_file("pages/1_Check_Eligibility.py", default_timeout=25)
        at.run()
        v = dict(at.session_state["profile"])
        feats = build_features(v)
        pred = predict(feats)
        at.session_state["estimate"] = {"features": feats, "result": pred, "values": v}
        at.session_state["view_mode"] = "results"
        at.run()
        self.assertEqual(at.session_state["results_section"], "result")

        # Click Fixes chip ONCE -> switches immediately
        at.button_group(key="results_section_nav").select("Fixes").run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["results_section"], "fixes")

        # Click active chip Fixes again (deselection) -> stays on fixes
        at.button_group(key="results_section_nav").unselect("Fixes").run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["results_section"], "fixes")

        # Toggle to Hindi -> section preserved
        at.session_state["language"] = "हिं"
        at.run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["results_section"], "fixes")
        self.assertEqual(at.session_state["results_section_nav"], "सुधार")

        # Toggle back to English -> section preserved
        at.session_state["language"] = "EN"
        at.run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["results_section"], "fixes")
        self.assertEqual(at.session_state["results_section_nav"], "Fixes")

if __name__ == "__main__":
    unittest.main()
