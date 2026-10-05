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


## Phase 31 engineering errors
- Run 37228929824 failed before research because the workflow checked out the Phase-30 branch and therefore could not find the Phase-31 script. Corrected workflow checkout/path configuration.
- Run 37229041262 failed because a frozen research dependency (`research.backtest_dynamic_n_corrected`) was absent from the Phase-31 branch. Restored the dependency.
- Run 37229148481 failed because the canonical Phase-10 trade ledger was absent. Restored the frozen `phase10_primary/trades.csv` ledger.
- These failed runs produced no accepted research evidence. Run 37229448057 was the first successful Phase-31 execution.


## Phase 32 initialization engineering note — 2026-10-06
- The first automated GitHub file-write batch failed locally because the wrapper script had JavaScript quoting/template-literal syntax errors.
- The failure occurred before any Phase-32 repository mutation from that batch; no numerical evidence was generated or affected.
- The same registered Phase-32 file set was then written successfully in a corrected batch.


## Phase 32 CI error — 2026-10-06
- GitHub Actions run 37380393437 failed in the Phase-32 backtest step before numerical research: `ModuleNotFoundError: No module named 'numpy'`.
- Root cause: the repository did not have a dependency-install path for the scientific Python stack on this branch.
- The push-triggered workflow also passed empty SAMPLE_START/SAMPLE_END variables because workflow_dispatch inputs are unavailable on push events.
- No numerical evidence was produced or accepted.
- Correction: explicitly install numpy, pandas, pyarrow and huggingface_hub; harden script defaults for empty environment variables.


## Phase 32 CI error — implied-delta vectorization — 2026-10-06
- GitHub Actions run 37380443812 reached historical data processing but failed in `implied_delta()` because a scalar strike argument was combined with a vector of option prices/strikes.
- No numerical result was accepted.
- Correction: vectorize strike handling inside the implied-volatility/delta inversion and expose the repository HF_TOKEN secret to the workflow.


## Phase 32 CI error — Black–Scholes strike vectorization — 2026-10-06
- GitHub Actions run 37380642460 failed after the first vectorization correction because the lower-level `bs_price()` helper still treated strike as scalar.
- No numerical evidence was accepted.
- Correction: vectorize S, K, T and sigma consistently in both Black–Scholes price and delta helpers.


## Phase 32 model-specification error — monthly expiry exclusion — 2026-10-06
- Audit of the active backtest engine found that expiry enumeration removed the last expiry in each calendar month.
- This excluded monthly expiries even though the frozen strategy rule is current weekly expiry; the monthly expiry is the current weekly contract during its expiry week.
- Therefore runs using the pre-correction engine are invalid for evidence and must not be interpreted as performance results.
- Correction: include all dated weekly-expiry parquet files in the registered sample.
- Corrected commit: d1b44be28b87b2d6a264cc6ddcd72d3a551a9a2f.
- Corrected numerical run: 37383091606.
