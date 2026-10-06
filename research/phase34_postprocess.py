# Phase-34 postprocess: dependency-light summary tables and SVG figures.
from pathlib import Path
import csv, html

OUT=Path("results/phase34_alternative_prediction")
OUT.mkdir(parents=True,exist_ok=True)

def read_csv(name):
    with open(OUT/name,newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

metrics=read_csv("model_metrics.csv")
econ=read_csv("directional_economic_diagnostic.csv")
models=["xgb","extra_trees","hist_gb","svm_rbf","elastic_net","hmm_regime","transformer","tcn","new_equal_8","tree_equal_3","rf_phase33_control"]
labels={"xgb":"XGB","extra_trees":"ExtraTrees","hist_gb":"HistGB","svm_rbf":"SVM","elastic_net":"ElasticNet","hmm_regime":"HMM","transformer":"Transformer","tcn":"TCN","new_equal_8":"Equal-8","tree_equal_3":"Tree-3","rf_phase33_control":"RF-33"}

mmap={(r["split"],r["model"]):r for r in metrics}
emap={(r["split"],r["model"]):r for r in econ}
summary=[]
for model in models:
    v=mmap[("validation",model)]; h=mmap[("holdout",model)]; eh=emap[("holdout",model)]
    summary.append({
        "model":model,
        "validation_accuracy":v["accuracy"],
        "validation_log_loss":v["log_loss"],
        "validation_auc":v["roc_auc"],
        "holdout_accuracy":h["accuracy"],
        "holdout_log_loss":h["log_loss"],
        "holdout_auc":h["roc_auc"],
        "holdout_mean_signed_log_return":eh["mean_signed_log_return"],
        "holdout_ci_low":eh["bootstrap_ci_low"],
        "holdout_ci_high":eh["bootstrap_ci_high"],
        "holdout_signflip_pvalue":eh["signflip_pvalue"],
    })

with open(OUT/"PHASE34_STATISTICAL_SUMMARY.csv","w",newline="",encoding="utf-8") as f:
    fields=list(summary[0].keys()); w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(summary)

def esc(x):
    return html.escape(str(x))

def write_accuracy_svg():
    W,H=1200,520; ml,mr,mt,mb=70,25,45,115; pw=W-ml-mr; ph=H-mt-mb
    n=len(models); gap=pw/n; bar=gap*0.31
    def y(v): return mt+ph*(1-v)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">','<rect width="100%" height="100%" fill="white"/>',
           '<text x="600" y="28" text-anchor="middle" font-size="20" font-family="sans-serif">Phase 34 direction accuracy</text>',
           '<text x="18" y="285" transform="rotate(-90 18 285)" text-anchor="middle" font-size="14" font-family="sans-serif">Accuracy</text>']
    for t in [0,.25,.5,.75,1]:
        yy=y(t); parts.append(f'<line x1="{ml}" y1="{yy:.1f}" x2="{W-mr}" y2="{yy:.1f}" stroke="#dddddd"/>')
        parts.append(f'<text x="{ml-8}" y="{yy+5:.1f}" text-anchor="end" font-size="11" font-family="sans-serif">{t:.2f}</text>')
    for i,r in enumerate(summary):
        cx=ml+gap*(i+.5); v=float(r["validation_accuracy"]); h=float(r["holdout_accuracy"])
        parts += [f'<rect x="{cx-bar-3:.1f}" y="{y(v):.1f}" width="{bar:.1f}" height="{(y(0)-y(v)):.1f}" fill="#4c78a8"/>',
                  f'<rect x="{cx+3:.1f}" y="{y(h):.1f}" width="{bar:.1f}" height="{(y(0)-y(h)):.1f}" fill="#f58518"/>',
                  f'<text x="{cx:.1f}" y="{H-mb+18}" text-anchor="middle" font-size="10" font-family="sans-serif" transform="rotate(35 {cx:.1f} {H-mb+18})">{esc(labels[r["model"]])}</text>']
    parts += ['<rect x="930" y="42" width="14" height="14" fill="#4c78a8"/><text x="950" y="54" font-size="12" font-family="sans-serif">Validation</text>',
              '<rect x="1030" y="42" width="14" height="14" fill="#f58518"/><text x="1050" y="54" font-size="12" font-family="sans-serif">2026 holdout</text>','</svg>']
    (OUT/"phase34_accuracy_comparison.svg").write_text("".join(parts),encoding="utf-8")

