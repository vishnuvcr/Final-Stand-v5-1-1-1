# Phase 51-2 Action Log

## 2026-10-09
User authorized proceeding with the available-data approach.

A separate partial-OOS study was registered rather than altering the frozen full-window protocol. The study endpoint is fixed at the last currently complete option expiry, 2026-07-21.

Two already-frozen TT-03 geometries are being replayed: BASE (distance 300) and OTM350 (distance 350).

No private chain-of-thought is stored. This log records research actions, decisions, outcomes and corrections only.

### Workflow audit and correction
Runs 37845718056 and 37845741103 both reached the replay stage but failed before numerical execution because the wrapper was invoked as a file path and could not import the `research` package.

The wrapper was corrected to add both repository-root and research-directory paths explicitly. During the same audit, an output-path collision with the inherited Phase-50B engine was identified and corrected so Phase-51-2 artifacts are written only under `results/phase51/partial_oos`.

Both failures are logged in PHASE51_2_ERROR_LOG.md as non-evidence. The partial-OOS research protocol and frozen endpoint were not changed.

## 2026-10-09 — Fresh-OOS opportunity enumeration correction

Corrected replay run 37846113617 reached the numerical engine but returned zero campaigns for both distances. Audit traced this to the inherited `expiry_dates()` helper reading a Phase-43 trade matrix rather than the frozen option-source expiry manifest.

The wrapper now overrides only the opportunity enumeration with the engine's existing source-manifest function `list_expiry_files()`. No strategy parameter, execution rule, frozen endpoint or cost assumption changed. Run 37846113617 remains non-evidence.

## 2026-10-09 — Source-manifest import correction

Run 37846264039 failed immediately because the prior wrapper correction referenced `base.list_expiry_files`, but the function is defined in `phase43_vix_strategy_sweep.py` and is not exported by the inherited TT-03 module.

The wrapper now imports the helper directly from its defining module. Run 37846264039 is non-evidence; no OOS P&L was produced.
