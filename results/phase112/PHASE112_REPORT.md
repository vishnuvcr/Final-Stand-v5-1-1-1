# Phase 112 — Greek Stop-Loss Combination Report

Generated UTC: 2026-10-24T07:16:11.288516+00:00
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

## Pooled all-available-data comparison (development + validation + holdout)
This is a descriptive aggregate across every eligible campaign, not a replacement for chronological validation. It includes all eligible events and must not be interpreted as an untouched out-of-sample estimate.
| Candidate | Trades / scheduled | Net P&L ₹ | Mean ₹/trade | Win % | Max DD ₹ | Stop % | Uplift vs no-stop ₹ |
|---|---:|---:|---:|---:|---:|---:|---:|
| NO STOP | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | — |
| DELTA=0.5+VEGA=0.2+THETA=0.25+RHO=0.0005|ALL | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| THETA=0.25+RHO=0.0005|ALL | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| VEGA=0.2+THETA=0.25|ALL | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| DELTA=0.5+THETA=0.25|ALL | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| GAMMA=0.2+THETA=0.25|ALL | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| THETA=0 | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| THETA=0.25 | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| GAMMA=0.2+VEGA=0.2+THETA=0.25+RHO=0.0005|ALL | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| VEGA=0.2+THETA=0.25+RHO=0.0005|ALL | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| DELTA=0.5+GAMMA=0.2+VEGA=0.2+THETA=0.25|ALL | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| DELTA=0.5+GAMMA=0.2+THETA=0.25+RHO=0.0005|ALL | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| DELTA=0.5+THETA=0.25+RHO=0.0005|ALL | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| GAMMA=0.2+VEGA=0.2+THETA=0.25|ALL | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| DELTA=0.5+VEGA=0.2+THETA=0.25|ALL | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| DELTA=0.5+GAMMA=0.2+VEGA=0.2+THETA=0.25+RHO=0.0005|ALL | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| GAMMA=0.2+THETA=0.25+RHO=0.0005|ALL | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| DELTA=0.5+GAMMA=0.2+THETA=0.25|ALL | 139/259 | 37150.89 | 267.27 | 86.3 | 7192.71 | 0.0 | 0.00 |
| THETA=0.5 | 139/259 | 35528.27 | 255.60 | 86.3 | 7192.71 | 14.4 | -1622.62 |
| GAMMA=0.3 | 139/259 | 26828.99 | 193.01 | 54.0 | 4596.78 | 51.1 | -10321.90 |
| DELTA=0.3 | 139/259 | 16894.32 | 121.54 | 77.7 | 9404.08 | 20.1 | -20256.56 |
| DELTA=0.5 | 139/259 | 16234.28 | 116.79 | 83.5 | 13666.73 | 12.2 | -20916.61 |
| DELTA=0.5+GAMMA=0.2+VEGA=0.2+RHO=0.0005|ALL | 139/259 | 16234.28 | 116.79 | 83.5 | 13666.73 | 12.2 | -20916.61 |
| DELTA=0.5+GAMMA=0.2|ALL | 139/259 | 16234.28 | 116.79 | 83.5 | 13666.73 | 12.2 | -20916.61 |
| DELTA=0.5+THETA=0.25|ANY | 139/259 | 16234.28 | 116.79 | 83.5 | 13666.73 | 12.2 | -20916.61 |
| DELTA=0.5+VEGA=0.2|ALL | 139/259 | 16234.28 | 116.79 | 83.5 | 13666.73 | 12.2 | -20916.61 |
| DELTA=0.5+RHO=0.0005|ALL | 139/259 | 16234.28 | 116.79 | 83.5 | 13666.73 | 12.2 | -20916.61 |
| DELTA=0.5+GAMMA=0.2+RHO=0.0005|ALL | 139/259 | 16234.28 | 116.79 | 83.5 | 13666.73 | 12.2 | -20916.61 |
| DELTA=0.5+VEGA=0.2+RHO=0.0005|ALL | 139/259 | 16234.28 | 116.79 | 83.5 | 13666.73 | 12.2 | -20916.61 |
| DELTA=0.5+GAMMA=0.2+VEGA=0.2|ALL | 139/259 | 16234.28 | 116.79 | 83.5 | 13666.73 | 12.2 | -20916.61 |
| GAMMA=0.2 | 139/259 | 15526.89 | 111.70 | 31.7 | 3693.43 | 71.2 | -21624.00 |
| DELTA=0.5+GAMMA=0.2+THETA=0.25|ANY | 139/259 | 15526.89 | 111.70 | 31.7 | 3693.43 | 71.2 | -21624.00 |
| GAMMA=0.2+VEGA=0.2+RHO=0.0005|ALL | 139/259 | 15526.89 | 111.70 | 31.7 | 3693.43 | 71.2 | -21624.00 |
| GAMMA=0.2+THETA=0.25|ANY | 139/259 | 15526.89 | 111.70 | 31.7 | 3693.43 | 71.2 | -21624.00 |
| DELTA=0.5+GAMMA=0.2|ANY | 139/259 | 15526.89 | 111.70 | 31.7 | 3693.43 | 71.2 | -21624.00 |
| GAMMA=0.2+RHO=0.0005|ALL | 139/259 | 15526.89 | 111.70 | 31.7 | 3693.43 | 71.2 | -21624.00 |
| GAMMA=0.2+VEGA=0.2|ALL | 139/259 | 15526.89 | 111.70 | 31.7 | 3693.43 | 71.2 | -21624.00 |
| DELTA=0.6 | 139/259 | 12901.06 | 92.81 | 84.9 | 10722.70 | 10.1 | -24249.82 |
| DELTA=0.4 | 139/259 | 7239.81 | 52.08 | 79.9 | 11789.60 | 17.3 | -29911.07 |
| GAMMA=0.1 | 139/259 | -2920.57 | -21.01 | 10.8 | 8240.14 | 92.8 | -40071.46 |
| GAMMA=0.05 | 139/259 | -8922.45 | -64.19 | 1.4 | 8922.45 | 98.6 | -46073.34 |
| VEGA=0.2+RHO=0.0005|ALL | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| VEGA=0.2+RHO=0.0005|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| VEGA=0.2+THETA=0.25|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| GAMMA=0.2+RHO=0.0005|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| GAMMA=0.2+VEGA=0.2|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| DELTA=0.5+RHO=0.0005|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| VEGA=0.2 | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| VEGA=0.3 | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| VEGA=0.05 | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| VEGA=0.1 | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| RHO=0.0001 | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| RHO=0.0025 | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| RHO=0.001 | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| RHO=0.0005 | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| DELTA=0.5+VEGA=0.2|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| THETA=0.25+RHO=0.0005|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| GAMMA=0.2+VEGA=0.2+RHO=0.0005|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| DELTA=0.5+VEGA=0.2+RHO=0.0005|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| GAMMA=0.2+VEGA=0.2+THETA=0.25|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| DELTA=0.5+GAMMA=0.2+RHO=0.0005|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| DELTA=0.5+GAMMA=0.2+VEGA=0.2|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| DELTA=0.5+VEGA=0.2+THETA=0.25|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| DELTA=0.5+THETA=0.25+RHO=0.0005|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| DELTA=0.5+GAMMA=0.2+VEGA=0.2+RHO=0.0005|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| DELTA=0.5+GAMMA=0.2+VEGA=0.2+THETA=0.25|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| GAMMA=0.2+THETA=0.25+RHO=0.0005|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| VEGA=0.2+THETA=0.25+RHO=0.0005|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| DELTA=0.5+VEGA=0.2+THETA=0.25+RHO=0.0005|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| DELTA=0.5+GAMMA=0.2+THETA=0.25+RHO=0.0005|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| GAMMA=0.2+VEGA=0.2+THETA=0.25+RHO=0.0005|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |
| DELTA=0.5+GAMMA=0.2+VEGA=0.2+THETA=0.25+RHO=0.0005|ANY | 139/259 | -10225.76 | -73.57 | 0.7 | 10225.76 | 100.0 | -47376.65 |

Full 72 × 24 × 4 rows (including pooled ALL_AVAILABLE) are in candidate_cost_grid.csv. Primary-cost campaign records are in campaign_ledger_primary.csv.
Holdout is not used to select a winner. Bootstrap intervals and one-sided tests are descriptive only and the grid creates multiple-comparison risk.

## Decision and limitations
No strategy is promoted. The supplied Pine source imports external DevLucem/ZigLib/1, whose library body was not provided; the Python pivot engine remains a causal proxy. Minute Black–Scholes Greeks, fixed rate/yield, partial CC BY-NC 4.0 option data, OHLC simulated fills and approximate Paytm Money cost assumptions limit conclusions. A sparse holdout or nominal p-value is not proof of an edge.

## Artifacts
- summary.json, coverage.json, candidate_registry.json, source_manifest.csv, scheduled_campaigns.csv, campaign_exclusions.csv
- candidate_cost_grid.csv and campaign_ledger_primary.csv
- results/phase112/figures/primary_costs_development.svg
- results/phase112/figures/primary_costs_validation.svg
- results/phase112/figures/primary_costs_holdout.svg
