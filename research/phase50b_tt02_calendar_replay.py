import json, math, os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import brentq

from phase43_vix_strategy_sweep import (
    TZ, START, END, DEV_END, VAL_END,
    load_parquet, load_vix, modal_step, exec_px, charges,
    lot_size_for_expiry, vix_state
)

OUT=Path("results/phase50b/tt02_replay")
OUT.mkdir(parents=True, exist_ok=True)

FAMILY="TT-02"
ENTRY_TIME=(9,20)
PRIMARY_SLIP_TICKS=1.0
TICK=0.05

# Deterministic source-faithful baseline assumptions that are NOT stated numerically
# by Tradetron: risk-free rate 0%, European Black-Scholes delta, first executable
# 09:20 observation, and last observed close used for each minute. These are frozen
# before looking at the replay result and recorded for sensitivity follow-up.
RISK_FREE=0.0

def norm_cdf(x):
    return 0.5*(1.0+math.erf(x/math.sqrt(2.0)))

def bs_price(s,k,t,sigma,r,call):
    if t<=0:
        return max(s-k,0.0) if call else max(k-s,0.0)
    if sigma<=0:
        return math.exp(-r*t)*max(s-k,0.0) if call else math.exp(-r*t)*max(k-s,0.0)
    d1=(math.log(s/k)+(r+0.5*sigma*sigma)*t)/(sigma*math.sqrt(t))
    d2=d1-sigma*math.sqrt(t)
    if call:
        return s*norm_cdf(d1)-k*math.exp(-r*t)*norm_cdf(d2)
    return k*math.exp(-r*t)*norm_cdf(-d2)-s*norm_cdf(-d1)

def bs_delta(s,k,t,sigma,r,call):
    if t<=0:
        return 1.0 if call and s>k else 0.0 if call else -1.0 if s<k else 0.0
    d1=(math.log(s/k)+(r+0.5*sigma*sigma)*t)/(sigma*math.sqrt(t))
    return norm_cdf(d1) if call else norm_cdf(d1)-1.0

def implied_vol(price,s,k,t,r,call):
    if not np.isfinite(price) or price<=0 or s<=0 or k<=0 or t<=0:
        return None
    intrinsic=math.exp(-r*t)*max(s-k,0.0) if call else math.exp(-r*t)*max(k-s,0.0)
    upper=s if call else k*math.exp(-r*t)
    if price <= intrinsic + 1e-8 or price >= upper:
        return None
    f=lambda sig: bs_price(s,k,t,sig,r,call)-price
    try:
        return brentq(f,1e-5,8.0,maxiter=80)
    except Exception:
        return None

def delta_from_price(price,spot,strike,ts,expiry,opt):
    t=max((expiry+pd.Timedelta(hours=15,minutes=30)-ts).total_seconds(),1.0)/(365*24*3600)
    iv=implied_vol(float(price),float(spot),float(strike),t,RISK_FREE,opt=="CE")
    return None if iv is None else bs_delta(float(spot),float(strike),t,iv,RISK_FREE,opt=="CE")

def next_expiry(expiries,cur):
    i=expiries.index(cur)
    return expiries[i+1] if i+1<len(expiries) else None

def nearest_delta_strike(snapshot,spot,expiry,ts,opt,target):
    z=snapshot[(snapshot.option_type==opt)&np.isfinite(snapshot.close)].copy()
    if z.empty:return None
    ds=[]
    for row in z.itertuples(index=False):
        d=delta_from_price(row.close,spot,float(row.strike),ts,expiry,opt)
        if d is not None:
            ds.append((abs(d-target),float(row.strike),d))
    if not ds:return None
    ds.sort(key=lambda x:(x[0],abs(x[1]-spot),x[1]))
    return ds[0][1]

def quote(snapshot,opt,strike):
    z=snapshot[(snapshot.option_type==opt)&(np.isclose(snapshot.strike,float(strike),rtol=0,atol=1e-8))]
    if z.empty:return None
    return float(z.iloc[-1].close)

def option_delta(snapshot,spot,expiry,ts,opt,strike):
    q=quote(snapshot,opt,strike)
    return None if q is None else delta_from_price(q,spot,float(strike),ts,expiry,opt)

