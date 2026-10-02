# Dynamic-n Strategy Specification — Corrected Restart

## 1. Entry snapshot

- NIFTY weekly options.
- Four trading sessions before expiry.
- Exactly 10:00 IST.
- ATM = available strike nearest NIFTY spot at 10:00.
- OTM-n = exact strike distance of n × ₹50.

## 2. Direction selector

Let:
- X_call_direction = CE8 + CE7 − CE6
- X_put_direction = PE8 + PE7 − PE6

Decision:
- call expression higher → BEARISH call-side trade;
- put expression higher → BULLISH put-side trade;
- equality → no trade.

## 3. Dynamic candidate score

For each n from 6 through 15:

X_n = P(OTM(n+2)) + P(OTM(n+1)) − P(OTM n)

All n values must be available on the selected side.

## 4. Weightage / higher-n preference

Primary rule:

threshold = 0.95 × max(X_6,...,X_15)

Eligible n values satisfy:

X_n >= threshold

Select the largest eligible n.

Interpretation: a higher n is preferred whenever its X value is within 5% of the best available X. This is the pre-registered higher-n preference and is not changed after observing returns.

## 5. Position

Selected n:
- Buy OTM-n.
- Sell OTM-(n+1).
- Sell OTM-(n+2).

## 6. Target

Target = 0.90 × X_selected × lot.

Exit at the first complete minute after entry where slippage-adjusted gross P&L reaches target.

Otherwise exit using the latest complete three-leg observation at or before 15:29 IST on expiry day.

## 7. Accounting

- Long leg P&L = exit premium − entry premium.
- Short-leg P&L = entry premium − exit premium.
- One adverse ₹0.05 tick per leg.
- Six orders per round-trip trade.
- Date-aware NIFTY lots.
- Brokerage ₹10/order.
- Audited statutory/transaction fees.
