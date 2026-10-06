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
            signed=np.where(pr==1,q["target_return"],-q["target_return"]).to_numpy(float)
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

    summary={"coverage":coverage,"garch":gsum,"decision":decision}
    (OUT/"PHASE33_POSTPROCESS_SUMMARY.json").write_text(json.dumps(summary,indent=2,default=str))
    print(json.dumps(summary,indent=2,default=str))

if __name__=="__main__":
    main()
