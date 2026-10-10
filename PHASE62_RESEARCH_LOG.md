# Phase 62 research log

## 2026-10-10 — New source lead admitted to bounded validation
- Reviewed vendor sample, live coverage catalog, FAQ/schema and terms.
- Sample documents 1-minute NIFTY contract OHLCV + OI for 2026-09-15 through 2026-09-17.
- Vendor terms permit own research/backtesting and derived results, prohibit raw-data redistribution, and disclaim completeness. Vendor states it is not affiliated with or authorized by NSE/BSE/MCX.
- No bid/ask/depth/Greeks are included.
- The target missing OOS sessions (2026-07-28 and 2026-08-04) are not in the public sample. A catalog span through Oct 2026 does not prove exact date/contract rows exist.
- This is a genuinely new source compared with Phase 61's five candidates; Phase 61 plan remains frozen.
- No purchase, user details, credentials, private API, raw data persistence, P&L or holdout use.


## 2026-10-10 — Automation implementation
- Added a Python smoke-test that fetches the public sample into temporary runner storage, inspects Parquet schemas, row counts, timestamp bounds, contract-minute duplicate keys, missing OI and true-zero OI counts.
- Added GitHub Actions workflow with automatic branch-push execution and a manual dispatch option.
- Artifact policy is aggregate-only; raw files and temporary signed URLs are not committed or uploaded.
- Runtime result is pending independent verification. No P&L, purchase, holdout use or strategy promotion.
