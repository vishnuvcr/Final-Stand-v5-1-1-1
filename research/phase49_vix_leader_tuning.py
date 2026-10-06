import json, os, itertools, hashlib
from pathlib import Path
import numpy as np
import pandas as pd

from research.phase43_vix_strategy_sweep import (
    TZ, START, END, DEV_END, VAL_END,
    load_parquet, load_vix, vix_state, active_states, modal_step,
    evaluate, lot_size_for_expiry
)

OUT=Path("results/phase49_vix_tuning"); OUT.mkdir(parents=True,exist_ok=True)
STATES=["LOW","NORMAL"]
TIMES=[(9,30),(10,0),(10,30),(11,0)]
DTES=[3,4,5]

def expiries():
    p=Path("results/phase43_vix/strategy_trade_matrix_all_splits.csv")
    return sorted(set(pd.to_datetime(pd.read_csv(p,usecols=["expiry"]).expiry).dt.tz_localize(TZ)))

def grid():
    g=[]
    for s,w,t,d in itertools.product([1,2,3,4],[1,2,3,4],TIMES,DTES):
        g.append(dict(family="bear_call",short_offset=s,width=w,long_offset=s+w,entry_h=t[0],entry_m=t[1],dte=d))
    for l,w,t,d in itertools.product([0,1,2],[1,2,3,4],TIMES,DTES):
        g.append(dict(family="bear_put",long_offset=l,width=w,short_offset=l-w,entry_h=t[0],entry_m=t[1],dte=d))
    for b,u,lo,t,d in itertools.product([0,1],[1,2,3,4],[1,2,3,4],TIMES,DTES):
        g.append(dict(family="put_bwb",body=b,upper=u,lower=lo,entry_h=t[0],entry_m=t[1],dte=d))
    return g
GRID=grid()

def baseline(f):
    return (dict(family=f,short_offset=1,width=2,long_offset=3,entry_h=10,entry_m=0,dte=4) if f=="bear_call"
            else dict(family=f,long_offset=0,width=1,short_offset=-1,entry_h=10,entry_m=0,dte=4) if f=="bear_put"
            else dict(family=f,body=0,upper=2,lower=1,entry_h=10,entry_m=0,dte=4))

def legs(c):
    if c["family"]=="bear_call": return [("cur","CE",c["short_offset"],-1),("cur","CE",c["long_offset"],1)]
    if c["family"]=="bear_put": return [("cur","PE",c["long_offset"],1),("cur","PE",c["short_offset"],-1)]
    return [("cur","PE",c["body"]+c["upper"],1),("cur","PE",c["body"],-2),("cur","PE",c["body"]-c["lower"],1)]

def entry_ts(index,expiry,dte,h,m):
    days=sorted(index.timestamp.dt.normalize().unique())
    prior=[x for x in days if x<expiry.normalize()]
    if len(prior)<dte:return None
    return prior[-dte]+pd.Timedelta(hours=h,minutes=m)

def key(c): return json.dumps(c,sort_keys=True,separators=(",",":"))

def one(index,vix,expiry,data,c):
    ts=entry_ts(index,expiry,c["dte"],c["entry_h"],c["entry_m"])
    if ts is None:return None
    sr=index[index.timestamp==ts]
    if sr.empty:return None
    vs=vix_state(vix,ts)
    if vs is None:return None
    snap=data[data.timestamp==ts]; step=modal_step(snap)
    if step is None:return None
    spot=float(sr.iloc[-1].spot)
    atm=float(min(snap.strike.unique(),key=lambda k:abs(float(k)-spot)))
    r=evaluate(c["family"],legs(c),data,data,ts,expiry,atm,step,lot_size_for_expiry(expiry))
    if r is None:return None
    return dict(expiry=str(expiry.date()),entry_ts=str(ts),year=ts.year,family=c["family"],
                param_json=key(c),state=vs["level_state"],net=r["net_rupees"],net50=r["net_plus50_cost_rupees"],
                exit_ts=r["exit_ts"])

def annual(g):
    out={}
    g=g.copy(); g["year"]=pd.to_datetime(g.entry_ts).dt.year
    for y,z in g.groupby("year"):
        a=z.net.to_numpy(float); s=z.net50.to_numpy(float); pos=a[a>0].sum(); neg=-a[a<0].sum()
        out[int(y)]=dict(trades=len(z),net=a.sum(),net50=s.sum(),mean_net=a.mean(),mean_net50=s.mean(),
                         pf=pos/neg if neg>0 else np.inf)
    return out

