# Phase 103.1C — Fixed-contract source and rights screen

**Date:** 2026-10-11  
**Decision:** NO-GO for strategy P&L because fixed-contract identity / price reconciliation failed. The user confirmed a Dhan subscription and research authorization; that access assumption is accepted, while raw market rows remain unpublished.  
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
| Automated use, retention/cache, and publication rights | User-confirmed subscription/research authorization; raw rows not committed or republished | Accepted for research access; account-specific public redistribution scope not independently audited |
| Paytm Money brokerage, statutory levies, spread, slippage, latency | Cannot estimate defensibly before contract/quote data and execution model are available | Blocked |

## Decision and bounded next step

Do not calculate strategy P&L from rolling ATM-offset bars, and do not infer that an HTTP-200 response is evidence of a complete contract tape. The user has confirmed research access; keep raw market rows out of this public repository and publish aggregates only.

The only justified source lead from this bounded review is an **official NSE Data & Analytics inquiry** for contract-level historical stock-options data. Required vendor confirmation: target dates and minute frequency; immutable symbol/expiry/strike/CE-PE keys; trade prices and preferably historical bid/ask plus quantities/depth; corporate-action and lot-size metadata; automated research, caching/retention, and derived-publication rights; price/usage limits. This is a procurement/entitlement dependency, not permission to buy data or a claim that a suitable package is available.

If a suitably licensed sample is not already accessible, close this branch's current empirical attempt as **data NO-GO**. No strategy is ranked or promoted. Reopen numerical testing only after a small authorized sample passes exact-contract, timestamp, coverage, quote-quality and rights checks. At that point, include verified Paytm Money charges, statutory fees, spread, slippage and latency; report sensitivity and uncertainty rather than a single optimistic fill estimate.

## Reproducibility and limitations

This is a metadata/documentation screen, not a new market-data acquisition run. Web pages were reviewed on 2026-10-11; provider terms and product availability may change. The review does not claim to exhaust every vendor or establish that a paid dataset is economically worthwhile.


## Expanded public-source screen and exact-strike result — 2026-10-11

### Dhan exact-strike diagnostic (run 38124954633)

