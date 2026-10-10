# Cross-year synthesis: incremental ATM IV prediction

Date: 2026-10-10. This note compares the fixed Phase 90 (2024) sample with the independent Phase 91 (2023) replication. It is descriptive; no pooled model or pooled effect was fitted.

## Primary results

| Sample | OOS rows / sessions | M1 MAE (bps) | M2 MAE (bps) | M1−M2 MAE (bps) | Paired session-bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|
| 2024, Phase 90 | 3,604 / 60 | 5.995294 | 5.962255 | +0.0330385 | +0.0001393 to +0.0561543 |
| 2023, Phase 91 | 3,633 / 60 | 3.9156 | 3.9155 | +0.0001111 | −0.0110700 to +0.0102532 |

M1 is the frozen lagged-spot plus India VIX model; M2 adds mean rolling ATM-relative CALL/PUT IV. Both phases fitted on January–June, used July–September for reporting only, and evaluated October–December OOS. Each used one registered endpoint, MAE(M1)−MAE(M2), and 5,000 session-cluster bootstrap resamples with seed 90210.

## Conclusion

The 2024 result was small and its lower confidence bound was close to zero. The independent 2023 replication had virtually no MAE change and a confidence interval spanning both benefit and harm. Across these fixed samples, reliable temporal replication of incremental IV-magnitude prediction beyond spot movement and India VIX **was not established**.

This does not prove IV has no predictive information. The registered evidence does not justify using this ATM-IV feature as a validated edge for selecting options strategies. VIX-regime results remain descriptive and were not separately tested for selection.

## Limits and next research decision

The target is absolute next-15-minute spot-return magnitude, not direction, option premium P&L or executable fills. Rolling ATM-relative data do not establish exact listed-contract identity, historic bid/ask/depth, slippage, or latency. No strategy P&L was run and Paytm Money charges were not estimated because no executed option fills were tested.

**Stop this incremental-IV prediction line at the planned replication.** Do not keep searching additional years or tuning features for a positive result. Reopen only with a materially new, preregistered hypothesis or authorized higher-quality data enabling exact-contract execution research. Such a future strategy replay must include Paytm Money brokerage, statutory charges, spread, adverse slippage, latency, and cost stress. The protected Phase 83 holdout remains sealed.

## Audit links

- [Phase 90 results](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-90-iv-incremental-prediction/results/phase90/PHASE90_RESULTS.md)
- [Phase 90 Actions run](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38048556674)
- [Phase 91 results](PHASE91_RESULTS.md)
- [Phase 91 Actions run](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38049302830)
- [Research plan](../../PHASE91_RESEARCH_PLAN.md)
- [Status](../../PHASE91_STATUS.md)
