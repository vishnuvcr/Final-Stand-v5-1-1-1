# Phase 42 Research Plan — Rank-to-Action Selective Policy

## Motivation

Phase 41 produced a clear methodological split. The registered uncertainty-penalized policies never overrode the canonical stateful strategy, so all six frozen diagnostics were exact no-ops at the trading layer. Yet the leading score retained economically meaningful ranking power: the highest-scored 10% of validation opportunities had positive observed counterfactual DeltaP&L, and the 2026 holdout top decile was also positive.

This creates a bounded next question:

> Does the observed counterfactual ranking signal translate into a robust trading policy when selection is defined by ex-ante score rank rather than an overly conservative absolute uncertainty penalty?

Phase 42 therefore does not introduce a new classifier family. It tests the leading Phase-41 economic-margin learner as a selective decision system.

## Research questions

1. Does raw predicted directional economic benefit contain usable selective-ranking information after the Phase-41 uncertainty penalty is removed?
2. Can a small, pre-registered coverage-controlled policy capture that ranking signal without excessive overrides or drawdown?
3. Does the selective rule survive exact sequential replay, the untouched 2026 holdout and realistic cost/slippage?
4. Does India-VIX still add value as a routing gate once rank controls the action coverage?

## Primary aim

Determine whether the leading Phase-41 economic-margin model can be converted from a ranking signal into a statistically and economically robust sparse override policy.

## Registered candidate universe

Only the leading Phase-41 model is used:

- SPLINE_RIDGE_VIX: 4-knot quadratic spline transform + Ridge alpha 10, with the same fixed point-in-time features and India-VIX interaction layer used in Phase 41.

Action score:
- directional predicted benefit relative to the current canonical control;
- no residual-MAD uncertainty subtraction;
- current predicted benefit must be strictly positive;
- score percentile is computed against past observed model scores only.

Coverage controls:
- TOP_5: current score at or above the historical 95th percentile;
- TOP_10: historical 90th percentile;
- TOP_20: historical 80th percentile.

Routing:
- ALL;
- HIGH_VIX.

Declared variants: 1 model × 3 rank cutoffs × 2 gates = 6.

No additional threshold family, model architecture or learned ensemble weight may be added after results are observed.

## Point-in-time and chronology rules

- Use the accepted Phase-39 477-opportunity panel.
- Development = 271 opportunities / 135 expiries.
- Validation = 172 opportunities / 82 expiries.
- Holdout = 34 opportunities / 20 expiries.
- Warm-up = 100 observed opportunities.
- The current score may use only features available strictly before the entry timestamp.
- The percentile reference distribution contains only previously observed model scores.
- The holdout is not examined for selection.

## Fixed-opportunity selection gate

For each of the six variants calculate development and validation:
- total uplift vs canonical control;
- mean uplift per opportunity and expiry;
- override count and rate;
- maximum drawdown;
- positive-expiry share.

Selection requires:
1. development uplift >= 0;
2. validation uplift > 0;
3. at least 5 validation overrides;
4. validation override rate <= 20%;
5. validation maximum drawdown <= 1.25 × control.

If none passes, retain the top three validation-ranked variants as diagnostic-only candidates and close the phase as NO PROMOTION.

If candidates pass, freeze the top three before the 2026 holdout is examined.

## Selective-ranking diagnostics

For the leading frozen candidate report:
- mean DeltaP&L and 95% bootstrap CI at 5%, 10% and 20% score coverage;
- positive-share at each coverage;
- economic risk-coverage curve;
- coverage versus cumulative counterfactual uplift;
- monotonicity across score quantiles;
- propensity-matched overlap where actual overrides exist.

The ranking diagnostics are descriptive and do not by themselves justify a trading promotion.

## Exact sequential replay

Top three frozen candidates are replayed through the exact canonical engine:
- no overlapping positions;
- established Continuous Delta 6x6 vertical structure;
- historical lot sizes;
- exact option timestamps and exit rules;
- one adverse tick slippage;
- brokerage and statutory charges;
- same canonical stateful shadow direction;
- every override can change exit time and therefore later opportunities.

The replay is authoritative for the trading claim.

## Statistical inference

Primary:
- paired-expiry bootstrap, 10,000 resamples;
- paired sign-flip test;
- 95% CI for mean and total incremental P&L.

Secondary:
- win rate;
- profit factor;
- maximum drawdown;
- override concentration by expiry;
- +25%, +50%, +100% aggregate cost stress;
- call/put action asymmetry;
- ranking coverage diagnostics.

## Promotion gate

No Phase-42 candidate may replace the canonical strategy unless all of the following hold:
1. positive sequential validation uplift;
2. positive untouched 2026 holdout uplift;
3. paired-expiry lower 95% CI is non-negative in both validation and holdout;
4. validation and holdout drawdown are no worse than 1.25× control;
5. +50% cost-stress uplift remains positive;
6. at least 5 untouched holdout overrides;
7. no single holdout expiry contributes more than 40% of total positive OOS uplift;
8. no leakage or execution audit defect;
9. ranking benefit is monotone or at least not materially inverted between validation and holdout.

## Literature and external evidence

Selective prediction literature frames the trade-off between coverage and reliability rather than treating every model output as an action. Gangrade et al. (AISTATS 2021) explicitly studies selective prediction and coverage/error trade-offs. Conformal prediction has also been studied for reliable financial stock selection, reinforcing the value of calibrated abstention/selection rather than unconditional prediction. The policy-learning and ranking literature used in Phase 41 remains directly relevant.

## Stop condition

Phase 42 closes after:
1. fixed six-variant ranking screen;
2. top-three freeze before holdout;
3. sequential replay;
4. ranking/coverage diagnostics;
5. propensity diagnostics where possible;
6. cost/slippage stress;
7. complete manuscript, logs, status and README update.

A materially different mechanism requires Phase 43.
