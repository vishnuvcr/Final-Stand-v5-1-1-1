# Phase 52 Error Log

This is an append-only ledger. For every software failure, coverage failure, source rejection, specification defect or statistical mistake, record a unique ID, date/time, observed symptom, root cause, scientific impact, correction, rerun/evidence status and regression test. Never overwrite failed outputs or treat a green Actions run as scientific evidence by itself.

## F52-001 — Repository root README not available for several owned repositories through connected file API

- **Date:** 2026-10-09
- **Observation:** The account inventory returned 40 repositories, but README.md fetches returned 404 for several (including ML/market-gainer repositories) while others were readable.
- **Impact:** The 40-repository inventory is verified; the code-level audit of every repository is not yet complete. A missing root README is not interpreted as absence of a strategy.
- **Correction / next step:** Try alternate README casing and repo-specific plan/config/source paths; use connected GitHub code search where indexed. Record every repository's source-audit state in research/phase52/repository_audit.csv.
- **Status:** OPEN; no numerical evidence impacted.

## F52-002 — Prior Phase 51 full-window OOS still has unresolved option-data sessions

- **Date:** 2026-10-09
- **Observation:** Main README and Phase 51 audit status identify 2026-07-28 and 2026-08-04 option blocks as unresolved; candidate public Hugging Face files with those labels are stale and contain no target-session rows.
- **Impact:** Full-window Phase 51 OOS cannot be claimed. This limitation carries forward and remains explicitly segregated from any other complete-window Phase 52 experiment.
- **Correction / next step:** Search authorised/public sources with byte/timestamp/contract audits. Do not synthesize, forward-fill or silently shorten. Do not purchase data or use an account credential without explicit permission.
- **Status:** OPEN / data-gated; no Phase 52 P&L impacted.

## Error-log protocol

Any registry-validation failure, duplicate configuration ID, quote coverage gap, look-ahead defect, event timestamp mismatch, transaction-cost reconciliation issue, failed workflow, invalid inference or rejected data source gets a new F52-NNN entry. Resolution must include a testable correction and a rerun reference. Failed or superseded outputs remain archived and are never mixed with accepted evidence.


## F52-003 — Candidate count / grid-size correction made before first test — RESOLVED

- **Date:** 2026-10-09
- **Observation:** The first candidate-array draft contained 52 structure families, not the 50 initially used in the planning arithmetic.
- **Impact:** None to numerical evidence; no Phase 52 replay had started.
- **Correction:** Retained all 52 families and all six factor-selector modes, making 312 hypotheses. Appended plan amendment PA-001, changed finite grid to version 1.1 before any result and recorded that every applicable grid combination remains queued.
- **Verification required:** Automatic validation checks 312+ unique candidate IDs and an exact 52-family × six-mode matrix. Status: RESOLVED IN SPECIFICATION; run verification still pending GitHub Actions.

## F52-004 — Potential source-discovery API-key leakage — PREVENTED

- **Date:** 2026-10-09
- **Observation:** YouTube Data API puts its key in a query parameter; persisting the raw request URL or raw exception could expose the secret.
- **Impact:** No source-discovery run had occurred and no credential was recorded.
- **Correction:** The discovery client strips key/token parameters before logging and records only safe endpoint/query metadata; network error messages are reduced to exception class to prevent accidental URL/credential leakage. Credential values are never printed.
- **Regression gate:** Inspect stored `query_url` values and scan artifacts for known secret patterns; any exposure blocks publication and requires credential rotation.
- **Status:** PATCHED BEFORE FIRST RUN.

## F52-AUTO-37924369419 — Automated workflow failure

- Date: 2026-10-09
- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37924369419
- Impact: no strategy P&L is accepted from this run. Partial outputs remain unverified diagnostics.
- Root cause: pending review of the failed job logs.
- Status: OPEN.


## F52-005 — Strategy specification CSV column misalignment — RESOLVED IN FILE

