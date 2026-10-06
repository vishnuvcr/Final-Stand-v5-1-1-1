# Phase 39 Step 1 — Fixed-Opportunity Counterfactual Conclusion

## Decision

**PASS / ACCEPTED.** Step 1 is complete and the fixed-opportunity counterfactual panel is the accepted data foundation for Phase 39 model fitting.

## Data provenance

The control ledger was derived from the accepted Phase-32 GitHub Actions artifact:

- Artifact ID: 11380124540
- Source run: 37388261915
- Source member: `results/dynamic_strategy_phase32/trades.csv`

The frozen comparator is retained exactly for the 2024-01-11 through 2026-05-19 period. The 2024-01-04 trade is intentionally excluded so Phase-38 comparator identity is preserved.

## Accepted panel

| Split | Trades | Expiries | Control net P&L |
|---|---:|---:|---:|
| Development | 271 | 135 | ₹17,657.15 |
| Validation | 172 | 82 | ₹63,948.22 |
| Untouched holdout | 34 | 20 | -₹275.65 |
| Validation + holdout frozen comparator | 206 | 102 | ₹63,672.58 |

Control reconstruction is effectively exact: maximum absolute error is below ₹2e-12 per trade across the complete accepted panel.

## Counterfactual findings

The target is:

`DeltaP&L = CALL_net - PUT_net`

The fixed-opportunity results are:

| Split | CALL net | PUT net | Mean DeltaP&L | Positive Delta share |
|---|---:|---:|---:|---:|
| Development | -₹25,248.33 | ₹61,615.75 | -₹320.53 | 52.0% |
| Validation | ₹61,240.45 | -₹5,284.71 | ₹386.77 | 59.3% |
| Holdout | ₹59,448.21 | -₹55,686.28 | ₹3,386.31 | 79.4% |

CALL beats PUT on 270 of 477 accepted opportunities; PUT beats CALL on 207; there are no ties.

These are **counterfactual opportunity results, not trading-policy results**. The complete fixed panel evaluates both possible actions at each historical entry timestamp. A learned policy can realize only one action, and that action can change the future sequence of entry/exit opportunities. Therefore the final claim must come from the preregistered sequential replay.

## Interpretation

The most important scientific signal is the change in the economic margin across time:

- development favors PUT on average;
- 2024–2025 validation shifts toward CALL;
- the 2026 holdout has a substantially stronger CALL advantage.

This supports testing adaptive and uncertainty-aware economic-margin learners. It does **not** justify selecting CALL as a static rule, because the development period points the opposite way.

## Controls and execution assumptions

The panel uses the frozen Continuous Delta 6x6 mechanics:

- six lots per leg;
- 50-point vertical;
- +0.25 CE / -0.25 PE short-leg entry delta;
- first short-leg delta exit at 0.50 or 0.04 magnitude;
- contract termination when no delta exit occurs;
- one-tick adverse slippage;
- brokerage and statutory/exchange charges;
- historical lot-size schedule;
- deterministic last-observation quote handling.

The historical implementation remains a 1-minute reproducible approximation of the continuous/tick-driven live concept.

## Step 1 limitations

The fixed opportunity ledger does not yet include the full point-in-time feature layer required for model fitting. The oracle uplift is therefore not evidence of realizable performance and must not be reported as a strategy return.

## Next step

Build and audit the point-in-time feature matrix, then fit the preregistered candidate families chronologically. The 2026 holdout remains untouched for model selection and threshold tuning.
