# Phase 39 Modeling Specification — Fixed-Opportunity Economic-Margin Screening

## Status

Locked before Phase-39 model fitting.

## Target

`delta_pnl = CALL_net_rupees - PUT_net_rupees`.

The target is the same two-action economic difference used in the accepted Step-1 fixed-opportunity ledger.

## Chronology

- Development labels: 2021-05-27 through 2023-12-28.
- Validation labels: 2024-01-11 through 2025-12-30.
- Holdout labels: 2026-01-06 through 2026-05-19.
- The 2026 holdout is not used for feature selection, model selection, threshold selection or hyperparameter selection.

For validation, each opportunity is predicted using all prior development observations plus prior validation observations only.

For holdout, after validation selection is frozen, each opportunity is predicted using prior development/validation observations plus prior holdout observations only.

## Feature eligibility

At every fit:
1. Remove identifiers and outcome columns.
2. Exclude any feature with more than 80% missingness in the current training window.
3. Impute remaining missing numeric values with training-window medians.
4. Standardize using training-window parameters.
5. Select at most 24 features by absolute Spearman correlation with the economic target, computed only inside the current training window.
6. Re-select features chronologically whenever the training window changes.

No future observation may influence imputation, scaling or feature selection.

## Registered model set

### M1 — Bayesian economic-margin model
Bayesian Ridge regression on standardized features.

Fixed parameters:
- `alpha_1=1e-6`
- `alpha_2=1e-6`
- `lambda_1=1e-6`
- `lambda_2=1e-6`

The posterior predictive mean and standard deviation are used directly.

### M2 — Robust economic-margin model
Huber regression.

Fixed parameters:
- `epsilon=1.35`
- `alpha=1e-4`
- `max_iter=2000`

Uncertainty is the training residual MAD scaled to an equivalent normal standard deviation.

### M3 — Additive spline economic-margin model
Fixed cubic spline expansion followed by ridge regression.

Fixed parameters:
- 4 knots per feature
- degree 3
- ridge alpha 10

Uncertainty is the training residual standard deviation.

### M4 — Recency-weighted local analog model
Standardized-feature weighted kNN regression.

Fixed parameters:
- (k=min(25, n_{train}))
- distance-weighted predictions
- uncertainty = weighted neighbor absolute deviation

Only past rows are eligible neighbors.

## CROL decision rule

The canonical stateful direction remains the default.

For a CALL control:
- alternative = PUT
- predicted alternative improvement = (-hat{Delta P&L}).

For a PUT control:
- alternative = CALL
- predicted alternative improvement = (hat{Delta P&L}).

Posterior/empirical uncertainty penalty:

[
U = widehat{improvement} - 1.0 	imes uncertainty
]

The uncertainty multiplier is fixed at 1.0 and is not tuned.

Override the control only when:

[
U > m
]

where (m) is one of the preregistered safety margins:
- ₹0
- ₹250
- ₹500

No margin is tuned on the 2026 holdout.

## Fixed-opportunity screening metrics

For each model and margin:
- RMSE / MAE of delta prediction;
- Spearman rank correlation;
- sign accuracy;
- number and percentage of overrides;
- realized counterfactual net P&L of the selected action;
- paired uplift versus canonical control;
- mean/median incremental P&L;
- paired-expiry bootstrap diagnostic;
- maximum drawdown of the opportunity-level selected stream.

These results are a model-screening study, not a final trading-policy claim.

## Promotion to sequential replay

Only models that show positive validation control-relative economics are eligible for sequential replay. The sequential replay then becomes the primary policy test because different actions can produce different exit timestamps and therefore different future opportunities.

The 2026 holdout remains frozen until the sequential policy configuration is locked.
