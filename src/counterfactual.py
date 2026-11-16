"""Run fast what-if changes and search for small changes reaching STRONG."""
from copy import deepcopy
from itertools import product

import streamlit as st

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


@st.cache_data(show_spinner=False)
def find_improvements(values: dict, max_suggestions=3):
    """Search combinations of modest loan, EMI, term, and card-use changes.

    Candidate probabilities are evaluated in one batch. Suggestions are sorted
    by the number and relative size of changes; only STRONG outcomes are shown.
    """
    baseline = predict(build_features(values))
    if baseline["label"] == "STRONG":
        return []

    loan = max(1.0, float(values.get("loan_amount", 0)))
    emi = max(0.0, float(values.get("existing_emi", 0)))
    usage = min(100.0, max(0.0, float(values.get("revol_util", 0))))
    current_term = int(values.get("tenure_months", 36))

    loan_step = max(5000, int(round(loan * 0.05 / 1000) * 1000))
    minimum_loan = max(1000, int(round(loan * 0.10 / 1000) * 1000))
    loan_values = [loan] + list(range(int(loan - loan_step), minimum_loan - 1, -loan_step)) + [minimum_loan]
    emi_values = [emi] + [round(emi * fraction / 1000) * 1000 for fraction in (80, 60, 40, 20)]
    usage_values = [
        usage, max(0, usage - 10), max(0, usage - 20), max(0, usage - 30),
        min(usage, 60), min(usage, 50), min(usage, 40), min(usage, 30),
        min(usage, 20), min(usage, 10), 0,
    ]
    term_values = [current_term, 36, 60]
    choices = [
        ("loan_amount", _unique(loan_values)),
        ("existing_emi", _unique(emi_values)),
        ("revol_util", _unique(usage_values)),
        ("tenure_months", _unique(term_values)),
    ]

    profiles, changes, costs, seen = [], [], [], set()
    for values_tuple in product(*(items for _, items in choices)):
        candidate = deepcopy(values)
        changed_fields = []
        cost = 0.0
        for (field, _), value in zip(choices, values_tuple):
            current = {
                "loan_amount": loan,
                "existing_emi": emi,
                "revol_util": usage,
                "tenure_months": current_term,
            }[field]
            if float(value) == float(current):
                continue
            candidate[field] = value
            changed_fields.append({"field": field, "value": value})
            if field == "loan_amount":
                cost += max(0.0, (loan - float(value)) / loan)
            elif field == "existing_emi":
                cost += 0.7 * (emi - float(value)) / max(emi, 1)
            elif field == "revol_util":
                cost += 0.4 * (usage - float(value)) / 100
            else:
                cost += 0.1
        if not changed_fields:
            continue
        signature = tuple((change["field"], round(float(change["value"]), 2)) for change in changed_fields)
        if signature in seen:
            continue
        seen.add(signature)
        cost += 0.25 * len(changed_fields)
        profiles.append(build_features(candidate))
        changes.append(changed_fields)
        costs.append(cost)

    predictions = predict_many(profiles)
    eligible = [
        {"changes": change_set, "field": change_set[0]["field"], "value": change_set[0]["value"],
         "label": prediction["label"], "risk": prediction["risk"], "cost": cost}
        for change_set, prediction, cost in zip(changes, predictions, costs)
        if prediction["label"] == "STRONG"
    ]
    eligible.sort(key=lambda item: (item["cost"], len(item["changes"]), item["risk"]))

    result, selected_signatures = [], set()
    for item in eligible:
        signature = tuple((change["field"], round(float(change["value"]), 2)) for change in item["changes"])
        if signature in selected_signatures:
            continue
        selected_signatures.add(signature)
        result.append(item)
        if len(result) == max_suggestions:
            break
    return result
