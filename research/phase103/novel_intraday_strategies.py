#!/usr/bin/env python3
"""Bounded Phase 103 replay of three preregistered intraday NIFTY options ideas."""
from __future__ import annotations
import argparse, bisect, json, math, os, re
from collections import Counter
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "phase103"
HF_REPO = "thetrademarkk/india-index-options-1m"
PINNED_REVISION = "3eacf762d401efd9a08e804592fa7882b354c4a2"
TZ = "Asia/Kolkata"
TICK = 0.05
DEV_START, DEV_END = pd.Timestamp("2024-01-01"), pd.Timestamp("2024-12-31")
VAL_START, VAL_END = pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")
MAX_SOURCE_DATE = pd.Timestamp("2025-12-31")
BOOT_REPLICATES, BOOT_BLOCK, RNG_SEED = 5000, 5, 1032026
INITIAL_ACCOUNT_RUPEES, MAX_DRAWDOWN_RUPEES = 300000.0, 60000.0
STRATEGIES = ("S103-A_XAC_ORB", "S103-B_FBR", "S103-C_RC_VIX_IC")
ASSET_RETURNS = ("SP500_ret1", "NASDAQ_ret1", "DOW_ret1", "NIKKEI_ret1")
REQ_INDEX = {"timestamp", "open", "high", "low", "close"}
REQ_OPTION = {"timestamp", "option_type", "strike", "open", "high", "low", "close"}

def local_ts(values):
    out = pd.to_datetime(values, errors="coerce")
    if out.dt.tz is None: return out.dt.tz_localize(TZ)
    return out.dt.tz_convert(TZ)

def load_hf_file(filename, token=None):
    path = hf_hub_download(repo_id=HF_REPO, filename=filename, repo_type="dataset",
                           revision=PINNED_REVISION, token=token or os.getenv("HF_TOKEN") or None)
    return pd.read_parquet(path)

