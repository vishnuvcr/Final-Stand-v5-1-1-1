import os, re, math, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

try:
    import yfinance as yf
except Exception:
    yf = None

from research.backtest_dynamic_n_corrected import (
    REPO, TZ, START, END, ENTRY_HOUR, ENTRY_MINUTE, DTE_SESSIONS,
    STRIKE_INTERVAL, HIGH_N_THRESHOLD, TARGET_FRACTION, SLIPPAGE_TICKS,
    TICK, BROKERAGE_PER_ORDER, load, normalize, prices_at, required_strikes,
    nearest_atm, exec_px, charges, pnl_points, lot_size_for_expiry,
)

OUT = Path(os.getenv("OUT_DIR", "results/dynamic_n_corrected/phase23_entry_state"))
OUT.mkdir(parents=True, exist_ok=True)

TRAIN_END = pd.Timestamp("2023-12-31", tz=TZ)
VALIDATION_END = pd.Timestamp("2025-12-31", tz=TZ)
HOLDOUT_START = pd.Timestamp("2026-01-01", tz=TZ)

FEATURE_AUDIT = []
ERRORS = []


def log_error(scope, msg):
    ERRORS.append({"scope": scope, "error": str(msg)})


def select_n_from_map(px_map, strike_map):
    req = {n: px_map.get(strike_map[n]) for n in range(6, 18)}
    if any(v is None or not np.isfinite(v) for v in req.values()):
        return None
    scores = pd.DataFrame({
        "n": range(6, 16),
        "x_n": [req[n+2] + req[n+1] - req[n] for n in range(6,16)]
    })
    x_max = float(scores.x_n.max())
    if not np.isfinite(x_max) or x_max <= 0:
        return None
    threshold = HIGH_N_THRESHOLD * x_max
    elig = scores[scores.x_n >= threshold]
    if elig.empty:
        return None
    n = int(elig.n.max())
    return {
        "n": n,
        "x_selected": float(scores.loc[scores.n == n, "x_n"].iloc[0]),
        "x_max": x_max,
        "threshold": threshold,
        "scores": scores,
        "prices": req,
    }


def bs_iv_proxy(price, spot, strike, t_years, is_call, r=0.0):
    if not np.isfinite(price) or price <= 0 or spot <= 0 or strike <= 0 or t_years <= 0:
        return np.nan
    intrinsic=max(spot-strike,0.0) if is_call else max(strike-spot,0.0)
    if price <= intrinsic:
        return np.nan
    def norm_cdf(x): return 0.5*(1.0+math.erf(x/math.sqrt(2.0)))
    def value(sig):
        if sig <= 0: return intrinsic
        d1=(math.log(spot/strike)+(r+0.5*sig*sig)*t_years)/(sig*math.sqrt(t_years))
        d2=d1-sig*math.sqrt(t_years)
        if is_call:
            return spot*norm_cdf(d1)-strike*math.exp(-r*t_years)*norm_cdf(d2)
        return strike*math.exp(-r*t_years)*norm_cdf(-d2)-spot*norm_cdf(-d1)
    lo,hi=1e-6,8.0
    vlo,vhi=value(lo)-price,value(hi)-price
    if vlo*vhi>0: return np.nan
    for _ in range(80):
        mid=(lo+hi)/2
        vm=value(mid)-price
        if abs(vm)<1e-8: return mid
        if vlo*vm<=0: hi=mid
        else: lo=mid; vlo=vm
    return (lo+hi)/2


