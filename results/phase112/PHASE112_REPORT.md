# Phase 112 — Greek Stop-Loss Combination Report

Generated UTC: 2026-10-24T07:03:44.109685+00:00
Status: EMPIRICAL_SCREEN_COMPLETE_NO_PROMOTION; strategy promotion: NONE.

## Coverage
Dataset revision 0f4800e43e6f96cec0794369d78eb4d3c4211ef5; expiries 2021-05-27 through 2026-08-04.
Scheduled / eligible / excluded: 259 / 139 / 124.
Eligible by split: {"development": 93, "validation": 45, "holdout": 1}; exclusion reasons: {"INCOMPLETE_OPTION_PATH": 50, "INCOMPLETE_SPOT_PATH": 1, "INVALID_MONITORING_IV": 3, "INVALID_SESSION_GRID": 1, "MISSING_INVALID_OR_DUPLICATE_ENTRY_BAR": 17, "NO_CONFIRMED_PIVOT_SIGNAL": 22, "NO_NEXT_OBSERVED_SESSION": 4, "NO_VALID_ABS_0_10_DELTA_CONTRACT": 22, "PREVIOUS_EXPIRY_DAILY_CANDLE_INCOMPLETE": 2, "UNSUPPORTED_HISTORICAL_LOT_SIZE_DATE": 2}.

## Frozen candidate design
72 candidates: 19 single-Greek threshold variations, 52 multi-Greek subset rules (OR/AND), and no-stop baseline.
Fixed multi-Greek thresholds: {"delta": 0.5, "gamma": 0.2, "rho": 0.0005, "theta": 0.25, "vega": 0.2}. Full thresholds are in PHASE112_RESEARCH_PLAN.md and candidate_registry.json.
Gamma is normalized as a 0.5% spot-shock convexity estimate/entry premium; Vega as 5 IV-points impact/entry premium; Theta relative to entry short-theta; Rho as rate-point sensitivity/entry premium.
Every completed-minute trigger fills at next exact observed minute open. The 24 cost scenarios include date-effective modeled charges and slippage.

## Primary cost case B20_S0.25_F1.0
| Split | Candidate | Trades/expected | Net P&L ₹ | Mean ₹ | Win % | Max DD ₹ | Stop % | Uplift vs no-stop ₹ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| development | NO STOP | 93/133 | 24244.61 | 260.69 | 86.0 | 7192.71 | 0.0 | — |
| development | DELTA=0.5 | 93/133 | 7116.47 | 76.52 | 81.7 | 13666.73 | 12.9 | -17128.13 |
| validation | NO STOP | 45/103 | 10854.87 | 241.22 | 86.7 | 3663.00 | 0.0 | — |
| validation | DELTA=0.5 | 45/103 | 7066.39 | 157.03 | 86.7 | 5133.91 | 11.1 | -3788.48 |
| holdout | NO STOP | 1/23 | 2051.41 | 2051.41 | 100.0 | 0.00 | 0.0 | — |
| holdout | DELTA=0.5 | 1/23 | 2051.41 | 2051.41 | 100.0 | 0.00 | 0.0 | 0.00 |

Full 72 × 24 × 3 rows are in candidate_cost_grid.csv. Primary-cost campaign records are in campaign_ledger_primary.csv.
Holdout is not used to select a winner. Bootstrap intervals and one-sided tests are descriptive only and the grid creates multiple-comparison risk.

## Decision and limitations
No strategy is promoted. The supplied Pine source imports external DevLucem/ZigLib/1, whose library body was not provided; the Python pivot engine remains a causal proxy. Minute Black–Scholes Greeks, fixed rate/yield, partial CC BY-NC 4.0 option data, OHLC simulated fills and approximate Paytm Money cost assumptions limit conclusions. A sparse holdout or nominal p-value is not proof of an edge.

## Artifacts
- summary.json, coverage.json, candidate_registry.json, source_manifest.csv, scheduled_campaigns.csv, campaign_exclusions.csv
- candidate_cost_grid.csv and campaign_ledger_primary.csv
- results/phase112/figures/primary_costs_development.svg
- results/phase112/figures/primary_costs_validation.svg
- results/phase112/figures/primary_costs_holdout.svg
