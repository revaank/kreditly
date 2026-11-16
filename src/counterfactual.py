"""Apply what-if changes and re-run the same prediction interface."""
from copy import deepcopy
from .features import build_features
from .predictor import predict

def apply_change(values: dict, *, income=None, loan=None, months=None, existing_emi=None, revol_util=None):
    changed = deepcopy(values)
    for key, value in (("annual_income",income),("loan_amount",loan),("tenure_months",months),("existing_emi",existing_emi),("revol_util",revol_util)):
        if value is not None: changed[key] = value
    return changed, predict(build_features(changed))
