# Kreditly — Explainable Loan Readiness Tool

Kreditly is an educational loan readiness demo. It combines an estimate from an unchanged XGBoost model trained on historical U.S. LendingClub data with a separate checklist of published minimum criteria from six Indian lenders. It is not a lender, credit bureau, approval decision, or financial advice.

## What the app shows

- **Model estimate:** calibrated probability, readiness band, SHAP factors, and possible next steps. The model uses historical U.S. loans and has not been validated for Indian borrowers or current lending. SHAP describes model associations, not causes.
- **Published lender criteria:** rule-by-rule comparisons using only `src/bank_rules.json`. Null rules are skipped. Official and typical sources are labeled; flagged sources are marked for review. A match does not mean approval, and rules may change.
- **What-if simulator:** recalculates the estimate and count of lenders matching the published criteria when supported values change. It does not change the trained model or its features.
- **Hindi and English:** available in the Streamlit app and the Next.js web app.
- **Downloadable report:** print or save the results page as PDF.

The bank checker shows the disclaimer and `last_checked` value from the rules file. Only borrow from RBI-registered lenders; be cautious of instant-loan apps that ask for unusual permissions or upfront fees.

## Run locally

Use Python 3.11. The model files, calibration artifacts, metrics, sample cases, and bank rules are committed; the raw dataset is not required to run the app.

### Existing Streamlit app

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

### API

In another terminal, activate the same environment and run:

```powershell
pip install -r requirements-api.txt
uvicorn api.main:app --reload
```

The API provides `GET /health`, `POST /predict`, `POST /lenders`, `POST /whatif`, and `GET /emi-table`. Interactive API documentation is at `http://localhost:8000/docs`. The API loads the saved model/calibrator and uses the existing finance, explanation, and bank-rule logic.

### New web app

Use Node.js 20.9 or newer:

```powershell
cd web
Copy-Item .env.example .env.local
corepack pnpm install
corepack pnpm dev
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `web/.env.local`, and run the API in another terminal. Open `http://localhost:3000`.

## Deploy

The deployment files are prepared for Vercel (frontend) and Render (API). The code is pushed to GitHub, but the cloud services have not been created or connected. Create a Vercel project with **Root Directory** set to `web`; create the Render web service from `render.yaml`. Set `NEXT_PUBLIC_API_URL` in Vercel to the public Render API URL and `KREDITLY_FRONTEND_ORIGIN` in Render to the exact Vercel origin. Both services deploy from this repository. Check the API's `/health` URL after deployment.

Set `KREDITLY_WEB_URL` on the Streamlit deployment to the public web app URL; the existing Streamlit home page uses it for the “Try the new Kreditly website” link. The link stays hidden until a real URL is configured.

## Model and data limitations

The model was trained on 396,030 historical U.S. loan records from 2007–2016 (318,357 Fully Paid; 77,673 Charged Off). It omits unresolved/current loans. The trained model and its features are unchanged. Probabilities are isotonic-calibrated on the validation partition; readiness bands use validation quantiles. The validation calibration score is an in-sample diagnostic, so the held-out test score is the stronger generalization check. These results do not establish performance for Indian borrowers or current lending.

The supplied dataset archive had no source URL, license, or data dictionary. Its raw CSV belongs at `data/lending_club_loan_two.csv`; the `data/` directory is Git-ignored and must not be committed. The recorded CSV SHA-256 is `7e63af47a810b1f5d8304108d606a4788c671efc992d23c05751611a7d4c1fda`. Confirm provenance and license before redistribution.

## Optional model retraining

```powershell
pip install -r requirements-training.txt
python -m notebook notebooks/train_model.ipynb
```

## Project map

```text
app.py, pages/              Existing Streamlit application
api/                        FastAPI endpoints
web/                        Next.js bilingual web app
src/bank_rules.json         Supplied lender criteria and source URLs
src/bank_checker.py         Rule evaluation and transparent fixes
src/finance.py              EMI, FOIR, and rupee calculations
src/features.py             Shared model features
src/predictor.py            Model inference and explanations
models/                     Committed model and evaluation artifacts
tests/                      Core and API checks
data/                       Local-only dataset; Git-ignored
```
