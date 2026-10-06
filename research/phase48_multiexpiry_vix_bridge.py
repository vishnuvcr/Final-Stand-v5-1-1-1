import json, math, os
from pathlib import Path
import numpy as np
import pandas as pd
import duckdb
from huggingface_hub import hf_hub_download

TZ="Asia/Kolkata"
HF_REPO="rissin/nse-options-intraday"
DATA_DIR=Path("data/phase48_bridge")
OUT=Path("results/phase48_multiexpiry")
OUT.mkdir(parents=True, exist_ok=True)
YEARS=[2024,2025,2026]
START=pd.Timestamp("2024-10-01",tz=TZ)
DEV_END=pd.Timestamp("2024-12-31",tz=TZ)
VAL_END=pd.Timestamp("2025-12-31",tz=TZ)

STATES=["ALL","LOW","NORMAL","HIGH","SPIKE","FALLING","RISING","HIGH_RISING"]

def as_tz(x):
    t=pd.Timestamp(x)
    return t.tz_localize(TZ) if t.tzinfo is None else t.tz_convert(TZ)

def lot_size_for_expiry(expiry):
    e=as_tz(expiry)
    if e < pd.Timestamp("2024-05-02",tz=TZ): return 75
    if e < pd.Timestamp("2024-12-26",tz=TZ): return 50
    if e <= pd.Timestamp("2024-12-26",tz=TZ): return 25
    if e <= pd.Timestamp("2025-01-23",tz=TZ): return 75
    if e == pd.Timestamp("2025-01-30",tz=TZ): return 25
    if e < pd.Timestamp("2026-01-06",tz=TZ): return 75
    return 65

def fee_rates(d):
    d=as_tz(d)
    stt=0.0015 if d>=pd.Timestamp("2026-04-01",tz=TZ) else 0.0010 if d>=pd.Timestamp("2024-10-01",tz=TZ) else 0.000625
    txn,ipft=((0.000355299,0.000000001) if d>=pd.Timestamp("2026-03-01",tz=TZ)
             else (0.0003503,0.000005) if d>=pd.Timestamp("2024-10-01",tz=TZ)
             else (0.000495,0.000005))
    return stt,txn,0.000001,ipft,0.00003

def exec_px(px,action):
    return max(0.0,float(px)+(0.05 if action=="buy" else -0.05))

def charges(orders,lot,mult=1.0):
    brokerage=10.0*mult*len(orders)
    exchange=sebi=ipft=stt=stamp=0.0
    for d,side,px in orders:
        sr,tx,se,ip,sd=fee_rates(d)
        turnover=float(px)*lot
        exchange+=tx*turnover*mult
        sebi+=se*turnover*mult
        ipft+=ip*turnover*mult
        if side=="sell": stt+=sr*turnover*mult
        else: stamp+=sd*turnover*mult
    gst=0.18*(brokerage+exchange+sebi+ipft)
    return brokerage+exchange+sebi+ipft+stt+stamp+gst

def download_year(y):
    return hf_hub_download(repo_id=HF_REPO,filename=f"upstox_intraday/NIFTY/NIFTY_{y}.parquet",
                            repo_type="dataset",token=os.getenv("HF_TOKEN") or None)

FILES={}

def get_file(y):
    if y not in FILES: FILES[y]=download_year(y)
    return FILES[y]

def duck(sql):
    con=duckdb.connect()
    try:
        return con.execute(sql).df()
    finally:
        con.close()


SCHEMAS={}

def get_schema(y):
    if y in SCHEMAS: return SCHEMAS[y]
    p=get_file(y)
    z=duck(f"DESCRIBE SELECT * FROM read_parquet('{p}')")
    cols=list(z['column_name'])
    SCHEMAS[y]=cols
    return cols

def pick_col(cols,candidates):
    low={x.lower():x for x in cols}
    for c in candidates:
        if c.lower() in low: return low[c.lower()]
    return None

