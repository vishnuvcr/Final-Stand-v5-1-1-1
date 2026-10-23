#!/usr/bin/env python3
"""Phase 111 fixed-rule replay. Signal is a causal MT4-style proxy, not verified ZigLib parity."""
from __future__ import annotations
import gc, hashlib, itertools, json, math, os, re
from collections import Counter
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from huggingface_hub import HfApi, hf_hub_download
from scipy.stats import ttest_1samp

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"results"/"phase111"
HF_REPO="thetrademarkk/india-index-options-1m"; TZ="Asia/Kolkata"
RATE,DIV,YEAR_DAYS=.06,0.0,365.25
DEPTH,DEVIATION,BACKSTEP,TICK=12,5,2,.05
TARGET_DELTA,STOP_DELTA,MIN_OI=.10,.50,100.0
ENTRY,SELECT,EXIT,EXPIRY_CLOSE="10:00:00","09:59:00","10:00:00","15:30:00"
COSTS=[{"cost_id":f"B{int(b)}_S{s:.2f}_F{f:.1f}","brokerage_per_order":b,"slippage_per_unit":s,"fee_multiplier":f} for b,s,f in itertools.product((10.,15.,20.),(0.,.05,.25,.5),(1.,1.5))]
PRIMARY={"brokerage_per_order":20.,"slippage_per_unit":.25,"fee_multiplier":1.}
REPS,SEED=3000,20261024

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""): h.update(b)
    return h.hexdigest()

def now(): return datetime.now(timezone.utc).isoformat()
def localize(s):
    x=pd.to_datetime(s,errors="coerce")
    return x.dt.tz_localize(TZ) if x.dt.tz is None else x.dt.tz_convert(TZ)

def valid_ohlc(r):
    try: o,h,l,c=(float(r[k]) for k in ("open","high","low","close"))
    except (TypeError,ValueError,KeyError): return False
    return all(math.isfinite(x) and x>0 for x in (o,h,l,c)) and l<=min(o,c) and h>=max(o,c) and h>=l

def cdf(x): return .5*(1+math.erf(x/math.sqrt(2)))
def price(s,k,t,v,typ):
    if min(s,k,t,v)<=0 or not all(math.isfinite(x) for x in (s,k,t,v)): return max(s-k,0) if typ=="CE" else max(k-s,0)
    rt=math.sqrt(t); d1=(math.log(s/k)+(RATE+.5*v*v)*t)/(v*rt); d2=d1-v*rt
    if typ=="CE": return s*cdf(d1)-k*math.exp(-RATE*t)*cdf(d2)
    return k*math.exp(-RATE*t)*cdf(-d2)-s*cdf(-d1)
def iv_est(s,k,t,p,typ):
    if min(s,k,t,p)<=0 or not all(math.isfinite(x) for x in (s,k,t,p)): return None
    lower=max(s-k*math.exp(-RATE*t),0) if typ=="CE" else max(k*math.exp(-RATE*t)-s,0)
    upper=s if typ=="CE" else k*math.exp(-RATE*t); tol=max(.05,1e-7*max(s,k,p))
    if p<lower-tol or p>=upper-tol: return None
    lo,hi=1e-5,5.
    if p<price(s,k,t,lo,typ)-tol or p>price(s,k,t,hi,typ)+tol: return None
    for _ in range(64):
        mid=(lo+hi)/2
        if price(s,k,t,mid,typ)<p: lo=mid
        else: hi=mid
    v=(lo+hi)/2
    return v if abs(price(s,k,t,v,typ)-p)<=max(.05,tol) else None
def delta(s,k,t,v,typ):
    if min(s,k,t,v)<=0: return None
    d1=(math.log(s/k)+(RATE+.5*v*v)*t)/(v*math.sqrt(t))
    return cdf(d1) if typ=="CE" else cdf(d1)-1

def lot_size(expiry):
    d=date.fromisoformat(expiry)
    if d<date(2021,8,1): return 75
    if d<=date(2024,4,25) and d>=date(2021,8,1): return 50
    if date(2024,5,2)<=d<=date(2024,12,19): return 25
    if date(2025,1,2)<=d<=date(2025,12,23): return 75
    if d>=date(2026,1,6): return 65
    return None

def fee_rates(d):
    d=date.fromisoformat(d); stt=.000625 if d<date(2024,10,1) else (.001 if d<date(2026,4,1) else .0015)
    if d>=date(2026,3,1): ex,ipft=.000355299,.000000001
    elif d>=date(2024,10,1): ex,ipft=.0003503,.000005
    else: ex,ipft=.000495,.000005
    return stt,ex,ipft,.000001,.00003

