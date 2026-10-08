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
