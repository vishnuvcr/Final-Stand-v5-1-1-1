# Phase 51-4 — Reproducibility and lineage audit

**Audit date:** 2026-10-09  
**Disposition:** PASS for artifact existence/lineage; PARTIAL for research scope; NO PROMOTION.

## Checks performed
1. Re-read the Phase 51-4 plan, status, error log and chat/action log from the active branch before continuing.
2. Queried GitHub Actions job records for authoritative run [37882057283](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37882057283). Both `check-marker` and `run-phase` jobs completed with conclusion `success`. The `run-phase` job included source/cache validation, the phase branch sweep, audit, artifact upload and publication steps.
3. Queried the run's artifacts. Found `phase51-3-available-oos-37882057283`, 14,975 bytes, not expired at audit time; GitHub-reported digest `sha256:225645fa85a4d8a3f8ce6ae65c535b820505cef8df86747b05c36116eed1d03b`.
4. Confirmed the run is the source of the previously published available-window results. This audit did not download/recompute the trade ledger and is not a new backtest execution.

## Results remain unchanged (descriptive partial window)
| Candidate | Trades | Net ₹10/order | Net +50% friction | Net ₹20/order | Net ₹20/order +50% |
|---|---:|---:|---:|---:|---:|
| TT-02 | 13 | -₹1,341.12 | -₹2,936.31 | -₹3,701.12 | -₹6,476.31 |
| TT-04 | 62 | +₹13,271.51 | +₹10,287.26 | +₹10,345.11 | +₹5,897.66 |
| TT-05 | 62 | +₹17,098.15 | +₹14,239.72 | +₹14,171.75 | +₹9,850.12 |

TT-05 is the descriptive leader by net rupees in each of the four displayed cost/friction scenarios. This is not evidence that TT-05 is statistically superior: the comparison uses the same short interval and a small number of campaigns, and no confirmatory test or multiplicity adjustment was performed.

## Audit limitations
- Artifact metadata was checked, but the ZIP payload was not re-downloaded and re-hashed here.
- No new workflow run or backtest is claimed.
- Results are based on 2026-04-21 through 2026-07-21 only; the preregistered full interval through 2026-08-04 is still blocked by missing expiry blocks on 2026-07-28 and 2026-08-04.
- No strategy is promoted and no parameter tuning is authorized under the current partial-window scope.

## Finite stopping decision
The Phase 51-4 partial-window continuation is **CLOSED — descriptive summary and lineage check complete**. The broader Phase 51 full-window validation remains **BLOCKED** pending accepted data for both missing expiry blocks and subsequent pre-specified validation. The next action is not more tuning on the same partial sample; it is to resume full-window validation only if acceptable data becomes available.
