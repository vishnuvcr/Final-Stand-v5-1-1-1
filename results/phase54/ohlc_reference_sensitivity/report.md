# Phase 54 OHLC-reference sensitivity feasibility audit

**BLOCKED: alternate-threshold eligibility is not computable from the stored parent output.**

- Input rows: 480
- Input SHA-256: 5052dcf08c20fe0bb921db2172ee7845327112a836145fe2eb91732015901abf
- Baseline statuses: {"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}
- Complete per-leg payload rows: 82
- Incomplete per-leg payload rows: 398
- Explicit hard prior-OI blockers with sufficient evidence to reject the full strategy: 100
- Range-excluded rows with complete leg payload: 81

| Threshold (%) | Eligible | Eligible (%) | OI/leg rejected | Entry-data rejected | Range rejected | Reconciled rows |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | — | — | — | — | — | — |
| 3 | — | — | — | — | — | — |
| 4 | — | — | — | — | — | — |
| 5 | — | — | — | — | — | — |
| 6 | — | — | — | — | — | — |
| 8 | — | — | — | — | — | — |
| 10 | — | — | — | — | — | — |
| 12 | — | — | — | — | — | — |
| 15 | — | — | — | — | — | — |
| 20 | — | — | — | — | — | — |
| 1000 | — | — | — | — | — | — |

## Interpretation
- This run did not compute alternate-threshold counts because at least one row lacked sufficient per-leg evidence to classify safely.
- A multi-leg row cannot be assumed eligible from a partial leg payload; the audit fails closed unless an observed prior-OI failure conclusively rejects the whole strategy at every threshold.
- The OHLC high-low/open percentage is a candle-range proxy, not a quoted bid/ask spread or executable liquidity measure.
- This is not a backtest: no exits, fills, fees, costs, P&L, strategy superiority or promotion can be inferred.
