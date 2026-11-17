from __future__ import annotations

"""Compare a borrower profile with the supplied, published lender criteria."""
import json
import math
from pathlib import Path

from .finance import foir, format_inr, loan_summary, principal_within_foir


RULES_PATH = Path(__file__).with_name("bank_rules.json")
CIBIL_BANDS = {
    "excellent": (750, math.inf),
    "good": (700, 749),
    "average": (650, 699),
    "low": (0, 649),
}
RULE_KEYS = (
    "employment_types_allowed", "min_age", "max_age", "min_monthly_income",
    "min_current_job_years", "min_cibil", "max_foir", "min_loan",
    "max_loan", "max_tenure_months",
)


class BankRulesError(ValueError):
    """Raised when the provided rules file is missing or malformed."""


def load_bank_rules(path: Path = RULES_PATH) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BankRulesError("Bank criteria are temporarily unavailable.") from error
    if not isinstance(data, dict) or not isinstance(data.get("lenders"), list):
        raise BankRulesError("The bank criteria file has an invalid structure.")
    return data


def _value(rule: dict | None):
    return rule.get("value") if isinstance(rule, dict) else None


def _cibil_band(user: dict):
    if user.get("cibil_unknown") or user.get("cibil_index") == 4:
        return None
    band_index = user.get("cibil_index")
    if isinstance(band_index, int) and 0 <= band_index <= 3:
        return [CIBIL_BANDS["excellent"], CIBIL_BANDS["good"],
                CIBIL_BANDS["average"], CIBIL_BANDS["low"]][band_index]
    label = str(user.get("cibil", "")).strip().lower()
    if "don't know" in label or "dont know" in label or "पता नहीं" in label:
        return None
    for name, band in CIBIL_BANDS.items():
        if label.startswith(name):
            return band
    return None


def _rule_row(key, status, user_value, requirement, rule, message_key=None, message_values=None):
    return {
        "key": key,
        "status": status,
        "user_value": user_value,
        "requirement": requirement,
        "reliability": rule.get("reliability"),
        "note": rule.get("note"),
        "source": rule.get("source"),
        "needs_review": bool(rule.get("needs_review", False)),
        "message_key": message_key,
        "message_values": message_values or {},
    }


