import json, math, os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.special import ndtr

from phase43_vix_strategy_sweep import (
    TZ, START, END, DEV_END, VAL_END,
    load_parquet, load_vix, vix_state,
    charges, exec_px, lot_size_for_expiry
)

OUT = Path("results/phase50b/tt02_calendar_replay")
OUT.mkdir(parents=True, exist_ok=True)

R = 0.0
ENTRY_START = pd.Timestamp("09:20").time()
ENTRY_END = pd.Timestamp("15:00").time()
EXIT_TIME = pd.Timestamp("15:15").time()

INDEX_CACHE = None
INDEX_SPOT = None
INDEX_DAY_TIMES = None
EXPIRY_DATES = None
OPTION_CACHE = {}
SNAP_CACHE = {}
DELTA_CACHE = {}

def clean_ts(df):
    x = df.copy()
    x["timestamp"] = pd.to_datetime(x["timestamp"])
    if x["timestamp"].dt.tz is None:
        x["timestamp"] = x["timestamp"].dt.tz_localize(TZ)
    else:
        x["timestamp"] = x["timestamp"].dt.tz_convert(TZ)
    x["strike"] = pd.to_numeric(x["strike"], errors="coerce")
    x["close"] = pd.to_numeric(x["close"], errors="coerce")
    x["option_type"] = x["option_type"].astype(str).str.upper()
    x=x.dropna(subset=["timestamp","strike","close"]).sort_values(["timestamp","option_type","strike"])
    # Performance-only index: scientific timestamps/quotes are unchanged.
    return x.set_index("timestamp",drop=False).sort_index()

def get_index():
    global INDEX_CACHE, INDEX_SPOT, INDEX_DAY_TIMES
    if INDEX_CACHE is None:
        x=load_parquet("index/NIFTY.parquet")
        x=x[["timestamp","close"]].rename(columns={"close":"spot"}).drop_duplicates("timestamp").sort_values("timestamp")
        INDEX_CACHE=x
        INDEX_SPOT={pd.Timestamp(r.timestamp): float(r.spot) for r in x.itertuples(index=False)}
        INDEX_DAY_TIMES={
            pd.Timestamp(day): g["timestamp"].tolist()
            for day,g in x.groupby(x["timestamp"].dt.normalize(), sort=True)
        }
    return INDEX_CACHE

def get_expiries():
    global EXPIRY_DATES
    if EXPIRY_DATES is None:
        p=Path("results/phase43_vix/strategy_trade_matrix_all_splits.csv")
        z=pd.read_csv(p,usecols=["expiry"])
        EXPIRY_DATES=sorted({pd.Timestamp(x).tz_localize(TZ) for x in z["expiry"].dropna()})
    return EXPIRY_DATES

def get_option(e):
    if e not in OPTION_CACHE:
        OPTION_CACHE[e]=clean_ts(load_parquet(f"options/NIFTY/{e.strftime('%Y-%m-%d')}.parquet"))
    # retain a small rolling cache
    for old in list(OPTION_CACHE):
        if old < e-pd.Timedelta(days=14):
            OPTION_CACHE.pop(old,None)
    return OPTION_CACHE[e]

def current_expiry(day):
    d=pd.Timestamp(day).normalize()
    for e in get_expiries():
        if e.normalize()>=d:
            return e
    return None

def next_expiry(cur):
    ex=get_expiries()
    try:i=ex.index(cur)
    except ValueError:return None
    return ex[i+1] if i+1<len(ex) else None

def snap(df,ts):
    # Timestamp index avoids full-frame boolean scans on every 1-minute observation.
    t=pd.Timestamp(ts)
    try:
        z=df.loc[t]
    except KeyError:
        return df.iloc[0:0]
    if isinstance(z,pd.Series):
        z=z.to_frame().T
    return z.drop_duplicates(["option_type","strike"],keep="last")
def quote(z,opt,strike):
    q=z[(z.option_type==opt)&(np.isclose(z.strike,float(strike),rtol=0,atol=1e-8))]
    return None if q.empty else float(q.iloc[-1].close)

