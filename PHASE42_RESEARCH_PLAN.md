# Phase 42 Research Plan — Confidence Calibration and Selective Counterfactual Routing

## Motivation

Phase 41 produced an important two-part result: all 24 preregistered regime-conditional policies made **zero overrides**, so their trading action was exactly the canonical control; however, the frozen leading score still ranked observed CALL-versus-PUT counterfactual margins positively in the top 10% of validation and holdout observations. This separates two questions:

1. Is the economic-margin model ranking informative?
2. Is its uncertainty/abstention layer too conservative to convert that ranking into an actionable policy?

Phase 42 tests that distinction directly. It does **not** revisit the Phase-41 feature universe, add new market variables, or inspect the holdout for tuning.

## Research questions

1. Does point-prediction ranking contain reproducible control-relative economic information?
2. Can sequentially calibrated uncertainty produce an actionable selective policy without sacrificing OOS robustness?
3. Does conformal-style calibration improve the trade-off between override frequency and false overrides?
4. Does calibration remain useful across India-VIX regimes?
5. Can a selective policy beat the canonical stateful strategy after realistic costs and slippage?

## Aims

### Primary aim
Determine whether a pre-registered confidence-calibration/abstention layer can safely convert the Phase-41 ranking signal into a robust economic-margin override policy.

### Secondary aims
- quantify calibration quality of economic-margin forecasts;
- compare raw score, rolling robust uncertainty and sequential conformal lower bounds;
- measure coverage/error trade-offs;
- test VIX routing without changing the predictor feature set;
- preserve the canonical strategy as default unless all promotion gates pass.

## Fixed data

Reuse exactly the accepted Phase-39 fixed-opportunity panel:
- 477 opportunities;
- 271 development;
- 172 validation;
- 34 untouched 2026 holdout;
- both CALL and PUT counterfactual net P&L;
- same point-in-time feature matrix;
- same India-VIX cache.

No new raw-data acquisition is required for the primary experiment.

## Predictor family

Exactly the two Phase-41 learners:
1. SPLINE_RIDGE_VIX;
2. EXTRATREES_VIX.

The predictor feature matrix is frozen. The only new object is the calibration/abstention layer.

## Calibration families

Four declared score modes:

1. **RAW** — economic benefit = predicted counterfactual improvement; no uncertainty subtraction.
2. **ROBUST_MAD** — subtract 1.0 × rolling residual MAD scale, exactly the Phase-41 uncertainty rule, retained as a control.
3. **CONFORMAL_80** — subtract the rolling 80th percentile of absolute past residuals.
4. **CONFORMAL_90** — subtract the rolling 90th percentile of absolute past residuals.

Calibration window: 60 previously observed predictions/residuals, with a minimum 20 before a calibrated score is actionable.

The conformal scores are sequential/rolling rather than randomly split because the research data are time ordered and potentially non-exchangeable. Formal finite-sample conformal guarantees are therefore not claimed.

## Policy grid

2 learners × 4 calibration modes × 3 fixed economic margins × 3 routing gates = **72 preregistered variants**.

Economic margins: ₹0, ₹250, ₹500.

Routing:
- ALL;
- HIGH_VIX;
- HIGH_VIX_RISING.

No holdout tuning.

## Chronological protocol

- Warm-up: 100 observations.
- Fit each learner only on observations strictly earlier than the prediction.
- Calibration uses only predictions that were already generated strictly earlier.
- No random CV.
- Development determines model/calibration/gate ranking.
- Validation selects the top three.
- 2026 holdout is evaluated once after freezing those three.

## Primary selection gate

A candidate must satisfy:
- development uplift >= 0;
- validation uplift > 0;
- at least 5 validation overrides;
- validation override rate <= 25%;
- validation drawdown <= 1.25× canonical control drawdown.

If no candidate passes, freeze the top three validation-ranked candidates for diagnostic replay only.

## Secondary calibration diagnostics

For every learner and calibration mode:
- mean absolute error;
- median absolute error;
- signed bias;
- rank correlation between predicted score and observed DeltaP&L;
- top 10/20/30% observed DeltaP&L;
- calibration-width distribution;
- override precision = fraction of overrides with realized positive counterfactual benefit;
- selective risk/coverage curve.

These are diagnostics, not additional selection criteria unless explicitly pre-registered above.

## Propensity matching

For the frozen leading policy only:
- treatment = override;
- outcome = observed counterfactual benefit relative to canonical action;
- propensity model fitted only on pre-evaluation history;
- same VIX regime matching;
- 0.05 propensity caliper;
- without replacement.

If there are fewer than 5 treated observations or inadequate common support, ATT is reported as not identifiable.

## Exact sequential replay

Top three frozen candidates are replayed through the exact chronological strategy engine. A changed direction is allowed to alter the future entry/exit path. Historical lot sizes, one adverse tick slippage, brokerage and statutory charges remain unchanged.

## Statistical analysis

Primary:
- paired expiry bootstrap, 10,000 resamples;
- paired sign-flip test;
- 95% CI for mean and total incremental P&L.

Secondary:
- profit factor;
- win rate;
- max drawdown;
- override contribution concentration;
- calibration/ranking metrics;
- +25%, +50%, +100% cost stress;
- slippage sensitivity if supported by the fixed engine.

## Promotion gate

A Phase-42 candidate may replace the canonical strategy only if all are true:
1. positive validation sequential uplift;
2. positive untouched 2026 holdout uplift;
3. at least 5 holdout overrides;
4. validation and holdout drawdown <= 1.25× control;
5. positive +50% cost-stress uplift in both validation and holdout;
6. paired-expiry 95% CI does not materially favor control;
7. no single expiry contributes >40% of positive OOS uplift;
8. no material CALL/PUT asymmetry;
9. no leakage/execution defects.

## Stop condition

Phase 42 ends after:
1. all 72 variants are screened;
2. top three are frozen before holdout;
3. exact sequential replay is complete;
4. calibration and ranking diagnostics are complete;
5. final statistical inference and manuscript are persisted.

A further model family requires Phase 43.
