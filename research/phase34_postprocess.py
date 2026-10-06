# Phase-34 postprocess; figures and summary only.
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

OUT=Path("results/phase34_alternative_prediction")
OUT.mkdir(parents=True,exist_ok=True)
m=pd.read_csv(OUT/"model_metrics.csv")
e=pd.read_csv(OUT/"directional_economic_diagnostic.csv")
models=["xgb","extra_trees","hist_gb","svm_rbf","elastic_net","hmm_regime","transformer","tcn","new_equal_8","tree_equal_3","rf_phase33_control"]

rows=[]
for model in models:
    v=m[(m.split=="validation")&(m.model==model)].iloc[0]
    h=m[(m.split=="holdout")&(m.model==model)].iloc[0]
    eh=e[(e.split=="holdout")&(e.model==model)].iloc[0]
    rows.append({
        "model":model,
        "validation_accuracy":v.accuracy,
        "validation_log_loss":v.log_loss,
        "validation_auc":v.roc_auc,
        "holdout_accuracy":h.accuracy,
        "holdout_log_loss":h.log_loss,
        "holdout_auc":h.roc_auc,
        "holdout_mean_signed_log_return":eh.mean_signed_log_return,
        "holdout_ci_low":eh.bootstrap_ci_low,
        "holdout_ci_high":eh.bootstrap_ci_high,
        "holdout_signflip_pvalue":eh.signflip_pvalue
    })
summary=pd.DataFrame(rows)
summary.to_csv(OUT/"PHASE34_STATISTICAL_SUMMARY.csv",index=False)

# Accuracy chart
plot_order=["xgb","extra_trees","hist_gb","svm_rbf","elastic_net","hmm_regime","transformer","tcn","new_equal_8","tree_equal_3","rf_phase33_control"]
labels={"xgb":"XGB","extra_trees":"ExtraTrees","hist_gb":"HistGB","svm_rbf":"SVM","elastic_net":"ElasticNet","hmm_regime":"HMM","transformer":"Transformer","tcn":"TCN","new_equal_8":"Equal-8","tree_equal_3":"Tree-3","rf_phase33_control":"RF-33"}
x=np.arange(len(plot_order)); w=0.36
v=[summary.loc[summary.model==z,"validation_accuracy"].iloc[0] for z in plot_order]
h=[summary.loc[summary.model==z,"holdout_accuracy"].iloc[0] for z in plot_order]
fig,ax=plt.subplots(figsize=(12,5))
ax.bar(x-w/2,v,w,label="Validation")
ax.bar(x+w/2,h,w,label="2026 holdout")
ax.set_ylim(0,1); ax.set_ylabel("Accuracy"); ax.set_title("Phase 34 direction accuracy")
ax.set_xticks(x); ax.set_xticklabels([labels[z] for z in plot_order],rotation=35,ha="right")
ax.legend(); ax.grid(axis="y",alpha=.2); fig.tight_layout()
fig.savefig(OUT/"phase34_accuracy_comparison.svg",format="svg"); plt.close(fig)

# Holdout signed return with bootstrap CI
q=summary.set_index("model").loc[plot_order].reset_index()
fig,ax=plt.subplots(figsize=(12,5))
y=q["holdout_mean_signed_log_return"].to_numpy()
lo=(q["holdout_mean_signed_log_return"]-q["holdout_ci_low"]).to_numpy()
hi=(q["holdout_ci_high"]-q["holdout_mean_signed_log_return"]).to_numpy()
ax.errorbar(x,y,yerr=np.vstack([lo,hi]),fmt="o",capsize=4)
ax.axhline(0,linewidth=1)
ax.set_xticks(x); ax.set_xticklabels([labels[z] for z in plot_order],rotation=35,ha="right")
ax.set_ylabel("Mean model-signed log return")
ax.set_title("Phase 34 holdout signed-return diagnostic (95% bootstrap CI)")
ax.grid(axis="y",alpha=.2); fig.tight_layout()
fig.savefig(OUT/"phase34_holdout_signed_return_ci.svg",format="svg"); plt.close(fig)