def norm_cdf(x):
    return 0.5*(1.0+math.erf(x/math.sqrt(2.0)))

def bs_price(s,k,t,sigma,call):
    if t<=0:return max(s-k,0.0) if call else max(k-s,0.0)
    if sigma<=0:return math.exp(-R*t)*max(s-k,0.0) if call else math.exp(-R*t)*max(k-s,0.0)
    q=math.sqrt(t); d1=(math.log(s/k)+(R+0.5*sigma*sigma)*t)/(sigma*q); d2=d1-sigma*q
    return s*norm_cdf(d1)-k*math.exp(-R*t)*norm_cdf(d2) if call else k*math.exp(-R*t)*norm_cdf(-d2)-s*norm_cdf(-d1)

def bs_delta(s,k,t,sigma,call):
    if t<=0:return 1.0 if call and s>k else 0.0 if call else -1.0 if s<k else 0.0
    d1=(math.log(s/k)+(R+0.5*sigma*sigma)*t)/(sigma*math.sqrt(t))
    return norm_cdf(d1) if call else norm_cdf(d1)-1.0

def implied_vol(price,s,k,t,call):
    if not np.isfinite(price) or price<=0 or s<=0 or k<=0 or t<=0:return None
    intrinsic=math.exp(-R*t)*max(s-k,0.0) if call else math.exp(-R*t)*max(k-s,0.0)
    upper=s if call else k*math.exp(-R*t)
    if price<=intrinsic+1e-8 or price>=upper:return None
    sigma=max(0.05,min(2.5,math.sqrt(2.0*math.pi/max(t,1e-12))*price/max(s,1e-9)))
    for _ in range(5):
        q=math.sqrt(t)
        d1=(math.log(s/k)+(R+0.5*sigma*sigma)*t)/(sigma*q)
        d2=d1-sigma*q
        model=s*norm_cdf(d1)-k*math.exp(-R*t)*norm_cdf(d2) if call else k*math.exp(-R*t)*norm_cdf(-d2)-s*norm_cdf(-d1)
        diff=model-price
        if abs(diff)<1e-6:return sigma
        vega=s*math.exp(-0.5*d1*d1)/math.sqrt(2*math.pi)*q
        if vega<1e-10:break
        sigma=max(1e-5,min(8.0,sigma-diff/vega))
    # Rare fallback preserves the same Black-Scholes root definition.
    try:return brentq(lambda x:bs_price(s,k,t,x,call)-price,1e-5,8.0,maxiter=40)
    except Exception:return None
def option_delta(opt_price,spot,strike,ts,expiry,opt):
    t=max((expiry.normalize()+pd.Timedelta(hours=15,minutes=30)-pd.Timestamp(ts)).total_seconds(),1.0)/(365*24*3600)
    iv=implied_vol(float(opt_price),float(spot),float(strike),t,opt=="CE")
    return None if iv is None else bs_delta(float(spot),float(strike),t,iv,opt=="CE")

def delta_cached(z,spot,strike,ts,expiry,opt):
    key=(str(pd.Timestamp(ts)),str(expiry.date()),opt,float(strike))
    if key not in DELTA_CACHE:
        q=quote(z,opt,strike)
        DELTA_CACHE[key]=None if q is None else option_delta(q,spot,strike,ts,expiry,opt)
    return DELTA_CACHE[key]

