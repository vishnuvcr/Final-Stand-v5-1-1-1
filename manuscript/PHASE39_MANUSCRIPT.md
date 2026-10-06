
# Phase 39 — Advanced and Counterfactual Direction Prediction
## Final Research Manuscript

### Abstract
Phase 39 tested whether NIFTY Continuous Delta 6x6 direction selection can be improved by predicting the post-cost economic advantage of the CALL spread versus the PUT spread instead of predicting expiry direction directly. A frozen 477-opportunity counterfactual panel was created with 271 development, 172 validation and 34 untouched 2026 holdout opportunities.

The strongest fixed-opportunity model was a Sparse GAM economic-margin model. At a ₹500 safety margin and uncertainty penalty of 1.0 it produced +₹11,609.60 validation uplift. Sequential replay through the complete stateful execution engine produced +₹17,983.53 validation uplift and +₹7,390.39 2026 holdout uplift with 7 overrides. Holdout maximum drawdown improved from ₹37,326.63 to ₹29,936.24 and the advantage survived +50% and +100% aggregate cost stress.

However, development control-relative uplift was −₹18,175.07 and only seven overrides generated the positive out-of-sample effect. The constrained symbolic candidate produced +₹11,474.77 validation uplift but zero holdout uplift. Online Hedge lost ₹416.82 in validation. DTW and SVR produced no independent improvement. Phase 39 therefore does not replace the canonical strategy. The Sparse-GAM rule is retained only as a prospective paper-trading research candidate.

## 1. Research questions
Primary: Can an action-aware, counterfactual or adaptive method identify when the CALL or PUT Continuous Delta 6x6 spread has superior post-cost outcome without unacceptable drawdown?

Secondary questions examined:
- whether CALL-minus-PUT economic margin is a better target than expiry direction;
- whether uncertainty-aware overrides can improve a strong control;
- whether adaptive/regime methods improve small-sample robustness;
- whether analog methods exploit recurring market states;
- whether online expert aggregation improves component policies;
- whether compact structural formulas capture useful economic information.

## 2. Frozen control and target
The frozen canonical comparator is the accepted Phase-32/Phase-38 stateful Continuous Delta 6x6 strategy with 50-point vertical width, six lots per leg, historical lot-size schedule, one-tick adverse slippage convention and recorded brokerage/statutory/exchange charges.

Primary target:
DeltaP&L = net P&L(CALL spread) − net P&L(PUT spread).

The fixed-opportunity panel evaluates both hypothetical arms at the same entry opportunity. Final policy claims are based only on chronological sequential replay.

## 3. Data
| Split | Trades/opportunities | Expiries | Period |
|---|---:|---:|---|
| Development | 271 | 135 | 2021–2023 |
| Validation | 172 | 82 | 2024–2025 |
| Holdout | 34 | 20 | 2026 |

Frozen validation + holdout control P&L: ₹63,672.5753.

The point-in-time feature layer contains 122 numeric features after construction. It incorporates available NIFTY, option, global, FII/DII and sentiment information while excluding sources whose point-in-time coverage was not defensible.

## 4. Methods
The preregistered families included control-relative economic-margin learning, Bayesian/regularized margin models, Bradley–Terry preference learning, dynamic Bayesian-style models, Gaussian-process margin regression, Sparse GAM, weighted kNN, DTW analogs, BOCPD regime gating, online Hedge and constrained symbolic discovery.

Chronology rules were expanding-window or otherwise explicitly past-only. Feature selection, imputation and scaling were learned without holdout information.

## 5. Fixed-opportunity model screen

| Method | Validation uplift | Decision |
|---|---:|---|
| Sparse GAM margin | +₹11,609.60 | Best candidate |
| CROL / Bayesian margin | ~₹0 | Reject |
| Bradley–Terry | ~₹0 | Reject |
| Dynamic Bayesian logistic | ~₹0 | Reject |
| Gaussian process | ~₹0 | Reject |
| Weighted kNN | ~₹0 | Reject |
| DTW | ~₹0 | Reject |
| SVR/RBF | ~₹0 | Reject |
| BOCPD-GAM | +₹11,609.60 | No independent improvement |
| Online Hedge | −₹416.82 | Reject |
| Symbolic candidate | +₹12,026.42 | Sequential test required |

Sparse-GAM fixed-opportunity paired-expiry bootstrap:
95% interval approximately −₹1,250 to +₹36,079.

This interval crosses zero, so the fixed-opportunity screen alone was not decisive.

## 6. Sequential Sparse-GAM result

