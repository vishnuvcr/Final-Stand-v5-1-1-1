# Phase 50B Chat / Decision Log

## 2026-10-07
User requested continuation of research, inclusion of seven supplied Tradetron strategies, and a search for earlier strategies across the user's GitHub repositories.

Actions taken:
- resolved the seven strategy names against finished Tradetron account backtests;
- preserved the seven supplied public report links in the frozen registry;
- searched the user's GitHub repositories for earlier NIFTY option strategy lineages;
- created a dedicated Phase-50B branch before numerical selection;
- preserved the running parent Phase-50 far-OTM workflow without cancelling it.

Research rule: prior reported performance remains provenance/control evidence only and is not imported as prospective validation evidence.

## 2026-10-07 — Resume / Proceed cycle

User requested continuation without pausing. Work performed:
- Rechecked the Phase-50B research plan, preregistration, registry, status and error log before proceeding.
- Confirmed canonical Actions run 37572527043 is the current TT-02 common-cost replay after a performance-only correction.
- Closed Phase 50 formally at NO PROMOTION; no Phase-50 candidate was promoted.
- Audited source semantics for TT-01, TT-03, TT-04, TT-05, TT-06 and TT-07 and created dedicated source-audit files.
- Added a source audit for the prior Final-stand-v2 OTM4/OTM5/OTM6 Monte-Carlo strategy.
- Logged the TT-02 replay performance bottleneck and corrected timestamp indexing / implied-vol computation without changing the mathematical replay definition.
- Added current literature review material and preserved the evidence hierarchy: native Tradetron results are provenance only; common-cost chronological replay is primary evidence.
- No Phase-50B strategy has been promoted. The TT-02 numerical result remains pending.


## 2026-10-07 — Proceed cycle: cost audit and TT-04 pre-execution preparation

- Confirmed canonical run 37572837253 remains active in TT-02 numerical replay; registry passed.
- Verified current Paytm Money/NSE execution-cost assumptions against current public sources: Paytm Money F&O FAQ states ₹10 per unique executed order; NSE lists 0.15% option-sale STT from 2026-04-01 and 0.003% buyer stamp duty on equity options.
- Audited current Tradetron TT-04 template 999088026. Validator warnings were preserved as source warnings rather than silently repaired: uncapped premium matching, fixed rupee stop, and repair/re-entry warning.
- Built a source-faithful TT-04 common-cost replay engine but caught a cashflow-sign/MTM accounting defect before numerical execution. That draft is non-evidence and was corrected; no TT-04 numerical result exists yet.
- A local syntax check was attempted but external DNS was unavailable; this was logged as F50B-014. GitHub Actions compile is the authoritative executable check.

## 2026-10-07 — Continue the research checkpoint
2026-10-07 — continuation checkpoint
- Canonical GitHub Actions run 37572837253 remains the active Phase-50B numerical replay.
- Registry/preflight job passed; TT-02 numerical replay is still in progress.
- No TT-02 P&L, VIX uplift, validation result or promotion claim is accepted while the numerical job is incomplete.
- TT-03 is dependency-gated behind TT-02; its source-faithful engine and audit are already prepared.
- TT-04 source-faithful engine is prepared and its pre-execution MTM/cashflow defect has been corrected; no TT-04 numerical evidence exists yet.
- The research sequence remains frozen as TT-02 → TT-03 → TT-04 → registered controls → statistical correction → final holdout/manuscript.
- Repo orchestration was audited before proceeding; README/status/chat/research-log paths do not trigger numerical execution.
- TT-04 will remain blocked until TT-02 and TT-03 have completed successfully and passed their artifact audits.


## 2026-10-07 — Workflow-gate hardening after continuation audit
- Canonical run **37572837253** remains in progress; TT-02 numerical execution has not produced an auditable result yet.
- Added a dedicated **TT-04 premium-match workflow** with manual dispatch and a push trigger file.
- Hardened the future canonical chain so an audited TT-03 success emits the TT-04 trigger; TT-04 preflight independently requires the persisted TT-03 summary/trade/error artifacts with zero data errors.
- No TT-04 trigger file was created now, so the active TT-02/TT-03 sequence cannot be bypassed.
- TT-04 workflow is compile/audit gated and uses the corrected source-faithful engine; no numerical TT-04 evidence exists yet.
- F50B-015 (live Actions log endpoint 404) was recorded as an operational/no-evidence-impact error.

