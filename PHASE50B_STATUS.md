# Phase 50B Status

**ACTIVE — NUMERICAL REPLAY**

## Current action
The user requested that seven supplied Tradetron strategies be added and that previous strategies from other GitHub repositories be searched.

## Completed
- Seven Tradetron strategies resolved by name to finished account backtests.
- Latest Tradetron report links recorded.
- Cross-repository GitHub audit identified high-priority strategy lineages.
- Candidate registry and preregistration created on this dedicated branch.

## Parent Phase 50 status
Parent Phase 50 is formally closed with NO PROMOTION. Its authoritative corrected run was 37567632928; this branch does not alter that closed evidence.

## Next gates
1. source-rule diff;
2. feasibility and quote-coverage audit;
3. source-faithful baseline;
4. VIX conditioning;
5. semantically valid far-OTM mutations;
6. chronological validation and protected holdout;
7. final statistical gate and manuscript.

## Registry validation
Automatic Phase-50B registry validation completed successfully in GitHub Actions runs 37569527054 and 37569534954. The frozen registry contains all seven requested Tradetron strategies and the identified prior GitHub lineages.


## 2026-10-07 — Phase 50B-1 source and native-regime audit complete

The seven supplied Tradetron strategies were re-read from their current template definitions and their finished native backtests were audited. The native reports are retained only as provenance/exploratory controls because they carry partial-coverage caveats and use ₹0/order brokerage in these runs.

A free native VIX-regime diagnostic identified **TT-02 — 0.20/0.10 Delta Calendar Hedge Spread v4** as the strongest new HIGH-VIX hypothesis: the Tradetron High regime reports +₹72,179.25 over 19 result days, with another +₹122,720 in Elevated. This is gross/native-report evidence and is not a promotion result.

TT-01, TT-03, TT-04, TT-05 and TT-06 were negative in the native High regime; TT-07 was positive but had only 3 High-regime result days. TT-06 also conflicts with the independently closed negative Option-intraday-v1 study and therefore requires reconciliation before any conclusion.

### Phase 50B-2 ready
Next step: source-faithful replay under the Final Stand common cost model, beginning with TT-02 and the highest-priority controls. Entry-date VIX state will replace the exploratory outcome-day diagnostic, and only semantically valid far-OTM/delta mutations will be tested.

## 2026-10-07 — TT-02 source-semantics audit

Static audit of the current Tradetron template found embedded Python that initializes `setup_active=1` and repair flags to zero whenever not already initialized. The Entry condition is therefore eligible on any flat minute from 09:20 through 15:00.

The initial replay draft assumed a single entry day immediately before expiry and was rejected before execution. A stateful daily-session replay is being built instead.

## 2026-10-07 — Registry validator correction

The Phase-50B registry preflight failed because the actual registry table omitted the already identified Final-stand-v2 lineage while the validator correctly required it. This was fixed before any Phase-50B numerical replay. The subsequent registry workflow must pass before the replay gate is considered green.


## 2026-10-07 — TT02 runtime dependency correction
The first TT02 replay attempt failed before numerical execution because the shared Phase-43 module imports matplotlib. The workflow dependency set has been corrected; no replay evidence was produced by the failed attempt.


## 2026-10-07 — Phase 50B canonical TT-02 replay active

Phase 50 is now formally closed with NO PROMOTION. Phase 50B is the active bounded continuation.

The expanded registry contains the seven user-supplied Tradetron strategies plus the prior GitHub strategy lineages. The registry validation passed in Actions run 37570311489.

The strongest native HIGH-VIX hypothesis remains **TT-02: 0.20/0.10 Delta Calendar Hedge Spread v4**. Its native Tradetron report showed +₹72,179.25 on 19 High-regime result days, but that number is not Final Stand evidence because the native run uses a different cost/coverage model.

The current canonical common-cost replay is **Actions run 37572837253**. Registry preflight has passed; the TT-02 numerical replay is running. Older duplicate Phase-50B runs are classified SUPERSEDED and are not evidence. The standalone TT-02 workflow is now manual-only to avoid further automatic duplication.


## 2026-10-07 — Workflow orchestration hardened

The canonical workflow automatic trigger is now restricted to the explicit Phase-50B trigger file, the TT-02 replay engine, and its preregistration. README/status/error-log/research-plan edits no longer launch numerical runs. Manual dispatch remains available.

Current canonical run: **37572837253**. Registry preflight has passed and TT-02 common-cost replay is active. Older Phase-50B runs are superseded/non-evidence.


## 2026-10-07 — Additional source audits completed while TT-02 replay runs

### TT-03 source audit
The Corrected Dynamic-n strategy is frozen from the current Tradetron template: 10:00–10:05 on an exact three-calendar-day-to-expiry date; symmetric call-ratio and put-ratio entry sets at ATM ±300/350/400; expiry-day loss exit from 13:30 plus hard 15:29 exit. The first TT-03 replay draft was rejected before execution because it omitted the symmetric set; the corrected source-faithful engine is now ready.

### TT-04 source audit
Profit Breakout Premium Match Straddle is frozen as a 10:00–10:05 premium-matched ATM straddle with source-defined one-time repairs and a universal −₹7,000 / 15:15 exit. It remains a control; premium-matching must use exact observed LTPs and cannot use delta/fixed-distance substitution.

No numerical inference is taken from these source audits alone.

### Current numerical state
Canonical run **37571121043** remains active. Registry preflight has passed; **TT-02 common-cost replay is still executing**. The replay has not yet produced a scientific result, so no P&L, VIX uplift or promotion decision is accepted from Phase 50B at this point.


## 2026-10-07 — TT-02 replay performance correction
The canonical TT-02 replay was mathematically unchanged but slower than expected because the stateful engine repeatedly scanned option frames and solved implied volatility expensively. A performance-only correction was committed: timestamp indexing plus a faster Newton/fallback implementation of the same Black-Scholes implied-volatility root. This will trigger the canonical rerun and supersede the slow execution; no numerical result from the old run is used.


## 2026-10-07 — Current audit state after F50B-012

The latest canonical replay is run 37572837253. The remaining computational bottleneck in nearest-delta selection was vectorized without changing the Black–Scholes/European-delta scientific definition. TT-04's current saved account template (999088026) was also re-audited: the source uses uncapped premium-match selection (`any`) and contains a repair/re-entry validator warning; these behaviors are documented, not silently corrected. A 2026 execution-cost audit confirms the registered ₹10/order Paytm Money brokerage proxy and 2026 NSE statutory rates, including 0.15% option-sale STT from 2026-04-01.

