import os, sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from research.payoff_boundary_stop_research import (
    TZ, load_trade_ledgers, build_boundary_metadata, load_spot,
    load_candidate_paths, phase19_fixed_mfe50_stop, net_at
)

OUT = Path(os.getenv("OUT_DIR", "results/dynamic_n_corrected/phase29_delta_change_exit"))
OUT.mkdir(parents=True, exist_ok=True)
TRAIN_END = pd.Timestamp("2023-12-31", tz=TZ)
VALIDATION_END = pd.Timestamp("2025-12-31", tz=TZ)
HOLDOUT_START = pd.Timestamp("2026-01-01", tz=TZ)

LOOKBACKS = [1,3,5,10,15]
DELTA_CHANGES = [0.02,0.05,0.08,0.10,0.15,0.20]
CONFIRMS = [1,3]
MODES = ["S1","S2","MEAN","BOTH"]

def norm_cdf(x):
    x=np.asarray(x,float)
    ax=np.abs(x)
    t=1.0/(1.0+0.2316419*ax)
    poly=((((1.330274429*t-1.821255978)*t+1.781477937)*t-0.356563782)*t+0.319381530)*t
    pdf=np.exp(-0.5*ax*ax)/np.sqrt(2.0*np.pi)
    cdf=1.0-pdf*poly
    return np.where(x>=0,cdf,1.0-cdf)

def bs_price(S,K,T,sig,typ,r=0.0,q=0.0):
    T=np.maximum(T,1e-10); sig=np.maximum(sig,1e-8)
    d1=(np.log(S/K)+(r-q+0.5*sig*sig)*T)/(sig*np.sqrt(T))
    d2=d1-sig*np.sqrt(T)
    if typ=="CE":
        return S*np.exp(-q*T)*norm_cdf(d1)-K*np.exp(-r*T)*norm_cdf(d2)
    return K*np.exp(-r*T)*norm_cdf(-d2)-S*np.exp(-q*T)*norm_cdf(-d1)

def bs_delta(S,K,T,sig,typ,r=0.0,q=0.0):
    T=np.maximum(T,1e-10); sig=np.maximum(sig,1e-8)
    d1=(np.log(S/K)+(r-q+0.5*sig*sig)*T)/(sig*np.sqrt(T))
    nd=norm_cdf(d1)
    return nd if typ=="CE" else nd-1.0

def implied_vol_delta(price,S,K,T,typ):
    price=np.asarray(price,float); S=np.asarray(S,float); K=float(K); T=np.asarray(T,float)
    intrinsic=np.maximum(S-K,0.0) if typ=="CE" else np.maximum(K-S,0.0)
    valid=(np.isfinite(price)&np.isfinite(S)&np.isfinite(T)&(T>0)&(S>0)&(price>=intrinsic-1e-7)&(price>1e-8))
    sig=np.full(price.shape, np.nan)
    if not valid.any(): return sig
    idx=np.where(valid)[0]
    p=price[idx]; s=S[idx]; t=T[idx]
    lo=np.full_like(p,1e-5); hi=np.full_like(p,5.0)
    x=np.full_like(p,0.30)
    for _ in range(10):
        px=bs_price(s,K,t,x,typ)
        v=s*np.exp(-0.5*((np.log(s/K)+0.5*x*x*t)/(x*np.sqrt(t)))**2)/np.sqrt(2*np.pi)*np.sqrt(t)
        step=(px-p)/np.maximum(v,1e-10)
        xn=np.clip(x-step,lo,hi)
        bad=(~np.isfinite(xn))|(v<1e-10)
        xn[bad]=(lo[bad]+hi[bad])/2
        pxn=bs_price(s,K,t,xn,typ)
        too_low=pxn<p
        lo=np.where(too_low,xn,lo); hi=np.where(too_low,hi,xn)
        x=xn
    sig[idx]=x
    # Validate residual; retain only reasonable fits.
    residual=np.abs(bs_price(s,K,t,x,typ)-p)
    bad=residual>0.02
    sig[idx[bad]]=np.nan
    d=bs_delta(s,K,t,x,typ)
    out=np.full(price.shape,np.nan); out[idx]=d
    out[idx[bad]]=np.nan
    return out

