# Phase 49 Status — VIX Leader Parameter Tuning

**CORRECTION IN PROGRESS — PRIOR NUMERICAL ATTEMPT NON-EVIDENCE**

Primary tuning families: Bear Call, Bear Put, Put BWB.
Primary regimes: LOW and NORMAL.
Raw geometry universe: 720.
Regime-expanded search universe: 1,440.

Development: 2021-2023.
Validation: 2024-2025.
Protected holdout: 2026.

The long-running GitHub Actions attempt 37535442553 is not evidence. A code audit found two scientific implementation defects before completion:
- the frozen-selection path referenced an undefined FAMILIES constant;
- validation was comparing active candidate trades against a pooled set of other candidate trades rather than the preregistered active-VIX versus complement-VIX opportunity set.

A further implementation mismatch was found between the preregistered forward-fold rule and the selector: the selector was requiring positive results in 2021/2022/2023 instead of using 2022 and 2023 as the registered forward scoring folds.

These corrections do not change the registered research question or parameter universe. The corrected run will:
1. select parameters using 2022 and 2023 forward-fold consistency, with 2021 retained as development context;
2. evaluate each frozen parameter on both its active VIX state and the complement states during validation;
3. use active-vs-complement bootstrap/permutation inference;
4. keep the 2026 holdout inaccessible to selection;
5. fail publication if development, validation or holdout data-error ledgers are non-empty.

No numerical conclusion, promotion, or holdout result from the superseded run is accepted.

Gate status:
- Definition audit: corrected, awaiting rerun.
- Data/lot-size audit: preflight passed on superseded run; corrected run must pass again.
- Development forward-fold sweep: pending.
- Parameter freeze: pending.
- Validation confirmation: pending.
- Holdout confirmation: pending.
- Final promotion: prohibited until all gates pass.
## 2026-10-07 — Execution watchdog correction

The superseded run 37535442553 stopped updating while the corrected run entered the Actions queue. Because the old run is already classified as NON-EVIDENCE, the workflow concurrency group is being advanced for the corrected execution rather than waiting indefinitely for a defective process.