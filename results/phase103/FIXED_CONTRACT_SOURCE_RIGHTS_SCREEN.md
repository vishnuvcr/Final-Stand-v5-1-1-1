# Phase 103.1C — Fixed-contract source and rights screen

**Date:** 2026-10-11  
**Decision:** NO-GO for strategy P&L until a fixed-contract source and permitted data use are verified.  
**Scope:** Bounded public-source review; no paid data was purchased, no protected endpoint was scraped, and no strategy rules or holdout data were changed.

## Question

Can the currently identified source set support a rights-compliant, fixed listed-contract stock-options replay with credible execution assumptions?

## Evidence reviewed

1. **Dhan expired-options API.** The API describes expired options history as a rolling basis and accepts relative strikes (ATM and offsets), with OHLC, IV, OI and volume. Our successful multi-session run 38115153795 returned 28/28 probes over five sessions, but strict timestamp alignment failed on all four selected panels and actual strikes changed 77–113 times per offset. The API response does not establish immutable contract-level quote/depth history. See [Dhan API docs](https://dhanhq.co/docs/v2/expired-options-data/) and [verified audit run](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38115153795).

2. **NSE Data & Analytics historical-data vending.** NSE publicly lists historical data products and a subscription inquiry/tariff route. This is a plausible official route to ask for contract-specific historical trade/order data, but the public page does not prove that the exact required fields, historical interval, storage rights, automated research rights, or derived-result publication rights are included in any available subscription. No price or entitlement is assumed. See [NSE Data & Analytics](https://www.nse.in/static/nse-data-and-analytics/data-information-vending).

3. **NSE order/trade data specification.** NSE's published order/trade specification includes equity-derivatives trade records and fields such as instrument type, underlying symbol, expiry date, option type, strike and trade time. This supports asking the vendor whether immutable contract identity and trade-price history can be supplied; it does not itself establish free access or permission to redistribute data. See [NSE Historical Data — Order and Trade Specification (PDF)](https://nsearchives.nseindia.com/web/mediaattachment/2026-01/NSE_Hist_Order_Trade_Data_117_20260105112141.pdf).

4. **NSE public option-chain page.** The page provides current option-chain information but explicitly states site-use restrictions against aggregating, copying or duplicating its content. It is not accepted as a source for bulk automated historical reconstruction. See [NSE option chain and terms](https://www.nseindia.com/option-chain).

5. **NSE individual-stock option contract definition.** NSE identifies an option contract by underlying, expiry date, option type and strike price. Therefore, a rolling ATM-relative series is not itself a fixed-contract identity. See [NSE individual securities F&O specifications](https://www.nseindia.com/static/products-services/equity-derivatives-individual-securities).

## Gate table

| Requirement | Current evidence | Gate |
|---|---|---|
| Minute OHLC/IV/OI/volume availability | Dhan returned data for all 28 requested probes | Partial pass |
| Fixed listed-contract identity across time | Rolling strike changed repeatedly; strict surfaces failed | Fail |
| Exact contract expiry mapping and continuity | Not verified in accepted aggregate output | Fail |
| Historical bid/ask and depth for realistic fills | Not established by the Dhan expired-options endpoint used | Fail |
| Automated use, retention/cache, and publication rights | Not verified for raw Dhan payloads or any replacement source | Fail |
| Paytm Money brokerage, statutory levies, spread, slippage, latency | Cannot estimate defensibly before contract/quote data and execution model are available | Blocked |

## Decision and bounded next step

Do not calculate strategy P&L from rolling ATM-offset bars, and do not infer that an HTTP-200 response is evidence of a complete contract tape. Keep raw market rows out of the public repository unless storage and redistribution rights are confirmed.

The only justified source lead from this bounded review is an **official NSE Data & Analytics inquiry** for contract-level historical stock-options data. Required vendor confirmation: target dates and minute frequency; immutable symbol/expiry/strike/CE-PE keys; trade prices and preferably historical bid/ask plus quantities/depth; corporate-action and lot-size metadata; automated research, caching/retention, and derived-publication rights; price/usage limits. This is a procurement/entitlement dependency, not permission to buy data or a claim that a suitable package is available.

If a suitably licensed sample is not already accessible, close this branch's current empirical attempt as **data NO-GO**. No strategy is ranked or promoted. Reopen numerical testing only after a small authorized sample passes exact-contract, timestamp, coverage, quote-quality and rights checks. At that point, include verified Paytm Money charges, statutory fees, spread, slippage and latency; report sensitivity and uncertainty rather than a single optimistic fill estimate.

## Reproducibility and limitations

This is a metadata/documentation screen, not a new market-data acquisition run. Web pages were reviewed on 2026-10-11; provider terms and product availability may change. The review does not claim to exhaust every vendor or establish that a paid dataset is economically worthwhile.