def fee_model(entry,exit,lot,ed,xd,cost):
    slip=float(cost["slippage_per_unit"]); sell,buy=entry-slip,exit+slip
    if min(entry,exit,sell,buy)<=0 or lot<=0: return None
    gross=(entry-exit)*lot; slippage=2*slip*lot; brokerage=2*float(cost["brokerage_per_order"])
    sell_turn,buy_turn=sell*lot,buy*lot
    stt0,ex0,ip0,sebi0,stamp0=fee_rates(ed); stt1,ex1,ip1,sebi1,stamp1=fee_rates(xd)
    fm=float(cost["fee_multiplier"]); stt=sell_turn*stt0*fm
    exraw=sell_turn*ex0+buy_turn*ex1; ipraw=sell_turn*ip0+buy_turn*ip1
    sebi_raw=(sell_turn+buy_turn)*sebi0; stamp=buy_turn*stamp1*fm
    ex,ip,sebi=exraw*fm,ipraw*fm,sebi_raw*fm; gst=.18*brokerage+.18*(exraw+ipraw+sebi_raw)*fm
    fees=stt+ex+ip+sebi+stamp+gst; total=slippage+brokerage+fees
    return {"gross_pnl_inr":gross,"net_pnl_inr":gross-total,"total_costs_inr":total,"slippage_cost_inr":slippage,
            "brokerage_inr":brokerage,"stt_inr":stt,"exchange_fee_inr":ex,"ipft_inr":ip,"sebi_fee_inr":sebi,
            "stamp_duty_inr":stamp,"gst_inr":gst,"entry_credit_inr":entry*lot}

def load_index(path):
    df=pd.read_parquet(path); req={"timestamp","open","high","low","close"}
    if not req<=set(df.columns): raise RuntimeError("NIFTY index parquet misses required fields")
    df=df[list(req)].copy(); df["timestamp"]=localize(df["timestamp"])
    for c in ("open","high","low","close"): df[c]=pd.to_numeric(df[c],errors="coerce")
    df=df.dropna(subset=["timestamp"]); dup=df["timestamp"].duplicated(keep=False); dupcount=int(dup.sum()); df=df.loc[~dup].sort_values("timestamp")
    spot={}
    for r in df.itertuples(index=False):
        ts=pd.Timestamp(r.timestamp)
        if time(9,15)<=ts.time()<=time(15,29):
            row={"open":float(r.open),"high":float(r.high),"low":float(r.low),"close":float(r.close)}
            if valid_ohlc(row): spot[ts]=row
    return spot,dupcount

def daily_candles(spot):
    byday={}
    for ts,row in spot.items(): byday.setdefault(ts.date().isoformat(),[]).append((ts,row))
    bars=[]; incomplete=0; exp_times=list(pd.date_range("2000-01-01 09:15",periods=375,freq="min").time)
    for d,rows in sorted(byday.items()):
        rows.sort(); times=[x[0].time() for x in rows]
        if len(rows)!=375 or times!=exp_times: incomplete+=1; continue
        bars.append({"date":d,"open":rows[0][1]["open"],"high":max(x[1]["high"] for x in rows),
                     "low":min(x[1]["low"] for x in rows),"close":rows[-1][1]["close"],"minute_rows":375})
    return pd.DataFrame(bars),incomplete

def confirmed_pivots(daily):
    """Non-repainting proxy: unique +/-12-bar extreme, swing >= 5 ticks, finalized only by opposite pivot."""
    if len(daily)<2*DEPTH+3: return []
    hi=daily.high.to_numpy(float); lo=daily.low.to_numpy(float); raw=[]
    for i in range(DEPTH,len(daily)-DEPTH):
        h=hi[i-DEPTH:i+DEPTH+1]; l=lo[i-DEPTH:i+DEPTH+1]
        if hi[i]==h.max() and int((h==hi[i]).sum())==1: raw.append({"idx":i,"known":i+DEPTH,"kind":"H","price":hi[i]})
        if lo[i]==l.min() and int((l==lo[i]).sum())==1: raw.append({"idx":i,"known":i+DEPTH,"kind":"L","price":lo[i]})
    raw.sort(key=lambda p:(p["known"],p["idx"],p["kind"]))
    clean=[]
    for p in raw:
        prev=next((x for x in reversed(clean) if x["kind"]==p["kind"]),None)
        if prev and p["idx"]-prev["idx"]<=BACKSTEP:
            better=p["price"]>prev["price"] if p["kind"]=="H" else p["price"]<prev["price"]
            if better: clean.remove(prev); clean.append(p)
        else: clean.append(p)
    clean.sort(key=lambda p:(p["known"],p["idx"],p["kind"]))
    active=None; out=[]
    for p in clean:
        if active is None: active=p.copy(); continue
        if p["kind"]==active["kind"]:
            if (p["price"]>active["price"] if p["kind"]=="H" else p["price"]<active["price"]): active=p.copy()
            continue
        if abs(p["price"]-active["price"])<DEVIATION*TICK: continue
        q=active.copy(); q["confirmation_idx"]=p["known"]; out.append(q); active=p.copy()
    prevh=prevl=None
    for p in out:
        if p["kind"]=="H":
            p["label"] = None if prevh is None else ("HH" if p["price"] > prevh else "LH")
            prevh = p["price"]
        else:
            p["label"] = None if prevl is None else ("HL" if p["price"] > prevl else "LL")
            prevl = p["price"]
    return out

