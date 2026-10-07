import json
from pathlib import Path
import numpy as np
import pandas as pd

from phase43_vix_strategy_sweep import (
    TZ, START, END, DEV_END, VAL_END,
    load_parquet, load_vix, vix_state, exec_px, charges, lot_size_for_expiry
)

TT06_ENGINE_REV = "50B-TT06-COVERAGE-V2"
OUT = Path("results/phase50b/tt06_intraday_asym_replay")
OUT.mkdir(parents=True, exist_ok=True)

ENTRY_START = pd.Timestamp("09:30").time()
ENTRY_END = pd.Timestamp("15:10").time()
EXIT_TIME = pd.Timestamp("15:15").time()
STOP = -4000.0

def clean(x):
    z=x.copy()
    z["timestamp"]=pd.to_datetime(z["timestamp"])
    if z["timestamp"].dt.tz is None:
        z["timestamp"]=z["timestamp"].dt.tz_localize(TZ)
    else:
        z["timestamp"]=z["timestamp"].dt.tz_convert(TZ)
    z["strike"]=pd.to_numeric(z["strike"],errors="coerce")
    z["close"]=pd.to_numeric(z["close"],errors="coerce")
    z["option_type"]=z["option_type"].astype(str).str.upper()
    return z.dropna(subset=["timestamp","strike","close"]).sort_values(["timestamp","option_type","strike"])

def quote(frame,opt,strike):
    if frame is None or frame.empty or strike is None:
        return None
    q=frame[(frame.option_type==opt)&np.isclose(frame.strike,float(strike),rtol=0,atol=1e-8)]
    return None if q.empty else float(q.iloc[-1].close)

def expiries():
    z=pd.read_csv("results/phase43_vix/strategy_trade_matrix_all_splits.csv",usecols=["expiry"])
    return sorted({pd.Timestamp(x).tz_localize(TZ) for x in z["expiry"].dropna()})

def current_expiry(exps,day):
    d=pd.Timestamp(day).normalize()
    for e in exps:
        if e.normalize()>=d:
            return e
    return None

def next_expiry(exps,cur):
    for e in exps:
        if e>cur:
            return e
    return None

def nearest_atm(frame,spot):
    if frame is None or frame.empty:
        return None
    strikes=np.asarray(sorted(set(pd.to_numeric(frame.strike,errors="coerce").dropna().astype(float))),dtype=float)
    return float(strikes[np.argmin(np.abs(strikes-spot))]) if len(strikes) else None

def exact_premium_match(frame,opt,target,spot):
    if frame is None or frame.empty or target is None or not np.isfinite(target):
        return None
    q=frame[(frame.option_type==opt)&np.isfinite(frame.close)&(np.abs(frame.close-float(target))<=1e-12)].copy()
    if q.empty:
        return None
    q["dist"]=(q.strike.astype(float)-float(spot)).abs()
    q=q.sort_values(["dist","strike"],kind="mergesort")
    return float(q.iloc[0].strike)

def mark_pnl(pos,cur_frame,nxt_frame):
    ce=pos["legs"]["ce"]; pe=pos["legs"]["pe"]
    cframe=cur_frame if ce["exp"]=="cur" else nxt_frame
    pframe=cur_frame if pe["exp"]=="cur" else nxt_frame
    cpx=quote(cframe,"CE",ce["strike"])
    ppx=quote(pframe,"PE",pe["strike"])
    if cpx is None or ppx is None:
        return None
    return pos["cash"] + ce["qty"]*cpx*pos["lot"] + pe["qty"]*ppx*pos["lot"]

