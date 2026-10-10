# Phase 98 Research Log

## 2026-10-10 — Registration and pre-flight checks
- User requested research to resume with an optimistic, determined search for an options strategy.
- Inspected the active repository README, root research/error logs, DYNAMIC_N_RESEARCH_PLAN, Phase 96/97 plans/status/chat/error logs and successful workflow result reports.
- Reconciled the negative Phase 96 validation net50 sum (−₹303,435.13) and Phase 97 sum (−₹158,202.95). Their selected HIGH regime cells each had only three validation trades. They are summary-table selection tests, not independent trade-level replays.
- Reviewed Phases 90–94: IV's very small 2024 predictive improvement did not independently replicate in 2023; synthetic-forward proxy/OI features degraded the tested 2022 magnitude predictor; no candidate was promoted.
- Retained the Phase 83 protected 2026 holdout boundary.
- Created a new branch and registered ORB15_DEBIT_V1 plus a prior-only VIX risk filter. The test will use only DEV through 2023 and VAL through 2025 with a pinned source revision, next-minute entry/exit prices, Paytm Money brokerage, statutory fees/GST, slippage and severe cost stress.
- Current status: implementation and runtime evidence pending. No numerical result is accepted yet.


## Run 38057371871 — tests=failure; replay=skipped; audit=skipped; runner_status=FAILED_BEFORE_NUMERICAL_RUN; economics=NOT_EVALUATED; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38057371871
- Result status: FAILED_BEFORE_NUMERICAL_RUN. Economic status: NOT_EVALUATED.
- Protected Phase 83 2026 holdout loaded: NO. No strategy is promoted.


## 2026-10-10 — First workflow failure and remediation
- Actions run 38057309811 failed at pytest collection because the repository root was not on sys.path. The strategy replay was skipped; this produced no market-data or performance evidence.
- The workflow's always-run log publisher also failed because it staged a results directory that did not yet exist.
- Corrected the test import path and made result-directory staging conditional.
- The first failure and logging defect are explicitly retained in PHASE98_ERROR_LOG.md. Re-run regression tests before any source-pinned replay.


## 2026-10-10 — Second and third pre-replay failures
- Run 38057371871 reached test collection after the path fix and failed because the test imported a nonexistent name (fee_components instead of the runner's fees function).
- Run 38057380129 repeated that same test import error. Its audit-publisher commit also conflicted on rebase because repository logs were manually updated while the workflow was active.
- Neither run read source data or ran the strategy. The stale import is removed before the next run; future log edits will wait until the automated publisher finishes.


## Run 38057516991 — tests=failure; replay=skipped; audit=skipped; runner_status=FAILED_BEFORE_NUMERICAL_RUN; economics=NOT_EVALUATED; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38057516991
- Result status: FAILED_BEFORE_NUMERICAL_RUN. Economic status: NOT_EVALUATED.
- Protected Phase 83 2026 holdout loaded: NO. No strategy is promoted.


## Run 38057561258 — tests=success; replay=success; audit=success; runner_status=PASS; economics=NO_PROMOTION; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38057561258
- Result status: PASS. Economic status: NO_PROMOTION.
- Protected Phase 83 2026 holdout loaded: NO. No strategy is promoted.


## 2026-10-10 — Phase 98 first source-pinned replay: BLOCKED, not performance evidence
- Workflow [38057561258](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38057561258) passed its test and artifact steps, but result audit found 0 option expiry files loaded, 0 trades, and 1,126 option-chain load exceptions.
- The common exception is a PyArrow timestamp-filter mismatch: data schema timestamp[ns, tz=+05:30] versus filter timestamp timestamp[s, tz=Asia/Kolkata].
- This means no empirical strategy conclusion, positive or negative, is estimable from the run. The report's technical PASS label is over-permissive and is being corrected.
- The schema also exposes open_interest rather than oi; the field will be explicitly normalized when present, without imputing absent OI.
- The strategy preregistration is unchanged. Next: type the filter scalars to the exact Parquet timestamp field, add regressions, and make source exceptions fail the evidence-acceptance gate. No 2026 holdout is accessed.


## Run 38057921675 — tests=success; replay=cancelled; audit=skipped; runner_status=PASS; economics=NO_PROMOTION; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38057921675
- Result status: PASS. Economic status: NO_PROMOTION.
- Protected Phase 83 2026 holdout loaded: NO. No strategy is promoted.


## Run 38058351337 — tests=success; replay=cancelled; audit=skipped; runner_status=PASS; economics=NO_PROMOTION; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38058351337
- Result status: PASS. Economic status: NO_PROMOTION.
- Protected Phase 83 2026 holdout loaded: NO. No strategy is promoted.


## Run 38058461330 — tests=success; replay=cancelled; audit=skipped; runner_status=PASS; economics=NO_PROMOTION; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38058461330
- Result status: PASS. Economic status: NO_PROMOTION.
- Protected Phase 83 2026 holdout loaded: NO. No strategy is promoted.


## Run 38058519330 — tests=success; replay=cancelled; audit=skipped; runner_status=FAILED_BEFORE_NUMERICAL_RUN; economics=NOT_EVALUATED; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38058519330
- Result status: FAILED_BEFORE_NUMERICAL_RUN. Economic status: NOT_EVALUATED.
- Protected Phase 83 2026 holdout loaded: NO. No strategy is promoted.


## Run 38058592320 — tests=success; replay=cancelled; audit=skipped; runner_status=REPLAY_NOT_SUCCESSFUL; economics=NOT_EVALUATED; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38058592320
- Result status: REPLAY_NOT_SUCCESSFUL. Economic status: NOT_EVALUATED.
- Protected Phase 83 2026 holdout loaded: NO. No strategy is promoted.


## Run 38059179785 — tests=success; replay=cancelled; audit=skipped; runner_status=REPLAY_NOT_SUCCESSFUL; economics=NOT_EVALUATED; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38059179785
- Result status: REPLAY_NOT_SUCCESSFUL. Economic status: NOT_EVALUATED.
- Protected Phase 83 2026 holdout loaded: NO. No strategy is promoted.


## Run 38059327298 — tests=success; replay=cancelled; audit=skipped; runner_status=REPLAY_NOT_SUCCESSFUL; economics=NOT_EVALUATED; URL=https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38059327298
- Result status: REPLAY_NOT_SUCCESSFUL. Economic status: NOT_EVALUATED.
- Protected Phase 83 2026 holdout loaded: NO. No strategy is promoted.
