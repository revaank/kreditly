"""Indian lending rule based standing, reasons, and safe borrowing limits."""
from __future__ import annotations

import math
from src.finance import max_principal_for_emi
from src.translations import t

# Rules and thresholds for Indian lending standing
# Based on retail lending benchmarks in India rather than historical US default datasets:
# - Conservative FOIR (Fixed Obligation to Income Ratio) <= 40%
# - Standard/upper FOIR threshold <= 55%
# - Minimum CIBIL bands and lender criteria rules
STANDING_RULES = {
    # "good":
    # - Total FOIR <= 40% (plenty of monthly cashflow cushion)
    # - CIBIL band is Excellent (750+) or Good (700-749)
    # - Lenders meeting >= half of lenders_total
    "good": {
        "max_foir": 40.0,
        "allowed_cibil": {"excellent", "good"},
        "min_lenders_ratio": 0.5,
    },
    # "almost":
    # - Total FOIR <= 55% (within common NBFC / private bank flexibility limits)
    # - CIBIL band is not Low (<650) - Excellent, Good, Average, and "Don't know" count as not Low
    # - Lenders meeting >= 1
    "almost": {
        "max_foir": 55.0,
        "disallowed_cibil": {"low"},
        "min_lenders_meeting": 1,
    },
    # otherwise: "work" (A few things to fix first)
}


def normalize_cibil(cibil_band: str | int | None) -> str:
    """Normalize user CIBIL band to 'excellent', 'good', 'average', 'low', 'no_history', or 'dont_know'."""
    if cibil_band is None:
        return "dont_know"
    if isinstance(cibil_band, int):
        mapping = {0: "excellent", 1: "good", 2: "average", 3: "low", 4: "no_history", 5: "dont_know"}
        return mapping.get(cibil_band, "dont_know")
    s = str(cibil_band).strip().lower()
    if any(k in s for k in ("no credit history", "no_history", "कोई क्रेडिट इतिहास नहीं")):
        return "no_history"
    if any(k in s for k in ("dont know", "don't know", "पता नहीं")):
        return "dont_know"
    if any(k in s for k in ("low", "below", "कम")):
        return "low"
    if any(k in s for k in ("excel", "750", "उत्कृष्ट")):
        return "excellent"
    if any(k in s for k in ("good", "700", "अच्छा")):
        return "good"
    if any(k in s for k in ("avg", "average", "650", "औसत")):
        return "average"
    return "dont_know"


def total_foir(monthly_income: float, existing_emi: float, new_emi: float) -> float:
    """Percent of take-home pay going to all EMIs after this loan."""
    if monthly_income <= 0:
        return 100.0 if (existing_emi + new_emi) > 0 else 0.0
    return round(((existing_emi + new_emi) / monthly_income) * 100, 1)


def standing(
    foir_pct: float,
    cibil_band: str | int | None,
    lenders_meeting: int,
    lenders_total: int,
) -> str:
    """Classify borrower standing: 'good' | 'almost' | 'work'.

    Follows Indian retail lending standards:
    - 'good': foir_pct <= 40 AND cibil band in (Excellent, Good) AND lenders_meeting >= lenders_total / 2
    - 'almost': foir_pct <= 55 AND cibil band is not Low (<650) AND lenders_meeting >= 1
                (CIBIL "Don't know" counts as not Low here, with an informative reason)
    - otherwise 'work'
    """
    cibil_norm = normalize_cibil(cibil_band)
    half_lenders = (lenders_total / 2.0) if lenders_total > 0 else 0.0

    # 1. Check "good"
    if (
        foir_pct <= STANDING_RULES["good"]["max_foir"]
        and cibil_norm in STANDING_RULES["good"]["allowed_cibil"]
        and lenders_meeting >= half_lenders
    ):
        return "good"

    # 2. Check "almost" (Don't know counts as not Low)
    if (
        foir_pct <= STANDING_RULES["almost"]["max_foir"]
        and cibil_norm not in STANDING_RULES["almost"]["disallowed_cibil"]
        and lenders_meeting >= STANDING_RULES["almost"]["min_lenders_meeting"]
    ):
        return "almost"

    # 3. Otherwise "work"
    return "work"


def standing_reasons(
    foir_pct: float,
    cibil_band: str | int | None,
    lenders_meeting: int,
    lenders_total: int,
) -> list[str]:
    """Return 1-3 short plain-language reasons explaining WHY the borrower received this standing."""
    reasons = []

    # Reason 1: FOIR / Debt burden
    if foir_pct <= STANDING_RULES["good"]["max_foir"]:
        reasons.append(t("standing_reason_foir_good", foir=f"{foir_pct:.0f}"))
    elif foir_pct <= STANDING_RULES["almost"]["max_foir"]:
        reasons.append(t("standing_reason_foir_almost", foir=f"{foir_pct:.0f}"))
    else:
        reasons.append(t("standing_reason_foir_work", foir=f"{foir_pct:.0f}"))

    # Reason 2: CIBIL Score range
    cibil_norm = normalize_cibil(cibil_band)
    if cibil_norm == "excellent":
        reasons.append(t("standing_reason_cibil_excellent"))
    elif cibil_norm == "good":
        reasons.append(t("standing_reason_cibil_good"))
    elif cibil_norm == "average":
        reasons.append(t("standing_reason_cibil_average"))
    elif cibil_norm == "low":
        reasons.append(t("standing_reason_cibil_low"))
    elif cibil_norm == "no_history":
        reasons.append(t("standing_reason_cibil_no_history"))
    else:
        reasons.append(t("standing_reason_cibil_unknown"))

    # Reason 3: Lender criteria matches
    if lenders_meeting > 0:
        reasons.append(
            t(
                "standing_reason_lenders_met",
                count=lenders_meeting,
                total=lenders_total,
            )
        )
    else:
        reasons.append(t("standing_reason_lenders_none", total=lenders_total))

    return reasons


def safe_loan_amount(
    monthly_income: float,
    existing_emi: float,
    annual_rate: float,
    months: int,
    max_foir: float,
) -> int:
    """Largest loan (rounded down to nearest ₹10,000) whose EMI keeps total FOIR <= max_foir.

    Uses standard reducing-balance EMI formula inverted.
    Returns 0 if existing EMIs already reach or exceed the limit.
    """
    if monthly_income <= 0 or months <= 0 or max_foir <= 0:
        return 0
    max_total_emi = monthly_income * (max_foir / 100.0)
    avail_emi = max_total_emi - existing_emi
    if avail_emi <= 0:
        return 0
    raw_principal = max_principal_for_emi(avail_emi, annual_rate, months)
    return int(math.floor(raw_principal / 10000.0) * 10000)
