import json, os
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, SplineTransformer
from sklearn.linear_model import Ridge
from sklearn.ensemble import ExtraTreesRegressor

import phase39_sequential_policy as p39
from phase39_counterfactual_engine import nearest_delta_strike, run_arm

ROOT=Path(".")
OUT=ROOT/"results/phase42_confidence_calibration"
SEL=OUT/"selection.json"
CONTROL_DEV=Path("results/phase39_data/development_control_trades_2021_2023.csv")
CONTROL_FROZEN=Path("results/phase39_data/frozen_control_trades_2024_2026-06-30.csv")
FOCUS_FEATURES=[
"nifty_ret_15m","nifty_ret_60m","nifty_ret_240m","nifty_rv_30m","nifty_rv_120m",
"nifty_daily_rv_20d","nifty_drawdown_20d","nifty_gap_from_prev_close","atm_iv_skew",
"atm_pcr_oi","atm_pcr_volume","candidate_iv_skew_25","candidate_credit_diff_call_minus_put",
"global_SP500_ret1","global_NASDAQ_ret1","global_NIKKEI_ret1","global_USDINR_ret1",
"global_GOLD_ret1","global_CRUDE_ret1","flow_fii_net_z20","flow_dii_net_z20","flow_flow_sentiment"]
WARMUP=100; WINDOW=60; WIDTH=50.0

def vix_load():
    v=pd.read_csv("data/phase40_vix/india_vix.csv")
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

def model(name):
    if name=="SPLINE_RIDGE_VIX":
        return Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler()),
                         ("spline",SplineTransformer(n_knots=4,degree=2,include_bias=False)),("ridge",Ridge(alpha=10.0))])
    return Pipeline([("impute",SimpleImputer(strategy="median")),
                     ("model",ExtraTreesRegressor(n_estimators=150,max_depth=5,min_samples_leaf=8,random_state=4101,n_jobs=2))])

def xify(frame):
    x=frame.reindex(columns=FOCUS_FEATURES).copy()
    for c in ["india_vix_level","india_vix_ret1","india_vix_high","india_vix_rising","india_vix_high_rising"]:
        x[c]=frame[c].to_numpy() if c in frame else np.nan
    for c in FOCUS_FEATURES:x[f"HIGHx_{c}"]=x[c].to_numpy()*x["india_vix_high"].to_numpy()
    return x

def width(mode,resid):
    x=np.asarray(resid[-WINDOW:],float); x=x[np.isfinite(x)]
    if mode=="RAW":return 0.0
    if len(x)<20:return np.nan
    if mode=="ROBUST_MAD":
        med=np.median(x); return float(max(1.4826*np.median(np.abs(x-med)),50.0))
    return float(max(np.quantile(np.abs(x),.80 if mode=="CONFORMAL_80" else .90),50.0))

def gate(fr,g):
    return g=="ALL" or (g=="HIGH_VIX" and bool(fr["india_vix_high"])) or (g=="HIGH_VIX_RISING" and bool(fr["india_vix_high_rising"]))

def shadow(control,ts):
    i=control.entry_ts.searchsorted(ts,side="right")-1
    return str(control.iloc[i].direction) if i>=0 else "CALL"

