# Phase 43 Manuscript — VIX-Conditioned NIFTY Weekly Options Strategy Sweep

## Abstract
Phase 43 evaluated whether India VIX can condition the choice of NIFTY weekly options strategy after realistic transaction costs and adverse slippage. A finite preregistered universe of 22 strategy families was tested across 262 expiry opportunities, producing 4,597 strategy observations. The experiment used a fixed entry at 10:00 IST four trading sessions before expiry, a structural exit at the latest common complete observation at or before 15:29 IST on expiry day, historical NIFTY lot sizes, ₹10 Paytm Money F&O brokerage per executed order, date-aware statutory charges, and one adverse ₹0.05 option tick per leg at entry and exit.

The raw strategy matrix completed successfully. A statistical implementation defect in the first inference layer was identified: a VIX-regime subset had been compared with the identical rows from the unconditional sample, mechanically forcing zero differences. The inference was rerun using regime-versus-complementary-non-regime validation observations. A second postprocess audit also caught an attempted benchmark contamination by unbounded ratio structures; the benchmark/router universe was corrected to the registered defined-risk universe.

Final result: **no VIX-conditioned strategy or router met the preregistered promotion gate.** The corrected regime tests produced no Holm-adjusted significant positive VIX effect, and no router survived the development-to-validation cost-stress screen. Stage-5 active-exit optimization was therefore not pursued.

## 1. Research questions
1. Does NIFTY weekly strategy performance differ systematically across India-VIX states?
2. Can India VIX improve strategy-family selection rather than merely describe volatility?
3. Does a development-frozen VIX router survive validation?
4. Do any apparent VIX-conditioned advantages survive realistic costs, adverse slippage and multiple-testing adjustment?

## 2. Aims and objectives
The primary aim was to determine whether India VIX provides a robust ex-ante state variable for selecting among major NIFTY weekly options structures.
Secondary objectives were to compare strategy families, measure regime dependence, quantify the effect of realistic execution frictions, and test a bounded VIX strategy router without holdout tuning.

## 3. Scientific methodology
### 3.1 Timing
Entry was fixed at exactly four trading sessions before expiry, 10:00 IST. The structural exit was the latest common complete observation at or before 15:29 IST on expiry day. No same-day post-entry information was used for VIX classification.

### 3.2 VIX state definition
The latest cached India VIX observation strictly before entry was used. Regime thresholds were based only on earlier observations. Declared states were LOW, NORMAL, HIGH, SPIKE, FALLING, RISING, HIGH_RISING and ALL.

### 3.3 Strategy universe
The declared universe contained straddles, strangles, debit and credit verticals, long butterflies, iron butterfly, iron condor, broken-wing butterflies, ratio spreads, backspreads, calendars and reverse calendars. For promotion, only the registered defined-risk universe was eligible. Unbounded straddles, strangles and ratio spreads were diagnostic only.

### 3.4 Execution model
Each leg received one adverse ₹0.05 option tick at both entry and exit. Brokerage was ₹10 per executed F&O order. Date-aware STT, exchange transaction charges, SEBI fees, IPFT, stamp duty and GST were applied. Historical NIFTY lot-size transitions were retained.

### 3.5 Chronology
Development was used for strategy/router selection, validation for confirmation, and 2026 was untouched until all validation selection was complete.

### 3.6 Statistical analysis
The primary inference unit was the expiry opportunity. Corrected VIX-regime tests used 10,000-resample mean-difference bootstrap intervals and permutation tests comparing regime observations with complementary non-regime validation observations for the same strategy. Holm adjustment was applied across the declared strategy×regime hypotheses.

## 4. Sample accounting
| Component | Result |
|---|---:|
| Declared strategy families | 22 |
| Defined-risk promotion families | 18 |
| Expiry opportunities | 262 |
| Strategy observations | 4,597 |
| Development observations | 2,398 |
| Validation observations | 1,821 |
| Untouched 2026 holdout observations | 378 |
| Data exclusions | 2 |
| Frozen strategy×VIX candidates | 0 |
| Frozen VIX routers | 0 |

The two data exclusions occurred because modal strike-step information was unavailable for the corresponding expiry files; they were not synthetically reconstructed.

## 5. Results
### 5.1 Unconditional defined-risk benchmark
The best development mean among the eligible defined-risk promotion universe was **call_backspread**, at approximately **₹247.08 per trade**. Its validation result was negative, so it did not provide a stable unconditional benchmark for promotion.

### 5.2 VIX-conditioned strategy grid
Several strategy×VIX combinations were profitable in validation, but none passed the complete development + validation + cost-stress promotion gate.

