# Phase 40 Manuscript — Exhaustive Direction-Model Ensembles with India VIX

## Abstract

### Background
Five machine-learning direction selectors had previously failed to demonstrate statistically reliable incremental value when tested individually against the canonical Continuous Delta 6x6 stateful NIFTY strategy. Phase 40 tested a different hypothesis: the rejected models might contain complementary information, and volatility regime information from India VIX might improve routing even when a model is weak unconditionally.

### Objective
To exhaustively evaluate combinations of CATBOOST, DART, WAVELET_TREE, OOF_STACK, MARKOV_REGIME_TREE and India VIX under fixed aggregation and VIX-routing rules, while preserving the canonical strategy's direction polarity, transaction-cost model, slippage and chronological state machine.

### Methods
A pre-registered grid of 1,764 combinations (63 non-empty expert subsets × four aggregators × seven VIX modes) was screened on the 2024-01-11 to 2025-12-30 validation window. India VIX thresholds were learned only from pre-2024 observations. Equivalent expiry-level signal sequences were deduplicated, yielding 306 unique validation policies. The top 10 unique policies were frozen before untouched 2026 holdout replay. Exact sequential replay used the Phase-32 state machine, including direction carry, delta-based exits, one-tick adverse slippage, brokerage, statutory charges and GST. Paired expiry bootstrap and sign-flip inference used 10,000 resamples.

### Results
The strongest validation policy was **CATBOOST with a HIGH India-VIX gate and canonical fallback**. It produced ₹97,533.94 exact-sequential validation net P&L versus ₹76,841.96 for the frozen control on 73 common expiries, an uplift of **₹20,691.98** (₹283.45 per expiry). However, its one-sided sign-flip p-value was **0.2185** and the 95% expiry-bootstrap CI for mean uplift included zero (approximately 0 to ₹779 per expiry).

On the untouched 2026 holdout, the same pre-selected CATBOOST/HIGH policy produced **₹12,797.11** versus **-₹275.65** for the control, an uplift of **₹13,072.75** (₹653.64 per expiry). The 95% CI for mean uplift was approximately **-₹183 to ₹2,144**, and the sign-flip p-value was **0.4006**. Thus the holdout point estimate is positive but statistically inconclusive.

The best holdout result among the frozen top 10 was a different policy, **VIX-only with a RISING gate**, at an uplift of **₹14,294.32**, but choosing that policy after seeing holdout performance would violate the pre-registered selection rule. It is therefore reported only as a diagnostic result and is not a promoted strategy.

### Conclusion
Phase 40 provides evidence that **India VIX regime conditioning is potentially important**, especially the high-VIX routing regime, but it does **not establish a statistically validated trading edge**. No Phase-40 ensemble is promoted. The canonical stateful strategy remains the control.

---

## 1. Research questions

1. Can combinations of previously tested direction models outperform the canonical stateful direction rule after realistic execution costs?
2. Does India VIX add information as an expert, regime classifier or gate?
3. Does model disagreement contain useful information for routing?
4. Are any improvements stable on untouched 2026 data and under cost stress?

## 2. Aims

The primary aim was to test whether complementary model information plus volatility-regime routing can improve the actual trading decision without changing the Continuous Delta 6x6 execution engine.

Secondary aims were to:
- quantify the contribution of India VIX;
- compare aggregation methods;
- distinguish model-label diversity from true decision-policy diversity;
- evaluate statistical and economic robustness;
- prevent holdout selection bias through a frozen top-10 protocol.

## 3. Pre-registered hypothesis

The phase assumed that at least one ensemble or VIX-gated policy would show positive incremental P&L relative to the canonical control and retain that advantage on untouched holdout data.

No learned ensemble weights were estimated from validation or holdout.

## 4. Data and study design

### Study periods
- Validation: 2024-01-11 through 2025-12-30.
- Untouched holdout: 2026-01-06 through 2026-05-19.
- Prediction-covered study universe used by the exhaustive model grid: 93 weekly-expiry blocks.

The canonical frozen Phase-38 control is independently archived at:
`results/phase38_corrected_model_robustness/frozen_control_expiry.csv`.

### Expert universe
- CATBOOST
- DART
- WAVELET_TREE
- OOF_STACK
- MARKOV_REGIME_TREE
- India VIX

The five model probabilities use the corrected economic polarity:
- bullish probability ≥ 0.50 -> PUT credit spread;
- bearish probability < 0.50 -> CALL credit spread.

India VIX is aligned point-in-time using the previous session's close and one-day change.

## 5. Exhaustive combination grid

All 63 non-empty subsets of the six experts were tested.

Aggregation:
- arithmetic mean;
- median;
- majority vote;
- confidence-weighted mean using fixed distance from 0.50.

