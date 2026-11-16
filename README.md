# Kreditly — Explainable Loan Readiness Tool for Indian Borrowers

Solo college project for **INT395 Supervised Learning, CA1 problem #28: FinClarity — Explainable Loan Eligibility Agent**.

Kreditly is an educational, explainable loan-readiness website. This phase uses a deterministic dummy model so the product flow can be reviewed before training. It is not a patient-level or credit-decision system, cannot guarantee an outcome, and is not financial advice. Reported estimates are not lender approvals.

## Features

- Three-step borrower form with English/Hindi labels and retained values when navigating back.
- Live EMI, interest, repayment and salary-to-EMI estimate, using Indian rupee grouping.
- Currency-free model inputs, plain-language reasons and a what-if simulator.
- Eight explicitly illustrative sample cases, downloadable text report and WhatsApp summary without personal figures.
- Insights page that leaves unavailable training results as pending placeholders.
- No form values are saved to disk or transmitted to the model service; the dummy model runs locally.

## Technology

Python 3.11, Streamlit, Plotly, pandas, NumPy, scikit-learn and SHAP (the last two are reserved for later model work).

## Folder structure

```text
app.py                       Home page
pages/                       Eligibility, examples and model insights
src/                         Features, predictor, finance, translation, UI and examples
models/                      Future model/metrics/threshold artifacts
notebooks/                   Future analysis notebooks
assets/                      Future static assets
data/                         Local-only data; ignored by Git
```

## Run locally (Windows PowerShell)

Install Python 3.11 and confirm that `python --version` reports 3.11 before creating the environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

For Streamlit Community Cloud, push the source repository to GitHub later, choose `app.py` as the entry point, and use `requirements.txt` for dependencies. Do not commit the `data/` folder or credentials.

## Model and data status

`src/predictor.py` exposes `predict()`, `explain()`, `FEATURES`, and `USE_REAL_MODEL`. `USE_REAL_MODEL` is currently `False`; all scores and cases are demonstrations and must not be interpreted as real probabilities. The future model adapter belongs in this module so page calls remain stable.

The supplied archive has not been extracted, read or treated as a validated Indian regional dataset in this phase. Review provenance, license, geography, labels and data suitability before any future analysis. No model metrics are available; insights show pending placeholders. The app describes possible future US training data limitations, not verified project dataset facts.

## Screenshots and deployment

- Live link: **Pending deployment**
- Screenshots: **Pending browser review**