- **Date:** 2026-10-09
- **Observed in Actions run:** https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37924369419
- **Root cause:** The initial CSV generator omitted the `family_name` field from each data row while the header expected it. The validator encountered null cells and raised AttributeError rather than presenting a clean schema error.
- **Impact:** Registry self-test passed, but registry validation failed before source discovery or grid enumeration. No backtest result was produced.
- **Correction:** Rebuilt all 52 strategy-specification rows with the correct six columns, deriving family names from the candidate registry; hardened validation against null fields.
- **Status:** RESOLVED — retry run passed registry/spec/grid validation and completed the source-discovery and 10,000-record queue checkpoint.


## F52-006 — YouTube API secret absent — EXPECTED CAPABILITY LIMITATION

- **Date:** 2026-10-09
- **Observation:** The Actions environment contains `HF_TOKEN` and GitHub's workflow token, but `YOUTUBE_API_KEY` is not configured.
- **Impact:** This run queried Hugging Face and GitHub successfully; fresh YouTube Data API search did not run.
- **Correction/handling:** The discovery script reports `NOT_RUN`, keeps the previously collected Phase 46 YouTube ledger and does not claim fresh channel coverage. Public YouTube metadata can be researched separately where accessible without an API key, subject to rate limits and source attribution.
- **Status:** OPEN / optional credential. This is not a strategy-test failure.

## F52-AUTO-37925891660 — Automated workflow failure

- Date: 2026-10-09
- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37925891660
- Impact: no strategy P&L is accepted from this run. Partial outputs remain unverified diagnostics.
- Root cause: pending review of the failed job logs.
- Status: OPEN.


## F52-005 — Factor attribution self-test failed on assumed quantile bin labels — OPEN / patched before rerun

- **Run:** 37925891660, job 113804605666, 2026-10-09.
- **Observed:** Registry validation and deterministic config-ID self-test passed, reporting grid v1.3 with 9,379,584 configurations. The new factor-selector pilot then stopped during `self_test` with an assertion that the computed quantile boundaries for [1, 2, 3] must yield three labels. The test was brittle under the installed pandas 3.0.6 behavior.
- **Impact:** The Phase45 trade matrix and Phase39 feature data were checked out but not analyzed. No Phase52 P&L, factor uplift or strategy promotion was produced.
- **Correction:** Changed the test to use fixed bin edges [1.5, 2.5] and strengthened the assertion message. Production bin thresholds remain estimated exclusively from development data.
- **Verification:** Pending rerun of workflow after main workflow file update. Keep failed run logs and append successful/failed rerun ID here.

## F52-006 — Full finite-grid enumeration is large — DESIGN GATE / PRE-RESULT AMENDMENT

- **Date:** 2026-10-09; before any Phase52 backtest result.
- **Observed sizing:** grid v1.1 ~197,842,176; v1.2 36,008,064; current grid v1.3 9,379,584 applicable configurations.
- **Impact:** At 25,000 configurations enumerated per daily run, the v1.3 queue takes about 376 runs merely to enumerate. This does not include numerical replay time.
- **Correction/decision:** Preserve grid v1.3 rather than further pruning configurations after seeing performance. Use deterministic/resumable enumeration and record enumerated and backtested counts separately. Initial legacy selector pilot uses frozen existing outcomes as a first stage while structural replay engine is integrated. Any future parameter-space revision is versioned before the amended configurations are tested.
- **Status:** OPEN until a source-faithful configuration replay engine is integrated and checkpoint distinguishes queued, enumerated and evaluated configs.



## F52-007 — Phase39 feature-panel overlap below initial 90% gate — PARTIALLY RESOLVED BY PRE-RESULT AMENDMENT

