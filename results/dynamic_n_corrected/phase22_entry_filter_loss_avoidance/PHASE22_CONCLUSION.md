# Phase 22 — Entry Filter Research Conclusion

## Decision

**No pre-registered entry filter is promoted. The Phase-20 entry rules remain unchanged.**

The research asked whether the known losing trades could be avoided *before entry* using information available at the 10:00 IST snapshot, while disturbing profitable trades as little as possible.

The answer for the registered feature families is **no**.

## Comparator

The frozen Phase-20 strategy remains:
- 10:00 IST entry;
- Stage-1 call/put direction selection;
- dynamic n from 6–15 using the 95%-of-maximum rule;
- buy OTM-n and sell OTM-(n+1)/(n+2);
- 90% target;
- 13:30 expiry-day MTM/MFE stop;
- 15:29 expiry fallback.

Historical comparator:
- 190 completed trades;
- net P&L ₹149,129.53;
- 179 positive trades;
- 11 losing trades;
- maximum drawdown ₹27,336.11.

## Pre-registered safety screen

Training period: through 2023-12-31.

A candidate had to:
1. retain at least 95% of baseline-positive trades;
2. remove at least 2 baseline-negative trades;
3. improve training net P&L.

**Zero candidates passed.**

More strongly, the zero-winner-loss-removal frontier was empty: **no tested candidate removed even one training loss without also removing at least one profitable training trade.**

## Closest loss-removing candidates

The closest candidate by winner retention was:

**direction_margin >= 0.15**

Training:
- net uplift: **−₹2,300.22**
- winners removed: **14**
- winner retention: **85.26%**
- losses removed: **1**

2024–2025 validation:
- net uplift: **−₹70,498.06**
- winners removed: **42**
- losses removed: **2**

2026 holdout:
- net uplift: **−₹11,906.12**
- winners removed: **7**
- losses removed: **3**

This is not a viable entry filter.

Another notable candidate was:

**20-day realized volatility <= training 80th percentile**

Training:
- net uplift: **−₹14,877.97**
- winner retention: **82.11%**
- losses removed: **2**

Validation:
- net uplift: **−₹41,885.62**

2026 holdout:
- net uplift: **+₹6,148.49**

Its isolated positive holdout result is insufficient because the rule failed training and validation and removed too many profitable trades.

## Feature-family findings

### Payoff-boundary distance

Entry-time distance from the dangerous expiry payoff boundary did not identify the losing trades cleanly.

For example, a normalized boundary distance >= 0.50 produced:
- training uplift: ₹0;
- training losses removed: 0;
- validation uplift: −₹2,527.62.

At stronger thresholds, winners were removed much faster than losses.

This is consistent with Phase 20: the payoff boundary is structurally informative about expiry risk, but it is not a sufficiently reliable predictor of which individual entry will eventually lose.

### Direction-selection confidence

Stronger X-call/X-put separation did not improve selection robustness.

At direction-margin >= 0.15:
- only one training loss was removed;
- 14 training winners were also removed;
- training P&L fell ₹2,300;
- validation P&L fell ₹70,498.

Therefore the magnitude of the Stage-1 directional signal is not a reliable loss filter in this sample.

### Structure quality

Thresholding X_selected, X_selected/long-premium, or X_selected/X_max generally removed profitable trades before it removed meaningful numbers of losses.

### Pre-entry NIFTY regime

Pre-entry returns and realized-volatility regimes also failed to provide a stable loss filter.

Some volatility thresholds removed losses, but only after sacrificing a large fraction of profitable trades. The apparent 2026 benefit of the 20-day-volatility <= 80th-percentile rule was not present in the earlier validation period.

### Two-feature combinations

The controlled combinations did not rescue the result. Combining payoff distance with direction confidence, trend or structure quality generally increased winner sacrifice without producing stable out-of-sample improvement.

## Important inference

The 11 historical losing trades appear **heterogeneous rather than sharing a simple common entry-state signature** among the tested variables.

This matters because the previous Phase-21 result showed that post-entry adverse movement also could not be converted into a stable fixed-point stop.

Taken together:

**The current evidence does not show that the strategy's tail losses can be solved by either a simple pre-entry filter or a simple post-entry NIFTY-point stop.**

That does not prove that no predictive entry signal exists. It means that the tested structural variables are insufficient.

## Strengths

- Entry filters use only information available at 10:00 IST.
- No future option prices or trade outcomes are used as features.
- Training/validation/holdout separation is preserved.
- The exact Phase-20 execution-cost model is retained.
- The filter family and thresholds were registered before evaluation.
- The zero-winner-loss-removal frontier was explicitly measured.

## Limitations

- Only 190 completed trades and 11 baseline losses are available.
- A small number of tail losses limits statistical power.
- The tested feature families are intentionally interpretable and relatively small.
- Option implied-volatility surface features beyond the selected three-leg premiums were not included.
- Market-event/news information was not included.
- Cross-market features were not included.
- A nonlinear model was deliberately not used because the sample is too small to justify unrestricted model selection without substantial overfitting risk.

## Conclusion

**Phase 22 does not justify changing the entry criteria.**

The canonical historical strategy remains exactly as specified after Phase 20.

The next scientifically meaningful direction, if research continues, is not another arbitrary threshold search. It should be a separately registered **entry-risk model phase** using richer but still economically interpretable information:
- full option IV/skew/term-structure information;
- NIFTY futures basis;
- India VIX and volatility regime;
- overnight/global-market gap information;
- FII/DII and index-flow proxies where available before 10:00;
- scheduled event/news regime;
- cross-asset risk indicators.

Any such model must remain severely constrained, walk-forward validated and benchmarked against the frozen 190-trade strategy.