def execute_close_open(pos,name,ts,spot,target_frame,target_exp,opt,target_strike):
    old=pos["legs"][name]
    old_frame=pos["cur_frame"] if old["exp"]=="cur" else pos["nxt_frame"]
    old_px=quote(old_frame,old["opt"],old["strike"])
    new_px=quote(target_frame,opt,target_strike)
    if old_px is None or new_px is None:
        return False
    close_side="buy" if old["qty"]<0 else "sell"
    open_side="sell" if old["qty"]<0 else "buy"
    close_ep=exec_px(old_px,close_side)
    open_ep=exec_px(new_px,open_side)
    pos["cash"] += (-close_ep if close_side=="buy" else close_ep)*abs(old["qty"])*pos["lot"]
    pos["cash"] += (open_ep if open_side=="sell" else -open_ep)*abs(old["qty"])*pos["lot"]
    pos["orders"].append((pd.Timestamp(ts),close_side,close_ep*abs(old["qty"])))
    pos["orders"].append((pd.Timestamp(ts),open_side,open_ep*abs(old["qty"])))
    pos["legs"][name]={"opt":opt,"strike":float(target_strike),"qty":old["qty"],"exp":"cur" if target_exp==pos["cur"] else "nxt"}
    return True

def finish(pos,ts,cur_frame,nxt_frame):
    rows=(
        ("ce",pos["legs"]["ce"],cur_frame if pos["legs"]["ce"]["exp"]=="cur" else nxt_frame),
        ("pe",pos["legs"]["pe"],cur_frame if pos["legs"]["pe"]["exp"]=="cur" else nxt_frame),
    )
    gross=pos["cash"]
    orders=list(pos["orders"])
    for _,leg,frame in rows:
        px=quote(frame,leg["opt"],leg["strike"])
        if px is None:
            return None,{"trade_id":pos["trade_id"],"expiry":str(pos["cur"].date()),
                          "trigger_ts":str(ts),"gap_type":"missing_exit_leg_quote"}
        side="sell" if leg["qty"]>0 else "buy"
        ep=exec_px(px,side)
        gross += ep*abs(leg["qty"])*pos["lot"] if side=="sell" else -ep*abs(leg["qty"])*pos["lot"]
        orders.append((pd.Timestamp(ts),side,ep*abs(leg["qty"])))
    cost=charges(orders,pos["lot"],1.0)
    cost50=charges(orders,pos["lot"],1.5)
    cost20=charges(orders,pos["lot"],1.0,brokerage_per_order=20.0)
    cost20_50=charges(orders,pos["lot"],1.5,brokerage_per_order=20.0)
    return {
        "trade_id":pos["trade_id"],"entry_ts":str(pos["entry_ts"]),"exit_ts":str(ts),
        "expiry":str(pos["cur"].date()),"entry_spot":pos["entry_spot"],"lot":pos["lot"],
        "gross":gross,"cost":cost,"net":gross-cost,"net50":gross-cost50,
        "net20":gross-cost20,"net20_50":gross-cost20_50,
        "vix":pos["vix"],"vix_state":pos["vix_state"],
        "repairs_ce":pos["repairs_ce"],"repairs_pe":pos["repairs_pe"]
    },None

