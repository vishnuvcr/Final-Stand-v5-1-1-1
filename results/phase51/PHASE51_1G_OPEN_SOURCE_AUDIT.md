# Phase 51-1G — Open-source alternatives audit

## Objective
Find an independently sourced, openly accessible 1-minute NIFTY option archive capable of covering the frozen missing expiries 2026-07-28 and 2026-08-04.

## Results

| Source | Raw 1m data | Missing expiries | Status |
|---|---|---|---|
| thetrademarkk/india-index-options-1m | Yes | Files exist by name, but actual bytes stop 2026-07-02 | REJECTED in 51-1E |
| codepyx23/india-index-options-1m-bucket | Public bucket advertised; requested `options/NIFTY/*.parquet` path returned 404 in Actions | Not available at advertised path | REJECTED / NOT-REPRODUCIBLE |
| Kaggle free NIFTY option-chain dataset | Yes, 1-minute, 6.8 GB | Coverage reported through 2026-03-24 only | CANNOT COVER FROZEN GAP |
| bhav / Backtesting-NSE sample | Yes, 1-minute ATM option sample | Jul-2025 through Jun-2026; June has ±2 chain | CANNOT COVER FROZEN GAP |
| SauMStats/nifty-options-data-engine | Open-source engine; documents `Nifty2026` Parquet layout | Repository contains code/docs, not the documented live data archive | NOT RAW SOURCE |
| pawan625 HF Space | Uses cached Kite 1-minute option candles and has July-2026 backtests | Data is generated through Kite with a paper token; raw full-chain cache is not exposed as an independent archive | NOT INDEPENDENT RAW SOURCE |
| QuantDev-stack/TickBytes | Open repository with sample tick/1-sec/1-min option structures | Full 300+ GB archive is licensed; public repo contains samples | LICENSED / SAMPLE ONLY |
| QuantDev-stack/OptionVault | 1m/1s options + Greeks | Full dataset licensed; samples only | LICENSED / SAMPLE ONLY |
| FNOTrader / OptionsData.shop | Relevant full archives | Commercial/authorized access | OUTSIDE OPEN-SOURCE TRACK |

## Scientific decision

No independently reproducible open-source raw dataset found so far passes the minimum feasibility requirement for the frozen missing expiries.

The frozen OOS window remains unchanged. No strategy P&L is calculated from:
- daily option-chain websites,
- synthetic data,
- broker-generated data without authorization,
- partial/sample datasets,
- or oracle backtest outputs.

## Important positive findings

The public ecosystem is useful for independent validation:
- Kaggle provides a large 1-minute option-chain dataset but it ends before the missing 2026-04-to-08 window.
- bhav provides a real offline NIFTY 1-minute option sample through June 2026.
- pawan625 demonstrates that 1-minute option candles for the 2026-07-28 expiry were obtainable through Kite, but this is broker-generated data rather than an independently archived open dataset.
- SauMStats provides an open research engine and documents a 2026 live-data layout, but the actual Parquet archive is not present in the public repository.

## Next open-source trigger

Do not purchase or bypass access. Resume this phase only if a new public raw archive becomes discoverable or a user supplies an authorized archive. Any new source must pass the existing RISSIN equivalence and >=95% replay-entry/exit coverage gates before OOS P&L.
