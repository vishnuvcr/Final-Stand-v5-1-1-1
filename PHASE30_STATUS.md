# Phase 30 Status

**Status: RUNNING**

This phase corrects Phase 29's definition.

Locked metric:
- entry combined short-leg delta = delta(S1) + delta(S2);
- operational magnitude = |delta(S1)| + |delta(S2)|;
- proportional change = current combined magnitude / entry combined magnitude - 1;
- no past-minute lookback;
- no difference in delta units;
- no mean of S1/S2.

Target = favorable proportional decrease from entry.
Stop = adverse proportional increase from entry.
Candidate exits use only this metric plus expiry fallback.

Training: through 2023-12-31.
Validation: 2024-01-01 through 2025-12-31.
Holdout: 2026-01-01 through 2026-09-30.

The frozen Phase-20 strategy remains the canonical comparator.
