# Dhan rolling weekly ATM historical-options audit

Generated: 2026-10-12T08:45:01.672414+00:00
Requested: 2024-10-01 through 2026-10-09 (end exclusive).
Status: **PASS**

| Metric | Value |
|---|---:|
| Chunks attempted | 50 |
| Successful non-empty chunks | 50 |
| Five-minute bars, call side | 37,590 |
| Five-minute bars, put side | 37,587 |
| Invalid OHLC rows | 0 |
| Invalid/missing IV rows | 463 |
| Invalid/missing volume rows | 10 |
| Invalid/missing OI rows | 0 |
| Invalid/missing spot rows | 0 |
| Duplicate timestamp-strike keys | 0 |
| Private compressed-cache bytes | 2,589,835 |
| Failed/empty chunk-side calls | 0 |

## Interpretation

The data are rolling weekly ATM observations, not a fixed-strike or fixed-expiry price series. Strike transitions are explicitly measured per chunk. Use these fields only for lagged features/confirmation after timestamp, IV units, OI semantics and release-time alignment are validated. Do not score any entry/exit from these records, and do not claim executable fills.
Raw authenticated rows remain in private Actions cache; public output contains aggregate quality checks and hashes only. No token or authenticated raw-response body is committed.
