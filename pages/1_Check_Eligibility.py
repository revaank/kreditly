from __future__ import annotations

# Five-screen guided wizard and progressive educational results.
from urllib.parse import quote
import streamlit as st
import streamlit.components.v1 as components

from src.bank_checker import check_all, count_meets, load_bank_rules
from src.bank_ui import aggregate_next_steps, render_bank_results, render_lender_cards
from src.counterfactual import apply_change, find_improvements
from src.explainer import explain_reasons, suggestion_text
from src.features import build_features
from src.finance import foir, format_inr, loan_summary
from src.predictor import explain, get_threshold_settings, predict
from src.readiness import safe_loan_amount, standing, standing_reasons, total_foir
from src.translations import t
from src.ui import (
    build_download_report,
    chip_selector,
    contribution_chart,
    footer,
    format_risk_pct,
    header,
    money_input,
    page_setup,
    render_emi_planner,
    render_feedback,
    render_running_emi,
    render_whatif_result,
    result_card,
    section_title,
)

page_setup()
header("check")

for k, def_v in [
    ("whatif_monthly_income", 65000),
    ("whatif_loan", 300000),
    ("whatif_emi", 5000),
    ("whatif_util", 30),
    ("whatif_tenure", 36),
]:
    if k not in st.session_state:
        st.session_state[k] = def_v

def _scroll_top_if_changed(target: str):
    """Scroll to top when wizard step or results section changes."""
    prev = st.session_state.get("last_scroll_target")
    st.session_state["last_scroll_target"] = target
    if prev is not None and prev != target:
        components.html(
            f"""<!-- {target} -->
            <script>
            (function() {{
                function doScroll() {{
                    try {{
                        window.parent.scrollTo(0, 0);
                        var doc = window.parent.document;
                        doc.documentElement.scrollTop = 0;
                        doc.body.scrollTop = 0;
                        var selectors = ['section.stMain', 'section.main', '[data-testid="stMain"]', '[data-testid="stAppViewContainer"]'];
                        selectors.forEach(function(sel) {{
                            var el = doc.querySelector(sel);
                            if (el) el.scrollTo(0, 0);
                        }});
                    }} catch (e) {{}}
                }}
                doScroll();
                requestAnimationFrame(doScroll);
                setTimeout(doScroll, 80);
            }})();
            </script>""",
            height=0,
        )

def india_profile(values: dict) -> dict:
    """Map Kreditly form values to the src.india_model.assess() profile dict."""
    from datetime import date
    band_map = {0: "excellent", 1: "good", 2: "average", 3: "low", 4: "no_history", 5: "dont_know"}
    cibil_idx = values.get("cibil_index")
    cibil_band = band_map.get(cibil_idx, "dont_know")

    if cibil_idx == 4 or values.get("credit_unknown") or values.get("credit_year") is None:
        credit_years = None
    else:
        credit_years = max(0, date.today().year - int(values["credit_year"]))

    active_loans = None if (cibil_idx == 4 or values.get("open_acc") is None) else int(values["open_acc"])
    emp = "self_employed" if values.get("employment") == "Self-employed" else "salaried"

    return {
        "age": float(values.get("age", 30)),
        "employment": emp,
        "cibil_band": cibil_band,
        "credit_years": credit_years,
        "active_loans": active_loans,
        "existing_emi": float(values.get("existing_emi", 0)),
        "missed_emi_last_6m": values.get("missed_emi_last_6m"),
        "overdue_loans": values.get("overdue_loans"),
        "new_loans_last_6m": values.get("new_loans_last_6m"),
        "loan_enquiries": values.get("loan_enquiries"),
    }


def assess_india_profile(values: dict, lang: str = "en") -> dict | None:
    """Safely run India repayment check; returns None if model files are missing."""
    try:
        from src.india_model import assess
        return assess(india_profile(values), lang=lang)
    except Exception:
        return None


def reset_whatif():
    p = st.session_state.get("estimate", {}).get("values") or st.session_state.get("profile", DEFAULT_PROFILE)
    st.session_state["whatif_monthly_income"] = int(p.get("monthly_income", 65000))
    st.session_state["whatif_loan"] = int(p.get("loan_amount", 300000))
    st.session_state["whatif_emi"] = int(p.get("existing_emi", 5000))
    st.session_state["whatif_util"] = int(p.get("revol_util", 30))
    st.session_state["whatif_tenure"] = int(p.get("tenure_months", 36))

# Initialize wizard profile defaults
DEFAULT_PROFILE = {
    "age": 30,
    "employment": "Salaried",
    "employment_index": 0,
    "job_years": 5,
    "home": "rented",
    "credit_year": 2015,
    "credit_unknown": False,
    "monthly_income": 65000,  # chip value
    "annual_income": 780000,  # 65000 * 12
    "existing_emi": 5000,
    "card_bill": 12000,
    "revol_util": 30,
    "open_acc": 3,
    "total_acc": 8,
    "mort_acc": 0,
    "pub_rec": 0,
    "bankruptcies": 0,
    "cibil": "Good · 700–749",
    "cibil_index": 1,
    "cibil_unknown": False,
    "loan_amount": 300000,
    "tenure_months": 36,
    "purpose": "debt_consolidation",
    "rate": 11.0,
    "missed_emi_last_6m": None,
    "overdue_loans": None,
    "new_loans_last_6m": None,
    "loan_enquiries": None,
}

if "profile" not in st.session_state:
    st.session_state.profile = dict(DEFAULT_PROFILE)

v = st.session_state.profile

# Sync monthly income and annual income
if "monthly_income" not in v:
    v["monthly_income"] = int(round(v.get("annual_income", 800000) / 12))
v["annual_income"] = int(round(v["monthly_income"] * 12))

