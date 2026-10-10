# Phase 94 Research Log

## 2026-10-10 — Step 1: preregister paper replication program
- Read Phase 93 status, plan, validation report and paper-by-paper literature evidence audit.
- Confirmed that Phase 93 was a literature/documentation audit with no new empirical experiment.
- Reviewed text-extracted contents of the 14 attached PDFs for distinct method/rule families.
- Created a paper/method register with source IDs, method names, inputs, downstream phase assignment and prior evidence guardrails.
- Defined a finite plan through Phase 100 with per-phase branches and explicit completion/stopping rules.
- Registered forecasting baselines, chronological validation, dependent-data inference, multiple-comparison handling and options cost/fill gates.
- Outcome: plan and scope registered; no empirical strategy/model run in Phase 94; no claim of reproduction; no strategy promoted.
- Next step: validate registry automatically, then proceed to Phase 95's empirical model replication.

## Decision record
- Include both exact source-metric reconstruction and common out-of-sample benchmark tests.
- Preserve each author's performance claims as claims until regenerated from data/code.
- Do not use the sealed Phase 83 2026 holdout.
- Use partial replication only when source period/feature/data is unavailable, clearly separating it from exact replication.

## E94-010 — registry CSV rows were not all column-aligned
- Detected from GitHub Actions run 38070702058 on 2026-10-10.
- Cause: two cross-paper rows had unquoted commas/omitted fields, causing malformed rows; validator surfaced a `NoneType.strip` error instead of a clearer schema message.
- Correction: normalized the two rows to the 11-column schema, RFC-4180-escaped the entire CSV, and strengthened validator to detect malformed row widths and report blank cells safely.
- Status: corrected; awaiting fresh validator run.

## E94-011 — status text validation false positive
- The CSV fix exposed an independent brittle wording assertion in the validator. The phase status clearly recorded no promotion, but the validator required literal `no strategy` wording.
- Replaced the literal phrase check with a semantic check for `Strategy promotion: NONE` (case-insensitive).
- Fresh GitHub Actions validation is pending.
