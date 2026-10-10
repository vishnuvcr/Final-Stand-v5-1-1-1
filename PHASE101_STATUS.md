# Phase 101 Status — Full PDF Strategy Replication Gap-Fill

**State:** REPLAY PASSED; ACCOUNTING RECONCILED — no strategy promoted  
**Branch:** `phase-101-full-pdf-strategy-replication`  
**Updated:** 2026-10-11  
**Strategy promotion:** NONE  
**Holdout:** 2026 remains excluded

## Planned tests

| Work item | Prior evidence | Phase 101 action | State |
|---|---|---|---|
| U02 — ML NIFTY options signals (RF/XGBoost/LSTM) | First run improperly reused initial ₹1 lakh to size every trade | Re-run with separate sequential ₹1 lakh equity per model, 95% premium exposure cap, 5% fee reserve, block bootstrap interval when sample permits | VALIDATED_PROXY_TEST |
| U05 — monthly trend/seasonality options rule | First run allowed some Thursday entries before Wednesday forecast | Re-run with literal first-Thursday entry; exclude months where that Thursday precedes the Wednesday signal; publish coverage limits | VALIDATED_PROXY_TEST |
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


## Runtime checkpoint — 2026-10-10T18:37:17Z

- Automated workflow run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38076280351
- Validation report: COMPLETED_WITH_EXPLICIT_LIMITATIONS; 14-paper matrix present; 2026 option holdout not downloaded; no strategy promoted.
- U05 completed trades: 10; sample status: COMPUTED; audit status counts: {'EXCLUDED_FIRST_WEDNESDAY_NOT_SESSION': 5, 'BLOCKED_NO_MATCHING_OPENING_WINDOW_OPTION': 30, 'BLOCKED_NO_EXACT_NEXT_MINUTE_EXIT': 6, 'BLOCKED_NO_THURSDAY_INDEX_BAR': 1, 'COMPLETED': 10, 'EXCLUDED_INSUFFICIENT_ACCOUNT_EQUITY': 3, 'EXCLUDED_FIRST_THURSDAY_NOT_SESSION': 1}.
- U02 predictions: 1330; completed trades: 164; model statuses: [{'model': 'RF', 'status': 'COMPLETED'}, {'model': 'XGBOOST', 'status': 'COMPLETED'}, {'model': 'LSTM5', 'status': 'COMPLETED'}].
- Result files are aggregate/derived only. A model/data blocker is not a negative efficacy finding.


## Corrected runtime checkpoint — 2026-10-10T18:37:18Z

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38076280351
- Validation: COMPLETED_WITH_EXPLICIT_LIMITATIONS; 14-paper matrix; no 2026 option data; no strategy promoted.
- U05: 10 completed / 56 opportunities; status COMPUTED; audit counts {'EXCLUDED_FIRST_WEDNESDAY_NOT_SESSION': 5, 'BLOCKED_NO_MATCHING_OPENING_WINDOW_OPTION': 30, 'BLOCKED_NO_EXACT_NEXT_MINUTE_EXIT': 6, 'BLOCKED_NO_THURSDAY_INDEX_BAR': 1, 'COMPLETED': 10, 'EXCLUDED_INSUFFICIENT_ACCOUNT_EQUITY': 3, 'EXCLUDED_FIRST_THURSDAY_NOT_SESSION': 1}.
- U02: 1330 predictions; 164 costed trades; model statuses [{'model': 'RF', 'status': 'COMPLETED'}, {'model': 'XGBOOST', 'status': 'COMPLETED'}, {'model': 'LSTM5', 'status': 'COMPLETED'}].
- Account sizing: sequential per-model ₹1 lakh starting equity, 95% premium deployment limit, 5% fee reserve.
- Bootstrap: circular moving-block 95% mean net-trade CI only when n>=20.


## Source-fidelity correction — 2026-10-10
The first corrected run prevented look-ahead by shifting some entries to the second Thursday. Audit showed this altered the paper's stated first-Thursday rule. The latest runner now preserves the literal first Thursday and explicitly excludes months where it precedes the first-Wednesday forecast. A final source-faithful replay is pending. Previous U05 P&L remains superseded.


