# Phase 82 — Expiry-cluster inference and candidate gate
Date: 2026-10-10
Status: FROZEN BEFORE INFERENCE

## Research question
After clustering paired observations by expiry and correcting for the registered family of tests, is overnight net P&L statistically different from intraday net P&L for any of the ten Phase 81 structure templates? Does any defined-risk structure/horizon remain net-positive in both development and validation under both friction settings?

## Input and scope
- Read only derived aggregate files already persisted by Phase 81: `results/phase81_intraday_overnight/paired_window_differences.csv` and `summary_by_split_variant_window.csv`.
- Do not load or download raw option prices or any 2026 holdout file.
- Ten variants and two registered splits (development through 2023-12-31; validation 2024-01-01 through 2025-12-31) form 20 primary tests.
- Primary outcome: overnight minus intraday net P&L per paired date×variant under one-tick adverse slippage.
- Two-tick sensitivity is summarized as a robustness case, not counted as another primary hypothesis family.

## Statistical methods
1. Reconcile required fields and reject duplicated date/expiry/split/variant rows rather than silently deduplicating.
2. Use expiry as the resampling and dependence cluster.
3. Report the mean and median paired effect, number of paired observations and expiry clusters, fraction of positive expiry-cluster means, CR1 expiry-cluster-robust standard error and t test with G−1 degrees of freedom.
4. Generate 10,000 expiry-cluster bootstrap resamples with frozen seed 820102 and report percentile 95% confidence intervals.
5. Apply Holm step-down family-wise error correction across all 20 primary tests, using two-sided raw p-values.
6. Report two-tick mean, median, bootstrap interval and diagnostic p-value separately; primary decision-making uses one-tick p-values with Holm correction.
7. Distinguish a statistically different horizon from profitable absolute returns; neither a low p-value nor a positive paired difference is sufficient to qualify a strategy.

## Frozen candidate gate and holdout protection
- The short ATM straddle is excluded from candidate eligibility because its risk is unbounded.
- A candidate must be a defined-risk variant paired with one fixed horizon (intraday or overnight); that same horizon must have positive aggregate net P&L in both DEV and VAL under one-tick and two-tick costs.
- The candidate's paired-window effect must favor its chosen horizon and meet Holm-adjusted alpha 0.05 in both DEV and VAL before considering the 2026 sealed holdout.
- If no candidate passes, do not load the holdout. Complete the statistical inference, document the no-go, and proceed to Phase 83 manuscript/terminal research closeout.
- No retuning, new structure additions, or changing the registered windows are permitted in this phase.

## Known limits
- Phase 81 uses option candle opens plus modeled slippage/fees, not historical bid/ask/depth. Results are not proof of executable fills.
- Expiry clustering handles within-expiry dependence but cannot guarantee independence between adjacent expiries or calendar sessions.
- The underlying dataset has a noncommercial license; raw rows must not be copied to the repository.
- No result from this phase alone can authorize live trading.

## Deliverables
- `results/phase82_expiry_cluster_inference/cluster_inference.csv`
- `results/phase82_expiry_cluster_inference/candidate_gate.csv`
- `results/phase82_expiry_cluster_inference/summary.json`
- `results/phase82_expiry_cluster_inference/report.md`
- Updated status, error log, research log and README checkpoint.