def list_expiry_dates(token=None):
    api = HfApi(token=token or os.getenv("HF_TOKEN") or None)
    pat = re.compile(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet$")
    dates = []
    for filename in api.list_repo_files(repo_id=HF_REPO, repo_type="dataset", revision=PINNED_REVISION):
        m = pat.fullmatch(filename)
        if m:
            d = pd.Timestamp(m.group(1))
            if pd.Timestamp("2024-01-01") <= d <= MAX_SOURCE_DATE: dates.append(d)
    return sorted(set(dates))

def expiry_for_session(day, expiry_dates):
    d = pd.Timestamp(day).tz_localize(None).normalize()
    i = bisect.bisect_left(expiry_dates, d)
    if i >= len(expiry_dates): return None
    expiry = expiry_dates[i]
    return expiry if (expiry-d).days <= 8 else None

def lot_size_for_expiry(expiry):
    d = pd.Timestamp(expiry).tz_localize(None).normalize()
    if d < pd.Timestamp("2021-07-29"): return 75
    if d < pd.Timestamp("2024-05-02"): return 50
    if d <= pd.Timestamp("2024-12-26"): return 25
    if d <= pd.Timestamp("2025-01-23"): return 75
    if d == pd.Timestamp("2025-01-30"): return 25
    if d < pd.Timestamp("2026-01-06"): return 75
    return 65

def fee_rates(day):
    d = pd.Timestamp(day)
    if d.tzinfo is not None: d = d.tz_convert(TZ).tz_localize(None)
    d = d.normalize()
    stt = 0.0010 if d >= pd.Timestamp("2024-10-01") else 0.000625
    txn = 0.0003503 if d >= pd.Timestamp("2024-10-01") else 0.000495
    return stt, txn, 0.000001, 0.000005, 0.00003

def adverse_fill(raw_price, action, ticks=1, impact_pct=0.0):
    price = float(raw_price)
    if not np.isfinite(price) or price <= 0: raise ValueError(f"invalid option price {raw_price!r}")
    slip = int(ticks)*TICK + price*float(impact_pct)
    if action == "buy": return price + slip
    if action == "sell": return max(0.0, price-slip)
    raise ValueError(f"unknown action {action!r}")

def charges(orders, multiplier=1.0, brokerage=10.0):
    broker = float(brokerage)*float(multiplier)*len(orders)
    exchange=sebi=ipft=stt=stamp=0.0
    for order in orders:
        sr, tx, se, ip, sd = fee_rates(order["timestamp"])
        turnover = float(order["price"])*int(order["lot"])*int(order["qty"])
        exchange += tx*turnover*multiplier
        sebi += se*turnover*multiplier
        ipft += ip*turnover*multiplier
        if order["side"] == "sell": stt += sr*turnover*multiplier
        else: stamp += sd*turnover*multiplier
    gst = 0.18*(broker+exchange+sebi+ipft)
    return float(broker+exchange+sebi+ipft+stt+stamp+gst)

def compute_trade_case(legs, entry_raw, exit_raw, entry_ts, exit_ts, lot,
                       ticks=1, multiplier=1.0, brokerage=10.0, impact_pct=0.0, extra=0.0):
    gross=0.0; orders=[]; cashflow=0.0
    for typ, strike, qty in legs:
        key=(typ,float(strike))
        ep=adverse_fill(entry_raw[key], "buy" if qty>0 else "sell", ticks, impact_pct)
        xp=adverse_fill(exit_raw[key], "sell" if qty>0 else "buy", ticks, impact_pct)
        gross += int(qty)*(xp-ep)*int(lot)
        cashflow -= int(qty)*ep*int(lot)
        orders.append({"timestamp":entry_ts,"side":"buy" if qty>0 else "sell","price":ep,"qty":1,"lot":lot})
        orders.append({"timestamp":exit_ts,"side":"sell" if qty>0 else "buy","price":xp,"qty":1,"lot":lot})
    fees=charges(orders,multiplier,brokerage)
    risk=max(0.0,-cashflow) if len(legs)==2 else max(0.0,100.0*lot-cashflow)
    return {"gross_after_slippage_rupees":float(gross),"fees_rupees":fees,
            "net_rupees":float(gross-fees-extra),"entry_cash_credit_rupees":float(cashflow),
            "risk_proxy_rupees":float(risk+fees)}

def read_daily_source(path):
    if not path.is_file(): return pd.DataFrame()
    frame=pd.read_parquet(path)
    if "date" not in frame.columns: return pd.DataFrame()
    d=pd.to_datetime(frame["date"],errors="coerce")
    if d.dt.tz is not None: d=d.dt.tz_convert(TZ).dt.tz_localize(None)
    frame=frame.copy(); frame["date"]=d.dt.normalize()
    return frame.dropna(subset=["date"]).sort_values("date").drop_duplicates("date",keep="last").reset_index(drop=True)

def previous_row(frame, day):
    if frame.empty or "date" not in frame.columns: return None
    d=pd.Timestamp(day).tz_localize(None).normalize()
    rows=frame[frame["date"]<d]
    return None if rows.empty else rows.iloc[-1]

def value(row, names):
    if row is None: return float("nan")
    cols={str(c).strip().lower():c for c in row.index}
    for name in names:
        col=cols.get(name.lower())
        if col is not None:
            try:
                n=float(row[col])
                if np.isfinite(n): return n
            except (TypeError,ValueError): pass
    return float("nan")

def global_breadth_direction(frame, day):
    row=previous_row(frame,day)
    vals=[value(row,[x]) for x in ASSET_RETURNS]
    signs=[1 if x>0 else -1 for x in vals if np.isfinite(x) and x!=0]
    if len(signs)<3: return None
    pos=sum(x>0 for x in signs); neg=sum(x<0 for x in signs)
    d=1 if pos>=3 else -1 if neg>=3 else 0
    return d if d else None

def prior_vix_low(vix,day):
    d=pd.Timestamp(day).tz_localize(None).normalize()
    prior=vix[vix["date"]<d]
    if len(prior)<60: return False,float("nan"),float("nan")
    vals=prior["close"].astype(float).to_numpy()[-60:]
    level=float(vals[-1]); threshold=float(np.quantile(vals,0.75))
    return bool(level<=threshold),level,threshold

def opening_range(bars,start="09:15",end="09:30"):
    tm=bars["timestamp"].dt.strftime("%H:%M")
    x=bars[(tm>=start)&(tm<end)]
    if len(x)<max(10, int((pd.Timestamp(end)-pd.Timestamp(start)).total_seconds()/120)):
        return float("nan"),float("nan")
    return float(x["high"].max()),float(x["low"].min())

def find_orb_signal(bars,hi,lo,breadth):
    if breadth not in (-1,1) or not np.isfinite(hi) or not np.isfinite(lo) or hi<=lo: return None
    x=bars[(bars["timestamp"].dt.strftime("%H:%M")>="09:30")&(bars["timestamp"].dt.strftime("%H:%M")<="14:30")]
    for r in x.sort_values("timestamp").itertuples(index=False):
        d=1 if float(r.close)>hi else -1 if float(r.close)<lo else 0
        if d and d==breadth: return {"signal_ts":r.timestamp,"direction":d,"setup":"GLOBAL_CONFIRMED_OPENING_RANGE_BREAKOUT"}
    return None

def find_failed_break_signal(bars,hi,lo):
    if not np.isfinite(hi) or not np.isfinite(lo) or hi<=lo: return None
    x=bars[(bars["timestamp"].dt.strftime("%H:%M")>="09:30")&(bars["timestamp"].dt.strftime("%H:%M")<="10:30")]
    state=None; rows=list(x.sort_values("timestamp").itertuples(index=False))
    for i,r in enumerate(rows):
        close=float(r.close)
        if state is None:
            if close>hi: state={"side":"HIGH","i":i,"extreme":float(r.high)}
            elif close<lo: state={"side":"LOW","i":i,"extreme":float(r.low)}
            continue
        state["extreme"]=max(float(state["extreme"]),float(r.high)) if state["side"]=="HIGH" else min(float(state["extreme"]),float(r.low))
        age=i-int(state["i"])
        if state["side"]=="HIGH" and close<=hi and age<=5:
            return {"signal_ts":r.timestamp,"direction":-1,"stop_extreme":float(state["extreme"]),"setup":"FAILED_HIGH_BREAK_REVERSAL"}
        if state["side"]=="LOW" and close>=lo and age<=5:
            return {"signal_ts":r.timestamp,"direction":1,"stop_extreme":float(state["extreme"]),"setup":"FAILED_LOW_BREAK_REVERSAL"}
        if age>=5: return None
    return None

def compression_setup(today_range,prior_ranges,vix_ok):
    if len(prior_ranges)<20 or not np.isfinite(today_range) or not vix_ok: return False
    x=np.asarray(prior_ranges[-20:],dtype=float)
    return bool(len(x)==20 and np.isfinite(x).all() and float(today_range)<float(np.median(x)))

def parse_index(raw):
    missing=REQ_INDEX.difference(raw.columns)
    if missing: raise ValueError(f"NIFTY data missing columns {sorted(missing)}")
    x=raw.copy(); x["timestamp"]=local_ts(x["timestamp"])
    x=x.dropna(subset=["timestamp"]); x=x[x["timestamp"]<pd.Timestamp("2026-01-01",tz=TZ)]
    for c in ("open","high","low","close"): x[c]=pd.to_numeric(x[c],errors="coerce")
    x=x.dropna(subset=["open","high","low","close"]).sort_values("timestamp").drop_duplicates("timestamp",keep="last")
    x["session_day"]=x["timestamp"].dt.tz_localize(None).dt.normalize()
    return x.reset_index(drop=True)

def parse_chain(raw,day):
    missing=REQ_OPTION.difference(raw.columns)
    if missing: raise ValueError(f"option data missing columns {sorted(missing)}")
    x=raw.copy(); x["timestamp"]=local_ts(x["timestamp"])
    x["option_type"]=x["option_type"].astype(str).str.upper().str.strip()
    x["strike"]=pd.to_numeric(x["strike"],errors="coerce")
    for c in ("open","high","low","close"): x[c]=pd.to_numeric(x[c],errors="coerce")
    x=x.dropna(subset=["timestamp","strike"])
    x=x[x["option_type"].isin(["CE","PE"])]
    d=pd.Timestamp(day).normalize()
    x=x[x["timestamp"].dt.tz_localize(None).dt.normalize()==d]
    return x.sort_values("timestamp").drop_duplicates(["timestamp","option_type","strike"],keep="last").reset_index(drop=True)

def snapshot_map(chain_day):
    result={}
    for ts,g in chain_day.groupby("timestamp",sort=True):
        z={}
        for r in g.itertuples(index=False):
            z[(str(r.option_type),float(r.strike))]={"open":float(r.open) if pd.notna(r.open) else np.nan,
             "high":float(r.high) if pd.notna(r.high) else np.nan,"low":float(r.low) if pd.notna(r.low) else np.nan,
             "close":float(r.close) if pd.notna(r.close) else np.nan}
        result[pd.Timestamp(ts)]=z
    return result

def make_legs(snapshots,signal_ts,spot,direction,strategy):
    snap=snapshots.get(pd.Timestamp(signal_ts))
    if not snap: return None,{"blocked_reason":"NO_OPTION_SNAPSHOT_AT_SIGNAL"}
    ce=sorted({k for typ,k in snap if typ=="CE"}); pe=sorted({k for typ,k in snap if typ=="PE"})
    if strategy=="S103-C_RC_VIX_IC":
        common=sorted(set(ce)&set(pe))
        if not common: return None,{"blocked_reason":"NO_COMMON_CALL_PUT_STRIKES"}
        atm=min(common,key=lambda k:abs(k-spot))
        specs=[("CE",atm+100,-1),("CE",atm+200,1),("PE",atm-100,-1),("PE",atm-200,1)]
        if not all((typ,float(k)) in snap for typ,k,_ in specs):
            return None,{"atm":atm,"blocked_reason":"EXACT_CONDOR_STRIKES_UNAVAILABLE"}
        return [(typ,float(k),int(q)) for typ,k,q in specs],{"atm":float(atm),"short_call_strike":float(atm+100),
          "short_put_strike":float(atm-100),"structure":"SHORT_IRON_CONDOR_100_WINGS"}
    typ="CE" if direction>0 else "PE"; strikes=ce if typ=="CE" else pe
    if not strikes: return None,{"blocked_reason":f"NO_{typ}_STRIKES"}
    atm=float(min(strikes,key=lambda k:abs(k-spot))); wing=atm+100 if typ=="CE" else atm-100
    specs=[(typ,atm,1),(typ,wing,-1)]
    if not all((t,float(k)) in snap for t,k,_ in specs):
        return None,{"atm":atm,"blocked_reason":"EXACT_DEBIT_SPREAD_STRIKES_UNAVAILABLE"}
    return [(t,float(k),int(q)) for t,k,q in specs],{"atm":atm,"structure":"BULL_CALL_DEBIT_SPREAD" if direction>0 else "BEAR_PUT_DEBIT_SPREAD"}

def open_prices(snapshots,ts,legs):
    snap=snapshots.get(pd.Timestamp(ts))
    if not snap:return None
    ret={}
    for typ,k,_ in legs:
        x=snap.get((typ,float(k)))
        if x is None or not np.isfinite(x["open"]) or x["open"]<=0:return None
        ret[(typ,float(k))]=float(x["open"])
    return ret

def first_complete_open(after,deadline,spot_times,snapshots,legs):
    for ts in spot_times:
        if after < ts <= deadline:
            prices=open_prices(snapshots,ts,legs)
            if prices is not None:return pd.Timestamp(ts),prices
    return None

def exit_decision(strategy,direction,bars,entry_ts,hi,lo,stop_extreme,short_ce,short_pe):
    x=bars[(bars["timestamp"]>entry_ts)&(bars["timestamp"].dt.strftime("%H:%M")<="15:14")].sort_values("timestamp")
    for r in x.itertuples(index=False):
        close=float(r.close); ts=pd.Timestamp(r.timestamp)
        if strategy=="S103-A_XAC_ORB" and ((direction>0 and close<=hi) or (direction<0 and close>=lo)):
            return ts,"OPENING_RANGE_REENTRY_STOP"
        if strategy=="S103-B_FBR":
            if direction>0 and stop_extreme is not None and close<=stop_extreme:return ts,"SWEEP_EXTREME_STOP"
            if direction<0 and stop_extreme is not None and close>=stop_extreme:return ts,"SWEEP_EXTREME_STOP"
            if direction>0 and close>=hi:return ts,"OPPOSITE_RANGE_TARGET"
            if direction<0 and close<=lo:return ts,"OPPOSITE_RANGE_TARGET"
        if strategy=="S103-C_RC_VIX_IC":
            if short_ce is not None and close>=short_ce:return ts,"SHORT_CALL_STRIKE_BREACH"
            if short_pe is not None and close<=short_pe:return ts,"SHORT_PUT_STRIKE_BREACH"
    possible=bars[bars["timestamp"].dt.strftime("%H:%M")<="15:14"]
    if possible.empty:raise RuntimeError("no spot bar for intraday hard close")
    return pd.Timestamp(possible.iloc[-1]["timestamp"]),"INTRADAY_HARD_CLOSE"

def trade_case(legs,entry_raw,exit_raw,entry_ts,exit_ts,lot):
    base=compute_trade_case(legs,entry_raw,exit_raw,entry_ts,exit_ts,lot,1,1.0,10.0)
    stress=compute_trade_case(legs,entry_raw,exit_raw,entry_ts,exit_ts,lot,2,1.5,20.0)
    severe=compute_trade_case(legs,entry_raw,exit_raw,entry_ts,exit_ts,lot,1,1.5,20.0,impact_pct=0.0025,extra=50.0)
    return {"net_rupees":base["net_rupees"],"stress_net_rupees":stress["net_rupees"],
      "severe_stress_net_rupees":severe["net_rupees"],"gross_after_slippage_rupees":base["gross_after_slippage_rupees"],
      "fees_rupees":base["fees_rupees"],"risk_proxy_rupees":base["risk_proxy_rupees"],
      "entry_cash_credit_rupees":base["entry_cash_credit_rupees"]}

def session_range(bars,start,end):
    tm=bars["timestamp"].dt.strftime("%H:%M"); x=bars[(tm>=start)&(tm<end)]
    expected=int((pd.Timestamp(end)-pd.Timestamp(start)).total_seconds()/60)
    if len(x)<max(10,expected//2):return float("nan"),float("nan")
    return float(x.high.max()),float(x.low.min())

def daily_feature_map(global_daily,vix,day):
    breadth=global_breadth_direction(global_daily,day)
    ok,level,threshold=prior_vix_low(vix,day)
    return {"global_breadth_direction":breadth,"vix_low_gate":bool(ok),
            "prior_vix_level":float(level) if np.isfinite(level) else None,
            "prior_vix_threshold_75":float(threshold) if np.isfinite(threshold) else None}

def build_feature_audit(root,session_days,global_daily,flow_daily,sent_daily,vix):
    def stats(frame):
        if frame.empty:return {"available":False,"rows":0,"covered_days":0,"coverage_pct":0.0,"columns":[]}
        p=frame[(frame.date>=pd.Timestamp("2024-01-01"))&(frame.date<=pd.Timestamp("2025-12-31"))]
        numeric=[c for c in p.columns if c!="date" and pd.api.types.is_numeric_dtype(p[c])]
        n=int(p[numeric].notna().any(axis=1).sum()) if numeric else 0
        return {"available":True,"rows":len(p),"covered_days":n,"coverage_pct":100*n/max(len(session_days),1),"columns":numeric}
    return {"option_source":{"repo_id":HF_REPO,"revision":PINNED_REVISION,"license":"CC-BY-NC-4.0"},
      "trade_window":"2024-01-01 through 2025-12-31","session_days":len(session_days),
      "prior_session_global_daily":stats(global_daily),"prior_publication_fii_dii":stats(flow_daily),
      "prior_publication_news_sentiment":stats(sent_daily),
      "india_vix_rows_2024_2025":int(((vix.date>=pd.Timestamp("2024-01-01"))&(vix.date<=pd.Timestamp("2025-12-31"))).sum()),
      "excluded_modalities":["FII/DII and sentiment were audited but not used in triggers because the existing validation feature manifest shows major FII/DII missingness and point-in-time sentiment timestamps are not independently qualified.",
       "No option Greeks, futures basis, historical bid/ask/depth, or single-stock corporate actions are fabricated." ]}

def execute_candidate(strategy,day,bars,snapshots,signal,meta,expiry,lot):
    sig_ts=pd.Timestamp(signal["signal_ts"])
    spotrow=bars[bars.timestamp==sig_ts]
    if spotrow.empty:return {"strategy":strategy,"trade_date":str(day.date()),"expiry":str(expiry.date()),"split":"development" if day<=DEV_END else "validation","status":"BLOCKED_NO_SIGNAL_SPOT","signal_ts":str(sig_ts),"reason":"missing spot signal bar"},None
    spot=float(spotrow.iloc[-1].close); direction=int(signal.get("direction",0))
    legs,lmeta=make_legs(snapshots,sig_ts,spot,direction,strategy)
    split="development" if day<=DEV_END else "validation"
    if legs is None:return {"strategy":strategy,"trade_date":str(day.date()),"expiry":str(expiry.date()),"split":split,"status":"BLOCKED_STRIKE_OR_SIGNAL_SNAPSHOT","signal_ts":str(sig_ts),"reason":lmeta.get("blocked_reason")},None
    spot_times=sorted(pd.Timestamp(t) for t in bars.timestamp.tolist())
    dayend=pd.Timestamp(day).tz_localize(TZ)+pd.Timedelta(hours=15,minutes=25)
    entry_deadline=min(sig_ts+pd.Timedelta(minutes=5),dayend)
    entry=first_complete_open(sig_ts,entry_deadline,spot_times,snapshots,legs)
    if entry is None:return {"strategy":strategy,"trade_date":str(day.date()),"expiry":str(expiry.date()),"split":split,"status":"BLOCKED_ENTRY_NO_COMPLETE_OPEN","signal_ts":str(sig_ts),"reason":"no complete option open within five minutes"},None
    entry_ts,entry_raw=entry
    stop=signal.get("stop_extreme")
    sc=lmeta.get("short_call_strike"); sp=lmeta.get("short_put_strike")
    dec_ts,reason=exit_decision(strategy,direction,bars,entry_ts,float(meta.get("or_high",np.nan)),
                                float(meta.get("or_low",np.nan)),float(stop) if stop is not None else None,sc,sp)
    deadline=min(dec_ts+pd.Timedelta(minutes=10 if reason=="INTRADAY_HARD_CLOSE" else 5),dayend)
    exitfill=first_complete_open(dec_ts,deadline,spot_times,snapshots,legs)
    if exitfill is None:
        return {"strategy":strategy,"trade_date":str(day.date()),"expiry":str(expiry.date()),"split":split,
          "status":"BLOCKED_EXIT_NO_COMPLETE_OPEN","signal_ts":str(sig_ts),"entry_ts":str(entry_ts),
          "exit_decision_ts":str(dec_ts),"reason":"no complete option open after exit decision"},None
    exit_ts,exit_raw=exitfill; pnl=trade_case(legs,entry_raw,exit_raw,entry_ts,exit_ts,lot)
    row={"strategy":strategy,"trade_date":str(day.date()),"expiry":str(expiry.date()),"split":split,
         "status":"COMPLETED","setup":signal.get("setup",""),"signal_ts":str(sig_ts),"entry_ts":str(entry_ts),
         "exit_decision_ts":str(dec_ts),"exit_ts":str(exit_ts),"exit_reason":reason,"direction":direction,
         "lot_size":int(lot),"legs_json":json.dumps(legs),"entry_delay_minutes":int((entry_ts-sig_ts).total_seconds()/60),
         "exit_delay_minutes":int((exit_ts-dec_ts).total_seconds()/60),"or_high":meta.get("or_high"),
         "or_low":meta.get("or_low"),"prior_vix_level":meta.get("prior_vix_level"),
         "prior_vix_threshold_75":meta.get("prior_vix_threshold_75"),"global_breadth_direction":meta.get("global_breadth_direction"),**pnl}
    return row,row

def holm_adjust(pvalues):
    vals=np.array([p if p is not None and np.isfinite(p) else 1.0 for p in pvalues],float)
    order=np.argsort(vals); out=np.ones(len(vals)); prev=0.0
    for rank,idx in enumerate(order):
        prev=max(prev,min(1.0,(len(vals)-rank)*vals[idx]));out[idx]=prev
    return out.tolist()

def block_bootstrap(daily_values,seed):
    x=np.asarray(daily_values,dtype=float);x=x[np.isfinite(x)];n=len(x)
    if n<30:return {"status":"NOT_ESTIMABLE_LT30_SESSIONS","n_sessions":n,"mean_daily":float(x.mean()) if n else None,"ci95_low":None,"ci95_high":None,"p_one_sided":None,"block_size":BOOT_BLOCK,"replicates":0}
    b=min(BOOT_BLOCK,n); blocks=int(math.ceil(n/b)); offsets=np.arange(b);rng=np.random.default_rng(seed+n)
    boot=np.empty(BOOT_REPLICATES);null=np.empty(BOOT_REPLICATES);centered=x-x.mean()
    for i in range(BOOT_REPLICATES):
        starts=rng.integers(0,n,size=blocks);ix=((starts[:,None]+offsets[None,:])%n).ravel()[:n]
        boot[i]=x[ix].mean();null[i]=centered[ix].mean()
    return {"status":"COMPUTED_CIRCULAR_BLOCK_BOOTSTRAP","n_sessions":n,"mean_daily":float(x.mean()),
      "ci95_low":float(np.quantile(boot,.025)),"ci95_high":float(np.quantile(boot,.975)),
      "p_one_sided":float((np.sum(null>=x.mean())+1)/(BOOT_REPLICATES+1)),"block_size":b,"replicates":BOOT_REPLICATES}

def max_drawdown(daily):
    x=np.asarray(daily,dtype=float);x=x[np.isfinite(x)]
    if not len(x):return 0.0
    eq=np.cumsum(x);peak=np.maximum.accumulate(np.r_[0.0,eq])[1:]
    return float(np.max(peak-eq))

def profit_factor(values):
    x=np.asarray(values,dtype=float);g=float(x[x>0].sum());l=float(abs(x[x<0].sum()))
    return g/l if l>0 else (float("inf") if g>0 else None)

def run_discovery(root=ROOT,token=None):
    OUT.mkdir(parents=True,exist_ok=True);token=token or os.getenv("HF_TOKEN") or None
    index=parse_index(load_hf_file("index/NIFTY.parquet",token))
    # Build warm-up ranges from 2021 onward; no 2026 bars or expiries are used.
    expiry_dates=list_expiry_dates(token)
    if not expiry_dates:raise RuntimeError("No option expiry files in the pinned 2024-2025 sample.")
    global_daily=read_daily_source(root/"results/phase39_feature_source/global_daily.parquet")
    flow_daily=read_daily_source(root/"results/phase39_feature_source/fii_dii_daily.parquet")
    sent_daily=read_daily_source(root/"results/phase39_feature_source/sentiment_daily.parquet")
    vix_path=root/"data/phase40_vix/india_vix.csv"
    if not vix_path.is_file():raise FileNotFoundError(f"India VIX cache missing: {vix_path}")
    vix=pd.read_csv(vix_path)
    if not {"date","close"}.issubset(vix.columns):raise ValueError("India VIX CSV missing date/close")
    vix["date"]=pd.to_datetime(vix.date,errors="coerce").dt.normalize()
    vix["close"]=pd.to_numeric(vix.close,errors="coerce")
    vix=vix.dropna(subset=["date","close"]).sort_values("date").drop_duplicates("date").reset_index(drop=True)

    groups={pd.Timestamp(d):x.sort_values("timestamp").copy() for d,x in index.groupby("session_day",sort=True)}
    ranges={}
    for d,bars in groups.items():
        hi,lo=session_range(bars,"09:15","10:00");ranges[pd.Timestamp(d)]=hi-lo if np.isfinite(hi) and np.isfinite(lo) else float("nan")
    session_days=sorted(d for d in groups if DEV_START<=d<=VAL_END)
    eligible=[];excluded=[];expmap={}
    for d in session_days:
        e=expiry_for_session(d,expiry_dates)
        if e is None:excluded.append({"trade_date":str(d.date()),"status":"EXCLUDED_NO_ELIGIBLE_EXPIRY"})
        else:eligible.append(d);expmap[d]=e
    if len(session_days)<350 or len(eligible)<300:raise RuntimeError(f"Insufficient trading sessions: sample={len(session_days)}, eligible expiry={len(eligible)}")
    # Cache the entire current expiry file; filter it per session rather than re-downloading or reusing yesterday's filtered bars.
    cur_exp=None;cur_raw=None
    trades=[];coverage=[];daily_rows=[];load_errors=[];signals=Counter()
    for ix,day in enumerate(eligible,1):
        expiry=expmap[day]
        if cur_exp!=expiry:
            try:
                cur_raw=load_hf_file(f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet",token)
                cur_exp=expiry
            except Exception as exc:
                cur_raw=None;load_errors.append({"expiry":str(expiry.date()),"stage":"load","error":repr(exc)})
        bars=groups.get(day)
        if bars is None or bars.empty:excluded.append({"trade_date":str(day.date()),"status":"EXCLUDED_NO_INDEX_BARS"});continue
        bars=bars[(bars.timestamp.dt.strftime("%H:%M")>="09:15")&(bars.timestamp.dt.strftime("%H:%M")<="15:30")].copy()
        if len(bars)<180:
            excluded.append({"trade_date":str(day.date()),"expiry":str(expiry.date()),"status":"EXCLUDED_SHORT_SESSION"})
            continue
        split="development" if day<=DEV_END else "validation"
        if cur_raw is None:
            excluded.append({"trade_date":str(day.date()),"expiry":str(expiry.date()),"status":"EXCLUDED_OPTION_FILE_ERROR"})
            for strategy in STRATEGIES:
                daily_rows.append({"strategy":strategy,"trade_date":str(day.date()),"split":split,"net_rupees":np.nan,"stress_net_rupees":np.nan,"severe_stress_net_rupees":np.nan,"session_status":"NO_OPTION_FILE"})
            continue
        chain=parse_chain(cur_raw,day)
        snapshots=snapshot_map(chain)
        f=daily_feature_map(global_daily,vix,day)
        hi15,lo15=opening_range(bars,"09:15","09:30")
        sig_a=find_orb_signal(bars,hi15,lo15,f["global_breadth_direction"])
        sig_b=find_failed_break_signal(bars,hi15,lo15)
        hi45,lo45=session_range(bars,"09:15","10:00")
        today_range=hi45-lo45 if np.isfinite(hi45) and np.isfinite(lo45) else float("nan")
        prior=[ranges.get(d,float("nan")) for d in sorted(ranges) if d<day][-20:]
        sig_c=None;meta_c={"current_range":today_range,"prior_median_range":float(np.median(prior)) if len(prior)==20 and np.isfinite(prior).all() else None,**f}
        if compression_setup(today_range,prior,bool(f["vix_low_gate"])):
            rows=bars[bars.timestamp.dt.strftime("%H:%M")=="09:59"]
            if not rows.empty:sig_c={"signal_ts":pd.Timestamp(rows.iloc[-1].timestamp),"direction":0,"setup":"RANGE_COMPRESSION_LOW_VIX_IRON_CONDOR"}
        metas={"S103-A_XAC_ORB":{"or_high":hi15,"or_low":lo15,**f},
               "S103-B_FBR":{"or_high":hi15,"or_low":lo15,**f},
               "S103-C_RC_VIX_IC":meta_c}
        sigs={"S103-A_XAC_ORB":sig_a,"S103-B_FBR":sig_b,"S103-C_RC_VIX_IC":sig_c}
        for strategy in STRATEGIES:
            row={"strategy":strategy,"trade_date":str(day.date()),"split":split,"net_rupees":0.0,
                 "stress_net_rupees":0.0,"severe_stress_net_rupees":0.0,"session_status":"ELIGIBLE_NO_SIGNAL"}
            sig=sigs[strategy]
            if sig is not None:
                signals[strategy]+=1;row["session_status"]="SIGNAL"
                attempt,completed=execute_candidate(strategy,day,bars,snapshots,sig,metas[strategy],expiry,lot_size_for_expiry(expiry))
                trades.append(attempt);coverage.append({"strategy":strategy,"trade_date":str(day.date()),"expiry":str(expiry.date()),
                  "split":split,"signal_ts":attempt.get("signal_ts",""),"status":attempt.get("status",""),"reason":attempt.get("reason","")})
                if completed is not None:
                    row["net_rupees"]=completed["net_rupees"];row["stress_net_rupees"]=completed["stress_net_rupees"]
                    row["severe_stress_net_rupees"]=completed["severe_stress_net_rupees"];row["session_status"]="TRADE_COMPLETED"
                else:
                    row["session_status"]="EXECUTION_GAP"
                    row["net_rupees"]=np.nan;row["stress_net_rupees"]=np.nan;row["severe_stress_net_rupees"]=np.nan
            daily_rows.append({"strategy":strategy,"trade_date":str(day.date()),"split":split,**row})
        if ix%25==0:print(f"Phase 103 processed {ix}/{len(eligible)} eligible sessions, expiry={expiry.date()}",flush=True)
    tradesdf=pd.DataFrame(trades);coverdf=pd.DataFrame(coverage);daily=pd.DataFrame(daily_rows)
    if tradesdf.empty:raise RuntimeError("No entry signals generated; no empirical strategy result can be estimated")
    tradesdf.to_csv(OUT/"trades.csv",index=False);coverdf.to_csv(OUT/"coverage_audit.csv",index=False);daily.to_csv(OUT/"daily_pnl.csv",index=False)
    pd.DataFrame(excluded).to_csv(OUT/"session_exclusions.csv",index=False);pd.DataFrame(load_errors).to_csv(OUT/"source_load_errors.csv",index=False)
    summaries=[]
    for strategy in STRATEGIES:
        for split in ("development","validation"):
            sub=daily[(daily.strategy==strategy)&(daily.split==split)].sort_values("trade_date")
            ta=tradesdf[(tradesdf.strategy==strategy)&(tradesdf.split==split)]
            done=ta[ta.status=="COMPLETED"];cv=coverdf[(coverdf.strategy==strategy)&(coverdf.split==split)]
            nsignal=len(cv); ncompleted=len(done); exit_gaps=int((ta.status=="BLOCKED_EXIT_NO_COMPLETE_OPEN").sum())
            entry_gaps=int(ta.status.str.startswith("BLOCKED").sum()-exit_gaps)
            coverage_pct=100*ncompleted/nsignal if nsignal else 100.0
            daily_pnl=pd.to_numeric(sub.net_rupees,errors="coerce").to_numpy(float)
            has_gap=entry_gaps>0 or exit_gaps>0 or not np.isfinite(daily_pnl).all()
            boot={"status":"NOT_ESTIMABLE_COVERAGE_GAP","n_sessions":int(np.isfinite(daily_pnl).sum()),"mean_daily":None,"ci95_low":None,"ci95_high":None,"p_one_sided":None,"replicates":0} if has_gap else block_bootstrap(daily_pnl,RNG_SEED+STRATEGIES.index(strategy)+(0 if split=="development" else 100))
            p=pd.to_numeric(done.get("net_rupees",pd.Series(dtype=float)),errors="coerce").dropna().to_numpy(float)
            sp=pd.to_numeric(done.get("stress_net_rupees",pd.Series(dtype=float)),errors="coerce").dropna().to_numpy(float)
            sev=pd.to_numeric(done.get("severe_stress_net_rupees",pd.Series(dtype=float)),errors="coerce").dropna().to_numpy(float)
            summaries.append({"strategy":strategy,"split":split,"eligible_sessions":len(sub),"signal_opportunities":nsignal,
              "completed_trades":ncompleted,"entry_or_strike_gaps":entry_gaps,"exit_gaps":exit_gaps,"execution_coverage_pct":coverage_pct,
              "net_completed_trades_rupees":float(p.sum()),"stress_net_completed_trades_rupees":float(sp.sum()),
              "severe_stress_net_completed_trades_rupees":float(sev.sum()),
              "mean_net_per_completed_trade":float(p.mean()) if len(p) else None,"median_net_per_completed_trade":float(np.median(p)) if len(p) else None,
              "win_rate":float((p>0).mean()) if len(p) else None,"profit_factor":profit_factor(p.tolist()) if len(p) else None,
              "max_drawdown_daily_pnl_rupees":None if has_gap else max_drawdown(daily_pnl),
              "bootstrap_status":boot["status"],"mean_daily_net_rupees":boot.get("mean_daily"),
              "mean_daily_net_ci95_low":boot.get("ci95_low"),"mean_daily_net_ci95_high":boot.get("ci95_high"),
              "p_one_sided":boot.get("p_one_sided"),"holm_adjusted_p_validation":None,
              "candidate_eligible_for_independent_followup":False,"promotion_decision":"NOT_PROMOTED"})
    validations=[r for r in summaries if r["split"]=="validation"]
    adj=holm_adjust([r["p_one_sided"] for r in validations])
    for r,padj in zip(validations,adj):
        r["holm_adjusted_p_validation"]=padj
        r["candidate_eligible_for_independent_followup"]=bool(r["completed_trades"]>=30 and r["execution_coverage_pct"]>=95
          and r["exit_gaps"]==0 and r["net_completed_trades_rupees"]>0 and r["stress_net_completed_trades_rupees"]>0
          and r["severe_stress_net_completed_trades_rupees"]>0 and r["mean_daily_net_ci95_low"] is not None
          and r["mean_daily_net_ci95_low"]>0 and padj<0.05 and r["max_drawdown_daily_pnl_rupees"] is not None
          and r["max_drawdown_daily_pnl_rupees"]<=MAX_DRAWDOWN_RUPEES)
        r["promotion_decision"]="ELIGIBLE_FOR_NEW_CONFIRMATORY_PHASE_ONLY" if r["candidate_eligible_for_independent_followup"] else "NOT_PROMOTED"
    summary=pd.DataFrame(summaries);summary.to_csv(OUT/"summary.csv",index=False)
    audit=build_feature_audit(root,session_days,global_daily,flow_daily,sent_daily,vix)
    audit["eligible_option_expiry_file_count"]=len(expiry_dates);audit["latest_option_expiry_available"]=str(max(expiry_dates).date())
    audit["latest_underlying_timestamp"]=str(index.timestamp.max())
    (OUT/"feature_coverage.json").write_text(json.dumps(audit,indent=2,default=str)+"\n",encoding="utf-8")
    result={"phase":103,"status":"PASS","decision":"NO_STRATEGY_PROMOTED","pinned_source_revision":PINNED_REVISION,
       "option_data_limited_to_2025":True,"holdout_2026_options_loaded":False,"sessions_2024_2025":len(session_days),
       "sessions_with_eligible_expiry":len(eligible),"session_exclusions":len(excluded),"source_load_error_rows":len(load_errors),
       "signal_attempts":len(coverdf),"completed_trade_rows":int((tradesdf.status=="COMPLETED").sum()),
       "blocked_exit_rows":int((tradesdf.status=="BLOCKED_EXIT_NO_COMPLETE_OPEN").sum()),
       "all_signal_rows_have_audit":len(coverdf)==len(tradesdf),"integrity_errors":[],
       "results":[{"strategy":r["strategy"],"trades":r["completed_trades"],"base_net":r["net_completed_trades_rupees"],
       "stress_net":r["stress_net_completed_trades_rupees"],"severe_net":r["severe_stress_net_completed_trades_rupees"],
       "coverage_pct":r["execution_coverage_pct"],"ci95":[r["mean_daily_net_ci95_low"],r["mean_daily_net_ci95_high"]],
       "holm_p":r["holm_adjusted_p_validation"],"eligible_for_independent_followup":r["candidate_eligible_for_independent_followup"]}
       for r in validations],
       "limits":["OHLC open prices and adverse slippage are a proxy, not quote/depth fills.",
       "Paytm Money charges are modeled by the existing date-effective assumptions and not verified contract notes.",
       "The data license is CC-BY-NC-4.0; commercial deployment rights are not established.",
       "FII/DII/sentiment are audited but not used as unqualified intraday inputs; no Greeks or futures basis are fabricated.",
       "No 2026 options were loaded. Drawdown is cumulative daily P&L, not full intratrade mark-to-market."]}
    errors=[]
    if len(coverdf)!=len(tradesdf):errors.append("signal coverage audit rows do not reconcile to attempts")
    if load_errors:errors.append(f"{len(load_errors)} option expiry files failed to load")
    if len(session_days)<350 or len(eligible)<300:errors.append("sample session gate failed")
    result["integrity_errors"]=errors;result["checks_total"]=3;result["checks_passed"]=3-len(errors)
    result["status"]="PASS" if not errors else "FAIL"
    (OUT/"validation.json").write_text(json.dumps(result,indent=2,default=str)+"\n",encoding="utf-8")
    _write_report(summary,result,audit)
    _write_plot(summary)
    print(json.dumps({"status":result["status"],"signals":len(coverdf),"completed_trades":result["completed_trade_rows"],
      "blocked_exits":result["blocked_exit_rows"],"results":result["results"],"integrity_errors":errors},indent=2),flush=True)
    if errors:raise RuntimeError("; ".join(errors))
    return result

def _write_report(summary,result,audit):
    val=summary[summary.split=="validation"]
    display=val[["strategy","completed_trades","execution_coverage_pct","net_completed_trades_rupees",
      "stress_net_completed_trades_rupees","severe_stress_net_completed_trades_rupees","mean_daily_net_ci95_low",
      "mean_daily_net_ci95_high","holm_adjusted_p_validation","max_drawdown_daily_pnl_rupees",
      "candidate_eligible_for_independent_followup"]]
    lines=["# Phase 103 — Novel Intraday Strategy Discovery Results","",
      f"Audit status: {result['status']}","Promotion decision: NO STRATEGY PROMOTED",
      f"Source revision: {PINNED_REVISION} (CC-BY-NC-4.0)","Sample: 2024 development / 2025 validation; 2026 options excluded.","",
      "## 2025 validation results","",display.to_string(index=False),"",
      "All results are fixed-one-lot rupee P&L sums, not compounded account returns. The decision statistic is mean net rupees per eligible session, including zero outcomes on sessions with no signal. A missing exit leaves that session non-estimable and disables inference rather than fabricating a price.","",
      "## Development results","",summary[summary.split=="development"].to_string(index=False),"",
      "## Coverage and execution audit","",
      f"- Signals: {result['signal_attempts']}; completed trades: {result['completed_trade_rows']}; blocked exits: {result['blocked_exit_rows']}.",
      f"- Option file load failures: {result['source_load_error_rows']}; eligible sessions: {result['sessions_with_eligible_expiry']}.",
      "- Entries use first complete observed option OPEN after signal within five minutes. Exits use first complete observed option OPEN after exit decision within the deadline. No interpolation or forward fill.",
      "- Each signal has a corresponding coverage-audit row; unfilled opportunities remain explicit.",
      "","## Feature/source availability audit","","",json.dumps(audit,indent=2,default=str),"",
      "FII/DII and sentiment were checked but not used as triggers because their point-in-time availability is not sufficiently qualified. Global return and India VIX features are strictly lagged by at least one session.","",
      "## Frozen hypotheses","",
      "S103-A: opening-range breakout with prior-session cross-market breadth confirmation; one 100-point debit vertical.",
      "S103-B: first opening-range breakout reversed only after a later closing-price reclaim within five bars; one 100-point debit vertical.",
      "S103-C: 09:15–09:59 range compression below its previous-20-session median plus prior-session low-VIX gate; 100-point-wide iron condor with short strikes 100 points from ATM and wings 200 points from ATM.","",
      "## Cost, risk and inference","",
      "Base: one adverse ₹0.05 tick per leg fill, ₹10/order and date-effective statutory/exchange levies/GST. Stress: two ticks, ₹20/order and +50% charges. Severe stress: one tick plus 0.25% adverse impact per fill, ₹20/order, +50% charges and ₹50 per round trip.",
      "Daily outcomes are bootstrapped in circular five-session blocks with 5,000 resamples. Holm correction covers exactly the three registered candidates. Follow-up eligibility requires ≥30 2025 trades, ≥95% filled signals, no exits missing, positive base and both stresses, 95% CI lower bound above zero, Holm p<0.05 and drawdown ≤₹60,000.","",
      "## Limitations","",
      "Minute OHLC is not executable bid/ask/depth. Costs follow the repo assumptions rather than independently verified Paytm Money contract notes. The dataset's CC-BY-NC license does not clear commercial use. FII/DII and news sentiment are only source-audited; Greeks, futures basis and depth were not invented. No 2026 options were loaded. Drawdown is cumulative daily P&L, not mark-to-market equity drawdown.","",
      "## Artifacts","",
      "trades.csv: completed and blocked attempts.","daily_pnl.csv: daily net, stress and severe stress by strategy/session.","coverage_audit.csv: signal statuses.","session_exclusions.csv and source_load_errors.csv: explicit source gaps.","summary.csv, feature_coverage.json, validation.json and comparison.svg: aggregate outcomes."]
    (OUT/"PHASE103_REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

def _write_plot(summary):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    x=summary[summary.split.isin(["development","validation"])].copy()
    labels=[f"{r.strategy.replace('S103-','')}\n{r.split}" for r in x.itertuples()]
    vals=[x.net_completed_trades_rupees.to_numpy(float),x.stress_net_completed_trades_rupees.to_numpy(float),x.severe_stress_net_completed_trades_rupees.to_numpy(float)]
    pos=np.arange(len(labels));w=.24
    fig,ax=plt.subplots(figsize=(13,6))
    ax.bar(pos-w,vals[0],w,label="Base");ax.bar(pos,vals[1],w,label="Friction stress");ax.bar(pos+w,vals[2],w,label="Severe stress")
    ax.axhline(0,linewidth=.8);ax.set_xticks(pos);ax.set_xticklabels(labels,rotation=35,ha="right")
    ax.set_ylabel("Net P&L (₹, fixed one lot)");ax.set_title("Phase 103 — frozen strategy hypotheses");ax.legend()
    fig.tight_layout();fig.savefig(OUT/"comparison.svg",format="svg");plt.close(fig)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo-root",default=str(ROOT))
    args=parser.parse_args()
    run_discovery(Path(args.repo_root).resolve())

if __name__=="__main__":main()
