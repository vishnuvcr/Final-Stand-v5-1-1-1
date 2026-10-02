# Strategy Specification — Corrected Dynamic-n Final Historical Specification

This file supersedes the older fixed-OTM15 specification as the canonical strategy definition for the corrected dynamic-n research.

## 1. Entry
- NIFTY weekly expiry.
- Enter exactly 4 trading sessions before expiry.
- Entry snapshot: exactly 10:00 IST.
- ATM = strike nearest NIFTY spot at 10:00.
- NIFTY strike interval = ₹50.
- OTM-n = exact ATM ± n×₹50.
- Missing exact strikes/data are exclusions; no ordinal substitution or forward filling.

## 2. Direction selector
- X_call = CE(OTM8) + CE(OTM7) − CE(OTM6)
- X_put = PE(OTM8) + PE(OTM7) − PE(OTM6)
- X_call > X_put → BEARISH call-side structure.
- X_call < X_put → BULLISH put-side structure.
- Equality → no trade.
- Missing OTM6/7/8 on either side → no trade.

## 3. Dynamic n
For n=6…15:
- X_n = Premium(OTM(n+2)) + Premium(OTM(n+1)) − Premium(OTM n)
- All candidate n values must be computable from exact OTM6…17 strikes.
- X_max = max(X_6…X_15)
- Eligible n: X_n >= 0.95×X_max
- Select the largest eligible n.
- Selected-side X must be positive.

## 4. Position
- Buy OTM-n.
- Sell OTM-(n+1).
- Sell OTM-(n+2).
- All legs same expiry and selected option type.

## 5. Target
T = 0.90 × X_selected × lot.

Exit at the first complete minute after entry where the slippage-adjusted combined three-leg gross P&L reaches or exceeds T.

## 6. Final conditional expiry-day stop
At 13:30 IST or later on expiry day, exit when:
- combined three-leg MTM < ₹0; and
- running MFE since entry < 0.50 × original target.

MFE is the cumulative running maximum of the combined three-leg slippage-adjusted gross P&L. It does not reset.

## 7. Expiry fallback
If neither target nor conditional stop occurs, exit at the latest complete three-leg observation at or before 15:29 IST on expiry day.

## 8. Payoff-boundary rule
No pre-expiry payoff-boundary/green-area stop is applied. Phase 20 tested 0/50/100/200/400 point boundary buffers, 1/3-minute confirmation, boundary-only and MTM/MFE-filtered variants; the selected boundary candidate failed validation and 2026 holdout and materially worsened drawdown.

## 9. Execution and costs
- One adverse ₹0.05 option tick per leg.
- Correct long/short P&L signs.
- Historical/date-aware NIFTY lot size.
- Six executed orders per completed trade.
- Modeled brokerage: ₹10 per unique executed F&O order.
- Date-aware transaction/exchange charges, STT, SEBI/IPFT, stamp duty and GST.
- No forward-filled, interpolated or synthetic option prices.
- Incomplete observations are excluded and logged.

## 10. Exit precedence
1. Target.
2. 13:30 expiry-day conditional stop.
3. 15:29 expiry fallback.

## 11. Historical final-rule result
- 190 completed trades.
- Net P&L: ₹149,129.53.
- Mean net/trade: ₹784.89.
- Net winning trades: 179/190 (94.21%).
- Profit factor: 2.34.
- Maximum cumulative drawdown: ₹27,336.11.
- Target exits: 178.
- Conditional-stop exits: 5.
- Expiry-fallback exits: 7.
- Baseline-positive trades stopped early: 0.

## 12. Research status
This is the final historical research specification. It is not a guarantee of future performance. Paper/forward execution should validate live bid/ask, spreads, partial fills, latency and broker execution before any live deployment.
