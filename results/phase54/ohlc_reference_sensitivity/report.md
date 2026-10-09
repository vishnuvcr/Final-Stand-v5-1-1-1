# Phase 54 OHLC-reference sensitivity

**Non-executable diagnostic only. No P&L was recalculated and no strategy was promoted.**

- Input rows: 480
- Baseline statuses: {"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}
- Strict prior-minute OI failure rows: 480

| OHLC range threshold (%) | Rows passing prior-OI + entry-data + range checks | % of 480 | Prior-OI/legs rejected | Entry-data rejected | Range rejected |
|---:|---:|---:|---:|---:|---:|
| 2 | 0 | 0.00% | 480 | 0 | 0 |
| 3 | 0 | 0.00% | 480 | 0 | 0 |
| 4 | 0 | 0.00% | 480 | 0 | 0 |
| 5 | 0 | 0.00% | 480 | 0 | 0 |
| 6 | 0 | 0.00% | 480 | 0 | 0 |
| 8 | 0 | 0.00% | 480 | 0 | 0 |
| 10 | 0 | 0.00% | 480 | 0 | 0 |
| 12 | 0 | 0.00% | 480 | 0 | 0 |
| 15 | 0 | 0.00% | 480 | 0 | 0 |
| 20 | 0 | 0.00% | 480 | 0 | 0 |
| 1000 | 0 | 0.00% | 480 | 0 | 0 |

## Interpretation
- The OHLC high-low/open percentage is a candle-range proxy, not a quoted spread or executable liquidity measure.
- Relaxing this threshold changes only a diagnostic eligibility count; it does not establish valid exits, fills, profitability or strategy superiority.
- Rows blocked by missing/zero strictly prior-minute OI remain blocked under every threshold.
- This output is not a backtest and cannot be used to promote a strategy or tune a live selector.
