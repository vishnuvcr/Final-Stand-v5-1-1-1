# Phase 39 Pre-Registration — Advanced Counterfactual and Adaptive Direction Prediction

## Frozen benchmark

The canonical trading benchmark is the Phase-38 frozen Phase-32 stateful control:

- initial direction = CALL;
- winning trade -> retain;
- losing trade -> flip;
- zero -> retain;
- 6x6 NIFTY vertical;
- 50-point width;
- six lots per leg;
- same delta entry/exit thresholds;
- same one-tick adverse slippage;
- same brokerage/statutory/exchange charges;
- same chronological non-overlap;
- same historical lot-size schedule.

The control artifact must be loaded from the frozen Phase-38 cache and not regenerated as a substitute.

## Core data units

Two datasets will be maintained separately:

### A. Fixed opportunity dataset

Each row is a candidate entry opportunity. The entry timestamp is fixed before action selection.

For that exact opportunity, the engine computes both counterfactual arms:
- CALL net P&L;
- PUT net P&L.

Primary economic target:

DeltaP&L = CALL_net − PUT_net.

No action is assumed to have been selected when constructing this fixed-opportunity label.

### B. Sequential policy dataset

A learned policy is then re-run through the complete chronological engine. Its selected arm determines the realized exit timestamp and therefore the future entry opportunity. This second simulation is the only dataset used for final trading-policy claims.

## Primary candidate: CROL

Control-Relative Counterfactual Override Learner.

Default:
- take the canonical control action.

Override:
- only when predicted incremental P&L of the alternative action is positive and exceeds the preregistered safety margin.

The initial registered margin grid is fixed:
- ₹0;
- ₹250;
- ₹500.

These thresholds are evaluated on development/validation according to the phase design and then frozen before the untouched holdout.

No threshold may be selected on 2026 holdout data.

## Primary predictive models

1. Bayesian/regularized DeltaP&L regression.
2. Huber/Elastic-Net DeltaP&L regression.
3. Gaussian-process DeltaP&L regression.
4. Sparse GAM/GA2M DeltaP&L model.
5. Pairwise Bradley-Terry preference model.
6. Dynamic Bayesian logistic regression / dynamic model averaging.
7. Recency-weighted kNN/analog model.
8. BOCPD-gated local model.

## Secondary expert pool

For online aggregation only:
- canonical stateful control;
- OTM678;
- OTM789;
- CATBOOST;
- MARKOV_REGIME_TREE;
- WAVELET_TREE;
- OOF_STACK;
- DART;
- best CROL candidate.

Expert weights may depend only on information available before the next decision.

## Training protocol

Development:
- through 2023-12-31.

Validation:
- 2024-01-01 through 2025-12-31.

Untouched holdout:
- 2026-01-01 through the frozen available sample end.

Allowed training schemes:
- expanding window;
- fixed 52-event rolling window where preregistered;
- exponential forgetting with preregistered decay.

Forbidden:
- random train/test splits;
- random k-fold;
- holdout tuning;
- feature selection using holdout;
- retrospective threshold tuning;
- use of future P&L in any decision feature.

## Primary success endpoint

A candidate succeeds only if the final sequential policy:

1. has positive net P&L after all recorded costs;
2. has positive incremental P&L versus the frozen stateful control;
3. has positive 2026 holdout incremental P&L;
4. has control-relative 95% paired-expiry evidence that does not materially favor the control;
5. survives +50% cost stress;
6. does not materially worsen maximum drawdown;
7. has no severe unexplained CALL/PUT asymmetry;
8. shows no information leakage;
9. remains stable across major volatility/regime subperiods.

## Statistical tests

Primary:
- common-expiry paired bootstrap, 10,000 deterministic resamples.

Secondary:
- paired sign-flip permutation;
- mean/median DeltaP&L;
- win/loss rate;
- profit factor;
- maximum drawdown;
- net-P&L/max-drawdown diagnostic;
- Brier/log loss/AUC when probabilistic;
- calibration curves;
- conformal coverage and width;
- regression MAE/RMSE/pinball loss;
- regime/subperiod stability.

For model families with many close variants, report the complete preregistered family rather than selectively reporting the best result.

## Economic stress

At minimum:
- base cost model;
- +25% costs;
- +50% costs;
- +100% costs;
- +1, +2 and +3 slippage ticks where the historical data permit;
- conservative fill haircut where bid/ask information exists.

## Novelty requirement

The primary CROL model must not be reduced to an ordinary directional classifier. It must learn the economic margin between the two available actions and be evaluated first on fixed opportunities and then as a sequential policy.

## Stop rule

After the registered candidate families and stress tests are complete, freeze the phase and issue a promotion/rejection decision. New model families require a new phase.
