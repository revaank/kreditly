"""Default profile definitions and sample mapping helpers."""
from __future__ import annotations

DEFAULT_PROFILE = {
    "age": 30,
    "employment": "Salaried",
    "employment_index": 0,
    "job_years": 5,
    "home": "rented",
    "credit_year": 2015,
    "credit_unknown": False,
    "monthly_income": 65000,
    "annual_income": 780000,
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
    "missed_emi_last_6m": None,
    "overdue_loans": None,
    "new_loans_last_6m": None,
    "loan_enquiries": None,
}


def map_cibil_to_index(cibil_val) -> int:
    """Map CIBIL string representation to the 6-option index (0..5)."""
    if isinstance(cibil_val, int):
        return max(0, min(5, cibil_val))
    s = str(cibil_val).strip().lower()
    if "excel" in s:
        return 0
    if "good" in s:
        return 1
    if "avg" in s or "aver" in s:
        return 2
    if "low" in s:
        return 3
    if "no_hist" in s or "no hist" in s or "none" in s:
        return 4
    return 5
