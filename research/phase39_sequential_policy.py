import json, math, os, re
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, SplineTransformer
from sklearn.linear_model import Ridge
from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.errors import RemoteEntryNotFoundError

from phase39_feature_matrix import (
    TZ, HF_REPO, norm_ts, norm_scalar_ts, load_option, intraday_features,
    daily_features, option_features, load_daily_source
)
from phase39_counterfactual_engine import nearest_delta_strike, run_arm

ROOT=Path(".")
FEATURE_FILE=ROOT/"results/phase39_models/locked_feature_list.json"
FEATURE_MATRIX=ROOT/"results/phase39_features/point_in_time_features.csv"
DEV_CONTROL=ROOT/"results/phase39_data/development_control_trades_2021_2023.csv"
FROZEN_CONTROL=ROOT/"results/phase39_data/frozen_control_trades_2024_2026-06-30.csv"
OUT=ROOT/"results/phase39_sequential_policy"
OUT.mkdir(parents=True,exist_ok=True)

MARGIN=500.0
UNCERTAINTY_Z=1.0
WARMUP=100
START=pd.Timestamp("2021-05-27",tz=TZ)
END=pd.Timestamp("2026-05-19",tz=TZ)
ENTRY_HOUR=9
ENTRY_MINUTE=20
LAST_ENTRY_HOUR=15
LAST_ENTRY_MINUTE=28
WIDTH=50.0
LOTS=6

def load_spot():
    p=hf_hub_download(repo_id=HF_REPO,filename="index/NIFTY.parquet",repo_type="dataset",token=os.getenv("HF_TOKEN") or None)
    d=pd.read_parquet(p)
    d["timestamp"]=pd.to_datetime(d["timestamp"])
    d["timestamp"]=d["timestamp"].dt.tz_localize(TZ) if d["timestamp"].dt.tz is None else d["timestamp"].dt.tz_convert(TZ)
    d=d.sort_values("timestamp").drop_duplicates("timestamp",keep="last")
    d["spot"]=d["close"]
    return d

def expected_expiries(spot):
    trading=sorted(set(pd.to_datetime(spot.timestamp.dt.normalize())))
    if not trading: return []
    first,last=min(trading),max(trading)
    out=[]
    weeks=pd.date_range(first-pd.Timedelta(days=7),last+pd.Timedelta(days=7),freq="W-MON",tz=TZ)
    for m in weeks:
        if m>=pd.Timestamp("2025-09-01",tz=TZ): wd=1
        elif m>=pd.Timestamp("2025-04-04",tz=TZ): wd=0
        else: wd=3
        sched=m+pd.Timedelta(days=wd)
        cand=[d for d in trading if m<=d<=sched]
        if cand:
            e=max(cand)
            if START<=e<=END: out.append(e)
    return sorted(set(out))

def lot_size_for_expiry(expiry):
    if expiry<pd.Timestamp("2021-07-29",tz=TZ): return 75
    if expiry<pd.Timestamp("2024-05-02",tz=TZ): return 50
    if expiry<=pd.Timestamp("2024-12-26",tz=TZ): return 25
    if expiry<=pd.Timestamp("2025-01-23",tz=TZ): return 75
    if expiry==pd.Timestamp("2025-01-30",tz=TZ): return 25
    if expiry<pd.Timestamp("2026-01-06",tz=TZ): return 75
    return 65

def locked_features():
    return json.loads(FEATURE_FILE.read_text())["features"]

