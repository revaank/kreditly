"""Translate grouped SHAP results into readable English and Hindi facts."""
from .translations import t


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


def explain_reasons(features: dict, contributions: list | None = None):
    """Turn highest-magnitude grouped SHAP values into value-specific reasons."""
    if not contributions:
        return []
    sentences = []
    for item in sorted(contributions, key=lambda row: abs(row.get("contribution", 0)), reverse=True)[:5]:
        feature = item["feature"]
        if feature not in features:
            continue
        detail = t(f"factor_{feature}", x=_format_feature_value(feature, features[feature]))
        moved_up = float(item.get("contribution", 0)) >= 0
        sentences.append({
            "feature": feature,
            "helpful": not moved_up,
            "contribution": float(item.get("contribution", 0)),
            "text": t("model_higher" if moved_up else "model_lower", detail=detail),
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
