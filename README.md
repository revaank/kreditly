# Kreditly — Explainable Loan Readiness Tool

Kreditly is a university project that demonstrates a model workflow and an educational loan-readiness interface. It is not a lender, does not guarantee approval, and is not financial advice.

## Important model limitation

The training file contains historical **U.S. LendingClub** loan outcomes. It is not representative or validated for Indian borrowers or current lending. The score is a classroom demonstration only; do not use it for a real credit decision. Historical feature associations are not causes.

## Phase 2 workflow

- `notebooks/train_model.ipynb` documents inspection, leakage exclusions, shared feature engineering, stratified splitting, model comparison, threshold selection, grouped SHAP analysis, sample selection, and artifact export.
- `src/features.py` is shared by the notebook and app. Only currency-free ratios, counts, term, purpose, employment length, home ownership, and credit-history length reach the model.
- The model pipeline fits numeric imputation, 1st–99th percentile clipping, scaling, rare-category grouping, categorical imputation, and one-hot encoding on training rows only.
- `models/` stores the trained pipeline, validation-selected cutoff, comparison/ROC/test metrics, and aggregated SHAP importance.
- `src/sample_cases.json` contains eight correctly predicted illustrative test profiles. Dollar amounts are multiplied by a fixed display factor of 20 for the rupee UI. This is not an exchange rate; ratios stay approximately the same.

## Dataset setup and provenance

Place the supplied `lending_club_loan_two.csv` at `data/lending_club_loan_two.csv`. The `data/` directory is Git-ignored; the raw dataset is not committed.

The supplied archive has no source URL, license, or data dictionary metadata. The notebook records this as unverified and includes a SHA-256 digest for the CSV. Verify the original source and license before redistribution. The file currently has 396,030 loan rows, 27 columns, and issue months from 2007 through 2016. Only Fully Paid and Charged Off outcomes are present; unresolved loans are not represented.

## Setup (Windows PowerShell)

Use Python 3.11. From the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run the training notebook from the project root in Jupyter or VS Code. Its outputs are saved to `models/` and `src/sample_cases.json`:

```powershell
python -m notebook notebooks/train_model.ipynb
```

Start the website after the model artifacts exist:

```powershell
streamlit run app.py
```

## Project layout

```text
app.py                       Home page
pages/                       Eligibility, examples, and model insights
src/features.py              Shared feature creation and preprocessing
src/predictor.py             Cached model and grouped SHAP explanations
src/counterfactual.py        What-if simulator and small-change search
src/training.py              Reusable training and metric helpers
notebooks/train_model.ipynb  Documented training and export workflow
models/                      Trained artifacts and actual evaluation results
data/                         Local-only raw data (Git-ignored)
```
