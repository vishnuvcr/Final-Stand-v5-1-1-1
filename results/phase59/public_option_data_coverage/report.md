# Phase 59 — Public option-data coverage audit

**NO-GO for free, license-clear automated exact-contract prior-minute OI plus quote/depth. Metadata-only; no source data downloaded.**

- Sources reviewed: 10
- Free/license-clear exact intraday OI sources accepted: 0
- Free/license-clear exact quote/depth sources accepted: 0
- Purchases: none; credentials used: no; raw market data committed: no.

| Candidate | OI at exact prior minute | Exact expiry/strike identity | Bid/ask/depth | Automation/license cleared | Decision |
|---|---:|---:|---:|---:|---|
| rissin/nse-options-intraday | No/unknown | Yes | No | No/unverified | REJECT_FOR_PRIOR_MINUTE_OI_AND_QUOTES |
| artist-23/nifty-options-data | Yes | No/unknown | No | No/unverified | REJECT_UNCLEAR_LICENSE_AND_CONTRACT_IDENTITY |
| darshkale/nse-options-data-pipeline | No/unknown | Yes | No | No/unverified | NOT_A_VERIFIED_INTRADAY_SOURCE |
| JATINDHURVE/Indian-market-data-pipeline | Yes | Yes | No | No/unverified | NOT_AN_INDEPENDENT_FREE_ARCHIVE |
| OptionsData.shop historical NIFTY option-chain Parquet | Yes | Yes | No | No/unverified | LICENSED_OI_FOLLOWUP_ONLY_NOT_ACCEPTED |
| QuantDev-stack OptionVault | Yes | Yes | Yes (claim) | No/unverified | LICENSED_QUOTE_FOLLOWUP_ONLY_NOT_ACCEPTED |
| QuantDev-stack TickBytes | Yes | Yes | Yes (claim) | No/unverified | LICENSED_QUOTE_FOLLOWUP_ONLY_NOT_ACCEPTED |
| NSE live option chain / derivatives archive | No/unknown | Yes | Yes (claim) | No/unverified | NOT_HISTORICAL_INTRADAY_QUOTES |
| StockMojo Timeseries Option Chain | Yes | Yes | No | No/unverified | MANUAL_ONLY_NOT_AUTOMATABLE |
| NiftyTrader historical option chain | Yes | Yes | No | No/unverified | INSUFFICIENT_FOR_FROZEN_TIMESTAMPS |

## Conclusion
- No candidate is verified to satisfy both exact-contract prior-minute OI coverage and permitted intraday bid/ask/depth at the frozen Phase 52 timestamps.
- The rissin dataset's published notes state that OI is NaN on Upstox intraday rows; daily bhavcopy OI is not a replacement for prior-minute OI.
- The artist-23 dataset's visible schema does not identify actual expiry and the page has no dataset card/license grant; it is not accepted without provenance and permission review.
- OptionsData.shop may be a licensed source for minute OHLC/OI, but its guide says it does not include bid/ask. No purchase was made.
- TickBytes and OptionVault remain licensed quote/depth follow-up candidates; exact target coverage and reuse/storage terms remain unverified.
- A public GitHub pipeline is code, not a guarantee of data rights or a complete, contract-matched archive.
- Stop this bounded audit here. Only reopen if explicit source access/license authorization and exact target-date/contract sample evidence become available.
