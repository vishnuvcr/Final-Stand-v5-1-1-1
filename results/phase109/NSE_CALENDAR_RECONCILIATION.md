# NSE archive and NIFTY 50 session-calendar reconciliation

Generated: 2026-10-12T04:27:16.915173+00:00

| Metric | Count |
|---|---:|
| Weekdays requested for option archives | 789 |
| Official NIFTY 50 observations | 0 |
| Official India VIX observations | 0 |
| Official NIFTY BANK observations | 0 |
| Valid NSE option archive dates | 743 |
| Option archive dates on NIFTY 50 dates | 0 |
| NIFTY 50 sessions without a valid option archive | 0 |
| No-archive statuses on observed NIFTY 50 sessions | 0 |
| Valid option archive dates without NIFTY 50 observations | 743 |
| Weekday no-archive statuses without index rows (holiday/other uncertain) | 46 |

## Interpretation

The official NIFTY 50 series is a cross-source proxy for whether the broad Indian cash market traded on a date. A date with a NIFTY 50 observation and no valid option archive is a data coverage gap; do not silently drop it. A weekday with neither source is ambiguous until reconciled against official exchange holidays and exceptions. API earliest/latest dates and unavailable chunks must also be considered.
This does not prove option liquidity or exact contract availability. Each date still needs option-contract identity, lot-size, positive-volume, valid-OHLC and source-quality checks. This is not a performance report.

See nse_calendar_reconciliation.json for date samples and machine-readable counts.