def write_econ_svg():
    W,H=1200,520; ml,mr,mt,mb=80,25,45,115; pw=W-ml-mr; ph=H-mt-mb; gap=pw/len(models)
    vals=[float(r["holdout_mean_signed_log_return"]) for r in summary]
    lows=[float(r["holdout_ci_low"]) for r in summary]; highs=[float(r["holdout_ci_high"]) for r in summary]
    lo=min(lows+[0.0]); hi=max(highs+[0.0]); pad=max((hi-lo)*.12,0.001); lo-=pad; hi+=pad
    def y(v): return mt+ph*(hi-v)/(hi-lo)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">','<rect width="100%" height="100%" fill="white"/>',
           '<text x="600" y="28" text-anchor="middle" font-size="20" font-family="sans-serif">Phase 34 holdout signed-return diagnostic (95% bootstrap CI)</text>']
    zero=y(0); parts.append(f'<line x1="{ml}" y1="{zero:.1f}" x2="{W-mr}" y2="{zero:.1f}" stroke="#333333"/>')
    for i,r in enumerate(summary):
        cx=ml+gap*(i+.5); yy=y(float(r["holdout_mean_signed_log_return"]))
        yl=y(float(r["holdout_ci_low"])); yh=y(float(r["holdout_ci_high"]))
        parts += [f'<line x1="{cx:.1f}" y1="{yl:.1f}" x2="{cx:.1f}" y2="{yh:.1f}" stroke="#333333" stroke-width="2"/>',
                  f'<line x1="{cx-7:.1f}" y1="{yl:.1f}" x2="{cx+7:.1f}" y2="{yl:.1f}" stroke="#333333"/>',
                  f'<line x1="{cx-7:.1f}" y1="{yh:.1f}" x2="{cx+7:.1f}" y2="{yh:.1f}" stroke="#333333"/>',
                  f'<circle cx="{cx:.1f}" cy="{yy:.1f}" r="5" fill="#4c78a8"/>',
                  f'<text x="{cx:.1f}" y="{H-mb+18}" text-anchor="middle" font-size="10" font-family="sans-serif" transform="rotate(35 {cx:.1f} {H-mb+18})">{esc(labels[r["model"]])}</text>']
    parts.append(f'<text x="18" y="285" transform="rotate(-90 18 285)" text-anchor="middle" font-size="14" font-family="sans-serif">Mean signed log return</text>')
    parts.append('</svg>')
    (OUT/"phase34_holdout_signed_return_ci.svg").write_text("".join(parts),encoding="utf-8")

write_accuracy_svg(); write_econ_svg()

man="""# Phase 34 Manuscript — Alternative NIFTY D−6 Prediction Models

## Abstract
Phase 34 expanded the Phase-33 NIFTY D−6 forecasting study with eight additional model families and two fixed ensembles. The reference remained exactly 10:00 IST on six calendar days before NIFTY expiry, using 128 development events, 95 validation events and an untouched 22-event 2026 holdout.

## Methods
The cached Phase-33 point-in-time event dataset contained 67 numeric predictors. Added models were XGBoost, ExtraTrees, histogram gradient boosting, RBF-SVM, elastic-net logistic regression, a point-in-time Gaussian-HMM regime model, a compact Transformer encoder and a temporal-convolution model. Fixed equal-weight ensembles were also evaluated. Sequence models used 30 completed NIFTY sessions before the reference timestamp.

## Results
XGBoost was the strongest new family on validation accuracy at 57.89% (ROC-AUC 0.620; log loss 0.6769). In the 2026 holdout, ExtraTrees and the eight-model equal-weight ensemble had the highest accuracy at 68.18%. The three-tree ensemble had the best new-family holdout log loss at 0.6350.

Histogram gradient boosting produced the most notable economic diagnostic: mean model-signed holdout log return 0.00832, 95% bootstrap CI 0.00138 to 0.01534, sign-flip p=0.0363. However, its 63.64% holdout accuracy merely tied the always-down baseline. The equal-weight eight-model ensemble achieved 68.18% holdout accuracy with mean signed log return 0.00746, but its 95% CI extended essentially to zero.

The compact Transformer and TCN did not improve prediction. TCN had a negative holdout signed-return result with a CI entirely below zero.

## Statistical interpretation
The holdout contains only 22 events, so individual accuracy differences are unstable. Bootstrap and sign-flip diagnostics therefore provide important context. The model-signed return is a predictive diagnostic, not executable option P&L.

## Decision
**No Phase-34 model is promoted to trading.** The registered gates require simultaneous out-of-sample improvement and uncertainty robustness. No model met all gates. Phase 20 remains canonical.

## Future direction
A new bounded phase may test a frozen direction overlay using the strongest Phase-34 candidates—particularly histogram gradient boosting and the equal-weight ensemble—against the canonical strategy with full Paytm Money brokerage, statutory charges, slippage, execution and expiry-gap assumptions.
"""
(OUT/"PHASE34_ALTERNATIVE_PREDICTION_MANUSCRIPT.md").write_text(man,encoding="utf-8")

idx="""# Phase 34 Results Index

## Accepted numerical run
- GitHub Actions run #2: 37422865721 — successful and persisted.
- Run #1: 37422843285 — numerical computation succeeded but persistence raced; non-final.
- Accepted sample: 245 events = 128 development + 95 validation + 22 holdout.

## Results
- PHASE34_STATISTICAL_SUMMARY.csv
- model_metrics.csv
- directional_economic_diagnostic.csv
- PHASE34_DECISION_TABLE.csv
- yearly_stability.csv
- model_predictions.csv
- PHASE34_ALTERNATIVE_PREDICTION_MANUSCRIPT.md
- phase34_accuracy_comparison.svg
- phase34_holdout_signed_return_ci.svg
"""
(OUT/"PHASE34_RESULTS_INDEX.md").write_text(idx,encoding="utf-8")
