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
- Hugging Face candidates requiring rights/schema/data-provenance review before use: AAdevloper/nifty50-market-regime (license=mit); GenAIDevTOProd/NIFTY-feature-enhanced (license=mit); average-developer/stocks-INDIAVIX-1D-candles (license=NOT_DECLARED); rahulkrraj/indian-stock-market-minute-data (license=mit); rissin/nse-options-intraday (license=other); tejhq/indian-markets (license=mit); thetrademarkk/india-index-options-1m (license=cc-by-nc-4.0); vishnun0027/indian-market-historical-ohlcv (license=mit). These are source limitations, not a technical workflow failure; the registry remains blocked until audit.
- This step enumerated the hypothesis/configuration space but evaluated no strategy returns; count totals must never be reported as backtests.
- Dhan endpoint data, if returned, were limited to a small access/schema probe. Full-window coverage, historical contract identity, source rights and fill realism remain unverified.
- Hugging Face results are dataset discovery metadata only. No candidate may be downloaded into the experiment until license, date coverage, schema and point-in-time leakage are checked.
- The exhaustive Cartesian grid is large and must be resumed by deterministic shards. Any failed/skipped shard or cost case must remain explicitly logged.
- Resolved workflow error: actions/setup-python pip caching failed because this repository has no requirements.txt or pyproject.toml; removed the pip-cache assumption.
- Resolved compiler error: the architecture gate assumed 1,000 families although 41 core rules × 5 confirmation structures × 5 regime gates creates 1,025; changed the gate to compare against registered Cartesian cardinality.

## 2026-10-12 — Acquisition/evaluator regression found during restart
- Acquisition run 38207969439 failed in the final India VIX/index summary with KeyError `unparseable_date_rows`: the overall-status expression looked for a chunk-only field on merged metrics. Corrected the audit to check the chunk summaries instead.
- Code review found a second, more consequential UDiFF mapping defect: evaluator and model-Greeks extractor filtered the modern `FinInstrmTp` values as legacy `OPTIDX`, while official UDiFF index options are `IDO` and futures are `IDF`. Normalized these codes before evaluation and added a network-free regression fixture. Prior evaluator runs with the old mapping must not be interpreted as strategy results.
- The current public backfill summary is stale (generated 04:22 UTC, before the UDiFF parser correction) and still reports legacy-only lot-size counts. Wait for fresh acquisition output before opening the source gate.
- Official NSE index/VIX endpoint response has not yet been validated end-to-end; no index/VIX availability or model-Greeks coverage is claimed until fresh run summaries confirm it.
