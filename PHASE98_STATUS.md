# Phase 98 Status — NIFTY Opening-Range Debit Spread

**Status:** BLOCKED — SOURCE TIMESTAMP-FILTER DEFECT FOUND; CORRECTION PENDING  
**Date:** 2026-10-10  
**Branch:** phase-98-nifty-opening-range-debit-spread

## Latest technical result
The first completed workflow [38057561258](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38057561258) passed its software steps, but its result report proves the option data were not read successfully: 0 option expiry files loaded, 0 completed trades, and 1,126 chain-load exceptions. The exception was a PyArrow timezone/type mismatch between the Parquet timestamp schema (+05:30) and Asia/Kolkata filter bounds.

Consequently, the report's prior technical PASS is superseded as an evidence-acceptance status. Economic performance is NOT ESTIMABLE; zero printed P&L is an empty sample, not a measured zero return. No strategy conclusion can be drawn from this run.

## Corrective steps
- [x] Freeze the strategy rules, source revision, splits, costs, and statistical design before looking at performance.
- [x] Regression tests passed on run 38057561258.
- [x] Confirm the root cause from 1,126 captured source exceptions and source manifest schema.
- [ ] Construct Arrow filter scalars using the exact declared timestamp type.
- [ ] Normalize open_interest to the internal OI field when present; never impute missing OI.
- [ ] Add regression tests and fail the evidence gate if any option-file schema/time-filter error occurs.
- [ ] Re-run the source-pinned replay and audit all resulting trades, costs, exclusions and inference.

## Decision
No numerical strategy result is accepted yet. No strategy promoted. Phase 83's protected 2026 holdout remains unopened.

## Links
- Plan: PHASE98_RESEARCH_PLAN.md
- Preregistration: PHASE98_PRE_REGISTRATION.md
- Workflow: .github/workflows/phase98-opening-range-spread.yml
- Runner: research/phase98_opening_range_spread.py
- Tests: tests/test_phase98_opening_range_spread.py
- Error log: PHASE98_ERROR_LOG.md
- Research log: PHASE98_RESEARCH_LOG.md
- Visible chat log: PHASE98_CHAT_LOG.md
