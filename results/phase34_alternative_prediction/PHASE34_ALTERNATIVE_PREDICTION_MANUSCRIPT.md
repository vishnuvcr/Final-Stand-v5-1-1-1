# Phase 34 Manuscript — Alternative NIFTY D−6 Prediction Models

## Sample and design
245 eligible events were evaluated: 128 development, 95 validation, and 22 untouched 2026 holdout. The reference remained exactly 10:00 IST on six calendar days before expiry.

## Models
XGBoost, ExtraTrees, HistGradientBoosting, RBF-SVM, Elastic-Net Logistic Regression, point-in-time HMM regime probability, a compact Transformer, a compact temporal-convolution model, an equal-weight eight-model ensemble, and a three-tree ensemble. Phase-33 Random Forest is the control.

## Results
Validation leader: XGBoost, 57.89% accuracy and 0.6769 log loss.
Holdout highest accuracy: ExtraTrees and the eight-model ensemble, both 68.18%.
Holdout best log loss: three-tree ensemble, 0.6350.
HistGradientBoosting produced the strongest holdout signed-return diagnostic: mean 0.00832, 95% bootstrap CI 0.00138 to 0.01534, sign-flip p=0.0363, but its 63.64% accuracy only tied the always-down baseline.
The eight-model ensemble reached 68.18% holdout accuracy, but its 95% signed-return interval extended to approximately zero.

## Decision
No Phase-34 model is promoted. The 2026 holdout is only 22 events and no model passed all preregistered validation, holdout, and uncertainty gates.

## Interpretation
Tree-based nonlinear models are the most credible alternative family in this test. Deep sequence models did not add evidence; TCN was materially negative on the holdout signed-return diagnostic.

## Next research
A fresh, frozen trading-overlay phase may test the strongest Phase-34 candidates against the canonical strategy, with Paytm Money brokerage, statutory charges, slippage, fills and expiry-gap handling fully modeled.
