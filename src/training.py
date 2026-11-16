"""Small reusable helpers for the explainable loan-default training notebook."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score, precision_score,
    precision_recall_curve, recall_score, roc_auc_score, roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from .features import FEATURES, make_preprocessor


def stratified_split(features, target, random_state=42):
    """Make reproducible 70/15/15 train, validation, and test partitions."""
    X_train, X_remaining, y_train, y_remaining = train_test_split(
        features, target, test_size=0.30, random_state=random_state, stratify=target
    )
    X_validation, X_test, y_validation, y_test = train_test_split(
        X_remaining, y_remaining, test_size=0.50, random_state=random_state,
        stratify=y_remaining,
    )
    return X_train, X_validation, X_test, y_train, y_validation, y_test


def make_pipeline(estimator):
    """Wrap an estimator in the shared preprocessing fitted only on its train split."""
    return Pipeline([("preprocessor", make_preprocessor()), ("model", estimator)])


def positive_probability(model, features):
    """Return probability for the 1 / Charged Off class."""
    positive_index = list(model.classes_).index(1)
    return model.predict_proba(features)[:, positive_index]


def binary_metrics(target, probabilities, threshold=0.5):
    """Calculate metrics with Charged Off as the positive/risky class."""
    prediction = (np.asarray(probabilities) >= threshold).astype(int)
    return {
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(target, prediction)),
        "precision": float(precision_score(target, prediction, zero_division=0)),
        "recall": float(recall_score(target, prediction, zero_division=0)),
        "f1": float(f1_score(target, prediction, zero_division=0)),
        "roc_auc": float(roc_auc_score(target, probabilities)),
        "confusion_matrix": confusion_matrix(target, prediction, labels=[0, 1]).tolist(),
    }


def choose_f1_threshold(target, probabilities):
    """Find a validation-only cutoff that maximizes F1 for charged-off loans."""
    precision, recall, candidates = precision_recall_curve(target, probabilities)
    scores = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-12)
    best = int(np.argmax(scores))
    return float(candidates[best]), float(scores[best])


def triage_labels(probabilities, threshold, band=0.1):
    """Translate default probabilities into website labels around the cutoff."""
    probabilities = np.asarray(probabilities)
    return np.where(
        probabilities < threshold - band, "STRONG",
        np.where(probabilities > threshold + band, "RISKY", "BORDERLINE"),
    )


def compact_roc(target, probabilities, points=250):
    """Keep evenly spaced ROC coordinates for a small, portable JSON artifact."""
    false_positive, true_positive, thresholds = roc_curve(target, probabilities)
    indexes = np.unique(np.linspace(0, len(false_positive) - 1, min(points, len(false_positive))).astype(int))
    return {
        "fpr": false_positive[indexes].astype(float).tolist(),
        "tpr": true_positive[indexes].astype(float).tolist(),
        "thresholds": thresholds[indexes].astype(float).tolist(),
    }


def transformed_feature_groups(preprocessor):
    """Map each one-hot encoded output column back to its original feature."""
    names = preprocessor.get_feature_names_out()
    mapping = []
    for name in names:
        bare = name.split("__", 1)[-1]
        original = next((feature for feature in FEATURES if bare == feature or bare.startswith(feature + "_")), None)
        if original is None:
            raise ValueError(f"Cannot map transformed model feature {name!r} to an original feature.")
        mapping.append(original)
    return names, mapping


def aggregate_shap(values, mapping):
    """Sum one-hot SHAP columns into the original user-facing feature columns."""
    values = np.asarray(values)
    if isinstance(values, list):
        values = np.asarray(values[-1])
    if values.ndim == 3:
        values = values[:, :, 1]
    result = np.zeros((values.shape[0], len(FEATURES)), dtype=float)
    positions = {feature: index for index, feature in enumerate(FEATURES)}
    for encoded_index, original in enumerate(mapping):
        result[:, positions[original]] += values[:, encoded_index]
    return result


def pick_sample_rows(target, probabilities, threshold, count=4, eligible_mask=None):
    """Select correctly classified, confidently low/high test rows."""
    labels = triage_labels(probabilities, threshold, 0.1)
    target = np.asarray(target)
    eligible_mask = np.ones(len(target), dtype=bool) if eligible_mask is None else np.asarray(eligible_mask, dtype=bool)
    rows = {}
    for group, expected in (("strong", 0), ("risky", 1)):
        eligible = np.flatnonzero(eligible_mask & (target == expected) & (labels == group.upper()))
        if len(eligible) < count:
            raise ValueError(f"Only {len(eligible)} correct {group} test cases; {count} are required.")
        ranked = sorted(eligible, key=lambda index: probabilities[index], reverse=(group == "risky"))
        rows[group] = ranked[:count]
    return rows, labels

