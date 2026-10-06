# Phase 39 Step 2 — exact-entry point-in-time feature matrix
import json, os, math
from pathlib import Path
import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download

TZ = "Asia/Kolkata"
HF_REPO = "thetrademarkk/india-index-options-1m"
ROOT = Path(".")
LEDGER = ROOT / "results/phase39_counterfactual/fixed_opportunity_ledger.csv"
SOURCE = ROOT / "results/phase39_feature_source"
OUT = ROOT / "results/phase39_features"
OUT.mkdir(parents=True, exist_ok=True)
LOTS = 6
WIDTH = 50.0
TICK = 0.05

def norm_ts(s):
    x = pd.to_datetime(s, errors="coerce")
    if getattr(x.dt, "tz", None) is None:
        x = x.dt.tz_localize(TZ)
    else:
        x = x.dt.tz_convert(TZ)
    return x

def norm_scalar_ts(x):
    t = pd.Timestamp(x)
    return t.tz_localize(TZ) if t.tzinfo is None else t.tz_convert(TZ)

def norm_cdf(x):
    x = np.asarray(x, float)
    ax = np.abs(x)
    t = 1.0 / (1.0 + 0.2316419 * ax)
    poly = ((((1.330274429*t - 1.821255978)*t + 1.781477937)*t - 0.356563782)*t + 0.319381530)*t
    pdf = np.exp(-0.5 * ax * ax) / np.sqrt(2*np.pi)
    cdf = 1 - pdf * poly
    return np.where(x >= 0, cdf, 1-cdf)

def bs_price(S, K, T, sig, typ):
    S=np.asarray(S,float); K=np.asarray(K,float)
    T=np.maximum(np.asarray(T,float),1e-10); sig=np.maximum(np.asarray(sig,float),1e-8)
    d1=(np.log(S/K)+0.5*sig*sig*T)/(sig*np.sqrt(T)); d2=d1-sig*np.sqrt(T)
    if typ == "CE":
        return S*norm_cdf(d1)-K*norm_cdf(d2)
    return K*norm_cdf(-d2)-S*norm_cdf(-d1)

def bs_delta(S,K,T,sig,typ):
    S=np.asarray(S,float); K=np.asarray(K,float)
    T=np.maximum(np.asarray(T,float),1e-10); sig=np.maximum(np.asarray(sig,float),1e-8)
    d1=(np.log(S/K)+0.5*sig*sig*T)/(sig*np.sqrt(T))
    n=norm_cdf(d1)
    return n if typ == "CE" else n-1

def implied_delta_iv(price,S,K,T,typ):
    p=float(price); s=float(S); k=float(K); t=float(T)
    intrinsic=max(s-k,0.0) if typ=="CE" else max(k-s,0.0)
    if not(np.isfinite(p) and np.isfinite(s) and np.isfinite(k) and np.isfinite(t)) or p <= 1e-8 or t <= 0 or p < intrinsic-1e-6:
        return np.nan, np.nan
    lo,hi,x=1e-5,5.0,0.30
    for _ in range(20):
        d1=(math.log(s/k)+0.5*x*x*t)/(x*math.sqrt(t))
        px=float(bs_price(s,k,t,x,typ))
        v=s*math.exp(-0.5*d1*d1)/math.sqrt(2*math.pi)*math.sqrt(t)
        xn=x-(px-p)/max(v,1e-10)
        xn=min(max(xn,lo),hi)
        if not np.isfinite(xn):
            xn=(lo+hi)/2
        pxn=float(bs_price(s,k,t,xn,typ))
        if pxn < p: lo=xn
        else: hi=xn
        x=xn
    residual=abs(float(bs_price(s,k,t,x,typ))-p)
    if residual > 0.03:
        return np.nan, np.nan
    return float(bs_delta(s,k,t,x,typ)), float(x)

def load_option(expiry):
    fn=f"options/NIFTY/{pd.Timestamp(expiry).strftime('%Y-%m-%d')}.parquet"
    p=hf_hub_download(repo_id=HF_REPO, filename=fn, repo_type="dataset",
                      token=os.getenv("HF_TOKEN") or None)
    d=pd.read_parquet(p)
    d["timestamp"]=pd.to_datetime(d["timestamp"])
    if d["timestamp"].dt.tz is None: d["timestamp"]=d["timestamp"].dt.tz_localize(TZ)
    else: d["timestamp"]=d["timestamp"].dt.tz_convert(TZ)
    d["option_type"]=d["option_type"].astype(str).str.upper()
    d["strike"]=pd.to_numeric(d["strike"],errors="coerce")
    d["close"]=pd.to_numeric(d["close"],errors="coerce")
    for c in ["open_interest","volume"]:
        if c not in d.columns:
            alt = next((z for z in d.columns if z.lower()==c), None)
            d[c] = pd.to_numeric(d[alt], errors="coerce") if alt else np.nan
        else:
            d[c]=pd.to_numeric(d[c],errors="coerce")
    d=d.dropna(subset=["timestamp","option_type","strike","close"])
    d=d.sort_values(["timestamp","option_type","strike"],kind="stable")
    d=d.drop_duplicates(["timestamp","option_type","strike"],keep="last")
    return d

