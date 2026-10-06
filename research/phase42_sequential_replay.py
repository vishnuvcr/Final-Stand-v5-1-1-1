import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler,SplineTransformer
from sklearn.linear_model import Ridge
from sklearn.ensemble import ExtraTreesRegressor

ROOT=Path("."); OUT=ROOT/"results/phase42_confidence_calibration"
SEL=OUT/"selection.json"
LEDGER=Path("results/phase39_counterfactual/fixed_opportunity_ledger.csv")
FEATURES=Path("results/phase39_features/point_in_time_features.csv")
FEATURES_USED=["nifty_ret_15m","nifty_ret_60m","nifty_ret_240m","nifty_rv_30m","nifty_rv_120m","nifty_daily_rv_20d","nifty_drawdown_20d","nifty_gap_from_prev_close","atm_iv_skew","atm_pcr_oi","atm_pcr_volume","candidate_iv_skew_25","candidate_credit_diff_call_minus_put","global_SP500_ret1","global_NASDAQ_ret1","global_NIKKEI_ret1","global_USDINR_ret1","global_GOLD_ret1","global_CRUDE_ret1","flow_fii_net_z20","flow_dii_net_z20","flow_flow_sentiment"]
WARMUP=100; WINDOW=60

def mdl(name):
    if name=="SPLINE_RIDGE_VIX":
        return Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler()),("spline",SplineTransformer(n_knots=4,degree=2,include_bias=False)),("ridge",Ridge(alpha=10.0))])
    return Pipeline([("impute",SimpleImputer(strategy="median")),("model",ExtraTreesRegressor(n_estimators=150,max_depth=5,min_samples_leaf=8,random_state=4101,n_jobs=2))])

def xify(z):
    x=z.reindex(columns=FEATURES_USED).copy()
    for c in ["india_vix_level","india_vix_ret1","india_vix_high","india_vix_rising","india_vix_high_rising"]:
        x[c]=z[c].to_numpy() if c in z else np.nan
    for c in FEATURES_USED:x[f"HIGHx_{c}"]=x[c].to_numpy()*x["india_vix_high"].to_numpy()
    return x

def width(mode,res):
    a=np.asarray(res[-WINDOW:],float); a=a[np.isfinite(a)]
    if mode=="RAW":return 0.0
    if len(a)<20:return np.nan
    if mode=="ROBUST_MAD":
        med=np.median(a); return max(1.4826*np.median(np.abs(a-med)),50.0)
    return max(float(np.quantile(np.abs(a),.80 if mode=="CONFORMAL_80" else .90)),50.0)

def gate(row,g):
    return g=="ALL" or (g=="HIGH_VIX" and bool(row.india_vix_high)) or (g=="HIGH_VIX_RISING" and bool(row.india_vix_high_rising))

