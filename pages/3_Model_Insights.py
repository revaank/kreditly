"""Show model results with readable feature labels and reproducibility details."""
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.bank_checker import load_bank_rules
from src.translations import EN, t
from src.ui import footer, header, page_setup, section_title

page_setup()
header("insights")
section_title(t("insights_title"))
st.warning(t("model_warning"))

ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT / "models" / "metrics.json"
IMPORTANCE_PATH = ROOT / "models" / "feature_importance.json"
def column_label(name):
    key = "feature_" + name
    if key not in EN:
        key = "column_" + name
    return t(key) if key in EN else name.replace("_", " ").title()

if not METRICS_PATH.exists() or not IMPORTANCE_PATH.exists():
    st.error(t("model_not_available"))
else:
    try:
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        importance = json.loads(IMPORTANCE_PATH.read_text(encoding="utf-8"))
        if not isinstance(metrics, dict) or not isinstance(importance, list):
            raise ValueError("Invalid metrics artifact structure")
        dataset = metrics["dataset"]
        best = metrics["best_test_tuned_threshold"]
    except Exception:
        st.error(t("insights_error"))
        footer()
        st.stop()

    st.markdown(f"**{t('selected_model_by', model=metrics['best_model'])}**")
    kpi = st.columns(4)
    for col, key, value in zip(
        kpi,
        ("metric_f1", "metric_recall", "metric_precision", "metric_auc"),
        (best["f1"], best["recall"], best["precision"], best["roc_auc"]),
    ):
        col.metric(t(key), f"{value:.3f}")
    st.caption(t("cutoff_caption", threshold=metrics["validation_tuned_threshold"], band=metrics["borderline_band"], class_name=t("outcome_charged_off")))
    calibration = metrics["calibration"]
    st.caption(t("calibration_summary", **{
        "validation_before": calibration["validation_brier_before"],
        "validation_after": calibration["validation_brier_after"],
        "test_before": calibration["test_brier_before"],
        "test_after": calibration["test_brier_after"],
    }))

    with st.expander(t("dataset_validation_context"), expanded=True):
        st.write(t("dataset_size", rows=dataset["rows"], columns=dataset["columns"]))
        st.write(t("issue_years", start=dataset["issue_year_range"][0], end=dataset["issue_year_range"][1]))
        st.write(f"**{t('observation_unit')}:** {t('observation_loan_record')}")
        st.write(f"**{t('license')}:** {t('license_unverified')}")
        target_counts = dataset["target_counts"]
        target_rows = [
            {t("target_outcome"): t("outcome_paid"), t("target_rows"): target_counts.get("Fully Paid", 0)},
            {t("target_outcome"): t("outcome_charged_off"), t("target_rows"): target_counts.get("Charged Off", 0)},
        ]
        st.dataframe(pd.DataFrame(target_rows), hide_index=True, use_container_width=True)

    with st.expander(t("reproducibility")):
        st.write(f"**{t('source_file')}:** {dataset['source_archive']}")
        st.caption(f"{t('checksum')}: {dataset['csv_sha256']}")
        missing = dataset.get("missing_values", {})
        missing_rows = [{t("column"): column_label(name), t("target_rows"): count} for name, count in missing.items()]
        if missing_rows:
            st.dataframe(pd.DataFrame(missing_rows), hide_index=True, use_container_width=True)
        st.caption(t("duplicate_rows", count=dataset.get("duplicate_full_rows", 0)))

    with st.expander(t("model_comparison"), expanded=True):
        rows = []
        for item in metrics["comparison"]:
            values = item["test_at_0_50"]
            rows.append({
                t("metric_model"): item["model"],
                t("metric_validation_auc"): item["validation_roc_auc"],
                t("metric_accuracy"): values["accuracy"],
                t("metric_test_precision"): values["precision"],
                t("metric_test_recall"): values["recall"],
                t("metric_test_f1"): values["f1"],
                t("metric_auc"): values["roc_auc"],
            })
        st.dataframe(pd.DataFrame(rows).style.format(precision=3), hide_index=True, use_container_width=True)
        st.caption(t("comparison_caption"))
        st.markdown(t("comparison_explanation"))

    with st.expander(t("test_roc_curves"), expanded=True):
        roc = go.Figure()
        for model_name, points in metrics["roc_curves"].items():
            roc.add_trace(go.Scatter(x=points["fpr"], y=points["tpr"], mode="lines", name=f"{model_name} (AUC {points['auc']:.3f})"))
        roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name=t("roc_chance"), line={"dash": "dash"}))
        roc.update_layout(xaxis_title=t("roc_fpr"), yaxis_title=t("roc_tpr"), yaxis_range=[0, 1], xaxis_range=[0, 1], height=420, margin={"t": 20}, legend={"orientation": "h", "y": -0.2})
        st.plotly_chart(roc, use_container_width=True)

    with st.expander(t("confusion_matrix"), expanded=True):
        matrix = metrics["confusion_matrix"]
        labels = [t("outcome_paid"), t("outcome_charged_off")]
        heatmap = go.Figure(go.Heatmap(
            z=matrix,
            x=[t("predicted_label", label=label) for label in labels],
            y=[t("actual_label", label=label) for label in labels],
            colorscale="Blues", text=[[f"{value:,}" for value in row] for row in matrix],
            texttemplate="%{text}", showscale=True,
        ))
        heatmap.update_layout(height=360, margin={"t": 20})
        st.plotly_chart(heatmap, use_container_width=True)
        st.caption(t("confusion_caption"))

    with st.expander(t("aggregated_shap"), expanded=True):
        ordered = sorted(importance, key=lambda item: item["mean_absolute_shap"])
        chart = go.Figure(go.Bar(
            x=[round(item["mean_absolute_shap"], 3) for item in ordered],
            y=[column_label(item["feature"]) for item in ordered],
            orientation="h", marker_color="#5b78e5", hovertemplate="%{y}: %{x:.3f}<extra></extra>",
        ))
        chart.update_layout(xaxis_title=t("shap_axis"), height=470, margin={"t": 20}, yaxis={"automargin": True})
        st.plotly_chart(chart, use_container_width=True)
        st.caption(t("shap_caption"))

    with st.expander(t("leakage_exclusions")):
        excluded = metrics.get("excluded_columns", [])
        st.dataframe(pd.DataFrame([
            {t("column"): column_label(key), t("reason"): t("reason_ex_" + key) if "reason_ex_" + key in EN else t("reason_ex_other")}
            for key in excluded
        ]), hide_index=True, use_container_width=True)

    with st.expander(t("currency_free_features")):
        st.write(f"**{t('numeric_features')}:** " + ", ".join(column_label(name) for name in metrics["numeric_features"]))
        st.write(f"**{t('categorical_features')}:** " + ", ".join(column_label(name) for name in metrics["categorical_features"]))
        st.markdown(t("currency_free_note"))

    with st.expander(t("limitations_fairness"), expanded=True):
        for limitation in dict.fromkeys(dataset.get("limitations", [])):
            if "Source URL" in limitation:
                text = t("limitation_source")
            elif "Only Fully Paid" in limitation:
                text = t("limitation_selection")
            elif "Historical U.S." in limitation:
                text = t("limitation_historical")
            elif "Random stratified" in limitation:
                text = t("limitation_random_split")
            else:
                text = limitation
            st.markdown(f"- {text}")
        st.markdown("- " + t("limitation_access") + "\n- " + t("limitation_not_decision"))