def add_deltas(meta, paths):
    rows=[]; errors=[]
    for entry in meta.itertuples():
        path=paths.get(entry.expiry)
        if not path: continue
        expiry_ts=pd.Timestamp(entry.expiry, tz=TZ)+pd.Timedelta(hours=15,minutes=30)
        ts=pd.to_datetime([p["ts"] for p in path])
        T=np.maximum((expiry_ts-ts).total_seconds()/31557600.0,1e-10)
        S=np.asarray([p["spot"] for p in path],float)
        strikes=[entry.k_n,entry.k_n1,entry.k_n2]
        typ=entry.option_type
        leg=[]
        for j,K in enumerate(strikes):
            px=np.asarray([p["raw_exit"][j] for p in path],float)
            leg.append(implied_vol_delta(px,S,K,T,typ))
        valid=np.isfinite(leg[0]) & np.isfinite(leg[1]) & np.isfinite(leg[2])
        for i,p in enumerate(path):
            z=dict(p)
            vals=[float(x[i]) if np.isfinite(x[i]) else np.nan for x in leg]
            z["long_delta"]=vals[0]
            z["short1_delta"]=vals[1]
            z["short2_delta"]=vals[2]
            z["long_abs_delta"]=abs(vals[0]) if np.isfinite(vals[0]) else np.nan
            z["short1_abs_delta"]=abs(vals[1]) if np.isfinite(vals[1]) else np.nan
            z["short2_abs_delta"]=abs(vals[2]) if np.isfinite(vals[2]) else np.nan
            z["delta_valid"]=bool(valid[i])
            rows.append({
                "expiry":entry.expiry,"ts":z["ts"],"direction":entry.direction,
                "option_type":typ,"spot":z["spot"],"gross":z["gross"],
                "mfe":z["mfe"],"target":entry.target,"raw_exit":z["raw_exit"],
                "long_delta":z["long_delta"],"short1_delta":z["short1_delta"],
                "short2_delta":z["short2_delta"],"long_abs_delta":z["long_abs_delta"],
                "short1_abs_delta":z["short1_abs_delta"],"short2_abs_delta":z["short2_abs_delta"],
                "delta_valid":z["delta_valid"]
            })
        if not valid.any(): errors.append({"expiry":entry.expiry,"error":"no valid individual-leg delta observations"})
    return pd.DataFrame(rows), pd.DataFrame(errors)

def split(df):
    exp=pd.to_datetime(df["expiry"]).dt.tz_localize(TZ)
    return df[exp<=TRAIN_END].copy(), df[(exp>TRAIN_END)&(exp<=VALIDATION_END)].copy(), df[exp>=HOLDOUT_START].copy()

def baseline_rows(meta):
    b=meta.copy()
    b=b.rename(columns={"base_net":"candidate_net"})
    b["base_net"]=b["candidate_net"]; b["net_uplift"]=0.0
    b["changed_before_base"]=False; b["winner_affected"]=False
    return b

def delta_change(path, i, mode, lookback):
    if i < lookback: return np.nan
    cur1=path[i].get("short1_abs_delta",np.nan); cur2=path[i].get("short2_abs_delta",np.nan)
    old1=path[i-lookback].get("short1_abs_delta",np.nan); old2=path[i-lookback].get("short2_abs_delta",np.nan)
    if not all(np.isfinite([cur1,cur2,old1,old2])): return np.nan
    d1=cur1-old1; d2=cur2-old2
    return {"S1":d1,"S2":d2,"MEAN":(d1+d2)/2.0,"BOTH":min(d1,d2)}[mode]

