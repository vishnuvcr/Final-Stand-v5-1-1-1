# Phase 40 Pre-registration

## Combination universe
All 2^6 - 1 = 63 non-empty subsets of:
CATBOOST, DART, WAVELET_TREE, OOF_STACK, MARKOV_REGIME_TREE, VIX.

## Aggregators
1. Arithmetic mean probability.
2. Median probability.
3. Majority vote.
4. Confidence-weighted probability with fixed weights proportional to |p-0.5|.

No learned weights are fit from validation or holdout.

## VIX modes
1. OFF.
2. VIX expert: prior-session VIX fall beyond a development-derived threshold => bullish; rise beyond threshold => bearish; otherwise neutral.
3. HIGH-REGIME gate.
4. LOW-REGIME gate.
5. RISING gate.
6. FALLING gate.
7. HIGH+RISING stress gate.

VIX thresholds are derived only from the development portion of the cached point-in-time VIX series.

## Grid
63 subsets × 4 aggregators × 7 VIX modes = 1,764 declared candidates.

## Holdout discipline
All 1,764 candidates are screened on validation. The top 10 are frozen before any 2026 holdout replay. Holdout is not used to tune or redesign the ensemble.

## Statistical analysis
Use paired expiry bootstrap (10,000 resamples), sign-flip permutation, 95% confidence intervals for incremental P&L, maximum drawdown, profit factor, win rate, disagreement and cost stress.

Raw p-values are interpreted alongside the multiple-comparison burden and economic robustness.
