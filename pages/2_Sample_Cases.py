"""Illustrative examples stored separately from any research dataset."""
import json
from pathlib import Path
import streamlit as st
from json import JSONDecodeError
from src.features import build_features
from src.india_model import assess
from src.predictor import predict, explain
from src.explainer import explain_reasons, suggestion_text
from src.finance import loan_summary, foir, format_inr
from src.counterfactual import apply_change, find_improvements
from src.profiles import DEFAULT_PROFILE, map_cibil_to_index
from src.translations import t
from src.ui import contribution_chart, footer, header, page_setup, render_whatif_result, result_card, section_title

def reset_sample(case_id):
    """Restore that example's original values in its what-if controls."""
    for name in ("income","loan","emi","util","tenure"):
        st.session_state.pop(f"sample_{name}_{case_id}",None)

page_setup(); header("samples"); section_title(t("cases_title")); st.info(t("sample_banner_note"))
try:
    cases=json.loads((Path(__file__).resolve().parents[1]/"src"/"sample_cases.json").read_text(encoding="utf-8"))
    if not isinstance(cases,list) or not cases or any(
        not isinstance(case,dict) or not {"group","values","title_key","id"}.issubset(case)
        for case in cases
    ):
        raise ValueError("empty sample list")
except (OSError,JSONDecodeError,TypeError,ValueError):
    st.error(t("sample_error")); footer(); st.stop()
for tab, group in zip(st.tabs([t("strong_tab"),t("risky_tab")]),["strong","risky"]):
    with tab:
        rows=[case for case in cases if case["group"]==group]
        for start in range(0,len(rows),2):
            cols=st.columns(2)
            for col,case in zip(cols,rows[start:start+2]):
                with col:
                    details = case["values"]
                    full_profile = {**DEFAULT_PROFILE, **details}
                    full_profile["cibil_index"] = map_cibil_to_index(full_profile.get("cibil"))
                    band_map = {0: "excellent", 1: "good", 2: "average", 3: "low", 4: "no_history", 5: "dont_know"}
                    india_p = {
                        "cibil_band": band_map.get(full_profile["cibil_index"], "dont_know"),
                        "age": full_profile.get("age", 30),
                        "employment": "self_employed" if full_profile.get("employment") == "Self-employed" else "salaried",
                        "credit_history_years": max(0, 2026 - full_profile.get("credit_year", 2015)) if full_profile.get("credit_year") else None,
                        "active_loans": full_profile.get("open_acc"),
                        "overdue_loans": full_profile.get("overdue_loans"),
                        "missed_emi_last_6m": full_profile.get("missed_emi_last_6m"),
                        "new_loans_last_6m": full_profile.get("new_loans_last_6m"),
                        "loan_enquiries": full_profile.get("loan_enquiries"),
                        "existing_emi": full_profile.get("existing_emi"),
                    }
                    try:
                        ia = assess(india_p)
                        band = ia["band"]
                        band_label = t(f"india_band_{band}")
                        band_bg = {"lower": "#ECFCCB", "typical": "#FEF3C7", "higher": "#FEE2E2"}.get(band, "#FEF3C7")
                        band_color = {"lower": "#365314", "typical": "#854D0E", "higher": "#991B1B"}.get(band, "#854D0E")
                        band_pill = f'<span style="display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700;background:{band_bg};color:{band_color};">{band_label}</span>'
                    except Exception:
                        band_pill = ""

                    with st.container(border=True):
                        st.markdown(
                            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
                            f'<div class="small-label">{t("sample_only")}</div>'
                            f'{band_pill}'
                            f'</div>'
                            f'<h3 style="margin:4px 0 14px;">{t(case["title_key"])}</h3>',
                            unsafe_allow_html=True,
                        )
                        if st.button(t("btn_try_profile"), key=f"btn_try_{case['id']}", type="primary", use_container_width=True):
                            st.session_state.profile = dict(full_profile)
                            st.session_state.pop("estimate", None)
                            st.session_state.view_mode = "wizard"
                            st.session_state.wizard_step = 1
                            for k, v in [
                                ("whatif_income", int(full_profile.get("annual_income", 800000))),
                                ("whatif_loan", int(full_profile.get("loan_amount", 300000))),
                                ("whatif_emi", int(full_profile.get("existing_emi", 5000))),
                                ("whatif_util", int(full_profile.get("revol_util", 30))),
                                ("whatif_tenure", int(full_profile.get("tenure_months", 36))),
                            ]:
                                st.session_state[k] = v
                            st.switch_page("pages/1_Check_Eligibility.py")

                    with st.expander(t("view_explanation")):
                        try:
                            features=build_features(details); result=predict(features)
                        except Exception:
                            st.warning(t("model_error")); continue
                        result_card(result,show_risk_details=False)
                        try:
                            contributions=explain(features)
                        except Exception:
                            contributions=[]; st.warning(t("explanation_error"))
                        for reason in explain_reasons(features,contributions): st.markdown(("✅ " if reason["helpful"] else "⚠️ ")+reason["text"])
                        contribution_chart(contributions,height=260)
                        if result["label"]!="STRONG":
                            section_title(t("improve"))
                            try:
                                suggestions=find_improvements(details)
                                if suggestions:
                                    for suggestion in suggestions:
                                        st.markdown("• "+" + ".join(suggestion_text(change) for change in suggestion["changes"]))
                                else:
                                    st.caption(t("no_counterfactual"))
                            except Exception:
                                st.caption(t("model_error"))
                            st.caption(t("recommendation_note"))
                        st.markdown(f"**{t('whatif')}**")
                        income=st.slider(t("income")+" (₹)",min_value=max(1,int(details["annual_income"]*.5)),max_value=max(2000000,int(details["annual_income"]*1.5)),value=int(details["annual_income"]),step=25000,key=f"sample_income_{case['id']}",format="₹%d")
                        st.caption(format_inr(income))
                        loan=st.slider(t("loan_amount")+" (₹)",min_value=max(1,min(50000,int(details["loan_amount"]*.5))),max_value=max(5000000,int(details["loan_amount"]*1.5)),value=int(details["loan_amount"]),step=25000,key=f"sample_loan_{case['id']}",format="₹%d")
                        st.caption(format_inr(loan))
                        emi_existing=st.slider(t("existing_emi")+" (₹)",min_value=0,max_value=max(100000,int(details["existing_emi"]*2+1000)),value=int(details["existing_emi"]),step=1000,key=f"sample_emi_{case['id']}",format="₹%d")
                        st.caption(format_inr(emi_existing))
                        util=st.slider(t("card_usage"),min_value=0,max_value=100,value=int(details["revol_util"]),step=5,key=f"sample_util_{case['id']}")
                        st.caption(f"{util}%")
                        tenure=st.select_slider(t("slider_tenure"),options=[36,60],value=int(details["tenure_months"]),format_func=lambda n:f"{n} {t('months')}",key=f"sample_tenure_{case['id']}")
                        try:
                            changed,new_result=apply_change(details,income=income,loan=loan,months=tenure,existing_emi=emi_existing,revol_util=util)
                        except Exception:
                            st.warning(t("model_error")); continue
                        monthly=loan_summary(loan,details["rate"],tenure)["emi"]
                        salary_share=foir(income/12,emi_existing,monthly)
                        render_whatif_result(new_result,result,show_risk_details=False)
                        st.caption(f'{t("monthly_emi")}: {format_inr(monthly)} · {t("salary_emi")}: {salary_share:.1f}%')
                        st.button(t("reset"),key=f"reset_{case['id']}",on_click=reset_sample,args=(case["id"],))
                        st.caption(t("dummy_notice"))
footer()