def build_feature_row(entry,expiry,snap,spot_value,spot_hist,daily,global_d,flows,sentiment,option_cache,expiries):
    expiry_ts=expiry+pd.Timedelta(hours=15,minutes=30)
    row={"entry_ts":entry,"expiry":str(expiry.date()),"dte_days":float((expiry_ts-entry).total_seconds()/86400.0),
         "entry_weekday":int(entry.weekday()),"entry_hour":int(entry.hour),"entry_minute":int(entry.minute)}
    row.update(intraday_features(spot_hist,entry))
    row.update(daily_features(daily,entry))
    row.update(option_features(snap,spot_value,expiry_ts))
    idx=expiries.index(expiry)
    if idx+1<len(expiries):
        ne=expiries[idx+1]; ns=option_cache.get(ne)
        if ns is None:
            try:
                ns=load_option(ne)
            except RemoteEntryNotFoundError:
                ns=pd.DataFrame()
            if not ns.empty:
                ns["expiry_ts"]=ne+pd.Timedelta(hours=15,minutes=30)
            option_cache[ne]=ns
        if not ns.empty:
            nsnap=ns[ns.timestamp==entry]
            if not nsnap.empty:
                row.update(option_features(snap,spot_value,expiry_ts,nsnap,ne+pd.Timedelta(hours=15,minutes=30)))
    # Previous available source date only.
    def prior_values(frame):
        if frame is None or frame.empty or "date" not in frame.columns: return {}
        dates=pd.to_datetime(frame.date)
        if getattr(dates,"dt",None) is None: return {}
        if dates.dt.tz is None: dates=dates.dt.tz_localize(TZ)
        else: dates=dates.dt.tz_convert(TZ)
        j=frame.loc[dates.dt.normalize() < entry.normalize()]
        if j.empty: return {}
        r=j.iloc[-1]
        return {c:r[c] for c in frame.columns if c!="date" and pd.api.types.is_numeric_dtype(frame[c])}
    for prefix,frame in [("global_",global_d),("flow_",flows),("sent_",sentiment)]:
        for c,v in prior_values(frame).items():
            row[prefix+c]=v
    return row

def fit_gam(history,test):
    feats=locked_features()
    tr=history.copy()
    x=tr.reindex(columns=feats).replace([np.inf,-np.inf],np.nan)
    y=tr["delta_pnl"].to_numpy(float)
    pipe=Pipeline([
        ("imp",SimpleImputer(strategy="median")),
        ("scale",StandardScaler()),
        ("spline",SplineTransformer(n_knots=4,degree=2,include_bias=False)),
        ("ridge",Ridge(alpha=10.0))
    ])
    pipe.fit(x,y)
    tx=pipe.predict(x)
    resid=y-tx
    sd=max(float(np.std(resid,ddof=1)),1.0)
    tx=test.reindex(columns=feats).replace([np.inf,-np.inf],np.nan)
    pred=float(pipe.predict(tx)[0])
    return pred,sd

from sklearn.pipeline import Pipeline

def paired_bootstrap(policy_exp,control_exp,B=10000,seed=1337):
    p=policy_exp.groupby("expiry").net.sum()
    c=control_exp.groupby("expiry").net.sum()
    keys=sorted(set(p.index)&set(c.index))
    d=np.asarray([p.get(k,0.0)-c.get(k,0.0) for k in keys],float)
    if len(d)==0: return {"expiries":0,"mean":np.nan,"lo":np.nan,"hi":np.nan,"p_positive":np.nan}
    rng=np.random.default_rng(seed); n=len(d)
    sims=np.empty(B)
    for i in range(B): sims[i]=rng.choice(d,size=n,replace=True).sum()
    return {"expiries":n,"mean":float(d.sum()),"lo":float(np.quantile(sims,.025)),"hi":float(np.quantile(sims,.975)),
            "p_positive":float(np.mean(sims>0))}

def max_drawdown(p):
    eq=np.cumsum(np.asarray(p,float)); peak=np.maximum.accumulate(np.r_[0.0,eq]); return float(np.max(peak[1:]-eq)) if len(eq) else 0.0

