# Phase 112 Data-Coverage Policy Amendment

Updated: 2026-10-24

## User directive
Do not exclude scheduled campaigns merely because one or more fields or source observations are missing. Use all available data.

## Required handling
1. Keep every scheduled campaign in the campaign denominator and coverage ledger.
2. For each missing field, first attempt deterministic recovery from already-cached/available sources and source-composite joins (official NSE/BSE data, Dhan data already configured, and existing cached public datasets). Record source, timestamp, join key, and precedence.
3. If recovery fails, retain the campaign and mark the exact missing fields and reason. Do not fabricate observations or silently convert missing prices/Greeks/signals into zero.
4. Where a defensible estimate is possible, produce an explicitly labelled imputed/proxy value, preserve the raw missing value, document the method, and run sensitivity cases (complete observed values only, conservative estimate, and alternative plausible estimate).
5. For a trade whose entry or exit price cannot be established even with source recovery, include it in coverage accounting but do not report a fabricated P&L. Report a bounded P&L only if defensible price bounds exist. Clearly separate observed, recovered, estimated, and unresolved records.
6. Keep results for all scheduled campaigns and all recoverable campaigns side by side. Any missingness-handling method must be fixed before comparing candidate strategies and applied identically to all candidates.
7. Re-run the registered 72-candidate × 24-cost grid on the expanded usable set after implementing this policy. Update the report, manuscript, CSV ledger, error log, status, and README with counts and results. Do not promote a strategy solely because imputation changes the result.

## Interpretation of the existing Phase 112 run
The existing 139/259 eligible-campaign analysis is a complete-case/valid-path result, not an all-campaign result. Its 124 exclusions must not be treated as evidence that those campaigns did not occur. Existing numerical results remain provisional until the missing-data policy is implemented and the full grid is rerun.

## Gate
- [ ] Campaign ledger retains all 259 scheduled campaigns.
- [ ] Recovery attempts and outcomes are recorded per missing field.
- [ ] Imputed/proxy values are explicitly marked and sensitivity-tested.
- [ ] No fabricated fills or silent zero-filling.
- [ ] All 72 candidates and 24 cost scenarios are rerun consistently.
- [ ] Report, manuscript, logs, status, and README are synchronized.
