# Phase 35 — Advanced Tree, Probabilistic, Adaptive and Regime-Gated NIFTY D-6 Prediction

## Abstract
Phase 35 tested an extensive, pre-specified family of NIFTY direction-prediction methods at the exact D-6 10:00 IST reference point used by the preceding research. The study evaluated gradient-boosted trees, probabilistic regressors, Bayesian Additive Regression Trees, signal-decomposition features, adaptive rolling trees, dynamic ensemble selection, leakage-safe out-of-fold stacking, probability calibration, temporal conformal intervals, and a reproducible two-state Markov-switching volatility-regime proxy. The dataset contained 245 eligible events: 128 development events, 95 validation events, and 22 untouched 2026 holdout events.

## Research question
Can advanced tree-based, probabilistic, decomposition, adaptive, ensemble, calibration, or regime-gated models provide a robust improvement over the existing NIFTY D-6 direction controls sufficient to justify testing as a direction chooser for the Continuous Delta 6x6 strategy?

## Methods
The reference event is the exact 10:00 IST observation six calendar days before expiry. The target is the NIFTY expiry close/latest complete observation before the expiry close cutoff. Development ends 2023-12-31; validation covers 2024-2025; the holdout covers 2026-01-01 through 2026-09-30.

All models were evaluated chronologically. No 2026 holdout labels were used for fitting or tuning. Metrics included accuracy, balanced accuracy, ROC-AUC, log loss and Brier score. The economic diagnostic is model-signed expiry-horizon log return, explicitly not option P&L. Bootstrap confidence intervals and paired sign-flip tests were used as robustness diagnostics.

## Results
The strongest 2026 holdout directional accuracy was 68.18%, achieved by CatBoost, ExtraTrees, LightGBM-DART, Wavelet-tree, OOF stacking, and the Markov-switching regime + tree proxy. The strongest holdout signed-return diagnostic was OOF stacking at +0.00951, followed by Wavelet-tree at +0.00880 and the Markov-regime tree at +0.00868. Several of these had bootstrap intervals excluding zero in this small holdout, but the sample contains only 22 events.

Validation performance was materially less uniform. XGBoost and CatBoost were 57.89% on validation; BART was 55.79%; VMD-tree was 55.79%; and several other methods were near or below chance. The 52-event adaptive model deteriorated to 36.36% on holdout. Conformal intervals achieved 89.47% validation and 86.36% holdout coverage for a nominal 90% interval, but no observation satisfied the strict confident-direction rule.

## Interpretation
The results support a narrower conclusion than “a new predictive model has been found.” Tree ensembles remain the most useful family, but the apparent 68.18% holdout performance is based on only 22 observations and multiple related models. The OOF stack and regime/decomposition variants are promising research candidates, not established trading signals.

The Markov-switching model used here is a reproducible proxy for the regime-gating role described in the literature, not a byte-for-byte reproduction of a specialized MS-Beta-t-QVAR specification. It should therefore be interpreted as supporting evidence about regime conditioning, not as validation of that exact published architecture.

## Strengths
- Chronological train/validation/holdout separation.
- Untouched 2026 holdout.
- Broad model-family comparison.
- Leakage-safe OOF stacking.
- Explicit uncertainty and calibration diagnostics.
- Cached data and reproducible GitHub Actions execution.
- Numerical failures were logged and corrected rather than silently discarded.

## Limitations
- Only 22 holdout events.
- Prediction target is direction/spot return, not executable option P&L.
- Model correlations reduce the effective number of independent tests.
- Several methods require larger samples for reliable probability calibration.
- Full transaction costs, option bid/ask fills, Paytm Money brokerage/statutory charges, slippage and expiry execution effects remain outside this screening phase.

## Conclusion
Phase 35 does **not** promote a new model directly into live trading. It narrows the research candidates to CatBoost, LightGBM-DART, Wavelet-tree, OOF stacking, and the Markov-regime tree proxy for a separate strategy-level overlay test.

## Future research
Freeze these candidates and test them without further tuning against the Continuous Delta 6x6 vertical-spread strategy. The next study must evaluate actual option-chain execution, Paytm Money charges, slippage, liquidity, expiry gaps, stop-loss rules, MFE/MAE, drawdown, risk-adjusted returns and regime-specific behavior. Only strategy-level net-of-cost evidence should be considered for promotion.
