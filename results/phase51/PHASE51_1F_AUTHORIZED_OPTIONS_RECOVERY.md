# Phase 51-1F — Authorized Options Recovery

## Objective
Recover reproducible 1-minute NIFTY option data for the two frozen missing expiry blocks (2026-07-28 and 2026-08-04) without changing the frozen OOS window and without selecting a source from strategy performance.

## Closed-source evidence entering this phase
- Primary RISSIN source ends at 2026-07-21.
- Public HF supplemental source was actually downloaded and rejected: its files named 2026-07-28 and 2026-08-04 both stop on 2026-07-02; common-expiry coverage versus RISSIN was 34.57%, 14.95% and 4.60%; 7-Jul p95 relative error was 14.79 bp.
- Therefore the HF source is closed and will not be retried unless its external bytes materially change again.

## Finite recovery matrix

| Priority | Route | Data capability | Authorization required | Decision rule |
|---|---|---|---|---|
| 1 | Upstox expired instruments + expired 1-minute candles | Exact expired contracts; 1-minute OHLCV+OI | UPSTOX_ACCESS_TOKEN and Plus | Acquire then run full source-equivalence gate |
| 2 | OptionsData.shop commercial archive | Full NIFTY chain, 1-minute, every strike/expiry, OI | Authorized purchase/download | Validate bytes before replay |
| 3 | ICICI Breeze historicalcharts | Exact option strike/expiry, 1-minute OHLCV+OI | Breeze API credentials/session | Enumerate required contracts and validate |
| 4 | Dhan expired-options rolling API | 1-minute rolling ATM-relative strikes, OHLCV/OI/IV/spot | Dhan access token | Use only if required frozen strategy legs are representable and overlap gate passes |
| 5 | FNOTrader | 1-minute NIFTY archive and backtesting oracle | Paid account/connector | Oracle only unless authorized reproducible export is obtained |
| 6 | MoneyTicks | Advertised 1-minute expired option history/API | Access currently unavailable for purchase | Catalog/oracle only unless authorized API access is obtained |

## Gate for any accepted raw source
1. Exact 2026-07-28 and 2026-08-04 coverage.
2. SHA-256 and byte-size capture.
3. Canonical schema mapping.
4. Duplicate contract-minute-key check.
5. Full expiry-session continuity and endpoint check.
6. Common-expiry equivalence against RISSIN using the fixed 10,000-row minimum, >=80% coverage, median abs <=0.05, p99 abs <=1.00, p95 relative error <=10 bp, and mean signed abs <=0.05.
7. Mandatory replay-entry/exit coverage >=95%.
8. Only after all gates pass may TT-03 / TT-03 OTM350 frozen OOS replay begin.

## Stop condition
If no authorized raw route is configured or purchased, Phase 51 remains DATA-BLOCKED. The OOS window is not shortened, and no P&L is calculated from partial data.

## Source notes
- Upstox official documentation currently states expired historical candles support 1-minute and require an Upstox Plus plan.
- OptionsData.shop currently advertises NIFTY 1-minute full-chain history through Sep-2026 and specifically a 29-Jun-2026 to 25-Sep-2026 pack containing the missing expiries.
- ICICI Breeze historicalcharts documents 1-minute option candles with expiry, right and strike parameters plus OHLCV and OI.
- Dhan documents minute-level expired rolling option data up to five years, strike-wise relative to ATM, with OHLCV/OI/IV and spot.
- FNOTrader advertises 1-minute NIFTY history and paid backtesting; it is retained as an oracle unless raw export provenance becomes reproducible.