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


## 2026-10-10 — Live coverage catalog delta
- Public live coverage page currently lists NIFTY 1-minute options from January 2023 through October 2026, so the two Phase 51 target dates lie within the advertised overall span. This is a series-level date range only; the rendered public page does not independently expose the exact per-date/per-expiry file manifest for 2026-07-28 and 2026-08-04.
- Source: https://optionsdata.shop/coverage (reviewed 2026-10-10). The vendor's dataset page lists the 1-minute full-chain pack at ₹7,249 and approximately 1.5 GB for options. No purchase authorized or made.
- The free sample is an actual 2026-09-15–17 sample and its public download redirects to a short-lived signed object URL. Direct execution in this environment was unavailable due network DNS resolution failure; this is an environment limitation, not evidence that the vendor file is corrupt. The GitHub Actions validator is intended to execute from a network-enabled runner; its run output must be inspected before claiming a pass.
- Decision: retain `BLOCKED_EXACT_TARGET_SAMPLE_REQUIRED`. Exact target contracts, all required minute keys, source OI semantics, and permitted retention/derived-publication terms have not been independently validated against the target files. No P&L or holdout use.
