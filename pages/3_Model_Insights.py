"""Show actual model results and clear limits of the historical training data."""
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.bank_checker import load_bank_rules
from src.translations import t
from src.ui import footer, header, page_setup, section_title


page_setup()
header("insights")
section_title(t("insights_title"))
st.warning(t("model_warning"))

root = Path(__file__).resolve().parents[1]
metrics_path = root / "models" / "metrics.json"
importance_path = root / "models" / "feature_importance.json"

if not metrics_path.exists() or not importance_path.exists():
    st.error(t("model_not_available"))
else:
    try:
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        importance = json.loads(importance_path.read_text(encoding="utf-8"))
        if not isinstance(metrics, dict) or not isinstance(importance, list):
            raise ValueError("Invalid metrics artifact structure")
    except Exception:
        st.error(t("insights_error"))
        footer()
        st.stop()
    dataset = metrics["dataset"]
    best = metrics["best_test_tuned_threshold"]
    threshold = metrics["validation_tuned_threshold"]
    band = metrics["borderline_band"]

    st.markdown(f"**Selected model:** {metrics['best_model']} · chosen by validation ROC-AUC")
    kpi = st.columns(4)
    kpi[0].metric("Test risky-class F1", f"{best['f1']:.3f}")
    kpi[1].metric("Test recall", f"{best['recall']:.3f}")
    kpi[2].metric("Test precision", f"{best['precision']:.3f}")
    kpi[3].metric("Test ROC-AUC", f"{best['roc_auc']:.3f}")
    st.caption(
        f"The score cutoff {threshold:.3f} was selected on validation data to maximize F1 for Charged Off. "
        f"The website labels estimates within ±{band:.2f} of that cutoff as BORDERLINE."
    )

    with st.expander("Dataset and validation context", expanded=True):
        st.write(
            f"**Source file:** {dataset['source_archive']}  \n"
            f"**Rows and columns:** {dataset['rows']:,} × {dataset['columns']}  ·  "
            f"**Loan issue years:** {dataset['issue_year_range'][0]}–{dataset['issue_year_range'][1]}  ·  "
            f"**Observation unit:** {dataset['observation_unit']}"
        )
        st.write(f"**License:** {dataset['license']}")
        st.write(f"**Target counts:** {dataset['target_counts']}")
        st.write(f"**Nonzero missing-value counts:** {dataset['missing_values']}")
        st.write(f"**Duplicate full rows:** {dataset['duplicate_full_rows']:,}")
        st.caption(f"Dataset checksum (SHA-256): {dataset['csv_sha256']}")

    with st.expander("Model comparison", expanded=True):
        rows = []
        for item in metrics["comparison"]:
            values = item["test_at_0_50"]
            rows.append({
                "Model": item["model"],
                "Validation ROC-AUC (selection)": item["validation_roc_auc"],
                "Test accuracy (0.50)": values["accuracy"],
                "Test precision (risky, 0.50)": values["precision"],
                "Test recall (risky, 0.50)": values["recall"],
                "Test F1 (risky, 0.50)": values["f1"],
                "Test ROC-AUC": values["roc_auc"],
            })
        st.dataframe(pd.DataFrame(rows).style.format(precision=3), hide_index=True, use_container_width=True)
        st.caption(
            "The comparison table uses the standard 0.50 cutoff for each model. "
            "The selected model's KPI and confusion matrix use its separate validation-tuned cutoff."
        )
        st.markdown(
            "Accuracy can hide missed defaults when outcomes are imbalanced. Precision, recall, and F1 "
            "describe charged-off detection; ROC-AUC compares ranking across probability cutoffs."
        )

    with st.expander("Test ROC curves", expanded=True):
        roc = go.Figure()
        for model_name, points in metrics["roc_curves"].items():
            roc.add_trace(go.Scatter(
                x=points["fpr"], y=points["tpr"], mode="lines",
                name=f"{model_name} (AUC {points['auc']:.3f})",
            ))
        roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Chance", line={"dash": "dash"}))
        roc.update_layout(
            xaxis_title="False positive rate", yaxis_title="True positive rate",
            yaxis_range=[0, 1], xaxis_range=[0, 1], height=420, margin={"t": 20},
            legend={"orientation": "h", "y": -0.2},
        )
        st.plotly_chart(roc, use_container_width=True)

    with st.expander("Selected model test confusion matrix", expanded=True):
        matrix = metrics["confusion_matrix"]
        labels = metrics["confusion_matrix_labels"]
        heatmap = go.Figure(go.Heatmap(
            z=matrix, x=[f"Predicted {label}" for label in labels],
            y=[f"Actual {label}" for label in labels], colorscale="Blues",
            text=[[f"{value:,}" for value in row] for row in matrix],
            texttemplate="%{text}", showscale=True,
        ))
        heatmap.update_layout(height=360, margin={"t": 20})
        st.plotly_chart(heatmap, use_container_width=True)
        st.caption("Rows are actual labels; columns are predicted labels. Positive/risky class is Charged Off.")

    with st.expander("Aggregated SHAP feature importance", expanded=True):
        ordered = sorted(importance, key=lambda item: item["mean_absolute_shap"])
        chart = go.Figure(go.Bar(
            x=[item["mean_absolute_shap"] for item in ordered],
            y=[item["feature"] for item in ordered], orientation="h", marker_color="#5b78e5",
        ))
        chart.update_layout(
            xaxis_title="Mean absolute grouped SHAP value", height=470,
            margin={"t": 20}, yaxis={"automargin": True},
        )
        st.plotly_chart(chart, use_container_width=True)
        st.caption(
            "One-hot contributions are summed back to their original feature names. "
            "Importance shows model association strength; it does not show causation or inherently mean higher risk."
        )

    with st.expander("Leakage exclusions"):
        reasons = {
            "int_rate": "Lender pricing is assigned after risk review.",
            "grade": "Lender risk grade reflects the underwriting decision.",
            "sub_grade": "Detailed lender risk grade reflects the underwriting decision.",
            "installment": "Payment amount is determined from loan pricing and terms.",
            "emp_title": "Free text with high cardinality and potential identity/proxy information.",
            "title": "Free text with high cardinality and potential identity information.",
            "address": "Location text can identify people or act as a social proxy.",
            "initial_list_status": "Platform/servicing detail outside the requested profile.",
            "verification_status": "Platform-specific verification status, excluded from the requested features.",
            "application_type": "Platform product/process field outside the requested features.",
        }
        st.dataframe(pd.DataFrame(
            [{"Column": key, "Reason": reasons[key]} for key in metrics["excluded_columns"]]
        ), hide_index=True, use_container_width=True)

    with st.expander("Currency-free features"):
        st.write("**Numeric:** " + ", ".join(metrics["numeric_features"]))
        st.write("**Categorical:** " + ", ".join(metrics["categorical_features"]))
        st.markdown(
            "Loan amount and annual income become loan-to-income; revolving balance and income become "
            "revolving-balance-to-income. Raw dollar or rupee amounts are never model columns. Term is in months. "
            "The app's available EMI information is an approximation of the dataset's reported DTI."
        )

    with st.expander("Limitations and fairness", expanded=True):
        for limitation in dataset["limitations"]:
            st.markdown(f"- {limitation}")
        st.markdown(
            "- The training data contain only resolved Fully Paid/Charged Off outcomes, which can create selection bias.\n"
            "- Random splitting is reproducible but does not test later-time performance.\n"
            "- Credit-history access and financial access can reflect unequal systems.\n"
            "- This educational tool cannot guarantee an outcome or replace a lender's review."
        )

