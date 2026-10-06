import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, SplineTransformer
from sklearn.linear_model import Ridge
from sklearn.ensemble import ExtraTreesRegressor

import phase41_regime_policy_screen as p41

ROOT=Path(".")
OUT=ROOT/"results/phase42_confidence_calibration"
SEL=OUT/"selection.json"
FIXED=ROOT/"results/phase39_counterfactual/fixed_opportunity_ledger.csv"
FEATURES=ROOT/"results/phase39_features/point_in_time_features.csv"
VIX_FILE=ROOT/"data/phase40_vix/india_vix.csv"
WARMUP=100
WINDOW=60

FOCUS_FEATURES=[
"nifty_ret_15m","nifty_ret_60m","nifty_ret_240m","nifty_rv_30m","nifty_rv_120m",
"nifty_daily_rv_20d","nifty_drawdown_20d","nifty_gap_from_prev_close","atm_iv_skew",
"atm_pcr_oi","atm_pcr_volume","candidate_iv_skew_25","candidate_credit_diff_call_minus_put",
"global_SP500_ret1","global_NASDAQ_ret1","global_NIKKEI_ret1","global_USDINR_ret1",
"global_GOLD_ret1","global_CRUDE_ret1","flow_fii_net_z20","flow_dii_net_z20","flow_flow_sentiment"]

def load_vix():
    v=pd.read_csv(VIX_FILE)
    v["date"]=pd.to_datetime(v["date"]).dt.normalize()
    v["close"]=pd.to_numeric(v["close"],errors="coerce")
    v=v.dropna(subset=["date","close"]).sort_values("date").drop_duplicates("date")
    v["ret1"]=v["close"].pct_change()
    return v

def prior_vix(v,ts):
    d=pd.Timestamp(ts).tz_localize(None).normalize()
    x=v[v.date<d]
    if x.empty:return np.nan,np.nan
    r=x.iloc[-1]
    return float(r.close),float(r.ret1) if pd.notna(r.ret1) else np.nan

def make_model(name):
    if name=="SPLINE_RIDGE_VIX":
        return Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler()),
                         ("spline",SplineTransformer(n_knots=4,degree=2,include_bias=False)),
                         ("ridge",Ridge(alpha=10.0))])
    return Pipeline([("impute",SimpleImputer(strategy="median")),
                     ("model",ExtraTreesRegressor(n_estimators=150,max_depth=5,min_samples_leaf=8,
                                                  random_state=4101,n_jobs=2))])

def xify(frame):
    x=frame.reindex(columns=FOCUS_FEATURES).copy()
    for c in ["india_vix_level","india_vix_ret1","india_vix_high","india_vix_rising","india_vix_high_rising"]:
        x[c]=frame[c].to_numpy() if c in frame.columns else np.nan
    for c in FOCUS_FEATURES:
        x[f"HIGHx_{c}"]=x[c].to_numpy()*x["india_vix_high"].to_numpy()
    return x

def calibration_width(mode,resid):
    x=np.asarray(resid[-WINDOW:],float)
    x=x[np.isfinite(x)]
    if mode=="RAW": return 0.0
    if len(x)<20: return np.nan
    if mode=="ROBUST_MAD":
        med=np.median(x)
        return float(max(1.4826*np.median(np.abs(x-med)),50.0))
    q=.80 if mode=="CONFORMAL_80" else .90
    return float(max(np.quantile(np.abs(x),q),50.0))

def gate_ok(fr,gate):
    return gate=="ALL" or (gate=="HIGH_VIX" and bool(fr["india_vix_high"])) or (gate=="HIGH_VIX_RISING" and bool(fr["india_vix_high_rising"]))

def paired_bootstrap(d,seed):
    d=np.asarray(d,float); d=d[np.isfinite(d)]
    if len(d)==0:return {"n":0}
    rng=np.random.default_rng(seed)
    idx=rng.integers(0,len(d),size=(10000,len(d)))
    means=d[idx].mean(1)
    signs=rng.choice([-1.,1.],size=(10000,len(d)))
    null=(d*signs).mean(1)
    obs=float(d.mean())
    return {"n":int(len(d)),"mean":obs,"ci_low":float(np.quantile(means,.025)),
            "ci_high":float(np.quantile(means,.975)),
            "p_one_sided":float((np.sum(null>=obs)+1)/10001),
            "positive_share":float(np.mean(d>0))}

