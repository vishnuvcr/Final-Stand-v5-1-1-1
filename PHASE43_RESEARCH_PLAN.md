# Phase 43 Research Plan — VIX-Conditioned NIFTY Options Strategy Sweep

## Research question
Can India VIX, used strictly as an ex-ante volatility-regime variable, identify which major NIFTY weekly options strategy families should or should not be traded after realistic Paytm Money transaction costs, adverse slippage and historical lot sizes?

## Primary aim
Test a finite, preregistered universe of common NIFTY weekly option strategies across VIX regimes and determine whether any VIX-conditioned strategy or regime router produces robust out-of-sample improvement without holdout tuning.

## Secondary aims
1. Compare strategy families on net P&L, drawdown, profit factor, win rate and tail loss.
2. Compare defined-risk strategies after normalization by maximum defined loss.
3. Test VIX level, VIX change and VIX spike regimes.
4. Separate conditional edge from unconditional strategy profitability.
5. Determine whether VIX is best used as a filter, selector or risk-state variable.
6. Preserve the canonical Phase-20/42 strategy as an untouched benchmark.

## Fixed common entry
- NIFTY weekly expiry.
- Entry exactly 4 trading sessions before expiry at 10:00 IST.
- ATM = strike nearest to NIFTY spot.
- Listed strike interval is verified from the chain.
- Primary holding period is to the latest complete observation at or before 15:29 IST on expiry day.
- No intraday target/stop optimization in the structural screen.

## Strategy universe
Core defined/limited-risk structures:
1. Long ATM straddle.
2. Short ATM straddle.
3. Long OTM1 strangle.
4. Short OTM1 strangle.
5. Bull call debit spread: long ATM call / short OTM1 call.
6. Bear put debit spread: long ATM put / short OTM1 put.
7. Bull put credit spread: short OTM1 put / long OTM3 put.
8. Bear call credit spread: short OTM1 call / long OTM3 call.
9. Long call butterfly.
10. Long put butterfly.
11. Iron butterfly.
12. Iron condor.
13. Call broken-wing butterfly.
14. Put broken-wing butterfly.
15. Call 1x2 ratio spread.
16. Put 1x2 ratio spread.
17. Call backspread.
18. Put backspread.
19. Long call calendar.
20. Long put calendar.
21. Reverse call calendar.
22. Reverse put calendar.

The first 18 are the core same-expiry screen. Calendars are included only when both expiries and timestamps are complete. Unbounded theoretical-loss structures are diagnostic-only for promotion.

## Frozen VIX regimes
A. ALL — unconditional comparator.
B. LOW — VIX at/below expanding historical 25th percentile.
C. NORMAL — between expanding 25th and 75th percentiles.
D. HIGH — VIX at/above expanding historical 75th percentile.
E. SPIKE — one-session VIX change at/above expanding historical 90th percentile of prior positive changes.
F. FALLING — one-session VIX change below expanding historical 10th percentile.
G. RISING — one-session VIX change above expanding historical 90th percentile.
H. HIGH+RISING — HIGH and RISING.

All thresholds use only prior VIX observations. The current observation cannot enter its own threshold.

## Research stages
### Stage 0 — governance/cache audit
Check README, research log, error log, Phase-42 status, VIX cache, option-data provenance and benchmark immutability.

### Stage 1 — data/execution audit
Verify expiry calendar, historical lot sizes, strike spacing, complete entry/expiry observations, current/next-expiry linkage, brokerage, statutory costs and one adverse 0.05 tick per leg.

### Stage 2 — structural strategy sweep
For every strategy x VIX regime calculate gross/net P&L, costs, win rate, profit factor, maximum drawdown, tail loss and finite-risk capital-normalized return.

### Stage 3 — VIX regime inference
Use minimum trade-count rules, 10,000 paired-expiry bootstrap intervals, sign-flip tests and Holm-adjusted p-values. Compare every regime with the ALL comparator.

### Stage 4 — chronological VIX router
Freeze only on development data. Candidates may select a strategy family from VIX state, with no learned validation/holdout weights.
Selection:
1. development net P&L non-negative;
2. validation net P&L positive;
3. at least 20 validation trades;
4. validation maximum drawdown <= 1.25x eligible benchmark;
5. +50% cost-stress uplift positive;
6. no single regime/strategy contributes >40% of positive validation uplift.
Freeze top three before 2026 holdout.

### Stage 5 — active-exit extension
Only if Stage 4 has an eligible candidate:
- targets: 25%, 50%, 75%, 100% of initial defined-risk premium/credit where meaningful;
- stops: 0.5x, 1.0x, 1.5x initial defined risk;
- expiry fallback 15:29;
- one-minute confirmation;
- train/validation/untouched-holdout discipline.

### Stage 6 — statistical inference
Primary unit is expiry. Report paired-expiry bootstrap, sign-flip, confidence intervals, drawdown, profit factor and multiple-testing corrected inference.

### Stage 7 — manuscript
Produce the full strategy x VIX matrix, top candidates, rejected candidates, router results, cost-stress results, figures, tables, appendix and reproducibility record.

## Promotion gate
A candidate may be promoted only if it has positive validation and untouched 2026 holdout uplift, acceptable paired-expiry confidence intervals, acceptable drawdown, positive +50% cost stress, adequate holdout opportunities, no concentration, no leakage and no execution defect.

## Stop condition
Close Phase 43 after the registered universe, VIX screen, router, prescribed active-exit extension if eligible, inference and manuscript are complete. New strategy classes or thresholds become Phase 44.