# Phase 65 error log

## F65-001 — expiry filename matcher over-escaped
- **Detection:** static source inspection before the first diagnostic run.
- **Issue:** the regular expression matched a literal backslash before digits instead of normal date digits, so the expiry-file name pattern would not match.
- **Correction:** fixed the pattern to match `options/NIFTY/YYYY-MM-DD.parquet` filenames.
- **Commit:** `96014cf610f3f47a7c0d70fa26c7b5a3eda47601`.
- **Prevention:** add a unit test for the pinned dataset file naming pattern if this code is extended. The full workflow result is not yet verified; do not treat this static correction as a successful data run.

## F65-002 — output publishing failed after diagnostic itself passed
- **Run:** [38027644035](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38027644035).
- **Diagnostic/test outcome:** source audit, syntax/unit tests, and aggregate-output validation passed. It audited 30 trigger rows, found 15 blocked by no strictly ITM strike on trigger minute, 12 by missing/out-of-window next-minute entry, and 3 by missing exact next-minute option bar. No 2026 option data was downloaded; no raw rows were published.
- **Failure cause A:** an unquoted shell heredoc interpreted Markdown backticks as command substitution, producing a permission-denied shell error.
- **Failure cause B:** a concurrent branch update caused a non-fast-forward push rejection.
- **Correction:** removed the shell-sensitive backticks and added fetch/rebase before workflow commits. The workflow must rerun before Phase 65 is considered fully published.
- **Interpretation caveat:** this is descriptive coverage evidence, not proof of profitability or a claim that the entire source is generally sparse; only the frozen trigger rows and monthly-expiry proxy files were audited.
