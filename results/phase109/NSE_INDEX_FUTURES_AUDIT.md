# Official NSE index-futures extraction audit

Generated: 2026-10-12T08:59:10.757763+00:00

| Metric | Count |
|---|---:|
| Option archives inspected | 743 |
| Archive dates parsed | 743 |
| Dates with selected index futures | 743 |
| Futures rows | 8,916 |
| Identity-complete rows | 8,916 |
| Positive-volume rows | 8,331 |
| Zero-volume rows | 585 |
| Invalid positive-volume OHLC rows | 4 |
| Duplicate date-symbol-expiry keys | 0 |
| Rows missing/nonpositive lot size | 2,220 |
| Failed date parses | 0 |

Futures prices, OI and volume are stored only in private Actions cache; public outputs contain date-level aggregates and hashes. Futures close/settlement is not an intraday executable-fill claim. Spot-futures basis strategies are not eligible until futures are synchronized against the underlying index close, maturity days are checked, contract sizes validated and point-in-time rates/corporate actions are applied if the rule requires them.
