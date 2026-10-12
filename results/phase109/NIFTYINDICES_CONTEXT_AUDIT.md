# NSE Indices historical index and India VIX audit

Generated: 2026-10-12T08:32:31.955817+00:00
Requested window: 2023-10-01 to 2026-10-09 (end exclusive)
Overall status: PASS

No strategy returns were evaluated. Full historical rows remain in the private GitHub Actions cache; this report exposes only aggregate audit metrics and hashes.

| Series | Unique dates | Range | Missing OHLC | Invalid OHLC | Close min | Close max |
|---|---:|---|---:|---:|---:|---:|
| INDIA_VIX | 218 | 2023-10-03–2026-10-08 | 0 | 0 | 9.15 | 16.6875 |
| NIFTY 50 | 218 | 2023-10-03–2026-10-08 | 0 | 0 | 18857.25 | 26328.55 |
| NIFTY BANK | 218 | 2023-10-03–2026-10-08 | 0 | 0 | 42280.15 | 60150.95 |

## Data gates

- A VIX series is accepted only from the official NSE Indices endpoint and must pass plausibility/duplicate/schema checks. Publisher-labelled VIX datasets are not used as substitutes.
- The selected NIFTY 50 and NIFTY BANK daily OHLC are inputs for lagged market-regime and cross-index/underlying features; only prior-known values may enter a strategy signal.
- Check the returned index/VIX dates against the official trading calendar and option-archive date manifest before model fitting.
- Any non-zero invalid OHLC count, duplicate dates, missing windows or implausible values blocks dependent families until resolved.

Sources: [NSE Indices historical-data page](https://www.niftyindices.com/reports/historical-data), [official India VIX endpoint](https://www.niftyindices.com/Backpage.aspx/BindHistoricalIndiaVixData), [index OHLC endpoint](https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString).
