# Phase 81 Status
Date: 2026-10-10
Status: CORRECTED RE-RUN IN PROGRESS — INITIAL SUMMARY SUPERSEDED.

- [x] First registered sweep completed, but initial duplicate diagnostics showed 6,039 pair-attempt exclusions.
- [x] Root cause found: the initial snapshot key omitted explicit expiry identity and did not distinguish identical duplicate rows from conflicting duplicates.
- [x] Corrected snapshot key includes expiry. Identical open+volume duplicates are deterministically collapsed; conflicting observations are excluded and counted.
- [x] Error logged as E81-006; correction committed.
- [ ] Verify corrected workflow result, data-quality counters and paired coverage.
- [ ] Only after verification, freeze descriptive development/validation summaries and open Phase 82 inference if coverage is adequate.
- No holdout was loaded; no strategy was promoted.