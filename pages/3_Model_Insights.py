"""Honest placeholders for metrics until a model has been trained and evaluated."""
import json
from pathlib import Path
import streamlit as st
from src.translations import t
from src.ui import footer, header, page_setup, section_title

page_setup(); header("insights"); section_title(t("insights_title"))
st.info("TODO: replace after training. No model metrics are available in this phase.")
metrics_path=Path(__file__).resolve().parents[1]/"models"/"metrics.json"
metrics=json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else None
with st.expander("Dataset overview · TODO: replace after training",expanded=True):
    st.write(metrics.get("dataset", "Pending: verify the dataset source, license, geography, observation unit, years, definitions, missingness, duplicates and limitations before reporting." ) if metrics else "Pending verification. This phase does not inspect or load the supplied data archive.")
with st.expander("Cleaning steps · TODO: replace after training"):
    st.write("Document validation, missing values and duplicate handling after source review. Exclude int_rate, grade, sub_grade and installment from predictors to reduce target leakage.")
with st.expander("Currency-free features · TODO: replace after training"):
    st.write("Income ratios (loan_to_income, revol_bal_to_income), dti, revol_util, open_acc, total_acc, pub_rec, mort_acc, pub_rec_bankruptcies, term, purpose, emp_length, home_ownership and credit_history_years.")
with st.expander("Model comparison · TODO: replace after training"):
    if metrics and metrics.get("comparison"): st.dataframe(metrics["comparison"],use_container_width=True)
    else: st.dataframe({"Model":["Logistic Regression","Random Forest","XGBoost"],"Accuracy":["Pending","Pending","Pending"],"Precision":["Pending","Pending","Pending"],"Recall":["Pending","Pending","Pending"],"F1":["Pending","Pending","Pending"],"ROC-AUC":["Pending","Pending","Pending"]},hide_index=True,use_container_width=True)
with st.expander("Confusion matrix · TODO: replace after training"):
    st.write(metrics.get("confusion_matrix","Pending evaluation") if metrics else "Pending evaluation")
with st.expander("Feature importance · TODO: replace after training"):
    st.write(metrics.get("feature_importance","Pending evaluation") if metrics else "Pending evaluation")
with st.expander("Limitations and fairness · TODO: replace after training",expanded=True):
    st.markdown("- This is a dummy rules demo, not a trained model or lender decision.\n- Any future US training data may not represent Indian borrowers.\n- User-entered figures can be incomplete or inaccurate.\n- Credit history and access to finance reflect unequal systems and may carry bias.\n- This tool cannot guarantee approval and is not financial advice.")
footer()