## 2026-10-07 — Automation audit correction
- Discovered and corrected a workflow-only TT-04 trigger placement defect before it could affect any numerical evidence.
- The active run 37572837253 remains on its original execution head and is unaffected.
- The corrected branch workflow now places TT-04 triggering strictly after audited TT-03 publication; the dedicated TT-04 workflow remains manually dispatchable.
## 2026-10-07 — TT-02 fallback performance audit
- The active canonical run **37572837253** remains in progress and remains the only numerical evidence candidate.
- Static profiling identified a second avoidable hot loop in the replay: repeated full NIFTY-index equality scans for every minute.
- Prepared `research/phase50b_tt02_calendar_replay_v3.py` as a **performance-only fallback** that pre-indexes spot by timestamp and trading-day timestamps.
- The Black–Scholes/European-delta definition, quote selection, state machine, entry/exit rules, slippage, brokerage, statutory charges and +50% stress are unchanged.
- The v3 fallback has **not** been executed and is not evidence; it exists only to avoid repeating an unnecessarily slow run if the current execution fails or times out.


## 2026-10-07 — Resume checkpoint / live-state audit
- User resumed Phase 50B research.
- Live Actions run **37572837253** was rechecked; registry remains successful and **TT-02 replay is still in progress**.
- No TT-02 artifact audit has started and no numerical result is accepted yet.
- The live run remains the sole canonical numerical evidence candidate; no duplicate replay was launched.
- Branch head currently advances independently of the running job, while the running job remains pinned to its original execution commit.


## 2026-10-07 — TT-04 pre-execution audit correction
- During the registered static audit while TT-02 remains active, a real TT-04 implementation defect was found and corrected before execution.
- On current-week expiry day, source semantics require new entries to use next-week options, but an existing prior-day position remains in the current-week series until its 15:15 exit.
- The engine now keeps the existing position's expiry immutable and uses a separate new-entry quote frame.
- Logged as F50B-020. No numerical TT-04 evidence was produced from the defective implementation.


## 2026-10-07 — TT-02 replay audit failure and correction
- Canonical run 37572837253 finished its numerical replay but failed the artifact audit because five expiry blocks lacked an exact 15:15 option quote.
- The replay had produced 237 candidate rows, with diagnostic net -₹85,250.87 and +50% cost-stress net -₹111,763.06; these values are explicitly **not evidence** because the data-error audit failed.
- Static audit identified the implementation mistake: source semantics say exit **at/after** 15:15, while the engine required exact 15:15.
- Corrected both TT-02 engines to choose the earliest common observed quote timestamp at or after 15:15 across all open legs, without forward-filling.
- The v2 source-faithful engine is now the canonical rerun; the v3 engine remains an unexecuted performance fallback.
- Automatic workflow rerun 37589199743 is active from the corrected v2 commit 6a11b859c646dccdacc03a68a22fe7a2be3a842f. No result will be accepted until its artifact audit passes.


## 2026-10-07 — Workflow gate F50B-022
- Corrected v2 commit triggered run 37589199743, but the run stopped in the registry publish step because a closing `fi` was missing.
- Registry validation passed and uploaded; TT-02 was not executed, so the run has no numerical impact.
- Corrected workflow commit e0d4bda09bb943272bac591d68aafa051d7b9f94 restores the missing `fi`, normalizes the TT-03 bot identity, and passes a structural `if`/`fi` balance check.


## 2026-10-07 — Operational polling note
- Local sleep polling timed out again; logged as F50B-023 with no research impact.
- Continued using direct GitHub Actions state checks; canonical run 37589400281 remains active in TT-02 replay.


## 2026-10-07 — Live-log monitoring note
- Direct run/job state confirms canonical TT-02 replay 37589400281 remains active.
- Live log endpoint returned 404/BlobNotFound while the job is running; logged as F50B-024 with no evidence impact.
- No P&L or scientific inference is being drawn before audited artifacts exist.


## 2026-10-07 — TT-02 coverage-gap handling correction
- Corrected TT-02 replay completed but found five opened positions without a complete common observed exit quote at/after 15:15.
- This is a data-coverage limitation in the historical option source, not evidence of a strategy or code defect.
- Formalized the 95% complete-exit coverage feasibility gate: gaps are separately logged, excluded from primary P&L and never imputed.
- The observed run had 247 complete exits and 5 gaps from 252 opened positions (~98.0%), so TT-02 remains eligible for an audited feasibility rerun.
- Workflow numerical launches are now controlled only by the explicit Phase-50B trigger file.


