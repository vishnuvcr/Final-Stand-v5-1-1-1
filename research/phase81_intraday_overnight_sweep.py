#!/usr/bin/env python3
"""Phase 81: paired static-structure intraday/overnight sweep, DEV+VAL only."""
from __future__ import annotations
import json, os, re, math, traceback
from collections import defaultdict, Counter
from datetime import date, datetime, time, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from huggingface_hub import HfApi, hf_hub_download

TZ = "Asia/Kolkata"
HF_REPO = "thetrademarkk/india-index-options-1m"
HF_REVISION = "0f4800e43e6f96cec0794369d78eb4d3c4211ef5"
CUTOFF = pd.Timestamp("2025-12-31 23:59:59", tz=TZ)
DEV_END = date(2023, 12, 31)
VAL_END = date(2025, 12, 31)
BROKERAGE = 10.0
TICK = 0.05
OUT = Path("results/phase81_intraday_overnight")
OUT.mkdir(parents=True, exist_ok=True)

# q=+1 long, q=-1 short. Offsets are absolute NIFTY points from the common ATM.
STRUCTURES = {
    "short_atm_straddle": [("CE", 0, -1), ("PE", 0, -1)],
    "short_iron_fly_w100": [("CE", 0, -1), ("PE", 0, -1), ("CE", 100, 1), ("PE", -100, 1)],
    "short_iron_fly_w200": [("CE", 0, -1), ("PE", 0, -1), ("CE", 200, 1), ("PE", -200, 1)],
    "short_iron_fly_w300": [("CE", 0, -1), ("PE", 0, -1), ("CE", 300, 1), ("PE", -300, 1)],
    "long_iron_fly_w100": [("CE", 0, 1), ("PE", 0, 1), ("CE", 100, -1), ("PE", -100, -1)],
    "long_iron_fly_w200": [("CE", 0, 1), ("PE", 0, 1), ("CE", 200, -1), ("PE", -200, -1)],
    "long_iron_fly_w300": [("CE", 0, 1), ("PE", 0, 1), ("CE", 300, -1), ("PE", -300, -1)],
    "short_iron_condor_100_300": [("PE", -300, 1), ("PE", -100, -1), ("CE", 100, -1), ("CE", 300, 1)],
    "bull_put_credit_100_300": [("PE", -100, -1), ("PE", -300, 1)],
    "bear_call_credit_100_300": [("CE", 100, -1), ("CE", 300, 1)],
}
WINDOWS = ("intraday", "overnight")

def ts_local(s):
    x = pd.to_datetime(s)
    if getattr(x, "tzinfo", None) is None:
        return x.tz_localize(TZ)
    return x.tz_convert(TZ)

def series_local(s):
    x = pd.to_datetime(s, errors="coerce")
    if x.dt.tz is None:
        return x.dt.tz_localize(TZ)
    return x.dt.tz_convert(TZ)

def at(day, hhmm):
    return pd.Timestamp(f"{day.isoformat()} {hhmm}:00", tz=TZ)

def split_for(d):
    if d <= DEV_END:
        return "development"
    if d <= VAL_END:
        return "validation"
    return "outside_registered_window"

def lot_size_for_expiry(e):
    # Frozen schedule used in the previous Phase-45 accounting engine.
    if e < date(2021, 7, 29): return 75
    if e < date(2024, 5, 2): return 50
    if e <= date(2024, 12, 26): return 25
    if e <= date(2025, 1, 23): return 75
    if e == date(2025, 1, 30): return 25
    if e < date(2026, 1, 6): return 75
    return 65

def fee_rates(d):
    # Historical NSE index-option premium charges from frozen Phase-45 model.
    stt = 0.0010 if d >= date(2024, 10, 1) else 0.000625
    if d >= date(2024, 10, 1):
        txn, ipft = 0.0003503, 0.000005
    else:
        txn, ipft = 0.000495, 0.000005
    return stt, txn, 0.000001, ipft, 0.00003

