import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from research.payoff_boundary_stop_research import TZ, load_trade_ledgers, build_boundary_metadata, load_spot, load_candidate_paths, net_at

OUT=Path(os.getenv("OUT_DIR","results/dynamic_n_corrected/phase30_entry_delta_proportion_exit"))
OUT.mkdir(parents=True,exist_ok=True)
TRAIN_END=pd.Timestamp("2023-12-31",tz=TZ); VALIDATION_END=pd.Timestamp("2025-12-31",tz=TZ); HOLDOUT_START=pd.Timestamp("2026-01-01",tz=TZ)
THRESHOLDS=[0.05,0.10,0.15,0.20,0.25,0.30,0.40,0.50,0.60]; CONFIRMS=[1,3]

def norm_cdf(x):
    x=np.asarray(x,float); ax=np.abs(x); t=1/(1+0.2316419*ax)
    poly=((((1.330274429*t-1.821255978)*t+1.781477937)*t-0.356563782)*t+0.319381530)*t
    pdf=np.exp(-0.5*ax*ax)/np.sqrt(2*np.pi); cdf=1-pdf*poly
    return np.where(x>=0,cdf,1-cdf)
def bs_price(S,K,T,sig,typ):
    T=np.maximum(T,1e-10); sig=np.maximum(sig,1e-8); d1=(np.log(S/K)+.5*sig*sig*T)/(sig*np.sqrt(T)); d2=d1-sig*np.sqrt(T)
    return S*norm_cdf(d1)-K*norm_cdf(d2) if typ=="CE" else K*norm_cdf(-d2)-S*norm_cdf(-d1)
def bs_delta(S,K,T,sig,typ):
    T=np.maximum(T,1e-10); sig=np.maximum(sig,1e-8); d1=(np.log(S/K)+.5*sig*sig*T)/(sig*np.sqrt(T)); nd=norm_cdf(d1)
    return nd if typ=="CE" else nd-1
def implied_delta(price,S,K,T,typ):
    price=np.asarray(price,float); S=np.asarray(S,float); T=np.asarray(T,float); intrinsic=np.maximum(S-K,0) if typ=="CE" else np.maximum(K-S,0)
    valid=np.isfinite(price)&np.isfinite(S)&np.isfinite(T)&(T>0)&(S>0)&(price>=intrinsic-1e-7)&(price>1e-8); out=np.full(price.shape,np.nan)
    if not valid.any(): return out
    idx=np.where(valid)[0]; p=price[idx]; s=S[idx]; t=T[idx]; lo=np.full_like(p,1e-5); hi=np.full_like(p,5.0); x=np.full_like(p,.30)
    for _ in range(12):
        d1=(np.log(s/K)+.5*x*x*t)/(x*np.sqrt(t)); px=bs_price(s,K,t,x,typ); v=s*np.exp(-.5*d1*d1)/np.sqrt(2*np.pi)*np.sqrt(t)
        xn=np.clip(x-(px-p)/np.maximum(v,1e-10),lo,hi); bad=~np.isfinite(xn)|(v<1e-10); xn[bad]=(lo[bad]+hi[bad])/2
        pxn=bs_price(s,K,t,xn,typ); low=pxn<p; lo=np.where(low,xn,lo); hi=np.where(low,hi,xn); x=xn
    residual=np.abs(bs_price(s,K,t,x,typ)-p); good=residual<=.02; out[idx[good]]=bs_delta(s[good],K,t[good],x[good],typ); return out