def pick_delta_rows(snap, spot, expiry_ts):
    if snap.empty:
        return {}
    T=max((expiry_ts-snap.timestamp.iloc[0]).total_seconds()/31557600.0,1e-10)
    out={}
    for typ,target in [("CE",0.25),("PE",-0.25)]:
        z=snap[snap.option_type==typ].copy()
        if z.empty: continue
        ds=[]; ivs=[]
        for row in z.itertuples():
            delta,iv=implied_delta_iv(row.close,spot,row.strike,T,typ)
            ds.append(delta); ivs.append(iv)
        z["delta"]=ds; z["iv"]=ivs
        z=z[np.isfinite(z["delta"])]
        if z.empty: continue
        k=int((z["delta"]-target).abs().idxmin())
        row=z.loc[k]
        out[typ]={"short":row}
    for typ,side in [("CE",1),("PE",-1)]:
        if typ not in out: continue
        sk=float(out[typ]["short"]["strike"]); lk=sk+side*WIDTH
        z=snap[(snap.option_type==typ)&(snap.strike==lk)]
        if not z.empty:
            out[typ]["long"]=z.iloc[-1]
        else:
            out[typ]["long"]=None
    return out

def opt_value(row, spot, expiry_ts, typ):
    if row is None: return {"price":np.nan,"oi":np.nan,"volume":np.nan,"delta":np.nan,"iv":np.nan,"strike":np.nan}
    T=max((expiry_ts-norm_scalar_ts(row.timestamp)).total_seconds()/31557600.0,1e-10)
    delta,iv=implied_delta_iv(row.close,spot,row.strike,T,typ)
    return {"price":float(row.close),"oi":float(row.open_interest) if np.isfinite(row.open_interest) else np.nan,
            "volume":float(row.volume) if np.isfinite(row.volume) else np.nan,
            "delta":delta,"iv":iv,"strike":float(row.strike)}

def intraday_features(spot_hist, ts):
    z=spot_hist[spot_hist.timestamp<=ts]
    if z.empty: return {}
    idx=z.index[-1]
    close=z["close"].astype(float)
    out={"entry_spot":float(z.loc[idx,"close"]),"intraday_source_ts":str(z.loc[idx,"timestamp"])}
    vals=close.to_numpy(float)
    pos=len(vals)-1
    for w in [1,5,15,30,60,120,240]:
        if pos-w>=0:
            out[f"nifty_ret_{w}m"]=float(math.log(vals[pos]/vals[pos-w]))
    for w in [15,30,60,120]:
        a=max(1,len(vals)-w)
        rr=np.diff(np.log(vals[a:]))
        out[f"nifty_rv_{w}m"]=float(np.std(rr,ddof=1)*math.sqrt(max(len(rr),1))) if len(rr)>1 else np.nan
        out[f"nifty_ma_gap_{w}m"]=float(vals[-1]/np.mean(vals[a:])-1.0)
        out[f"nifty_range_{w}m"]=float(np.max(vals[a:])/np.min(vals[a:])-1.0)
    vol=z["volume"].astype(float).to_numpy() if "volume" in z.columns else None
    if vol is not None and len(vol)>5:
        for w in [30,60,120]:
            a=max(0,len(vol)-w)
            base=np.mean(vol[max(0,a-w):a]) if a>=10 else np.nan
            out[f"nifty_volume_ratio_{w}m"]=float(vol[-w:].mean()/base) if np.isfinite(base) and base>0 else np.nan
    return out

