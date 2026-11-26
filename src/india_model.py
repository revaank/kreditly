"""India repayment check, trained on the L&T Vehicle Loan Default dataset.

It estimates how likely someone with a similar credit profile was to miss their
first EMI, compared with the average borrower in the data. It never decides
loan approval. See notebooks/train_india_model.py for training.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

MODEL_DIR = Path(__file__).resolve().parents[1] / "models" / "india"

FEATURES = [
    "bureau_score", "no_credit_history", "age", "self_employed", "employment_missing",
    "credit_history_months", "active_loans", "overdue_loans", "missed_emi_last_6m",
    "new_loans_last_6m", "loan_enquiries", "existing_emi",
]

# Representative bureau score for each CIBIL band used in the Kreditly form
# (Excellent 750+, Good 700-749, Average 650-699, Low <650, plus "no history").
CIBIL_BAND_SCORE = {"excellent": 780, "good": 720, "average": 670, "low": 600, "no_history": 0}

# Values used when a user skips an optional question: medians of borrowers in
# the training data who had a credit score (people with no history get 0s).
DEFAULTS = {
    "bureau_score": 679, "credit_history_months": 24, "active_loans": 1, "overdue_loans": 0,
    "missed_emi_last_6m": 0, "new_loans_last_6m": 0, "loan_enquiries": 0, "existing_emi": 2072,
}
NO_HISTORY_DEFAULTS = {k: 0 for k in DEFAULTS}

# Wording used when a feature's value is 0 (e.g. salaried, no enquiries)
ZERO_LABELS = {
    "en": {
        "self_employed": "Being salaried", "active_loans": "No active loans",
        "overdue_loans": "No overdue loans", "missed_emi_last_6m": "No missed EMIs in the last 6 months",
        "new_loans_last_6m": "No new loans in the last 6 months", "loan_enquiries": "No recent loan enquiries",
        "existing_emi": "No current EMIs", "credit_history_months": "No credit history yet",
    },
    "hi": {
        "self_employed": "वेतनभोगी होना", "active_loans": "कोई चालू लोन नहीं",
        "overdue_loans": "कोई ओवरड्यू लोन नहीं", "missed_emi_last_6m": "पिछले 6 महीनों में कोई EMI नहीं छूटी",
        "new_loans_last_6m": "पिछले 6 महीनों में कोई नया लोन नहीं", "loan_enquiries": "हाल में कोई लोन पूछताछ नहीं",
        "existing_emi": "कोई मौजूदा EMI नहीं", "credit_history_months": "अभी कोई क्रेडिट इतिहास नहीं",
    },
}

FEATURE_LABELS = {
    "en": {
        "bureau_score": "Your CIBIL score", "no_credit_history": "No credit history yet",
        "age": "Your age", "self_employed": "Being self-employed", "employment_missing": "Employment not stated",
        "credit_history_months": "How long you've had credit", "active_loans": "Number of active loans",
        "overdue_loans": "Loans currently overdue", "missed_emi_last_6m": "Missed EMIs in the last 6 months",
        "new_loans_last_6m": "New loans in the last 6 months", "loan_enquiries": "Recent loan enquiries",
        "existing_emi": "Your current EMIs",
    },
    "hi": {
        "bureau_score": "आपका CIBIL स्कोर", "no_credit_history": "अभी कोई क्रेडिट इतिहास नहीं",
        "age": "आपकी उम्र", "self_employed": "स्व-रोज़गार होना", "employment_missing": "रोज़गार नहीं बताया गया",
        "credit_history_months": "आपका क्रेडिट इतिहास कितना पुराना है", "active_loans": "चालू लोन की संख्या",
        "overdue_loans": "अभी बकाया (ओवरड्यू) लोन", "missed_emi_last_6m": "पिछले 6 महीनों में छूटी EMI",
        "new_loans_last_6m": "पिछले 6 महीनों में नए लोन", "loan_enquiries": "हाल की लोन पूछताछ",
        "existing_emi": "आपकी मौजूदा EMI",
    },
}


def _months(text: str) -> int:
    years, months = text.split(" ")
    return int(years.replace("yrs", "")) * 12 + int(months.replace("mon", ""))


def features_from_lt(d: pd.DataFrame) -> pd.DataFrame:
    """Build the user-answerable feature table from raw L&T columns."""
    dob = pd.to_datetime(d["Date.of.Birth"], format="%d-%m-%y")
    dob = dob.where(dob.dt.year <= 2000, dob - pd.DateOffset(years=100))
    disb = pd.to_datetime(d["DisbursalDate"], format="%d-%m-%y")
    return pd.DataFrame({
        "bureau_score": d["PERFORM_CNS.SCORE"],
        "no_credit_history": (d["PERFORM_CNS.SCORE"] == 0).astype(int),
        "age": ((disb - dob).dt.days / 365.25).round(1),
        "self_employed": (d["Employment.Type"] == "Self employed").astype(int),
        "employment_missing": d["Employment.Type"].isna().astype(int),
        "credit_history_months": d["CREDIT.HISTORY.LENGTH"].map(_months),
        "active_loans": d["PRI.ACTIVE.ACCTS"] + d["SEC.ACTIVE.ACCTS"],
        "overdue_loans": d["PRI.OVERDUE.ACCTS"] + d["SEC.OVERDUE.ACCTS"],
        "missed_emi_last_6m": d["DELINQUENT.ACCTS.IN.LAST.SIX.MONTHS"],
        "new_loans_last_6m": d["NEW.ACCTS.IN.LAST.SIX.MONTHS"],
        "loan_enquiries": d["NO.OF_INQUIRIES"],
        "existing_emi": d["PRIMARY.INSTAL.AMT"] + d["SEC.INSTAL.AMT"],
    })[FEATURES]


def build_features(profile: dict) -> tuple[pd.DataFrame, list[str]]:
    """Map a Kreditly profile to one model row. Returns (row, assumed_fields).

    profile keys (all optional except age):
      age, employment ("salaried"/"self_employed"/other), cibil_score (int) or
      cibil_band (excellent/good/average/low/no_history; anything else = don't know), credit_years,
      active_loans, overdue_loans, missed_emi_last_6m, new_loans_last_6m,
      loan_enquiries, existing_emi
    """
    assumed: list[str] = []

    score = profile.get("cibil_score")
    if score is None:
        band = str(profile.get("cibil_band") or "").strip().lower()
        if band in CIBIL_BAND_SCORE:
            score = CIBIL_BAND_SCORE[band]
        else:
            score = DEFAULTS["bureau_score"]
            assumed.append("bureau_score")
    score = int(score)

    fallback = NO_HISTORY_DEFAULTS if score == 0 else DEFAULTS

    def pick(key):
        val = profile.get(key)
        if val is None:
            if score > 0:
                assumed.append(key)
            return fallback[key]
        return val

    credit_years = profile.get("credit_years")
    if credit_years is None:
        credit_months = pick("credit_history_months")
    else:
        credit_months = int(round(float(credit_years) * 12))

    emp = profile.get("employment")
    row = {
        "bureau_score": score,
        "no_credit_history": int(score == 0),
        "age": float(profile["age"]),
        "self_employed": int(emp == "self_employed"),
        "employment_missing": int(emp is None),
        "credit_history_months": credit_months,
        "active_loans": pick("active_loans"),
        "overdue_loans": pick("overdue_loans"),
        "missed_emi_last_6m": pick("missed_emi_last_6m"),
        "new_loans_last_6m": pick("new_loans_last_6m"),
        "loan_enquiries": pick("loan_enquiries"),
        "existing_emi": pick("existing_emi"),
    }
    return pd.DataFrame([row])[FEATURES], assumed


@lru_cache(maxsize=1)
def load():
    import joblib
    model = joblib.load(MODEL_DIR / "model.pkl")
    calibrator = joblib.load(MODEL_DIR / "calibrator.pkl")
    metrics = json.loads((MODEL_DIR / "metrics.json").read_text())
    return model, calibrator, metrics


@lru_cache(maxsize=1)
def _explainer():
    import shap
    model, _, _ = load()
    return shap.TreeExplainer(model)


def risk_band(raw_score: float, metrics: dict) -> str:
    """Band from the raw model score (cut-offs = validation 30th/70th percentiles)."""
    b = metrics["bands"]
    if raw_score <= b["lower_max"]:
        return "lower"
    if raw_score >= b["higher_min"]:
        return "higher"
    return "typical"


def assess(profile: dict, lang: str = "en", top_n: int = 3) -> dict:
    """Return band, calibrated probability, average, and top reasons."""
    model, calibrator, metrics = load()
    X, assumed = build_features(profile)
    raw = float(model.predict_proba(X)[0, 1])
    prob = float(calibrator.predict([raw])[0])

    contrib = _explainer().shap_values(X)[0]
    labels = FEATURE_LABELS.get(lang, FEATURE_LABELS["en"])
    order = np.argsort(-np.abs(contrib))
    reasons = []
    for i in order:
        name = FEATURES[i]
        if name in ("no_credit_history", "employment_missing") and X.iloc[0][name] == 0:
            continue
        value = X.iloc[0][name]
        label = labels[name]
        if value == 0 and name in ZERO_LABELS["en"]:
            if name == "credit_history_months" and X.iloc[0]["bureau_score"] > 0:
                label = labels[name]
            else:
                label = ZERO_LABELS.get(lang, ZERO_LABELS["en"])[name]
        reasons.append({"feature": name, "label": label, "value": float(value),
                        "direction": "raises" if contrib[i] > 0 else "lowers",
                        "impact": float(contrib[i]), "assumed": name in assumed})
        if len(reasons) == top_n:
            break

    band = risk_band(raw, metrics)
    return {
        "band": band,
        "probability": prob,
        "average": metrics["base_rate"],
        "band_test_rate": metrics["test_default_rate_by_band"][band]["default_rate"],
        "reasons": reasons,
        "assumed": assumed,
    }
