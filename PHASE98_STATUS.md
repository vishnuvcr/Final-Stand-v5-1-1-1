# Phase 98 Status — NIFTY Opening-Range Debit Spread

**Status:** PREREGISTERED / IMPLEMENTATION AND SOURCE-COVERAGE RUN PENDING  
**Date:** 2026-10-10  
**Branch:** phase-98-nifty-opening-range-debit-spread

## Decision
No numerical results accepted yet. No strategy promoted.

## Checklist
- [x] Read repository README, global research/error logs, Phase 96 and 97 plans/status/chat/error/results, Phase 90–94 cross-phase findings, Phase 83 holdout boundary, and the cached dataset/execution engines.
- [x] Register one new trade-level hypothesis and freeze split/cost/exit rules.
- [ ] Add tests for opening-range signals, next-minute entries, debit spread exits and fees.
- [ ] Run against the pinned Hugging Face source through GitHub Actions.
- [ ] Verify contract coverage, exact entry/exit bars, fee math, ledgers, exclusions, and report invariants.
- [ ] Update README, root research/error logs and phase logs with every result or failure.
- [ ] Close within this preregistered bounded test; do not tune failed parameters.

## Protected boundary
Phase 83's 2026 holdout is not read. An unavailable source, inadequate exact-contract coverage, or insufficient validation trade counts will result in a documented BLOCKED, FAIL_COVERAGE, or INSUFFICIENT_EVIDENCE conclusion, not invented P&L.

## Links
- Plan: PHASE98_RESEARCH_PLAN.md
- Preregistration: PHASE98_PRE_REGISTRATION.md
- Workflow: .github/workflows/phase98-opening-range-spread.yml
- Runner: research/phase98_opening_range_spread.py
- Error log: PHASE98_ERROR_LOG.md
- Research log: PHASE98_RESEARCH_LOG.md
- Visible chat log: PHASE98_CHAT_LOG.md
