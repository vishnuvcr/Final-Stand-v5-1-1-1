# Phase 29 Status — Delta-Change Exit Research

**Status: COMPLETE — REJECTED / NOT PROMOTED**

## Research question

Can the exit target and stop be driven entirely by change in the individual short-leg deltas, especially S1 and S2, without any target-percentage criterion, absolute-delta level criterion, portfolio-delta criterion, or Phase-20 conditional stop?

## Registered design

- S1 = short OTM-(n+1) leg; S2 = short OTM-(n+2) leg.
- Delta-change lookbacks: 1, 3, 5, 10, 15 minutes.
- Modes: S1, S2, MEAN, BOTH.
- Thresholds: 0.02, 0.05, 0.08, 0.10, 0.15, 0.20.
- Confirmation: 1 or 3 consecutive complete minutes.
- Target = favorable fall in short-leg absolute delta.
- Stop = adverse rise in short-leg absolute delta.
- No target percentage, absolute-delta level, portfolio-delta trigger, or Phase-20 conditional stop in the candidate.
- Expiry fallback only if neither delta trigger fires.
- Same execution-cost/slippage engine and walk-forward partitions as the corrected dynamic-n research.

## Data quality

Three-leg delta coverage: 99.21%.

## Training selection

Target: MEAN_target_lb5_d0.20_c3

Stop: S1_stop_lb1_d0.05_c3

The selected stop produced zero uplift in every partition, so the joint candidate was effectively driven by the selected target.

## Raw no-stop diagnostic comparison

| Period | No-stop control | Phase-29 candidate | Uplift |
|---|---:|---:|---:|
| Training | ₹60,942.32 | ₹81,157.47 | +₹20,215.16 |
| Validation | ₹73,886.19 | ₹74,717.64 | +₹831.46 |
| 2026 holdout | ₹4,108.62 | ₹3,533.92 | −₹574.69 |
| Full | ₹138,937.12 | ₹159,409.04 | +₹20,471.92 |

These are diagnostic only. The canonical control is Phase 20.

## Canonical Phase-20 comparison

Phase-20 net P&L: training ₹62,905.98; validation ₹75,809.78; 2026 holdout ₹10,413.76; full ₹149,129.53.

Phase-29 candidate minus Phase 20:

| Period | Difference |
|---|---:|
| Training | +₹18,251.49 |
| Validation | −₹1,092.14 |
| 2026 holdout | −₹6,879.84 |
| Full | +₹10,279.51 |

The candidate fails the out-of-sample promotion requirement.

## Bootstrap diagnostic

The persisted bootstrap was relative to the no-stop diagnostic control:

- Validation mean uplift +₹10.80; 95% CI −₹21.17 to +₹53.57.
- 2026 holdout mean uplift −₹35.92; 95% CI −₹107.75 to ₹0.00.
- Full mean uplift +₹107.75; 95% CI −₹14.51 to +₹338.21.

These intervals do not override the negative canonical Phase-20 comparison.

## Decision

**NO PROMOTION.**

Phase 29 does not replace or modify the Phase-20 canonical strategy.

The evidence suggests short-leg delta change contains some development-period timing information, but the selected rule did not persist through the 2026 holdout and did not improve the frozen canonical strategy in either out-of-sample period.

## Research conclusion

Phase 28 rejected absolute short-leg delta levels. Phase 29 now rejects fixed short-leg delta-change thresholds. More threshold sweeps of the same mechanism should not be added to the current plan.

Phase 20 remains the historical canonical strategy. No live deployment recommendation follows from Phase 29.