def neighborhood(sel):
    def near(a,b):
        if a["family"]!=b["family"]: return False
        ks=["short_offset","width","entry_h","entry_m","dte"] if a["family"]=="bear_call" else ["long_offset","width","entry_h","entry_m","dte"] if a["family"]=="bear_put" else ["body","upper","lower","entry_h","entry_m","dte"]
        return sum(a[k]!=b[k] for k in ks)==1
    vals=[]
    for _,r in sel.iterrows():
        a=json.loads(r.param_json); n=0
        for _,q in sel[(sel.family==r.family)&(sel.state==r.state)].iterrows():
            b=json.loads(q.param_json)
            if near(a,b) and q.med_net50>0.8*r.med_net50:n+=1
        vals.append(n)
    out=sel.copy(); out["neighbor_support"]=vals; return out

def choose(tr):
    rows=[]
    for (f,s,pj),g in tr.groupby(["family","state","param_json"]):
        m=annual(g)
        if not all(y in m for y in [2021,2022,2023]):continue
        if any(m[y]["trades"]<6 or m[y]["mean_net"]<=0 or m[y]["mean_net50"]<=0 for y in [2021,2022,2023]):continue
        rows.append(dict(family=f,state=s,param_json=pj,trades_dev=len(g),
                         med_net50=float(np.median([m[y]["mean_net50"] for y in [2021,2022,2023]])),
                         avg_net50=float(np.mean([m[y]["mean_net50"] for y in [2021,2022,2023]])),
                         med_pf=float(np.median([m[y]["pf"] for y in [2021,2022,2023] if np.isfinite(m[y]["pf"])]))))
    return neighborhood(pd.DataFrame(rows))

def boot(a,b,seed):
    if len(a)<5 or len(b)<5:return (np.nan,np.nan,np.nan,np.nan)
    rng=np.random.default_rng(seed); a=np.asarray(a,float); b=np.asarray(b,float)
    ia=rng.integers(0,len(a),(10000,len(a))); ib=rng.integers(0,len(b),(10000,len(b)))
    d=a[ia].mean(1)-b[ib].mean(1); obs=a.mean()-b.mean(); pooled=np.r_[a,b]; n=len(a); pp=[]
    for _ in range(10000):
        p=rng.permutation(pooled); pp.append(p[:n].mean()-p[n:].mean())
    return float(obs),float(np.quantile(d,.025)),float(np.quantile(d,.975)),float(np.mean(np.array(pp)>=obs))

def holm(p):
    p=np.asarray(p,float); o=np.argsort(np.nan_to_num(p,nan=1.0)); out=np.ones(len(p)); r=0
    for k,i in enumerate(o): r=max(r,min(1,(len(p)-k)*(p[i] if np.isfinite(p[i]) else 1))); out[i]=r
    return out

def preflight():
    assert len(GRID)==720
    assert legs(baseline("bear_call"))==[("cur","CE",1,-1),("cur","CE",3,1)]
    assert legs(baseline("bear_put"))==[("cur","PE",0,1),("cur","PE",-1,-1)]
    assert legs(baseline("put_bwb"))==[("cur","PE",2,1),("cur","PE",0,-2),("cur","PE",-1,1)]
    es=expiries(); assert len(es)>=100
    return {"grid":len(GRID),"expiries":len(es),"dev":sum(e<=DEV_END for e in es),
            "validation":sum(DEV_END<e<=VAL_END for e in es),"holdout":sum(e>VAL_END for e in es)}

