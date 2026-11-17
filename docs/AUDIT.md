# Kreditly v2 audit (before changes)

Date: 2026-11-17  
Repository state: `main`, clean at `08b6907` (`Phase 3: bank checker, Hindi, and deploy prep`).  
This audit records the existing implementation before v2 changes. The raw CSV exists locally at `data/lending_club_loan_two.csv` (about 100 MB), is ignored by Git, and is not tracked.

## Folder structure

- `app.py`: Streamlit home page.
- `pages/1_Check_Eligibility.py`: three-step profile form, estimate, explanations, what-if simulator, bank results, downloadable text report and WhatsApp share link.
- `pages/2_Sample_Cases.py`: examples, explanations, and what-if controls.
- `pages/3_Model_Insights.py`: training data context, metrics, comparisons, ROC curves, confusion matrix, SHAP importance, leakage exclusions, and lender rule sources.
- `src/`: the shared Python package used by Streamlit. It contains feature engineering (`features.py`), training helpers (`training.py`), inference and SHAP (`predictor.py`), financial calculations (`finance.py`), counterfactual search (`counterfactual.py`), lender checks/UI (`bank_checker.py`, `bank_ui.py`), translations (`translations.py`), and page chrome (`ui.py`). This package can be imported by the future API, avoiding a second copy of ML or lender logic.
- `notebooks/train_model.ipynb`: the documented model training and artifact export workflow.
- `models/`: tracked `model.pkl`, `threshold.json`, `metrics.json`, and `feature_importance.json`.
- `src/bank_rules.json`: six supplied lender records, source metadata, reliability, disclaimer and `last_checked` date. Do not change published values as part of v2.
- `src/sample_cases.json`: generated sample profiles.
- `.streamlit/config.toml`: Streamlit theme/server settings; Streamlit's sidebar page navigation is not currently disabled.
- `requirements.txt`: pinned runtime dependencies. `requirements-training.txt` extends it for notebooks.
- `data/`: local ignored source data; no data file is tracked.
- `assets/`: currently only `.gitkeep`.

## Training, model save/load, and current scores

The notebook reads the local ignored CSV, validates its columns/outcomes, and maps `Fully Paid` to 0 and `Charged Off` to 1. It removes lender-pricing/grade/instalment columns, free text/address fields, and platform-specific columns. `src.features.features_from_dataset` produces the fixed ordered features documented below.

`src.training.stratified_split` creates reproducible 70% train, 15% validation, and 15% test partitions (`random_state=42`). Preprocessing is fit inside each model pipeline on training rows only. The notebook compares Logistic Regression and Random Forest with balanced class weights against XGBoost with `scale_pos_weight` equal to the train negative/positive count ratio. The selected model is the one with the highest validation ROC-AUC; the current committed winner is XGBoost.

The notebook tunes a decision threshold by maximizing validation F1 for the charged-off class. Current artifacts record threshold `0.5194309949874878` and triage band `±0.10`. It currently saves only the selected pipeline to `models/model.pkl`, threshold/band to `models/threshold.json`, evaluation and provenance metadata to `models/metrics.json`, and aggregated feature importance to `models/feature_importance.json`. There is no probability calibrator or readiness-band configuration yet. The notebook has the raw split and fitted objects needed to add the requested validation-fitted isotonic calibrator and persist it beside the existing model.

`src.predictor._load_model` uses `joblib` and Streamlit resource caching. `predict_many` calls `predict_proba` directly on the selected pipeline, then `_labels` maps the probabilities using `threshold.json`. Thus the current displayed probability is uncalibrated, and the current `STRONG`/`BORDERLINE`/`RISKY` labels come from the validation-tuned cutoff plus fixed borderline band.

The dataset metadata currently records 396,030 rows: 318,357 Fully Paid and 77,673 Charged Off (about 19.6% charged off). The model metrics page rounds its four top-line metrics to three decimals and rounds comparison metrics to three decimals, but currently prints source filename, target counts as a raw dictionary, missing counts as a dictionary, and CSV checksum in an expanded dataset section. Feature names in the SHAP chart are raw internal names. `limitations` are printed alongside another hard-coded list, duplicating at least one issue.

