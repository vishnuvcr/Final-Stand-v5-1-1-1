import json, os
from pathlib import Path
import numpy as np
import pandas as pd

import phase39_sequential_policy as p39
import phase41_sequential_replay as p41s
from phase39_counterfactual_engine import nearest_delta_strike, run_arm

ROOT=Path(".")
OUT=ROOT/"results/phase42_rank_policy"
SEL=OUT/"selection.json"
CONTROL_DEV=Path("results/phase39_data/development_control_trades_2021_2023.csv")
CONTROL_FROZEN=Path("results/phase39_data/frozen_control_trades_2024_2026-06-30.csv")
FOCUS_FEATURES=p41s.FOCUS_FEATURES
TZ=p39.TZ
WARMUP=100
WIDTH=50.0
BOOT=10000
RANK_Q={"TOP_5":0.95,"TOP_10":0.90,"TOP_20":0.80}

def load_vix(): return p41s.load_vix()
def prior_vix(v,ts): return p41s.prior_vix(v,ts)
def enrich(*args,**kwargs): return p41s.enrich_row(*args,**kwargs)
def model(): return p41s.model("SPLINE_RIDGE_VIX")
def Xify(fr): return p41s.Xify(fr)
def shadow_direction(control,ts): return p41s.shadow_direction(control,ts)

def maxdd(x):
    a=np.asarray(x,float)
    if len(a)==0:return 0.0
    eq=np.cumsum(a); pk=np.maximum.accumulate(np.r_[0.0,eq])
    return float((pk[1:]-eq).max())

def boot(policy,control,seed):
    p=policy.groupby("expiry")["policy_net_rupees"].sum()
    c=control.groupby("expiry")["net_rupees"].sum()
    keys=p.index.intersection(c.index)
    d=np.asarray([p[k]-c[k] for k in keys],float)
    if len(d)==0:return {"n":0}
    rng=np.random.default_rng(seed); idx=rng.integers(0,len(d),size=(BOOT,len(d)))
    means=d[idx].mean(axis=1); signs=rng.choice([-1,1],size=(BOOT,len(d))); null=(d*signs).mean(axis=1)
    obs=float(d.mean())
    return {"n":int(len(d)),"mean":obs,"total":float(d.sum()),
            "ci_lo":float(np.quantile(means,.025)),"ci_hi":float(np.quantile(means,.975)),
            "total_ci_lo":float(np.quantile(means*len(d),.025)),
            "total_ci_hi":float(np.quantile(means*len(d),.975)),
            "p_one_sided":float((np.sum(null>=obs)+1)/(BOOT+1)),
            "positive_expiry_share":float(np.mean(d>0))}

def cost_stress(a,c,m):
    if not {"gross_rupees","cost_rupees"}.issubset(a.columns)|not {"gross_rupees","cost_rupees"}.issubset(c.columns):
        return float("nan")
    return float((a.gross_rupees.sum()-m*a.cost_rupees.sum())-(c.gross_rupees.sum()-m*c.cost_rupees.sum()))

def identity_proven(rank):
    f=pd.read_csv(OUT/"frozen_top3_fixed_results.csv")
    s=f[(f.get("rank")==rank)&(f["split"].isin(["development","validation","holdout"]))]
    return len(s)==3 and int(s["overrides"].sum())==0

