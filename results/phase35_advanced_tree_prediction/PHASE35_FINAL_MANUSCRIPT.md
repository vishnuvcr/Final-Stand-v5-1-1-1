# Phase 35 Final Manuscript — Advanced Tree, Probabilistic and Adaptive NIFTY D−6 Prediction

## Abstract

Phase 35 tested the most important prediction methods remaining after Phases 33–34 while deliberately retaining tree-based learning as the central forecasting family. The locked reference remained exactly 10:00 IST on six calendar days before each NIFTY 50 expiry. The eligible sample contained 245 events: 128 development, 95 chronological validation and 22 untouched 2026 holdout observations.

The numerical program covered LightGBM, CatBoost, DART, XGBoost and prior tree controls; equal-weight and winsorized tree pooling; recursive feature selection; NGBoost; quantile boosting; BART; wavelet, EMD, VMD and explicit CEEMDAN decomposition followed by trees; adaptive rolling and exponentially weighted trees; dynamic model pooling; chronological out-of-fold stacking; Platt and isotonic calibration; conformal uncertainty; regime-gated trees; and a reproducible two-state Markov-switching volatility-gate proxy inspired by the 2026 NIFTY MS-Beta-t-QVAR literature.

No model passed the complete promotion gate. The strongest holdout directional results were produced by several tree-family and stacked methods, but their validation performance was not sufficiently strong or consistent to justify treating the 22-event 2026 holdout as proof of a durable edge. Therefore **Phase 20 remains the canonical trading strategy and no Phase-35 predictor is promoted directly to live trading**.

## Research question

Can advanced tree-based, probabilistic, decomposition-enhanced, adaptive, regime-aware and uncertainty-calibrated methods improve the D−6 / 10:00 IST NIFTY direction forecast beyond the strongest Phase-34 tree baseline under strict chronological out-of-sample testing?

## Study design

Reference:
- expiry minus six calendar days;
- exactly 10:00:00 IST;
- events without an exact reference observation excluded.

Target:
- NIFTY expiry-day close/latest complete observation at or before 15:29 IST;
- directional target = sign of log(expiry_close / reference_spot).

Evaluation:
- development through 2023-12-31;
- validation 2024-01-01 through 2025-12-31;
- untouched holdout 2026-01-01 through 2026-09-30.

Leakage controls:
- backward-only joins;
- global-market values shifted to information-available timestamps;
- FII/DII backward joins;
- all feature selection and scaling fitted within the chronological training window;
- sequence/decomposition features constructed only from observations before the reference;
- stacking trained from chronological out-of-fold predictions;
- no holdout-driven threshold or weight optimization.

## Models tested

### Core tree family
XGBoost, LightGBM, CatBoost, HistGradientBoosting, ExtraTrees, LightGBM-DART.

### Tree combinations
Equal six-tree pooling, winsorized pooling, dynamic accuracy-weighted pooling, regime-gated tree selection, and chronological OOF stacking.

### Probabilistic / distributional tree methods
NGBoost, quantile boosting and Bayesian Additive Regression Trees.

### Decomposition-enhanced trees
Wavelet, EMD, VMD and explicit CEEMDAN decomposition of past-only NIFTY returns followed by LightGBM-style tree prediction.

### Adaptive methods
Fixed 52-event rolling tree training and exponentially weighted recent-history trees.

### Calibration and uncertainty
Platt scaling, isotonic calibration and temporal conformal-style interval/abstention diagnostics.

### Regime method
A reproducible two-state Markov-switching variance proxy feeding a LightGBM tree model. This is explicitly a **proxy for the role of a regime/volatility gate** and is not claimed to reproduce the published NIFTY MS-Beta-t-QVAR model byte-for-byte.

## Results

The Phase-35 validation leader by accuracy remained XGBoost at 57.89%, tied by CatBoost at 57.89%. No new model exceeded the Phase-34 validation benchmark.

The strongest raw 2026 holdout accuracy was 68.18%, achieved by several methods:
- CatBoost;
- ExtraTrees;
- LightGBM-DART;
- Wavelet + tree;
- chronological OOF stack;
- Markov-switching regime proxy + tree.

The strongest holdout signed-return diagnostics were:
- OOF stack: mean +0.00951; 95% bootstrap CI +0.00255 to +0.01627; sign-flip p=0.0139.
- Wavelet + tree: +0.00880; CI +0.00164 to +0.01560; p=0.0252.
- Markov-switching regime + tree: +0.00868; CI +0.00154 to +0.01559; p=0.0267.
- Equal six-tree pool: +0.00863; CI +0.00186 to +0.01549; p=0.0300.
- LightGBM-DART: +0.00856; CI +0.00139 to +0.01561; p=0.0311.
- LightGBM: +0.00844; CI +0.00132 to +0.01550; p=0.0350.
- HistGradientBoosting: +0.00832; CI +0.00141 to +0.01532; p=0.0359.

