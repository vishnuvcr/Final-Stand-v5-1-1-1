import json
from pathlib import Path
import numpy as np
import pandas as pd
from phase43_vix_strategy_sweep import (
    TZ, START, END, DEV_END, VAL_END,
    load_parquet, load_vix, vix_state, exec_px, charges, lot_size_for_expiry
)

TT04_ENGINE_REV = "50B-TT04-COVERAGE-V3"
OUT = Path("results/phase50b/tt04_premium_match_replay")
OUT.mkdir(parents=True, exist_ok=True)
ENTRY_START = pd.Timestamp("10:00").time()
ENTRY_END = pd.Timestamp("10:05").time()
EXIT_TIME = pd.Timestamp("15:15").time()
STOP_RUPEES = -7000.0

def option_clean(df):
    x=df.copy()
    x["timestamp"]=pd.to_datetime(x["timestamp"])
    if x["timestamp"].dt.tz is None: x["timestamp"]=x["timestamp"].dt.tz_localize(TZ)
    else: x["timestamp"]=x["timestamp"].dt.tz_convert(TZ)
    x["strike"]=pd.to_numeric(x["strike"],errors="coerce")
    x["close"]=pd.to_numeric(x["close"],errors="coerce")
    x["option_type"]=x["option_type"].astype(str).str.upper()
    return x.dropna(subset=["timestamp","strike","close"]).sort_values(["timestamp","option_type","strike"])

def q(z,opt,k):
    a=z[(z.option_type==opt)&(np.isclose(z.strike,float(k),rtol=0,atol=1e-8))]
    return None if a.empty else float(a.iloc[-1].close)

def exact_ltp_strike(z,opt,target,spot):
    if z is None or z.empty or target is None or not np.isfinite(float(target)):
        return None
    a=z[(z.option_type==opt)&np.isfinite(z.close)&(np.abs(z.close.astype(float)-float(target))<=1e-12)][["strike","close"]].drop_duplicates("strike")
    if a.empty:
        return None
    a=a.assign(dist=(a.strike.astype(float)-float(spot)).abs())
    a=a.sort_values(["dist","strike"],kind="stable")
    return float(a.iloc[0].strike)

def expiry_list():
    p=Path("results/phase43_vix/strategy_trade_matrix_all_splits.csv")
    z=pd.read_csv(p,usecols=["expiry"])
    return sorted({pd.Timestamp(x).tz_localize(TZ) for x in z["expiry"].dropna()})

def current_expiry(exps,day):
    d=pd.Timestamp(day).normalize()
    for e in exps:
        if e.normalize()>=d:return e
    return None

def next_expiry(exps,cur):
    for e in exps:
        if e>cur:return e
    return None

def index_data():
    x=load_parquet("index/NIFTY.parquet")
    return x[["timestamp","close"]].rename(columns={"close":"spot"}).drop_duplicates("timestamp").sort_values("timestamp")

def mark_pnl(pos,ts,z):
    # P&L = executed cashflow + current marked value of open positions.
    cash=pos["cash"]
    for name,leg in pos["legs"].items():
        px=q(z,leg["opt"],leg["strike"])
        if px is None:return None
        cash += leg["qty"]*float(px)*pos["lot"]
    return cash

def order_ledger(pos,ts,side,px,qty,opt,leg,phase):
    pos["orders"].append({"ts":str(ts),"side":side,"price":float(px),"qty":int(qty),"lot":int(pos["lot"]),"opt":opt,"strike":float(leg),"phase":phase})

def execute_close(pos,ts,name,px,phase):
    leg=pos["legs"][name]
    side="buy" if leg["qty"]<0 else "sell"
    ep=exec_px(px,side)
    pos["cash"] -= ep*abs(leg["qty"])*pos["lot"] if side=="buy" else -ep*abs(leg["qty"])*pos["lot"]
    order_ledger(pos,ts,side,ep,leg["qty"],leg["opt"],leg["strike"],phase)
    return ep

def execute_open(pos,ts,side,opt,strike,px,qty,phase):
    ep=exec_px(px,side)
    leg={"opt":opt,"strike":float(strike),"qty":int(qty),"avg_entry":float(ep)}
    pos["legs"][phase.split("_")[0]]=leg
    order_ledger(pos,ts,side,ep,leg["strike"],leg["opt"],leg["strike"],phase)

