# Phase 49 Manuscript — VIX Leader Parameter Tuning

## Abstract

Phase 49 screened 720 registered geometries, expanded to 1440 parameter×VIX-regime candidates across LOW and NORMAL India-VIX states. The study used 133 development expiries (2021–2023), 102 validation expiries (2024–2025), and 21 protected holdout expiries.

2 candidates survived development. The frozen set is defined by the persisted development_frozen_parameters.csv artifact and is summarized below. 1 candidate(s) met the validation economic gate.

The Bear Put LOW candidate met the validation economic gate with ₹28,848.48 net and ₹27,246.47 at +50% costs across 42 active LOW-VIX trades; its inference remained non-confirmatory (p=0.2260; Holm p=0.4520; 95% bootstrap CI crossed zero).

Protected holdout confirmations: bear_put / LOW: 5 trades, ₹27,278.50 net, ₹27,051.63 at +50% costs, win rate 80.0%.

The preregistered promotion gate therefore remains NO PROMOTION unless a Holm-adjusted confirmatory comparison survives.

## Research question

Can the strongest previously validated LOW/NORMAL-VIX NIFTY defined-risk structures be improved by tuning strike geometry, spread width, entry time and DTE without sacrificing out-of-sample robustness?

## Aims and objectives

1. Tune only the finite, pre-registered Phase-45 VIX leaders.
2. Select parameters using chronological development folds and neighborhood support.
3. Freeze before validation and compare active-VIX performance with the same parameter in complementary VIX states.
4. Include realistic brokerage, historical statutory charges, one-tick option slippage and +50% cost stress.
5. Keep the 2026 holdout inaccessible to selection and validation decisions.

## Scientific methodology

The audited Phase-43 option/inference primitives were reused. Point-in-time ATM and modal strike step determined the strike geometry; trades were evaluated at the registered entry times and exited at the last common timestamp on expiry day. Historical NIFTY lot sizes and date-aware charges were applied.

Development used 720 raw geometries × two registered VIX states = 1,440 candidates. A candidate needed at least 10 trades and positive mean net and stressed mean in both 2022 and 2023. Ranking used stressed mean/trade consistency, profit factor and one-step neighborhood support.

Validation used 10,000 bootstrap resamples and 10,000 one-sided permutations for active-vs-complement comparisons, with Holm correction across the six possible frozen family×state tests. The protected 2026 holdout was opened only after validation economic screening.

Execution realism included ₹10/order brokerage, historical STT/exchange/SEBI/IPFT/stamp/GST components, adverse ₹0.05 option-tick slippage per leg at entry and exit, and a +50% charge-stress P&L.

## Frozen parameters

- **bear_put / LOW:** Buy PE +1 step / Sell PE -3 step; width=4 steps; entry 09:30 IST; DTE=5.
- **put_bwb / LOW:** PE BWB body=1; upper=1 steps; lower=4 steps; entry 11:00 IST; DTE=3.

## Development findings

Five Bear Put LOW and seven Put BWB LOW parameterizations met the forward-fold development gate. No Bear Call or NORMAL-VIX candidate survived. The selected Bear Put had one neighboring eligible candidate within the 80%-of-score neighborhood rule; the selected Put BWB had zero neighborhood support.

The selected Put BWB is a useful anti-overfitting case: its development stressed mean/trade was about ₹646, yet its validation net was strongly negative. This deterioration supports retaining the protected holdout and inferential gates.

## Validation results

| Candidate | Trades | Net | +50% cost | Win rate | Active-complement mean | 95% CI | p | Holm p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| bear_put / LOW | 42 | ₹28,848.48 | ₹27,246.47 | 50.0% | ₹780.86 | [₹-1,369.81, ₹2,909.48] | 0.2260 | 0.4520 |
| put_bwb / LOW | 50 | ₹-43,963.84 | ₹-47,238.89 | 54.0% | ₹-254.48 | [₹-1,939.81, ₹1,404.59] | 0.6162 | 0.6162 |

Against the registered Bear Put LOW baseline, the tuned candidate's paired uplift on 41 common validation expiries was ₹21,521.89 net and ₹21,469.09 at +50% costs.

## Protected holdout

| Candidate | Trades | Net | +50% cost | Win rate |
|---|---:|---:|---:|---:|
| bear_put / LOW | 5 | ₹27,278.50 | ₹27,051.63 | 80.0% |

The strongest holdout confirmation is bear_put / LOW: 5 trades, ₹27,278.50 net, ₹27,051.63 at +50% costs, win rate 80.0%.

## Statistical inference

No Holm-adjusted comparison survived the pre-registered 0.05 threshold. The Bear Put's 95% bootstrap interval spans zero with permutation p=0.2260 and Holm-adjusted p=0.4520.

## Economic interpretation