def run_candidate(cand,spot,daily,global_d,flows,sentiment,vix,expected_all,control,rank):
    cutoff=str(cand["rank_cutoff"]); gate=str(cand["gate"]); q=RANK_Q[cutoff]
    if identity_proven(rank):
        t=control.copy()
        t["action"]=t["direction"].astype(str); t["shadow_control"]=t["direction"].astype(str)
        t["override"]=False;t["pred_delta"]=np.nan;t["rank_score"]=np.nan;t["rank_threshold"]=np.nan;t["rank_percentile"]=np.nan
        t["policy_net_rupees"]=t["net_rupees"].astype(float);t["gross_rupees"]=pd.to_numeric(t["gross_rupees"],errors="coerce")
        t["cost_rupees"]=pd.to_numeric(t["cost_rupees"],errors="coerce");t["lot_size"]=pd.to_numeric(t["lot_size"],errors="coerce")
        return t

    high_thr=float(vix.loc[vix.date<pd.Timestamp("2024-01-01"),"close"].quantile(.67))
    history=[];score_hist=[];trades=[]
    option_cache={}
    api_files=None
    def get_option(e):
        if e not in option_cache:
            d=p39.load_option(e);d["expiry_ts"]=e+pd.Timedelta(hours=15,minutes=30);option_cache[e]=d
        return option_cache[e]
    for expiry in expected_all:
        od=get_option(expiry);expiry_day=expiry.normalize();end_ts=expiry+pd.Timedelta(hours=15,minutes=29)
        idx_exp=expected_all.index(expiry);window_start=(expected_all[idx_exp-1]+pd.Timedelta(hours=15,minutes=30)) if idx_exp>0 else p39.START
        timeline=spot[(spot.timestamp>window_start)&(spot.timestamp<=end_ts)].copy()
        timeline=timeline[timeline.timestamp<expiry_day].sort_values("timestamp").reset_index(drop=True)
        cursor=0
        while cursor<len(timeline):
            entry=p39.norm_scalar_ts(timeline.iloc[cursor].timestamp)
            if entry.normalize()==expiry_day:break
            if entry.hour<9 or (entry.hour==9 and entry.minute<20) or entry.hour>15 or (entry.hour==15 and entry.minute>=28):
                cursor+=1;continue
            snap=od[od.timestamp==entry];sr=spot[spot.timestamp==entry]
            if snap.empty or sr.empty:cursor+=1;continue
            s=float(sr.iloc[0]["close"]);shadow=shadow_direction(control,entry)
            fr=enrich(entry,expiry,snap,s,spot,daily,global_d,flows,sentiment,option_cache,expected_all,vix,high_thr,0.0)
            # rising threshold is not needed for Phase-42 gates
            pred=np.nan;score=np.nan;threshold=np.nan;percentile=np.nan;override=False
            if len(history)>=WARMUP:
                hist=pd.DataFrame(history);m=model();m.fit(Xify(hist),hist["delta_pnl"].to_numpy(float))
                pred=float(m.predict(Xify(pd.DataFrame([fr])))[0])
                score=(-pred) if shadow=="CALL" else pred
                finite=np.asarray(score_hist,float);finite=finite[np.isfinite(finite)]
                if len(finite)>=WARMUP and np.isfinite(score):
                    threshold=float(np.quantile(finite,q));percentile=float((finite<=score).mean())
                    gate_ok=(gate=="ALL") or (gate=="HIGH_VIX" and bool(fr["india_vix_high"]))
                    override=bool(score>0 and score>=threshold and gate_ok)
            action=("PUT" if shadow=="CALL" else "CALL") if override else shadow
            typ="CE" if action=="CALL" else "PE";tgt=0.25 if typ=="CE" else -0.25
            chosen=nearest_delta_strike(snap,s,entry,typ,tgt)
            if chosen is None:cursor+=1;continue
            sk,_=chosen;lk=sk+WIDTH if typ=="CE" else sk-WIDTH
            arm=run_arm(od,spot,entry,expiry,typ,sk,lk,p39.lot_size_for_expiry(expiry))
            at="PE" if typ=="CE" else "CE";atgt=-0.25 if at=="PE" else 0.25
            alt_sel=nearest_delta_strike(snap,s,entry,at,atgt)
            if alt_sel is None:cursor+=1;continue
            ask,_=alt_sel;alk=ask-WIDTH if at=="PE" else ask+WIDTH
            alt=run_arm(od,spot,entry,expiry,at,ask,alk,p39.lot_size_for_expiry(expiry))
            delta=float(arm["net_rupees"]-alt["net_rupees"])
            if action=="PUT":delta=-delta
            trades.append({"entry_ts":str(entry),"expiry":str(expiry.date()),"shadow_control":shadow,"action":action,
                           "override":bool(override),"pred_delta":pred,"rank_score":score,"rank_threshold":threshold,"rank_percentile":percentile,
                           "policy_net_rupees":float(arm["net_rupees"]),"gross_rupees":float(arm["gross_rupees"]),
                           "cost_rupees":float(arm["cost_rupees"]),"call_put_delta":float(delta),
                           "exit_ts":str(arm["exit_ts"]),"exit_reason":arm["exit_reason"],"lot_size":int(p39.lot_size_for_expiry(expiry))})
            hrow={k:fr.get(k,np.nan) for k in FOCUS_FEATURES}
            hrow.update({"india_vix_level":fr.get("india_vix_level",np.nan),"india_vix_ret1":fr.get("india_vix_ret1",np.nan),
                         "india_vix_high":fr.get("india_vix_high",0),"india_vix_rising":fr.get("india_vix_rising",0),
                         "india_vix_high_rising":fr.get("india_vix_high_rising",0),
                         "delta_pnl":float(arm["net_rupees"]-alt["net_rupees"])})
            history.append(hrow)
            if np.isfinite(score):score_hist.append(float(score))
            nxt=np.flatnonzero(timeline.timestamp.to_numpy()==p39.norm_scalar_ts(arm["exit_ts"]))
            if len(nxt)==0:break
            cursor=int(nxt[0])+1
    t=pd.DataFrame(trades)
    if t.empty:raise RuntimeError("candidate produced zero trades")
    t["entry_ts"]=p39.norm_ts(t["entry_ts"]);t["exit_ts"]=p39.norm_ts(t["exit_ts"])
    t["expiry_dt"]=pd.to_datetime(t.expiry).dt.tz_localize(TZ)
    t["period"]=np.where(t.expiry_dt.dt.year<=2023,"development",np.where(t.expiry_dt.dt.year<=2025,"validation","holdout"))
    return t

