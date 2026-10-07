# Research Log — main branch

## 2026-10-03 — Phase 20 isolated runner trigger
- Added a temporary main-branch execution bridge that checks out only `phase-20-payoff-boundary-stop-research`, executes the pre-registered boundary-stop research, and persists outputs back to that phase branch.
- The strategy code and research artifacts remain isolated on the Phase-20 branch.
- Phase history and detailed step logs continue on the phase branch.
[RUN_PHASE20_BRIDGE]

## 2026-10-03 — Phase 20 optimized execution trigger
- Optimized Phase 20 to reuse the locked 190-trade ledger and NIFTY spot file, loading option files only for expiry dates capable of breaching the entry payoff boundary.
- Corrected strike-column access in the option-path reconstruction before triggering the run.
[RUN_PHASE20_BRIDGE_OPTIMIZED]


## 2026-10-03 — Main-branch Phase 20 final status
- Phase 20 payoff-boundary research completed on isolated branch `phase-20-payoff-boundary-stop-research`.
- Boundary-stop family rejected after negative validation and 2026 holdout results.
- Final historical exit rule: target → 13:30 expiry-day negative-MTM/MFE<0.50×target stop → 15:29 expiry fallback.
- Final historical result: ₹149,129.53 net P&L across 190 trades; 179/190 positive net trades; 5 conditional stops; 0 baseline-positive trades stopped.
- Canonical final rules: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/FINAL_STRATEGY_RULES.md
- Detailed Phase 20 log, errors and artifacts remain on the isolated research branch.


## Final research closeout — 2026-10-03
- Phase 23 complete; no OOS strategy adjustment promoted.
- Phase 24 complete; no reversal trigger promoted.
- Final strategy remains the Phase-20 canonical dynamic-n specification.
- Final manuscript and evidence package are retained on branch phase-24-targeted-reversal-trigger.


## 2026-10-04 — Phase 27 final status
- Phase 27 delta-based exit research completed on isolated branch `phase-27-delta-exit-research`.
- Training-selected delta profit rule: MTM ≥ 0.90×target and |portfolio delta| ≤ 0.05.
- Validation uplift: −₹2,334.04. 2026 holdout uplift: −₹1,108.04.
- Holdout bootstrap 95% CI for mean trade-level uplift: −₹141.92 to −₹13.82.
- No adverse-delta stop selected.
- **No Phase-27 rule promoted; Phase-20 remains canonical.**


## Phase 28 — individual-leg delta research — COMPLETE — 2026-10-04

Phase 28 tested S1=short OTM-(n+1) and S2=short OTM-(n+2) deltas independently. Coverage was 99.21%. The least-bad training rule was S1 |delta|≤0.05 after 90% target, but it lost ₹2,998.16 training, ₹2,487.05 validation and ₹35.91 in the 2026 holdout. No adverse short-leg delta stop passed. **No promotion; Phase-20 remains canonical.**


## 2026-10-05 — Phase 29 complete: short-leg delta-change exits
- Tested target and stop entirely from individual/combined short-leg delta change; removed target-percentage criteria.
- Delta coverage 99.21%; 480 preregistered rules.
- Training-selected target: MEAN, 5-minute, 0.20 threshold, 3-minute confirmation.
- Training-selected stop: S1, 1-minute, 0.05 threshold, 3-minute confirmation; zero uplift.
- Versus canonical Phase 20: +₹18,251.49 training, −₹1,092.14 validation, −₹6,879.84 2026 holdout, +₹10,279.51 full.
- **Decision: no promotion; Phase 20 remains canonical.**
- Artifacts persisted on the Phase-29 branch.


## 2026-10-06 — Phase 41 active interim status
- Isolated branch phase-41-regime-conditional-policy-learning created from Phase 40.
- The registered fixed-opportunity screen completed successfully: 24 variants evaluated; zero passed the validation safety screen.
- The top three diagnostic policies produced zero overrides across development, validation and the frozen 2026 fixed panel.
- Exact sequential identity validation remains the registered closing step.


