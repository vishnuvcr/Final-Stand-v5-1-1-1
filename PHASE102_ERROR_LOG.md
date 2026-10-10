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


### E102-004 — Initial source-text assertions were too brittle
**Affected runs:** [38082218752](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38082218752), [38082247835](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38082247835), [38082297783](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38082297783).  
**Symptom:** 12/14 or 13/14 source-artifact checks passed; specific narrative checks failed although the underlying reports documented the intended result.  
**Cause:** one decimal-prefix assertion expected `-40244.6808` while the source number is `-40244.680782...`; a factor-report assertion expected text (“not a direction classifier”) not present verbatim in the source report.  
**Correction:** use a stable numeric prefix and assert source-supported phrases (factor study was not pooled and contains explicit strategy-P&L limits). No numerical source artifacts, strategy rules or evidence interpretations were changed.  
**Verification:** [run 38082303704](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38082303704) passed all 14 checks and 2 unit tests; validation artifact uploaded. Earlier failed runs are retained as non-final audit history.