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


## Phase 32 execution-convention error — final 120-second entry cutoff — 2026-10-06
- Audit found that the engine allowed fresh entries during the 15:28 and 15:29 one-minute bars.
- The frozen live execution convention states that action stops in the final 120 seconds before the 15:30 close.
- Those runs are invalid for evidence because they can create trades that the live strategy would not initiate.
- Correction: reject fresh entries at or after 15:28 IST in the 1-minute historical engine.
- Corrected commit: 1513a1c00df8693ea630f6dae52d67a28164c1c7.


## Phase 32 serious state-machine/lookahead error — 2026-10-06
- The first continuous-loop implementation selected an exit by scanning future observations and then continued the entry-day timestamp loop.
- This could permit a new entry at a timestamp earlier than the already-selected future exit, creating impossible overlapping/re-entry behavior and lookahead contamination.
- No numerical evidence from those runs is accepted.
- Correction: replace the nested day/entry loop with a strict chronological cursor; after exit, resume only at the first timestamp strictly after the realized exit.
- Corrected commit: df8f9c0ca6e3fd3f84bcd6bd9c432f0b03ea171e.


## Phase 32 implementation regression — missing expiry_ts after state-machine rewrite — 2026-10-06
- Corrected run 37384048259 failed before numerical execution because the rewritten `run_expiry()` did not restore the `expiry_ts` column required by `nearest_delta_strike()`.
- No research evidence was produced or accepted.
- Correction: restore the expiry timestamp column in `run_expiry()`.
- Corrected commit: 81b83fb4af8f075a9fec2bab42304a7c8964b45a.


## Phase 32 historical lot-size schedule error — 2026-10-06
- Audit found that the engine used a simplified calendar-date lot-size schedule that did not distinguish the transition dates for NIFTY weekly versus monthly expiries in late 2024/early 2025.
- This can materially scale trade P&L and costs, so earlier numerical outputs are invalid for evidence.
- Corrected using NSE expiry-specific transition dates: 02-May-2024, 19-Dec-2024 / 02-Jan-2025 weekly transition, 30-Jan-2025 / 27-Feb-2025 monthly transition, and 06-Jan-2026 / 27-Jan-2026 transition to 65 lots.
- Corrected commit: a29a17470b751c947ba1aa0f8c7ed6d3abfc6e13.


## Phase 32 state-machine error — zero-net outcome handling — 2026-10-06
- The engine treated every non-positive net result as a loss and therefore flipped direction after an exactly zero-net trade.
- The frozen rule explicitly states zero P&L -> keep the same direction.
- No result from the pre-correction run is accepted.
- Correction: branch direction on positive, negative, and exactly zero net P&L separately.
- Corrected commit: 559f520ba7feb795e2b09fd6ab17bfc083fd7ba0.


## Phase 32 historical contract-size error — 30-Jan-2025 NIFTY monthly lot — 2026-10-06
- Audit against NSE Circular 131/2024 found that the existing NIFTY monthly expiry on 30-Jan-2025 retained the old 25 lot, while revised weekly contracts had already moved to 75 from the 02-Jan-2025 weekly expiry.
- The date-only lot-size function incorrectly assigned 75 to the 30-Jan-2025 monthly expiry.
- No result from the pre-correction engine is accepted.
- Correction: explicit 30-Jan-2025 monthly exception at 25 lots.
- Corrected commit: 29458cacb40eab39cdd96c1b57881a70b1829b74.


## Phase 32 current-week contract window error — 2026-10-06
- The prior engine examined each expiry using the preceding 14 calendar days, which could trade the next week's contract before it became the current weekly expiry.
- This violates the frozen strategy definition and can materially change entries, direction state and P&L.
- Correction: each expiry gets a non-overlapping evaluation window beginning strictly after the previous expiry's contract termination. The first available expiry has no prior in-sample window and therefore cannot generate a valid entry.
- Corrected commit: 1675f86b8a71add7a73c03479731e3a5623716b.


## Phase 32 performance bottleneck — scalar exit-delta inversion — 2026-10-06
- The corrected engine performed Black–Scholes implied-volatility inversion separately for every future minute and every trade.
- This created excessive runtime without adding methodological information and could exceed the CI timeout.
- Correction: vectorize the same exit-delta calculation over the entire future path, then select the first qualifying observation chronologically.
- This does not alter the trading rules or numerical inputs.
- Corrected commit: c0ec4b90fd33eee75ed0515343e28d431aee924a.
