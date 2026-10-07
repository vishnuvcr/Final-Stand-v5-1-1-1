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