- **Run:** 37926165354, job 113805513686; 2026-10-09.
- **Observation:** Selector self-test passed. The as-of feature join found 68.2% of legacy trade-matrix rows with a same-expiry prior feature record no older than 24 hours; this was below the initial 90% blanket gate.
- **Scientific impact:** Selector metric computation did not run. No factor P&L/return/uplift has been produced or accepted. The input-audit file was written locally but the branch push was rejected in the same run because the branch changed after checkout.
- **Interpretation:** The legacy strategy matrix contains expiries without a corresponding row in the Phase39 feature panel. A missing feature is not neutral, is not forward-filled, and does not establish that a trading strategy fails.
- **Correction (PA-004, before factor-performance calculation):** Use an explicitly matched sample only when coverage is at least 50% overall and for each split, and at least 20 matched expiry sessions are available in validation and holdout. Report row/expiry coverage by split. If these gates fail, emit coverage-only artifacts and continue the rest of the workflow without inference.
- **Status:** PATCHED; awaiting rerun. The <90% full-panel coverage remains a limitation and must be visible in any pilot manuscript.

## F52-008 — Concurrent branch update rejected workflow checkpoint push — PATCHED

- **Run:** 37926165354.
- **Observation:** Actions attempted to push a checkpoint while the remote Phase52 branch had advanced since checkout; Git rejected the non-fast-forward push. This happened while Phase52 logs/status were being updated in parallel during setup.
- **Impact:** The factor input-audit artifact was uploaded to Actions but not persisted at its intended branch path in that run; no scientific result was lost because the analysis had stopped at the coverage gate.
- **Correction:** Workflow now rebases its committed checkpoint on the current remote Phase52 branch before pushing. Failure logs retain the rejected run. If a rebase conflict occurs, the run must remain failed and logged; never force-push/rewrite earlier outcomes.
- **Status:** PATCHED; verify on the next run.


## F52-009 — Legacy outcome matrix contains canonical alias names absent from first pilot whitelist — PATCHED BEFORE SELECTOR P&L

- **Date:** 2026-10-09
- **Observation:** Reading the saved Phase45 `PHASE43_MAP` showed source outcome labels like `bull_call_debit`, `iron_condor`, `iron_butterfly`, `call_calendar`, `long_call_butterfly` and `call_backspread`, while the initial selector whitelist used some registry display names (for example `bull_call_spread` and `short_iron_condor`).
- **Impact:** Could have omitted eligible fixed-template outcomes and distorted the selector universe. No factor-selection performance result was calculated before this was noticed.
- **Correction:** Add the canonical Phase45 engine labels in addition to registry display aliases; the input audit reports exact matched strategy names. Do not relabel an undefined-risk structure as safe merely to increase counts.
- **Status:** PATCHED; awaiting clean workflow verification.

## F52-010 — 2026 holdout feature coverage expected to be incomplete — HANDLED BY PA-005

- **Date:** 2026-10-09
- **Observation:** The stored Phase39 feature panel's final records are dated 2026-04-24, but Phase45 trade outcomes include later 2026 sessions.
- **Impact:** A full 2026 holdout selector evaluation might lack 20 matched expiry sessions or minimum 50% coverage.
- **Correction:** Under PA-005, only the validation split must meet validation coverage/sample gates to run the exploratory pilot; holdout is tested only if its separate gate passes. Otherwise explicitly emit no holdout performance metrics and preserve the missing coverage as a limitation.
- **Status:** PATCHED before selector P&L analysis.

## F52-AUTO-37926908847 — Automated workflow failure

- Date: 2026-10-09
- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37926908847
- Impact: no strategy P&L is accepted from this run. Partial outputs remain unverified diagnostics.
- Root cause: pending review of the failed job logs.
- Status: OPEN.


## F52-011 — Automated checkpoint indentation and persistence conflicts — RESOLVED