## 2026-10-07 — Corrected TT-02 rerun launched
- Explicit Phase-50B trigger launched run 37593965525 after the coverage-feasibility and audit-gate corrections.
- Numerical evidence remains blocked until TT-02 completes and the revised coverage audit passes.


## 2026-10-07 — TT-03 pre-execution audit correction
- Found that the initial TT-03 engine collapsed the 10:00–10:05 source window to one timestamp.
- Corrected it to scan the complete frozen window and take the earliest feasible complete ratio set.
- No TT-03 numerical run had started, so no evidence was affected.


## 2026-10-07 — Stale TT-03 evidence guard
- Added engine revision stamping and downstream validation for TT-03.
- Future runs refresh the TT-03 source from the branch before execution.
- Old-run TT-03 artifacts without revision `50B-TT03-WINDOW-V2` cannot pass the TT04 dependency gate.


## 2026-10-07 — TT-04 coverage audit correction
- Found a silent path where `finish()` could discard a trade if an exit leg quote was missing.
- Corrected it to log a coverage exclusion and added a 95% coverage audit gate to the TT-04 workflow.
- No numerical TT-04 evidence existed yet.


## 2026-10-07 — TT-02 terminal accounting safeguard
- Added explicit accounting for terminal open positions as coverage exclusions.
- Current active run predates this correction; latest-code rerun will be required before accepting final TT-02 evidence.


## 2026-10-07 — TT-02 engine revision gate
- Added `50B-TT02-COVERAGE-V3` revision stamping and workflow verification.
- Current active run predates the stamp, so latest-code rerun remains required for final evidence.


## 2026-10-07 — Paytm brokerage robustness scenario
- Verified current public Paytm Money materials and found ₹10 vs ₹20/order inconsistency.
- Retained ₹10 as the preregistered primary model and added a ₹20/order robustness scenario to avoid overstating economic viability.


## 2026-10-07 — TT-03 coverage/accounting correction
- Found silent loss of TT-03 trades when mandatory exit quotes were missing.
- Added explicit coverage exclusions and a 95% feasibility gate.
- Added current Paytm brokerage robustness outputs to the corrected replay.


## 2026-10-07 — TT-04 revision gate
- Added TT-04 engine revision `50B-TT04-COVERAGE-V2` and workflow validation against it.


## 2026-10-07 — Workflow serialization
- Added a canonical concurrency group to prevent overlapping Phase-50B numerical runs.
- Current run remains unaffected.


## 2026-10-07 — TT-05 execution chain prepared
- Implemented and workflow-gated TT-05 Simple Intraday Short Straddle.
- It will run only after TT-04 passes its evidence gate.


## 2026-10-07 — TT-02 fallback equivalence audit
- Confirmed v3 is a performance-only traversal optimization and not a scientific variant.
- It remains dormant while v2 is active.


## 2026-10-07 — Run-overlap control
- GitHub admitted a corrected TT-02 run while the stale canonical run remained active despite concurrency configuration.
- Corrected run 19 is authoritative; stale run 18 is diagnostic-only.


## 2026-10-07 — Dependency-chain hardening
- Found and corrected a missing TT-03 coverage/cost gate in TT-04 preflight.
- TT-05 workflow was also hardened against overlapping executions.


## 2026-10-07 — TT-06/TT-07 replay contracts
- Froze source-faithful deterministic replay specifications before implementation.
- No numerical results have been generated from these controls yet.


## 2026-10-07 — TT-02 revision-contract correction
- Found a compile-time-invisible undefined revision constant in TT-02.
- Fixed it and added an AST-based workflow guard; the active pre-fix run is non-authoritative.


## 2026-10-07 — TT-06 control prepared
- Added TT-06 replay engine/workflow and chained execution behind TT-05 evidence.
- Verified workflow shell balance for main, TT05 and TT06 workflows.


## 2026-10-07 — TT-07 source reconciliation
- Raw export resolves the six-state transition graph but leaves ic_entered lifecycle ambiguous.
- TT-07 numerical execution is blocked until the ambiguity is resolved from authoritative behavior.


