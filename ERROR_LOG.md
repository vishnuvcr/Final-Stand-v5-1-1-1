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