VIX routing:
- OFF;
- VIX expert;
- HIGH;
- LOW;
- RISING;
- FALLING;
- HIGH_RISING.

Total declared combinations: **1,764**.

Equivalent expiry-level direction sequences were hashed and collapsed to **306 unique validation policies** before top-10 holdout selection.

## 6. India VIX thresholds

Development-only thresholds:
- absolute daily-return q67: **0.03988018**
- level q33: **14.7474**
- level q67: **20.4300**

The most important grid-level result was that the **HIGH VIX** mode dominated validation:
- 252 HIGH-mode candidates;
- all 252 were positive relative to the common-expiry control;
- best uplift: **₹21,262.83**.

By contrast:
- OFF: no positive validation candidates at the grid-selection stage;
- LOW: no positive validation candidates;
- EXPERT: no positive validation candidates;
- RISING: only 11 positive candidates;
- FALLING: 40 positive candidates;
- HIGH_RISING: 252 positive candidates, but with much smaller best uplift than HIGH.

This concentration strongly suggests that volatility regime is more useful as a **routing variable** than as a direct bullish/bearish predictor.

## 7. Validation ranking

The pre-selected top policy was:

**Candidate 3 — CATBOOST + HIGH India VIX gate + canonical fallback**

Exact sequential validation:
- net P&L: **₹97,533.94**
- control: **₹76,841.96**
- uplift: **₹20,691.98**
- mean uplift: **₹283.45/expiry**
- 73 common expiry blocks
- one-sided sign-flip p-value: **0.2185**
- 95% bootstrap CI for mean uplift: approximately **₹0 to ₹779/expiry**
- validation drawdown by expiry: **₹23,478.38**

The large validation uplift is economically interesting but cannot be treated as independent evidence because the policy was selected using validation performance.

## 8. Untouched 2026 holdout

The pre-selected Candidate 3 produced:

- candidate net: **₹12,797.11**
- control net: **-₹275.65**
- uplift: **₹13,072.75**
- mean uplift: **₹653.64/expiry**
- 20 common holdout expiries
- 95% bootstrap CI for mean uplift: **-₹183 to ₹2,144**
- one-sided sign-flip p-value: **0.4006**
- positive expiry blocks: 4/20

The holdout point estimate is positive, but the confidence interval is wide and crosses zero.

### Important holdout-selection safeguard
A different frozen-top-10 candidate, VIX-only with a RISING gate (Candidate 873), produced the largest holdout uplift of **₹14,294.32**. This result cannot be used to select a trading policy because Candidate 873 was not chosen as the primary policy from holdout data. Its result is retained only as a descriptive robustness observation.

## 9. Cost and execution robustness

The sequential replay used:
- one tick of adverse slippage per execution;
- four orders per completed spread trade;
- brokerage;
- exchange transaction charges;
- SEBI charges;
- IPFT;
- STT;
- stamp duty;
- GST;
- expiry-specific NIFTY lot sizes;
- exact historical option quotes;
- delta-triggered exits.

For the pre-selected Candidate 3, the sequential validation stress remained positive under +25%, +50% and +100% cost multipliers at the candidate level. This does not by itself establish incremental superiority because the control must also be stressed under the same cost multiplier.

## 10. Statistical methodology

The primary incremental estimand is expiry-level:
[
Delta_t = P&L_{candidate,t} - P&L_{control,t}.
]

Inference:
- paired expiry bootstrap, 10,000 resamples;
- sign-flip permutation test;
- 95% confidence intervals;
- positive-expiry fraction;
- maximum drawdown;
- profit factor;
- cost stress.

Because 1,764 specifications were screened and 306 unique decision policies remained after deduplication, validation-only p-values are not treated as confirmatory. The untouched holdout is the principal test of generalization.

## 11. Results by candidate

| Candidate | Policy | Validation uplift | Validation p | Holdout uplift | Holdout p |
|---|---|---:|---:|---:|---:|
| 3 | CATBOOST + HIGH VIX | ₹20,691.98 | 0.2185 | ₹13,072.75 | 0.4006 |
| 199 | OOF_STACK + HIGH VIX | ₹15,492.77 | 0.4131 | ₹12,692.64 | 0.4531 |
| 426 | MARKOV_REGIME_TREE + FALLING VIX | ₹11,741.75 | 0.3295 | -₹29.60 | 0.5595 |
| 566 | CATBOOST+WAVELET_TREE+MARKOV + FALLING | ₹9,004.21 | 0.3637 | -₹29.60 | 0.5618 |
| 587 | same + confidence weighted + FALLING | ₹4,240.65 | 0.4548 | -₹29.60 | 0.5576 |
| 629 | CATBOOST+DART+WAVELET+MARKOV + FALLING | ₹3,936.84 | 0.4442 | -₹29.60 | 0.5580 |
| 517 | CATBOOST+DART+MARKOV + FALLING | ₹3,399.51 | 0.4530 | -₹29.60 | 0.5521 |
| 873 | VIX + RISING | ₹2,643.12 | 0.1690 | **₹14,294.32** | 0.3109 |
| 7 | CATBOOST + HIGH_RISING | ~₹0.00 | 0.7619 | ₹13,072.75 | 0.4017 |
| 573 | CATBOOST+WAVELET+MARKOV + median FALLING | -₹403.59 | 0.5062 | -₹29.60 | 0.5593 |