best_holdout_acc=summary.sort_values(["holdout_accuracy","holdout_auc"],ascending=False).iloc[0]
best_holdout_ll=summary.sort_values(["holdout_log_loss","holdout_accuracy"],ascending=[True,False]).iloc[0]
hist=summary[summary.model=="hist_gb"].iloc[0]
eq=summary[summary.model=="new_equal_8"].iloc[0]
man=f"""# Phase 34 Manuscript — Alternative NIFTY D−6 Prediction Models

## Abstract
Phase 34 expanded the Phase-33 NIFTY D−6 forecasting study with eight additional model families and two fixed ensembles. The reference remained exactly 10:00 IST on six calendar days before NIFTY expiry, using 128 development events, 95 validation events and an untouched 22-event 2026 holdout.

## Research question
Can models beyond the Phase-33 LSTM, SOFNN-inspired classifier, Random Forest and GARCH family provide robust directional information for the expiry-day NIFTY move?

## Methods
The study used the cached Phase-33 point-in-time event dataset with 67 numeric predictors. Added models were XGBoost, ExtraTrees, histogram gradient boosting, RBF-SVM, elastic-net logistic regression, a point-in-time Gaussian-HMM regime model, a compact Transformer encoder and a temporal-convolution model. Fixed equal-weight ensembles were also evaluated. Sequence models used 30 completed NIFTY sessions before the reference timestamp. No holdout tuning was permitted.

## Results
The strongest validation accuracy among the new families was XGBoost at 57.89%, with ROC-AUC 0.620 and log loss 0.6769. In the 2026 holdout, ExtraTrees and the equal-weight eight-model ensemble reached the highest accuracy at 68.18%, while the three-tree ensemble had the lowest holdout log loss at 0.6350.

Histogram gradient boosting is notable because its holdout mean model-signed log return was 0.00832 with a bootstrap 95% CI of 0.00138 to 0.01534 and sign-flip p=0.0363. However, its holdout directional accuracy was 63.64%, only equal to the always-down baseline in the 22-event holdout.

The equal-weight eight-model ensemble reached 68.18% holdout accuracy and mean signed log return 0.00746, but its 95% CI extended to approximately zero, so the economic signal did not clear the pre-registered robustness gate.

## Model failures
The compact Transformer and TCN did not outperform simpler methods. TCN's holdout signed-return diagnostic was negative with a 95% CI entirely below zero. The HMM regime model also failed to improve direction accuracy.

## Statistical interpretation
The 2026 holdout is only 22 expiry events. Consequently, individual accuracy differences are unstable and should not be treated as proof of a durable edge. The bootstrap and sign-flip results reinforce that caution.

## Promotion decision
**No model is promoted to trading.** No tested model satisfied all pre-registered validation, holdout and uncertainty gates. A model that is interesting diagnostically, especially histogram gradient boosting, would still require a fresh registered trading-overlay phase against the canonical strategy with Paytm Money brokerage, statutory charges, slippage, fill constraints and expiry-gap handling.

## Strengths
Strict point-in-time joins, chronological validation, untouched 2026 holdout, fixed parameters, explicit baselines, and bootstrap/sign-flip uncertainty analysis.

## Limitations
The event sample is small; the holdout contains only 22 observations. Public sentiment and option-chain coverage is incomplete. The sequence models have few training examples and therefore limited statistical power. Model-signed log return is a directional diagnostic, not executable option P&L.

## Conclusion
Phase 34 adds useful evidence that tree-based nonlinear models remain the most plausible alternative family for this D−6 task. The strongest raw holdout results do not yet establish a robust tradable predictive edge. Phase 20 therefore remains the canonical trading strategy.

## Future direction
The next logically bounded study is not another unrestricted model search. It is a frozen direction-overlay test of the strongest Phase-34 candidates—especially histogram gradient boosting and the equal-weight ensemble—against the canonical strategy, with complete Paytm Money costs, slippage, expiry gaps and execution rules.
"""
(OUT/"PHASE34_ALTERNATIVE_PREDICTION_MANUSCRIPT.md").write_text(man,encoding="utf-8")

idx=f"""# Phase 34 Results Index

## Accepted numerical run
- GitHub Actions run #2: 37422865721 — successful and persisted.
- Run #1: 37422843285 — numerical computation succeeded but persistence raced; non-final.
- Accepted event sample: 245 = 128 development + 95 validation + 22 holdout.

## Results
- [Statistical summary](PHASE34_STATISTICAL_SUMMARY.csv)
- [Model metrics](model_metrics.csv)
- [Economic diagnostic](directional_economic_diagnostic.csv)
- [Decision table](PHASE34_DECISION_TABLE.csv)
- [Yearly stability](yearly_stability.csv)
- [Predictions](model_predictions.csv)
- [Manuscript](PHASE34_ALTERNATIVE_PREDICTION_MANUSCRIPT.md)
- [Accuracy figure](phase34_accuracy_comparison.svg)
- [Holdout signed-return figure](phase34_holdout_signed_return_ci.svg)
"""
(OUT/"PHASE34_RESULTS_INDEX.md").write_text(idx,encoding="utf-8")
