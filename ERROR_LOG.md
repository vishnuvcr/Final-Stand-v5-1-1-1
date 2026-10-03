# Error Log

| Date | Phase | Error / limitation | Action |
|---|---|---|---|
| 2026-10-02 | Phase 1 restart | Prior implementation used a global maximum over all 20 call/put candidates. | Superseded prior results and restarted with the two-stage selector. |
| 2026-10-02 | Phase 1 restart | Prior DTE convention counted expiry as one of four sessions. | Restarted with four trading sessions before expiry, expiry=0 DTE. |
| 2026-10-02 | Phase 1 restart | Higher-n preference lacked a numeric weight. | Pre-registered 95%-of-maximum-X threshold; 90%/97.5% reserved for robustness. |
| 2026-10-02 | Phase 1 restart | Non-positive X would make target non-meaningful. | Record NO_POSITIVE_X and do not enter. |
| 2026-10-02 | Phase 1 restart | Far-strike coverage can be sparse. | Require complete selected legs and log exclusions without imputation. |
| 2026-10-02 | Phase 1 restart | Historical bid/ask unavailable. | Use explicit adverse slippage and label fills as modelled. |
| 2026-10-02 | Phase 2 | Initial implementation accepted incomplete n=6..15 candidate sets. | Corrected to require complete candidate set and reran. |
| 2026-10-02 | Phase 2 | Workflow temporarily push-gated for autonomous execution. | Restored manual-only after execution. |
| 2026-10-02 | Phase 3 | First statistics run failed in grouped aggregation. | Replaced groupby-apply with explicit grouped loops; rerun succeeded. |
| 2026-10-02 | Phase 3 | Trade-level Sharpe/Sortino denominator is not portfolio capital-at-risk and trades have irregular duration. | Reported explicitly as non-annualized credit-normalized diagnostics, not as annualized investment Sharpe. |
| 2026-10-02 | Phase 3 | n=7/8/15 samples are very small. | Report descriptive values only; do not treat them as stable estimates. |

## 2026-10-02 — Phase 4 execution correction
- The first retry still used a workflow commit whose checked-out tree preceded the syntax fix. A fresh marker commit is required so the runner checks out the corrected backtest.

## 2026-10-02 — Phase 4 second syntax correction
- A second literal-newline insertion existed in the summary metadata block. Corrected before the next autonomous run.
| 2026-10-02 | Phase 4 | Robustness runner completed all scenarios, but its result-persistence push was rejected because the remote branch had advanced; remote summary files therefore retained stale returncode metadata. | Record runner output as valid only after reconciliation; fix workflow persistence with fetch/rebase before push and explicitly write returncode=0 for completed scenarios. |

| 2026-10-03 | Phase 6 restart | Earlier v2 strategy used OTM6-based Stage 1 and high-n selection, which does not match the newly requested fixed OTM15 strategy. | Superseded v2 evidence and created a new v3 fixed-OTM15 research plan, specification, branch and backtest. |

| 2026-10-03 | Phase 7 execution | Three push-triggered runs were started because the workflow was temporarily push-gated for autonomous execution. | All runs used the same locked code/data; primary successful result was persisted once and will be used for Phase 8. Workflow will be restored to manual-only after automated execution is complete. |

| 2026-10-03 | Phase 8 trigger | First Phase 8 push-triggered run was skipped before executing the statistical job. | Added explicit marker retry; no research calculation was performed by the skipped run. |


| 2026-10-03 | Phase 9A audit | Uploaded AlgoTest reports are not configuration-equivalent to the locked research strategy: 09:35 vs 10:00 entry, 15:14 fixed exit vs target/expiry exit, four visible legs vs three, separate static call/put tests vs conditional X selector, fixed quantity 65 vs date-aware historical lot sizes, and 0%/disabled cost settings vs modeled costs. | Added a dedicated reconciliation audit before interpreting the apparent performance contradiction. |


