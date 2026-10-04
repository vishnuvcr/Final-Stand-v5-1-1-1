import os, sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from research.payoff_boundary_stop_research import (
    TZ, load_trade_ledgers, build_boundary_metadata, load_spot,
    load_candidate_paths, phase19_fixed_mfe50_stop, net_at
)

OUT = Path(os.getenv("OUT_DIR", "results/dynamic_n_corrected/phase27_delta_exit"))
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
        dport=leg[0]-leg[1]-leg[2]
        valid=np.isfinite(dport)
        favorable=np.where(typ=="CE",dport,-dport)
        adverse=-favorable
        for i,p in enumerate(path):
            z=dict(p)
            z["portfolio_delta"]=float(dport[i]) if valid[i] else np.nan
            z["abs_delta"]=float(abs(dport[i])) if valid[i] else np.nan
            z["favorable_delta"]=float(favorable[i]) if valid[i] else np.nan
            z["adverse_delta"]=float(adverse[i]) if valid[i] else np.nan
            z["delta_valid"]=bool(valid[i])
            rows.append({
                "expiry":entry.expiry,"ts":z["ts"],"direction":entry.direction,
                "option_type":typ,"spot":z["spot"],"gross":z["gross"],
                "mfe":z["mfe"],"target":entry.target,
                "raw_exit":z["raw_exit"],
                "portfolio_delta":z["portfolio_delta"],"abs_delta":z["abs_delta"],
                "favorable_delta":z["favorable_delta"],"adverse_delta":z["adverse_delta"],
                "delta_valid":z["delta_valid"]
            })
        if not valid.any(): errors.append({"expiry":entry.expiry,"error":"no valid delta observations"})
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
        control_stop=None
        control_net=e.base_net
        control_ts=e.exit_ts
        control_reason="BASELINE"
        if path:
            p19=phase19_fixed_mfe50_stop(e,path)
            if p19 is not None:
                control_stop=p19
                control_net=net_at(e,p19)
                control_ts=p19["ts"]
                control_reason="P19_STOP"
        stop=None
        if path:
            for i,p in enumerate(path):
                if p.get("delta_valid") and p["gross"]>=e.target:
                    stop={"p":p,"reason":"TARGET"}
                    break
                if p.get("delta_valid"):
                    if rule["profit_frac"] is not None and p["gross"]>=rule["profit_frac"]*e.target and p["abs_delta"]<=rule["abs_delta"]:
                        stop={"p":p,"reason":"DELTA_PROFIT"}
                        break
                    if rule["adverse_delta"] is not None and p["gross"]<0 and p["adverse_delta"]>=rule["adverse_delta"]:
                        if rule["confirm"]==1:
                            stop={"p":p,"reason":"DELTA_STOP"}
                            break
                        if i>=rule["confirm"]-1:
                            win=path[i-rule["confirm"]+1:i+1]
                            ok=all(x.get("delta_valid") and x["gross"]<0 and x["adverse_delta"]>=rule["adverse_delta"] for x in win)
                            exact=all((pd.Timestamp(win[j]["ts"])-pd.Timestamp(win[j-1]["ts"])).total_seconds()==60 for j in range(1,len(win)))
                            if ok and exact:
                                stop={"p":win[0],"reason":"DELTA_STOP"}
                                break
                if control_stop is not None and pd.Timestamp(p["ts"]) == pd.Timestamp(control_ts):
                    # Phase-20 control stop has reached its exact observed trigger minute.
                    stop={"p":p,"reason":control_reason}
                    break
        if stop is None:
            cand=control_net; ts=control_ts; reason=control_reason
        else:
            cand=net_at(e,stop["p"]); ts=stop["p"]["ts"]; reason=stop["reason"]
        changed=pd.Timestamp(ts)<pd.Timestamp(control_ts)
        out.append({"expiry":e.expiry,"base_net":control_net,"candidate_net":cand,
                    "net_uplift":cand-control_net,"base_positive":control_net>0,
                    "changed_before_base":changed,"winner_affected":bool(control_net>0 and changed),
                    "exit_reason":reason,"exit_ts":ts,
                    "abs_delta_at_exit":stop["p"].get("abs_delta") if stop else np.nan,
                    "adverse_delta_at_exit":stop["p"].get("adverse_delta") if stop else np.nan})
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
    delta_long=pd.DataFrame()
    delta_rows, delta_errors=add_deltas(meta,raw_paths)
    # Rebuild paths with delta annotations.
    paths={}
    for exp,g in delta_rows.groupby("expiry",sort=False):
        paths[exp]=g.to_dict("records")
    if delta_errors.empty:
        delta_errors.to_csv(OUT/"delta_errors.csv",index=False)
    else: delta_errors.to_csv(OUT/"delta_errors.csv",index=False)
    pd.DataFrame(path_errors).to_csv(OUT/"path_errors.csv",index=False)

    if delta_rows.empty or delta_rows["delta_valid"].mean()<0.95:
        raise RuntimeError("Delta coverage below 95%; do not accept the phase.")

    # Diagnostics: delta distribution at target proximity and before baseline exit.
    delta_rows.to_csv(OUT/"minute_delta_panel.csv",index=False)
    diagnostics=[]
    for _,g in delta_rows.groupby("expiry"):
        last=g.iloc[-1]
        diagnostics.append({"expiry":_,"direction":last.direction,"final_abs_delta":last.abs_delta,
                            "final_adverse_delta":last.adverse_delta,"final_gross":last.gross,
                            "max_abs_delta":g.abs_delta.max(),"min_adverse_delta":g.adverse_delta.min(),
                            "max_adverse_delta":g.adverse_delta.max()})
    pd.DataFrame(diagnostics).to_csv(OUT/"delta_trade_diagnostics.csv",index=False)

    rules=[]
    for f in PROFIT_FRACS:
        for d in ABS_DELTAS:
            rules.append({"name":f"profit_f{f:.2f}_d{d:.2f}","profit_frac":f,"abs_delta":d,"adverse_delta":None,"confirm":1})
    for d in ADVERSE_DELTAS:
        for c in CONFIRMS:
            rules.append({"name":f"stop_d{d:.2f}_c{c}","profit_frac":None,"abs_delta":None,"adverse_delta":d,"confirm":c})
    grid=[]
    details={}
    for r in rules:
        df=apply_rule(meta,paths,r); details[r["name"]]=df
        grid.append({**r,**summary(df)})
    grid_df=pd.DataFrame(grid)
    grid_df.to_csv(OUT/"delta_rule_grid.csv",index=False)

    train=[]
    for r in rules:
        tr,va,ho=split(details[r["name"]]); train.append({**r,**summary(tr)})
    train_df=pd.DataFrame(train)
    train_df.to_csv(OUT/"delta_training_grid.csv",index=False)

    # Profit candidates intentionally may affect winners; adverse stops prefer zero training winners.
    profit_train=train_df[train_df.profit_frac.notna()].sort_values(["net_uplift","candidate_dd"],ascending=[False,True])
    stop_train=train_df[train_df.adverse_delta.notna() & (train_df.winner_affected==0)].sort_values(["net_uplift","candidate_dd"],ascending=[False,True])
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
    pd.DataFrame(selections).to_csv(OUT/"selected_rules_walkforward.csv",index=False)

    # Combined: use selected training rules together.
    combined_rule={"profit_frac":selected_profit["profit_frac"] if selected_profit else None,
                   "abs_delta":selected_profit["abs_delta"] if selected_profit else None,
                   "adverse_delta":selected_stop["adverse_delta"] if selected_stop else None,
                   "confirm":int(selected_stop["confirm"]) if selected_stop else 1}
    combined=apply_rule(meta,paths,combined_rule)
    combined.to_csv(OUT/"combined_trade_level.csv",index=False)
    tr,va,ho=split(combined)
    comb_s={"train":summary(tr),"validation":summary(va),"holdout":summary(ho),"full":summary(combined)}
    pd.DataFrame([{ "period":k,**v} for k,v in comb_s.items()]).to_csv(OUT/"combined_summary.csv",index=False)

    # Bootstrap paired mean uplift on validation and holdout.
    rng=np.random.default_rng(20261004)
    boot=[]
    for period,df in [("validation",va),("holdout",ho),("full",combined)]:
        vals=df.net_uplift.to_numpy(float)
        if len(vals):
            sims=np.array([rng.choice(vals,len(vals),replace=True).mean() for _ in range(5000)])
            boot.append({"period":period,"mean_uplift":vals.mean(),
                         "ci95_low":np.quantile(sims,0.025),"ci95_high":np.quantile(sims,0.975)})
    pd.DataFrame(boot).to_csv(OUT/"bootstrap_uplift_ci.csv",index=False)

    # Promotion screen.
    cva=comb_s["validation"]; cho=comb_s["holdout"]
    promote=(cva["net_uplift"]>0 and cho["net_uplift"]>0 and
             cva["candidate_dd"]<=1.05*cva["base_dd"] and
             cho["candidate_dd"]<=1.05*cho["base_dd"])
    pd.DataFrame([{"combined_promote":promote,"train_rule_profit":selected_profit["name"] if selected_profit else "",
                   "train_rule_stop":selected_stop["name"] if selected_stop else "",
                   "delta_coverage":float(delta_rows.delta_valid.mean()),
                   "validation_uplift":cva["net_uplift"],"holdout_uplift":cho["net_uplift"],
                   "validation_dd":cva["candidate_dd"],"holdout_dd":cho["candidate_dd"]}]).to_csv(OUT/"phase27_status.csv",index=False)

    report=f"""# Phase 27 Delta Exit Research — Conclusion

Delta was reconstructed minute-by-minute from observed option prices using European Black-Scholes implied volatility (r=0, q=0 baseline), then aggregated using the actual three-leg position signs.

Delta coverage: {delta_rows.delta_valid.mean():.2%}

Training-selected profit rule: {selected_profit["name"] if selected_profit else "NONE"}
Training-selected adverse stop: {selected_stop["name"] if selected_stop else "NONE"}

Combined walk-forward:
- Training: {comb_s["train"]}
- Validation: {comb_s["validation"]}
- Holdout: {comb_s["holdout"]}
- Full: {comb_s["full"]}

Promotion screen: **{promote}**

The locked Phase-20 strategy remains the control. A delta rule is not promoted unless it passes the registered validation/holdout and drawdown gates.
"""
    (OUT/"PHASE27_CONCLUSION.md").write_text(report,encoding="utf-8")
    print(report)

if __name__=="__main__":
    main()
