# Phase 57 status — cost-aware OHLC-range sensitivity replay

**Overall:** ACTIVE — independent endpoint reproduction of Phase 56 modeled-P&L sensitivity; no strategy promotion.

- Branch: `phase-57-cost-aware-range-sensitivity-replay`
- Parent: Phase 55 leg audit PASS; Phase 54 coverage sensitivity CLOSED; Phase 56 source OI diagnosis PASS.
- Frozen universe: 40 BASELINE configurations × 24 development/validation events = 480 configuration-event rows.
- Frozen data revision: `0f4800e43e6f96cec0794369d78eb4d3c4211ef5` (CC BY-NC 4.0 research-only).
- Thresholds for this independent reproduction: 2% frozen baseline and 1000% diagnostic near-removal. The canonical Phase 56 report already covers all 11 preregistered thresholds.
- Costs: ₹20/order primary; ₹10/order sensitivity; date-aware statutory charges; ₹0.05 adverse slippage per leg fill with 0/50/100% stress.
- Not a spread or executable-fill test. No holdout, winner ranking or promotion.

## Gates
- Plan: FROZEN.
- Regression tests: PENDING.
- 11-threshold replay: PENDING.
- Cost reconciliation and source hashes: PENDING.
- Artifact/log persistence: PENDING.


## Plan amendment PA-57-001

The original 11-threshold source-driven replay was too computationally expensive because each configuration-event call repeatedly scans full option frames. Phase 56 already supplies the complete 11-threshold cost matrix, so Phase 57 is narrowed to two endpoint thresholds for independent reproduction. Workflow concurrency now cancels superseded runs; the bounded run must finish within 30 minutes.
