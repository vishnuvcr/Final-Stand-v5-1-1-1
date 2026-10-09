# Phase 51-3 — Available-Data OOS Diagnostic Report

**Decision:** PASS_AVAILABLE_OOS for the frozen partial interval only. No strategy promotion.

## Abstract

A source-faithful replay of the frozen eligible Phase-50B strategies was executed on NIFTY 1-minute options and validated NIFTY spot observations from 2026-04-21 through 2026-07-21. The primary option object was hash- and byte-size-locked. The run passed source, candidate-set, coverage and row-level error checks. TT-04 and TT-05 were positive under the registered costs and friction stresses, while TT-02 was negative. This is descriptive evidence from a short partial interval, not confirmatory validation or a basis for deployment. The complete Phase-51 window through 2026-08-04 remains blocked by missing 2026-07-28 and 2026-08-04 option blocks.

## Research question and objectives

**Question:** Among frozen strategies with eligible opportunities in the complete available interval, which can produce auditable source-faithful partial-OOS evidence without changing trading rules?

Objectives were to preserve frozen rules, evaluate only the registered interval, enforce at least 95% execution coverage and zero data errors, report Paytm Money ₹10/order and ₹20/order costs with +50% friction stress, retain row-level artifacts, and prohibit promotion from this partial interval.

## Data lineage and quality

- Primary options source: `rissin/nse-options-intraday`, `upstox_intraday/NIFTY/NIFTY_2026.parquet`.
- SHA-256: `bae9943b2fa99ee9c1214fb7c695b84f9f661a050a5cd04d9c5c2ffc7bc59f73`.
- Size: 394,805,617 bytes.
- Spot source: validated Technovusin NIFTY 1-minute CSV repository, cached by the workflow.
- Spot rows: 23,625; first timestamp 2026-04-21 09:15 IST; last timestamp 2026-07-21 15:29 IST.
- Expiry dates observed directly in the primary option file: 14 weekly dates from 2026-04-21 through 2026-07-21.
- Authoritative workflow: [GitHub Actions run 37882057283](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37882057283).
- Artifact: [phase51-3-available-oos-37882057283](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37882057283).

No synthetic option prices, interpolation or forward filling was used. The wrapper changes source and date/output dependencies only; the frozen strategy rules, costs, slippage and execution semantics were not tuned.

## Frozen eligible set and exclusions

| Candidate | Treatment | Reason |
|---|---|---|
| TT-02 | Evaluated | Eligible, frozen engine |
| TT-03 | Excluded as non-informative | Exact frozen entry schedule yielded no eligible campaigns for the observed Tuesday expiry schedule; see Phase 51-2 |
| TT-04 | Evaluated | Eligible, frozen engine |
| TT-05 | Evaluated | Eligible, frozen engine |
| TT-06 | Not re-evaluated | Terminal feasibility/coverage failure in Phase 50B |
| TT-07 | Not re-evaluated | Terminal feasibility/coverage failure in Phase 50B |

The audited eligible set was exactly TT02, TT04 and TT05. All three produced results; the workflow reported no candidate errors.

## Results

All values are rupees. Net scenarios are as published by the frozen engines and include the registered execution/cost model.

| Strategy | Trades | Coverage | Data errors | Net ₹10/order | Net +50% friction | Net ₹20/order | Net ₹20/order +50% |
|---|---:|---:|---:|---:|---:|---:|---:|
| TT-02 | 13 | 100% | 0 | -1,341.12 | -2,936.31 | -3,701.12 | -6,476.31 |
| TT-04 | 62 | 100% | 0 | +13,271.51 | +10,287.26 | +10,345.11 | +5,897.66 |
| TT-05 | 62 | 100% | 0 | +17,098.15 | +14,239.72 | +14,171.75 | +9,850.12 |

### Descriptive trade statistics

These are calculated from the chronological trade CSVs. Drawdown is peak-to-trough on cumulative trade-level net P&L; it is not capital-normalized and is not a mark-to-market equity drawdown.

