# Phase 98 Error, Limitation and Correction Log

## E98-001 — Pre-execution evidence boundary
Phases 96–97 ran on previously explored summary rows. Their successful code runs are not evidence of profitable strategy execution. Phase 98 uses a new rule-level entry/exit simulation and does not ingest the old selection leaderboard for training or selection.

## E98-002 — Historical quote limitations
The public one-minute dataset reports option OHLCV(+OI), not a complete historic bid/ask/depth tape. Bar opens with fixed adverse slippage are execution proxies. Results cannot establish live fills, queue position, intrabar spread, or latency costs.

## E98-003 — Missing contract-minute coverage
Public option coverage is partial. Every missing exact contract/time, unavailable next-minute entry/exit, missing option field, pinned-revision error, or low active-path coverage must be counted by reason. No interpolation or forward-fill is allowed. Any incomplete campaign is excluded from P&L with a specific reason.

## E98-004 — Holdout quarantine
Never load a 2026 expiry file or use protected Phase 83 HOLD results. Entries requiring a 2026 expiry are excluded and counted.

## E98-005 — No promotion by success of computation
A passing workflow only demonstrates reproducible computation. Phase 98 cannot approve live/paper promotion; a later independent phase is mandatory if all gates pass.

## Correction incidents
New errors, invalid outputs, workflow failures and fixes are appended below with run URLs. The first failing run remains in this log as an audit record. No failure is silently overwritten.


## Automated execution issue — Run 38057371871 — tests=failure; replay=skipped; audit=skipped; runner_status=FAILED_BEFORE_NUMERICAL_RUN; economics=NOT_EVALUATED; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38057371871
- Failure is logged as infrastructure/data/validation status, not as strategy-performance evidence.
- Runner detail: See workflow logs and validation_report.json.


## E98-006 — Initial regression-test import failure (2026-10-10)
- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38057309811
- The first test job failed during collection because the workflow's pytest entry point did not include the repository root on sys.path; error: ModuleNotFoundError: No module named 'research'.
- The strategy runner was skipped. No market data were read, no trades were replayed, and no performance result was produced.
- Correction: the test module now explicitly adds the repository root to sys.path before importing the Phase 98 runner. Rerun required.

## E98-007 — First failure logger assumed numerical-output directory existed (2026-10-10)
- In the same run, the always-run publishing step failed at git add because results/phase98_opening_range_spread did not exist when tests failed before the numerical step.
- This prevented that workflow from persisting the failure to repository logs; it did not affect any numerical evidence because no replay ran.
- Correction: result-directory staging is now conditional, so status and error logs can still be committed on pre-replay failures. This incident is separately logged rather than hidden.


## E98-008 — Stale cost-function name in regression-test imports (2026-10-10)
- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38057371871
- After the repository import path was fixed, pytest failed at collection because the test imported fee_components, but the actual runner function is named fees.
- The replay was skipped and no source data or strategy returns were produced.
- Correction: remove the unused, stale fee_components test import. The executed fee schedule is exercised through run_scenario.

## E98-009 — Follow-up attempt repeated test collection failure and log-publisher rebase conflict (2026-10-10)
- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38057380129
- The same stale fee_components import still existed in the workflow's checked-out revision; numerical replay remained skipped.
- The always-run publisher's local append conflicted with concurrently updated Phase 98 chat/error/research logs during git rebase. This happened while the logs were being updated directly through repository writes during the workflow; no numerical files were involved.
- The test import is being corrected before the next run. No manual repository log edits should be made while the next run's publisher is active; let the workflow commit its audit checkpoint first.


## Automated execution issue — Run 38057516991 — tests=failure; replay=skipped; audit=skipped; runner_status=FAILED_BEFORE_NUMERICAL_RUN; economics=NOT_EVALUATED; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38057516991
- Failure is logged as infrastructure/data/validation status, not as strategy-performance evidence.
- Runner detail: See workflow logs and validation_report.json.
