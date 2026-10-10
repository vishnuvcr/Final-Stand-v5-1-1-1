# Phase 70 — Cost-effective historical options data source review
Date: 2026-10-10
Status: PUBLIC-SOURCE REVIEW COMPLETE; purchase not authorized; no vendor coverage accepted without file-level validation.

## Research question
What is the lowest-cost, fit-for-purpose data acquisition plan for Final Stand's Indian options research, including historical expired contracts, option-chain/OI factors, spot/futures/synthetic futures, volatility and robust execution-cost analysis?

## Recommendation
First choice to evaluate: OptionsData.shop NIFTY Complete 1-minute pack, currently listed at ₹7,999 one-time (vendor lists no GST added) with SAVE10 advertised through 31 Oct 2026. Its listed coverage is rolling three years, 3 Oct 2023–29 Sep 2026 on the product page reviewed, with option files through 25 Sep 2026 and spot/futures through 29 Sep 2026. Current pack catalogue can shift dates as the rolling window moves; get exact date list at order time. This is the most economical single bundle found publicly that includes NIFTY full-chain options, futures and spot. It is not a complete solution for all data needs.

Before paying, request written confirmation that 28 Jul 2026 and 4 Aug 2026 each contain the required expiry/strike/call-put contracts and usable intraday rows, and verify the date/contract file manifest. Phase 68 found two HF files named for those dates were stale and had zero target-session rows; do not assume a new vendor fixes this until exact files are checked. Vendor free sample is only 15–17 Sep 2026, so it verifies format/schema, not those target dates.

## Public-source comparison

### OptionsData.shop
- NIFTY options 1-minute full chain: ₹7,249 for three years, option-only; OI on every row per vendor; Parquet; one-time purchase.
- NIFTY Complete options + futures + spot 1-minute: ₹7,999, three years, listed 3 Oct 2023–29 Sep 2026 in the product page reviewed.
- NIFTY + SENSEX Complete: ₹11,999 for three years; useful only if the research expands to BSE/SENSEX.
- NIFTY options + spot 1-second: ₹23,999 for full archive Jan 2023–Sep 2026; not justified as first purchase while the 1-minute data gate remains unresolved.
- NIFTY Complete 1-year pack listed at ₹3,999; potentially useful for a smaller pilot, but does not cover the whole multi-year research period.
- Coupon SAVE10 is advertised through 31 Oct 2026 on some current product pages; verify at checkout.
- Vendor says data are broker-feed-derived, not official/exchange-authorised; internal research/backtesting permitted, raw redistribution prohibited.
- Standard files have OHLC, volume, OI, expiry/strike/right; no bid/ask, depth or tick-by-tick trades. Some older option files have an IV column, described by vendor as feed-provided and unverified; IV coverage is not uniform. Greeks are not included.
- Schema/layout varies across historical files, so ingestion must normalise fields and validate timestamps, expiry, OI, duplicate rows and coverage.

### TrueData
- Workspace pricing page lists ₹3,999/month for Pro and ₹5,999/month for Power before 18% GST; Power advertises 3-year intraday history and market replay. API access is separate and requires application/approval. Confirm historical expired-option coverage, export rights, exact contract coverage and whether a data archive can be retained before subscribing.
- TrueData API advertises historical data, live option chain and live Greeks; public pricing for the exact historical dataset/API scope is quote-based/not established in this review.
- Support forum says expired options available via API from Feb 2020, but this is old information and must be reconfirmed in writing.
- Potentially useful if we need ongoing updates, API ingestion, replay or live quote/Greek access; likely more expensive than one-time historical pack for a bounded backtest.

### Global Datafeeds
- Advertises historical tick/minute/day data and real-time L1 data with best bid/ask, plus real-time option chain and Greeks.
- Pricing is tailored/quote-based; no public price was verified. Public page lists historical availability as tick 7 days, 1–4 minute 3 months, 5–10 minute 4.5 months, 15–30 minute 6 months and daily since 2010; confirm product-specific depth and expired-option archive before considering it for multi-year historical options.
- Better candidate for a quote if execution-quality L1 data is required, not yet proven cost-effective for this historical study.

### NSE official historical data
- Free public historical contract-wise price/volume and daily derivatives reports can support end-of-day checks, daily OHLC/OI/settlement and source validation.
- NSE Data & Analytics offers paid historical/order/trade data with quote-based/specified tariff. Not a budget choice until a precise requirement and quote are obtained.
- Daily official data do not substitute for intraday full-chain historical bars or historical best bid/ask snapshots.