| Strategy | Mean net/trade | Median net/trade | Win rate | Max cumulative trade-P&L drawdown |
|---|---:|---:|---:|---:|
| TT-02 | -₹103.16 | -₹1,530.71 | 38.5% | ₹27,015.52 |
| TT-04 | +₹214.06 | +₹884.94 | 67.7% | ₹12,024.81 |
| TT-05 | +₹275.78 | +₹1,056.82 | 66.1% | ₹12,217.19 |

## Statistical analysis and inference

This phase was preregistered as descriptive/diagnostic, so no confirmatory p-values, multiple-comparison claims, parameter optimization, or promotion tests were run.

- TT-02 was negative under all four cost/friction scenarios; it is not supported by this partial-window result.
- TT-04 remained positive under all four scenarios, but its stressed net fell to ₹5,897.66.
- TT-05 remained positive under all four scenarios, but its stressed net fell to ₹9,850.12.
- Positive partial-window outcomes are not proof of persistent edge. Only 62 trades were observed for TT-04 and TT-05, and the time window is short and market-regime-specific.
- TT-04 had two LOW-VIX trades totaling a loss of about ₹4,900; this subgroup is too small to justify a regime rule.
- No strategy is promoted or authorized for live deployment from this report.

## Strengths

- Primary option source is fixed by SHA-256 and exact byte size.
- Spot source is cached and verified to span the entire partial interval.
- Expiry universe is derived from primary source observations rather than a stale external registry.
- Frozen strategy logic and cost/friction scenarios are preserved.
- Raw trades, summaries, coverage gaps and data-error files are retained in the repository.
- The run's software success was followed by source and candidate-set audits.

## Limitations

- The result covers only 2026-04-21 through 2026-07-21, not the full preregistered OOS window through 2026-08-04.
- Option blocks for 2026-07-28 and 2026-08-04 remain unavailable from the validated source.
- Public-source provenance and licensing should be reviewed before redistribution or production use.
- Results depend on observed LTP availability and the frozen cost/slippage model; real fills, market impact, broker-specific charges and operational latency can differ.
- Trade-level cumulative drawdown does not include full intratrade mark-to-market path or capital normalization.
- The partial sample is too small to support robust regime-conditioned inference or generalization.
- The report does not independently establish future profitability.

## Conclusion

Phase 51-3 is closed as **PASS_AVAILABLE_OOS for partial diagnostics**. TT-04 and TT-05 show positive net results across the registered scenarios in this interval; TT-02 is negative. No strategy is promoted. Full Phase-51 OOS claims remain blocked until the 2026-07-28 and 2026-08-04 option blocks are recovered from an accepted raw-data source and the complete frozen window is replayed.

## Future research

1. Recover the two missing weekly option blocks through an authorized broker/data-vendor route or another source that passes the same raw-byte, schema, coverage and lineage gates.
2. Replay the unchanged strategies over the full 2026-04-21 through 2026-08-04 interval.
3. Reconcile every candidate opportunity and report excluded/missing sessions explicitly.
4. Generate mark-to-market equity curves and capital-normalized drawdowns using the frozen execution assumptions.
5. Only after full-window validation, preregister a separate confirmatory analysis; do not tune on this partial diagnostic sample.

## Reproducibility files

- [Sweep summary JSON](sweep_summary.json)
- [TT-02 trades](tt02/tt02_trades.csv) and [summary](tt02/summary.json)
- [TT-04 trades](tt04/tt04_trades.csv) and [summary](tt04/summary.json)
- [TT-05 trades](tt05/tt05_trades.csv) and [summary](tt05/summary.json)
- [Phase status](../../../PHASE51_3_STATUS.md)
- [Error log](../../../PHASE51_3_ERROR_LOG.md)
- [Research plan](../../../PHASE51_3_RESEARCH_PLAN.md)
