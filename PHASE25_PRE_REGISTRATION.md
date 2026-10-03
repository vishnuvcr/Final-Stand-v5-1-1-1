# Phase 25 Pre-registration — Alternative Direction Choosers

## Research question
Can the Phase-20 direction chooser be improved by replacing the specific OTM6/7/8 premium-curvature comparison with other point-in-time option-price, implied-volatility, OI/volume, cross-market, or opening-state directional signals, while keeping every other strategy rule unchanged?

## Scientific isolation
Only the direction chooser changes. Dynamic-n selection, target, expiry-day conditional stop, expiry fallback, slippage, brokerage, statutory charges, lot sizes, and all other execution rules remain identical to Phase 20.

Baseline:
- X_call = CE8 + CE7 − CE6.
- X_put = PE8 + PE7 − PE6.
- X_call > X_put => bearish/call-side structure.
- X_put > X_call => bullish/put-side structure.

## Temporal split
- Training: through 2023-12-31.
- Validation: 2024-01-01 through 2025-12-31.
- Untouched holdout: 2026-01-01 through 2026-09-30.

Candidate selection uses training data only.

## Preregistered candidate families

### A. Premium-curvature alternatives
For k = 6,...,15: X_type,k = P(k+2) + P(k+1) − P(k). Choose the side with larger X.
Also test NX_type,k = X_type,k / P(k). Choose the side with larger normalized score.

### B. Matched call/put relative-price signal
For k = 6,...,15: R_k = log(CE_k / PE_k). Positive R_k => bullish/put-side; negative => bearish/call-side.

### C. Matched IV-spread signal
For k = 6,...,10: IVS_k = CE_IV_k − PE_IV_k. Positive IVS_k => bullish/put-side; negative => bearish/call-side.

### D. OI and volume PCR signals
For k = 6,...,10: PCR_OI_k = log(PE_OI_k / CE_OI_k), PCR_VOL_k = log(PE_VOL_k / CE_VOL_k).
Because the literature contains both predictive and contrarian interpretations, both sign conventions are preregistered: momentum and contrarian.

### E. Direct underlying/cross-market signals
- NIFTY 1-session return: positive => bullish.
- 10:00 return from prior close: positive => bullish.
- overnight gap: positive => bullish.
- equal-weighted global-equity return across S&P 500, Nasdaq, Dow, Nikkei, Hang Seng, KOSPI and Shanghai: positive => bullish.

### F. Fixed aggregate signals
- Median of R_6...R_10.
- Median of IVS_6...IVS_10.
- Majority vote of premium-ratio, IV-spread, global-equity, NIFTY 10:00 return, and PCR-OI contrarian. Ties => no trade.

No additional signal family may be added after observing results.

## Data handling
A candidate that cannot produce a directional decision from required entry-time fields is a no-trade. No imputation is allowed.
Candidate P&L uses the already reconstructed canonical and opposite-side dynamic-n ledgers. If the opposite-side ledger is unavailable, selecting that side results in no-trade.

## Training eligibility
1. Training net uplift > ₹0.
2. Training winner retention >=95%.
3. Zero baseline-positive trades become losing trades.
4. Candidate coverage >=95% of the 190-trade universe.
5. At least two training trades improve because the alternative selected the opposite side.

If several candidates pass: highest training winner retention, then lowest direction-switch count, then highest training uplift, then highest coverage.

## OOS promotion gate
- Validation uplift > ₹0.
- Holdout uplift > ₹0.
- Validation winner retention >=90%.
- Holdout winner retention >=90%.
- Zero baseline-positive trade becomes a loss in either OOS period.
- Validation and holdout maximum drawdown no more than 5% worse than baseline.
- Candidate coverage >=95% in both OOS periods.
- At least two OOS trades where the alternative direction improves net P&L.

Failure means Phase-20 OTM6/7/8 remains the direction chooser.

## Diagnostics
Report direction agreement, switch counts, retrospective chooser accuracy against the better of canonical/reverse outcomes, corrected losses, winning-trade damage, P&L uplift, profit factor, maximum drawdown, worst trade, and bootstrap confidence intervals.
Retrospective accuracy is diagnostic only and cannot select a candidate.

## Literature rationale
Option-price and implied-volatility transformations have documented relationships with subsequent underlying returns, including relative call/put prices, implied-volatility spreads/skew, and option volume ratios. These motivate the candidate families but do not establish an edge for NIFTY weekly options or this strategy.

Relevant sources:
- Balyeat & Erturk, relative OTM call/put prices and aggregate returns.
- Pan & Poteshman (2006), option volume and future stock prices.
- Ratcliff (2013), relative option prices/risk-neutral skew and index returns.
- Implied-volatility spread/skew literature.
- NSE India VIX methodology.

## Stopping rule
Phase 25 ends after the complete preregistered candidate grid is evaluated. No post-result signal engineering or additional direction rule may be introduced. If no candidate passes, OTM6/7/8 remains the final chooser.