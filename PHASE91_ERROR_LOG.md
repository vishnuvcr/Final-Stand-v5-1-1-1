# Phase 91 Error Log

Opened: 2026-10-10. Never log credentials, raw response bodies, row-level market values, or hidden reasoning.

## Registered checks and failure handling

- E91-001 — Temporal independence: acquire calendar 2023 only; do not reuse Phase 90's 2024 cache/data or Phase 89's 2025 sample.
- E91-002 — Protected holdout: do not request, load, cache or analyze Phase 83's 2026 holdout.
- E91-003 — Date boundary: requests cover 2023-01-01 inclusive to 2024-01-01 exclusive; validate timestamp rows are within 2023.
- E91-004 — India VIX: resolve its ID dynamically from the current official instrument master and require exactly one eligible match.
- E91-005 — Pairing/temporal correctness: exact CALL/PUT timestamp join, matching strikes, spot consistency, session-only lags/target, and VIX as-of staleness at most five minutes.
- E91-006 — Leakage: model preprocessing/coefficients fit on Jan–Jun 2023 only; Jul–Sep validation is report-only and Oct–Dec OOS never informs fitting.
- E91-007 — Statistics: fixed model definitions, one primary endpoint, fixed seed 90210 and 5,000 session-cluster bootstrap resamples; no OOS tuning or subgroup significance tests.
- E91-008 — Safe publication: raw data stays in the Phase 91 Actions cache; only aggregate results and sanitized issue summaries are published.
- E91-009 — Execution evidence: rolling ATM IV/spot prediction does not prove exact-contract fills/profitability; do not compute strategy P&L or promote a strategy from this phase.

## Runtime / trigger verification checkpoint — 2026-10-10

- After registering the engine, workflow, and plan update, the branch still contained the initial PREREGISTERED status and no `results/phase91/summary.json` or `results/phase91/PHASE91_RESULTS.md` file was yet present.
- The available repository status checks did not surface an Actions run ID for the latest phase commit. This is an execution-verification blocker, not a data result. It does **not** mean the model failed or the IV signal is absent.
- Do not claim acquisition succeeded, do not infer a negative/positive replication result, and do not promote any strategy until the Actions-generated aggregate results are available.
- Manual dispatch remains available in the workflow's GitHub Actions UI. The workflow itself is registered with both a branch/path push trigger and `workflow_dispatch`.

Append the automated runtime summary here after a confirmed workflow run. Keep failures explicit even if the workflow process itself exits successfully.
