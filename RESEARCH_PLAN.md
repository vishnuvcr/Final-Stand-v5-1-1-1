# Research Plan — Restarted NIFTY Ratio Strategy (v2)

## Research question
Does the restarted two-stage directional-selection and high-OTM-preference 3-leg ratio strategy produce positive gross and net returns after realistic execution costs on historical NIFTY weekly index options?

## Locked primary algorithm

### Stage 1 — Direction
X_call6 = CE8 + CE7 - CE6
X_put6 = PE8 + PE7 - PE6

If X_call6 > X_put6 -> BEARISH call structure.
If X_call6 < X_put6 -> BULLISH put structure.
Exact equality -> NO_TRADE_TIE.

### Stage 2 — n
For the selected side only, calculate X(n) for n=6..15.
- X_max = max X(n).
- Eligible n satisfy X(n) >= 95% of X_max.
- Select the highest eligible n.
- If X_max <= 0, record NO_POSITIVE_X and do not enter.

The 95% rule is the primary transparent implementation of the requested higher-n preference with significant X. Phase 4 tests 90%, 95% and 97.5%.

### Stage 3 — position
BULLISH:
- buy OTMn PE
- sell OTM(n+1) PE
- sell OTM(n+2) PE

BEARISH:
- buy OTMn CE
- sell OTM(n+1) CE
- sell OTM(n+2) CE

### Stage 4 — exit
T = 0.90 * X_selected * lot quantity.
Exit at the first complete minute where slippage-adjusted gross P&L >= T.
Otherwise exit at 15:29 IST on expiry day using the latest complete three-leg observation.
No stop-loss.

## DTE definition
"4 trading Days to expiry" means four trading sessions before expiry, with expiry day = 0 DTE. For an ordinary Thursday expiry, entry is the preceding Friday at 10:00 IST. Holiday/exception expiries use actual trading sessions and are logged.

## Data
Primary executable source: thetrademarkk/india-index-options-1m. Public documentation describes 1-minute NIFTY spot and option-chain OHLCV(+OI), option files with strike, option type and expiry, and partial far/illiquid strike coverage. Current executable option files begin 2021-05-27.

The earlier Zenodo 2019–2020 source remains rejected for the weekly-contract primary test because row-level expiry identification was not available.

## Cost/execution
Primary:
- one adverse tick per leg, configurable;
- date-aware NIFTY lot size;
- Paytm Money F&O brokerage assumption of Rs 10 per unique executed order according to its current F&O FAQ;
- statutory/exchange charges explicitly modelled.
Historical pricing differences are a sensitivity item.

## Research phases
1. Phase 1 — restarted specification and implementation audit
2. Phase 2 — restarted primary backtest
3. Phase 3 — statistical analysis
4. Phase 4 — robustness and sensitivity
5. Phase 5 — complete manuscript

Phase 2 must persist Stage-1 directional X, all Stage-2 candidates, selection threshold, selected n, trade results and missing observations.

## Stop condition
Stop after Phase 5.

## Supersession
All prior Phase 2 results using the global 20-candidate selector are superseded and must not be used as evidence for this restart.
