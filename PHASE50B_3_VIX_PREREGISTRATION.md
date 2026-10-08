# Phase 50B-3 — VIX Conditioning Preregistration

## Status
FROZEN before Phase-50B-3 execution.

## Research question
Do the already-feasible source-faithful Phase-50B strategies exhibit economically and chronologically distinct performance across the preregistered India-VIX state family?

## Scope
Only candidates that passed the Phase-50B >=95% mandatory-exit coverage gate are eligible:
- TT-02
- TT-03
- TT-04
- TT-05

TT-06 and TT-07 are terminal FAIL_COVERAGE and are excluded from all downstream VIX analysis. Their diagnostic P&L is not consumed.

## Fixed VIX mode family
For each trade, VIX state is reconstructed from the **entry timestamp**:
- LOW
- NORMAL
- HIGH
- SPIKE
- FALLING
- RISING
- HIGH_RISING

The state definitions already implemented in the audited Phase-43 VIX engine are reused. No new threshold is introduced.

## No outcome-day leakage
The trade's VIX regime is determined only from information available at entry. Outcome-day VIX is not used for conditioning, selection, or inference.

## Analysis set
All 4 × 7 = **28 strategy-regime hypotheses** are retained. There is **no post-result selection of a preferred VIX regime** in Phase 50B-3.

This is deliberate: regime cells with small samples are retained and reported rather than silently dropped, while the statistical gate later applies multiplicity correction across the full registered hypothesis family.

## Chronological partitions
- DEV: expiry through 2023-12-31
- VAL: 2024-01-01 through 2025-12-31
- HOLD: 2026 onward

HOLD is descriptive confirmation only and is never used for regime selection or hypothesis testing.

## Primary descriptive outputs
For every strategy × VIX mode × split:
- trade count
- net P&L
- +50% friction net
- ₹20/order net
- ₹20/order +50% friction net
- mean net/trade
- median net/trade
- win rate
- worst trade
- chronological maximum drawdown

## Statistical handoff
Phase 50B-6 will test the same 28 registered hypotheses using the already-audited bootstrap/permutation framework, DEV+VAL only, with Holm correction across all tested hypotheses. No hypothesis will be added or removed after observing Phase-50B-3 results.

## Promotion protection
A positive VIX cell is not a promotion result. Any later promotion candidate must also pass the preregistered chronological validation, cost-stress, coverage, inference and protected-holdout requirements.

## Literature rationale
India-VIX regime conditioning is scientifically plausible but not assumed to be profitable. Existing literature documents asymmetric India-VIX/NIFTY relationships and regime dependence, while recent NIFTY option studies also emphasize variance-risk premia, skew and transaction-cost effects. These are hypotheses for testing, not evidence for the repository's strategies.

## Reproducibility
The phase consumes only persisted Phase-50B trade ledgers and the audited VIX source. No market source is downloaded merely to rerun the descriptive phase unless the existing cache is unavailable.
