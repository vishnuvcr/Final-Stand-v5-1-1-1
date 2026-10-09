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


## F52-027 — Concurrent stale audit could overwrite patched strike coverage — PREVENTIVE GUARD ADDED

- **Date:** 2026-10-09
- **Observation:** Runs 37936777969 and 37937164472 started before the latest point-in-time strike-ladder correction and may complete after the corrected run. Without a source-revision guard, an older run could publish its stale selected-strike CSV after a newer run.
- **Correction:** Workflow persistence now compares the selected-strike auditor in the checked-out research branch with the current remote branch. If the source changed during the run, it discards only that run's stale selected-strike output (or restores the remote result state) while preserving other outputs. It fails closed for non-log conflicts.
- **Verification:** Guard added to main and branch workflows; next Actions run must confirm the guard and patched self-test execute successfully.
- **Status:** PATCHED IN WORKFLOW; verification pending.


## F52-028 — Stale-output cleanup could leave an invalid Git pathspec — PATCHED BEFORE VERIFICATION

- **Date:** 2026-10-09
- **Observation:** The stale-result guard removes the selected-strike output directory when the remote branch has no accepted output. The persistence step later stages that directory by path, so an absent/empty directory could cause a second persistence failure.
- **Correction:** After removing stale output when no remote result exists, recreate the directory and add a .gitkeep placeholder. The pathspec therefore remains valid and no stale CSV is committed.
- **Status:** PATCHED IN MAIN AND BRANCH WORKFLOWS; end-to-end verification pending.


## F52-030 — Stale registry audit could overwrite PA-010 specification reconciliation — PREVENTIVE GUARD ADDED

- **Date:** 2026-10-09
- **Observation:** Two workflow runs checked out the older strategy-specification CSV before PA-010 reconciled 11 named presets. Their generated registry_audit.json could become stale if persisted after the updated registry was validated.
- **Correction:** Workflow persistence now compares the checked-out strategy_specifications.csv with the current remote branch and restores the remote registry_audit.json (or discards the stale copy) when the specification snapshot changed.
- **Impact:** No P&L is affected; registry audit counts must correspond to the exact specification CSV hash.
- **Status:** PATCHED IN MAIN AND BRANCH WORKFLOWS; end-to-end verification pending.


## F52-031 — First selected-strike audit ran on pre-correction snapshot — NOT ACCEPTED

- **Date:** 2026-10-09
- **Run:** 37937164472; the selected-strike audit step completed successfully at the process level.
- **Issue:** This run checked out the earlier strike-ladder implementation, which sourced candidate strikes from the full expiry file rather than the exact entry-time contract set. Therefore a green step is not a valid scientific pass.
- **Handling:** Mark the run's selected-strike output stale and do not use its counts. The workflow now compares the auditor against the remote branch before persistence and discards/restores stale output. The next queued run should use the point-in-time correction and reconciled PA-010 strategy specs.
- **Status:** Superseded by F52-033: the patched-source rerun [37942202655](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37942202655) passed the exact-entry strike-ladder guard; only its accepted summary and files are retained. The earlier counts remain rejected.


## F52-032 — Concurrent generated-result conflicts blocked checkpoint persistence — PATCHED IN WORKFLOW

- **Date:** 2026-10-09
- **Run:** [37937164472](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37937164472).
- **Symptom:** The data/audit steps completed, but persistence failed because two workflow runs had concurrently changed generated artifacts (queue checkpoint, source ledger, manifests, coverage summaries and EOD outputs). The conflict resolver correctly refused to overwrite non-log files.
- **Root cause:** Temporary concurrency-group versioning allowed two old/new group runs to overlap. Both started from the same branch snapshot and attempted to persist the same generated paths.
- **Correction:** Restored one shared concurrency group and extended the conflict resolver narrowly: append-only status/research/error logs are unioned; conflicts under generated-result directories preserve the already-persisted remote version so the losing deterministic shard can be re-emitted. Conflicts in source/code files still fail closed. The new shared-group run will wait for the older run to finish.
- **Status:** PATCHED IN MAIN AND BRANCH WORKFLOWS; end-to-end verification pending.