def build_path(df, entry_ts, expiry, typ, strike_map, sel):
    n = sel["n"]
    k = [float(strike_map[n]), float(strike_map[n+1]), float(strike_map[n+2])]
    raw_entry = (sel["prices"][n], sel["prices"][n+1], sel["prices"][n+2])
    ep = (exec_px(raw_entry[0],"buy"), exec_px(raw_entry[1],"sell"), exec_px(raw_entry[2],"sell"))
    lot = lot_size_for_expiry(expiry)
    target = TARGET_FRACTION * sel["x_selected"] * lot
    end_ts = expiry.normalize() + pd.Timedelta(hours=15, minutes=29)
    q = df[(df.timestamp > entry_ts) & (df.timestamp <= end_ts) &
           (df.option_type == typ) & (df.strike.isin(k))]
    piv = q.pivot_table(index="timestamp", columns="strike", values="close", aggfunc="last")
    piv = piv.dropna(subset=k)
    if piv.empty:
        return None
    mfe = -np.inf
    exit_ts = piv.index[-1]
    reason = "EXPIRY"
    exit_raw = None
    for ts, row in piv.iterrows():
        raw = (float(row[k[0]]), float(row[k[1]]), float(row[k[2]]))
        xp = (exec_px(raw[0],"sell"), exec_px(raw[1],"buy"), exec_px(raw[2],"buy"))
        gross = pnl_points(ep, xp) * lot
        mfe = max(mfe, gross)
        if gross >= target:
            exit_ts, reason, exit_raw = ts, "TARGET", raw
            break
        if ts.date() == expiry.date() and (ts.hour > 13 or (ts.hour == 13 and ts.minute >= 30)):
            if gross < 0 and mfe < 0.50 * target:
                exit_ts, reason, exit_raw = ts, "CONDITIONAL_STOP", raw
                break
    if exit_raw is None:
        r = piv.loc[exit_ts]
        exit_raw = (float(r[k[0]]), float(r[k[1]]), float(r[k[2]]))
    xp = (exec_px(exit_raw[0],"sell"), exec_px(exit_raw[1],"buy"), exec_px(exit_raw[2],"buy"))
    gross = pnl_points(ep, xp) * lot
    entry_orders=[(entry_ts,"buy",ep[0]),(entry_ts,"sell",ep[1]),(entry_ts,"sell",ep[2])]
    exit_orders=[(exit_ts,"sell",xp[0]),(exit_ts,"buy",xp[1]),(exit_ts,"buy",xp[2])]
    cost=charges(entry_orders, exit_orders, lot)
    return {
        "entry_ts": str(entry_ts), "exit_ts": str(exit_ts), "option_type": typ,
        "n": n, "k_n": k[0], "k_n1": k[1], "k_n2": k[2],
        "x_selected": sel["x_selected"], "x_max": sel["x_max"],
        "target": target, "lot": lot, "gross": gross,
        "cost": cost, "net": gross-cost, "mfe": mfe,
        "exit_reason": reason,
    }


def daily_close_series(tickers, start_date, end_date):
    out={}
    if yf is None:
        return out
    for name,ticker in tickers.items():
        try:
            d=yf.download(ticker, start=(start_date-pd.Timedelta(days=8)).date(),
                          end=(end_date+pd.Timedelta(days=2)).date(),
                          progress=False, auto_adjust=False, group_by="column", threads=False)
            if d.empty: raise RuntimeError("empty")
            close=d["Close"]
            if isinstance(close,pd.DataFrame): close=close.iloc[:,0]
            close=pd.to_numeric(close, errors="coerce").dropna()
            close.index=pd.to_datetime(close.index).tz_localize(None)
            out[name]=close
            FEATURE_AUDIT.append({"feature":name,"source":ticker,"status":"available",
                                  "granularity":"daily close; prior-session only"})
        except Exception as e:
            log_error("cross_market:"+name,e)
            FEATURE_AUDIT.append({"feature":name,"source":ticker,"status":"unavailable","reason":repr(e)})
    return out


def prior_return(series, date):
    if series is None or len(series)==0: return np.nan
    s=series[series.index < date.tz_localize(None)]
    if len(s)<2: return np.nan
    return float(np.log(s.iloc[-1]/s.iloc[-2]))


