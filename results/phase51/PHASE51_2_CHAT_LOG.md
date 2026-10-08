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

## 2026-10-09 — Partial-window opportunity-calendar finding

Run 37846507265 executed the wrapper after the source-manifest correction but again found zero campaigns. Audit against the Phase-50B frozen TT-03 rule and Phase-51-1 source gate showed why: all 14 observed expiries from 2026-04-21 through 2026-07-21 are Tuesdays, while entry is exactly three calendar days before expiry, which lands on Saturday for every one.

The partial study therefore cannot produce a numerical OOS P&L sample without changing the frozen strategy rule. The branch has been changed to record an explicit `NO_ELIGIBLE_CAMPAIGNS` calendar-audit result rather than treating zero opportunities as a data failure. Full Phase 51 remains blocked by the missing 2026-07-28 and 2026-08-04 option blocks.

## 2026-10-09 — Errors P51-2-006/P51-2-007: reference artifact was absent from concurrent workflow checkouts

Runs **37846806366** and **37846815991** failed because the newly added `PHASE51_1_SOURCE_GATE_REFERENCE.json` was not present in the commit being executed.

**Evidence status:** non-evidence / repository-ordering issue.

**Correction:** the reference artifact was recreated and verified on the current Phase-51-2 branch. The wrapper will be retriggered from a subsequent commit after the reference artifact is definitely in its ancestry.

## 2026-10-09 — Partial-OOS audit completed

Corrected workflow run **37847094909** completed successfully for both matrix geometries.

Final accepted Phase-51-2 status: **NO_ELIGIBLE_CAMPAIGNS**. Both d300 and d350 found the same 14 observed expiries, zero eligible entries, and therefore no P&L sample. The complete Phase-51 window remains blocked by the unresolved 2026-07-28 and 2026-08-04 option blocks.

The phase report was written to results/phase51/PHASE51_2_PARTIAL_OOS_REPORT.md. No strategy was promoted or rejected on economic grounds.
