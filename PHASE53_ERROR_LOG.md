# Phase 53 error log

## F53-INIT-001 — Coverage gate inherited from Phase 52 — CLOSED AS A SOURCE NO-GO

- **Date:** 2026-10-10.
- **Evidence:** Phase 52 v0.2 produced only one eligible replay out of 480 planned rows. One hundred rows were blocked because strictly prior minute OI was zero; 379 failed the fixed OHLC high-low/open proxy.
- **Impact:** no defensible factor-conditioned strategy ranking or efficacy inference can proceed from the current pilot.
- **Action:** separate source-coverage phase; preserve all Phase 52 definitions and holdout. Explore actual source coverage, revisions/licensing, and exact contract keys; distinguish daily reports from intraday data.
- **Resolution:** Phase 53 completed the source/go-no-go audit in run 37986608468. The data coverage limit is a documented scientific limitation, not a software fault. It is handed to separately preregistered Phase 54 OHLC-reference sensitivity; no live/quote-aware conclusion permitted.
- **Status:** CLOSED / CONTINUED AS PHASE 54 NON-EXECUTABLE SENSITIVITY.

## F53-RUN-37985435622 — Output path and artifact label — RESOLVED

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37985435622
- Root causes: a relative output path was passed to Path.relative_to against an absolute ROOT, and a backslash was emitted in the Actions artifact name due to escaped workflow expressions.
- Fixes: normalize both paths with resolve() before relative_to; correct Actions expression interpolation.
- Verification: source-audit and artifact-upload steps passed in later runs 37985738190, 37985806731 and 37986608468.
- Status: CLOSED.
## F53-RUN-37985550672 — Artifact name expression — RESOLVED

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37985550672
- Root cause: artifact name contained a literal backslash before the run ID.
- Fix: remove the accidental backslash from the GitHub Actions expression.
- Verification: artifact uploads passed in 37985738190, 37985806731 and 37986608468.
- Status: CLOSED.
## F53-RUN-37986160359 — Inventory test schema mismatch — RESOLVED

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37986160359
- Root cause: tests still read present_count/missing_count after the inventory result was renamed to distinguish partial listings from confirmed file absence.
- Fix: update unit tests and add complete/partial listing assertions.
- Verification: full test suite passed in 37986295801 and 37986608468.
- Status: CLOSED.
## F53-RUN-37986178539 — Inventory self-test schema mismatch — RESOLVED

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37986178539
- Root cause: command-line self-test still asserted deprecated inventory keys after unit tests were updated.
- Fix: self-test now asserts the renamed inventory fields and verifies partial results are not called missing.
- Verification: self-test and full suite passed in 37986295801 and 37986608468.
- Status: CLOSED.
## F53-RUN-37986217366 — Stale self-test assertion — RESOLVED

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37986217366
- Root cause: the same deprecated inventory keys remained in command-line self-test.
- Fix: update assertions; validate both the CLI self-test and unit suite.
- Verification: runs 37986309805, 37986469317, 37986536666 and 37986608468 passed.
- Status: CLOSED.


## F53-RUN-37985565318 — Concurrent checkpoint conflict — RESOLVED

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37985565318
- Root cause: a queued run used an old checkout and could not rebase concurrent append-only status/report changes.
- Fix: refresh latest branch tip before starting the audit; archive each report under unique run ID; merge only allowlisted append-only logs; retain remote canonical report on collisions; retry safe pushes, without force-pushing.
- Verification: runs 37985738190, 37985806731 and 37986608468 passed audit, artifact upload and persistence.
- Status: CLOSED.

## F53-TREE-001 — Partial tree listing / false missing-path semantics — RESOLVED

- Root cause: a prior HF tree request used unsupported limit=1000. Earlier results could confuse a partial metadata response with actual missing files even though direct HEAD checks returned 200.
- Fix: remove unsupported parameter, follow paginated Link rel=next responses, check all pages, and mark incomplete metadata as “not listed in returned metadata,” never missing. Disable automated retrieval of the current NSE option-chain page under site conditions.
- Verification: [run 37986608468](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37986608468) passed; 6 option-directory metadata pages + 1 index page returned 270 file records and included all 13 selected paths.
- Status: CLOSED.

## F53-SOURCE-001 — No qualifying independent free historical quotes — CLOSED BY NO-GO DECISION

- Primary revision 0f4800e43e6f96cec0794369d78eb4d3c4211ef5 confirmed; 13/13 required paths available, no 404s or unknown statuses.
- Codepyx23 mirror: equal ETags on 13/13 paths; not independent. Rissin: no intraday OI and licence listed as “other”. Artist-23: API license absent and exact-expiry field not established in displayed schema. Zenodo: 2017–2020 OHLC/volume only. Exchange reports are daily controls; paid feeds not purchased; current NSE option-chain page is not scraped.
- Outcome: no registered source has cleared legal status + exact prior-minute OI + historical bid/ask/depth gates. Phase53 source audit is COMPLETE / NO-GO for true quote/depth validation. Phase54 is an OHLC-reference cost sensitivity only, no live/promotion claims.
- Status: CLOSED / HANDOFF TO PHASE54.
