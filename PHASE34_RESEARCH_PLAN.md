# Phase 34 Research Plan — Alternative NIFTY D−6 Prediction Models

## Research question
At exactly 10:00 IST on six calendar days before NIFTY 50 expiry, do model families not tested in Phase 33 provide reproducible out-of-sample predictive information about the expiry-day NIFTY close direction or horizon return?

## Secondary questions
1. Do gradient-boosting, margin-based and regularized-linear models improve on Phase-33 Random Forest?
2. Does a point-in-time Hidden Markov regime model add value by conditioning direction on latent market state?
3. Does a small Transformer or temporal-convolution sequence model add information beyond the Phase-33 LSTM?
4. Can a fixed, pre-registered ensemble of the new families outperform simple baselines without holdout-driven weighting?

## Scope and stopping rule
This phase is a bounded model-family extension. It is not a free-form hyperparameter search. Eight new model families plus two fixed ensembles are tested once under fixed parameters. No additional threshold, architecture, feature or weight may be added after inspecting validation or holdout results.

## Locked reference and target
- Reference = expiry minus six calendar days at exactly 10:00:00 IST.
- Exact 10:00 observation is required; missing events are excluded.
- Target = NIFTY expiry-day latest complete close at or before 15:29 IST.
- Primary target = direction of log(expiry_close / reference_spot).
- Secondary target = expiry-horizon log return.

## Chronological evaluation
- Development/train: through 2023-12-31.
- Validation: 2024-01-01 through 2025-12-31.
- Untouched holdout: 2026-01-01 through 2026-09-30.
- Validation model selection is allowed only against development-trained models.
- Holdout is never used for tuning.

## Models

### A1 — XGBoost
Fixed gradient-boosted tree classifier:
- n_estimators=250
- max_depth=3
- learning_rate=0.03
- subsample=0.80
- colsample_bytree=0.80
- min_child_weight=5
- reg_lambda=2
- objective=binary:logistic
- eval_metric=logloss
- random_state=1337

### A2 — ExtraTrees
Fixed extremely-randomized tree classifier:
- n_estimators=400
- max_depth=6
- min_samples_leaf=4
- class_weight=balanced
- random_state=1337

### A3 — HistGradientBoosting
Fixed scikit-learn histogram gradient boosting:
- max_iter=250
- learning_rate=0.03
- max_leaf_nodes=15
- max_depth=4
- min_samples_leaf=8
- l2_regularization=1.0
- random_state=1337

### A4 — RBF-SVM
Fixed support-vector classifier:
- C=1.0
- gamma=scale
- class_weight=balanced
- probability=True
- random_state=1337
Features are median-imputed and standardized using the fit sample only.

### A5 — Elastic-Net Logistic Regression
Fixed regularized linear probability model:
- solver=saga
- penalty=elasticnet
- C=0.20
- l1_ratio=0.50
- class_weight=balanced
- max_iter=5000
- random_state=1337

### A6 — HMM Regime Probability Model
A 3-state Gaussian HMM is fit only on NIFTY daily information strictly before each reference timestamp. Current-state posterior is converted into an expiry-horizon up-probability using smoothed historical horizon-return frequencies observed before the reference. No future observation enters the regime fit.

### A7 — Tiny Transformer
A fixed, intentionally small Transformer encoder over the previous 30 completed NIFTY trading sessions:
- d_model=32
- nhead=4
- num_layers=1
- feedforward=64
- dropout=0.10
- Adam lr=0.003
- 50 epochs
- MSE return target
Direction probability is obtained from the predicted return using the training-period return standard deviation.

### A8 — Temporal Convolution Network (TCN-lite)
A fixed compact dilated-convolution sequence model over the same 30-session history:
- channels 16 -> 16
- kernel_size=3
- dilations 1, 2, 4
- dropout=0.10
- Adam lr=0.003
- 50 epochs
- MSE return target

### Fixed ensembles
- NEW_EQUAL_8 = equal-weight probability average of A1–A8.
- TREE_EQUAL_3 = equal-weight probability average of A1–A3.
No holdout-derived weights are used.

## Features
The same Phase-33 point-in-time event feature set is used:
- NIFTY returns, volatility, ranges, drawdowns, RSI, MACD and moving-average gaps;
- prior-session global markets;
- point-in-time sentiment where available;
- backward-looking FII/DII flows;
- exact-time option-chain diagnostics where available.
For the sequence models, only completed NIFTY trading sessions strictly before the D−6 reference date are used.

## Leakage controls
- All imputers/scalers fit only on the fitting period.
- Sequence windows end before the reference date.
- HMM uses only data before each reference.
- Same-day global markets that were still open at the reference are shifted to previous-session values.
- FII/DII joins are backward-only.
- No forward-return fields are used as features.
- Holdout remains untouched until all model code and parameters are frozen.

## Statistical analyses
For each model and split:
- accuracy, balanced accuracy, ROC-AUC, log loss, Brier score;
- model-signed horizon log return;
- bootstrap 95% CI for mean signed return;
- comparison against constant/always-up/always-down baselines;
- yearly stability table on validation/holdout where sample size permits.

## Promotion gates
A model is only considered for a future strategy overlay if it:
1. beats the strongest simple baseline and Phase-33 best model on validation without materially worse calibration;
2. remains positive against the strongest baseline on untouched holdout;
3. has a bootstrap interval excluding zero for signed-return performance;
4. remains directionally consistent across subperiods;
5. can be translated into an executable direction chooser with full Paytm Money brokerage, statutory charges, slippage and expiry-gap assumptions.

Failure of any gate means no promotion.

## Phase sequence
1. Freeze plan, pre-registration and literature review.
2. Implement A1–A8 and fixed ensembles using the Phase-33 cache.
3. Run chronological validation and untouched holdout.
4. Generate statistical diagnostics and figures.
5. Review errors, robustness and model-family evidence.
6. Produce manuscript, decision table, limitations and conclusion.
7. Update phase status and main README.
8. Stop. Further model families require a new registered phase.

## Canonical control
Phase 20 remains the canonical trading specification unless a new model passes a separately registered overlay test. Phase 33 is retained as the immediate predecessor and is not modified.
