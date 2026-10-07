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