def signal_asof(daily,cutoff):
    found=daily.index[daily.date.eq(cutoff)]
    if len(found)!=1: return None
    i=int(found[0]); piv=[p for p in confirmed_pivots(daily) if p["confirmation_idx"]<=i and p["idx"]<=i]
    if not piv: return None
    p=piv[-1]
    return {"label":p["label"],"pivot_date":daily.iloc[p["idx"]]["date"],"confirmed_date":daily.iloc[p["confirmation_idx"]]["date"],
            "signal_date":cutoff,"side":"PE" if p["label"] in ("HL","LL") else "CE","pivot_price":float(p["price"])}

def normalize_options(path,expiry):
    cols=set(pq.ParquetFile(path).schema.names)
    req={"timestamp","option_type","strike","open","high","low","close","open_interest","expiry"}
    if not req<=cols: raise RuntimeError("Options file is missing required fields: "+str(sorted(req-cols)))
    keep=list(req | ({"volume"} if "volume" in cols else set()) | ({"symbol"} if "symbol" in cols else set()) | ({"trading_day"} if "trading_day" in cols else set()))
    df=pd.read_parquet(path,columns=keep); df["timestamp"]=localize(df.timestamp)
    df["option_type"]=df.option_type.astype(str).str.upper().replace({"CALL":"CE","C":"CE","PUT":"PE","P":"PE"})
    df["expiry"]=pd.to_datetime(df.expiry,errors="coerce").dt.strftime("%Y-%m-%d")
    for c in ("strike","open","high","low","close","open_interest"): df[c]=pd.to_numeric(df[c],errors="coerce")
    total=len(df); df=df.loc[df.expiry.eq(expiry)].dropna(subset=["timestamp","strike"]).copy()
    if df.empty: raise RuntimeError("No exact-expiry rows")
    canon=[c for c in ("timestamp","expiry","option_type","strike","open","high","low","close","volume","open_interest","trading_day") if c in df]
    n=len(df); df=df.drop_duplicates(subset=canon,keep="first")
    return df,{"rows_before_filter":total,"rows_exact_expiry":n,"identical_duplicates_removed":n-len(df),"schema_columns":sorted(cols)}

def expected_grid(entry,exit_ts,spot):
    days=sorted({t.date() for t in spot if entry.date()<=t.date()<=exit_ts.date() and time(9,15)<=t.time()<=time(15,29)})
    if entry.date() not in days or exit_ts.date() not in days:return pd.DatetimeIndex([])
    result=pd.DatetimeIndex([])
    for d in days:
        a=entry if d==entry.date() else pd.Timestamp(f"{d} 09:15:00",tz=TZ)
        b=exit_ts if d==exit_ts.date() else pd.Timestamp(f"{d} 15:29:00",tz=TZ)
        if a<=b: result=result.append(pd.date_range(a,b,freq="min"))
    return result

def choose_contract(df,sig,expiry,entry_date,spot):
    st=pd.Timestamp(f"{entry_date} {SELECT}",tz=TZ); et=pd.Timestamp(f"{entry_date} {ENTRY}",tz=TZ)
    sr=spot.get(st); snap=df.loc[df.timestamp.eq(st)&df.option_type.eq(sig["side"])].copy()
    if sr is None or snap.empty:return None,"MISSING_EXACT_SELECTION_BAR"
    keys=["timestamp","expiry","option_type","strike","open","high","low","close","open_interest"]
    snap=snap.drop_duplicates(subset=[k for k in keys if k in snap],keep="first")
    if snap.duplicated(["option_type","strike"],keep=False).any(): return None,"CONFLICTING_SELECTION_DUPLICATE"
    tau=(pd.Timestamp(f"{expiry} {EXPIRY_CLOSE}",tz=TZ)-(st+pd.Timedelta(minutes=1))).total_seconds()/(YEAR_DAYS*86400)
    cand=[]
    for r in snap.itertuples(index=False):
        if not valid_ohlc({"open":r.open,"high":r.high,"low":r.low,"close":r.close}) or not math.isfinite(float(r.open_interest)) or r.open_interest<MIN_OI:continue
        k,p=float(r.strike),float(r.close); v=iv_est(sr["close"],k,tau,p,sig["side"])
        if v is None:continue
        d=delta(sr["close"],k,tau,v,sig["side"])
        if d is not None:cand.append({"strike":k,"selection_delta":d,"selection_oi":float(r.open_interest),"selection_iv":v,
            "distance":abs(k-sr["close"]),"selection_close":p,"side":sig["side"]})
    if not cand:return None,"NO_VALID_ABS_0_10_DELTA_CONTRACT"
    c=min(cand,key=lambda x:(abs(abs(x["selection_delta"])-TARGET_DELTA),x["distance"],x["strike"]))
    e=df.loc[df.timestamp.eq(et)&df.option_type.eq(sig["side"])&np.isclose(df.strike.to_numpy(float),c["strike"],rtol=0,atol=1e-9)].copy()
    e=e.drop_duplicates(subset=[k for k in keys if k in e],keep="first")
    if len(e)!=1 or not valid_ohlc(e.iloc[0]):return None,"MISSING_INVALID_OR_DUPLICATE_ENTRY_BAR"
    c["entry_price"]=float(e.iloc[0]["open"]); c["entry_ts"]=et
    es=spot.get(et)
    if es is None:return None,"MISSING_EXACT_ENTRY_SPOT"
    tau0=(pd.Timestamp(f"{expiry} {EXPIRY_CLOSE}",tz=TZ)-et).total_seconds()/(YEAR_DAYS*86400)
    v0=iv_est(es["open"],c["strike"],tau0,c["entry_price"],sig["side"])
    if v0 is None:return None,"INVALID_ENTRY_IV"
    c["entry_delta"]=delta(es["open"],c["strike"],tau0,v0,sig["side"])
    return (c,"PASS") if c["entry_delta"] is not None else (None,"INVALID_ENTRY_DELTA")