## Corrected runtime checkpoint — 2026-10-10T18:43:17Z

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38076645768
- Validation: COMPLETED_WITH_EXPLICIT_LIMITATIONS; 14-paper matrix; no 2026 option data; no strategy promoted.
- U05: 7 completed / 56 opportunities; status COMPUTED; audit counts {'EXCLUDED_FIRST_WEDNESDAY_NOT_SESSION': 5, 'BLOCKED_NO_MATCHING_OPENING_WINDOW_OPTION': 26, 'EXCLUDED_ENTRY_PRECEDES_FORECAST': 7, 'BLOCKED_NO_EXACT_NEXT_MINUTE_EXIT': 6, 'BLOCKED_NO_THURSDAY_INDEX_BAR': 1, 'COMPLETED': 7, 'EXCLUDED_INSUFFICIENT_ACCOUNT_EQUITY': 3, 'EXCLUDED_FIRST_THURSDAY_NOT_SESSION': 1}.
- U02: 1330 predictions; 164 costed trades; model statuses [{'model': 'RF', 'status': 'COMPLETED'}, {'model': 'XGBOOST', 'status': 'COMPLETED'}, {'model': 'LSTM5', 'status': 'COMPLETED'}].
- Account sizing: sequential per-model ₹1 lakh starting equity, 95% premium deployment limit, 5% fee reserve.
- Bootstrap: circular moving-block 95% mean net-trade CI only when n>=20.


## Runtime checkpoint — 2026-10-10T18:47:09Z

- Automated workflow run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38076670672
- Validation report: COMPLETED_WITH_EXPLICIT_LIMITATIONS; 14-paper matrix present; 2026 option holdout not downloaded; no strategy promoted.
- U05 completed trades: 7; sample status: COMPUTED; audit status counts: {'EXCLUDED_FIRST_WEDNESDAY_NOT_SESSION': 5, 'BLOCKED_NO_MATCHING_OPENING_WINDOW_OPTION': 26, 'EXCLUDED_ENTRY_PRECEDES_FORECAST': 7, 'BLOCKED_NO_EXACT_NEXT_MINUTE_EXIT': 6, 'BLOCKED_NO_THURSDAY_INDEX_BAR': 1, 'COMPLETED': 7, 'EXCLUDED_INSUFFICIENT_ACCOUNT_EQUITY': 3, 'EXCLUDED_FIRST_THURSDAY_NOT_SESSION': 1}.
- U02 predictions: 1330; completed trades: 164; model statuses: [{'model': 'RF', 'status': 'COMPLETED'}, {'model': 'XGBOOST', 'status': 'COMPLETED'}, {'model': 'LSTM5', 'status': 'COMPLETED'}].
- Result files are aggregate/derived only. A model/data blocker is not a negative efficacy finding.


## Corrected runtime checkpoint — 2026-10-10T18:47:10Z

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38076670672
- Validation: COMPLETED_WITH_EXPLICIT_LIMITATIONS; 14-paper matrix; no 2026 option data; no strategy promoted.
- U05: 7 completed / 56 opportunities; status COMPUTED; audit counts {'EXCLUDED_FIRST_WEDNESDAY_NOT_SESSION': 5, 'BLOCKED_NO_MATCHING_OPENING_WINDOW_OPTION': 26, 'EXCLUDED_ENTRY_PRECEDES_FORECAST': 7, 'BLOCKED_NO_EXACT_NEXT_MINUTE_EXIT': 6, 'BLOCKED_NO_THURSDAY_INDEX_BAR': 1, 'COMPLETED': 7, 'EXCLUDED_INSUFFICIENT_ACCOUNT_EQUITY': 3, 'EXCLUDED_FIRST_THURSDAY_NOT_SESSION': 1}.
- U02: 1330 predictions; 164 costed trades; model statuses [{'model': 'RF', 'status': 'COMPLETED'}, {'model': 'XGBOOST', 'status': 'COMPLETED'}, {'model': 'LSTM5', 'status': 'COMPLETED'}].
- Account sizing: sequential per-model ₹1 lakh starting equity, 95% premium deployment limit, 5% fee reserve.
- Bootstrap: circular moving-block 95% mean net-trade CI only when n>=20.


## Audit checkpoint — 2026-10-11

- Corrected the extra 0.25%-per-side impact sensitivity to use the same execution-price helper and date-effective fee model as the baseline, plus ₹50 round-trip cost.
- Code commit: `c75b43da2592b02c520b2500b9f63e5d72a7b12d`.
- The push-triggered workflow must pass before the new sensitivity figures are accepted.
- Drawdown review remains open: inspect equity peak/trough and trade chronology; do not assume a drawdown above initial capital is automatically an accounting error.
- Strategy promotion: NONE. 2026 options holdout remains excluded.


## Additional accounting controls — 2026-10-11

- U02 output now includes equity reconciliation `ending equity - (initial equity + sum of net trade P&L)`, a pass/fail flag, peak equity/date, peak and trough at maximum drawdown, trough date, and drawdown as a percentage of the relevant peak.
- The run must regenerate summary/ledger files before the audit is closed. The earlier run's large drawdown values are not yet certified as correct or incorrect.


