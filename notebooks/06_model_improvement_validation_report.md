# Model Improvement and Validation: Troubleshooting Report

## Issue resolution

| Cell | Issue identified | Root cause | Solution implemented | Verification |
|---|---|---|---|---|
| 06, original cell 1 | `Path`, `pd`, and `joblib` were used later but were not imported; several imported estimators were unused. | Imports did not cover the variables needed by later cells, and output reflected an earlier kernel state. | Replaced with explicit imports for the final workflow; added the Python executable and fixed random state to the output. | Fresh-kernel execution printed `G:\AIOT\smart-irrigation\.venv\Scripts\python.exe`; imports succeeded. |
| 06, original cell 2 | Dataset selection used the newest CSV by modification time and did not verify required files or the target. | Which CSV loaded could change with timestamps; missing inputs could fail later with less useful errors. | Load the project's named processed CSV and baseline artifact; check both paths, target presence, non-empty data, and target missingness up front. | Loaded `irrigation_prediction_processed.csv` (10,000 x 20); checks passed. |
| 06, staged version of original cell 2 | The staged copy omitted a comma between the `glob` argument and `key=` in `sorted(...)`, which would raise `SyntaxError`. | The staged notebook source differed from the corrected working-tree version. | Replaced the cell with an explicit, deterministic dataset path rather than relying on sorted file discovery. | Final notebook executed from a fresh kernel without syntax errors. |
| 06, original cell 3 | Dataset checks did not validate the feature/model contract and omitted class proportions. | A missing target or changed numeric columns could fail downstream; imbalance was not made visible. | Report missing values and class counts/proportions; select numeric predictors only and align/validate them against the serialized model's feature names. | Zero missing values; 11 matching numeric features; class proportions: High 3.36%, Low 58.64%, Medium 38.00%. |
| 06, original cell 4 | Model loading depended on undefined `joblib` and stopped after printing artifact metadata. | No evaluation, cross-validation, comparison, or feature-schema check was implemented. | Load and verify the baseline, evaluate training and held-out scores, run stratified CV and training-only randomized search, compare per-class results, and reload the saved candidate. | Baseline loaded as `RandomForestClassifier`; all evaluation cells completed. Reloaded optimized-model predictions exactly matched pre-save predictions. |
| 06, original cell 5 | Empty cell produced no output; the notebook contained no model improvement or validation workflow. | The notebook ended before splitting data, tuning, or evaluating. | Added deterministic split, 5-fold `StratifiedKFold`, 12-candidate `RandomizedSearchCV`, comparison tables, classification reports, confusion matrices, and model persistence. | All 10 non-empty code cells executed; no code cell is empty. |
| 03, training split / 06 split | The saved baseline was trained using an unstratified 80/20 split. The rare High class has only 336 records overall. | A stratified test split would not correspond to the rows on which the existing artifact was trained, making a direct baseline comparison invalid. | Reconstructed the original `test_size=0.2`, `random_state=42` split for both models; used shuffled stratified 5-fold CV within training data. | Same 8,000/2,000 split used for comparison; test set has 59 High, 1,204 Low, and 737 Medium examples. |
| 04, evaluation cell | The fallback selected the full processed CSV and evaluated predictions on all 10,000 rows, including model-training rows. | The model had already been fit on 8,000 of those rows; this mixed in-sample and held-out performance and produced the misleading 0.946 accuracy. | Prefer a dedicated `test.csv` when present; otherwise recreate the training notebook's fixed 20% hold-out split. | Executed evaluation reports 2,000 held-out rows and 0.728 accuracy, matching the baseline evaluation in notebook 06. |
| 06, optimization and save cells | No protection against test-set tuning or overwriting the baseline artifact. | Optimization and persistence logic had not been implemented. | Search only on `X_train`/`y_train`, select on mean CV macro F1, evaluate the test set afterward, and save to `irrigation_model_optimized.joblib`. | Search ran 60 CV fits; original baseline file timestamp remained unchanged; optimized artifact reloaded successfully. |

## Baseline versus optimized model

The test set was not used for hyperparameter optimization. Macro F1 was the selection metric because the class distribution is imbalanced.

