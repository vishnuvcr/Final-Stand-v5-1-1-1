# Phase 56 error log

Append every source, data, software, calculation, statistical or persistence error with the failing run URL/step, observed symptom, root cause, scientific impact, correction and regression verification. Never overwrite a failed result. Do not treat a successful Actions run as evidence without output inspection.

No Phase 56 execution errors recorded at initialization.

## F56-RUN-37995733702 — workflow or output validation failure

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37995733702
- Workflow status: failure
- Report accepted: False; report present: False
- No result or strategy conclusion accepted.
- Status: OPEN.


## F56-VALIDATION-001 — Canonical OI exclusion reason rejected by prose-only validator — FIXED, VERIFICATION RUN TRIGGERED

- Failing run: [37995733702](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37995733702).
- Symptom: replay stopped before analysis with `ValueError: OI-blocked row does not retain its canonical reason`; report absent.
- Root cause: the validator accepted only prose variants like “prior-bar OI” or “prior OI”, while the repaired canonical ledger stores `PRIOR_OI_MISSING_OR_BELOW_GATE` with underscores.
- Correction: normalize underscores and hyphens to spaces before validating the reason; retain the hard requirement that each blocked row has a selected leg with observed OI below 100.
- Scientific impact: no P&L output was produced by the failed run; no result accepted or strategy conclusion affected.
- Regression verification: workflow is triggered by the validator-file change; require the full 480-row ledger, all 11 thresholds, all 132 cost cases and all output invariants to pass before accepting results.
- Status: FIX APPLIED; awaiting workflow verification.

## F56-RUN-38019102367 — workflow or output validation failure

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38019102367
- Workflow status: failure
- Report accepted: False; report present: False
- No result or strategy conclusion accepted.
- Status: OPEN.