def add_deltas(meta,paths):
    rows=[]; errors=[]
    for e in meta.itertuples():
        path=paths.get(e.expiry,[])
        if not path: continue
        expiry_ts=pd.Timestamp(e.expiry,tz=TZ)+pd.Timedelta(hours=15,minutes=30); ts=pd.to_datetime([p["ts"] for p in path])
        T=np.maximum((expiry_ts-ts).total_seconds()/31557600.0,1e-10); S=np.asarray([p["spot"] for p in path],float); vals=[]
        # Entry reference is reconstructed at the actual buy timestamp, not from the first post-entry minute.
        entry_T=max((expiry_ts-pd.Timestamp(e.entry_ts)).total_seconds()/31557600.0,1e-10)
        entry_S=float(e.spot_entry)
        entry_short=[]
        for K,px in [(e.k_n1,e.raw_entry[1]),(e.k_n2,e.raw_entry[2])]:
            ed=implied_delta(np.asarray([float(px)]),np.asarray([entry_S]),float(K),np.asarray([entry_T]),e.option_type)[0]
            entry_short.append(ed)
        entry_combined=abs(entry_short[0])+abs(entry_short[1]) if all(np.isfinite(entry_short)) else np.nan
        for j,K in enumerate([e.k_n,e.k_n1,e.k_n2]):
            vals.append(implied_delta(np.asarray([p["raw_exit"][j] for p in path],float),S,float(K),T,e.option_type))
        valid=np.isfinite(vals[0])&np.isfinite(vals[1])&np.isfinite(vals[2])
        for i,p in enumerate(path):
            d1,d2=vals[1][i],vals[2][i]; comb=abs(d1)+abs(d2) if np.isfinite(d1+d2) else np.nan
            rows.append({"expiry":e.expiry,"ts":p["ts"],"direction":e.direction,"option_type":e.option_type,"spot":p["spot"],"gross":p["gross"],"mfe":p["mfe"],"target":e.target,"raw_exit":p["raw_exit"],"short1_delta":d1,"short2_delta":d2,"short1_abs_delta":abs(d1) if np.isfinite(d1) else np.nan,"short2_abs_delta":abs(d2) if np.isfinite(d2) else np.nan,"combined_short_abs_delta":comb,"entry_combined_short_abs_delta":entry_combined,"delta_valid":bool(valid[i])})
        if not valid.any(): errors.append({"expiry":e.expiry,"error":"no valid combined short-leg delta observations"})
    return pd.DataFrame(rows),pd.DataFrame(errors)
def split(df):
    exp=pd.to_datetime(df.expiry).dt.tz_localize(TZ); return df[exp<=TRAIN_END].copy(),df[(exp>TRAIN_END)&(exp<=VALIDATION_END)].copy(),df[exp>=HOLDOUT_START].copy()
def max_dd(vals):
    s=peak=dd=0.
    for v in vals: s+=float(v); peak=max(peak,s); dd=max(dd,peak-s)
    return dd
def summary(df):
    return {"trades":len(df),"base_net":df.base_net.sum(),"candidate_net":df.candidate_net.sum(),"net_uplift":df.net_uplift.sum(),"winner_affected":int(df.winner_affected.sum()),"changed":int(df.changed_before_base.sum()),"base_dd":max_dd(df.base_net),"candidate_dd":max_dd(df.candidate_net),"win_rate":float((df.candidate_net>0).mean()) if len(df) else np.nan}
def apply_rule(meta,paths,target,stop,confirm):
    out=[]
    for e in meta.itertuples():
        path=paths.get(e.expiry,[]); base=e.base_net
        entry=path[0].get("entry_combined_short_abs_delta",np.nan) if path else np.nan
        sig=np.array([p.get("combined_short_abs_delta",np.nan) for p in path],float)/entry-1 if np.isfinite(entry) and entry>0 else np.full(len(path),np.nan)
        hit=None
        for i in range(confirm-1,len(path)):
            idx0=i-confirm+1
            if not all((pd.Timestamp(path[j]["ts"])-pd.Timestamp(path[j-1]["ts"])).total_seconds()==60 for j in range(idx0+1,i+1)): continue
            if all(np.isfinite(sig[j]) and sig[j]<=-target for j in range(idx0,i+1)): hit=(idx0,"DELTA_PROP_TARGET"); break
            if all(np.isfinite(sig[j]) and sig[j]>=stop for j in range(idx0,i+1)): hit=(idx0,"DELTA_PROP_STOP"); break
        if hit: p=path[hit[0]]; cand=net_at(e,p); ts=p["ts"]; reason=hit[1]
        else: cand=base; ts=e.exit_ts; reason="EXPIRY_FALLBACK"
        changed=pd.Timestamp(ts)<pd.Timestamp(e.exit_ts)
        out.append({"expiry":e.expiry,"base_net":base,"candidate_net":cand,"net_uplift":cand-base,"winner_affected":bool(base>0 and changed),"changed_before_base":changed,"exit_reason":reason,"exit_ts":ts,"entry_short_delta":entry})
    return pd.DataFrame(out)
