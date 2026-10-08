# Phase 50B-3 Research Plan — VIX Conditioning

## Phase objective
Measure whether the feasible Phase-50B strategies behave differently across the fixed India-VIX state family using entry-time information only.

## Steps
1. Verify TT-02/03/04/05 terminal feasibility and zero-error artifacts.
2. Verify trade ledgers contain entry timestamps and all four registered cost fields.
3. Reconstruct VIX modes from the audited cached VIX series at each entry timestamp.
4. Produce DEV/VAL/HOLD regime-by-strategy tables.
5. Produce chronological equity/drawdown diagnostics for every registered regime cell.
6. Persist a machine-readable manifest of the exact 28 hypotheses.
7. Hand the unchanged 28-hypothesis family to Phase 50B-6 statistical inference.
8. Close the phase without selecting a regime from HOLD or changing VIX thresholds.

## Stop conditions
- Any missing required artifact -> fail closed.
- Any candidate below 95% coverage -> exclude using its terminal classification.
- Any VIX-unobservable trade -> report separately; never impute.
- No regime threshold tuning is permitted.
