# Phase 39 Research Plan — Advanced and Counterfactual Direction Prediction

## Purpose

Search beyond the model families already tested through Phase 35 and Phase 38. The goal is not another generic classifier leaderboard. The primary objective is to discover a prediction/policy method that is better aligned with the actual trading decision: choosing between the CALL-side and PUT-side Continuous Delta 6x6 spreads after costs.

Phase 35 already tested XGBoost, LightGBM, CatBoost, ExtraTrees, HistGradientBoosting, DART, NGBoost, quantile trees, BART, wavelet/EMD/VMD/CEEMDAN trees, adaptive trees, dynamic pools, chronological OOF stacking, regime-gated trees, calibration and conformal overlays. Phase 38 showed that the five corrected selectors do not outperform the canonical stateful control.

Phase 39 therefore moves from generic directional classification toward **policy learning, counterfactual spread-value prediction, adaptive Bayesian methods and selective decision-making**.

## Primary research question

Can an action-aware, counterfactual or adaptive prediction method identify when the CALL or PUT Continuous Delta 6x6 spread has the superior post-cost outcome, and thereby improve the canonical stateful strategy without increasing unacceptable drawdown?

## Secondary research questions

1. Does predicting CALL-versus-PUT **spread P&L difference** outperform predicting NIFTY expiry direction?
2. Can a control-relative model identify rare situations where overriding the stateful rule has positive incremental value?
3. Can uncertainty-aware abstention avoid low-confidence direction switches?
4. Can time-varying Bayesian models adapt to regime changes better than static tree models?
5. Can nearest-neighbor/analog methods exploit recurring market states with only ~100–200 independent expiry-level events?
6. Can a simple expert-aggregation policy combine heterogeneous signals better than any single selector?
7. Can change-point/regime detection be used as a gate rather than as the directional predictor itself?

## Candidate method families

### Tier 0 — mandatory new formulation: direct counterfactual spread-value learning

For each eligible entry opportunity, construct the same entry context and evaluate both hypothetical arms under the frozen execution rules:

- CALL spread outcome;
- PUT spread outcome.

Define:

DeltaP&L = net_P&L_CALL − net_P&L_PUT.

The model predicts either:
- sign(DeltaP&L), or
- expected DeltaP&L.

This changes the target from an indirect market-direction label to the actual decision variable.

Important: this fixed-opportunity counterfactual screen is only a prediction study. The final policy must be re-simulated sequentially because the chosen direction can change exit time and therefore future entry availability.

### Tier 1 — Control-Relative Override Learner (CROL)

Invented Phase-39 method.

The canonical stateful control remains the default action.

For every control opportunity:
- identify the control's chosen arm;
- identify the alternative arm;
- construct the counterfactual incremental reward of switching;
- train a model to estimate expected improvement from overriding the control.

Policy:
- retain control when predicted incremental improvement <= 0;
- override only when predicted incremental improvement exceeds a preregistered safety margin and uncertainty is acceptable.

This is deliberately conservative. The research question is whether a model can improve the existing strategy by making a small number of high-quality overrides rather than replacing the control everywhere.

### Tier 1 — Bayesian Counterfactual Margin Model (BCMM)

A robust Bayesian linear/elastic-net model predicts DeltaP&L directly.

Components:
- standardized point-in-time features;
- Bayesian/regularized linear effect;
- Student-t residual option;
- rolling/expanding Bayesian update;
- posterior mean and posterior uncertainty.

Decision score:

utility = posterior_mean(DeltaP&L) − lambda * posterior_sd(DeltaP&L).

Lambda values will be preregistered before holdout and not selected from holdout performance.

### Tier 1 — Pairwise Preference / Bradley-Terry learner

Treat each entry opportunity as a pair:
CALL outcome versus PUT outcome.

Learn P(CALL is superior | context) using a pairwise logistic/Bradley-Terry formulation. This is conceptually closer to a ranking problem than ordinary binary NIFTY direction prediction.

### Tier 1 — Bayesian Dynamic Logistic / Dynamic Model Averaging

Use time-varying coefficients and online forgetting rather than a static classifier.

Candidate:
- dynamic logistic regression;
- dynamic model averaging across a small set of low-dimensional experts;
- posterior predictive weighting updated chronologically.

This is specifically intended to address the 2025-to-2026 regime instability observed in Phase 38.

### Tier 2 — uncertainty-aware nonlinear small-data models

1. Gaussian-process classification/regression with a Matérn/ARD kernel.
2. Robust kernel ridge regression.
3. RBF/SVM classifier with chronological probability calibration.
4. Generalized additive model / sparse GAM.
5. Explainable additive model with restricted pairwise interactions.
6. Huber/quantile regression for DeltaP&L.

These are intentionally low-capacity relative to deep neural networks.

### Tier 2 — analog and local-state methods

1. Recency-weighted k-nearest-neighbour analog forecasting.
2. Mahalanobis-neighbor model.
3. DTW-based analog similarity on past-only NIFTY/volatility trajectories.
4. Nearest-regime expert selection.

Recent literature supports weighted nearest-neighbor time-series forecasting as a viable low-data method; parameter selection will be strictly chronological.

### Tier 2 — regime/change-point methods

