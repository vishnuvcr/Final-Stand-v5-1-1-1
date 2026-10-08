# Phase 51-2 — Available-data partial OOS

**Status: ACTIVE — NUMERICAL REPLAY**

## Scope
This study uses only the currently complete frozen option-data endpoint: **2026-04-21 through 2026-07-21**.

It is deliberately separate from the complete Phase-51 OOS validation, whose frozen window remains **2026-04-21 through 2026-08-04**.

## Frozen candidates
- TT-03 BASE: 300/350/400 symmetric ratio geometry.
- TT-03 OTM350: 350/400/450 symmetric ratio geometry.

The implementation uses distance 300 and distance 350 respectively. No parameter is selected from this study.

## Execution model
Existing audited TT-03 V5 engine; one-tick execution stress; Paytm Money ₹10 and ₹20 brokerage scenarios; statutory charges; explicit coverage exclusions; no forward-fill or synthetic quote repair.

## Interpretation rule
Positive partial-OOS results are evidence of performance over the available complete interval only. They cannot close the complete Phase-51 gate or establish endpoint confirmation for 2026-07-28 and 2026-08-04.

The Actions artifacts must pass zero-error, >=95% coverage and complete cost-output checks before numerical interpretation.
