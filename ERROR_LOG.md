# Error Log

| Date | Phase | Error / limitation | Action |
|---|---|---|---|
| 2026-10-02 | Phase 1 restart | Prior implementation used a global maximum over all 20 call/put candidates. | Superseded prior results and restarted with the two-stage selector. |
| 2026-10-02 | Phase 1 restart | Prior DTE convention counted expiry as one of four sessions. | Restarted with four trading sessions before expiry, expiry=0 DTE. |
| 2026-10-02 | Phase 1 restart | Higher-n preference lacked a numeric weight. | Pre-registered 95%-of-maximum-X threshold, then highest eligible n; test 90%/97.5% later. |
| 2026-10-02 | Phase 1 restart | Non-positive X would make the target non-meaningful. | Record NO_POSITIVE_X and do not enter. |
| 2026-10-02 | Phase 1 restart | Far-strike option coverage can be sparse. | Require complete selected legs and log exclusions without imputation. |
| 2026-10-02 | Phase 1 restart | Historical bid/ask is unavailable. | Use explicit adverse slippage; label fills as modelled. |
| 2026-10-02 | Phase 2 | First execution run used an incomplete-candidate acceptance condition. | Corrected implementation to require all n=6..15 candidates before selecting n, then reran. |
| 2026-10-02 | Phase 2 | Workflow was temporarily push-gated solely to allow autonomous execution because direct dispatch was unavailable through the connector. | Restored workflow to manual-only immediately after successful run. |
| 2026-10-02 | Phase 2 | Results were generated on the Phase 1 branch before phase separation was finalized. | Created dedicated phase-2-restart-v2 branch and retained the successful run/results as audit history. |
