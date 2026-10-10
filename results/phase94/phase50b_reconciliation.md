# Phase 94 — Canonical Phase 50B Reconciliation

Sources were read from the `phase-50b-final-manuscript` branch. The summary rows below are directly transcribed from canonical result JSON/CSV. They are not a claim that the entire historical strategy universe has been audited.

| Strategy | Trades / candidates | Coverage | Base net | +50% cost stress | ₹20/order | ₹20/order +50% stress | Chronological HOLD | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| TT-02 | 247 / 252 | 98.02% | -₹3,387.42 | -₹32,226.76 | -₹47,212.62 | -₹97,964.56 | Not in checked summary | No-go: negative across all listed cost cases |
| TT-03 | 200 / 201 | 99.50% | +₹89,669.15 | +₹82,074.11 | +₹75,509.15 | +₹60,834.11 | +₹6,201.79 on 3 trades | Research-only; HOLD sample too small; statistical gate failed |
| TT-03 OTM350 | 200 / 201 | 99.50% | +₹69,552.06 | +₹62,094.34 | +₹55,392.06 | +₹40,854.34 | +₹5,105.64 on 3 trades | Research-only; HOLD sample too small; statistical gate failed |
| TT-04 | 1,214 / 1,232 | 98.54% | +₹55,582.71 | +₹11,429.95 | -₹1,718.09 | -₹74,521.25 | -₹6,456.29 on 96 trades | No-go under higher cost cases; negative HOLD |
| TT-05 | 1,184 / 1,225 | 96.65% | +₹52,337.89 | +₹9,429.09 | -₹3,546.91 | -₹74,398.11 | -₹40,244.68 on 78 trades | No-go under higher cost cases; negative HOLD |
| TT-06 | 692 / 983 complete candidates | 70.40% | Not eligible for promotion | — | — | — | — | Terminal coverage failure |
| TT-07 | 1 / 59 complete candidates | 1.69% | Not eligible for promotion | — | — | — | — | Terminal coverage failure |

## Statistical gate and caveats

The canonical Phase 50B-6 `strategy_robustness_summary.csv` reports that **none** of TT03, TT03_OTM350, TT04 or TT05 passed both the all-four-cost positive criterion and Holm-corrected inference criterion. `inference_summary.json` records 16 hypotheses and an empty `robust_positive_strategies` list. Therefore, positive base/stress point estimates do not justify promotion.

The cost columns are the source ledger's scenarios, not a claim that each historical trade had reconstructed live executable quotes. The chronology report contains only three HOLD trades for TT03 and TT03_OTM350, which is inadequate to establish robust temporal performance. TT04 and TT05 have materially negative HOLD results and lose profitability under ₹20/order stress. TT02 is negative even in its base scenario.

TT06 and TT07 terminal P&L is diagnostic only and explicitly excluded from promotion/inference due coverage failures.

## Source links

- [TT-02 summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-final-manuscript/results/phase50b/tt02_calendar_replay/summary.json)
- [TT-03 summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-final-manuscript/results/phase50b/tt03_dynamic_n_replay/summary.json)
- [TT-03 terminal decision](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-final-manuscript/results/phase50b/tt03_dynamic_n_replay/terminal_decision.json)
- [TT-03 OTM350 summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-final-manuscript/results/phase50b/tt03_far_otm/OTM350/summary.json)
- [TT-04 summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-final-manuscript/results/phase50b/tt04_premium_match_replay/summary.json)
- [TT-05 summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-final-manuscript/results/phase50b/tt05_short_straddle_replay/summary.json)
- [Chronological strategy summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-final-manuscript/results/phase50b/phase50b5_chronological_validation/chronological_strategy_summary.csv)
- [Statistical robustness summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-final-manuscript/results/phase50b/phase50b6_statistical_inference/strategy_robustness_summary.csv)
- [Inference summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-final-manuscript/results/phase50b/phase50b6_statistical_inference/inference_summary.json)

## Interpretation

TT-03 is the most promising of these checked candidates by reported net point estimates, but it is **not a promoted strategy**: the protected chronological HOLD is only three trades and the registered Phase 50B statistical robustness gate was not passed. This ranking is descriptive, not proof of an edge. Phase 83's protected 2026 holdout remains sealed.