def make_leg(opt,strike,qty,expiry_key):
    return {"opt":opt,"strike":float(strike),"qty":int(qty),"exp_key":expiry_key}

def leg_value(leg,frames,spot,ts,expiries_by_key):
    exp=expiries_by_key[leg["exp_key"]]
    q=quote(frames[leg["exp_key"]],leg["opt"],leg["strike"])
    if q is None:return None
    return q

def pnl_from_ledger(ledger):
    # ledger rows: timestamp, side, option_price, qty, expiry, opt
    if not ledger:return 0.0, []
    orders=[]
    gross=0.0
    for r in ledger:
        side=r["side"]; price=float(r["price"]); qty=abs(int(r["qty"])); lot=r["lot"]
        ep=exec_px(price,side)
        gross += (-1 if side=="buy" else 1) * ep*qty*lot
        orders.append((pd.Timestamp(r["ts"]),side,ep*qty))
    return gross,orders

def expiry_dates():
    idx=load_parquet("index/NIFTY.parquet")
    days=sorted(pd.to_datetime(idx.timestamp).dt.normalize().dropna().unique())
    # Exact expiry files already used by Phase 43.
    p=Path("results/phase43_vix/strategy_trade_matrix_all_splits.csv")
    x=pd.read_csv(p,usecols=["expiry"])
    return sorted(set(pd.to_datetime(x.expiry).map(lambda z: z.tz_localize(TZ) if pd.Timestamp(z).tzinfo is None else pd.Timestamp(z).tz_convert(TZ))))

