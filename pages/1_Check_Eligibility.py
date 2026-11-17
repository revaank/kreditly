from __future__ import annotations

# Five-screen guided wizard and progressive educational results.
from urllib.parse import quote
import streamlit as st

from src.bank_checker import check_all, count_meets, load_bank_rules
try:
    from src.bank_ui import aggregate_next_steps, render_bank_results, render_lender_cards
except ImportError:
    from src.bank_ui import aggregate_next_steps, render_bank_results
    STATUS_RANK = {"meets": 0, "close": 1, "not_yet": 2}
    def render_lender_cards(results: list[dict]):
        for lender in sorted(results, key=lambda item: STATUS_RANK.get(item.get("status"), 3)):
            with st.container(border=True):
                col_name, col_status = st.columns([3, 2], vertical_alignment="center")
                with col_name:
                    st.markdown(f"### {lender['name']}")
                    badge_key = "bank_type_nbfc" if lender.get("type") == "NBFC" else "bank_type_bank"
                    st.caption(f"{t(badge_key)} · {lender.get('product', '')}")
                with col_status:
                    status = lender.get("status", "meets")
                    badge_text = t("qualify_badge_meets") if status == "meets" else (t("qualify_badge_close") if status == "close" else t("qualify_badge_not_yet"))
                    st.markdown(f'<span class="bank-status {status}">{badge_text}</span>', unsafe_allow_html=True)
                fixes = lender.get("fixes", [])
                key_reason = fixes[0] if fixes else t("lender_all_met")
                st.markdown(f'<p style="font-size:14px;color:#34433A;margin:8px 0 10px;"><b>{t("key_reason")}:</b> {key_reason}</p>', unsafe_allow_html=True)
from src.counterfactual import apply_change, find_improvements
from src.explainer import explain_reasons, suggestion_text
from src.features import build_features
from src.finance import foir, format_inr, loan_summary
from src.predictor import explain, predict
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