def main():
    spot=load_spot()
    daily=load_daily_source("nifty_daily.parquet")
    global_d=load_daily_source("global_daily.parquet")
    flows=load_daily_source("fii_dii_daily.parquet")
    sentiment=load_daily_source("sentiment_daily.parquet")
    expected_all=expected_expiries(spot)
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    repo_files=set(api.list_repo_files(HF_REPO,repo_type="dataset"))
    expiries=[e for e in expected_all if f"options/NIFTY/{e.strftime('%Y-%m-%d')}.parquet" in repo_files]
    option_cache={}
    def get_option(e):
        e=norm_scalar_ts(e).normalize()
        if e not in option_cache:
            d=load_option(e)
            d["expiry_ts"]=e+pd.Timedelta(hours=15,minutes=30)
            option_cache[e]=d
        return option_cache[e]
    # Canonical shadow direction schedule.
    ctl=pd.concat([pd.read_csv(DEV_CONTROL),pd.read_csv(FROZEN_CONTROL)],ignore_index=True)
    ctl["entry_ts"]=norm_ts(ctl["entry_ts"])
    ctl=ctl.sort_values("entry_ts").reset_index(drop=True)
    ctl=ctl[(ctl.entry_ts>=START)&(ctl.entry_ts<=END)]
    control_times=ctl.entry_ts.to_numpy()
    control_dirs=ctl.direction.to_numpy()
    def shadow_direction(ts):
        i=ctl.entry_ts.searchsorted(ts,side="right")-1
        if i<0: return "CALL"
        return str(control_dirs[i])

    history=[]
    trades=[]
    skipped=[]
    cursor_start=True

    # Iterate expiry by expiry, preserving continuous chronological state.
    for expiry in expiries:
        od=get_option(expiry)
        expiry_day=expiry.normalize()
        end_ts=expiry+pd.Timedelta(hours=15,minutes=29)
        idx_exp=expected_all.index(expiry)
        window_start=(expected_all[idx_exp-1]+pd.Timedelta(hours=15,minutes=30)) if idx_exp>0 else START
        timeline=spot[(spot.timestamp>window_start)&(spot.timestamp<=end_ts)].copy()
        timeline=timeline[timeline.timestamp<expiry_day].sort_values("timestamp").reset_index(drop=True)
        # New entry is allowed any day except expiry day and after 09:20, before the final-entry cutoff.
        cursor=0
        while cursor<len(timeline):
            entry=norm_scalar_ts(timeline.iloc[cursor].timestamp)
            if entry.normalize()==expiry_day: break
            if entry.hour<ENTRY_HOUR or (entry.hour==ENTRY_HOUR and entry.minute<ENTRY_MINUTE):
                cursor+=1; continue
            if entry.hour>LAST_ENTRY_HOUR or (entry.hour==LAST_ENTRY_HOUR and entry.minute>=LAST_ENTRY_MINUTE):
                cursor+=1; continue
            snap=od[od.timestamp==entry]
            if snap.empty:
                cursor+=1; continue
            srow=spot[spot.timestamp==entry]
            if srow.empty:
                cursor+=1; continue
            s=float(srow.iloc[0]["close"])
            shadow=shadow_direction(entry)
            # Current point-in-time features.
            fr=build_feature_row(entry,expiry,snap,s,spot,daily,global_d,flows,sentiment,option_cache,expiries)
            fdf=pd.DataFrame([fr])
            if len(history)<WARMUP:
                action=shadow
                pred=np.nan; unc=np.nan; override=False
            else:
                pred,unc=fit_gam(pd.DataFrame(history),fdf)
                improvement=(-pred) if shadow=="CALL" else pred
                score=improvement-UNCERTAINTY_Z*unc
                override=bool(score>MARGIN)
                action=("PUT" if shadow=="CALL" else "CALL") if override else shadow
            typ="CE" if action=="CALL" else "PE"
            target=0.25 if typ=="CE" else -0.25
            found=nearest_delta_strike(snap,s,entry,typ,target)
            if found is None:
                skipped.append({"entry_ts":str(entry),"expiry":str(expiry.date()),"reason":"no_delta_strike"})
                cursor+=1; continue
            sk,entry_delta=found
            lk=sk+WIDTH if typ=="CE" else sk-WIDTH
            arm=run_arm(od,spot,entry,expiry,typ,sk,lk,lot_size_for_expiry(expiry))
            # Counterfactual alternative arm is computed now for future model training.
            alt_typ="PE" if typ=="CE" else "CE"
            alt_target=-0.25 if alt_typ=="PE" else 0.25
            af=nearest_delta_strike(snap,s,entry,alt_typ,alt_target)
            if af is None:
                skipped.append({"entry_ts":str(entry),"expiry":str(expiry.date()),"reason":"no_counterfactual_delta_strike"})
                cursor+=1; continue
            ask,adelta=af; alk=ask-WIDTH if alt_typ=="PE" else ask+WIDTH
            alt=run_arm(od,spot,entry,expiry,alt_typ,ask,alk,lot_size_for_expiry(expiry))
            delta=float(arm["net_rupees"]-alt["net_rupees"]) if action=="CALL" else float(alt["net_rupees"]-arm["net_rupees"])
            # Note: history target is always CALL-PUT, independent of chosen action.
            delta_call_put=float(arm["net_rupees"]-alt["net_rupees"]) if action=="CALL" else float(alt["net_rupees"]-arm["net_rupees"])
            chosen_net=float(arm["net_rupees"])
            trades.append({
                "expiry":str(expiry.date()),"entry_ts":str(entry),"exit_ts":arm["exit_ts"],
                "shadow_control_direction":shadow,"action":action,"override":bool(override),
                "pred_delta":pred,"pred_unc":unc,
                "policy_net_rupees":chosen_net,"policy_gross_rupees":arm["gross_rupees"],"policy_cost_rupees":arm["cost_rupees"],
                "call_put_delta":delta_call_put,
                "exit_reason":arm["exit_reason"],"short_strike":arm["short_strike"],"long_strike":arm["long_strike"]
            })
            history.append({**{k:fr.get(k,np.nan) for k in locked_features()},"delta_pnl":delta_call_put})
            exit_ts=norm_scalar_ts(arm["exit_ts"])
            future=np.flatnonzero(timeline.timestamp.to_numpy()==exit_ts)
            if len(future)==0: break
            cursor=int(future[0])+1

    tr=pd.DataFrame(trades)
    if tr.empty: raise RuntimeError("Sequential policy produced zero trades")
    tr["entry_ts"]=norm_ts(tr["entry_ts"]); tr["exit_ts"]=norm_ts(tr["exit_ts"])
    tr["period"]=np.where(tr.entry_ts<pd.Timestamp("2024-01-01",tz=TZ),"development",
                          np.where(tr.entry_ts<pd.Timestamp("2026-01-01",tz=TZ),"validation","holdout"))
    tr["cum_net"]=tr.policy_net_rupees.cumsum(); tr["peak"]=tr.cum_net.cummax(); tr["drawdown"]=tr.peak-tr.cum_net
    tr.to_csv(OUT/"sequential_trades.csv",index=False)
    control=pd.concat([DEV_CONTROL.assign(period="development"),FROZEN_CONTROL.assign(period=np.where(pd.to_datetime(FROZEN_CONTROL.expiry).dt.year<=2025,"validation","holdout"))],ignore_index=True)
    control["entry_ts"]=norm_ts(control.entry_ts); control["exit_ts"]=norm_ts(control.exit_ts)
    control["period"]=np.where(control.entry_ts<pd.Timestamp("2024-01-01",tz=TZ),"development",
                               np.where(control.entry_ts<pd.Timestamp("2026-01-01",tz=TZ),"validation","holdout"))
    # Compare complete calendar-period P&L, and common-expiry paired uplift.
    summaries=[]
    for period in ["development","validation","holdout"]:
        p=tr[tr.period==period]
        c=control[control.period==period]
        uplift=float(p.policy_net_rupees.sum()-c.net_rupees.sum())
        summaries.append({"period":period,"policy_trades":len(p),"policy_net_rupees":float(p.policy_net_rupees.sum()),
                          "control_trades":len(c),"control_net_rupees":float(c.net_rupees.sum()),
                          "uplift_rupees":uplift,"policy_win_rate":float((p.policy_net_rupees>0).mean()) if len(p) else np.nan,
                          "policy_max_drawdown_rupees":max_drawdown(p.policy_net_rupees)})
    sm=pd.DataFrame(summaries); sm.to_csv(OUT/"period_summary.csv",index=False)
    boot=paired_bootstrap(tr[tr.period=="validation"],control[control.period=="validation"])
    hold=paired_bootstrap(tr[tr.period=="holdout"],control[control.period=="holdout"])
    summary={"status":"COMPLETE","model":"Sparse_GAM_margin","margin":MARGIN,"uncertainty_z":UNCERTAINTY_Z,
             "warmup_policy_trades":WARMUP,"trades":len(tr),"overrides":int(tr.override.sum()),
             "validation_paired_expiry_bootstrap":boot,"holdout_paired_expiry_bootstrap":hold,
             "validation_uplift_rupees":float(sm.loc[sm.period=="validation","uplift_rupees"].iloc[0]),
             "holdout_uplift_rupees":float(sm.loc[sm.period=="holdout","uplift_rupees"].iloc[0]),
             "fixed_opportunity_step3_result_used":"Sparse_GAM_margin / margin 500 / z 1.0",
             "promotion_status":"PENDING_FULL_ENGINE_AUDIT"}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str))
    (OUT/"status.json").write_text(json.dumps(summary,indent=2,default=str))
    print(json.dumps(summary,indent=2,default=str))
    print(sm.to_string(index=False))

if __name__=="__main__": main()