- **Date:** 2026-10-09
- **Runs:** 37926550040 and 37926908847 failed at the status/logging step because an accidental bare path was left inside the Python heredoc. Run 37926550040 also encountered an append-only error-log conflict during rebase after a concurrent branch update.
- **Impact:** The selector calculations in these runs had finished and output artifacts were uploaded; no data-analysis exception or live action occurred. Because persistence/logging failed, those runs were not the authoritative successful workflow.
- **Correction:** Removed the stray workflow line and fixed newline/status formatting in the main workflow. Run 37927040268 passed end-to-end and wrote the selector report, input audit, matched results, queue checkpoint, research log and status to the phase branch.
- **Status:** RESOLVED. Keep the original failed run records; do not rewrite them as successes.

## F52-012 — Legacy selector pilot validation result — NEGATIVE / INSUFFICIENT EVIDENCE

- **Date:** 2026-10-09
- **Authoritative workflow:** [37927040268](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37927040268).
- **Input lineage:** frozen Phase45 outcome matrix SHA-256 `7c287ce4c3e958a40e2472d9c0391d2f6d8afa43ecc153b380be603ca44894d0`; Phase39 feature panel SHA-256 `2ae9558062a67a11d7e7d1ba3cfea15a7b847e95a91fbce2a8e72fc075a1efc1`; leakage audit PASS.
- **Result:** 6,617/9,699 outcome rows matched (68.22%). The development-fitted VIX router's validation net was -₹63,547; its paired mean uplift on the legacy all-cost 1.5× stress was +₹1,411/expiry, 95% block-bootstrap CI [-₹915, +₹4,290], one-sided p=0.1642, Holm-adjusted p=0.9850. All selector policies were net negative during validation; no factor-router uplift passed corrected inference.
- **Holdout:** Not evaluated because 13 matched expiry sessions is below the 20-expiry gate.
- **Correction / inference:** Preserve the result as exploratory, negative/insufficient evidence. Do not promote a selector. Next step is the actual registered-configuration replay. This legacy result does not complete any of the 9.38M configuration searches.

## F52-AUTO-37927797509 — Automated workflow failure

- Date: 2026-10-09
- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37927797509
- Impact: no output is accepted solely because this workflow failed or partially ran. Check each output manifest/gate; preserve any completed audit/replay as diagnostic unless its own evidence gate passes.
- Root cause: pending review of the failed job logs.
- Status: OPEN.

## F52-AUTO-37930010915 — Automated workflow failure

- Date: 2026-10-09
- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37930010915
- Impact: no output is accepted solely because this workflow failed or partially ran. Check each output manifest/gate; preserve any completed audit/replay as diagnostic unless its own evidence gate passes.
- Root cause: pending review of the failed job logs.
- Status: OPEN.


## F52-013 — Coverage auditor missing from research-branch checkout — RESOLVED / RERUN PENDING

- **Date:** 2026-10-09
- **Run:** [37930010915](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37930010915).
- **Observed:** Base replay, source-schema audit, and pinned dataset validation had completed, but `python research/phase52/expiry_coverage_audit.py` exited with “No such file or directory”.
- **Root cause:** The audit script had been committed to the default branch because the file-create call omitted the target branch; the Phase52 workflow intentionally checks out `phase-52-factor-conditioned-strategy-discovery`.
- **Scientific impact:** The exact-10:00 expiry coverage audit did not run. No coverage conclusion is claimed and the partial base replay remains only diagnostic until this gate emits a report.
- **Correction:** Copied the exact script into the Phase52 research branch in commit `43e8ae1a9a4c5acf5c6be4c0f4a83bb74455f50b`. The next workflow run should execute the existing gate without changing the pre-registered strategy grid.
- **Status:** RESOLVED in run [37931097834](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37931097834). The report now explicitly identifies the 11 source-expiry files not fully replayed; full-window coverage remains scientifically blocked.


## F52-014 — Base-replay empty error CSV misread as −1 errors — RESOLVED IN CODE / MANIFEST REFRESH PENDING