## 2026-10-07 — Authoritative TT-02 handoff
- Run 20 is the intended authoritative corrected TT-02 replay; run 19 remains excluded from evidence.


## 2026-10-07 — TT-02 authoritative execution
- Run 20 is now the sole active and eligible numerical replay.
- Stale run 19 was cancelled and excluded from evidence.


## 2026-10-07 — TT-02 active-run checkpoint
- Run 37598918723 remains active; no result artifact is available yet.
- GitHub live-log endpoint returned BlobNotFound; no research conclusion drawn from that failure.


## 2026-10-07 — Continue checkpoint
- User requested continuation.
- Rechecked authoritative TT-02 run 37598918723: still in progress; registry passed and TT-02 numerical replay remains the active step.
- Re-read the Phase-50B workflow and confirmed trigger isolation plus `cancel-in-progress: true`; no duplicate run was launched.
- Re-read TT-07 source audit: exact six-state graph is resolved, but `ic_entered` reset/scope remains unresolved, so no speculative replay is permitted.


## 2026-10-07 — Continue checkpoint: downstream controls hardened
- TT-02 authoritative replay remains in progress; no result artifact is accepted yet.
- Added pre-execution hardening to TT04/TT05 dependency gates and corrected TT06 timestamp-based exit selection.
- These changes do not trigger the canonical Phase-50B run because the workflow is restricted to the explicit TT02 trigger path.
- TT03 remains ready behind the TT02 audit; TT07 remains blocked on the documented runtime-variable ambiguity.


## 2026-10-07 — Continue checkpoint: TT-02 result accepted, TT-03 repaired
- TT-02 is now an accepted Phase-50B baseline, but its negative common-cost net means it is not promoted.
- TT-03's first numerical attempt failed only in DEV/VAL/HOLD accounting because of timezone mismatch; no TT-03 evidence was accepted.
- Corrected the timezone handling and created a dedicated gated TT-03 workflow to avoid repeating the full TT-02 replay.
- The next numerical transition is TT-03 corrected replay; downstream TT-04 remains dependency-gated.


## 2026-10-07 — Continue checkpoint: TT-03 and TT-07
- Rechecked the corrected TT-03 trigger: GitHub reports the trigger commit status as pending; no TT03 result artifact or TT04 trigger is visible, so no duplicate replay was started.
- Checked the previously blocked TT-07 runtime-variable semantics against official Tradetron documentation.
- Resolved `ic_entered` as counter-scoped runtime state lasting until Universal Exit; updated the source audit and replay spec.
- Added TT-07 source-faithful replay engine and dependency-gated workflow.
- Self-audit caught and fixed transition-delta selection using the actual held short strike before numerical execution.


## 2026-10-07 — Continue checkpoint: TT-07 integrity hardening
- Before numerical execution, self-audited TT-07 state transitions.
- Found and fixed a latent partial-cash-mutation path when a later leg quote was absent.
- No TT-07 replay has run; the workflow remains dependency-gated behind audited TT-06 evidence.


## 2026-10-07 — Continue checkpoint: TT-03 controlled retry
- The corrected TT03 trigger remained at commit-status `pending`, with no published result.
- Refreshed the existing TT03 trigger rather than changing the research specification or launching a parallel numerical path.
- The refreshed commit is also currently `pending`; TT03 evidence remains absent.


## 2026-10-07 — Continue checkpoint: documentation write conflict
- A multi-file documentation synchronization hit a stale SHA conflict after an earlier write advanced the branch.
- No scientific artifact changed because of the failed write.
- The repository-write procedure was corrected to use fresh SHAs sequentially.


## 2026-10-07 — Continue checkpoint: statistical-gate self-audit
- Audited the execution-only statistical gate before its first run.
- Found that VIX bootstrap/permutation inference was pooling protected 2026 HOLD observations.
- Corrected the inference sample to DEV+VAL only; HOLD is now excluded from hypothesis testing and retained for separate confirmation.
- No statistical result from the defective implementation was accepted.


## 2026-10-07 — Continue checkpoint: VIX inference self-audit
- Audited the statistical gate against the full preregistered VIX mode family.
- Found that trade tables store only LOW/NORMAL/HIGH, which is insufficient to test SPIKE/RISING/FALLING/HIGH_RISING.
- Corrected the gate to reconstruct the full mode set from entry-date VIX and to exclude VIX-unobservable observations from both regime and complement.

