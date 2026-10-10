# Phase 101 Research Log

## 2026-10-10 — Phase initialization

- Reviewed the current main README checkpoint and Phase 100 plan/status/manuscript/paper-status ledger before opening this phase.
- Phase 100 had reached its finite synthesis stop but expressly identified incomplete U02 and U05 executable-method evidence; this is a new bounded plan rather than reopening Phase 100.
- Created isolated branch `phase-101-full-pdf-strategy-replication` from `phase-100-cross-paper-reproducibility-synthesis`.
- Registered fixed scope for U02 and U05 gap-fill tests; retained prior Phase 95/96/66/99 conclusions for other papers.
- Data availability gate and numerical outcomes remain pending workflow execution. No strategy promoted; the 2026 holdout remains sealed.

## 2026-10-10 — First run / dependency correction

- Workflow run [38074995935](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38074995935) passed dependency installation and all deterministic tests but failed before loading market data because pandas could not import the installed PyArrow 26.0.0 Parquet engine.
- Rejected the run as a research result; it produced no accepted U02/U05 performance figures.
- Pinned PyArrow 18.1.0 and added an explicit import check. Awaiting the rerun before interpreting strategy metrics.


## Runtime checkpoint — 2026-10-10T18:23:56Z

- Automated workflow run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38075221554
- Validation report: COMPLETED_WITH_EXPLICIT_LIMITATIONS; 14-paper matrix present; 2026 option holdout not downloaded; no strategy promoted.
- U05 completed trades: 7; sample status: COMPUTED; audit status counts: {'EXCLUDED_FIRST_WEDNESDAY_NOT_SESSION': 5, 'BLOCKED_NO_EXACT_ENTRY_SNAPSHOT': 35, 'BLOCKED_NO_THURSDAY_INDEX_BAR': 1, 'COMPLETED': 7, 'BLOCKED_NO_EXACT_NEXT_MINUTE_EXIT': 5, 'BLOCKED_NO_PENULTIMATE_EXIT_BAR': 1, 'EXCLUDED_FIRST_THURSDAY_NOT_SESSION': 2}.
- U02 predictions: 1330; completed trades: 896; model statuses: [{'model': 'RF', 'status': 'COMPLETED'}, {'model': 'XGBOOST', 'status': 'COMPLETED'}, {'model': 'LSTM5', 'status': 'COMPLETED'}].
- Result files are aggregate/derived only. A model/data blocker is not a negative efficacy finding.


## 2026-10-10 — First output review and correction

- Run [38075221554](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38075221554) completed and published a preliminary U02/U05 proxy result set. It was not accepted after manual audit found two research-design defects.
- U05 date audit showed the forecast could occur after the entry date in months when the first calendar Thursday preceded the first Wednesday. The trade calendar has been corrected and tested so entry is strictly after the forecast.
- U02 had used the original ₹1 lakh capital cap on each trade rather than carrying equity forward. The simulator now updates account equity per model and blocks entries if premium cannot be funded while preserving cash for charges.
- Added 95% moving-block bootstrap intervals for the mean net trade result when n >= 20; no precision claim for U05 if its resulting sample remains sparse.
- The first result CSVs/report are superseded. The corrected runtime workflow is the only result set eligible for evaluation.


## Runtime checkpoint — 2026-10-10T18:37:17Z

- Automated workflow run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38076280351
- Validation report: COMPLETED_WITH_EXPLICIT_LIMITATIONS; 14-paper matrix present; 2026 option holdout not downloaded; no strategy promoted.
- U05 completed trades: 10; sample status: COMPUTED; audit status counts: {'EXCLUDED_FIRST_WEDNESDAY_NOT_SESSION': 5, 'BLOCKED_NO_MATCHING_OPENING_WINDOW_OPTION': 30, 'BLOCKED_NO_EXACT_NEXT_MINUTE_EXIT': 6, 'BLOCKED_NO_THURSDAY_INDEX_BAR': 1, 'COMPLETED': 10, 'EXCLUDED_INSUFFICIENT_ACCOUNT_EQUITY': 3, 'EXCLUDED_FIRST_THURSDAY_NOT_SESSION': 1}.
- U02 predictions: 1330; completed trades: 164; model statuses: [{'model': 'RF', 'status': 'COMPLETED'}, {'model': 'XGBOOST', 'status': 'COMPLETED'}, {'model': 'LSTM5', 'status': 'COMPLETED'}].
- Result files are aggregate/derived only. A model/data blocker is not a negative efficacy finding.


