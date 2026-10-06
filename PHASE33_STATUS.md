# Phase 33 Status — NIFTY Prediction Models

## Current state
**COMPLETE — NO PROMOTION.**

### Step 1 — repository audit — COMPLETE
- Audited main README, research log, error log and dynamic-n research plan.
- Audited Phase-32 research plan, pre-registration, status, strategy specification and accepted result.
- Confirmed Phase 32 is frozen as historical evidence and will not be silently modified.
- Confirmed no existing project artifact records a Phase-33 prediction-model study.

### Step 2 — isolated branch — COMPLETE
- Created phase-33-nifty-prediction-models from main.
- All Phase-33 artifacts are isolated on this branch.

### Step 3 — research registration — COMPLETE
- Added Phase-33 research plan and pre-registration.
- Locked D−6 calendar-day / 10:00 IST reference.
- Locked expiry-close target and chronological train/validation/holdout split.
- Locked requested model families and an equal-weight ensemble.

### Numerical execution
**GITHUB ACTIONS RUN #1 IN PROGRESS — numerical execution underway.**

### Errors
No numerical evidence has been accepted and no failed run has been used as research evidence.

### Next step
Build the compact point-in-time dataset, run leakage/coverage audit, then execute M1–M5 through the Phase-33 GitHub Actions workflow.


### Step 4 — model implementation — COMPLETE
- Added the cached point-in-time NIFTY event engine.
- Added price/volatility, cross-market, option-chain, sentiment and FII/DII feature families with backward-only joins.
- Added LSTM, Random Forest, SOFNN-inspired fuzzy classifier, GARCH/EGARCH/GJR-GARCH volatility models and fixed equal-weight ensemble.
- Added explicit sentiment-model subtrack using 2024 development, 2025 validation and 2026 holdout because the selected Indian sentiment source begins in January 2024.
- Added manual and push-triggered GitHub Actions workflow.

### Step 5 — numerical run
- Workflow run #1: 37420357853.
- Current state at registration checkpoint: in progress.
- Accepted evidence remains empty until the run succeeds and artifacts are persisted.


### Step 6 — LSTM lookback audit — CORRECTED
- Code review found the first implementation used prior D−6 expiry events rather than 30 completed NIFTY trading sessions.
- No numerical result from runs before this correction is accepted.
- Corrected the LSTM to use the 30 most recent completed NIFTY trading sessions strictly before each D−6 reference date.
- Corrected commit: 6bb06e263b0c46da9510d40c7effc5d93c2c0f1e.

### Step 7 — corrected numerical run #11 — COMPUTATION SUCCESS / EVIDENCE PROVISIONAL
- Run #11 completed model computation successfully after the exact-timestamp correction.
- 245 events: 128 development, 95 validation, 22 2026 holdout.
- Preliminary direction results: RF validation accuracy 54.74%; RF 2026 holdout 54.55%; equal-weight ensemble 2026 holdout 59.09%.
- The 2026 holdout always-down baseline is 63.64%, so the preliminary models did not beat the simple downside baseline on accuracy.
- The preliminary GARCH run is not final because EGARCH multi-step analytic forecasts were unsupported and therefore omitted from the family average.
- The artifact is retained, but final conclusions await the corrected EGARCH simulation run.
- Run #11 numerical artifact: 11392817248.


### Step 8 — verified artifact reconciliation — COMPLETE
- Corrected Phase-33 run #13 artifact has been reconciled into the branch: cached NIFTY, sentiment, global, FII/DII and event datasets plus model result tables.
- Postprocessing automation is being triggered from this status update after its branch-expression correction.


### Step 9 — postprocess automation correction — COMPLETE
- Postprocess checkout failed because the action constructed an invalid wildcard refspec.
- The checkout step is now pinned directly to phase-33-nifty-prediction-models with fetch-depth 1.

- Postprocess run #2 failed inside statistics code because numpy.where already returned an ndarray and the script called .to_numpy(). Corrected in 2fc43d3db44a06743850ec6b339bd402bbecfd3c.

### Step 10 — corrected postprocessing — COMPLETE
- Final postprocessing run succeeded: GitHub Actions run #4 (37422362350).
- Final statistical tables, yearly stability, decision table, GARCH summary, figures and manuscript were generated and persisted.
- Final evidence set = corrected run #13 artifact + successful postprocessing; superseded runs are not used.
- Sample: 245 eligible events = 128 development, 95 validation, 22 untouched 2026 holdout.
- Validation: Random Forest is best among full models by accuracy/log loss (54.74% accuracy; 0.6851 log loss).
- 2026 holdout: equal-weight ensemble has highest full-model accuracy at 59.09%, but the always-down baseline is 63.64%; RF has best holdout log loss at 0.6562.
- All model signed-return bootstrap 95% intervals include zero.
- GARCH-family forecast correlation with realized absolute return is only 0.0658; QLIKE is 66,548.975.
- Decision: **do not promote any Phase-33 model to trading.** Phase 20 remains canonical.
- A future direction-overlay test, if desired, must be a separately registered phase with full Paytm Money brokerage/statutory-cost/slippage/execution modeling.
