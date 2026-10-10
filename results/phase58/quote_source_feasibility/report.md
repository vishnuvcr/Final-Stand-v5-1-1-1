# Phase 58 — quote/depth source feasibility

**Decision: NO_GO_FREE_AUTOMATABLE_HISTORICAL_BID_ASK_DEPTH_AT_FROZEN_TIMESTAMPS**

- Source candidates audited: 6
- Full historical bid/ask/depth sources verified for target dates: 0
- Sources with exact 09:45/13:00/15:15 timestamps verified: 0
- Sources eligible for automated replay: []
- Purchases made: False

## Source decisions

| Source | Decision | Automation | Full quote/depth history verified | Exact timestamps verified |
|---|---|---:|---:|---:|
| [NSE live option chain and derivatives archive](https://www.nseindia.com/option-chain) | NOT_ACCEPTED_FOR_AUTOMATED_HISTORICAL_QUOTES | False | False | False |
| [StockMojo Timeseries Option Chain](https://stockmojo.in/timeseries-option-chain) | MANUAL_FEATURE_RESEARCH_ONLY_NOT_AUTOMATABLE | False | False | False |
| [NiftyTrader historical option chain](https://www.niftytrader.in/nse-option-historical-data) | INSUFFICIENT_FOR_FROZEN_ENTRY_EXIT_TIMES | False | False | False |
| [QuantDev-stack TickBytes](https://github.com/QuantDev-stack/TickBytes) | PROMISING_LICENSED_CANDIDATE_SAMPLE_ONLY | False | False | False |
| [QuantDev-stack OptionVault](https://github.com/QuantDev-stack/OptionVault) | PROMISING_LICENSED_CANDIDATE_SAMPLE_ONLY | False | False | False |
| [thetrademarkk/india-index-options-1m](https://huggingface.co/datasets/thetrademarkk/india-index-options-1m) | RESEARCH_ONLY_NO_QUOTE_DEPTH | True | False | False |

## Conclusion

No free, legally cleared, automated source has been verified for full historical bid/ask/depth at the frozen entry and exit timestamps. StockMojo is manual-only under its published terms; NiftyTrader's documented intraday snapshot times do not match the frozen times; TickBytes and OptionVault have promising quote/depth sample schemas but full historical target-date coverage requires licensed access. NSE live data and daily archives do not establish a free exact historical quote series.

No purchase was made, no site was scraped against terms, and no P&L or strategy selection was performed. The next gate is explicit user authorization for a licensed sample and reuse/storage terms, or a newly verified free source.
