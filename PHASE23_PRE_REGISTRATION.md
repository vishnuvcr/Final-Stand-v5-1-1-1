# Phase 23 — Conditional BULLISH Entry Filter

## Motivation

Phase 22 found that every one of the 11 losing final-strategy trades was a BULLISH/put-structure trade, while all 18 BEARISH/call-structure trades were profitable.

This is a subgroup observation, not a rule. Phase 23 tests whether a **BULLISH-only entry filter** can exploit that asymmetry without affecting BEARISH trades.

## Comparator

Frozen Phase-20 strategy:
- 190 trades;
- net P&L ₹149,129.53;
- 179 positive trades;
- 11 negative trades;
- maximum drawdown ₹27,336.11.

## Core restriction

Every BEARISH trade must pass unchanged.

Only BULLISH entries may be filtered.

Primary training safety:
- retain at least 95% of all baseline-positive trades;
- remove at least 2 baseline-negative trades;
- positive training net-P&L uplift.

The preferred diagnostic is zero BULLISH winners removed.

Promotion:
- positive validation uplift;
- positive 2026 holdout uplift;
- at least 90% overall winner retention in validation and holdout;
- at least one baseline loss removed in both periods;
- maximum drawdown no more than 5% worse than comparator.

## Entry-only feature families

All features come from the Phase-22 10:00 IST feature ledger.

### A. Direction-aligned 5-session return

For BULLISH trades this is the ordinary 5-session NIFTY return.

Test BULLISH-only minimum thresholds:
- -2.0%
- -1.5%
- -1.0%
- -0.5%
- 0%
- +0.5%
- +1.0%.

BEARISH trades are always retained.

### B. Direction confidence

BULLISH-only minimum Stage-1 direction margin:
- 0.05
- 0.10
- 0.15
- 0.20
- 0.25.

### C. Normalized dangerous-side payoff buffer

BULLISH-only minimum:
- boundary distance / four-session expected move >=
  0.75, 1.00, 1.25, 1.50.

This is an entry filter only; it is not an intraday payoff-boundary stop.

## Controlled two-feature combinations

BULLISH-only conjunctions:
1. signed 5-session return × direction margin;
2. signed 5-session return × normalized payoff buffer.

Thresholds are exactly the single-feature grids above.

No additional feature family, three-way combination, machine-learning model or post-result threshold expansion is permitted.

## Walk-forward protocol

- training/selection: through 2023-12-31;
- validation: 2024-01-01 through 2025-12-31;
- holdout: 2026-01-01 through 2026-09-30.

The rule is frozen after training.

## Required outputs

For every rule and period:
- retained trades;
- excluded trades;
- net P&L;
- net uplift;
- winner retention;
- BULLISH winners removed;
- BULLISH losses removed;
- overall losses removed;
- maximum drawdown;
- worst trade;
- 5th percentile P&L;
- loss capture;
- winner P&L sacrificed.

For the selected rule:
- validation and holdout bootstrap 95% CI of P&L uplift;
- exact executable entry criterion.

## Completion

If a conditional BULLISH filter passes the temporal promotion screen, report it as a candidate modification to entry rules.

If none passes, the final entry rules remain unchanged.
