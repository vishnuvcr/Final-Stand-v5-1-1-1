# Phase 56 OHLC price-reference P&L sensitivity

**NON-EXECUTABLE PRICE-REFERENCE SENSITIVITY — not a quote-based backtest, liquidity validation, or strategy recommendation.**

- Input rows: 480
- Input SHA-256: 8b0a1167573fdbd7ee32c77bcf493b79db23f8eeeb67aa92700a15c4e8c3683f
- Pinned revision: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
- Parent status counts: {"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}
- Full selected-leg payload rows: 480
- Hard prior-OI-blocked rows rejected at all thresholds: 100
- Price-reference scenario rows: 18960
- Configurations passing the severe-cost screen at any threshold: 5

## Threshold sensitivity: eligibility and pooled grid diagnostics

Pooled figures below aggregate configuration-event rows with overlapping dates/strategies. They are not a single portfolio P&L or an investable equity curve.

| Range threshold | Eligible rows | Net grid sum ₹10/order + ₹0.05 slip | Net grid sum ₹20/order + ₹0.50 slip |
|---:|---:|---:|---:|
| 2% | 1 | ₹-166.19 (1 rows) | ₹-214.80 (1 rows) |
| 3% | 1 | ₹-166.19 (1 rows) | ₹-214.80 (1 rows) |
| 4% | 8 | ₹13115.04 (8 rows) | ₹12312.13 (8 rows) |
| 5% | 24 | ₹-1864.05 (24 rows) | ₹-4231.65 (24 rows) |
| 6% | 55 | ₹-10397.39 (55 rows) | ₹-17151.22 (55 rows) |
| 8% | 91 | ₹-15196.81 (91 rows) | ₹-26407.31 (91 rows) |
| 10% | 150 | ₹7426.04 (150 rows) | ₹-10386.81 (150 rows) |
| 12% | 227 | ₹9673.12 (227 rows) | ₹-18464.68 (227 rows) |
| 15% | 298 | ₹45114.40 (298 rows) | ₹7183.14 (298 rows) |
| 20% | 345 | ₹40144.70 (345 rows) | ₹-3138.02 (345 rows) |
| 1000% | 380 | ₹55926.12 (380 rows) | ₹7902.95 (380 rows) |

## Interpretation

- The range thresholds were preregistered in Phase 54, before Phase 56 P&L is computed; no threshold is selected from P&L results.
- Every aggregate across configurations is a parameter-grid diagnostic, not a deployable portfolio. Configurations reuse dates and overlapping contract opportunities.
- An OHLC open is a price reference only; it does not prove that the corresponding fill was available. The OHLC high-low/open proxy is not a quoted bid/ask spread.
- The fixed prior-minute OI minimum of 100, event/configuration universe, exact entry/exit timestamps, source revision and holdout boundary are unchanged.
- No p-values, confidence intervals, strategy ranking or profitability/generalization claim is made. Any severe-cost screen pass is only a lead for separately licensed/authorized quote validation.
- The source declares CC BY-NC 4.0; commercial use and live-strategy promotion remain outside scope and prohibited by the source/licensing gate.

## Detailed machine-readable output

- \`eligibility_by_threshold.csv\`: every input row at every threshold, including exclusions and hard OI blockers.
- \`trade_scenarios.csv\`: every eligible configuration-event row under every threshold and all 12 cost scenarios.
- \`configuration_summary.csv\`: complete configuration × threshold × cost matrix, including zero-eligibility rows.
- \`family_summary.csv\`: family-pooled descriptive summaries; these also are not portfolio returns.
- \`threshold_summary.csv\`: 132 threshold × brokerage × slippage summaries.
- \`robustness_screen.csv\`: every configuration × threshold at ₹20/order and ₹0.50 adverse slippage per fill; pass only means a lead for future quote-validated research.
