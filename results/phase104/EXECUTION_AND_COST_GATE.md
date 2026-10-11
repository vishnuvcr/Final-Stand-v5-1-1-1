# Phase 104.2 — Execution and Cost Feasibility Gate

**Reviewed:** 2026-10-11  
**Input audit:** [Phase 104.1 run 38129231405](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38129231405)  
**Decision:** EOD contract identity PASS; executable-price gate NOT PASSED; strategy P&L remains NOT RUN.

## 1. Data result that can be used

Across the 30-calendar-day target window (2026-08-03 inclusive to 2026-09-02 exclusive), the audit parsed 22 official NSE daily archive files for the five registered stock-option symbols. It counted 18,082 selected stock-option rows. All selected rows had the defined trade-date/underlying/expiry/strike/CE-or-PE identity fields and complete daily OHLC; there were zero duplicate daily contract keys or trade-date mismatches. Volume, OI, underlying value and lot-size fields were non-missing for all included records. The 5,922 zero-volume rows are kept separate from 12,160 positive-volume rows.

This is sufficient evidence that the official daily archive supplies a stable, exact daily contract key for this bounded sample. It does not mean all 18,082 contracts were liquid or executable, and it does not establish a usable intraday tape.

## 2. Publicly documented fee inputs for a future EOD test

These are source-based inputs and scenario ranges, not a claim about the user's account-specific contract note.

| Component | Registered model value for the August 2026 sample | Evidence / caveat |
|---|---|---|
| Paytm Money options brokerage | Sensitivity at ₹10, ₹15 and ₹20 per executed order; one buy and one sell each incur their own fee | Paytm Money's current F&O FAQ states ₹10 per unique executed order. Its brokerage-history page says charges depend on the account cohort, with older cohorts at ₹10/₹15 and newer cohorts at ₹20. The user's account cohort has not been inspected. Sources: https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web and https://www.paytmmoney.com/blog/brokerage-charges-increase-from-25th-aug-23-existing-users-will-continue-on-old-brokerage-charges/ |
| NSE equity-options transaction charge | ₹35.52 per ₹1 lakh of premium value on each side (0.03552%) from 1 March 2026 | NSE Finance circular dated 27 February 2026: https://nsearchives.nseindia.com/content/circulars/FA73061.pdf |
| STT on sale of an option | 0.15% of option premium from 1 April 2026 | Official NSE rate page: https://www.nseindia.com/static/products-services/equity-derivatives-securities-transaction-tax |
| Stamp duty | 0.003% of option premium turnover on the buy side | Official NSE levies page: https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies |
| SEBI turnover fee | 0.0001% of premium turnover on purchase and sale | Official NSE levies page above |
| NSE IPFT contribution | Separately itemized in the model: ₹50/crore through February 2026 and ₹0.01/crore from 1 March 2026 | NSE circular above distinguishes transaction charges from IPFT contribution. For March onward it rounds the combined total per crore to ₹3,553; the code uses separate inputs so the contract note can be reconciled. |
| GST | 18% applied in the cost engine to brokerage, NSE transaction charges and SEBI turnover fee | Statutory/service tax assumption; retain as an explicit component for reconciliation against contract notes |
| Exercise/assignment | Separate effective-date STT-on-exercise path is supported by the fee model | Initial strategies should exit before expiry; physical settlement and exercise obligations require explicit handling if any future rule can reach expiry. |

The fee implementation is in `research/phase104_eod_stock_options/cost_model.py`. Tests cover effective-date boundaries for NSE transaction charges, the separately itemized IPFT contribution and STT, brokerage sensitivity, arithmetic reconciliation and explicit marking of unmodelled execution costs. The GST base includes brokerage, NSE transaction charges and SEBI fee; GST treatment of any separately billed IPFT amount must be checked against the user's actual contract note.

## 3. Why the execution gate remains blocked

The official daily archive supplies daily OHLC, traded volume, OI, underlying value, and lot-size fields. It does **not** supply the historical best bid/ask, quote depth, queue position, order arrival latency, partial-fill status, or the price available when an intended order reached the market. Open/close are actual daily bar fields, but do not demonstrate that a hypothetical strategy could transact its chosen quantity at those marks.

The EOD archive also does not independently establish the rights to cache or redistribute raw exchange records. This phase has therefore not cached or published the underlying data; only aggregate quality results and payload hashes were published. User-confirmed Dhan access is not treated as a licence for NSE raw-data redistribution.

Potential paths to better execution evidence:
- NSE Data & Analytics' historical F&O order/trade product, with written confirmation of fields, permissible automated research, retention, and derived-publication rights: https://www.nseindia.com/static/market-data/eod-historical-data-subscription
- A vendor historical-feed trial or licence that explicitly includes expired individual stock-option contracts, expiry/strike identity, and historical executable-side/quote evidence. Global Datafeeds describes NFO historical APIs, but coverage for the exact expired contracts and research/cache rights require confirmation: https://globaldatafeeds.in/apis/

No purchase or vendor-account action has been taken.

## 4. Decision under the preregistered gate

- **EOD contract identity and daily field completeness:** PASS for the bounded 30-calendar-day sample.
- **Legal raw-data caching/republication:** not verified; raw rows remain ephemeral.
- **Paytm Money statutory/brokerage cost arithmetic:** implementable as source-based fee components with ₹10/₹15/₹20 account-cohort sensitivity; an actual contract-note reconciliation remains outstanding.
- **Spread/slippage/latency/market impact/partial-fill evidence:** NOT PASSED.
- **Strategy P&L:** NOT RUN. No net expectancy, return, drawdown, win rate, or profitable strategy claim is produced by this phase.

Under the registered stop rule, do not compute a strategy's P&L using daily OHLC as if it were a validated executable-fill proxy. The Phase 104 final manuscript will close this bounded study with the usable conclusion that daily contract identity is recoverable, while execution-quality evidence is still needed to make a credible after-cost strategy claim.
