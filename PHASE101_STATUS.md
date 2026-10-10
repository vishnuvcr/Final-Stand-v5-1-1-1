# Phase 101 Status — Full PDF Strategy Replication Gap-Fill

**State:** OPEN — plan registered; implementation/runtime validation pending  
**Branch:** `phase-101-full-pdf-strategy-replication`  
**Updated:** 2026-10-10  
**Strategy promotion:** NONE  
**Holdout:** 2026 remains excluded

## Planned tests

| Work item | Prior evidence | Phase 101 action | State |
|---|---|---|---|
| U02 — ML NIFTY options signals (RF/XGBoost/LSTM) | Phase 97 data gate blocked exact-contract model; paper method not fully reproducible | Run a fixed, chronological proxy on the pinned 2021–2025 contract archive if usable features/entry/exit coverage exist | PENDING |
| U05 — monthly trend/seasonality options rule | Rules extracted; historical trade replay previously blocked | Run source-informed first-Thursday/three-year same-month return method on modern sample with explicit operationalizations/cost sensitivities | PENDING |
| U07 — payoff structures | Phase 99 algebra tested 13 structures over nine expiry spots; not historical P&L | Carry forward formula evidence; keep history P&L blocked absent entry signals/quotes | CARRIED FORWARD |
| U10 — moving averages | Phase 96 fixed SMA/EMA screen | Carry forward descriptive comparison, not claim of exact reproduction | CARRIED FORWARD |
| U14 — CCI options | Phase 66 zero completed trades; Phase 67 exact-time coverage 8/30 triggers, 5/30 next-minute rows; Phase 68 missing target-date audit | Carry forward no-expectancy-inference decision; no rule loosening | CARRIED FORWARD |
| U01/U03/U04/U06/U08/U09/U11/U12/U13 — forecasting methods | Phase 95 common-data model-family screen | Carry forward paper-specific PARTIAL/DATA_BLOCKED statuses | CARRIED FORWARD |

## Gate restrictions

- Historical options data is pinned to revision `3eacf762d401efd9a08e804592fa7882b354c4a2`.
- Use option expiries only through 2025-12-31; never download 2026 options.
- Raw licensed option data stays in runner cache; publish aggregate/derived outputs only.
- Source claims and proxy assumptions must be separated.
- Zero completed trades means metrics are NOT ESTIMABLE, not zero observed return.
- This phase is a research test, not investment advice. No strategy promotion is assumed.
