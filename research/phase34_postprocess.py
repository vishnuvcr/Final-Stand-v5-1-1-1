from pathlib import Path
import csv

OUT=Path("results/phase34_alternative_prediction")

def rows(path):
    with open(OUT/path,newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

m=rows("model_metrics.csv")
e=rows("directional_economic_diagnostic.csv")
models=["xgb","extra_trees","hist_gb","svm_rbf","elastic_net","hmm_regime","transformer","tcn","new_equal_8","tree_equal_3","rf_phase33_control"]
labels={"xgb":"XGB","extra_trees":"ExtraTrees","hist_gb":"HistGB","svm_rbf":"SVM","elastic_net":"ElasticNet","hmm_regime":"HMM","transformer":"Transformer","tcn":"TCN","new_equal_8":"Equal8","tree_equal_3":"Tree3","rf_phase33_control":"RF33"}
mm={(r["split"],r["model"]):r for r in m}; ee={(r["split"],r["model"]):r for r in e}
summary=[]
for name in models:
    v=mm[("validation",name)]; h=mm[("holdout",name)]; econ_name="rf_phase33" if name=="rf_phase33_control" else name; z=ee[("holdout",econ_name)]
    summary.append([name,v["accuracy"],v["log_loss"],h["accuracy"],h["log_loss"],h["roc_auc"],z["mean_signed_log_return"],z["bootstrap_ci_low"],z["bootstrap_ci_high"],z["signflip_pvalue"]])

fields=["model","validation_accuracy","validation_log_loss","holdout_accuracy","holdout_log_loss","holdout_auc","holdout_mean_signed_log_return","holdout_ci_low","holdout_ci_high","holdout_signflip_pvalue"]
with open(OUT/"PHASE34_STATISTICAL_SUMMARY.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(fields); w.writerows(summary)

W,H=1200,520
def rect(x,y,w,h,fill,extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'
def text(x,y,s,size=11,anchor="middle"):
    return f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}" text-anchor="{anchor}">{s}</text>'

# Accuracy SVG
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">',rect(0,0,W,H,"white"),text(600,28,"Phase 34 direction accuracy",20)]
left=70; top=55; plot_h=370; slot=(W-100)/len(summary); bw=slot*0.30
for t in [0,.25,.5,.75,1]:
    y=top+plot_h*(1-t); svg.append(f'<line x1="{left}" y1="{y}" x2="{W-30}" y2="{y}" stroke="#dddddd"/>'); svg.append(text(left-8,y+4,f"{t:.2f}",10,"end"))
for i,r in enumerate(summary):
    a=float(r[1]); h=float(r[3]); cx=left+slot*(i+.5)
    ya=top+plot_h*(1-a); yh=top+plot_h*(1-h)
    svg.append(rect(cx-bw-2,ya,bw,top+plot_h-ya,"#4c78a8"))
    svg.append(rect(cx+2,yh,bw,top+plot_h-yh,"#f58518"))
    svg.append(text(cx,H-70,labels[r[0]],10))
svg += [rect(940,45,14,14,"#4c78a8"),text(962,57,"Validation",11,"start"),rect(1035,45,14,14,"#f58518"),text(1057,57,"Holdout",11,"start"),"</svg>"]
(OUT/"phase34_accuracy_comparison.svg").write_text("".join(svg),encoding="utf-8")

# Signed-return CI SVG
W2,H2=1200,520; left=80; top=55; ph=370; slot=(W2-110)/len(summary)
vals=[float(r[6]) for r in summary]; lows=[float(r[7]) for r in summary]; highs=[float(r[8]) for r in summary]
lo=min(lows+[0.0]); hi=max(highs+[0.0]); span=max(hi-lo,0.001); lo-=span*0.1; hi+=span*0.1
def yy(v): return top+ph*(hi-v)/(hi-lo)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W2}" height="{H2}">',rect(0,0,W2,H2,"white"),text(600,28,"Phase 34 holdout signed-return diagnostic",20)]
svg.append(f'<line x1="{left}" y1="{yy(0)}" x2="{W2-30}" y2="{yy(0)}" stroke="#333333"/>')
for i,r in enumerate(summary):
    cx=left+slot*(i+.5); y=yy(float(r[6])); yl=yy(float(r[7])); yh=yy(float(r[8]))
    svg += [f'<line x1="{cx}" y1="{yl}" x2="{cx}" y2="{yh}" stroke="#333333" stroke-width="2"/>',f'<circle cx="{cx}" cy="{y}" r="5" fill="#4c78a8"/>',text(cx,H2-70,labels[r[0]],10)]
svg.append("</svg>")
(OUT/"phase34_holdout_signed_return_ci.svg").write_text("".join(svg),encoding="utf-8")

man="""# Phase 34 Manuscript — Alternative NIFTY D−6 Prediction Models

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
"""
(OUT/"PHASE34_ALTERNATIVE_PREDICTION_MANUSCRIPT.md").write_text(man,encoding="utf-8")
(OUT/"PHASE34_RESULTS_INDEX.md").write_text("# Phase 34 Results Index\n\nAccepted numerical run: GitHub Actions 37422865721.\n\nArtifacts: model_metrics.csv, directional_economic_diagnostic.csv, PHASE34_DECISION_TABLE.csv, PHASE34_STATISTICAL_SUMMARY.csv, yearly_stability.csv, model_predictions.csv, manuscript, and two SVG figures.\n",encoding="utf-8")
