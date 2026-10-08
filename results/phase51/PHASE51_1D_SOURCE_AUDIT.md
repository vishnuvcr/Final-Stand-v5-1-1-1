# Phase 51-1D — Commercial / UI / External Data-Source Audit
Date: 2026-10-09

## Purpose
Resolve the Phase-51 frozen OOS option-data gap for 2026-07-28 and 2026-08-04 without changing the protected OOS window or inspecting strategy P&L.

## Frozen gap
- Fresh OOS: 2026-04-21 through 2026-08-04.
- Primary RISSIN 1-minute options source ends at expiry 2026-07-21.
- Thetrademarkk supplemental files nominally named 2026-07-28 and 2026-08-04 were already audited and actually end on 2026-07-02; they are rejected.
- No Phase-51 OOS strategy P&L has been calculated from incomplete option coverage.

## Source decisions

| Source | Minute historical data | Expired contracts | Raw export/API evidence | Coverage relevant to 2026-07-28/08-04 | Decision |
|---|---|---|---|---|---|
| StockMock | YES — official terms say backtesting uses 1-min OHLC | YES for the supported historical weeks/months | No documented public raw export/API found in this audit | Site advertises historical simulator; exact gap-session export not verified | ORACLE / calibration only |
| StockMojo | YES — official pages advertise 1-minute historical NIFTY chain replay with price, OI, volume, IV and Greeks | YES — pages explicitly describe expired options | No documented public raw export/API found; historical page contrasts its UI with raw CSV download | Exact 2026-07-28 and 2026-08-04 contract-level export not verified | ORACLE / validation only |
| FNOTrader | YES — official FAQ advertises NIFTY/BANKNIFTY 1-minute archives; other FNOTrader docs describe 1-minute option OHLC/OI/IV | YES / backtest archive | Public MCP/API surface is documented, but no installed repo connector/account access is available here | 2026 dates are within claimed archive | HIGH-PRIORITY authenticated oracle/acquisition candidate |
| Upstox | YES — official expired historical candle API supports 1-minute | YES — official expired contract API | Authenticated API; Plus plan required for expired historical candles | Directly suitable if token is configured | HIGH-PRIORITY raw acquisition |
| OptionsData.shop | YES — full-chain 1-minute Parquet, all strikes/expiries, OI | YES | Downloadable after purchase; free sample is schema-validation only | Catalog explicitly spans 2023 to Sep-2026 and therefore includes the frozen gap | HIGHEST raw commercial candidate |
| NSE official | YES — paid 1-minute/5-minute snapshot feed and paid historical order/trade data | YES | Official licensed data channels | Direct official provenance; access is commercial/licensed | PRIMARY exchange route, commercial |
| MoneyTicks | YES — claims 1-minute OHLC/OI for expired NIFTY/BANKNIFTY/SENSEX, API + CSV/XLSX | YES | API/export claimed | Archive claimed through present | WAITLIST / NOT CURRENTLY AVAILABLE FOR PURCHASE |
| QuantFlo | YES — site advertises 1-minute options since 2021 and net-of-cost backtests | YES | No public raw export/API for underlying historical tape found | 2026 dates should be inside claimed history | INDEPENDENT BACKTEST ORACLE |
| AlgoTest | YES — official docs/video advertise minute-by-minute historical option backtesting | YES / historical backtests | No raw archive export/API documented in this audit | Exact frozen-gap contract availability not independently verified | INDEPENDENT BACKTEST ORACLE |
| thetrademarkk/india-index-options-1m | YES | Partial | Raw Parquet public | Failed actual endpoint coverage and overlap gate | REJECTED |
| RISSIN HF NIFTY 1m options | YES | YES for available files | Raw Parquet public | Ends 2026-07-21 in frozen cache | PRIMARY FROZEN SOURCE, INCOMPLETE AT OOS ENDPOINT |

## Source-specific evidence

### StockMock
Official Terms and Conditions state that StockMock uses 1-minute OHLC data for backtesting and that the service exposes same-week/same-month historical data. The current site also advertises simulator/backtesting functionality. We did not find a documented public API or export that authorizes bulk extraction of the minute tape.
Use: independent strategy-level comparison / spot-check oracle. Do not scrape or circumvent access controls.

### StockMojo
StockMojo's NIFTY time-series pages state that historical option-chain snapshots can be replayed minute-by-minute with strike-level OI, volume, premium, IV and Greeks, and its historical-option page explicitly covers expired options. Its historical page is presented as an interactive chart rather than a raw CSV export. We did not find a documented public raw API/export in this audit.
Use: independent chain/strategy oracle; not a raw repository source unless an authorized export/API becomes available.

### FNOTrader
FNOTrader's official FAQ says NIFTY/BANKNIFTY options have 1-minute historical coverage going back years. Its MCP documentation advertises programmatic AI access to the same backtest engine. Because this environment has no FNOTrader connector/account, it is not yet a directly ingestible repo source.
Use: first external platform to prioritize for an authorized backtest/oracle comparison once access is available.

### Upstox
Official Upstox API documentation confirms expired option contracts can be enumerated by underlying and expiry; expired historical candles support 1-minute OHLC plus volume and OI; expired historical candle access requires an Upstox Plus plan. The repo already contains the Phase 51-1C acquisition script and it fails closed when the required access token is absent.
Use: raw acquisition if UPSTOX_ACCESS_TOKEN is legitimately configured.

### OptionsData.shop
The public catalog advertises NIFTY options at 1-minute resolution from 2023 through September 2026, every strike and expiry, with OHLC, volume and OI in Parquet. Its free sample is only for schema validation and does not cover the missing July/August OOS dates. The commercial catalog explicitly covers the needed dates.
Use: strongest commercially available raw-data candidate for the missing blocks, subject to authorized purchase/download and independent equivalence audit before OOS replay.

### NSE official
NSE's public historical contract-wise page provides daily contract OHLC/LTP/OI and notes a 90-day public query limit. NSE separately advertises licensed 1-minute/5-minute snapshot data and paid historical order/trade data.
Use: official provenance and validation; minute data requires licensed access rather than the free contract-wise page.

### MoneyTicks
MoneyTicks currently advertises 1-minute OHLC/OI expired-option history and API/export delivery but simultaneously states that data access is not currently being sold while licensing is finalized.
Use: monitor only; not an available acquisition path today.

### QuantFlo / AlgoTest
Both are useful independent black-box backtest checks, but neither was found to expose an authorized raw historical-tape export in public documentation during this audit. They should not be treated as primary numerical evidence unless the exact data/engine provenance and export semantics are independently validated.

## Research consequence
The correct research action is NOT to substitute a UI screenshot or an opaque platform result for raw data. The frozen OOS remains blocked.

Priority order for the next acquisition gate:
1. Upstox authenticated raw 1-minute expired candles.
2. Authorized OptionsData.shop commercial raw Parquet for 2026-07-28 and 2026-08-04 (ideally with common-expiry overlap sample first).
3. FNOTrader authorized MCP/backtest oracle for independent strategy-level reconciliation.
4. StockMock and StockMojo as independent UI/backtest cross-checks.
5. NSE licensed 1-minute snapshot/order-trade data if commercially obtainable.

No strategy tuning, strike selection, or OOS P&L inspection is permitted until the source-quality gate passes.