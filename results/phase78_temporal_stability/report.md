# Phase 78 — Temporal stability reconciliation

**Decision: NO_PROMOTION_TEMPORAL_STABILITY_FAIL**

## Results

| Strategy | Historical HOLD trades | Historical HOLD net ₹10/order | HOLD +50% friction | HOLD ₹20/order | HOLD ₹20/order +50% | Partial trades | Partial net ₹10/order | Partial +50% friction | Partial ₹20/order | Partial ₹20/order +50% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TT-04 | 96 | -6456.294614748596 | -11148.566922122842 | NA | NA | 62 | 13271.506311950925 | 10287.259467926428 | 10345.106311950924 | 5897.659467926425 |
| TT-05 | 78 | -40244.680782598574 | -44082.89617389783 | -43926.280782598595 | -49605.29617389782 | 62 | 17098.146574629933 | 14239.719861944934 | 14171.746574629931 | 9850.119861944935 |
| TT-02 | None | NA | NA | NA | NA | 13 | -1341.120832479497 | -2936.306248719252 | -3701.120832479496 | -6476.306248719249 |

## Interpretation

This is a reconciliation of previously committed summaries, not a new independent test. The partial window is short and does not supersede the frozen historical HOLD split. Where historical HOLD and partial results disagree, the discrepancy is treated as temporal instability, not an invitation to retune. The two missing expiry dates remain excluded. No strategy is promoted.

## Audit errors

- None.