# Wizard steps
STEP_NAMES = [
    t("step_loan"),
    t("step_income"),
    t("step_emis"),
    t("step_credit"),
    t("step_about"),
]

if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1

# Handle edit mode or reset
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "wizard" if "estimate" not in st.session_state else "results"

# -------------------------------------------------------------
# WIZARD MODE: 5 short screens, ONE screen visible at a time
# -------------------------------------------------------------
if st.session_state.view_mode == "wizard":
    step = int(st.session_state.wizard_step)
    _scroll_top_if_changed(f"wizard_{step}")
    st.progress(step / 5, text=t("step_of", step=step, total=5, name=STEP_NAMES[step - 1]))

    with st.container(border=True):
        # ---------------- Screen 1: The Loan ----------------
        if step == 1:
            st.markdown(f"### {t('q_loan')}")
            st.caption(f"💡 {t('why_loan')}")

            # Amount chips + custom input
            amount_chips = ["₹1,00,000", "₹2,00,000", "₹3,00,000", "₹5,00,000", "₹10,00,000", "Custom"]
            chip_map = {
                "₹1,00,000": 100000,
                "₹2,00,000": 200000,
                "₹3,00,000": 300000,
                "₹5,00,000": 500000,
                "₹10,00,000": 1000000,
            }
            rev_chip_map = {v_val: k for k, v_val in chip_map.items()}
            cur_amt_chip = rev_chip_map.get(int(v["loan_amount"]), "Custom")
            selected_chip = chip_selector(t("loan_amount"), amount_chips, cur_amt_chip, key="chip_loan_amt")

            if selected_chip in chip_map:
                v["loan_amount"] = chip_map[selected_chip]

            num_loan = st.number_input(
                t("loan_amount") + " (₹)",
                min_value=10000,
                max_value=5000000,
                value=int(v["loan_amount"]),
                step=25000,
                key="num_loan_amt",
            )
            if num_loan != v["loan_amount"]:
                v["loan_amount"] = num_loan
                st.session_state["chip_loan_amt"] = rev_chip_map.get(num_loan, "Custom")

            # Repayment period chips
            tenure_chips = ["12 months (1 yr)", "24 months (2 yrs)", "36 months (3 yrs)", "48 months (4 yrs)", "60 months (5 yrs)"]
            tenure_map = {12: tenure_chips[0], 24: tenure_chips[1], 36: tenure_chips[2], 48: tenure_chips[3], 60: tenure_chips[4]}
            rev_tenure_map = {tenure_chips[0]: 12, tenure_chips[1]: 24, tenure_chips[2]: 36, tenure_chips[3]: 48, tenure_chips[4]: 60}
            def_tenure_chip = tenure_map.get(v["tenure_months"], tenure_chips[2])
            selected_tenure_chip = chip_selector(t("tenure"), tenure_chips, def_tenure_chip, key="chip_tenure")
            v["tenure_months"] = rev_tenure_map.get(selected_tenure_chip, 36)

            # Purpose
            purposes = [t("p_debt"), t("p_card"), t("p_home"), t("p_purchase"), t("p_business"), t("p_vehicle"), t("p_medical"), t("p_other")]
            purpose_codes = ["debt_consolidation", "credit_card", "home_improvement", "major_purchase", "small_business", "car", "medical", "other"]
            p_idx = purpose_codes.index(v["purpose"]) if v["purpose"] in purpose_codes else 0
            selected_p = st.selectbox(t("purpose"), purposes, index=p_idx, key="select_purpose")
            v["purpose"] = purpose_codes[purposes.index(selected_p)]

            with st.expander(t("rate")):
                v["rate"] = st.number_input(t("rate"), min_value=1.0, max_value=40.0, step=0.5, value=float(v["rate"]), key="num_rate")

            render_running_emi(v["loan_amount"], v["rate"], v["tenure_months"])

            if st.button(t("continue"), type="primary", use_container_width=True, key="btn_step1_cont"):
                if v["loan_amount"] <= 0:
                    st.error(t("loan_positive"))
                else:
                    st.session_state.wizard_step = 2
                    st.rerun()

        # ---------------- Screen 2: Your Income ----------------
        elif step == 2:
            st.markdown(f"### {t('q_income')}")
            st.caption(f"💡 {t('why_income')}")

            salary_chips = ["₹25,000", "₹50,000", "₹65,000", "₹75,000", "₹1,00,000", "Custom"]
            salary_map = {"₹25,000": 25000, "₹50,000": 50000, "₹65,000": 65000, "₹75,000": 75000, "₹1,00,000": 100000}
            rev_salary_map = {v_val: k for k, v_val in salary_map.items()}
            cur_sal_chip = rev_salary_map.get(int(v["monthly_income"]), "Custom")
            selected_sal_chip = chip_selector(t("monthly_salary"), salary_chips, cur_sal_chip, key="chip_salary")
            if selected_sal_chip in salary_map:
                v["monthly_income"] = salary_map[selected_sal_chip]

            num_sal = st.number_input(
                t("monthly_salary") + " (₹)",
                min_value=5000,
                max_value=2000000,
                value=int(v["monthly_income"]),
                step=5000,
                key="num_salary",
            )
            if num_sal != v["monthly_income"]:
                v["monthly_income"] = num_sal
                st.session_state["chip_salary"] = rev_salary_map.get(num_sal, "Custom")
            v["annual_income"] = int(round(v["monthly_income"] * 12))
            st.caption(f"Yearly income equivalent: {format_inr(v['annual_income'])}")

            # Employment type
            emp_chips = [t("salaried"), t("self_employed")]
            def_emp = emp_chips[0] if v["employment"] in ("Salaried", "वेतनभोगी") else emp_chips[1]
            selected_emp = chip_selector(t("employment"), emp_chips, def_emp, key="chip_emp")
            v["employment"] = "Salaried" if selected_emp == emp_chips[0] else "Self-employed"
            v["employment_index"] = 0 if v["employment"] == "Salaried" else 1

            # Job years
            job_chips = ["< 1 year", "1–2 years", "3–5 years", "5+ years", "10+ years"]
            job_map = {"< 1 year": 0, "1–2 years": 2, "3–5 years": 4, "5+ years": 6, "10+ years": 10}
            cur_job_chip = "5+ years" if v["job_years"] >= 5 and v["job_years"] < 10 else ("10+ years" if v["job_years"] >= 10 else "3–5 years")
            selected_job = chip_selector(t("job_years"), job_chips, cur_job_chip, key="chip_job")
            v["job_years"] = job_map.get(selected_job, 5)

            render_running_emi(v["loan_amount"], v["rate"], v["tenure_months"])

            col_b, col_c = st.columns(2)
            with col_b:
                if st.button(t("back"), use_container_width=True, key="btn_step2_back"):
                    st.session_state.wizard_step = 1
                    st.rerun()
            with col_c:
                if st.button(t("continue"), type="primary", use_container_width=True, key="btn_step2_cont"):
                    if v["monthly_income"] <= 0:
                        st.error(t("income_positive"))
                    else:
                        st.session_state.wizard_step = 3
                        st.rerun()

        # ---------------- Screen 3: Your EMIs ----------------
        elif step == 3:
            st.markdown(f"### {t('q_emis')}")
            st.caption(f"💡 {t('why_emis')}")

            # Existing EMIs
            emi_chips = ["₹0", "₹2,000", "₹5,000", "₹10,000", "₹20,000", "Custom"]
            emi_map = {"₹0": 0, "₹2,000": 2000, "₹5,000": 5000, "₹10,000": 10000, "₹20,000": 20000}
            rev_emi_map = {v_val: k for k, v_val in emi_map.items()}
            cur_emi_chip = rev_emi_map.get(int(v["existing_emi"]), "Custom")
            selected_emi_chip = chip_selector(t("existing_emi"), emi_chips, cur_emi_chip, key="chip_existing_emi")
            if selected_emi_chip in emi_map:
                v["existing_emi"] = emi_map[selected_emi_chip]

            num_emi = st.number_input(
                t("existing_emi") + " (₹)",
                min_value=0,
                max_value=500000,
                value=int(v["existing_emi"]),
                step=1000,
                key="num_existing_emi",
            )
            if num_emi != v["existing_emi"]:
                v["existing_emi"] = num_emi
                st.session_state["chip_existing_emi"] = rev_emi_map.get(num_emi, "Custom")

            # Card usage
            card_chips = [t("no_card"), t("very_little"), t("third"), t("half"), t("almost_all")]
            card_vals = [0, 10, 30, 50, 90]
            cur_util_idx = card_vals.index(v["revol_util"]) if v["revol_util"] in card_vals else 2
            selected_card_chip = chip_selector(t("card_usage"), card_chips, card_chips[cur_util_idx], key="chip_card_util")
            v["revol_util"] = card_vals[card_chips.index(selected_card_chip)]

            # Card bill
            bill_chips = ["₹0", "₹5,000", "₹12,000", "₹25,000", "₹50,000+", "Custom"]
            bill_map = {"₹0": 0, "₹5,000": 5000, "₹12,000": 12000, "₹25,000": 25000, "₹50,000+": 50000}
            rev_bill_map = {v_val: k for k, v_val in bill_map.items()}
            cur_bill_chip = rev_bill_map.get(int(v["card_bill"]), "Custom")
            selected_bill_chip = chip_selector(t("card_bill"), bill_chips, cur_bill_chip, key="chip_card_bill")
            if selected_bill_chip in bill_map:
                v["card_bill"] = bill_map[selected_bill_chip]

            num_bill = st.number_input(
                t("card_bill") + " (₹)",
                min_value=0,
                max_value=1000000,
                value=int(v["card_bill"]),
                step=2000,
                key="num_card_bill",
            )
            if num_bill != v["card_bill"]:
                v["card_bill"] = num_bill
                st.session_state["chip_card_bill"] = rev_bill_map.get(num_bill, "Custom")

            render_running_emi(v["loan_amount"], v["rate"], v["tenure_months"])

            col_b, col_c = st.columns(2)
            with col_b:
                if st.button(t("back"), use_container_width=True, key="btn_step3_back"):
                    st.session_state.wizard_step = 2
                    st.rerun()
            with col_c:
                if st.button(t("continue"), type="primary", use_container_width=True, key="btn_step3_cont"):
                    st.session_state.wizard_step = 4
                    st.rerun()

        # ---------------- Screen 4: Your Credit ----------------
        elif step == 4:
            st.markdown(f"### {t('q_credit')}")
            st.caption(f"💡 {t('why_credit')}")

            cibil_chips = [t("excellent"), t("good"), t("average"), t("low"), t("no_history"), t("dont_know")]
            cibil_idx = min(int(v.get("cibil_index", 1)), len(cibil_chips) - 1)
            selected_cibil = chip_selector(t("cibil"), cibil_chips, cibil_chips[cibil_idx], key="chip_cibil")
            v["cibil"] = selected_cibil
            v["cibil_index"] = cibil_chips.index(selected_cibil)
            v["cibil_unknown"] = v["cibil_index"] in (4, 5)
            st.caption(t("cibil_help"))

            with st.expander(t("credit_details_expander"), expanded=False):
                ic1, ic2 = st.columns(2)
                with ic1:
                    v["missed_emi_last_6m"] = st.number_input(
                        t("india_missed_emi"), min_value=0, max_value=20,
                        value=v.get("missed_emi_last_6m"), step=1,
                        placeholder=t("not_sure"), help=t("india_missed_emi_help"),
                        key="num_india_missed_emi",
                    )
                    v["new_loans_last_6m"] = st.number_input(
                        t("india_new_loans"), min_value=0, max_value=20,
                        value=v.get("new_loans_last_6m"), step=1,
                        placeholder=t("not_sure"), help=t("india_new_loans_help"),
                        key="num_india_new_loans",
                    )
                with ic2:
                    v["overdue_loans"] = st.number_input(
                        t("india_overdue_loans"), min_value=0, max_value=20,
                        value=v.get("overdue_loans"), step=1,
                        placeholder=t("not_sure"), help=t("india_overdue_loans_help"),
                        key="num_india_overdue_loans",
                    )
                    v["loan_enquiries"] = st.number_input(
                        t("india_loan_enquiries"), min_value=0, max_value=20,
                        value=v.get("loan_enquiries"), step=1,
                        placeholder=t("not_sure"), help=t("india_loan_enquiries_help"),
                        key="num_india_loan_enquiries",
                    )

                st.markdown("---")
                st.caption(t("credit_defaults_caption"))
                if v["cibil_index"] != 4:
                    col1, col2 = st.columns(2)
                    with col1:
                        v["credit_year"] = st.number_input(t("credit_year"), 1980, 2026, int(v["credit_year"]), key="num_credit_year")
                        v["credit_unknown"] = st.checkbox(t("dont_know"), value=bool(v.get("credit_unknown", False)), key="chk_credit_unknown")
                    with col2:
                        v["open_acc"] = st.number_input(t("open_accounts"), min_value=0, max_value=100, value=int(v["open_acc"]), key="num_open_acc")
                col3, col4 = st.columns(2)
                with col3:
                    v["total_acc"] = st.number_input(t("total_accounts"), min_value=0, max_value=150, value=int(v["total_acc"]), key="num_total_acc")
                with col4:
                    v["mort_acc"] = st.number_input(t("mort_accounts"), min_value=0, max_value=50, value=int(v["mort_acc"]), key="num_mort_acc")
                col5, col6 = st.columns(2)
                with col5:
                    v["pub_rec"] = st.number_input(t("public_records"), min_value=0, max_value=50, value=int(v["pub_rec"]), key="num_pub_rec")
                with col6:
                    v["bankruptcies"] = st.number_input(t("bankruptcies"), min_value=0, max_value=20, value=int(v["bankruptcies"]), key="num_bankruptcies")

            render_running_emi(v["loan_amount"], v["rate"], v["tenure_months"])

            col_b, col_c = st.columns(2)
            with col_b:
                if st.button(t("back"), use_container_width=True, key="btn_step4_back"):
                    st.session_state.wizard_step = 3
                    st.rerun()
            with col_c:
                if st.button(t("continue"), type="primary", use_container_width=True, key="btn_step4_cont"):
                    if v["open_acc"] > v["total_acc"]:
                        st.error(t("accounts_check"))
                    else:
                        st.session_state.wizard_step = 5
                        st.rerun()

        # ---------------- Screen 5: About You ----------------
        elif step == 5:
            st.markdown(f"### {t('q_about')}")
            st.caption(f"💡 {t('why_about')}")

            age_chips = ["22", "26", "30", "35", "42", "50", "Custom"]
            cur_age_str = str(int(v["age"]))
            def_age_chip = cur_age_str if cur_age_str in age_chips else "Custom"
            selected_age_chip = chip_selector(t("age"), age_chips, def_age_chip, key="chip_age")
            if selected_age_chip != "Custom" and selected_age_chip.isdigit():
                v["age"] = int(selected_age_chip)

            num_age = st.number_input(t("age"), min_value=18, max_value=100, value=int(v["age"]), key="num_age")
            if num_age != v["age"]:
                v["age"] = num_age
                st.session_state["chip_age"] = str(int(num_age)) if str(int(num_age)) in age_chips else "Custom"

            home_chips = [t("rented"), t("own"), t("own_loan")]
            home_key_map = {t("rented"): "rented", t("own"): "own", t("own_loan"): "own_loan"}
            rev_home_map = {"rented": t("rented"), "own": t("own"), "own_loan": t("own_loan")}
            def_home = rev_home_map.get(v["home"], t("rented"))
            selected_home = chip_selector(t("home"), home_chips, def_home, key="chip_home")
            v["home"] = home_key_map.get(selected_home, "rented")

            render_running_emi(v["loan_amount"], v["rate"], v["tenure_months"])

            col_b, col_c = st.columns(2)
            with col_b:
                if st.button(t("back"), use_container_width=True, key="btn_step5_back"):
                    st.session_state.wizard_step = 4
                    st.rerun()
            with col_c:
                if st.button(t("run_check"), type="primary", use_container_width=True, key="btn_run_check"):
                    with st.spinner(t("checking_lenders", count=15)):
                        try:
                            features = build_features(v)
                            prediction = predict(features)
                            st.session_state.estimate = {
                                "features": features,
                                "result": prediction,
                                "values": dict(v),
                            }
                            st.session_state.results_section = "result"
                            st.session_state.view_mode = "results"
                        except Exception:
                            st.error(t("model_error"))
                            st.stop()
                    st.rerun()

    footer()

