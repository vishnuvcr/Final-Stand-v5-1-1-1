# Phase 51-2 — Available-data partial OOS

**Status: ACTIVE — SOURCE-MANIFEST CORRECTION READY**

## Scope
This study uses only the currently complete frozen option-data endpoint: **2026-04-21 through 2026-07-21**.

It is deliberately separate from the complete Phase-51 OOS validation, whose frozen window remains **2026-04-21 through 2026-08-04**.

## Frozen candidates
- TT-03 BASE: 300/350/400 symmetric ratio geometry.
- TT-03 OTM350: 350/400/450 symmetric ratio geometry.

The implementation uses distance 300 and distance 350 respectively. No parameter is selected from this study.

## Execution model
Existing audited TT-03 V5 engine; one-tick execution stress; Paytm Money ₹10 and ₹20 brokerage scenarios; statutory charges; explicit coverage exclusions; no forward-fill or synthetic quote repair.

## Latest execution state
Runs **37845718056** and **37845741103** failed before numerical execution because the wrapper could not import the inherited replay module when invoked as a file.

The wrapper has been corrected and the artifact output root has been isolated to `results/phase51/partial_oos`.

These failed runs are non-evidence. The corrected branch push is expected to trigger the registered Actions replay automatically.

## Interpretation rule
Positive partial-OOS results are evidence of performance over the available complete interval only. They cannot close the complete Phase-51 gate or establish endpoint confirmation for 2026-07-28 and 2026-08-04.

The Actions artifacts must pass zero-error, >=95% coverage and complete cost-output checks before numerical interpretation.


## Latest execution state

Run **37846113617** passed the import stage but failed the fail-closed artifact validation because both replay jobs discovered zero campaigns. This was traced to inherited Phase-50B opportunity enumeration rather than missing OOS data.

The wrapper has been corrected to enumerate explicit expiry files from the frozen Hugging Face options source using the existing `list_expiry_files()` function. The trade engine and frozen research rules remain unchanged.

Run 37846113617 is non-evidence. Push-triggered run **37846264039** is the registered validation attempt for this correction.

## Latest execution state — 2026-10-09

Run **37846264039** failed before numerical execution with an import/attribute error in the wrapper's source-manifest correction.

The wrapper has now been corrected to import `list_expiry_files()` directly from `phase43_vix_strategy_sweep.py`. No strategy rule, parameter, cost model or frozen endpoint was changed.

Run 37846264039 is non-evidence. The next push-triggered Actions run is the validation attempt for this correction.