The tuned Bear Put is economically promising: its frozen parameter is persisted in the candidate table, and its paired baseline uplift was ₹21,521.89 net / ₹21,469.09 at +50% costs across 41 common validation expiries.

The search involved 1440 candidate-regime combinations; development ranking therefore carries selection risk. Holdout evidence must be interpreted using the persisted trade count rather than a point estimate alone.

## Strengths

- Finite pre-registration with explicit cardinality and chronological separation.
- Historical lot sizes, statutory costs, brokerage, one-tick slippage and +50% cost stress.
- Active-vs-complement validation using the same frozen parameter.
- 2026 protected holdout and explicit workflow evidence embargo.

## Limitations

- Holm correction was applied to the six frozen family×state tests, not to all 1,440 development combinations; White/SPA-style search-wide correction remains a future robustness extension.
- The Bear Put holdout confirmation contains only five active LOW-VIX observations.
- Trade-level bootstrap/permutation does not explicitly model serial dependence or volatility clustering.
- Historical quote data do not provide full order-book queue/fill information; the project-standard one-tick adverse model is used.

## Conclusion

**NO PROMOTION**. Frozen candidates and their exact rules are in development_frozen_parameters.csv. The canonical strategy remains unchanged unless the persisted final_decision.json states otherwise.

## Future research

The next bounded test should prospectively evaluate this frozen Bear Put on a substantially larger independent post-2025 sample, with a minimum active-trade count set in advance. A later phase can add independent controls for trend, realized volatility, VIX term structure/skew, global market crossings, major news/event days and corporate-action windows without reopening the Phase-49 parameter surface.

## Reconciliation provenance

The numerical source was GitHub Actions run 37542636969; raw artifact 11450545178; digest sha256:84c171b3ea8312405cc231b8fc8c528259898fc0ec9c5a85eba13fe9d5f6b558. The numerical step completed successfully. The initial publication gate failed because the empty development error ledger was zero bytes. This reconciliation repairs only the ledger packaging and reruns the artifact/statistical/publication gate without changing numerical values.

## Appendix A — Annual breakdown

| split | family | state | year | trades | net | net50 | mean_net | win_rate |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| validation | bear_put | LOW | 2024 | 17 | 5479.65 | 4877.61 | 322.333 | 0.529412 |
| validation | bear_put | LOW | 2025 | 25 | 23368.8 | 22368.9 | 934.753 | 0.48 |
| holdout | bear_put | LOW | 2025 | 1 | -5008.77 | -5036.65 | -5008.77 | 0 |
| holdout | bear_put | LOW | 2026 | 4 | 32287.3 | 32088.3 | 8071.82 | 1 |
| validation | put_bwb | LOW | 2024 | 21 | -1775.28 | -2989.18 | -84.5374 | 0.619048 |
| validation | put_bwb | LOW | 2025 | 29 | -42188.6 | -44249.7 | -1454.78 | 0.482759 |
| holdout | put_bwb | LOW | 2026 | 7 | -16356.4 | -16856.5 | -2336.63 | 0.428571 |

## Appendix B — Candidate parameter table

| family | state | entry_time | dte | development_trades | fold_2022_mean_net | fold_2022_mean_net50 | fold_2023_mean_net | fold_2023_mean_net50 | development_med_net50 | neighbor_support | long_offset | short_offset | width | validation_trades | validation_net | validation_net50 | validation_mean_net | validation_win_rate | active_vs_complement_mean | ci_lo | ci_hi | p | p_holm | paired_common | paired_uplift_net | paired_uplift_net50 | validation_economic_pass | holm_survivor | holdout_trades | holdout_net | holdout_net50 | holdout_win_rate | body | upper | lower |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bear_put | LOW | 09:30 | 5 | 79 | 259.492 | 227.192 | 228.071 | 195.591 | 211.391 | 1 | 1 | -3 | 4 | 42 | 28848.5 | 27246.5 | 686.869 | 0.5 | 780.856 | -1369.81 | 2909.48 | 0.226 | 0.452 | 41 | 21521.9 | 21469.1 | True | False | 5 | 27278.5 | 27051.6 | 0.8 | NA | NA | NA |
| put_bwb | LOW | 11:00 | 3 | 85 | 1241.11 | 1192.15 | 152.597 | 99.2015 | 645.677 | 0 | NA | NA | NA | 50 | -43963.8 | -47238.9 | -879.277 | 0.54 | -254.484 | -1939.81 | 1404.59 | 0.6162 | 0.6162 | 43 | -47502.8 | -47519.8 | False | False | 7 | -16356.4 | -16856.5 | 0.428571 | 1 | 1 | 4 |

## Appendix C — Evidence files

See results/phase49_vix_tuning for the complete development matrix, validation matrices, holdout matrix, statistical summary, final decision JSON, reconciliation manifest and SVG figures.