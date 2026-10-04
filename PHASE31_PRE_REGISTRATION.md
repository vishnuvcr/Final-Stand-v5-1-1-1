# Phase 31 Pre-Registration — Asymmetric Entry-Referenced Combined Short-Leg Delta Exit

## Research question
Does an asymmetric target/stop rule based solely on proportional change in the combined absolute delta of the two short option legs improve the canonical Phase-20 strategy?

## Definition
At entry:
D0 = |delta(S1_entry)| + |delta(S2_entry)|

At observation t:
Dt = |delta(S1_t)| + |delta(S2_t)|

R(t) = Dt / D0 - 1

Target: R(t) <= -target_threshold.
Stop: R(t) >= +stop_threshold.

Thus target 0.25 means a 25% reduction in combined short-leg delta magnitude. Stop 1.50 means a 150% increase, i.e. Dt >= 2.5*D0.

## Grid
Targets: 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50.
Stops: 0.50, 0.75, 1.00, 1.25, 1.50, 2.00, 2.50, 3.00.
Confirmations: 1 and 3 complete minutes.
Total rules: 128.

## Frozen methodology
Use the corrected Phase-20 strike mapping, direction chooser, dynamic-n selection, slippage, transaction costs, historical lot sizes, Paytm Money brokerage assumptions, no interpolation/forward fill, and expiry fallback. Remove the option-P&L target and Phase-20 MFE stop only for the candidate mechanism. Training ends 2023-12-31; validation is 2024-2025; holdout is 2026-01-01 through 2026-09-30.

## Selection and promotion
Select the best target/stop/confirmation on training net uplift, DD secondary. Promote only if validation and holdout both beat Phase 20 and DD is no worse than 1.05x Phase 20.

## Statistical checks
Report trade counts, net P&L, win rate, profit factor where available, maximum drawdown, changed exits, winner-affected trades, bootstrap uplift confidence intervals, and canonical Phase-20 comparisons.

No numerical evidence is accepted until GitHub Actions completes successfully.
