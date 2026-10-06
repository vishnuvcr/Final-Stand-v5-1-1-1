# Phase 39 Step 3 — Economic-Margin Model Specification

## Objective

Estimate the post-cost counterfactual margin:
DeltaP&L = CALL_net_P&L - PUT_net_P&L
from information available at the exact historical entry timestamp.

The canonical Phase-38 stateful strategy remains the control. A model is used as an override learner, not as an unconditional classifier.

## Data lock

- Fixed opportunities: 477.
- Development: 271 trades / 135 expiries, through 2023-12-28.
- Validation: 172 trades / 82 expiries, 2024-01-11 through 2025-12-30.
- Holdout: 34 trades / 20 expiries, 2026; not evaluated in Step 3.
- Frozen comparator: validation + holdout control remains ₹63,672.5753.
- All target values are post-cost and include the accepted slippage/cost model.

## Feature eligibility

Predictor eligibility is determined using development data only:

1. exclude all audit/target/control columns;
2. exclude a numeric predictor if development missingness exceeds 50%;
3. exclude a numeric predictor with fewer than 5 distinct non-missing development values;
4. fit all imputers/scalers inside each chronological training window;
5. never use validation or holdout missingness to choose the feature set.

This deliberately excludes FII/DII variables from the primary Step-3 fit because their cached historical publication series are unavailable throughout development. They remain in the feature matrix for later supplemental tests.

## Primary chronological evaluation

### Development walk-forward OOF

- chronological warm-up: first 100 development opportunities;
- expanding training window;
- prediction batches of 20 opportunities;
- repeat until the end of development.
- hyperparameter/override-threshold choices are made only from these OOF predictions.

### Validation replay

Fit each model using all development observations, then predict validation chronologically using the locked feature set and hyperparameters.

No model, feature, or threshold is changed after seeing validation outcomes.

## Model families in Step 3

Primary:
- CROL / Bayesian Ridge economic-margin model;
- Bayesian counterfactual margin regression;
- Bradley–Terry pairwise preference model;
- dynamic Bayesian-style logistic model with recursive forgetting.

Secondary:
- Gaussian-process margin regression;
- sparse spline/GAM-style regularized regression;
- weighted kNN economic-margin analogue.

Step 4 will cover DTW analogue, BOCPD regime gating, online Hedge/model averaging, kernel/SVM, foundation-model exploratory tests, and constrained symbolic regression where practical.

## Action rule

For an estimated margin m_hat and uncertainty s_hat, use the fixed conservative score:

`score = alternative_expected_improvement - 1.0 × uncertainty`.

The uncertainty multiplier is fixed at 1.0 and is not tuned.

The only permitted safety margins are exactly:
- ₹0
- ₹250
- ₹500

The selected margin is chosen from development walk-forward OOF only. Validation and holdout cannot change it.

For a CALL control, alternative_expected_improvement = -m_hat.
For a PUT control, alternative_expected_improvement = +m_hat.
Override only when score > M; otherwise retain the canonical control.

## Primary selection metrics

1. fixed-opportunity validation net P&L;
2. uplift versus canonical control;
3. paired-expiry bootstrap 95% confidence interval for uplift;
4. override share and number of overrides;
5. chronological maximum drawdown on the fixed opportunity sequence;
6. model MAE and rank correlation for DeltaP&L;
7. stability across development OOF windows.

Fixed-opportunity results are model-screening evidence only. Final strategy acceptance requires sequential policy replay because an overridden direction can alter exit time and therefore future entry availability.