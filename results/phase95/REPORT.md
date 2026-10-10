# Phase 95 — Daily Forecast Model Replication Report\n\nRun UTC: 2026-10-10T17:49:19.950714+00:00\nStatus: COMPLETED\n\n## Evidence boundary\nThis is a common-data NIFTY adaptation, not exact replication of every source's stock universe, period, external features or disclosed hyperparameters. Forecast accuracy is not options profitability. No strategy is promoted.\n\n## Data provenance\n- Source: Yahoo Finance ^NSEI\n- Dates: 2007-09-17 to 2025-12-31\n- Rows: 4487\n- SHA-256: 73894ea5dd0db39182da83cd6d279670d7ae7f26d1ea31d64b1a183ee187b5f2\n- Cache used: True\n- Blocker: none\n\n## Coverage\n- Successful model/target/window rows: 132\n- Explicit model failures: 0\n- Common test targets are restricted to 2025; no 2026 targets are scored.\n- Inference: circular moving-block bootstrap CI (5 sessions, 2,000 draws), HAC paired loss-difference p-values (lag 5), and Holm correction.\n\n## Top ten by MAE improvement over persistence (descriptive only)\n\n| Model | Target | Training years | OOS n | MAE | Persistence MAE | Improvement | Bootstrap CI | Holm p | Decision |\n|---|---|---:|---:|---:|---:|---:|---|---:|---|\n| linear_regression | Open | 10 | 249 | 68.4216 | 146.1693 | 77.7477 | [65.6479, 89.7064] | 9.57e-27 | MAE_GAIN_CI_ABOVE_ZERO |\n| linear_regression | Open | 5 | 249 | 69.2177 | 146.1693 | 76.9516 | [64.0108, 89.3488] | 2.712e-26 | MAE_GAIN_CI_ABOVE_ZERO |\n| linear_regression | Open | 20 | 249 | 69.2799 | 146.1693 | 76.8894 | [65.1219, 88.7549] | 2.954e-25 | MAE_GAIN_CI_ABOVE_ZERO |\n| lasso | Open | 5 | 249 | 69.9649 | 146.1693 | 76.2044 | [65.5182, 87.9831] | 1.936e-27 | MAE_GAIN_CI_ABOVE_ZERO |\n| slp | Open | 5 | 249 | 70.0985 | 146.1693 | 76.0709 | [64.5476, 88.0665] | 8.201e-26 | MAE_GAIN_CI_ABOVE_ZERO |\n| slp | Open | 10 | 249 | 70.5056 | 146.1693 | 75.6638 | [64.2281, 88.0389] | 2.632e-26 | MAE_GAIN_CI_ABOVE_ZERO |\n| slp | Open | 20 | 249 | 72.2892 | 146.1693 | 73.8801 | [61.9249, 85.4384] | 6.545e-26 | MAE_GAIN_CI_ABOVE_ZERO |\n| lasso | Open | 10 | 249 | 73.2401 | 146.1693 | 72.9292 | [62.2800, 83.9642] | 7.961e-28 | MAE_GAIN_CI_ABOVE_ZERO |\n| elastic_net | Open | 5 | 249 | 75.1656 | 146.1693 | 71.0037 | [60.5954, 81.8022] | 3.078e-27 | MAE_GAIN_CI_ABOVE_ZERO |\n| lasso | Open | 20 | 249 | 77.4761 | 146.1693 | 68.6933 | [58.4573, 79.2518] | 1.603e-27 | MAE_GAIN_CI_ABOVE_ZERO |\n\n## Limitations and paper-specific blockers\n- USD/INR, historical FII/DII, India VIX, PCR, options Greeks and point-in-time news were not supplied by the primary price feed. The multimodal papers remain partial/data-gated.\n- U12's source includes turnover; Yahoo index volume is not asserted to be equivalent.\n- The common 2025 test period is chronological relative to this runner's fit but may overlap the source data period of newer papers. It is not automatically post-publication validation.\n- Price-level R-squared can be inflated by persistence. Consider error improvement, return/directional skill and calibrated confidence, not accuracy alone.\n- Fixed settings are transparent operationalizations when source-specific settings are unavailable. Exact paper-metric reproduction must be separately audited.\n- Options P&L is not calculated in this phase; no promotion.\n\n## Artifacts\n- \`model_metrics.csv\`: metrics/failures/inference\n- \`coverage.csv\`: target/window sample gates\n- \`modality_status.csv\`: unavailable external inputs\n- \`data_manifest.json\`: source provenance/hash\n- \`run_summary.json\`: machine-readable decision\n

## Reconciled primary endpoint


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

See paper_claim_status.csv for the source-by-source coverage ledger; no paper is labelled exactly reproduced by this common-data screen.
