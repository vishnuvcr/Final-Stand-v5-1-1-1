#!/usr/bin/env python3
"""Phase 92: test lagged synthetic-forward proxy and CALL/PUT OI predictors beyond spot, VIX and IV.

All fitted models use the same complete-case rows; no data are imputed."""
from __future__ import annotations
import csv, io, json, math, os, sys, time, urllib.error, urllib.request
from datetime import date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

START=date(2022,1,1)
STOP=date(2023,1,1)  # non-inclusive API boundary; retain only 2022 timestamps
CACHE=Path(".cache/phase92/raw")
OUT=Path("results/phase92")
TOKEN=os.environ.get("DHAN_ACCESS_TOKEN","").strip()
IST=ZoneInfo("Asia/Kolkata")
REPO=os.environ.get("GITHUB_REPOSITORY","vishnuvcr/Final-Stand-v5-1-1")
RUN_ID=os.environ.get("GITHUB_RUN_ID","")
RUN_URL=f"https://github.com/{REPO}/actions/runs/{RUN_ID}" if RUN_ID else "(local run)"
FIELDS=("open","high","low","close","iv","volume","strike","oi","spot","timestamp")
SIDES=(("CALL","ce"),("PUT","pe"))
SPLITS=[("DEV",date(2022,1,1),date(2022,7,1)),
        ("VALIDATION",date(2022,7,1),date(2022,10,1)),
        ("CONFIRMATORY_OOS",date(2022,10,1),date(2023,1,1))]
BASE=["rv15_bps","rv60_bps","ret15_bps","ret60_bps","time_sin","time_cos"]
REGIME=BASE+["vix_level","vix_change15"]
IVMODEL=REGIME+["iv_mean"]
SYNTHMODEL=IVMODEL+["synthetic_gap_bps"]
FULLMODEL=SYNTHMODEL+["oi_imbalance"]
ISSUES=[]
COVERAGE=[]
VIX_COVERAGE=[]
QUALITY={}
MASTER={"status":"NOT_ATTEMPTED","candidate_count":0,"security_id_resolved":False}

def log(s): print(s,flush=True)
def fnum(x):
    try:
        x=float(x); return x if math.isfinite(x) else np.nan
    except (TypeError,ValueError): return np.nan
def fmt(x):
    try: return "NA" if x is None or not math.isfinite(float(x)) else f"{float(x):.4f}"
    except (TypeError,ValueError): return "NA"
def ts_parse(v):
    try:
        if isinstance(v,(int,float)) or (isinstance(v,str) and v.strip().replace(".","",1).isdigit()):
            n=float(v)
            t=pd.to_datetime(n,unit="ms" if abs(n)>1e12 else "s",utc=True,errors="coerce")
            if pd.isna(t): return pd.NaT
            return t.tz_convert(IST).tz_localize(None)
        t=pd.Timestamp(v)
        if pd.isna(t): return pd.NaT
        return t.tz_localize(IST).tz_localize(None) if t.tzinfo is None else t.tz_convert(IST).tz_localize(None)
    except Exception: return pd.NaT
def request(url,body=None,headers=None,timeout=22):
    data=None if body is None else json.dumps(body).encode()
    req=urllib.request.Request(url,data=data,headers=headers or {},method="GET" if body is None else "POST")
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r: return r.status,r.read()
    except urllib.error.HTTPError as e: return int(e.code),b""
    except Exception as e: return 0,type(e).__name__.encode()
def cachepath(kind,start,end,suffix=""):
    return CACHE/f"{kind}_{start.isoformat()}_{end.isoformat()}_{suffix.lower()}.json"