## F52-033 — Selected-strike audit corrected and rerun — ATM-OFFSET COVERAGE ACCEPTED; DELTA STILL BLOCKED

- **Date:** 2026-10-09
- **Authoritative workflow:** [37942202655](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37942202655), completed successfully after the corrected source was checked out.
- **Correction verified:** The strike ladder is now resolved from contracts present at the exact entry timestamp, not all strikes appearing anywhere in the expiry file. This prevents future-listed contracts from leaking into historical strike selection. Timestamp-indexed lookups preserve exact timestamps; no nearest timestamp or interpolation is used.
- **Result:** 267/267 option expiry files audited; zero file errors; all 1,068 expected events represented; 27,768 event × offset × option-type rows across offsets -6..+6; 11,222 leg rows meet the entry OI≥100 gate; 15,718 leg rows have valid target-expiry exit OHLC; 11,108 leg rows satisfy exact index + entry OI + valid target-expiry exit.
- **Interpretation:** Coverage is reported at individual selected ATM-offset leg-event level, not full strategy level. It does not establish all legs in a multi-leg strategy can execute, does not test path-dependent exits, and contains no P&L. The two 2026-07-28/2026-08-04 sessions still have no usable expiry exit bars in this pinned source; full holdout remains blocked.
- **Remaining gate:** ABS_DELTA configurations are still blocked until the separate point-in-time IV/delta resolver passes regression and coverage tests. The pinned dataset is CC BY-NC 4.0, so any research outputs from it remain non-commercial/research-only pending rights review.
- **Status:** ATM-offset source coverage audit PASS; variable-grid replay NOT STARTED; no strategy promotion.


## F52-034 — Selected-strike offsets used rank instead of configured strike steps — SUPERSEDED / CORRECTED CODE AWAITING RERUN

- **Date:** 2026-10-09.
- **Affected output:** selected ATM-offset coverage artifact from run [37942202655](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37942202655); 27,768 leg-event rows.
- **Observed:** The script advanced by ordinal rank in the available strike list rather than by `atm_offset_steps × modal strike spacing`. A missing/intermittent listed strike could change the effective offset, so rows did not faithfully represent grid offsets 1 and 3.
- **Impact:** Coverage counts were not exact evidence for the registered ATM-offset configurations. The script had no P&L output, so no profitability result is affected.
- **Correction:** Compute modal strike gap from the exact entry-time option snapshot (Phase43 helper semantics), resolve ATM from that snapshot using exact-time NIFTY index `open`, then target exact arithmetic strike `ATM + offset × step`. If the exact contract is absent, record missing.
- **Status:** PATCHED in main and research branch; a regression and fresh workflow output are pending. Old counts must not be reused as current coverage.

## F52-035 — ATM-offset audit used index close instead of registered entry open — SUPERSEDED / CORRECTED CODE AWAITING RERUN

- **Date:** 2026-10-09.
- **Observed:** The previous strike coverage screen used the NIFTY index bar `close` at the configured entry timestamp as its ATM anchor. The frozen protocol specifies the index bar `open` at that timestamp for selection; using the close is incompatible with an open-fill decision.
- **Impact:** Selected ATM anchors and strike coverage for that audit could differ from the registered config semantics. No P&L was calculated in that audit.
- **Correction:** Index reader and `spot_map` now use exact-timestamp `open`. The regression includes a 50-point modal-step fixture and verifies the target arithmetic.
- **Status:** PATCHED; rerun pending.

## F52-036 — Delta resolver regression fixture used 180 volatility and invalid below-intrinsic case — RESOLVED IN CODE / RERUN PENDING

