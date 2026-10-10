# Phase 70 Addendum — Lower-cost options-data acquisition
Date: 2026-10-10
Status: DESKTOP RESEARCH COMPLETE; subscription/purchase not authorized.

## Correction to the first comparison
The ₹7,249 and ₹7,999 one-time packs are not the only practical route, and they are too expensive to recommend as the first step under a tight budget. The current OptionsData.shop catalogue also lists NIFTY options-only one-calendar-year packs for ₹2,999 (2023, 2024, 2025, or 2026 YTD) and a last-three-month full-chain pack at ₹1,499. The 3-year options-only pack is listed at ₹7,249 and the 3-year NIFTY options+futures+spot bundle at ₹7,999. Prices and rolling dates must be verified at checkout.

## Recommended lowest-cost test: DhanHQ Data API
Dhan's official published Data API subscription is ₹499 plus applicable taxes per 30 days (₹588.82 if 18% GST applies). Official API documentation states that its expired-options rolling endpoint provides up to five years of minute-level data and fields including OHLC, IV, volume, OI and spot, with up to 30 days per request. For index options it offers rolling strikes around ATM (up to ATM±10 in the supported near-expiry case; the documentation says ATM±3 for other contracts). This is materially cheaper than buying a multi-year full-chain pack, but it is not the full chain.

Official sources:
- Subscription fee / recurring billing: https://dhan.co/support/platforms/dhanhq-api/how-does-the-dhanhq-data-api-subscription-work/
- Expired options API scope and field coverage: https://dhanhq.co/docs/v2/expired-options-data/
- General API rate limits: https://dhanhq.co/docs/v2/

Estimated one-month subscription cost, assuming 18% GST: ₹499 × 1.18 = ₹588.82. This is a research estimate, not a confirmed checkout quote.

### Important limitations and acceptance gates
1. Requires a Dhan account and Data API access; it is not a public anonymous download.
2. Data are relative-to-ATM rolling strikes, not every listed strike. Far-OTM strategies and wide wings can be out of scope; do not silently treat this as full-chain data.
3. API supports 1-minute, 5-minute, 15-minute, 25-minute and 60-minute rolling-option intervals. A maximum of 30 days is documented per request. Total historical export rate, quota and all expiry-code coverage should be measured in a small pilot first.
4. Standard response does not provide historical bid/ask/depth or actual executable trade prints. Backtesting must continue to use conservative spreads/slippage and cannot be called quote-accurate.
5. Before paying, confirm Dhan's current API terms permit the intended research use and retaining an internally cached dataset after subscription expiry; do not redistribute source data. Do not assume the subscription can be used to bulk-export and retain every requested series until verified.
6. Pilot should pull a small historical range containing 2026-07-28 and 2026-08-04 and audit target rows, expiry mapping, strike offsets, time zone, OI/IV and completeness before scaling to five years. The API's availability for those precise dates is not yet tested.
7. Because the endpoint returns rolling moneyness rather than full-chain contract coverage, register which strategies/factors fit the supported band before using its data for conclusions.

## Free baseline: NSE daily F&O bhavcopy
NSE's daily F&O bhavcopy contains daily contract-level information and is a free/public route for long-horizon EOD research/validation; it does not replace minute-level bars. A public GitHub mirror/archive has validated daily files from 13 Apr 2020 through 31 Aug 2026, sourced from NSE. Treat the mirror as a retrieval helper and cross-check the original official source and licence/availability.
- Official derivatives reports: https://www.nseindia.com/all-reports-derivatives
- Archive automation/project: https://github.com/SantoshSrinivas79/NSE-FNO-Data-bank
- Historical option-chain ETL built from official EOD bhavcopy: https://github.com/shayakbanerjee99/nifty-options-elt

EOD rows can support contract selection and daily OI/settlement studies, regime context and sanity checks. They are not adequate for minute-by-minute intraday exits or exact intraday Greeks.

## Revised cost recommendation
1. Spend ₹0 to ingest/cache official daily F&O reports and validate existing repository data first.
2. If five-year intraday near-ATM rolling data is enough for the target strategies, test DhanHQ with one month at ~₹589 including assumed GST, only after confirming API licence/retention and access. Batch by 30-day windows; checkpoint every request, cache only where permitted, and log gaps/errors.
3. If full-chain historical minute bars are mandatory, do not buy the ₹7,249/₹7,999 bundle yet. Consider one single year from OptionsData.shop at ₹2,999 only if that year answers a bounded question; otherwise request a smaller custom period for the exact target dates.
4. Do not purchase multiple years or switch vendor until the minimal sample passes schema, target-date and contract-coverage gates.
5. Never store raw data in the public repository unless the licence explicitly permits redistribution. Public repo should hold code, manifests, checksums, aggregate validation results and citations only.

## Decision
Current most cost-effective candidate to pilot: DhanHQ Data API at ₹499 + tax for one month, conditional on legal retention permission and required strike/expiry coverage. Free official daily EOD data is the baseline. No purchase/subscription has been made or authorized.
