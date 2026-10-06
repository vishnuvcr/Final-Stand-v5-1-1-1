# Phase 48 Literature / Data Bridge Review

## Independent data source

The rissin/nse-options-intraday Hugging Face dataset describes NIFTY 1-minute intraday data from October 2024 onward with expiry, strike, option type, OHLC, volume and source metadata. This is structurally more suitable for multi-expiry same-day research than the prior expiry-centric source because the dataset is organized by trade year and retains an expiry field on each option row.

## Public NIFTY data-engine reference

The SauMStats NIFTY market-data engine documents a multi-expiry query interface and a volatility-surface snapshot workflow using historical NIFTY options. Its public documentation confirms the research requirement that an entry-time surface must expose multiple expiries and that Black-Scholes IV/Greeks can be derived from spot, strike, time-to-expiry and observed option prices. It also notes that 2024 data is sourced from a Kaggle archive and that its 2026 live layer is separate.

## Methodological interpretation

Neither source is treated as a substitute for the canonical project dataset. The independent source is used to establish whether the previously data-infeasible multi-expiry hypotheses survive an independent data construction. Any discrepancy in pricing, contract availability or timestamp coverage is retained as a limitation rather than normalized away.