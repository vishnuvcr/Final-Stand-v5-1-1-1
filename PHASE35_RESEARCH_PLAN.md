# Phase 35 Research Plan — Advanced Tree, Probabilistic and Adaptive NIFTY D−6 Prediction

## Objective
Identify and, in the next numerical phase, test the strongest prediction methods that remain after Phases 33–34, while **retaining tree-based models as the core family**.

## Research question
At exactly 10:00 IST on six calendar days before NIFTY expiry, can advanced tree-based, probabilistic-tree, adaptive-regime or decomposition-enhanced methods improve the Phase-34 tree baseline under strict chronological out-of-sample testing?

## Priority model families

### Tier 1 — mandatory tree-family expansion
1. **LightGBM** — distinct GBDT implementation using GOSS and EFB.
2. **CatBoost** — ordered boosting; tested even though the current feature set is mostly numeric, because its optimization differs from XGBoost/HistGB.
3. **DART boosting** — dropout over boosted trees to reduce over-specialization.
4. **NGBoost** — probabilistic gradient boosting with a tree base learner, directly producing a conditional distribution rather than only a point probability/return.
5. **Bayesian Additive Regression Trees (BART)** — Bayesian sum-of-trees with posterior uncertainty; appropriate for small samples and nonlinear interactions.
6. **Quantile boosting / quantile tree ensemble** — estimate lower/median/upper conditional return quantiles; derive directional probability and downside-risk features without assuming Normality.

### Tier 2 — tree + signal decomposition
7. **Wavelet + tree models** — DWT/WPD decomposition of pre-reference NIFTY and cross-market signals followed by LightGBM/XGBoost/CatBoost.
8. **EMD/CEEMDAN/VMD + tree models** — decompose nonstationary signals into intrinsic modes, then model the modes with trees.
9. **RFE/stability feature selection + tree models** — feature selection must be fitted within the training window only.
10. **Hybrid decomposition + tree ensemble** — use a frozen, low-dimensional decomposition feature set rather than a large hyperparameter sweep.

### Tier 3 — adaptation and combination
11. **Rolling/expanding adaptive tree models** — explicitly test concept drift through expanding, fixed-window and recency-weighted training.
12. **Dynamic model selection / dynamic ensemble selection** — choose among tree specialists based on current feature-space/regime neighborhood.
13. **OOF stacking** — combine LightGBM, CatBoost, XGBoost, ExtraTrees and HistGB through a simple Ridge/Logistic meta-learner trained only on chronological out-of-fold predictions.
14. **Forecast pooling + winsorization** — cap extreme individual model forecasts before combination.
15. **Regime-conditioned trees** — use volatility/regime information as a gating variable; the regime model is a gate, not a stand-alone direction predictor.
16. **Score-driven / Markov-switching volatility gate** — use the recently published NIFTY MS-Beta-t-QVAR family as a volatility/regime state variable, not as the primary directional model.

### Tier 4 — uncertainty/calibration layers
17. **Rolling conformal prediction / conformalized quantile regression** — generate valid uncertainty intervals under sequential dependence using rolling calibration rather than ordinary iid conformal assumptions.
18. **Probability calibration** — isotonic/Platt/temperature calibration fitted from chronological out-of-fold predictions only.
19. **Confidence filter / abstention** — trade-direction prediction only when calibrated probability exceeds a fixed preregistered confidence band; otherwise classify as NO-EDGE. Threshold must be frozen before holdout.
20. **False-confidence diagnostics** — evaluate whether forecast confidence is systematically too high in specific volatility/regime cells.

## Features and data
Reuse the Phase-33/34 point-in-time cache:
- NIFTY price/returns/volatility/range/drawdown;
- options at the exact reference timestamp where available;
- FII/DII;
- global markets shifted to information-available timestamps;
- sentiment;
- market regime/volatility diagnostics.

Additional features:
- wavelet/EMD/VMD coefficients from past-only windows;
- cross-market dispersion;
- realized-volatility term structure;
- regime-state probabilities;
- tree-model forecast dispersion;
- calibration residuals.

No feature may use post-reference information.

## Chronological evaluation
- Development: through 2023-12-31.
- Validation: 2024-01-01 through 2025-12-31.
- Untouched holdout: 2026-01-01 through 2026-09-30.

For adaptive methods, model updating must use only observations whose outcomes would have been known at each prediction date.

## Required statistical tests
- Accuracy, balanced accuracy, ROC-AUC, log loss, Brier score.
- Mean signed expiry-horizon log return.
- Bootstrap 95% CI.
- Sign-flip permutation test.
- Calibration error / reliability curve.
- Quantile score/pinball loss for probabilistic models.
- Coverage and interval score for conformal intervals.
- Diebold–Mariano tests for paired forecast loss where assumptions and sample size permit.
- Regime/subperiod stability.
- Multiple-comparison awareness for the expanded model family.

## Promotion gates
No candidate is promoted merely because it wins a single metric.

A candidate must:
1. outperform the best Phase-34 tree/control model on validation;
2. remain superior to the strongest simple baseline on the untouched holdout;
3. show economically positive signed-return performance with uncertainty compatible with a genuine edge;
4. remain reasonably calibrated;
5. survive regime/subperiod checks;
6. remain useful after a frozen trading-overlay test with Paytm Money brokerage, statutory charges, slippage, fills and expiry gaps.

## Important anti-overfitting rules
- No random k-fold CV on the complete event set.
- No holdout-driven threshold selection.
- No feature selection using holdout observations.
- No unrestricted model/feature sweep after inspecting holdout.
- Stacking meta-learners must use chronological OOF predictions.
- Adaptive windows must be pre-registered.
- Decomposition parameters must be fixed or selected only within training.

## Explicitly deprioritized
- Another generic LSTM.
- Another generic Transformer architecture.
- Stand-alone HMM direction prediction.
- Large hyperparameter sweeps.
- Any method whose main advantage can only be demonstrated through random cross-validation.

## Phase sequence
1. Freeze this plan and literature review.
2. Implement mandatory Tier-1 tree models.
3. Implement one decomposition pathway (wavelet/EMD family) with a tree learner.
4. Implement one adaptive/stacking pathway.
5. Add calibration/conformal diagnostics.
6. Run chronological validation and untouched holdout.
7. Produce manuscript, uncertainty figures, model comparison and final decision.
8. Stop. Any further family is a new phase.
