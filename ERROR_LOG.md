# Error Log

| Date | Phase | Error / limitation | Action |
|---|---|---|---|
| 2026-10-02 | Phase 1 restart | Prior implementation used a global maximum over all 20 call/put candidates. | Superseded prior results and restarted with the two-stage selector. |
| 2026-10-02 | Phase 1 restart | Prior DTE convention counted expiry as one of four sessions, making ordinary Thursday entry Monday rather than 4 DTE Friday. | Restarted with four trading sessions before expiry, expiry=0 DTE. |
| 2026-10-02 | Phase 1 restart | Higher-n preference was requested without a numeric weight. | Pre-registered 95%-of-maximum-X threshold, then highest eligible n; test 90%/97.5% later. |
| 2026-10-02 | Phase 1 restart | Non-positive X would make a 90%-of-X target non-meaningful. | Record NO_POSITIVE_X and do not enter. |
| 2026-10-02 | Phase 1 restart | Far-strike option coverage can be sparse. | Require complete selected legs; log and exclude missing observations without imputation. |
| 2026-10-02 | Phase 1 restart | Historical bid/ask is unavailable in the primary dataset. | Use explicit adverse slippage and label fills as modelled rather than observed bid/ask. |
| 2026-10-02 | Phase 1 restart | Target basis needed explicit distinction from executable credit. | Lock target to raw user-specified X*lot and report executable credit/costs separately. |