def main():
    pf=preflight(); (OUT/"preflight.json").write_text(json.dumps(pf,indent=2))
    if os.getenv("PHASE49_PREFLIGHT_ONLY")=="1": print(json.dumps(pf,indent=2)); return
    index=__import__("research.phase43_vix_strategy_sweep",fromlist=["load_index"]).load_index()
    vix=load_vix(); es=[e for e in expiries() if START<=e<=END]
    rows=[]; errs=[]
    for i,e in enumerate(es):
        if e>DEV_END: break
        try:
            data=load_parquet(f"options/NIFTY/{e.strftime('%Y-%m-%d')}.parquet")
            for c in GRID:
                r=one(index,vix,e,data,c)
                if r and r["state"] in STATES: rows.append(r)
        except Exception as ex: errs.append({"expiry":str(e.date()),"error":repr(ex)})
        if i%10==0: pd.DataFrame(rows).to_csv(OUT/"progress_development.csv",index=False)
    tr=pd.DataFrame(rows); assert not tr.empty
    tr.to_csv(OUT/"development_parameter_trade_matrix.csv",index=False); pd.DataFrame(errs).to_csv(OUT/"data_errors.csv",index=False)
    sel=choose(tr); sel.to_csv(OUT/"development_candidate_scores.csv",index=False)
    frozen=[]
    for f,s in itertools.product(FAMILIES,STATES):
        q=sel[(sel.family==f)&(sel.state==s)].sort_values(["med_net50","neighbor_support","avg_net50","med_pf"],ascending=False)
        if len(q): frozen.append(q.iloc[0].to_dict())
    fr=pd.DataFrame(frozen); fr.to_csv(OUT/"development_frozen_parameters.csv",index=False)

    index=__import__("research.phase43_vix_strategy_sweep",fromlist=["load_index"]).load_index()
    fmap={(r.family,r.state):json.loads(r.param_json) for _,r in fr.iterrows()}
    val=[]; hold=[]; base=[]
    for e in es:
        if e<=DEV_END: continue
        try:
            data=load_parquet(f"options/NIFTY/{e.strftime('%Y-%m-%d')}.parquet")
            for (f,s),c in fmap.items():
                r=one(index,vix,e,data,c)
                if not r or r["state"]!=s: continue
                (val if e<=VAL_END else hold).append(r)
                b=baseline(f); rb=one(index,vix,e,data,b)
                if rb and rb["state"]==s: base.append(rb)
        except Exception: pass
    val=pd.DataFrame(val); hold=pd.DataFrame(hold); base=pd.DataFrame(base)
    val.to_csv(OUT/"validation_frozen_trade_matrix.csv",index=False); hold.to_csv(OUT/"holdout_frozen_trade_matrix.csv",index=False); base.to_csv(OUT/"validation_baseline_trade_matrix.csv",index=False)
    rows2=[]
    for f,s in fmap:
        z=val[(val.family==f)&(val.state==s)]; b=base[(base.family==f)&(base.state==s)]
        a=z.net.to_numpy(float); rest=val[~((val.family==f)&(val.state==s))].net.to_numpy(float)
        diff,lo,hi,p=boot(a,rest,4901+sum(map(ord,f+s)))
        c={"family":f,"state":s,"trades":len(z),"net":float(z.net.sum()) if len(z) else 0,
           "net50":float(z.net50.sum()) if len(z) else 0,"mean_net":float(z.net.mean()) if len(z) else np.nan,
           "win_rate":float((a>0).mean()) if len(a) else np.nan,
           "active_vs_rest_mean":diff,"ci_lo":lo,"ci_hi":hi,"p":p}
        if len(b):
            m=z[["expiry","net","net50"]].merge(b[["expiry","net","net50"]],on="expiry",suffixes=("_t","_b"))
            c["paired_common"]=len(m); c["paired_uplift_net"]=float((m.net_t-m.net_b).sum()) if len(m) else np.nan; c["paired_uplift_net50"]=float((m.net50_t-m.net50_b).sum()) if len(m) else np.nan
        rows2.append(c)
    vs=pd.DataFrame(rows2); vs["p_holm"]=holm(vs.p.to_numpy()); vs.to_csv(OUT/"validation_confirmatory_summary.csv",index=False)
    hs=[]
    for r in vs.itertuples(index=False):
        if r.trades>=20 and r.net>0 and r.net50>0 and r.active_vs_rest_mean>0:
            z=hold[(hold.family==r.family)&(hold.state==r.state)]
            if len(z): hs.append({"family":r.family,"state":r.state,"trades":len(z),"net":float(z.net.sum()),"net50":float(z.net50.sum()),"mean_net":float(z.net.mean()),"win_rate":float((z.net>0).mean())})
    hc=pd.DataFrame(hs); hc.to_csv(OUT/"holdout_confirmation.csv",index=False)
    decision={"phase":49,"grid_total":len(GRID),"frozen":len(fr),"validation_rows":len(vs),
              "validation_economic_passes":int(((vs.trades>=20)&(vs.net>0)&(vs.net50>0)&(vs.active_vs_rest_mean>0)).sum()),
              "holm_survivors":int((vs.p_holm<0.05).sum()),"holdout_confirmations":len(hc)}
    (OUT/"summary.json").write_text(json.dumps(decision,indent=2))
    fr.to_csv(OUT/"frozen_parameter_details.csv",index=False)
    Path(OUT/"PHASE49_MANUSCRIPT.md").write_text("# Phase 49 Manuscript — VIX Leader Parameter Tuning\n\n"+json.dumps(decision,indent=2))
    print(json.dumps(decision,indent=2))

if __name__=="__main__": main()
