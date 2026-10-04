# Phase 28 Pre-registration — Individual-Leg Delta Research

## Question
Does the delta of the individual option legs, especially the two short legs, contain exit information that is lost when deltas are aggregated into portfolio delta?

NSE identifies NIFTY 50 index options as European-style CE/PE contracts. citeturn0search1

## Control
Frozen Phase-20 strategy. No changes to entry, dynamic-n selection, target, 13:30/MFE stop, expiry fallback, slippage, brokerage or statutory charges.

## Primary variables
- S1 = short OTM-(n+1), the nearer short leg.
- S2 = short OTM-(n+2), the farther short leg.
- Long OTM-n is retained as a diagnostic/control variable.
- Use absolute delta magnitude for cross-CE/PE comparison.
- Track delta level and, in a diagnostic extension, delta change.

## Delta reconstruction
For each leg, infer implied volatility from its observed option price with European Black-Scholes, r=0 and q=0 baseline, then calculate that leg's delta. No interpolation or forward filling. A minute is delta-valid only if all three leg deltas are valid.

The literature indicates that implied-BS delta can differ from smile-adjusted or minimum-variance deltas, so this phase treats the reconstructed delta as an empirical state variable, not an exact hedge ratio. citeturn0search12turn0search13

## Tests

### A. Short-leg profit booking
For each of S1 and S2 independently:
- MTM fraction: 0.50, 0.60, 0.70, 0.80, 0.90 × original target.
- absolute short-leg delta threshold: 0.05, 0.10, 0.15, 0.20, 0.25, 0.30.
- Exit at first valid minute satisfying both conditions.
- Original target remains a hard exit.
- Existing Phase-20 stop remains active if reached first.

### B. Short-leg adverse stop
For each of S1 and S2:
- MTM < 0.
- absolute short-leg delta >= 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50.
- 1 or 3 consecutive exact minutes.
- Training preference: zero profitable control trades stopped early.

### C. Walk-forward
Training through 2023-12-31.
Validation 2024-01-01 through 2025-12-31.
Holdout 2026-01-01 through 2026-09-30.

Select thresholds only on training. Validation and holdout are confirmation only.

### Promotion
Both validation and holdout must have positive net uplift, maximum DD no worse than 5% above control, and no material profit-factor degradation. The rule must not depend on one isolated threshold.

## Important distinction from Phase 27
Phase 27 tested net portfolio delta and is retained as a separate rejected hypothesis. Phase 28 tests individual leg delta, with S1 as the primary economic hypothesis.