## 2026-10-07 — Resume checkpoint: TT-03 dependency fix
- Inspected the latest TT03 Actions run and found a preflight-only dependency failure: pandas was not installed.
- Corrected the workflow and refreshed the TT03 trigger.
- No numerical result was accepted and no downstream phase was bypassed.

## 2026-10-07 — Resume checkpoint: TT-03 engine hardening
- Self-audit caught two TT03 source-semantic issues before accepting evidence.
- Corrected the hard close to never advance beyond 15:29.
- Removed the unnecessary modal strike-step gate.
- The active old-code run will be superseded by a controlled retrigger rather than reused as evidence.

## 2026-10-07 — Resume checkpoint: TT-03 coverage denominator
- Self-audit found a denominator-loss path when an eligible campaign had no complete entry set.
- Corrected the engine to record explicit coverage gaps rather than silently omit the campaign.
- The running old-code attempt will be superseded before evidence acceptance.

## 2026-10-07 — Resume checkpoint: TT-03 corrected replay executing
- Current TT03 run 37611676386 is executing the corrected engine after all identified pre-execution defects were fixed.
- Preflight and static controls passed. Awaiting replay artifact audit; no downstream TT04 trigger has been created yet.


## 2026-10-07 — Resume checkpoint: TT03 feasibility gate
- Inspected run 37611676386 directly.
- Corrected TT03 numerical replay completed, but the artifact audit correctly rejected it because coverage was 187/202 = 92.57%, below the frozen 95% feasibility threshold.
- TT03 is therefore a no-promotion feasibility failure despite positive diagnostic P&L.
- Rerun is for diagnostic persistence only.
- TT04 is being decoupled as an independent candidate so the finite research universe can continue without using TT03 as evidence.


## 2026-10-07 — Resume checkpoint: TT03 terminal failure and TT04 continuation
- TT03 corrected baseline failed the frozen 95% coverage gate at 92.57%.
- Positive TT03 P&L is diagnostic only; TT03 is closed for promotion and tuning.
- Added a candidate-local stopping rule so an infeasible TT03 does not halt unrelated registered candidates.
- TT04 now requires a persisted TT03 terminal feasibility classification but can proceed after a clean TT03 FAIL_COVERAGE without treating TT03 P&L as evidence.
- TT03 diagnostic-capture run 37612856834 is currently executing.


## 2026-10-07 — Resume checkpoint: TT04 V3 self-audit
- Before TT04 execution, audited the premium-match and 15:15 exit semantics.
- Found nearest-premium substitution where the source requires exact observed LTP matching; corrected to exact matching with deterministic distance tie-break.
- Found an exit-coverage path that could reject the first 15:15+ observation instead of searching later same-day complete quotes; corrected to earliest complete observed exit timestamp.
- TT04 engine revision V3 is now the only eligible implementation; downstream TT05 gate updated accordingly.


## 2026-10-07 — Resume checkpoint: TT03 latest-head rerun queued
- The first diagnostic rerun was pinned to an earlier workflow commit, so it is being superseded by the serialized latest-head rerun.
- New TT03 run 37613416831 is pending on trigger commit 5397259b5501db1f0bd32bfe08425e5bd820e966.
- No scientific evidence is taken from the superseded run.


## 2026-10-07 — Resume checkpoint: TT03 terminal classification
- Run 37613416831 completed the diagnostic capture successfully; artifact audit intentionally rejected the candidate because coverage remained below 95%.
- The raw diagnostic tables are now persisted, so TT03 is terminal FEASIBILITY FAIL / NO PROMOTION.
- TT04 run 37614211996 continues independently on the corrected V3 engine.


## 2026-10-07 — Resume checkpoint: TT-03 V2 coverage failure audited
- V2 produced 187/202 complete campaigns (92.57%), so the evidence gate correctly rejected it.
- Self-audit found a likely artificial source of coverage loss in the hard-close search: latest timestamp could have some but not all legs.
- Corrected the engine to search backward for the latest complete all-leg quote at or before 15:29.
- Workflow and trigger were advanced to V3; no V2 result is accepted and TT04 remains blocked.