- **Date:** 2026-10-09.
- **Run:** [37944408314](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37944408314), failed before any market-data delta audit.
- **Root causes:** The synthetic known-IV test used `sigma=180.0` instead of `0.18`; the negative test used a call strike above spot, so premium 0.01 was not below intrinsic.
- **Correction:** Synthetic IV is now 18%; the negative test is an in-the-money call with strike 21,900 versus spot 22,000 and premium 0.01.
- **Status:** Corrected in main and branch code; the regression rerun must pass before any delta coverage result is accepted.

## F52-037 — Delta strike selector used same-entry-bar close (lookahead against open fill) — CORRECTED / RERUN PENDING

- **Date:** 2026-10-09.
- **Observed:** The first delta-selection audit solved IV/delta using the entry-bar option close and same-time index close, then described it as point-in-time at the bar open.
- **Impact:** The model-based strike choice would have used information unavailable at the OHLC open fill. This is an audit-engine timing error; no Phase52 grid P&L was computed.
- **Correction:** Delta selection now uses exact prior completed one-minute option/index closes at `entry_ts − 1 minute`, checks OI from that prior bar, and separately requires the selected contract to have a valid exact entry-time OHLC bar/open. No nearest-minute fallback is used; missing exact prior data are recorded.
- **Status:** PATCHED; full audit rerun pending.


## F52-038 — ATM-offset OI gate used same-entry-bar OI for an open fill — PATCHED / RERUN PENDING

- **Date:** 2026-10-09.
- **Observed:** The selected ATM-offset audit read OI from the exact entry-time bar and then checked it as an eligibility gate while separately assuming an entry fill at that bar's open.
- **Impact:** Coverage can be overstated if the OI field is only observed after the bar completes; no P&L was calculated in the audit.
- **Correction:** Check OI>=100 on the exact prior completed one-minute bar at entry_ts minus one minute, require a unique valid exact entry bar/open independently, retain current-bar OI as diagnostic only, and fail closed when prior OI is missing. No OI forward-fill is permitted.
- **Status:** Code patched on main and research branch. The currently running factor workflow checked out the earlier commit and is not accepted for this selected-leg gate. Rerun after that run finishes; delta audit queued afterward.


## F52-039 — Replay-kernel test manifest used literal runner-temp path — RESOLVED

- **Date:** 2026-10-09.
- **Initial run:** [37957499754](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37957499754).
- **Observed:** The deterministic replay-kernel self-test printed `SELF_TEST_PASS`, but its following manifest writer tried to create `$RUNNER_TEMP/phase52-kernel-test/manifest.json` as a literal relative path and exited with FileNotFoundError. Thus the overall workflow failed although the kernel assertions passed.
- **Correction:** Python manifest path now resolves `os.environ["RUNNER_TEMP"]` and writes inside the created output directory.
- **Verification:** [Run 37957753452](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37957753452) completed successfully, wrote evidence and uploaded its artifact. Kernel tests: exact bar selection, common exit timestamps, hand-computed gross P&L, six cost combinations, prior OI gate, liquidity-range proxy, TP next-open execution, blocked family/data gates.
- **Scientific impact:** No real-market P&L existed in either run. This was test-evidence persistence only.
- **Status:** RESOLVED.

## F52-040 — Closure of prior ATM/delta coverage-audit timing defects — VERIFIED, P&L STILL BLOCKED

- **Date:** 2026-10-09.
- **ATM-offset:** [Run 37956261518](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37956261518) produced the corrected summary with code/protocol fingerprints, 267/267 files, zero source errors, exact-time index open/modal strike steps, and prior-completed-minute OI eligibility. Prior output from run 37942202655 remains superseded.
- **ABS_DELTA:** [Run 37956675818](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37956675818) produced the corrected prior-minute/model-IV summary with code/protocol fingerprints, 267/267 files, zero source errors, and no current-bar close lookahead. Only 2,232/4,272 selected delta/type rows had a valid exact entry-bar fill reference; 3,892 rows passed predecision OI.
- **Inference:** These successful audits mean only that the coverage/model-selection scans executed cleanly. Missing exact entry bars and the incomplete index tail remain explicit. They are not completed strategy legs, P&L, or promotion evidence.
- **Status:** Audit implementation defect gate closed; production strategy resolver and complete grid P&L remain not started.


