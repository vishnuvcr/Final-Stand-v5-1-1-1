#!/usr/bin/env python3
"""Phase 98 frozen NIFTY opening-range breakout + defined-risk debit spread."""
from __future__ import annotations
import json, math, os, re, traceback
from bisect import bisect_left
from collections import Counter
from datetime import date, datetime, time
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from huggingface_hub import HfApi, hf_hub_download

TZ="Asia/Kolkata"; HF_REPO="thetrademarkk/india-index-options-1m"
HF_REVISION="0f4800e43e6f96cec0794369d78eb4d3c4211ef5"; TICK=.05
DEV_START,DEV_END=date(2021,5,27),date(2023,12,31)
VAL_START,VAL_END=date(2024,1,1),date(2025,12,31)
MAX_EXPIRY=pd.Timestamp("2025-12-31",tz=TZ)
OUT=Path("results/phase98_opening_range_spread"); OUT.mkdir(parents=True,exist_ok=True)
SEED,N_RESAMPLES,BLOCK_LEN=980010,10000,5
ISSUES=[]; EXPIRY_FILES_USED=set(); SOURCE_SCHEMA={}; COUNTS=Counter()

def localize(s):
    x=pd.to_datetime(s,errors="coerce")
    return x.dt.tz_localize(TZ) if x.dt.tz is None else x.dt.tz_convert(TZ)

def split_for_day(d):
    if DEV_START<=d<=DEV_END:return "development"
    if VAL_START<=d<=VAL_END:return "validation"
    return "excluded"

def lot_size_for_expiry(e):
    if e<pd.Timestamp("2021-07-29",tz=TZ):return 75
    if e<pd.Timestamp("2024-05-02",tz=TZ):return 50
    if e<=pd.Timestamp("2024-12-26",tz=TZ):return 25
    if e<=pd.Timestamp("2025-01-23",tz=TZ):return 75
    if e==pd.Timestamp("2025-01-30",tz=TZ):return 25
    if e<pd.Timestamp("2026-01-06",tz=TZ):return 75
    return 65

def fee_rates(d):
    t=pd.Timestamp(d,tz=TZ)
    stt=.0010 if t>=pd.Timestamp("2024-10-01",tz=TZ) else .000625
    txn,ipft=(.0003503,.000005) if t>=pd.Timestamp("2024-10-01",tz=TZ) else (.000495,.000005)
    return stt,txn,.000001,ipft,.00003

def slip(px,action,ticks):
    px=float(px)
    if not math.isfinite(px) or px<=0:raise ValueError("invalid_price")
    out=px+TICK*ticks if action=="buy" else px-TICK*ticks
    if not math.isfinite(out) or out<=0:raise ValueError("nonpositive_after_slippage")
    return round(out,8)

def fees(orders,bpo,mult):
    brokerage=bpo*len(orders); exchange=sebi=ipft=stt=stamp=0.
    for d,side,px,qty in orders:
        sr,tx,se,ip,sd=fee_rates(d); turnover=max(0.,float(px))*abs(int(qty))
        exchange+=tx*turnover*mult; sebi+=se*turnover*mult; ipft+=ip*turnover*mult
        if side=="sell":stt+=sr*turnover*mult
        else:stamp+=sd*turnover*mult
    gst=.18*(brokerage+exchange+sebi+ipft)
    out={"brokerage":brokerage,"exchange_transaction":exchange,"sebi":sebi,"ipft":ipft,"stt":stt,"stamp_duty":stamp,"gst":gst}
    out["total"]=sum(out.values());return out

def opening_range_signal(session):
    if session.empty:return {"status":"NO_INDEX_ROWS"}
    z=session.copy();z["timestamp"]=localize(z.timestamp)
    z=z.dropna(subset=["timestamp"]).drop_duplicates("timestamp").sort_values("timestamp")
    d=z.timestamp.iloc[0].date(); start=pd.Timestamp(datetime.combine(d,time(9,15)),tz=TZ)
    rts=pd.date_range(start,periods=15,freq="min")
    sts=pd.date_range(start+pd.Timedelta(minutes=15),pd.Timestamp(datetime.combine(d,time(14,45)),tz=TZ),freq="min")
    ix=z.set_index("timestamp")
    if not all(t in ix.index for t in rts):return {"status":"INDEX_OPENING_RANGE_INCOMPLETE"}
    if not all(t in ix.index for t in sts):return {"status":"INDEX_SIGNAL_SCAN_INCOMPLETE"}
    rg=ix.loc[rts]
    if rg[["high","low"]].isna().any().any():return {"status":"INDEX_OPENING_RANGE_BAD_PRICE"}
    hi,lo=float(rg.high.max()),float(rg.low.min())
    for ts in sts:
        c=float(ix.loc[ts,"close"])
        if not math.isfinite(c):return {"status":"INDEX_SIGNAL_SCAN_BAD_PRICE"}
        if c>hi:return {"status":"SIGNAL","direction":"BULLISH","signal_ts":ts,"signal_spot":c,"or_high":hi,"or_low":lo}
        if c<lo:return {"status":"SIGNAL","direction":"BEARISH","signal_ts":ts,"signal_spot":c,"or_high":hi,"or_low":lo}
    return {"status":"NO_BREAKOUT","or_high":hi,"or_low":lo}

