"""Illustrative examples stored separately from any research dataset."""
import json
from pathlib import Path
import streamlit as st
from json import JSONDecodeError
from src.features import build_features
from src.predictor import predict, explain
from src.explainer import explain_reasons, suggestion_text
from src.finance import loan_summary, foir, format_inr
from src.counterfactual import apply_change, find_improvements
from src.translations import t
from src.ui import contribution_chart, footer, header, page_setup, result_card, section_title

def reset_sample(case_id):
    """Restore that example's original values in its what-if controls."""
    for name in ("income","loan","emi","util","tenure"):
        st.session_state.pop(f"sample_{name}_{case_id}",None)

page_setup(); header("samples"); section_title(t("cases_title")); st.info(t("model_warning"))
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
                    st.markdown(f'<div class="case-card"><div class="small-label">{t("sample_only")}</div><h3>{t(case["title_key"])}</h3></div>',unsafe_allow_html=True)
                    with st.expander(t("view_explanation")):
                        details=case["values"]
                        try:
                            features=build_features(details); result=predict(features)
                        except Exception:
                            st.warning(t("model_error")); continue
                        result_card(result)
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
                        new_label=t({"STRONG":"strong","BORDERLINE":"borderline","RISKY":"risky"}[new_result["label"]])
                        st.metric(t("simulator_result"),f'{new_result["risk"]:.0%} · {new_label}',delta=f'{new_result["risk"]-result["risk"]:+.0%} {t("vs_original")}',delta_color="inverse")
                        st.caption(f'{t("monthly_emi")}: {format_inr(monthly)} · {t("salary_emi")}: {salary_share:.1f}%')
                        st.button(t("reset"),key=f"reset_{case['id']}",on_click=reset_sample,args=(case["id"],))
                        st.caption(t("dummy_notice"))
footer()