## F52-039 — Replay-kernel evidence manifest wrote to literal runner-temp path — RESOLVED

- **Date:** 2026-10-09.
- **Initial run:** [37957499754](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37957499754).
- **Observed:** Synthetic kernel assertions printed `SELF_TEST_PASS`, but the following Python manifest writer addressed `$RUNNER_TEMP/phase52-kernel-test/manifest.json` as a literal path and raised FileNotFoundError.
- **Impact:** The first overall workflow was red although its tests had passed; the evidence manifest was not written. No market data or P&L was involved.
- **Correction:** Manifest path now uses `os.environ["RUNNER_TEMP"]`.
- **Verification:** [Run 37957753452](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37957753452) passed and uploaded test evidence. Self-test covered exact bar matching, common timestamps, prior-bar OI, ₹1,293.50 hand-computed gross P&L, six brokerage/slippage cases, OHLC-range proxy, TP next-open, and fail-closed config gates.
- **Status:** RESOLVED.

## F52-040 — Closure of PA-011/PA-012/PA-013 coverage implementation defects — VERIFIED; full replay still blocked

- **Date:** 2026-10-09.
- **ATM-offset:** [Run 37956261518](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37956261518) emitted the corrected code/protocol fingerprinted result across all 267 source files with zero source errors. It uses exact-time NIFTY open, exact-time modal strike spacing, true strike-step arithmetic, and OI from the exact prior minute.
- **ABS_DELTA:** [Run 37956675818](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37956675818) emitted a fingerprinted diagnostic result for all 4,272 checks with zero file errors, prior-bar-only input semantics, and a separate exact entry-bar open gate. Only 2,232 selection rows have valid entry fill bars.
- **Inference:** These close the audit-code defects, not the market-data or strategy profitability gates. They are not evidence of returns or that every configured multi-leg position is executable.
- **Status:** Coverage-audit implementation gate resolved; end-to-end configuration strategy runner and full finite-grid P&L are still not implemented.


## F52-021 — Reference-lot scale absent from resolved leg quantities — RESOLVED BEFORE HISTORICAL P&L

- **Date:** 2026-10-09
- **Observed during resolver audit:** `reference_lots_per_leg` was included in the resolved configuration record, but `quantity_lots` was not multiplied by it after the optional first-two-leg ratio override.
- **Impact:** Any eventual historical replay could understate or misstate position size, P&L, turnover, brokerage and risk whenever the grid used `reference_lots_per_leg=2`. No historical Phase52 grid P&L had been calculated, so no accepted backtest result was affected.
- **Correction:** Resolver code now validates a positive integer reference-lot input, applies ratio overrides first, then scales every resolved leg quantity. Tests assert a ratio spread becomes [4,2] under ratio [2,1] and reference lot scale 2, and a native 1:2:1 butterfly becomes [2,4,2].
- **Verification:** Source-bound resolver tests and the end-to-end whole-position workflow [37960484240](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37960484240) passed after the correction.
- **Status:** RESOLVED; zero historical configuration results affected.

## F52-022 — Whole-position test fixture accidentally overrode the native butterfly ratio — RESOLVED

- **Date:** 2026-10-09
- **Run:** [37960340815](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37960340815), failed at the butterfly lot-scaling assertion; source-bound resolver stage had already passed.
- **Root cause:** The supposed “native 1:2:1 butterfly scaled ×2” case explicitly passed `leg_ratio=[1,1]`, which correctly replaced the first two leg quantities under the frozen protocol. The test setup was wrong; the resolver output [2,2,2] was consistent with the supplied override, not evidence that the scale patch failed.
- **Correction:** Removed the ratio override from this test case so it now exercises native template quantities [1,2,1] multiplied by reference-lot scale 2. Added an explicit kernel non-common-timestamp intersection assertion.
- **Verification:** Rerun [37960484240](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37960484240) passed all steps: resolver self-test, 45-template synthetic position integration, kernel/Phase43 cost parity and evidence upload.
- **Scientific impact:** Failed synthetic-only attempt; no historical data/P&L were accessed. The failed run remains preserved.
- **Status:** RESOLVED.

