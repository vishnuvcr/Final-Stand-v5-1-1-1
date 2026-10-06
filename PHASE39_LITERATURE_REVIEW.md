# Phase 39 Literature Review — Beyond Standard Direction Classifiers

## Why the search changes after Phase 38

The repository already contains a broad Phase-35 model search covering conventional boosted trees, tree ensembles, probabilistic boosting, BART, quantile trees, decomposition hybrids, adaptive trees, OOF stacking, regime gating, calibration and conformal prediction. Phase 38 then showed that the corrected model selectors do not beat the canonical stateful control.

The next search therefore emphasizes methods that change the **problem formulation**, handle **nonstationarity**, or exploit the small-data structure rather than adding more deep architectures.

## 1. Counterfactual and policy learning

The strongest methodological opportunity is to model the reward difference between the two actual actions.

Offline contextual-bandit research treats action choice as a context-dependent reward problem and provides policy-learning frameworks for logged data. Recent work on counterfactual sample identification emphasizes learning action success by comparison with a counterfactual action under the same context, rather than relying only on a direct reward predictor. citeturn824625academia0

For this research, the historical option-path data allow something stronger than ordinary bandit feedback: for a fixed entry opportunity, the research engine can evaluate both CALL and PUT outcomes under the same historical market path. That creates a paired counterfactual margin:

DeltaP&L = P&L(CALL) − P&L(PUT).

This is a much closer target to the actual trading decision than expiry-direction classification.

Relevant literature:
- Counterfactual Sample Identification, 2025: https://arxiv.org/abs/2509.10520
- Counterfactual Risk Minimization, 2015: https://arxiv.org/abs/1502.02362
- Efficient Counterfactual Learning from Bandit Feedback, 2018: https://arxiv.org/abs/1809.03084

## 2. Bayesian dynamic logistic regression and dynamic model averaging

Dynamic Bayesian classification explicitly allows model coefficients and model weights to change over time. A dynamic logistic/DMA framework was developed for streaming binary classification with forgetting and Bayesian model averaging, designed for changing data-generating processes. citeturn640625search3

This is especially relevant because Phase 38 showed a striking 2025-versus-2026 regime reversal. A static classifier can be systematically misaligned when the relationship between predictors and direction changes.

Candidate:
- time-varying logistic coefficients;
- online forgetting;
- dynamic model averaging over a few low-dimensional experts.

## 3. Bayesian online change-point detection

Bayesian Online Changepoint Detection estimates the posterior distribution of the current run length and detects abrupt changes in the data-generating process online. The original method was explicitly motivated by financial and other sequential settings. citeturn738228academia0

A change-point model should be used as a **gate/state variable**, not as a stand-alone direction predictor. The research hypothesis is that model behavior changes after a detected structural break.

## 4. Conformal prediction adapted to time series

Ordinary conformal prediction assumes exchangeability that does not directly hold for dependent time series. Recent work has focused on online/rolling conformal methods and conformal approaches that explicitly account for autocorrelation and change points. citeturn414793academia2turn414793academia3turn414793academia1

Phase 39 will use conformal uncertainty as a selective-trading layer:
- predict a margin/distribution;
- estimate uncertainty sequentially;
- abstain when the confidence interval overlaps zero or the expected economic advantage is too small.

The research goal is not a mathematically decorative interval; it is whether uncertainty-aware abstention improves realized risk-adjusted P&L.

## 5. Nearest-neighbor / analog forecasting

Nearest-neighbor methods are attractive here because the event count is small. A 2024 Journal of Forecasting study proposes weighted nearest-neighbor time-series forecasting methods that search historical subsequences and improve computation through restricted neighbor sets. citeturn640625search0turn640625search1

A related 2024 International Journal of Forecasting study uses dynamic-time-warping similarity and neighborhood averaging to improve forecasts across heterogeneous time series. citeturn640625search4turn640625search9

This motivates:
- Mahalanobis analogs on event features;
- DTW similarity on past-only price/volatility sequences;
- recency-weighted neighbor outcomes;
- regime-aware neighbor selection.

## 6. Context-tree Bayesian mixtures

Context-tree weighting provides a hierarchical Bayesian framework where recent discretized context determines which local time-series model is used. It is designed for limited-data settings, supports exact Bayesian inference, and permits sequential online updates. citeturn807145search5

A lightweight context-tree policy could be particularly suitable for this project because it creates state-conditioned local models without training a large neural network.

## 7. Generalized additive models

Sparse generalized additive models offer an interpretable middle ground between linear models and unrestricted tree interactions. Recent M-GAM work uses sparse additive structure and remains effective with missingness, while IGANN-style methods show how additive shape functions can capture nonlinear effects with controlled complexity. citeturn640625search5turn640625search2

For Phase 39:
- use spline/GAM effects;
- allow only preregistered pairwise interactions;
- compare both direction classification and direct DeltaP&L regression.

## 8. Gaussian-process methods

Gaussian processes are attractive for this problem because the training set is small and the model naturally produces posterior uncertainty. They can be used for:
- DeltaP&L regression;
- probability of CALL superiority;
- uncertainty-aware abstention.

A 2024 IEEE Access study explicitly examines Gaussian-process-based approaches for time-series classification in domains including finance, motivated by uncertainty and stochastic-process structure. citeturn640625search13

The key constraint is that GP kernel complexity must remain low and hyperparameters must be selected chronologically.

## 9. Mixture-of-experts

Recent time-series research continues to use mixture-of-experts to route inputs to different specialist forecasters, including wavelet-based and task-aware MoE architectures. citeturn807145academia2turn807145academia3

For this project, a lightweight MoE is preferable to a large neural MoE:
- specialist = one low-capacity predictor;
- gate = regime/uncertainty/context;
- gate output = expert weights;
- no end-to-end high-dimensional training.

## 10. Time-series foundation models

Recent work suggests time-series foundation models can be useful in data-constrained settings and can work with conformalized uncertainty. citeturn414793academia0

However, this is a lower-priority exploratory track because:
- the local event sample is small;
- external model versions can change;
- zero-shot scalar forecasts may not align with option-spread P&L;
- reproducibility and licensing need to be verified.

Foundation models will therefore be compared only after the simpler methods.

## 11. What is genuinely new in Phase 39

The proposed **Control-Relative Counterfactual Override Learner (CROL)** is the primary novel method.

Rather than ask:

> Will NIFTY expire higher or lower?

CROL asks:

> At this exact entry opportunity, how much better or worse would CALL have performed than PUT, and how confident am I in that estimate?

Then:

1. keep the canonical stateful action by default;
2. estimate the counterfactual incremental value of switching;
3. override only when the posterior/ensemble estimate is positive by a pre-registered margin;
4. abstain when uncertainty is too high;
5. evaluate the resulting policy sequentially with the complete trading engine.

This directly aligns the learning objective with the trading objective.

## 12. Recommended priority order

1. CROL / direct counterfactual DeltaP&L regression.
2. Bayesian Counterfactual Margin Model.
3. Pairwise Bradley-Terry/utility-ranking model.
4. Dynamic Bayesian logistic/DMA.
5. Gaussian-process margin model.
6. Sparse GAM/GA2M.
7. Analog/kNN/DTW model.
8. BOCPD + adaptive expert gate.
9. Online Hedge/DMA expert aggregation.
10. Foundation-model exploratory track.
11. Constrained symbolic regression.

## Literature conclusion

The evidence does not justify another generic neural-network sweep. The strongest research opportunity is to transform the prediction problem from indirect market-direction classification into **counterfactual, action-aware economic policy learning**, with uncertainty and conservative control-relative overrides.
