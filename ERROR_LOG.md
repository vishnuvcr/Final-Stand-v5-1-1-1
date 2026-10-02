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
