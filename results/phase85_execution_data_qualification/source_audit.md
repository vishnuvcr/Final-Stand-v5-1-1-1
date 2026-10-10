# Phase 85 — Source audit and decision

Date: 2026-10-10. Scope: public documentation review only; no bulk data downloaded; no backtest run.

## Decision
NO-GO for a new execution-quality numerical replay at this time. Public documentation identifies useful EOD/context data and possible formal routes to richer historical data, but does not establish a freely accessible, rights-cleared dataset with exact-contract bid/ask and depth for the missing sessions. This is not proof that no such dataset exists.

## Findings

### Official NSE daily reports
The derivatives reports list daily volatility, settlement prices, bhavcopy/common bhavcopy, open interest, participant-wise reports, FII derivatives statistics and historical contract-wise price/volume archives. Useful for daily context and EOD checks; not proof of historical bid/ask/depth.
Sources: https://www.nseindia.com/all-reports-derivatives
https://www.nseindia.com/static/resources/historical-reports-capital-market-daily-monthly-archives
Decision: EOD/context only; execution gate fails.

### Official NSE historical products and usage terms
The official historical-data page describes EOD and historical order/trade products for F&O with subscription/contact details. The usage policy defines restrictions and terms for data handling and redistribution. This is a formal route, not a verified free source; no subscription was purchased.
Sources: https://www.nse.in/static/market-data/eod-historical-data-subscription
https://www.nseindia.com/static/market-data/nse-data-policy
Decision: potentially relevant only after written rights and deliverable confirmation.

### Historical dissemination documentation
NSE documentation describes historical F&O data organized into bhavcopy, masters, snapshots, trades and circulars. This shows product categories exist, not that the complete requested files are openly downloadable or redistributable.
Source: https://archives.nseindia.com/content/press/Data_Details_F_n_O.pdf
Decision: potentially relevant after access/rights verification.

### OptionVault
Public repository documentation advertises broad Indian cash/index/futures/options data and mentions tick/Level-2 coverage; it also says the complete bulk dataset is available to licensed users and sample files are for evaluation. Public repository visibility does not establish free, complete, redistributable access.
Sources: https://github.com/QuantDev-stack/OptionVault
https://github.com/QuantDev-stack/OptionVault/blob/main/docs/dataset_coverage.md
Decision: not a verified free bulk source.

### TickBytes
Public project documentation describes tick/1-second/1-minute data and top-five bid/ask prices and quantities. Public documentation alone does not establish target-date coverage, free bulk access, provenance or permission to cache/redistribute raw records.
Source: https://github.com/QuantDev-stack/TickBytes
Decision: unverified candidate; do not ingest until sample, coverage and rights are checked.

### NSE option chain
The official interactive page supports current chain views and CSV download, but does not establish a complete authorized historical quote/depth archive for the target dates.
Source: https://www.nseindia.com/option-chain
Decision: context/current checks only; not a validated replay source.

## Decision matrix

| Source | Publicly supported capability | Free exact historical bid/ask/depth verified? | Bulk storage/publication rights verified? | Result |
|---|---|---:|---:|---|
| NSE daily reports | EOD contract/market context, OI and participant reports | No | Product-dependent | EOD only |
| NSE historical products | Formal historical EOD/order-trade route | No; subscription route | No | No purchase without approval |
| NSE dissemination docs | Snapshots and trades are product categories | No open archive verified | No | Access required |
| OptionVault | Broad data advertised; full data licensed | Not verified | Not verified | Do not bulk download |
| TickBytes | Tick/Level-2 fields advertised | Not verified for target dates | Not verified | Metadata-only follow-up |
| NSE option chain | Interactive chain/current download | No historical archive verified | Not established | Not a replay source |

## Next gate
Before any acquisition, record (1) exact license and automated-use/storage/publication terms, (2) schema with timestamp/timezone, expiry, strike, option side, bid/ask and quantities, (3) proof of coverage for 2026-07-28 and 2026-08-04 and the full registered interval if applicable, (4) source revision and file hashes, and (5) frozen Paytm Money costs, slippage, latency and fill rules.

Do not treat missing observations as zeros/losses, tune around missing dates, use paid sources without approval, or access the Phase 83 sealed holdout. No reviewed source passes every gate on current public documentation alone.
