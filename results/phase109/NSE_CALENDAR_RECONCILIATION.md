# NSE archive and NIFTY 50 session-calendar reconciliation

Generated: 2026-10-12T09:16:33.953480+00:00

| Metric | Count |
|---|---:|
| Weekdays requested for option archives | 794 |
| Official NIFTY 50 observations | 748 |
| Official India VIX observations | 748 |
| Official NIFTY BANK observations | 748 |
| Valid NSE option archive dates | 748 |
| Option archive dates on NIFTY 50 dates | 748 |
| NIFTY 50 sessions without a valid option archive | 0 |
| No-archive statuses on observed NIFTY 50 sessions | 0 |
| Valid option archive dates without NIFTY 50 observations | 0 |
| Weekday no-archive statuses without index rows (holiday/other uncertain) | 46 |

## Interpretation

The official NIFTY 50 series is a cross-source proxy for whether the broad Indian cash market traded on a date. A date with a NIFTY 50 observation and no valid option archive is a data coverage gap; do not silently drop it. A weekday with neither source is ambiguous until reconciled against official exchange holidays and exceptions. API earliest/latest dates and unavailable chunks must also be considered.
This does not prove option liquidity or exact contract availability. Each date still needs option-contract identity, lot-size, positive-volume, valid-OHLC and source-quality checks. This is not a performance report.

See nse_calendar_reconciliation.json for date samples and machine-readable counts.
