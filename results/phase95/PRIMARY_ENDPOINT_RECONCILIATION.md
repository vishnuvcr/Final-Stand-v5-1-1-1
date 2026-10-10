# Phase 95 — Reconciled primary endpoint

Run reconciliation: 2026-10-10T17:49:22.146842+00:00

## Primary endpoint: next-session closing price

- Successful closing-price model/window comparisons: 75.
- Positive MAE-improvement point estimates: 3/75.
- Bootstrap 95% intervals entirely above zero: 0/75.
- Positive gain with interval above zero and Holm-adjusted p below 0.05: 0/75.
- Directional accuracy range: 43.37%–53.01%.
- In this common-data screen, no closing-price variant establishes a statistically reliable MAE improvement over last-close persistence. This does not refute the original papers: most source-specific data, targets, metrics, splits and external inputs have not been matched.

| Closing model | Train years | MAE | Persistence MAE | Improvement | Bootstrap 95% CI | Holm p | Direction accuracy |
|---|---:|---:|---:|---:|---|---:|---:|
| linear_regression | 10 | 132.5985 | 132.9619 | 0.3633 | [-1.7260, 2.6993] | 1 | 49.80% |
| slp | 10 | 132.6463 | 132.9619 | 0.3156 | [-3.0012, 3.6058] | 1 | 47.79% |
| slp | 20 | 132.7751 | 132.9619 | 0.1868 | [-3.5008, 3.4316] | 1 | 48.19% |
| linear_regression | 20 | 133.2031 | 132.9619 | -0.2412 | [-1.7164, 1.0402] | 1 | 48.19% |
| slp | 5 | 133.2453 | 132.9619 | -0.2834 | [-4.0817, 3.4639] | 1 | 48.59% |
| lasso | 5 | 133.6703 | 132.9619 | -0.7084 | [-4.4218, 3.1604] | 1 | 49.40% |
| linear_regression | 5 | 134.0141 | 132.9619 | -1.0522 | [-4.4353, 2.3937] | 1 | 51.00% |
| lasso | 10 | 134.9239 | 132.9619 | -1.9620 | [-6.1351, 2.0989] | 1 | 48.19% |
| elastic_net | 5 | 136.9927 | 132.9619 | -4.0309 | [-9.0284, 0.6692] | 1 | 46.59% |
| cnn | 20 | 137.3554 | 132.9619 | -4.3935 | [-13.1552, 3.8126] | 1 | 53.01% |
| lasso | 20 | 138.1816 | 132.9619 | -5.2197 | [-10.6887, 0.1539] | 0.8389 | 46.59% |
| elastic_net | 10 | 138.5731 | 132.9619 | -5.6113 | [-10.9002, -0.3336] | 0.6556 | 43.37% |

## Supplemental opening-price results

- Successful opening-price comparisons: 45.
- Opening-price results are a separate endpoint; the overall top-ten table across targets must not be used as the primary close result.

## Paper claim status

- See paper_claim_status.csv. The common-data screen is not exact source reproduction.
- U02 options claims and U06 multimodal claims remain data-gated; source payoff methods are queued for Phase 99.

## Limitations

- The 2025 test is not necessarily post-publication for the newest papers.
- Source datasets, metric definitions, forecast horizons, splits and external features must be matched before a claim can be called reproduced.
- High price-level R-squared is not proof of incremental forecasting skill or tradable alpha.
- Phase 95 is a forecast comparison, not an options backtest. No strategy is promoted; Phase 83's 2026 holdout remains sealed.
