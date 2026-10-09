# Phase 51-4 Status

**State: CLOSED — DESCRIPTIVE PARTIAL-WINDOW SUMMARY COMPLETE; NO STRATEGY PROMOTION.**

Authorized interval: 2026-04-21 through 2026-07-21. The two unresolved expiry blocks, 2026-07-28 and 2026-08-04, remain excluded from this partial analysis; the original full-window preregistration is unchanged.

Authoritative replay: [Actions run 37882057283](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37882057283). A metadata audit found both jobs successful and the unexpired 14,975-byte artifact `phase51-3-available-oos-37882057283` with GitHub-reported digest `sha256:225645fa85a4d8a3f8ce6ae65c535b820505cef8df86747b05c36116eed1d03b`. Artifact payload was not re-downloaded/re-hashed; no new backtest was run.

| Candidate | Trades | Net ₹10/order | Net +50% friction | Net ₹20/order | Net ₹20/order +50% |
|---|---:|---:|---:|---:|---:|
| TT-02 | 13 | -₹1,341.12 | -₹2,936.31 | -₹3,701.12 | -₹6,476.31 |
| TT-04 | 62 | +₹13,271.51 | +₹10,287.26 | +₹10,345.11 | +₹5,897.66 |
| TT-05 | 62 | +₹17,098.15 | +₹14,239.72 | +₹14,171.75 | +₹9,850.12 |

TT-05 leads descriptively in all four displayed cost/friction cases, but no confirmatory hypothesis test, multiple-comparison correction, parameter tuning or new holdout was run. TT-03 remains non-informative (zero eligible campaigns under its frozen entry rule); TT-06 and TT-07 remain excluded after earlier feasibility/coverage failures.

**Full-window Phase 51 remains BLOCKED** until acceptable, contract-complete data for 2026-07-28 and 2026-08-04 is available. No candidate is promoted and live deployment is not authorized.

- [Partial-window report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-4-partial-window-continuation/results/phase51/PHASE51_4_PARTIAL_WINDOW_REPORT.md)
- [Reproducibility audit](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-4-partial-window-continuation/results/phase51/PHASE51_4_REPRODUCIBILITY_AUDIT.md)
- [Closure addendum](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-4-partial-window-continuation/PHASE51_4_CLOSURE_ADDENDUM.md)
- [Plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-4-partial-window-continuation/PHASE51_4_PARTIAL_WINDOW_PLAN.md)
- [Error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-4-partial-window-continuation/PHASE51_4_ERROR_LOG.md)
- [Chat/action log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-4-partial-window-continuation/PHASE51_4_CHAT_LOG.md)
