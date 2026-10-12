# Official NSE archive access and schema feasibility

Generated: 2026-10-12T03:12:06.299973+00:00
Overall probe: PASS

Three schema-boundary dates are sampled: last pre-UDiFF session (5 July 2024), first UDiFF session (8 July 2024), and a recent session (8 October 2026). ZIP bytes were parsed in memory and not saved or published. This is not a historical backfill or performance test.

## 2024-07-05 — SCHEMA_AND_ROWS_PROBED

Format: LEGACY; HTTP: 200.
Index-option rows: 6228; exact daily contract keys: 6228; duplicate keys: 0.
Identity complete: 6228; price-complete: 6228; positive volume: 2037; invalid OHLC with positive volume: 0.
Source URL: https://archives.nseindia.com/content/historical/DERIVATIVES/2024/JUL/fo05JUL2024bhav.csv.zip
Details: One session only; this does not prove continuous history, source rights or achievable intraday fills.

## 2024-07-08 — SCHEMA_AND_ROWS_PROBED

Format: UDiFF; HTTP: 200.
Index-option rows: 6292; exact daily contract keys: 6292; duplicate keys: 0.
Identity complete: 6292; price-complete: 6292; positive volume: 2130; invalid OHLC with positive volume: 0.
Source URL: https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_20240708_F_0000.csv.zip
Details: One session only; this does not prove continuous history, source rights or achievable intraday fills.

## 2026-10-08 — SCHEMA_AND_ROWS_PROBED

Format: UDiFF; HTTP: 200.
Index-option rows: 4089; exact daily contract keys: 4089; duplicate keys: 0.
Identity complete: 4089; price-complete: 4089; positive volume: 1791; invalid OHLC with positive volume: 0.
Source URL: https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_20261008_F_0000.csv.zip
Details: One session only; this does not prove continuous history, source rights or achievable intraday fills.

## Source-policy gate

If schema and data-quality gates pass, use official NSE daily archives as primary exact-contract EOD options data. Store raw archives only in private workflow cache/working storage; publish aggregate coverage reports and hashes. EOD OHLC is not bid/ask/depth or proof of achievable fills.
Before any strategy result, bulk coverage must reconcile expected trading sessions, missing files, duplicate contract keys, lot-size changes, positive volume, contract expiry and chronology. This probe alone does not establish development/validation/untouched-test coverage.