def build_option_entry_row(expiry, entry_ts, spot_entry, atm, cpx, ppx, cks, pks, selected_direction, snapshot):
    row={"expiry":str(expiry.date()),"entry_date":str(entry_ts.date()),"entry_ts":str(entry_ts),"spot":spot_entry,"atm":atm,
         "x_call":float(cpx[cks[8]]+cpx[cks[7]]-cpx[cks[6]]),
         "x_put":float(ppx[pks[8]]+ppx[pks[7]]-ppx[pks[6]]),
         "selected_direction":selected_direction}
    sx=row["x_call"] if selected_direction=="BEARISH" else row["x_put"]
    ox=row["x_put"] if selected_direction=="BEARISH" else row["x_call"]
    row["direction_margin"]=(sx-ox)/(abs(sx)+abs(ox)) if abs(sx)+abs(ox)>0 else np.nan
    row["selected_x"]=sx; row["opposite_x"]=ox
    for typ, px, strikes in [("CE",cpx,cks),("PE",ppx,pks)]:
        for n in range(6,18):
            v=px.get(strikes[n])
            row[f"{typ}_p{n}"]=float(v) if v is not None else np.nan
    for typ, px, strikes in [("CE",cpx,cks),("PE",ppx,pks)]:
        for n in range(6,18):
            strike=strikes[n]
            recs=[] if px.get(strike) is None else [px[strike]]
    for typ, px, strikes in [("CE",cpx,cks),("PE",ppx,pks)]:
        for n in range(6,18):
            k = strikes[n]
            rec = snapshot.get((typ, float(k)))
            row[f"{typ}_oi{n}"] = rec.get("open_interest", np.nan) if rec else np.nan
            row[f"{typ}_vol{n}"] = rec.get("volume", np.nan) if rec else np.nan
    row["total_ce_oi"] = float(np.nansum([row.get(f"CE_oi{n}",np.nan) for n in range(6,18)]))
    row["total_pe_oi"] = float(np.nansum([row.get(f"PE_oi{n}",np.nan) for n in range(6,18)]))
    row["put_call_oi_ratio"] = row["total_pe_oi"]/row["total_ce_oi"] if row["total_ce_oi"] > 0 else np.nan
    return row


def make_external_features(dates):
    start=min(dates).tz_localize(None); end=max(dates).tz_localize(None)
    tickers={
      "vix":"^INDIAVIX","nifty":"^NSEI","sp500":"^GSPC","nasdaq":"^IXIC","dow":"^DJI",
      "nikkei":"^N225","hangseng":"^HSI","kospi":"^KS11","shanghai":"000001.SS",
      "usd_inr":"INR=X","gold":"GC=F","brent":"BZ=F","us10y":"^TNX","us_vix":"^VIX"
    }
    series=daily_close_series(tickers,start,end)
    rows=[]
    for d in dates:
        x={"entry_date":str(d.date())}
        for name,s in series.items():
            if name=="vix":
                prior=s[s.index < d.tz_localize(None)]
                x["india_vix_prev"]=float(prior.iloc[-1]) if len(prior) else np.nan
                x["india_vix_change1"]=float(np.log(prior.iloc[-1]/prior.iloc[-2])) if len(prior)>=2 else np.nan
            else:
                x[f"{name}_ret1"]=prior_return(s,d)
        rows.append(x)
    return pd.DataFrame(rows)