def close_and_replace(pos,ts,name,z,opt,target,phase_prefix):
    old=pos["legs"][name]
    old_px=q(z,old["opt"],old["strike"])
    if old_px is None:return False
    new_strike=exact_ltp_strike(z,opt,target,pos["entry_spot"])
    if new_strike is None:return False
    new_px=q(z,opt,new_strike)
    if new_px is None:return False
    execute_close(pos,ts,name,old_px,phase_prefix+"_close")
    side="sell" if old["qty"]<0 else "buy"
    ep=exec_px(new_px,side)
    if side=="buy": pos["cash"] -= ep*abs(old["qty"])*pos["lot"]
    else: pos["cash"] += ep*abs(old["qty"])*pos["lot"]
    pos["legs"][name]={"opt":opt,"strike":float(new_strike),"qty":int(old["qty"]),"avg_entry":float(ep)}
    order_ledger(pos,ts,side,ep,old["qty"],opt,new_strike,phase_prefix+"_open")
    return True

def finish(pos,ts,z):
    for name,leg in pos["legs"].items():
        px=q(z,leg["opt"],leg["strike"])
        if px is None:
            pos["_coverage_gap"]={
                "trade_id":pos["trade_id"],"expiry":str(pos["expiry"].date()),
                "trigger_ts":str(ts),"gap_type":"missing_exit_leg_quote"
            }
            return None
        side="sell" if leg["qty"]>0 else "buy"
        ep=exec_px(px,side)
        pos["cash"] += ep*abs(leg["qty"])*pos["lot"] if side=="sell" else -ep*abs(leg["qty"])*pos["lot"]
        order_ledger(pos,ts,side,ep,leg["qty"],leg["opt"],leg["strike"],"exit")
    orders=[(pd.Timestamp(o["ts"]),o["side"],o["price"]*abs(o["qty"])) for o in pos["orders"]]
    gross=pos["cash"]
    cost=charges(orders,pos["lot"],1.0)
    cost50=charges(orders,pos["lot"],1.5)
    cost20=charges(orders,pos["lot"],1.0,brokerage_per_order=20.0)
    cost20_50=charges(orders,pos["lot"],1.5,brokerage_per_order=20.0)
    return {"expiry":str(pos["expiry"].date()),"entry_ts":pos["entry_ts"],"exit_ts":str(ts),"entry_spot":pos["entry_spot"],"lot":pos["lot"],"gross":float(gross),"cost":float(cost),"net":float(gross-cost),"net50":float(gross-cost50),"net20":float(gross-cost20),"net20_50":float(gross-cost20_50),"repairs_ce":pos["repairs_ce"],"repairs_pe":pos["repairs_pe"],"vix":pos["vix"],"vix_state":pos["vix_state"]}

