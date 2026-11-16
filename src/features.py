"""Shared feature engineering and training-time preprocessing for Kreditly.

The notebook and the Streamlit pages call these same functions so that the
model sees the same feature names, units, and category labels at both points.
"""
from datetime import date
import re

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


CATEGORICAL_FEATURES = ["purpose", "home_ownership"]
FEATURES = [
    "loan_to_income", "revol_bal_to_income", "dti", "revol_util", "open_acc",
    "total_acc", "pub_rec", "mort_acc", "pub_rec_bankruptcies", "term",
    "purpose", "emp_length", "home_ownership", "credit_history_years",
]
NUMERIC_FEATURES = [name for name in FEATURES if name not in CATEGORICAL_FEATURES]


def parse_emp_length(value):
    """Convert LendingClub employment labels to completed years; missing stays NaN."""
    if pd.isna(value):
        return np.nan
    text = str(value).strip().lower()
    if text in {"< 1 year", "<1 year", "less than 1 year"}:
        return 0.0
    if text in {"10+ years", "10 years or more"}:
        return 10.0
    match = re.search(r"\d+", text)
    return float(match.group()) if match else np.nan


def parse_term(value):
    """Extract the number of months from labels such as ' 36 months'."""
    if pd.isna(value):
        return np.nan
    match = re.search(r"\d+", str(value))
    return float(match.group()) if match else np.nan


def map_purpose(value):
    """Normalize purpose strings while leaving rare-category grouping to training."""
    if pd.isna(value):
        return np.nan
    text = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "credit_card_payoff": "credit_card", "car_loan": "car",
        "vehicle": "car", "big_purchase": "major_purchase",
        "other": "other",
    }
    return aliases.get(text, text)


def map_home_ownership(value):
    """Map the website's English options and dataset labels to shared categories."""
    if pd.isna(value):
        return np.nan
    text = str(value).strip().upper().replace(" ", "_")
    aliases = {
        "RENTED": "RENT", "OWN_LOAN": "MORTGAGE", "OWN_WITH_HOME_LOAN": "MORTGAGE",
        "MORTGAGE": "MORTGAGE", "OWN": "OWN", "RENT": "RENT",
        "OTHER": "OTHER", "NONE": "OTHER", "ANY": "OTHER",
    }
    return aliases.get(text, "OTHER")


def features_from_dataset(raw: pd.DataFrame) -> pd.DataFrame:
    """Build the ordered, currency-free model columns from LendingClub rows."""
    income = pd.to_numeric(raw["annual_inc"], errors="coerce").replace(0, np.nan)
    issue_year = pd.to_datetime(raw["issue_d"], format="%b-%Y", errors="coerce").dt.year
    credit_year = pd.to_datetime(raw["earliest_cr_line"], format="%b-%Y", errors="coerce").dt.year
    result = pd.DataFrame(index=raw.index)
    result["loan_to_income"] = pd.to_numeric(raw["loan_amnt"], errors="coerce") / income
    result["revol_bal_to_income"] = pd.to_numeric(raw["revol_bal"], errors="coerce") / income
    result["dti"] = pd.to_numeric(raw["dti"], errors="coerce")
    for name in ("revol_util", "open_acc", "total_acc", "pub_rec", "mort_acc", "pub_rec_bankruptcies"):
        result[name] = pd.to_numeric(raw[name], errors="coerce")
    result["term"] = raw["term"].map(parse_term)
    result["purpose"] = raw["purpose"].map(map_purpose)
    result["emp_length"] = raw["emp_length"].map(parse_emp_length)
    result["home_ownership"] = raw["home_ownership"].map(map_home_ownership)
    result["credit_history_years"] = issue_year - credit_year
    return result[FEATURES]


