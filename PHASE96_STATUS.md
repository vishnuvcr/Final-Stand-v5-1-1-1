# Phase 96 Status — Moving-Average and Seasonality Replication

**Updated:** 2026-10-10  
**Branch:** `phase-96-moving-average-seasonality-replication`  
**Status:** INITIAL REPLAY PASSED; drawdown-window correction committed; corrected rerun pending  
**Strategy promotion:** NONE

## Completed
- Implemented deterministic SMA/EMA replay, fixed 2020–2025 test window, cache restore/acquisition fallback, tests and manual/push workflow.
- Initial CI caught an escaped-newline syntax defect and an absent-results-directory logging defect; both are corrected in the latest source.
- Created a dedicated phase branch from Phase 95.
- Registered scope and stopping rule before implementation.
- Preserved distinction between signal-level index tests and executable option P&L.

## Pending
- Re-run after the drawdown calculation correction and accept only outputs from the corrected commit.
- Add inference/uncertainty and paper-specific seasonality/timing rule audit before declaring Phase 96 complete.
- Verify Phase 95 reconciliation separately; its workflow remains active at last check.

## Quality guardrails
No 2026 holdout access; no same-close execution for close-derived signals; no invented option quotes, strikes, stop rules or fill assumptions; all unresolved source settings remain partial/data-blocked. A negative or empty outcome is recorded rather than tuned away.

## Records
- [Plan](PHASE96_RESEARCH_PLAN.md)
- [Research log](PHASE96_RESEARCH_LOG.md)
- [Error/limitation log](PHASE96_ERROR_LOG.md)
- [Decision/chat summary](PHASE96_CHAT_LOG.md)
- [Workflow](.github/workflows/phase96-moving-average-seasonality-replication.yml)
- Results will be published under `results/phase96/`.