def options_chunk(start,end,side,key,allow_split=True):
    cp=cachepath("options",start,end,side)
    payload=None; status=0; hit=False; error=""
    if cp.exists():
        try:
            obj=json.loads(cp.read_text())
            if obj.get("http_status")==200 and isinstance(obj.get("payload"),dict):
                payload=obj["payload"]; status=200; hit=True
        except Exception: cp.unlink(missing_ok=True)
    if payload is None:
        if not TOKEN: error="MissingSecret"
        else:
            body={"exchangeSegment":"NSE_FNO","interval":"5","securityId":13,"instrument":"OPTIDX",
                  "expiryFlag":"MONTH","expiryCode":1,"strike":"ATM","drvOptionType":side,
                  "requiredData":["open","high","low","close","iv","volume","strike","oi","spot"],
                  "fromDate":start.isoformat(),"toDate":end.isoformat()}
            for attempt in range(3):
                status,raw=request("https://api.dhan.co/v2/charts/rollingoption",body,
                    {"access-token":TOKEN,"Accept":"application/json","Content-Type":"application/json"},timeout=22)
                if status==200:
                    try:
                        payload=json.loads(raw.decode("utf-8"))
                        cp.parent.mkdir(parents=True,exist_ok=True)
                        cp.write_text(json.dumps({"http_status":200,"payload":payload},separators=(",",":")))
                        break
                    except Exception as e: error=type(e).__name__; payload=None
                else: payload=None; error="TimeoutOrNetworkError" if status==0 else "HTTPError"
                if attempt<2: time.sleep(attempt+1)
    if payload is None:
        if allow_split and (end-start).days>7:
            mid=start+timedelta(days=(end-start).days//2)
            ISSUES.append(f"Options {start}–{end} {side}: initial window failed; retried as two smaller windows.")
            return options_chunk(start,mid,side,key,False)+options_chunk(mid,end,side,key,False)
        COVERAGE.append({"source":"options","from_date":start.isoformat(),"to_date_exclusive":end.isoformat(),
            "side":side,"http_status":status,"rows":0,"arrays_aligned":False,"cache_hit":hit,"valid":False,"error_class":error or "EmptyPayload"})
        ISSUES.append(f"Options {start}–{end} {side}: bounded retries failed ({error or 'EmptyPayload'}).")
        log(f"OPTIONS {start}/{end}/{side} status={status} rows=0 valid=false")
        return []
    data=payload.get("data",{}) if isinstance(payload,dict) else {}
    block=data.get(key) if isinstance(data,dict) else None
    block=block if isinstance(block,dict) else {}
    arrays=[block.get(k) for k in FIELDS]
    lengths=[len(x) for x in arrays if isinstance(x,list)]
    aligned=len(lengths)==len(FIELDS) and len(set(lengths))==1
    n=len(block.get("timestamp",[])) if isinstance(block.get("timestamp",[]),list) else 0
    valid=aligned and n>0
    COVERAGE.append({"source":"options","from_date":start.isoformat(),"to_date_exclusive":end.isoformat(),
        "side":side,"http_status":status,"rows":n,"arrays_aligned":aligned,"cache_hit":hit,"valid":valid,
        "error_class":"" if valid else "SchemaOrEmpty"})
    log(f"OPTIONS {start}/{end}/{side} status={status} rows={n} aligned={aligned} cache_hit={hit} valid={valid}")
    if not valid:
        ISSUES.append(f"Options {start}–{end} {side}: schema or array-alignment gate failed.")
        return []
    result=[]
    for i,t in enumerate(block["timestamp"]):
        stamp=ts_parse(t)
        if pd.isna(stamp) or stamp<pd.Timestamp(START) or stamp>=pd.Timestamp(STOP): continue
        row={"timestamp":stamp}
        for k in FIELDS[:-1]: row[k]=fnum(block[k][i])
        result.append(row)
    return result

def fetch_options(side,key):
    rows=[]; cursor=START
    while cursor<STOP:
        end=min(cursor+timedelta(days=14),STOP)
        rows.extend(options_chunk(cursor,end,side,key))
        cursor=end; time.sleep(.25)
    columns=["timestamp"]+[f"{side.lower()}_{k}" for k in FIELDS[:-1]]
    f=pd.DataFrame(rows)
    if f.empty: return pd.DataFrame(columns=columns)
    f=f.dropna(subset=["timestamp"]).sort_values("timestamp")
    QUALITY[f"{side.lower()}_duplicate_rows_removed"]=int(f.duplicated("timestamp",keep="last").sum())
    f=f.drop_duplicates("timestamp",keep="last")
    f=f.rename(columns={k:f"{side.lower()}_{k}" for k in FIELDS[:-1]})
    f=f[(f.timestamp>=pd.Timestamp(START))&(f.timestamp<pd.Timestamp(STOP))]
    return f[columns].reset_index(drop=True)

def fetch_master():
    p=CACHE/"dhan_instrument_master.csv"
    if p.exists() and p.stat().st_size>1000:
        return p.read_text(encoding="utf-8-sig",errors="replace")
    status,raw=request("https://images.dhan.co/api-data/api-scrip-master.csv",timeout=30)
    if status!=200 or not raw:
        MASTER.update({"status":"FETCH_FAILED","http_status":status})
        ISSUES.append("Dhan instrument master unavailable; India VIX ID not guessed.")
        return ""
    txt=raw.decode("utf-8-sig",errors="replace")
    p.write_text(txt)
    MASTER.update({"status":"FETCHED","http_status":status})
    return txt

def vix_id_from_master():
    txt=fetch_master()
    if not txt: return None
    try:
        rows=list(csv.DictReader(io.StringIO(txt)))
        if not rows: MASTER["status"]="EMPTY_MASTER"; return None
        cols=list(rows[0].keys())
        idcols=[c for c in cols if c and "SECURITY_ID" in c.upper()]
        excols=[c for c in cols if c and ("EXM_EXCH_ID" in c.upper() or c.upper()=="EXCHANGE")]
        icols=[c for c in cols if c and ("INSTRUMENT_NAME" in c.upper() or c.upper()=="INSTRUMENT")]
        sycols=[c for c in cols if c and "SYMBOL" in c.upper()]
        segcols=[c for c in cols if c and "SEGMENT" in c.upper()]
        cand={}
        for row in rows:
            label=" ".join(str(row.get(c,"") or "").upper() for c in sycols)
            if "INDIA VIX" not in label: continue
            exch=" ".join(str(row.get(c,"") or "").upper() for c in excols)
            ins=" ".join(str(row.get(c,"") or "").upper() for c in icols)
            seg=" ".join(str(row.get(c,"") or "").upper() for c in segcols)
            if exch and "NSE" not in exch: continue
            if "OPT" in ins or "FUT" in ins or "DERIVATIVE" in seg: continue
            sid=next((str(row[c]).strip() for c in idcols if row.get(c) not in (None,"")),None)
            if sid and ("INDEX" in ins or seg.strip() in ("I","IDX_I","INDEX")):
                cand[sid]={"security_id":sid,"instrument":ins,"segment":seg,"exchange":exch}
        MASTER.update({"candidate_count":len(cand),"candidate_ids":list(cand.keys())[:5]})
        if len(cand)!=1:
            MASTER["status"]="AMBIGUOUS_OR_MISSING"
            ISSUES.append(f"India VIX instrument-master search produced {len(cand)} eligible unique IDs; no ID guessed.")
            return None
        item=next(iter(cand.values()))
        MASTER.update({"status":"UNIQUE_MATCH","security_id_resolved":True,"instrument":item["instrument"],"segment":item["segment"]})
        return item["security_id"]
    except Exception as e:
        MASTER.update({"status":"PARSE_FAILED","error_class":type(e).__name__})
        ISSUES.append(f"India VIX instrument-master parse failed ({type(e).__name__}); no ID guessed.")
        return None

def vix_chunk(secid,start,end):
    cp=cachepath("vix",start,end,str(secid))
    payload=None; status=0; hit=False; error=""
    if cp.exists():
        try:
            obj=json.loads(cp.read_text())
            if obj.get("http_status")==200: payload=obj.get("payload"); status=200; hit=True
        except Exception: cp.unlink(missing_ok=True)
    if payload is None:
        if not TOKEN: error="MissingSecret"
        else:
            body={"securityId":str(secid),"exchangeSegment":"IDX_I","instrument":"INDEX","interval":"5","oi":False,
                "fromDate":f"{start.isoformat()} 09:15:00","toDate":f"{(end-timedelta(days=1)).isoformat()} 15:30:00"}
            for attempt in range(3):
                status,raw=request("https://api.dhan.co/v2/charts/intraday",body,
                    {"access-token":TOKEN,"Accept":"application/json","Content-Type":"application/json"},timeout=25)
                if status==200:
                    try:
                        payload=json.loads(raw.decode("utf-8"))
                        cp.parent.mkdir(parents=True,exist_ok=True)
                        cp.write_text(json.dumps({"http_status":200,"payload":payload},separators=(",",":")))
                        break
                    except Exception as e: error=type(e).__name__; payload=None
                else: payload=None; error="TimeoutOrNetworkError" if status==0 else "HTTPError"
                if attempt<2: time.sleep(attempt+1)
    d=payload if isinstance(payload,dict) else {}
    arrs=[d.get(k) for k in ("open","high","low","close","volume","timestamp")]
    lengths=[len(a) for a in arrs if isinstance(a,list)]
    aligned=len(lengths)==6 and len(set(lengths))==1
    n=len(d.get("timestamp",[])) if isinstance(d.get("timestamp",[]),list) else 0
    valid=status==200 and aligned and n>0
    VIX_COVERAGE.append({"source":"vix","from_date":start.isoformat(),"to_date_exclusive":end.isoformat(),
        "side":"","http_status":status,"rows":n,"arrays_aligned":aligned,"cache_hit":hit,"valid":valid,
        "error_class":"" if valid else (error or "SchemaOrEmpty")})
    log(f"VIX {start}/{end} status={status} rows={n} aligned={aligned} cache_hit={hit} valid={valid}")
    if not valid:
        ISSUES.append(f"India VIX {start}–{end}: bounded fetch/schema gate failed ({error or 'SchemaOrEmpty'}).")
        return []
    return [{"timestamp":t,"vix_level":fnum(d["close"][i])}
        for i,t0 in enumerate(d["timestamp"])
        if not pd.isna(t:=ts_parse(t0)) and pd.Timestamp(START)<=t<pd.Timestamp(STOP)]

def fetch_vix(secid):
    rows=[]; cursor=START
    while cursor<STOP:
        end=min(cursor+timedelta(days=80),STOP)
        rows.extend(vix_chunk(secid,cursor,end))
        cursor=end; time.sleep(.25)
    f=pd.DataFrame(rows)
    if f.empty: return f
    f=f.dropna(subset=["timestamp"]).sort_values("timestamp").drop_duplicates("timestamp",keep="last")
    return f[(f.timestamp>=pd.Timestamp(START))&(f.timestamp<pd.Timestamp(STOP))].reset_index(drop=True)

def build_panel(calls,puts,vix):
    if calls.empty or puts.empty: return pd.DataFrame()
    m=calls.merge(puts,on="timestamp",how="inner",validate="one_to_one")
    QUALITY["call_rows"]=int(len(calls)); QUALITY["put_rows"]=int(len(puts))
    QUALITY["paired_timestamps_before_checks"]=int(len(m))
    rel=(m.call_spot-m.put_spot).abs()/m[["call_spot","put_spot"]].abs().max(axis=1).replace(0,np.nan)
    bad=rel>0.0002
    QUALITY["spot_mismatch_excluded"]=int(bad.sum())
    m=m.loc[~bad].copy()
    same=np.isclose(m.call_strike,m.put_strike,rtol=0,atol=1e-9)
    QUALITY["strike_mismatch_excluded"]=int((~same).sum())
    m=m.loc[same].copy()
    m["spot"]=(m.call_spot+m.put_spot)/2
    m=m[(m.spot>0)&m.timestamp.notna()].sort_values("timestamp").reset_index(drop=True)
    if vix.empty: m["vix_level"]=np.nan
    else:
        m["session"]=m.timestamp.dt.strftime("%Y-%m-%d")
        vix=vix.copy(); vix["session"]=vix.timestamp.dt.strftime("%Y-%m-%d")
        parts=[]
        for sess,g in m.groupby("session",sort=True):
            vg=vix[vix.session==sess].sort_values("timestamp")
            g=g.sort_values("timestamp")
            if vg.empty: g=g.copy(); g["vix_level"]=np.nan
            else: g=pd.merge_asof(g,vg[["timestamp","vix_level"]],on="timestamp",direction="backward",
                                  tolerance=pd.Timedelta("5min"),suffixes=("","_vix"))
            parts.append(g)
        m=pd.concat(parts,ignore_index=True).sort_values("timestamp").reset_index(drop=True)
    m["session"]=m.timestamp.dt.strftime("%Y-%m-%d")
    panels=[]
    for sess,g in m.groupby("session",sort=True):
        g=g.sort_values("timestamp").copy().reset_index(drop=True)
        delta=g.timestamp.diff().dt.total_seconds()/60
        ret5=((g.spot/g.spot.shift(1)-1)*10000).where(delta==5)
        g["rv15_bps"]=ret5.abs().rolling(3,min_periods=3).sum()
        g["rv60_bps"]=ret5.abs().rolling(12,min_periods=12).sum()
        lag15=(g.timestamp-g.timestamp.shift(3)).dt.total_seconds()/60
        lag60=(g.timestamp-g.timestamp.shift(12)).dt.total_seconds()/60
        g["ret15_bps"]=((g.spot/g.spot.shift(3)-1)*10000).where(lag15==15)
        g["ret60_bps"]=((g.spot/g.spot.shift(12)-1)*10000).where(lag60==60)
        ahead=(g.timestamp.shift(-3)-g.timestamp).dt.total_seconds()/60
        g["target_abs15_bps"]=(((g.spot.shift(-3)/g.spot)-1)*10000).abs().where(ahead==15)
        minute=g.timestamp.dt.hour*60+g.timestamp.dt.minute-555
        g["time_sin"]=np.sin(2*np.pi*minute/375.0)
        g["time_cos"]=np.cos(2*np.pi*minute/375.0)
        # Dhan rolling-option timestamp is candle-start time. Lag option candle values
        # by one complete 5-minute row so close-derived premiums/OI/IV are available only
        # after the corresponding bar is finished.
        g["iv_mean_raw"]=(g.call_iv+g.put_iv)/2
        g["synthetic_forward_proxy_raw"]=g.call_strike+g.call_close-g.put_close
        g["synthetic_gap_raw_bps"]=((g.synthetic_forward_proxy_raw-g.spot)/g.spot)*10000
        oi_total=g.call_oi+g.put_oi
        g["oi_imbalance_raw"]=((g.call_oi-g.put_oi)/oi_total).where(oi_total>0)
        g["iv_mean"]=g.iv_mean_raw.shift(1)
        g["synthetic_gap_bps"]=g.synthetic_gap_raw_bps.shift(1)
        g["oi_imbalance"]=g.oi_imbalance_raw.shift(1)
        # VIX data are conservatively lagged one row as well.
        g["vix_level"]=g.vix_level.shift(1)
        vdiff=(g.timestamp-g.timestamp.shift(3)).dt.total_seconds()/60
        g["vix_change15"]=(g.vix_level/g.vix_level.shift(3)-1).where(vdiff==15)
        panels.append(g)
    p=pd.concat(panels,ignore_index=True).replace([np.inf,-np.inf],np.nan)
    QUALITY["paired_rows_after_checks"]=int(len(p))
    QUALITY["paired_sessions"]=int(p.session.nunique())
    QUALITY["vix_row_coverage"]=float(p.vix_level.notna().mean()) if len(p) else 0.0
    oos_mask=(p.timestamp>=pd.Timestamp("2022-10-01"))&(p.timestamp<pd.Timestamp("2023-01-01"))
    oos=p.loc[oos_mask]
    QUALITY["oos_vix_coverage"]=float(oos.vix_level.notna().mean()) if len(oos) else 0.0
    QUALITY["iv_mean_valid_share"]=float(p.iv_mean.notna().mean()) if len(p) else 0.0
    QUALITY["synthetic_gap_valid_share"]=float(p.synthetic_gap_bps.notna().mean()) if len(p) else 0.0
    QUALITY["oi_imbalance_valid_share"]=float(p.oi_imbalance.notna().mean()) if len(p) else 0.0
    return p

def fit_model(frame,features):
    x=frame[features].astype(float).to_numpy()
    y=frame.target_abs15_bps.astype(float).to_numpy()
    mu=x.mean(axis=0); sd=x.std(axis=0)
    sd=np.where(np.isfinite(sd)&(sd>1e-12),sd,1.0)
    coef=np.linalg.lstsq(np.column_stack([np.ones(len(x)),(x-mu)/sd]),y,rcond=None)[0]
    return {"features":features,"mu":mu,"sd":sd,"coef":coef}
def predict(model,frame):
    x=frame[model["features"]].astype(float).to_numpy()
    return np.maximum(0,np.column_stack([np.ones(len(x)),(x-model["mu"])/model["sd"]])@model["coef"])
def metrics(y,pred):
    y=np.asarray(y,float); pred=np.asarray(pred,float)
    denom=np.sum((y-y.mean())**2)
    return {"n":int(len(y)),"mae_bps":float(np.mean(np.abs(y-pred))),
        "rmse_bps":float(np.sqrt(np.mean((y-pred)**2))),
        "r2":float(1-np.sum((y-pred)**2)/denom) if denom>0 else None}
def bootstrap_delta(df,base_col,aug_col,seed=90210,nboot=5000):
    groups=[g for _,g in df.groupby("session",sort=True)]
    if len(groups)<2: return {"delta_mae_bps":None,"ci95_low":None,"ci95_high":None,"positive_share":None,"replicates":0,"seed":seed}
    rng=np.random.default_rng(seed); n=len(groups); vals=np.empty(nboot)
    for k in range(nboot):
        indexes=rng.integers(0,n,size=n)
        be=np.concatenate([np.abs(groups[i].target_abs15_bps.to_numpy()-groups[i][base_col].to_numpy()) for i in indexes])
        ae=np.concatenate([np.abs(groups[i].target_abs15_bps.to_numpy()-groups[i][aug_col].to_numpy()) for i in indexes])
        vals[k]=be.mean()-ae.mean()
    observed=float(np.mean(np.abs(df.target_abs15_bps-df[base_col]))-np.mean(np.abs(df.target_abs15_bps-df[aug_col])))
    lo,hi=np.quantile(vals,[.025,.975])
    return {"delta_mae_bps":observed,"ci95_low":float(lo),"ci95_high":float(hi),
        "positive_share":float(np.mean(vals>0)),"replicates":nboot,"seed":seed}
def save_csv(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore"); w.writeheader(); w.writerows(rows)
def publish(status,metrics_rows,primary,regime_rows,summary):
    OUT.mkdir(parents=True,exist_ok=True)
    coverage=COVERAGE+VIX_COVERAGE
    cov_fields=["source","from_date","to_date_exclusive","side","http_status","rows","arrays_aligned","cache_hit","valid","error_class"]
    save_csv(OUT/"coverage.csv",coverage,cov_fields)
    save_csv(OUT/"model_metrics.csv",metrics_rows,["split","model","features","n","sessions","mae_bps","rmse_bps","r2"])
    save_csv(OUT/"vix_regime_metrics.csv",regime_rows,["regime","n","sessions","mae_baseline_bps","mae_plus_features_bps","delta_mae_bps"])
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False)+"\n")
    issue_md="\n".join("- "+x for x in ISSUES) if ISSUES else "- No API/network/schema failures."
    table="\n".join(f"| {x['split']} | {x['model']} | {x.get('n',0)} | {x.get('sessions',0)} | {fmt(x.get('mae_bps'))} | {fmt(x.get('rmse_bps'))} | {fmt(x.get('r2'))} |" for x in metrics_rows)
    if primary.get("delta_mae_bps") is None:
        primary_text="Not estimable: data, predictor availability, or minimum-sample gate did not yield a valid matched comparison."
    else:
        primary_text=f"M2 MAE − M4 MAE = {fmt(primary['delta_mae_bps'])} bps (paired session-cluster bootstrap 95% CI {fmt(primary['ci95_low'])} to {fmt(primary['ci95_high'])}; bootstrap positive share {fmt(primary.get('positive_share'))}; {primary.get('replicates',0)} resamples; seed {primary.get('seed')})."
    m2_oos=next((x for x in metrics_rows if x["split"]=="CONFIRMATORY_OOS" and x["model"]=="M2_spot_VIX_plus_IV"),None)
    m4_oos=next((x for x in metrics_rows if x["split"]=="CONFIRMATORY_OOS" and x["model"]=="M4_add_synthetic_proxy_and_OI"),None)
    if m2_oos and m4_oos and m2_oos.get("mae_bps"):
        relative=100.0*(m2_oos["mae_bps"]-m4_oos["mae_bps"])/m2_oos["mae_bps"]
        effect_context=(f"OOS MAE changes from {fmt(m2_oos['mae_bps'])} to {fmt(m4_oos['mae_bps'])} bps, a {fmt(relative)}% relative reduction. RMSE changes by {fmt(m2_oos['rmse_bps']-m4_oos['rmse_bps'])} bps; R² moves from {fmt(m2_oos['r2'])} to {fmt(m4_oos['r2'])}. The confidence interval, not the point estimate alone, governs the registered conclusion.")
    else:
        effect_context="Effect-size context is not estimable because the matched baseline/full-feature OOS comparison is incomplete."
    regime_text="\n".join(f"- {x['regime']}: rows={x['n']}, sessions={x['sessions']}, M2 baseline MAE={fmt(x.get('mae_baseline_bps'))}, M4 full-feature MAE={fmt(x.get('mae_plus_features_bps'))}, delta={fmt(x.get('delta_mae_bps'))} bps." for x in regime_rows) if regime_rows else "- No descriptive regime groups estimable."
    report=f"""# Phase 92 Results — synthetic-forward proxy and CALL/PUT OI imbalance

Run: {RUN_URL}  
Status: **{status}**  
Sample: calendar 2022 only. Phase 90/91 cached payloads are not reused. The protected Phase 83 2026 holdout was not requested or loaded.

## Coverage and data-quality summary
- Options chunks valid: {sum(bool(x["valid"]) for x in COVERAGE)}/{len(COVERAGE)}.
- India VIX chunks valid: {sum(bool(x["valid"]) for x in VIX_COVERAGE)}/{len(VIX_COVERAGE)}.
- Instrument-master resolution: {MASTER.get("status")}; unique eligible India VIX IDs={MASTER.get("candidate_count",0)}.
- Paired option rows after spot/strike validation: {QUALITY.get("paired_rows_after_checks",0)} across {QUALITY.get("paired_sessions",0)} sessions.
- Mismatched spot rows excluded: {QUALITY.get("spot_mismatch_excluded",0)}; mismatched strike rows excluded: {QUALITY.get("strike_mismatch_excluded",0)}.
- Valid lagged IV coverage={fmt(QUALITY.get("iv_mean_valid_share"))}; synthetic-gap coverage={fmt(QUALITY.get("synthetic_gap_valid_share"))}; OI-imbalance coverage={fmt(QUALITY.get("oi_imbalance_valid_share"))}.
- Lagged VIX row coverage={fmt(QUALITY.get("vix_row_coverage"))}; OOS VIX coverage={fmt(QUALITY.get("oos_vix_coverage"))}.
- Complete OOS rows/sessions with the full predictor set: {summary.get("oos_n",0)}/{summary.get("oos_sessions",0)}.
- Minimum sample gate: {"PASS" if summary.get("sample_gate_pass") else "FAIL"}; India VIX gate: {"PASS" if summary.get("vix_gate_pass") else "FAIL"}.

## Frozen models
M0 = lagged spot realized movement, signed 15/60-minute returns and time-of-day terms.  
M1 = M0 + India VIX level and trailing 15-minute VIX change.  
M2 = M1 + mean ATM CALL/PUT IV.  
M3 = M2 + a lagged rolling-ATM synthetic-forward proxy gap, defined as (K + CALL close − PUT close − spot) / spot × 10,000 bps.  
M4 = M3 + lagged CALL/PUT OI imbalance, defined as (CALL OI − PUT OI) / (CALL OI + PUT OI), where the denominator is positive.

Option IV, close-derived synthetic proxy and OI features are lagged one full five-minute row to avoid using current-candle close/OI values before the candle is complete. VIX candles are conservatively lagged one row, too. The CALL and PUT strikes must match at the paired timestamp. All scaling and coefficients are fitted on DEV only; validation is report-only; predictions are clipped at zero. All compared models are scored on the same complete rows.

**Primary endpoint:** M2 MAE − M4 MAE. Positive values favour the combined synthetic-forward/OI feature block. The M2-to-M3 and M3-to-M4 differences are secondary descriptive model comparisons only; no separate subgroup significance tests are performed.

| Split | Model | N | Sessions | MAE (bps) | RMSE (bps) | R² |
|---|---|---:|---:|---:|---:|---:|
{table if table else "| — | — | 0 | 0 | NA | NA | NA |"}

## Primary result
{primary_text}

## Effect size
{effect_context}

Decision rule: claim added predictive value only if all data/sample gates pass and the entire 95% paired session-cluster bootstrap interval for M2 MAE − M4 MAE is above zero. An interval crossing zero does not establish a gain, and does not prove the features contain no information.

## Descriptive VIX regimes
VIX tertiles are determined on DEV data. The following are descriptive only and must not be used to select features or strategies:
{regime_text}

## API/data issues
{issue_md}

## Interpretation limits
This is a predictor study of absolute next-15-minute spot-return magnitude, not a direction classifier, strategy P&L study, or executable futures/option strategy. The synthetic-forward proxy is calculated from rolling ATM CALL/PUT bar closes; it is **not** a traded NIFTY futures price or an arbitrage signal. The endpoint does not provide exact listed-contract bid/ask/depth, transaction latency, or executable fills. No direct historical FUTIDX basis is claimed, no strategy P&L is computed, and no strategy is promoted. Any later rule-level replay requires authorized exact-contract data and Paytm Money brokerage, statutory levies, spread, adverse slippage, latency and stress costs.
"""
    (OUT/"PHASE92_RESULTS.md").write_text(report)
    status_md=f"""# Phase 92 Status

Date: 2026-10-10  
Status: **{status}**  
Latest workflow run: [{RUN_ID}]({RUN_URL})  
Strategy promotion: **NONE**.

- [Research plan](PHASE92_RESEARCH_PLAN.md)
- [Error log](PHASE92_ERROR_LOG.md)
- [Auditable chat/decision log](PHASE92_CHAT_LOG.md)
- [Engine](research/phase92/synthetic_forward_oi_study.py)
- [Phase branch workflow](.github/workflows/phase92-synthetic-forward-oi-2022.yml)
- [Default-branch runner + manual dispatch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/main/.github/workflows/phase92-pr-runner.yml)
- [Detailed results](results/phase92/PHASE92_RESULTS.md)
- [Summary JSON](results/phase92/summary.json)
- [Coverage ledger](results/phase92/coverage.csv)
- [Model metrics](results/phase92/model_metrics.csv)
- [Descriptive VIX-regime metrics](results/phase92/vix_regime_metrics.csv)

## Primary conclusion
{primary_text}

Complete OOS rows/sessions: {summary.get("oos_n",0)}/{summary.get("oos_sessions",0)}. Sample gate={"PASS" if summary.get("sample_gate_pass") else "FAIL"}; VIX gate={"PASS" if summary.get("vix_gate_pass") else "FAIL"}. The Phase 83 2026 holdout remains sealed.
"""
    Path("PHASE92_STATUS.md").write_text(status_md)
    import re
    ep=Path("PHASE92_ERROR_LOG.md"); old=ep.read_text() if ep.exists() else "# Phase 92 Error Log\n"
    runtime=f"""<!-- PHASE92_RUNTIME_START -->
## Runtime summary — {RUN_ID or 'local'}
- Status: {status}
- Options valid chunks: {sum(bool(x["valid"]) for x in COVERAGE)}/{len(COVERAGE)}
- VIX valid chunks: {sum(bool(x["valid"]) for x in VIX_COVERAGE)}/{len(VIX_COVERAGE)}
- Instrument master: {MASTER.get("status")}; candidate count={MASTER.get("candidate_count",0)}
- Paired rows: {QUALITY.get("paired_rows_after_checks",0)}; spot mismatches={QUALITY.get("spot_mismatch_excluded",0)}; strike mismatches={QUALITY.get("strike_mismatch_excluded",0)}
- OOS rows/sessions: {summary.get("oos_n",0)}/{summary.get("oos_sessions",0)}
- Primary result: {primary_text}
- Issues:
{issue_md}
- No token, raw response, row-level price, or hidden reasoning is logged.
<!-- PHASE92_RUNTIME_END -->"""
    if "<!-- PHASE92_RUNTIME_START -->" in old: old=re.sub(r"<!-- PHASE92_RUNTIME_START -->.*?<!-- PHASE92_RUNTIME_END -->",runtime,old,flags=re.S)
    else: old=old.rstrip()+"\n\n"+runtime+"\n"
    ep.write_text(old)
    cp=Path("PHASE92_CHAT_LOG.md"); old=cp.read_text() if cp.exists() else "# Phase 92 Chat / Decision Log\n"
    chat=f"""<!-- PHASE92_RUNTIME_START -->
## Automated execution record — {RUN_ID or 'local'}
- Workflow: {RUN_URL}
- Status: {status}
- VIX ID resolved dynamically: {MASTER.get("security_id_resolved",False)}
- Options valid chunks={sum(bool(x["valid"]) for x in COVERAGE)}/{len(COVERAGE)}; VIX valid chunks={sum(bool(x["valid"]) for x in VIX_COVERAGE)}/{len(VIX_COVERAGE)}
- OOS rows/sessions={summary.get("oos_n",0)}/{summary.get("oos_sessions",0)}
- Primary result: {primary_text}
- Option-derived close/IV/OI features were lagged one full five-minute row; no raw market responses were printed, committed, or uploaded as artifacts.
- Phase 83's 2026 holdout was not requested.
<!-- PHASE92_RUNTIME_END -->"""
    if "<!-- PHASE92_RUNTIME_START -->" in old: old=re.sub(r"<!-- PHASE92_RUNTIME_START -->.*?<!-- PHASE92_RUNTIME_END -->",chat,old,flags=re.S)
    else: old=old.rstrip()+"\n\n"+chat+"\n"
    cp.write_text(old)
    readme=Path("README.md").read_text() if Path("README.md").exists() else "# Final Stand v5 1-1-1\n"
    block=f"""<!-- PHASE92_START -->
# Resume checkpoint — Phase 92 synthetic-forward proxy and OI study

**Status: {status}.** Automated run [{RUN_ID}]({RUN_URL}). This fixed 2022 sample tests whether lagged rolling-ATM synthetic-forward gap and CALL/PUT OI imbalance improve next-15-minute absolute NIFTY spot-move prediction beyond spot, India VIX and IV. The protected 2026 holdout was not requested or loaded.

- [Phase 92 plan](PHASE92_RESEARCH_PLAN.md)
- [Phase 92 status](PHASE92_STATUS.md)
- [Phase 92 error log](PHASE92_ERROR_LOG.md)
- [Phase 92 auditable chat log](PHASE92_CHAT_LOG.md)
- [Detailed results](results/phase92/PHASE92_RESULTS.md)
- [Cross-feature model metrics](results/phase92/model_metrics.csv)
- [Coverage ledger](results/phase92/coverage.csv)
- [Summary JSON](results/phase92/summary.json)
- [Analysis engine](research/phase92/synthetic_forward_oi_study.py)
- [Phase branch workflow](.github/workflows/phase92-synthetic-forward-oi-2022.yml)
- [Default-branch PR runner + manual dispatch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/main/.github/workflows/phase92-pr-runner.yml)

**Interpretation boundary:** predictor association is not strategy profitability. The synthetic-forward proxy is not actual traded futures price; rolling options do not provide exact-contract bid/ask/depth or fills. No strategy is promoted.
<!-- PHASE92_END -->"""
    if "<!-- PHASE92_START -->" in readme: readme=re.sub(r"<!-- PHASE92_START -->.*?<!-- PHASE92_END -->\n*","",readme,flags=re.S)
    Path("README.md").write_text(block+"\n\n"+readme.lstrip())

