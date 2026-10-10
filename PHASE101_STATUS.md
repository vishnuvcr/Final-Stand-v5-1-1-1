# Phase 101 Status — Full PDF Strategy Replication Gap-Fill

**State:** OPEN — first proxy outputs generated, but invalidated by a detected U05 calendar look-ahead and U02 capital-reuse flaw; corrected rerun pending  
**Branch:** `phase-101-full-pdf-strategy-replication`  
**Updated:** 2026-10-10  
**Strategy promotion:** NONE  
**Holdout:** 2026 remains excluded

## Planned tests

| Work item | Prior evidence | Phase 101 action | State |
|---|---|---|---|
| U02 — ML NIFTY options signals (RF/XGBoost/LSTM) | First run improperly reused initial ₹1 lakh to size every trade | Re-run with separate sequential ₹1 lakh equity per model, 95% premium exposure cap, 5% fee reserve, block bootstrap interval when sample permits | RETESTING |
| U05 — monthly trend/seasonality options rule | First run allowed some Thursday entries before Wednesday forecast | Re-run with first Thursday strictly after first Wednesday; preserve exclusions and publish sample-coverage limits | RETESTING |
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


## Runtime checkpoint — 2026-10-10T18:23:56Z

- Automated workflow run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38075221554
- Validation report: COMPLETED_WITH_EXPLICIT_LIMITATIONS; 14-paper matrix present; 2026 option holdout not downloaded; no strategy promoted.
- U05 completed trades: 7; sample status: COMPUTED; audit status counts: {'EXCLUDED_FIRST_WEDNESDAY_NOT_SESSION': 5, 'BLOCKED_NO_EXACT_ENTRY_SNAPSHOT': 35, 'BLOCKED_NO_THURSDAY_INDEX_BAR': 1, 'COMPLETED': 7, 'BLOCKED_NO_EXACT_NEXT_MINUTE_EXIT': 5, 'BLOCKED_NO_PENULTIMATE_EXIT_BAR': 1, 'EXCLUDED_FIRST_THURSDAY_NOT_SESSION': 2}.
- U02 predictions: 1330; completed trades: 896; model statuses: [{'model': 'RF', 'status': 'COMPLETED'}, {'model': 'XGBOOST', 'status': 'COMPLETED'}, {'model': 'LSTM5', 'status': 'COMPLETED'}].
- Result files are aggregate/derived only. A model/data blocker is not a negative efficacy finding.


## Correction gate — 2026-10-10
The first successful runtime output set is superseded and not accepted as final because U05 had look-ahead on months where the first Thursday preceded the first Wednesday, and U02 did not maintain account equity between signals. Both defects are corrected in the runner. The corrected phase results remain pending the next validated workflow run; no numerical finding from the first output set is promoted.