def run_candidate(cand,fixed,features,vix):
    high_thr=float(vix[vix.date<pd.Timestamp("2024-01-01")].close.quantile(.67))
    rising_thr=float(vix[vix.date<pd.Timestamp("2024-01-01")].ret1.abs().quantile(.67))
    history=[]
    rows=[]
    active_until=pd.Timestamp("2000-01-01",tz="Asia/Kolkata")
    for i,r in fixed.iterrows():
        entry=pd.Timestamp(r.entry_ts)
        if entry.tzinfo is None: entry=entry.tz_localize("Asia/Kolkata")
        # A different action can change the exit path. Skip opportunities while
        # the previous selected trade is still open.
        if entry<=active_until: continue
        fr=features.loc[features.entry_ts==entry]
        if fr.empty: continue
        fr=fr.iloc[0].to_dict()
        level,ret1=prior_vix(vix,entry)
        fr.update({"india_vix_level":level,"india_vix_ret1":ret1,
                   "india_vix_high":int(np.isfinite(level) and level>=high_thr),
                   "india_vix_rising":int(np.isfinite(ret1) and ret1>=rising_thr)})
        fr["india_vix_high_rising"]=int(fr["india_vix_high"] and fr["india_vix_rising"])
        pred=np.nan; width=np.nan; score=np.nan; override=False
        if len(history)>=WARMUP:
            hist=pd.DataFrame(history)
            y=hist.delta_pnl.to_numpy(float)
            m=make_model(cand["model"])
            m.fit(xify(hist),y)
            pred=float(m.predict(xify(pd.DataFrame([fr])))[0])
            fit=np.asarray(m.predict(xify(hist)),float)
            width=calibration_width(cand["calibration"],y-fit)
            benefit=-pred if str(r.control_direction)=="CALL" else pred
            score=benefit-width
            override=bool(np.isfinite(score) and gate_ok(fr,cand["gate"]) and score>float(cand["margin"]))
        shadow=str(r.control_direction)
        action=("PUT" if shadow=="CALL" else "CALL") if override else shadow
        if action=="CALL":
            net=float(r.call_net_rupees); exit_ts=pd.Timestamp(r.call_exit_ts); exit_reason=str(r.call_exit_reason)
            sk=float(r.call_short_strike); lk=float(r.call_long_strike)
        else:
            net=float(r.put_net_rupees); exit_ts=pd.Timestamp(r.put_exit_ts); exit_reason=str(r.put_exit_reason)
            sk=float(r.put_short_strike); lk=float(r.put_long_strike)
        if exit_ts.tzinfo is None: exit_ts=exit_ts.tz_localize("Asia/Kolkata")
        rows.append({
            "entry_ts":entry,"expiry":str(r.expiry),"shadow_control":shadow,"action":action,
            "override":override,"pred_delta":pred,"calibration_width":width,"override_score":score,
            "policy_net_rupees":net,"control_net_rupees":float(r.control_net_rupees),
            "call_net_rupees":float(r.call_net_rupees),"put_net_rupees":float(r.put_net_rupees),
            "delta_pnl":float(r.delta_pnl_call_minus_put),"exit_ts":exit_ts,
            "exit_reason":exit_reason,"short_strike":sk,"long_strike":lk,
            "india_vix_high":fr["india_vix_high"],"india_vix_rising":fr["india_vix_rising"]
        })
        history_row={k:fr.get(k,np.nan) for k in FOCUS_FEATURES}
        history_row.update({k:fr[k] for k in ["india_vix_level","india_vix_ret1","india_vix_high","india_vix_rising","india_vix_high_rising"]})
        history_row["delta_pnl"]=float(r.delta_pnl_call_minus_put)
        history.append(history_row)
        active_until=exit_ts
    t=pd.DataFrame(rows)
    if t.empty: raise RuntimeError("zero replay opportunities")
    t["period"]=np.where(pd.to_datetime(t.expiry).dt.year<=2023,"development",
                         np.where(pd.to_datetime(t.expiry).dt.year<=2025,"validation","holdout"))
    return t

def main():
    sel=json.load(open(SEL))
    candidates=sel["top3_frozen_before_holdout"]
    fixed=pd.read_csv(FIXED)
    fixed["entry_ts"]=pd.to_datetime(fixed.entry_ts)
    fixed["expiry_dt"]=pd.to_datetime(fixed.expiry)
    fixed=fixed.sort_values("entry_ts").reset_index(drop=True)
    features=pd.read_csv(FEATURES)
    features["entry_ts"]=pd.to_datetime(features.entry_ts)
    if features.entry_ts.dt.tz is None: features.entry_ts=features.entry_ts.dt.tz_localize("Asia/Kolkata")
    fixed.entry_ts=fixed.entry_ts.dt.tz_localize("Asia/Kolkata") if fixed.entry_ts.dt.tz is None else fixed.entry_ts.dt.tz_convert("Asia/Kolkata")
    features=features.sort_values("entry_ts").drop_duplicates("entry_ts",keep="last")
    vix=load_vix()
    all_rows=[]
    for rank,c in enumerate(candidates,1):
        print("candidate",rank,c,flush=True)
        t=run_candidate(c,fixed,features,vix)
        t.to_csv(OUT/f"sequential_candidate_{rank}.csv",index=False)
        for per in ["development","validation","holdout"]:
            a=t[t.period==per]
            d=a.groupby("expiry").policy_net_rupees.sum()-a.groupby("expiry").control_net_rupees.sum()
            boot=paired_bootstrap(d.to_numpy(float),6000+rank)
            all_rows.append({"rank":rank,**c,"period":per,"policy_trades":len(a),
              "policy_net_rupees":float(a.policy_net_rupees.sum()),
              "control_net_rupees":float(a.control_net_rupees.sum()),
              "uplift_rupees":float(a.policy_net_rupees.sum()-a.control_net_rupees.sum()),
              "overrides":int(a.override.sum()),"override_rate":float(a.override.mean()) if len(a) else 0.,
              "policy_max_drawdown":float((a.policy_net_rupees.cumsum().cummax()-a.policy_net_rupees.cumsum()).max()) if len(a) else 0.,
              "control_max_drawdown":float((a.control_net_rupees.cumsum().cummax()-a.control_net_rupees.cumsum()).max()) if len(a) else 0.,
              **{f"boot_{k}":v for k,v in boot.items()}})
    s=pd.DataFrame(all_rows)
    s.to_csv(OUT/"sequential_summary.csv",index=False)
    print(s.to_string(index=False))

if __name__=="__main__":
    main()
