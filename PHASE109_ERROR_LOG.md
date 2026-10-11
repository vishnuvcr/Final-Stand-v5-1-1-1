# Phase 109 Error and Limitation Log

## At registration
- No Phase 109 runner or grid execution has completed yet.
- Phase 108 uses a short previously inspected daily OHLC sample; it cannot serve as independent OOS.
- OHLC open/close plus assumed slippage does not verify spread, depth, latency, partial fills or market impact.
- Paytm Money account-specific charges are not verified against the user's contract note.
- Exhaustive search creates severe selection/multiple-testing risk; all tested configurations must be logged and inference corrected.
- Missing dates, unavailable expiry/contract identity, skipped tuples and accounting discrepancies must be logged. Never fabricate data or duplicate configurations to reach 1,000.

## 2026-10-12 — Grid compilation and source probe
- Hugging Face Hub returned no matches for 2 of the discovery terms. This is a search-coverage limitation, not an API outage; broaden the search and inspect known candidates.
- Hugging Face candidates requiring rights/schema/data-provenance review before use: rissin/nse-options-intraday (license=other); thetrademarkk/india-index-options-1m (license=cc-by-nc-4.0); tejhq/indian-markets (license=mit); AAdevloper/nifty50-market-regime (license=mit); average-developer/stocks-INDIAVIX-1D-candles (license=NOT_DECLARED); vishnun0027/indian-market-historical-ohlcv (license=mit); rahulkrraj/indian-stock-market-minute-data (license=mit); GenAIDevTOProd/NIFTY-feature-enhanced (license=mit). These are source limitations, not a technical workflow failure; the registry remains blocked until audit.
- This step enumerated the hypothesis/configuration space but evaluated no strategy returns; count totals must never be reported as backtests.
- Dhan endpoint data, if returned, were limited to a small access/schema probe. Full-window coverage, historical contract identity, source rights and fill realism remain unverified.
- Hugging Face results are dataset discovery metadata only. No candidate may be downloaded into the experiment until license, date coverage, schema and point-in-time leakage are checked.
- The exhaustive Cartesian grid is large and must be resumed by deterministic shards. Any failed/skipped shard or cost case must remain explicitly logged.
- Resolved workflow error: actions/setup-python pip caching failed because this repository has no requirements.txt or pyproject.toml; removed the pip-cache assumption.
- Resolved compiler error: the architecture gate assumed 1,000 families although 41 core rules × 5 confirmation structures × 5 regime gates creates 1,025; changed the gate to compare against registered Cartesian cardinality.
