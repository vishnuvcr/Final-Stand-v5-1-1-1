# Phase 109 Error and Limitation Log

## At registration
- No Phase 109 runner or grid execution has completed yet.
- Phase 108 uses a short previously inspected daily OHLC sample; it cannot serve as independent OOS.
- OHLC open/close plus assumed slippage does not verify spread, depth, latency, partial fills or market impact.
- Paytm Money account-specific charges are not verified against the user's contract note.
- Exhaustive search creates severe selection/multiple-testing risk; all tested configurations must be logged and inference corrected.
- Missing dates, unavailable expiry/contract identity, skipped tuples and accounting discrepancies must be logged. Never fabricate data or duplicate configurations to reach 1,000.
