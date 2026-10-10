# Phase 63 Research Plan — Available-data inference audit

## Research question
What can be concluded from existing development/validation data without waiting for the two missing 2026 option blocks or further using the protected 2026 holdout?

## Aim
Continue using data already available in the repository, while keeping Phase 51's full window and Phase 52's factor-source gates unchanged. This is an evidence audit and reanalysis of existing development/validation artifacts, not a new strategy search on the 2026 partial holdout.

## Objectives
1. Inspect existing Phase 50B development (2021–2023) and validation (2024–2025) artifacts and frozen inference workflow.
2. Verify candidate identities, source hashes/manifests, trade ledgers, costs, coverage and error gates before using results.
3. Use only preregistered development/validation inferential procedures; do not invent thresholds after inspecting outcomes.
4. Keep 2026 holdout out of hypothesis tests, Holm correction, parameter selection, candidate ranking and model choice.
5. Use available-data Phase 51-3 results only as already-published descriptive context; do not run additional selection tests on those holdout results.
6. Preserve Paytm Money ₹10/order and ₹20/order scenarios, +50% friction stress, slippage, statutory costs, coverage exclusions and drawdown caveats.
7. Publish a manuscript-quality evidence matrix, limitations and finite stop decision.

## Frozen constraints
- Do not change Phase 50B strategy definitions, preregistration, regime thresholds or inference family.
- Development: 2021–2023; validation: 2024–2025; protected holdout: 2026.
- The 2026 Phase 51 partial interval (2026-04-21 to 2026-07-21) is already exposed in existing reports and must not be treated as untouched confirmation.
- Missing 2026-07-28 and 2026-08-04 option blocks remain missing. Do not claim full Phase 51 completion or alter the full-window endpoint.
- Phase 52 remains blocked for new factor-conditioned claims requiring prior-minute OI/quote sufficiency. Do not treat OHLC ranges as bid/ask spreads.
- No paid data purchases, credentials, live deployment or trade execution.
- Raw/licensed data must not be committed or redistributed.

## Methods and analysis
1. Read Phase 50B preregistration, candidate registry, source/baseline audit, error logs, and existing statistical-gate/manuscript artifacts.
2. For each candidate, verify inference uses DEV+VAL only, VIX state is reconstructed at entry using frozen definitions, and missing history is excluded consistently from active and complement samples.
3. Reproduce only existing registered analyses: active-regime versus complement bootstrap inference, two-sided permutation inference, Holm correction across the frozen family, paired common-expiry baseline comparisons, and annual/regime summaries where underlying artifacts exist.
4. Verify cost robustness at ₹10/order and ₹20/order with +50% friction; if any required cost output or source artifact is absent, mark that candidate incomplete rather than substitute values.
5. Do not calculate new p-values from the Phase 51 2026 partial-OOS sample.
6. Independently reconcile result tables against source artifacts, preserve exclusions, and log every discrepancy.

## Decision rules
- AUDIT_PASS: frozen preregistered DEV+VAL artifacts reproduce and all gates are evidenced.
- INCOMPLETE: any required data/artifact/lineage is missing.
- NO_PROMOTION: default unless all preregistered economic, statistical, coverage and cost gates are already satisfied.
- This audit cannot promote a strategy on its own. A protected holdout confirmation must already be valid and must not be reused for tuning.
- If repository artifacts are incomplete, stop with an exact missing-artifact list rather than launching repetitive source searches.

## Deliverables
- Phase status, detailed research log, user-visible chat/action log and error log.
- Machine-readable candidate evidence matrix.
- Structured research report with methodology, results, statistical caveats, strengths/limitations, conclusions and future work.
- Workflow with manual dispatch and bounded automated execution, using repository/cached artifacts where possible.
- README links and current status update.

## Finite stop rule
Audit the existing DEV+VAL evidence and frozen inference results once. Do not initiate another strategy sweep, mutate parameters, or reanalyse the exposed 2026 holdout for selection. Close after reproducibility and evidence sufficiency are determined.