def nearest_delta(z,spot,ts,expiry,opt,target):
    q=z[z.option_type==opt][["strike","close"]].drop_duplicates("strike")
    if q.empty:return None
    strikes=q["strike"].to_numpy(dtype=float)
    prices=q["close"].to_numpy(dtype=float)
    t=max((expiry.normalize()+pd.Timedelta(hours=15,minutes=30)-pd.Timestamp(ts)).total_seconds(),1.0)/(365*24*3600)
    valid=(prices>0)&np.isfinite(prices)&(strikes>0)&np.isfinite(strikes)&(spot>0)
    if not np.any(valid):return None
    k=strikes[valid]; p=prices[valid]
    call=(opt=="CE")
    intrinsic=np.maximum(spot-k,0.0) if call else np.maximum(k-spot,0.0)
    upper=np.full_like(k,spot) if call else k
    valid2=(p>intrinsic+1e-8)&(p<upper)
    if not np.any(valid2):return None
    k=k[valid2]; p=p[valid2]
    sigma=np.clip(np.sqrt(2*np.pi/max(t,1e-12))*p/max(spot,1e-9),0.05,2.5)
    sqrt_t=math.sqrt(t); disc=np.exp(-R*t)
    for _ in range(7):
        d1=(np.log(spot/k)+(R+0.5*sigma*sigma)*t)/(sigma*sqrt_t)
        d2=d1-sigma*sqrt_t
        if call:
            model=spot*ndtr(d1)-k*disc*ndtr(d2)
        else:
            model=k*disc*ndtr(-d2)-spot*ndtr(-d1)
        diff=model-p
        vega=spot*np.exp(-0.5*d1*d1)/math.sqrt(2*np.pi)*sqrt_t
        good=vega>1e-10
        if not np.any(good):break
        sigma=np.where(good,np.clip(sigma-diff/vega,1e-5,8.0),sigma)
    d1=(np.log(spot/k)+(R+0.5*sigma*sigma)*t)/(sigma*sqrt_t)
    delta=ndtr(d1) if call else ndtr(d1)-1.0
    err=np.abs(delta-target)
    j=int(np.nanargmin(err))
    return float(k[j])

def make_position(trade_id,ts,spot,cur,nxt,sc,sp,lc,lp,lot):
    return {
        "trade_id":trade_id,"entry_ts":ts,"entry_spot":spot,
        "cur":cur,"nxt":nxt,"lot":lot,
        "ce_decay":0,"ce_rev":0,"pe_decay":0,"pe_rev":0,"lc_spike":0,"lp_spike":0,
        "legs":{
            "short_ce":{"opt":"CE","strike":sc,"qty":-1,"exp":"cur"},
            "short_pe":{"opt":"PE","strike":sp,"qty":-1,"exp":"cur"},
            "long_ce":{"opt":"CE","strike":lc,"qty":2,"exp":"nxt"},
            "long_pe":{"opt":"PE","strike":lp,"qty":2,"exp":"nxt"},
        },
        "ledger":[]
    }

def add_order(pos,ts,side,price,qty,opt,leg,phase):
    pos["ledger"].append({"ts":ts,"side":side,"price":float(price),"qty":int(qty),"lot":pos["lot"],"opt":opt,"leg":leg,"phase":phase})

def close_open_replace(pos,name,target_frame,target_exp,opt,target_delta,ts,spot,phase):
    old=pos["legs"][name]
    old_frame=get_option(pos["cur"]) if old["exp"]=="cur" else get_option(pos["nxt"])
    old_px=quote(snap(old_frame,ts),old["opt"],old["strike"])
    if old_px is None:return False
    new_strike=nearest_delta(target_frame,spot,ts,target_exp,opt,target_delta)
    if new_strike is None:return False
    new_px=quote(snap(target_frame,ts),opt,new_strike)
    if new_px is None:return False
    add_order(pos,ts,"buy" if old["qty"]<0 else "sell",old_px,old["qty"],old["opt"],name,phase+"_close")
    add_order(pos,ts,"sell" if old["qty"]<0 else "buy",new_px,old["qty"],opt,name,phase+"_open")
    pos["legs"][name]={"opt":opt,"strike":float(new_strike),"qty":old["qty"],"exp":"cur" if target_exp==pos["cur"] else "nxt"}
    return True