## Feature pipeline

`src.features.FEATURES` fixes the model input order to: `loan_to_income`, `revol_bal_to_income`, `dti`, `revol_util`, `open_acc`, `total_acc`, `pub_rec`, `mort_acc`, `pub_rec_bankruptcies`, `term`, `purpose`, `emp_length`, `home_ownership`, and `credit_history_years`.

Dataset preprocessing derives loan and revolving-balance to annual-income ratios, parses term and employment length, normalizes purpose and home-ownership values, and derives credit-history duration from issue and earliest-credit years. The shared `build_features` converts the Streamlit profile to this same schema, using existing EMI as the available approximation of DTI. The pipeline imputes numeric medians, clips numeric values to train-fitted 1st/99th percentiles, standardizes numeric columns, groups rare categorical values based on training data, imputes unknown categories, and one-hot encodes the two categorical features (`purpose`, `home_ownership`).

## SHAP explanations

`src.predictor._load_shap_explainer` caches a `shap.TreeExplainer` for the underlying tree estimator in the saved pipeline. `explain_many` applies the saved preprocessor, calculates tree SHAP values on encoded inputs, and uses `src.training.transformed_feature_groups` and `aggregate_shap` to sum one-hot contributions back to original feature groups. The Streamlit pages pass these to `src.explainer.explain_reasons`, which formats feature values and uses English/Hindi template strings. SHAP reports associations from this historical model; it does not explain causation. If probability calibration is added, SHAP should remain on the original uncalibrated tree, as requested, because it explains that model rather than the calibration mapping.

## Lender rule evaluation

`src.bank_checker.load_bank_rules` reads the supplied JSON. `check_all(user)` derives monthly income from yearly income, computes EMI and FOIR with `src.finance`, evaluates only populated rule values (null values are skipped), and returns criterion rows with pass/warn/fail, profile value, requirement, reliability, notes, and source URL. CIBIL bands are Excellent 750+, Good 700–749, Average 650–699, and Low under 650. Income exceptions for existing salary-account customers and disclosed self-employed rule limits are represented as warnings. Lender statuses are `meets`, `close`, and `not_yet`; `count_meets` counts only `meets`. Fix suggestions use `src.finance` for rupee/EMI computations and never advise concealing debts or misstating income.

`src.bank_ui.render_bank_results` shows the rule-file disclaimer, last-checked date, match count, sorted lender cards, criteria, source links, and fixes. In compact mode it returns the same results and displays a counter for the what-if state. The eligibility page includes bank outcomes and date/disclaimer in its downloadable text report.

Two rule source URLs have been identified by the v2 prompt for manual review; the current JSON still contains them and they must be flagged, not silently replaced:

1. SBI records reference `https://www.bankbazaar.com/state-bank-of-hyderabad-loan.html` for several criteria. The prompt notes this is a State Bank of Hyderabad page and asks for review due to the 2017 merger.
2. Tata Capital's `interest_rate_from` cites `https://www.tatacapital.com/covid.html`; the prompt notes that it may be outdated.

## Language toggle and Streamlit pages

`src.translations.py` stores English and Hindi strings in dictionaries and exposes `t(key, **values)`, which chooses from `st.session_state.language`. `src.ui.header` initializes the session value to `EN` and renders a button whose callback toggles between `EN` and `हिं`. Page labels mostly call `t`; hard-coded text remains on the Model Insights page by design in the previous Phase 3 request, and the current v2 prompt asks for a working toggle and missing translations across the app. The eligibility page remembers whether the credit-history answer is unknown when its localized widget is hidden between wizard steps.

The eligibility page always renders the EMI summary from its current default profile, even on step 1. It runs the model only after the loan step's submit action. Its what-if controls call the same model on changed values and show bank result counter updates. The current counterfactual search enumerates combinations, then filters to STRONG and sorts by a change-cost heuristic; it can return multiple suggestions using the same lever rather than maximizing calibrated risk reduction across distinct levers.

## Existing run and deployment contract

