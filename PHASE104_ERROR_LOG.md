# Phase 104 Error and Limitation Log

No Phase 104 data-audit execution has yet completed. All new errors, failed workflows, data gaps and corrective actions must be added chronologically below.

## Initial known limitations
- NSE EOD archives supply daily contract OHLC, volume, OI and underlying values, but do not by themselves establish intraday bid/ask, queue depth, or exact execution quality.
- User-confirmed Dhan subscription authorizes the project to use the subscribed Dhan source as the user's working assumption, but it does not independently validate NSE caching/republication permissions or rights for any other vendor.
- No raw market rows are to be committed or uploaded; only aggregates and safe diagnostics may be published.
- Paytm Money cost schedules and applicable statutory rates must be date-effective. A current webpage snapshot alone is insufficient to validate older historical charge schedules.