## F52-023 — Phase52 status and research log contained literal escaped newline markers — RESOLVED

- **Date:** 2026-10-09
- **Observed:** `PHASE52_STATUS.md` and `PHASE52_RESEARCH_LOG.md` contained hundreds of literal backslash-n sequences instead of real Markdown line breaks, making those documents difficult to read and reducing reliable status scanning.
- **Impact:** Research code/results were unaffected, but status/log readability and auditability were degraded.
- **Correction:** Normalized newline separators in both Markdown files; existing research content and historical entries were preserved. Future writes should use real newlines, and post-update line-count/escape checks are added to the release checklist.
- **Status:** RESOLVED in this checkpoint.

## F52-HIST-37962192723 — Bounded historical pilot failed or did not produce an accepted report

- **Date:** 2026-10-09T16:58:30.925413+00:00
- **Workflow:** https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37962192723
- **Stage outcomes:** self-test=success; plan-only=success; replay=failure; job=failure.
- **Observation:** Historical pilot report missing or workflow non-success. Do not infer P&L from partial artifacts.
- **Impact:** No result from this run is accepted unless report.json exists, input/source hashes match the frozen manifest and the overall job succeeds.
- **Next:** inspect the failing step log, fix the root cause, rerun with a new run ID, and preserve this entry.
- **Status:** OPEN / FAILED RUN PRESERVED.


## F52-HIST-DUP-001 — Byte-identical duplicate option rows obstructed the first historical pilot

- **Date:** 2026-10-10
- **Evidence:** Pilot v0.1 report at `results/phase52/historical_pilot/report.json`; 274/480 config-event rows blocked with duplicate exact contract bars, 205/480 excluded by the OHLC high-low/open proxy, one row replayed.
- **Root cause:** The runner required exactly one row for each contract/time but did not remove byte-identical full-row duplicates in the normalized pinned source partition.
- **Correction:** v0.2 removes only full-row duplicates after canonical normalization and logs counts per source file. Duplicate rows that differ in any column are retained and fail closed; no averaging, nearest-bar substitution or conflict selection is permitted.
- **Scientific impact:** v0.1 is an engineering diagnostic with insufficient effective sample and cannot support any profitability claim. v0.2 is coverage debugging only; frozen events/configurations/costs are unchanged.
- **Status:** PATCHED; regression and workflow rerun pending.

## F52-HIST-LIQ-001 — OHLC range proxy is not observed bid/ask spread

- **Date:** 2026-10-10
- **Observation:** Pilot's `liquidity_max_spread_pct=2` is implemented as `100*(high-low)/open`.
- **Impact:** This is an intrabar range proxy, not quoted spread, so it must not be interpreted as a liquidity or executable-fill measurement. The current preregistered 2% threshold is retained as a conservative OHLC data-quality exclusion to avoid outcome-informed relaxation.
- **Next:** Seek point-in-time bid/ask or trade/quote data. Until then, report the exclusion separately and do not claim live liquidity validation.
- **Status:** OPEN / methodology limitation.

## F52-HIST-PERSIST-37980455805 — Pilot replay succeeded but checkpoint persistence failed