| Period | Policy net P&L | Control net P&L | Incremental P&L |
|---|---:|---:|---:|
| Development | −₹517.92 | ₹17,657.15 | −₹18,175.07 |
| Validation | ₹81,931.75 | ₹63,948.22 | +₹17,983.53 |
| 2026 holdout | ₹7,114.74 | −₹275.65 | +₹7,390.39 |
| Combined | ₹88,528.57 | ₹81,329.72 | +₹7,198.85 |

Overrides: 7.

Validation maximum drawdown:
- policy ₹32,021.65;
- control ₹32,021.65.

2026 holdout maximum drawdown:
- policy ₹29,936.24;
- control ₹37,326.63.

Cost-stress uplift:
- validation +₹17,799.05 at +50% costs and +₹17,614.56 at +100%;
- holdout +₹7,546.34 at +50% costs and +₹7,702.28 at +100%.

These results are the strongest new finding in Phase 39, but they are still not sufficient for promotion.

## 7. Symbolic sequential result
The constrained symbolic candidate selected the simple feature candidate_credit_diff_call_minus_put with zero safety margin.

Sequential validation uplift: +₹11,474.77.
2026 holdout uplift: ₹0.
2026 holdout drawdown: unchanged from control.
+50% validation cost-stress uplift: +₹11,268.41.
+100% validation cost-stress uplift: +₹11,062.05.

Because the holdout effect is exactly zero, the symbolic policy is rejected.

## 8. Online Hedge
Development uplift: +₹2,598.30.
Validation uplift: −₹416.82.
Holdout: not evaluated.

The online ensemble is rejected because its frozen validation result is negative.

## 9. Main scientific finding
The research supports a change in framing: the useful object is not merely NIFTY direction but the economic margin between two directly tradable spread structures.

The positive validation/holdout Sparse-GAM effect suggests that rare, selective overrides can sometimes improve the control, especially during later regimes. However, the effect is sparse and unstable enough that it should not yet be treated as a durable trading edge.

## 10. Strengths
- economic counterfactual target rather than indirect direction classification;
- frozen canonical comparator;
- strict chronological training;
- explicit uncertainty penalty;
- complete sequential replay;
- historical slippage and transaction costs retained;
- untouched 2026 holdout;
- deterministic paired-expiry bootstrap;
- explicit error logging and supersession of invalid results.

## 11. Limitations
- only 477 fixed opportunities and 34 holdout observations;
- seven overrides in the strongest sequential result;
- negative development control-relative uplift;
- limited availability of fully point-in-time NSE/BSE breadth, futures basis/OI, corporate-action and timestamp-verified news feeds;
- historical simulation cannot establish future liquidity, fill quality, latency or regime stability.

## 12. Final conclusion
Phase 39 does not replace the canonical strategy.

The canonical Phase-20/24 strategy remains authoritative.

The strongest research candidate is:
Sparse GAM economic-margin override policy — retain the canonical stateful direction by default and override only when predicted alternative post-cost improvement minus uncertainty exceeds ₹500.

Promotion decision: REJECTED FOR CANONICAL STRATEGY.

Reason:
1. development incremental P&L is negative;
2. only seven overrides create the positive out-of-sample result;
3. fixed-opportunity paired-expiry uncertainty crosses zero;
4. symbolic improvement disappears on holdout;
5. online aggregation is negative in validation;
6. no other registered family provides an independent advantage.

The Sparse-GAM policy is retained as a paper-trading/prospective candidate only.

## 13. Future research
The next highest-value research phase should be prospective/paper validation with live broker-quality quotes, real Paytm Money fills and costs, latency and bid/ask information.

A separate data-enrichment phase should add defensible point-in-time NIFTY futures basis/OI, NSE/BSE breadth, corporate actions and timestamp-verified news. This should be treated as a new data phase rather than another unrestricted model sweep.

The seven historical override events should also be monitored prospectively for regime persistence.

## 14. Reproducibility
All accepted Phase-39 artifacts live on branch phase-39-advanced-direction-models, including the research plan, preregistration, literature review, counterfactual ledger, point-in-time feature matrix, model screens, sequential replay, cost audits, symbolic audit and ERROR_LOG.md.

## 15. Decision statement
Phase 39 is scientifically complete under its registered stop rule.

Final decision:
REJECT PROMOTION.
RETAIN SPARSE-GAM AS A PAPER-TRADING RESEARCH CANDIDATE.
KEEP THE CANONICAL PHASE-20/24 STRATEGY UNCHANGED.
