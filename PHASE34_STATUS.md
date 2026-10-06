# Phase 34 Status — Alternative NIFTY D−6 Prediction Models

## Current state
**IMPLEMENTATION REGISTERED — NUMERICAL RUN PENDING**

### Step 1 — repository audit — COMPLETE
Phase 33 is closed with no promotion. Phase 20 remains canonical. Phase 33 cache and point-in-time event construction are reused rather than re-downloaded.

### Step 2 — isolated branch — COMPLETE
Branch: `phase-34-alternative-nifty-prediction-models`

### Step 3 — literature/model-family screen — COMPLETE
Selected additional families:
- XGBoost
- ExtraTrees
- HistGradientBoosting
- RBF-SVM
- Elastic-Net Logistic Regression
- point-in-time HMM regime probability model
- compact Transformer encoder
- compact temporal-convolution model

### Step 4 — preregistration — COMPLETE
The model parameters, split, targets and promotion gates are frozen in PHASE34_PRE_REGISTRATION.md.

### Step 5 — implementation — IN PROGRESS
The Phase-34 script reuses the Phase-33 cached event and daily datasets and adds no new model-selection loop.

### Accepted evidence
None yet. A successful, persisted GitHub Actions run is required before any numerical conclusion is accepted.

### Next step
Run the Phase-34 GitHub Actions workflow, inspect all errors, reconcile artifacts if the persistence step races, then generate the final statistical summary and manuscript.

### Canonical decision
Until this phase passes all preregistered gates, **Phase 20 remains canonical**.