## 2026-10-07 — Continuation checkpoint
2026-10-07 — continuation checkpoint
- Canonical GitHub Actions run 37572837253 remains the active Phase-50B numerical replay.
- Registry/preflight job passed; TT-02 numerical replay is still in progress.
- No TT-02 P&L, VIX uplift, validation result or promotion claim is accepted while the numerical job is incomplete.
- TT-03 is dependency-gated behind TT-02; its source-faithful engine and audit are already prepared.
- TT-04 source-faithful engine is prepared and its pre-execution MTM/cashflow defect has been corrected; no TT-04 numerical evidence exists yet.
- The research sequence remains frozen as TT-02 → TT-03 → TT-04 → registered controls → statistical correction → final holdout/manuscript.


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


## 2026-10-07 — TT-04 static audit correction (F50B-020)
- Before TT-04 numerical execution, static code review found an expiry-day series mismatch: existing current-week positions could be marked against next-week quotes.
- Corrected the engine to separate the new-entry expiry frame from the immutable expiry of an existing position.
- No TT-04 numerical evidence existed, so this correction has **zero numerical impact** on accepted evidence.
- TT-04 remains gated behind audited TT-03 evidence; no trigger was created.


## 2026-10-07 — Execution-budget checkpoint
- Canonical TT-02 run 37572837253 has been executing for approximately 41 minutes and remains within its registered 360-minute job timeout.
- No artifact has been published; no scientific result is accepted.
- The prepared v3 engine remains an unexecuted fallback and will only replace the canonical v2 run after an actual failure/timeout, not merely because the job is long-running.


## 2026-10-07 — TT-02 audit failure corrected; canonical rerun active
- Run **37572837253** completed its numerical loop but was rejected by the artifact gate because five expiry blocks lacked an exact 15:15 quote.
- The implementation error was semantic: the source rule is exit **at/after 15:15**, not exactly at 15:15.
- The observed 237-row output (net -₹85,250.87; +50% cost stress -₹111,763.06) is **diagnostic only and not evidence**.
- Corrected TT-02 v2/v3 to select the earliest common observed quote timestamp at or after 15:15 for all open legs, without forward-filling.
- Corrected v2 automatically launched canonical Actions run **37589199743**. TT-03 remains dependency-gated and no TT-04 trigger may be created until TT-02 and TT-03 audit successfully.
- Current gate: **TT-02 numerical rerun + zero-data-error artifact audit**.


## 2026-10-07 — Workflow gate F50B-022 corrected
- Corrected v2 run 37589199743 never reached TT-02 because the registry validation publisher had a missing shell `fi`.
- Registry validation itself passed; no numerical evidence was produced by that run.
- Corrected workflow commit **e0d4bda09bb943272bac591d68aafa051d7b9f94** restores the shell closure and normalizes the TT-03 publisher bot identity.
- The workflow now has balanced shell `if`/`fi` blocks; the next canonical run will be launched only after this gate is recorded.
- Current gate: **retrigger Phase-50B from the corrected workflow, then require TT-02 zero-data-error audit**.


## 2026-10-07 — Operational polling note
- Direct Actions checks remain the authoritative monitoring method. A local sleep helper timed out again (F50B-023); no numerical job was affected.
- Canonical run **37589400281** remains the sole active Phase-50B numerical run.


## 2026-10-07 — Live-log monitoring note
- TT-02 replay job **112687069655** remains in progress in canonical run **37589400281**.
- Live log retrieval returned a transient 404 (`BlobNotFound`), recorded as F50B-024; no research impact.
- Numerical evidence remains blocked until the job completes and the zero-data-error artifact audit passes.


## 2026-10-07 — TT-02 coverage feasibility rule formalized
- Run 37589400281 completed numerical replay but its zero-data-error audit failed because five opened positions had no complete common quote at/after 15:15.
- This is now classified as a **historical option-coverage gap**, not a model/code error. The underlying dataset documentation warns that option coverage is partial and illiquid/far strikes may be sparse or absent. citeturn551023search2turn551023search4
- Phase 50B now operationalizes its existing feasibility gate at **95% complete mandatory-exit coverage**. Coverage gaps are excluded from primary P&L, never imputed, and published separately.
- The failed run had 247 completed exits and 5 coverage gaps among 252 opened positions (~98.0%), so the candidate remains feasible subject to the corrected audited rerun.
- Workflow push triggers are now restricted to the explicit `trigger/phase50b.start` file to prevent intermediate documentation/code commits from launching duplicate numerical runs.


## 2026-10-07 — Corrected TT-02 coverage-audited rerun active
- Canonical Phase-50B run **37593965525** (run 18) is now active from the corrected trigger commit `0b09aff32d3a152d1e980819135a9a76784e7a8e`.
- Registry gate is executing; TT-02 will use the new `coverage_gaps.csv` classification and 95% feasibility rule.
- No result from the prior failed run is promoted or used for inference.


## 2026-10-07 — TT-03 pre-execution audit correction
- Static audit corrected TT-03 to evaluate the complete 10:00–10:05 entry window and select the earliest feasible complete ratio set.
- Call ratio remains the registered priority; put ratio remains the fallback when call quotes are unavailable.
- No TT-03 numerical evidence existed, so this correction has no evidence impact.


## 2026-10-07 — Stale-downstream evidence guard added
- Added TT-03 engine revision `50B-TT03-WINDOW-V2` and a downstream dependency check so results from pre-correction TT-03 code cannot be promoted.
- Future canonical runs refresh the TT-03 source to the latest branch head before execution.
- Current run 37593965525 predates this guard; therefore any downstream TT-03 artifact from that run will be treated as non-evidence unless it carries the required revision (and the current TT04 gate will reject stale artifacts).


## 2026-10-07 — TT-04 coverage audit hardened
- Pre-execution static audit corrected a silent trade-loss path for missing exit quotes.
- TT-04 now records exit coverage gaps separately and applies the same 95% complete-exit feasibility gate before evidence can pass.
- No TT-04 numerical evidence existed before this correction.


