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
