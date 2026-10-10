# Phase 65 error log

## F65-001 — expiry filename matcher over-escaped
- **Detection:** static source inspection before the first diagnostic run.
- **Issue:** the regular expression matched a literal backslash before digits instead of normal date digits, so the expiry-file name pattern would not match.
- **Correction:** fixed the pattern to match `options/NIFTY/YYYY-MM-DD.parquet` filenames.
- **Commit:** `96014cf610f3f47a7c0d70fa26c7b5a3eda47601`.
- **Prevention:** add a unit test for the pinned dataset file naming pattern if this code is extended. The full workflow result is not yet verified; do not treat this static correction as a successful data run.

## F65-002 — output publishing failed after diagnostic itself passed
- **Initial failing run:** [38027644035](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38027644035).
- **Failure causes:** an unquoted shell heredoc interpreted Markdown backticks as command substitution; a concurrent branch update caused a non-fast-forward push rejection.
- **Correction and verification:** removed shell-sensitive backticks and added fetch/rebase before workflow commits. The corrected diagnostic was verified by successful workflow [38027791757](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38027791757). All steps, including aggregate-output validation and publication/status-log update, completed successfully; the failure-recording step was correctly skipped.
- **Accepted diagnostic outcome:** 30 frozen trigger rows audited; 15 had no strictly ITM strike on the trigger minute, 12 had missing/out-of-window next-minute entry, and 3 lacked the exact next-minute option bar. No 2026 option data was downloaded; no raw rows were published and no P&L was computed.
- **Interpretation caveat:** this is descriptive coverage evidence, not proof of profitability or a claim that the entire source is generally sparse; only the frozen trigger rows and monthly-expiry proxy files were audited.
