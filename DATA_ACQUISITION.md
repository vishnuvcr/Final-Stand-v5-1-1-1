# Data Acquisition and Coverage

## Primary executable source

**Hugging Face: `thetrademarkk/india-index-options-1m`**

- 1-minute NIFTY spot and option OHLCV(+OI) data.
- Dataset card reports approximately 2021–2026 coverage, 377M rows and about 4 GB.
- Layout: `index/NIFTY.parquet` plus `options/NIFTY/{EXPIRY}.parquet`.
- The dataset explicitly warns that option coverage is partial and illiquid/far strikes may be sparse or absent.
- The Phase 2 workflow therefore defaults to **2021-01-01 through 2026-09-30**, while logging missing expiries/candidates rather than imputing them.
- Raw data are not committed to Git because of size/licensing constraints; GitHub Actions caches the Hugging Face cache and the repository stores manifests/results.

Source: https://huggingface.co/datasets/thetrademarkk/india-index-options-1m

## Supplemental historical source identified

**Zenodo: Nifty spot, futures and options one-minute data from 2017 to 2020**

- Published dataset contains one-minute NIFTY spot, futures and options data for 2017–2020.
- Options are organized by option type, strike, trade date/time and OHLC/volume, with yearly/monthly folders.
- This source could extend the research before 2021, but its file organization/schema and contract coverage must be mapped and validated against the Phase 2 selector before it is merged into the executable primary sample.

Source: https://zenodo.org/records/10899828

## Other sources assessed

- **OptionVault** claims NIFTY 1-minute options coverage from 2018 onward, but its repository states that the complete dataset is licensed rather than freely stored in the public repository. It is therefore recorded as a potential validation/supplemental source, not silently substituted into the primary run.
- **optionsdata.shop** advertises a full-chain NIFTY 1-minute archive from 2021/2023 through 2026, but it is a paid source. It is recorded for future cross-validation if access is obtained.
- **rissin/nse-options-intraday** provides daily NIFTY history back to 2001 and 1-minute intraday data from 2024 onward; daily data are insufficient for this 10:00-to-expiry strategy, so it is not used as the primary intraday source.

## Coverage policy

1. Prefer real observed 1-minute option prices.
2. Never synthesize missing option prices for the primary backtest.
3. Log missing expiry files, missing 10:00 observations, insufficient OTM17 coverage, and incomplete selected-leg time series.
4. Keep the source, coverage window, and dataset limitations in the research log.
5. Any pre-2021 extension must pass schema, expiry, strike, timestamp and data-completeness validation before being combined with the primary sample.

## Current acquisition target

The current primary target is the longest openly accessible minute-level NIFTY option history that can be executed reproducibly from GitHub Actions: **approximately 2021 through September 2026**. A validated 2017–2020 extension is a separate acquisition/validation task rather than an assumption.