def run_candidate(cand,spot,daily,global_d,flows,sentiment,vix,expiries,control):
    high_thr=float(vix[vix.date<pd.Timestamp("2024-01-01")].close.quantile(.67))
    history=[]; trades=[]; cache={}
    for expiry in expiries:
        if expiry not in cache:
            od=p39.load_option(expiry); od["expiry_ts"]=expiry+pd.Timedelta(hours=15,minutes=30); cache[expiry]=od
        od=cache[expiry]
        end=expiry+pd.Timedelta(hours=15,minutes=29)
        timeline=spot[(spot.timestamp<=end)&(spot.timestamp<expiry.normalize())].copy().sort_values("timestamp").reset_index(drop=True)
        cursor=0
        while cursor<len(timeline):
            entry=p39.norm_scalar_ts(timeline.iloc[cursor].timestamp)
            if entry.hour<9 or (entry.hour==9 and entry.minute<20) or entry.hour>15 or (entry.hour==15 and entry.minute>=28):
                cursor+=1; continue
            snap=od[od.timestamp==entry]; sr=spot[spot.timestamp==entry]
            if snap.empty or sr.empty:cursor+=1;continue
            s=float(sr.iloc[0].close)
            shadow_dir=shadow(control,entry)
            level,ret1=prior_vix(vix,entry)
            fr=p39.build_feature_row(entry,expiry,snap,s,spot,daily,global_d,flows,sentiment,cache,expiries)
            fr.update({"india_vix_level":level,"india_vix_ret1":ret1,
                       "india_vix_high":int(np.isfinite(level) and level>=high_thr),
                       "india_vix_rising":int(np.isfinite(ret1) and ret1>=float(vix[vix.date<pd.Timestamp("2024-01-01")].ret1.abs().quantile(.67)))})
            fr["india_vix_high_rising"]=int(fr["india_vix_high"] and fr["india_vix_rising"])
            fdf=pd.DataFrame([fr])
            override=False; pred=np.nan; w=np.nan; score=np.nan
            if len(history)>=WARMUP:
                hist=pd.DataFrame(history); m=model(cand["model"]); X=xify(hist); y=hist.delta_pnl.to_numpy(float)
                m.fit(X,y); pred=float(m.predict(xify(fdf))[0]); fitted=np.asarray(m.predict(X),float)
                res=y-fitted; w=width(cand["calibration"],res)
                benefit=-pred if shadow_dir=="CALL" else pred
                score=benefit-w
                override=bool(np.isfinite(score) and gate(fr,cand["gate"]) and score>float(cand["margin"]))
            action=("PUT" if shadow_dir=="CALL" else "CALL") if override else shadow_dir
            typ="CE" if action=="CALL" else "PE"; target=.25 if typ=="CE" else -.25
            chosen=nearest_delta_strike(snap,s,entry,typ,target)
            if chosen is None:cursor+=1;continue
            short_k,_=chosen; long_k=short_k+WIDTH if typ=="CE" else short_k-WIDTH
            arm=run_arm(od,spot,entry,expiry,typ,short_k,long_k,p39.lot_size_for_expiry(expiry))
            alt_typ="PE" if typ=="CE" else "CE"; alt_target=-.25 if alt_typ=="PE" else .25
            alt_sel=nearest_delta_strike(snap,s,entry,alt_typ,alt_target)
            if alt_sel is None:cursor+=1;continue
            alt_k,_=alt_sel; alt_long=alt_k-WIDTH if alt_typ=="PE" else alt_k+WIDTH
            alt=run_arm(od,spot,entry,expiry,alt_typ,alt_k,alt_long,p39.lot_size_for_expiry(expiry))
            delta=float(arm["net_rupees"]-alt["net_rupees"]) if action=="CALL" else float(alt["net_rupees"]-arm["net_rupees"])
            trades.append({"entry_ts":str(entry),"expiry":str(expiry.date()),"shadow_control":shadow_dir,"action":action,
                           "override":override,"pred_delta":pred,"calibration_width":w,"override_score":score,
                           "policy_net_rupees":float(arm["net_rupees"]),"gross_rupees":float(arm["gross_rupees"]),
                           "cost_rupees":float(arm["cost_rupees"]),"delta_pnl":delta,"exit_ts":str(arm["exit_ts"]),
                           "exit_reason":arm["exit_reason"]})
            row={k:fr.get(k,np.nan) for k in FOCUS_FEATURES}
            row.update({"india_vix_level":fr["india_vix_level"],"india_vix_ret1":fr["india_vix_ret1"],
                        "india_vix_high":fr["india_vix_high"],"india_vix_rising":fr["india_vix_rising"],
                        "india_vix_high_rising":fr["india_vix_high_rising"],"delta_pnl":delta})
            history.append(row)
            exit_ts=p39.norm_scalar_ts(arm["exit_ts"]); hits=np.flatnonzero(timeline.timestamp.to_numpy()==exit_ts)
            if len(hits)==0:break
            cursor=int(hits[0])+1
    t=pd.DataFrame(trades)
    if t.empty:raise RuntimeError("zero sequential trades")
    t["entry_ts"]=p39.norm_ts(t.entry_ts); t["exit_ts"]=p39.norm_ts(t.exit_ts)
    t["expiry_dt"]=pd.to_datetime(t.expiry).dt.tz_localize(p39.TZ)
    t["period"]=np.where(t.expiry_dt.dt.year<=2023,"development",np.where(t.expiry_dt.dt.year<=2025,"validation","holdout"))
    return t

