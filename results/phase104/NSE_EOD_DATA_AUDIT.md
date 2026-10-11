# Phase 104.1 — NSE EOD Stock-Options Data Audit

**Run:** 38129231405
**Status:** PASS_EOD_CONTRACT_IDENTITY
**Target window:** 2026-08-03 inclusive to 2026-09-02 exclusive (30 calendar days)
**Official NSE daily archives parsed:** 22
**No-archive dates (weekend/holiday/absent file not distinguished automatically):** 8
**Source/schema errors:** 0
**Selected five-stock stock-option rows:** 18082
**Parsed rows:** 18082
**Identity completeness:** 18082/18082 (100.0%)
**OHLC completeness:** 18082/18082 (100.0%)
**Unique daily contract keys:** 18082
**Duplicate daily contract keys:** 0
**Rows with positive volume / zero volume / missing volume:** 12160 / 5922 / 0
**Missing OI / underlying / lot-size rows:** 0 / 0 / 0
**Date-mismatch rows:** 0
**Aggregate expiry-date counts:** {"2026-08-25": 6234, "2026-09-29": 6977, "2026-10-27": 4161, "2026-11-23": 710}
**Raw rows persisted or uploaded:** False / False

## Coverage by stock

| Symbol | Rows | Dates | Unique daily contracts | Positive-volume rows | Zero-volume rows | Missing OI | Missing underlying | Missing lot size |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| HDFCBANK | 3022 | 22 | 3022 | 2468 | 554 | 0 | 0 | 0 |
| ICICIBANK | 4241 | 22 | 4241 | 2044 | 2197 | 0 | 0 | 0 |
| INFY | 2734 | 22 | 2734 | 2240 | 494 | 0 | 0 | 0 |
| RELIANCE | 4303 | 22 | 4303 | 3035 | 1268 | 0 | 0 | 0 |
| SBIN | 3782 | 22 | 3782 | 2373 | 1409 | 0 | 0 | 0 |

## Daily file checkpoints