def main():
    idx=index_data()
    exps=expiry_list()
    vix=load_vix()
    days=sorted(idx.timestamp.dt.normalize().unique())
    option_cache={}
    rows=[];errors=[];coverage_gaps=[];session_exclusions=[];trade_id=1;position=None
    for day in days:
        day=pd.Timestamp(day)
        if day<START.normalize() or day>END.normalize():continue
        cur=current_expiry(exps,day)
        if cur is None:continue
        next_exp=next_expiry(exps,cur)
        target=next_exp if day.normalize()==cur.normalize() else cur
        if target is None:continue

        regular=index_data_for_day=idx[(idx.timestamp.dt.normalize()==day.normalize())&
                                      (idx.timestamp.dt.time>=pd.Timestamp("09:15").time())&
                                      (idx.timestamp.dt.time<=pd.Timestamp("15:30").time())]
        if regular.empty:
            session_exclusions.append({"date":str(day.date()),
                                       "reason":"no_normal_09:15_to_15:30_session"})
            continue

        try:
            if target not in option_cache:
                option_cache[target]=option_clean(load_parquet(f"options/NIFTY/{target.strftime('%Y-%m-%d')}.parquet"))
            z_entry=option_cache[target]
            # Existing positions retain the expiry chosen at their original entry.
            # On the current expiry day, NEW entries use next-week quotes, but an
            # existing current-week position must be marked/exited against its own
            # current-week option series.
            day_rows=idx[(idx.timestamp.dt.normalize()==day.normalize())&(idx.timestamp.dt.time>=ENTRY_START)&(idx.timestamp.dt.time<=EXIT_TIME)]
            entered_today=False
            for ts in day_rows.timestamp.tolist():
                ts=pd.Timestamp(ts)
                ix=idx[idx.timestamp==ts]
                if ix.empty:continue
                spot=float(ix.iloc[-1].spot)
                if position is None:
                    z=z_entry[z_entry.timestamp==ts]
                else:
                    pos_exp=position["expiry"]
                    if pos_exp not in option_cache:
                        option_cache[pos_exp]=option_clean(load_parquet(f"options/NIFTY/{pos_exp.strftime('%Y-%m-%d')}.parquet"))
                    z=option_cache[pos_exp]
                    z=z[z.timestamp==ts]
                if z.empty:continue
                if position is None and ts.time()<=ENTRY_END:
                    atm=float(z_entry[z_entry.timestamp==ts].iloc[(z_entry[z_entry.timestamp==ts].strike.astype(float)-spot).abs().argsort().iloc[0]].strike)
                    ce=q(z,"CE",atm); pe=q(z,"PE",atm)
                    if ce is None or pe is None:continue
                    vs=vix_state(vix,ts)
                    position={"trade_id":trade_id,"expiry":target,"entry_ts":str(ts),"entry_spot":spot,"lot":lot_size_for_expiry(target),"cash":0.0,"repairs_ce":0,"repairs_pe":0,"vix":vs["vix"] if vs else np.nan,"vix_state":vs["level_state"] if vs else None,"orders":[],"legs":{}}
                    for name,opt,px in [("ce","CE",ce),("pe","PE",pe)]:
                        ep=exec_px(px,"sell")
                        position["legs"][name]={"opt":opt,"strike":atm,"qty":-1,"avg_entry":ep}
                        position["cash"] += ep*position["lot"]
                        order_ledger(position,ts,"sell",ep,-1,opt,atm,"entry")
                    entered_today=True
                    trade_id+=1
                if position is None:continue
                # Source repair triggers use ORIGINAL ENTRY premiums and raw LTPs.
                entry_ce=next(o["price"] for o in position["orders"] if o["phase"]=="entry" and o["opt"]=="CE")
                entry_pe=next(o["price"] for o in position["orders"] if o["phase"]=="entry" and o["opt"]=="PE")
                # Recover the source-side trigger values by undoing execution slippage.
                entry_ce_raw=entry_ce+0.05; entry_pe_raw=entry_pe+0.05
                # The repair condition compares the original entry premiums, as in the source.
                if position["repairs_ce"]==0 and entry_pe_raw-entry_ce_raw>=100:
                    if close_and_replace(position,ts,"ce",z,"CE",entry_pe_raw,"ce_repair"):
                        position["repairs_ce"]=1
                if position["repairs_pe"]==0 and entry_ce_raw-entry_pe_raw>=100:
                    if close_and_replace(position,ts,"pe",z,"PE",entry_ce_raw,"pe_repair"):
                        position["repairs_pe"]=1
                # Stop uses source-rule P&L at observed prices; exit fill receives adverse slippage.
                raw_pnl=mark_pnl(position,ts,z)
                if raw_pnl is not None and raw_pnl<=STOP_RUPEES:
                    out=finish(position,ts,z)
                    if out:rows.append(out)
                    else:coverage_gaps.append(position.get("_coverage_gap",{"trade_id":position["trade_id"],"expiry":str(position["expiry"].date()),"trigger_ts":str(ts),"gap_type":"missing_exit_leg_quote"}))
                    position=None
                    continue
                if ts.time()>=EXIT_TIME:
                    # Source rule is exit at/after 15:15. Search the same day's
                    # observed timestamps for the earliest complete exit rather
                    # than requiring the first timestamp after 15:15 to contain
                    # every leg.
                    exit_candidates=idx[(idx.timestamp.dt.normalize()==day.normalize())&(idx.timestamp.dt.time>=EXIT_TIME)&(idx.timestamp.dt.time<=pd.Timestamp("15:30").time())]["timestamp"].tolist()
                    exited=False
                    for exit_ts in exit_candidates:
                        exit_ts=pd.Timestamp(exit_ts)
                        z_exit=option_cache[position["expiry"]]
                        z_exit=z_exit[z_exit.timestamp==exit_ts]
                        out=finish(position,exit_ts,z_exit) if not z_exit.empty else None
                        if out is not None:
                            rows.append(out)
                            exited=True
                            break
                    if not exited:
                        coverage_gaps.append({"trade_id":position["trade_id"],"expiry":str(position["expiry"].date()),"trigger_ts":str(position["entry_ts"]),"gap_type":"no_complete_exit_quote_at_or_after_15:15"})
                    position=None
                    break
            if not entered_today and position is None:
                coverage_gaps.append({"trade_id":trade_id,"expiry":str(target.date()),
                                      "trigger_ts":str(day),"gap_type":"missing_complete_entry_at_10:00_to_10:05"})
                trade_id+=1
        except Exception as e:
            errors.append({"day":str(day.date()),"error":repr(e)})
            if position is None:
                coverage_gaps.append({"trade_id":trade_id,"expiry":str(target.date()),
                                      "trigger_ts":str(day),"gap_type":"entry_or_replay_exception"})
                trade_id+=1
    df=pd.DataFrame(rows)
    df.to_csv(OUT/"tt04_trades.csv",index=False)
    pd.DataFrame(errors,columns=["day","error"]).to_csv(OUT/"data_errors.csv",index=False)
    pd.DataFrame(coverage_gaps,columns=["trade_id","expiry","trigger_ts","gap_type"]).to_csv(OUT/"coverage_gaps.csv",index=False)
    pd.DataFrame(session_exclusions,columns=["date","reason"]).to_csv(OUT/"session_exclusions.csv",index=False)
    if df.empty:
        summary={"strategy":"TT-04","engine_revision":TT04_ENGINE_REV,"trades":0,"candidate_trades":len(coverage_gaps),"coverage_exclusions":len(coverage_gaps),"coverage_rate":0.0,"session_exclusions":len(session_exclusions),"net":0.0,"net50":0.0,"net20":0.0,"net20_50":0.0}
    else:
        df["expiry_dt"]=pd.to_datetime(df.expiry)
        splits=[]
        for name,mask in [("DEV",df.expiry_dt<=DEV_END),("VAL",(df.expiry_dt>DEV_END)&(df.expiry_dt<=VAL_END)),("HOLD",df.expiry_dt>VAL_END)]:
            z=df[mask]
            splits.append({"split":name,"trades":len(z),"net":float(z.net.sum()),"net50":float(z.net50.sum()),"win_rate":float((z.net>0).mean()) if len(z) else 0})
        vx=df.groupby("vix_state").agg(trades=("net","size"),net=("net","sum"),net50=("net50","sum"),mean=("net","mean")).reset_index()
        vx.to_csv(OUT/"vix_summary.csv",index=False)
        candidate_trades=len(df)+len(coverage_gaps); coverage_rate=len(df)/candidate_trades if candidate_trades else 0.0
        summary={"strategy":"TT-04","engine_revision":TT04_ENGINE_REV,"trades":len(df),"candidate_trades":candidate_trades,"coverage_exclusions":len(coverage_gaps),"coverage_rate":coverage_rate,"session_exclusions":len(session_exclusions),"net":float(df.net.sum()),"net50":float(df.net50.sum()),"net20":float(df.net20.sum()),"net20_50":float(df.net20_50.sum()),"splits":splits,"by_vix":vx.to_dict("records")}
        pd.DataFrame(splits).to_csv(OUT/"split_summary.csv",index=False)
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()

# F50B-029: pre-execution correction. Missing exit-leg quotes are explicit coverage exclusions, never silent trade loss or imputation.

# F50B-068: exact observed premium matching and earliest complete 15:15+ exit semantics are enforced in V3.
