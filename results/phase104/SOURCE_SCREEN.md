# Phase 104 Source Screen — EOD Contract-Identified Stock Options

**Screen date:** 2026-10-11

| Source | What official/public evidence supports | Potential use | Remaining blocker |
|---|---|---|---|
| NSE daily UDiFF F&O bhavcopy archive | Official derivatives reports list the UDiFF daily file; Phase 103 already downloaded five files and parsed symbol, expiry, strike, CE/PE and daily OHLC, volume and OI. | Daily contract identity and coverage audit. | Reuse, raw caching, retention and derived-publication terms are not independently verified. This phase publishes aggregate outputs only. |
| NSE EOD/historical order/trade data | Official NSE describes historical order/trade products for F&O and provides a vendor-inquiry route. | Potential future tick/order-level execution/identity evidence. | Product details, price, historical depth, delivery rights, API automation and retention terms require written confirmation / subscription. No purchase initiated. |
| Global Datafeeds | Vendor says it provides NFO historical data APIs, minute/EOD data, and tick history with stated horizon limits. Source: https://globaldatafeeds.in/apis/ and https://globaldatafeeds.in/global-datafeeds-apis/global-datafeeds-apis/rest-api-documentation/function-gethistory/ | Commercial alternative for exact-contract historical prices if matching old contracts are supported. | Pricing and actual contract identity, historical bid/ask availability, retention and use terms not verified. Its public terms limit data to single-subscriber charting/analysis and disallow gaming/virtual-trading applications without approvals; verify that automated research/testing is permitted before use. |
| Open-source daily archive mirror | The repository https://github.com/SantoshSrinivas79/NSE-FNO-Data-bank says it validates official daily NSE F&O bhavcopy files and has an MIT code license while noting market data remain subject to NSE rights. | Discovery/implementation reference only. | Code license does not grant a market-data licence. Do not commit its raw archive or infer redistribution rights. |
| Dhan expired-options rolling API | Phase 103 shows 28/28 request-level row returns, but only 3/88 full-session exact-strike profiles match NSE EOD on all four OHLC fields, all expiry rank 1 instead of expected rank 2. | Archived access diagnostic only. | Phase 103 terminal NO-GO; no further selector/date/stock/offset fishing in that phase. |

## Official references
- NSE daily derivatives reports: https://www.nseindia.com/all-reports-derivatives
- NSE individual-stock option specifications: https://www.nseindia.com/static/products-services/equity-derivatives-individual-securities
- NSE historical/EOD data subscription: https://www.nseindia.com/static/market-data/eod-historical-data-subscription
- NSE Data & Analytics data vending: https://www.nseindia.com/static/nse-data-and-analytics/data-information-vending
- NSE STT rates effective 2026-04-01: https://www.nseindia.com/static/products-services/equity-derivatives-securities-transaction-tax
- Paytm Money pricing: https://www.paytmmoney.com/stocks/pricing

**Access vs rights:** technical download success is not proof of rights to cache, redistribute or publish raw records. The working policy is aggregate-only outputs until the relevant rights are documented.

## Final Phase 104.1 audit result and Phase 104.2 stop decision — 2026-10-11

Official NSE archives in run [38129389678](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38129389678) parsed successfully for 22 trading days in the 30-calendar-day sample. The fixed five-stock set had 18,082 daily stock-option rows, 100% identity and OHLC completeness, zero duplicate daily contract keys, and zero date mismatch/source-schema errors. Zero-volume observations (5,922) were separated from positive-volume (12,160) and missing (0) records. Per-symbol counts are in [NSE_EOD_DATA_AUDIT.md](NSE_EOD_DATA_AUDIT.md), and the figure is [eod_contract_rows_by_symbol.svg](figures/eod_contract_rows_by_symbol.svg).

The official daily archive is accepted for bounded daily contract identity and descriptive coverage, not for executable fills. Raw NSE records are not cached or published because the right to do so was not independently verified. Paytm Money fee arithmetic is available as a source-based, date-effective scenario model, but account-specific brokerage and contract-note reconciliation remain outstanding. Historical bid/ask/depth, queue and fill evidence are missing, so strategy P&L remains NO-GO. See [execution/cost gate](EXECUTION_AND_COST_GATE.md) and [final manuscript](PHASE104_FINAL_MANUSCRIPT.md).


## Final locked audit and closeout confirmation — 2026-10-11

The final locked-workflow run [38129926977](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38129926977) again passed the Phase 104 unit-test, official archive acquisition, aggregate-only publication and checkpoint steps. The JSON's run ID matches this run; 22 daily archives and 18,082 records passed the identity/OHLC gates. This is a reproducibility confirmation, not a strategy test. The phase stays closed with executable strategy P&L NOT RUN.