- **Date:** 2026-10-10.
- **Workflow:** https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37980455805
- **Observed:** self-test, plan and replay steps succeeded; the report showed 480 reconciled statuses (379 OHLC-range exclusions, 100 leg-eligibility blocks, 1 replay pass) and six cost scenario rows. The job then failed in persistence.
- **Root cause:** persist_historical_pilot.py committed log/status edits from its checked-out snapshot and attempted to rebase onto a newer branch tip. The three shared files PHASE52_STATUS.md, PHASE52_RESEARCH_LOG.md and PHASE52_CHAT_LOG.md had changed remotely, so the automatic rebase conflicted. Artifact ID 11641042776 was uploaded before this failure.
- **Scientific impact:** no replay exception or source-file error was reported; the coverage result is still only an engineering diagnostic, not a usable profitability sample. Do not infer success from the artifact upload or the replay-stage status alone.
- **Correction path:** preserve the run summary under a unique run-specific filename; fix persistence to read the latest branch version and append idempotently after fetching it, or isolate generated results from shared-log updates. Run a regression or successful checkpoint write before the next pilot workflow.
- **Status:** OPEN / WORKFLOW PERSISTENCE DEFECT; source and replay outcomes remain separately reported.

## F52-OPENCHART-001 — OpenChart cannot yet be treated as a complete historical options source

- **Date:** 2026-10-10.
- **Source:** https://github.com/marketcalls/openchart at pinned commit a207108890c96a9830b35a8d15442c896ea0a9d6.
- **Observed:** inspected client schema returns OHLCV for one selected instrument; no exposed historical all-strike chain API, OI, Greeks, bid/ask, depth or trade-by-trade feed was found. Full expired-contract discovery, oldest history and timestamp convention remain unverified. Public issue list includes data access/rate-limit complaints.
- **Impact:** the project cannot assume this source fills every contract/session, factor input or execution-price requirement. Absence of fields cannot be substituted with inferred values.
- **Correction / next step:** run bounded low-frequency probe, verify target sessions 2026-07-28 and 2026-08-04 against an independent archive, audit expected-vs-observed contract coverage and timestamps, and confirm NSE data-use/storage terms. Preserve raw market data outside the public repo until permitted.
- **Status:** SOURCE CANDIDATE ONLY / NOT ACCEPTED.

## F52-OPENCHART-002 — Dynamic symbol search returns index-only identical result set — OPEN / SOURCE BLOCKER