def charges(orders, lot):
    brokerage = BROKERAGE * len(orders)
    exchange = sebi = ipft = stt = stamp = 0.0
    for d, side, premium, qty in orders:
        sr, tx, se, ip, sd = fee_rates(d)
        turnover = max(0.0, float(premium)) * lot * abs(qty)
        exchange += tx * turnover
        sebi += se * turnover
        ipft += ip * turnover
        if side == "sell":
            stt += sr * turnover
        else:
            stamp += sd * turnover
    gst = 0.18 * (brokerage + exchange + sebi + ipft)
    return brokerage + exchange + sebi + ipft + stt + stamp + gst

def adverse(px, action, ticks):
    adj = float(px) + (TICK*ticks if action == "buy" else -TICK*ticks)
    if not np.isfinite(adj) or adj <= 0:
        raise ValueError("nonpositive price after adverse slippage")
    return adj

def load_vix():
    p=Path("data/phase40_vix/india_vix.csv")
    if not p.exists():
        return pd.DataFrame(columns=["date","vix"])
    x=pd.read_csv(p)
    dc=next((c for c in x.columns if c.lower()=="date"),None)
    cc=next((c for c in x.columns if c.lower()=="close"),None)
    if not dc or not cc:
        return pd.DataFrame(columns=["date","vix"])
    x["date"]=series_local(x[dc])
    x["date"]=x["date"].dt.normalize()
    x["vix"]=pd.to_numeric(x[cc],errors="coerce")
    return x[["date","vix"]].dropna().drop_duplicates("date").sort_values("date")

def lagged_vix_state(vix, d):
    if vix.empty:
        return "UNAVAILABLE"
    day=pd.Timestamp(d.isoformat(),tz=TZ)
    hist=vix[vix["date"] < day].tail(253)
    if len(hist)<60:
        return "UNAVAILABLE"
    last=float(hist.iloc[-1]["vix"])
    basis=hist.iloc[:-1].tail(252)["vix"].astype(float)
    if len(basis)<40:
        return "UNAVAILABLE"
    q25=float(basis.quantile(.25)); q75=float(basis.quantile(.75))
    if last <= q25: return "LOW"
    if last >= q75: return "HIGH"
    return "NORMAL"

def get_option_row(snapshots, ts, typ, strike, expected_expiry):
    snap=snapshots.get(ts)
    if snap is None:
        raise ValueError("missing_exact_timestamp")
    key=(typ, float(strike), expected_expiry.isoformat())
    row=snap.get(key, "__MISSING__")
    if row == "__MISSING__":
        raise ValueError("missing_exact_contract_bar")
    if row is None:
        raise ValueError("duplicate_exact_contract_bar")
    if row["expiry_date"] != expected_expiry.isoformat():
        raise ValueError("explicit_expiry_identity_mismatch")
    if not np.isfinite(row["open"]) or row["open"] <= 0:
        raise ValueError("invalid_open_price")
    if not np.isfinite(row["volume"]) or row["volume"] <= 0:
        raise ValueError("zero_or_missing_volume")
    return row

def eval_trade(snapshots, entry_ts, exit_ts, atm, expiry, legs, lot, ticks):
    pnl=0.0; orders=[]
    for typ, off, q in legs:
        strike=float(atm+off)
        ent=get_option_row(snapshots,entry_ts,typ,strike,expiry)
        ext=get_option_row(snapshots,exit_ts,typ,strike,expiry)
        ent_side="buy" if q>0 else "sell"
        ext_side="sell" if q>0 else "buy"
        ep=adverse(ent["open"],ent_side,ticks)
        xp=adverse(ext["open"],ext_side,ticks)
        pnl += q*(xp-ep)*lot
        orders.append((entry_ts.date(),ent_side,ep,1))
        orders.append((exit_ts.date(),ext_side,xp,1))
    fee=charges(orders,lot)
    return {"net":pnl-fee,"pnl_after_slippage_pre_fee":pnl,"fees":fee,
            "gross_unadjusted":None,"lot_size":lot,"legs":len(legs),"ticks":ticks}