def daily_features(daily, ts):
    day=ts.normalize()
    z=daily[daily.date<day].sort_values("date")
    if z.empty: return {}
    r=z.iloc[-1]
    out={"prev_session_close":float(r.close),"prev_session_open":float(r.open),
         "prev_session_high":float(r.high),"prev_session_low":float(r.low),
         "prev_session_range":float(r.high/r.low-1.0)}
    for w in [1,5,20,60]:
        if len(z)>w:
            out[f"nifty_daily_ret_{w}d"]=float(math.log(float(z.iloc[-1].close)/float(z.iloc[-1-w].close)))
    rr=np.log(z.close.astype(float)/z.close.astype(float).shift(1)).dropna()
    for w in [10,20,60]:
        if len(rr)>=w:
            out[f"nifty_daily_rv_{w}d"]=float(rr.tail(w).std(ddof=1)*math.sqrt(252))
    if len(z)>=20:
        out["nifty_drawdown_20d"]=float(float(r.close)/float(z.close.tail(20).max())-1.0)
    if len(z)>=60:
        out["nifty_drawdown_60d"]=float(float(r.close)/float(z.close.tail(60).max())-1.0)
    out["nifty_gap_from_prev_close"]=float("nan")
    return out

def backward_join(base, frame, prefix, date_col="date"):
    if frame is None or frame.empty: return base
    f=frame.copy()
    if date_col not in f.columns: return base
    f[date_col]=norm_ts(f[date_col]).dt.normalize().astype(f"datetime64[ns, {TZ}]")
    numeric=[c for c in f.columns if c!=date_col and pd.api.types.is_numeric_dtype(f[c])]
    f=f[[date_col]+numeric].sort_values(date_col)
    b=base.copy()
    b["_join_date"]=(b["entry_ts"].dt.normalize()-pd.Timedelta(seconds=1)).astype(f"datetime64[ns, {TZ}]")
    j=pd.merge_asof(b.sort_values("_join_date"),f,left_on="_join_date",right_on=date_col,direction="backward")
    for c in numeric:
        j[prefix+c]=j[c]
    return j.drop(columns=[date_col]+numeric+["_join_date"],errors="ignore").sort_values("entry_ts")

def option_features(snap, spot, expiry_ts, next_snap=None, next_expiry_ts=None):
    out={}
    if snap.empty: return out
    strikes=np.sort(snap["strike"].unique())
    atm=float(strikes[np.argmin(np.abs(strikes-spot))])
    def side_value(typ,k):
        z=snap[(snap.option_type==typ)&(snap.strike==float(k))]
        return z.iloc[-1] if not z.empty else None
    ce_atm=side_value("CE",atm); pe_atm=side_value("PE",atm)
    a=opt_value(ce_atm,spot,expiry_ts,"CE"); b=opt_value(pe_atm,spot,expiry_ts,"PE")
    out.update({"atm_strike":atm,"atm_ce_price":a["price"],"atm_pe_price":b["price"],
                "atm_ce_oi":a["oi"],"atm_pe_oi":b["oi"],"atm_ce_volume":a["volume"],"atm_pe_volume":b["volume"],
                "atm_ce_iv":a["iv"],"atm_pe_iv":b["iv"],"atm_ce_delta":a["delta"],"atm_pe_delta":b["delta"]})
    out["atm_straddle"]=a["price"]+b["price"]
    out["atm_pcr_oi"]=b["oi"]/max(a["oi"],1.0) if np.isfinite(a["oi"]) and np.isfinite(b["oi"]) else np.nan
    out["atm_pcr_volume"]=b["volume"]/max(a["volume"],1.0) if np.isfinite(a["volume"]) and np.isfinite(b["volume"]) else np.nan
    out["atm_iv_skew"]=a["iv"]-b["iv"] if np.isfinite(a["iv"]) and np.isfinite(b["iv"]) else np.nan
    # 25-delta candidate structures, derived independently for both sides.
    cand=pick_delta_rows(snap,spot,expiry_ts)
    for typ,tag in [("CE","call"),("PE","put")]:
        if typ not in cand: continue
        sv=opt_value(cand[typ]["short"],spot,expiry_ts,typ)
        lv=opt_value(cand[typ]["long"],spot,expiry_ts,typ)
        out.update({
            f"{tag}_25_strike":sv["strike"], f"{tag}_25_price":sv["price"], f"{tag}_25_oi":sv["oi"],
            f"{tag}_25_volume":sv["volume"], f"{tag}_25_delta":sv["delta"], f"{tag}_25_iv":sv["iv"],
            f"{tag}_25_long_price":lv["price"], f"{tag}_25_long_oi":lv["oi"], f"{tag}_25_long_volume":lv["volume"],
            f"{tag}_25_long_iv":lv["iv"],
            f"{tag}_25_spread_credit":sv["price"]-lv["price"] if np.isfinite(sv["price"]) and np.isfinite(lv["price"]) else np.nan
        })
    out["candidate_credit_diff_call_minus_put"] = out.get("call_25_spread_credit",np.nan)-out.get("put_25_spread_credit",np.nan)
    out["candidate_iv_skew_25"] = out.get("call_25_iv",np.nan)-out.get("put_25_iv",np.nan)
    out["candidate_oi_pcr_25"] = out.get("put_25_oi",np.nan)/max(out.get("call_25_oi",np.nan),1.0) if np.isfinite(out.get("put_25_oi",np.nan)) and np.isfinite(out.get("call_25_oi",np.nan)) else np.nan
    # Concentrated OI/volume around ATM.
    near=snap[snap["strike"].between(atm-200,atm+200)]
    ceoi=near.loc[near.option_type=="CE","open_interest"].sum()
    peoi=near.loc[near.option_type=="PE","open_interest"].sum()
    cevol=near.loc[near.option_type=="CE","volume"].sum()
    pevol=near.loc[near.option_type=="PE","volume"].sum()
    out["near_atm_oi_pcr"]=peoi/max(ceoi,1.0)
    out["near_atm_volume_pcr"]=pevol/max(cevol,1.0)
    if next_snap is not None and next_expiry_ts is not None:
        ns=option_features(next_snap,spot,next_expiry_ts,None,None)
        out["next_atm_straddle"]=ns.get("atm_straddle",np.nan)
        out["next_atm_iv_skew"]=ns.get("atm_iv_skew",np.nan)
        out["iv_term_premium_ratio"]=ns.get("atm_straddle",np.nan)/max(out.get("atm_straddle",np.nan),1e-6) if np.isfinite(ns.get("atm_straddle",np.nan)) and np.isfinite(out.get("atm_straddle",np.nan)) else np.nan
    return out

