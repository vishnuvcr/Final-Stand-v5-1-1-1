# Phase 50B Pre-Registration

## Frozen source universe

Seven user-supplied Tradetron exports:
- Dynamic Ratio Reversals
- 0.20/0.10 Delta Calendar Hedge Spread v4
- Corrected Dynamic-n NIFTY Weekly Options Strategy
- Profit Breakout Premium Match Straddle
- Simple Intraday Short Straddle
- Intraday Asym Premium
- Dynamic IC to Ratio

Prior repository lineages:
- Iron-condor-to-ratio v1/v2
- Option-intraday-v1
- NoDip-Stage-1
- MC1/MC2/MC3 BATMAN
- Final-stand-v4 option branches
- Daily-Options closed/registered strategy families
- Naked-option-v1 diagnostic long-option family

## Explicit non-claims

- Tradetron page backtest values are not treated as independent historical evidence unless the underlying rule is re-run on the project's point-in-time data.
- Previous repository P&L is not pooled with new results.
- Duplicated strategy lineages are not double-counted.
- Unfinished repository research is not converted into completed evidence.

## Variant universe

VIX:
LOW, NORMAL, HIGH, RISING, FALLING, SPIKE, HIGH_RISING.

Tail distances:
2, 3, 4, 5, 6, 8, 10, 12 strike steps where structurally meaningful.

Delta equivalents:
0.05, 0.08, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.65 where the source strategy uses delta and the historical chain supports stable delta.

Only source-compatible dimensions are varied.

## Controls

Every tuned strategy must be compared with its own exact source-faithful baseline.

## Confirmation

The registered statistical gate is active-vs-complement + paired baseline uplift + bootstrap/permutation + Holm correction + 2026 holdout.

## Cost model

Use the current project Paytm Money/NSE brokerage, statutory charges, historical lot sizes and adverse slippage model with +50% cost stress.