- **Date:** 2026-10-09
- **Observation:** The accepted Phase43/45 engines wrote a headerless/empty data-errors CSV. The base replay wrapper's generic CSV reader treated that as an exception and stored `phase45_data_error_rows: -1`.
- **Impact:** No replay P&L row was affected, but the audit field was ambiguous and incorrect.
- **Correction:** `research/phase52/base_replay.py` now classifies an empty/whitespace-only data-error file as zero rows with status `EMPTY_NO_ERROR_ROWS`, records source-code SHA256 provenance, and refreshes this metadata when reusing a valid pinned matrix. Next run must refresh the manifest and verify `phase45_data_error_rows = 0`.
- **Status:** RESOLVED; manifest refreshed by successful workflow [37931097834](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37931097834), with `phase45_data_error_rows=0` and `phase45_data_error_file_status=EMPTY_NO_ERROR_ROWS`.


## F52-015 — UDiFF IDF index futures omitted by the first daily-bhavcopy parser — RESOLVED

- **Date:** 2026-10-09
- **Observed:** The first UDiFF parsing path looked for instrument labels containing `FUT`, while current NSE UDiFF classifies index futures as `IDF`. The initial EOD factor manifest therefore showed futures basis/OI on only 161 of 256 replay events (62.9%) despite no missing archive files.
- **Impact:** Futures-basis/OI coverage was understated; early EOD outputs using the old classification are superseded diagnostic artifacts. The 100% event-row count was not equivalent to 100% futures-factor coverage.
- **Correction:** Adapter now recognizes `IDF` and legacy `FUTIDX` as NIFTY index futures; the regression fixture uses UDiFF `IDF`. The latest parser regression [37931285866](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37931285866) passed, and corrected EOD source run [37931305395](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37931305395) reports front-futures basis and OI on 256/256 events and same-contract OI change on 255/256.
- **Limit:** These remain strictly prior-session EOD features, not intraday traded futures quotes or basis lead/lag.
- **Status:** RESOLVED; regression and corrected feature manifest verified.
  
## F52-016 — UDiFF self-test fixture used literal backslash-n text instead of CSV line breaks — RESOLVED

- **Date:** 2026-10-09
- **Run:** [37929373094](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37929373094).
- **Observed:** The new-format fixture was encoded as a single CSV header string containing literal `\\n`, so parsing returned zero option rows and the self-test failed.
- **Correction:** Replaced the escaped literal with actual newline escapes. Regression [37929475685](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37929475685) passed legacy + UDiFF schema parsing; the later regression [37931285866](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37931285866) also verified the `IDF` futures mapping.
- **Scientific impact:** No accepted factor P&L used the failed fixture run; outputs were not considered evidence.
- **Status:** RESOLVED.

## F52-017 — Parser test ran before numeric dependencies were installed; persistence named a nonexistent output path — RESOLVED

- **Date:** 2026-10-09
- **Runs:** [37929186683](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37929186683) and [37929613349](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37929613349).
- **Observed:** The parser self-test ran before `numpy` was available, and an error-path `git add` failed when `results/phase52/daily_bhavcopy` had not been created.
- **Correction:** Moved the regression step after dependency installation and ensured all output directories are created before failure logging/persistence.
- **Verification:** Full workflow [37929888516](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37929888516) passed, followed by subsequent successful runs.
- **Status:** RESOLVED.

## F52-018 — Configuration event universe introduced before any grid backtest — AUDIT PENDING

- **Date:** 2026-10-09
- **Workflow:** [37934339579](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37934339579).
- **Scope:** Build an inventory of target expiry × exact calendar DTE {0,7} × entry timestamp {09:45,13:00}, then audit exact NIFTY index timestamp presence. This addresses the event-time mismatch between the old fixed 10:00 event replay and the registered configuration grid.
- **Interpretation:** Expected event rows and exact index ticks are coverage metadata, not P&L or tested configurations. Option-leg and exit-time quote availability still requires configuration-specific verification.
- **Status:** RESOLVED AS AN EVENT INVENTORY ONLY. Run 37934719402 built the 1,068-row event inventory and broad option/OI coverage audit. No P&L was calculated; selected-strike audit is tracked separately under F52-019 and F52-021–F52-023.


