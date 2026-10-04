import os, sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from research.payoff_boundary_stop_research import (
    TZ, load_trade_ledgers, build_boundary_metadata, load_spot,
    load_candidate_paths, phase19_fixed_mfe50_stop, net_at
)

OUT = Path(os.getenv("OUT_DIR", "results/dynamic_n_corrected/phase28_leg_delta_exit"))
OUT.mkdir(parents=True, exist_ok=True)
TRAIN_END = pd.Timestamp("2023-12-31", tz=TZ)
VALIDATION_END = pd.Timestamp("2025-12-31", tz=TZ)
HOLDOUT_START = pd.Timestamp("2026-01-01", tz=TZ)

PROFIT_FRACS = [0.50,0.60,0.70,0.80,0.90]
ABS_DELTAS = [0.05,0.10,0.15,0.20,0.25,0.30]
ADVERSE_DELTAS = [0.10,0.15,0.20,0.25,0.30,0.40,0.50]
CONFIRMS = [1,3]

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

def apply_rule(meta, paths, rule):
    out=[]
    for e in meta.itertuples():
        path=paths.get(e.expiry)
        control_stop=None; control_net=e.base_net; control_ts=e.exit_ts; control_reason="BASELINE"
        if path:
            p19=phase19_fixed_mfe50_stop(e,path)
            if p19 is not None:
                control_stop=p19; control_net=net_at(e,p19); control_ts=p19["ts"]; control_reason="P19_STOP"
        stop=None
        if path:
            for i,p in enumerate(path):
                if p.get("delta_valid") and p["gross"]>=e.target:
                    stop={"p":p,"reason":"TARGET"}; break
                if p.get("delta_valid"):
                    delta=p.get(rule["leg_col"],np.nan)
                    if rule["profit_frac"] is not None and p["gross"]>=rule["profit_frac"]*e.target and delta<=rule["profit_threshold"]:
                        stop={"p":p,"reason":"LEG_DELTA_PROFIT"}; break
                    if rule["adverse_threshold"] is not None and p["gross"]<0 and delta>=rule["adverse_threshold"]:
                        if rule["confirm"]==1:
                            stop={"p":p,"reason":"LEG_DELTA_STOP"}; break
                        if i>=rule["confirm"]-1:
                            win=path[i-rule["confirm"]+1:i+1]
                            ok=all(x.get("delta_valid") and x["gross"]<0 and x.get(rule["leg_col"],np.nan)>=rule["adverse_threshold"] for x in win)
                            exact=all((pd.Timestamp(win[j]["ts"])-pd.Timestamp(win[j-1]["ts"])).total_seconds()==60 for j in range(1,len(win)))
                            if ok and exact:
                                stop={"p":win[0],"reason":"LEG_DELTA_STOP"}; break
                if control_stop is not None and pd.Timestamp(p["ts"]) == pd.Timestamp(control_ts):
                    stop={"p":p,"reason":control_reason}; break
        if stop is None:
            cand=control_net; ts=control_ts; reason=control_reason
        else:
            cand=net_at(e,stop["p"]); ts=stop["p"]["ts"]; reason=stop["reason"]
        changed=pd.Timestamp(ts)<pd.Timestamp(control_ts)
        out.append({"expiry":e.expiry,"base_net":control_net,"candidate_net":cand,
                    "net_uplift":cand-control_net,"base_positive":control_net>0,
                    "changed_before_base":changed,"winner_affected":bool(control_net>0 and changed),
                    "exit_reason":reason,"exit_ts":ts,
                    "delta_at_exit":stop["p"].get(rule["leg_col"]) if stop else np.nan})
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
    delta_rows, delta_errors=add_deltas(meta,raw_paths)
    paths={}
    for exp,g in delta_rows.groupby("expiry",sort=False):
        paths[exp]=g.to_dict("records")
    delta_errors.to_csv(OUT/"delta_errors.csv",index=False)
    pd.DataFrame(path_errors).to_csv(OUT/"path_errors.csv",index=False)
    coverage=float(delta_rows.delta_valid.mean())
    if delta_rows.empty or coverage<0.95:
        raise RuntimeError(f"Individual-leg delta coverage below 95%: {coverage:.4f}")
    delta_rows.to_csv(OUT/"minute_leg_delta_panel.csv",index=False)

    # Diagnostics at key control-state landmarks.
    diagnostics=[]
    for exp,g in delta_rows.groupby("expiry",sort=False):
        g=g.sort_values("ts")
        diagnostics.append({
            "expiry":exp,"direction":g.direction.iloc[0],
            "entry_short1_abs_delta":g.short1_abs_delta.iloc[0],
            "entry_short2_abs_delta":g.short2_abs_delta.iloc[0],
            "max_short1_abs_delta":g.short1_abs_delta.max(),
            "max_short2_abs_delta":g.short2_abs_delta.max(),
            "min_short1_abs_delta":g.short1_abs_delta.min(),
            "min_short2_abs_delta":g.short2_abs_delta.min(),
            "final_short1_abs_delta":g.short1_abs_delta.iloc[-1],
            "final_short2_abs_delta":g.short2_abs_delta.iloc[-1]
        })
    pd.DataFrame(diagnostics).to_csv(OUT/"leg_delta_trade_diagnostics.csv",index=False)

    # Test each leg independently. For calls and puts, absolute delta is used so sign does not bias the comparison.
    rules=[]
    for leg,label in [("short1_abs_delta","S1"),("short2_abs_delta","S2")]:
        for f in PROFIT_FRACS:
            for d in ABS_DELTAS:
                rules.append({"name":f"{label}_profit_f{f:.2f}_d{d:.2f}","leg_col":leg,"profit_frac":f,
                              "profit_threshold":d,"adverse_threshold":None,"confirm":1})
        for d in ADVERSE_DELTAS:
            for c in CONFIRMS:
                rules.append({"name":f"{label}_stop_d{d:.2f}_c{c}","leg_col":leg,"profit_frac":None,
                              "profit_threshold":None,"adverse_threshold":d,"confirm":c})
    grid=[]; details={}
    for r in rules:
        df=apply_rule(meta,paths,r); details[r["name"]]=df; grid.append({**r,**summary(df)})
    grid_df=pd.DataFrame(grid); grid_df.to_csv(OUT/"individual_leg_delta_grid.csv",index=False)

    train_rows=[]
    for r in rules:
        tr,va,ho=split(details[r["name"]]); train_rows.append({**r,**summary(tr)})
    train_df=pd.DataFrame(train_rows); train_df.to_csv(OUT/"individual_leg_delta_training_grid.csv",index=False)

    # Select the best profit rule across both short legs and the best adverse stop with zero training winners affected.
    profit_train=train_df[train_df.profit_frac.notna()].sort_values(["net_uplift","candidate_dd"],ascending=[False,True])
    stop_train=train_df[train_df.adverse_threshold.notna() & (train_df.winner_affected==0)].sort_values(["net_uplift","candidate_dd"],ascending=[False,True])
    selected_profit=profit_train.iloc[0].to_dict() if len(profit_train) else None
    selected_stop=stop_train.iloc[0].to_dict() if len(stop_train) else None
    selections=[]
    for label,sel in [("profit",selected_profit),("stop",selected_stop)]:
        if sel:
            d=details[sel["name"]]; tr,va,ho=split(d)
            selections.append({"selection":label,"rule":sel["name"],"train_uplift":summary(tr)["net_uplift"],
                               "validation_uplift":summary(va)["net_uplift"],"holdout_uplift":summary(ho)["net_uplift"],
                               "validation_dd":summary(va)["candidate_dd"],"holdout_dd":summary(ho)["candidate_dd"],
                               "validation_winners_affected":summary(va)["winner_affected"],
                               "holdout_winners_affected":summary(ho)["winner_affected"]})
    pd.DataFrame(selections).to_csv(OUT/"selected_leg_rules_walkforward.csv",index=False)

    # Combined candidate uses the selected S1/S2 profit rule and adverse stop simultaneously.
    if selected_profit:
        combined_rules=[selected_profit]
    else: combined_rules=[]
    combined=apply_rule(meta,paths,selected_profit if selected_profit else {"leg_col":"short1_abs_delta","profit_frac":None,"profit_threshold":None,"adverse_threshold":None,"confirm":1})
    # Add adverse stop separately only if it exists and is on the same leg; otherwise the selected profit rule is the primary candidate.
    if selected_stop:
        combined_rule=dict(selected_profit) if selected_profit else dict(selected_stop)
        combined_rule["adverse_threshold"]=selected_stop["adverse_threshold"]
        combined_rule["confirm"]=int(selected_stop["confirm"])
        combined=apply_rule(meta,paths,combined_rule)
    combined.to_csv(OUT/"combined_leg_delta_trade_level.csv",index=False)
    tr,va,ho=split(combined)
    comb_s={"train":summary(tr),"validation":summary(va),"holdout":summary(ho),"full":summary(combined)}
    pd.DataFrame([{ "period":k,**v} for k,v in comb_s.items()]).to_csv(OUT/"combined_leg_delta_summary.csv",index=False)

    rng=np.random.default_rng(20261004); boot=[]
    for period,df in [("validation",va),("holdout",ho),("full",combined)]:
        vals=df.net_uplift.to_numpy(float)
        if len(vals):
            sims=np.array([rng.choice(vals,len(vals),replace=True).mean() for _ in range(5000)])
            boot.append({"period":period,"mean_uplift":vals.mean(),"ci95_low":np.quantile(sims,0.025),"ci95_high":np.quantile(sims,0.975)})
    pd.DataFrame(boot).to_csv(OUT/"leg_delta_bootstrap_uplift_ci.csv",index=False)

    cva=comb_s["validation"]; cho=comb_s["holdout"]
    promote=(cva["net_uplift"]>0 and cho["net_uplift"]>0 and
             cva["candidate_dd"]<=1.05*cva["base_dd"] and cho["candidate_dd"]<=1.05*cho["base_dd"])
    pd.DataFrame([{"combined_promote":promote,
                   "train_rule_profit":selected_profit["name"] if selected_profit else "",
                   "train_rule_stop":selected_stop["name"] if selected_stop else "",
                   "delta_coverage":coverage,"validation_uplift":cva["net_uplift"],
                   "holdout_uplift":cho["net_uplift"],"validation_dd":cva["candidate_dd"],
                   "holdout_dd":cho["candidate_dd"]}]).to_csv(OUT/"phase28_status.csv",index=False)

    report=f"""# Phase 28 Individual-Leg Delta Research — Conclusion

NSE documents NIFTY index options as European-style CE/PE contracts. Individual-leg deltas were reconstructed minute-by-minute from observed option prices using European Black-Scholes implied volatility (r=0, q=0 baseline). Coverage: {coverage:.2%}.

Primary hypothesis: the two short legs, especially the nearer OTM-(n+1) short leg, may provide more useful exit information than net portfolio delta.

Training-selected profit rule: {selected_profit["name"] if selected_profit else "NONE"}
Training-selected adverse stop: {selected_stop["name"] if selected_stop else "NONE"}

Combined walk-forward:
- Training: {comb_s["train"]}
- Validation: {comb_s["validation"]}
- Holdout: {comb_s["holdout"]}
- Full: {comb_s["full"]}

Promotion screen: **{promote}**

The Phase-20 strategy remains the control. No rule is promoted unless it passes validation and 2026 holdout with the preregistered drawdown gate.
"""
    (OUT/"PHASE28_CONCLUSION.md").write_text(report,encoding="utf-8")
    print(report)

if __name__=="__main__":
    main()