def norm_relation(y):
    p=get_file(y); cols=get_schema(y)
    ts=pick_col(cols,['timestamp','datetime','date_time'])
    expiry=pick_col(cols,['expiry','expiry_date'])
    strike=pick_col(cols,['strike'])
    typ=pick_col(cols,['option_type','type','side'])
    close=pick_col(cols,['close','close_price','market_price'])
    datec=pick_col(cols,['date','trade_date'])
    spot=pick_col(cols,['spot_price','underlying_spot','spot','underlying_price'])
    volume=pick_col(cols,['volume'])
    oi=pick_col(cols,['oi','open_interest'])
    required={'timestamp':ts,'expiry':expiry,'strike':strike,'option_type':typ,'close':close}
    missing=[k for k,v in required.items() if v is None]
    if missing: raise RuntimeError(f'F48-001 {y} missing required normalized columns: {missing}; actual={cols}')
    date_expr=f'CAST({datec} AS DATE)' if datec else f'CAST({ts} AS DATE)'
    spot_expr=f'CAST({spot} AS DOUBLE)' if spot else 'CAST(NULL AS DOUBLE)'
    vol_expr=f'CAST({volume} AS DOUBLE)' if volume else 'CAST(NULL AS DOUBLE)'
    oi_expr=f'CAST({oi} AS DOUBLE)' if oi else 'CAST(NULL AS DOUBLE)'
    return f"""(SELECT CAST({ts} AS TIMESTAMP) AS timestamp, {date_expr} AS date, CAST({expiry} AS DATE) AS expiry, CAST({strike} AS DOUBLE) AS strike, UPPER(CAST({typ} AS VARCHAR)) AS option_type, CAST({close} AS DOUBLE) AS close, {spot_expr} AS spot_price, {vol_expr} AS volume, {oi_expr} AS oi FROM read_parquet('{p}'))"""
def audit_dataset():
    out={}
    for y in YEARS:
        p=get_file(y); cols=get_schema(y)
        mapping={
            'timestamp':pick_col(cols,['timestamp','datetime','date_time']),
            'expiry':pick_col(cols,['expiry','expiry_date']),
            'strike':pick_col(cols,['strike']),
            'option_type':pick_col(cols,['option_type','type','side']),
            'close':pick_col(cols,['close','close_price','market_price']),
            'spot_price':pick_col(cols,['spot_price','underlying_spot','spot','underlying_price']),
            'date':pick_col(cols,['date','trade_date'])}
        if any(mapping[k] is None for k in ['timestamp','expiry','strike','option_type','close']):
            raise RuntimeError(f'F48-001 {y} missing required normalized columns; actual={cols}')
        rel=norm_relation(y)
        mn=duck(f'SELECT MIN(date) AS min_date, MAX(date) AS max_date, COUNT(*) AS rows FROM {rel}')
        out[str(y)]={'path':p,'columns':sorted(cols),'mapping':mapping,'min_date':str(mn.iloc[0].min_date),'max_date':str(mn.iloc[0].max_date),'rows':int(mn.iloc[0].rows)}
    (OUT/'data_audit.json').write_text(json.dumps(out,default=str,indent=2))
    return out
def expiries_all():
    rows=[]
    for y in YEARS:
        rel=norm_relation(y)
        z=duck(f"SELECT DISTINCT expiry FROM {rel} WHERE date>='2024-10-01'")
        rows.extend(z['expiry'].tolist())
    return sorted(set(pd.Timestamp(x,tz=TZ) for x in rows))
def monthly_expiries(expiries):
    z=pd.DataFrame({"expiry":sorted(expiries)})
    z["ym"]=z["expiry"].dt.tz_localize(None).dt.to_period("M").astype(str)
    return list(z.groupby("ym").expiry.max().sort_values())

def trade_days_for_year(y):
    rel=norm_relation(y)
    z=duck(f"SELECT DISTINCT date AS d FROM {rel} ORDER BY 1")
    return [pd.Timestamp(x,tz=TZ) for x in z['d'].tolist()]
def all_trade_days():
    a=[]
    for y in YEARS: a.extend(trade_days_for_year(y))
    return sorted(set(a))

def first_trade_after(days,day):
    for d in days:
        if d>day: return d
    return None