## Corrected run 38076280351 — 2026-10-10T18:37:18Z
- Validation: COMPLETED_WITH_EXPLICIT_LIMITATIONS; U05 completed trades 10; U02 costed trades 164; no 2026 option data; no strategy promoted.
- U05 timing corrected to enforce entry strictly after the Wednesday forecast. U02 now carries sequential account equity per model.


## 2026-10-10 — Source-faithful U05 calendar correction

- The first no-look-ahead fix moved the strategy entry to a second Thursday in months where first Thursday preceded the first Wednesday. Although it eliminated temporal leakage, it altered the paper's actual entry rule.
- Replaced that workaround: preserve the PDF's first-Thursday rule and exclude each such month with `EXCLUDED_ENTRY_PRECEDES_FORECAST`. No second-Thursday trade is fabricated.
- Added regression tests for July 2021 (exclude) and June 2024 (chronologically eligible). The prior corrected-run U05 P&L is superseded pending the new replay.


## Corrected run 38076645768 — 2026-10-10T18:43:17Z
- Validation: COMPLETED_WITH_EXPLICIT_LIMITATIONS; U05 completed trades 7; U02 costed trades 164; no 2026 option data; no strategy promoted.
- U05 timing corrected to enforce entry strictly after the Wednesday forecast. U02 now carries sequential account equity per model.


## Runtime checkpoint — 2026-10-10T18:47:09Z

- Automated workflow run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38076670672
- Validation report: COMPLETED_WITH_EXPLICIT_LIMITATIONS; 14-paper matrix present; 2026 option holdout not downloaded; no strategy promoted.
- U05 completed trades: 7; sample status: COMPUTED; audit status counts: {'EXCLUDED_FIRST_WEDNESDAY_NOT_SESSION': 5, 'BLOCKED_NO_MATCHING_OPENING_WINDOW_OPTION': 26, 'EXCLUDED_ENTRY_PRECEDES_FORECAST': 7, 'BLOCKED_NO_EXACT_NEXT_MINUTE_EXIT': 6, 'BLOCKED_NO_THURSDAY_INDEX_BAR': 1, 'COMPLETED': 7, 'EXCLUDED_INSUFFICIENT_ACCOUNT_EQUITY': 3, 'EXCLUDED_FIRST_THURSDAY_NOT_SESSION': 1}.
- U02 predictions: 1330; completed trades: 164; model statuses: [{'model': 'RF', 'status': 'COMPLETED'}, {'model': 'XGBOOST', 'status': 'COMPLETED'}, {'model': 'LSTM5', 'status': 'COMPLETED'}].
- Result files are aggregate/derived only. A model/data blocker is not a negative efficacy finding.


## Corrected run 38076670672 — 2026-10-10T18:47:10Z
- Validation: COMPLETED_WITH_EXPLICIT_LIMITATIONS; U05 completed trades 7; U02 costed trades 164; no 2026 option data; no strategy promoted.
- U05 timing corrected to enforce entry strictly after the Wednesday forecast. U02 now carries sequential account equity per model.


## 2026-10-11 — Cost-stress audit correction

- Audited the latest successful run's U02 trade ledger and found the additional 0.25%-per-side impact column omitted baseline date-effective fees and the repository execution-price convention. Corrected the stress calculation to use impacted raw prices, execution-price rounding/slippage, date-effective charges, and the additional ₹50 round-trip cost.
- The corrected code commit is `c75b43da2592b02c520b2500b9f63e5d72a7b12d`. A push-triggered workflow is expected to regenerate derived outputs and validate the result contract.
- Drawdown values have not been clipped or declared erroneous. The next audit will reconcile the model equity path, peak, trough and dates; drawdown can exceed initial capital if equity first rises materially above its starting value.
- No strategy is promoted; 2026 option data remain excluded. Previous values in the additional-impact column are superseded until the new run passes.


- Extended U02 summary output to expose maximum account equity and date, peak/trough at the maximum drawdown, drawdown as a percentage of its peak, and an ending-equity reconciliation check. This distinguishes a legitimate compounded-equity drawdown from a bookkeeping mismatch without clipping the reported rupee value. Code commit: `ef34c38aeca5ddc73ee1f948e4216f2fba8bb5bd`.

- Added a unit test using a deterministic synthetic Phase 66 cost helper to verify the adverse-impact sensitivity includes execution-price rounding, baseline charges, and the extra ₹50. The synthetic helper is a test fixture only and is not presented as a broker tariff. Test commit: `770571241898d2d408efc4f0bb73bf531bbabfee`.
