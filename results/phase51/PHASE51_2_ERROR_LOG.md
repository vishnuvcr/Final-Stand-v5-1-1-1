# Phase 51-2 Error Log

No numerical error has been accepted yet. The execution boundary is fail-closed: artifacts must satisfy zero data errors, >=95% complete-campaign coverage and required cost fields before interpretation.

The missing 2026-07-28 and 2026-08-04 expiries are intentionally excluded from this partial study and remain unresolved for complete Phase-51 validation.

## 2026-10-09 — Error P51-2-001: replay module import failure

**Affected workflow runs:** 37845718056 and 37845741103  
**Affected jobs:** replay (300) and replay (350)

**Symptom:** both jobs failed before numerical execution with `ModuleNotFoundError: No module named 'research'` when executing `python research/phase51_2_partial_oos.py`.

**Cause:** GitHub Actions executes the entry point as a file, so Python placed `research/` on `sys.path` but not the repository root. The wrapper attempted a package-style import `research.phase50b_tt03_otm_distance_replay`.

**Evidence status:** non-evidence. No OOS P&L or statistical output was produced.

**Correction:** the wrapper now explicitly adds both the repository root and `research/` directory to `sys.path` before importing the frozen Phase-50B engine.

**Prevention:** phase wrappers executed as file paths must establish deterministic import paths explicitly rather than relying on interpreter invocation context.

## 2026-10-09 — Error P51-2-002: inherited output path mismatch detected during code audit

**Status:** corrected before accepting any numerical result.

The inherited TT-03 engine writes to `results/phase50b/tt03_otm_distance/d<distance>`, while the Phase-51-2 workflow validates `results/phase51/partial_oos/d<distance>`. Without an explicit output override, a successful replay would have produced artifacts in the wrong phase namespace and caused the validation step to fail or, worse, create cross-phase artifact ambiguity.

**Correction:** the Phase-51-2 wrapper now overrides the engine output root to `results/phase51/partial_oos/d<distance>`.

**Evidence status:** no numerical evidence was affected because the mismatch was identified while repairing the import failure, before an accepted replay.

## 2026-10-09 — Error P51-2-003: inherited expiry enumeration yielded zero fresh-OOS campaigns

**Affected workflow run:** 37846113617  
**Affected jobs:** replay (300) and replay (350)

**Symptom:** the corrected wrapper executed successfully but produced `trades=0` and `candidate_trades=0` for both frozen geometries. The workflow validation correctly rejected the artifacts.

**Cause:** the inherited Phase-50B engine's `expiry_dates()` read `results/phase43_vix/strategy_trade_matrix_all_splits.csv`, which does not enumerate the fresh Phase-51 OOS opportunities. This was an opportunity-discovery defect, not a data-quality result.

**Evidence status:** non-evidence. No OOS P&L was calculated.

**Correction:** Phase 51-2 now overrides only the expiry enumeration to use the existing frozen source manifest function `list_expiry_files()`, which enumerates explicit NIFTY option expiry files from the registered Hugging Face source within the frozen 2026-04-21 to 2026-07-21 endpoint. The trade engine, costs, entry/exit rules and candidate parameters remain unchanged.

**Prevention:** every fresh-OOS wrapper must enumerate opportunities from the frozen OOS source manifest, not from a prior phase's strategy-trade matrix.

## 2026-10-09 — Error P51-2-004: source-expiry helper imported from the wrong module

**Affected workflow run:** 37846264039  
**Affected jobs:** replay (300) and replay (350)

**Symptom:** both jobs failed before numerical execution with `AttributeError: module 'research.phase50b_tt03_otm_distance_replay' has no attribute 'list_expiry_files'`.

**Cause:** the first correction assumed `list_expiry_files()` was re-exported by the inherited TT-03 engine. It is defined in `phase43_vix_strategy_sweep.py` and only selected functions were imported into the TT-03 module.

**Evidence status:** non-evidence. No OOS P&L or coverage result was produced.

**Correction:** the wrapper now imports `list_expiry_files` explicitly from `phase43_vix_strategy_sweep` and assigns that source-manifest function to the inherited engine's `expiry_dates` hook.

**Prevention:** source-manifest helpers must be resolved from their defining module during phase-wrapper audit; do not assume incidental re-export.