def main():
    meta=build_boundary_metadata(load_trade_ledgers()); raw_paths,path_errors=load_candidate_paths(meta,load_spot()); panel,delta_errors=add_deltas(meta,raw_paths)
    coverage=float(panel.delta_valid.mean()) if len(panel) else 0.; print(f"Phase30: {len(meta)} trades; delta coverage={coverage:.4%}",flush=True)
    panel.to_csv(OUT/"minute_combined_short_delta_panel.csv",index=False); delta_errors.to_csv(OUT/"delta_errors.csv",index=False); pd.DataFrame(path_errors).to_csv(OUT/"path_errors.csv",index=False)
    if coverage<.95: raise RuntimeError(f"Delta coverage below 95%: {coverage:.4f}")
    paths={e:g.sort_values("ts").to_dict("records") for e,g in panel.groupby("expiry",sort=False)}; rules=[]; details={}
    for t in THRESHOLDS:
        for s in THRESHOLDS:
            for c in CONFIRMS:
                name=f"target{t:.2f}_stop{s:.2f}_c{c}"; df=apply_rule(meta,paths,t,s,c); details[name]=df; rules.append({"name":name,"target":t,"stop":s,"confirm":c,**summary(df)})
    grid=pd.DataFrame(rules); grid.to_csv(OUT/"entry_delta_proportion_grid.csv",index=False)
    train=[]
    for r in rules: train.append({**r,**summary(split(details[r["name"]])[0])})
    train_df=pd.DataFrame(train); train_df.to_csv(OUT/"entry_delta_proportion_training_grid.csv",index=False)
    sel=train_df.sort_values(["net_uplift","candidate_dd"],ascending=[False,True]).iloc[0].to_dict(); selected=details[sel["name"]]; tr,va,ho=split(selected)
    wf=pd.DataFrame([{"period":"training",**summary(tr)},{"period":"validation",**summary(va)},{"period":"holdout",**summary(ho)},{"period":"full",**summary(selected)}]); wf.to_csv(OUT/"selected_entry_delta_proportion_walkforward.csv",index=False); selected.to_csv(OUT/"selected_entry_delta_proportion_trade_level.csv",index=False)
    phase20={"training":62905.98,"validation":75809.78,"holdout":10413.76,"full":149129.53}; ours={"training":summary(tr)["candidate_net"],"validation":summary(va)["candidate_net"],"holdout":summary(ho)["candidate_net"],"full":summary(selected)["candidate_net"]}
    comp=pd.DataFrame([{"period":k,"phase20_net":phase20[k],"phase30_net":ours[k],"difference":ours[k]-phase20[k]} for k in phase20]); comp.to_csv(OUT/"phase20_canonical_comparison.csv",index=False)
    promote=(comp.loc[comp.period=="validation","difference"].iloc[0]>0 and comp.loc[comp.period=="holdout","difference"].iloc[0]>0 and summary(va)["candidate_dd"]<=1.05*summary(va)["base_dd"] and summary(ho)["candidate_dd"]<=1.05*summary(ho)["base_dd"])
    rng=np.random.default_rng(20261005); boot=[]
    for period,df in [("validation",va),("holdout",ho),("full",selected)]:
        vals=df.net_uplift.to_numpy(float); sims=np.array([rng.choice(vals,len(vals),replace=True).mean() for _ in range(5000)]); boot.append({"period":period,"mean_uplift":vals.mean(),"ci95_low":np.quantile(sims,.025),"ci95_high":np.quantile(sims,.975)})
    pd.DataFrame(boot).to_csv(OUT/"bootstrap_uplift_ci.csv",index=False)
    pd.DataFrame([{"selected_rule":sel["name"],"delta_coverage":coverage,"promotion":promote,"validation_vs_phase20":comp.loc[comp.period=="validation","difference"].iloc[0],"holdout_vs_phase20":comp.loc[comp.period=="holdout","difference"].iloc[0]}]).to_csv(OUT/"phase30_status.csv",index=False)
    report=f"""# Phase 30
# Execution revision: path-filter trigger only; research parameters unchanged Conclusion — Entry-Referenced Combined Short-Leg Delta Proportion

**Selected rule:** {sel["name"]}

The tested variable is the proportional change from entry of the sum of the two short-leg delta magnitudes. There is no prior-minute lookback, no delta-difference measure, and no mean of the two short legs.

Delta coverage: {coverage:.2%}

{wf.to_string(index=False)}

## Canonical Phase-20 comparison
{comp.to_string(index=False)}

**Promotion decision: {"PROMOTE" if promote else "REJECT"}.**
"""
    (OUT/"PHASE30_CONCLUSION.md").write_text(report,encoding="utf-8"); print(report,flush=True)
if __name__=="__main__": main()
