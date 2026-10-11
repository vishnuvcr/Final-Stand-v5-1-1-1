# Phase 104 Error and Limitation Log

Phase 104.1 EOD data audit completed successfully in run 38129389678. New errors, failed workflows, data gaps and corrective actions are recorded chronologically below.

## Initial known limitations
- NSE EOD archives supply daily contract OHLC, volume, OI and underlying values, but do not by themselves establish intraday bid/ask, queue depth, or exact execution quality.
- User-confirmed Dhan subscription authorizes the project to use the subscribed Dhan source as the user's working assumption, but it does not independently validate NSE caching/republication permissions or rights for any other vendor.
- No raw market rows are to be committed or uploaded; only aggregates and safe diagnostics may be published.
- Paytm Money cost schedules and applicable statutory rates must be date-effective. A current webpage snapshot alone is insufficient to validate older historical charge schedules.

## E104-001 — EOD archives do not establish executable historical fills
**Type:** data limitation / strategy-inference stop, not a code failure.  
**Evidence:** run [38129389678](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38129389678) passed the source-data quality gate (18,082 rows; 100% identity and OHLC completeness), but daily bars contain no historical best bid/ask, depth, queue position, order arrival latency or partial-fill outcomes.  
**Handling:** strategy P&L, trade statistics and profitability inference were not run. Do not assume zero spread/slippage or treat OHLC values as guaranteed fills. Reopen only with authorized quote/trade evidence or a validated conservative execution proxy under a new bounded plan.

## E104-002 — Paytm Money user-specific brokerage tier not verified
**Type:** cost schedule limitation.  
**Evidence:** official public materials expose a current ₹10 per unique executed order and also document historical account cohorts with ₹10/₹15/₹20 charges. This project has not read the user's account or contract note.  
**Handling:** fee model retains ₹10/₹15/₹20 per-order sensitivity and date-effective statutory/exchange components, including a separate NSE IPFT component. Account-specific fee reconciliation and treatment of any separately billed charges remain required before any P&L.

## E104-003 — Raw NSE data-use and retention rights not independently verified
**Type:** licensing / publication limitation.  
**Evidence:** the archive was technically downloadable, but no account-specific licence or written exchange terms were reviewed to establish public raw-data retention, redistribution or caching rights.  
**Handling:** raw rows and archive payloads remain ephemeral. Only aggregate counts, archive SHA-256 hashes, safe quality diagnostics and derived figures are in the repository/artifacts.