def main():
    l=pd.read_csv(LEDGER); f=pd.read_csv(FEATURES)
    l["entry_ts"]=pd.to_datetime(l.entry_ts); f["entry_ts"]=pd.to_datetime(f.entry_ts)
    z=l.merge(f.drop(columns=[c for c in ["split","control_direction","control_net_rupees","delta_pnl_call_minus_put"] if c in f]),on=["entry_ts","expiry"],how="inner",suffixes=("","_f")).sort_values("entry_ts").reset_index(drop=True)
    assert len(z)==477
    # Point-in-time VIX is inherited from the Phase-42 fixed screen by recomputing
    # the same prior-session alignment from the cached series.
    v=pd.read_csv("data/phase40_vix/india_vix.csv"); v["date"]=pd.to_datetime(v.date).dt.normalize(); v["close"]=pd.to_numeric(v.close,errors="coerce"); v=v.dropna(subset=["date","close"]).sort_values("date").drop_duplicates("date"); v["ret1"]=v.close.pct_change()
    q=float(v[v.date<pd.Timestamp("2024-01-01")].close.quantile(.67)); rq=float(v[v.date<pd.Timestamp("2024-01-01")].ret1.abs().quantile(.67))
    vals=[]
    for ts in z.entry_ts:
        x=v[v.date<pd.Timestamp(ts).normalize()]
        if x.empty: vals.append((np.nan,np.nan))
        else: vals.append((float(x.iloc[-1].close),float(x.iloc[-1].ret1) if pd.notna(x.iloc[-1].ret1) else np.nan))
    z["india_vix_level"]=[a for a,b in vals]; z["india_vix_ret1"]=[b for a,b in vals]
    z["india_vix_high"]=(z.india_vix_level>=q).astype(int); z["india_vix_rising"]=(z.india_vix_ret1>=rq).astype(int); z["india_vix_high_rising"]=(z.india_vix_high&z.india_vix_rising).astype(int)
    sel=json.load(open(SEL)); rows=[]
    for rank,c in enumerate(sel["top3_frozen_before_holdout"],1):
        pred=np.full(len(z),np.nan); wid=np.full(len(z),np.nan); score=np.full(len(z),np.nan)
        y=z.delta_pnl_call_minus_put.to_numpy(float); X=xify(z)
        actions=[]
        for i in range(len(z)):
            if i<WARMUP: actions.append(False); continue
            m=mdl(c["model"]); m.fit(X.iloc[:i],y[:i]); p=float(m.predict(X.iloc[[i]])[0]); pred[i]=p
            res=y[:i]-np.asarray(m.predict(X.iloc[:i]),float); w=width(c["calibration"],res); wid[i]=w
            benefit=-p if str(z.iloc[i].control_direction)=="CALL" else p; score[i]=benefit-w
            actions.append(bool(np.isfinite(score[i]) and gate(z.iloc[i],c["gate"]) and score[i]>float(c["margin"])))
        out=z[["split","expiry","entry_ts","control_direction","control_net_rupees","call_net_rupees","put_net_rupees","call_exit_ts","put_exit_ts","call_exit_reason","put_exit_reason"]].copy()
        out["pred_delta"]=pred; out["calibration_width"]=wid; out["override_score"]=score; out["override"]=actions
        out["action"]=np.where(out.override,np.where(out.control_direction=="CALL","PUT","CALL"),out.control_direction)
        out["policy_net_rupees"]=np.where(out.override,np.where(out.control_direction=="CALL",out.put_net_rupees,out.call_net_rupees),out.control_net_rupees)
        out["exit_ts"]=np.where(out.override,np.where(out.control_direction=="CALL",out.put_exit_ts,out.call_exit_ts),np.where(out.control_direction=="CALL",out.call_exit_ts,out.put_exit_ts))
        out.to_csv(OUT/f"sequential_candidate_{rank}.csv",index=False)
        for per in ["development","validation","holdout"]:
            a=out[out.split==per]; d=a.groupby("expiry").policy_net_rupees.sum()-a.groupby("expiry").control_net_rupees.sum(); d=d.to_numpy(float)
            rng=np.random.default_rng(5200+rank); idx=rng.integers(0,len(d),size=(10000,len(d))); means=d[idx].mean(1); signs=rng.choice([-1.,1.],size=(10000,len(d))); null=(d*signs).mean(1)
            rows.append({"rank":rank,"model":c["model"],"calibration":c["calibration"],"margin":c["margin"],"gate":c["gate"],"period":per,
             "policy_trades":len(a),"control_trades":len(a),"policy_net_rupees":float(a.policy_net_rupees.sum()),"control_net_rupees":float(a.control_net_rupees.sum()),
             "uplift_rupees":float(d.sum()),"overrides":int(a.override.sum()),"override_rate":float(a.override.mean()),
             "boot_n":len(d),"boot_mean_uplift_per_expiry":float(d.mean()),"boot_ci_low":float(np.quantile(means,.025)),"boot_ci_high":float(np.quantile(means,.975)),
             "boot_p_one_sided":float((np.sum(null>=d.mean())+1)/10001)})
    pd.DataFrame(rows).to_csv(OUT/"sequential_summary.csv",index=False)
    print(pd.DataFrame(rows).to_string(index=False))

if __name__=="__main__":main()