def build_features(values: dict) -> dict:
    """Convert a website profile into the exact model feature names.

    All cash amounts are converted to ratios before reaching the model. The
    website's current EMI information is its available approximation of DTI.
    """
    annual_income = max(float(values.get("annual_income", 0) or 0), 1.0)
    loan_amount = float(values.get("loan_amount", 0) or 0)
    revolving_balance = float(values.get("revol_bal", values.get("card_bill", 0)) or 0)
    dti = values.get("dti")
    if dti is None:
        dti = float(values.get("existing_emi", 0) or 0) / (annual_income / 12) * 100
    today_year = date.today().year
    if values.get("credit_history_years") is not None:
        credit_history_years = float(values["credit_history_years"])
    elif values.get("credit_unknown"):
        credit_history_years = 5.0
    else:
        credit_history_years = max(0.0, today_year - int(values.get("credit_year", today_year)))
    emp_length = values.get("emp_length", values.get("job_years", 0))
    return {
        "loan_to_income": loan_amount / annual_income,
        "revol_bal_to_income": revolving_balance / annual_income,
        "dti": float(dti),
        "revol_util": float(values.get("revol_util", 0) or 0),
        "open_acc": float(values.get("open_acc", 0) or 0),
        "total_acc": float(values.get("total_acc", 0) or 0),
        "pub_rec": float(values.get("pub_rec", 0) or 0),
        "mort_acc": float(values.get("mort_acc", 0) or 0),
        "pub_rec_bankruptcies": float(values.get("bankruptcies", values.get("pub_rec_bankruptcies", 0)) or 0),
        "term": parse_term(values.get("tenure_months", values.get("term", 36))),
        "purpose": map_purpose(values.get("purpose", "other")),
        "emp_length": parse_emp_length(emp_length),
        "home_ownership": map_home_ownership(values.get("home", values.get("home_ownership", "Rented"))),
        "credit_history_years": credit_history_years,
    }


class RareCategoryGrouper(BaseEstimator, TransformerMixin):
    """Fold infrequent categories into OTHER using counts from fit data only."""

    def __init__(self, min_frequency=0.01):
        self.min_frequency = min_frequency

    def fit(self, X, y=None):
        frame = pd.DataFrame(X)
        self.keep_categories_ = []
        for column in frame.columns:
            values = frame[column].dropna().astype(str)
            counts = values.value_counts(normalize=True)
            self.keep_categories_.append(set(counts[counts >= self.min_frequency].index))
        self.n_features_in_ = frame.shape[1]
        return self

    def transform(self, X):
        frame = pd.DataFrame(X).copy()
        for index, column in enumerate(frame.columns):
            keep = self.keep_categories_[index]
            mask = frame[column].notna()
            frame.loc[mask, column] = frame.loc[mask, column].astype(str).where(
                frame.loc[mask, column].astype(str).isin(keep), "OTHER"
            )
        return frame.to_numpy(dtype=object)

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return np.asarray([f"x{i}" for i in range(self.n_features_in_)], dtype=object)
        return np.asarray(input_features, dtype=object)


class QuantileClipper(BaseEstimator, TransformerMixin):
    """Clip numeric columns to fit-data quantiles, then reuse bounds at inference."""

    def __init__(self, lower=0.01, upper=0.99):
        self.lower = lower
        self.upper = upper

    def fit(self, X, y=None):
        values = np.asarray(X, dtype=float)
        self.lower_bounds_ = np.nanquantile(values, self.lower, axis=0)
        self.upper_bounds_ = np.nanquantile(values, self.upper, axis=0)
        self.lower_bounds_ = np.nan_to_num(self.lower_bounds_, nan=0.0)
        self.upper_bounds_ = np.nan_to_num(self.upper_bounds_, nan=0.0)
        self.n_features_in_ = values.shape[1]
        return self

    def transform(self, X):
        values = np.asarray(X, dtype=float)
        return np.clip(values, self.lower_bounds_, self.upper_bounds_)

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return np.asarray([f"x{i}" for i in range(self.n_features_in_)], dtype=object)
        return np.asarray(input_features, dtype=object)


def make_preprocessor():
    """Return the shared train-fit-only clipping, imputation, scaling, and encoding."""
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("clip", QuantileClipper(0.01, 0.99)),
        ("scale", StandardScaler()),
    ])
    categorical = Pipeline([
        ("rare", RareCategoryGrouper(min_frequency=0.01)),
        ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("numeric", numeric, NUMERIC_FEATURES),
        ("categorical", categorical, CATEGORICAL_FEATURES),
    ])