def replay_expiry(index,vix,data,expiry,expiries):
    cur=expiry; nxt=next_expiry(expiries,cur)
    if nxt is None:return None
    idx_days=sorted(pd.to_datetime(index.timestamp).dt.normalize().dropna().unique())
    prior=[d for d in idx_days if d<cur.normalize()]
    if len(prior)<1:return None
    entry_day=prior[-1]
    ts=entry_day+pd.Timedelta(hours=ENTRY_TIME[0],minutes=ENTRY_TIME[1])
    idxrow=index[index.timestamp==ts]
    if idxrow.empty:return None
    spot=float(idxrow.iloc[-1].spot)
    snap=data[data.timestamp==ts]
    if snap.empty:return None
    short_ce=nearest_delta_strike(snap,spot,cur,ts,"CE",0.20)
    short_pe=nearest_delta_strike(snap,spot,cur,ts,"PE",-0.20)
    long_ce=nearest_delta_strike(snap,spot,nxt,ts,"CE",0.10)
    long_pe=nearest_delta_strike(snap,spot,nxt,ts,"PE",-0.10)
    if None in (short_ce,short_pe,long_ce,long_pe):return None

    lot=lot_size_for_expiry(cur)
    legs=[make_leg("CE",short_ce,-1,"cur"),make_leg("PE",short_pe,-1,"cur"),make_leg("CE",long_ce,2,"next"),make_leg("PE",long_pe,2,"next")]
    state={"ce_decay":0,"ce_rev":0,"pe_decay":0,"pe_rev":0,"lc_spike":0,"lp_spike":0}
    ledger=[]
    for leg in legs:
        ledger.append({"ts":ts,"side":"sell" if leg["qty"]<0 else "buy","price":quote(snap,leg["opt"],leg["strike"]),"qty":leg["qty"],"lot":lot,"opt":leg["opt"]})
    # Minute replay from entry through current-week expiry.
    end=cur.normalize()+pd.Timedelta(hours=15,minutes=15)
    times=sorted(set(data[(data.timestamp>=ts)&(data.timestamp<=end)].timestamp.unique()))
    for t in times:
        t=pd.Timestamp(t)
        if t==ts: continue
        idxr=index[index.timestamp==t]
        if idxr.empty: continue
        s=float(idxr.iloc[-1].spot)
        snap_t=data[data.timestamp==t]
        if snap_t.empty: continue

        # One deterministic repair pass in source order.
        def replace_leg(which,new_opt,target_exp,target_delta):
            nonlocal legs,ledger
            old=legs[which]
            px=quote(snap_t,old["opt"],old["strike"])
            if px is None:return False
            ledger.append({"ts":t,"side":"buy" if old["qty"]<0 else "sell","price":px,"qty":old["qty"],"lot":lot,"opt":old["opt"]})
            exp=cur if target_exp=="cur" else nxt
            st=nearest_delta_strike(snap_t,s,exp,t,new_opt,target_delta)
            if st is None:return False
            q=quote(snap_t,new_opt,st)
            if q is None:return False
            legs[which]=make_leg(new_opt,st,old["qty"],target_exp)
            ledger.append({"ts":t,"side":"sell" if old["qty"]<0 else "buy","price":q,"qty":old["qty"],"lot":lot,"opt":new_opt})
            return True

        # Find current short CE delta.
        ce_short=[i for i,l in enumerate(legs) if l["opt"]=="CE" and l["qty"]<0 and l["exp_key"]=="cur"]
        pe_short=[i for i,l in enumerate(legs) if l["opt"]=="PE" and l["qty"]<0 and l["exp_key"]=="cur"]
        lc=[i for i,l in enumerate(legs) if l["opt"]=="CE" and l["qty"]>0 and l["exp_key"]=="next"]
        lp=[i for i,l in enumerate(legs) if l["opt"]=="PE" and l["qty"]>0 and l["exp_key"]=="next"]

        if ce_short:
            i=ce_short[0]; d=option_delta(snap_t,s,cur,t,"CE",legs[i]["strike"])
            if d is not None and d<=0.08 and state["ce_decay"]==0:
                if replace_leg(i,"CE","cur",0.20): state["ce_decay"]=1
            elif d is not None and d<=0.08 and state["ce_decay"]==1 and state["ce_rev"]==0:
                if replace_leg(i,"CE","cur",0.20): state["ce_decay"]=2
            elif d is not None and d>=0.50 and state["ce_decay"]==1 and state["ce_rev"]==0:
                if replace_leg(i,"CE","cur",0.40): state["ce_rev"]=1

        if pe_short:
            i=pe_short[0]; d=option_delta(snap_t,s,cur,t,"PE",legs[i]["strike"])
            if d is not None and d>=-0.08 and state["pe_decay"]==0:
                if replace_leg(i,"PE","cur",-0.20): state["pe_decay"]=1
            elif d is not None and d>=-0.08 and state["pe_decay"]==1 and state["pe_rev"]==0:
                if replace_leg(i,"PE","cur",-0.20): state["pe_decay"]=2
            elif d is not None and d<=-0.50 and state["pe_decay"]==1 and state["pe_rev"]==0:
                if replace_leg(i,"PE","cur",-0.40): state["pe_rev"]=1

        if lc and state["lc_spike"]==0:
            i=lc[0]; d=option_delta(snap_t,s,nxt,t,"CE",legs[i]["strike"])
            if d is not None and d>=0.40:
                old=legs[i]
                px=quote(snap_t,old["opt"],old["strike"])
                if px is not None:
                    ledger.append({"ts":t,"side":"sell","price":px,"qty":old["qty"],"lot":lot,"opt":"CE"})
                    curstrike=old["strike"]
                    q1=quote(snap_t,"CE",curstrike)
                    newstrike=nearest_delta_strike(snap_t,s,nxt,t,"CE",0.25)
                    q2=quote(snap_t,"CE",newstrike) if newstrike is not None else None
                    if q2 is not None:
                        # short 2 current-week at same long strike + buy 2 next-week 0.25D
                        legs[lc[0]]=make_leg("CE",newstrike,2,"next")
                        ledger.append({"ts":t,"side":"buy","price":q2,"qty":2,"lot":lot,"opt":"CE"})
                        ledger.append({"ts":t,"side":"sell","price":q1,"qty":2,"lot":lot,"opt":"CE"})
                        state["lc_spike"]=1

        if lp and state["lp_spike"]==0:
            i=lp[0]; d=option_delta(snap_t,s,nxt,t,"PE",legs[i]["strike"])
            if d is not None and d<=-0.40:
                old=legs[i]; px=quote(snap_t,old["opt"],old["strike"])
                if px is not None:
                    ledger.append({"ts":t,"side":"sell","price":px,"qty":old["qty"],"lot":lot,"opt":"PE"})
                    newstrike=nearest_delta_strike(snap_t,s,nxt,t,"PE",-0.25)
                    q2=quote(snap_t,"PE",newstrike) if newstrike is not None else None
                    q1=quote(snap_t,"PE",old["strike"])
                    if q2 is not None and q1 is not None:
                        legs[i]=make_leg("PE",newstrike,2,"next")
                        ledger.append({"ts":t,"side":"buy","price":q2,"qty":2,"lot":lot,"opt":"PE"})
                        ledger.append({"ts":t,"side":"sell","price":q1,"qty":2,"lot":lot,"opt":"PE"})
                        state["lp_spike"]=1

        if t>=end:
            break

    # Force final exits at 15:15 expiry day.
    exit_snap=data[data.timestamp==end]
    if exit_snap.empty:
        # fallback last available observation on expiry day before/at close
        day=data[(data.timestamp.dt.normalize()==cur.normalize())&(data.timestamp<=end)]
        if day.empty:return None
        extts=day.timestamp.max(); exit_snap=day[day.timestamp==extts]; end=extts
    for leg in legs:
        q=quote(exit_snap,leg["opt"],leg["strike"])
        if q is None:return None
        ledger.append({"ts":end,"side":"buy" if leg["qty"]<0 else "sell","price":q,"qty":leg["qty"],"lot":lot,"opt":leg["opt"]})
    gross,orders=pnl_from_ledger(ledger)
    cost=charges(orders,lot,1.0)
    cost50=charges(orders,lot,1.5)
    vs=vix_state(vix,ts)
    if vs is None:return None
    return {
        "expiry":str(cur.date()),"entry_ts":str(ts),"year":ts.year,
        "net":gross-cost,"net50":gross-cost50,"gross":gross,"cost":cost,
        "vix":vs["vix"],"vix_state":vs["level_state"],"dvix":vs["dvix"],
        "adjustments":len(ledger)-4-4,"legs_final":len(legs)
    }