def main():
    CACHE.mkdir(parents=True,exist_ok=True); OUT.mkdir(parents=True,exist_ok=True)
    if not TOKEN:
        ISSUES.append("DHAN_ACCESS_TOKEN missing; no authenticated market-data requests were sent.")
        summary={"oos_n":0,"oos_sessions":0,"sample_gate_pass":False,"vix_gate_pass":False}
        status="BLOCKED — secret missing; no data request sent"
        publish(status,[],{"delta_mae_bps":None},[],summary)
        return 2
    calls=fetch_options("CALL","ce"); puts=fetch_options("PUT","pe")
    vid=vix_id_from_master()
    vix=fetch_vix(vid) if vid else pd.DataFrame()
    if vid and vix.empty: ISSUES.append("India VIX ID resolved but no usable 2022 bars returned.")
    panel=build_panel(calls,puts,vix) if not calls.empty and not puts.empty else pd.DataFrame()
    model_rows=[]; regime_rows=[]; primary={"delta_mae_bps":None}
    summary={"oos_n":0,"oos_sessions":0,"sample_gate_pass":False,"vix_gate_pass":False}
    status="INCONCLUSIVE — no sufficiently complete paired option panel"
    if not panel.empty:
        panel["split"]="OUTSIDE"
        for name,a,z in SPLITS:
            panel.loc[(panel.timestamp>=pd.Timestamp(a))&(panel.timestamp<pd.Timestamp(z)),"split"]=name
        needed=FULLMODEL+["target_abs15_bps"]
        clean=panel.replace([np.inf,-np.inf],np.nan)
        dev=clean[clean.split=="DEV"].dropna(subset=needed).copy()
        val=clean[clean.split=="VALIDATION"].dropna(subset=needed).copy()
        oos=clean[clean.split=="CONFIRMATORY_OOS"].dropna(subset=needed).copy()
        summary.update({"paired_rows":int(len(panel)),"paired_sessions":int(panel.session.nunique()),
            "dev_complete_rows":int(len(dev)),"validation_complete_rows":int(len(val)),
            "oos_complete_rows":int(len(oos)),"oos_n":int(len(oos)),
            "oos_sessions":int(oos.session.nunique()) if len(oos) else 0})
        vixgate=bool(MASTER.get("security_id_resolved") and QUALITY.get("oos_vix_coverage",0)>=.80 and len(oos)>0)
        samplegate=bool(len(oos)>=1000 and oos.session.nunique()>=30)
        train_gate=bool(len(dev)>=1000 and len(val)>=100)
        summary["vix_gate_pass"]=vixgate; summary["sample_gate_pass"]=samplegate; summary["training_gate_pass"]=train_gate
        if train_gate and len(oos)>0:
            specs=[
                ("M0_spot_only",BASE),
                ("M1_spot_plus_VIX",REGIME),
                ("M2_spot_VIX_plus_IV",IVMODEL),
                ("M3_add_synthetic_forward_proxy",SYNTHMODEL),
                ("M4_add_synthetic_proxy_and_OI",FULLMODEL)]
            fitted={}
            for name,features in specs:
                model=fit_model(dev,features); fitted[name]=model
                for split,frame in (("VALIDATION",val),("CONFIRMATORY_OOS",oos)):
                    mm=metrics(frame.target_abs15_bps,predict(model,frame))
                    model_rows.append({"split":split,"model":name,"features":";".join(features),**mm,"sessions":int(frame.session.nunique())})
            oos=oos.copy()
            oos["pred_m2"]=predict(fitted["M2_spot_VIX_plus_IV"],oos)
            oos["pred_m3"]=predict(fitted["M3_add_synthetic_forward_proxy"],oos)
            oos["pred_m4"]=predict(fitted["M4_add_synthetic_proxy_and_OI"],oos)
            primary=bootstrap_delta(oos,"pred_m2","pred_m4")
            q=np.quantile(dev.vix_level.dropna().to_numpy(),[1/3,2/3])
            oos["vix_regime"]=np.where(oos.vix_level<=q[0],"LOW_VIX",np.where(oos.vix_level<=q[1],"MID_VIX","HIGH_VIX"))
            for regime,g in oos.groupby("vix_regime",sort=True):
                b=metrics(g.target_abs15_bps,g.pred_m2)["mae_bps"]
                a=metrics(g.target_abs15_bps,g.pred_m4)["mae_bps"]
                regime_rows.append({"regime":regime,"n":len(g),"sessions":int(g.session.nunique()),
                    "mae_baseline_bps":b,"mae_plus_features_bps":a,"delta_mae_bps":b-a})
        if not vixgate:
            status="INCONCLUSIVE — India VIX ID/join coverage gate failed"
        elif not samplegate:
            status="INCONCLUSIVE — confirmatory OOS sample gate failed"
        elif not train_gate:
            status="INCONCLUSIVE — DEV/validation training sample gate failed"
        elif primary.get("ci95_low") is not None and primary["ci95_low"]>0:
            status="PASS — lagged synthetic-forward/OI feature block adds OOS magnitude-prediction value; not strategy evidence"
        else:
            status="NO INCREMENTAL GAIN ESTABLISHED — primary bootstrap interval includes or falls below zero"
    summary.update({"phase":92,"run_url":RUN_URL,"status":status,
        "requested_period":["2022-01-01","2023-01-01_exclusive"],
        "holdout_2026_requested":False,"instrument_master":MASTER,"quality":QUALITY,
        "options_chunks_valid":sum(bool(x["valid"]) for x in COVERAGE),"options_chunks_total":len(COVERAGE),
        "vix_chunks_valid":sum(bool(x["valid"]) for x in VIX_COVERAGE),"vix_chunks_total":len(VIX_COVERAGE),
        "primary":primary,"issue_count":len(ISSUES),
        "primary_comparison":"M2_spot_VIX_plus_IV versus M4_add_synthetic_proxy_and_OI",
        "features_lagged_one_full_five_minute_row":True})
    publish(status,model_rows,primary,regime_rows,summary)
    log(f"PHASE92_STATUS={status}")
    log(f"OPTIONS_VALID={sum(bool(x['valid']) for x in COVERAGE)}/{len(COVERAGE)}")
    log(f"VIX_VALID={sum(bool(x['valid']) for x in VIX_COVERAGE)}/{len(VIX_COVERAGE)}")
    log(f"VIX_ID_RESOLVED={MASTER.get('security_id_resolved',False)}")
    log(f"OOS_ROWS={summary.get('oos_n',0)}")
    log(f"OOS_SESSIONS={summary.get('oos_sessions',0)}")
    log(f"PRIMARY_DELTA_MAE_BPS={fmt(primary.get('delta_mae_bps'))}")
    log("RAW_PAYLOADS_PRINTED_OR_COMMITTED=false")
    log("PHASE83_2026_HOLDOUT_REQUESTED_OR_LOADED=false")
    return 0

if __name__=="__main__":
    sys.exit(main())
