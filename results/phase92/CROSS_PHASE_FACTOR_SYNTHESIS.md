# Cross-phase factor-prediction synthesis — Phases 89–92

Date: 2026-10-10  
Scope: summarize rolling-ATM NIFTY option-factor predictive studies from Phases 89–92. The studies have different hypotheses and target designs; numbers are not pooled, and association tests are not treated as model/strategy confirmation.

## Executive decision

**No options strategy is promoted. Close this rolling-ATM incremental-prediction line at Phase 92's preregistered stopping boundary.** IV was associated with absolute next-15-minute spot movement in one 2025 feature study and yielded a very small positive 2024 incremental OOS result, but the independent 2023 replication did not establish a gain. The combined synthetic-forward proxy/OI feature block degraded OOS prediction in the fixed 2022 study. None of these tests measures executable option fills or strategy P&L.

## Evidence by phase

| Phase / period | Question | Main evidence | Decision |
|---|---|---|---|
| 89 / 2025 | Are rolling ATM IV/OI features associated with the absolute next-15-minute spot move? | Mean ATM IV association survived Holm correction (Holm p=0.00706). IV skew, OI imbalance and stable-strike OI-change tests were not significant after the strike-roll audit. | A feature association, not evidence of incremental model utility or profitability; data window coverage caveat remained. |
| 90 / 2024 | Does ATM IV improve a frozen spot+India VIX predictor? | M1−M2 MAE improvement +0.0330385 bps; paired session-cluster 95% CI +0.0001393 to +0.0561543; OOS n=3,604 across 60 sessions. The effect was very small and the lower CI bound close to zero. | Weak positive result pending independent replication. |
| 91 / 2023 | Does the 2024 IV gain replicate on a distinct annual sample? | M1−M2 MAE +0.0001111 bps; 95% CI −0.0110700 to +0.0102532; OOS n=3,633 across 60 sessions. | No incremental IV gain established; 2024 finding did not replicate. |
| 92 / 2022 | Do a lagged rolling-ATM synthetic-forward proxy gap and CE/PE OI imbalance add value beyond spot+VIX+IV? | M2−M4 MAE −0.1708363 bps; 95% CI −0.2298769 to −0.1152015; OOS n=3,660 across 61 sessions. MAE worsened from 4.8214 to 4.9922 bps. | Negative incremental value for the combined feature block in this sample. No evidence for actual futures basis or arbitrage. |

## Phase 92 model comparison

[Figure 1 — OOS MAE comparison](OOS_MAE_COMPARISON.svg)

The registered feature block is a lagged rolling-ATM proxy only: (F_{syn}=K+C-P), with its spot-normalized gap, plus previous-bar ((OI_{CE}-OI_{PE})/(OI_{CE}+OI_{PE})). Dhan candle-close-derived features and VIX are lagged by a full five-minute row.

| OOS model | MAE (bps) | RMSE (bps) | R² |
|---|---:|---:|---:|
| Spot + India VIX | 4.7987 | 6.6109 | 0.0693 |
| Spot + VIX + IV (M2) | 4.8214 | 6.6003 | 0.0723 |
| M2 + synthetic-forward proxy (M3) | 4.8791 | 6.6208 | 0.0665 |
| M3 + OI imbalance (M4) | 4.9922 | 6.6615 | 0.0550 |

The proxy alone worsened MAE by approximately 0.0577 bps relative to M2. The combined proxy/OI model worsened it by 0.1708 bps. The registered primary CI was entirely below zero; this indicates degraded prediction of this target in the fixed 2022 period. It does not establish that OI or a correctly identified traded-futures basis can never be useful.

## Scientific limitations

1. The target is absolute next-15-minute NIFTY **spot** return magnitude, not direction, option premiums, futures basis, or strategy returns.
2. Rolling ATM-relative fields do not guarantee unchanged listed contracts and do not provide exact historical bid/ask/depth or executable fills.
3. (K+C-P) from rolling ATM candle closes is a proxy, not a traded FUTIDX close, risk-neutral forward estimate with known maturity/carry assumptions, or executable arbitrage residual.
4. Phase 92 does not include direct exact-contract futures/OI mapping, Greeks, historic bid/ask/depth, or Paytm Money fill simulation. The cost model is therefore not estimable because no rule-level P&L was run.
5. VIX subgroups in these studies are descriptive unless their own inference and multiplicity plan says otherwise. They must not be used to choose live strategies.
6. All runs use fixed out-of-sample splits, no tuning on OOS and no 2026 holdout access. Raw market payloads were not published.

## Recommendation and stop rule

Do not continue searching calendar years or changing features to salvage a positive result. The specific rolling-IV/synthetic-proxy/OI magnitude-prediction line is closed at the preregistered Phase 92 boundary.

Reopen only for either:
- a materially new, preregistered research question with a defensible mechanism, or
- authorized data that materially improves on the current rolling-ATM endpoint for exact listed-contract reconstruction and execution-quality validation.

A future trading-strategy replay must use exact contract identity and valid timestamps, retain out-of-sample discipline, and report Paytm Money brokerage, statutory charges, spread, adverse slippage, latency and cost-stress cases. Phase 60/61 source-gates remain closed; do not repeat rejected metadata-only searches. Phase 83's 2026 holdout remains sealed.

## Research manuscript and supplement

- [Full structured manuscript draft](MANUSCRIPT_DRAFT.md)
- [Supplementary methods and tables](SUPPLEMENTARY_MATERIALS.md)
- [IV incremental effects figure](IV_INCREMENTAL_EFFECTS.svg)
- [Phase 92 OOS MAE comparison figure](OOS_MAE_COMPARISON.svg)

## Audit links

- [Phase 89 results](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-89-rolling-options-feature-study/results/phase89/PHASE89_RESULTS.md)
- [Phase 90 results](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-90-iv-incremental-prediction/results/phase90/PHASE90_RESULTS.md)
- [Phase 91 results](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-91-iv-temporal-replication-2023/results/phase91/PHASE91_RESULTS.md)
- [Phase 91 cross-year synthesis](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-91-iv-temporal-replication-2023/results/phase91/CROSS_YEAR_SYNTHESIS.md)
- [Phase 92 results](PHASE92_RESULTS.md)
- [Phase 92 workflow run 38050805106](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050805106)
- [Phase 92 source/coverage error log](../../PHASE92_ERROR_LOG.md)