def apply_rule(meta, paths, rule):
    out=[]
    for e in meta.itertuples():
        path=paths.get(e.expiry, []); control_net=e.base_net; control_ts=e.exit_ts; stop=None
        for i,p in enumerate(path):
            if not p.get("delta_valid"): continue
            ch=delta_change(path,i,rule["mode"],rule["lookback"])
            if not np.isfinite(ch): continue
            hit=(ch <= -rule["threshold"]) if rule["kind"]=="TARGET" else (ch >= rule["threshold"])
            if not hit: continue
            if rule["confirm"]==1: stop={"p":p,"reason":"DELTA_CHANGE_TARGET" if rule["kind"]=="TARGET" else "DELTA_CHANGE_STOP"}; break
            if i < rule["confirm"]-1: continue
            win=path[i-rule["confirm"]+1:i+1]
            exact=all((pd.Timestamp(win[j]["ts"])-pd.Timestamp(win[j-1]["ts"])).total_seconds()==60 for j in range(1,len(win)))
            vals=[delta_change(path,j,rule["mode"],rule["lookback"]) for j in range(i-rule["confirm"]+1,i+1)]
            ok=exact and all(np.isfinite(v) and ((v <= -rule["threshold"]) if rule["kind"]=="TARGET" else (v >= rule["threshold"])) for v in vals)
            if ok: stop={"p":win[0],"reason":"DELTA_CHANGE_TARGET" if rule["kind"]=="TARGET" else "DELTA_CHANGE_STOP"}; break
        if stop is None: cand=control_net; ts=control_ts; reason="EXPIRY_FALLBACK"
        else: cand=net_at(e,stop["p"]); ts=stop["p"]["ts"]; reason=stop["reason"]
        changed=pd.Timestamp(ts)<pd.Timestamp(control_ts)
        out.append({"expiry":e.expiry,"base_net":control_net,"candidate_net":cand,"net_uplift":cand-control_net,
                    "base_positive":control_net>0,"changed_before_base":changed,"winner_affected":bool(control_net>0 and changed),
                    "exit_reason":reason,"exit_ts":ts})
    return pd.DataFrame(out)


def summary(df):
    x=df.candidate_net
    base=df.base_net
    return {"trades":len(df),"base_net":base.sum(),"candidate_net":x.sum(),
            "net_uplift":df.net_uplift.sum(),"winner_affected":int(df.winner_affected.sum()),
            "stops":int(df.changed_before_base.sum()),"base_dd":max_dd(base),
            "candidate_dd":max_dd(x),"win_rate":float((x>0).mean())}

def max_dd(vals):
    s=peak=dd=0.0
    for v in vals:
        s+=float(v); peak=max(peak,s); dd=max(dd,peak-s)
    return dd

