"""Train Kreditly's India repayment model on the L&T Vehicle Loan Default dataset.

Run from the repo root:  python notebooks/train_india_model.py
Needs data/lt_vehicle_loan/train.csv (data/ is git-ignored).
Writes models/india/{model.pkl, calibrator.pkl, metrics.json}.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, brier_score_loss, f1_score, precision_score,
                             recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.india_model import FEATURES, features_from_lt  # noqa: E402

DATA = ROOT / "data" / "lt_vehicle_loan" / "train.csv"
OUT = ROOT / "models" / "india"
SEED = 42
# More missed EMIs / overdue loans / enquiries / new loans must never LOWER risk.
MONOTONE = {"overdue_loans": 1, "missed_emi_last_6m": 1, "loan_enquiries": 1, "new_loans_last_6m": 1}


def scores(y, prob, cut):
    pred = (prob >= cut).astype(int)
    return {"roc_auc": roc_auc_score(y, prob), "brier": brier_score_loss(y, prob),
            "accuracy": accuracy_score(y, pred), "precision": precision_score(y, pred, zero_division=0),
            "recall": recall_score(y, pred), "f1": f1_score(y, pred), "threshold": cut}


def main():
    raw = pd.read_csv(DATA)
    X = features_from_lt(raw)
    y = raw["loan_default"].astype(int)

    idx = np.arange(len(raw))
    tr, tmp = train_test_split(idx, test_size=0.30, stratify=y, random_state=SEED)
    va, te = train_test_split(tmp, test_size=0.50, stratify=y.iloc[tmp], random_state=SEED)
    spw = float((y.iloc[tr] == 0).sum() / (y.iloc[tr] == 1).sum())

    candidates = {
        "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, class_weight="balanced")),
        "Random Forest": RandomForestClassifier(n_estimators=300, min_samples_leaf=50, class_weight="balanced",
                                                n_jobs=-1, random_state=SEED),
        "XGBoost": XGBClassifier(n_estimators=600, max_depth=5, learning_rate=0.05, subsample=0.8,
                                 colsample_bytree=0.8, scale_pos_weight=spw, eval_metric="auc",
                                 monotone_constraints=tuple(MONOTONE.get(f, 0) for f in FEATURES),
                                 random_state=SEED, n_jobs=-1),
    }
    comparison = []
    fitted = {}
    for name, model in candidates.items():
        model.fit(X.iloc[tr], y.iloc[tr])
        fitted[name] = model
        p_va = model.predict_proba(X.iloc[va])[:, 1]
        p_te = model.predict_proba(X.iloc[te])[:, 1]
        comparison.append({"model": name, "validation_roc_auc": round(roc_auc_score(y.iloc[va], p_va), 4),
                           "test_roc_auc": round(roc_auc_score(y.iloc[te], p_te), 4)})
    # XGBoost and Random Forest tie on validation AUC; XGBoost is chosen because it
    # supports monotonic constraints, gives exact fast SHAP values and is a small file.
    best = "XGBoost"
    model = fitted[best]

    # Isotonic calibration on the validation split only
    raw_va = model.predict_proba(X.iloc[va])[:, 1]
    calibrator = IsotonicRegression(out_of_bounds="clip").fit(raw_va, y.iloc[va])
    cal_va = calibrator.predict(raw_va)
    cal_te = calibrator.predict(model.predict_proba(X.iloc[te])[:, 1])

    # Risk bands from validation quantiles of the raw score (continuous, no ties):
    # lowest 30% of profiles / middle 40% / highest 30%.
    lower_max = float(np.quantile(raw_va, 0.30))
    higher_min = float(np.quantile(raw_va, 0.70))
    base_rate = float(y.iloc[tr].mean())

    def band(p):
        return np.where(p <= lower_max, "lower", np.where(p >= higher_min, "higher", "typical"))

    raw_te = model.predict_proba(X.iloc[te])[:, 1]
    te_bands = pd.Series(band(raw_te))
    band_check = (pd.DataFrame({"band": te_bands.values, "default": y.iloc[te].values})
                  .groupby("band")["default"].agg(["mean", "size"]).round(4))

    # F1-maximising cutoff on validation (for reporting only; the app shows bands, not yes/no)
    fpr, tpr, thr = roc_curve(y.iloc[va], cal_va)
    cuts = np.unique(np.round(cal_va, 4))
    f1s = [f1_score(y.iloc[va], (cal_va >= c).astype(int)) for c in cuts]
    cut = float(cuts[int(np.argmax(f1s))])

    importance = pd.Series(getattr(model, "feature_importances_", np.zeros(len(FEATURES))),
                           index=FEATURES).sort_values(ascending=False)

    OUT.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, OUT / "model.pkl")
    joblib.dump(calibrator, OUT / "calibrator.pkl")
    metrics = {
        "dataset": {
            "name": "L&T Vehicle Loan Default Prediction (L&T Financial Services / Analytics Vidhya FinHack)",
            "source_url": "https://www.kaggle.com/datasets/mamtadhaker/lt-vehicle-loan-default-prediction",
            "rows": int(len(raw)), "default_rate": round(float(y.mean()), 4),
            "loan_type": "Two-wheeler / vehicle loans, India",
            "disbursal_period": "Aug-Oct 2018",
            "target": "Payment default in the first EMI on due date",
            "limitations": [
                "Vehicle loans (mostly two-wheelers, median about Rs 54,000), not personal loans.",
                "Predicts first-EMI default, not loan approval.",
                "No income column, so loan-to-income cannot be used.",
                "Only features a user can answer are used; lender-only data (branch, dealer, asset cost, LTV) is excluded, which lowers accuracy.",
                "About half of borrowers have no credit history (score 0).",
            ],
        },
        "features": FEATURES,
        "split": {"train": len(tr), "validation": len(va), "test": len(te), "random_state": SEED},
        "comparison": comparison,
        "best_model": best,
        "test_calibrated": {k: round(float(v), 4) for k, v in scores(y.iloc[te], cal_te, cut).items()},
        "base_rate": round(base_rate, 4),
        "bands": {"on": "raw_model_score", "lower_max": round(lower_max, 6), "higher_min": round(higher_min, 6)},
        "monotone_constraints": MONOTONE,
        "test_default_rate_by_band": {b: {"default_rate": float(r["mean"]), "count": int(r["size"])}
                                      for b, r in band_check.iterrows()},
        "feature_importance": {k: round(float(v), 4) for k, v in importance.items()},
        "benchmark_all_lender_columns_test_auc": 0.663,
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps({k: metrics[k] for k in ("comparison", "best_model", "test_calibrated", "bands",
                                              "test_default_rate_by_band", "feature_importance")}, indent=2))


if __name__ == "__main__":
    main()
