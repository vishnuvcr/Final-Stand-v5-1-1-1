import json
from pathlib import Path
import numpy as np
import pandas as pd
from phase43_vix_strategy_sweep import (
    TZ, START, END, DEV_END, VAL_END, load_parquet, load_vix, vix_state,
    exec_px, charges, lot_size_for_expiry
)

TT05_ENGINE_REV="50B-TT05-BASE-V1"
OUT=Path("results/phase50b/tt05_short_straddle_replay"); OUT.mkdir(parents=True,exist_ok=True)
ENTRY_START=pd.Timestamp("09:30").time()
ENTRY_END=pd.Timestamp("15:10").time()
EXIT_TIME=pd.Timestamp("15:15").time()
STOP=-3000.0

def clean(x):
    x=x.copy(); x["timestamp"]=pd.to_datetime(x["timestamp"])
    if x["timestamp"].dt.tz is None:x["timestamp"]=x["timestamp"].dt.tz_localize(TZ)
    else:x["timestamp"]=x["timestamp"].dt.tz_convert(TZ)
    x["strike"]=pd.to_numeric(x["strike"],errors="coerce"); x["close"]=pd.to_numeric(x["close"],errors="coerce")
    x["option_type"]=x["option_type"].astype(str).str.upper()
    return x.dropna(subset=["timestamp","strike","close"])

def q(z,opt,k):
    a=z[(z.option_type==opt)&np.isclose(z.strike,float(k),rtol=0,atol=1e-8)]
    return None if a.empty else float(a.iloc[-1].close)

def exps():
    z=pd.read_csv("results/phase43_vix/strategy_trade_matrix_all_splits.csv",usecols=["expiry"])
    return sorted({pd.Timestamp(x).tz_localize(TZ) for x in z.expiry.dropna()})

def current_expiry(exps,day):
    d=pd.Timestamp(day).normalize()
    for e in exps:
        if e.normalize()>=d:return e
    return None

def next_expiry(exps,cur):
    for e in exps:
        if e>cur:return e
    return None

def idx():
    z=load_parquet("index/NIFTY.parquet")
    return z[["timestamp","close"]].rename(columns={"close":"spot"}).drop_duplicates("timestamp").sort_values("timestamp")

def finish(pos,exit_ts,z):
    gross=pos["cash"]; orders=list(pos["orders"])
    for name,leg in pos["legs"].items():
        px=q(z,leg["opt"],leg["strike"])
        if px is None:
            return None,{"trade_id":pos["trade_id"],"expiry":str(pos["expiry"].date()),"trigger_ts":str(exit_ts),"gap_type":"missing_exit_leg_quote"}
        side="sell" if leg["qty"]>0 else "buy"; ep=exec_px(px,side)
        gross += ep*abs(leg["qty"])*pos["lot"] if side=="sell" else -ep*abs(leg["qty"])*pos["lot"]
        orders.append((pd.Timestamp(exit_ts),side,ep*abs(leg["qty"])))
    cost=charges(orders,pos["lot"],1.0)
    cost50=charges(orders,pos["lot"],1.5)
    cost20=charges(orders,pos["lot"],1.0,brokerage_per_order=20.0)
    cost20_50=charges(orders,pos["lot"],1.5,brokerage_per_order=20.0)
    return {
        "trade_id":pos["trade_id"],"entry_ts":pos["entry_ts"],"exit_ts":str(exit_ts),
        "expiry":str(pos["expiry"].date()),"entry_spot":pos["entry_spot"],"lot":pos["lot"],
        "gross":gross,"cost":cost,"net":gross-cost,"net50":gross-cost50,
        "net20":gross-cost20,"net20_50":gross-cost20_50,
        "vix":pos["vix"],"vix_state":pos["vix_state"]
    },None