def fourth_before(days,expiry):
    prior=[d for d in days if d<expiry.normalize()]
    return prior[-4] if len(prior)>=4 else None

def prior_vix(vix,entry):
    z=vix[vix.date < entry.normalize()]
    if z.empty: return None
    return z.iloc[-1]

def vix_states(vix,entry):
    cur=prior_vix(vix,entry)
    if cur is None or not np.isfinite(cur.vix): return []
    hist=vix[vix.date < entry.normalize()].iloc[:-1]
    if len(hist)<60: return []
    q25,q75=hist.vix.quantile(.25),hist.vix.quantile(.75)
    d=hist.dvix.dropna()
    out=["ALL"]
    out.append("LOW" if cur.vix<=q25 else "HIGH" if cur.vix>=q75 else "NORMAL")
    if len(d)>=20 and np.isfinite(cur.dvix):
        if cur.dvix>=d.quantile(.90): out.append("RISING")
        if cur.dvix<=d.quantile(.10): out.append("FALLING")
    if len(d)>=20 and np.isfinite(cur.dvix) and cur.dvix>=d[d>0].quantile(.90) if (d>0).sum()>=20 else False:
        out.append("SPIKE")
    if "HIGH" in out and "RISING" in out: out.append("HIGH_RISING")
    return sorted(set(out))

def load_vix():
    x=pd.read_csv("data/phase40_vix/india_vix.csv")
    dc=next(c for c in x.columns if c.lower()=="date")
    cc=next(c for c in x.columns if c.lower()=="close")
    x["date"]=pd.to_datetime(x[dc]).dt.tz_localize(TZ)
    x["vix"]=pd.to_numeric(x[cc],errors="coerce")
    x["dvix"]=x.vix.diff()
    return x[["date","vix","dvix"]].dropna().sort_values("date")

def sql_day(y,day,expiry=None,time=None):
    rel=norm_relation(y); ds=day.date().isoformat()
    wh=[f"date='{ds}'"]
    if expiry is not None: wh.append(f"expiry='{as_tz(expiry).date().isoformat()}'")
    if time is not None: wh.append(f"strftime(timestamp,'%H:%M')='{time}'")
    where=' AND '.join(wh)
    return duck(f"SELECT timestamp, expiry, strike, option_type, close, spot_price, volume, oi FROM {rel} WHERE {where} AND close IS NOT NULL")
def option_snapshot(day,expiry,time="10:00"):
    return sql_day(day.year,day,expiry,time)

def latest_exit(expiry,legs):
    y=as_tz(expiry).year; rel=norm_relation(y); ds=as_tz(expiry).date().isoformat()
    cond=[]
    for typ,strike,_ in legs:
        cond.append(f"(option_type='{typ}' AND abs(strike-{float(strike)})<1e-9)")
    where=' OR '.join(cond)
    z=duck(f"SELECT timestamp, option_type, strike, close FROM {rel} WHERE date='{ds}' AND timestamp>='{ds} 15:00:00' AND timestamp<='{ds} 15:29:59' AND ({where}) AND close IS NOT NULL ORDER BY timestamp")
    if z.empty:return None
    by={}
    for typ,strike,_ in legs:
        q=z[(z.option_type==typ)&np.isclose(z.strike,float(strike))]
        if q.empty:return None
        by[(typ,float(strike))]=q.set_index('timestamp').close
    common=None
    for s in by.values(): common=s.index if common is None else common.intersection(s.index)
    if common is None or len(common)==0:return None
    ts=max(common)
    return ts,[float(by[(typ,float(strike))].loc[ts]) for typ,strike,_ in legs]
def norm_cdf(x): return 0.5*(1+math.erf(x/math.sqrt(2)))

def bs_delta(spot,strike,T,sigma,typ):
    if min(spot,strike,T,sigma)<=0: return np.nan
    d1=(math.log(spot/strike)+0.5*sigma*sigma*T)/(sigma*math.sqrt(T))
    return norm_cdf(d1) if typ=="CE" else norm_cdf(d1)-1

