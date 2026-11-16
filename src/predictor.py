"""Load the trained LendingClub pipeline and explain its risk estimates."""
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
import shap
import streamlit as st

from .features import FEATURES
from .training import aggregate_shap, transformed_feature_groups


USE_REAL_MODEL = True
ROOT = Path(__file__).resolve().parents[1]


@st.cache_resource(show_spinner=False)
def _load_model():
    """Load one model object for the lifetime of the Streamlit server."""
    model_path = ROOT / "models" / "model.pkl"
    if not model_path.exists():
        raise FileNotFoundError("The trained model is missing. Run notebooks/train_model.ipynb first.")
    return joblib.load(model_path)


@st.cache_resource(show_spinner=False)
def _load_shap_explainer():
    """Build the model-specific SHAP tree explainer once per app process."""
    return shap.TreeExplainer(_load_model().named_steps["model"])


def _settings():
    path = ROOT / "models" / "threshold.json"
    if not path.exists():
        raise FileNotFoundError("The validation-tuned models/threshold.json file is missing.")
    values = json.loads(path.read_text(encoding="utf-8"))
    threshold = float(values["threshold"])
    band = float(values["borderline_band"])
    if not 0 < threshold < 1 or not 0 <= band <= 0.5:
        raise ValueError("The stored model threshold settings are invalid.")
    return threshold, band


def _model_frame(features):
    return pd.DataFrame([{name: features.get(name) for name in FEATURES}], columns=FEATURES)


def _frame_for_profiles(features_list):
    return pd.DataFrame([{name: features.get(name) for name in FEATURES} for features in features_list], columns=FEATURES)


def _labels(probabilities):
    threshold, band = _settings()
    return np.where(
        probabilities < threshold - band, "STRONG",
        np.where(probabilities > threshold + band, "RISKY", "BORDERLINE"),
    )


def predict_many(features_list):
    """Predict a batch in one model call (also used by the what-if search)."""
    if not features_list:
        return []
    model = _load_model()
    class_index = list(model.classes_).index(1)
    probabilities = model.predict_proba(_frame_for_profiles(features_list))[:, class_index]
    labels = _labels(probabilities)
    return [{"label": str(label), "risk": float(probability)} for label, probability in zip(labels, probabilities)]


def predict(features: dict) -> dict:
    """Return Charged Off probability and STRONG/BORDERLINE/RISKY label."""
    return predict_many([features])[0]


def explain_many(features_list):
    """Return grouped SHAP contributions for each original feature in a batch."""
    if not features_list:
        return []
    model = _load_model()
    preprocessor = model.named_steps["preprocessor"]
    encoded = preprocessor.transform(_frame_for_profiles(features_list))
    if hasattr(encoded, "toarray"):
        encoded = encoded.toarray()
    raw_values = _load_shap_explainer()(encoded)
    grouped_names, mapping = transformed_feature_groups(preprocessor)
    _ = grouped_names  # the mapping is used to collapse one-hot columns
    grouped_values = aggregate_shap(raw_values.values, mapping)
    result = []
    for row, values in zip(features_list, grouped_values):
        order = np.argsort(np.abs(values))[::-1][:8]
        result.append([
            {"feature": FEATURES[index], "value": row.get(FEATURES[index]), "contribution": float(values[index])}
            for index in order
        ])
    return result


def explain(features: dict) -> list:
    """Return the largest per-original-feature SHAP values for one profile."""
    return explain_many([features])[0]
