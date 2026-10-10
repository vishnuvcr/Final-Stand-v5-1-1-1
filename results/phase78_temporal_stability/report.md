# Phase 78 — Temporal stability reconciliation

**Decision: NO_PROMOTION_TEMPORAL_STABILITY_FAIL**

## Results

| Strategy | Historical HOLD trades | Historical HOLD net ₹10/order | HOLD +50% friction | HOLD ₹20/order | HOLD ₹20/order +50% | Partial trades | Partial net ₹10/order | Partial +50% friction | Partial ₹20/order | Partial ₹20/order +50% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TT-04 | 96 | -6456.29 | -11148.57 | nan | nan | 62 | 13271.51 | 10287.26 | 10345.11 | 5897.66 |
| TT-05 | 78 | -40244.68 | -44082.90 | -43926.28 | -49605.30 | 62 | 17098.15 | 14239.72 | 14171.75 | 9850.12 |
| TT-02 | None | nan | nan | nan | nan | 13 | -1341.12 | -2936.31 | -3701.12 | -6476.31 |

## Interpretation

This is a reconciliation of previously committed summaries, not a new independent test. The partial window is short and does not supersede the frozen historical HOLD split. Where historical HOLD and partial results disagree, the discrepancy is treated as temporal instability, not an invitation to retune. The two missing expiry dates remain excluded. No strategy is promoted.

## Audit errors

- None.