def choose_delta(snap,spot,sigma,expiry,entry,typ,target):
    z=snap[snap.option_type==typ].dropna(subset=["close"]).copy()
    if z.empty: return None
    T=max((as_tz(expiry)-as_tz(entry)).total_seconds()/31536000,1e-6)
    tgt=target if typ=="CE" else -target
    z["delta"]=z.strike.map(lambda k:bs_delta(spot,float(k),T,sigma,typ))
    z=z.dropna(subset=["delta"]).copy()
    z["err"]=(z.delta-tgt).abs()
    if z.empty: return None
    return float(z.sort_values(["err","strike"]).iloc[0].strike)

def choose_parity(snap,spot):
    c=snap[snap.option_type=="CE"][["strike","close"]].rename(columns={"close":"ce"})
    p=snap[snap.option_type=="PE"][["strike","close"]].rename(columns={"close":"pe"})
    z=c.merge(p,on="strike")
    if z.empty:return None
    z["gap"]=(z.ce-z.pe).abs(); z["spot_gap"]=(z.strike-spot).abs()
    return float(z.sort_values(["gap","spot_gap"]).iloc[0].strike)

def choose_atm(snap,spot):
    z=snap.dropna(subset=["strike"])
    if z.empty:return None
    return float(min(z.strike.unique(),key=lambda k:abs(float(k)-spot)))

def build_trade(strategy,entry,expiry,legs,entry_px,exit_ts,exit_px,source_exactness,extra=None):
    lot=lot_size_for_expiry(expiry); gross=0.0; orders=[]
    for leg,ep,xp in zip(legs,entry_px,exit_px):
        typ,strike,qty=leg
        epx=exec_px(ep,"buy" if qty>0 else "sell")
        xpx=exec_px(xp,"buy" if qty<0 else "sell")
        gross+=qty*(xpx-epx)*lot
        orders += [(entry,"buy" if qty>0 else "sell",epx),(exit_ts,"buy" if qty<0 else "sell",xpx)]
    c=charges(orders,lot,1.0); c50=charges(orders,lot,1.5)
    r={"strategy":strategy,"entry":str(entry),"expiry":str(as_tz(expiry).date()),
       "exit_ts":str(exit_ts),"gross":gross,"cost":c,"net":gross-c,"net50":gross-c50,
       "lot":lot,"legs":len(legs),"source_exactness":source_exactness}
    if extra:r.update(extra)
    return r

def trade_b1(expiry,next_expiry,days,vix):
    entry_day=fourth_before(days,expiry)
    if entry_day is None:return None
    entry=entry_day+pd.Timedelta(hours=10)
    cur=option_snapshot(entry_day,expiry); nxt=option_snapshot(entry_day,next_expiry)
    if cur.empty or nxt.empty:return None
    spot=pd.concat([cur,nxt]).spot_price.dropna()
    if spot.empty:return None
    s=float(spot.median()); ac=choose_atm(cur,s); an=choose_atm(nxt,s)
    if ac is None or an is None:return None
    legs=[("CE",ac,-1),("PE",ac,-1),("CE",an,1),("PE",an,1)]
    eps=[]
    for typ,strike,q in legs:
        z=cur if strike==ac and typ in ("CE","PE") and q<0 else nxt
        row=z[(z.option_type==typ)&np.isclose(z.strike,strike)]
        if row.empty:return None
        eps.append(float(row.iloc[0].close))
    ex=latest_exit(expiry,legs)
    if ex is None:return None
    ts,xps=ex
    return build_trade("double_calendar_straddle",entry,expiry,legs,eps,ts,xps,"independent_multi_expiry")