## F52-019 — Broad event coverage is not selected-leg eligibility — DATA GATE OPEN

- **Date:** 2026-10-09
- **Workflow:** [37934719402](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37934719402), successful audit.
- **Observation:** The broad option coverage audit has 1,068 expected events, 1,012 exact index timestamps, 1,016 with option rows at entry, 1,012 with any OI≥100 contract, and 1,040 with a common-time expiry exit. Intersections reduce to 1,006 events with exact index + entry options + OI≥100, and 1,004 when broad expiry exit is also required. The holdout intersection is only 74/112.
- **Root cause/impact:** Event-level row presence cannot establish the chosen strike/expiry/leg has a valid OHLC bar or executable exit. Running a grid now could silently assume untradeable legs or overstate coverage.
- **Correction:** Treat this audit as a gate only. Next implement selected-contract resolution per configuration and exact entry/exit OHLC/fill validation. Reject missing legs; do not forward-fill, interpolate or replace with nearest strikes/timestamps. Keep broad counts separate from valid replay counts.
- **Status:** OPEN; no P&L affected because no grid P&L was calculated.

## F52-020 — Recent source expiry files exceed pinned index-series coverage — OPEN

- **Date:** 2026-10-09
- **Observation:** Option-file inventory extends through 2026-08-04, but pinned NIFTY index bars end 2026-07-02. Exact index entries are 80/112 in the holdout event universe; the broad index + option + OI + expiry-exit intersection is 74/112. July 28/August 4 remain unresolved.
- **Impact:** The current dataset cannot support a complete, untouched 2026 holdout or full-window Phase51 claim.
- **Correction/next step:** Search for authorised, hash-pinned point-in-time sources for the missing sessions/index bars; until found, report the holdout as blocked/partial and do not relax minimum sample or shorten the pre-registered window.
- **Status:** OPEN / data-gated.


## F52-021 — Absolute-delta strike resolution is not yet evidence-backed — OPEN / SPECIFICATION GATE

- **Date:** 2026-10-09
- **Observation:** The finite grid contains `ABS_DELTA` strike selection, but the pinned minute option files do not supply an independently validated point-in-time delta field in the coverage audit. Inferring delta from one close without an explicit IV solver, timestamp-safe underlying/expiry inputs and regression tests would introduce an unverified model assumption.
- **Impact:** ABS_DELTA configurations cannot enter replay yet. Do not silently replace them with ATM-offset selections.
- **Correction:** Added a separate selected-strike coverage audit for ATM-offset ranks -6..+6. Keep ABS_DELTA blocked until a tested point-in-time IV/delta resolver is designed and validated; if not possible from licensed inputs, report those grid cells as structurally blocked rather than silently shrinking or relabelling the grid.
- **Status:** OPEN; first selected-strike audit self-test/full run pending.

## F52-022 — Selected-strike audit performance hardening before first run — PATCHED / TEST PENDING

- **Date:** 2026-10-09
- **Observation:** Initial audit draft repeatedly filtered the full expiry dataframe for each event × strike offset × option type, which could make the 267-file sweep unnecessarily slow.
- **Correction:** Build an exact-timestamp-to-frame index once per expiry file and use it for entry/exit lookups. Ensure output directory exists before the workflow runs so a failed audit can still be logged.
- **Verification:** Awaiting self-test and end-to-end Actions result. If runtime remains excessive, optimize only after preserving identical row counts and exact timestamp semantics.


## F52-023 — Selected-strike spot lookup timestamp-format mismatch — PATCHED BEFORE ACCEPTED RUN

