# Phase 96 Error Log

## Guardrails
- E96-001: Never retain/use `holdout` split rows; Phase 83's protected 2026 holdout remains sealed.
- E96-002: Use only LOW/NORMAL/HIGH regimes; do not add overlapping directional/spike states after seeing results.
- E96-003: Defined-risk-only strategies; minimum 20 DEV and 20 VAL trades per selected regime.
- E96-004: Selection is based only on DEV net50, never validation.
- E96-005: This is retrospective summary-table research, not independent blinded evidence or a new strategy replay.
- E96-006: Source net50 is not proof of complete Paytm Money all-in costs or executable fills.
- E96-007: No capital denominator or trade-overlap ledger means aggregate state P&L is not a deployable portfolio return.
- E96-008: No strategy promotion from Phase 96.

No execution defects observed yet.


## E96-009 — HIGH-regime feasibility failure (2026-10-10)
- First registered run [38054761000](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38054761000) failed because no defined-risk HIGH-regime candidate met the 20-DEV/20-VAL trade minimum.
- Resolution: preregistered a feasibility amendment before examining candidate P&L: minimum 5 trades in both DEV and VAL for every fixed regime. This reduces evidential strength; report exact counts and retain NO PROMOTION.


## E96-010 — Second HIGH-regime coverage failure (2026-10-10)
- The 5-trade minimum still found no eligible HIGH candidate. A split-filtered coverage audit found HIGH-regime DEV rows have 6 trades but matching validation rows only 3 trades for the available defined-risk candidates.
- Resolution: registered a minimum of 3 trades per split for all three regimes. HIGH-regime findings are explicitly low-powered and descriptive; no promotion allowed.

## E96-011 — Regime-selection result failed (2026-10-10)
- Successful computation run [38054856414](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38054856414) selected LOW=`strap`, NORMAL=`strip`, HIGH=`short_iron_condor` by development net50. Validation net50 values were −₹187,009.45, −₹113,665.57 and −₹2,760.10; aggregate −₹303,435.13.
- Decision: method fails; no strategy promoted. HIGH has only 3 validation trades after documented feasibility amendments and is not inferentially reliable.
- Limitation retained: source net50 is not evidence of complete Paytm Money all-in execution costs; no trade-overlap/capital-allocation ledger exists to support portfolio claims.