def trade_b2(expiry,next_expiry,prev_month,days,vix):
    entry_day=first_trade_after(days,prev_month)
    if entry_day is None:return None
    entry=entry_day+pd.Timedelta(hours=10)
    cur=option_snapshot(entry_day,expiry); nxt=option_snapshot(entry_day,next_expiry)
    if cur.empty or nxt.empty:return None
    spot=pd.concat([cur,nxt]).spot_price.dropna()
    if spot.empty:return None
    s=float(spot.median()); pv=prior_vix(vix,entry)
    if pv is None:return None
    sigma=float(pv.vix)/100
    ce=choose_delta(cur,s,sigma,expiry,entry,"CE",.30)
    pe=choose_delta(cur,s,sigma,expiry,entry,"PE",.30)
    h=choose_parity(nxt,s)
    if any(x is None for x in [ce,pe,h]):return None
    legs=[("CE",ce,-1),("PE",pe,-1),("CE",h,1),("PE",h,1)]
    eps=[]
    for typ,strike,q in legs:
        z=cur if q<0 else nxt
        row=z[(z.option_type==typ)&np.isclose(z.strike,strike)]
        if row.empty:return None
        eps.append(float(row.iloc[0].close))
    ex=latest_exit(expiry,legs)
    if ex is None:return None
    ts,xps=ex
    return build_trade("monthly_wide_range_static",entry,expiry,legs,eps,ts,xps,"delta_proxy",{"delta_target":.30})

def trade_b3(expiry,next_expiry,prev_expiry,days,vix):
    entry_day=first_trade_after(days,prev_expiry)
    if entry_day is None:return None
    entry=entry_day+pd.Timedelta(hours=10)
    cur=option_snapshot(entry_day,expiry); nxt=option_snapshot(entry_day,next_expiry)
    if cur.empty or nxt.empty:return None
    spot=pd.concat([cur,nxt]).spot_price.dropna()
    if spot.empty:return None
    s=float(spot.median()); pv=prior_vix(vix,entry)
    if pv is None:return None
    sigma=float(pv.vix)/100
    atm=choose_atm(cur,s); p30=choose_delta(cur,s,sigma,expiry,entry,"PE",.30)
    c30=choose_delta(cur,s,sigma,expiry,entry,"CE",.30)
    nc30=choose_delta(nxt,s,sigma,next_expiry,entry,"CE",.30)
    if any(x is None for x in [atm,p30,c30,nc30]):return None
    legs=[("CE",atm,1),("PE",atm,-1),("PE",p30,1),("CE",c30,-1),("CE",nc30,-1)]
    eps=[]
    for i,(typ,strike,q) in enumerate(legs):
        z=cur if i<4 else nxt
        row=z[(z.option_type==typ)&np.isclose(z.strike,strike)]
        if row.empty:return None
        eps.append(float(row.iloc[0].close))
    ex=latest_exit(expiry,legs)
    if ex is None:return None
    ts,xps=ex
    return build_trade("covered_call_2_static_proxy",entry,expiry,legs,eps,ts,xps,"synthetic_future_proxy",{"delta_target":.30})

def split(entry):
    e=as_tz(entry)
    if e<=DEV_END:return "development"
    if e<=VAL_END:return "validation"
    return "holdout"

def summary_stats(g):
    a=g.net.to_numpy(float)
    c=np.cumsum(a); dd=float(np.max(np.maximum.accumulate(c)-c)) if len(c) else 0
    pos=a[a>0].sum(); neg=-a[a<0].sum()
    return {"trades":len(g),"net":float(a.sum()),"net50":float(g.net50.sum()),
            "mean_net":float(a.mean()) if len(a) else np.nan,
            "win_rate":float((a>0).mean()) if len(a) else np.nan,
            "max_dd":dd,"profit_factor":float(pos/neg) if neg>0 else np.inf}

def deterministic_p(a,b):
    if len(a)<2 or len(b)<2:return (np.nan,np.nan,np.nan)
    obs=float(a.mean()-b.mean()); rng=np.random.default_rng(4801)
    ia=rng.integers(0,len(a),(10000,len(a))); ib=rng.integers(0,len(b),(10000,len(b)))
    boots=a[ia].mean(axis=1)-b[ib].mean(axis=1)
    pooled=np.concatenate([a,b]); n=len(a); perms=[]
    for _ in range(10000):
        p=rng.permutation(pooled); perms.append(p[:n].mean()-p[n:].mean())
    return obs,float(np.quantile(boots,.025)),float(np.mean(np.asarray(perms)>=obs))


