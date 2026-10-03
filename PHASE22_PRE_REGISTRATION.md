# Phase 22 — Entry Filter Research to Avoid Tail-Loss Trades

## Research question

Can the 10:00 IST entry snapshot identify trades that are disproportionately likely to become the final strategy's losing trades, so that the strategy can skip those entries while retaining most profitable trades?

This phase changes only entry eligibility. It does not change the frozen Phase-20 exit logic.

## Comparator

The frozen Phase-20 final strategy:
- 10:00 IST entry;
- dynamic-n direction selector;
- 90% target;
- 13:30 expiry-day MTM < 0 and MFE < 0.50×target stop;
- 15:29 expiry fallback.

Historical comparator:
- 190 trades;
- net P&L ₹149,129.53;
- 179 positive trades;
- 11 losing trades;
- maximum drawdown ₹27,336.11.

## Core safety principle

A useful entry filter must not simply maximize training P&L by deleting winners.

Primary training safety constraint:
- retain at least 95% of baseline-positive trades;
- remove at least 2 baseline-negative trades;
- require positive training net-P&L uplift.

Preferred diagnostic:
- identify any candidate with zero profitable trades removed.

Promotion requires:
1. positive net uplift in 2024–2025 validation;
2. positive net uplift in 2026 holdout;
3. validation and holdout retain at least 90% of baseline-positive trades;
4. validation and holdout maximum drawdown is no more than 5% worse than the comparator;
5. no look-ahead features;
6. all original execution costs remain unchanged.

The training selector maximizes net-P&L uplift among candidates satisfying the primary safety screen, then loss removal, then winner retention.

## Temporal split

- Training/selection: 2021-05-27 through 2023-12-31.
- Validation: 2024-01-01 through 2025-12-31.
- Holdout: 2026-01-01 through 2026-09-30.

The selected rule is frozen before validation and holdout evaluation.

## Entry-time feature families

All features are calculated only from information available by 10:00 IST.

### A. Payoff-buffer geometry

For the selected call structure, calculate the expiry zero-P&L dangerous-side boundary:

boundary = K_(n+1) + K_(n+2) - K_n + entry_credit

For the selected put structure:

boundary = K_(n+1) + K_(n+2) - K_n - entry_credit

Define 'boundary_distance' as the positive distance from entry spot to this dangerous boundary.

Test minimum absolute distances:
- 0, 50, 100, 150, 200, 300, 400 NIFTY points.

Also normalize the distance by the estimated four-session move:

expected_move_4d = spot × RV10 × sqrt(4/252)

Test minimum 'boundary_distance / expected_move_4d':
- 0.50, 0.75, 1.00, 1.25, 1.50, 2.00.

This is an entry filter, not an intraday payoff-boundary stop.

### B. Direction-selection confidence

From the already computed Stage-1 X_call and X_put:

direction_margin =
(selected_X − opposite_X) /
(|selected_X| + |opposite_X| + epsilon)

Test minimum margins:
- 0.05, 0.10, 0.15, 0.20, 0.30.

When both X values are positive, also test:
- selected_X / opposite_X >= 1.05, 1.10, 1.20, 1.30, 1.50.

### C. Structure quality

Test:
- X_selected >= 1, 2, 3, 5, 8 premium points;
- X_selected / long-leg-entry-premium >= 0.10, 0.20, 0.30, 0.40, 0.50, 0.75;
- X_selected / X_max >= 0.97, 0.98, 0.99, 1.00;
- selected n == 6;
- selected n <= 7.

These are all known at entry.

### D. Pre-entry NIFTY regime

Using only daily NIFTY data strictly before the entry session:

- 1-session return;
- 3-session return;
- 5-session return;
- annualized 5-session realized volatility;
- annualized 10-session realized volatility;
- annualized 20-session realized volatility;
- direction-aligned 5-session return:
  + return for BULLISH put structures;
  - return for BEARISH call structures.

For the direction-aligned 5-session return, test:
- >= 0%;
- >= +0.5%;
- >= +1.0%;
- >= +1.5%;
- <= 0%;
- <= −0.5%;
- <= −1.0%;
- <= −1.5%.

For RV5/RV10/RV20, thresholds are defined by the training distribution only at the 20th, 40th, 60th and 80th percentiles, then frozen for validation and holdout. Both low-volatility and high-volatility variants are tested.

## Controlled two-feature combinations

To test whether the information becomes useful only jointly, the following combinations are pre-registered:

1. boundary-distance-z × direction-margin;
2. boundary-distance-z × direction-aligned 5-session return;
3. boundary-distance-z × X_selected/long-premium;
4. direction-margin × direction-aligned 5-session return.

The combination thresholds are drawn only from the fixed single-feature grids above.

No three-feature combination, arbitrary tree search, neural network or post-result threshold expansion is permitted.

## Primary statistical outputs

For every rule and each period report:

- trades retained;
- trades excluded;
- net P&L;
- net uplift versus comparator;
- number and percentage of winners retained;
- number and percentage of losses removed;
- winner P&L sacrificed;
- losing P&L removed;
- loss-capture ratio;
- profit sacrificed per losing trade removed;
- profit factor;
- maximum drawdown;
- worst trade;
- 5th-percentile trade P&L.

For the selected fixed rule, also calculate a trade-level bootstrap confidence interval for validation and holdout net-P&L uplift.

## Multiple-testing protection

Because many deterministic filters are tested against a small 11-loss sample, a positive training result alone is not evidence of a valid rule.

The primary promotion gate is temporal:
- training selection only;
- frozen validation test;
- frozen 2026 holdout test.

A rule that looks excellent in training but fails either later period is rejected.

A diagnostic report will also show the zero-winner-loss-removal frontier so that the research distinguishes a genuinely robust entry criterion from a filter that simply deletes profitable trades.

## Phase completion

If a rule passes the promotion screen, report the exact entry criterion in executable form and compare the filtered strategy with the unfiltered final strategy.

If none passes, the final entry rules remain unchanged and the phase records which entry features were most informative but non-robust.

A materially different feature family requires a separately registered phase.
