# Phase 28 Status — COMPLETE

**Question:** Does individual-leg delta, especially the two short legs, improve exits relative to the frozen Phase-20 strategy?

**Branch:** `phase-28-individual-leg-delta-research`

**Delta coverage:** 99.21%

## Result

Training-selected profit rule: **S1 |delta| ≤ 0.05 after MTM ≥ 90% of original target**.

| Period | Control net | Candidate net | Uplift |
|---|---:|---:|---:|
| Training | ₹62,905.98 | ₹59,907.82 | −₹2,998.16 |
| Validation 2024–2025 | ₹75,809.78 | ₹73,322.73 | −₹2,487.05 |
| 2026 holdout | ₹10,413.76 | ₹10,377.85 | −₹35.91 |
| Full | ₹149,129.53 | ₹143,608.40 | −₹5,521.12 |

Bootstrap mean paired uplift:
- Validation: −₹32.30/trade, 95% CI [−₹45.80, −₹20.92]
- Holdout: −₹2.24/trade, 95% CI [−₹6.73, ~₹0]
- Full: −₹29.06/trade, 95% CI [−₹35.64, −₹23.19]

No adverse short-leg delta stop was promoted.

## Interpretation

S1 is more delta-sensitive than S2 at entry on average (mean absolute delta ≈0.180 vs 0.155), but this did not provide robust incremental exit timing. The absolute-delta level hypothesis is therefore rejected.

**Canonical strategy remains Phase-20.**
