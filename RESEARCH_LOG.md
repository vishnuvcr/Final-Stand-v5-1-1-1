# Research Log

## 2026-10-02 — Research restart
- Restarted because the prior implementation did not exactly match the latest strategy definition.
- Created branch phase-1-restart-strategy-v2.
- Prior global n=6..15 x Call/Put results are superseded.

## 2026-10-02 — Direction selector locked
- Stage 1 uses OTM6/7/8 only.
- X_call6 > X_put6 selects the user-defined BEARISH call structure.
- X_call6 < X_put6 selects the user-defined BULLISH put structure.
- Exact equality is NO_TRADE_TIE.

## 2026-10-02 — High-n selector locked
- Stage 2 evaluates n=6..15 only on the Stage-1-selected side.
- Because no numeric weight was specified for higher n, the primary rule is X(n) >= 95% of selected-side X_max, then choose the highest n.
- 90% and 97.5% thresholds are reserved for robustness analysis.
- Non-positive X_max is recorded as NO_POSITIVE_X with no fabricated entry.

## 2026-10-02 — DTE correction
- "4 trading Days to expiry" is interpreted as four trading sessions before expiry, with expiry=0 DTE.
- Ordinary Thursday weekly expiry therefore uses preceding Friday 10:00, not Monday 10:00.

## 2026-10-02 — Target locked
- Target is exactly T = 0.9 * X_selected * lot quantity.
- X_selected is the raw 10:00 premium expression for final selected n.
- Slippage and transaction costs affect realized P&L and are reported separately.

## 2026-10-02 — Data/provenance audit
- Primary dataset documentation was rechecked for 1-minute NIFTY options schema and partial far-strike coverage.
- Primary executable option files begin 2021-05-27.
- Current Paytm Money F&O FAQ states Rs 10 brokerage per unique executed order; historical fee differences will be sensitivity-tested.