def replay(df,spot,expiry,prev,entry_date,sig,lot):
    c,why=choose_contract(df,sig,expiry,entry_date,spot)
    if c is None:return None,why
    ent=pd.Timestamp(f"{entry_date} {ENTRY}",tz=TZ); ex=pd.Timestamp(f"{expiry} {EXIT}",tz=TZ)
    grid=expected_grid(ent,ex,spot)
    if len(grid)<2 or grid[0]!=ent or grid[-1]!=ex:return None,"INVALID_SESSION_GRID"
    op=df.loc[df.option_type.eq(sig["side"])&np.isclose(df.strike.to_numpy(float),c["strike"],rtol=0,atol=1e-9)&df.timestamp.between(ent,ex)].copy()
    if op.timestamp.duplicated(keep=False).any():return None,"CONFLICTING_CONTRACT_MINUTE"
    op=op.set_index("timestamp").reindex(grid)
    if op.open.isna().any() or op.close.isna().any():return None,"INCOMPLETE_OPTION_PATH"
    sr=[spot.get(t) for t in grid]
    if any(x is None for x in sr):return None,"INCOMPLETE_SPOT_PATH"
    if any(not valid_ohlc(op.iloc[i]) or not valid_ohlc(sr[i]) for i in range(len(grid))):return None,"INVALID_MONITORING_OHLC"
    exp_ts=pd.Timestamp(f"{expiry} {EXPIRY_CLOSE}",tz=TZ); stop=None
    for i,t in enumerate(grid[:-1]):
        tau=(exp_ts-(t+pd.Timedelta(minutes=1))).total_seconds()/(YEAR_DAYS*86400)
        v=iv_est(sr[i]["close"],c["strike"],tau,float(op.iloc[i]["close"]),sig["side"])
        if v is None:return None,"INVALID_STOP_IV"
        d=delta(sr[i]["close"],c["strike"],tau,v,sig["side"])
        if d is None:return None,"INVALID_STOP_DELTA"
        if abs(d)>=STOP_DELTA: stop={"ts":grid[i+1],"price":float(op.iloc[i+1]["open"]),"delta":float(d)};break
    strat_px=stop["price"] if stop else float(op.iloc[-1]["open"])
    strat_ts=stop["ts"] if stop else ex
    if not math.isfinite(strat_px) or strat_px<=0:return None,"INVALID_EXIT_PRICE"
    return {"event_id":f"{prev}_{expiry}_{entry_date}","expiry":expiry,"previous_expiry":prev,"entry_date":entry_date,
      "exit_date":strat_ts.date().isoformat(),"split":"development" if expiry<="2023-12-31" else ("validation" if expiry<="2025-12-31" else "holdout"),
      "signal_label":sig["label"],"signal_side":sig["side"],"pivot_date":sig["pivot_date"],"confirmed_date":sig["confirmed_date"],
      "strike":c["strike"],"selection_delta":c["selection_delta"],"selection_oi":c["selection_oi"],"entry_delta":c["entry_delta"],
      "entry_price":c["entry_price"],"entry_ts":ent.isoformat(),"scheduled_exit_price":float(op.iloc[-1]["open"]),
      "scheduled_exit_ts":ex.isoformat(),"strategy_exit_price":strat_px,"strategy_exit_ts":strat_ts.isoformat(),
      "stop_hit":stop is not None,"stop_delta":stop["delta"] if stop else None,"stop_reason":"ABS_DELTA_GE_0_50" if stop else "SCHEDULED_EXPIRY_EXIT",
      "lot_size":lot,"monitoring_minutes":len(grid)}, "PASS"

