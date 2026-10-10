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

## Static and orchestration issues — resolved / superseded by completed run

- E91-010 — Static review found the copied engine initially emitted `"phase": 90` in the aggregate summary. It was corrected to `"phase": 91` before the completed run; the published summary verifies `phase: 91` and the registered period `2023-01-01` through `2024-01-01` exclusive.
- The initial repository check did not expose a run ID/results; this pending-trigger status was superseded by completed workflow run [38049302830](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38049302830). Job, engine, and aggregate publication steps all completed successfully.
- Phase 91 branch workflow declares `workflow_dispatch`; its Run button availability on the branch itself was not separately verified. The Phase90-base PR-triggered runner executed this PR's bounded study and published to the Phase91 branch; its availability is sufficient for the completed study.

## Final runtime result

- Run: [38049302830](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38049302830), workflow job `temporal-replication`, overall conclusion `success`.
- Options windows: 54/54 valid; India VIX windows: 5/5 valid; unique VIX instrument-master match.
- Paired CALL/PUT rows after validation: 18,473 across 246 sessions; zero spot mismatches and zero strike mismatches. India VIX coverage 99.984%; OOS VIX coverage 99.978%.
- Confirmatory OOS: 3,633 complete observations across 60 sessions. Both registered quality gates passed.
- Primary M1 MAE − M2 MAE: +0.0001111 bps; 95% paired session-cluster bootstrap CI −0.0110700 to +0.0102532 bps; positive share 52.4% (5,000 resamples, seed 90210). The interval crosses zero; no incremental gain was established.
- No API/network/schema failures. The workflow itself passed, but the primary research hypothesis did not meet its registered acceptance rule. This distinction is deliberate.

<!-- PHASE91_RUNTIME_START -->
## Runtime summary — 38050932108
- Status: NO INCREMENTAL GAIN ESTABLISHED — primary bootstrap interval includes or falls below zero
- Options valid chunks: 54/54
- VIX valid chunks: 5/5
- Instrument master: UNIQUE_MATCH; candidate count=1
- Paired rows: 18473
- OOS rows/sessions: 3633/60
- Issues:
- No API/network/schema failures.
- No token, raw response, row-level price, or hidden reasoning is logged.
<!-- PHASE91_RUNTIME_END -->