| Strategy / VIX state | Development net | Validation net | Validation +50% cost net |
|---|---:|---:|---:|
| Bear call credit / LOW | −₹45,473.64 | +₹24,742.59 | +₹23,082.00 |
| Bear call credit / NORMAL | −₹1,408.51 | +₹12,501.60 | +₹10,658.02 |
| Bear put debit / LOW | −₹14,243.73 | +₹13,892.13 | +₹12,108.82 |
| Bear put debit / NORMAL | −₹1,798.33 | +₹4,907.89 | +₹3,037.45 |
| Put broken-wing / LOW | −₹38,215.82 | +₹13,672.68 | +₹10,477.15 |
| Iron butterfly / LOW | −₹34,172.52 | +₹3,713.90 | +₹221.47 |

The common failure is chronological instability: positive validation regime outcomes were not preceded by positive development results under the preregistered selection rule.

### 5.3 Unbounded diagnostic structures
Short straddle, short strangle and ratio structures generated some positive validation/holdout numbers. They were not eligible for promotion because their theoretical risk is not bounded on the same capital basis as the defined-risk structures.

### 5.4 Corrected VIX inference
The first inference implementation was rejected because it compared a regime subset with its identical rows in the ALL sample, producing mechanically zero paired differences. The corrected analysis used complementary non-regime validation observations.

**Final statistical finding:** no strategy×VIX test survived Holm adjustment at p < 0.05, and the corrected 95% bootstrap intervals crossed zero.

### 5.5 Router selection
The corrected promotion universe contained only defined-risk candidates with adequate development history. The three preregistered router scoring methods did not produce a router with positive validation net P&L and positive +50% cost-stress performance under the required gate. Frozen VIX routers = **0**.

No holdout router was selected and no active-exit optimization was allowed.

## 6. Discussion
The most important finding is negative. India VIX may describe the volatility environment, but within this finite NIFTY weekly options universe it did not produce a stable strategy-selection edge that survived chronological validation and multiple-testing correction.

There were isolated regime/strategy combinations with positive validation outcomes. However, these were generally accompanied by negative development performance or unstable cross-period behavior. The strongest unconditional development benchmark among eligible defined-risk strategies also failed validation, reinforcing the conclusion that simple historical profitability did not translate into forward robustness.

The unbounded strategies are especially important to interpret correctly. Short-volatility structures can show attractive historical win rates and cumulative P&L, but their risk profile is materially different from the defined-risk structures and therefore cannot be used to justify promotion under this study.

## 7. Strengths
- broad but finite preregistered strategy universe;
- point-in-time VIX states;
- realistic brokerage and statutory charges;
- adverse one-tick-per-leg slippage;
- historical NIFTY lot-size handling;
- untouched 2026 holdout;
- multiple-testing adjustment;
- explicit exclusion of unbounded structures from promotion;
- invalid statistical implementation discovered and corrected before final conclusion.

## 8. Limitations
- public historical bars do not reproduce live queue position or exact bid/ask fills;
- India VIX is represented by the latest prior observation rather than a full intraday volatility surface;
- strategy-family comparisons inherently involve multiple hypotheses;
- calendar structures have sparse historical coverage in the available minute dataset and therefore were not eligible for router promotion under the minimum-trade rule;
- only the declared VIX states were tested; new threshold families would constitute a new research phase.

## 9. Conclusion
**Phase 43 concludes with NO PROMOTION.**

The study does not provide sufficient evidence that India VIX can robustly select a NIFTY weekly option strategy after realistic transaction costs and slippage.

No VIX-conditioned strategy, regime policy, or router is promoted. The canonical Phase-20/42 strategy remains unchanged.

## 10. Future research
The highest-value next phase is not another unconstrained search over VIX thresholds. The more defensible next step is execution realism: exchange-grade bid/ask reconstruction, fill-probability modelling, and prospective paper validation of the existing canonical strategy and any future VIX hypothesis.

## Appendix A — Core evidence artifacts
- results/phase43_vix/strategy_trade_matrix_all_splits.csv
- results/phase43_vix/corrected_strategy_summary_by_split.csv
- results/phase43_vix/corrected_strategy_vix_validation_grid.csv
- results/phase43_vix/corrected_strategy_vix_inference.csv
- results/phase43_vix/corrected_frozen_strategy_vix_candidates.csv
- results/phase43_vix/corrected_frozen_top10_strategy_vix_candidates.csv
- results/phase43_vix/corrected_router_dev_validation.csv
- results/phase43_vix/corrected_frozen_router_holdout.csv
- results/phase43_vix/corrected_router_maps.json
- results/phase43_vix/data_errors.csv
- results/phase43_vix/strategy_vix_heatmap.png