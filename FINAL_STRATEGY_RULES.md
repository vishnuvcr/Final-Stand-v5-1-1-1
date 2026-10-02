# Final Strategy Rules — Corrected Dynamic-n NIFTY 3-Leg Ratio

**Status:** Final historical research specification after Phase 20  
**Data window:** 2021-05-27 through 2026-09-30  
**Instrument:** NIFTY weekly index options  
**Branch:** phase-20-payoff-boundary-stop-research

## 1. Entry eligibility

For each eligible NIFTY weekly expiry:

1. Identify the fourth prior trading session, excluding expiry day.
2. Take the exact **10:00 IST** NIFTY spot and option snapshot.
3. Select ATM as the NIFTY strike nearest the 10:00 spot.
4. Use the exact ₹50 NIFTY strike ladder.
5. Define OTM-n as exactly n strike intervals from ATM:
   - calls: ATM + n×₹50;
   - puts: ATM − n×₹50.
6. Do not substitute an ordinal/nearest quoted strike for a missing exact strike.
7. If required 10:00 data are incomplete, do not trade and log the exclusion.

## 2. Direction selection

Calculate:

**X_call = CE(OTM8) + CE(OTM7) − CE(OTM6)**

**X_put = PE(OTM8) + PE(OTM7) − PE(OTM6)**

Decision:

- X_call > X_put → **BEARISH**, use the call-side structure.
- X_call < X_put → **BULLISH**, use the put-side structure.
- X_call = X_put → **no trade**.
- Missing any OTM6/7/8 price on either side → **no trade**.

The selected-side X values must be positive before a position is opened.

## 3. Dynamic-n selection

On the selected call or put side, calculate for every n from 6 through 15:

**X_n = Premium(OTM(n+2)) + Premium(OTM(n+1)) − Premium(OTM n)**

All n=6…15 candidates must be computable from the exact OTM6…17 strikes. If the candidate set is incomplete, exclude the expiry.

Then:

1. X_max = max(X_6,…,X_15)
2. Eligibility threshold = 0.95 × X_max
3. Eligible n satisfy X_n >= 0.95 × X_max
4. Select the **largest eligible n**

This 95% higher-n preference is fixed and is not re-optimized from trade outcomes.

## 4. Position construction

For the selected n and selected option type:

- **Buy OTM-n**
- **Sell OTM-(n+1)**
- **Sell OTM-(n+2)**

All three legs have the same expiry.

## 5. Target

Original target:

**T = 0.90 × X_selected × lot size**

Monitor the combined three-leg position at complete minute observations after entry.

Target exit occurs on the first complete minute where the **slippage-adjusted combined three-leg gross P&L >= T**.

Target is evaluated before the expiry-day conditional stop when both conditions are simultaneously observable.

## 6. Final expiry-day conditional stop

This is the stop rule selected and confirmed by the Phase-19 walk-forward analysis and retained after Phase 20.

At **13:30 IST or later on expiry day**, exit all three legs when both conditions are true:

1. **Current combined three-leg MTM < ₹0**
2. **Running MFE since entry < 0.50 × the original target**

MFE is the running maximum of the **combined three-leg slippage-adjusted gross P&L** from entry until the current minute. It does not reset.

Examples:
- Target ₹10,000; MFE ₹4,000; current MTM −₹1,000 at 13:30 → stop triggers.
- Target ₹10,000; MFE ₹6,000; current MTM −₹1,000 at 13:30 → stop does not trigger.
- Target ₹10,000; current MTM +₹500 at 13:30 → stop does not trigger.

The stop is evaluated on exact minute observations. It is not a per-leg stop.

## 7. Expiry fallback

If neither the target nor the 13:30 conditional stop has occurred:

- exit at the **latest complete three-leg observation at or before 15:29 IST on expiry day**;
- no forward filling or synthetic price is used;
- incomplete three-leg observations are ignored.

## 8. Payoff-boundary rule

**No payoff-boundary stop is used.**

Phase 20 tested entry-time expiry zero-P&L/green-area boundaries with 0/50/100/200/400 point buffers, one- and three-minute confirmation, and MTM/MFE filters. The selected training-safe boundary rule was positive only in training and materially negative in validation and the 2026 holdout. The combined boundary-plus-expiry-stop rule was also negative out of sample.

Therefore NIFTY crossing beyond the entry-time payoff green area **does not by itself trigger an exit before expiry day**.

## 9. Execution model

The historical research implementation uses:

- one adverse **₹0.05 option tick per leg**;
- correct long/short P&L signs:
  - long leg: exit − entry;
  - short legs: entry − exit;
- historical/date-aware NIFTY lot size;
- **six executed option orders** per completed trade;
- modeled **₹10 brokerage per unique executed F&O order**;
- date-aware transaction/exchange costs, STT, SEBI/IPFT, stamp duty and GST assumptions already audited in the research engine;
- no price interpolation, forward filling or synthetic option marks.

The stop's MTM/MFE decision is based on the slippage-adjusted three-leg gross P&L path; exit brokerage/statutory charges are then applied to compute realized net P&L.

## 10. Complete exit precedence

For each open trade, evaluate in this order at every complete minute:

1. **Target:** combined gross P&L >= original target → exit.
2. **Expiry-day conditional stop:** expiry day, time >=13:30, combined MTM <0 and MFE <0.50×target → exit.
3. **Expiry fallback:** if still open, exit at the last complete three-leg observation <=15:29 on expiry.

There is no separate pre-expiry hard stop or payoff-boundary stop.

## 11. Historical final-rule result

Applying the final exit logic to the 190 corrected dynamic-n trades:

| Metric | Final-rule result |
|---|---:|
| Completed trades | 190 |
| Net P&L | **₹149,129.53** |
| Mean net/trade | **₹784.89** |
| Net winning trades | **179 / 190 (94.21%)** |
| Profit factor | **2.34** |
| Maximum cumulative drawdown | **₹27,336.11** |
| Target exits | **178** |
| Conditional-stop exits | **5** |
| Expiry-fallback exits | **7** |
| Baseline-positive trades stopped early | **0** |

The stop changed five exits, all baseline losing trades. It did not eliminate every loss; it truncated selected expiry losses.

## 12. Research status and deployment caveat

This is the **complete historical research specification**, not a guarantee of future performance.

Before any live deployment, the same exact rules should be forward/paper tested with live bid/ask, partial-fill behavior, latency, spread costs and broker execution logs. No live performance inference is made from the historical backtest alone.
