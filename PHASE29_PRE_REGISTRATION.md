# Phase 29 Pre-Registration — Delta-Change-Only Target and Stop

## Research question
Can the strategy's target and stop decisions be determined entirely by **changes in the two short legs' absolute delta**, without using the 0.90 target percentage, absolute delta levels, portfolio delta, or the Phase-20 13:30 conditional stop?

## Hypothesis
For the short OTM-(n+1) and OTM-(n+2) legs:
- a sufficiently large **decrease** in absolute delta indicates favorable movement and can trigger profit booking;
- a sufficiently large **increase** in absolute delta indicates adverse directional exposure and can trigger a stop.

## Signal definitions
For lookback L minutes:
- S1 change = |ΔS1(t)| − |ΔS1(t−L)|
- S2 change = |ΔS2(t)| − |ΔS2(t−L)|
- MEAN change = (S1 change + S2 change)/2
- BOTH change = min(S1 change, S2 change), requiring both legs to show the relevant direction when used as a trigger.

Target signal: delta change <= −threshold.
Stop signal: delta change >= +threshold.

No target-percentage condition is permitted.

## Pre-registered grid
- Modes: S1, S2, MEAN, BOTH.
- Lookbacks: 1, 3, 5, 10, 15 minutes.
- Delta-change thresholds: 0.02, 0.05, 0.08, 0.10, 0.15, 0.20.
- Confirmation: 1 or 3 consecutive complete minutes.
- Target and stop are tested independently and jointly.

## Exit precedence
1. If a target delta-change signal and stop signal occur at the same observation, the target signal is evaluated first only when its condition is already satisfied; otherwise stop.
2. If neither signal occurs, expiry fallback remains the latest complete three-leg observation at or before 15:29 IST.
3. The candidate does **not** use the Phase-20 0.90×target trigger.
4. The candidate does **not** use the Phase-20 13:30 MTM/MFE stop.

The Phase-20 strategy remains the historical comparator only.

## Validation protocol
- Training: through 2023-12-31.
- Validation: 2024-01-01 through 2025-12-31.
- Holdout: 2026-01-01 through 2026-09-30.
- Selection is training-only.
- Stop selection requires zero training baseline-positive trades affected.
- Promotion requires positive validation and holdout uplift, maximum DD no more than 5% worse, and no material execution-data coverage failure.

## Execution
The exact Phase-20 slippage, brokerage, statutory charges, date-aware lot sizes and complete-leg observation rules are retained.

## Important distinction
This phase tests **delta dynamics**, not delta level. It is therefore a new hypothesis and does not reopen the rejected Phase-28 absolute-delta threshold grid.
