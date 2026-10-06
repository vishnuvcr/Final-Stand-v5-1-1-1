# Phase 44 Manuscript — VIX Candidate Tuning for NIFTY Weekly Options

## Abstract

Phase 44 tested whether the strongest defined-risk candidates from the Phase-43 India-VIX sweep could be improved by finite tuning of strike geometry, entry time and prior-only India-VIX thresholds.

Six families were tested: bear call credit spread, bear put debit spread, put backspread, put broken-wing butterfly, iron butterfly and call backspread. Strike grids, entry times and VIX percentile grids were fixed before the numerical study. The option execution model used historical NIFTY lot sizes, ₹10 Paytm Money F&O brokerage per order, date-aware statutory charges and GST, and one adverse ₹0.05 option tick of slippage per leg at entry and exit.

The chronological study used development through 2023-12-31, validation from 2024-01-01 through 2025-12-31 and a protected 2026 holdout.

A major implementation defect was identified in the first development selection layer: the candidate was compared with the same structure on the same selected expiries, which made uplift exactly zero by construction. That implementation was quarantined. The accepted structural P&L matrix was retained, and the selection layer was recomputed so that active expiries carry candidate P&L, inactive expiries carry zero, and the unconditional comparator trades every eligible expiry.

The corrected development stage produced 13,292 structural observations, 3,500 development profile evaluations, 522 development-eligible configurations and a frozen set of 30 candidates. On validation, 18/30 had positive net P&L, 16/30 remained positive under +50% cost stress, and 9/30 had positive total uplift versus the unconditional tuned structure. However, zero candidates had a strictly positive 95% confidence-interval lower bound, zero had p < 0.05, and zero survived Holm correction.

Phase 44 therefore concludes NO PROMOTION. Active-exit tuning was not justified and the untouched 2026 holdout was not opened. The canonical Phase-20/42 strategy remains unchanged.

## Research Question

Can disciplined tuning of strike geometry, entry time and point-in-time India-VIX thresholds convert the strongest Phase-43 defined-risk NIFTY weekly option candidates into a statistically defensible, cost-robust out-of-sample strategy?

## Aims

1. Tune only the preregistered strongest Phase-43 defined-risk families.
2. Tune economically meaningful strike geometries rather than unrestricted continuous parameters.
3. Test 09:30, 10:00, 10:30 and 11:00 IST entry times.
4. Use only prior India-VIX observations for threshold classification.
5. Require resilience to +50% execution-cost stress.
6. Compare filtered candidates with the corresponding unconditional tuned structure.
7. Preserve an untouched 2026 holdout.
8. Stop the phase when no validation candidate survives the registered gates.

## Registered Candidate Universe

The six families were:

- bear_call_credit
- bear_put_debit
- put_backspread
- put_broken_wing
- iron_butterfly
- call_backspread

Unbounded strategies were excluded from promotion.

### Strike geometry

Bear call credit used short call +1 step and long call +2/+3/+4/+5 steps.

Bear put debit used long ATM put and short put at −1/−2/−3/−4 steps.

Put backspread used short ATM put with 1×2 long puts at −1/−2/−3 steps.

Put broken-wing butterflies used fixed unequal finite wings around the ATM short pair.

Iron butterflies used symmetric widths of 1–5 steps.

Call backspreads used short ATM call with 1×2 long calls at +1/+2/+3 steps.

### VIX states and thresholds

Level thresholds used low quantiles 15%, 20%, 25%, 30% and high quantiles 70%, 75%, 80%, 85%.

Directional thresholds used rising 80%, 85%, 90%, 95%; falling 5%, 10%, 15%, 20%; spike 80%, 85%, 90%, 95%; and the fixed HIGH_RISING combinations.

Every threshold used information strictly before the entry date.

## Chronological Methodology

Development: expiry <= 2023-12-31.

Validation: 2024-01-01 through 2025-12-31.

Holdout: 2026, protected until final candidate and active-exit rules are frozen.

No 2026 observation influenced tuning or selection.

## Execution Model

The accepted Phase-43 structural engine was reused.

Costs included:

- historical NIFTY lot sizes;
- ₹10 per executed F&O order brokerage;
- adverse ₹0.05 option tick per leg on entry and exit;
- date-aware STT;
- exchange charges;
- SEBI charges;
- IPFT;
- stamp duty;
- GST.

No forward filling or synthetic option prices were permitted. Expiry exits used the latest complete observation at or before 15:29 IST.

## Statistical Analysis

Primary unit: expiry.

Candidate P&L on each opportunity was:

- active expiry: observed candidate strategy net P&L;
- inactive expiry: zero.

The unconditional comparator used the same tuned structure on every eligible expiry.

Expiry-level uplift was candidate P&L minus unconditional comparator P&L.

Each candidate received:

- total net P&L;
- +50% cost-stress P&L;
- maximum drawdown;
- total uplift;
- mean uplift;
- 95% bootstrap confidence interval;
- sign-flip p-value;
- positive-uplift concentration.

Holm correction was applied across the 30 frozen validation candidates.

## Results

### Development

| Measure | Result |
|---|---:|
| Structural observations | 13,292 |
| Development profile evaluations | 3,500 |
| Development-eligible profiles | 522 |
| Frozen validation candidates | 30 |
| 2026 holdout opened | No |

### Validation

