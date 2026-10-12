# Phase 109 Family Compliance — Research Log

## 2026-10-12 — Scope restoration
- User reiterated the requirement for more than 1,000 strategy families and accepted proceeding with scope recovery.
- Inspected the main Phase 109 plan, registry compiler summary, family feasibility summary, broad v1 evaluator, and narrow remediation-v4 evaluator.
- Confirmed broad manifest: 1,025 architecture combinations, 3,719,520 configuration tuples, 89,268,480 cost rows. These are registration counts, not completed backtests.
- Confirmed the broad evaluator supports a larger set of core IDs but contains semantic defects documented by the remediation branch; the remediation branch corrects semantics but currently allows only eight core IDs.
- Confirmed the older feasibility report is stale for official index/VIX density (218 observations per series), while the remediation branch's latest official source audit has 748 dates per series and 748/748 option-session alignment. Feasibility must be recalculated against refreshed source outputs.
- Opened this branch to keep scope audit and full-family recovery separate from the active narrow V4 evaluator.
- No strategy results were added and no strategy promoted.