| 2026-10-03 | Phase 9A audit | The first AlgoTest PDFs supplied were the wrong files and led to an invalid four-leg interpretation. | Marked that interpretation superseded; re-audited the newly uploaded three-leg call/put reports. |


| 2026-10-03 | Phase 7B strike-mapping audit | Initial fixed OTM15 implementation treated OTM15/16/17 as ordinal ranks among quoted strikes. This skipped exact strikes when a minute quote was missing. | Reclassified OTM15/16/17 as exact NIFTY strike-ladder distances using the ₹50 weekly/monthly strike interval; missing exact strikes will be logged/excluded. All initial Phase 7/8/9 numerical results are superseded pending rerun. |


| 2026-10-03 | Phase 7C P&L accounting audit | The P&L formula had the signs of all three legs inverted relative to the actual long/short execution directions. For a long OTM15, P&L is exit minus entry; for the short OTM16/17 legs, P&L is entry minus exit. | Corrected the shared P&L formula in the primary backtest and AlgoTest reproduction. The Phase 7B and Phase 9C numerical outputs are superseded. The uploaded AlgoTest first trade independently confirms the corrected convention: buy 1.90 -> sell 0.05 is -₹120.25, sell 1.70 -> buy 0.05 is +₹107.25, sell 1.80 -> buy 0.05 is +₹113.75, total +₹100.75. |


| 2026-10-03 | Dynamic-n restart | Previous dynamic-n results were generated before the strike-mapping and P&L-sign corrections discovered during AlgoTest reconciliation. | Marked all previous dynamic-n numerical results and ledgers superseded; new branch uses exact strike distances and corrected long/short accounting. |


| 2026-10-03 | Dynamic-n execution audit | First dynamic-n Actions run failed because Stage 1 checked only dictionary length, which could equal three while a required OTM6/7/8 key was absent; direct key access then raised KeyError. | Changed validation to explicitly require OTM6, OTM7 and OTM8 on both call and put sides before calculating Stage 1. No research result was produced by the failed run. |


| 2026-10-03 | Dynamic-vs-fixed comparison | Comparison script failed during construction of the direction table because two DataFrames with different indexes were passed directly to DataFrame(). | Replaced with pandas concat; no comparison result was produced by the failed run. |


| 2026-10-03 | Research design extension | Full-sample dynamic-n vs fixed OTM15 comparison also changes the Stage-1 direction selector, so it cannot isolate the contribution of n-selection alone. | Added controlled fixed6/fixed15/dynamic ablation with the same OTM6/7/8 Stage-1 direction selector and identical execution assumptions. |


| 2026-10-03 | Phase 15 n-selection ablation | First ablation Actions run failed before completing the matrix. | Reran with an explicit marker commit; fixed6, fixed15 and dynamic jobs completed successfully and persisted results. |


| 2026-10-03 | Phase 17 stop-loss execution | First Phase 17 GitHub Actions run failed before calculation because `research/stop_loss_research.py` could not import the local `research` module under the Actions execution path. | Added the repository root to `sys.path`; no stop-loss result was produced by the failed run. |


| 2026-10-03 | Phase 17 stop-loss script | Second Phase 17 execution exited successfully but produced no results because the `summarize/main` section had been truncated during a file patch; the script defined helper functions but never invoked the research. | Restored the full `summarize()` and `main()` execution section and added full-sample selected-rule outputs. No research result from that run is used. |


| 2026-10-03 | Phase 20 design | Entry-time payoff-chart green area is an expiry-time construct; an intraday NIFTY breach can occur while option time value remains. | Treat the expiry zero-P&L boundary as a structural stress boundary and pre-register negative-MTM and MFE-filtered variants rather than assuming every breach is an automatic loss. |
| 2026-10-03 | Phase 20 data alignment | NIFTY spot and all three option legs may not share every exact minute timestamp. | Use only exact common timestamps for boundary-stop evaluation; no forward filling or interpolation. |

