# Phase 41 Pre-registration

## Benchmark

Canonical Phase-32/38 stateful Continuous Delta 6x6 strategy. It remains the default action and the only promoted historical benchmark.

## Outcome

Primary economic margin:

DeltaP&L = CALL_net_P&L - PUT_net_P&L.

For a canonical CALL state, the benefit of overriding is -DeltaP&L.
For a canonical PUT state, the benefit of overriding is +DeltaP&L.

## Models

A. VIX-interaction Sparse-GAM/Ridge:
- fixed low-dimensional feature list;
- SplineTransformer: 4 knots, degree 2;
- Ridge alpha = 10;
- explicit high-VIX and high-VIX+rising interaction terms.

B. VIX-aware ExtraTrees:
- 150 trees;
- max_depth = 5;
- min_samples_leaf = 8;
- random_state = 4101;
- n_jobs = 2;
- no post-hoc tuning.

## Fixed feature list

- nifty_ret_15m
- nifty_ret_60m
- nifty_ret_240m
- nifty_rv_30m
- nifty_rv_120m
- nifty_daily_rv_20d
- nifty_drawdown_20d
- nifty_gap_from_prev_close
- atm_iv_skew
- atm_pcr_oi
- atm_pcr_volume
- candidate_iv_skew_25
- candidate_credit_diff_call_minus_put
- global_SP500_ret1
- global_NASDAQ_ret1
- global_NIKKEI_ret1
- global_USDINR_ret1
- global_GOLD_ret1
- global_CRUDE_ret1
- flow_fii_net_z20
- flow_dii_net_z20
- flow_flow_sentiment
- India-VIX level, return and regime flags from the cached Phase-40 series

The target columns delta_pnl_call_minus_put, call_net_rupees, put_net_rupees, control_net_rupees, recalculated_control_net_rupees and any exit/P&L outcome fields are excluded from predictors.

## VIX thresholds

Recomputed only from pre-2024 India VIX observations:
- high regime = prior available VIX close >= development q67;
- rising regime = prior-session percentage change >= development q67 of VIX absolute/one-day return distribution;
- high+rising = conjunction.

## Chronology

Rows are ordered by entry_ts. A row may use only information from earlier rows/dates. Warm-up = 100 rows.

## Policy variants

2 learners × 4 override margins × 3 routing gates = 24 variants.

Margins:
0, 250, 500, 1000 rupees.

Routing:
ALL, HIGH_VIX, HIGH_VIX_RISING.

Uncertainty penalty:
1.0 × recent residual MAD scale. Recent scale window = 60 observed training residuals; minimum scale = ₹50.

## Validation selection gate

Development uplift >= 0.
Validation uplift > 0.
Validation overrides >= 5.
Validation override rate <= 25%.
Validation max drawdown <= 1.25 × control max drawdown.

Top three validation candidates are frozen before 2026 results are examined.

## Propensity-matched scoring

Treatment = override.
Outcome = DeltaP&L.
Ten state variables are fixed before fitting the propensity model.
Logistic regression is fit on the non-holdout history only.
Validation and holdout matching:
- same VIX regime;
- logit-propensity caliper 0.05;
- nearest available non-treated observation;
- without replacement.

If overlap is insufficient, ATT is reported as not identifiable. No candidate may be promoted based on matching alone.

## Primary statistics

- 10,000 paired expiry bootstrap resamples;
- paired sign-flip p-value;
- 95% confidence intervals;
- maximum drawdown;
- profit factor;
- win rate;
- override concentration;
- cost/slippage stress.

## Holdout discipline

The 2026 holdout is untouched during variant selection.
The top three are frozen from development/validation only, then replayed on the holdout once.

## Decision labels

PROMOTE only if the sequential promotion gate in PHASE41_RESEARCH_PLAN.md is fully satisfied.
Otherwise classify as:
- PROMISING / INCONCLUSIVE;
- WEAK / NO PROMOTION; or
- REJECTED / NEGATIVE.

No intermediate result is a live-trading recommendation.
