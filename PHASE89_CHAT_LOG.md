# Phase 89 Chat / Decision Log

Date: 2026-10-10

## Auditable request
User asked: “Rerun the research with this data now!”

## Prior evidence used
- Phase 86 Dhan API connectivity PASS.
- Phase 87 rolling expired-options response-shape PASS.
- Phase 88 all four CALL/PUT probes passed on the two previously missing 2026 dates, but those 2026 dates and the Phase 83 holdout are excluded from the Phase 89 study.

## Registered decisions
1. Read Phase 88 plan, status, error log and README before starting.
2. Study calendar-year 2025 only, with DEV/VALIDATION/CONFIRMATORY OOS splits defined before the data run.
3. Evaluate only four primary hypotheses: mean ATM IV vs future absolute spot return, IV skew vs future signed return, OI imbalance vs future signed return, and trailing total-OI change vs future signed return.
4. Use exact timestamp joining, within-session windows, chronological splits, date-clustered standard errors and Holm correction.
5. Do not treat feature association as options strategy profitability; do not open the Phase 83 2026 holdout.
6. Keep raw response payloads in the repository-scoped Actions cache only and publish aggregate results / audit data.

## Execution
Pending the automatically triggered Phase 89 GitHub Actions run.