def main():
    spot=load("index/NIFTY.parquet")[["timestamp","close"]].rename(columns={"close":"spot"}).sort_values("timestamp")
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    all_exp=[]
    for f in api.list_repo_files(REPO,repo_type="dataset"):
        m=re.match(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet$",f)
        if m:
            d=pd.Timestamp(m.group(1),tz=TZ)
            if START<=d<=END: all_exp.append(d)
    exps=sorted(set(all_exp))
    monthly=set()
    for y,m in {(d.year,d.month) for d in exps}:
        mm=[d for d in exps if d.year==y and d.month==m]
        if mm: monthly.add(max(mm))
    exps=[d for d in exps if d not in monthly]

    canonical=[]; reverse=[]; entry_rows=[]; status=[]
    for expiry in exps:
        try:
            window_start=expiry-pd.Timedelta(days=14)
            dates=sorted(pd.to_datetime(spot[(spot.timestamp>=window_start)&(spot.timestamp<=expiry)].timestamp.dt.normalize().unique()))
            pre=[d for d in dates if d < expiry.normalize()]
            if len(pre)<DTE_SESSIONS: log_error(str(expiry.date()),"insufficient sessions"); continue
            entry_date=pre[-DTE_SESSIONS]
            entry_ts=entry_date+pd.Timedelta(hours=ENTRY_HOUR,minutes=ENTRY_MINUTE)
            sr=spot[spot.timestamp==entry_ts]
            if sr.empty: log_error(str(expiry.date()),"missing spot"); continue
            spot_entry=float(sr.iloc[0].spot)
            df=normalize(load(f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet"))
            eq=df[df.timestamp==entry_ts]
            for col in ("open_interest","volume"):
                if col not in df.columns:
                    FEATURE_AUDIT.append({"feature":"option_"+col,"source":"primary HF option parquet","status":"unavailable","reason":f"missing column {col}"})
                else:
                    FEATURE_AUDIT.append({"feature":"option_"+col,"source":"primary HF option parquet","status":"available","granularity":"entry timestamp"})
            atm=nearest_atm(eq,spot_entry)
            if atm is None: log_error(str(expiry.date()),"no ATM"); continue
            cks=required_strikes(atm,"CE"); pks=required_strikes(atm,"PE")
            cpx=prices_at(df,entry_ts,"CE",tuple(cks.values())); ppx=prices_at(df,entry_ts,"PE",tuple(pks.values()))
            if any(cpx.get(cks[n]) is None for n in (6,7,8)) or any(ppx.get(pks[n]) is None for n in (6,7,8)):
                log_error(str(expiry.date()),"missing Stage1 OTM6/7/8"); continue
            xc=cpx[cks[8]]+cpx[cks[7]]-cpx[cks[6]]
            xp=ppx[pks[8]]+ppx[pks[7]]-ppx[pks[6]]
            if xc==xp: continue
            direction="BEARISH" if xc>xp else "BULLISH"
            snapshot = {}
            for _, rr in eq.iterrows():
                snapshot[(str(rr.option_type).upper(), float(rr.strike))] = {
                    "open_interest": float(rr.open_interest) if "open_interest" in df.columns and pd.notna(rr.open_interest) else np.nan,
                    "volume": float(rr.volume) if "volume" in df.columns and pd.notna(rr.volume) else np.nan,
                }
            row=build_option_entry_row(expiry,entry_ts,spot_entry,atm,cpx,ppx,cks,pks,direction,snapshot)
            t_years=max((expiry-entry_ts).total_seconds()/31557600.0, 1e-6)
            selected_typ = "CE" if direction == "BEARISH" else "PE"
            sstrikes = cks if selected_typ == "CE" else pks
            spx = cpx if selected_typ == "CE" else ppx
            sel_tmp = select_n_from_map(spx,sstrikes)
            sn = sel_tmp["n"] if sel_tmp else np.nan
            if pd.notna(sn) and all(spx.get(sstrikes[int(sn)+j]) is not None for j in (0,1,2)):
                sn = int(sn)
                p0,p1,p2 = float(spx[sstrikes[sn]]),float(spx[sstrikes[sn+1]]),float(spx[sstrikes[sn+2]])
                credit = (p1-SLIPPAGE_TICKS*TICK)+(p2-SLIPPAGE_TICKS*TICK)-(p0+SLIPPAGE_TICKS*TICK)
                k0,k1,k2 = float(sstrikes[sn]),float(sstrikes[sn+1]),float(sstrikes[sn+2])
                boundary = (k1+k2-k0+credit) if selected_typ=="CE" else (k1+k2-k0-credit)
                row["boundary_distance"] = (boundary-spot_entry) if selected_typ=="CE" else (spot_entry-boundary)
                row["expected_move_4d"] = np.nan
                row["boundary_z"] = np.nan
                row["selected_x_over_long_premium"] = row["selected_x"]/p0 if p0>0 else np.nan
                row["selected_x_over_xmax"] = sel_tmp["x_selected"]/sel_tmp["x_max"] if sel_tmp["x_max"]>0 else np.nan
                row["selected_n"] = sn
            else:
                row["boundary_distance"]=np.nan; row["expected_move_4d"]=np.nan; row["boundary_z"]=np.nan
                row["selected_x_over_long_premium"]=np.nan; row["selected_x_over_xmax"]=np.nan; row["selected_n"]=np.nan
            for typ, px, strikes, is_call in [("CE",cpx,cks,True),("PE",ppx,pks,False)]:
                for n in range(6,18):
                    prem=px.get(strikes[n])
                    row[f"{typ}_iv{n}"]=bs_iv_proxy(float(prem) if prem is not None else np.nan,spot_entry,float(strikes[n]),t_years,is_call)
                ivs=[row[f"{typ}_iv{n}"] for n in range(6,18)]
                row[f"{typ}_iv_skew_6_17"]=float(np.nanmean(ivs[:3])-np.nanmean(ivs[-3:])) if np.isfinite(np.nanmean(ivs)) else np.nan
            row["iv_proxy_call_minus_put"]=row.get("CE_iv_skew_6_17",np.nan)-row.get("PE_iv_skew_6_17",np.nan)
            for typ,px,strikes in [("CE",cpx,cks),("PE",ppx,pks)]:
                complete=all(px.get(strikes[n]) is not None for n in range(6,18))
                sel=select_n_from_map(px,strikes) if complete else None
                row[f"{typ}_complete_6_17"]=complete
                row[f"{typ}_selected_n"]=sel["n"] if sel else np.nan
                row[f"{typ}_x_selected"]=sel["x_selected"] if sel else np.nan
                row[f"{typ}_x_max"]=sel["x_max"] if sel else np.nan
            entry_rows.append(row)
            sel_typ="CE" if direction=="BEARISH" else "PE"
            opp_typ="PE" if sel_typ=="CE" else "CE"
            for side,label in [(sel_typ,"CANONICAL"),(opp_typ,"REVERSE")]:
                px=strikes=None
                if side=="CE": px, strikes=cpx,cks
                else: px, strikes=ppx,pks
                sel=select_n_from_map(px,strikes)
                if not sel:
                    status.append({"expiry":str(expiry.date()),"status":label+"_UNAVAILABLE"})
                    continue
                trade=build_path(df,entry_ts,expiry,side,strikes,sel)
                if trade is None:
                    status.append({"expiry":str(expiry.date()),"status":label+"_NO_PATH"})
                    continue
                trade.update({"expiry":str(expiry.date()),"entry_date":str(entry_date.date()),
                             "spot":spot_entry,"atm":atm,"canonical_direction":direction,
                             "action":label,"stage1_x_call":xc,"stage1_x_put":xp})
                (canonical if label=="CANONICAL" else reverse).append(trade)
            status.append({"expiry":str(expiry.date()),"status":"OK"})
        except Exception as e:
            log_error(str(expiry.date()),repr(e))

    opt=pd.DataFrame(entry_rows)
    dates=[pd.Timestamp(x).tz_localize(TZ).normalize() for x in opt.entry_date] if not opt.empty else []
    ext=make_external_features(dates) if dates else pd.DataFrame()
    if not opt.empty and not ext.empty:
        opt=opt.merge(ext,on="entry_date",how="left")

    # Safe pre-10:00 NIFTY opening state from primary spot data.
    for i,row in opt.iterrows():
        ts=pd.Timestamp(row["entry_ts"])
        day=spot[spot.timestamp.dt.normalize()==ts.normalize()]
        pre10=day[day.timestamp<=ts]
        prior=spot[spot.timestamp.dt.normalize()<ts.normalize()]
        opt.loc[i,"nifty_open"]=float(day.iloc[0].spot) if len(day) else np.nan
        opt.loc[i,"overnight_gap_pct"]=float((opt.loc[i,"nifty_open"]-prior.iloc[-1].spot)/prior.iloc[-1].spot) if len(day) and len(prior) else np.nan
        opt.loc[i,"ret_10am_pct"]=float(np.log(row["spot"]/opt.loc[i,"nifty_open"])) if len(day) and opt.loc[i,"nifty_open"]>0 else np.nan
        opt.loc[i,"range_to_10am_pct"]=float((pre10.spot.max()-pre10.spot.min())/opt.loc[i,"nifty_open"]) if len(pre10) else np.nan

    can=pd.DataFrame(canonical); rev=pd.DataFrame(reverse)
    if not opt.empty:
        daily_nifty = spot.groupby(spot.timestamp.dt.normalize())["spot"].last().sort_index()
        for i,row in opt.iterrows():
            d = pd.Timestamp(row["entry_date"], tz=TZ).normalize()
            prior = daily_nifty[daily_nifty.index < d]
            for k in (5,10,20):
                cls = prior.iloc[-(k+1):] if len(prior) >= k+1 else pd.Series(dtype=float)
                if len(cls) == k+1:
                    rr = np.log(pd.Series(cls).astype(float)).diff().dropna().to_numpy()
                    opt.loc[i,f"nifty_rv{k}"] = float(np.std(rr,ddof=1)*np.sqrt(252.0))
                else:
                    opt.loc[i,f"nifty_rv{k}"] = np.nan
            rv10_tmp = opt.loc[i,"nifty_rv10"] if "nifty_rv10" in opt.columns else np.nan
            opt.loc[i,"expected_move_4d"] = float(row["spot"])*rv10_tmp*np.sqrt(4/252.0) if pd.notna(rv10_tmp) and rv10_tmp>0 else np.nan
            opt.loc[i,"boundary_z"] = opt.loc[i,"boundary_distance"]/opt.loc[i,"expected_move_4d"] if pd.notna(opt.loc[i,"expected_move_4d"]) and opt.loc[i,"expected_move_4d"]>0 else np.nan
        for feat in ["nifty_futures_basis","nifty_futures_oi_change","gift_nifty_overnight","fii_dii_prior_flow"]:
            FEATURE_AUDIT.append({"feature":feat,"source":"separate historical source not yet validated for point-in-time backfill","status":"unavailable","granularity":"not used"})
        opt.to_csv(OUT/"phase23_entry_features.csv",index=False)
    can.to_csv(OUT/"canonical_trade_ledger.csv",index=False)
    rev.to_csv(OUT/"reverse_trade_ledger.csv",index=False)
    pd.DataFrame(status).to_csv(OUT/"availability_status.csv",index=False)
    pd.DataFrame(FEATURE_AUDIT).to_csv(OUT/"feature_source_audit.csv",index=False)
    pd.DataFrame(ERRORS).to_csv(OUT/"data_errors.csv",index=False)

    meta={
      "control_universe_entries":int(len(opt)),
      "canonical_completed":int(len(can)),
      "reverse_completed":int(len(rev)),
      "reverse_completion_rate":float(len(rev)/len(can)) if len(can) else np.nan,
      "features":sorted(opt.columns.tolist()) if not opt.empty else [],
      "india_vix_present":bool("india_vix_prev" in opt.columns and opt.india_vix_prev.notna().any()) if not opt.empty else False,
      "script_note":"External daily data are used only at prior-session close relative to 10:00 IST; same-day observations after 10:00 are excluded.",
    }
    (OUT/"availability_metadata.json").write_text(json.dumps(meta,indent=2,default=str))
    print(json.dumps(meta,indent=2,default=str))


if __name__=="__main__":
    main()