def aggregate(rows,expected,seed):
    n=len(rows)
    if not n:return {"expected_campaigns":expected,"trades":0,"coverage_pct":0. if expected else None,"net_pnl_inr":None,
      "mean_net_trade_inr":None,"win_rate_pct":None,"profit_factor":None,"max_drawdown_inr":None,"stop_hit_rate_pct":None,
      "paired_uplift_sum_inr":None,"paired_uplift_mean_inr":None,"paired_uplift_ci95_low":None,"paired_uplift_ci95_high":None,
      "mean_net_ci95_low":None,"mean_net_ci95_high":None,"p_value_greater_than_zero":None}
    x=np.array([r["net"] for r in rows],float); pos=float(x[x>0].sum()); neg=float(-x[x<0].sum()); cum=np.cumsum(x)
    dd=np.maximum.accumulate(np.maximum(cum,0))-cum
    def ci(a,off):
        a=np.asarray(a,float)
        if len(a)<2:return (None,None)
        rng=np.random.default_rng(seed+off); m=np.empty(REPS)
        for j in range(REPS):m[j]=a[rng.integers(0,len(a),size=len(a))].mean()
        return float(np.quantile(m,.025)),float(np.quantile(m,.975))
    mlo,mhi=ci(x,0); ups=[r["uplift"] for r in rows if r.get("uplift") is not None]; ulo,uhi=ci(ups,1)
    try:pval=float(ttest_1samp(x,0,alternative="greater").pvalue) if n>=2 else None
    except Exception:pval=None
    if pval is not None and not math.isfinite(pval):pval=None
    return {"expected_campaigns":expected,"trades":n,"coverage_pct":100*n/expected if expected else 0.,
      "gross_pnl_inr":float(sum(r["gross"] for r in rows)),"net_pnl_inr":float(x.sum()),
      "mean_net_trade_inr":float(x.mean()),"median_net_trade_inr":float(np.median(x)),
      "return_on_entry_credit_pct":float(100*x.sum()/sum(r["credit"] for r in rows)) if sum(r["credit"] for r in rows) else None,
      "win_rate_pct":float(100*(x>0).mean()),"profit_factor":pos/neg if neg else (None if not pos else "INF"),
      "max_drawdown_inr":float(dd.max()),"stop_hit_rate_pct":float(100*np.mean([r["stop"] for r in rows])),
      "paired_uplift_sum_inr":float(sum(ups)) if ups else None,"paired_uplift_mean_inr":float(np.mean(ups)) if ups else None,
      "paired_uplift_ci95_low":ulo,"paired_uplift_ci95_high":uhi,"mean_net_ci95_low":mlo,"mean_net_ci95_high":mhi,
      "p_value_greater_than_zero":pval}