def main():
    index=idx(); vix=load_vix(); E=exps()
    cache={}; rows=[]; gaps=[]; errors=[]; trade_id=1
    for day in sorted(index.timestamp.dt.normalize().unique()):
        day=pd.Timestamp(day)
        if day<START.normalize() or day>END.normalize():continue
        cur=current_expiry(E,day)
        if cur is None:continue
        nxt=next_expiry(E,cur)
        target=nxt if day.weekday()==3 else cur
        if target is None:continue
        if target not in cache: cache[target]=clean(load_parquet(f"options/NIFTY/{target.strftime('%Y-%m-%d')}.parquet"))
        z=cache[target]
        dayidx=index[(index.timestamp.dt.normalize()==day)&(index.timestamp.dt.time>=ENTRY_START)&(index.timestamp.dt.time<=EXIT_TIME)]
        traded=False
        for ts in dayidx.timestamp.tolist():
            ts=pd.Timestamp(ts)
            ix=index[index.timestamp==ts]
            if ix.empty:continue
            spot=float(ix.iloc[-1].spot)
            snap=z[z.timestamp==ts]
            if snap.empty:continue
            if not traded and ts.time()<=ENTRY_END:
                strikes=snap.strike.astype(float).unique()
                if len(strikes)==0:continue
                atm=float(min(strikes,key=lambda k:abs(k-spot)))
                ce=q(snap,"CE",atm); pe=q(snap,"PE",atm)
                if ce is None or pe is None:continue
                vs=vix_state(vix,ts)
                lot=lot_size_for_expiry(target)
                orders=[]; cash=0.0; legs={}
                for name,opt,px in [("ce","CE",ce),("pe","PE",pe)]:
                    ep=exec_px(px,"sell"); cash+=ep*lot
                    orders.append((ts,"sell",ep))
                    legs[name]={"opt":opt,"strike":atm,"qty":-1}
                pos={"trade_id":trade_id,"entry_ts":str(ts),"entry_spot":spot,"expiry":target,
                     "lot":lot,"cash":cash,"orders":orders,"legs":legs,
                     "vix":vs["vix"] if vs else np.nan,"vix_state":vs["level_state"] if vs else None}
                trade_id+=1; traded=True
            if not traded:continue
            snap=z[z.timestamp==ts]
            if snap.empty:continue
            mark=pos["cash"]
            ok=True
            for leg in pos["legs"].values():
                px=q(snap,leg["opt"],leg["strike"])
                if px is None:ok=False;break
                mark += leg["qty"]*px*pos["lot"]
            if not ok:continue
            if mark<=STOP or ts.time()>=EXIT_TIME:
                out,gap=finish(pos,ts,snap)
                if out is not None:rows.append(out)
                else:gaps.append(gap)
                break
    df=pd.DataFrame(rows)
    df.to_csv(OUT/"tt05_trades.csv",index=False)
    pd.DataFrame(gaps,columns=["trade_id","expiry","trigger_ts","gap_type"]).to_csv(OUT/"coverage_gaps.csv",index=False)
    pd.DataFrame(errors,columns=["day","error"]).to_csv(OUT/"data_errors.csv",index=False)
    cand=len(df)+len(gaps); cov=len(df)/cand if cand else 0.0
    splits=[]
    if not df.empty:
        d=pd.to_datetime(df.expiry)
        for n,m in [("DEV",d<=DEV_END),("VAL",(d>DEV_END)&(d<=VAL_END)),("HOLD",d>VAL_END)]:
            qv=df[m]; splits.append({"split":n,"trades":len(qv),"net":float(qv.net.sum()),"net50":float(qv.net50.sum()),"net20":float(qv.net20.sum()),"net20_50":float(qv.net20_50.sum())})
    summary={"strategy":"TT-05","engine_revision":TT05_ENGINE_REV,"trades":len(df),"candidate_trades":cand,
             "coverage_exclusions":len(gaps),"coverage_rate":cov,
             "net":float(df.net.sum()) if not df.empty else 0.0,
             "net50":float(df.net50.sum()) if not df.empty else 0.0,
             "net20":float(df.net20.sum()) if not df.empty else 0.0,
             "net20_50":float(df.net20_50.sum()) if not df.empty else 0.0,
             "splits":splits}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