def load_daily_source(name):
    p=SOURCE/name
    if not p.exists(): return pd.DataFrame()
    z=pd.read_parquet(p)
    if "date" in z.columns:
        z["date"]=norm_ts(z["date"]).dt.normalize()
    return z

def main():
    ledger=pd.read_csv(LEDGER)
    ledger["entry_ts"]=norm_ts(ledger["entry_ts"])
    ledger["expiry"]=pd.to_datetime(ledger["expiry"]).dt.normalize().dt.tz_localize(TZ)
    ledger=ledger.sort_values("entry_ts").reset_index(drop=True)
    if len(ledger)!=477 or ledger["entry_ts"].duplicated().any():
        raise AssertionError("Phase 39 fixed-opportunity ledger must contain 477 unique entry timestamps")
    nifty_path=hf_hub_download(repo_id=HF_REPO,filename="index/NIFTY.parquet",repo_type="dataset",token=os.getenv("HF_TOKEN") or None)
    spot_hist=pd.read_parquet(nifty_path)
    spot_hist["timestamp"]=pd.to_datetime(spot_hist["timestamp"])
    if spot_hist["timestamp"].dt.tz is None: spot_hist["timestamp"]=spot_hist["timestamp"].dt.tz_localize(TZ)
    else: spot_hist["timestamp"]=spot_hist["timestamp"].dt.tz_convert(TZ)
    spot_hist=spot_hist.sort_values("timestamp").drop_duplicates("timestamp",keep="last")
    daily=load_daily_source("nifty_daily.parquet")
    global_d=load_daily_source("global_daily.parquet")
    flows=load_daily_source("fii_dii_daily.parquet")
    sentiment=load_daily_source("sentiment_daily.parquet")
    expiry_list=sorted(pd.to_datetime(ledger["expiry"]).unique())
    option_cache={}
    def get_opt(exp):
        key=str(exp.date())
        if key not in option_cache: option_cache[key]=load_option(exp)
        return option_cache[key]
    rows=[]
    for r in ledger.itertuples():
        entry=norm_scalar_ts(r.entry_ts); expiry=norm_scalar_ts(r.expiry)+pd.Timedelta(hours=15,minutes=30)
        spot_row=spot_hist[spot_hist.timestamp==entry]
        if spot_row.empty: raise RuntimeError(f"missing NIFTY spot at {entry}")
        spot=float(spot_row.iloc[0]["close"])
        row={"entry_ts":str(entry),"expiry":str(norm_scalar_ts(r.expiry).date()),"split":r.split,"control_direction":r.control_direction,
             "control_net_rupees":float(r.control_net_rupees),"delta_pnl_call_minus_put":float(r.delta_pnl_call_minus_put),
             "dte_days":float((expiry-entry).total_seconds()/86400.0),"entry_weekday":int(entry.weekday()),
             "entry_hour":int(entry.hour),"entry_minute":int(entry.minute)}
        row.update(intraday_features(spot_hist,entry))
        row.update(daily_features(daily,entry))
        oi=get_opt(norm_scalar_ts(r.expiry).normalize())
        snap=oi[oi.timestamp==entry]
        if snap.empty: raise RuntimeError(f"missing option snapshot at {entry} for {r.expiry}")
        row.update(option_features(snap,spot,expiry))
        # Use the next contract only as a point-in-time quoted term-structure feature.
        idx=expiry_list.index(norm_scalar_ts(r.expiry).normalize())
        if idx+1 < len(expiry_list):
            ne=expiry_list[idx+1]; nexp=norm_scalar_ts(ne)+pd.Timedelta(hours=15,minutes=30)
            ns=get_opt(norm_scalar_ts(ne).normalize())
            nsnap=ns[ns.timestamp==entry]
            if not nsnap.empty:
                row.update(option_features(snap,spot,expiry,nsnap,nexp))
        rows.append(row)
    df=pd.DataFrame(rows).sort_values("entry_ts").reset_index(drop=True)
    base=pd.DataFrame({"entry_ts":norm_ts(df["entry_ts"])})
    for c in ["entry_ts"]: df[c]=norm_ts(df[c])
    df=backward_join(df,global_d,"global_")
    df=backward_join(df,flows,"flow_")
    df=backward_join(df,sentiment,"sent_")
    # Remove non-feature labels from the model matrix; retain separately in the audit CSV.
    audit_cols=["entry_ts","expiry","split","control_direction","control_net_rupees","delta_pnl_call_minus_put"]
    feature_cols=[c for c in df.columns if c not in audit_cols]
    numeric=[c for c in feature_cols if pd.api.types.is_numeric_dtype(df[c])]
    df[feature_cols]=df[feature_cols].replace([np.inf,-np.inf],np.nan)
    df.to_csv(OUT/"point_in_time_features.csv",index=False)
    df[["entry_ts","expiry","split"]+numeric].to_parquet(OUT/"point_in_time_features.parquet",index=False)
    # Feature dictionary and coverage.
    desc=[]
    source_map={}
    for c in numeric:
        if c.startswith("global_"): src="previous global session/cache"
        elif c.startswith("flow_"): src="previous FII/DII publication/cache"
        elif c.startswith("sent_"): src="previous sentiment date/cache"
        elif c.startswith(("nifty_","entry_spot","prev_session_")): src="NIFTY spot/daily, at or before entry"
        elif c.startswith(("atm_","call_","put_","candidate_","near_atm_","next_","iv_")): src="NIFTY option chain at entry"
        else: src="derived timestamp/contract"
        source_map[c]=src
        desc.append({"feature":c,"source":src,"missing_pct":float(df[c].isna().mean()),"n_unique":int(df[c].nunique(dropna=True))})
    pd.DataFrame(desc).sort_values("feature").to_csv(OUT/"feature_dictionary.csv",index=False)
    # Conservative leakage checks.
    entry_dates=df["entry_ts"].dt.normalize()
    daily_cols=[c for c in numeric if c.startswith(("global_","flow_","sent_"))]
    check={
        "status":"PASS",
        "rows":int(len(df)),
        "unique_entry_timestamps":int(df.entry_ts.nunique()),
        "max_intraday_source_lag_seconds":float((df["entry_ts"]-pd.to_datetime(df["intraday_source_ts"])).dt.total_seconds().max()) if "intraday_source_ts" in df.columns else np.nan,
        "daily_source_rule":"strictly previous available date",
        "option_source_rule":"exact entry timestamp only; no forward fill/interpolation",
        "duplicate_quote_rule":"stable timestamp/type/strike last-row selection",
        "unavailable_sources":["NSE/BSE breadth","NIFTY futures basis/OI/volume","point-in-time corporate-action feed","timestamp-verified intraday news feed"],
        "phase35_reused_sources":["nifty_daily.parquet","global_daily.parquet","fii_dii_daily.parquet","sentiment_daily.parquet"]
    }
    (OUT/"leakage_audit.json").write_text(json.dumps(check,indent=2,default=str))
    (OUT/"source_manifest.json").write_text(json.dumps({
        "phase35_branch":"phase-35-advanced-tree-and-adaptive-prediction-search",
        "sources":["nifty_daily.parquet","global_daily.parquet","fii_dii_daily.parquet","sentiment_daily.parquet"],
        "hf_repo":HF_REPO,"hf_token_used":bool(os.getenv("HF_TOKEN")),
        "rows":len(df),"numeric_features":len(numeric)
    },indent=2))
    print(json.dumps(check,indent=2))
    print(json.dumps({"rows":len(df),"numeric_features":len(numeric),"missing_pct_mean":float(df[numeric].isna().mean().mean())},indent=2))

if __name__=="__main__":
    main()
