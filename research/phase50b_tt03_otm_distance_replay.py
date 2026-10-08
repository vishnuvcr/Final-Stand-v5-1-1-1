import json, os, math
from pathlib import Path
import numpy as np
import pandas as pd
from phase43_vix_strategy_sweep import (
    TZ, START, END, DEV_END, VAL_END,
    load_parquet, load_vix, exec_px, charges, lot_size_for_expiry, vix_state
)

OUT=Path("results/phase50b/tt03_otm_distance") / ("d" + os.environ.get("TT03_DISTANCE","300"))
OUT.mkdir(parents=True,exist_ok=True)
TT03_ENGINE_REV="50B-TT03-WINDOW-V5"

def expiry_dates():
    p=Path("results/phase43_vix/strategy_trade_matrix_all_splits.csv")
    z=pd.read_csv(p,usecols=["expiry"])
    return sorted({pd.Timestamp(x).tz_localize(TZ) for x in z["expiry"].dropna()})

def option_clean(df):
    x=df.copy()
    x["timestamp"]=pd.to_datetime(x["timestamp"])
    if x["timestamp"].dt.tz is None:x["timestamp"]=x["timestamp"].dt.tz_localize(TZ)
    else:x["timestamp"]=x["timestamp"].dt.tz_convert(TZ)
    x["strike"]=pd.to_numeric(x["strike"],errors="coerce")
    x["close"]=pd.to_numeric(x["close"],errors="coerce")
    x["option_type"]=x["option_type"].astype(str).str.upper()
    return x.dropna(subset=["timestamp","strike","close"])

def q(z,opt,k):
    a=z[(z.option_type==opt)&(np.isclose(z.strike,float(k),rtol=0,atol=1e-8))]
    return None if a.empty else float(a.iloc[-1].close)

def entry_day(expiry,index):
    target=(expiry-pd.Timedelta(days=3)).normalize()
    if target.weekday()>=5:return None
    return target if not index[index.timestamp.dt.normalize()==target].empty else None