with st.expander("Data sources · bank eligibility criteria"):
    try:
        bank_rules = load_bank_rules()
        st.caption("Source URLs and reliability labels are reproduced from the supplied bank_rules.json.")
        labels = {
            "employment_types_allowed": "Employment type", "min_age": "Minimum age",
            "max_age": "Maximum age", "min_monthly_income": "Minimum monthly income",
            "min_current_job_years": "Current job experience", "min_cibil": "Minimum CIBIL",
            "max_foir": "Maximum FOIR", "min_loan": "Minimum loan",
            "max_loan": "Maximum loan", "max_tenure_months": "Maximum tenure",
            "interest_rate_from": "Starting interest rate",
        }
        for lender in bank_rules["lenders"]:
            st.markdown(f"**{lender['name']}**")
            seen = set()
            for key, rule in lender.items():
                if not isinstance(rule, dict) or not rule.get("source") or rule["source"] in seen:
                    continue
                seen.add(rule["source"])
                reliability = rule.get("reliability") or "source page"
                label = labels.get(key, key.replace("_", " ").title())
                st.markdown(f"- [{label} · {reliability}]({rule['source']})")
            official_page = lender.get("official_page")
            if official_page and official_page not in seen:
                st.markdown(f"- [Lender information page]({official_page})")
    except Exception:
        st.info("Bank rule source URLs are temporarily unavailable.")

footer()
