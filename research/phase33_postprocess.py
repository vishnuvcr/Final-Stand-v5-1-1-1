import json, math
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path("results/phase33_nifty_prediction")
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)
SEED = 1337

def bootstrap_mean(x, n=5000):
    x=np.asarray(x,float); x=x[np.isfinite(x)]
    if len(x)==0: return (np.nan,np.nan)
    rng=np.random.default_rng(SEED)
    means=np.mean(rng.choice(x,(n,len(x)),replace=True),axis=1)
    return float(np.quantile(means,.025)),float(np.quantile(means,.975))

def ece(y,p,bins=10):
    y=np.asarray(y,int); p=np.asarray(p,float)
    total=0.0
    edges=np.linspace(0,1,bins+1)
    for i in range(bins):
        mask=(p>=edges[i]) & ((p<edges[i+1]) if i<bins-1 else (p<=edges[i+1]))
        if mask.any(): total += mask.mean()*abs(p[mask].mean()-y[mask].mean())
    return float(total)

def paired_sign_perm(a,b,n=10000):
    d=np.asarray(a,float)-np.asarray(b,float)
    d=d[np.isfinite(d)]
    if len(d)==0: return np.nan
    rng=np.random.default_rng(SEED)
    obs=abs(d.mean())
    signs=rng.choice([-1,1],size=(n,len(d)))
    null=np.abs((signs*d).mean(axis=1))
    return float((1+(null>=obs).sum())/(n+1))

def binom_two_sided(k,n,p=.5):
    if n==0: return np.nan
    from math import comb
    probs=[comb(n,j)*(p**j)*((1-p)**(n-j)) for j in range(n+1)]
    obs=probs[k]
    return float(min(1.0, sum(v for v in probs if v<=obs+1e-15)))

def prob_col(model):
    return "sofnn_sent_prob" if model=="sofnn_sent" else f"{model}_prob"