| 2026-10-03 | Phase 20 execution | First real Phase 20 Actions run failed with `ModuleNotFoundError: No module named 'research'` before analysis. | Added the repository root to `sys.path`, matching the proven Phase-17 fix; no research output from the failed run is used. |

| 2026-10-03 | Phase 20 execution | Second Actions run reached the boundary evaluation but failed because the path map returned metadata dictionaries instead of minute-path lists, causing `TypeError: string indices must be integers`. | Changed the path-map return value to map each expiry directly to its `path`; no research output from this run is used. |

| 2026-10-03 | Phase 20 execution | Third Actions run failed in `charges()` because the reconstructed path stored the DataFrame integer row index as the stop timestamp. | Changed the path builder to store `row['timestamp']` as a timezone-aware pandas timestamp; no numerical result from the failed run is used. |

| 2026-10-03 | Phase 20 execution | Fourth Actions run completed the research calculations but failed in the final alignment-error reporting because the refactored path map now contains lists rather than dictionaries. | Returned the path map together with its error-record list and updated the final report writer; no persisted numerical result from that run is used. |

| 2026-10-03 | Phase 20 result persistence | Fifth Actions run completed the boundary research successfully but result commit push was rejected because the branch advanced during execution. | Persistence step now fetches and rebases onto the current Phase-20 branch before pushing. The numerical output itself was valid; the persisted copy is being regenerated with the corrected Phase-19 0.50x comparator. |

| 2026-10-03 | Phase 20 result persistence | Sixth run completed the corrected comparison but was still executed with the pre-rebase workflow revision, so its generated result commit was rejected by the remote branch. | Workflow revision `96bf697` now rebases before pushing; a final calculation trigger will use that revision. |


| 2026-10-03 | Phase 20 completion audit | Phase-19 published selected ledger represented the formal 1.00× MFE train-selected rule, while the locked research comparator was the 0.50× robustness candidate. | Reconstructed the 0.50× comparator directly from minute paths and required an exact cross-check against Phase-19 grid values before accepting the Phase-20 comparison. Cross-check passed. |
| 2026-10-03 | Phase 20 final decision | Entry-time payoff-boundary stops can appear attractive in training while harming later periods because expiry payoff boundaries are not intraday fair-value boundaries. | Retain the fixed 13:30 expiry-day conditional stop and explicitly reject all payoff-boundary stops from the final historical specification. |

| 2026-10-03 | Phase 21 design | Extra hedge option data initially lacked normalization. | Normalization was fixed before the first workflow run; no Phase 21 result was produced before the fix. |
| 2026-10-03 | Phase 21 start | Pre-expiry adverse-move protection requested. | Frozen a bounded test of early exits and one-lot OTM-(n+3) tail hedges on top of the Phase-20 comparator. |

| 2026-10-03 | Phase 21 execution | Final research grid contained no rule with zero baseline-positive training trades affected; the first implementation aborted before persisting diagnostics. | Changed the phase runner to persist the complete grid and top unconstrained diagnostics instead of aborting. No candidate was promoted. |
| 2026-10-03 | Phase 21 reporting | The first diagnostic persistence retry failed because the reporting code sorted the full grid using training-only column names. | Replaced that reference with the training-selection table and reran; final Phase 21 workflow completed successfully. |

| 2026-10-03 | Phase 22 design | Prior Phase-21 fixed-point interventions could not identify a robust rule. | Registered an entry-only filter phase with temporal validation and an explicit 95% training winner-retention cap. |

| 2026-10-03 | Phase 22 execution | First feature build incorrectly required exact OTM6–17 prices on both call and put sides, causing 10 of 190 valid trades to be discarded before analysis. | Corrected completeness logic to require OTM6–8 on both sides and OTM6–17 only on the selected side, exactly matching the frozen dynamic-n specification. No filter result from the failed run is used. |

| 2026-10-03 | Phase 23 design | Phase 22 broad filters could not isolate losses while preserving winners, but all observed losses were in the BULLISH subgroup. | Registered a narrow BULLISH-only filter phase so BEARISH trades are never affected. |