def _add_rule(rows, lender, key, user, context):
    """Append one check only when the source supplies a real value."""
    rule = lender.get(key)
    value = _value(rule)
    if value is None:
        return

    age = float(user.get("age", 0))
    employment = user.get("employment", "")
    income = float(user.get("annual_income", 0)) / 12
    job_years = float(user.get("job_years", 0))
    loan = float(user.get("loan_amount", 0))
    months = int(user.get("tenure_months", 0))
    rate = float(user.get("rate", 0))
    monthly_emi = context["monthly_emi"]
    current_foir = context["foir"]

    if key == "employment_types_allowed":
        allowed = value if isinstance(value, list) else []
        ok = employment in allowed
        rows.append(_rule_row(key, "pass" if ok else "fail", employment, allowed, rule))
    elif key == "min_age":
        rows.append(_rule_row(key, "pass" if age >= value else "fail", age, value, rule))
    elif key == "max_age":
        effective_age = age + months / 12 if rule.get("at_loan_maturity", False) else age
        rows.append(_rule_row(
            key, "pass" if effective_age <= value else "fail", effective_age,
            {"value": value, "at_maturity": bool(rule.get("at_loan_maturity", False))}, rule,
        ))
    elif key == "min_monthly_income":
        employment_notes = " ".join(
            str(lender.get(field, {}).get("note", ""))
            for field in ("employment_types_allowed", key, "min_current_job_years")
            if isinstance(lender.get(field), dict)
        ).lower()
        job_note = str(lender.get("min_current_job_years", {}).get("note", "")).lower()
        not_published_for_self_employed = employment == "Self-employed" and (
            "only salaried" in employment_notes
            or ("income" in employment_notes and "not checked" in employment_notes)
        )
        if not_published_for_self_employed:
            rows.append(_rule_row(
                key, "warn", income, value, rule,
                "bank_self_employed_not_checked", {"field": "income"},
            ))
            return
        existing_value = rule.get("existing_customer_value")
        if income >= value:
            status, message = "pass", None
        elif existing_value is not None and income >= existing_value:
            status, message = "warn", "bank_salary_account_only"
        else:
            status, message = "fail", None
        rows.append(_rule_row(
            key, status, income,
            {"value": value, "existing_customer_value": existing_value}, rule, message,
            {"short_name": lender.get("short_name", lender.get("name", ""))},
        ))
    elif key == "min_current_job_years":
        employment_notes = " ".join(
            str(lender.get(field, {}).get("note", ""))
            for field in ("employment_types_allowed", key)
            if isinstance(lender.get(field), dict)
        ).lower()
        if employment == "Self-employed" and (
            "only salaried" in employment_notes or "not checked" in employment_notes
        ):
            rows.append(_rule_row(
                key, "warn", job_years, value, rule,
                "bank_self_employed_not_checked", {"field": "work history"},
            ))
            return
        rows.append(_rule_row(key, "pass" if job_years >= value else "fail", job_years, value, rule))
    elif key == "min_cibil":
        band = _cibil_band(user)
        if band is None:
            status, message = "warn", "bank_cibil_unknown"
        elif band[0] >= value:
            status, message = "pass", None
        elif band[1] < value:
            status, message = "fail", None
        else:
            status, message = "warn", "bank_cibil_overlap"
        rows.append(_rule_row(key, status, user.get("cibil", ""), value, rule, message))
    elif key == "max_foir":
        rows.append(_rule_row(key, "pass" if current_foir <= value else "fail", current_foir, value, rule))
    elif key == "min_loan":
        rows.append(_rule_row(key, "pass" if loan >= value else "fail", loan, value, rule))
    elif key == "max_loan":
        rows.append(_rule_row(key, "pass" if loan <= value else "fail", loan, value, rule))
    elif key == "max_tenure_months":
        rows.append(_rule_row(key, "pass" if months <= value else "fail", months, value, rule))


def _fixes_for(lender, user, result, lenders):
    """Offer only changes that follow from a published criterion or exact EMI math."""
    from .translations import t

    fixes = []
    by_key = {row["key"]: row for row in result["rules"]}
    income = float(user.get("annual_income", 0)) / 12
    existing_emi = float(user.get("existing_emi", 0))
    loan = float(user.get("loan_amount", 0))
    months = int(user.get("tenure_months", 0))
    rate = float(user.get("rate", 0))

    foir_rule = by_key.get("max_foir")
    if foir_rule and foir_rule["status"] == "fail":
        limit = float(_value(lender.get("max_foir")))
        max_loan = principal_within_foir(income, existing_emi, limit, rate, months)
        fixes.append(t("bank_fix_foir_loan", amount=format_inr(max_loan)))
        longest = int(_value(lender.get("max_tenure_months")) or months)
        if lender.get("max_age", {}).get("at_loan_maturity", False):
            max_age = _value(lender.get("max_age"))
            age_cap = max(0, math.floor((float(user.get("age", 0)) - max_age) * -12))
            longest = min(longest, age_cap)
        if longest > 0:
            new_emi = loan_summary(loan, rate, longest)["emi"]
            new_foir = foir(income, existing_emi, new_emi)
            fixes.append(t("bank_fix_foir_tenure", months=longest, foir=new_foir))
        target_emi = income * limit / 100
        required_clear = max(0, math.ceil(existing_emi + loan_summary(loan, rate, months)["emi"] - target_emi))
        if required_clear > existing_emi:
            remaining_foir = foir(income, 0, loan_summary(loan, rate, months)["emi"])
            fixes.append(t("bank_fix_clear_all", amount=format_inr(existing_emi), foir=remaining_foir))
        else:
            fixes.append(t("bank_fix_clear_emi", amount=format_inr(required_clear)))

    min_loan = _value(lender.get("min_loan"))
    if min_loan is not None and loan < min_loan:
        fixes.append(t("bank_fix_loan_min", amount=format_inr(min_loan)))
    max_loan_rule = by_key.get("max_loan")
    if max_loan_rule and max_loan_rule["status"] == "fail":
        fixes.append(t("bank_fix_loan_max", amount=format_inr(_value(lender.get("max_loan")))))
    tenure_rule = by_key.get("max_tenure_months")
    if tenure_rule and tenure_rule["status"] == "fail":
        fixes.append(t("bank_fix_max_tenure", months=_value(lender.get("max_tenure_months"))))

    income_rule = by_key.get("min_monthly_income")
    if income_rule and income_rule["status"] == "fail":
        required = income_rule["requirement"]["value"]
        alternatives = []
        for other in lenders:
            if other["id"] == lender["id"]:
                continue
            other_income_rule = other.get("min_monthly_income", {})
            other_values = [
                candidate for candidate in (
                    _value(other_income_rule), other_income_rule.get("existing_customer_value")
                ) if candidate is not None
            ]
            if other_values and min(other_values) < required:
                alternatives.append(other.get("short_name", other["name"]))
        alternative_text = ", ".join(alternatives) if alternatives else t("bank_no_lower_alternatives")
        fixes.append(t("bank_fix_income", amount=format_inr(required), alternatives=alternative_text))

    age_rule = by_key.get("max_age")
    if age_rule and age_rule["status"] == "fail" and age_rule["requirement"].get("at_maturity"):
        months_fit = max(0, math.floor((age_rule["requirement"]["value"] - float(user.get("age", 0))) * 12))
        max_tenure = _value(lender.get("max_tenure_months"))
        if max_tenure is not None:
            months_fit = min(months_fit, max_tenure)
        fixes.append(t("bank_fix_age_tenure", months=months_fit) if months_fit else t("bank_fix_age_no_tenure"))

    cibil_rule = by_key.get("min_cibil")
    if cibil_rule and cibil_rule["status"] == "fail":
        fixes.append(t("bank_fix_cibil"))
    for row in result["rules"]:
        if row.get("message_key"):
            fixes.append(t(row["message_key"], **row.get("message_values", {})))
    return list(dict.fromkeys(fixes))