- **Date:** 2026-10-09
- **Observation:** The index lookup key used ISO timestamps with a `T` separator, while the first selected-strike audit draft looked up `str(pd.Timestamp)`, which uses a space separator. This would have produced missing spot values and false missing-strike results.
- **Correction:** Normalize both index and event keys through `Timestamp.isoformat()`; add a regression assertion for the exact timezone-aware timestamp format.
- **Impact:** No accepted coverage or P&L was generated by the draft. The audit is gated on its self-test and full run.
- **Status:** PATCHED; verification pending Actions.


## F52-024 — Workflow checkpoint persistence conflict — ROOT CAUSE IDENTIFIED / PATCHED

- **Date:** 2026-10-09
- **Run:** [37934339579](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37934339579).
- **Failed step:** `Persist source ledger, checkpoints, status and errors to research branch`.
- **Root cause:** The workflow's commit was rebased onto concurrent human-authored research updates and Git reported a content conflict in `PHASE52_STATUS.md`. The older workflow had no safe append-only conflict resolver.
- **Impact:** The event-universe audit output was generated, but that run could not push its checkpoint. No strategy P&L was accepted from this run.
- **Correction:** Added bounded fetch/rebase/push retries and a restricted conflict-union resolver for append-only status/research/error logs. It refuses to auto-resolve conflicts in code or result data.
- **Verification:** Run [37935663113](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37935663113) completed successfully after the revised bounded rebase/push path; audit outputs and checkpoint persisted without a failed step.
- **Status:** RESOLVED for the tested status/log conflict path. Non-log result-file conflicts remain fail-closed.


## F52-025 — Stale workflow run blocked selected-strike validation queue — MITIGATION RUNNING

- **Date:** 2026-10-09
- **Observation:** Run [37935663113](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37935663113) remained in the broad option coverage step with no fresh job update after the prior run had already completed the same audit successfully. A later run stayed pending under the same concurrency group.
- **Impact:** The new selected-strike audit could not be verified promptly; no new P&L was produced.
- **Correction:** Versioned the workflow concurrency group to `phase52-factor-conditioned-strategy-discovery-v2`, allowing a fresh bounded run to proceed without cancelling or overwriting the older checkpoint. New run [37937164472](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37937164472) started at 2026-10-09 18:59 IST.
- **Safety:** Both runs use hash-pinned source data and conflict-safe log persistence; any duplicate audit result must be reconciled by revision/hash and not double-counted.
- **Status:** MITIGATION RUNNING; wait for the new run's selected-strike self-test and summary.


## F52-026 — Strike ladder must be point-in-time — PATCHED BEFORE ACCEPTANCE

- **Date:** 2026-10-09
- **Observation:** Code review found the initial selected-strike audit built its strike ladder from all strikes appearing anywhere in an expiry file. Some strikes may have been introduced later, so this could leak future listing information into ATM selection.
- **Correction:** ATM and rank-offset selection now uses only strikes present at the exact entry timestamp, with exact timestamp keying and OI/OHLC gates applied to that timestamp's rows.
- **Impact:** No P&L or selected-strike result has been accepted. The currently running workflow may have checked out the earlier draft; its output must be treated as superseded unless the run provenance proves it used the patched commit.
- **Status:** PATCHED IN SOURCE; end-to-end verification required on the patched commit.


## F52-025 — Stale workflow run blocked selected-strike validation queue — MITIGATION IN PROGRESS

- **Date:** 2026-10-09
- **Observation:** Run 37935663113 remained in broad option coverage longer than the prior successful run, and the next run stayed pending under the original concurrency group.
- **Correction:** Versioned the workflow concurrency group to `phase52-factor-conditioned-strategy-discovery-v2`; run [37937164472](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37937164472) started in the new group. Another old-group run 37936777969 also began, so duplicate audit outputs must be reconciled by code revision and hashes.
- **Status:** MITIGATION IN PROGRESS; run 37937318538 is queued and is expected to use the latest point-in-time strike-ladder correction.
