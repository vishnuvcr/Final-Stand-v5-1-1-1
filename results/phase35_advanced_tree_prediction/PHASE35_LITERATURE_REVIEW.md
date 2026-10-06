# Phase 35 Literature Review — Advanced Tree, Probabilistic and Adaptive Forecasting

## 1. Advanced gradient-boosted tree families

**LightGBM.** LightGBM is a distinct gradient-boosting implementation based on Gradient-based One-Side Sampling (GOSS) and Exclusive Feature Bundling (EFB). Its importance here is not speed alone: it is a materially different tree-growth/sampling implementation from the XGBoost and HistGB models already tested. citeturn311551search0turn311551search1

**CatBoost.** CatBoost uses ordered boosting and permutation-based processing designed to reduce prediction shift caused by target leakage during boosting. Even though our current predictors are mostly numeric, its boosting dynamics are sufficiently different to justify a fixed benchmark. citeturn311551search3

**DART.** DART applies dropout to boosted regression trees to reduce over-specialization of later trees. It is a meaningful variant of boosted-tree ensembles rather than a new neural architecture. citeturn311551academia175

## 2. Probabilistic tree prediction

**NGBoost.** NGBoost converts boosting into probabilistic prediction of an entire conditional distribution and commonly uses decision trees as base learners. This is attractive for NIFTY because the trading problem needs not only a direction probability but also uncertainty around the expiry-horizon move. citeturn847947search6turn847947search10

**Quantile boosting.** Quantile boosting has evidence of short-horizon stock-return predictability concentrated in conditional tails. For our research, the key use is to estimate lower-tail and upper-tail expiry returns rather than assume a Normal mapping from a point forecast. citeturn577843search3

**BART.** Bayesian Additive Regression Trees model nonlinearities through a sum of trees while providing posterior uncertainty. Multivariate BART has been used for density and tail forecasting and has shown gains in overall and tail forecast performance in macro/financial applications. citeturn577843search9turn577843search12

## 3. Decomposition before tree learning

A recent financial-forecasting study reports gains from Empirical Mode Decomposition (EMD) plus recursive feature elimination before ensemble prediction; the study compared Random Forest, XGBoost, LightGBM, AdaBoost, CatBoost, Bagging and ExtraTrees and found XGBoost, Random Forest and LightGBM among the strongest. citeturn847947search3turn847947search8

Wavelet-based feature engineering is also promising. A 2024 study proposed discrete-wavelet decomposition, feature reduction and PSO-optimized ensemble learning and reported strong NIFTY index results. Because that literature uses different sample design and may contain preprocessing choices that are inappropriate for a live D−6 task, our implementation must recompute every decomposition strictly from information available before 10:00. citeturn847947search5

Recent work also combines empirical-mode decomposition with XGBoost and other hybrid models for nonstationary financial series. citeturn577843search2turn577843search7

## 4. Model combination and stacking

Stacking has direct empirical support in stock-return forecasting. A Journal of Empirical Finance study found stacking of different model types can improve out-of-sample return forecasts, with gains particularly pronounced in downside markets, while warning that excessive meta-model complexity increases overfitting. citeturn841619search2

A recent 2026 study emphasizes generating leakage-safe out-of-fold predictions within the training window and fitting a simple meta-learner on those OOF forecasts. That design is especially relevant here because naive stacking would leak the same label information into the meta-model. citeturn736928search1

Forecast pooling and winsorization are also supported by recent financial forecasting evidence: a 2024 Journal of Empirical Finance paper reports that winsorizing and pooling machine-learning forecasts improves out-of-sample robustness across several countries. citeturn841619search11

## 5. Non-stationarity and concept drift

This is likely more important for NIFTY than adding another deep architecture. A 2025 dynamic-ensemble paper explicitly addresses concept drift with adaptive dynamic ensemble selection. citeturn841619search0

A July 2026 paper on adaptive financial time-series classification argues that financial relationships evolve and proposes continuous adaptation to distribution changes. citeturn841619search1

The implication for this project is to test **recency weighting, rolling windows, adaptive tree retraining and dynamic expert selection**, rather than assuming a single tree model trained on the entire historical sample remains optimal.

## 6. NIFTY-specific regime/volatility advances

A 2026 Applied Economics paper uses daily NIFTY 50 returns from July 1990 to April 2025 and proposes an MS-Beta-t-QVAR score-driven Markov-switching model. It reports superior out-of-sample volatility-forecasting performance versus several single-regime and Markov-switching GARCH/EGARCH benchmarks. citeturn847947search7

This is not necessarily a superior directional predictor. Its strongest role for our project is as a **regime/uncertainty gate feeding a tree model**.

## 7. Probability calibration and uncertainty

Tree models can produce probabilities that are poorly calibrated. A 2026 financial-ML calibration study emphasizes that raw tree probabilities can be overconfident and recommends fitting calibration models using leakage-safe out-of-fold predictions. citeturn736928search2

Temporal conformal prediction is also becoming relevant for financial forecasting. A 2025/2026 literature stream evaluates rolling conformal methods for dependent financial returns and explicitly warns that ordinary split-conformal assumptions do not automatically hold for serially dependent returns. citeturn577843search6turn577843academia149

Therefore conformal methods should be used here as an **uncertainty/calibration layer**, not as a substitute for the base tree predictor.

## 8. Most relevant synthesis for this project

The most promising unexplored combination is:

**LightGBM + CatBoost + XGBoost + ExtraTrees/HistGB**
→ **chronological OOF forecasts**
→ **simple Ridge/Logistic stacker**
→ **probability calibration**
→ **regime/volatility gate**
→ **optional conformal uncertainty/abstention**

A second strong pathway is:

**past-only wavelet/EMD features**
→ **LightGBM/XGBoost/CatBoost**
→ **quantile or probabilistic output**
→ **calibrated direction probability**

These two pathways preserve the project's demonstrated tree-model strength while directly addressing the major weaknesses seen in Phases 33–34: small sample size, nonstationarity, calibration uncertainty and noisy tail behavior.
