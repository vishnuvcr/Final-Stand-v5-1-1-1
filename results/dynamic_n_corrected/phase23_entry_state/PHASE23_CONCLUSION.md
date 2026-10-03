# Phase 23 Conclusion — Rich Entry-State and Directional-Switch Research

## Research question

Can richer point-in-time entry information identify trades where the Phase-20 canonical direction should be reversed or skipped, while preserving most profitable trades?

## Data integrity

The accepted Phase-23 feature/model run uses an exact 190/190 canonical-trade alignment. The reconstructed opposite-side structure is available for 185 of the 190 trades; unavailable reverse cases were never imputed.

The accepted feature table contains entry-time option premiums, OI/volume, IV proxies/skew, India VIX, prior-session cross-market variables, overnight/opening state, realized NIFTY volatility, and strategy/payoff geometry. External daily series were restricted to information available before the 10:00 IST entry.

## Model

Two low-complexity balanced logistic models were fit using training data only:
1. canonical-loss probability;
2. reverse-superiority probability.

The candidate action space was canonical/reverse/skip.

Training ended 2023-12-31; validation covered 2024–2025; 2026 was untouched holdout.

## Results

The selected combined policy used:
- skip when loss probability >= 0.80, unless the reverse probability triggered;
- reverse when reverse-superiority probability >= 0.70;
- otherwise canonical.

Training uplift was +₹23,352.60 with 98.96% winner retention.

Validation uplift was **−₹1,344.36** with 100% winner retention.

2026 holdout uplift was **₹0.00** with 100% winner retention.

The promotion gate therefore failed.

The reverse-only policy had the same OOS behavior at its selected training threshold: it improved training by +₹25,000.24, but validation uplift was −₹1,344.36 and holdout uplift was ₹0.00.

The skip-only policy also failed OOS promotion: training uplift +₹17,693.53, validation and holdout uplift both ₹0.

## Important descriptive finding

All 11 historical canonical losing trades had a profitable reconstructed opposite-side trade available. This is a retrospective property of the historical sample, not a deployable rule. Across those 11 losses, canonical P&L summed to approximately −₹111,651, while the corresponding reverse trades summed to approximately +₹18,075. A perfect ex-post classifier would therefore have changed those losses by about ₹129,726. This is an upper-bound diagnostic and must not be interpreted as out-of-sample performance.

The Phase-23 model did not demonstrate that these losses can be identified reliably enough at entry to realize that retrospective opportunity.

## Interpretation

The richer entry state contains predictive information, but the information is not stable enough in the tested low-complexity policy to improve the strategy out of sample. Several individual features show substantial training-period association with losses, while their direction or magnitude changes in validation and holdout. This instability is consistent with regime dependence and the very small number of canonical losses.

The result does not justify changing the canonical direction-selection rule.

## Decision

**Phase-23 adjustment is not promoted.**

The canonical Phase-20 entry and exit rules remain the active research comparator.

A materially narrower hypothesis—reversing only when both canonical loss-risk and reverse-superiority are simultaneously high—has been registered separately as Phase 24. Phase 24 is not a modification of Phase 23; it is a new preregistered test designed to reduce false reversals.
