# Phase 42 Pre-registration

## Hypothesis

The Phase-41 zero-override result may reflect an over-conservative uncertainty layer rather than absence of economic-margin ranking information. Sequentially calibrated selective prediction may improve the action/abstention trade-off.

## Frozen predictor set

SPLINE_RIDGE_VIX and EXTRATREES_VIX using the exact Phase-41 feature schema.

## Calibration modes

RAW, ROBUST_MAD_1X, CONFORMAL_80, CONFORMAL_90.

## Conformal definition

At prediction time t, let e_i = |y_i - yhat_i| for the most recent previously observed model predictions. For CONFORMAL_q, q_t is the empirical q quantile of the previous 60 absolute residuals, using at least 20 observations. The lower-confidence economic benefit is predicted benefit minus q_t.

No future residual enters q_t.

## Policy thresholds

Margins: 0, 250, 500 rupees.

Gates: ALL, HIGH_VIX, HIGH_VIX_RISING.

Total = 2 × 4 × 3 × 3 = 72.

## Selection

Development/validation only. The 2026 holdout remains untouched until top-three freezing.

Selection gate:
development uplift >= 0; validation uplift > 0; validation overrides >=5; override rate <=25%; validation DD <=1.25× control.

## Statistical inference

10,000 paired-expiry bootstrap resamples and paired sign-flip test. Primary unit is expiry, not individual trade.

## No-promotion conditions

Any leakage, any post-hoc holdout tuning, negative holdout uplift, insufficient treated observations, material drawdown deterioration, or cost-stress failure blocks promotion.

## Interpretation

Conformal-style intervals are treated as sequential calibration heuristics. Because financial observations may violate exchangeability, no formal distribution-free coverage claim is made.