def dd(x):
    a=np.asarray(x,float); eq=np.cumsum(a); return float((np.maximum.accumulate(np.r_[0.,eq])[1:]-eq).max()) if len(a) else 0.

def main():
    sel=json.load(open(SEL)); candidates=sel["top3_frozen_before_holdout"]
    vix=vix_load(); spot=p39.load_spot(); daily=p39.load_daily_source("nifty_daily.parquet")
    global_d=p39.load_daily_source("global_daily.parquet"); flows=p39.load_daily_source("fii_dii_daily.parquet")
    sentiment=p39.load_daily_source("sentiment_daily.parquet"); expiries=p39.expected_expiries(spot)
    from huggingface_hub import HfApi
    api=HfApi(token=os.getenv("HF_TOKEN") or None); files=set(api.list_repo_files(p39.HF_REPO,repo_type="dataset"))
    expiries=[e for e in expiries if f"options/NIFTY/{e.strftime('%Y-%m-%d')}.parquet" in files]
    control=pd.concat([pd.read_csv(CONTROL_DEV),pd.read_csv(CONTROL_FROZEN)],ignore_index=True)
    control["entry_ts"]=p39.norm_ts(control.entry_ts); control["expiry_dt"]=pd.to_datetime(control.expiry).dt.tz_localize(p39.TZ)
    control["period"]=np.where(control.expiry_dt.dt.year<=2023,"development",np.where(control.expiry_dt.dt.year<=2025,"validation","holdout"))
    rows=[]
    for rank,c in enumerate(candidates,1):
        print("candidate",rank,c,flush=True)
        t=run_candidate(c,spot,daily,global_d,flows,sentiment,vix,expiries,control)
        t.to_csv(OUT/f"sequential_candidate_{rank}.csv",index=False)
        for per in ["development","validation","holdout"]:
            a=t[t.period==per]; cc=control[control.period==per]
            p=a.groupby("expiry").policy_net_rupees.sum(); q=cc.groupby("expiry").net_rupees.sum()
            keys=p.index.intersection(q.index); d=np.asarray([p[k]-q[k] for k in keys],float)
            rng=np.random.default_rng(5200+rank); idx=rng.integers(0,len(d),size=(10000,len(d))) if len(d) else np.empty((0,0))
            means= d[idx].mean(1) if len(d) else np.array([])
            signs=rng.choice([-1.,1.],size=(10000,len(d))) if len(d) else np.empty((0,0))
            null=(d*signs).mean(1) if len(d) else np.array([])
            obs=float(d.mean()) if len(d) else np.nan
            rows.append({"rank":rank,"model":c["model"],"calibration":c["calibration"],"margin":c["margin"],"gate":c["gate"],
                          "period":per,"policy_trades":len(a),"control_trades":len(cc),
                          "policy_net_rupees":float(a.policy_net_rupees.sum()),"control_net_rupees":float(cc.net_rupees.sum()),
                          "uplift_rupees":float(a.policy_net_rupees.sum()-cc.net_rupees.sum()),"overrides":int(a.override.sum()),
                          "override_rate":float(a.override.mean()) if len(a) else 0.,
                          "policy_drawdown_rupees":dd(a.policy_net_rupees),"control_drawdown_rupees":dd(cc.net_rupees),
                          "boot_n":len(d),"boot_mean_uplift_per_expiry":obs,
                          "boot_ci_low":float(np.quantile(means,.025)) if len(means) else np.nan,
                          "boot_ci_high":float(np.quantile(means,.975)) if len(means) else np.nan,
                          "boot_p_one_sided":float((np.sum(null>=obs)+1)/10001) if len(null) else np.nan})
    pd.DataFrame(rows).to_csv(OUT/"sequential_summary.csv",index=False)
    print(pd.DataFrame(rows).to_string(index=False))

if __name__=="__main__":main()
