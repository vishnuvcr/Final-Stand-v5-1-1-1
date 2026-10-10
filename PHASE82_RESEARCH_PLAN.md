# Phase 82 — Expiry-clustered inference and promotion gate
Date: 2026-10-10
Status: FROZEN BEFORE INFERENCE RUN

## Research question
Do any Phase 81 structure/window results show a statistically credible positive net outcome after modeled Paytm Money costs and one-/two-tick adverse slippage, and is the difference between intraday and overnight exposure stable across expiry clusters?

## Hypothesis families
Phase 81 tested ten fixed structure variants and two registered friction assumptions. Phase 82 will assess a fixed family of 60 validation hypotheses:
1. 20 net-outcome hypotheses: ten structures × two holding windows, each under one-tick and two-tick costs (H1: mean expiry-cluster net result > 0).
2. 20 additional? The family is defined as 10 structures × 2 windows × 2 friction assumptions = 40 net-outcome hypotheses.
3. 20 horizon contrasts: ten structures × two friction assumptions (H1/H0 two-sided difference in net return between overnight and intraday).
Total confirmatory family: 60 tests. Holm step-down correction is applied jointly across all 60 validation p-values. Development results are diagnostic only and do not enter candidate ranking or confirmatory p-value adjustment.

## Data and temporal boundary
- Read only frozen Phase 81 derived outputs for dates through 2025-12-31.
- Validate that neither trade ledger nor paired-difference input contains any 2026 date or non-DEV/VAL split.
- Development through 2023-12-31 is descriptive.
- Validation 2024-01-01 to 2025-12-31 is the only confirmatory split in this phase.
- Do not download/load/score 2026 expiry option data unless an eligible defined-risk candidate first passes this phase's pre-registered gates. If no candidate passes, holdout remains sealed and research proceeds to final manuscript.

## Inferential method
- Cluster on listed expiry to account for dependence among daily trades sharing one expiry cycle.
- Compute each expiry's mean return/difference and use equal-weighted expiry-cluster mean as the estimand.
- Confidence intervals: 20,000-resample percentile bootstrap over expiry clusters, fixed seed 820026.
- Net profitability tests: one-sided cluster-mean t-test against zero, H1 positive net expectancy. Paired horizon differences: two-sided cluster-mean t-test against zero.
- Apply Holm adjustment over all 60 validation tests. Report raw p-value, adjusted p-value, number of trades, number of expiry clusters, mean and median, total net P&L, 95% cluster-bootstrap interval, win rate, and one-/two-tick sensitivity.
- Do not treat this as replication of Bhat et al. (2024): their result is delta-hedged; this test studies static option structures.
- No model tuning, new strategies, new indicator thresholds, or post-result sample changes are allowed.

## Promotion / holdout gate
A strategy can be nominated for a later holdout phase only if all apply:
1. Defined-risk strategy (the naked short ATM straddle is explicitly ineligible).
2. At least 100 complete trades across at least 50 expiry clusters in validation.
3. Positive total net P&L in validation at two-tick stress.
4. Positive lower 95% expiry-cluster bootstrap bound for two-tick mean net expectancy.
5. Holm-adjusted p < 0.05 for the two-tick profitability test across the full 60-test family.
6. No source, coverage, contract identity or execution-model integrity failure.

If no candidate passes, do not open the 2026 holdout. Report NO-GO and proceed to Phase 83 manuscript closeout. A positive total in a single cell or a naked option seller is not a promotion.

## Outputs
- Cluster-inference results and Holm-adjusted testing ledger.
- Development descriptive table and validation inference report.
- Plots for horizon effects and per-strategy net P&L.
- Candidate gate decision, phase status, error log, research log and README links.
- No raw OHLC prices copied; the input is already-derived Phase 81 data on the branch.

## Finite stop
Phase 82 is one inference pass with no parameter expansion. If no eligible candidate passes, Phase 83 prepares the complete manuscript (with figures/tables/appendix/limitations) and ends the registered research programme.