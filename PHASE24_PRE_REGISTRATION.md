# Phase 24 Pre-registration — Targeted Reversal Trigger

## Research question

Can a point-in-time, entry-only two-stage reversal trigger improve the frozen Phase-20 strategy by reversing only trades that are simultaneously high-risk for canonical loss and high-confidence candidates for the opposite-side structure?

## Comparator

Frozen Phase-20 canonical dynamic-n strategy:
- 10:00 IST entry at 4 trading sessions before expiry.
- Stage-1 call/put premium expression: (OTM7 + OTM8 - OTM6).
- Higher expression selects direction.
- Dynamic n from 6–15 using the frozen 95%-of-maximum rule.
- Buy OTM-n and sell OTM-(n+1)/(n+2).
- 90% target.
- Expiry-day 13:30 conditional stop: MTM < 0 and MFE < 0.50 × target.
- 15:29 expiry fallback.
- Existing slippage, brokerage, statutory and Paytm Money cost assumptions unchanged.

## Data and temporal discipline

Use the exact corrected 190-trade Phase-23 universe.

Training: through 2023-12-31.
Validation: 2024-01-01 through 2025-12-31.
Untouched holdout: 2026-01-01 through 2026-09-30.

All features must be measurable by 10:00 IST on entry day. No post-entry information is permitted.

## Fixed model

Reuse the exact Phase-23 low-complexity loss-risk and reverse-superiority model construction:
- same eight feature groups;
- same training-only robust normalization;
- same balanced L2 logistic models;
- same training fit only.

No additional feature family is permitted in Phase 24.

## Action rules to test

### Family A — two-stage AND gate

Reverse when all are true:
1. canonical loss probability >= L;
2. reverse-superiority probability >= R;
3. reverse structure is available.

Thresholds:
- L ∈ {0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95}
- R ∈ {0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95}

### Family B — two-stage AND + superiority margin

Reverse when the Family-A conditions hold and:
P(reverse-better) - P(canonical-loss) >= M.

M ∈ {-0.10, 0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30}.

No skip action is used in Phase 24; this isolates the reversal question.

## Training selection gate

A candidate is training-eligible only if all are true:
1. positive training P&L uplift;
2. at least one canonical training loss is reversed;
3. >=95% of baseline-positive trades remain profitable;
4. zero baseline-positive trades are converted into losses;
5. profitable-trade P&L sacrificed by reversals <=5% of baseline training positive P&L;
6. no reverse execution gap for an action that was taken.

If multiple candidates pass, select the least aggressive qualifying rule:
- highest loss-risk threshold L;
- then highest reverse threshold R;
- then highest margin M;
- then highest training uplift only as a final tie-break.

## OOS promotion gate

A selected rule can be promoted only if:
- validation uplift > 0;
- untouched holdout uplift > 0;
- validation winner retention >= 90%;
- holdout winner retention >= 90%;
- zero baseline-positive trade becomes a loss in either OOS period;
- maximum drawdown is no more than 5% worse than the canonical comparator;
- no execution/data gaps;
- at least one canonical loss is reversed in validation OR holdout.

No rule failing this gate may alter the strategy.

## Statistical outputs

Report trade count; canonical/reversal counts; net P&L and uplift; winner retention; losing trades reversed; profitable P&L sacrificed; profit factor; maximum drawdown; worst trade; 5% lower-tail mean; bootstrap CI for P&L uplift; trade-level ledger; train/validation/holdout breakdown; and L/R/M sensitivity.

## Pre-registered interpretation

Phase 24 is a targeted hypothesis test, not a free optimization pass. Retrospective identification of known losses is not sufficient. Only the frozen training-selection procedure and untouched OOS gates may change the canonical strategy.

## Stopping rule

Phase 24 ends after the preregistered L/R/M grid is exhausted and evaluated. No new feature, threshold family, or alternative model may be introduced after observing results. If no candidate passes, retain the Phase-20 canonical strategy unchanged.