## 2026-10-07 — Resume checkpoint: TT03 fail-closed downstream routing
- Audited the full TT03 workflow after the V2/V3 coverage failure.
- Found that FAIL_COVERAGE could still create the TT04 trigger.
- Corrected downstream routing to PASS-only and retriggered TT03 under the serialized workflow.
- No TT04 execution from a failed-coverage TT03 state is permitted.


## 2026-10-07 — Resume checkpoint: TT03 V4 session handling and routing guard
- Audited all V2 coverage-gap categories using the diagnostic artifact.
- 13 exit gaps are plausible hard-close quote issues; the V3/V4 backward-complete-quote search addresses them.
- One entry gap (2022-10-24) was a non-standard Muhurat evening session, not a daytime data outage; V4 excludes it from the candidate denominator and records it separately.
- Also hardened TT04 routing to require a current-run V4 PASS feasibility artifact, preventing stale diagnostic files from triggering downstream.


## 2026-10-07 — Resume checkpoint: TT03 V4 persistence fix
- Self-audit of the V4 workflow found the new session-exclusion dataframe was referenced before loading.
- Corrected the workflow persistence step before accepting V4 evidence.
- The next TT03 run is the sole valid V4 attempt; TT04 remains blocked until current-run V4 feasibility PASS.


## 2026-10-07 — Resume checkpoint: TT04 fail-closed dependency correction
- Audited the downstream TT04 workflow after the TT03 V2/V3 feasibility issues.
- Found that the older workflow allowed FAIL_COVERAGE to proceed; corrected it to require current TT03 V4 PASS.
- Existing TT04 weak-gate execution is explicitly non-evidence; retriggered TT04 under the corrected gate.


## 2026-10-07 — Resume checkpoint: TT03 V4 evidence rejection
- V4 achieved 99.47% nominal coverage but had 14 runtime/data errors and therefore failed the evidence gate.
- Root cause: negative-P&L exit path did not retain the contemporaneous exit snapshot.
- Fixed in V5 and retriggered. No V4 P&L is accepted; TT04 remains blocked.


## 2026-10-07 — Resume checkpoint: TT03 V5 feasibility correction
- The latest completed TT03 run was V2 and failed the preregistered 95 percent coverage gate at 187/202 = 92.57 percent; no evidence was accepted.
- Audited the current V5 engine and confirmed that it changes session and coverage treatment, so the V2 result cannot be used as the final TT03 disposition.
- Updated the dedicated workflow revision checks to V5 before the next numerical replay.


## 2026-10-07 — Resume checkpoint: TT03 workflow cleanup
- Audited the accumulated TT03 workflow after the V2, V4 and V5 corrections.
- Replaced duplicated persistence and routing blocks with one terminal feasibility classifier and one independent downstream route.
- TT03 failure states remain non-evidence; TT04 can continue without consuming TT03 P&L.
- Final V5 trigger is held until the cleaned workflow is committed.


## 2026-10-07 — Resume checkpoint: TT04 coverage self-audit
- Audited the TT04 V3 replay before numerical execution.
- Found a silent candidate-denominator path on normal sessions with no complete 10:00–10:05 ATM CE/PE entry.
- Corrected it to explicit coverage gaps, with non-regular sessions handled separately.
- No TT04 numerical evidence has been accepted.


## 2026-10-07 — Resume after network interruption
- Reconnected to the repository and verified the current branch head and Actions state.
- TT03 V5 run 37620274641 is still executing its numerical replay; no result has been accepted and no duplicate was started.
- Used the interruption interval for downstream pre-execution audit rather than idle waiting.
- Hardened TT04, TT05, TT06 and TT07 workflow checks so persisted exclusion diagnostics must reconcile to their summary counts.


## 2026-10-07 — Resume checkpoint: TT03 V5 PASS
- TT03 V5 completed and passed feasibility at 200/201 coverage candidates (99.50%) with zero data errors.
- Primary/common-cost result is positive, but this is baseline evidence only; no promotion or VIX-selection inference is made yet.
- The downstream TT04 marker written by the Actions job did not create a new TT04 run because it was pushed using GITHUB_TOKEN.
- Dispatched TT04 using a normal repository commit so the dedicated TT04 workflow can start.

## 2026-10-07 — Resume checkpoint: TT04 V3
- After TT03 V5 PASS, dispatched TT04 with a normal repository commit because the Actions GITHUB_TOKEN push does not trigger ordinary push workflows.
- TT04 run 37621965843 is now executing V3; no evidence has been accepted yet.
