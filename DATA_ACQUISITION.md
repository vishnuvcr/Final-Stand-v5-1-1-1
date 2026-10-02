# Data Acquisition and Coverage

## Primary source

Hugging Face dataset: `thetrademarkk/india-index-options-1m`.

The dataset provides 1-minute NIFTY spot and option OHLCV/OI data and is described as covering approximately 2021–2026. Its documentation warns that far/illiquid option strikes can be sparse or absent.

## Supplemental source

Zenodo DOI 10.5281/zenodo.10899828: Nifty spot, futures and options one-minute data from 2017–2020.

The Zenodo source describes option fields including option type, strike, trade date/time, OHLC and volume. It is being used as a candidate extension for 2019–2020 after schema validation.

## Weekly-options boundary

NIFTY 50 weekly options began trading in February 2019. Therefore 2017–2018 cannot be used for this exact weekly-options strategy.

## Coverage policy

- No synthetic option prices.
- No forward-filling missing option prices.
- Strike ranking uses only strikes observed at the entry timestamp.
- OTM17 must be available for the selected 20-candidate evaluation.
- Missing observations are logged.
- Supplemental sources must pass schema, timestamp, expiry, weekly/monthly, and completeness validation before merging.
- Raw large datasets are cached in GitHub Actions rather than committed to Git.

## Current acquisition target

The research target is the longest compatible weekly-options sample available: approximately May 2021 through September 2026 using the validated Hugging Face source.