## Corrected runtime checkpoint — 2026-10-10T19:43:01Z

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38080659162
- Validation: COMPLETED_WITH_EXPLICIT_LIMITATIONS; 14-paper matrix; no 2026 option data; no strategy promoted.
- U05: 7 completed / 56 opportunities; status COMPUTED; audit counts {'EXCLUDED_FIRST_WEDNESDAY_NOT_SESSION': 5, 'BLOCKED_NO_MATCHING_OPENING_WINDOW_OPTION': 26, 'EXCLUDED_ENTRY_PRECEDES_FORECAST': 7, 'BLOCKED_NO_EXACT_NEXT_MINUTE_EXIT': 6, 'BLOCKED_NO_THURSDAY_INDEX_BAR': 1, 'COMPLETED': 7, 'EXCLUDED_INSUFFICIENT_ACCOUNT_EQUITY': 3, 'EXCLUDED_FIRST_THURSDAY_NOT_SESSION': 1}.
- U02: 1330 predictions; 164 costed trades; model statuses [{'model': 'RF', 'status': 'COMPLETED'}, {'model': 'XGBOOST', 'status': 'COMPLETED'}, {'model': 'LSTM5', 'status': 'COMPLETED'}].
- Account sizing: sequential per-model ₹1 lakh starting equity, 95% premium deployment limit, 5% fee reserve.
- Bootstrap: circular moving-block 95% mean net-trade CI only when n>=20.


## Runtime checkpoint — 2026-10-10T19:46:50Z

- Automated workflow run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38080831113
- Validation report: COMPLETED_WITH_EXPLICIT_LIMITATIONS; 14-paper matrix present; 2026 option holdout not downloaded; no strategy promoted.
- U05 completed trades: 7; sample status: COMPUTED; audit status counts: {'EXCLUDED_FIRST_WEDNESDAY_NOT_SESSION': 5, 'BLOCKED_NO_MATCHING_OPENING_WINDOW_OPTION': 26, 'EXCLUDED_ENTRY_PRECEDES_FORECAST': 7, 'BLOCKED_NO_EXACT_NEXT_MINUTE_EXIT': 6, 'BLOCKED_NO_THURSDAY_INDEX_BAR': 1, 'COMPLETED': 7, 'EXCLUDED_INSUFFICIENT_ACCOUNT_EQUITY': 3, 'EXCLUDED_FIRST_THURSDAY_NOT_SESSION': 1}.
- U02 predictions: 1330; completed trades: 164; model statuses: [{'model': 'RF', 'status': 'COMPLETED'}, {'model': 'XGBOOST', 'status': 'COMPLETED'}, {'model': 'LSTM5', 'status': 'COMPLETED'}].
- Result files are aggregate/derived only. A model/data blocker is not a negative efficacy finding.


## Corrected runtime checkpoint — 2026-10-10T19:46:51Z

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38080831113
- Validation: COMPLETED_WITH_EXPLICIT_LIMITATIONS; 14-paper matrix; no 2026 option data; no strategy promoted.
- U05: 7 completed / 56 opportunities; status COMPUTED; audit counts {'EXCLUDED_FIRST_WEDNESDAY_NOT_SESSION': 5, 'BLOCKED_NO_MATCHING_OPENING_WINDOW_OPTION': 26, 'EXCLUDED_ENTRY_PRECEDES_FORECAST': 7, 'BLOCKED_NO_EXACT_NEXT_MINUTE_EXIT': 6, 'BLOCKED_NO_THURSDAY_INDEX_BAR': 1, 'COMPLETED': 7, 'EXCLUDED_INSUFFICIENT_ACCOUNT_EQUITY': 3, 'EXCLUDED_FIRST_THURSDAY_NOT_SESSION': 1}.
- U02: 1330 predictions; 164 costed trades; model statuses [{'model': 'RF', 'status': 'COMPLETED'}, {'model': 'XGBOOST', 'status': 'COMPLETED'}, {'model': 'LSTM5', 'status': 'COMPLETED'}].
- Account sizing: sequential per-model ₹1 lakh starting equity, 95% premium deployment limit, 5% fee reserve.
- Bootstrap: circular moving-block 95% mean net-trade CI only when n>=20.


## Latest verified run — 2026-10-11

- [GitHub Actions run 38080831113](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38080831113) completed successfully; syntax/unit tests, historical replay, output contract and publication all passed.
- U02 equity reconciliation passes for LSTM5, RF and XGBoost (absolute difference below ₹0.01). Peak/trough and percentage-of-peak drawdown are now published in `u02_strategy_summary.csv`.
- All three U02 accounts ended down approximately 99.99%; drawdown approached 100% from elevated compounded equity peaks. This is a severe risk outcome, not a bookkeeping discrepancy.
- Corrected additional-impact stress totals are negative for all three models. Bootstrap confidence intervals cross zero. No strategy promoted; 2026 holdout remains excluded.
- The U05 result remains only a modern-sample proxy with seven completed trades; do not infer robust expectancy.
