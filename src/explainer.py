from __future__ import annotations

"""Translate grouped SHAP results into readable English and Hindi facts."""
from .translations import t


EXPLANATION_TEMPLATES = {
    "loan_to_income": {"higher": "explain_loan_to_income_higher", "lower": "explain_loan_to_income_lower"},
    "revol_bal_to_income": {"higher": "explain_revol_bal_to_income_higher", "lower": "explain_revol_bal_to_income_lower"},
    "dti": {"higher": "explain_dti_higher", "lower": "explain_dti_lower"},
    "revol_util": {"higher": "explain_revol_util_higher", "lower": "explain_revol_util_lower"},
    "open_acc": {"higher": "explain_open_acc_higher", "lower": "explain_open_acc_lower"},
    "total_acc": {"higher": "explain_total_acc_higher", "lower": "explain_total_acc_lower"},
    "pub_rec": {"higher": "explain_pub_rec_higher", "lower": "explain_pub_rec_lower"},
    "mort_acc": {"higher": "explain_mort_acc_higher", "lower": "explain_mort_acc_lower"},
    "pub_rec_bankruptcies": {"higher": "explain_bankruptcies_higher", "lower": "explain_bankruptcies_lower"},
    "term": {"higher": "explain_term_higher", "lower": "explain_term_lower"},
    "purpose": {"higher": "explain_purpose_higher", "lower": "explain_purpose_lower"},
    "emp_length": {"higher": "explain_emp_length_higher", "lower": "explain_emp_length_lower"},
    "home_ownership": {"higher": "explain_home_higher", "lower": "explain_home_lower"},
    "credit_history_years": {"higher": "explain_history_higher", "lower": "explain_history_lower"},
}


def _format_feature_value(key, value):
    if key == "loan_to_income":
        ratio = float(value)
        return f"{ratio:.2f}" if abs(ratio) < 0.1 else f"{ratio:.1f}"
    if key == "revol_bal_to_income":
        return f"{float(value) * 100:.1f}"
    if key in {"dti", "revol_util"}:
        return f"{float(value):.0f}"
    if key == "purpose":
        purpose_labels = {
            "debt_consolidation": "p_debt", "credit_card": "p_card",
            "home_improvement": "p_home", "major_purchase": "p_purchase",
            "small_business": "p_business", "car": "p_vehicle",
            "medical": "p_medical", "other": "p_other",
        }
        return t(purpose_labels.get(str(value), "p_other"))
    if key == "home_ownership":
        home_labels = {"RENT": "rented", "OWN": "own", "MORTGAGE": "own_loan", "OTHER": "home_other"}
        return t(home_labels.get(str(value), "home"))
    try:
        return f"{float(value):g}"
    except (TypeError, ValueError):
        return t("dont_know")


ASSUMED_FEATURE_LABELS = {
    "open_acc": "open_accounts",
    "total_acc": "total_accounts",
    "mort_acc": "mort_accounts",
    "pub_rec": "public_records",
    "pub_rec_bankruptcies": "bankruptcies",
    "credit_history_years": "feature_history",
}


def explain_reasons(features: dict, contributions: list | None = None, assumed_fields: set | None = None):
    """Turn highest-magnitude grouped SHAP values into value-specific reasons."""
    if not contributions:
        return []
    assumed = set(assumed_fields or ())
    sentences = []
    for item in sorted(contributions, key=lambda row: abs(row.get("contribution", 0)), reverse=True)[:5]:
        feature = item["feature"]
        if feature not in features:
            continue
        detail = _format_feature_value(feature, features[feature])
        moved_up = float(item.get("contribution", 0)) >= 0
        direction = "higher" if moved_up else "lower"
        is_assumed = feature in assumed
        if is_assumed:
            feature_label = t(ASSUMED_FEATURE_LABELS.get(feature, feature))
            text = t("explain_assumed", feature=feature_label, x=detail)
        else:
            template = EXPLANATION_TEMPLATES.get(feature, {}).get(direction, "explain_generic_" + direction)
            text = t(template, x=detail)
        sentences.append({
            "feature": feature,
            "helpful": not moved_up,
            "assumed": is_assumed,
            "contribution": float(item.get("contribution", 0)),
            "text": text,
        })
    return sentences


def suggestion_text(suggestion):
    """Render a counterfactual action using exact profile values."""
    key = suggestion["field"]
    value = suggestion["value"]
    if key == "loan_amount":
        return t("suggest_loan", x=f"{value:,.0f}")
    if key == "existing_emi":
        return t("suggest_emi", x=f"{value:,.0f}")
    if key == "revol_util":
        return t("suggest_util", x=f"{value:.0f}")
    if key == "tenure_months":
        return t("suggest_term", x=f"{value:.0f}")
    return ""
