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


## 2026-10-06 — Phase 33 setup/process errors
- Local container Git clone failed because outbound DNS/network access to github.com is unavailable in the container. No research evidence was affected; GitHub connector operations were used instead.
- An intermediate GitHub file-update call omitted the required current blob SHA and was rejected before any repository write. The operation was retried correctly using the fetched SHA. No incorrect repository content was committed from that failed call.

- Pre-run code review identified three issues before accepting any numerical result: push-trigger workflow inputs could override Python defaults with empty strings; the price-feature merge selected duplicate date/derived columns; and non-price global return columns were not shifted with their source levels. All were corrected before accepting Phase-33 evidence.
- LSTM lookback audit: pre-evidence review found the first implementation used prior expiry events rather than 30 completed trading sessions. Those runs are superseded. Corrected in commit 6bb06e263b0c46da9510d40c7effc5d93c2c0f1e.
- GitHub Actions run #7 (37420498240) failed before model execution. The run log showed Python receiving the literal string "\\2021-05-27" in SAMPLE_START because the workflow file contained an incorrectly escaped GitHub expression. No numerical evidence was produced. Corrected in 24fa7560fa486d0a11fe6902675cbe46c4489072.
- GitHub Actions run #8 (37420506663) reproduced the same pre-fix interpolation failure as run #7: SAMPLE_START was the literal "\\2021-05-27". No numerical evidence was produced. Runs #1–#8 before commit 24fa7560 are considered superseded/non-evidence; the exact date-expression bug was confirmed from run artifacts #7 and #8.
- Run #11 (37420911851) completed the full model computation successfully, but GitHub persistence failed with a non-fast-forward push. The runner committed the 15 output/cache files locally as commit f19f775 and then received "fetch first" because another Phase-33 run pushed to the same branch. The numerical artifact was preserved and inspected; future runs are now serialized with a concurrency group.
- Run #11 also exposed a methodological GARCH issue: EGARCH multi-step analytic forecasts are unsupported by the arch package, producing repeated "Analytic forecasts not available for horizon > 1" messages. This result is not accepted as the final GARCH evidence. Phase 33 was corrected to use simulation-based EGARCH forecasts for horizons >1.

- Reconcile workflow run #1 (37422050386) first failed because its shell inherited literal backslashes before variables from the template. Reconciliation run #2 fixed that and successfully downloaded/copy-staged the verified run-13 artifact, but failed at git commit because the runner had no configured user.name/user.email. This is corrected in commit 9716f8ec18d18e9db3ad4c5501f1b6b62d22d865.
- Postprocess run #2 (37422340652) failed on a numpy.ndarray .to_numpy() call in the signed-return diagnostic. Corrected in commit 2fc43d3db44a06743850ec6b339bd402bbecfd3c.
- Postprocess run #3 was superseded during correction; final postprocess run #4 (37422362350) completed successfully. No failed postprocess output was accepted as evidence.

- Postprocess run #2 failed because `np.where(...)` already returned an ndarray and the script called `.to_numpy()`. Corrected before the successful postprocess run #3 (37422362350).