def vix_filter_state(vix,d):
    if vix.empty:return {"available":False,"skip":False,"reason":"VIX_DATA_EMPTY"}
    p=vix[vix.date<pd.Timestamp(d,tz=TZ)].sort_values("date")
    if len(p)<253:return {"available":False,"skip":False,"reason":"VIX_HISTORY_LT_253"}
    close=float(p.iloc[-1].vix); hist=p.iloc[:-1].vix.tail(252).astype(float)
    if len(hist)<252 or not math.isfinite(close):return {"available":False,"skip":False,"reason":"VIX_THRESHOLD_HISTORY_INCOMPLETE"}
    q=float(hist.quantile(.75))
    return {"available":True,"skip":close>q,"prior_close":close,"threshold":q,"prior_observation_date":str(p.iloc[-1].date.date())}

def mode_step(snap):
    modes=[]
    for typ in ("CE","PE"):
        s=np.sort(snap.loc[snap.option_type==typ,"strike"].dropna().unique().astype(float))
        dif=np.round(np.diff(s),8);dif=dif[dif>0]
        if len(dif):
            c=Counter(dif.tolist());modes.append(float(sorted(c.items(),key=lambda v:(-v[1],v[0]))[0][0]))
    return modes[0] if modes else None

def prep_options(x):
    if x.empty:return x
    x=x.copy();x["timestamp"]=localize(x.timestamp)
    x["option_type"]=x.option_type.astype(str).str.upper().str.strip().replace({"CALL":"CE","PUT":"PE"})
    x["strike"]=pd.to_numeric(x.strike,errors="coerce")
    if "oi" not in x.columns and "open_interest" in x.columns:
        x["oi"] = x["open_interest"]
    for c in ("open","close","volume","oi"):
        if c in x.columns:x[c]=pd.to_numeric(x[c],errors="coerce")
    return x[x.option_type.isin(["CE","PE"])&x.strike.notna()&x.timestamp.notna()].drop_duplicates().sort_values(["timestamp","option_type","strike"]).reset_index(drop=True)

def val_at(x,ts,typ,strike,field):
    if field not in x.columns:return None
    z=x[(x.timestamp==ts)&(x.option_type==typ)&np.isclose(x.strike.astype(float),float(strike),atol=1e-7,rtol=0)]
    if len(z)!=1:return None
    v=pd.to_numeric(pd.Series([z.iloc[0][field]]),errors="coerce").iloc[0]
    return float(v) if pd.notna(v) and math.isfinite(float(v)) else None

def load_index():
    p=hf_hub_download(repo_id=HF_REPO,filename="index/NIFTY.parquet",repo_type="dataset",revision=HF_REVISION,token=os.getenv("HF_TOKEN") or None)
    names=pq.ParquetFile(p).schema_arrow.names;req={"timestamp","open","high","low","close"}
    if not req.issubset(names):raise ValueError(f"index_schema_missing:{sorted(req-set(names))}")
    SOURCE_SCHEMA["index"]=names;x=pd.read_parquet(p,columns=sorted(req));x["timestamp"]=localize(x.timestamp)
    x=x.dropna(subset=["timestamp","open","high","low","close"])
    x=x[(x.timestamp.dt.date>=DEV_START)&(x.timestamp.dt.date<=VAL_END)]
    return x.drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)

