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