def main():
    index=load_parquet("index/NIFTY.parquet")
    index=index[["timestamp","close"]].rename(columns={"close":"spot"}).drop_duplicates("timestamp").sort_values("timestamp")
    vix=load_vix()
    expiries=expiry_dates()
    expiries=[e for e in expiries if START<=e<=END]
    rows=[]; errs=[]
    for e in expiries:
        try:
            data=load_parquet(f"options/NIFTY/{e.strftime('%Y-%m-%d')}.parquet")
            z=replay_expiry(index,vix,data,e,expiries)
            if z is not None:rows.append(z)
        except Exception as ex:
            errs.append({"expiry":str(e.date()),"error":repr(ex)})
    df=pd.DataFrame(rows)
    if not df.empty:
        df.to_csv(OUT/"tt02_trades.csv",index=False)
        summary=[]
        for split_name,lo,hi in [("DEV",None,DEV_END),("VAL",DEV_END,VAL_END),("HOLD",VAL_END,None)]:
            z=df[(df.expiry.map(pd.Timestamp)>=START) & (df.expiry.map(pd.Timestamp)<=END)]
            if lo is not None:z=z[z.expiry.map(pd.Timestamp)>lo]
            if hi is not None:z=z[z.expiry.map(pd.Timestamp)<=hi]
            summary.append({"split":split_name,"trades":len(z),"net":float(z.net.sum()) if len(z) else 0.0,"net50":float(z.net50.sum()) if len(z) else 0.0,"mean":float(z.net.mean()) if len(z) else 0.0})
        pd.DataFrame(summary).to_csv(OUT/"split_summary.csv",index=False)
        by=df.groupby("vix_state").agg(trades=("net","size"),net=("net","sum"),net50=("net50","sum"),mean=("net","mean"),win_rate=("net",lambda x:(x>0).mean())).reset_index()
        by.to_csv(OUT/"vix_summary.csv",index=False)
        final={"strategy":"TT-02","trades":len(df),"net":float(df.net.sum()),"net50":float(df.net50.sum()),"by_vix":by.to_dict("records")}
    else:
        final={"strategy":"TT-02","trades":0,"net":0,"net50":0,"by_vix":[]}
    (OUT/"summary.json").write_text(json.dumps(final,indent=2))
    pd.DataFrame(errs).to_csv(OUT/"data_errors.csv",index=False)
    print(json.dumps(final,indent=2))
if __name__=="__main__":main()