def main():
    sel=json.load(open(SEL));cands=sel["top3_frozen_before_holdout"]
    vix=load_vix();spot=p39.load_spot();daily=p39.load_daily_source("nifty_daily.parquet")
    global_d=p39.load_daily_source("global_daily.parquet");flows=p39.load_daily_source("fii_dii_daily.parquet");sentiment=p39.load_daily_source("sentiment_daily.parquet")
    expected=p39.expected_expiries(spot)
    from huggingface_hub import HfApi
    api=HfApi(token=os.getenv("HF_TOKEN") or None);repo_files=set(api.list_repo_files(p39.HF_REPO,repo_type="dataset"))
    expected=[e for e in expected if f"options/NIFTY/{e.strftime('%Y-%m-%d')}.parquet" in repo_files]
    control=pd.concat([pd.read_csv(CONTROL_DEV).assign(period="development"),pd.read_csv(CONTROL_FROZEN)],ignore_index=True)
    control["entry_ts"]=p39.norm_ts(control["entry_ts"]);control["expiry_dt"]=pd.to_datetime(control.expiry).dt.tz_localize(TZ)
    control["period"]=np.where(control.expiry_dt.dt.year<=2023,"development",np.where(control.expiry_dt.dt.year<=2025,"validation","holdout"))
    out=[]
    for rank,cand in enumerate(cands,1):
        print(f"Running frozen candidate rank {rank}: {cand}",flush=True)
        t=run_candidate(cand,spot,daily,global_d,flows,sentiment,vix,expected,control,rank)
        t.to_csv(OUT/f"sequential_candidate_{rank}.csv",index=False)
        for per in ["development","validation","holdout"]:
            a=t[t.period==per];c=control[control.period==per];b=boot(a,c,52000+rank)
            rr={"rank":rank,"rank_cutoff":cand["rank_cutoff"],"gate":cand["gate"],"period":per,
                "policy_trades":len(a),"control_trades":len(c),"policy_net_rupees":float(a.policy_net_rupees.sum()),
                "control_net_rupees":float(c.net_rupees.sum()),"uplift_rupees":float(a.policy_net_rupees.sum()-c.net_rupees.sum()),
                "overrides":int(a.override.sum()),"override_rate":float(a.override.mean()) if len(a) else 0.0,
                "policy_dd":maxdd(a.policy_net_rupees),"control_dd":maxdd(c.net_rupees)}
            rr.update({f"boot_{k}":v for k,v in b.items()})
            for m in [1.25,1.5,2.0]:rr[f"cost_stress_{int(m*100)}pct_uplift"]=cost_stress(a,c,m)
            out.append(rr)
    s=pd.DataFrame(out);s.to_csv(OUT/"sequential_summary.csv",index=False)
    (OUT/"sequential_summary.json").write_text(json.dumps({"status":"SEQUENTIAL_COMPLETE","candidates":cands},indent=2,default=str))
    (ROOT/"PHASE42_STATUS.md").write_text("# Phase 42 Status — Rank-to-Action Selective Policy\n\n**STEP 2 COMPLETE — EXACT SEQUENTIAL REPLAY FINISHED**\n\nFinal closeout next.\n")
    print(s.to_string(index=False))

if __name__=="__main__":main()