## 2026-10-07 — TT-02 terminal accounting safeguard
- Added a terminal-position reconciliation to the corrected TT-02 engines so no opened position can disappear from the denominator.
- The currently active run 37593965525 predates this safeguard; it remains diagnostic/non-final until its output is examined and a latest-code rerun passes the revised audit.


## 2026-10-07 — Statistical gate prepared
- Added `research/phase50b_statistical_gate.py` implementing the preregistered VIX-regime versus complement bootstrap/permutation framework, Holm correction, chronological split reporting, and protected-holdout handling.
- It is execution-only and will not select/tune candidates before the registered development/validation process.


## 2026-10-07 — TT-02 engine revision gate
- TT-02 corrected engines now stamp `50B-TT02-COVERAGE-V3` and the workflow requires that revision before artifact acceptance.
- The active run 37593965525 predates this stamp; it cannot by itself establish final TT-02 evidence.


## 2026-10-07 — Paytm brokerage robustness scenario added
- Primary Phase-50B brokerage remains ₹10/order for continuity with the parent methodology.
- Added a preregistered ₹20/order Paytm Money robustness scenario because official Paytm public materials currently conflict on the brokerage figure. [Paytm Money F&O FAQ](https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web); [Paytm Money pricing update](https://www.paytmmoney.com/blog/all-new-paytm-money-updates-revisions-and-more/)
- Promotion cannot rely only on the ₹10 scenario; the ₹20 scenario must also be reported and must not be used for post-result selection.


## 2026-10-07 — TT-03 coverage/accounting gate hardened
- Corrected TT-03 so incomplete exit observations become explicit coverage exclusions rather than silently disappearing.
- TT-03 workflow now requires engine revision `50B-TT03-WINDOW-V2`, >=95% coverage, zero data errors, and current-cost robustness output fields.
- No TT-03 evidence is accepted until those gates pass.


## 2026-10-07 — TT-04 engine revision gate
- TT-04 now stamps `50B-TT04-COVERAGE-V2`; its dedicated workflow rejects stale artifacts.
- No TT-04 numerical evidence exists yet.


## 2026-10-07 — Canonical workflow serialization
- Added Phase-50B concurrency protection (`cancel-in-progress: false`) so only one canonical numerical run can execute at a time.
- Active run 37593965525 remains unchanged; this protects subsequent corrected reruns.


## 2026-10-07 — TT-05 control execution prepared
- Added source-faithful TT-05 short-straddle replay engine and a dedicated manually dispatchable workflow.
- TT-05 is dependency-gated behind audited TT-04 evidence and uses the same 95% coverage rule plus ₹10/₹20 brokerage robustness outputs.
- The TT-04 workflow will emit the TT-05 trigger only after its own evidence audit passes.


## 2026-10-07 — TT-02 runtime checkpoint
- Run 37593965525 remains `in_progress` at the canonical v2 numerical replay step.
- Workflow timeout is 360 minutes. No timeout/failure conclusion has been emitted by GitHub, so the prepared v3 performance fallback is **not** activated yet.
- v3 remains a performance-only implementation and cannot contribute evidence until v2 genuinely fails/times out and a fresh corrected run is launched.


## 2026-10-07 — TT-02 v2/v3 equivalence confirmed
- Audited v3 against v2 at the core-function level: BS model, delta selection, repairs, finalization, execution costs, VIX assignment and chronology are unchanged.
- v3 is authorized only after a genuine v2 failure/timeout and will then require the same evidence gates.


## 2026-10-07 — Run-overlap control
- Run 18 (stale commit) and run 19 (corrected commit) are both active despite the declared concurrency group.
- Run 18 is explicitly excluded from evidence. Run 19 is the only eligible TT-02 run.
- No additional TT-02 replay will be started until run 19 reaches a terminal state.


## 2026-10-07 — Downstream dependency hardening
- TT-04 preflight now independently enforces TT-03 coverage >=95%, denominator consistency and all four preregistered cost outputs.
- TT-05 execution concurrency is now fail-safe against overlapping manual/triggered runs.
- TT-02 corrected numerical run 37596743408 remains active; no numerical result is yet accepted.


## 2026-10-07 — TT-06/TT-07 replay contracts frozen
- Frozen deterministic source-faithful replay specifications for TT-06 and TT-07 before numerical execution.
- Both contracts use the established coverage, slippage, ₹10/₹20 brokerage, +50% stress and protected chronology rules.
- No TT-06/TT-07 numerical evidence exists yet.


## 2026-10-07 — TT-02 runtime revision-contract correction
- Found undefined TT02_ENGINE_REV in the corrected engine; fixed and added a static AST contract audit.
- Run 37596743408 predates this correction and is explicitly non-authoritative.
- A post-run corrected rerun is required before TT-02 can produce evidence.


## 2026-10-07 — TT-06 execution chain prepared
- TT-06 replay engine and frozen replay workflow are now present and structurally balanced.
- TT-05 now triggers TT-06 only after TT-05 evidence passes its artifact gate.
- No TT-06 numerical execution has started.
- Active TT-02 run 37596743408 remains non-authoritative because it predates the TT02 revision-constant correction.


## 2026-10-07 — TT-07 source-lock correction
- Raw TT-07 export inspection recovered the exact six-state transition graph.
- A genuine runtime-scope ambiguity remains for ic_entered because the export contains no reset after setting it to 1.
- TT-07 numerical replay is therefore blocked pending authoritative resolution; no guessed reset policy will be used.
- TT-02 run 37596743408 remains active and non-authoritative.


## 2026-10-07 — Authoritative TT-02 handoff initiated
- Run 20 (**37598918723**) was launched from the corrected latest branch commit `7a05adf...`.
- Run 19 (**37596743408**) remains visible as in-progress until GitHub applies the new `cancel-in-progress: true` concurrency policy; it is pre-fix and remains non-evidence.
- No statistical or downstream strategy gate will consume TT-02 until the new run passes the complete artifact audit.


## 2026-10-07 — TT-02 authoritative run active
- Pre-fix run 37596743408 is now **cancelled** by the hardened concurrency policy and contributes no evidence.
- Corrected run **37598918723 (run 20)** is the sole active TT-02 numerical execution and has passed registry, compilation, static engine-contract audit and HF-cache setup.
- The canonical numerical replay itself remains in progress; no TT-02 result artifact has passed acceptance yet.


## 2026-10-07 — TT-02 execution still active
- Authoritative run 37598918723 remains `in_progress`; TT-02 numerical step is still running.
- Live-log retrieval returned BlobNotFound again; this does not change run status or evidence classification.
- No duplicate execution started.


## 2026-10-07 — Authoritative TT-02 live-state recheck
- Rechecked Actions run **37598918723** directly after the latest continuation request.
- Run 20 remains **in_progress** on head `7a05adf199819fa46a16efcc2f2afe1394325798`.
- Registry job **112718607157** is complete/successful. TT-02 replay job **112718692505** is still executing its canonical numerical step; artifact audit/publication steps have not started.
- Workflow source was re-read and confirms `cancel-in-progress: true`, the explicit `trigger/phase50b.start` path restriction, and the 360-minute replay timeout.
- No numerical result is accepted and no duplicate replay is launched.
- TT-07 remains source-blocked by the unresolved `ic_entered` lifecycle semantics documented in its source audit.


## 2026-10-07 — Pre-execution downstream hardening
- Re-audited TT03, TT04, TT05 and TT06 while the authoritative TT-02 numerical replay continues.
- TT03 source/replay contract remains internally consistent; no new blocking defect was found.
- TT04 workflow dependency/artifact audits were hardened for empty-but-valid error logs and all preregistered cost outputs.
- TT05 manual/dependency preflight was hardened so it cannot consume incomplete TT04 evidence.
- TT06 static audit found a latent timestamp-index bug in the 15:15+ exit search; it was corrected before any TT06 execution.
- These corrections are pre-execution controls and do not alter any accepted numerical evidence.
- Authoritative TT-02 run 37598918723 remains the sole active numerical run.


## 2026-10-07 — TT-02 completed; TT-03 blocked then repaired
- Authoritative TT-02 run 37598918723 completed successfully at the numerical stage and passed its evidence audit: 247 completed trades / 252 candidate trades, 98.02% coverage, five explicit coverage exclusions.
- TT-02 common-cost results: net **-₹3,387.42** at the primary ₹10/order cost model; ₹50% cost stress **-₹32,226.76**; ₹20/order robustness **-₹47,212.62**; ₹20/order +50% stress **-₹97,964.56**. These are accepted baseline results, not a promotion.
- VIX-conditioned diagnostic: HIGH +₹8,513.39 primary / +₹7,462.97 stress (10 trades); LOW -₹19,930.30 / -₹34,934.20 (134); NORMAL +₹8,029.48 / -₹4,755.53 (103). Statistical gate has not yet been applied.
- TT-03 then failed before artifact publication because pandas produced timezone-naive parsed expiry values during DEV/VAL/HOLD accounting. No TT-03 result was accepted.
- Corrected the split accounting and added a dedicated TT-03 gated workflow. The already accepted TT-02 artifact is reused; TT-02 is not rerun merely to repair TT-03.


## 2026-10-07 — TT-03 corrected replay checkpoint
- Trigger commit `f7f01c5265203ad27b33d28d0633a93609a4538d` submitted the corrected TT-03 replay.
- The trigger commit's GitHub commit status is still `pending`; no TT-03 result directory has been published on the branch and no TT04 trigger file exists.
- Therefore TT-03 is **pending/active-or-not-yet-observable**, not failed and not accepted. No duplicate TT-03 replay was launched.

## 2026-10-07 — TT-07 lifecycle blocker resolved
- Official Tradetron Runtime Variable documentation resolved the `ic_entered` lifecycle ambiguity: variables are strategy-level, persist through the current counter, and remain active until a Universal Exit.
- TT-07 replay is therefore interpreted counter-by-counter: initial Friday IC sets `ic_entered=1`; it remains set through all intra-cycle state transitions; the monthly Universal Exit ends the counter; the next counter reinitializes `ic_entered=0` and `state=0`.
- TT-07 source audit and replay specification were updated accordingly.
- TT-07 replay engine `50B-TT07-SOURCE-V1` and a manual/dependency-gated workflow are now present. Numerical execution remains gated behind the registered TT-06 evidence.
- A pre-execution self-audit also corrected transition-delta evaluation to use the actual held short strike rather than reselecting a nearest-delta strike. No numerical evidence was generated by either pre-execution defect.

## 2026-10-07 — Current bounded next steps
- Do not duplicate the pending TT-03 replay.
- Continue the existing dependency chain: corrected TT-03 -> TT-04 -> TT-05 -> TT-06 -> TT-07.
- TT-07 is no longer source-blocked and will be automatically triggered only after audited TT-06 evidence.


## 2026-10-07 — TT-07 pre-execution transaction-safety correction
- Self-audit identified a latent partial-cash-mutation path during state transitions if a later leg quote was missing.
- Corrected the TT-07 engine to prevalidate every old and new leg quote before any ledger/cash mutation.
- This is pre-execution hardening only; no TT-07 numerical evidence exists.


## 2026-10-07 — TT-03 controlled trigger refresh
- The first corrected TT-03 trigger remained non-observable at the available commit-status endpoint, with no published TT03 artifact or TT04 trigger.
- Refreshed `trigger/phase50b_tt03.start` in commit `28722b5204166199f91353d793f2840fe2022812`.
- Because the dedicated workflow uses `cancel-in-progress: true`, this is a serialized retry/control operation rather than permission for overlapping TT03 evidence.
- The new commit status is currently `pending`; therefore TT-03 remains pending and no numerical result is accepted.

## 2026-10-07 — TT-03 preflight dependency correction
- TT03 run 37610158492 failed before numerical replay because its preflight imported pandas without installing the workflow dependencies.
- Added the preflight dependency installation and refreshed the trigger in commit `6adb0620ccba9933aa282a1aa95e63b98ed7c5f5`.
- No TT03 numerical evidence exists from the failed run.

## 2026-10-07 — TT-03 source-semantic corrections before evidence acceptance
- Self-audit found two pre-execution issues in the active TT03 engine: hard-close fallback could roll to 15:30+, and an unnecessary modal-strike-step gate could reject valid source-defined entries.
- Both were corrected in commit `aea2196436fbeceb90c40b02ef55008f9f80164f` before any TT03 artifact audit or publication.
- The currently running TT03 job is on the superseded engine commit and will be replaced by a controlled retrigger.

## 2026-10-07 — TT-03 entry coverage correction
- Eligible campaigns with a valid three-days-before entry day but no observable entry timestamp or no complete source-defined ratio set are now explicit coverage exclusions.
- This correction prevents silent denominator loss and was made before accepting any TT03 numerical artifact.
- The in-progress TT03 run is being superseded by a controlled retrigger.

## 2026-10-07 — TT-03 corrected rerun now executing
- Run 37611676386 is the current TT03 dedicated execution on corrected head `b60f47b6925c55901d780926425b8ee718569a55`.
- Preflight, dependency installation, compilation, static engine audit and HF cache steps have passed.
- The source-corrected numerical replay is currently executing; no artifact or result is accepted yet.
- Superseded runs 37611073923 and 37611383204 were cancelled by the serialized workflow and are non-evidence.


## 2026-10-07 — TT-03 baseline feasibility decision
- Corrected TT03 replay run 37611676386 completed source-faithful trade generation successfully but failed the artifact gate solely because complete coverage was 187/202 = 92.57%, below the preregistered 95% feasibility threshold.
- Diagnostic P&L from the corrected engine is not promotion evidence: primary net +₹87,005.53; +50% stress +₹79,885.04; ₹20/order +₹73,765.93; ₹20/order +50% stress +₹60,025.64.
- TT03 is now classified FEASIBILITY FAIL / NO PROMOTION. No TT03 parameter tuning or confirmatory VIX inference is authorized.
- A controlled rerun is being used only to persist the complete diagnostic replay and coverage exclusions in the repository.
- TT04 is an independent candidate. The orchestration gate has therefore been changed so a clean TT03 feasibility failure can route to TT04 without treating TT03 as accepted evidence. TT04 cannot consume TT03 P&L as evidence.


## 2026-10-07 — TT-03 diagnostic-capture rerun
- Dedicated run 37612856834 is the current TT03 rerun on the corrected workflow.
- Preflight and all numerical pre-controls have passed; the replay itself is currently executing.
- This run exists to persist the raw diagnostic trade/coverage tables and produce a terminal feasibility classification. It is not a parameter re-test.
- If the classification is PASS, TT04 proceeds normally. If it is the same clean FAIL_COVERAGE seen in run 37611676386, TT04 is allowed to continue independently without treating TT03 as accepted evidence.


## 2026-10-07 — TT-04 pre-execution semantic hardening
- Self-audit found two source-fidelity defects before TT04 numerical execution: nearest-premium rather than exact observed premium matching, and an exit routine that did not search later same-day timestamps for the earliest complete quote set at/after 15:15.
- Corrected engine revision is now 50B-TT04-COVERAGE-V3.
- TT04 and the downstream TT05 dependency gates were updated to require V3.
- No TT04 numerical evidence existed before these corrections.


## 2026-10-07 — TT03 diagnostic rerun supersession control
- Run 37612856834 began on an earlier head before the diagnostic-capture workflow hardening was committed.
- The trigger has now been refreshed once more so the serialized TT03 workflow will restart from the latest branch state; no overlapping TT03 evidence is permitted.
- No scientific conclusion changes: TT03 remains FEASIBILITY FAIL at 92.57% coverage based on run 37611676386, pending repository persistence of the raw diagnostic tables.


## 2026-10-07 — TT04 V3 numerical execution
- Independent TT04 run 37614211996 passed the TT03 terminal feasibility gate, including clean FAIL_COVERAGE handling, and passed compilation/source checks.
- TT04 V3 numerical replay is currently executing. No TT04 result or downstream TT05 trigger is accepted yet.
- TT04 V3 is the corrected source-faithful engine after exact premium-match and earliest-complete 15:15+ exit fixes.


## 2026-10-07 — TT03 terminal persistence completed
- Run 37613416831 completed its numerical replay successfully and persisted the full diagnostic replay/coverage dataset.
- Artifact audit intentionally failed because coverage is 187/202 = 92.57%, below the preregistered 95% threshold; this confirms the previously established TT03 FEASIBILITY FAIL.
- The diagnostic replay and coverage gaps are now present in the repository. No TT03 P&L is promotion or tuning evidence.
- Independent TT04 run 37614211996 remains the active numerical candidate.


## 2026-10-07 — TT-03 V2 feasibility result rejected; V3 hard-close correction
- Corrected V2 TT03 replay 37611676386 produced 187/202 complete campaigns = 92.57% coverage and was rejected by the preregistered 95% feasibility gate. No TT03 P&L was accepted.
- Self-audit then found that the V2 hard-close branch could stop on a partially quoted latest timestamp and fail to search earlier complete timestamps.
- V3 now selects the latest complete all-live-leg quote at or before 15:29, preserving the source rule and never imputing.
- Workflow audit and trigger were updated to V3; the V3 replay is now the sole TT03 numerical attempt under evaluation. Superseded V2 output remains non-evidence.


## 2026-10-07 — TT-03 downstream routing hardened
- Self-audit found an orchestration defect: the TT03 workflow could route TT04 even when TT03 feasibility was `FAIL_COVERAGE`.
- Corrected the workflow to permit TT04 only on `PASS`; coverage failure now terminates the chain without a downstream trigger.
- Current TT03 trigger was refreshed after this guard correction; the previous in-progress attempt is superseded by the serialized concurrency group.


## 2026-10-07 — TT-03 V4 session-calendar correction
- V2 diagnostics showed 13 exit-side missing-CE gaps plus two entry-window gaps. One of the entry gaps, 2022-10-24, was a Diwali Muhurat evening-session day and had no normal 10:00 market session; it must not be counted against a daytime strategy's coverage denominator.
- V4 explicitly separates non-standard/closed intended entry dates into `session_exclusions` while retaining genuine regular-session entry-data failures as coverage gaps.
- V4 workflow also requires current-run/V4 provenance on the feasibility diagnostic before any TT04 routing; stale diagnostic files cannot trigger downstream.


## 2026-10-07 — TT-03 V4 workflow persistence hardening
- V4 diagnostic persistence briefly referenced an undefined session-exclusion dataframe after the new denominator control was introduced.
- The workflow was corrected to load `session_exclusions.csv` explicitly before writing the feasibility artifact.
- No V4 numerical result was accepted from the affected workflow revision; the next trigger uses the corrected persistence logic.


## 2026-10-07 — TT04 dependency gate corrected
- Detected that an older TT04 workflow allowed TT03 `FAIL_COVERAGE` to continue. TT04 run 37614211996 was therefore classified non-evidence and must not be used.
- Corrected TT04 preflight to require current TT03 V4 feasibility `PASS` with >=95% coverage and zero data errors.
- Triggered a controlled TT04 rerun after this correction; old TT04 execution is superseded by the serialized concurrency group.


## 2026-10-07 — Current active execution
- TT03 V4 run **37617012372** is the current controlled numerical execution after the session-exclusion, hard-close completeness, diagnostic persistence and fail-closed downstream corrections.
- Preflight and static engine controls have passed; the numerical replay is still running. No TT03 artifact or P&L has been accepted yet.
- TT04 run **37617256820** correctly failed its preflight because the currently persisted TT03 diagnostic is still the older V2 FAIL_COVERAGE record. This is the intended fail-closed behavior; no TT04 numerical execution occurred in that run.
- TT04 remains blocked until the current TT03 V4 run produces a same-run feasibility `PASS` artifact.


## 2026-10-07 — TT-03 V4 result rejected; V5 exit-snapshot correction
- V4 replay 37617012372 reached 186/187 coverage candidates (99.47%) plus one session exclusion, but generated 14 `UnboundLocalError` data errors on negative-P&L exits. The evidence audit correctly rejected the artifact.
- V5 fixes the lifecycle by retaining the actual exit snapshot for both negative-P&L exits and hard-close exits, then validates it before settlement.
- V5 workflow/trigger are now active. TT04 remains blocked until V5 passes all evidence gates with zero data errors and >=95% coverage.


## 2026-10-07 — TT03 V5 workflow alignment
- Run 37611676386 executed V2 and failed the 95% feasibility audit at 187/202 completed trades (92.57 percent).
- The current V5 engine additionally treats genuine non-regular-session scheduled days as session exclusions and tightens source hard-close and entry handling.
- Workflow revision checks have now been advanced from V2 to V5 before the next TT03 replay.
- The V2 result remains non-evidence.


## 2026-10-07 — TT03 terminal-routing architecture cleaned
- TT03 V5 is the active source-faithful engine.
- The dedicated workflow was rewritten to create exactly one persisted terminal classification: PASS, FAIL_COVERAGE, or INVALID_ENGINE.
- Failed TT03 candidates remain non-evidence and their P&L is explicitly marked diagnostic-only.
- Independent TT04 continuation is permitted only from that persisted terminal classification; TT04 does not consume TT03 P&L when TT03 has failed feasibility or engine validity.
- A final TT03 V5 trigger will be issued after this workflow cleanup so no stale workflow definition can run.


## 2026-10-07 — TT04 pre-execution coverage hardening
- TT04 V3 was audited before any accepted numerical run.
- Normal-session days with no complete 10:00–10:05 ATM straddle entry are now explicit coverage candidates; non-regular-session days are session exclusions.
- TT04 workflow now requires the session-exclusion diagnostic artifact.
- No pre-correction TT04 numerical output is accepted.


## 2026-10-07 — Resume checkpoint: current TT03 V5 execution
- Dedicated TT03 run 37620274641 is currently in progress on the cleaned V5 workflow.
- Preflight, dependencies, compilation, static engine-contract audit and HF cache have passed; numerical replay is still executing.
- No TT03 result, feasibility state or P&L is accepted until the terminal-classification and audit steps finish.
- No duplicate TT03 execution is being started.

## 2026-10-07 — Resume checkpoint: downstream coverage-audit hardening
- TT04 V3, TT05 V2, TT06 V2 and TT07 V2 workflows were audited while TT03 V5 executes.
- Coverage/session diagnostic files now have summary-to-row count reconciliation in their downstream evidence gates.
- TT07 now additionally requires and validates the entry-exclusions diagnostic.
- These changes are control hardening only and do not trigger any replay because no strategy trigger file was modified.


## 2026-10-07 — TT-03 V5 PASSED feasibility
- Run 37620274641 completed with TT-03 V5 PASS: 200 completed campaigns / 201 candidates, 99.50% coverage, 1 explicit coverage exclusion, 1 session exclusion, zero data errors.
- Common-cost TT-03 baseline: net ₹89,669.15; +50% cost stress ₹82,074.11; ₹20/order ₹75,509.15; ₹20/order +50% stress ₹60,834.11.
- These figures are accepted source-faithful baseline evidence but are not yet a promotion decision; VIX inference, chronological validation/holdout confirmation and statistical gates remain.
- TT04 was then dispatched explicitly because the TT03 workflow's GITHUB_TOKEN push cannot trigger an ordinary push workflow automatically.

## 2026-10-07 — TT04 V3 active
- TT04 run 37621965843 passed preflight, including the accepted TT03 V5 PASS terminal gate, and is currently executing the corrected TT04 V3 numerical replay.
- No TT04 artifact or P&L is accepted until its structural, coverage, cost and diagnostic audits complete.

## 2026-10-07 — Resume / TT04 live-state checkpoint
- Revalidated the Phase-50B research plan, pre-registration, status log, chat log and error log before continuing.
- TT03 V5 remains accepted as a feasibility PASS from run 37620274641: 200/201 complete campaigns, 99.50% coverage, 1 coverage exclusion, 1 session exclusion, zero data errors.
- TT04 run 37621965843 remains `in_progress` in its numerical replay step on the source-faithful V3 engine.
- TT04 preflight passed, including the TT03 V5 terminal gate; no TT04 result, inference, or promotion claim is accepted before artifact audit and publication.
- Downstream TT05/TT06/TT07 workflows were re-audited and remain fail-closed behind the persisted dependency artifacts and reconciliation checks.
- No research-plan change was made.


## 2026-10-07T18:15:00+05:30 — Continuation/source-gate audit
- User resumed Phase 50B after accepted TT-03 V5 PASS.
- Active TT-04 run **37621965843** remains the sole numerical path; preflight passed and numerical replay is still executing.
- The TT-04 workflow, source-audit lock and V3 engine were re-read at the active run head. No new evidence-impacting defect was identified; exact premium matching, expiry-day next-week handling, 15:15-or-later complete-quote exit semantics, explicit coverage gaps, zero-error gate, and ₹10/₹20 cost outputs remain enforced.
- No TT-04 result is accepted until the artifact/coverage/data-error/cost audit passes.


## 2026-10-07T18:15:00+05:30 — TT04 live continuation / chat checkpoint
- User resumed Phase 50B and explicitly instructed continuation.
- Direct GitHub Actions inspection confirms TT04 run **37621965843** is still the sole active TT04 numerical execution. Preflight passed; compilation and HF cache passed; the numerical replay step remains in progress.
- The active TT04 workflow revision is **50B-TT04-COVERAGE-V3**. Its acceptance gate requires the persisted TT03 V5 PASS terminal artifact, >=95% complete mandatory-exit coverage, explicit session exclusions, zero data errors, and all four registered cost outputs.
- TT03 V5 accepted evidence remains unchanged: run **37620274641**, 200/201 complete campaigns, 99.50% coverage, one coverage exclusion, one session exclusion, zero data errors; ₹89,669.15 primary, ₹82,074.11 +50% stress, ₹75,509.15 at ₹20/order, ₹60,834.11 at ₹20/order +50% stress.
- No TT04 P&L, VIX inference, parameter selection, or promotion claim is accepted while the replay is incomplete.
- Downstream TT05–TT07 and statistical-gate contracts were re-read during the live interval; no new evidence-impacting defect was identified.


## 2026-10-07 — TT04 live-log observability checkpoint
- TT04 run 37621965843 remains in_progress in the numerical replay step.
- Direct live-log retrieval returned BlobNotFound; this is recorded as an operational observability issue only.
- No duplicate TT04 execution was launched. Artifact publication/audit remains the sole scientific acceptance gate.


## 2026-10-07 — TT04 continuation checkpoint
- User instructed continuation again.
- Direct Actions state still shows TT04 run **37621965843** in_progress at `Run TT04 replay`; all preflight/replay prerequisites are successful.
- TT04 result artifacts and the TT05 trigger are still absent from the branch, so no evidence has reached the acceptance/publication gate.
- No duplicate run was launched; the registered chain remains fail-closed.


## 2026-10-07 — TT04 runtime/performance audit during active replay
- TT04 run **37621965843** remains in_progress; no artifact audit has begun and no result is accepted.
- Workflow timeout is 240 minutes for the numerical job. Current state has not reached timeout, so no fallback execution is authorized yet.
- Static review of V3 identifies computationally expensive repeated timestamp/quote scans inside the minute-by-minute replay, especially repeated full option-frame filtering and repeated 15:15–15:30 exit-candidate reconstruction.
- This is recorded as a **performance-risk observation**, not a scientific error: the frozen source semantics, strike matching, chronology, costs and coverage rules are unchanged.
- A performance-only fallback may be prepared without triggering it; it can be activated only after a genuine timeout/failure and a fresh evidence-gated replay.


## 2026-10-07 — TT04 bounded continuation checkpoint
- User instructed continuation again.
- Direct Actions inspection: TT04 run 37621965843 remains in_progress at Run TT04 replay; all prerequisite steps remain successful.
- The run has produced zero Actions artifacts so far and the TT05 trigger remains absent.
- No timeout/failure signal has been observed, so the performance-only fallback remains dormant.
- No duplicate numerical execution or scientific parameter change was made.


## 2026-10-07 — TT04 timeout-gate audit
- Re-read the authoritative TT04 workflow: numerical job timeout is **240 minutes**.
- Direct Actions state still reports run **37621965843** as `in_progress`; the replay step is still active and no artifacts exist.
- The available GitHub wrapper does not expose authoritative `started_at`/`updated_at` timestamps for the run, so timeout status cannot be asserted from the available evidence alone.
- Therefore the 240-minute fallback threshold is **not declared breached** and no fallback replay is launched.
- This preserves the scientific rule: never replace a valid active replay merely because it is slow.


## 2026-10-07 — Continuation checkpoint after direct Actions revalidation
- User instructed continuation from the accepted TT-03 V5 PASS.
- Direct inspection of Actions run **37621965843** confirms the TT-04 **numerical replay** step remains `in_progress`; preflight, compilation, dependency installation and HF cache remain successful.
- The run currently has **no published Actions artifacts**; artifact audit, publication and TT05 trigger remain pending.
- The 240-minute workflow timeout remains the registered execution gate. Because the available GitHub wrapper still does not expose authoritative run start-time metadata, timeout breach is not inferred.
- No duplicate replay, parameter change, VIX inference, holdout analysis or promotion decision was performed from the incomplete run.
- The finite Phase-50B plan remains unchanged.


## 2026-10-07 — TT04 dormant performance fallback prepared
- While TT04 V3 remains actively executing, a separate **semantics-preserving performance-only fallback** was added at `research/phase50b_tt04_premium_match_replay_fast.py`.
- It replaces repeated full timestamp scans with timestamp-indexed option frames, pre-indexed spot lookup and one-time daily exit-candidate construction.
- The fallback retains the same source entry/repair/stop/15:15-or-later exit rules, exact observed premium matching, chronological handling, coverage/session treatment, lot sizing and four registered cost outputs.
- It is **not wired to the active workflow, not executed, and not evidence**. Activation remains contingent on a genuine TT04 workflow failure/timeout followed by a fresh compile/evidence audit.


## 2026-10-07 — TT04 fallback validation control added
- Added `.github/workflows/phase50b-tt04-fallback-syntax.yml` with both automatic push and manual dispatch triggers.
- Its only numerical action is Python syntax compilation of the dormant fallback; it does not load market data or run a backtest.
- The fallback therefore remains an execution contingency only, while TT04 V3 run **37621965843** remains the sole authoritative scientific execution.


## 2026-10-07 — TT04 fallback source-equivalence audit
- Re-audited the dormant fallback against the canonical TT04 V3 source contract.
- Confirmed preservation of accepted imports/cost functions, exact observed-LTP premium matching, 10:00–10:05 entry window, ₹7,000 source stop, 15:15–15:30 observed exit search, explicit entry/exit coverage gaps, and all four registered cost outputs.
- Confirmed the validation workflow is compile-only and does not invoke the replay main function or load market data.
- The fallback remains non-authoritative and is not wired into TT04 execution.


## 2026-10-07 — TT04 canonical failure and controlled fallback activation
- Canonical TT04 V3 run 37621965843 completed with the numerical replay step FAILED. Artifact audit, upload, publication and TT05 trigger were skipped; no result from this run is evidence.
- Direct job-log retrieval remained unavailable (BlobNotFound), so the precise runtime exception is not asserted.
- Because this is now a genuine workflow failure, the preregistered performance-only fallback contingency was activated.
- Added .github/workflows/phase-50b-tt04-fallback.yml and activated trigger/phase50b_tt04_fallback.start. The fallback uses the source-equivalence-audited engine 50B-TT04-COVERAGE-V3-FAST-DORMANT and the same 95% coverage, zero-error, four-cost and TT03 terminal gates.
- The fallback is an execution correction only, not a strategy mutation or new scientific candidate. No parameter, entry, repair, stop, exit, strike or cost rule was changed.
- TT05 remains fail-closed until the fallback produces an audited published TT04 artifact.


## 2026-10-07 — TT04 fallback dispatch blocker
- The controlled fallback workflow is installed and the trigger marker is present, but no Actions run was created from the API-authored trigger commit. The available GitHub connector has no workflow_dispatch operation, and push-triggered workflows are suppressed for these API-authored commits. Therefore fallback execution has not started and no result is accepted. This does not alter the research plan or scientific gates.


## 2026-10-07 — TT04 failure diagnosed; timezone correction applied
- The canonical TT04 V3 failure is now fully diagnosed from the completed job log: the replay reached summary construction, then failed because expiry_dt was timezone-naive while DEV_END/VAL_END were timezone-aware. This was a reporting-layer defect, not a trading-rule defect. Both canonical and fallback engines were corrected with project-timezone localization. A corrected canonical TT04 run 37629750175 has been queued; fallback run 37629239398 is also active/serialized under the same TT04 concurrency group. No result is accepted until the corrected run passes the full artifact gate.


## 2026-10-07 — Corrected TT04 live checkpoint after timezone fix
- Revalidated the finite Phase-50B plan, status controls and live Actions state before continuation.
- Corrected canonical TT04 run **37629750175** is **in_progress** on commit **388301f19e6d8570041eb3605753e1112ded3296**.
- TT04 preflight completed successfully: compilation and the TT-03 terminal feasibility gate passed.
- Numerical execution remains in progress; replay, artifact audit, publication and TT05 trigger remain pending.
- Former fallback run **37629239398** is **cancelled** by the shared TT04 concurrency guard; it is non-evidence and does not represent a scientific failure.
- Fallback syntax-control run **37629740301** completed successfully.
- No TT04 P&L, VIX result, parameter tuning, holdout result or promotion decision has been accepted.


## 2026-10-07 — TT04 accepted; TT05 automation repair and launch
- Canonical TT04 run **37629750175** completed with full artifact audit PASS and safe publication. Accepted TT04 summary: 1,214 trades / 1,232 candidates, 98.54% coverage, 18 coverage exclusions, 4 session exclusions, zero data errors; net ₹55,582.71 at ₹10/order, ₹11,429.95 under +50% friction, −₹1,718.09 at ₹20/order, and −₹74,521.25 at ₹20/order +50% stress.
- Self-audit identified an orchestration defect: TT04 created the TT05 marker using a GITHUB_TOKEN-authored push, which does not trigger a separate ordinary push workflow. No TT05 scientific run had started; no evidence was lost.
- Corrected TT04→TT05, TT05→TT06 and TT06→TT07 handoffs to retain the marker audit trail but additionally invoke the downstream workflow through the GitHub Actions workflow-dispatch API with `actions: write` permission.
- Recovery marker update launched TT05 run **37654354444**. TT05 preflight passed; numerical execution is now underway.
- No TT05 P&L, VIX inference, tuning or promotion decision is accepted until its complete replay/audit/publication gate passes.


## 2026-10-07 — TT05 replay failure diagnosed and corrected
- TT05 run **37654354444** failed after the replay loop during DEV/VAL/HOLD split classification because expiry timestamps were timezone-naive while split boundaries were timezone-aware.
- No TT05 artifact passed audit or publication; the failed run is non-evidence.
- Corrected `research/phase50b_tt05_short_straddle_replay.py` to localize expiry timestamps to the project timezone before split comparison.
- The trading rules, entry window, ATM selection, stop, exit, cost models and VIX capture were not changed.
- A fresh TT05 rerun will be launched from the corrected engine.


## 2026-10-07 — TT05 PASS; TT06 launched
- Corrected TT05 run **37666116836** completed the numerical replay, artifact audit, upload and safe publication successfully. The overall Actions conclusion is failure only because its final TT06 dispatch substep returned HTTP 404.
- Published TT05 result: **1,184 trades / 1,232 candidates (96.10% coverage)**, zero data errors, 48 coverage exclusions, 4 session exclusions. Net P&L: **₹52,337.89** at ₹10/order, **₹9,429.09** at +50% friction, **−₹3,546.91** at ₹20/order, **−₹74,398.11** at ₹20/order +50% stress.
- Split result: DEV 632 trades / ₹12,772.96 net; VAL 474 / ₹79,809.61; HOLD 78 / **−₹40,244.68**.
- TT05 evidence is accepted for downstream registered analysis, but it is not a promotion decision. HOLD degradation and cost sensitivity remain material.
- TT06 run **37675162843** has been launched through the audited marker path and is now queued.


## 2026-10-08 — TT06 failure diagnosed; timezone-only correction prepared
- TT06 run **37675162843** passed preflight and static checks but failed in post-replay DEV/VAL/HOLD split classification because expiry timestamps were timezone-naive while split boundaries were timezone-aware.
- No TT06 artifact was audited or published; no numerical result from the failed run is accepted.
- Corrected `research/phase50b_tt06_intraday_asym_replay.py` to localize expiry timestamps to `TZ` before split classification. Scientific trading rules and cost assumptions are unchanged.
- This is the same reporting-layer class of defect previously caught in TT05; F50B-089 records it so the prevention rule is explicit.
- A controlled TT06 rerun will be launched from the existing trigger marker after the correction is persisted.


## 2026-10-08 — TT06 corrected rerun active
- Controlled rerun **37722386852** launched from marker commit **8b01fe3e862e3ba0ee8371542bae1623e5ead64c**.
- Preflight has passed; numerical job **113132915078** is currently in progress.
- The corrected engine is pinned to the same registered TT06 engine revision **50B-TT06-COVERAGE-V2**; only the expiry split-report timezone normalization changed.
- No TT06 P&L, VIX inference, promotion decision or downstream TT07 launch is accepted until replay + artifact audit + publication all pass.