def trade_one(expiry,index,data,distance):
    day=entry_day(expiry,index)
    if day is None:return None
    # A source-defined 10:00-10:05 entry is only possible on a normal NSE
    # daytime session. A date with no 09:15-15:30 index observations is a
    # closed/non-standard-session day (e.g. Muhurat evening session), not a
    # missing data observation for this intraday strategy.
    day_regular=index[(index.timestamp.dt.normalize()==day)&
                      (index.timestamp.dt.time>=pd.Timestamp("09:15").time())&
                      (index.timestamp.dt.time<=pd.Timestamp("15:30").time())]
    if day_regular.empty:
        return {"_session_exclusion":{"expiry":str(expiry.date()),"entry_day":str(day.date()),
                                      "reason":"no_normal_09:15_to_15:30_session_on_scheduled_entry_day"}}
    ts_candidates=sorted(index[(index.timestamp.dt.normalize()==day)&
                              (index.timestamp>=day+pd.Timedelta(hours=10))&
                              (index.timestamp<day+pd.Timedelta(hours=10,minutes=6))].timestamp.unique())
    if len(ts_candidates)==0:
        return {"_coverage_gap":{"expiry":str(expiry.date()),"entry_ts":str(day),
                                 "gap_type":"missing_entry_observation_in_10:00_to_10:05_window"}}

    # Tradetron evaluates continuously inside the 10:00-10:05 entry window.
    # Use the earliest timestamp at which a complete source-defined ratio set exists.
    chosen=None
    for ts0 in ts_candidates:
        ts0=pd.Timestamp(ts0)
        ix=index[index.timestamp==ts0]
        if ix.empty:continue
        spot=float(ix.iloc[-1].spot)
        snap=data[data.timestamp==ts0]
        if snap.empty:continue
        atm=float(min(snap.strike.unique(),key=lambda k:abs(float(k)-spot)))
        call_legs=[("CE",atm+distance,+1),("CE",atm+distance+50.0,-1),("CE",atm+distance+100.0,-1)]
        put_legs=[("PE",atm-distance,+1),("PE",atm-distance-50.0,-1),("PE",atm-distance-100.0,-1)]
        if all(q(snap,o,k) is not None for o,k,_ in call_legs):
            chosen=(ts0,spot,atm,call_legs,"CALL_RATIO_BEARISH",snap)
            break
        if all(q(snap,o,k) is not None for o,k,_ in put_legs):
            chosen=(ts0,spot,atm,put_legs,"PUT_RATIO_BULLISH",snap)
            break
    if chosen is None:
        return {"_coverage_gap":{"expiry":str(expiry.date()),"entry_ts":str(day),
                                 "gap_type":"missing_complete_call_or_put_ratio_quotes_in_entry_window"}}

    ts,spot,atm,legs,direction,snap=chosen
    lot=lot_size_for_expiry(expiry)
    ledger=[]
    entry_px={(o,k):q(snap,o,k) for o,k,_ in legs}
    for o,k,qty in legs:
        px=entry_px[(o,k)]
        ledger.append({"ts":ts,"side":"buy" if qty>0 else "sell","price":px,"qty":qty,"lot":lot,"opt":o,"strike":k,"phase":"entry"})

    expday=expiry.normalize()
    day_data=data[(data.timestamp.dt.normalize()==expday)&
                  (data.timestamp.dt.time>=pd.Timestamp("13:30").time())&
                  (data.timestamp.dt.time<=pd.Timestamp("15:29").time())]
    idxday=index[(index.timestamp.dt.normalize()==expday)&
                 (index.timestamp.dt.time>=pd.Timestamp("13:30").time())&
                 (index.timestamp.dt.time<=pd.Timestamp("15:29").time())]
    if day_data.empty:
        return {"_coverage_gap":{"expiry":str(expiry.date()),"entry_ts":str(ts),"gap_type":"missing_expiry_day_exit_data"}}
    exit_ts=None
    exit_snap=None
    for t in sorted(set(idxday.timestamp).intersection(set(day_data.timestamp))):
        snap_t=day_data[day_data.timestamp==t]
        pnl=0.0
        for o,k,qty in legs:
            px=q(snap_t,o,k)
            if px is None:
                pnl=None;break
            pnl += qty*(px-entry_px[(o,k)])*lot
        if pnl is not None and pd.Timestamp(t).time()>=pd.Timestamp("13:30").time() and pnl<0:
            exit_ts=pd.Timestamp(t)
            exit_snap=snap_t
            break
    if exit_ts is None:
        # Source rule is "no later than 15:29". Therefore use the latest
        # simultaneously observed index/option timestamp at or BEFORE 15:29.
        # Never roll forward to 15:30+ and never require an exact 15:29 quote.
        hard_close=pd.Timestamp("15:29").time()
        common=sorted(set(idxday.timestamp).intersection(set(day_data.timestamp)))
        eligible=[pd.Timestamp(t) for t in common if pd.Timestamp(t).time()<=hard_close]
        exit_ts=None
        exit_snap=None
        # Search backward for the latest timestamp at or before 15:29 for which
        # every live leg has an observed quote. Do not stop at a timestamp that
        # has some-but-not-all legs; that would create an artificial coverage gap.
        for candidate in reversed(eligible):
            snap_candidate=day_data[day_data.timestamp==candidate]
            if all(q(snap_candidate,o,k) is not None for o,k,_ in legs):
                exit_ts=candidate
                exit_snap=snap_candidate
                break
        if exit_ts is None:
            return {"_coverage_gap":{"expiry":str(expiry.date()),"entry_ts":str(ts),
                                     "gap_type":"missing_complete_hard_close_quote_at_or_before_15:29"}}
    if exit_snap is None:
        exit_snap=day_data[day_data.timestamp==exit_ts]
    if exit_snap.empty:
        return {"_coverage_gap":{"expiry":str(expiry.date()),"entry_ts":str(ts),
                                 "exit_ts":str(exit_ts),"gap_type":"missing_exit_snapshot"}}
    for o,k,qty in legs:
        px=q(exit_snap,o,k)
        ledger.append({"ts":exit_ts,"side":"sell" if qty>0 else "buy","price":px,"qty":qty,"lot":lot,"opt":o,"strike":k,"phase":"exit"})
    gross=0.0; orders=[]
    for r in ledger:
        ep=exec_px(r["price"],r["side"])
        gross += (-1 if r["side"]=="buy" else 1)*ep*abs(r["qty"])*r["lot"]
        orders.append((pd.Timestamp(r["ts"]),r["side"],ep*abs(r["qty"])))
    cost=charges(orders,lot,1.0); cost50=charges(orders,lot,1.5)
    cost20=charges(orders,lot,1.0,brokerage_per_order=20.0); cost20_50=charges(orders,lot,1.5,brokerage_per_order=20.0)
    vs=vix_state(VIX,ts)
    return {
      "expiry":str(expiry.date()),"entry_ts":str(ts),"exit_ts":str(exit_ts),
      "year":ts.year,"spot":spot,"atm":atm,
      "net":gross-cost,"net50":gross-cost50,"net20":gross-cost20,"net20_50":gross-cost20_50,"gross":gross,"cost":cost,
      "vix":vs["vix"] if vs else np.nan,"vix_state":vs["level_state"] if vs else None,
      "direction":direction,
      "distance_points":DISTANCE,
      "win":int((gross-cost)>0)
    }

