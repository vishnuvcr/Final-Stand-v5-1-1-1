# Phase 54 error log

No Phase 54 errors recorded at plan creation. Append any workflow/test/persistence failure with its run URL, failing step, root cause, fix, regression test and verification run. Preserve earlier entries.


## F54-DATA-001 — Stale parent branch input — RESOLVED

- Symptom: successful Phase 54 run 37988153104 reported 373 empty leg payloads and refused threshold sensitivity.
- Root cause: Phase 54 branch inherited Phase 52 v0.2 CSV instead of canonical v0.2.1 audit-provenance CSV from phase-52-factor-conditioned-strategy-discovery.
- Fix: replace Phase 54 copy with canonical v0.2.1 CSV (source file blob SHA 33c82a92e4546c4be10138dbf518ce0e51a83c03; 480 rows; 533,125 bytes).
- Remaining gate: multi-leg range exclusions still contain partial evidence in canonical parent output. Phase 52 runner patch f484d6672f3bb06088adb5aab2888a0a682f1683 must be exercised in a fresh historical pilot before sensitivity can be computed.
- Status: input mismatch closed; evidence completeness gate OPEN.

## F54-RUN-37992224177 — workflow/report failure

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992224177
- Job status: failure
- Report present: False
- No result or strategy conclusion accepted.
- Status: OPEN.

## F54-TEST-001 — regression fixture not updated with required exclusion reason — RESOLVED

- Failing run: [37992224177](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992224177).
- Symptom: the new fail-closed schema required `exclusion_reason`, but the partial-payload unit-test fixture omitted it, so the test failed before it could test the intended evidence gate.
- Correction: updated the fixture to include a representative range-exclusion reason and added tests for both computable cases with a conclusive OI blocker and non-computable cases with unresolved partial legs.
- Verification: unit tests passed in [37992405659](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992405659) and final accepted run [37992502101](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992502101).

## F54-TEST-002 — incorrect threshold index in self-test — RESOLVED

- Failing runs: [37992248683](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992248683) and [37992317454](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992317454).
- Symptom: test expected a spread with 5.5% range to become eligible at the 4% threshold, though it should only pass at a threshold above 5.5%.
- Correction: changed the synthetic self-test to assert eligibility at 6%, with explicit reconciliation counts.
- Verification: [37992405659](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992405659) and [37992502101](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992502101) passed regression tests and self-test.

## F54-WORKFLOW-001 — failure-path persistence assumed a report directory existed — RESOLVED

- Failing runs: [37992248683](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992248683) and [37992317454](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992317454).
- Root cause: workflow removes the output directory before tests; when a preceding step failed, the unconditional `git add results/phase54/ohlc_reference_sensitivity` caused the persistence step itself to fail with pathspec exit 128.
- Correction: always stage status/log/README files, and stage report outputs only when the report directory exists.
- Verification: persistence succeeded in [37992423020](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992423020) and the full accepted run [37992502101](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992502101).

## F54-DATA-001 — stale Phase 54 parent CSV — RESOLVED

- Earlier status: the copied input had only 81 complete range-exclusion payloads, so the analysis correctly withheld alternate-threshold counts.
- Correction: synchronized the exact Phase 52 post-repair ledger into the Phase 54 branch. Both branch file contents match exactly (blob SHA `dc0d600be6bd96da6e016623f6b5f4ffaef9a644`; 480 rows); run [37992502101](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992502101) reports input SHA-256 `47904fac8b5fedc5fdca81af6cd555886f27ecec444d68403e4d2a5ccdb5621f`.
- Final reconciliation: 379/379 range-excluded rows and 1/1 replay-pass row contain complete per-leg payloads. The remaining 100 rows are rejected by an explicit required-leg prior-OI failure (prior OI below 100) and remain ineligible at all thresholds. All 11 thresholds reconcile to 480 rows; OI rejection and entry-data rejection counts are invariant; eligibility is monotonic in threshold.
- **Status:** RESOLVED. Phase 54 is closed as coverage sensitivity only; no P&L or bid/ask spread is inferred.