- **Date:** 2026-10-10.
- **Evidence:** Final bounded run [37982673873](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37982673873), report `results/phase52/openchart_probe/runs/37982673873/probe_report.json`.
- **Observation:** The FO query for NIFTY and the IDX control returned the same 20 rows. Four further FO queries (current-month option prefix, the README's documented option example, and the two missing-session prefixes) also returned the identical normalized result fingerprint `6284a00ec2a8cc5c102d30f0b7e3dce5d5ccb9d8588b5c6a98b9a440d761d837`; every result was typed Index. No options or futures were identified. Charting search returned HTTP 200, while the cookie/homepage request returned HTTP 403.
- **Impact:** The current `NSEData.search()` implementation cannot discover the requested option contract universe in this test. No history request was made, so this is not proof that the underlying historical endpoint itself cannot return bars.
- **Correction / next step:** Do not use this wrapper for Phase 52 instrument discovery until request/query semantics are repaired and verified. Alternatively, use a trusted, independently verified contract/token master and test `historical_direct()` for known exact contracts. Then reconcile complete expiry/strike/date coverage, OHLC/timestamps, required factor inputs and permitted data retention.
- **Status:** OPEN / SOURCE NOT ACCEPTED FOR ALL-OPTIONS ACQUISITION.

## F52-OPENCHART-003 — First source-probe report under-specified instrument classification — RESOLVED FOR DIAGNOSTICS

- **Date:** 2026-10-10.
- **Observation:** The initial report counted options/futures but did not include the distribution of returned `type` labels, query-match counts or a normalized-result fingerprint. A zero option count alone could not distinguish a classification bug from irrelevant/search-insensitive results.
- **Correction:** Expanded the probe to report type histograms, CE/PE/FUT suffix counts, query-match counts and a SHA-256 fingerprint of only symbol/type/exchange fields; raw symbols, descriptions, tokens and OHLCV remain unpersisted.
- **Verification:** Final run [37982673873](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37982673873) shows all six result sets are identically index-only.
- **Status:** RESOLVED AS A DIAGNOSTIC DEFECT; underlying source blocker remains open.

## F52-OPENCHART-004 — Planned target windows were initially labeled as tested — RESOLVED

- **Date:** 2026-10-10.
- **Observation:** An earlier report field `target_date_windows_tested=2` could imply history requests occurred, even when `historical_probes` was empty.
- **Correction:** The report schema now distinguishes `target_date_windows_planned` from `target_date_windows_with_history_requests`.
- **Verification:** Final run [37982673873](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37982673873) records 2 planned windows and 0 history requests.
- **Status:** RESOLVED IN REPORT SCHEMA.

## F52-RESUME-001 — Pilot persistence conflict and coverage diagnosis queued — OPEN

- **Date:** 2026-10-10.
- **Evidence:** historical pilot run [37980455805](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37980455805) replay succeeded but final persistence failed when rebasing stale log/status edits onto a branch tip with concurrent changes.
- **Scientific impact:** the 480-row replay summary is reconciled separately, but automated checkpoint completion is not reliable yet. Current coverage remains 379 OHLC-range exclusions, 100 leg-eligibility blocks and 1 execution. No profitability inference.
- **Next correction:** make persistence latest-tip-aware and idempotent; add a regression test for concurrent append-only log updates and unique run artifacts. Then decompose each first-failure status using the frozen row ledger and exact source provenance.
- **Acceptance:** a successful persistence test plus a complete 480-row status reconciliation. Never turn excluded/blocked rows into losses or relax the frozen filter to manufacture coverage.
- **Status:** OPEN / NEXT PHASE 52 ENGINEERING GATE.


## F52-DATA-PROVENANCE-001 — Pilot version/count mismatch

- Date: 2026-10-10
- Evidence: committed `results/phase52/historical_pilot/report.json`, `excluded_events.csv`, and `event_replay.csv` identify v0.1 and report 274 `BLOCKED_LEG_ELIGIBILITY`, 205 `EXCLUDED_OHLC_RANGE_PROXY`, and 1 `REPLAY_PASS` (480 total).
- Conflicting record: later v0.2 run summary reports 100 blocked / 379 excluded / 1 pass. The v0.2 artifact has not yet been reconciled against these committed files.
- Impact: canonical pilot status counts and root-cause breakdown remain OPEN. Neither count set may be silently substituted for the other; no strategy ranking or promotion.
- Next: retrieve run 37980455805 artifact and v0.2 run outputs, compare run IDs, manifests, source hashes and row keys; only then publish a versioned breakdown and rerun if warranted.
- Status: OPEN.

## F52-DATA-PROVENANCE-001 — RESOLVED by artifact reconciliation (2026-10-10)

- **Resolution:** retrieved run 37980455805 artifact ID 11641042776 and inspected `report.json`, `pilot_manifest.json`, and both event CSVs directly. All artifact outputs identify v0.2 and agree on 379 OHLC-proxy exclusions / 100 prior-OI eligibility blocks / 1 replay pass (480 total). The different 274/205/1 counts in committed branch files belong to the prior v0.1 run. There is no v0.2 row-count discrepancy; outputs must continue to be labeled by run ID/version.
- **Root-cause diagnosis:** all 100 v0.2 eligibility blocks have prior OI 0.0 and status `PRIOR_OI_MISSING_OR_BELOW_GATE`; all are validation rows. The 379 OHLC failures are range-proxy breaches, not bid-ask spread observations.
- **Verified data:** artifact digest `sha256:34b987e2fa19821898582145ae6d4403a64f6d9d085f588628a07b6e78da2aaa`; no source file errors or replay exceptions. Still insufficient usable coverage, no profitability inference.
- **Status:** RESOLVED as a provenance issue; coverage limitation remains OPEN under F52-RESUME-001.