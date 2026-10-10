# Phase 102 Error and Limitation Log

## 2026-10-11 — Initialization

### E102-001 — Cross-study raw P&L is not directly rankable
**Type:** design limitation, not a runtime error.  
**Finding:** the repository compares dissimilar periods, data windows, account sizing, instruments, cost models and drawdown definitions.  
**Resolution:** rank by evidence quality / next-action priority; retain native values and units; do not compute one blended score or treat higher rupee P&L as an automatic winner.

### E102-002 — TT-03 hold split too small for confirmatory evidence
**Type:** evidence limitation.  
**Finding:** the Phase 50B summary has 200 trades overall but only 3 in HOLD.  
**Resolution:** keep TT-03 at highest *revalidation priority only*, not promoted; independent validation with sufficient expiry clusters is required.

### E102-003 — TT-04 / TT-05 temporal conflict
**Type:** evidence limitation.  
**Finding:** Phase 51-3 partial-window results are positive while Phase 78 historical HOLD totals are negative; Phase 79 also fails temporal-stability and data-completeness gates.  
**Resolution:** preserve both results and no-go decision; do not retune or erase the earlier negative sample.

No Phase 102 runtime test errors have been observed yet. This file must be appended to if any validator or workflow error occurs; resolved entries must remain in the record.
