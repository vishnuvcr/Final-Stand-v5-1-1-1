# Phase 39 Status — Advanced and Counterfactual Direction Prediction

**INITIALIZED — LITERATURE/FORMULATION COMPLETE; NUMERICAL ENGINEERING IN PROGRESS**

## Why Phase 39 exists

Phase 35 already exhaustively screened a broad conventional model family:
- XGBoost/LightGBM/CatBoost/ExtraTrees/HistGB/DART;
- NGBoost/BART/quantile trees;
- wavelet/EMD/VMD/CEEMDAN hybrids;
- adaptive rolling/EW models;
- dynamic pools and chronological OOF stacks;
- calibration/conformal methods;
- regime-gated trees.

Phase 38 then showed that the corrected five model selectors do not outperform the canonical stateful control.

Therefore Phase 39 is **not another classifier sweep**.

## New central hypothesis

The prediction target itself may be wrong for the trading decision.

Instead of predicting:

> Is NIFTY's expiry return positive?

Phase 39 will ask:

> At this exact entry opportunity, what is the post-cost expected advantage of CALL spread versus PUT spread?

This creates an economic counterfactual margin:

DeltaP&L = CALL_net_P&L − PUT_net_P&L.

## Invented primary method

### Control-Relative Counterfactual Override Learner (CROL)

The canonical stateful strategy remains the default.

A model estimates the incremental P&L from switching to the alternative direction.

The policy changes direction only when:
- predicted incremental P&L is positive;
- the predicted advantage exceeds the preregistered safety margin;
- uncertainty is sufficiently low.

This is intentionally a conservative **override policy**, not a replacement classifier.

## Other new candidate families

- Bayesian counterfactual margin regression;
- Bradley-Terry/pairwise preference learning;
- dynamic Bayesian logistic regression and dynamic model averaging;
- Gaussian-process economic-margin prediction;
- sparse GAM/GA2M;
- weighted kNN/DTW analog forecasting;
- Bayesian online change-point detection as a regime gate;
- online Hedge/Bayesian expert aggregation;
- constrained symbolic regression;
- time-series foundation models as a lower-priority exploratory track.

## Literature review findings

Recent work supports several components of the design:
- counterfactual offline contextual-bandit/policy learning;
- dynamic Bayesian classification with forgetting/model averaging;
- online conformal methods for dependent time series;
- change-point-aware conformal inference;
- weighted nearest-neighbor time-series forecasting;
- sparse generalized additive models;
- Bayesian context-tree mixtures;
- lightweight mixture-of-experts.

The literature review and sources are recorded in PHASE39_LITERATURE_REVIEW.md.

## Registered data design

Two separate datasets will be maintained:

1. Fixed opportunity dataset — both hypothetical CALL and PUT outcomes calculated for the same historical entry opportunity.
2. Sequential policy dataset — the learned policy is replayed chronologically, allowing its chosen exit time to determine future entry availability.

Only the second dataset can support a final trading-policy claim.

## Current status

- Branch created: phase-39-advanced-direction-models
- Research plan: committed
- Literature review: committed
- Pre-registration: committed
- Candidate-method registry: committed
- Numerical results: **none accepted yet**
- Phase-38 canonical strategy remains unchanged

## Next engineering step

Build the fixed-opportunity counterfactual engine and validate it against the frozen control before any model is trained.


## Step 1 — fixed-opportunity counterfactual engine

**CORRECTED IMPLEMENTATION — rerun required before model training.** The first 206-opportunity calculation reproduced the frozen control essentially exactly, but it was correctly rejected as insufficient for the preregistered 2021–2023 development split. The engine has now been corrected to use 271 development trades from the accepted Phase-32 artifact plus the exact frozen 206-trade validation/holdout panel, and to apply deterministic stable duplicate-quote handling.

The accepted panel is therefore:
- Development: 271 trades / 135 expiries (2021-05-27 through 2023-12-28)
- Validation: 172 trades (2024-01-11 through 2025-12-30)
- Holdout: 34 trades (2026-01-06 through 2026-05-19)
- Intentionally excluded: the 2024-01-04 trade, preserving the exact Phase-38 benchmark

The complete corrected counterfactual engine must re-run before any model training is accepted. The control arm must still reconstruct the frozen ₹63,672.5753 benchmark within the preregistered tolerance.


## Current execution state — 2026-10-06

The corrected Step-1 implementation is committed and automatically queued in GitHub Actions with serialized execution. The research is **not yet allowed to advance to model fitting**: the corrected 271/172/34 counterfactual panel must first pass the full control-reconstruction audit. The earlier 206-row counterfactual result remains exploratory only and is explicitly superseded.


## Step 1 audit checkpoint — 2026-10-06

The frozen Phase-32 strategy specification confirms that the Phase-39 fixed-opportunity engine uses the correct state-independent spread mechanics for both arms: +0.25/-0.25 entry delta selection, 50-point vertical width, six lots per leg, and first short-leg delta hit at 0.50 or 0.04 magnitude, followed by contract termination when no delta exit occurs.

The latest known Step-1 run was cancelled before producing accepted evidence. A status-only commit also did not match the workflow path filter. No model training is permitted yet.

The next trigger will include explicit panel invariants:
- exactly 271 development, 172 validation and 34 holdout rows;
- no accidental 2024-01-04 opportunity in the frozen comparator;
- deterministic timestamp ordering for first-hit exit detection;
- exact frozen-control P&L reconstruction within 0.75 rupees per trade and the authoritative ₹63,672.5753 aggregate.


## Step 1 numerical result checkpoint — 2026-10-06

The audited engine itself completed on run 37437767581 with the corrected 271/172/34 panel:
- Development: 271 rows / 135 expiries; control ₹17,657.15
- Validation: 172 rows / 82 expiries; control ₹63,948.22
- Holdout: 34 rows / 20 expiries; control -₹275.65
- Frozen validation+holdout control: ₹63,672.5753
- Maximum control reconstruction error: <2e-12 rupees across the accepted panel.

The run is not yet accepted as Step-1 CI evidence because the workflow verification used exact float equality for one aggregate-sum assertion. The calculation itself passed its substantive checks. A verification-only workflow correction is being applied; no research parameter or dataset rule is changing.