| Date | Status | Selected rows | Identity-complete rows | Archive SHA-256 |
|---|---|---:|---:|---|
| 2026-08-03 | ARCHIVE_PARSED | 788 | 788 | 4caeaccc0e69507d6746fe263e54bb801dcea6914fa8f65b478e11cb43d7b734 |
| 2026-08-04 | ARCHIVE_PARSED | 810 | 810 | 66680e99150aa568e18927d78164dc9caefdb4cbfb92efb081c98188c1c978a9 |
| 2026-08-05 | ARCHIVE_PARSED | 810 | 810 | 4b6554d42fb40f33187272cc6f42ccbf86e320c77ccc69cb599ee28eb81ffa25 |
| 2026-08-06 | ARCHIVE_PARSED | 814 | 814 | 2525a6549c47e64e305baa6cc42c14685321ffb05f50728dddf55dcacec1daf2 |
| 2026-08-07 | ARCHIVE_PARSED | 836 | 836 | a5ca8f06fd69554ea123134fc823a8a868ccca454d286727c22290dc37daac82 |
| 2026-08-08 | NO_ARCHIVE_OR_NONTRADING_DATE | 0 | 0 |  |
| 2026-08-09 | NO_ARCHIVE_OR_NONTRADING_DATE | 0 | 0 |  |
| 2026-08-10 | ARCHIVE_PARSED | 851 | 851 | 8a97db352122ce75dc7cf4b1d2ffccfb7e15bab3d5e827c04519e9fa11349e05 |
| 2026-08-11 | ARCHIVE_PARSED | 851 | 851 | 0c4cff21f0e20e9a1aa0e27894597ff40e287ed3000567880abbc0f6775bc5c1 |
| 2026-08-12 | ARCHIVE_PARSED | 855 | 855 | a93fa82a1b43c48cc646eeaa369aee438ab3cb2ca437d7ebb6f2fbd9603ccf91 |
| 2026-08-13 | ARCHIVE_PARSED | 855 | 855 | 00d088350e833543939d7adab1fe9e2632bd9a9c6189d52ee972737395ad0a7b |
| 2026-08-14 | ARCHIVE_PARSED | 861 | 861 | 614807e1050487ad00d1ca825ab04ed0a444c4ba9451e8db095b6254377ea49f |
| 2026-08-15 | NO_ARCHIVE_OR_NONTRADING_DATE | 0 | 0 |  |
| 2026-08-16 | NO_ARCHIVE_OR_NONTRADING_DATE | 0 | 0 |  |
| 2026-08-17 | ARCHIVE_PARSED | 861 | 861 | a8ab5f733287bc097c318b8dda9ab00e86500ce5e775fda266e2a5683c3bcaec |
| 2026-08-18 | ARCHIVE_PARSED | 861 | 861 | ca8b662150517d3c343322e21bc1bf4c4496d65ef160a2331a498562e0bf59ae |
| 2026-08-19 | ARCHIVE_PARSED | 861 | 861 | d2607f215cc2e3e1e92b97aca97ec59be352ff920ceea1104117077f48464d4d |
| 2026-08-20 | ARCHIVE_PARSED | 861 | 861 | 9c5f793941678f5cf93ad0516c887efad617c466b73c06786f5b0b259b811db6 |
| 2026-08-21 | ARCHIVE_PARSED | 861 | 861 | 577c04c20bc7e4550f4a2ebfc849cada332611e94dbb1cdb11e5cff9e1e252f6 |
| 2026-08-22 | NO_ARCHIVE_OR_NONTRADING_DATE | 0 | 0 |  |
| 2026-08-23 | NO_ARCHIVE_OR_NONTRADING_DATE | 0 | 0 |  |
| 2026-08-24 | ARCHIVE_PARSED | 861 | 861 | 922d768844e8cce6a8e820606022b512e4f99f6a40a9df974c658290f31949ff |
| 2026-08-25 | ARCHIVE_PARSED | 861 | 861 | 398f2636d757c8fbdc9182ef2eb2be290afd6e9950cdbad6841e618846463837 |
| 2026-08-26 | ARCHIVE_PARSED | 744 | 744 | 254e419b0101eb26f8916314286f57b285d866b5228f9c5f3be2bd0eb90c894d |
| 2026-08-27 | ARCHIVE_PARSED | 728 | 728 | db31cbb3247a5a9ace5081088f7ea34d96373b7a99e5f8ddbf24d6d3282df2b7 |
| 2026-08-28 | ARCHIVE_PARSED | 741 | 741 | 33a1708ceba84a807e2b6e7bcf6b94e385ab0f65658eb99578eda92e735a88b5 |
| 2026-08-29 | NO_ARCHIVE_OR_NONTRADING_DATE | 0 | 0 |  |
| 2026-08-30 | NO_ARCHIVE_OR_NONTRADING_DATE | 0 | 0 |  |
| 2026-08-31 | ARCHIVE_PARSED | 748 | 748 | 1e435806057655142a50ce380d74dca174e26be98bfec625f8ded211e62c78b1 |
| 2026-09-01 | ARCHIVE_PARSED | 763 | 763 | 328cfdef6953b86b56c40b28f4b9677e8e4701f5027d00daa6b1d1708b64fa63 |

## Interpretation

Technical daily contract identity and OHLC integrity passed this bounded sample. This does not establish data-use/caching rights, executable prices, strategy profitability or suitability for intraday fills.

## Limitations

- Daily OHLC bars do not provide historical bid/ask, depth, queue position, latency or verified executable fills.
- Daily archive schema and technical access do not prove rights to cache or redistribute raw exchange data; this workflow publishes aggregates only.
- Corporate-action and point-in-time universe adjustments are separate required inputs for multi-year strategy research.
- Paytm Money brokerage and statutory/exchange costs must be date-effective before strategy P&L.
