# Phase 90 Error Log

Date opened: 2026-10-10. Never log credentials, raw response bodies, row-level market values or hidden reasoning.

## Registered guardrails
- E90-001 — Sample independence: do not re-use 2025 as a new confirmatory test; use 2024 only.
- E90-002 — Protected holdout: no 2026 dates or Phase 83 holdout records requested, loaded, cached or analyzed.
- E90-003 — Security ID: resolve India VIX from the current official Dhan instrument master; do not hardcode an unverified VIX ID.
- E90-004 — Timestamp alignment: option CALL/PUT spot/strike checks; exact 15/60-minute historical returns and 15-minute forward target; VIX as-of match max five minutes and session-bounded.
- E90-005 — Model leakage: scaler and coefficients fit only on Jan–Jun 2024. Validation is reporting-only; Oct–Dec OOS is never used for fitting.
- E90-006 — Caching/publication: raw payloads remain in Actions cache; publish only sanitized coverage and aggregate outputs.
- E90-007 — Execution gate: no strategy P&L or executable fills can be inferred from rolling ATM-relative OHLC/IV/OI; costs/slippage/latency are required for a later trade replay.

## Runtime issues
No run outcome recorded yet.

<!-- PHASE90_RUNTIME_START -->
## Runtime summary — 38048556674
- Status: PASS — small incremental OOS IV magnitude-prediction gain beyond spot features and India VIX; not strategy evidence
- Options valid chunks: 54/54
- VIX valid chunks: 5/5
- Instrument master: UNIQUE_MATCH; candidate count=1
- Paired rows: 18554
- OOS rows/sessions: 3604/60
- Issues:
- No API/network/schema failures.
- No token, raw response, row-level price, or hidden reasoning is logged.
<!-- PHASE90_RUNTIME_END -->
