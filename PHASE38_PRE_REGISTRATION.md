# Phase 38 Pre-Registration — Control-Relative Robustness

The Phase-37 corrected polarity is frozen. Phase 38 does not change model predictions or execution rules.

The canonical stateful control is the accepted/frozen Phase-32 result with initial CALL direction and win-retain/loss-flip/zero-retain transitions. The frozen comparator artifact is cached under `results/phase38_corrected_model_robustness/frozen_control_*`. A fresh Phase-32 reconstruction is audit-only; if it differs from the frozen artifact, the frozen comparator remains authoritative and the discrepancy must be logged.

Primary statistical test: common-expiry paired selector-minus-control P&L bootstrap, 10,000 deterministic resamples.

Secondary tests: yearly/holdout splits, drawdown/PF, +25/+50/+100% transaction-cost stress, direction asymmetry.

No threshold, model, feature, polarity or execution parameter may be tuned using Phase-38 outcomes.