def finalize(pos,ts,cur_frame,nxt_frame):
    for name,leg in pos["legs"].items():
        frame=cur_frame if leg["exp"]=="cur" else nxt_frame
        px=quote(snap(frame,ts),leg["opt"],leg["strike"])
        if px is None:return None
        add_order(pos,ts,"sell" if leg["qty"]>0 else "buy",px,leg["qty"],leg["opt"],name,"exit")
    gross=0.0; orders=[]
    for r in pos["ledger"]:
        ep=exec_px(r["price"],r["side"])
        gross += (-1 if r["side"]=="buy" else 1)*ep*abs(r["qty"])*r["lot"]
        orders.append((pd.Timestamp(r["ts"]),r["side"],ep*abs(r["qty"])))
    cost=charges(orders,pos["lot"],1.0)
    cost50=charges(orders,pos["lot"],1.5)
    vs=vix_state(VIX,pos["entry_ts"])
    return {
        "trade_id":pos["trade_id"],"entry_ts":str(pos["entry_ts"]),"expiry":str(pos["cur"].date()),
        "entry_spot":pos["entry_spot"],"lot":pos["lot"],"gross":gross,"cost":cost,
        "net":gross-cost,"net50":gross-cost50,
        "vix":vs["vix"] if vs else np.nan,"vix_state":vs["level_state"] if vs else None,
        "adjustments":sum(1 for x in pos["ledger"] if x["phase"].endswith("_open"))-4,
        "entry_ce_strike":pos["ledger"][0]["price"] if False else pos["legs"]["short_ce"]["strike"],
    }

VIX=None