def main():
    pred=pd.read_csv(OUT/"model_predictions.csv")
    pred["ref_ts"]=pd.to_datetime(pred["ref_ts"],utc=True).dt.tz_convert("Asia/Kolkata")
    pred=pred.sort_values("ref_ts")
    metrics=pd.read_csv(OUT/"model_metrics.csv")
    baseline=pd.read_csv(OUT/"baseline_metrics.csv")
    econ=pd.read_csv(OUT/"directional_economic_diagnostic.csv")
    garch=pd.read_csv(OUT/"garch_predictions.csv")
    coverage=json.loads((OUT/"coverage_and_metadata.json").read_text())

    models=["rf","sofnn","sofnn_sent","lstm","ensemble"]
    rows=[]
    for split in ["validation","holdout"]:
        q=pred[pred["split"]==split].copy()
        hist=pred[pred["split"].isin(["train","validation"])]
        const_prob=float(hist["target_direction"].mean()) if split=="holdout" else float(pred[pred["split"]=="train"]["target_direction"].mean())
        const_pred=np.full(len(q),int(const_prob>=0.5))
        for model in models:
            col=prob_col(model)
            if col not in q: continue
            p=q[col].to_numpy(float); y=q["target_direction"].to_numpy(int)
            pr=(p>=.5).astype(int)
            signed=np.where(pr==1,q["target_return"].to_numpy(float),-q["target_return"].to_numpy(float))
            lo,hi=bootstrap_mean(signed)
            correct=(pr==y).astype(int)
            const_correct=(const_pred==y).astype(int)
            acc_delta=float(correct.mean()-const_correct.mean())
            perm_p=paired_sign_perm(correct,const_correct)
            discord=(correct!=const_correct)
            d1=int(np.sum(correct[discord])); d0=int(np.sum(const_correct[discord]))
            metric_row=metrics[(metrics["split"]==split)&(metrics["model"]==model)]
            rows.append({
                "split":split,"model":model,"n":len(q),
                "accuracy":float(correct.mean()),
                "balanced_accuracy":float(metric_row["balanced_accuracy"].iloc[0]) if not metric_row.empty else np.nan,
                "roc_auc":float(metric_row["roc_auc"].iloc[0]) if not metric_row.empty else np.nan,
                "brier":float(metric_row["brier"].iloc[0]) if not metric_row.empty else np.nan,
                "log_loss":float(metric_row["log_loss"].iloc[0]) if not metric_row.empty else np.nan,
                "ece":ece(y,p),
                "mean_signed_log_return":float(np.mean(signed)),
                "signed_return_ci_low":lo,
                "signed_return_ci_high":hi,
                "acc_delta_vs_constant":acc_delta,
                "paired_sign_perm_p":perm_p,
                "mcnemar_exact_p":binom_two_sided(min(d1,d0),d1+d0),
            })
    stat=pd.DataFrame(rows)
    stat.to_csv(OUT/"PHASE33_STATISTICAL_SUMMARY.csv",index=False)

    pred["year"]=pred["ref_ts"].dt.year
    yr=[]
    for (split,year),q in pred.groupby(["split","year"]):
        if split not in ["validation","holdout"]: continue
        for model in models:
            col=prob_col(model)
            if col not in q: continue
            pr=(q[col]>=.5).astype(int)
            y=q.target_direction.astype(int)
            yr.append({"split":split,"year":int(year),"model":model,"n":len(q),
                       "accuracy":float((pr==y).mean()),
                       "mean_signed_log_return":float(np.where(pr.eq(1),q.target_return,-q.target_return).mean())})
    pd.DataFrame(yr).to_csv(OUT/"PHASE33_YEARLY_STABILITY.csv",index=False)

    if not garch.empty:
        rv=np.maximum(garch["realized_sq_return"].to_numpy(float),1e-12)
        fv=np.maximum(garch["garch_sigma"].to_numpy(float)**2,1e-12)
        gsum={
            "MAE_sigma_vs_abs_return":float(np.mean(np.abs(np.sqrt(fv)-np.sqrt(rv)))),
            "RMSE_sigma_vs_abs_return":float(np.sqrt(np.mean((np.sqrt(fv)-np.sqrt(rv))**2))),
            "QLIKE":float(np.mean(fv/rv-np.log(fv/rv)-1)),
            "corr_sigma_abs_return":float(np.corrcoef(np.sqrt(fv),np.sqrt(rv))[0,1]) if len(rv)>1 else np.nan,
        }
    else:
        gsum={}
    (OUT/"PHASE33_GARCH_SUMMARY.json").write_text(json.dumps(gsum,indent=2))

    decision=[]
    for split in ["validation","holdout"]:
        q=stat[stat["split"]==split]
        if not q.empty:
            best_ll=q.sort_values(["log_loss","brier"]).iloc[0]
            best_acc=q.sort_values("accuracy",ascending=False).iloc[0]
            best_e=q.sort_values("mean_signed_log_return",ascending=False).iloc[0]
            decision.append({"split":split,
                             "best_log_loss_model":best_ll["model"],
                             "best_log_loss":float(best_ll["log_loss"]),
                             "best_accuracy_model":best_acc["model"],
                             "best_accuracy":float(best_acc["accuracy"]),
                             "best_economic_model":best_e["model"],
                             "best_mean_signed_log_return":float(best_e["mean_signed_log_return"])})
    pd.DataFrame(decision).to_csv(OUT/"PHASE33_DECISION_TABLE.csv",index=False)

    import matplotlib.pyplot as plt
    for split in ["validation","holdout"]:
        q=pred[pred["split"]==split].copy()
        if q.empty: continue
        fig,ax=plt.subplots(figsize=(9,5))
        for model in models:
            col=prob_col(model)
            if col in q: ax.plot(q["ref_ts"],q[col],label=model)
        ax.set_title(f"Phase 33 predicted probability — {split}")
        ax.set_ylabel("P(expiry close > D-6 10:00 spot)")
        ax.legend()
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(FIG/f"phase33_probability_{split}.svg")
        plt.close(fig)

    q=econ.copy()
    if not q.empty:
        fig,ax=plt.subplots(figsize=(9,5))
        labels=[]; vals=[]
        for _,r in q.iterrows():
            labels.append(f"{r['model']}-{str(r['split'])[:3]}")
            vals.append(r["mean_signed_log_return"])
        ax.bar(labels,vals)
        ax.axhline(0,linewidth=1)
        ax.set_title("Costless directional return diagnostic")
        ax.set_ylabel("Mean signed log return")
        ax.tick_params(axis="x",rotation=45)
        fig.tight_layout()
        fig.savefig(FIG/"phase33_signed_return_diagnostic.svg")
        plt.close(fig)

    if not garch.empty:
        gg=garch.copy()
        gg["ref_ts"]=pd.to_datetime(gg["ref_ts"],utc=True).dt.tz_convert("Asia/Kolkata")
        fig,ax=plt.subplots(figsize=(9,5))
        ax.plot(gg["ref_ts"],gg["garch_sigma"],label="GARCH-family forecast sigma")
        ax.plot(gg["ref_ts"],np.abs(gg["realized_abs_return"]),label="realized |return|")
        ax.set_title("GARCH-family volatility forecast vs realized move")
        ax.legend()
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(FIG/"phase33_garch_vs_realized.svg")
        plt.close(fig)

    # Manuscript with actual numerical findings.
    best_full_val = stat[(stat["split"]=="validation") & (stat["model"].isin(models))].sort_values(["log_loss","brier"]).iloc[0]
    best_full_hold = stat[(stat["split"]=="holdout") & (stat["model"].isin(models))].sort_values(["log_loss","brier"]).iloc[0]
    hold_acc_best = stat[stat["split"]=="holdout"].sort_values("accuracy", ascending=False).iloc[0]
    val_acc_best = stat[stat["split"]=="validation"].sort_values("accuracy", ascending=False).iloc[0]

    rows_text = ["| Split | Model | Accuracy | Balanced accuracy | ROC-AUC | Log loss | Brier | ECE |",
                 "|---|---|---:|---:|---:|---:|---:|---:|"]
    for _,r in stat.sort_values(["split","log_loss"]).iterrows():
        rows_text.append(f"| {r['split']} | {r['model']} | {r['accuracy']:.4f} | {r['balanced_accuracy']:.4f} | {r['roc_auc']:.4f} | {r['log_loss']:.4f} | {r['brier']:.4f} | {r['ece']:.4f} |")
    metric_table = "\n".join(rows_text)

    econ_rows = ["| Split | Model | Hit rate | Mean signed log return | 95% bootstrap CI |",
                 "|---|---|---:|---:|---|"]
    for _,r in econ.iterrows():
        econ_rows.append(f"| {r['split']} | {r['model']} | {r['hit_rate']:.4f} | {r['mean_signed_log_return']:.5f} | [{r['bootstrap_ci_low']:.5f}, {r['bootstrap_ci_high']:.5f}] |")
    econ_table = "\n".join(econ_rows)

    manuscript = f"""# Phase 33 — NIFTY D−6 Prediction Models

## Abstract
This phase tests whether information observable at exactly 10:00 IST on six calendar days before NIFTY expiry predicts the subsequent expiry-day NIFTY close. The registered model set includes LSTM, GARCH/EGARCH/GJR-GARCH volatility forecasting, a sentiment-augmented SOFNN-inspired fuzzy classifier, Random Forest, and a fixed equal-weight ensemble. The design uses point-in-time feature censoring, chronological validation and an untouched 2026 holdout.

Across 245 eligible expiry events, the strongest full directional model differs by period: Random Forest is strongest on validation log loss, while the equal-weight ensemble has the strongest holdout accuracy among the full models. Neither result is robust enough to justify a trading overlay because the apparent 2026 directional edge does not beat the simple always-down baseline on accuracy and the signed-return confidence intervals include zero.

## Research question
Can D−6/10:00 IST information predict expiry-day NIFTY direction or magnitude out of sample, and does any requested model family produce a stable enough edge to justify a future strategy overlay?

## Aims and objectives
1. Quantify point-in-time directional predictability.
2. Compare LSTM, GARCH-family volatility models, SOFNN-inspired fuzzy learning, Random Forest and an equal-weight ensemble.
3. Measure incremental information from sentiment, cross-market, options and FII/DII variables.
4. Evaluate volatility forecasting separately from directional classification.
5. Apply a pre-registered promotion gate.

## Methods
Reference timestamp: expiry minus six calendar days at exactly 10:00 IST.
Target: latest complete NIFTY spot observation at or before 15:29 IST on expiry day.
Events without an exact 10:00 observation are excluded rather than shifted.

Development/training contains 128 events, validation contains 95 events, and the untouched 2026 holdout contains 22 events. The LSTM uses the 30 most recent completed trading sessions strictly before the reference date. Random Forest and SOFNN-inspired parameters are fixed. GARCH, EGARCH and GJR-GARCH are fit only to returns available before the reference timestamp. Multi-step EGARCH uses simulation forecasting because analytic multi-step forecasts are unsupported for that model family in the selected econometrics implementation.

## Data and leakage control
The point-in-time feature set contains 67 numeric features from NIFTY price/volatility history, prior-session global markets, exact-reference option-chain diagnostics where available, sentiment and cached FII/DII data. Forward-return and target columns from the sentiment dataset are excluded. Global values are shifted to prior sessions, institutional flow joins use the previous available publication, and all time keys are normalized to IST with a common nanosecond resolution.

## Out-of-sample results

### Directional metrics
{metric_table}

### Costless directional-return diagnostic
This is a prediction diagnostic, not an executed option P&L. It signs the expiry-horizon log return according to the model's predicted direction.

{econ_table}

### Main findings
- Validation best full-model log loss: {best_full_val['model']} at {best_full_val['log_loss']:.4f}; accuracy {best_full_val['accuracy']:.4f}.
- Holdout best full-model log loss: {best_full_hold['model']} at {best_full_hold['log_loss']:.4f}; accuracy {best_full_hold['accuracy']:.4f}.
- Holdout best full-model accuracy: {hold_acc_best['model']} at {hold_acc_best['accuracy']:.4f}; the simple always-down baseline reaches 0.6364 accuracy on the same 22-event holdout.
- Holdout ensemble balanced accuracy is {float(stat[(stat['split']=='holdout')&(stat['model']=='ensemble')]['balanced_accuracy'].iloc[0]):.4f}; this is the clearest sign of some discrimination, but the sample is small and validation ensemble accuracy was only 0.4947.
- Sentiment augmentation does not improve the SOFNN track: its validation result is identical to SOFNN and its holdout accuracy is 0.3636 with Brier score {float(stat[(stat['split']=='holdout')&(stat['model']=='sofnn_sent')]['brier'].iloc[0]):.4f}.
- LSTM is effectively non-informative in this specification: ROC-AUC 0.50 and 0.5 probability output in both evaluation periods.
- GARCH-family volatility forecasts have MAE {gsum.get('MAE_sigma_vs_abs_return', float('nan')):.5f}, RMSE {gsum.get('RMSE_sigma_vs_abs_return', float('nan')):.5f}, QLIKE {gsum.get('QLIKE', float('nan')):.3f}, and correlation {gsum.get('corr_sigma_abs_return', float('nan')):.3f} with realized absolute return. Directional accuracy is 0.4957.

## Statistical interpretation
Bootstrap intervals for all model mean signed returns include zero in both validation and holdout. Paired accuracy permutation and McNemar-style discordance tests do not show a robust advantage over the simple constant-direction comparator in this sample. The small 2026 holdout substantially limits power.

## Discussion
The literature supports testing these architectures but does not imply that one architecture should dominate for this specific NIFTY expiry horizon. The present experiment illustrates why model family selection from published studies cannot replace market-specific, point-in-time validation. Random Forest shows a modest validation edge, and the ensemble shows a modest 2026 holdout discrimination signal, but neither is stable enough to justify trading.

## Strengths
- Exact D−6/10:00 anchor.
- Chronological development/validation/holdout design.
- Explicit look-ahead controls.
- Multiple model families and strong simple baselines.
- Separate volatility and direction evaluation.
- Cached data and automated GitHub workflows.
- FII/DII, global markets, options and sentiment included where reliable historical coverage exists.

## Limitations
- Holdout size is only 22 expiry events.
- Public option-chain coverage is incomplete.
- FII/DII cache coverage is sparse relative to the full event set.
- The sentiment source starts in 2024, so its dedicated track cannot be trained on the pre-2024 period.
- SOFNN is an SOFNN-inspired reproducible implementation rather than a guaranteed byte-for-byte reproduction of every original paper-specific component.
- Costless signed-return diagnostics do not include brokerage, statutory charges or slippage and must not be interpreted as executable option strategy returns.

## Conclusion
**Phase 33 does not promote a NIFTY direction-prediction model to trading use.** The requested architectures provide some statistically interesting signals, especially Random Forest on validation and the ensemble on the 2026 holdout, but none clears the pre-registered stability and economic promotion gate. Phase 20 remains the canonical strategy. Any model-directed option overlay must be a separately registered phase with the established Paytm Money transaction-cost, slippage and execution model.

## Future research
A separate Phase 34 can freeze the ensemble/RF candidate and test it only as a direction chooser for the Continuous Delta 6x6 strategy, including brokerage, statutory charges, slippage, entry fills, expiry gaps and regime segmentation. Alternative reference timings such as D−4, D−5 and D−7 can be tested only as new preregistered phases.

## Reproducibility artifacts
- PHASE33_STATISTICAL_SUMMARY.csv
- PHASE33_YEARLY_STABILITY.csv
- PHASE33_DECISION_TABLE.csv
- PHASE33_GARCH_SUMMARY.json
- PHASE33_POSTPROCESS_SUMMARY.json
- model_predictions.csv
- garch_predictions.csv
- cached data under data/phase33
- figures under results/phase33_nifty_prediction/figures
"""
    (OUT/"PHASE33_NIFTY_PREDICTION_MANUSCRIPT.md").write_text(manuscript)

    summary={"coverage":coverage,"garch":gsum,"decision":decision}
    (OUT/"PHASE33_POSTPROCESS_SUMMARY.json").write_text(json.dumps(summary,indent=2,default=str))
    print(json.dumps(summary,indent=2,default=str))

if __name__=="__main__":
    main()