The Streamlit entry point is `app.py`; Streamlit Cloud depends on it, `pages/`, `requirements.txt`, tracked model artifacts, and the JSON rule file. Keep these paths intact. Current dependencies are pinned in `requirements.txt`; the app can be run from a Python 3.11 virtual environment using `pip install -r requirements.txt && streamlit run app.py`. The current app has no FastAPI or Next.js directories, API tests, Dockerfile, Render config, or Vercel config. The user reports the prior site is deployed at `https://kreditly.streamlit.app`; the Streamlit app should remain available as the legacy path.

## Phase 1 baseline and acceptance notes

- The class weighting in the current XGBoost training pipeline is a plausible reason its raw probabilities may be overconfident; the required isotonic calibrator must be fitted on validation probabilities and applied at inference without replacing model features or the booster.
- The requested strong-profile probability and readiness band are empirical acceptance criteria and must be checked against the saved validation-trained calibrator. Calibration must not be described as proof of suitability for Indian credit decisions.
- There are no tests in the repository at this baseline. The requested tests should protect finance math, calibrated probability bounds/bands, distinct-lever suggestions, and the example lender result including Tata Capital's CIBIL overlap.
- The current result summary appears before loan details; the what-if display delegates delta formatting to `st.metric` and does not explicitly neutralize exact zero; suggestions are not constrained to distinct levers.
- The current `.streamlit/config.toml` sets `showErrorDetails = false` but does not set `showSidebarNavigation = false`.

## Phase 1 implementation and validation (2026-11-17)

The existing XGBoost pipeline and its 14 input features remain unchanged. The updated training notebook now fits `CalibratedClassifierCV(estimator=best_pipeline, method="isotonic", cv="prefit")` on the existing validation partition, saves `models/calibrator.pkl`, retunes the triage cutoff from calibrated validation probabilities, and writes `models/readiness.json`. Inference uses calibrated probabilities; SHAP continues to use the original uncalibrated tree. `models/metrics.json` records the calibration and readiness metadata.

The Brier scores are:

| Partition | Before calibration | After calibration |
|---|---:|---:|
| Validation (calibrator fit partition) | 0.2205 | 0.1447 |
| Held-out test | 0.2195 | 0.1449 |

The validation score is an in-sample calibration diagnostic because isotonic regression is fitted on the validation partition; the independent held-out test result is the stronger generalization check. Both scores improve substantially on this split.

Readiness bands use the 1/3 and 2/3 quantiles of calibrated validation probabilities: `good_max=0.1340`, `fair_max=0.2239`; higher values are `needs_work`. On the requested example (₹8,00,000 annual income, ₹3,00,000 loan, 36 months at 11%, 22% FOIR, CIBIL 700–749, 30% card use), the calibrated probability is 0.4288 (42.9%) and the band is `needs_work`. This lands around the 96th percentile of the validation probabilities. It is below 50%, but it does not support the requested `good` band under validation-tertile cutoffs. The implementation deliberately does not label that high relative-risk estimate as good. This is the unresolved Phase 1 acceptance conflict; Phase 2 has not started.

The same profile matches five lenders; Tata Capital is `close` because the selected 700–749 range overlaps its published 725 threshold. The what-if suggestions are three distinct helpful levers (card use, loan amount, existing EMI), ranked by calibrated risk reduction.

Other Phase 1 changes: the EMI summary now appears from step 3 onward; zero what-if deltas are neutral and arrow-free; lower risk is green/down and higher risk orange/up; review flags were added only to the affected SBI and Tata source entries without changing rule values or URLs; raw risk percentages appear under a details disclosure; Model Insights now rounds metrics, labels features readably, uses a target-count table, hides filename/checksum in a collapsed reproducibility section, removes duplicate limitations, and lists flagged rule sources. Streamlit's default sidebar navigation is hidden. English and Hindi strings have matching key coverage.

The loopback-only Streamlit smoke check returned HTTP 200. Browser checks confirmed the home, Hindi eligibility form, Hindi sample page, English eligibility result, bank results, and the source-review tags rendered without a runtime traceback after fixing a nested-expander error in the sample view.

Six core checks pass using `python -m unittest discover -s tests -v`. `pytest` is pinned in `requirements-training.txt`, but could not be installed in this environment because outbound access to PyPI is unavailable. The tests use `unittest.TestCase`, which pytest can collect when installed.
