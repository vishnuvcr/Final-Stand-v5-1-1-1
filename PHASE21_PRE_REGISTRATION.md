# Phase 21 — Pre-Expiry Adverse-Move Risk Control

## Research question

Can a pre-expiry, direction-aware adverse NIFTY move be used to either:
1. exit the current three-leg position early and reduce tail losses; or
2. mechanically add one farther-OTM protective option to cap the adverse tail,

without materially sacrificing historically profitable trades?

The comparator is the frozen final Phase-20 strategy, including the 13:30 IST expiry-day MTM/MFE stop.

## Locked comparator

1. 90% of selected-X target.
2. From 13:30 IST on expiry day, exit when combined three-leg MTM < 0 and running MFE < 0.50× target.
3. Otherwise exit at the latest complete observation at or before 15:29 IST.
4. No payoff-boundary stop.

## Development / validation / holdout

- Training/selection: 2021-05-27 through 2023-12-31
- Validation: 2024-01-01 through 2025-12-31
- Holdout: 2026-01-01 through 2026-09-30

No candidate is selected using validation or holdout outcomes.

## Adverse-move signal

Let S0 be the 10:00 IST entry NIFTY spot.

For the BEARISH call structure, adverse movement is St-S0.
For the BULLISH put structure, adverse movement is S0-St.

Thresholds: 200, 300, 400, 500 and 600 NIFTY points.

Confirmation: 1, 5 or 15 consecutive complete minutes.

Signal families:
1. spot-only;
2. spot + current three-leg MTM < 0;
3. spot + MTM < 0 + running MFE < 0.50× original target.

Exact common timestamps only; no interpolation, forward filling or unobserved crossing.

## Candidate A — early exit

When a pre-expiry adverse-move signal fires, close all three original legs.

Training selection requires zero baseline-positive trades exited before the frozen comparator exit.

Promotion requires positive validation and 2026 holdout uplift, zero baseline-positive trades affected in both periods, and no more than 5% max-drawdown deterioration versus the frozen comparator.

## Candidate B — tail-hedge repair

When the same signal fires, buy one lot of OTM-(n+3) on the same option type:
- BEARISH -> buy OTM-(n+3) CE;
- BULLISH -> buy OTM-(n+3) PE.

Two post-adjustment exits are pre-registered:
1. target-or-baseline-exit: continue until the original target is reached; otherwise exit at the frozen comparator exit;
2. recover-to-zero-or-baseline-exit: exit at the first complete observation where repaired combined gross P&L reaches 0 or above; otherwise exit at the frozen comparator exit.

The hedge uses the same ₹0.05 adverse execution tick, the same historical lot size, the same ₹10/order brokerage assumption and the audited date-aware statutory/transaction charges.

Training selection requires zero baseline-positive trades adjusted before the frozen comparator exit and zero missing hedge execution at triggered adjustments.

Promotion requires positive validation and holdout uplift, zero baseline-positive trades affected, no material max-drawdown deterioration, and zero hedge execution gaps.

## Required outputs

For each candidate and train/validation/holdout/full period:
- net P&L and uplift versus frozen comparator;
- maximum drawdown;
- number of triggers/adjustments;
- baseline-positive trades affected;
- loss reduction;
- losses eliminated;
- worst single-trade net loss;
- 5th percentile trade P&L;
- hedge execution gaps.

## Phase completion

The phase is complete when either a candidate passes the walk-forward promotion screen or no candidate does and the frozen Phase-20 strategy remains unchanged.

No new threshold family will be added after seeing results. A materially different repair mechanism requires a new explicitly registered phase.