# -------------------------------------------------------------
# RESULTS MODE: Revealed step by step with Section Switcher
# -------------------------------------------------------------
else:
    estimate = st.session_state.estimate
    result = estimate["result"]
    values = estimate["values"]
    features = estimate["features"]

    # Calculate finance summaries
    summary = loan_summary(values["loan_amount"], values["rate"], values["tenure_months"])
    monthly_inc = float(values.get("monthly_income", values.get("annual_income", 800000) / 12))
    ratio = foir(monthly_inc, values["existing_emi"], summary["emi"])

    # Load bank results
    try:
        rules = load_bank_rules()
        bank_results = check_all(values, rules)
    except Exception:
        bank_results = []

    # Section switcher
    sections = [
        ("result", t("sec_result")),
        ("banks", t("sec_banks")),
        ("fixes", t("sec_fixes")),
        ("plan", t("sec_plan")),
        ("save", t("sec_save")),
    ]
    sec_keys = [k for k, _ in sections]
    sec_labels = [label for _, label in sections]

    cur_sec = st.session_state.get("results_section", "result")
    cur_label = dict(sections).get(cur_sec, sec_labels[0])

    selected_sec_label = chip_selector(t("section_label"), sec_labels, cur_label, key="results_section_nav")
    # Sync selected section key
    for k, label in sections:
        if label == selected_sec_label:
            st.session_state.results_section = k
            cur_sec = k
            break

    _scroll_top_if_changed(f"results_{cur_sec}")

    # ==================== Section 1: Your Result ====================
    if cur_sec == "result":
        monthly_inc = float(values.get("annual_income", 0)) / 12.0
        exist_emi = float(values.get("existing_emi", 0))
        new_loan_emi = summary["emi"]
        cur_foir_pct = total_foir(monthly_inc, exist_emi, new_loan_emi)
        lenders_met = count_meets(bank_results)
        lenders_total = len(bank_results)
        cibil_val = values.get("cibil_index") if values.get("cibil_index") is not None else values.get("cibil")

        # 1. Headline card (Indian lending standing)
        st_status = standing(cur_foir_pct, cibil_val, lenders_met, lenders_total)
        st_title = t(f"standing_{st_status}_title")
        st_reasons = standing_reasons(cur_foir_pct, cibil_val, lenders_met, lenders_total)

        if st_status == "good":
            st_border = "#15803D"
            st_card_class = "good"
        elif st_status == "almost":
            st_border = "#D97706"
            st_card_class = "borderline"
        else:
            st_border = "#DC2626"
            st_card_class = "risky"

        reasons_html = "".join([f'<div style="font-size:14px;color:#35443A;line-height:1.6;margin:3px 0;">• {r}</div>' for r in st_reasons])

        st.markdown(
            f'<div class="result-card {st_card_class}" style="margin-top:12px;margin-bottom:16px;border-top-color:{st_border}!important;">'
            f'<div class="small-label">{t("where_you_stand").upper()}</div>'
            f'<h2 style="font-size:30px;margin:8px 0 12px;font-family:\'Space Grotesk\',sans-serif;color:#0F1B15;">{st_title}</h2>'
            f'{reasons_html}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # 2. "How much can you safely borrow?" card
        rate = float(values.get("rate", 11.0))
        months = int(values.get("tenure_months", 36))
        safe_comf = safe_loan_amount(monthly_inc, exist_emi, rate, months, 40)
        safe_stretch = safe_loan_amount(monthly_inc, exist_emi, rate, months, 50)
        loan_asked = float(values.get("loan_amount", 0))

        if loan_asked <= safe_comf:
            asked_icon = "✅"
        elif loan_asked <= safe_stretch:
            asked_icon = "⚠️"
        else:
            asked_icon = "❌"

        with st.container(border=True):
            st.markdown(f'<div class="small-label">{t("safe_borrow_label").upper()}</div>', unsafe_allow_html=True)
            st.markdown(f'<h3 style="font-size:20px;margin:4px 0 12px;font-family:\'Space Grotesk\',sans-serif;color:#0F1B15;">{t("safe_borrow_title")}</h3>', unsafe_allow_html=True)
            col_comf, col_asked = st.columns([1, 1])
            with col_comf:
                st.markdown(
                    f'<div style="font-size:13px;color:#4A554F;margin-bottom:2px;">{t("safe_comfortable_label")}</div>'
                    f'<div style="font-size:26px;font-weight:700;color:#15803D;font-family:\'Space Grotesk\',sans-serif;">{format_inr(safe_comf)}</div>'
                    f'<div style="font-size:12px;color:#6B7280;margin-top:2px;">{t("safe_stretch_label")}: <b>{format_inr(safe_stretch)}</b></div>',
                    unsafe_allow_html=True,
                )
            with col_asked:
                st.markdown(
                    f'<div style="font-size:13px;color:#4A554F;margin-bottom:2px;">{t("safe_asked_label")}</div>'
                    f'<div style="font-size:26px;font-weight:700;color:#0F1B15;font-family:\'Space Grotesk\',sans-serif;">{asked_icon} {format_inr(loan_asked)}</div>'
                    f'<div style="font-size:12px;color:#6B7280;margin-top:2px;">{t("safe_tenure_rate_note", months=months, rate=rate)}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown(
                f'<p style="font-size:13px;color:#4A554F;margin-top:14px;margin-bottom:0;line-height:1.5;">'
                f'{t("safe_borrow_explainer")}'
                f'</p>',
                unsafe_allow_html=True,
            )

        # 3. 3 stat tiles
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f'<div class="panel" style="text-align:center;padding:16px 12px;">'
                f'<div class="small-label">{t("monthly_emi")}</div>'
                f'<strong style="font-size:22px;color:#0F1B15;font-family:\'Space Grotesk\',sans-serif;">{format_inr(summary["emi"])}</strong>'
                f'<div style="font-size:12px;color:#4A554F;">{t("per_month")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="panel" style="text-align:center;padding:16px 12px;">'
                f'<div class="small-label">{t("v2_lenders_met")}</div>'
                f'<strong style="font-size:22px;color:#0F1B15;font-family:\'Space Grotesk\',sans-serif;">{lenders_met} / {lenders_total}</strong>'
                f'<div style="font-size:12px;color:#4A554F;">{t("lenders_matched")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="panel" style="text-align:center;padding:16px 12px;">'
                f'<div class="small-label">{t("total_interest")}</div>'
                f'<strong style="font-size:22px;color:#0F1B15;font-family:\'Space Grotesk\',sans-serif;">{format_inr(summary["interest"])}</strong>'
                f'<div style="font-size:12px;color:#4A554F;">{t("over_months", months=values["tenure_months"])}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # 4. India repayment check (main ML card)
        lang_code = "hi" if st.session_state.get("language") == "हिं" else "en"
        india_res = assess_india_profile(values, lang=lang_code)
        if india_res is not None:
            band = india_res["band"]
            band_color = {"lower": "#15803D", "typical": "#8A4B00", "higher": "#B63E32"}.get(band, "#8A4B00")
            band_bg = {"lower": "#ECFCCB", "typical": "#FEF3C7", "higher": "#FEE2E2"}.get(band, "#FEF3C7")
            band_label = t(f"india_band_{band}")
            with st.container(border=True):
                st.markdown(f'<div class="small-label">{t("india_card_top_label")}</div>', unsafe_allow_html=True)
                col_ititle, col_ibadge = st.columns([3, 2], vertical_alignment="center")
                with col_ititle:
                    st.markdown(f'<h3 style="font-size:20px;margin:2px 0 6px;font-family:\'Space Grotesk\',sans-serif;color:#0F1B15;">{t("india_card_title")}</h3>', unsafe_allow_html=True)
                with col_ibadge:
                    st.markdown(f'<div style="text-align:right;"><span style="display:inline-block;padding:4px 10px;border-radius:999px;font-size:13px;font-weight:700;color:{band_color};background:{band_bg};">{band_label}</span></div>', unsafe_allow_html=True)
                st.markdown(
                    f'<p style="font-size:14px;color:#0F1B15;line-height:1.5;margin:6px 0 12px;">'
                    f'{t("india_band_rate_desc", rate=india_res["band_test_rate"], avg=india_res["average"])}'
                    f'</p>',
                    unsafe_allow_html=True,
                )
                st.markdown(f'**{t("india_affecting_title")}**')
                for r in india_res["reasons"]:
                    dir_text = t("india_raises_risk") if r["direction"] == "raises" else t("india_lowers_risk")
                    dir_color = "#B63E32" if r["direction"] == "raises" else "#15803D"
                    assumed_html = f' <span style="font-size:11px;color:#6B7280;background:#F3F4F6;padding:1px 6px;border-radius:4px;">{t("india_assumed_tag")}</span>' if r.get("assumed") else ""
                    st.markdown(
                        f'<div style="font-size:13px;margin:4px 0;"><span style="color:{dir_color};font-weight:600;">{dir_text}</span> — {r["label"]}{assumed_html}</div>',
                        unsafe_allow_html=True,
                    )
                if len(india_res.get("assumed", [])) >= 3:
                    st.info(t("india_fill_details_note"), icon="ℹ️")
                st.caption(t("india_card_caption"))

        # 5. US model card inside collapsed expander ("Second opinion: US lending data")
        readiness_band = result.get("readiness_band", "fair")
        if readiness_band in ("good", "strong"):
            warning_label = t("warning_few")
            warning_color = "#15803D"
        elif readiness_band in ("fair", "borderline"):
            warning_label = t("warning_some")
            warning_color = "#8A4B00"
        else:
            warning_label = t("warning_several")
            warning_color = "#8A4B00"

        with st.expander(t("us_second_opinion_expander"), expanded=False):
            st.markdown(f'<p style="font-size:13px;color:#4A554F;line-height:1.5;margin-bottom:12px;">{t("us_second_opinion_note")}</p>', unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(f'<div class="small-label">{t("us_data_label")}</div>', unsafe_allow_html=True)
                col_mtitle, col_mbadge = st.columns([3, 2], vertical_alignment="center")
                with col_mtitle:
                    st.markdown(f'<h3 style="font-size:20px;margin:2px 0 6px;font-family:\'Space Grotesk\',sans-serif;color:#0F1B15;">{t("us_model_card_title")}</h3>', unsafe_allow_html=True)
                with col_mbadge:
                    st.markdown(f'<div style="text-align:right;"><span style="display:inline-block;padding:4px 10px;border-radius:999px;font-size:13px;font-weight:700;color:{warning_color};background:#F3F4F6;">{warning_label}</span></div>', unsafe_allow_html=True)
                st.caption(t("us_model_card_caption"))
                st.markdown(f'<p style="font-size:13px;color:#4A554F;line-height:1.5;margin-bottom:12px;">{t("us_model_card_desc")}</p>', unsafe_allow_html=True)

                optional_credit_feature_map = {
                    "credit_year": "credit_history_years",
                    "open_acc": "open_acc",
                    "total_acc": "total_acc",
                    "mort_acc": "mort_acc",
                    "pub_rec": "pub_rec",
                    "bankruptcies": "pub_rec_bankruptcies",
                }
                assumed_fields = set()
                for prof_key, feat_key in optional_credit_feature_map.items():
                    if values.get(prof_key) == DEFAULT_PROFILE[prof_key] or (prof_key == "credit_year" and values.get("credit_unknown")):
                        assumed_fields.add(feat_key)

                st.markdown(f"#### {t('see_what_influenced')}")
                try:
                    contributions = explain(features)
                    reasons = explain_reasons(features, contributions, assumed_fields=assumed_fields)
                    for reason in reasons:
                        icon = "ℹ️ " if reason.get("assumed") else ("✅ " if reason["helpful"] else "⚠️ ")
                        st.markdown(icon + reason["text"])
                    if assumed_fields:
                        st.caption(t("assumed_values_note"))
                    st.markdown("---")
                    contribution_chart(contributions)
                except Exception:
                    st.warning(t("explanation_error"))

                st.markdown(f"#### {t('risk_details')}")
                risk_pct_str = format_risk_pct(result["risk"])
                st.write(f"**{t('calibrated_risk')}:** {risk_pct_str}")
                cutoff_threshold, cutoff_band = get_threshold_settings()
                st.caption(t("cutoff_caption", threshold=cutoff_threshold, band=cutoff_band, class_name=t("outcome_charged_off")))
                st.caption(t("model_warning"))

        if st.button(t("next_to_banks"), type="primary", use_container_width=True, key="btn_next_banks"):
            st.session_state.results_section = "banks"
            st.rerun()

    # ==================== Section 2: Banks ====================
    elif cur_sec == "banks":
        met_count = count_meets(bank_results)
        total_count = len(bank_results)
        st.markdown(f"### {t('bank_summary', count=met_count, total=total_count)}")
        rules_meta = load_bank_rules()
        disclaimer_text = rules_meta.get("disclaimer_hi") if st.session_state.get("language") == "हिं" and rules_meta.get("disclaimer_hi") else rules_meta.get("disclaimer", t("bank_disclaimer"))
        st.caption(disclaimer_text)

        render_lender_cards(bank_results)

        if st.button(t("next_to_fixes"), type="primary", use_container_width=True, key="btn_next_fixes"):
            st.session_state.results_section = "fixes"
            st.rerun()

    # ==================== Section 3: Fixes ====================
    elif cur_sec == "fixes":
        st.markdown(f"### {t('improve')}")
        st.caption(t("fixes_subtitle"))

        # Action formatting helper
        def _format_action_title(change: dict, current_vals: dict) -> str:
            key = change["field"]
            val = change["value"]
            if key == "revol_util":
                return t("action_card_usage_down", pct=int(round(val)))
            if key == "loan_amount":
                cur_amt = current_vals.get("loan_amount", 300000)
                return t("action_borrow_instead", val=format_inr(val), cur=format_inr(cur_amt))
            if key == "existing_emi":
                return t("action_emi_down", amount=format_inr(val))
            if key == "tenure_months":
                return t("action_extend_term", months=int(round(val)))
            return suggestion_text(change)

        # Top numbered action cards
        try:
            suggestions = find_improvements(values, max_suggestions=3)
        except Exception:
            suggestions = []

        action_items = []
        for sug in suggestions:
            changes_text = " + ".join(_format_action_title(c, values) for c in sug["changes"])
            pts = round(sug["risk_reduction"] * 100)
            action_items.append({
                "text": changes_text,
                "note": t("estimated_risk_reduction", pts=pts),
                "is_top": True,
            })

        # Merge lender qualification fixes prefixed with lender name (no duplicates)
        status_rank = {"meets": 0, "close": 1, "not_yet": 2}
        seen_texts = {item["text"].lower() for item in action_items}
        for lender in sorted(bank_results, key=lambda item: status_rank.get(item.get("status"), 3)):
            if lender.get("status") in ("close", "not_yet"):
                for fix in lender.get("fixes", []):
                    if not fix:
                        continue
                    display_fix = fix[0].lower() + fix[1:] if fix.startswith("Your ") else fix
                    labeled_fix = f"{lender['name']}: {display_fix}"
                    if labeled_fix.lower() not in seen_texts:
                        seen_texts.add(labeled_fix.lower())
                        action_items.append({
                            "text": labeled_fix,
                            "note": t("lender_criterion_note"),
                            "is_top": False,
                        })

        if action_items:
            for idx, item in enumerate(action_items, start=1):
                is_first = (idx == 1)
                bg_style = "background:#F1F9DF;border:2px solid #0F1B15;" if is_first else "background:#fff;border:1px solid #E2E5DC;"
                tag_badge = f'<span style="background:#0F1B15;color:#C6F24E;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700;">{t("top_action_badge")}</span>' if is_first else ''
                st.markdown(
                    f'<div style="{bg_style} border-radius:16px;padding:18px;margin-bottom:12px;">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">'
                    f'<span style="font-weight:800;color:#52751E;font-size:12px;letter-spacing:0.08em;">ACTION {idx:02d}</span>'
                    f'{tag_badge}'
                    f'</div>'
                    f'<p style="font-size:15px;font-weight:600;color:#0F1B15;margin:4px 0 6px;">{item["text"]}</p>'
                    f'<div style="font-size:12px;color:#4A554F;">{item["note"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info(t("no_fixes_needed"))

        if st.button(t("next_to_plan"), type="primary", use_container_width=True, key="btn_next_plan"):
            st.session_state.results_section = "plan"
            st.rerun()

    # ==================== Section 4: Plan ====================
    elif cur_sec == "plan":
        render_emi_planner(values["loan_amount"], values["rate"], values["tenure_months"])

        section_title(t("whatif"))
        signature = tuple(values.get(k) for k in ("monthly_income", "annual_income", "loan_amount", "tenure_months", "existing_emi", "revol_util"))
        if st.session_state.get("whatif_signature") != signature:
            reset_whatif()
            st.session_state.whatif_signature = signature

        m_min = min(15000, int(values.get("monthly_income", 65000)))
        m_max = max(250000, int(values.get("monthly_income", 65000)) * 2)
        l_min = max(1, min(50000, int(values["loan_amount"] * 0.5)))
        l_max = max(5000000, int(values["loan_amount"] * 1.5))
        e_min = 0
        e_max = max(100000, int(values["existing_emi"] * 2 + 1000))
        tenure_options = [12, 24, 36, 48, 60]

        st.session_state["whatif_monthly_income"] = max(m_min, min(m_max, int(st.session_state.get("whatif_monthly_income", values.get("monthly_income", 65000)))))
        st.session_state["whatif_loan"] = max(l_min, min(l_max, int(st.session_state.get("whatif_loan", values["loan_amount"]))))
        st.session_state["whatif_emi"] = max(e_min, min(e_max, int(st.session_state.get("whatif_emi", values["existing_emi"]))))
        st.session_state["whatif_util"] = max(0, min(100, int(st.session_state.get("whatif_util", values["revol_util"]))))
        if int(st.session_state.get("whatif_tenure", values["tenure_months"])) not in tenure_options:
            st.session_state["whatif_tenure"] = 36

        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                monthly_salary = st.slider(
                    t("monthly_salary") + " (₹)",
                    min_value=m_min,
                    max_value=m_max,
                    step=2500,
                    key="whatif_monthly_income",
                    format="₹%d",
                )
                annual_income_equiv = monthly_salary * 12
                st.caption(f"{format_inr(monthly_salary)} {t('per_month')} ({format_inr(annual_income_equiv)} / {t('year')})")
            with col2:
                loan = st.slider(
                    t("loan_amount") + " (₹)",
                    min_value=l_min,
                    max_value=l_max,
                    step=25000,
                    key="whatif_loan",
                    format="₹%d",
                )
                st.caption(format_inr(loan))

            col3, col4 = st.columns(2)
            with col3:
                emi_old = st.slider(
                    t("existing_emi") + " (₹)",
                    min_value=e_min,
                    max_value=e_max,
                    step=1000,
                    key="whatif_emi",
                    format="₹%d",
                )
                st.caption(format_inr(emi_old))
            with col4:
                util = st.slider(t("card_usage"), min_value=0, max_value=100, step=5, key="whatif_util")
                st.caption(f"{util}%")

            tenure = st.select_slider(
                t("slider_tenure"),
                options=tenure_options,
                format_func=lambda n: f"{n} {t('months')}",
                key="whatif_tenure",
            )

            try:
                # Map 12/24/48 to 36/60 for model predictions that accept only 36 or 60
                model_tenure = 60 if tenure >= 48 else 36
                new_values, new_result = apply_change(
                    values,
                    income=annual_income_equiv,
                    loan=loan,
                    months=model_tenure,
                    existing_emi=emi_old,
                    revol_util=util,
                )
                # Keep user-selected tenure and monthly income in values for bank check
                new_values["tenure_months"] = tenure
                new_values["monthly_income"] = monthly_salary
            except Exception:
                new_values = dict(values)
                new_values.update({
                    "monthly_income": monthly_salary,
                    "annual_income": annual_income_equiv,
                    "loan_amount": loan,
                    "tenure_months": tenure,
                    "existing_emi": emi_old,
                    "revol_util": util,
                })
                new_result = None

            new_emi = loan_summary(loan, values["rate"], tenure)["emi"]
            new_foir = foir(monthly_salary, emi_old, new_emi)

            if new_result:
                render_whatif_result(new_result, result)
                status_label = t(f"readiness_{new_result.get('readiness_band', 'fair')}")
                st.caption(f"{t('monthly_emi')}: {format_inr(new_emi)} · {t('salary_emi')}: {new_foir:.1f}% · {status_label}")

            st.button(t("reset"), on_click=reset_whatif, key="btn_reset_whatif")
            render_bank_results(new_values, compact=True)

        if st.button(t("next_to_save"), type="primary", use_container_width=True, key="btn_next_save"):
            st.session_state.results_section = "save"
            st.rerun()

    # ==================== Section 5: Save ====================
    elif cur_sec == "save":
        st.markdown(f"### {t('download')}")
        st.caption(t("save_report_caption"))

        report = build_download_report(result, summary, ratio, bank_results)

        col_dl, col_wa = st.columns(2)
        with col_dl:
            st.download_button(
                t("download"),
                report,
                file_name="kreditly-readiness-estimate.txt",
                mime="text/plain",
                use_container_width=True,
                key="btn_download_report",
            )
        with col_wa:
            band_str = t(f"readiness_{result.get('readiness_band', 'fair')}")
            wa_text = quote(t("wa_summary", band=band_str))
            st.link_button(t("whatsapp"), f"https://wa.me/?text={wa_text}", use_container_width=True)

        st.markdown("---")
        col_edit, col_restart = st.columns(2)
        with col_edit:
            if st.button(t("edit_details"), use_container_width=True, key="btn_edit_answers"):
                for k in [
                    "chip_loan_amt", "num_loan_amt", "chip_tenure", "select_purpose", "num_rate",
                    "chip_salary", "num_salary", "chip_emp", "chip_job",
                    "chip_existing_emi", "num_existing_emi", "chip_card_util", "chip_card_bill", "num_card_bill",
                    "chip_cibil", "num_credit_year", "chk_credit_unknown", "num_open_acc", "num_total_acc",
                    "num_mort_acc", "num_pub_rec", "num_bankruptcies",
                    "chip_age", "num_age", "chip_home"
                ]:
                    st.session_state.pop(k, None)
                st.session_state.view_mode = "wizard"
                st.session_state.wizard_step = 1
                st.rerun()
        with col_restart:
            if st.button(t("start_over"), use_container_width=True, key="btn_start_over"):
                for k in [
                    "chip_loan_amt", "num_loan_amt", "chip_tenure", "select_purpose", "num_rate",
                    "chip_salary", "num_salary", "chip_emp", "chip_job",
                    "chip_existing_emi", "num_existing_emi", "chip_card_util", "chip_card_bill", "num_card_bill",
                    "chip_cibil", "num_credit_year", "chk_credit_unknown", "num_open_acc", "num_total_acc",
                    "num_mort_acc", "num_pub_rec", "num_bankruptcies",
                    "chip_age", "num_age", "chip_home"
                ]:
                    st.session_state.pop(k, None)
                st.session_state.profile = dict(DEFAULT_PROFILE)
                st.session_state.pop("estimate", None)
                st.session_state.view_mode = "wizard"
                st.session_state.wizard_step = 1
                reset_whatif()
                st.rerun()

        st.info(f"🛡️ **RBI Safety Reminder:** {t('bank_footer')}")

    render_feedback("results")
    footer()
