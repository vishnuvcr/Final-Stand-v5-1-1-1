# Phase 95 Error Log

## Guardrails
- E95-001: Phase 83 protected 2026 holdout stays sealed; do not use HOLD rows.
- E95-002: Do not reopen the closed Phase 50B-7 candidate universe or tune existing strategies.
- E95-003: Use only the frozen source CSV and preregistered defined-risk/minimum-trade filter.
- E95-004: Structural validator PASS is not evidence of profitability.
- E95-005: Net50 is the source's 50%-friction scenario, not a claim of complete Paytm Money all-in execution costs.
- E95-006: No capital denominator means no return percentage claim.
- E95-007: Dataset has prior project exposure; this is retrospective, not blinded confirmatory evidence.
- E95-008: No strategy promotion based on Phase 95.

## E95-009 — Git blob fingerprint mismatch (2026-10-10)
- First hardened script used an incorrectly escaped NUL byte in Git's blob-hash prefix and rejected the unchanged source CSV.
- Evidence: failed workflow run [38054357252](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38054357252) reported expected blob SHA `4208da2e1189a68af697e11d03dd7d4ac937ddf7` but calculated `2fd4de73780ca29d21900712e55dae4248b86a0a`.
- Fix: construct the Git blob prefix using `bytes([0])`; the next run [38054413016](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38054413016) passed with the expected source fingerprint.

## E95-010 — Validation JSON newline encoding (2026-10-10)
- Code review found the generated JSON appended a literal backslash-n rather than a newline.
- Fix: changed the write suffix to a real newline escape. A subsequent workflow run is required to validate the final script revision.
- This was an output-format defect, not a change to the frozen selection result.

## E95-011 — Eligible-universe count corrected (2026-10-10)
- Initial prose used 22 candidates based on manual counting; the executable filter and canonical result register show 23 eligible candidates.
- Fix: corrected report denominator to 23, with 3 positive and 20 non-positive validation net50 outcomes.
- No candidate selection or primary endpoint changed.
