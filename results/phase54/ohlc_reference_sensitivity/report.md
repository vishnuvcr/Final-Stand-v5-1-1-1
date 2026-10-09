# Phase 54 OHLC-reference sensitivity feasibility audit

**BLOCKED: alternate-threshold eligibility is not computable from the stored parent output. No P&L was recalculated.**

- Input rows: 480
- Baseline statuses: {"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}
- Complete per-leg payload rows: 102
- Incomplete per-leg payload rows: 378
- Empty leg payload rows: 0
- Partial leg payload rows: 378
- Range-excluded rows with complete leg payload: 81

| Threshold (%) | Sensitivity computable? | Result |
|---:|:---:|---|
| 2 | No | Not computed: parent event_replay output does not preserve complete per-leg evidence for every row. Replaying the threshold from partial payload would invent leg coverage. |
| 3 | No | Not computed: parent event_replay output does not preserve complete per-leg evidence for every row. Replaying the threshold from partial payload would invent leg coverage. |
| 4 | No | Not computed: parent event_replay output does not preserve complete per-leg evidence for every row. Replaying the threshold from partial payload would invent leg coverage. |
| 5 | No | Not computed: parent event_replay output does not preserve complete per-leg evidence for every row. Replaying the threshold from partial payload would invent leg coverage. |
| 6 | No | Not computed: parent event_replay output does not preserve complete per-leg evidence for every row. Replaying the threshold from partial payload would invent leg coverage. |
| 8 | No | Not computed: parent event_replay output does not preserve complete per-leg evidence for every row. Replaying the threshold from partial payload would invent leg coverage. |
| 10 | No | Not computed: parent event_replay output does not preserve complete per-leg evidence for every row. Replaying the threshold from partial payload would invent leg coverage. |
| 12 | No | Not computed: parent event_replay output does not preserve complete per-leg evidence for every row. Replaying the threshold from partial payload would invent leg coverage. |
| 15 | No | Not computed: parent event_replay output does not preserve complete per-leg evidence for every row. Replaying the threshold from partial payload would invent leg coverage. |
| 20 | No | Not computed: parent event_replay output does not preserve complete per-leg evidence for every row. Replaying the threshold from partial payload would invent leg coverage. |
| 1000 | No | Not computed: parent event_replay output does not preserve complete per-leg evidence for every row. Replaying the threshold from partial payload would invent leg coverage. |

## Interpretation
- The 480-row parent status reconciliation is retained: 100 BLOCKED_LEG_ELIGIBILITY, 379 EXCLUDED_OHLC_RANGE_PROXY, and 1 REPLAY_PASS.
- A 373-row empty leg payload and partial payloads on range-excluded multi-leg strategies prevent faithful recalculation at alternate thresholds.
- The exclusion reason may identify one failing leg, but the persisted payload does not necessarily include every leg's OHLC/OI values. That is insufficient to determine whether a row would pass a different threshold.
- No alternative threshold eligibility counts are reported. The correct next step is to repair the Phase 52 audit output to preserve all selected legs for every exclusion, then rerun this preregistered sensitivity.
- The OHLC high-low/open percentage is a candle-range proxy, not a quoted spread or executable liquidity measure.
- This is not a backtest; no exits, fills, costs, P&L, strategy superiority or promotion can be inferred.