| Metric | Baseline | Optimized |
|---|---:|---:|
| Training accuracy | 1.000 | 0.940 |
| Training macro F1 | 1.000 | 0.926 |
| Held-out accuracy | 0.728 | 0.722 |
| Held-out macro precision | 0.699 | 0.627 |
| Held-out macro recall | 0.571 | 0.654 |
| Held-out macro F1 | 0.607 | 0.639 |
| Held-out weighted F1 | 0.722 | 0.724 |
| 5-fold CV validation macro F1 (mean +/- std) | 0.606 +/- 0.016 | 0.647 +/- 0.017 |
| 5-fold CV validation accuracy | 0.733 | 0.731 |

**Per-class held-out results (precision / recall / F1):**

| Class | Baseline | Optimized |
|---|---:|---:|
| High | 0.68 / 0.29 / 0.40 | 0.46 / 0.54 / 0.50 |
| Low | 0.77 / 0.83 / 0.80 | 0.80 / 0.78 / 0.79 |
| Medium | 0.64 / 0.59 / 0.61 | 0.62 / 0.64 / 0.63 |

The optimized model improves held-out macro F1 by 0.032 and High-class recall by 0.25, with similar CV gains. It does **not** improve accuracy (0.728 to 0.722), and High-class precision falls from 0.68 to 0.46. This is a trade-off, not an unqualified improvement. The baseline's training accuracy and CV training macro F1 are both 1.000, indicating substantial overfitting; the candidate narrows but does not eliminate the train-validation gap.

The previously reported 0.946 accuracy came from the full 10,000-row dataset, not a held-out-only evaluation. The baseline was perfect on its 8,000 training rows and scored 0.728 on its 2,000 held-out rows; combining those in-sample and held-out predictions gives 0.9456, consistent with the earlier rounded 0.946.

## Search and saved model

- Search: `RandomizedSearchCV`, 12 parameter samples, 5-fold stratified CV, `random_state=42`, refit on training data.
- Best parameters: `n_estimators=300`, `max_depth=30`, `min_samples_split=10`, `min_samples_leaf=4`, `max_features="sqrt"`, `class_weight="balanced_subsample"`.
- Optimized artifact: `models/irrigation_model_optimized.joblib`; the existing `models/irrigation_model.joblib` was not overwritten.
- Feature contract: both models use the same 11 numeric features. Eight categorical predictors remain excluded to preserve compatibility with the baseline and existing inference contract.

## Execution and dependencies

- Executed `notebooks/06_model_improvement_validation.ipynb` from a fresh kernel using the activated `.venv`; all 10 non-empty code cells completed, and notebook structure validation passed.
- Executed the corrected `notebooks/04_model_evaluation.ipynb`; its held-out result matches the baseline result above.
- Verified the old full-dataset accuracy directly: 0.9456 versus 0.728 on the reconstructed held-out rows. The optimized artifact also loaded through `src.predict.predict` and returned predictions for five rows.
- The `.venv` initially lacked packages declared in `requirements.txt` (including pandas, joblib, plotting, and notebook dependencies). Installed/restored the declared requirements; no dependency manifest changes were needed.
- Verified environment: Python 3.13.15, pandas 2.3.3, NumPy 2.5.4, scikit-learn 1.9.1, joblib 1.6.0, matplotlib 3.11.2, seaborn 0.13.2, nbconvert 7.17.2.

## Remaining limitations and deployment assessment

- The processed data is one 10,000-row CSV; no independent farm, season, or future-time test set is available. Random hold-out and CV results do not prove robustness under deployment distribution shift.
- The High class has only 59 examples in the fixed test set. Its precision/recall estimates are therefore uncertain; class-weighting increases recall but also false positives.
- Categorical features are not used. Adding them would require a separately evaluated preprocessing/model pipeline and an updated prediction input contract.
- Confirm field units and that every predictor—especially `Previous_Irrigation_mm`—is available before the irrigation decision and is not recorded after the outcome. The current data has no missing values; broader preprocessing leakage was not exercised here.
- **Not ready for operational deployment.** The candidate is suitable for prototype API integration only if clearly labeled experimental. Before controlling irrigation, validate against representative real sensor data and independent sites/seasons, agree on the cost of false irrigation decisions, and establish monitoring and fallback behavior.
