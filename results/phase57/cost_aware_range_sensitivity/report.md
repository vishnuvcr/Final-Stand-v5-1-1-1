# Phase 57 — cost-aware OHLC-range sensitivity replay

**Modeled P&L only. Not bid/ask, executable liquidity, portfolio returns, or a strategy recommendation.**

- Revision: `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`
- Configurations: 40; selected development/validation events: 24
- Cost model: ₹20/order primary and ₹10/order sensitivity; date-aware statutory charges; ₹0.05 adverse slippage per leg fill at 0/50/100% stress.

## Replay passes by threshold

| OHLC range threshold (%) | Replay-pass configuration-event rows | Total planned rows |
|---:|---:|---:|
| 2 | 1 | 480 |
| 1000 | 380 | 480 |

## Interpretation

Results are descriptive sensitivity only. Increasing the threshold mechanically admits more high-range bars; this is not evidence of narrower spreads or better fills.
Net P&L summaries aggregate configuration-event rows and must not be interpreted as a single deployable portfolio. The same event appears under multiple configurations.
No strategy, configuration or threshold was selected. Holdout remains untouched, and CC BY-NC source licensing prohibits treating this as commercial/live evidence.

See `threshold_summary.csv`, `family_summary.csv`, `configuration_summary.csv`, `event_outcomes.csv` and `cost_scenarios.csv` for complete ledgers.
