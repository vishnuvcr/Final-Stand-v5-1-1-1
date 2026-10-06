# Phase 39 Final Conclusion

## Decision

**Phase 39 is complete. No candidate is promoted to the canonical strategy.**

The canonical Phase-20/24 strategy remains unchanged.

## Strongest candidate

Sparse-GAM Control-Relative Counterfactual Override:

- Default: retain canonical stateful direction.
- Target: post-cost CALL-minus-PUT economic margin.
- Uncertainty penalty: 1.0 × predictive uncertainty.
- Override threshold: ₹500.
- Historical sequential overrides: 7.

## Sequential performance

| Period | Incremental P&L |
|---|---:|
| Development | -₹18,175.07 |
| 2024–2025 validation | +₹17,983.53 |
| 2026 holdout | +₹7,390.39 |
| Full compared sample | +₹7,198.85 |

2026 holdout maximum drawdown improved from ₹37,326.63 control to ₹29,936.24 policy.

The validation/holdout improvement survived +50% and +100% aggregate cost stress.

## Why it is not promoted

The development contribution is negative, only seven overrides generate the positive out-of-sample effect, and the fixed-opportunity paired-expiry validation uncertainty interval crosses zero. The symbolic candidate has zero holdout uplift and the online Hedge family is negative in validation.

This combination is insufficient to claim a durable edge.

## Research disposition

The Sparse-GAM rule is retained as a **paper-trading/prospective validation candidate**.

No additional ad-hoc model family is added after the registered Phase-39 stop rule.

## Canonical strategy

The Phase-20/24 canonical strategy remains the authoritative historical entry-to-exit specification.

## Next research priority

A future phase should focus on prospective validation and higher-fidelity point-in-time market data, especially broker-quality bid/ask/fill information, NIFTY futures basis/OI, breadth, corporate actions and timestamp-verified news. It should not be another unrestricted classifier sweep.
