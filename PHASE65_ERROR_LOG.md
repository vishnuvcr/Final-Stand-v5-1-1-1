# Phase 65 error log

## F65-001 — expiry filename matcher over-escaped
- **Detection:** static source inspection before the first diagnostic run.
- **Issue:** the regular expression matched a literal backslash before digits instead of normal date digits, so the expiry-file name pattern would not match.
- **Correction:** fixed the pattern to match `options/NIFTY/YYYY-MM-DD.parquet` filenames.
- **Commit:** `96014cf610f3f47a7c0d70fa26c7b5a3eda47601`.
- **Prevention:** add a unit test for the pinned dataset file naming pattern if this code is extended. The full workflow result is not yet verified; do not treat this static correction as a successful data run.