def main():
    idx=load_parquet("index/NIFTY.parquet")
    idx=idx[["timestamp","close"]].rename(columns={"close":"spot"}).drop_duplicates("timestamp").sort_values("timestamp")
    vix=load_vix()
    E=expiries()
    cache={}
    rows=[]; gaps=[]; errors=[]; session_exclusions=[]
    trade_id=1

    days=sorted(idx.timestamp.dt.normalize().unique())
    for day0 in days:
        day=pd.Timestamp(day0)
        if day<START.normalize() or day>END.normalize() or day.weekday()==0:
            continue
        cur=current_expiry(E,day)
        nxt=next_expiry(E,cur) if cur is not None else None
        if cur is None or nxt is None:
            continue
        regular=idx[(idx.timestamp.dt.normalize()==day)&
                    (idx.timestamp.dt.time>=pd.Timestamp("09:15").time())&
                    (idx.timestamp.dt.time<=pd.Timestamp("15:30").time())]
        if regular.empty:
            session_exclusions.append({"date":str(day.date()),
                                       "reason":"no_normal_09:15_to_15:30_session"})
            continue
        for e in {cur,nxt}:
            if e not in cache:
                try: cache[e]=clean(load_parquet(f"options/NIFTY/{e.strftime('%Y-%m-%d')}.parquet"))
                except Exception as exc:
                    errors.append({"day":str(day.date()),"error":f"load {e.date()}: {exc}"})
                    cache[e]=pd.DataFrame(columns=["timestamp","strike","close","option_type"])
        cf=cache[cur]; nf=cache[nxt]
        dayidx=idx[(idx.timestamp.dt.normalize()==day)&(idx.timestamp.dt.time>=ENTRY_START)&(idx.timestamp.dt.time<=EXIT_TIME)]
        pos=None
        for ts0 in dayidx.timestamp.tolist():
            ts=pd.Timestamp(ts0)
            spot=float(idx.loc[idx.timestamp==ts].iloc[-1].spot)
            cs=cf[cf.timestamp==ts]
            ns=nf[nf.timestamp==ts]
            if pos is None and ts.time()<=ENTRY_END and not cs.empty and not ns.empty:
                ca=nearest_atm(cs,spot)
                na=nearest_atm(ns,spot)
                ce=quote(cs,"CE",ca)
                pe=quote(ns,"PE",na)
                if ca is not None and na is not None and ce is not None and pe is not None:
                    lot=lot_size_for_expiry(cur)
                    orders=[]
                    cash=0.0
                    for opt,px in [("CE",ce),("PE",pe)]:
                        ep=exec_px(px,"sell")
                        cash += ep*lot
                        orders.append((ts,"sell",ep))
                    vs=vix_state(vix,ts)
                    pos={"trade_id":trade_id,"entry_ts":ts,"entry_spot":spot,"cur":cur,"nxt":nxt,
                         "cur_frame":cf,"nxt_frame":nf,"lot":lot,"cash":cash,"orders":orders,
                         "legs":{"ce":{"opt":"CE","strike":ca,"qty":-1,"exp":"cur"},
                                 "pe":{"opt":"PE","strike":na,"qty":-1,"exp":"nxt"}},
                         "repairs_ce":0,"repairs_pe":0,
                         "vix":vs["vix"] if vs else np.nan,
                         "vix_state":vs["level_state"] if vs else None}
                    trade_id += 1

            if pos is None:
                continue

            pos["cur_frame"]=cf; pos["nxt_frame"]=nf
            pnl=mark_pnl(pos,cf,nf)
            if pnl is None:
                continue

            # CE repair: current-week CE <= 50% next-week PE.
            ce_leg=pos["legs"]["ce"]; pe_leg=pos["legs"]["pe"]
            ce_px=quote(cf,"CE",ce_leg["strike"] if ce_leg["exp"]=="cur" else None)
            pe_px=quote(nf,"PE",pe_leg["strike"] if pe_leg["exp"]=="nxt" else None)
            if ce_px is not None and pe_px is not None and ce_px <= 0.5*pe_px:
                strike=exact_premium_match(cs,"CE",pe_px,spot)
                if strike is not None and execute_close_open(pos,"ce",ts,spot,cs,cur,"CE",strike):
                    pos["repairs_ce"]+=1

            # PE repair: next-week PE <= 50% current-week CE.
            ce_px=quote(cf,"CE",pos["legs"]["ce"]["strike"]) if pos["legs"]["ce"]["exp"]=="cur" else None
            pe_px=quote(nf,"PE",pos["legs"]["pe"]["strike"]) if pos["legs"]["pe"]["exp"]=="nxt" else None
            if ce_px is not None and pe_px is not None and pe_px <= 0.5*ce_px:
                strike=exact_premium_match(ns,"PE",ce_px,spot)
                if strike is not None and execute_close_open(pos,"pe",ts,spot,ns,nxt,"PE",strike):
                    pos["repairs_pe"]+=1

            pnl=mark_pnl(pos,cf,nf)
            if pnl is None:
                continue
            if pnl<=STOP:
                out,gap=finish(pos,ts,cf,nf)
                if out is not None: rows.append(out)
                else: gaps.append(gap)
                pos=None
                break
            if ts.time()>=EXIT_TIME:
                # Use earliest common observed timestamp at/after 15:15.
                # Use the earliest common observed option timestamp at/after 15:15.
                cur_ts=set(cf.loc[cf["timestamp"]>=ts,"timestamp"].tolist())
                nxt_ts=set(nf.loc[nf["timestamp"]>=ts,"timestamp"].tolist())
                candidates=sorted(cur_ts & nxt_ts)
                exit_done=False
                for exitt in candidates:
                    cfs=cf[cf["timestamp"]==exitt]
                    nfs=nf[nf["timestamp"]==exitt]
                    ce_frame=cfs if pos["legs"]["ce"]["exp"]=="cur" else nfs
                    pe_frame=cfs if pos["legs"]["pe"]["exp"]=="cur" else nfs
                    ok=(quote(ce_frame,"CE",pos["legs"]["ce"]["strike"]) is not None and
                        quote(pe_frame,"PE",pos["legs"]["pe"]["strike"]) is not None)
                    if ok:
                        out,gap=finish(pos,pd.Timestamp(exitt),cfs,nfs)
                        if out is not None:
                            rows.append(out)
                        else:
                            gaps.append(gap)
                        pos=None
                        exit_done=True
                        break
                if exit_done:
                    break
        if pos is not None:
            gaps.append({"trade_id":pos["trade_id"],"expiry":str(pos["cur"].date()),
                         "trigger_ts":str(pos["entry_ts"]),"gap_type":"open_position_without_complete_exit"})
        if pos is None:
            entered_candidates=idx[(idx.timestamp.dt.normalize()==day)&
                                   (idx.timestamp.dt.time>=ENTRY_START)&
                                   (idx.timestamp.dt.time<=ENTRY_END)]
            if not any((not cf[cf.timestamp==pd.Timestamp(ts)].empty and not nf[nf.timestamp==pd.Timestamp(ts)].empty and
                        nearest_atm(cf[cf.timestamp==pd.Timestamp(ts)],float(idx.loc[idx.timestamp==pd.Timestamp(ts)].iloc[-1].spot)) is not None and
                        nearest_atm(nf[nf.timestamp==pd.Timestamp(ts)],float(idx.loc[idx.timestamp==pd.Timestamp(ts)].iloc[-1].spot)) is not None)
                       for ts in entered_candidates.timestamp.tolist()):
                gaps.append({"trade_id":trade_id,"expiry":str(cur.date()),
                             "trigger_ts":str(day),"gap_type":"missing_complete_entry_at_09:30_to_15:10"})
                trade_id += 1

    df=pd.DataFrame(rows)
    df.to_csv(OUT/"tt06_trades.csv",index=False)
    pd.DataFrame(gaps,columns=["trade_id","expiry","trigger_ts","gap_type"]).to_csv(OUT/"coverage_gaps.csv",index=False)
    pd.DataFrame(errors,columns=["day","error"]).to_csv(OUT/"data_errors.csv",index=False)
    pd.DataFrame(session_exclusions,columns=["date","reason"]).to_csv(OUT/"session_exclusions.csv",index=False)
    cand=len(rows)+len(gaps); cov=len(rows)/cand if cand else 0.0
    splits=[]
    if not df.empty:
        d=pd.to_datetime(df.expiry)
        for n,m in [("DEV",d<=DEV_END),("VAL",(d>DEV_END)&(d<=VAL_END)),("HOLD",d>VAL_END)]:
            qv=df[m]
            splits.append({"split":n,"trades":len(qv),"net":float(qv.net.sum()) if len(qv) else 0.0,
                           "net50":float(qv.net50.sum()) if len(qv) else 0.0,
                           "net20":float(qv.net20.sum()) if len(qv) else 0.0,
                           "net20_50":float(qv.net20_50.sum()) if len(qv) else 0.0})
    summary={"strategy":"TT-06","engine_revision":TT06_ENGINE_REV,"trades":len(df),"candidate_trades":cand,
             "coverage_exclusions":len(gaps),"coverage_rate":cov,"session_exclusions":len(session_exclusions),
             "net":float(df.net.sum()) if not df.empty else 0.0,
             "net50":float(df.net50.sum()) if not df.empty else 0.0,
             "net20":float(df.net20.sum()) if not df.empty else 0.0,
             "net20_50":float(df.net20_50.sum()) if not df.empty else 0.0,
             "splits":splits}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
