# Strategy Specification — Fixed OTM15 Restart (v3)

## 1. Entry-time directional selector

At exactly 10:00 IST, on the date that is 4 trading sessions before expiry (expiry day excluded), identify the nearest available ATM strike using the exact 10:00 option snapshot.

Use the exchange strike ladder rather than the nth available quote. For NIFTY weekly/monthly index options, the strike interval is ₹50. OTM15/16/17 therefore mean exactly 15/16/17 strike intervals away from the selected ATM strike: calls = ATM + n×50; puts = ATM − n×50. Missing exact strikes are exclusions; they are never replaced by a farther available strike.

Calculate:
- X_call = CE(OTM17) + CE(OTM16) - CE(OTM15)
- X_put = PE(OTM17) + PE(OTM16) - PE(OTM15)

Direction:
- X_call > X_put -> BEARISH
- X_call < X_put -> BULLISH
- X_call = X_put -> NO_TRADE_TIE

## 2. Fixed three-leg position

No n-selection, threshold, or optimization is performed.

BULLISH:
- Buy OTM15 PE
- Sell OTM16 PE
- Sell OTM17 PE

BEARISH:
- Buy OTM15 CE
- Sell OTM16 CE
- Sell OTM17 CE

The OTM ranking is determined from strikes available in the exact 10:00 snapshot. No look-ahead from later observations is permitted.

## 3. Entry

- 4 trading sessions before expiry
- 10:00 IST
- Raw X is the selected-side expression above.

## 4. Exit

Target:
T = 0.90 × X × lot quantity

The primary backtest exits at the first complete minute after entry at which the slippage-adjusted gross P&L of the three-leg position reaches or exceeds T.

If target is not reached:
- exit at 15:29 IST on expiry day;
- use the latest complete observation of all three legs at or before 15:29.

No stop loss.

## 5. Execution/accounting

- Primary slippage: one adverse ₹0.05 tick per leg.
- Record raw premiums, executable prices, gross P&L, all modeled charges, and net P&L separately.
- Date-aware NIFTY lot size.
- Brokerage assumption: ₹10 per unique F&O order, six orders per completed trade.
- Model exchange/transaction charges, STT, SEBI/IPFT, stamp duty and GST using date-aware assumptions.
- Missing observations are logged and not imputed.

## 6. Tie/non-positive X

If X_call == X_put, no trade.

If selected-side X <= 0, no trade because the requested 90%-of-X target would be non-positive. This is an explicit data-quality/strategy rule and will be counted.

## 7. Strike-mapping audit correction

The initial v3 implementation incorrectly interpreted OTM15/16/17 as the 15th/16th/17th available strike in the exact snapshot. That can skip strikes when a minute quote is missing. The corrected interpretation uses the fixed NIFTY ₹50 strike interval and exact strike distance. This correction supersedes the initial Phase 7/8 numerical results.

## 8. Supersession

This v3 specification supersedes the earlier v2 strategy. v2 results remain in history for audit only.