| Result | Count |
|---|---:|
| Positive validation net P&L | 18/30 |
| Positive +50% cost-stress P&L | 16/30 |
| Positive total uplift | 9/30 |
| Positive 95% CI lower bound | 0/30 |
| Unadjusted p < 0.05 | 0/30 |
| Holm-adjusted p < 0.05 | 0/30 |
| Validation gate passed | 0/30 |
| Inference survivors | 0/30 |

### Strongest validation uplift point estimate

Put backspread, width 1, 10:30 IST, NORMAL VIX, L=25%, H=70%:

- active trades: 48;
- validation net P&L: approximately −₹47,667;
- +50% cost-stress P&L: approximately −₹49,752;
- total uplift versus unconditional structure: approximately +₹36,029;
- mean uplift: approximately +₹356.72 per expiry;
- 95% CI: approximately −₹1,137 to +₹1,712;
- p ≈ 0.315;
- Holm-adjusted p = 1.0.

Thus the strongest uplift point estimate did not translate into a profitable or statistically defensible validation strategy.

### Highest validation net P&L

Iron butterfly, width 5, 11:00 IST, FALLING VIX, F0.20:

- validation net P&L: approximately ₹36,006;
- +50% cost stress: approximately ₹34,610;
- total uplift: approximately ₹9,278;
- 95% CI lower bound: approximately −₹818;
- p ≈ 0.423.

This also failed the validation inference gate.

## Discussion

The development period produced numerous apparently attractive filters. The correction of the uplift definition is important because it prevents an artificial zero-uplift construction and measures the economic consequence of trading only when the VIX filter is active.

After correction, development produced 522 eligible configurations and 30 frozen candidates. Validation sharply weakened these apparent advantages. Only 9 of 30 retained positive total uplift, none had a confidence interval separated from zero, and none survived multiple-testing correction.

The pattern is more consistent with parameter and regime instability than with a persistent exploitable VIX edge.

The study therefore does not support selecting a specific VIX threshold, entry time or strike geometry for live deployment.

## Stage 3 and Holdout Decision

Stage 3 active-exit tuning was preregistered only for validation inference survivors. There were none.

Consequently:

- active-exit tuning was skipped;
- the 2026 holdout was not opened;
- no holdout-driven parameter choice was permitted.

## Implementation Audit

F44-001 through F44-015 covered candidate-freeze logic, VIX profile mapping, runtime, data enumeration, memory, parquet filtering, artifact naming, schema mismatch, staged execution, trigger gating and persistence race conditions.

F44-016 corrected the development uplift comparison.

F44-017 recorded the premature validation attempt against an empty development freeze.

F44-018 optimized profile activity caching.

F44-019 corrected validation uplift accounting and removed premature holdout triggering.

All superseded outputs were treated as non-evidence.

## Strengths

- preregistered finite hypothesis universe;
- chronological development/validation separation;
- realistic transaction costs and adverse slippage;
- point-in-time VIX thresholds;
- expiry-level inference;
- Holm multiple-testing correction;
- explicit drawdown and concentration gates;
- protected 2026 holdout;
- explicit quarantining of implementation defects.

## Limitations

Historical backtesting cannot fully reproduce live bid/ask spreads, queue position, latency and fills.

The VIX state space was deliberately finite and cannot establish that every possible continuous volatility formulation is ineffective.

The validation sample is smaller than the development sample.

The phase examined selected structural families rather than every possible exotic or path-dependent option structure.

## Conclusion

Phase 44 found no statistically defensible VIX-conditioned NIFTY weekly option strategy suitable for promotion.

Corrected development screening produced 522 eligible configurations and 30 frozen candidates. Validation produced 18 candidates with positive net P&L, 16 positive under +50% cost stress and 9 with positive total uplift, but zero had a strictly positive confidence-interval lower bound, zero had p < 0.05 and zero survived Holm correction.

**Final Phase 44 decision: NO PROMOTION.**

No active-exit tuning was justified. The 2026 holdout remained protected. The canonical Phase-20/42 strategy remains unchanged.

## Future Research

Future work should be registered as new phases rather than retrofitted into Phase 44. The most promising directions are continuous volatility state, implied-versus-realized volatility spread, volatility term structure, cross-market overnight information, FII/DII flows, option open-interest structure, and stateful risk management.

A particularly useful question is whether India VIX is more valuable as a position-sizing or risk-control variable than as a binary trade/no-trade router.

## Appendix A — Stop Condition

Phase 44 closes after its registered tuning and validation stages when no candidate survives the validation inference gate. The 2026 holdout is not required to manufacture a promotion result.

## Appendix B — Reproducibility

Primary artifacts:

- PHASE44_RESEARCH_PLAN.md
- PHASE44_PRE_REGISTRATION.md
- PHASE44_LITERATURE_REVIEW.md
- PHASE44_STATUS.md
- PHASE44_CHAT_LOG.md
- PHASE44_MANUSCRIPT.md
- results/phase44_vix_tuning/stage1_structure_time_matrix.csv
- results/phase44_vix_tuning/stage1_all_dev_profiles.csv
- results/phase44_vix_tuning/stage1_candidates.csv
- results/phase44_vix_tuning/frozen_stage1.csv
- results/phase44_vix_tuning/validation_structure_time_matrix.csv
- results/phase44_vix_tuning/validation_confirmation.csv
- results/phase44_vix_tuning/validation_summary.json
- results/phase44_vix_tuning/final_decision.json
- results/phase44_vix_tuning/phase44_gate_summary.csv
- ERROR_LOG.md
- RESEARCH_LOG.md