def main():
    token=os.getenv("HF_TOKEN") or None
    api=HfApi(token=token)
    repo_files=api.list_repo_files(repo_id=HF_REPO,repo_type="dataset",revision=HF_REVISION)
    rx=re.compile(r"^options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet$")
    expiries={}
    for filename in repo_files:
        m=rx.match(filename)
        if not m: continue
        e=date.fromisoformat(m.group(1))
        if e <= VAL_END:
            expiries[e]=filename
    expiry_dates=sorted(expiries)
    if len(expiry_dates)<10:
        raise RuntimeError(f"Too few expiry files in pinned revision: {len(expiry_dates)}")

    idx_path=hf_hub_download(repo_id=HF_REPO,filename="index/NIFTY.parquet",
                             repo_type="dataset",revision=HF_REVISION,token=token)
    idx=pd.read_parquet(idx_path,columns=["timestamp","close"])
    idx["timestamp"]=series_local(idx["timestamp"])
    idx=idx[idx["timestamp"] <= CUTOFF].copy()
    idx["close"]=pd.to_numeric(idx["close"],errors="coerce")
    idx=idx.dropna(subset=["timestamp","close"]).drop_duplicates("timestamp").sort_values("timestamp")
    idx["day"]=idx["timestamp"].dt.date
    idx["hm"]=idx["timestamp"].dt.strftime("%H:%M")
    spot_lookup={(r.day,r.hm):float(r.close) for r in idx.itertuples(index=False)}
    session_dates=sorted(set(idx.loc[(idx["timestamp"] >= pd.Timestamp("2021-05-27",tz=TZ)),"day"]))
    eligible_dates=[]
    by_expiry=defaultdict(list)
    date_to_next={}
    expiry_set=set(expiry_dates)
    for i,d in enumerate(session_dates[:-1]):
        nd=session_dates[i+1]
        if d < date(2021,5,27) or d>VAL_END: continue
        # Keep contracts alive through both exit points. The next session may not be expiry.
        possible=[e for e in expiry_dates if e>nd]
        if not possible: continue
        e=possible[0]
        if e<=nd or e>VAL_END: continue
        date_to_next[d]=nd
        by_expiry[e].append(d)
        eligible_dates.append(d)

    vix=load_vix()
    trades=[]; exclusions=[]; file_errors=[]; files_loaded=0
    quality_counters=Counter()
    expected_dates=len(eligible_dates)
    for expiry, days in sorted(by_expiry.items()):
        filename=expiries[expiry]
        try:
            path=hf_hub_download(repo_id=HF_REPO,filename=filename,repo_type="dataset",
                                 revision=HF_REVISION,token=token)
            cols=["timestamp","open","volume","option_type","strike","expiry"]
            df=pd.read_parquet(path,columns=cols)
            df["timestamp"]=series_local(df["timestamp"])
            df["option_type"]=df["option_type"].astype(str).str.upper().str.strip()
            df["strike"]=pd.to_numeric(df["strike"],errors="coerce")
            df["open"]=pd.to_numeric(df["open"],errors="coerce")
            df["volume"]=pd.to_numeric(df["volume"],errors="coerce")
            df["expiry_date"]=pd.to_datetime(df["expiry"],errors="coerce").dt.strftime("%Y-%m-%d")
            # Verify explicit contract identity before time selection.
            relevant_days=set(days)
            needed_ts=set()
            for d in days:
                nd=date_to_next[d]
                needed_ts.update([at(d,"09:20"),at(d,"15:20"),at(nd,"09:20")])
            df=df[df["timestamp"].isin(needed_ts)].copy()
            if df.empty:
                for d in days:
                    exclusions.append({"date":d.isoformat(),"expiry":expiry.isoformat(),"variant":"ALL","reason":"no_option_rows_at_required_times","split":split_for(d)})
                continue
            # The strike/side key must include explicit expiry identity.
            expected_expiry=expiry.isoformat()
            mismatch_mask=df["expiry_date"] != expected_expiry
            quality_counters["rows_with_expiry_not_matching_file_name"] += int(mismatch_mask.sum())
            df=df[~mismatch_mask].copy()
            if df.empty:
                for d in days:
                    exclusions.append({"date":d.isoformat(),"expiry":expiry.isoformat(),"variant":"ALL","reason":"no_expected_expiry_rows_at_required_times","split":split_for(d)})
                continue
            snapshots={}
            for ts,group in df.groupby("timestamp",sort=False):
                snap={}
                for (typ,strike,exp),contract_rows in group.groupby(["option_type","strike","expiry_date"],dropna=False,sort=False):
                    if pd.isna(strike) or pd.isna(typ) or pd.isna(exp):
                        quality_counters["rows_with_invalid_identity_fields"] += int(len(contract_rows))
                        continue
                    key=(str(typ),float(strike),str(exp))
                    value_rows=contract_rows[["open","volume"]].drop_duplicates()
                    if len(contract_rows)>1:
                        if len(value_rows)==1:
                            quality_counters["identical_duplicate_rows_collapsed"] += int(len(contract_rows)-1)
                            chosen=contract_rows.iloc[0]
                        else:
                            quality_counters["conflicting_duplicate_contract_minute_keys"] += 1
                            snap[key]=None
                            continue
                    else:
                        chosen=contract_rows.iloc[0]
                    snap[key]={"open":float(chosen["open"]) if pd.notna(chosen["open"]) else np.nan,
                               "volume":float(chosen["volume"]) if pd.notna(chosen["volume"]) else np.nan,
                               "expiry_date":str(chosen["expiry_date"])}
                snapshots[ts]=snap
            files_loaded += 1
        except Exception as exc:
            file_errors.append({"expiry":expiry.isoformat(),"file":filename,"error":repr(exc)})
            for d in days:
                exclusions.append({"date":d.isoformat(),"expiry":expiry.isoformat(),"variant":"ALL","reason":"file_load_or_schema_error","split":split_for(d)})
            continue

        lot=lot_size_for_expiry(expiry)
        for d in days:
            nd=date_to_next[d]
            spot=spot_lookup.get((d,"09:19"))
            if spot is None or not np.isfinite(spot) or spot<=0:
                exclusions.append({"date":d.isoformat(),"expiry":expiry.isoformat(),"variant":"ALL","reason":"missing_prior_0919_spot","split":split_for(d)})
                continue
            atm=float(int(math.floor(spot/50.0+0.5))*50)
            day_entry=at(d,"09:20"); day_exit=at(d,"15:20")
            overnight_entry=at(d,"15:20"); overnight_exit=at(nd,"09:20")
            for variant,legs in STRUCTURES.items():
                results={}
                err=[]
                for window,ent,ext in [("intraday",day_entry,day_exit),("overnight",overnight_entry,overnight_exit)]:
                    try:
                        one=eval_trade(snapshots,ent,ext,atm,expiry,legs,lot,1)
                        two=eval_trade(snapshots,ent,ext,atm,expiry,legs,lot,2)
                        results[window]=(one,two)
                    except Exception as exc:
                        err.append(f"{window}:{str(exc)}")
                # Retain only complete pairs to avoid comparing different session samples.
                if len(results)!=2:
                    reason="paired_sample_incomplete:"+";".join(err)
                    exclusions.append({"date":d.isoformat(),"expiry":expiry.isoformat(),"variant":variant,"reason":reason,"split":split_for(d)})
                    continue
                state=lagged_vix_state(vix,d)
                for window,(one,two) in results.items():
                    trades.append({"date":d.isoformat(),"next_date":nd.isoformat(),"expiry":expiry.isoformat(),
                        "split":split_for(d),"vix_state_lagged":state,"variant":variant,"window":window,
                        "atm_anchor_0919":int(atm),"lot_size":lot,"leg_count":len(legs),
                        "pnl_after_slippage_pre_fee":round(one["pnl_after_slippage_pre_fee"],6),
                        "fees_1tick":round(one["fees"],6),"net_1tick":round(one["net"],6),
                        "fees_2tick":round(two["fees"],6),"net_2tick":round(two["net"],6)})
            if len(trades)%200==0 and trades:
                pd.DataFrame(trades).to_csv(OUT/"progress_trades.csv",index=False)
        print(f"expiry={expiry.isoformat()} session_days={len(days)} records={len(trades)} exclusions={len(exclusions)}")

    trade_df=pd.DataFrame(trades)
    excl_df=pd.DataFrame(exclusions)
    errors_df=pd.DataFrame(file_errors)
    if trade_df.empty:
        raise RuntimeError("No complete paired trades; inspect exclusions and source schema")
    trade_df.to_csv(OUT/"paired_trade_ledger.csv",index=False)
    excl_df.to_csv(OUT/"exclusions.csv",index=False)
    errors_df.to_csv(OUT/"file_errors.csv",index=False)

    # Main summary only for DEV and VAL; no 2026 rows were loaded or ranked.
    summaries=[]
    for keys,g in trade_df.groupby(["split","variant","window"],sort=True):
        split,variant,window=keys
        g=g.sort_values(["date","expiry"])
        vals=g["net_1tick"].to_numpy(float)
        vals2=g["net_2tick"].to_numpy(float)
        losses=-vals[vals<0].sum()
        pf=float(vals[vals>0].sum()/losses) if losses>0 else (float("inf") if vals.sum()>0 else None)
        eq=np.cumsum(vals)
        dd=float(np.max(np.maximum.accumulate(np.r_[0,eq])-np.r_[0,eq])) if len(eq) else 0.0
        summaries.append({"split":split,"variant":variant,"window":window,"trades":int(len(g)),
          "total_net_1tick":round(float(vals.sum()),2),"mean_net_1tick":round(float(vals.mean()),2),
          "median_net_1tick":round(float(np.median(vals)),2),"win_rate_1tick":round(float((vals>0).mean()),4),
          "profit_factor_1tick":None if pf is None or not np.isfinite(pf) else round(pf,4),
          "max_drawdown_trade_order":round(dd,2),"total_net_2tick":round(float(vals2.sum()),2),
          "mean_net_2tick":round(float(vals2.mean()),2),"total_fees_1tick":round(float(g["fees_1tick"].sum()),2),
          "median_trade_fees_1tick":round(float(g["fees_1tick"].median()),2)})
    summary_df=pd.DataFrame(summaries)
    summary_df.to_csv(OUT/"summary_by_split_variant_window.csv",index=False)

    pairs=trade_df.pivot_table(index=["date","expiry","split","variant"],columns="window",values=["net_1tick","net_2tick"],aggfunc="first")
    if ("net_1tick","intraday") in pairs.columns and ("net_1tick","overnight") in pairs.columns:
        pairs=pairs.dropna(subset=[("net_1tick","intraday"),("net_1tick","overnight")]).copy()
        pair_rows=[]
        for (d,e,split,variant),row in pairs.iterrows():
            pair_rows.append({"date":d,"expiry":e,"split":split,"variant":variant,
                "overnight_minus_intraday_1tick":round(float(row[("net_1tick","overnight")]-row[("net_1tick","intraday")]),6),
                "overnight_minus_intraday_2tick":round(float(row[("net_2tick","overnight")]-row[("net_2tick","intraday")]),6)})
        pair_df=pd.DataFrame(pair_rows)
    else:
        pair_df=pd.DataFrame(columns=["date","expiry","split","variant","overnight_minus_intraday_1tick","overnight_minus_intraday_2tick"])
    pair_df.to_csv(OUT/"paired_window_differences.csv",index=False)

    vix_rows=[]
    for keys,g in trade_df.groupby(["split","variant","window","vix_state_lagged"],sort=True):
        split,variant,window,state=keys
        vix_rows.append({"split":split,"variant":variant,"window":window,"vix_state_lagged":state,"trades":len(g),
                         "total_net_1tick":round(float(g["net_1tick"].sum()),2),"mean_net_1tick":round(float(g["net_1tick"].mean()),2),
                         "total_net_2tick":round(float(g["net_2tick"].sum()),2)})
    pd.DataFrame(vix_rows).to_csv(OUT/"descriptive_lagged_vix_summary.csv",index=False)

    counts=Counter(excl_df["reason"].astype(str)) if not excl_df.empty else Counter()
    bysplit=trade_df.groupby("split").agg(rows=("date","size"),sessions=("date","nunique")).reset_index().to_dict("records")
    summary={"phase":81,"decision":"EXPLORATORY_SWEEP_COMPLETE_NO_PROMOTION",
      "source":{"dataset":HF_REPO,"revision":HF_REVISION,"license":"CC-BY-NC-4.0","raw_prices_committed":False},
      "universe":{"declared_structure_variants":len(STRUCTURES),"paired_windows":list(WINDOWS),"paired_difference_tests":len(STRUCTURES),
                  "session_assignment_count":expected_dates,"expiry_files_loaded":files_loaded,"eligible_trade_rows":int(len(trade_df)),
                  "complete_paired_session_variant_count":int(len(pair_df))},
      "temporal_policy":{"development_through":DEV_END.isoformat(),"validation_through":VAL_END.isoformat(),"holdout_2026":"not downloaded/read for this sweep and not ranked"},
      "exclusions":{"records":int(len(excl_df)),"reason_counts":dict(counts),"file_errors":int(len(errors_df))},
      "data_quality":{"rows_with_expiry_not_matching_file_name":int(quality_counters["rows_with_expiry_not_matching_file_name"]),
        "rows_with_invalid_identity_fields":int(quality_counters["rows_with_invalid_identity_fields"]),
        "identical_duplicate_rows_collapsed":int(quality_counters["identical_duplicate_rows_collapsed"]),
        "conflicting_duplicate_contract_minute_keys":int(quality_counters["conflicting_duplicate_contract_minute_keys"]),
        "note":"Only duplicates identical on open and volume for the same timestamp/expiry/side/strike are collapsed; conflicting duplicates remain excluded."},
      "cost_model":{"paytm_money_brokerage_per_executed_order_inr":BROKERAGE,"one_tick_inr":TICK,"stress_ticks_per_fill":2,
        "fee_schedule":"frozen Phase-45 historical model: STT 0.0625% before 2024-10-01 and 0.10% after; historical exchange/IPFT/SEBI, stamp duty and 18% GST; no expiry exercise assumed"},
      "limitations":["No bid/ask/depth; candle-open fills plus adverse tick are not executable quote evidence.",
        "Short ATM straddle is unbounded-risk diagnostic-only, not eligible for live promotion.",
        "Static multi-leg structures do not replicate the delta-hedged Bhat et al. (2024) paper.",
        "Expiry-session dates and dates where next session equals expiry are skipped.",
        "Only ten frozen structure variants were tested; this is not all combinations.",
        "Lagged VIX summaries are descriptive and not independently selected for profitability.",
        "2026 holdout was kept out of the computation and candidate ranking."]}

    # Make report a conservative descriptive summary, no inferential claims.
    report=["# Phase 81 — Paired intraday vs overnight option-structure sweep","",
       "**Decision: exploratory comparison complete; no strategy promotion from this phase.**","",
       f"- Pinned source revision: {HF_REVISION}",
       f"- Declared structure variants: {len(STRUCTURES)}; paired windows: intraday and overnight.",
       f"- Expiry files loaded: {files_loaded}; complete paired rows: {len(trade_df)}; paired date×variant differences: {len(pair_df)}.",
       f"- Assigned sessions before completeness exclusions: {expected_dates}; exclusion records: {len(excl_df)}; file errors: {len(errors_df)}.",
       "- Temporal window: development through 2023-12-31, validation through 2025-12-31. No 2026 holdout rows are loaded, scored or ranked.",
       "- Primary prices are 09:20/15:20 candle opens with common 09:19 spot-based ATM anchor; require all exact expiry/strike/side bars and nonzero volume at entry/exit.",
       "- Costs include assumed Paytm Money brokerage of ₹10 per executed order, historical statutory fees, one adverse ₹0.05 tick per leg/fill and a two-tick stress. OHLC-only fills do not prove executable prices.",
       "",
       "## Highest-level results (descriptive only)","","See summary_by_split_variant_window.csv for every structure and time window; paired_window_differences.csv for matched overnight-minus-intraday comparisons; descriptive_lagged_vix_summary.csv for lagged regime counts and outcomes; exclusions.csv for omitted observations.",
       "",
       "## Method boundary","","The holding-window test is a static-structure adaptation motivated by published delta-hedged overnight/intraday evidence; it is not a direct replication. The 10 declared structure variants are a bounded test basket, not all possible options strategies/parameter combinations. No candidate has been promoted; Phase 82 must perform paired/expiry-cluster inference and multiple-testing correction before any holdout confirmation.",
       "",
       "## File errors"]
    if errors_df.empty: report.append("None logged.")
    else:
        for rr in errors_df.to_dict("records"): report.append(f"- {rr['expiry']}: {rr['error']}")
    (OUT/"report.md").write_text("\n".join(report)+"\n")
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"phase":81,"decision":summary["decision"],"files_loaded":files_loaded,
        "eligible_rows":len(trade_df),"paired_differences":len(pair_df),"exclusions":len(excl_df),"file_errors":len(errors_df)},indent=2))

if __name__=="__main__":
    main()
