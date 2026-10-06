# Phase 38 Research Plan — Corrected Model Robustness vs Stateful Control

## Purpose
Determine whether the Phase-37 corrected predictive selectors are genuinely superior or merely positive in isolation.

## Primary question
Do the corrected model selectors improve post-cost performance relative to the canonical Phase-32 stateful direction rule on identical available expiries?

## Registered treatments
- CATBOOST
- MARKOV_REGIME_TREE
- WAVELET_TREE
- OOF_STACK
- DART

## Canonical control
The accepted Phase-32 stateful result is treated as a **frozen comparator artifact** for Phase 38:
- 206 trades;
- net +₹63,672.58;
- 102 expiry blocks;
- source artifact SHA-256 `f98fc6e38e84bdfab09aeeffc2df333da1a3060d3756b1ab12b7e8cb5f32435f`;
- expiry-level P&L is cached in `results/phase38_corrected_model_robustness/frozen_control_expiry.csv`.
The Phase-32 state machine remains the scientific definition of the control. A fresh reconstruction is run for audit, but any mismatch with the frozen artifact is logged and the frozen comparator is retained for treatment comparison.

## Frozen execution
Same Phase-32/37 NIFTY 50 6x6 strategy:
- 6 lots/leg;
- 50-point vertical;
- short leg nearest ±0.25 delta;
- exits at ±0.50 or ±0.04;
- 09:20 first entry;
- 15:28 last entry;
- no expiry-day new entry;
- chronological non-overlap;
- same adverse one-tick option-price slippage;
- same brokerage/statutory charges;
- same historical lot-size schedule.

## Statistical analysis
1. Aggregate selector and control net P&L by expiry.
2. Pair selector minus control on common expiry blocks.
3. Bootstrap common-expiry differences with 10,000 deterministic resamples.
4. Report mean, median, 2.5/97.5 percentiles, probability selector > control, and observed win rate of expiry blocks.
5. Evaluate 2024, 2025 and 2026 separately.
6. Compare maximum drawdown and profit factor.
7. Run cost sensitivity by increasing recorded transaction costs by +25%, +50%, +100%.
8. Do not retune any selector or threshold.

## Promotion gate
A selector can advance only if:
- positive post-cost full sample;
- positive 2026 holdout;
- bootstrap does not materially favor the control;
- performance survives at least +50% cost stress;
- no severe direction asymmetry unexplained by the research;
- no evidence of leakage.

## Output
Complete manuscript, paired-bootstrap table, cost-stress table, selector rankings and Phase-39 recommendation.
