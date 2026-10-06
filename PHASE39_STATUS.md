# Phase 39 Status — Advanced and Counterfactual Direction Prediction

**STEP 1 COMPLETE — FIXED-OPPORTUNITY COUNTERFACTUAL PANEL ACCEPTED; MODEL FITTING NEXT**

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

- Branch: phase-39-advanced-direction-models
- Research plan: committed and unchanged
- Literature review: committed
- Pre-registration: committed
- Candidate-method registry: committed
- **Step 1: COMPLETE / ACCEPTED**
- Fixed-opportunity panel: 477 trades / 237 expiry observations
- Development: 271 trades / 135 expiries
- Validation: 172 trades / 82 expiries
- Untouched holdout: 34 trades / 20 expiries
- Frozen validation + holdout control: **₹63,672.5753**
- Maximum per-trade control reconstruction error: **< 2e-12 rupees**
- Numerical result: **both CALL and PUT outcomes are now available for every accepted opportunity**
- Strategy promotion: **not permitted yet**
- Phase-38 canonical stateful strategy remains unchanged and authoritative

## Step 1 conclusion

The fixed-opportunity dataset provides a valid economic target for model training: `DeltaP&L = CALL_net - PUT_net`.

A useful new finding is visible before any model fitting, but it is **not a model result**:
- development mean DeltaP&L = **-₹320.53**;
- validation mean DeltaP&L = **+₹386.77**;
- 2026 holdout mean DeltaP&L = **+₹3,386.31**;
- CALL beats PUT on **270/477** opportunities (56.6%);
- the holdout alone has CALL beating PUT on **27/34** opportunities (79.4%).

The control reconstruction is effectively exact, so these are counterfactual opportunity-level observations rather than control-rebuild artifacts. The regime reversal between development and 2024–2026 strengthens the preregistered case for adaptive/uncertainty-aware models rather than a static direction classifier.

## Step 2 — point-in-time feature matrix — COMPLETE / ACCEPTED

- 477 unique entry opportunities.
- 122 numeric feature columns in the Step-2 matrix.
- Leakage audit PASS.
- Exact-entry option data used without forward fill/interpolation.
- Global/daily sources use strictly previous available session/date.
- Development-only feature eligibility is enforced in the Step-3 model runner.
- Known unavailable supplemental sources remain documented: NSE/BSE breadth, NIFTY futures basis/OI/volume, point-in-time corporate-action feed, timestamp-verified intraday news.

## Step 3 — economic-margin fixed-opportunity model screen — COMPLETE / CORRECTED

The first Step-3 run was rejected because realized CALL/PUT P&L columns leaked into the predictor set. The leak-free rerun is the only accepted evidence.

Accepted models:
- CROL / Bayesian margin
- Bayesian counterfactual margin
- Bradley-Terry
- Dynamic Bayesian-style logistic
- Gaussian process
- Sparse GAM
- weighted kNN

Accepted leak-free validation result:
- Sparse GAM, ₹500 override margin, uncertainty multiplier 1.0.
- Validation fixed-opportunity uplift: **+₹11,609.60**.
- Paired-expiry bootstrap 95% interval for total uplift: approximately **−₹1,250 to +₹36,079**.
- Only 2 validation overrides.
- Other registered models produced zero validation overrides at their selected safety margins.

The Step-3 model results are screening evidence only. No holdout was used to select the model.

## Step 4 — sequential policy replay — COMPLETE / AUDITED

Selected fixed-opportunity candidate:
- Sparse GAM economic-margin model.
- Safety margin = ₹500.
- Uncertainty penalty = 1.0 × predictive uncertainty.
- Canonical stateful control remains the default action.

Corrected sequential results:
- Total policy trades: **479**.
- Overrides: **7**.
- Validation uplift: **+₹17,983.53**.
- 2026 holdout uplift: **+₹7,390.39**.
- Validation maximum drawdown: **₹32,021.65**, identical to control ₹32,021.65.
- 2026 holdout maximum drawdown: **₹29,936.24**, versus control ₹37,326.63.
- +50% cost-stress uplift: **+₹17,799.05 validation / +₹7,546.34 holdout**.
- +100% cost-stress uplift: **+₹17,614.56 validation / +₹7,702.28 holdout**.

Override concentration:
- 2022 development: 3 overrides, net negative contribution.
- June 2024 validation: 3 overrides, all profitable.
- March 2026 holdout: 1 override, profitable.

The complete chronology/state/cost audit passes. However, this candidate is **NOT PROMOTED**:
1. development-period incremental P&L is **−₹18,175.07**;
2. only 7 overrides exist, so the positive OOS effect is fragile;
3. the paired-expiry evidence is positive but not strong enough to establish a durable effect;
4. other preregistered Phase-39 model families remain untested;
5. final promotion still requires the complete family comparison and stress screen.

The 2026 holdout remains frozen for model selection.

## Step 5 — advanced analog/regime screen — COMPLETE / NO NEW WINNER

Registered advanced methods tested:
- DTW analog margin model.
- RBF/SVR economic-margin regression.
- BOCPD-gated Sparse-GAM economic-margin model.

Accepted fixed-opportunity results:
- DTW: no validation overrides; validation uplift ~₹0.
- SVR: no validation overrides; validation uplift ~₹0.
- BOCPD-GAM: 2 validation overrides and **+₹11,609.60** validation uplift, exactly matching the Sparse-GAM fixed-opportunity screen; paired-expiry 95% interval **−₹1,250.46 to +₹36,079.27**.

Decision:
- No new Step-5 method supersedes Sparse-GAM.
- 2026 holdout was not touched.
- The BOCPD result is treated as a redundant regime-gated representation of the same Sparse-GAM economic signal, not independent confirmation.

## Next engineering step

Build the point-in-time feature matrix and leakage audit. Then fit the preregistered CROL/BCMM/Bradley-Terry/Dynamic-Bayesian and low-capacity nonlinear models chronologically, with the 2026 holdout frozen until the model family and override thresholds are locked.


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
