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

## 2026-10-12 07:14 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 08:02 UTC — Grid evaluator failure
- Run 38221168260 failed before a successful shard checkpoint. Inspect the Actions log; do not copy credentials or raw authenticated responses into the repo. Last committed checkpoint remains the resume point.

## 2026-10-12 — NSE historical backfill limitations
- Backfill reported 46 requested session dates with no archive or fetch/schema error across 794 total date probes (789 weekdays plus 5 observed special-session dates). Do not treat these as all exchange holidays or all missing sessions; cross-check against an official calendar and retry non-holiday failures.
- Legacy archive records report 1,019,883 rows with missing/nonpositive lot size (legacy format lacks the UDiFF lot-size field). Historical quantity P&L is blocked until contract-size schedule is recovered from approved dated sources.
- Zero-volume option rows (1,983,705) are excluded from executable-entry eligibility. OHLC completeness is not spread/bid-ask/fill validation.
- Official NSE Indices context audit status=PASS; failed series-chunk requests=0. Review error detail in niftyindices_context_summary.json before any VIX/regime family is marked feasible.
- Dhan rolling ATM supplement status=PASS; failed/empty chunk-side requests=0; any missing window remains blocked. All Dhan rows are rolling ATM feature series, not fixed-contract execution prices.
- Index-futures source gate: 0 archive dates failed extraction; 2,256 futures rows lack positive lot size; 4 positive-volume rows fail OHLC checks. Future/basis families stay blocked until these and spot synchronization are audited.
- Model-IV/Greeks assumption warning: r=6.5%, q=0%, and EOD close/spot marks can bias estimates; 59,187 premiums were below the model lower bound and 0 above the model upper bound. Do not use excluded rows or report model Greeks as directly observed.
- Cross-source session reconciliation found 0 NIFTY 50-observed dates without a valid option archive and 0 archive dates without a NIFTY 50 observed date. These require gap/boundary investigation and are not silently removed.
- Raw source archives are cached privately and are not committed to this public repository. Public outputs contain date-level aggregates and hashes only.

## 2026-10-12 09:39 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 10:35 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 11:57 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 13:13 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 13:22 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 13:36 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 13:51 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 14:04 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 14:22 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 14:36 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 14:45 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 14:49 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 14:53 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 14:57 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 15:00 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 15:04 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 15:09 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 15:14 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 15:18 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 15:22 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 15:25 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 15:33 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 15:46 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 15:50 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 15:59 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 16:05 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 16:16 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 16:21 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 16:28 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 16:33 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 16:39 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 16:46 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 16:54 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 17:05 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 17:20 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 17:30 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 17:45 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 17:50 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 18:01 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 18:15 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 18:31 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 18:39 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 18:52 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 19:08 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 19:14 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.

## 2026-10-12 19:26 UTC — Data-quality and execution notes
- Archive parse/duplicate warnings in this shard: 0. Source gaps, zero-volume and unmatchable exact contracts are excluded and reported; detailed raw price rows are not published. Daily OHLC does not prove achieved fills.