The corrected diagnostic passed for unique timestamp/actual-strike keys in all four panels, with zero duplicate keys and five trading sessions of union timestamps (1,925 per panel). This means the cross-offset union is internally non-duplicated; it **does not** establish a complete fixed-contract history because the API response does not return the actual contract expiry date or an immutable option contract identifier. The request uses `expiryFlag=MONTH`, `expiryCode=1` (“Next Expiry” per Dhan's annexure), but the selector is not an observed per-row expiry key.

| Panel | Distinct actual strikes | Actual strikes observed for all 1,925 union timestamps | Best individual-strike union coverage | Decision |
|---|---:|---:|---:|---|
| ICICIBANK CALL | 11 | 3 | Three strikes at 100% (1430, 1440, 1450) | Partial strike coverage; expiry still unverified |
| RELIANCE CALL | 14 | 0 | 1300 at 99.065% (1,907 minutes) | No strike covers every union timestamp |
| RELIANCE PUT | 14 | 0 | 1300 at 99.065% (1,907 minutes) | No strike covers every union timestamp |
| SBIN CALL | 16 | 0 | 1060 at 94.130% (1,812 minutes) | No strike covers every union timestamp |

Even the 100% figures are only five-session timestamp/strike coverage in the offset union. They do not establish historical expiry identity, complete listed-contract OHLC, executability, or data-use rights. The automated workflow passed and committed run [38124954633](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38124954633). The code now explicitly sets `contract_identity_status=BLOCKED_EXPIRY_NOT_RETURNED` so consumers cannot misread the exact-strike key diagnostic as a fixed-contract PASS.

### Other data leads reviewed

1. **NSE public historical contract-wise price/volume report.** The page supports symbol, expiry, option type, strike and CSV download, but says only 90 days are accessible through its date filter and supplies daily contract-level OHLC, LTP, settlement, contracts, turnover and OI. This is an EOD lead, not minute-by-minute execution/quote data. It is not accepted for this intraday strategy question or as permission to cache raw data in the public repo. [Source](https://www.nseindia.com/report-detail/fo_eq_security).
2. **jugaad-data / NSE F&O bhavcopy.** The open-source client documents downloading F&O bhavcopies, including stock options, but its documented option history is daily bhavcopy-level—not historical 1-minute option quotes—and it does not provide historical Greeks or IV. The software licence does not independently grant a data licence or settle NSE data retention/republication rights. [Repository](https://github.com/jugaad-py/jugaad-data).
3. **Hugging Face index-options datasets.** `rissin/nse-options-intraday` documents NIFTY, BANKNIFTY and SENSEX, with 1-minute data sourced from Upstox and EOD data from NSE bhavcopy, and marks the dataset licence as `other`; it does not provide the registered individual stock-option universe. `thetrademarkk/india-index-options-1m` documents index options only under CC BY-NC 4.0 and does not provide historical bid/ask. Both are excluded from Phase 103 stock-options P&L. [rissin dataset](https://huggingface.co/datasets/rissin/nse-options-intraday) · [TradeMarkk dataset](https://huggingface.co/datasets/thetrademarkk/india-index-options-1m).
4. **OptionVault (commercial lead, not free access).** The public repository advertises stock-options 1-minute OHLCV/OI/Greeks and level-2/tick datasets, but its README states that the full archive is available to licensed users and that samples are for evaluation; commercial datasets require licensing. A code repository's MIT licence is not proof that market-data payloads are freely licensed. No paid access or sample entitlement was assumed. [Repository](https://github.com/QuantDev-stack/OptionVault).
5. **NSE Data & Analytics historical order/trade data.** NSE lists F&O historical order and trade data delivered via an online platform, publishes related specification/sample links, and directs enquiries to its market-data group. The public site does not confirm price, date coverage, exact depth/quote fields, or permitted automated retention and derived-publication rights for this use. This remains the strongest official vendor inquiry route, not a currently available free source. [Historical-data subscription details](https://www.nse.in/static/market-data/eod-historical-data-subscription) · [Data vending](https://www.nse.in/static/nse-data-and-analytics/data-information-vending) · [Data-use policy](https://www.nseindia.com/static/market-data/nse-data-policy).

### Bounded conclusion

The expanded search did not find a verified free source with all three required properties for this branch: (a) individual NSE stock-option intraday history with returned/reconstructable exact expiry/strike/CE-PE identity; (b) adequate historical executable quote evidence or a defensible fill proxy; and (c) explicit usable data retention/caching rights. Therefore the present **intraday stock-options empirical gate is NO-GO**. The Dhan API remains a demonstrated aggregate data-feasibility source, not a strategy-testing dataset under the registered hard gates. Do not silently substitute index-options data or daily EOD data for the registered stock-options question. Reopen numerical P&L only after an authorized contract-specific sample passes the gates; otherwise complete the branch as a documented data NO-GO at the registered closeout phase.



## User-confirmed Dhan subscription — 2026-10-11

The user explicitly confirmed that they have the required rights and subscribed to Dhan, and authorized research continuation. This confirmation is accepted as the project's access/entitlement assumption; it is not an independent legal review of the account-specific agreement. Raw Dhan minute data are not committed or publicly republished. This branch stores only aggregate audit results, schema/quality diagnostics and non-row-level expiry counts. The NSE EOD files are used only for an independent contract-identity cross-check; any raw rows remain ephemeral and are not cached in the public repository. This step does not infer that subscription rights automatically include redistribution of raw market data.


## Follow-up reconciliation results and bounded stop — 2026-10-11

The user confirmed Dhan subscription and research authorization. That is accepted for research access; it is no longer treated as the primary blocker, although this repository does not republish raw Dhan or NSE rows.

The code-1 run [38126663036](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38126663036) downloaded all 5 NSE daily files but found only 3 unique four-field OHLC matches among 88 complete-session profiles, all at the 2026-08-25 expiry; zero matched the expected rank-2 expiry and 85 were unmatched. The code-0 attempt [38127361683](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38127361683) was rejected by Dhan at the first request with HTTP 400 / DH-905 / “expiryCode is required”, so no price comparison was possible. The one-shot selector calibration is exhausted. Current phase outcome remains **NO-GO for strategy P&L** based on data identity/price quality, not lack of subscription.
