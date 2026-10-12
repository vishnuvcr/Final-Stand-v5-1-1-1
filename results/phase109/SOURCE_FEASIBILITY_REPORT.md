# Phase 109 source-feasibility report

Generated: 2026-10-12T06:17:49.706242+00:00

This records candidate sources and their current gates; it does not claim that they are approved, downloaded, or used in a backtest.

## Runtime checks

- Official NSE legacy/UDiFF probe: 3/3 dates passed; report status PASS.
- Dhan: initial authenticated schema probe is a short rolling strike-relative sample; fixed expiry/contract use remains blocked pending reconciliation.
- Hugging Face: eight dataset cards inspected for declared license, update time and file listing. Metadata and publisher claims are not independent data-quality proof.

## Source decisions

- Use NSE official legacy/UDiFF archives as the primary exact-contract daily options source only after bulk trading-session, identity, expiry, lot-size, positive-volume and OHLC audits.
- Use Dhan as a supplementary IV/OI/flow source, not fixed-contract fills, until strike/expiry transitions and executable price mapping are proven.
- rissin/nse-options-intraday is blocked for now: license=other; intraday source is Upstox and provider terms apply; visible examples include zero-price/zero-volume rows.
- thetrademarkk/india-index-options-1m has CC BY-NC 4.0 and publisher-described partial coverage; block pending license compatibility and official reconciliation.
- tejhq/indian-markets is a promising MIT-declared EOD equity/corporate-action/symbol-history candidate, not an option-price source; validate point-in-time membership and exchange terms.
- AAdevloper/nifty50-market-regime is rejected for India VIX use until corrected: the displayed 2015-10-23 value is about 8,295, inconsistent with VIX-point units.
- average-developer/stocks-INDIAVIX-1D-candles is blocked because no license is declared and rows/schema are not independently validated.
- News/feature-enhanced datasets are excluded until publication-time alignment and look-ahead checks pass.
- Official NSE historical index and India VIX reports and FII/participant files exist; automated historical acquisition, coverage and publication-lag audits remain pending.
- Global indices, volatility, gold and rates must be timestamp-aligned so only information available before each Indian decision can be used.

## Registered source URLs

- [Official NSE F&O UDiFF daily bhavcopy](https://www.nseindia.com/all-reports-derivatives) — SCHEMA_PROBE_PASS_BULK_COVERAGE_PENDING.
- [Official NSE F&O legacy bhavcopy](https://archives.nseindia.com/content/historical/DERIVATIVES/{YYYY}/{MON}/fo{DDMONYYYY}bhav.csv.zip) — SCHEMA_PROBE_PASS_BULK_COVERAGE_PENDING.
- [DhanHQ rolling expired-options API](https://dhanhq.co/docs/v2/expired-options-data/) — ACCESS_SCHEMA_PROBE_PASS_FIXED_CONTRACT_GATE_PENDING.
- [rissin/nse-options-intraday](https://huggingface.co/datasets/rissin/nse-options-intraday) — BLOCKED_RIGHTS_AND_QUALITY_REVIEW.
- [thetrademarkk/india-index-options-1m](https://huggingface.co/datasets/thetrademarkk/india-index-options-1m) — BLOCKED_PENDING_LICENSE_AND_COVERAGE_REVIEW.
- [tejhq/indian-markets](https://huggingface.co/datasets/tejhq/indian-markets) — CANDIDATE_SCHEMA_AUDIT_PENDING.
- [AAdevloper/nifty50-market-regime](https://huggingface.co/datasets/AAdevloper/nifty50-market-regime) — REJECTED_SUSPECT_FIELD_LABEL.
- [average-developer/stocks-INDIAVIX-1D-candles](https://huggingface.co/datasets/average-developer/stocks-INDIAVIX-1D-candles) — BLOCKED_LICENSE_MISSING.
- [vishnun0027/indian-market-historical-ohlcv](https://huggingface.co/datasets/vishnun0027/indian-market-historical-ohlcv) — CANDIDATE_SOURCE_AND_SYMBOL_AUDIT_PENDING.
- [rahulkrraj/indian-stock-market-minute-data](https://huggingface.co/datasets/rahulkrraj/indian-stock-market-minute-data) — BLOCKED_PROVENANCE_AND_SCALE_AUDIT.
- [GenAIDevTOProd/NIFTY-feature-enhanced](https://huggingface.co/datasets/GenAIDevTOProd/NIFTY-feature-enhanced) — BLOCKED_LOOKAHEAD_AND_PROVENANCE_AUDIT.
- [NSE official historical index and India VIX reports](https://www.nseindia.com/reports-indices-historical-vix) — ACCESS_AND_BULK_COVERAGE_PENDING.
- [NSE FII derivatives and participant statistics](https://www.nseindia.com/all-reports-derivatives) — ACCESS_AND_PUBLICATION_LAG_PENDING.
- [Free global-index and macro time-series sources to be compared](https://stooq.com/ ; https://fred.stlouisfed.org/ ; https://finance.yahoo.com/) — SOURCE_CATALOGUE_PENDING.

See source_feasibility_matrix.csv, source_access_audit.csv, NSE archive probe output and Hugging Face metadata for machine-readable evidence.
