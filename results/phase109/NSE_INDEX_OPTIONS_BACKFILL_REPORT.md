# NSE index-options daily archive coverage report

Generated: 2026-10-12T06:42:42.579973+00:00
Window: 2023-10-01 through 2026-10-09 (end exclusive)

**Data-acquisition audit only; no strategy/configuration P&L evaluated.**

| Metric | Result |
|---|---:|
| Weekdays requested | 789 |
| Valid archive dates parsed | 743 |
| Legacy archives | 185 |
| UDiFF archives | 558 |
| Selected option rows | 3,321,984 |
| Identity-complete rows | 3,321,984 |
| Price-complete rows | 3,321,984 |
| Positive-volume rows | 1,353,090 |
| Zero-volume rows | 1,968,894 |
| Invalid positive-volume OHLC rows | 0 |
| Duplicate daily contract keys | 0 |
| Date mismatch rows | 0 |
| Rows missing/without lot size | 1,003,768 |
| Raw cache bytes | 787,820,355 |
| Weekday no-archive/fetch failures | 46 |

## Interpretation

The downloader caches original official NSE daily archives privately and publishes no raw option rows. Weekdays without a valid archive can include exchange holidays or source/network issues; this is not an authoritative exchange-calendar coverage count.
Before using these data for strategy backtesting, Phase 109 still needs: (1) reconcile all actual exchange sessions using an official trading calendar; (2) verify exact expiry/strike/option-type identity and schema transitions; (3) confirm lot size and contract specifications per date (legacy files do not supply lot size); (4) exclude zero-volume and otherwise non-executable rows; (5) build development/validation/untouched chronological splits; and (6) prove cost/accounting reconciliation. EOD high/low cannot be used to claim exact stop/target execution or bid/ask fills.
No profitable strategy or completed exhaustive grid is implied by this archive count.
