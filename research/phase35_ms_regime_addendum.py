import json, warnings
from pathlib import Path
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
SEED=1337
TZ="Asia/Kolkata"
DATA=Path("data/phase33")
OUT=Path("results/phase35_advanced_tree_prediction")
TRAIN_END=pd.Timestamp("2023-12-31 23:59:59",tz=TZ)
VAL_END=pd.Timestamp("2025-12-31 23:59:59",tz=TZ)
HOLD_START=pd.Timestamp("2026-01-01",tz=TZ)
HOLD_END=pd.Timestamp("2026-09-30 23:59:59",tz=TZ)

def norm(x):
    y=pd.to_datetime(x,errors="coerce")
    if getattr(y.dt,"tz",None) is None:y=y.dt.tz_localize(TZ)
    else:y=y.dt.tz_convert(TZ)
    return y.astype(f"datetime64[ns, {TZ}]")
def load():
    ev=pd.read_parquet(DATA/"events.parquet"); d=pd.read_parquet(DATA/"nifty_daily.parquet")
    ev["expiry"]=norm(ev.expiry).dt.normalize(); ev["ref_ts"]=norm(ev.ref_ts)
    d["date"]=norm(d.date).dt.normalize()
    ev=ev[(ev.ref_ts>=pd.Timestamp("2021-05-27",tz=TZ))&(ev.ref_ts<=HOLD_END)].sort_values("ref_ts").copy()
    ev["split"]=np.where(ev.ref_ts<=TRAIN_END,"train",np.where(ev.ref_ts<=VAL_END,"validation","holdout"))
    return ev,d.sort_values("date")
def markov_feature(ref,daily):
    from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
    z=daily[daily.date<ref.normalize()].copy()
    r=np.log(z.close/z.close.shift(1)).dropna()*100
    if len(r)<300:return [0.5,0.5,0.0]
    try:
        res=MarkovRegression(r,k_regimes=2,trend="c",switching_variance=True).fit(disp=False,maxiter=150)
        p=np.asarray(res.filtered_marginal_probabilities.iloc[-1],float)
        p=np.clip(p,1e-6,1-1e-6); p=p/p.sum()
        return [float(p[0]),float(p[1]),float(-np.sum(p*np.log(p)))]
    except Exception:
        return [0.5,0.5,np.log(2)]
def prep_states(ev,daily):
    p=Path("data/phase35_ms_regime.parquet")
    if p.exists():
        z=pd.read_parquet(p); z["ref_ts"]=norm(z.ref_ts); return z
    rows=[]
    for _,r in ev.iterrows():
        p0,p1,en=markov_feature(pd.Timestamp(r.ref_ts),daily)
        rows.append({"ref_ts":r.ref_ts,"ms_p0":p0,"ms_p1":p1,"ms_entropy":en})
    z=pd.DataFrame(rows); z["ref_ts"]=norm(z.ref_ts); z.to_parquet(p,index=False); return z
def cols(ev):
    drop={"expiry","ref_ts","ref_spot","expiry_close","target_return","target_direction","split"}
    return [c for c in ev if c not in drop and pd.api.types.is_numeric_dtype(ev[c])]
def fit_lgb(fit,test,features):
    from sklearn.impute import SimpleImputer
    from lightgbm import LGBMClassifier
    imp=SimpleImputer(strategy="median").fit(fit[features]); A=imp.transform(fit[features]); B=imp.transform(test[features])
    m=LGBMClassifier(n_estimators=220,num_leaves=15,max_depth=4,learning_rate=.03,min_child_samples=8,reg_lambda=2.0,verbosity=-1,random_state=SEED)
    m.fit(A,fit.target_direction.astype(int)); return m.predict_proba(B)[:,1]
def metrics(y,p):
    from sklearn.metrics import accuracy_score,balanced_accuracy_score,roc_auc_score,log_loss,brier_score_loss
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6); y=np.asarray(y,int)
    return {"n":len(y),"accuracy":accuracy_score(y,p>=.5),"balanced_accuracy":balanced_accuracy_score(y,p>=.5),
            "roc_auc":roc_auc_score(y,p) if len(np.unique(y))==2 else np.nan,
            "log_loss":log_loss(y,np.c_[1-p,p],labels=[0,1]),"brier":brier_score_loss(y,p)}
def boot(x,n=4000):
    rng=np.random.default_rng(SEED); a=np.array([rng.choice(x,len(x),replace=True).mean() for _ in range(n)])
    return float(np.quantile(a,.025)),float(np.quantile(a,.975))
def sf(x,n=12000):
    rng=np.random.default_rng(SEED); obs=abs(np.mean(x)); s=rng.choice([-1,1],size=(n,len(x))); z=np.abs((s*x).mean(axis=1))
    return float((1+(z>=obs).sum())/(n+1))
def main():
    ev,d=load(); z=prep_states(ev,d)
    ev=ev.drop(columns=["ms_p0","ms_p1","ms_entropy"],errors="ignore").merge(z[["ref_ts","ms_p0","ms_p1","ms_entropy"]],on="ref_ts",how="left")
    base=[c for c in cols(ev) if c not in {"ms_p0","ms_p1","ms_entropy"}]; ms=base+["ms_p0","ms_p1","ms_entropy"]
    tr=ev[ev.split=="train"].copy(); va=ev[ev.split=="validation"].copy(); ho=ev[ev.split=="holdout"].copy()
    rows=[]; econ=[]
    for split,fit,test in [("validation",tr,va),("holdout",pd.concat([tr,va]).sort_values("ref_ts"),ho)]:
        p=fit_lgb(fit,test,ms); q=test[["expiry","ref_ts","target_return","target_direction"]].copy(); q["ms_regime_tree_prob"]=p; q["split"]=split; rows.append(q)
        sr=np.where(p>=.5,1,-1)*test.target_return.to_numpy(float); lo,hi=boot(sr)
        econ.append({"split":split,"model":"ms_regime_tree","hit_rate":float((sr>0).mean()),"mean_signed_log_return":float(sr.mean()),"sum_signed_log_return":float(sr.sum()),"bootstrap_ci_low":lo,"bootstrap_ci_high":hi,"signflip_pvalue":sf(sr)})
    pr=pd.concat(rows,ignore_index=True); pr.to_csv(OUT/"ms_regime_tree_predictions.csv",index=False)
    met=[]
    for split,g in pr.groupby("split"): met.append({"split":split,"model":"ms_regime_tree",**metrics(g.target_direction,g.ms_regime_tree_prob)})
    pd.DataFrame(met).to_csv(OUT/"ms_regime_tree_metrics.csv",index=False)
    pd.DataFrame(econ).to_csv(OUT/"ms_regime_tree_economic.csv",index=False)
    with open(OUT/"ms_regime_tree_metadata.json","w") as f: json.dump({"method":"2-state Markov-switching volatility gate + LightGBM","proxy_note":"Reproducible proxy for the role of the published MS-Beta-t-QVAR regime gate; not a byte-for-byte implementation of that paper's full model.","events":len(ev)},f,indent=2)
    print(pd.DataFrame(met).to_string(index=False)); print(pd.DataFrame(econ).to_string(index=False))
if __name__=="__main__":main()