def list_expiries():
    files=HfApi().list_repo_files(repo_id=HF_REPO,repo_type="dataset",revision=HF_REVISION);out=[]
    for f in files:
        m=re.fullmatch(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet",f)
        if m:
            e=pd.Timestamp(m.group(1),tz=TZ)
            if e.date()<=VAL_END:out.append(e)
    return sorted(set(out))

def load_chain_day(expiry,d):
    name=f"options/NIFTY/{expiry.date().isoformat()}.parquet"
    p=hf_hub_download(repo_id=HF_REPO,filename=name,repo_type="dataset",revision=HF_REVISION,token=os.getenv("HF_TOKEN") or None)
    pf=pq.ParquetFile(p);names=pf.schema_arrow.names;req={"timestamp","open","close","option_type","strike"}
    if not req.issubset(names):raise ValueError(f"option_schema_missing:{name}:{sorted(req-set(names))}")
    cols=[c for c in ("timestamp","open","close","option_type","strike","volume","oi","open_interest") if c in names]
    SOURCE_SCHEMA[name]=names
    lo=pd.Timestamp(datetime.combine(d,time(9,15)),tz=TZ);hi=pd.Timestamp(datetime.combine(d,time(15,16)),tz=TZ)
    ts_type=pf.schema_arrow.field("timestamp").type
    # Match Arrow scalar type exactly, including unit and timezone, for predicate pushdown.
    a=pa.scalar(lo.to_pydatetime(),type=ts_type)
    b=pa.scalar(hi.to_pydatetime(),type=ts_type)
    tab=pq.read_table(p,columns=cols,filters=[("timestamp",">=",a),("timestamp","<=",b)])
    x=tab.to_pandas()
    if x.empty:return prep_options(x)
    x["timestamp"]=localize(x.timestamp);x=x[(x.timestamp>=lo)&(x.timestamp<=hi)]
    EXPIRY_FILES_USED.add(name);COUNTS["option_day_rows_loaded"]+=len(x)
    return prep_options(x)

def select_vertical(chain,ts,spot,direction):
    s=chain[chain.timestamp==ts]
    if s.empty:return {"status":"NO_SIGNAL_TIME_CHAIN"}
    step=mode_step(s)
    if step is None or step<=0:return {"status":"NO_STRIKE_STEP"}
    ce=set(s.loc[s.option_type=="CE","strike"].astype(float));pe=set(s.loc[s.option_type=="PE","strike"].astype(float))
    common=sorted(ce&pe)
    if not common:return {"status":"NO_COMMON_ATM_STRIKE"}
    atm=min(common,key=lambda k:(abs(k-float(spot)),k));typ="CE" if direction=="BULLISH" else "PE"
    ks=float(atm+2*step if direction=="BULLISH" else atm-2*step)
    if ks<=0:return {"status":"INVALID_SHORT_STRIKE"}
    return {"status":"OK","option_type":typ,"atm":float(atm),"step":float(step),"long_strike":float(atm),"short_strike":ks,"width":abs(ks-float(atm))}

def run_scenario(chain,d,entry,direction,v,lot,ticks,bpo,mult):
    typ,kl,ks=v["option_type"],float(v["long_strike"]),float(v["short_strike"])
    lm,sm=val_at(chain,entry,typ,kl,"open"),val_at(chain,entry,typ,ks,"open")
    if lm is None or sm is None or lm<=0 or sm<=0:return {"status":"ENTRY_OPEN_MISSING"}
    try:el,es=slip(lm,"buy",ticks),slip(sm,"sell",ticks)
    except ValueError as e:return {"status":f"ENTRY_PRICE_INVALID:{e}"}
    debit,width=el-es,float(v["width"])
    if not 0<debit<width:return {"status":"DEBIT_OUTSIDE_VERTICAL_WIDTH","debit":debit}
    target,stop=debit+.5*(width-debit),.5*debit
    last=pd.Timestamp(datetime.combine(d,time(15,14)),tz=TZ)
    trigger_ts=None;trigger="TIME"
    for ts in pd.date_range(entry,last,freq="min"):
        lc,sc=val_at(chain,ts,typ,kl,"close"),val_at(chain,ts,typ,ks,"close")
        if lc is None or sc is None:continue
        mark=lc-sc
        if mark>=target:trigger_ts,trigger=ts,"TARGET";break
        if mark<=stop:trigger_ts,trigger=ts,"STOP";break
    end=trigger_ts if trigger_ts is not None else last;path=pd.date_range(entry,end,freq="min")
    seen=sum(val_at(chain,t,typ,kl,"close") is not None and val_at(chain,t,typ,ks,"close") is not None for t in path)
    coverage=seen/len(path) if len(path) else 0.
    if coverage<.95:return {"status":"ACTIVE_PATH_COVERAGE_LT_95","path_coverage":coverage,"path_expected":len(path),"path_observed":seen}
    ex=trigger_ts+pd.Timedelta(minutes=1) if trigger_ts is not None else pd.Timestamp(datetime.combine(d,time(15,15)),tz=TZ)
    if ex>pd.Timestamp(datetime.combine(d,time(15,15)),tz=TZ):return {"status":"EXIT_AFTER_CUTOFF"}
    xl0,xs0=val_at(chain,ex,typ,kl,"open"),val_at(chain,ex,typ,ks,"open")
    if xl0 is None or xs0 is None or xl0<=0 or xs0<=0:return {"status":"EXIT_OPEN_MISSING","path_coverage":coverage,"exit_ts":str(ex)}
    try:xl,xs=slip(xl0,"sell",ticks),slip(xs0,"buy",ticks)
    except ValueError as e:return {"status":f"EXIT_PRICE_INVALID:{e}","path_coverage":coverage}
    gross=((xl-el)+(es-xs))*lot
    orders=[(d,"buy",el,lot),(d,"sell",es,lot),(d,"sell",xl,lot),(d,"buy",xs,lot)]
    fc=fees(orders,bpo,mult)
    return {"status":"COMPLETE","entry_ts":str(entry),"exit_ts":str(ex),"trigger":trigger,
            "trigger_ts":str(trigger_ts) if trigger_ts is not None else None,"path_coverage":coverage,
            "entry_long_mid":lm,"entry_short_mid":sm,"entry_long_fill":el,"entry_short_fill":es,
            "exit_long_mid":xl0,"exit_short_mid":xs0,"exit_long_fill":xl,"exit_short_fill":xs,
            "debit_points":debit,"width_points":width,"target_points":target,"stop_points":stop,
            "gross_after_slippage_before_fees":gross,"fees":fc,"net":gross-fc["total"],
            "max_defined_loss_rupees":debit*lot,"potential_max_profit_rupees":(width-debit)*lot}

def read_vix():
    p=Path("data/phase40_vix/india_vix.csv")
    if not p.exists():return pd.DataFrame(columns=["date","vix"])
    x=pd.read_csv(p);dc=next((c for c in x.columns if c.lower()=="date"),None);cc=next((c for c in x.columns if c.lower()=="close"),None)
    if not dc or not cc:return pd.DataFrame(columns=["date","vix"])
    x["date"]=pd.to_datetime(x[dc],errors="coerce");x["date"]=x.date.dt.tz_localize(TZ) if x.date.dt.tz is None else x.date.dt.tz_convert(TZ)
    x["vix"]=pd.to_numeric(x[cc],errors="coerce")
    return x[["date","vix"]].dropna().drop_duplicates("date").sort_values("date").reset_index(drop=True)

def profit_factor(x):
    w=float(x[x>0].sum());l=float(-x[x<0].sum());return w/l if l>0 else (float("inf") if w>0 else float("nan"))

def drawdown(x):
    if not len(x):return float("nan")
    c=np.cumsum(x);return float(np.max(np.maximum.accumulate(np.r_[0.,c])[1:]-c))

def es95(x):
    if not len(x):return float("nan")
    q=float(np.quantile(x,.05));z=x[x<=q];return float(z.mean()) if len(z) else q

def block_ci(x,rng):
    x=np.asarray(x,float);n=len(x)
    if n<20 or not np.isfinite(x).all():return [float("nan"),float("nan")]
    out=np.empty(N_RESAMPLES)
    for i in range(N_RESAMPLES):
        parts=[];left=n
        while left:
            j=int(rng.integers(0,max(1,n-BLOCK_LEN+1)));p=x[j:min(n,j+BLOCK_LEN)]
            take=min(left,len(p));parts.append(p[:take]);left-=take
        out[i]=np.concatenate(parts).mean()
    return [float(np.quantile(out,.025)),float(np.quantile(out,.975))]

def signflip(x,rng):
    x=np.asarray(x,float)
    if len(x)<20 or not np.isfinite(x).all():return float("nan")
    observed=float(x.mean());s=rng.choice(np.array([-1.,1.]),size=(N_RESAMPLES,len(x)))
    return float((1+np.count_nonzero((s*x[None,:]).mean(axis=1)>=observed))/(N_RESAMPLES+1))

def holm(ps):
    a=np.asarray(ps,float);o=np.full(len(a),np.nan);ids=np.where(np.isfinite(a))[0];ids=ids[np.argsort(a[ids])];run=0.;m=len(ids)
    for rank,i in enumerate(ids):run=max(run,min(1.,(m-rank)*a[i]));o[i]=run
    return o.tolist()

def trade_summary(rows,arm,split):
    z=[r for r in rows if r.get(arm+"_taken") and r.get("split")==split and r.get("base_status")=="COMPLETE"]
    b=np.asarray([float(r["base_net"]) for r in z]);s=np.asarray([float(r["stress_net"]) for r in z if r.get("stress_status")=="COMPLETE"])
    return {"arm":arm,"split":split,"completed_trades":len(b),"base_net_pnl":float(b.sum()) if len(b) else 0.,
      "stress_net_pnl":float(s.sum()) if len(s) else 0.,"mean_net_per_trade":float(b.mean()) if len(b) else None,
      "median_net_per_trade":float(np.median(b)) if len(b) else None,"win_rate":float(np.mean(b>0)) if len(b) else None,
      "profit_factor":profit_factor(b) if len(b) else None,"max_drawdown_trade_order":drawdown(b) if len(b) else None,
      "worst_trade":float(b.min()) if len(b) else None,"expected_shortfall_95":es95(b) if len(b) else None,
      "stress_completed_trades":len(s)}

def main():
  try:
    idx=load_index();vix=read_vix();expiries=list_expiries()
    if not expiries:raise RuntimeError("NO_ELIGIBLE_EXPIRY_FILES_AT_PINNED_REVISION")
    COUNTS.update(index_rows=len(idx),expiry_files_metadata=len(expiries),vix_rows=len(vix))
    groups={d:g.copy() for d,g in idx.groupby(idx.timestamp.dt.date,sort=True) if DEV_START<=d<=VAL_END}
    rows=[];daily=[];skips=Counter()
    for n,d in enumerate(sorted(groups)):
      split=split_for_day(d);sig=opening_range_signal(groups[d]);vf=vix_filter_state(vix,d)
      dr={"date":d.isoformat(),"split":split,"signal":sig["status"],"arm_a_base_net":0.,"arm_a_stress_net":0.,
          "arm_b_base_net":0.,"arm_b_stress_net":0.,"arm_a_unknown":False,"arm_b_unknown":False,
          "vix_available":vf.get("available",False),"vix_skip":vf.get("skip",False)}
      if sig["status"] not in ("SIGNAL","NO_BREAKOUT"):
        skips[sig["status"]]+=1;dr["arm_a_unknown"]=dr["arm_b_unknown"]=True
        for k in ("arm_a_base_net","arm_a_stress_net","arm_b_base_net","arm_b_stress_net"):dr[k]=np.nan
        daily.append(dr);continue
      if sig["status"]=="NO_BREAKOUT":skips["NO_BREAKOUT"]+=1;daily.append(dr);continue
      st,entry=sig["signal_ts"],sig["signal_ts"]+pd.Timedelta(minutes=1);bskip=bool(vf.get("available") and vf.get("skip"))
      j=bisect_left(expiries,pd.Timestamp(d,tz=TZ))
      if j>=len(expiries) or expiries[j]>MAX_EXPIRY:
        status="NO_ALLOWED_EXPIRY_BEFORE_2026";skips[status]+=1
        rows.append({"date":d.isoformat(),"split":split,"signal_ts":str(st),"entry_ts":str(entry),"direction":sig["direction"],"status":status,"arm_b_filter_skip":bskip})
        if not bskip:
          dr["arm_a_unknown"]=dr["arm_b_unknown"]=True
          for k in ("arm_a_base_net","arm_a_stress_net","arm_b_base_net","arm_b_stress_net"):dr[k]=np.nan
        daily.append(dr);continue
      expiry=expiries[j]
      try:chain=load_chain_day(expiry,d)
      except Exception as e:
        chain=pd.DataFrame();ISSUES.append({"date":d.isoformat(),"expiry":str(expiry.date()),"stage":"load_chain","error":repr(e)})
      vert=select_vertical(chain,st,sig["signal_spot"],sig["direction"]) if not chain.empty else {"status":"NO_CHAIN_ROWS_FOR_SESSION"}
      if vert["status"]!="OK":
        status=vert["status"];skips[status]+=1
        rows.append({"date":d.isoformat(),"expiry":str(expiry.date()),"split":split,"signal_ts":str(st),"entry_ts":str(entry),
          "direction":sig["direction"],"status":status,"arm_b_filter_skip":bskip,"vix_prior_close":vf.get("prior_close"),"vix_threshold":vf.get("threshold")})
        if not bskip:
          dr["arm_a_unknown"]=dr["arm_b_unknown"]=True
          for k in ("arm_a_base_net","arm_a_stress_net","arm_b_base_net","arm_b_stress_net"):dr[k]=np.nan
        daily.append(dr);continue
      lot=lot_size_for_expiry(expiry);base=run_scenario(chain,d,entry,sig["direction"],vert,lot,1,10.,1.);stress=run_scenario(chain,d,entry,sig["direction"],vert,lot,2,20.,1.5)
      bok=base.get("status")=="COMPLETE";sok=stress.get("status")=="COMPLETE";status="COMPLETE" if bok else base.get("status","UNKNOWN");skips[status]+=1
      rec={"date":d.isoformat(),"expiry":str(expiry.date()),"split":split,"signal_ts":str(st),"entry_ts":str(entry),
        "direction":sig["direction"],"or_high":sig["or_high"],"or_low":sig["or_low"],"signal_spot":sig["signal_spot"],
        "arm_b_filter_skip":bskip,"vix_prior_close":vf.get("prior_close"),"vix_threshold":vf.get("threshold"),"vix_filter_available":vf.get("available"),
        "long_option_type":vert["option_type"],"long_strike":vert["long_strike"],"short_strike":vert["short_strike"],"strike_step":vert["step"],
        "lot_size":lot,"base_status":base.get("status"),"stress_status":stress.get("status"),"base_net":base.get("net"),"stress_net":stress.get("net"),
        "base_gross_after_slippage_before_fees":base.get("gross_after_slippage_before_fees"),"stress_gross_after_slippage_before_fees":stress.get("gross_after_slippage_before_fees"),
        "base_fees_total":base.get("fees",{}).get("total"),"stress_fees_total":stress.get("fees",{}).get("total"),
        "base_fee_components":json.dumps(base.get("fees",{}),sort_keys=True),"stress_fee_components":json.dumps(stress.get("fees",{}),sort_keys=True),
        "base_trigger":base.get("trigger"),"stress_trigger":stress.get("trigger"),"base_exit_ts":base.get("exit_ts"),"stress_exit_ts":stress.get("exit_ts"),
        "base_path_coverage":base.get("path_coverage"),"stress_path_coverage":stress.get("path_coverage"),
        "base_defined_max_loss_rupees":base.get("max_defined_loss_rupees"),"base_potential_max_profit_rupees":base.get("potential_max_profit_rupees"),
        "base_status":base.get("status"),"arm_a_taken":bok,"arm_b_taken":bok and not bskip,"status":status}
      rows.append(rec)
      if bok:
        dr["arm_a_base_net"]=float(base["net"]);dr["arm_a_stress_net"]=float(stress["net"]) if sok else np.nan
        if not sok:dr["arm_a_unknown"]=True
        if not bskip:
          dr["arm_b_base_net"]=float(base["net"]);dr["arm_b_stress_net"]=float(stress["net"]) if sok else np.nan
          if not sok:dr["arm_b_unknown"]=True
      elif not bskip:
        dr["arm_a_unknown"]=dr["arm_b_unknown"]=True
        for k in ("arm_a_base_net","arm_a_stress_net","arm_b_base_net","arm_b_stress_net"):dr[k]=np.nan
      daily.append(dr)
      if (n+1)%50==0:pd.DataFrame(rows).to_csv(OUT/"trade_ledger_progress.csv",index=False)
    tdf,pdf=pd.DataFrame(rows),pd.DataFrame(daily)
    tdf.to_csv(OUT/"trade_ledger.csv",index=False);pdf.to_csv(OUT/"daily_returns.csv",index=False)
    pd.DataFrame([{"reason":k,"count":int(v)} for k,v in sorted(skips.items())]).to_csv(OUT/"coverage_audit.csv",index=False)
    ss=pd.DataFrame([trade_summary(rows,a,s) for a in ("arm_a","arm_b") for s in ("development","validation")]);ss.to_csv(OUT/"summary.csv",index=False)
    monthly=pdf[pdf.split=="validation"].copy();monthly["month"]=monthly.date.str[:7]
    monthly.groupby("month",as_index=False)[["arm_a_base_net","arm_a_stress_net","arm_b_base_net","arm_b_stress_net"]].sum(min_count=1).to_csv(OUT/"monthly_stability.csv",index=False)
    val=pdf[pdf.split=="validation"].sort_values("date");h1=val.arm_a_base_net.to_numpy(float);h2=(val.arm_b_base_net-val.arm_a_base_net).to_numpy(float)
    u1=int((~np.isfinite(h1)).sum());u2=int((~np.isfinite(h2)).sum())
    an=int(ss[(ss.arm=="arm_a")&(ss.split=="validation")].completed_trades.iloc[0]);bn=int(ss[(ss.arm=="arm_b")&(ss.split=="validation")].completed_trades.iloc[0]);rng=np.random.default_rng(SEED)
    def test(x,unknown,n):
      if unknown:return {"status":"NOT_ESTIMABLE_UNKNOWN_SESSIONS","mean":None,"ci95":None,"p":None}
      if n<100:return {"status":"UNDERPOWERED_LT_100_TRADES","mean":float(np.mean(x)),"ci95":None,"p":None}
      return {"status":"ESTIMABLE","mean":float(np.mean(x)),"ci95":block_ci(x,rng),"p":signflip(x,rng)}
    h1s=test(h1,u1,an);h2s=test(h2,u2,min(an,bn));pa=holm([h1s["p"] if h1s["p"] is not None else np.nan,h2s["p"] if h2s["p"] is not None else np.nan])
    inf={"seed":SEED,"resamples":N_RESAMPLES,"block_length_sessions":BLOCK_LEN,"validation_sessions":len(val),"h1_unknown_sessions":u1,"h2_unknown_sessions":u2,
      "arm_a_completed_trades":an,"arm_b_completed_trades":bn,
      "H1_arm_A_positive_daily_net":{**h1s,"p_holm_adjusted":pa[0] if math.isfinite(pa[0]) else None},
      "H2_filter_paired_daily_uplift":{**h2s,"p_holm_adjusted":pa[1] if math.isfinite(pa[1]) else None}}
    (OUT/"inference.json").write_text(json.dumps(inf,indent=2,allow_nan=False))
    manifest={"dataset":HF_REPO,"revision":HF_REVISION,"dev_end":str(DEV_END),"validation_end":str(VAL_END),
      "option_expiry_files_loaded":sorted(EXPIRY_FILES_USED),"expiry_file_count_loaded":len(EXPIRY_FILES_USED),"source_schema_by_file":SOURCE_SCHEMA,"counts":dict(COUNTS),"holdout_loaded":False}
    (OUT/"source_manifest.json").write_text(json.dumps(manifest,indent=2))
    va=ss[(ss.arm=="arm_a")&(ss.split=="validation")].iloc[0];vb=ss[(ss.arm=="arm_b")&(ss.split=="validation")].iloc[0]
    h1pass=h1s["status"]=="ESTIMABLE" and pa[0] is not None and pa[0]<.05 and h1s["ci95"][0]>0 and va.base_net_pnl>0 and va.stress_net_pnl>=0
    h2pass=h2s["status"]=="ESTIMABLE" and pa[1] is not None and pa[1]<.05 and h2s["ci95"][0]>0
    decision={"computation_status":"PASS","primary_economic_status":"VALIDATION_PROMISING_REQUIRES_INDEPENDENT_CONFIRMATION" if h1pass and h2pass else "NO_PROMOTION",
      "arm_a_h1_pass":bool(h1pass),"arm_b_h2_pass":bool(h2pass),"arm_a_validation_base_net_pnl":float(va.base_net_pnl),"arm_a_validation_stress_net_pnl":float(va.stress_net_pnl),
      "arm_b_validation_base_net_pnl":float(vb.base_net_pnl),"arm_b_validation_stress_net_pnl":float(vb.stress_net_pnl),"phase98_live_or_paper_promotion":False,"holdout_loaded":False,
      "warning":"OHLC bar-open fills with fixed slippage are modeled references, not historical bid/ask/depth or live-fill proof."}
    (OUT/"decision.json").write_text(json.dumps(decision,indent=2,allow_nan=False))
    no26=not any(str(x).startswith("2026") for x in tdf.get("date",pd.Series(dtype=str)).tolist())
    checks={"all_loaded_expiry_content_at_or_before_2025_12_31":all(pd.Timestamp(re.search(r"(\d{4}-\d{2}-\d{2})\.parquet$",f).group(1),tz=TZ)<=MAX_EXPIRY for f in EXPIRY_FILES_USED),"no_2026_result_rows":no26,"protected_holdout_loaded":False}
    accepted_checks = (checks["all_loaded_expiry_content_at_or_before_2025_12_31"] and checks["no_2026_result_rows"] and checks["protected_holdout_loaded"] is False and len(ISSUES) == 0 and len(EXPIRY_FILES_USED) > 0)
    vr={"status":"PASS" if accepted_checks else "BLOCKED_SOURCE_OR_COVERAGE_ERRORS","index_rows":len(idx),"index_sessions":len(groups),"expiry_files_seen_through_2025":len(expiries),"expiry_files_used":len(EXPIRY_FILES_USED),"signal_rows":len(tdf),"source_issues":ISSUES,"skip_reason_counts":dict(skips),"checks":checks}
    (OUT/"validation_report.json").write_text(json.dumps(vr,indent=2,allow_nan=False))
    def money(x):return "NA" if pd.isna(x) else f"₹{x:,.2f}"
    report=["# Phase 98 — NIFTY Opening-Range Debit-Spread Results","",
      f"**Computation:** PASS. **Economic decision:** {decision['primary_economic_status']}. **Live/paper promotion:** NO.","",
      f"- Dataset revision: {HF_REVISION}",f"- Option expiry files loaded (expiry <= 2025-12-31): {len(EXPIRY_FILES_USED)}",
      f"- Validation sessions: {len(val)}; Arm A trades: {an}; Arm B trades: {bn}",
      f"- Arm A validation net P&L: base {money(va.base_net_pnl)}; severe stress {money(va.stress_net_pnl)}",
      f"- Arm B validation net P&L: base {money(vb.base_net_pnl)}; severe stress {money(vb.stress_net_pnl)}",
      f"- Unknown validation returns: H1={u1}; H2={u2}","","## Frozen strategy",
      "Arm A is the first observed close outside the 09:15–09:29 NIFTY range. Entry is the next minute's exact option open, using one-lot ATM long / two-strike-step OTM short debit vertical. Target/stop are evaluated on paired closes; fills are next-minute opens or the 15:15 time exit.",
      "Arm B is identical but skips signals only when prior-session India VIX exceeds the prior-only trailing 252-close 75th percentile.","","## Validation summary","",ss[ss.split=="validation"].to_markdown(index=False),"",
      "## Primary inference","",json.dumps(inf,indent=2),"","## Coverage reasons","",pd.DataFrame([{"reason":k,"count":int(v)} for k,v in sorted(skips.items())]).to_markdown(index=False),"",
      f"Source/schema issue events: {len(ISSUES)}.","","## Decision and limitations",
      "- Option OHLC bar opens plus fixed slippage are modeled references, not full historical bid/ask/depth, latency, or guaranteed fills.",
      "- Computation PASS is not proof of profitability. Unknown signal-session returns block an inferential claim.",
      "- The protected Phase 83 2026 holdout was not loaded; Phase 98 cannot promote live or paper trading.","",
      "## Reproducibility files","- summary.csv, coverage_audit.csv, trade_ledger.csv, daily_returns.csv, monthly_stability.csv",
      "- inference.json, decision.json, source_manifest.json, validation_report.json"]
    (OUT/"report.md").write_text("\n".join(report)+"\n")
    if ISSUES:(OUT/"source_issues.jsonl").write_text("".join(json.dumps(x,default=str)+"\n" for x in ISSUES))
    print(json.dumps({"status":vr["status"],"decision":decision,"counts":dict(COUNTS),"skip_reasons":dict(skips)},indent=2,default=str))
    if vr["status"] != "PASS":
      raise RuntimeError("Phase 98 evidence gate failed: " + vr["status"])
  except Exception as e:
    issue={"stage":"fatal","error":repr(e),"traceback":traceback.format_exc()}
    (OUT/"validation_report.json").write_text(json.dumps({"status":"BLOCKED_OR_FAILED","error":repr(e),"traceback":traceback.format_exc(),"protected_2026_holdout_loaded":False},indent=2))
    (OUT/"source_issues.jsonl").write_text(json.dumps(issue)+"\n")
    (OUT/"report.md").write_text(f"# Phase 98 — Runtime Feasibility Failure\n\nStatus: BLOCKED_OR_FAILED before accepted numerical conclusion.\n\nError: {type(e).__name__}: {e}\n\nNo partial output is accepted as performance evidence. The 2026 holdout was not loaded.\n")
    raise

if __name__=="__main__":main()