The simple always-down baseline achieved 63.64% accuracy on the 22-event holdout. Several 68.18% methods therefore beat it on raw direction, but the sample is too small for that result to be considered independently decisive.

### Methods that did poorly

The weakest families were:
- Adaptive 52-event window: 36.36% holdout accuracy.
- CEEMDAN + tree: 50.00%.
- EMD + tree: 45.45%.
- Quantile tree: 50.00%.
- NGBoost: 54.55%.
- BART: 54.55%.
- Conformal direction rule: 36.36%.

The compact probabilistic models generally did not outperform the stronger deterministic tree models in this small event sample.

## Calibration and uncertainty

The model probabilities were not uniformly well calibrated. BART, NGBoost, decomposition models and several adaptive approaches showed substantially larger calibration error than the best calibrated controls.

The conformal interval layer produced approximately:
- 89.47% empirical coverage on validation against a nominal 90%;
- 86.36% on the 2026 holdout.

However, the interval-based confidence rule never declared a confident direction. Every event remained within the predictive interval, so the conformal layer produced no actionable directional filter.

This is an important negative result rather than a failure of the research: uncertainty-aware prediction did not find a sufficiently strong confidence region in this dataset.

## Statistical interpretation

The central statistical issue is the holdout size of only 22 observations. A single event changes directional accuracy by 4.55 percentage points. Consequently, apparent 68.18% holdout accuracy should not be interpreted as proof of a persistent 68% directional edge.

There is also dependence among tree-family results. CatBoost, ExtraTrees, DART, Wavelet-tree and the stack are not independent experiments. Their simultaneous success therefore does not provide 5 independent confirmations.

The positive signed-return intervals are encouraging, particularly for the OOF stack, Wavelet-tree and regime-tree candidates, but they are still predictive diagnostics rather than option-strategy P&L.

## Promotion decision

**NO MODEL IS PROMOTED TO LIVE TRADING.**

The registered validation gate requires improvement over the strongest Phase-34 validation benchmark. None of the new methods exceeded the 57.89% validation-accuracy benchmark; CatBoost merely tied it.

The correct next step is a separate frozen trading-overlay phase rather than further model tuning.

## Discussion

The strongest evidence from Phase 35 is not that one model has won. It is that **tree-based representations remain the most promising structural family**, while adding probabilistic or adaptive complexity does not automatically improve robustness.

DART, LightGBM, Wavelet-tree and the OOF stack generated particularly strong holdout diagnostics. Their common characteristic is nonlinear tree learning combined with either ensemble diversity, multiscale features or forecast combination. Conversely, large amounts of adaptation or highly flexible probabilistic modeling often degraded validation stability.

The conformal result also matters. A well-constructed uncertainty layer should be willing to abstain when the data do not support a reliable decision. Here it abstained everywhere. That argues against forcing a direction on every expiry.

The 2026 NIFTY MS-Beta-t-QVAR literature supports the existence of economically important high- and low-volatility regimes, but the exact published model is primarily a volatility/regime model rather than a directional classifier. The Phase-35 implementation therefore treated regime detection as a gate/feature rather than pretending the published model itself had been reproduced.

## Strengths

- Strict point-in-time D−6 reference.
- Untouched 2026 holdout.
- Chronological validation.
- Cached data rather than repeated uncontrolled downloading.
- Tree-model diversity.
- Explicit probabilistic and uncertainty methods.
- Decomposition only from past information.
- Chronological OOF stacking.
- Bootstrap and sign-flip inference.
- Full error/correction logging.

## Limitations

- Only 22 holdout events.
- Public option/sentiment coverage is incomplete.
- Model families are statistically correlated.
- Some sophisticated methods require larger samples for reliable estimation.
- Signed-return prediction is not executable options P&L.
- No direct broker-fill or option transaction-cost overlay was part of this prediction-only phase.

## Conclusion

Phase 35 exhaustively expanded the prediction-model search while preserving tree-based models as the core family.

The evidence does **not** justify promoting a new direction model to live use.

The most promising frozen candidates for a separate trading-overlay study are:
1. OOF tree stack;
2. Wavelet + tree;
3. DART;
4. CatBoost;
5. ExtraTrees;
6. Markov-switching regime proxy + tree.

That shortlist must now be tested against the actual Continuous Delta 6x6 strategy with:
- exact option entry/exit fills;
- Paytm Money brokerage and statutory charges;
- slippage;
- spread/liquidity constraints;
- expiry gaps;
- existing expiry-day stop rules;
- trade-level MAE/MFE;
- drawdown;
- regime stability;
- no additional tuning on the untouched holdout.

Phase 35 therefore closes the **prediction-model search**. Any further improvement belongs to a new, explicitly registered trading-overlay phase.

## Reproducibility

Accepted principal numerical run:
- GitHub Actions **37425240176**.

Accepted Markov-switching addendum:
- GitHub Actions **37426499636**.

Accepted CEEMDAN addendum:
- GitHub Actions **37426761476**.

All failed/superseded runs are recorded in `ERROR_LOG.md` and are excluded from the evidence set.
