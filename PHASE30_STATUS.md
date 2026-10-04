# Phase 30 Status

**Status: COMPLETE — REJECTED**

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


## Final result

GitHub Actions run **37228084351** completed successfully. Delta coverage was **99.21%**.

Training selected `target0.60_stop0.60_c1`, equivalent to exiting on a 60% proportional decrease/increase in combined short-leg delta magnitude from entry, with one-minute confirmation.

The selected rule was rejected because it underperformed the frozen Phase-20 strategy in validation by **₹56,130.10** and in the 2026 holdout by **₹17,171.69**. Full-sample P&L fell from **₹138,937.12** for the no-stop diagnostic comparator to **₹24,088.97** under the selected rule. Against canonical Phase 20, full-sample difference was **−₹125,040.56**.

The research conclusion is that **entry-referenced proportional change in the combined short-leg delta is not a useful exit mechanism for this strategy under the tested specification**.