def run_preflight():
    audit=audit_dataset()
    days=all_trade_days()
    exps=expiries_all()
    monthly=monthly_expiries(exps)
    if len(days)<30 or len(exps)<20 or len(monthly)<6:
        raise RuntimeError("F48-006 insufficient independent dataset universe")
    checks=[]
    for e in monthly:
        if e < START: continue
        ne=next((x for x in monthly if x>e),None)
        if ne is None: continue
        entry_day=fourth_before(days,e)
        if entry_day is None: continue
        cur=option_snapshot(entry_day,e); nxt=option_snapshot(entry_day,ne)
        checks.append({"expiry":str(e.date()),"entry_day":str(entry_day.date()),
                       "current_rows":int(len(cur)),"next_rows":int(len(nxt)),
                       "current_spot":bool(cur.spot_price.notna().any()),
                       "next_spot":bool(nxt.spot_price.notna().any())})
    z=pd.DataFrame(checks)
    multi=int(((z.current_rows>0)&(z.next_rows>0)).sum())
    result={"audit":audit,"trade_days":len(days),"expiries":len(exps),
            "monthly_expiries":len(monthly),"monthly_checks":len(z),
            "multi_expiry_entry_checks":multi}
    z.to_csv(OUT/"preflight_monthly_checks.csv",index=False)
    (OUT/"preflight.json").write_text(json.dumps(result,indent=2,default=str))
    if multi<3:
        raise RuntimeError("F48-007 independent dataset did not demonstrate multi-expiry entry coverage")
    return result

