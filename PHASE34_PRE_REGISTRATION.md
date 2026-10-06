# Phase 34 Pre-registration — Alternative NIFTY Prediction Models

Registered objective: test only the eight model families and two fixed ensembles specified in PHASE34_RESEARCH_PLAN.md at the locked D−6 / 10:00 IST reference.

No model-specific parameter tuning will be performed after seeing validation results. Holdout observations from 2026 are untouched until the final scoring run.

Primary comparison set:
- constant-rate baseline
- always-up
- always-down
- Phase-33 Random Forest control
- Phase-34 A1–A8
- NEW_EQUAL_8
- TREE_EQUAL_3

Primary success criterion:
A model must improve out-of-sample directional performance and economic signed-return diagnostics versus simple baselines, with no evidence of calibration collapse. Trading promotion requires a separate frozen overlay phase with explicit Paytm Money costs and slippage.

Sequence-model target:
forecast expiry-horizon log return from the 30 most recent completed NIFTY sessions before the reference timestamp.

HMM target:
estimate the probability of a positive expiry-horizon return from the current latent state and pre-reference state-conditional historical horizon returns.

All failed workflow runs, implementation errors and corrections must be logged in ERROR_LOG.md. Earlier Phase-34 numerical runs are non-evidence until the corrected final run is explicitly marked accepted.
