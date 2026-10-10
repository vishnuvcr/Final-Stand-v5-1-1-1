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
- F94-04: Existing recent summaries do not by themselves reconcile every historical TT strategy to a canonical ledger; no cross-strategy ranking should be invented from those summaries.

## Defects and corrections
No Phase 94 validator defect has yet been observed. Add an entry if validation exposes one; distinguish documentation/tooling defects from research/data errors.