def check_all(user: dict, rules: dict | None = None) -> list[dict]:
    """Return criteria checks for each lender without inferring unpublished rules."""
    data = rules if rules is not None else load_bank_rules()
    loan = float(user.get("loan_amount", 0))
    rate = float(user.get("rate", 0))
    months = int(user.get("tenure_months", 0))
    income = float(user.get("annual_income", 0)) / 12
    existing_emi = float(user.get("existing_emi", 0))
    if not all(math.isfinite(value) for value in (loan, rate, income, existing_emi)):
        raise BankRulesError("Profile values must be finite numbers.")
    if loan <= 0 or rate < 0 or months <= 0 or income <= 0 or existing_emi < 0:
        raise BankRulesError("Enter a positive income, loan amount, and tenure to check lender criteria.")
    monthly_emi = loan_summary(loan, rate, months)["emi"]
    context = {"monthly_emi": monthly_emi, "foir": foir(income, existing_emi, monthly_emi)}
    results = []
    for lender in data["lenders"]:
        rows = []
        for key in RULE_KEYS:
            _add_rule(rows, lender, key, user, context)
        fails = sum(row["status"] == "fail" for row in rows)
        warns = sum(row["status"] == "warn" for row in rows)
        status = "meets" if rows and fails == 0 and warns == 0 else "close" if fails <= 1 else "not_yet"
        result = {
            "id": lender["id"], "name": lender["name"], "short_name": lender["short_name"],
            "type": lender["type"], "product": lender["product"], "status": status,
            "rules": rows, "foir": context["foir"], "monthly_emi": context["monthly_emi"],
            "interest_rate_from": lender.get("interest_rate_from", {}).get("value"),
            "interest_rate_rule": lender.get("interest_rate_from", {}),
            "official_page": lender.get("official_page"), "fixes": [],
        }
        result["fixes"] = _fixes_for(lender, user, result, data["lenders"])
        results.append(result)
    return results


def count_meets(results: list[dict]) -> int:
    return sum(item["status"] == "meets" for item in results)