def main():
    global VIX
    DISTANCE=int(os.environ.get("TT03_DISTANCE","300"))
    index=load_parquet("index/NIFTY.parquet")
    index=index[["timestamp","close"]].rename(columns={"close":"spot"}).drop_duplicates("timestamp").sort_values("timestamp")
    VIX=load_vix()
    exps=[e for e in expiry_dates() if START<=e<=END]
    rows=[];errors=[];coverage_gaps=[];session_exclusions=[]
    for e in exps:
        try:
            data=option_clean(load_parquet(f"options/NIFTY/{e.strftime('%Y-%m-%d')}.parquet"))
            z=trade_one(e,index,data,DISTANCE)
            if isinstance(z,dict) and "_coverage_gap" in z:
                coverage_gaps.append(z["_coverage_gap"])
            elif isinstance(z,dict) and "_session_exclusion" in z:
                session_exclusions.append(z["_session_exclusion"])
            elif z is not None:
                rows.append(z)
        except Exception as ex:
            errors.append({"expiry":str(e.date()),"error":repr(ex)})
    df=pd.DataFrame(rows)
    df.to_csv(OUT/"tt03_trades.csv",index=False)
    pd.DataFrame(errors,columns=["expiry","error"]).to_csv(OUT/"data_errors.csv",index=False)
    pd.DataFrame(coverage_gaps).to_csv(OUT/"coverage_gaps.csv",index=False)
    pd.DataFrame(session_exclusions).to_csv(OUT/"session_exclusions.csv",index=False)
    if not df.empty:
        splits=[]
        expiry_series=pd.to_datetime(df["expiry"],utc=True).dt.tz_convert(TZ)
        for n,m in [("DEV",expiry_series<=DEV_END),("VAL",(expiry_series>DEV_END)&(expiry_series<=VAL_END)),("HOLD",expiry_series>VAL_END)]:
            z=df[m]
            splits.append({"split":n,"trades":len(z),"net":float(z.net.sum()),"net50":float(z.net50.sum()),"win_rate":float(z.win.mean()) if len(z) else 0})
        pd.DataFrame(splits).to_csv(OUT/"split_summary.csv",index=False)
        vx=df.groupby("vix_state").agg(trades=("net","size"),net=("net","sum"),net50=("net50","sum"),mean=("net","mean"),win_rate=("win","mean")).reset_index()
        vx.to_csv(OUT/"vix_summary.csv",index=False)
        result={"strategy":"TT-03","engine_revision":TT03_ENGINE_REV,"trades":len(df),"candidate_trades":len(df)+len(coverage_gaps),"coverage_exclusions":len(coverage_gaps),"coverage_rate":len(df)/(len(df)+len(coverage_gaps)) if len(df)+len(coverage_gaps) else 0.0,
                "session_exclusions":len(session_exclusions),"net":float(df.net.sum()),"net50":float(df.net50.sum()),"net20":float(df.net20.sum()),"net20_50":float(df.net20_50.sum()),"by_vix":vx.to_dict("records")}
    else: result={"strategy":"TT-03","engine_revision":TT03_ENGINE_REV,"trades":0,"candidate_trades":len(coverage_gaps),"coverage_exclusions":len(coverage_gaps),"coverage_rate":0.0,"net":0.0,"net50":0.0,"net20":0.0,"net20_50":0.0,"by_vix":[]}
    (OUT/"summary.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()

# F50B-010 fixed before numerical execution: emulate both symmetric sets, call-set priority as listed in Tradetron, with put-set fallback only when call-set quotes are unavailable.
# F50B-026: evaluate the full 10:00-10:05 entry window and select the earliest feasible complete ratio set.
# F50B-063 correction: expiry-day hard close uses the latest observed common quote at or before 15:29; no forward-to-15:30 is permitted.
# F50B-064 correction: modal strike-step availability is not a source condition; removed the unnecessary step gate.
# F50B-065 correction: every eligible expiry campaign with a valid entry day but no complete entry set is retained as an explicit coverage exclusion.

# F50B-033: TT03 opened positions cannot silently disappear; incomplete exits are explicit coverage exclusions.

# 50B-4 preregistration: finite TT-03 natural strike-distance variants 200/300/400/500/600.
