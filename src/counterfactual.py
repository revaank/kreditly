from __future__ import annotations

"""Run fast what-if changes and search for small changes reaching STRONG."""
from copy import deepcopy

from .features import build_features
from .predictor import predict, predict_many


def apply_change(values: dict, *, income=None, loan=None, months=None, existing_emi=None, revol_util=None):
    """Apply one simulator state and call the same trained model as the result card."""
    changed = deepcopy(values)
    for key, value in (("annual_income", income), ("loan_amount", loan),
                       ("tenure_months", months), ("existing_emi", existing_emi),
                       ("revol_util", revol_util)):
        if value is not None:
            changed[key] = value
    return changed, predict(build_features(changed))


def _unique(values):
    return list(dict.fromkeys(values))


def find_improvements(values: dict, max_suggestions=3):
    """Rank helpful single-lever changes by calibrated risk reduction."""
    baseline = predict(build_features(values))
    loan = max(1.0, float(values.get("loan_amount", 0)))
    emi = max(0.0, float(values.get("existing_emi", 0)))
    usage = min(100.0, max(0.0, float(values.get("revol_util", 0))))
    current_term = int(values.get("tenure_months", 36))
    choices = {
        "loan_amount": _unique([round(loan * ratio / 1000) * 1000 for ratio in (0.95, 0.9, 0.8, 0.7, 0.6, 0.5)]),
        "existing_emi": _unique([round(emi * ratio / 1000) * 1000 for ratio in (0.9, 0.75, 0.5, 0.25, 0)]),
        "revol_util": _unique([max(0, usage - amount) for amount in (5, 10, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100)]),
        "tenure_months": [months for months in (48, 60) if months > current_term],
    }
    current = {"loan_amount": loan, "existing_emi": emi, "revol_util": usage, "tenure_months": current_term}
    profiles, candidates = [], []
    for field, options in choices.items():
        for value in options:
            if field == "tenure_months":
                if value <= current_term:
                    continue
            elif float(value) >= float(current[field]):
                continue
            candidate = deepcopy(values)
            candidate[field] = value
            profiles.append(build_features(candidate))
            candidates.append((field, value))

    predictions = predict_many(profiles)
    best_by_lever = {}
    for (field, value), prediction in zip(candidates, predictions):
        reduction = float(baseline["risk"]) - float(prediction["risk"])
        if reduction <= 1e-6:
            continue
        if field not in best_by_lever or reduction > best_by_lever[field]["risk_reduction"]:
            best_by_lever[field] = {
                "field": field, "value": value, "risk": prediction["risk"],
                "label": prediction["label"], "risk_reduction": reduction,
                "changes": [{"field": field, "value": value}],
            }
    return sorted(best_by_lever.values(), key=lambda item: item["risk_reduction"], reverse=True)[:max_suggestions]
