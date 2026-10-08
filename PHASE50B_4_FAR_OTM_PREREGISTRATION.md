# Phase 50B-4 — Far-OTM Geometry Preregistration

## Status
FROZEN before Phase-50B-4 numerical execution.

## Scope
Only TT-03 is eligible because its source semantics contain a natural symmetric strike-distance variable.

Registered geometry family:
1. **BASE:** +300/+350/+400 CE ratio and -300/-350/-400 PE ratio.
2. **OTM350:** +350/+400/+450 CE ratio and -350/-400/-450 PE ratio.
3. **OTM400:** +400/+450/+500 CE ratio and -400/-450/-500 PE ratio.

BASE is the source-faithful control. OTM350 and OTM400 are the only mutations.

## No tuning
No additional distance, width, DTE, entry time, stop, exit or VIX threshold may be introduced.

## Execution
The source-faithful TT-03 engine is reused. Only the strike-distance tuple changes. All other semantics remain frozen:
- complete 10:00–10:05 entry window;
- call-ratio priority with put-ratio fallback;
- expiry-day negative-MTM conditional exit;
- hard close no later than 15:29;
- explicit coverage/session exclusions;
- historical lot sizes;
- no forward fill or synthetic quote repair;
- ₹10 and ₹20 brokerage scenarios;
- statutory charges and +50% cost stress.

## Feasibility gate
Each geometry must independently achieve:
- >=95% complete mandatory-exit coverage;
- zero unexplained data errors.

A geometry below 95% is terminal FAIL_COVERAGE and cannot proceed to selection or inference.

## Development selection rule
Among OTM350 and OTM400 only, a mutation must have:
1. >=95% coverage;
2. positive DEV net;
3. positive DEV +50% cost-stress net.

If both qualify, select the higher DEV +50% stress net. If neither qualifies, no far-OTM mutation is selected.

BASE is never selected against itself; it is the fixed source-faithful control.

## Protected validation/holdout
Validation and 2026 HOLD are evaluated only after the development decision is frozen. HOLD is descriptive confirmation and never selects geometry.

## Statistical protection
If one OTM mutation is selected, Phase 50B-6 will test the frozen selected mutation versus the fixed BASE using the registered dependence-aware inference framework. No holdout-based geometry selection is permitted.
