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


## F56-VALIDATION-002 — Normalized prior-bar wording still rejected — FIXED, VERIFICATION RUN TRIGGERED

- Failing verification run: [38019102367](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38019102367).
- Symptom: two unit tests still failed at the canonical OI reason check after the first validator correction.
- Root cause: converting hyphens to spaces changes “prior-bar OI” into “prior bar OI”; the updated check accepted “prior OI” and “prior open interest” but omitted “prior bar OI”.
- Correction: explicitly accept the normalized phrases “prior OI”, “prior bar OI” and “prior open interest”, including the canonical underscore form after normalization.
- Scientific impact: tests failed before the P&L analysis; no outputs accepted.
- Verification: a new automatic workflow run is triggered by this correction. Full regression suite and all report invariants must pass.
- Status: FIX APPLIED; awaiting verification.


## F56-VALIDATION-001 / F56-VALIDATION-002 — RESOLVED

- Corrected the reason validator to normalize underscores/hyphens and accept “prior OI”, “prior bar OI” and “prior open interest” wording while retaining the explicit OI<100 hard-block invariant.
- Verification: [run 38019146547](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38019146547) passed syntax validation, all five regression tests, deterministic self-test, complete matrix generation, output invariant validation, artifact upload and checkpoint persistence.
- Accepted outputs: 480-row parent reconciliation, 11 threshold counts matching Phase 54, 18,960 cost-scenario rows, and all monotonic cost invariants PASS.
- Scientific impact of prior failed runs: no result was accepted from them; the failures occurred before P&L output. No strategy conclusion was changed by the repair.
- Status: RESOLVED; Phase 56 closed as non-executable price-reference sensitivity.
