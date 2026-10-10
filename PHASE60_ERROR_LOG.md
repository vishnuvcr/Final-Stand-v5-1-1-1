# Phase 60 error log

Append every failed test/workflow with run URL, exact cause, correction and regression verification. Do not erase previous failures.

No Phase 60 execution errors recorded at initialization.

## F60-RUN-38021585340 — gate failure

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38021585340
- Status: failure
- Report present: False
- No conclusion accepted.
- Status: OPEN.

## F60-RUN-38021594949 — gate failure

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38021594949
- Status: failure
- Report present: True
- No conclusion accepted.
- Status: OPEN.

## F60-RUN-38021608375 — gate failure

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38021608375
- Status: failure
- Report present: True
- No conclusion accepted.
- Status: OPEN.

## F60-RUN-38021614375 — gate failure

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38021614375
- Status: failure
- Report present: True
- No conclusion accepted.
- Status: OPEN.

## F60-ROOT-001 — incorrect repository root / Phase59 report schema — RESOLVED

- Failing runs: [38021585340](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38021585340), [38021594949](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38021594949), [38021608375](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38021608375).
- Root causes: the script resolved the repository root one directory too high and initially expected source-count/status fields not present in the canonical Phase59 JSON schema.
- Correction: use the repository root at `parents[2]`; validate `source_count`, `authorized_exact_intraday_oi_sources` and `authorized_exact_quote_depth_sources`.
- Verification: regression tests and decision report validation passed in [38021649621](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38021649621); checkpoint persistence exposed a separate summary-key mismatch corrected below.
- Status: RESOLVED.

## F60-ROOT-002 — decision function did not return its report object — RESOLVED

- Failing run: [38021614375](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38021614375).
- Root cause: `evaluate()` wrote files but returned `None`, causing test assertions to fail.
- Correction: return the validated decision dictionary after writing the report.
- Verification: regression tests and decision validation passed in [38021649621](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38021649621).
- Status: RESOLVED.

## F60-PERSIST-001 — checkpoint summary used obsolete report keys — RESOLVED

- Failing run: [38021649621](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38021649621).
- Root cause: persistence summary referenced pre-normalization field names, causing a KeyError after analysis/tests passed.
- Correction: use the actual decision-report keys `authorized_exact_prior_minute_oi_sources` and `authorized_exact_quote_depth_sources`.
- Verification: full workflow including checkpoint persistence passed in [38021675579](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38021675579).
- Status: RESOLVED.