with st.expander(t("bank_sources")):
    try:
        bank_rules = load_bank_rules()
        st.caption(t("bank_sources_caption"))
        criterion_labels = {
            "employment_types_allowed": "bank_rule_employment_types_allowed", "min_age": "bank_rule_min_age",
            "max_age": "bank_rule_max_age", "min_monthly_income": "bank_rule_min_monthly_income",
            "min_current_job_years": "bank_rule_min_current_job_years", "min_cibil": "bank_rule_min_cibil",
            "max_foir": "bank_rule_max_foir", "min_loan": "bank_rule_min_loan",
            "max_loan": "bank_rule_max_loan", "max_tenure_months": "bank_rule_max_tenure_months",
            "interest_rate_from": "bank_rule_interest_rate_from",
        }
        for lender in bank_rules["lenders"]:
            st.markdown(f"**{lender['name']}**")
            seen = set()
            for key, rule in lender.items():
                if not isinstance(rule, dict) or not rule.get("source") or rule["source"] in seen:
                    continue
                seen.add(rule["source"])
                reliability = t("bank_official" if rule.get("reliability") == "official" else "bank_typical")
                label_key = criterion_labels.get(key)
                label = t(label_key) if label_key and label_key in EN else t("bank_source_field")
                st.markdown(f"- [{label} · {reliability}]({rule['source']})")
                if rule.get("needs_review"):
                    st.caption(t("source_review"))
            official_page = lender.get("official_page")
            if official_page and official_page not in seen:
                st.markdown(f"- [{t('lender_information_page')}]({official_page})")
    except Exception:
        st.info(t("bank_sources_unavailable"))

footer()
