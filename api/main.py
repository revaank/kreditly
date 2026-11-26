"""HTTP API over the existing Kreditly model, finance, explanation, and rule logic."""
from contextlib import asynccontextmanager
import os
from typing import Literal

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.bank_checker import check_all, count_meets, load_bank_rules
from src.counterfactual import find_improvements
from src.explainer import explain_reasons, suggestion_text
from src.features import build_features
from src.finance import loan_summary, foir
from src.predictor import _load_calibrator, _load_model, _load_shap_explainer, explain, predict
from src.translations import reset_language, set_language


Employment = Literal["Salaried", "Self-employed"]
Purpose = Literal[
    "debt_consolidation", "credit_card", "home_improvement", "major_purchase",
    "small_business", "car", "medical", "other",
]
Home = Literal["rented", "own", "own_loan"]


class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age: int = Field(ge=21, le=65)
    employment: Employment = "Salaried"
    job_years: float = Field(default=5, ge=0, le=60)
    annual_income: float = Field(gt=0, le=1_000_000_000)
    existing_emi: float = Field(default=0, ge=0, le=100_000_000)
    card_bill: float = Field(default=0, ge=0, le=100_000_000)
    revol_util: float = Field(default=30, ge=0, le=100)
    open_acc: int = Field(default=5, ge=0, le=100)
    total_acc: int = Field(default=8, ge=0, le=150)
    mort_acc: int = Field(default=0, ge=0, le=50)
    pub_rec: int = Field(default=0, ge=0, le=50)
    bankruptcies: int = Field(default=0, ge=0, le=20)
    cibil_index: int = Field(default=1, ge=0, le=4)
    cibil: str = "Good · 700–749"
    cibil_unknown: bool = False
    credit_year: int = Field(default=2016, ge=1950, le=2026)
    credit_unknown: bool = False
    home: Home = "rented"
    loan_amount: float = Field(gt=0, le=1_000_000_000)
    tenure_months: int = Field(default=36, ge=1, le=360)
    purpose: Purpose = "debt_consolidation"
    rate: float = Field(default=11, ge=0, le=40)
    language: Literal["en", "hi"] = "en"


class WhatIfRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile: Profile
    changes: dict[str, float | int]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Load these once per process; predictor functions reuse the same LRU-cached objects.
    _load_model()
    _load_calibrator()
    _load_shap_explainer()
    yield


app = FastAPI(title="Kreditly API", version="2.0.0", lifespan=lifespan)
allowed_origins = [
    origin.strip() for origin in os.getenv("KREDITLY_FRONTEND_ORIGIN", "http://localhost:3000").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Accept", "Accept-Language"],
)


def _user(profile: Profile) -> dict:
    return profile.model_dump(exclude={"language"})


def _with_language(language: str):
    return set_language(language)


def _prediction_result(user: dict, language: str) -> dict:
    token = _with_language(language)
    try:
        features = build_features(user)
        estimate = predict(features)
        reasons = explain_reasons(features, explain(features))
        summary = loan_summary(user["loan_amount"], user["rate"], user["tenure_months"])
        monthly_income = user["annual_income"] / 12
        existing_emi = user["existing_emi"]
        suggestions = find_improvements(user)
        return {
            "probability": estimate["risk"],
            "readiness_band": estimate["readiness_band"],
            "label": estimate["label"],
            "top_factors": reasons[:3],
            "suggestions": [
                {**item, "text": suggestion_text(item)} for item in suggestions[:3]
            ],
            "finance": {
                "emi": summary["emi"],
                "total_interest": summary["interest"],
                "total_repayment": summary["total"],
                "foir": foir(monthly_income, existing_emi, summary["emi"]),
            },
        }
    finally:
        reset_language(token)


@app.get("/health")
def health():
    return {"status": "ok", "service": "kreditly-api"}


@app.exception_handler(RequestValidationError)
async def validation_error(_request: Request, _error: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Please check the submitted profile values and try again."},
    )


@app.exception_handler(Exception)
async def friendly_server_error(_request: Request, _error: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Kreditly could not complete that request. Please try again."},
    )


@app.post("/predict")
def predict_profile(profile: Profile):
    return _prediction_result(_user(profile), profile.language)


@app.post("/lenders")
def lender_results(profile: Profile):
    user = _user(profile)
    token = _with_language(profile.language)
    try:
        lenders = check_all(user)
    finally:
        reset_language(token)
    status_map = {"meets": "qualify", "close": "close", "limited": "limited", "not_yet": "miss"}
    rules_file = load_bank_rules()
    return {
        "lenders": [
            {**item, "status": status_map[item["status"]]} for item in lenders
        ],
        "qualify_count": count_meets(lenders),
        "total": len(lenders),
        "disclaimer": rules_file.get("disclaimer"),
        "last_checked": rules_file.get("last_checked"),
    }


@app.post("/whatif")
def what_if(request: WhatIfRequest):
    allowed = {"annual_income", "loan_amount", "tenure_months", "existing_emi", "revol_util"}
    invalid = set(request.changes) - allowed
    if invalid:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Unsupported what-if field.")
    original = _user(request.profile)
    updated_values = {**original, **request.changes}
    updated = Profile.model_validate(updated_values)
    result = _prediction_result(_user(updated), updated.language)
    baseline = predict(build_features(original))
    result["delta"] = {
        "risk": result["probability"] - baseline["risk"],
        "from_band": baseline["readiness_band"],
    }
    return result


@app.get("/emi-table")
def emi_table(
    amount: float = Query(gt=0, le=1_000_000_000),
    rate: float = Query(ge=0, le=40),
):
    return {
        "amount": amount,
        "rate": rate,
        "terms": [
            {"months": months, **loan_summary(amount, rate, months)}
            for months in (12, 24, 36, 48, 60)
        ],
    }
