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


## E98-010 — Source-pinned replay falsely passed with zero option chains (2026-10-10)
- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38057561258
- The workflow's tests, runner, and artifact checks exited successfully, but the persisted report shows 0 option expiry files loaded, 0 completed trades, and 1,126 option-chain load errors. The result is not performance evidence and the economic hypothesis is NOT ESTIMABLE.
- Root cause from the recorded errors: PyArrow compared a Parquet timestamp column declared as timestamp[ns, tz=+05:30] with filter bounds serialized as timestamp[s, tz=Asia/Kolkata]; the timezone identifiers differ, so all filtered chain reads failed with ArrowNotImplementedError.
- The data schema also names open interest open_interest, while the first runner only requested oi. This has not created valid OI observations and must be mapped explicitly for diagnostics; missing OI must never be imputed as zero.
- The published technical status PASS is too permissive because the workflow did not reject source-load exceptions. It is corrected to a source/data blocker for this run.
- Resolution: construct PyArrow filter scalars using the exact timestamp type from the Parquet schema, map open_interest to the internal OI field only when present, add regression tests for timezone-typed filtering/schema aliases, and make source-read exceptions fail the result audit. Strategy rules, split dates, thresholds, and cost scenarios remain unchanged.
- No 2026 data/holdout was loaded; no strategy or parameter was promoted.


## Automated execution issue — Run 38057921675 — tests=success; replay=cancelled; audit=skipped; runner_status=PASS; economics=NO_PROMOTION; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38057921675
- Failure is logged as infrastructure/data/validation status, not as strategy-performance evidence.
- Runner detail: See workflow logs and validation_report.json.


## Automated execution issue — Run 38058351337 — tests=success; replay=cancelled; audit=skipped; runner_status=PASS; economics=NO_PROMOTION; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38058351337
- Failure is logged as infrastructure/data/validation status, not as strategy-performance evidence.
- Runner detail: See workflow logs and validation_report.json.


## Automated execution issue — Run 38058461330 — tests=success; replay=cancelled; audit=skipped; runner_status=PASS; economics=NO_PROMOTION; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38058461330
- Failure is logged as infrastructure/data/validation status, not as strategy-performance evidence.
- Runner detail: See workflow logs and validation_report.json.


## Automated execution issue — Run 38058519330 — tests=success; replay=cancelled; audit=skipped; runner_status=FAILED_BEFORE_NUMERICAL_RUN; economics=NOT_EVALUATED; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38058519330
- Failure is logged as infrastructure/data/validation status, not as strategy-performance evidence.
- Runner detail: See workflow logs and validation_report.json.


## E98-011 — Stale output provenance in interrupted workflow attempts (2026-10-10)
- Runs 38057921675, 38058351337, and 38058461330 were interrupted before a successful replay/audit. Their publisher read previously committed result files and emitted stale runner_status=PASS / NO_PROMOTION labels. Those runs are not economic evidence; any zero P&L values in their status entries are not measurements.
- Correction: clear derived result files at the start of every run and derive published status from the current run test/replay/audit outcomes. Cancelled/failed replay now publishes REPLAY_NOT_SUCCESSFUL and NOT_EVALUATED. The README keeps a single current Phase 98 status block.


## Automated execution issue — Run 38058592320 — tests=success; replay=cancelled; audit=skipped; runner_status=REPLAY_NOT_SUCCESSFUL; economics=NOT_EVALUATED; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38058592320
- Failure is logged as infrastructure/data/validation status, not as strategy-performance evidence.
- Runner detail: See workflow logs and validation_report.json.


## Automated execution issue — Run 38059179785 — tests=success; replay=cancelled; audit=skipped; runner_status=REPLAY_NOT_SUCCESSFUL; economics=NOT_EVALUATED; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38059179785
- Failure is logged as infrastructure/data/validation status, not as strategy-performance evidence.
- Runner detail: See workflow logs and validation_report.json.


## Automated execution issue — Run 38059327298 — tests=success; replay=cancelled; audit=skipped; runner_status=REPLAY_NOT_SUCCESSFUL; economics=NOT_EVALUATED; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38059327298
- Failure is logged as infrastructure/data/validation status, not as strategy-performance evidence.
- Runner detail: See workflow logs and validation_report.json.
