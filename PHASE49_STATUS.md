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
## 2026-10-07 — Performance correction F49-009

The second self-audit found one more execution-only bottleneck: per-candidate recalculation of the full index day set, spot lookup and VIX historical quantiles. The engine has now been corrected to cache these metadata objects across candidates. No scientific definition changed and no numerical output from the slower runs is accepted.
## 2026-10-07 — Optimized numerical execution

GitHub Actions **run 37538954063 (#9)** is the current accepted execution candidate. Its preflight has passed; the numerical step is active. It uses the F49-009 metadata-cache correction. No result is accepted until the numerical, artifact, statistical and publication audits all pass.

## 2026-10-07 — F49-010 runtime-path correction

A final static audit found a remaining validation-stage import-path defect plus an unhandled zero-candidate development branch. The active optimized run #9 is therefore classified NON-EVIDENCE and will be superseded by a corrected execution. No result has been accepted.
## 2026-10-07 — Corrected rerun #11 active

After F49-010, GitHub Actions **run 37540089501 (#11)** is the current authoritative numerical execution. Its preflight has passed and the full tuning/confirmation step is running. Runs #9 and #10 are superseded/non-evidence.

## 2026-10-07 — F49-011 artifact-audit correction

Run #11 completed the numerical computation successfully but failed only at the artifact self-audit because the empty development error ledger was zero bytes. The numerical result is therefore not yet accepted. Run #12 is the authoritative corrected full rerun with the error-ledger header fix; parameter values and scientific definitions are unchanged.
## 2026-10-07 — F49-012 publication conflict

Run #12 passed the numerical and artifact self-audits. The only failure was the final Git publication step: concurrent repository audit updates to PHASE49_STATUS.md and RESEARCH_LOG.md conflicted with the workflow's rebase. The numerical evidence is therefore valid but not yet the canonical published closeout. A branch-triggered automatic reconciliation workflow has been started to publish the preserved artifact without rerunning the science.
## 2026-10-07 — F49-013 closeout packaging correction

Automatic closeout located the correct run #12 artifact and downloaded it successfully. The reconciliation failed only at manuscript table rendering because `tabulate` was not installed. This does not affect numerical evidence. The manuscript generator has been made dependency-independent and the closeout trigger will be rerun.