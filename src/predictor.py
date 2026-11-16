"""Plug-in point for a future trained model. Phase 1 uses a transparent dummy score."""
from pathlib import Path
from functools import lru_cache
import json

FEATURES = ["loan_to_income", "revol_bal_to_income", "dti", "revol_util", "open_acc", "total_acc", "pub_rec", "mort_acc", "pub_rec_bankruptcies", "term", "purpose", "emp_length", "home_ownership", "credit_history_years"]
USE_REAL_MODEL = False
ROOT = Path(__file__).resolve().parents[1]

def _threshold():
    path = ROOT / "models" / "threshold.json"
    if path.exists():
        try: return min(.9, max(.1, float(json.loads(path.read_text(encoding="utf-8")).get("threshold", .5))))
        except (ValueError, OSError, AttributeError): pass
    return .5

@lru_cache(maxsize=1)
def _load_model():
    """Load the later model once, when the real-model flag is enabled."""
    import joblib
    model_path=ROOT/"models"/"model.pkl"
    if not model_path.exists():
        raise FileNotFoundError("USE_REAL_MODEL is true, but models/model.pkl is not present.")
    return joblib.load(model_path)

def _model_frame(features):
    import pandas as pd
    return pd.DataFrame([{name:features.get(name) for name in FEATURES}],columns=FEATURES)

def _risk_class_index(model):
    classes=[str(value).upper().replace(" ","_") for value in model.classes_]
    for label in ("RISKY","DEFAULT","CHARGED_OFF"):
        if label in classes: return classes.index(label)
    if classes==["0","1"]: return 1
    raise ValueError("The trained model must expose a RISKY/DEFAULT class or binary 0/1 classes.")

def _dummy_risk(features: dict) -> float:
    score = .22
    score += min(.24, max(0, features.get("dti", 0) - 15) * .004)
    score += min(.2, max(0, features.get("loan_to_income", 0) - .5) * .09)
    score += min(.12, max(0, features.get("revol_util", 0) - 30) * .002)
    score += min(.12, features.get("pub_rec", 0) * .035)
    score += min(.16, features.get("pub_rec_bankruptcies", 0) * .08)
    score += .07 if features.get("term") == 60 else 0
    score -= min(.09, features.get("emp_length", 0) * .008)
    score -= min(.06, features.get("mort_acc", 0) * .015)
    score -= min(.1, features.get("credit_history_years", 0) * .008)
    return min(.95, max(.03, score))

def predict(features: dict) -> dict:
    if USE_REAL_MODEL:
        model=_load_model(); probabilities=model.predict_proba(_model_frame(features))[0]
        risk=float(probabilities[_risk_class_index(model)]); threshold=_threshold()
        label="BORDERLINE" if abs(risk-threshold)<=.1 else ("STRONG" if risk<threshold else "RISKY")
        return {"label":label,"risk":risk}
    risk = _dummy_risk(features); threshold = _threshold()
    label = "BORDERLINE" if abs(risk-threshold) <= .1 else ("STRONG" if risk < threshold else "RISKY")
    return {"label": label, "risk": risk}

def explain(features: dict) -> list:
    if USE_REAL_MODEL:
        import shap
        model=_load_model(); explanation=shap.Explainer(model)(_model_frame(features))
        values=explanation.values[0]
        if getattr(values,"ndim",1)>1: values=values[:,_risk_class_index(model)]
        named=sorted(zip(FEATURES,values),key=lambda item:abs(float(item[1])),reverse=True)[:8]
        return [{"feature":name,"value":round(float(value),3),"contribution":round(float(value),3)} for name,value in named]
    contributions = [("Loan compared with yearly income", max(0, features.get("loan_to_income",0)-.5)*.09),
      ("Existing monthly EMIs", max(0,features.get("dti",0)-15)*.004), ("Card limit used",max(0,features.get("revol_util",0)-30)*.002),
      ("Past defaults or court records",features.get("pub_rec",0)*.035),("Bankruptcy records",features.get("pub_rec_bankruptcies",0)*.08),
      ("Time in current job",-features.get("emp_length",0)*.008),("Credit history length",-features.get("credit_history_years",0)*.008),
      ("Home loans",-features.get("mort_acc",0)*.015),("Repayment period",.07 if features.get("term")==60 else 0)]
    return [{"feature": n, "value": round(v,3), "contribution": round(v,3)} for n,v in sorted(contributions,key=lambda x:abs(x[1]),reverse=True)[:8]]
