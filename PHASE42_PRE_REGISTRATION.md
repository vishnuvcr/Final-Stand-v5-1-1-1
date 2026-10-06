# Phase 42 Pre-registration

## Benchmark

Canonical Phase-32/38 stateful strategy.

## Target

DeltaP&L = CALL net P&L minus PUT net P&L.

For a canonical CALL control, directional benefit = -predicted DeltaP&L.
For a canonical PUT control, directional benefit = predicted DeltaP&L.

## Model

SPLINE_RIDGE_VIX only:
- SplineTransformer n_knots = 4
- degree = 2
- Ridge alpha = 10
- same fixed Phase-41 feature layer and VIX interactions
- expanding-window fit
- warm-up = 100 opportunities

## Selective score

score = directional predicted benefit.

No uncertainty subtraction is permitted in Phase 42.

Current score must be positive.

## Rank cutoffs

The score threshold is the corresponding empirical quantile of all prior finite scores:
- TOP_5: prior 95th percentile
- TOP_10: prior 90th percentile
- TOP_20: prior 80th percentile

No current or future observation may enter the percentile reference set.

## Routing gates

- ALL
- HIGH_VIX

Declared candidates: 6.

## Selection

Development/validation only:
- development uplift >= 0;
- validation uplift > 0;
- validation overrides >= 5;
- validation override rate <= 20%;
- validation drawdown <= 1.25 × control.

Top three freeze before holdout.

## Statistical tests

- paired-expiry bootstrap: 10,000 resamples;
- paired sign-flip;
- 95% confidence intervals;
- economic risk-coverage diagnostics;
- propensity matching only where overrides exist and only with pre-evaluation propensity fitting.

## Holdout

2026 remains untouched until the three candidates are frozen.

## Execution assumptions

The canonical execution engine is retained unchanged:
- one adverse tick of slippage;
- brokerage and statutory charges;
- historical lot sizes;
- exact cached option timestamps;
- same entry/exit mechanics as the canonical strategy.

## Decision labels

PROMOTE only if every Phase-42 promotion gate passes.
Otherwise NO PROMOTION.
