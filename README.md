# Final Stand v5 1-1-1-1

Systematic research repository for options strategy testing.

## Current status
- Phase 3 — initial stop-loss experiment completed.
- Primary sample: NIFTY 50 weekly index options, 2024-01-01 through 2025-12-31.
- Entry: 4-DTE market-session convention, 10:00 IST.
- Strategy selector: compare OTM7 + OTM8 - OTM6 for calls and puts; trade the higher positive premium expression.
- Base target: 90% of the entry flatline premium.
- Execution model: 1-minute closes, one adverse option tick per leg, six executed orders per round trip.
- Paytm brokerage assumption: ₹20/order for the primary run; configurable for older-account ₹10/₹15 rates.
- Baseline result: 122 trades; 42.6% winners; mean net P&L about -11.23 option points/trade after modeled costs.
- Call selections: 23 trades, mean -14.57 points.
- Put selections: 99 trades, mean -10.45 points.
- Stop-loss grid: 0.25x–2.00x of entry flatline premium; every tested candidate remained negative.
- 0.25x produced the least-negative mean in this grid (-9.15 points), but stopped out on 82.0% of trades; this is not a validated live-trading rule.

## Data limitations
The selected public 1-minute dataset has incomplete observations in parts of 2026. Those partial 2026 observations are excluded from the primary conclusion.

## Research files
- RESEARCH_PLAN.md
- STRATEGY_SPEC.md
- RESEARCH_LOG.md
- ERROR_LOG.md
- results/summary.csv
- results/stoploss_summary.csv
- results/trades.csv
- results/missing.csv

## Important
This is research, not a trading recommendation. The structure has an uncovered tail. Robustness, out-of-sample validation, liquidity/bid-ask modeling, and a more accurate historical lot-size/charge schedule are still required before any live-use conclusion.
