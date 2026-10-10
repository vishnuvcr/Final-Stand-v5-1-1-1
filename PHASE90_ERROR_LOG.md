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
The initial study run and cached interpretation rerun both completed successfully. No API/network/schema failures occurred. The measured gain is small; see the effect-size caveat in the results report.

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

## E90-008 — downstream replication complete; result does not replicate the small 2024 gain

Phase 91 completed successfully in [Actions run 38050932108](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050932108). The 2023 sample had 3,633 OOS rows across 60 sessions; M1−M2 MAE = +0.0001111 bps, 95% paired session-cluster CI −0.0110700 to +0.0102532. The interval crossed zero, so no incremental gain was established. This is a child-phase scientific result, not a Phase 90 execution error. No strategy P&L was computed or strategy promoted.


## E90-009 — Phase 92 cross-phase stopping decision

Phase 92's independent 2022 synthetic-forward/OI predictor study completed successfully in [run 38050805106](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050805106). The primary result was negative incremental value for the added feature block: M2−M4 MAE −0.1708363 bps, 95% CI −0.2298769 to −0.1152015. The [cross-phase synthesis](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-92-synthetic-forward-oi-study-2022/results/phase92/CROSS_PHASE_FACTOR_SYNTHESIS.md) closes this feature-prediction line at its preregistered stopping condition. No strategy P&L was computed or strategy promoted.