1. Bayesian Online Change-Point Detection.
2. Hidden semi-Markov regime model with explicit duration.
3. Change-point-conditioned GAM/Bayesian margin model.
4. Regime-dependent expert weights.

These are gates/state variables, not automatic directional predictors.

### Tier 3 — online expert aggregation

Create a small expert pool:

- canonical stateful control;
- OTM678;
- OTM789;
- CatBoost;
- Markov-tree;
- Wavelet-tree;
- BCMM;
- CROL;
- analog model.

Use only past realized rewards to update expert weights. Candidate algorithms:
- exponential weights/Hedge;
- discounted Hedge;
- Bayesian model averaging;
- dynamic model averaging.

The policy must not use future outcomes and must be re-simulated sequentially.

### Tier 3 — time-series foundation-model exploratory track

Only after the low-capacity models have been tested:

- zero-shot/low-shot time-series foundation forecasts for NIFTY/volatility;
- TimesFM/Chronos-class models where licensing and reproducibility permit;
- convert forecasts into direction, expected move and uncertainty features.

This is an exploratory track, not a primary promotion candidate, because the sample is small and external model changes can complicate reproducibility.

### Tier 4 — symbolic/structural discovery

Use strongly constrained symbolic regression only to discover compact formulas for the counterfactual margin. Complexity penalties and nested chronological validation are mandatory.

No unrestricted genetic-programming sweep.

## Feature/data expansion

The new models will use a frozen point-in-time feature layer. Where available, it should incorporate:

- NIFTY spot returns, range, realized volatility, drawdown and momentum;
- NIFTY option premium/IV/OI/volume/skew/term structure;
- India VIX;
- NIFTY futures basis and volume/OI;
- BANKNIFTY and other major Indian index relationships;
- BSE/NSE cross-sectional breadth and dispersion;
- FII/DII activity;
- global equity-index futures/spot returns;
- USD/INR;
- crude oil and gold;
- major Asian/European/U.S. market lead-lag variables;
- scheduled corporate actions;
- point-in-time news/sentiment variables where timestamp reliability can be proven.

No feature may use information unavailable at the decision timestamp.

## Counterfactual engine design

The engine must create a fixed opportunity ledger first.

For each eligible opportunity:
1. determine the exact entry timestamp;
2. determine the exact spot/options snapshot;
3. create both the CALL and PUT 6x6 spread;
4. apply identical delta-selection and exit rules;
5. apply identical one-tick adverse slippage;
6. apply the same brokerage/statutory/exchange charges;
7. record both net outcomes;
8. calculate DeltaP&L;
9. retain the opportunity timestamp and all point-in-time predictors.

A second sequential-policy engine will then evaluate the learned selector because a different action can cause a different exit time and change later opportunities.

## Statistical methodology

Development:
- through 2023-12-31.

Validation:
- 2024-01-01 through 2025-12-31.

Untouched holdout:
- 2026-01-01 through the frozen available sample end.

Primary metrics:
- control-relative net P&L;
- mean DeltaP&L;
- median DeltaP&L;
- probability of positive incremental P&L;
- paired expiry bootstrap;
- sign-flip permutation;
- maximum drawdown;
- profit factor;
- win/loss rate;
- calibration/Brier/log loss where probabilistic;
- decision-curve/abstention diagnostics.

For regression:
- MAE/RMSE;
- pinball loss;
- CRPS where a full predictive distribution is available.

For uncertainty:
- rolling conformalized intervals;
- coverage and interval width;
- calibration by volatility regime.

For sequential policy:
- exact trade chronology;
- no overlapping positions;
- no future state information;
- full transaction-cost model.

## Multiple-comparison discipline

The candidate set will be fixed before holdout evaluation.

The research will use:
- a small Tier-1 set;
- a predefined Tier-2 set;
- a limited exploratory Tier-3 set.

No candidate will be repeatedly redesigned based on holdout results.

If more than one candidate passes, selection will be based on a preregistered composite:
1. positive control-relative validation;
2. positive untouched holdout;
3. positive paired common-expiry bootstrap tendency;
4. lower/equivalent drawdown;
5. adequate calibration;
6. no severe CALL/PUT asymmetry;
7. robustness to +50% costs and adverse slippage stress.

## Novel primary hypothesis

H1: predicting the **counterfactual economic margin between the two tradable spreads**, rather than predicting NIFTY direction, can identify profitable overrides of the canonical stateful policy that are invisible to standard directional classifiers.

H2: a conservative control-relative policy that abstains except when posterior expected incremental P&L is sufficiently positive can improve return-to-drawdown without materially reducing the control's win rate.

## Stop condition

Phase 39 stops after the fixed candidate families have been implemented, evaluated chronologically, stress-tested and subjected to the promotion gate.

It does not expand endlessly into arbitrary architectures.

## Deliverables

- literature review;
- preregistration;
- counterfactual opportunity ledger;
- model prediction tables;
- sequential policy trades;
- bootstrap/permutation results;
- calibration and uncertainty diagnostics;
- risk-adjusted comparison;
- figures and tables;
- complete Phase-39 manuscript;
- promotion/rejection decision;
- updated README, research log and error log.

## Branch and governance

Branch: phase-39-advanced-direction-models

All numerical workflows must support automatic push execution and manual workflow dispatch.

No Phase-39 result can replace the Phase-38 canonical decision without passing the full promotion gate.
