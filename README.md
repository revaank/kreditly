# Kreditly — Explainable Loan Readiness Tool

Kreditly is an educational loan-readiness demo, not a lender, credit bureau, approval decision, or financial advice. It combines two separate views: an ML estimate of historical loan outcomes and a checklist of lender criteria included in `src/bank_rules.json`.

## What the results mean

- **Model estimate:** The unchanged Phase 2 XGBoost model learned from historical U.S. LendingClub loans. It is not validated for Indian borrowers or current lending. SHAP explanations describe model associations, not causes.
- **Bank rule checker:** Compares the profile with the supplied published minimum criteria for six lenders. `Official` and `Typical` tags preserve the data file's reliability labels. A “meets” result is only a match against the criteria present in that file; it does not mean eligible or guarantee approval. Null criteria are skipped. Criteria can change, so verify each lender's source before applying.
- **What-if:** The simulator updates the model estimate and the number of lenders whose published criteria the changed profile meets. It does not change the trained model or its features.

The app displays the rule-file disclaimer and `last_checked` date. Rule source URLs and reliability labels are also listed on Model Insights and beside the relevant checks.

## Run the app locally

The trained model, threshold, metrics, sample cases, and bank rules are committed. The raw CSV is not needed to run the app.

Use Python 3.11 from the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

For deployment, use Python 3.11, install from `requirements.txt`, and set `app.py` as the Streamlit entry point. No API keys or secrets are required.

## Retrain the model (optional)

Place the supplied `lending_club_loan_two.csv` at `data/lending_club_loan_two.csv`. The `data/` directory is Git-ignored; never commit the raw dataset. The file has 396,030 loan rows and 27 columns, with issue years 2007–2016. It contains 318,357 Fully Paid and 77,673 Charged Off outcomes; unresolved/current loans are absent. Its supplied archive had no source URL, license, or data dictionary. The recorded CSV SHA-256 is `7e63af47a810b1f5d8304108d606a4788c671efc992d23c05751611a7d4c1fda`. Verify the original provenance and license before redistribution.

Install notebook-only dependencies and open the training notebook:

```powershell
pip install -r requirements-training.txt
python -m notebook notebooks/train_model.ipynb
```

The notebook documents the training workflow and writes model artifacts to `models/` and example profiles to `src/sample_cases.json`. Historical features and results should not be treated as current Indian credit guidance.

## Project layout

```text
app.py                       Home page
pages/                       Eligibility, samples, and model insights
src/bank_rules.json          Supplied published lender criteria and source URLs
src/bank_checker.py          Rule evaluation and transparent next-step maths
src/finance.py               EMI, FOIR, and rupee calculations
src/features.py              Shared model feature creation (unchanged in Phase 3)
src/predictor.py             Cached model and grouped SHAP explanations
src/training.py              Reusable model-training helpers
notebooks/train_model.ipynb  Documented training workflow
models/                      Committed model and evaluation artifacts
data/                         Local-only raw dataset (Git-ignored)
```
