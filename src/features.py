"""Convert form values to currency-free features; rupee amounts stay out of the model."""
from datetime import date

def build_features(values: dict) -> dict:
    annual_income = max(float(values.get("annual_income", 0)), 1)
    return {
        "loan_to_income": float(values.get("loan_amount", 0)) / annual_income,
        "revol_bal_to_income": float(values.get("card_bill", 0)) / annual_income,
        # Existing monthly EMIs only, consistent with the brief's DTI definition.
        "dti": float(values.get("existing_emi", 0)) / (annual_income / 12) * 100,
        "revol_util": float(values.get("revol_util", 0)),
        "open_acc": int(values.get("open_acc", 0)), "total_acc": int(values.get("total_acc", 0)),
        "pub_rec": int(values.get("pub_rec", 0)), "mort_acc": int(values.get("mort_acc", 0)),
        "pub_rec_bankruptcies": int(values.get("bankruptcies", 0)),
        "term": int(values.get("tenure_months", 36)), "purpose": values.get("purpose", "other"),
        "emp_length": int(values.get("job_years", 0)), "home_ownership": values.get("home", "rented"),
        # If the user does not know the year, use a conservative five-year default.
        "credit_history_years": 5 if values.get("credit_unknown") else max(0, date.today().year - int(values.get("credit_year", date.today().year))),
    }
