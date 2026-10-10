# Phase 54 OHLC-reference sensitivity results

**COMPUTED — coverage sensitivity only. No P&L or executable liquidity claim.**

- Input rows: 480
- Input SHA-256: fbae8f080a685b2bafcc1248995b9342fea4c598110916e42296bee1af57dd55
- Baseline statuses: {"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}
- Complete per-leg payload rows: 480
- Incomplete per-leg payload rows: 0
- Explicit hard prior-OI blockers with sufficient evidence to reject the full strategy: 100
- Range-excluded rows with complete leg payload: 379

| Threshold (%) | Eligible | Eligible (%) | OI/leg rejected | Entry-data rejected | Range rejected | Reconciled rows |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 1 | 0.208 | 100 | 0 | 379 | 480 |
| 3 | 1 | 0.208 | 100 | 0 | 379 | 480 |
| 4 | 8 | 1.667 | 100 | 0 | 372 | 480 |
| 5 | 24 | 5.000 | 100 | 0 | 356 | 480 |
| 6 | 55 | 11.458 | 100 | 0 | 325 | 480 |
| 8 | 91 | 18.958 | 100 | 0 | 289 | 480 |
| 10 | 150 | 31.250 | 100 | 0 | 230 | 480 |
| 12 | 227 | 47.292 | 100 | 0 | 153 | 480 |
| 15 | 298 | 62.083 | 100 | 0 | 82 | 480 |
| 20 | 345 | 71.875 | 100 | 0 | 35 | 480 |
| 1000 | 380 | 79.167 | 100 | 0 | 0 | 480 |

## Interpretation
- Threshold counts are descriptive eligibility/coverage diagnostics only; they do not validate executable fills, bid/ask spread, exits or profitability.
- The 100 rows explicitly blocked by observed prior-bar OI below the fixed minimum remain rejected at every threshold. The remaining leg payload is unnecessary for those rows because one required leg failure is sufficient to reject the complete multi-leg strategy.
- Every range-excluded row and the single baseline replay-pass row has a complete selected-leg payload; alternate thresholds were computed only from those leg-specific OI, entry-status and range-proxy fields.
- The OHLC high-low/open percentage is a candle-range proxy, not a quoted bid/ask spread or executable liquidity measure.
- No P&L, fill, exit, transaction-cost, Sharpe, drawdown or strategy ranking calculations were performed; no holdout used and no strategy promoted.
- The pinned source is declared CC BY-NC 4.0; commercial/live strategy promotion remains prohibited by the source-license and execution-data gates.