def write_figures(smry):
    paths=[]
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fd=OUT/"figures"; fd.mkdir(parents=True,exist_ok=True)
        sub=smry.loc[smry.cost_id.eq("B20_S0.25_F1.0")]
        for sp in ("development","validation","holdout"):
            q=sub.loc[sub.split.eq(sp)]
            if q.empty: continue
            fig,ax=plt.subplots(figsize=(8,4.5))
            vals=[float(v) if pd.notna(v) else 0.0 for v in q.net_pnl_inr]
            ax.bar(q.candidate.tolist(),vals)
            ax.axhline(0,linewidth=1)
            ax.set_ylabel("Net P&L INR (one lot; primary modeled costs)")
            ax.set_title("Phase 111 stopped vs no-stop: "+sp)
            ax.tick_params(axis="x",rotation=12)
            fig.tight_layout()
            fp=fd/("net_pnl_"+sp+".svg"); fig.savefig(fp,format="svg"); plt.close(fig)
            paths.append(str(fp.relative_to(ROOT)))
        return paths
    except Exception as e:
        (OUT/"figure_error.txt").write_text(type(e).__name__+": "+str(e)[:300]+"\n")
        return paths

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for p in OUT.iterdir():
        if p.is_file():p.unlink()
        elif p.is_dir(): 
            import shutil;shutil.rmtree(p)
    token=os.environ.get("HF_TOKEN"); revreq=os.environ.get("PHASE111_DATASET_REVISION","main") or "main"
    api=HfApi(token=token or None); info=api.dataset_info(repo_id=HF_REPO,revision=revreq); rev=str(info.sha)
    names=api.list_repo_files(repo_id=HF_REPO,repo_type="dataset",revision=rev)
    efiles={}
    for f in names:
        m=re.fullmatch(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet",f)
        if m:efiles[m.group(1)]=f
    expiries=sorted(efiles)
    if len(expiries)<3:raise RuntimeError("Fewer than 3 expiry files at the resolved data revision")
    ipath=Path(hf_hub_download(repo_id=HF_REPO,filename="index/NIFTY.parquet",repo_type="dataset",revision=rev,token=token))
    spot,dupcount=load_index(ipath);daily,incomplete=daily_candles(spot)
    if daily.empty:raise RuntimeError("No complete 375-minute NIFTY daily candles")
    (OUT/"daily_coverage.json").write_text(json.dumps({"complete_daily_candles":int(len(daily)),
      "first_complete_session":str(daily.iloc[0]["date"]),"last_complete_session":str(daily.iloc[-1]["date"]),
      "incomplete_sessions_excluded":int(incomplete)},indent=2)+"\n")
    daily_ix={d:i for i,d in enumerate(daily.date.tolist())}; sessions=sorted({t.date().isoformat() for t in spot})
    planned=[];excluded=[];manifest=[];trades=[]
    for j in range(1,len(expiries)):
        prev,exp=expiries[j-1],expiries[j];gap=(date.fromisoformat(exp)-date.fromisoformat(prev)).days
        if gap<4 or gap>10:continue
        nextdays=[d for d in sessions if date.fromisoformat(d)>date.fromisoformat(prev)]
        eid=f"{prev}_{exp}_{nextdays[0] if nextdays else 'NO_ENTRY'}"
        if not nextdays:excluded.append({"event_id":eid,"expiry":exp,"reason":"NO_NEXT_OBSERVED_SESSION"});continue
        ent=nextdays[0];split="development" if exp<="2023-12-31" else ("validation" if exp<="2025-12-31" else "holdout")
        planned.append({"event_id":eid,"previous_expiry":prev,"expiry":exp,"entry_date":ent,"split":split,"gap_days":gap})
        if prev not in daily_ix:excluded.append({"event_id":eid,"expiry":exp,"reason":"PREVIOUS_EXPIRY_DAILY_CANDLE_INCOMPLETE"});continue
        sig=signal_asof(daily,prev)
        if sig is None:excluded.append({"event_id":eid,"expiry":exp,"reason":"NO_CONFIRMED_PIVOT_SIGNAL"});continue
        lot=lot_size(exp)
        if lot is None:excluded.append({"event_id":eid,"expiry":exp,"reason":"UNSUPPORTED_HISTORICAL_LOT_SIZE_DATE"});continue
        try:
            path=Path(hf_hub_download(repo_id=HF_REPO,filename=efiles[exp],repo_type="dataset",revision=rev,token=token))
            opt,audit=normalize_options(path,exp);manifest.append({"expiry":exp,"file":efiles[exp],"sha256":sha256(path),"bytes":path.stat().st_size,"status":"PASS",**audit})
            ev,why=replay(opt,spot,exp,prev,ent,sig,lot)
            if ev is None:excluded.append({"event_id":eid,"expiry":exp,"reason":why})
            else:trades.append(ev)
            del opt;gc.collect()
        except Exception as e:
            manifest.append({"expiry":exp,"file":efiles.get(exp),"status":"ERROR","error_type":type(e).__name__})
            excluded.append({"event_id":eid,"expiry":exp,"reason":"SOURCE_OR_PROCESSING_ERROR","detail":f"{type(e).__name__}: {str(e)[:160]}"})
    pd.DataFrame(manifest).to_csv(OUT/"source_manifest.csv",index=False)
    pd.DataFrame(excluded).to_csv(OUT/"campaign_exclusions.csv",index=False)
    pd.DataFrame(planned).to_csv(OUT/"scheduled_campaigns.csv",index=False)
    bysplit={s:sum(x["split"]==s for x in planned) for s in ("development","validation","holdout")}
    elsplit={s:sum(x["split"]==s for x in trades) for s in bysplit}
    summary={"generated_at_utc":now(),"dataset_repo":HF_REPO,"dataset_revision_requested":revreq,"dataset_revision_resolved_sha":rev,
      "index_file_sha256":sha256(ipath),"index_file_bytes":ipath.stat().st_size,"expiry_file_count":len(expiries),
      "first_expiry":expiries[0],"last_expiry":expiries[-1],"complete_daily_candles":len(daily),"incomplete_daily_sessions":incomplete,
      "duplicate_index_timestamps":dupcount,"scheduled_campaigns":len(planned),"eligible_campaigns":len(trades),
      "excluded_campaigns":len(excluded),"scheduled_by_split":bysplit,"eligible_by_split":elsplit,"cost_scenarios":len(COSTS),
      "signal_proxy":"confirmed unique local extrema +/-12 days, minimum 5 ticks reversal, 2-bar backstep",
      "ziglib_parity":"NOT VERIFIED: supplied Pine references external DevLucem/ZigLib/1; proxy only",
      "status":"EMPIRICAL_SCREEN_COMPLETE_NO_PROMOTION" if trades else "BLOCKED_NO_VALID_CAMPAIGNS",
      "strategy_promotion":"NONE","tester_review":"WAIVED BY USER"}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    (OUT/"coverage.json").write_text(json.dumps({"scheduled":len(planned),"eligible":len(trades),"excluded":len(excluded),
      "scheduled_by_split":bysplit,"eligible_by_split":elsplit,"exclusion_reasons":dict(Counter(x["reason"] for x in excluded))},indent=2)+"\n")
    led=[];srows=[]
    for split in bysplit:
      tr=[x for x in trades if x["split"]==split]
      for cost in COSTS:
       for candidate in ("ZIGZAG_DELTA_STOP_050","ZIGZAG_NO_STOP"):
        rows=[]
        for t in tr:
            xp=t["strategy_exit_price"] if candidate=="ZIGZAG_DELTA_STOP_050" else t["scheduled_exit_price"]
            xt=t["strategy_exit_ts"] if candidate=="ZIGZAG_DELTA_STOP_050" else t["scheduled_exit_ts"]
            f=fee_model(t["entry_price"],xp,t["lot_size"],t["entry_date"],pd.Timestamp(xt).date().isoformat(),cost)
            b=fee_model(t["entry_price"],t["scheduled_exit_price"],t["lot_size"],t["entry_date"],t["expiry"],cost)
            if f is None or b is None:continue
            rows.append({"net":f["net_pnl_inr"],"gross":f["gross_pnl_inr"],"credit":f["entry_credit_inr"],
                         "stop":t["stop_hit"] if candidate=="ZIGZAG_DELTA_STOP_050" else False,
                         "uplift":f["net_pnl_inr"]-b["net_pnl_inr"] if candidate=="ZIGZAG_DELTA_STOP_050" else None})
            led.append({"event_id":t["event_id"],"split":split,"candidate":candidate,"cost_id":cost["cost_id"],"expiry":t["expiry"],
              "signal_label":t["signal_label"],"side":t["signal_side"],"strike":t["strike"],"selection_delta":t["selection_delta"],
              "entry_ts":t["entry_ts"],"exit_ts":xt,"stop_hit":bool(t["stop_hit"]) if candidate=="ZIGZAG_DELTA_STOP_050" else False,
              "exit_reason":t["stop_reason"] if candidate=="ZIGZAG_DELTA_STOP_050" else "SCHEDULED_EXPIRY_EXIT",
              "gross_pnl_inr":f["gross_pnl_inr"],"net_pnl_inr":f["net_pnl_inr"],"total_costs_inr":f["total_costs_inr"],**{k:v for k,v in f.items() if k.endswith("_inr") and k not in ("gross_pnl_inr","net_pnl_inr","total_costs_inr","entry_credit_inr")}})
        srows.append({"split":split,"candidate":candidate,**cost,**aggregate(rows,bysplit[split],SEED+len(srows))})
    pd.DataFrame(led).to_csv(OUT/"campaign_ledger.csv",index=False); pd.DataFrame(srows).to_csv(OUT/"cost_grid.csv",index=False)
    figure_paths=write_figures(pd.DataFrame(srows))
    (OUT/"result_summary.json").write_text(json.dumps({"status":summary["status"],"scheduled_campaigns":len(planned),
      "eligible_campaigns":len(trades),"excluded_campaigns":len(excluded),"cost_rows":len(srows),"figure_paths":figure_paths,"promoted":False},indent=2)+"\n")
    report=f"""# Phase 111 — ZigZag weekly options report

Generated UTC: {summary['generated_at_utc']}

Status: **{summary['status']}**. Strategy promotion: **NONE**.

## Data coverage
- Dataset revision: {rev}
- Observed expiry files: {len(expiries)}, from {expiries[0]} through {expiries[-1]}.
- Campaigns scheduled: {len(planned)}; exact-path eligible: {len(trades)}; excluded: {len(excluded)}.
- Complete daily index candles: {len(daily)}; incomplete sessions excluded: {incomplete}.
- Eligible campaign counts by split: {json.dumps(elsplit)}.
- Exclusions: {json.dumps(dict(Counter(x['reason'] for x in excluded)),sort_keys=True)}.

## Locked strategy
Last confirmed daily HL/LL means sell a put; HH/LH means sell a call. Option target is absolute model delta 0.10 using the exact 09:59 completed bar; sell at the exact 10:00 open on the first observed session after the previous expiry. Scheduled exit is the exact 10:00 open on target weekly expiry. A completed one-minute observation with absolute model delta >= 0.50 exits at the next exact market minute's open.

## Cost model
24 scenarios: brokerage ₹10/₹15/₹20 per order; adverse slippage ₹0/₹0.05/₹0.25/₹0.50 per option unit on entry and exit; modeled fee multipliers 1.0×/1.5×. One-lot historical quantity and date-aware STT, exchange/IPFT, SEBI, stamp duty and GST are included. Account-specific Paytm Money contract-note charges are not verified. OHLC opens are simulation proxies, not proven executions.

## Indicator limitation
The supplied Pine script imports external DevLucem/ZigLib/1; the library code body was not included in the user submission. The engine's causal MT4-style proxy is not verified as byte-identical to the TradingView library. Do not treat this as a definitive test of the exact plotted indicator until confirmed-label parity is demonstrated.

## Result interpretation
Cost rows are in cost_grid.csv; event-level summary outcomes (without raw minute prices) are in campaign_ledger.csv; exclusion counts/reasons are in campaign_exclusions.csv. Null statistics from empty samples indicate unestimable performance, not a zero-return result. The no-stop benchmark uses the same signal, strike and entry, with a scheduled expiry-day 10:00 exit.

No strategy is promoted. If the sample is small, coverage is selective, or the signal implementation does not match TradingView, any apparent edge is provisional.
"""
    (OUT/"PHASE111_REPORT.md").write_text(report,encoding="utf-8")
    manuscript="""# Phase 111 — Non-Repainting ZigZag Weekly Options Research Manuscript

## Abstract
This fixed-rule exploratory study tests single-leg weekly NIFTY option selling from the last confirmed daily ZigZag-style pivot. Because the submitted Pine script imports an external library whose body was not included, the Python signal is a causal MT4-style proxy rather than verified TradingView parity. No strategy promotion follows from this screen.

## Research question, aim and objectives
Test whether selling the 0.10-absolute-delta option indicated by the last confirmed daily pivot, with buyback at absolute model delta 0.50 or fixed expiry-day 10:00 exit, produces robust after-cost outcomes versus no-stop hold-to-expiry. Objectives are no-look-ahead signals, exact contracts/minutes, explicit exclusions, 24 costs and chronological splits.

## Methodology
One-minute NIFTY OHLC is aggregated into complete 375-minute sessions. Depth 12, Deviation 5 ticks and Backstep 2 are used by a deterministic causal ZigZag proxy. Only opposite-reversal-confirmed pivots known by previous expiry close are eligible. HL/LL selects a put; HH/LH selects a call. The exact 09:59 bar close determines the nearest valid 0.10 absolute-delta option; entry uses exact 10:00 open. A completed minute whose model-estimated absolute delta is at least 0.50 fills at the next exact minute open. No interpolation/forward-fill is allowed. One historical lot and a date-aware fee model are used.

## Statistical analysis
Development is through expiry 2023-12-31; validation is 2024–2025; holdout is 2026 onward to the available source cutoff. The 24-case registered cost grid compares stopped and no-stop outcomes on matched eligible campaigns. Campaign bootstrap confidence intervals and one-sided t-tests are descriptive only; no signal parameters are tuned.

## Results
The Phase 111 report, summary.json, coverage.json, campaign_exclusions.csv, campaign_ledger.csv and cost_grid.csv carry the source revision, coverage funnel, costs and results. A null estimate on an empty split is not a measured zero return.

## Discussion
Exact option coverage may select a nonrepresentative subset. Model IV/delta assumes European Black–Scholes, a fixed 6% rate and 0% yield. OHLC prices are simulated fills, not bid/ask/depth. The source dataset is declared CC BY-NC 4.0 and has a historical coverage cutoff; account-specific Paytm Money contract charges are unverified. Confirmed-label parity against TradingView remains open.

## Strengths and limitations
Strengths: frozen single rule, causal confirmation, exact timestamp joins, matched no-stop comparison, cost stresses and recorded exclusions. Limitations: unverified ZigLib parity, partial options data, sparse holdout, proxy prices/model Greeks and potential selection bias from path-complete campaigns.

## Conclusion and future direction
No strategy is promoted from this screen. A bounded follow-up may compare a supplied TradingView label fixture to this proxy and test the frozen rule with better quote data. No recursive parameter search is authorized.

## Appendices
Source hashes and expiry files are in source_manifest.csv; exact scheduled/excluded denominators are in scheduled_campaigns.csv and campaign_exclusions.csv; cost and split summaries are in cost_grid.csv.
"""
    (OUT/"PHASE111_MANUSCRIPT.md").write_text(manuscript,encoding="utf-8")
    print(json.dumps({"status":summary["status"],"dataset_revision":rev,"scheduled":len(planned),"eligible":len(trades),
      "excluded":len(excluded),"cost_rows":len(srows)},indent=2))
    return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except Exception as e:
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/"runtime_error.json").write_text(json.dumps({"status":"RUNTIME_ERROR","created_at_utc":now(),
          "error_type":type(e).__name__,"error":str(e)[:1400]},indent=2)+"\n",encoding="utf-8")
        raise