def main():
    base=load_trade_ledgers(); meta=build_boundary_metadata(base); spot=load_spot()
    raw_paths, path_errors=load_candidate_paths(meta,spot)
    delta_rows, delta_errors=add_deltas(meta,raw_paths); coverage=float(delta_rows.delta_valid.mean())
    print(f"Phase29: {len(meta)} trades; delta coverage {coverage:.4%}",flush=True)
    delta_errors.to_csv(OUT/"delta_errors.csv",index=False); pd.DataFrame(path_errors).to_csv(OUT/"path_errors.csv",index=False)
    if delta_rows.empty or coverage<0.95: raise RuntimeError(f"Delta coverage below 95%: {coverage:.4f}")
    delta_rows.to_csv(OUT/"minute_short_leg_delta_panel.csv",index=False)
    paths={exp:g.to_dict("records") for exp,g in delta_rows.groupby("expiry",sort=False)}
    rules=[]
    for mode in MODES:
        for lb in LOOKBACKS:
            for th in DELTA_CHANGES:
                for conf in CONFIRMS:
                    for kind in ["TARGET","STOP"]:
                        rules.append({"name":f"{mode}_{kind.lower()}_lb{lb}_d{th:.2f}_c{conf}","mode":mode,"lookback":lb,"threshold":th,"confirm":conf,"kind":kind})
    grid=[]; details={}
    for idx,r in enumerate(rules,1):
        df=apply_rule(meta,paths,r); details[r["name"]]=df; grid.append({**r,**summary(df)})
        if idx%50==0: print(f"Phase29 rule {idx}/{len(rules)} complete",flush=True)
    pd.DataFrame(grid).to_csv(OUT/"delta_change_grid.csv",index=False)
    train_rows=[]
    for r in rules:
        tr,va,ho=split(details[r["name"]]); train_rows.append({**r,**summary(tr)})
    train_df=pd.DataFrame(train_rows); train_df.to_csv(OUT/"delta_change_training_grid.csv",index=False)
    target_train=train_df[train_df.kind=="TARGET"].sort_values(["net_uplift","candidate_dd"],ascending=[False,True])
    stop_train=train_df[(train_df.kind=="STOP")&(train_df.winner_affected==0)].sort_values(["net_uplift","candidate_dd"],ascending=[False,True])
    selected_target=target_train.iloc[0].to_dict() if len(target_train) else None
    selected_stop=stop_train.iloc[0].to_dict() if len(stop_train) else None
    selections=[]
    for label,sel in [("target",selected_target),("stop",selected_stop)]:
        if sel:
            tr,va,ho=split(details[sel["name"]]); selections.append({"selection":label,"rule":sel["name"],
                "train_uplift":summary(tr)["net_uplift"],"validation_uplift":summary(va)["net_uplift"],"holdout_uplift":summary(ho)["net_uplift"],
                "validation_dd":summary(va)["candidate_dd"],"holdout_dd":summary(ho)["candidate_dd"],
                "validation_winners_affected":summary(va)["winner_affected"],"holdout_winners_affected":summary(ho)["winner_affected"]})
    pd.DataFrame(selections).to_csv(OUT/"selected_delta_change_walkforward.csv",index=False)
    combined=[]
    for e in meta.itertuples():
        path=paths.get(e.expiry,[]); stop=None
        for i,p in enumerate(path):
            if not p.get("delta_valid"): continue
            for rule in [selected_target,selected_stop]:
                if not rule: continue
                ch=delta_change(path,i,rule["mode"],int(rule["lookback"]))
                hit=(ch<=-float(rule["threshold"])) if rule["kind"]=="TARGET" else (ch>=float(rule["threshold"]))
                if hit:
                    stop={"p":p,"reason":"DELTA_CHANGE_TARGET" if rule["kind"]=="TARGET" else "DELTA_CHANGE_STOP"}; break
            if stop: break
        if stop is None: cand=e.base_net; ts=e.exit_ts; reason="EXPIRY_FALLBACK"
        else: cand=net_at(e,stop["p"]); ts=stop["p"]["ts"]; reason=stop["reason"]
        changed=pd.Timestamp(ts)<pd.Timestamp(e.exit_ts)
        combined.append({"expiry":e.expiry,"base_net":e.base_net,"candidate_net":cand,"net_uplift":cand-e.base_net,
                         "winner_affected":bool(e.base_net>0 and changed),"changed_before_base":changed,"exit_reason":reason,"exit_ts":ts})
    combined=pd.DataFrame(combined); combined.to_csv(OUT/"delta_change_trade_level.csv",index=False)
    tr,va,ho=split(combined); comb={"train":summary(tr),"validation":summary(va),"holdout":summary(ho),"full":summary(combined)}
    pd.DataFrame([{"period":k,**v} for k,v in comb.items()]).to_csv(OUT/"delta_change_summary.csv",index=False)
    rng=np.random.default_rng(20261005); boot=[]
    for period,df in [("validation",va),("holdout",ho),("full",combined)]:
        vals=df.net_uplift.to_numpy(float); sims=np.array([rng.choice(vals,len(vals),replace=True).mean() for _ in range(5000)])
        boot.append({"period":period,"mean_uplift":vals.mean(),"ci95_low":np.quantile(sims,.025),"ci95_high":np.quantile(sims,.975)})
    pd.DataFrame(boot).to_csv(OUT/"delta_change_bootstrap_uplift_ci.csv",index=False)
    cva,cho=comb["validation"],comb["holdout"]
    promote=(cva["net_uplift"]>0 and cho["net_uplift"]>0 and cva["candidate_dd"]<=1.05*cva["base_dd"] and cho["candidate_dd"]<=1.05*cho["base_dd"])
    pd.DataFrame([{"combined_promote":promote,"train_target":selected_target["name"] if selected_target else "",
        "train_stop":selected_stop["name"] if selected_stop else "","delta_coverage":coverage,
        "validation_uplift":cva["net_uplift"],"holdout_uplift":cho["net_uplift"],"validation_dd":cva["candidate_dd"],"holdout_dd":cho["candidate_dd"]}]).to_csv(OUT/"phase29_status.csv",index=False)
    report=f"""# Phase 29 Delta-Change Exit Research — Conclusion

No target-percentage criterion was used. Candidate target and stop exits were driven entirely by short-leg absolute-delta change over fixed lookback windows. No Phase-20 target or 13:30 conditional stop was used by the candidate; only expiry fallback remains.

Delta coverage: {coverage:.2%}
Training-selected target: {selected_target["name"] if selected_target else "NONE"}
Training-selected stop: {selected_stop["name"] if selected_stop else "NONE"}

Training: {comb["train"]}
Validation: {comb["validation"]}
2026 holdout: {comb["holdout"]}
Full: {comb["full"]}

Promotion: {promote}
"""
    (OUT/"PHASE29_CONCLUSION.md").write_text(report,encoding="utf-8"); print(report)

if __name__=="__main__":
    main()
