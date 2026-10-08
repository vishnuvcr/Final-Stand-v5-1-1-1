# Phase 50B-4 Status

**CLOSED — PASS / FROZEN CANDIDATE**

## Frozen universe
- BASE: 300/350/400 — persisted control
- OTM350: 350/400/450
- OTM400: 400/450/500

Only the strike-distance tuple changed.

## Replay result
Both OTM mutations completed with:
- 200 trades;
- 201 candidate campaigns;
- 99.50% coverage;
- zero unexplained data errors;
- one explicit coverage gap;
- one explicit session exclusion.

## Development gate
- OTM350 DEV net: ₹36,634.92; DEV +50% stress: ₹32,213.01.
- OTM400 DEV net: ₹18,891.16; DEV +50% stress: ₹14,511.75.
- Both passed the preregistered feasibility and development gates.
- OTM350 selected because its DEV +50% stress net was higher.

## Control comparison
BASE remained economically stronger:
- BASE aggregate net: ₹89,669.15;
- OTM350 aggregate net: ₹69,552.06;
- OTM400 aggregate net: ₹48,998.58.

Therefore OTM350 is **frozen for statistical comparison, not promoted over BASE**.

## Cost robustness
All three geometries remained positive at ₹20/order plus +50% friction stress:
- BASE: ₹60,834.11
- OTM350: ₹40,854.34
- OTM400: ₹20,396.62

## Evidence and publication
Actions run 37850091712 completed both numerical replays and audits successfully. The workflow artifact uploads succeeded for both mutations. Branch publication initially failed because the publish step reset the generated output before copying it; this was logged as F50B4-003 and the workflow was corrected for future runs.

## Next phase
Phase 50B-6: dependence-aware statistical inference of frozen OTM350 versus fixed BASE. HOLD remains protected from selection.
