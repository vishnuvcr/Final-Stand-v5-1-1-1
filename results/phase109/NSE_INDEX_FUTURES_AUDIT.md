# Official NSE index-futures extraction audit

Generated: 2026-10-12T09:13:27.721624+00:00

| Metric | Count |
|---|---:|
| Option archives inspected | 748 |
| Archive dates parsed | 748 |
| Dates with selected index futures | 748 |
| Futures rows | 8,976 |
| Identity-complete rows | 8,976 |
| Positive-volume rows | 8,387 |
| Zero-volume rows | 589 |
| Invalid positive-volume OHLC rows | 4 |
| Duplicate date-symbol-expiry keys | 0 |
| Rows missing/nonpositive lot size | 2,256 |
| Failed date parses | 0 |

Futures prices, OI and volume are stored only in private Actions cache; public outputs contain date-level aggregates and hashes. Futures close/settlement is not an intraday executable-fill claim. Spot-futures basis strategies are not eligible until futures are synchronized against the underlying index close, maturity days are checked, contract sizes validated and point-in-time rates/corporate actions are applied if the rule requires them.
