# Phase 29 Manuscript Supplement — Short-Leg Delta-Change Exits

## Abstract

Phase 29 tested whether exits for the corrected NIFTY dynamic-n option strategy could be determined entirely from changes in the individual short-leg deltas. The previous target-percentage criterion was removed. The candidate did not use portfolio delta, absolute delta levels, or the Phase-20 conditional stop.

Delta coverage was 99.21%. The training-selected target was a 5-minute mean short-leg absolute-delta decrease of at least 0.20 with three-minute confirmation. The selected adverse stop was a one-minute S1 absolute-delta increase of at least 0.05 with three-minute confirmation; it produced zero uplift and did not materially drive the joint result.

Against the no-stop diagnostic control, the candidate gained ₹20,215.16 in training and ₹831.46 in validation but lost ₹574.69 in the 2026 holdout. Against the actual Phase-20 canonical strategy, it lost ₹1,092.14 in validation and ₹6,879.84 in the 2026 holdout. Phase 29 therefore failed promotion.

## Methods

For each open trade, European Black-Scholes implied volatility was reconstructed from each observed leg price and used to obtain each leg's delta. The primary variables were changes in absolute short-leg deltas:

- S1: change in absolute delta of OTM-(n+1).
- S2: change in absolute delta of OTM-(n+2).
- MEAN: arithmetic mean of S1 and S2 changes.
- BOTH: minimum of S1 and S2 changes.

A favorable target signal was a sufficiently negative change; an adverse stop signal was a sufficiently positive change. Confirmation required one or three exact consecutive complete minutes.

The search grid contained 480 rules: 4 modes × 5 lookbacks × 6 thresholds × 2 confirmation lengths × 2 exit types.

Training selection was performed only on the 2023 training period. The joint candidate used the selected target and stop without any target percentage or absolute-delta criterion.

## Results

| Period | Phase-20 canonical | Phase-29 candidate | Difference |
|---|---:|---:|---:|
| Training | ₹62,905.98 | ₹81,157.47 | +₹18,251.49 |
| Validation | ₹75,809.78 | ₹74,717.64 | −₹1,092.14 |
| 2026 holdout | ₹10,413.76 | ₹3,533.92 | −₹6,879.84 |
| Full sample | ₹149,129.53 | ₹159,409.04 | +₹10,279.51 |

The full-sample gain is not evidence of improvement because both independent out-of-sample periods are negative relative to the canonical strategy.

## Discussion

The selected mean short-leg delta-change target appears to capture a transient relationship between short-option sensitivity and favorable MTM during development. That relationship was not stable enough to survive the 2026 holdout.

This is an important distinction between an explanatory variable and a robust trading trigger. Delta change can describe how the short legs are becoming more or less sensitive while still failing to identify the economically optimal exit after spreads, slippage, brokerage and other transaction costs.

Phase 28 rejected absolute short-leg delta levels. Phase 29 now rejects fixed short-leg delta-change thresholds. Together, the results argue against adding more threshold sweeps of the same mechanism.

## Strengths

- Preregistered grid and walk-forward selection.
- Individual short-leg treatment rather than portfolio aggregation.
- No target-percentage criterion in the candidate.
- No forward filling, interpolation or synthetic crossings.
- 99.21% delta coverage.
- Existing audited execution-cost/slippage engine retained.
- Independent 2026 holdout.
- Canonical Phase-20 comparison performed before the final decision.

## Limitations

- Black-Scholes delta is model-dependent and reconstructed from market prices.
- One-minute observations do not fully model intraminute execution.
- The 2026 holdout contains only 16 trades.
- The study did not test nonlinear delta acceleration or gamma-state models.
- The persisted bootstrap intervals are relative to the no-stop diagnostic control and are not a substitute for the canonical Phase-20 comparison.

## Conclusion

Short-leg delta change did not provide sufficient robust out-of-sample evidence to replace the Phase-20 exit logic.

**Phase 29 is rejected. Phase 20 remains canonical.**

## Future direction

If delta research is reopened, the next hypothesis should be materially different rather than another fixed threshold sweep. A preregistered delta-acceleration or gamma-state model, combined with volatility/regime context and strict holdout protection, would constitute a distinct research question.
