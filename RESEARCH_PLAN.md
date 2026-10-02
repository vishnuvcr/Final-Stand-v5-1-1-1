# Research Plan — Fixed OTM15 Restart (v3)

## Research question
Does the fixed-OTM15, 4-DTE, 10:00 IST NIFTY weekly-options directional 3-leg ratio strategy produce positive gross and net returns after realistic execution costs over the validated historical sample?

## Locked primary algorithm

### Stage 1 — Direction
At exactly 10:00 IST on the date that is 4 trading sessions before expiry (expiry day = 0 DTE), identify the nearest available ATM strike from the exact 10:00 option snapshot.

Rank strikes outward from ATM separately for calls and puts.

Calculate:
- X_call = CE(OTM17) + CE(OTM16) - CE(OTM15)
- X_put = PE(OTM17) + PE(OTM16) - PE(OTM15)

Directional rule:
- If X_call > X_put -> trade the BEARISH call structure.
- If X_call < X_put -> trade the BULLISH put structure.
- If exactly equal -> NO_TRADE_TIE; do not invent a direction.

### Stage 2 — Position
There is no high-n optimization or threshold in this restart. OTM15/16/17 are fixed.

BULLISH:
- buy OTM15 PE
- sell OTM16 PE
- sell OTM17 PE

BEARISH:
- buy OTM15 CE
- sell OTM16 CE
- sell OTM17 CE

### Stage 3 — Target exit
Let X be the selected-side raw 10:00 premium expression.

T = 0.90 * X * lot quantity.

Exit at the first complete minute after entry where slippage-adjusted gross three-leg P&L >= T.

### Stage 4 — Expiry exit
If target is not reached, exit at 15:29 IST on expiry day using the latest complete three-leg observation at or before 15:29.

No stop-loss.

## DTE definition
Four trading sessions before expiry, excluding expiry itself. For an ordinary Thursday expiry this normally means the preceding Friday; holiday/exception expiries use the actual exchange sessions.

## Data and provenance
Primary executable source remains thetrademarkk/india-index-options-1m, with 1-minute NIFTY spot/options data and expiry-specific option files. Existing validated date coverage begins 2021-05-27.

The earlier Zenodo 2019–2020 dataset remains excluded from the primary weekly-contract backtest because row-level expiry identification was not adequate.

## Execution and costs
Primary assumptions:
- one adverse ₹0.05 option tick per leg;
- date/expiry-aware NIFTY lot size;
- six executed orders per completed round-trip trade;
- Paytm Money F&O brokerage assumption: ₹10 per unique executed order;
- statutory/exchange charges explicitly modelled;
- no forward filling or synthetic prices;
- incomplete three-leg observations are excluded and logged.

## Research phases for this restart
1. Phase 6 — fixed-OTM15 specification and implementation audit
2. Phase 7 — fixed-OTM15 primary backtest
3. Phase 8 — statistical analysis
4. Phase 9 — robustness/sensitivity
5. Phase 10 — final manuscript

## Pre-registered robustness scope
After the primary result, robustness will examine:
- adverse slippage;
- entry time;
- DTE definition/sensitivity;
- brokerage sensitivity;
- target fraction;
- fixed strike rank around OTM15 only if needed to diagnose sensitivity.

The primary strategy itself remains fixed at OTM15/16/17.

## Supersession
All earlier v2 results using OTM6-based Stage 1 and n=6..15 high-n selection are superseded for this restart and must not be used as evidence for the present strategy.

## Stop condition
Stop after Phase 10.
