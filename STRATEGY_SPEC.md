# Strategy Specification — Restarted Research (v2)

## 1. Entry-time directional selector

At exactly 10:00 IST on the date that is **4 trading sessions before expiry** (expiry day excluded from the DTE count), identify the nearest available ATM strike from the 10:00 option-chain snapshot.

For OTM rank k, rank strikes outward from ATM separately for calls and puts.

First calculate only OTM6/OTM7/OTM8:
- X_call6 = CE(OTM8) + CE(OTM7) - CE(OTM6)
- X_put6 = PE(OTM8) + PE(OTM7) - PE(OTM6)

Directional rule:
- If X_call6 > X_put6: select the BEARISH strategy (call structure).
- If X_call6 < X_put6: select the BULLISH strategy (put structure).
- If X_call6 = X_put6: record NO_TRADE_TIE rather than inventing a direction.

## 2. n selection inside the selected strategy

For the selected side only, calculate for every n = 6,...,15:

X(n) = Premium(OTM(n+2)) + Premium(OTM(n+1)) - Premium(OTMn).

The requested higher-n preference has no numeric weight supplied. The primary pre-registered rule is:
1. Let X_max be the largest X(n).
2. Keep n where X(n) >= 0.95 * X_max.
3. Select the highest n among those candidates.

Phase 4 will test 90%, 95% and 97.5% thresholds.

If X_max <= 0, record NO_POSITIVE_X and do not enter because the requested 90%-of-credit target is not meaningful for a non-positive credit.

For selected n:
- BULLISH: buy OTMn PE; sell OTM(n+1) PE; sell OTM(n+2) PE.
- BEARISH: buy OTMn CE; sell OTM(n+1) CE; sell OTM(n+2) CE.

## 3. Entry
- Exact timestamp: 10:00 IST.
- DTE: four trading sessions before expiry, excluding expiry.
- ATM and OTM ranks use only strikes present at the 10:00 snapshot.
- No synthetic prices or forward filling.

## 4. Exit

Initial X is the raw 10:00 premium expression for the selected n.

User-specified target:
T = 0.90 * X * lot quantity.

The primary implementation keeps this target basis exactly as specified. Slippage and transaction costs are deducted from realized P&L and are reported separately.

At each available minute after entry, calculate slippage-adjusted gross three-leg P&L. Exit at the first complete timestamp where gross P&L >= T.

If not reached, exit at 15:29 IST on expiry day using the latest complete three-leg observation at or before that time.

No stop-loss.

## 5. Execution and accounting
- One adverse slippage tick per leg, configurable.
- Report raw X, executable entry credit, gross P&L, costs and net P&L separately.
- Date/expiry-aware NIFTY lot size.
- Explicit brokerage, STT, exchange, SEBI/IPFT, stamp duty and GST model.
- Missing observations are logged, not imputed.

## 6. Supersession

This specification supersedes the earlier global 20-candidate selector. Earlier Phase 2 performance results are retained for audit history only and are not results for this restarted strategy.