## 2026-10-06 — Phase 41 final closeout
- Phase 41 completed with 24 pre-registered regime-conditional economic-margin variants.
- No variant passed the validation safety gate; the top three frozen diagnostics all had zero overrides across the full development/validation/2026 counterfactual panel.
- Exact sequential replay was completed by the registered identity/no-op audit and matched the canonical control exactly: zero validation and holdout uplift, zero overrides, p=1.0000.
- **Decision: no promotion. Canonical stateful strategy remains unchanged.**


## 2026-10-06 — Phase 42 closeout published to main
- Accepted numerical workflow: 37470344620.
- 72 preregistered variants screened; 2 passed development/validation selection.
- Primary sequential policy: SPLINE_RIDGE_VIX + RAW + ₹500 + ALL; +₹26,542.28 validation uplift and +₹20,607.09 2026 holdout uplift.
- Holdout paired-expiry 95% CI for mean uplift crossed zero (−₹2,020.42 to +₹4,297.35); one-sided sign-flip p=0.3054.
- Final decision: no promotion; canonical stateful strategy unchanged.


## 2026-10-06 — Phase 43 registered
- Created isolated branch `phase-43-vix-all-options-strategies` from the Phase-42 research head.
- Registered the finite VIX-conditioned NIFTY strategy universe, point-in-time VIX regimes, Paytm Money cost model, development/validation/untouched-2026 holdout design, router selection and 10,000-resample inference.
- Canonical Phase-20/42 strategy remains unchanged pending a separately accepted Phase-43 result.
- Initial implementation-writing incident F43-001 was logged on the Phase-43 branch; no numerical evidence was affected.


## 2026-10-06 — Phase 43 final closeout published
- Phase 43 completed on isolated branch `phase-43-vix-all-options-strategies`.
- 22 strategy families / 4,597 observations / 262 expiry opportunities evaluated under point-in-time India VIX and realistic execution costs.
- Corrected regime inference found no Holm-adjusted significant VIX advantage.
- Corrected promotion universe restricted to defined-risk strategies; zero strategy×VIX candidates and zero routers passed the full gate.
- Stage 5 active-exit optimization skipped.
- **Final decision: NO PROMOTION; canonical Phase-20/42 strategy unchanged.**
- Final manuscript: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-43-vix-all-options-strategies/PHASE43_MANUSCRIPT.md


## 2026-10-06 — Phase 44 VIX candidate tuning initialized
- Created isolated branch `phase-44-vix-candidate-tuning` from completed Phase 43.
- Registered finite tuning of six defined-risk Phase-43 candidates using strike geometry, entry time and prior-only VIX percentile profiles.
- The 2026 holdout remains protected until validation/inference freezing.
- Automated branch workflow and main execution bridge registered.
- Initial implementation audit F44-001 was logged and quarantined before evidence acceptance.


## 2026-10-06 — Phase 44 corrected numerical execution
- F44-002 and F44-003 were corrected before accepting any numerical evidence.
- The active Phase-44 run now uses the optimized corrected engine with development-only candidate freeze, validation-only confirmation and 2026 holdout protection.


## 2026-10-06 — Phase 44 active corrected run
- Current numerical run: **37488148310** after F44-005 bounded-memory correction.
- No Phase-44 numerical result has been accepted yet; holdout protection remains active until validation/inference freeze.


## 2026-10-06 — Phase 44 active run update
- Current corrected Stage-1 execution is run **37491292566**.
- No Phase-44 result is accepted yet; 2026 holdout protection remains in force.


## 2026-10-06 — Phase 44 staged execution
- Phase 44 was converted from a monolithic numerical run to development → validation → holdout execution.
- Current corrected development run: **37496337984** after F44-013.
- Premature validation/holdout attempts were classified as failures/non-evidence and logged.
- 2026 holdout remains protected.


## 2026-10-06 — Phase 44 final closeout
- Completed corrected VIX candidate tuning and validation under the registered chronological and cost model.
- No candidate survived the validation inference gate.
- Final decision: **NO PROMOTION**.


## 2026-10-07 18:15 IST — Phase 50B continuation
- Resumed from the accepted TT-03 V5 PASS.
- Live TT-04 run 37621965843 was rechecked; preflight passed and numerical replay remained in progress.
- Re-read TT-04 source audit/workflow/engine at the active run head. No new evidence-impacting defect was identified.
- No TT-04 numerical result is accepted until the artifact audit passes.
