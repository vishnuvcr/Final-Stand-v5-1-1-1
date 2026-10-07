# Phase 50B — TT-02 Common-Cost Replay Specification

## Strategy
0.20/0.10 Delta Calendar Hedge Spread v4.

## Frozen source semantics
- Continuous evaluation.
- Entry eligible from 09:20 through 15:00 while flat.
- Current-week expiry = first listed NIFTY expiry on/after the calendar date; next-week expiry = next listed expiry.
- Initial legs: sell one current-week CE at +0.20 delta; sell one current-week PE at -0.20 delta; buy two next-week CE at +0.10 delta; buy two next-week PE at -0.10 delta.
- Repair CE when short CE delta <= +0.08: close and replace at +0.20 delta; the same repair may occur again once.
- After the first CE repair, if that short CE delta reaches >= +0.50, replace it at +0.40 delta.
- PE logic is symmetric: -0.08 repair, then -0.50 reversal to -0.40.
- If next-week long CE delta >= +0.40, replace 2 lots at +0.25 delta.
- If next-week long PE delta <= -0.40, replace 2 lots at -0.25 delta.
- Universal exit on current-week expiry day at/after 15:15.

## Point-in-time delta reconstruction
The historical option dataset stores price/strike/expiry/option type/OHLCV/OI but no precomputed Greek column. Delta is therefore reconstructed from the exact observed option close using Black-Scholes implied volatility, European delta and r=0%. Missing/invalid option prices are never interpolated.

## Execution model
- Market-price source semantics are preserved at the rule level.
- Final Stand execution layer applies adverse 0.05-point option tick per leg/execution.
- ₹10 brokerage per order.
- Date-aware STT, exchange, SEBI, IPFT, stamp and GST charges.
- +50% total monetary-cost stress.

## Evidence hierarchy
1. Native Tradetron report: provenance only.
2. Final Stand common-cost replay: primary research evidence.
3. Chronological development/validation/holdout and active-VIX inference determine promotion.

## Reconciliation targets
The native report has 3,896 fills, 1,948 buys and 1,948 sells from 2021-10-06 to 2026-10-06. Its first native entry is 2021-10-06 09:20 with current-week 0.20-delta-like short legs and next-week 0.10-delta-like long hedges. Common replay results will be compared against native fill timing/geometry only as a source-fidelity audit; native P&L is not used as the comparator.