The holdout rankings should not be used to re-select the strategy. Candidate 3 remains the proper primary interpretation because it was selected on validation.

## 12. Interpretation

### Main finding
The new information in Phase 40 is not that a particular classifier has suddenly become reliable. The stronger finding is that **volatility regime materially changes the value of direction information**.

High India VIX routing produced the strongest validation concentration. This is consistent with the idea that directional model information has conditional usefulness in stressed markets rather than a stable unconditional edge.

### Why this is still not a promoted strategy
Three conditions remain unmet:
1. the primary holdout uplift is not statistically distinguishable from zero;
2. the holdout contains only 20 expiry blocks;
3. the exhaustive validation search creates substantial selection pressure.

The fact that four of ten frozen candidates are positive on holdout is encouraging, but it is not enough to establish an independent trading edge.

### Why the VIX finding matters
India VIX appears more useful as a **state/routing variable** than as a direct direction predictor. That is a meaningful methodological result and is worth carrying into a subsequent, separately registered phase.

## 13. Strengths

- exhaustive, pre-registered combination universe;
- explicit holdout freeze;
- deduplication of equivalent policies;
- point-in-time VIX alignment;
- corrected model-to-spread polarity;
- exact stateful replay;
- realistic slippage, brokerage and taxes/charges;
- paired expiry inference;
- comprehensive error logging.

## 14. Limitations

- the untouched 2026 holdout is short;
- multiple testing remains substantial despite policy deduplication;
- India VIX source caching uses a market-data provider and should be cross-audited against official NSE historical India VIX before live deployment;
- historical 1-minute quote data may not represent live bid/ask fill probability;
- fixed transaction-cost assumptions cannot fully reproduce broker-specific live execution;
- the top-10 selection is validation-driven, so validation uplift is not independent evidence;
- no claim of causal efficacy is made.

## 15. Conclusion

Phase 40 **does not validate a new production trading strategy**.

The best pre-selected policy is:

> **CATBOOST direction model, activated only when India VIX is in the high regime (VIX ≥ 20.43 using the prior-session close), otherwise revert to the canonical stateful direction rule.**

On the exact sequential replay it produced:
- validation: **₹97,533.94**, +₹20,691.98 vs control;
- holdout: **₹12,797.11**, +₹13,072.75 vs control;
- holdout p-value: **0.4006**.

Therefore the scientifically correct label is:

**PROMISING / INCONCLUSIVE — NOT PROMOTED.**

The canonical stateful strategy remains the accepted benchmark.

## 16. Future research

The next registered research direction should not be another unrestricted classifier sweep. The stronger hypothesis is **regime-conditional decision value**.

A follow-on phase should test:
- India VIX percentile and term/regime measures;
- VIX level × VIX change interactions;
- option-implied skew and put/call volatility asymmetry;
- global volatility cross-market confirmation;
- regime-duration and transition features;
- abstention rules based on model disagreement;
- broker-realistic bid/ask and fill-probability simulation;
- a longer untouched prospective holdout before any live promotion.

Any such work should begin on a new branch with a new pre-registration and should not use the Phase-40 2026 holdout for tuning.

## 17. Reproducibility artifacts

- Exhaustive grid: `results/phase40_ensemble/grid_validation.csv`
- Frozen top 10: `results/phase40_ensemble/selection.json`
- Fixed-opportunity inference: `results/phase40_ensemble/inference_top10.csv`
- Exact sequential replay: `results/phase40_ensemble/sequential_top10.csv`
- Expiry-level sequential audit: `results/phase40_ensemble/sequential_top10_expiry.csv`
- India VIX cache: `data/phase40_vix/india_vix.csv`
- Validation VIX figure: `results/phase40_ensemble/validation_uplift_by_vix_mode.png`
- Holdout figure: `results/phase40_ensemble/holdout_top10.png`
- Error log: `ERROR_LOG.md`
- Workflow: `.github/workflows/phase-40-ensemble-direction-models.yml`

## 18. Final decision

**Phase 40 decision: NO PROMOTION.**

The result is sufficient to close the phase as a completed scientific experiment. Any future use of the CATBOOST/HIGH-VIX idea must be treated as a new hypothesis, not as an accepted live strategy.