def reset_whatif():
    p = st.session_state.get("profile", DEFAULT_PROFILE)
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

            cibil_chips = [t("excellent"), t("good"), t("average"), t("low"), t("dont_know")]
            cibil_idx = int(v.get("cibil_index", 1))
            selected_cibil = chip_selector(t("cibil"), cibil_chips, cibil_chips[cibil_idx], key="chip_cibil")
            v["cibil"] = selected_cibil
            v["cibil_index"] = cibil_chips.index(selected_cibil)
            v["cibil_unknown"] = v["cibil_index"] == 4
            st.caption(t("cibil_help"))

            with st.expander(t("credit_details_expander")):
                st.caption("Pre-filled with typical defaults. You can adjust if you know your exact numbers.")
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
                    with st.spinner(t("checking_lenders")):
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

    selected_sec_label = chip_selector("Section", sec_labels, cur_label, key="results_section_nav")
    # Sync selected section key
    for k, label in sections:
        if label == selected_sec_label:
            st.session_state.results_section = k
            cur_sec = k
            break

    # ==================== Section 1: Your Result ====================
    if cur_sec == "result":
        band = result.get("readiness_band", "fair")
        band_label = t(f"readiness_{band}")
        band_class = "risky" if band == "needs_work" else ("borderline" if band == "fair" else "")
        eyebrow_text = t("eyebrow_results") if t("eyebrow_results") != "eyebrow_results" else "Your loan readiness"
        lenders_matched_label = t("lenders_matched") if t("lenders_matched") != "lenders_matched" else "lenders matched"

        st.markdown(
            f'<div class="result-card {band_class}" style="margin-top:12px;margin-bottom:16px;">'
            f'<div class="small-label">{eyebrow_text.upper()}</div>'
            f'<h2 style="font-size:32px;margin:8px 0 12px;font-family:\'Space Grotesk\',sans-serif;color:#0F1B15;">{band_label}</h2>'
            f'<p style="font-size:16px;line-height:1.6;color:#35443A;margin-bottom:6px;">'
            f'Your estimated monthly EMI would be <b>{format_inr(summary["emi"])}</b>, which takes about <b>{ratio:.1f}%</b> of your monthly take-home income.'
            f'</p>'
            f'<p style="font-size:15px;line-height:1.6;color:#4A554F;margin-bottom:0;">'
            f'Based on published criteria, you qualify for <b>{count_meets(bank_results)} of {len(bank_results)}</b> lenders.'
            f'</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # 3 stat cards
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
                f'<strong style="font-size:22px;color:#0F1B15;font-family:\'Space Grotesk\',sans-serif;">{count_meets(bank_results)} / {len(bank_results)}</strong>'
                f'<div style="font-size:12px;color:#4A554F;">{lenders_matched_label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="panel" style="text-align:center;padding:16px 12px;">'
                f'<div class="small-label">{t("total_interest")}</div>'
                f'<strong style="font-size:22px;color:#0F1B15;font-family:\'Space Grotesk\',sans-serif;">{format_inr(summary["interest"])}</strong>'
                f'<div style="font-size:12px;color:#4A554F;">over {values["tenure_months"]} months</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # SHAP and reasons expander
        with st.expander(t("see_what_influenced")):
            try:
                contributions = explain(features)
                for reason in explain_reasons(features, contributions):
                    st.markdown(("✅ " if reason["helpful"] else "⚠️ ") + reason["text"])
                st.markdown("---")
                contribution_chart(contributions)
            except Exception:
                st.warning(t("explanation_error"))

        # Risk details expander
        with st.expander(t("risk_details")):
            risk_pct_str = format_risk_pct(result["risk"])
            st.write(f"**{t('calibrated_risk')}:** {risk_pct_str}")
            st.caption(t("cutoff_caption", threshold=0.324, band=0.10, class_name=t("outcome_charged_off")))
            st.caption(t("model_warning"))

        st.caption(t("dummy_notice"))

        if st.button(t("next_to_banks"), type="primary", use_container_width=True, key="btn_next_banks"):
            st.session_state.results_section = "banks"
            st.rerun()

    # ==================== Section 2: Banks ====================
    elif cur_sec == "banks":
        met_count = count_meets(bank_results)
        total_count = len(bank_results)
        st.markdown(f"### {t('bank_summary', count=met_count, total=total_count)}")
        st.caption(t("bank_disclaimer"))

        render_lender_cards(bank_results)

        if st.button(t("next_to_fixes"), type="primary", use_container_width=True, key="btn_next_fixes"):
            st.session_state.results_section = "fixes"
            st.rerun()

    # ==================== Section 3: Fixes ====================
    elif cur_sec == "fixes":
        st.markdown(f"### {t('improve')}")
        st.caption("Here are practical adjustments to improve affordability and lender matching.")

        # Action formatting helper
        def _format_action_title(change: dict, current_vals: dict) -> str:
            key = change["field"]
            val = change["value"]
            lang = st.session_state.get("language", "EN")
            is_hi = lang == "हिं"
            if key == "revol_util":
                pct = int(round(val))
                if is_hi:
                    return f"कार्ड उपयोग {pct}% से कम लाएं" if pct <= 10 else f"कार्ड उपयोग घटाकर {pct}% करें"
                return f"Bring your card usage under {pct}%" if pct <= 10 else f"Bring your card usage down to {pct}%"
            elif key == "loan_amount":
                cur_amt = current_vals.get("loan_amount", 300000)
                if is_hi:
                    return f"{format_inr(cur_amt)} के बजाय {format_inr(val)} का ऋण लें"
                return f"Borrow {format_inr(val)} instead of {format_inr(cur_amt)}"
            elif key == "existing_emi":
                if is_hi:
                    return f"मौजूदा किस्तों को घटाकर लगभग {format_inr(val)} करें"
                return f"Reduce existing EMIs to about {format_inr(val)}"
            elif key == "tenure_months":
                t_m = int(round(val))
                if is_hi:
                    return f"ऋण अवधि बढ़ाकर {t_m} महीने करें"
                return f"Extend loan repayment term to {t_m} months"
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
            reduction_text = f"अनुमानित जोखिम में कमी: ~{pts} अंक" if st.session_state.get("language") == "हिं" else f"Estimated risk reduction: ~{pts} points"
            action_items.append({
                "text": changes_text,
                "note": reduction_text,
                "is_top": True,
            })

        # Merge lender qualification fixes (no duplicates)
        overall_fixes = aggregate_next_steps(bank_results)
        seen_texts = {item["text"].lower() for item in action_items}
        for fix in overall_fixes:
            if fix and fix.lower() not in seen_texts:
                seen_texts.add(fix.lower())
                lender_note = "ऋणदाता पात्रता आवश्यकता" if st.session_state.get("language") == "हिं" else "Lender qualification criterion"
                action_items.append({
                    "text": fix,
                    "note": lender_note,
                    "is_top": False,
                })

        if action_items:
            for idx, item in enumerate(action_items, start=1):
                is_first = (idx == 1)
                bg_style = "background:#F1F9DF;border:2px solid #0F1B15;" if is_first else "background:#fff;border:1px solid #E2E5DC;"
                tag_badge = '<span style="background:#0F1B15;color:#C6F24E;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700;">Top action</span>' if is_first else ''
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
            st.info("Your profile already meets standard readiness criteria.")

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

        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                cur_m_inc = int(values.get("monthly_income", 65000))
                monthly_salary = st.slider(
                    t("monthly_salary") + " (₹)",
                    min_value=15000,
                    max_value=250000,
                    value=cur_m_inc,
                    step=2500,
                    key="whatif_monthly_income",
                    format="₹%d",
                )
                annual_income_equiv = monthly_salary * 12
                st.caption(f"{format_inr(monthly_salary)} / month ({format_inr(annual_income_equiv)} / year)")
            with col2:
                loan = st.slider(
                    t("loan_amount") + " (₹)",
                    min_value=max(1, min(50000, int(values["loan_amount"] * 0.5))),
                    max_value=max(5000000, int(values["loan_amount"] * 1.5)),
                    value=int(values["loan_amount"]),
                    step=25000,
                    key="whatif_loan",
                    format="₹%d",
                )
                st.caption(format_inr(loan))

            col3, col4 = st.columns(2)
            with col3:
                emi_old = st.slider(
                    t("existing_emi") + " (₹)",
                    0,
                    max(100000, int(values["existing_emi"] * 2 + 1000)),
                    int(values["existing_emi"]),
                    step=1000,
                    key="whatif_emi",
                    format="₹%d",
                )
                st.caption(format_inr(emi_old))
            with col4:
                util = st.slider(t("card_usage"), 0, 100, int(values["revol_util"]), step=5, key="whatif_util")
                st.caption(f"{util}%")

            tenure = st.select_slider(
                t("slider_tenure"),
                options=[12, 24, 36, 48, 60],
                value=int(values["tenure_months"]),
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
        st.caption("Save a copy of your educational readiness report or share it.")

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

    footer()
