# Phase 94 Error Log

Opened: 2026-10-10. Record reproducible defects, evidence gaps, and corrective actions. Never record credentials, raw protected holdout data, or hidden reasoning.

## Guardrails
- E94-001 — Source precedence: canonical result ledger and successful workflow run outrank README, prose summaries, and chat recollections.
- E94-002 — Empty samples: zero completed trades means non-estimable profitability, not zero-risk or validated zero return.
- E94-003 — Predictor boundary: spot forecast/feature association is not strategy P&L.
- E94-004 — Costs: do not call a result fully net unless brokerage, statutory charges, spread, slippage and relevant execution assumptions are accounted for.
- E94-005 — Denominators: no profit/trade, return percentage, or profit factor without valid denominator definitions.
- E94-006 — Holdout: Phase 83's 2026 holdout remains sealed.
- E94-007 — Multiplicity: do not select a strategy only because it is the top result among many unadjusted tests.
- E94-008 — Scope: no new market-data acquisition, trading rule replay, additional year sweep, or OOS tuning in Phase 94.
- E94-009 — Audit trail: record visible user instructions and work/outcomes only; do not copy hidden reasoning.

## Findings at initialization
- F94-01: Phase 66's two fixed CCI variants had zero completed trades in both DEV and VAL, making profitability metrics non-estimable.
- F94-02: Phase 89–92 results target absolute next-15-minute spot-return magnitude; they do not provide option P&L.
- F94-03: Phase 93 literature metrics are source-reported claims unless independently replicated.
- F94-04: Historical TT strategy metrics cannot be inferred from chat summaries; they require canonical source files and run IDs.

## E94-010 — Recent strategy ranking blocked by statistical gate (2026-10-10)
- Canonical Phase 50B files were checked on branch `phase-50b-final-manuscript`: TT-02/03/03-OTM350/04/05 summary outputs, TT-06/07 terminal classifications, chronological strategy summary, robustness summary, inference summary, and Phase 50B-7 status.
- TT-02 was negative across the four recorded cost scenarios. TT-04 and TT-05 turned negative at ₹20/order; both had negative chronological HOLD results. TT-03 and OTM350 point estimates remained positive in listed cost scenarios, but each had only three chronological HOLD trades.
- The preregistered Phase 50B-6 robustness artifact records 16 hypotheses and no robust-positive strategy; none of TT03, TT03_OTM350, TT04 or TT05 passed both all-cost positivity and Holm-corrected inference. The manuscript's terminal decision is NO PROMOTION.
- Correction/decision: added a separate canonical reconciliation artifact, kept the main evidence register's structural validator independent, and prohibited promotion based on raw point-estimate ranking. No model, strategy or market-data replay was run; Phase 83's 2026 holdout was not accessed.