def main():
    if os.getenv("PHASE48_PREFLIGHT_ONLY")=="1":
        print(json.dumps(run_preflight(),indent=2,default=str))
        return
    audit=audit_dataset()
    days=all_trade_days()
    exps=expiries_all()
    if not days or not exps: raise RuntimeError("F48-002 no trade days/expiries")
    monthly=monthly_expiries(exps)
    weekly=sorted(exps)
    vix=load_vix()
    (OUT/"universe.json").write_text(json.dumps({
        "days":len(days),"expiries":len(exps),"monthly_expiries":len(monthly),
        "min_expiry":str(min(exps).date()),"max_expiry":str(max(exps).date())
    },indent=2))
    rows=[]; errors=[]
    for e in monthly:
        if not (e>START): continue
        ne=next((x for x in monthly if x>e),None)
        prev=next((x for x in reversed(monthly) if x<e),None)
        if ne is None: continue
        try:
            r=trade_b1(e,ne,days,vix)
            if r:
                r["split"]=split(r["entry"]); r["states"]=json.dumps(vix_states(vix,as_tz(r["entry"])))
                rows.append(r)
        except Exception as ex: errors.append({"strategy":"B1","expiry":str(e.date()),"error":repr(ex)})
        if prev is not None:
            try:
                r=trade_b2(e,ne,prev,days,vix)
                if r:
                    r["split"]=split(r["entry"]); r["states"]=json.dumps(vix_states(vix,as_tz(r["entry"])))
                    rows.append(r)
            except Exception as ex: errors.append({"strategy":"B2","expiry":str(e.date()),"error":repr(ex)})
    # weekly B3; use first trading day after prior expiry.
    exps_sorted=weekly
    for i,e in enumerate(exps_sorted):
        if e<START or i+1>=len(exps_sorted) or i==0: continue
        ne=exps_sorted[i+1]; prev=exps_sorted[i-1]
        try:
            r=trade_b3(e,ne,prev,days,vix)
            if r:
                r["split"]=split(r["entry"]); r["states"]=json.dumps(vix_states(vix,as_tz(r["entry"])))
                rows.append(r)
        except Exception as ex: errors.append({"strategy":"B3","expiry":str(e.date()),"error":repr(ex)})
    t=pd.DataFrame(rows)
    if t.empty: raise RuntimeError("F48-003 no trades generated")
    t.to_csv(OUT/"trade_matrix.csv",index=False)
    pd.DataFrame(errors).to_csv(OUT/"data_errors.csv",index=False)
    # Audit.
    dup=t.duplicated(["strategy","expiry","entry"],keep=False)
    if dup.any(): raise RuntimeError(f"F48-004 duplicate trade keys {int(dup.sum())}")
    if t["states"].apply(lambda x:"ALL" not in json.loads(x)).any(): raise RuntimeError("F48-005 missing ALL state")
    # Full state summary, including zero-trade states.
    rowsum=[]
    for (strategy,sp),g in t.groupby(["strategy","split"]):
        for state in STATES:
            a=g[g.states.apply(lambda x: state in json.loads(x))]
            st=summary_stats(a)
            st.update({"strategy":strategy,"split":sp,"state":state})
            rowsum.append(st)
    sm=pd.DataFrame(rowsum)
    sm.to_csv(OUT/"strategy_vix_summary.csv",index=False)
    # Validation inference where enough data exists.
    inf=[]
    val=t[t.split=="validation"]
    for strategy,g in val.groupby("strategy"):
        for state in STATES[1:]:
            a=g[g.states.apply(lambda x: state in json.loads(x))].net.to_numpy(float)
            b=g[g.states.apply(lambda x: state not in json.loads(x))].net.to_numpy(float)
            obs,lo,p=deterministic_p(a,b)
            inf.append({"strategy":strategy,"state":state,"n_active":len(a),"n_rest":len(b),
                        "diff_mean":obs,"ci_lo":lo,"p":p})
    iv=pd.DataFrame(inf)
    # Holm adjustment among all non-null p-values.
    valid=iv.p.notna(); ps=iv.loc[valid,"p"].to_numpy()
    order=np.argsort(ps); adj=np.ones(len(ps)); running=0
    for rank,j in enumerate(order):
        running=max(running,min(1,(len(ps)-rank)*ps[j])); adj[j]=running
    iv.loc[valid,"p_holm"]=adj
    iv.to_csv(OUT/"validation_inference.csv",index=False)
    # Working candidates: >=20 validation active trades, positive net and +50% fee stress.
    working=sm[(sm.split=="validation")&(sm.state!="ALL")&(sm.trades>=20)&(sm.net>0)&(sm.net50>0)].copy()
    working=working.sort_values(["state","net50"],ascending=[True,False])
    working.to_csv(OUT/"validation_working_candidates.csv",index=False)
    # Freeze only B3 because B1/B2 have <20 validation opportunities by design.
    freeze=working[(working.strategy=="covered_call_2_static_proxy") & (working.state!="ALL")].head(6)
    freeze.to_csv(OUT/"validation_freeze.csv",index=False)
    hold=[]
    h=t[t.split=="holdout"]
    for r in freeze.itertuples(index=False):
        z=h[(h.strategy==r.strategy)&h.states.apply(lambda x:r.state in json.loads(x))]
        if not z.empty:
            hold.append({"strategy":r.strategy,"state":r.state,**summary_stats(z)})
    hc=pd.DataFrame(hold); hc.to_csv(OUT/"holdout_confirmation.csv",index=False)
    summary={"trade_rows":len(t),"strategies":sorted(t.strategy.unique()),"data_errors":len(errors),
             "validation_working_states":len(working),"frozen_rows":len(freeze),
             "holdout_confirmation_rows":len(hc),
             "holm_survivors":int((iv.p_holm<.05).sum()) if "p_holm" in iv else 0}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str))
    (OUT/"PHASE48_MANUSCRIPT.md").write_text("# Phase 48 Manuscript — Independent Multi-Expiry Data Bridge\n\n"
      "## Summary\n\n"+json.dumps(summary,indent=2)+"\n\n## Validation working states\n\n"+
      working.to_markdown(index=False)+"\n\n## Validation inference\n\n"+
      iv.sort_values(["p_holm","p"]).head(40).to_markdown(index=False)+"\n\n## Holdout confirmation\n\n"+
      (hc.to_markdown(index=False) if len(hc) else "No frozen confirmations.")+
      "\n\n## Important limitation\n\nThis phase uses an independent dataset beginning in late 2024; it is supplementary and cannot overwrite the canonical 2021-2025 evidence.")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