def main():
    global VIX
    idx=get_index()
    VIX=load_vix()
    expiries=get_expiries()
    days=sorted(INDEX_DAY_TIMES)
    position=None; trade_id=1; rows=[]; errors=[]

    for day in days:
        day=pd.Timestamp(day)
        if day<START.normalize() or day>END.normalize():continue
        cur_for_day=current_expiry(day)
        if cur_for_day is None:continue
        nxt_for_day=next_expiry(cur_for_day)
        if nxt_for_day is None:continue
        cur_frame=get_option(cur_for_day); nxt_frame=get_option(nxt_for_day)

        ts_list=[
            t for t in INDEX_DAY_TIMES.get(day.normalize(), [])
            if ENTRY_START <= pd.Timestamp(t).time() <= EXIT_TIME
        ]
        for ts in ts_list:
            ts=pd.Timestamp(ts)
            spot=INDEX_SPOT.get(ts)
            if spot is None: continue
            scur=snap(cur_frame,ts); snxt=snap(nxt_frame,ts)

            if position is None and ts.time()<=ENTRY_END:
                if not scur.empty and not snxt.empty:
                    sc=nearest_delta(scur,spot,ts,cur_for_day,"CE",0.20)
                    sp=nearest_delta(scur,spot,ts,cur_for_day,"PE",-0.20)
                    lc=nearest_delta(snxt,spot,ts,nxt_for_day,"CE",0.10)
                    lp=nearest_delta(snxt,spot,ts,nxt_for_day,"PE",-0.10)
                    entry_quotes=(quote(scur,"CE",sc),quote(scur,"PE",sp),quote(snxt,"CE",lc),quote(snxt,"PE",lp)) if None not in (sc,sp,lc,lp) else (None,None,None,None)
                    if None not in entry_quotes:
                        lot=lot_size_for_expiry(cur_for_day)
                        position=make_position(trade_id,ts,spot,cur_for_day,nxt_for_day,sc,sp,lc,lp,lot)
                        add_order(position,ts,"sell",entry_quotes[0],-1,"CE","short_ce","entry")
                        add_order(position,ts,"sell",entry_quotes[1],-1,"PE","short_pe","entry")
                        add_order(position,ts,"buy",entry_quotes[2],2,"CE","long_ce","entry")
                        add_order(position,ts,"buy",entry_quotes[3],2,"PE","long_pe","entry")
                        trade_id+=1

            if position is None:continue

            cur=position["cur"]; nxt=position["nxt"]
            if cur.normalize()!=cur_for_day.normalize():
                # Current-week expiry rolled only after the prior position has exited.
                continue

            # Repair triggers are evaluated on current observed minute closes.
            dc=delta_cached(scur,spot,position["legs"]["short_ce"]["strike"],ts,cur,"CE") if not scur.empty else None
            if dc is not None:
                if dc<=0.08 and position["ce_decay"]==0:
                    if close_open_replace(position,"short_ce",scur,cur,"CE",0.20,ts,spot,"ce_decay1"):position["ce_decay"]=1
                elif dc<=0.08 and position["ce_decay"]==1 and position["ce_rev"]==0:
                    if close_open_replace(position,"short_ce",scur,cur,"CE",0.20,ts,spot,"ce_decay2"):position["ce_decay"]=2
                elif dc>=0.50 and position["ce_decay"]==1 and position["ce_rev"]==0:
                    if close_open_replace(position,"short_ce",scur,cur,"CE",0.40,ts,spot,"ce_rev"):position["ce_rev"]=1

            dp=delta_cached(scur,spot,position["legs"]["short_pe"]["strike"],ts,cur,"PE") if not scur.empty else None
            if dp is not None:
                if dp>=-0.08 and position["pe_decay"]==0:
                    if close_open_replace(position,"short_pe",scur,cur,"PE",-0.20,ts,spot,"pe_decay1"):position["pe_decay"]=1
                elif dp>=-0.08 and position["pe_decay"]==1 and position["pe_rev"]==0:
                    if close_open_replace(position,"short_pe",scur,cur,"PE",-0.20,ts,spot,"pe_decay2"):position["pe_decay"]=2
                elif dp<=-0.50 and position["pe_decay"]==1 and position["pe_rev"]==0:
                    if close_open_replace(position,"short_pe",scur,cur,"PE",-0.40,ts,spot,"pe_rev"):position["pe_rev"]=1

            dlc=delta_cached(snxt,spot,position["legs"]["long_ce"]["strike"],ts,nxt,"CE") if not snxt.empty else None
            if dlc is not None and dlc>=0.40 and position["lc_spike"]==0:
                if close_open_replace(position,"long_ce",snxt,nxt,"CE",0.25,ts,spot,"lc_spike"):position["lc_spike"]=1

            dlp=delta_cached(snxt,spot,position["legs"]["long_pe"]["strike"],ts,nxt,"PE") if not snxt.empty else None
            if dlp is not None and dlp<=-0.40 and position["lp_spike"]==0:
                if close_open_replace(position,"long_pe",snxt,nxt,"PE",-0.25,ts,spot,"lp_spike"):position["lp_spike"]=1

            if cur.normalize()==day.normalize() and ts.time()>=EXIT_TIME:
                z=finalize(position,ts,cur_frame,nxt_frame)
                if z is None:
                    errors.append({"trade_id":position["trade_id"],"expiry":str(cur.date()),"error":"missing exact 15:15 exit quote"})
                else:
                    rows.append(z)
                position=None

        if day.dayofweek==0 or day.day==1:
            pd.DataFrame(rows).to_csv(OUT/"progress_trades.csv",index=False)

    df=pd.DataFrame(rows)
    df.to_csv(OUT/"tt02_trades.csv",index=False)
    pd.DataFrame(errors).to_csv(OUT/"data_errors.csv",index=False)
    result={"strategy":"TT-02","trades":len(df),
            "net":float(df.net.sum()) if not df.empty else 0.0,
            "net50":float(df.net50.sum()) if not df.empty else 0.0,
            "by_vix":df.groupby("vix_state").agg(trades=("net","size"),net=("net","sum"),net50=("net50","sum"),mean=("net","mean"),win_rate=("net",lambda x:(x>0).mean())).reset_index().to_dict("records") if not df.empty else []}
    (OUT/"summary.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()

# F50B-005: corrected v2 replay uses the 09:20-15:00 flat-entry gate, source runtime initialization, and exact 15:15 expiry exit.

# F50B-005 fixed: workflow installs matplotlib for shared Phase-43 import dependency.

# F50B-006 fixed: numerical TT02 workflow now installs matplotlib too.

# F50B-011: performance-only optimization. Option frames are timestamp-indexed and implied-vol Newton iterations are reduced with the same BS root and rare Brent fallback.

# F50B-012: vectorized nearest-delta scan; preserves the same BS-implied-volatility/European-delta definition while removing per-strike Python loops.

# F50B-018 fallback performance-only patch: pre-index NIFTY spot and per-day timestamps to remove repeated full-index equality scans.
# Scientific definitions, quote selection, BS implied-volatility root, European delta, state machine, costs and exits are unchanged.
