# Error Log — main branch

## Phase 20 final status

The detailed Phase 20 error history is maintained on branch `phase-20-payoff-boundary-stop-research` because every research phase is isolated there.

No failed numerical run was used as evidence. Phase 20 ultimately completed successfully, its corrected 0.50× MFE comparator cross-check passed, and all final result artifacts were persisted.

See:
- https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/ERROR_LOG.md
- https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/results/dynamic_n_corrected/phase20_payoff_boundary/BOUNDARY_STOP_CONCLUSION.md


## Phase 23–24 final status

The detailed implementation-error history for the final research phases is maintained on branch `phase-24-targeted-reversal-trigger`, with every failed run logged and corrected before evidence acceptance.

See:
- https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-24-targeted-reversal-trigger/ERROR_LOG.md
- https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-24-targeted-reversal-trigger/results/dynamic_n_corrected/phase24_targeted_reversal/PHASE24_CONCLUSION.md


## Phase 27 final status

Phase 27 had multiple implementation corrections before evidence acceptance: raw exit-price retention, IV argument order, comparator/exit-precedence correction, and an artifact-persistence race. All were logged on the isolated Phase-27 branch. The final numerical run completed successfully and its artifacts were persisted. No superseded run was used as evidence.

See: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-27-delta-exit-research/ERROR_LOG.md


## Phase 28 engineering note — 2026-10-04
- The first Phase-28 calculation run remained in the minute-level calculation step without advancing its job metadata. This was treated as an infrastructure/run-management issue, not as research evidence.
- The workflow was hardened with concurrency cancellation and progress checkpoints. The replacement run completed and persisted the full individual-leg delta grid. No result from the stalled run was used.


## Phase 29 engineering corrections — 2026-10-05
- The initial joint-candidate implementation did not consistently apply selected 3-minute confirmation. The run was cancelled before evidence acceptance and the joint logic was corrected.
- The first corrected implementation used repeated Python path loops and was too slow for efficient CI execution. It was cancelled before evidence acceptance and replaced with vectorized first-hit confirmation logic. The replacement run completed successfully.
- The raw Phase-29 summary used the no-stop dynamic-n ledger as an internal diagnostic control. Before any promotion decision, the candidate was explicitly recomputed against the canonical Phase-20 P&L. No misleading raw full-sample uplift was used to promote the rule.
- Cancelled-run outputs were not accepted as evidence.


## 2026-10-06 — Phase 34 alternative prediction models
- Phase-34 numerical run #1 (37422843285) completed model computation but failed only at persistence because a newer code-touch run advanced the same branch. Its artifact was retained but not accepted as final evidence.
- Phase-34 numerical run #2 (37422865721) recomputed the frozen model set and successfully persisted the accepted evidence.
- Postprocess runs #1–#6 failed before producing accepted reporting output. The final diagnosis was a naming mismatch between `rf_phase33_control` in the model-metrics table and `rf_phase33` in the economic diagnostic. The mapping was corrected.
- Postprocess run #7 (37423631294) completed successfully. Earlier postprocess outputs are non-evidence.
- No numerical conclusion or promotion decision uses a failed or superseded run.


## Phase 37 correction record — 2026-10-06
Phase 36 model-selector direction polarity was found to be inverted relative to the Phase-35 up/down target semantics. The valid economic mapping is bullish/up -> PUT spread and bearish/down -> CALL spread. Phase 37 is registered to rerun the five model selectors with this correction. Phase-36 model-selector P&L is audit-only for this hypothesis.

See: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-37-model-direction-polarity-correction


## 2026-10-06 — Phase 41 interim implementation corrections
- Run 37463493504 failed in sequential replay because the live feature-row constructor did not preserve three registered auxiliary flow/sentiment columns. The correction reindexed the live matrix to the frozen feature schema before imputation.
- Run 37463984884 is the corrected sequential replay and supersedes the failed run; any failed/incomplete result is excluded from evidence.
- A no-op identity optimization was added after the fixed screen proved zero overrides for all frozen candidates across all three splits. This is an execution optimization, not a research-parameter change.


## 2026-10-06 — Phase 41 final closeout
- Run 37463493504 failed before evidence acceptance due missing live sparse feature columns; superseded.
- Run 37463984884 was superseded/cancelled during the no-op replay optimization; no result from it is used.
- Final accepted workflow run 37466520042 completed successfully after the schema correction and identity audit.


## F42-004 — 2026-10-06 — Accepted Phase 42 execution
- Corrected GitHub Actions run 37470344620 completed successfully through preflight, 72-variant screen, exact sequential replay, final inference/manuscript and artifact persistence.
- Earlier Phase 42 failures remain logged as non-evidence.


## F43-001 — 2026-10-06 — Phase 43 registration incident
- Initial attempt to persist Phase-43 registration files used an invalid JavaScript string payload because a repository identifier token was parsed as JavaScript syntax.
- No repository file was modified by the failed call and no numerical execution occurred.
- The payload was corrected; the Phase-43 research plan, pre-registration, status and literature review were then persisted successfully.
- This was an orchestration error only and is not research evidence.


## F43-002 — 2026-10-06 — Phase 43 workflow expression escaping
- The initial Phase-43 workflow/bridge persistence retained literal backslashes before GitHub Actions expression markers.
- No numerical evidence was accepted. The workflows were corrected before the next execution trigger.


## F43-007 — 2026-10-06 — Corrected postprocess bridge race-hardening
- The main-branch Phase-43 postprocess bridge is now rebase-safe before publishing corrected artifacts to the isolated phase branch.
- This change is infrastructure-only; no research parameter or data definition changed.


## 2026-10-06 — Phase 43 final correction log

### F43-004 — Invalid first VIX inference implementation
- The first regime inference compared a regime subset with the identical ALL rows, mechanically producing zero differences.
- Non-evidence output was superseded by regime-versus-complement inference.

### F43-005 — Unbounded benchmark contamination
- The first corrected postprocessor allowed `put_ratio_1x2` into the promotion benchmark even though unbounded ratio structures are diagnostic-only under the preregistration.
- Corrected promotion universe is now strictly defined-risk; final benchmark is `call_backspread`.

### F43-006 — Corrected postprocess publication race
- The corrected postprocess completed but its first artifact push was rejected non-fast-forward.
- Publication was hardened with fetch/rebase-before-push and rerun successfully.

### F43-007 — Main-bridge publication hardening
- The main-branch Phase-43 postprocess bridge was made rebase-safe before publishing to the isolated phase branch.
- Infrastructure-only; no research parameter changed.

**Phase-43 evidence rule:** only the final corrected/persisted branch artifacts support the conclusion; superseded inference and failed publication runs are audit-only.


## 2026-10-06 — Phase 44 initialization / F44-001 quarantine
- Phase 44 VIX candidate tuning was opened on isolated branch `phase-44-vix-candidate-tuning`.
- The first tuning implementation was audited before evidence acceptance; its initial workflow snapshot is classified **NON-EVIDENCE** because candidate-freeze logic did not satisfy the registered development-only selection discipline and the VIX threshold grid was incomplete.
- A corrected implementation was persisted on the Phase-44 branch before accepting numerical evidence.
