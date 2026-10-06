# Phase 35 Final Literature Review

## Advanced tree learning

LightGBM introduced Gradient-based One-Side Sampling and Exclusive Feature Bundling for efficient gradient-boosted trees: https://papers.nips.cc/paper/6907-lightgbm-a-highly-efficient-gradient-boosting-decision-tree

CatBoost introduced ordered boosting and permutation-based techniques designed to reduce prediction shift: https://proceedings.neurips.cc/paper/2018/hash/14491b756b3a51daac4124863285549-Abstract.html

DART introduced dropout over boosted regression trees to reduce over-specialization: https://proceedings.mlr.press/v38/korlakaivinayak15.html

## Probabilistic and tail forecasting

NGBoost produces conditional probability distributions through gradient boosting rather than only a point forecast: https://proceedings.mlr.press/v119/duan20a.html

Quantile-based stock-return forecasting has found predictability concentrated in conditional tails: https://doi.org/10.1016/j.frl.2017.08.003

Bayesian Additive Regression Trees have been used for nonlinear density and tail forecasting with financial indicators: https://doi.org/10.1111/iere.12619

## Decomposition and ensemble forecasting

Recent financial forecasting literature combines EMD/feature-selection with tree ensembles and reports strong performance from XGBoost, Random Forest and LightGBM: https://www.sciencedirect.com/science/article/pii/S2666659625001022

Wavelet/decomposition methods are relevant to nonstationary financial series because they separate multiple time scales before tree learning. Phase 35 reimplemented decomposition strictly from the past-only D−6 window.

## Stacking, pooling and adaptation

Stacking of heterogeneous return forecasts can improve out-of-sample stock-return prediction, but meta-model complexity raises overfitting risk: https://doi.org/10.1016/j.jempfin.2022.100835

Forecast winsorization and pooling have been reported to improve out-of-sample robustness in financial machine learning: https://doi.org/10.1016/j.jempfin.2024.101500

Adaptive dynamic ensemble selection is motivated by concept drift in financial time series: https://doi.org/10.1016/j.inffus.2025.102481

## NIFTY-specific regime research

A 2026 Applied Economics paper applies a score-driven MS-Beta-t-QVAR model to daily NIFTY 50 returns from July 1990 to April 2025 and reports regime-dependent volatility dynamics with superior volatility forecasting against several Markov-switching and single-regime alternatives: https://doi.org/10.1080/00036846.2026.2632711

Phase 35 uses a reproducible two-state Markov-switching variance proxy only as a regime/volatility gate; it does not claim to reproduce the full MS-Beta-t-QVAR model.

## Conformal uncertainty

Recent work emphasizes that ordinary exchangeability assumptions are problematic for dependent financial time series, motivating rolling/temporal conformal methods and formal coverage testing:
- https://proceedings.mlr.press/v313/barber26a.html
- https://proceedings.mlr.press/v266/retzlaff25a.html
- https://arxiv.org/abs/2601.18509

## Interpretation for this project

The literature supports a shift away from adding generic neural architectures and toward:
1. heterogeneous tree experts;
2. probabilistic/tail tree forecasts;
3. multiscale decomposition;
4. concept-drift adaptation;
5. leakage-safe stacking;
6. calibration and uncertainty/abstention.

Phase 35 tested these families under the project's stricter D−6 / 10:00 IST point-in-time protocol. Literature results are therefore treated as motivation for candidate selection, not as expected performance guarantees.
