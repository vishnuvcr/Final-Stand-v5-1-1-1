# Phase 30 Status

**Status: IMPLEMENTED — AWAITING GITHUB ACTIONS EXECUTION**

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


## Execution state
The corrected script and workflow are committed. The GitHub connector available to this research session does not expose a workflow-dispatch operation, and no workflow run is currently visible for the branch commits. Therefore no Phase-30 numerical result is accepted yet.

This is an infrastructure state, not a research result. The phase remains open until the registered workflow executes successfully and persists its grid, walk-forward comparison, bootstrap diagnostics, and conclusion.