### Zerodha Kite Connect
- Historical candle API supports OHLCV and optional OI for available instrument tokens. Official documentation says instrument tokens are flushed on expiry; continuous data covers expired futures daily bars, not expired option contracts. The vendor forum explicitly says expired options candles are not offered. Do not plan the long expired-option archive around Kite alone.
- Can be useful for ongoing capture of contracts while live, if we implement and maintain our own cache and verify terms; this does not repair historical gaps retrospectively.

### Free/public sources and derived variables
- NSE official reports: daily contract-wise data, bhavcopy/reports, settlement and OI checks.
- Global indices, India VIX, rates, FX, gold and market proxies: prefer official exchange/regulator/central-bank or well-documented public sources where available; cache provenance, timestamps, licence and missingness. Avoid assuming a free adjusted history is identical to point-in-time data.
- FII/DII: official exchange/NSDL/NSE daily published reports where accessible; record release dates and avoid look-ahead leakage.
- Corporate actions and constituents: exchange/company filings and point-in-time dates.
- Greeks: compute from validated option prices, spot/futures, expiry/time-to-expiry and a documented rate/dividend model if required; label as model-derived, not observed. Vendor feed IV should be treated as unverified and nonuniform.
- News/sentiment: public feeds only where permitted; timestamp event availability and preserve citations/licences. Do not use present-day revisions as if known historically.
- Kaggle, GitHub and Hugging Face may contain useful research data but should be treated as discovery/secondary sources; validate lineage, timestamps, completeness, terms and actual target dates before any backtest. Phase 68 demonstrated that filenames can point to stale content.

## Cost plan
1. Spend ₹0 first: download the vendor's free sample; test Parquet decoding, schema, timestamps, contract identifiers, OI and ingestion normalisation.
2. Request exact-file proof for 28 Jul and 4 Aug 2026 plus full manifest/date coverage. No purchase based solely on a broad archive span.
3. If confirmed, purchase only NIFTY Complete 1-minute at listed ₹7,999 (or 1-year ₹3,999 only if a bounded pilot is sufficient). Use SAVE10 only if it applies at checkout; do not count the discount until confirmed.
4. Do not buy 1-second, SENSEX or broad multi-index packs until the NIFTY 1-minute data passes and the registered research needs justify expansion.
5. Use free official daily data and existing caches for independent validation and auxiliary covariates.
6. Obtain a quote from TrueData and Global Datafeeds only if a specific unmet requirement (historical quote/Greek snapshots, recurring API, or quote-level execution research) is demonstrated.

## Purchase gate / acceptance tests
- Written licence covers internal quantitative research and backtesting; no redistribution.
- Exact missing target sessions and expiries/contracts enumerated in a manifest.
- Validate all expected trading sessions, expiry dates, strike/right coverage, timestamps in IST, row counts, duplicate keys, missing intervals, impossible OHLC, nonnegative volume/OI and suspicious zeros.
- Compare a stratified subset to independent sources where possible.
- Check layout changes across dates and normalize into a versioned schema.
- Preserve original archive, manifest, checksums and acquisition date in repository cache; raw-data storage must respect licence and repository visibility restrictions. Do not publish raw vendor data publicly.
- Backtests must not equate OHLC bar close with executable fills; include Paytm Money brokerage, statutory charges, spread/slippage stress and conservative entry/exit timing.
- No strategy promotion based only on vendor's broad coverage claims.

## Decision
Recommended candidate: NIFTY Complete 1-minute ₹7,999, conditional on exact-file and licence checks. Not sufficient alone for all programme variables or quote-quality execution research. No purchase made or authorised.

## Sources reviewed
- OptionsData catalogue: https://optionsdata.shop/packs
- NIFTY Complete: https://optionsdata.shop/packs/nifty-complete-options-futures-spot-3-years
- NIFTY + SENSEX Complete: https://optionsdata.shop/packs/nifty-sensex-complete-options-futures-spot-3-years
- OptionsData dataset catalogue: https://optionsdata.shop/data
- OptionsData free sample: https://optionsdata.shop/sample
- OptionsData FAQ/licence: https://optionsdata.shop/faq
- TrueData pricing: https://www.truedata.in/workspace/pricing
- TrueData API: https://www.truedata.in/products/marketdataapi
- Global Datafeeds API pricing: https://globaldatafeeds.in/global-datafeeds-apis/global-datafeeds-apis/pricing-sales/api-pricing/
- NSE historical data: https://www.nse.in/static/nse-data-and-analytics/data-information-vending
- NSE public derivatives reports: https://www.nseindia.com/all-reports-derivatives
- Kite historical API docs: https://www.kite.trade/docs/connect/v3/historical/
