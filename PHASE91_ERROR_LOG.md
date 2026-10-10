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

## Runtime issues

No run recorded yet. Append the automated runtime summary after the workflow completes. Keep this log factual and make data/API failures explicit even if the workflow itself succeeds.
