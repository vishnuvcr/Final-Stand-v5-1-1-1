#!/usr/bin/env python3
"""Deterministic, resumable EOD options grid evaluator for Phase 109.

This runner is deliberately strict:
* only exact-contract option prices from the official NSE daily archives are fills;
* only P&L dates supported by the canonical dated transaction cost model are eligible;
* zero-volume, missing, unmatched, expired and invalid-price contracts are excluded;
* unsupported signal architectures and unverified feature sources are BLOCKED, not proxied;
* EOD high/low stop-target ambiguity is resolved stop-first and recorded as a proxy;
* each registered config is evaluated once for its gross trade tape, then all 24 cost cases.
Full raw history and per-contract trades remain private in Actions cache. Public shard rows
are per-configuration/per-cost summary statistics, not raw quote data.
"""
from __future__ import annotations

import argparse, csv, gzip, hashlib, importlib.util, inspect, io, json, math, os, re, sys, time, zipfile
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from itertools import product
from pathlib import Path
from statistics import median

ROOT=Path(".")
OUT=Path("results/phase109")
CACHE=Path("data/cache/phase109")
OPTION_CACHE=CACHE/"nse_eod"
CONTEXT_CACHE=CACHE/"niftyindices_history"
MODEL_GREEKS_CACHE=CACHE/"options_model_greeks"
FUTURES_CACHE=CACHE/"futures_eod"
FIRST_COST_DATE=date(2024,10,1)
ENGINE_VERSION="phase109-eod-engine-v3-context-coverage"
# Exact registered core IDs only. Unimplemented architectures are blocked, never proxied.
SUPPORTED_CORE_METHODS={
 "ROC_MOMENTUM","EMA_CROSS","EMA_SLOPE","RETURN_ZSCORE_FADE",
 "RSI_REBOUND","BOLLINGER_REVERSION","EMA_DEVIATION_FADE","RELATIVE_STRENGTH",
}
# Cross-asset/basis/flow confirmation schemas other than the audited daily chain flow
# are intentionally blocked until their own point-in-time feature pipeline exists.
SUPPORTED_CONFIRMS={"NONE","OPTIONS_FLOW"}
# REALIZED_VOL_LOW_HIGH has no registered target-state axis; block until preregistered.
SUPPORTED_REGIMES={"NONE","TREND_RANGE","INDIA_VIX"}
INDEX_SYMBOLS={"NIFTY","BANKNIFTY"}
COST_MODEL_PATH=ROOT/"research/phase104_eod_stock_options/cost_model.py"


def canonical(value):
    return str(value or "").strip().upper().replace("-","_").replace(" ","_").replace("/","_")


def read_csv(path):
    p=Path(path)
    if not p.exists(): return []
    with p.open(newline="",encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def read_json(path,default=None):
    p=Path(path)
    if not p.exists(): return default if default is not None else {}
    return json.loads(p.read_text(encoding="utf-8"))


def shard_result_filename(sample,shard):
    """Include the engine version in result filenames to preserve old-engine evidence."""
    sample_tag="holdout" if sample=="holdout" else "eval"
    engine_tag=ENGINE_VERSION.replace("phase109-eod-engine-","").replace("-","_")
    return f"phase109_{sample_tag}_{engine_tag}_{shard}.csv.gz"


def parse_date(value):
    s=str(value or "").strip()
    for fmt in ("%Y-%m-%d","%d-%b-%Y","%d-%B-%Y","%d/%m/%Y","%d%m%Y","%Y%m%d","%d %b %Y"):
        try: return datetime.strptime(s[:10] if fmt=="%Y-%m-%d" else s,fmt).date()
        except ValueError: pass
    return None


def number(value):
    try:
        v=float(str(value).strip())
        return v if math.isfinite(v) else None
    except (ValueError,TypeError,OverflowError): return None


def value(row,*names,default=""):
    for name in names:
        if row.get(name) not in (None,""): return row[name]
    return default


def json_field(row,*names,default=None):
    raw=value(row,*names)
    if isinstance(raw,(dict,list)): return raw
    try: return json.loads(raw) if raw else (default if default is not None else {})
    except Exception: return default if default is not None else {}


def load_cost_model():
    if not COST_MODEL_PATH.exists():
        raise RuntimeError("Canonical Phase 104 cost model is missing; no net performance may be scored.")
    spec=importlib.util.spec_from_file_location("phase104_cost_model",COST_MODEL_PATH)
    module=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def find_cost_function(module):
    preferred=("round_trip_cost","calculate_round_trip_cost","compute_round_trip_cost","estimate_round_trip_cost","calculate_trade_cost")
    for name in preferred:
        fn=getattr(module,name,None)
        if callable(fn): return name,fn
    candidates=[(n,v) for n,v in vars(module).items() if callable(v) and not n.startswith("_") and "cost" in n.lower()]
    if len(candidates)==1: return candidates[0]
    return None,None


def call_cost_model(module,trade_date,buy_price,sell_price,quantity,brokerage_per_order,fee_multiplier):
    """Adapt by parameter names to the canonical model; fail closed if its API is unknown."""
    name,fn=find_cost_function(module)
    if fn is None:
        raise RuntimeError("Canonical cost model has no uniquely identifiable round-trip cost callable; evaluator fails closed.")
    try:
        sig=inspect.signature(fn)
        params=sig.parameters
        kwargs={}
        brokerage_names={"brokerage_per_order","brokerage_rupees_per_order","brokerage_per_trade","brokerage"}
        has_var_kwargs=any(p.kind==inspect.Parameter.VAR_KEYWORD for p in params.values())
        if not has_var_kwargs and not brokerage_names.intersection(params):
            raise RuntimeError("Canonical dated cost model exposes no configurable brokerage input; refusing to score the ₹10/₹15/₹20 scenarios.")
        aliases={
          "trade_date":trade_date.isoformat(),"date":trade_date.isoformat(),"session_date":trade_date.isoformat(),
          "entry_date":trade_date.isoformat(),"buy_date":trade_date.isoformat(),
          "entry_price":buy_price,"buy_price":buy_price,"buy_premium":buy_price,"entry_premium":buy_price,
          "exit_price":sell_price,"sell_price":sell_price,"sell_premium":sell_price,"exit_premium":sell_price,
          "quantity":quantity,"qty":quantity,"lot_size":quantity,"contracts":quantity,"units":quantity,
          "brokerage_per_order":brokerage_per_order,"brokerage_per_trade":brokerage_per_order,
          "brokerage":brokerage_per_order,"fee_multiplier":fee_multiplier,"fees_multiplier":fee_multiplier,
          "option_type":"OPTION","instrument":"OPTIDX","side":"ROUND_TRIP",
        }
        unknown_required=[]
        for p in params.values():
            if p.kind in (inspect.Parameter.VAR_POSITIONAL,inspect.Parameter.VAR_KEYWORD): continue
            if p.name in aliases: kwargs[p.name]=aliases[p.name]
            elif p.default is inspect.Parameter.empty:
                unknown_required.append(p.name)
        if unknown_required:
            raise RuntimeError("Unmapped required canonical cost-model parameters: "+",".join(unknown_required))
        result=fn(**kwargs)
    except TypeError as exc:
        raise RuntimeError(f"Canonical cost model call failed for {name}: {exc}") from exc
    if isinstance(result,(int,float)):
        base=max(0.0,float(result))
        return base*fee_multiplier,{"total_cost":base*fee_multiplier,"unscaled_modeled_cost":base,"fee_multiplier_applied_after_model":fee_multiplier,"model_callable":name,"breakdown":"numeric_return"}
    if isinstance(result,dict):
        flat={canonical(k).lower():v for k,v in result.items()}
        candidates=("total_cost","total_fees","total_reported_fees","round_trip_cost","total_charges","grand_total")
        found=None
        for k in candidates:
            if k in flat:
                found=number(flat[k])
                if found is not None: break
        if found is None:
            numeric_parts=[number(v) for v in result.values() if isinstance(v,(int,float))]
            if len(numeric_parts)==1: found=numeric_parts[0]
        if found is None:
            raise RuntimeError("Canonical cost model result lacks a recognized numeric total; keys="+",".join(map(str,result.keys())))
        return max(0.0,found)*fee_multiplier,{"total_cost":max(0.0,found)*fee_multiplier,"unscaled_modeled_cost":found,"fee_multiplier_applied_after_model":fee_multiplier,"model_callable":name,"breakdown":json.dumps(result,sort_keys=True,default=str)}
    raise RuntimeError(f"Canonical cost model returned unsupported result type: {type(result).__name__}")


def normalize_family(row):
    family_id=value(row,"family_id","family_key","id")
    core=canonical(value(row,"core_id","core","signal_core","core_name"))
    confirm=canonical(value(row,"confirmation_id","confirmation","confirm_id"))
    regime=canonical(value(row,"regime_id","regime","regime_gate"))
    desc=value(row,"family_name","name","label",default=family_id)
    required=json_field(row,"required_inputs_json","required_inputs",default=[])
    if not isinstance(required,list): required=[]
    return {"family_id":family_id,"family_name":desc,"core":core,"confirmation":confirm,"regime":regime,"required_inputs":required,"raw":row}


def is_trend_method(method):
    return method in {"ROC_MOMENTUM","EMA_CROSS","EMA_SLOPE","RELATIVE_STRENGTH"}


def is_mean_reversion_method(method):
    return method in {"RETURN_ZSCORE_FADE","RSI_REBOUND",
                      "BOLLINGER_REVERSION","EMA_DEVIATION_FADE"}


def core_method(core):
    """Return a method only for an exact registered ID with a coded implementation."""
    normalized=canonical(core)
    return normalized if normalized in SUPPORTED_CORE_METHODS else None


def read_archive(path,expected_date):
    with zipfile.ZipFile(path) as z:
        members=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(members)!=1: raise ValueError("ARCHIVE_CSV_MEMBER_COUNT_"+str(len(members)))
        raw=z.read(members[0])
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    fields=reader.fieldnames or []
    udiff=any(k in fields for k in ("FinInstrmTp","TckrSymb","OptnTp"))
    aliases={
      "instrument":("FinInstrmTp",) if udiff else ("INSTRUMENT",),
      "symbol":("TckrSymb",) if udiff else ("SYMBOL",),
      "date":("BizDt","TradDt") if udiff else ("TIMESTAMP",),
      "expiry":("FininstrmActlXpryDt","XpryDt") if udiff else ("EXPIRY_DT",),
      "strike":("StrkPric",) if udiff else ("STRIKE_PR",),
      "side":("OptnTp",) if udiff else ("OPTION_TYP",),
      "open":("OpnPric",) if udiff else ("OPEN",),
      "high":("HghPric",) if udiff else ("HIGH",),
      "low":("LwPric",) if udiff else ("LOW",),
      "close":("ClsPric",) if udiff else ("CLOSE",),
      "volume":("TtlTradgVol",) if udiff else ("CONTRACTS",),
      "oi":("OpnIntrst",) if udiff else ("OPEN_INT",),
      "lot":("NewBrdLotQty",) if udiff else ("BOARD_LOT",),
      "spot":("UndrlygPric",) if udiff else (),
    }
    result=[]
    for row in reader:
        sym=str(value(row,*aliases["symbol"])).strip().upper()
        inst=str(value(row,*aliases["instrument"])).strip().upper()
        if sym not in INDEX_SYMBOLS: continue
        # NSE UDiFF uses IDO/IDF; normalize to evaluator's canonical names.
        if udiff:
            if inst=="IDO": inst="OPTIDX"
            elif inst=="IDF": inst="FUTIDX"
        if inst not in {"OPTIDX","FUTIDX"}: continue
        record={"date":expected_date.isoformat(),"symbol":sym,"instrument":inst,
          "expiry":parse_date(value(row,*aliases["expiry"])),"strike":number(value(row,*aliases["strike"])),
          "side":str(value(row,*aliases["side"])).strip().upper(),
          "open":number(value(row,*aliases["open"])),"high":number(value(row,*aliases["high"])),
          "low":number(value(row,*aliases["low"])),"close":number(value(row,*aliases["close"])),
          "volume":number(value(row,*aliases["volume"])),"oi":number(value(row,*aliases["oi"])),
          "lot":number(value(row,*aliases["lot"])),"spot":number(value(row,*aliases["spot"])) if aliases["spot"] else None}
        if inst=="OPTIDX" and record["side"] in {"CE","PE"} and record["strike"] and record["expiry"]:
            result.append(record)
    return result


def read_vix_cache():
    out={}
    if not CONTEXT_CACHE.exists(): return out
    for p in CONTEXT_CACHE.glob("*.json"):
        try:
            obj=json.loads(p.read_text(encoding="utf-8"))
            if obj.get("kind")!="INDIA_VIX": continue
            for row in obj.get("rows",[]):
                d=parse_date(row.get("date"))
                close=number(row.get("close"))
                if d and close and close>0: out[d]=close
        except Exception: continue
    return out


def read_index_closes():
    out=defaultdict(dict)
    if not CONTEXT_CACHE.exists(): return out
    for p in CONTEXT_CACHE.glob("*.json"):
        try:
            obj=json.loads(p.read_text(encoding="utf-8"))
            name=canonical(obj.get("index_name",""))
            if name not in {"NIFTY_50","NIFTY_BANK"}: continue
            sym="NIFTY" if name=="NIFTY_50" else "BANKNIFTY"
            for row in obj.get("rows",[]):
                d=parse_date(row.get("HistoricalDate") or row.get("date"))
                close=number(row.get("CLOSE") or row.get("close"))
                if d and close and close>0: out[sym][d]=close
        except Exception: continue
    return out


def validate_context_coverage(dates,vix_by_date,index_closes):
    """Fail closed when the official index/VIX history is materially truncated."""
    if not dates:
        raise RuntimeError("OFFICIAL_CONTEXT_COVERAGE_GATE_FAILED: no market dates available.")
    start=min(dates)
    end_exclusive=max(dates)+timedelta(days=1)
    weekday_count=sum(
        1 for offset in range((end_exclusive-start).days)
        if (start+timedelta(days=offset)).weekday()<5
    )
    minimum=max(1,math.ceil(weekday_count*0.90))
    observed={
        "INDIA_VIX":len(vix_by_date),
        "NIFTY 50":len(index_closes.get("NIFTY",{})),
        "NIFTY BANK":len(index_closes.get("BANKNIFTY",{})),
    }
    missing={name:count for name,count in observed.items() if count<minimum}
    report={
        "window_start":start.isoformat(),
        "window_end_inclusive":max(dates).isoformat(),
        "expected_weekdays":weekday_count,
        "minimum_unique_dates_per_series":minimum,
        "coverage_ratio_threshold":0.90,
        "observed_unique_dates":observed,
        "coverage_pass":not missing,
    }
    if missing:
        raise RuntimeError(
            "OFFICIAL_CONTEXT_COVERAGE_GATE_FAILED: need at least "
            +str(minimum)+" unique dates per official VIX/index series over "
            +start.isoformat()+"–"+max(dates).isoformat()
            +"; observed "+json.dumps(observed,sort_keys=True)
            +". No strategy configurations were scored."
        )
    return report


def ema(values,period,end):
    if period<1 or end<period-1: return None
    alpha=2/(period+1)
    current=values[end-period+1]
    for x in values[end-period+2:end+1]:
        if x is None: continue
        current=alpha*x+(1-alpha)*current
    return current


def rsi(values,end,period):
    if end<period: return None
    ups=downs=0.0
    for i in range(end-period+1,end+1):
        if values[i] is None or values[i-1] is None: continue
        delta=values[i]-values[i-1]
        if delta>0: ups+=delta
        elif delta<0: downs-=delta
    if ups+downs<=0: return 50.0
    if downs==0: return 100.0
    rs=(ups/period)/(downs/period)
    return 100.0-100.0/(1.0+rs)


def mean_sd(values):
    if not values: return None,None
    m=sum(values)/len(values)
    v=sum((x-m)**2 for x in values)/len(values)
    return m,math.sqrt(max(0,v))


def compute_signal(method,values,idx,lookback,threshold,params=None):
    params=params or {}
    if idx<max(lookback,3): return 0
    now=values[idx]
    past=values[idx-lookback]
    if now is None or past is None or not now or not past or past<=0: return 0
    change_pct=(now/past-1.0)*100.0
    thr=float(threshold)
    if method=="ROC_MOMENTUM":
        if change_pct>=thr:return 1
        if change_pct<=-thr:return -1
        return 0
    if method=="EMA_SLOPE":
        current=ema(values,lookback,idx)
        previous=ema(values,lookback,idx-1)
        if current is None or previous is None or previous<=0:return 0
        slope=(current/previous-1.0)*100.0
        if slope>=thr:return 1
        if slope<=-thr:return -1
        return 0
    if method=="EMA_CROSS":
        fast=max(2,lookback//2)
        fast_now,slow_now=ema(values,fast,idx),ema(values,lookback,idx)
        fast_prev,slow_prev=ema(values,fast,idx-1),ema(values,lookback,idx-1)
        if None in (fast_now,slow_now,fast_prev,slow_prev) or slow_now<=0 or slow_prev<=0:return 0
        spread_now=(fast_now/slow_now-1.0)*100.0
        spread_prev=(fast_prev/slow_prev-1.0)*100.0
        if spread_prev<=0 and spread_now>=thr/2.0:return 1
        if spread_prev>=0 and spread_now<=-thr/2.0:return -1
        return 0
    if method in {"RETURN_ZSCORE_FADE","RETURN_ZSCORE_MEAN_REVERSION"}:
        window=[values[j]/values[j-1]-1 for j in range(max(1,idx-lookback+1),idx+1) if values[j] is not None and values[j-1] is not None and values[j-1]>0]
        m,sd=mean_sd(window)
        if sd is None or sd<=1e-10:return 0
        z=(values[idx]/values[idx-1]-1-m)/sd
        if z>=thr:return -1
        if z<=-thr:return 1
        return 0
    if method in {"RSI_REBOUND"}:
        x=rsi(values,idx,lookback)
        if x is None:return 0
        if x<=max(5,30-thr*5): return 1
        if x>=min(95,70+thr*5): return -1
        return 0
    if method in {"BOLLINGER_REVERSION"}:
        w=values[idx-lookback+1:idx+1]
        m,sd=mean_sd(w)
        if sd is None or sd<=0:return 0
        z=(now-m)/sd
        if z<=-max(0.75,thr):return 1
        if z>=max(0.75,thr):return -1
        return 0
    if method in {"EMA_DEVIATION_FADE"}:
        e=ema(values,lookback,idx)
        if e is None or e<=0:return 0
        deviation=(now/e-1)*100
        if deviation<=-thr:return 1
        if deviation>=thr:return -1
        return 0
    if method in {"RELATIVE_STRENGTH","RELATIVE_STRENGTH_ROTATION"}:
        other=params.get("other_values",[])
        if idx>=len(other) or len(other)<=lookback:return 0
        op=other[idx-lookback]
        if not op or op<=0:return 0
        other_change=(other[idx]/op-1)*100
        rel=change_pct-other_change
        if rel>=thr:return 1
        if rel<=-thr:return -1
    return 0


def realized_vol(values,end,period):
    if end<period:return None
    rets=[]
    for j in range(end-period+1,end+1):
        if values[j-1] is not None and values[j] is not None and values[j-1]>0 and values[j]>0:
            rets.append(math.log(values[j]/values[j-1]))
    if len(rets)<max(2,period//2):return None
    m,sd=mean_sd(rets)
    return sd*math.sqrt(252) if sd is not None else None


def make_signal(method,confirm,regime,values,other_values,vix_values,idx,entry_idx,axes,symbol,chain_features):
    method=canonical(method)
    confirm=canonical(confirm)
    regime=canonical(regime)
    if method not in SUPPORTED_CORE_METHODS:return 0,"CORE_IMPLEMENTATION_NOT_REGISTERED"
    if confirm not in SUPPORTED_CONFIRMS:return 0,"CONFIRMATION_NOT_IMPLEMENTED"
    if regime not in SUPPORTED_REGIMES:return 0,"REGIME_NOT_IMPLEMENTED"
    lookback=int(axes.get("lookback_sessions",axes.get("signal_lookback_sessions",axes.get("lookback",5))))
    threshold=float(axes.get("move_threshold_pct",axes.get("move_or_signal_threshold_pct",axes.get("threshold_pct",0.5))))
    vol_lb=int(axes.get("vol_lookback_sessions",axes.get("volatility_lookback_sessions",5)))
    method_params={"other_values":other_values}
    side=compute_signal(method,values,idx,lookback,threshold,method_params)
    if side==0:return 0,"NO_SIGNAL"
    # Options-flow uses only prior-close/close-index daily OI and volume deltas.
    if confirm=="OPTIONS_FLOW":
        feat=chain_features.get((symbol,idx),{})
        method=canonical(axes.get("oi_confirmation_method","OI_AND_VOLUME"))
        is_call_signal=side>0
        side_oi_delta=feat.get("ce_oi_delta",0) if is_call_signal else feat.get("pe_oi_delta",0)
        side_volume=feat.get("ce_volume",0) if is_call_signal else feat.get("pe_volume",0)
        side_volume_delta=feat.get("ce_volume_delta",0) if is_call_signal else feat.get("pe_volume_delta",0)
        needs_oi=("OI" in method or "OPEN_INTEREST" in method)
        needs_volume=("VOLUME" in method or "VOL" in method)
        if not needs_oi and not needs_volume:return 0,"OI_CONFIRMATION_METHOD_NOT_IMPLEMENTED"
        if needs_oi and side_oi_delta<=0:return 0,"OPTIONS_FLOW_OI_CONFIRMATION_FAIL"
        if needs_volume:
            # Methods labelled volume-change/spike require the signed volume delta;
            # simple volume confirmation requires a positive volume total.
            if "DELTA" in method or "SPIKE" in method:
                if side_volume_delta<=0:return 0,"OPTIONS_FLOW_VOLUME_DELTA_FAIL"
            elif side_volume<=0:return 0,"OPTIONS_FLOW_VOLUME_FAIL"
    elif confirm not in {"NONE",""}:
        return 0,"CONFIRMATION_NOT_IMPLEMENTED"
    if regime=="TREND_RANGE":
        move=abs(values[idx]/values[idx-lookback]-1)*100 if values[idx-lookback] and values[idx-lookback]>0 else 0
        trailing=[]
        for j in range(max(lookback+1,idx-60),idx):
            if values[j-lookback] and values[j-lookback]>0:
                trailing.append(abs(values[j]/values[j-lookback]-1)*100)
        bound=sorted(trailing)[len(trailing)//2] if trailing else None
        if bound is None:return 0,"TREND_REGIME_HISTORY_MISSING"
        is_trend=move>=bound
        trend_method=is_trend_method(method)
        reversion_method=is_mean_reversion_method(method)
        if (trend_method and not is_trend) or (reversion_method and is_trend):return 0,"TREND_RANGE_REGIME_FILTER"
    elif regime=="INDIA_VIX":
        if idx>=len(vix_values) or vix_values[idx] is None:return 0,"INDIA_VIX_MISSING"
        # The high/low regime threshold is the historical expanding median, using no future values.
        past_vix=[v for v in vix_values[:idx] if v is not None]
        if not past_vix:return 0,"INDIA_VIX_HISTORY_MISSING"
        bound=sorted(past_vix)[len(past_vix)//2]
        # Low VIX admits mean-reversion cores; high VIX admits trend/momentum cores.
        if is_mean_reversion_method(method) and vix_values[idx]>bound:
            return 0,"VIX_REGIME_FILTER"
        if is_trend_method(method) and vix_values[idx]<bound:
            return 0,"VIX_REGIME_FILTER"
    elif regime not in {"NONE",""}:
        return 0,"REGIME_NOT_IMPLEMENTED"
    return side,"SIGNAL"


def load_market():
    if not OPTION_CACHE.exists():
        raise RuntimeError("Private NSE data cache is missing; run the official NSE acquisition workflow first.")
    contracts=defaultdict(dict)
    closes=defaultdict(dict)
    option_dates=set()
    archive_errors=[]
    archive_paths=sorted(OPTION_CACHE.glob("*/*.zip"))
    if not archive_paths: raise RuntimeError("No cached official NSE daily archives were restored.")
    for p in archive_paths:
        d=parse_date(p.stem)
        if d is None: continue
        try:
            rows=read_archive(p,d)
        except Exception as exc:
            archive_errors.append({"date":d.isoformat(),"error":type(exc).__name__+":"+str(exc)[:160]})
            continue
        option_dates.add(d)
        per_symbol_spot=defaultdict(list)
        daymap=contracts[d]
        for r in rows:
            symbol=r["symbol"]
            if r["spot"] and r["spot"]>0:per_symbol_spot[symbol].append(r["spot"])
            if r["instrument"]!="OPTIDX":continue
            k=(symbol,r["expiry"],r["strike"],r["side"])
            if k in daymap:
                archive_errors.append({"date":d.isoformat(),"error":"DUPLICATE_KEY:"+repr(k)})
                continue
            daymap[k]=r
        for sym,vals in per_symbol_spot.items():
            closes[sym][d]=median(vals)
    index_closes=read_index_closes()
    for sym,by_day in index_closes.items():
        # Use official index close when present; underlying from option archive remains available as a fallback.
        for d,price in by_day.items():
            closes[sym][d]=price
    # All rows are indexed by the official archive/session dates; index-context gap reconciliation is separate.
    dates=sorted(set(closes["NIFTY"]) | set(closes["BANKNIFTY"]) | option_dates)
    if not dates: raise RuntimeError("No usable official option/index dates.")
    vix=read_vix_cache()
    context_coverage=validate_context_coverage(dates,vix,index_closes)
    vix_series=[vix.get(d) for d in dates]
    data={
      "contracts":contracts,"closes":closes,"dates":dates,"vix":vix_series,"vix_by_date":vix,
      "option_dates":option_dates,"archive_errors":archive_errors,
      "raw_archive_count":len(archive_paths),"context_coverage":context_coverage,
    }
    return data


def aggregate_chain_features(data,symbol,dates):
    out={}
    previous=None
    for idx,d in enumerate(dates):
        rows=[r for (sym,exp,k,side),r in data["contracts"].get(d,{}).items() if sym==symbol]
        spot=data["closes"][symbol].get(d)
        if not spot: continue
        ce_oi=sum(max(0,r["oi"] or 0) for r in rows if r["side"]=="CE" and r["strike"] and abs(r["strike"]/spot-1)<=0.03)
        pe_oi=sum(max(0,r["oi"] or 0) for r in rows if r["side"]=="PE" and r["strike"] and abs(r["strike"]/spot-1)<=0.03)
        ce_vol=sum(max(0,r["volume"] or 0) for r in rows if r["side"]=="CE" and r["strike"] and abs(r["strike"]/spot-1)<=0.03)
        pe_vol=sum(max(0,r["volume"] or 0) for r in rows if r["side"]=="PE" and r["strike"] and abs(r["strike"]/spot-1)<=0.03)
        previous=previous or (ce_oi,pe_oi,ce_vol,pe_vol)
        out[(symbol,idx)]={
           "ce_oi":ce_oi,"pe_oi":pe_oi,"ce_volume":ce_vol,"pe_volume":pe_vol,
           "ce_oi_delta":ce_oi-previous[0],"pe_oi_delta":pe_oi-previous[1],
           "ce_volume_delta":ce_vol-previous[2],"pe_volume_delta":pe_vol-previous[3],
        }
        previous=(ce_oi,pe_oi,ce_vol,pe_vol)
    return out

def precompute_chain_features(data,dates):
    """Build each supported underlying's daily chain features once per shard.

    These features are invariant across parameter configurations. Recomputing the
    full option chain inside the configuration loop multiplies archive-row scans
    by the grid size without changing the signal definitions.
    """
    return {symbol:aggregate_chain_features(data,symbol,dates)
            for symbol in sorted(INDEX_SYMBOLS)}


def load_cost_cases():
    rows=read_csv(OUT/"cost_scenarios.csv")
    if len(rows)!=24:
        raise RuntimeError(f"Expected 24 registered cost cases; found {len(rows)}.")
    result=[]
    for row in rows:
        brokerage=number(value(row,"brokerage_per_order","brokerage_rupees_per_order"))
        slippage=number(value(row,"slippage_per_unit_per_side","slippage_rupees_per_unit_per_side"))
        multiplier=number(value(row,"fee_multiplier","statutory_fee_multiplier"))
        if brokerage is None or slippage is None or multiplier is None:
            raise RuntimeError("Cost scenario has missing numeric brokerage, slippage, or fee-multiplier field.")
        result.append({
          "cost_case_id":value(row,"cost_case_id","scenario_id","cost_id"),
          "brokerage_per_order":brokerage,
          "slippage_per_unit_per_side":slippage,
          "fee_multiplier":multiplier,
          "raw":row,
        })
    actual={(x["brokerage_per_order"],x["slippage_per_unit_per_side"],x["fee_multiplier"]) for x in result}
    expected={(b,s,m) for b in (10.0,15.0,20.0) for s in (0.0,0.05,0.25,0.5) for m in (1.0,1.5)}
    if actual!=expected or len(actual)!=24:
        raise RuntimeError("Registered cost grid does not equal the required 3×4×2 scenario Cartesian product.")
    return result


def load_tasks(max_configs=0):
    family_rows=read_csv(OUT/"strategy_families.csv")
    space_rows=read_csv(OUT/"family_configuration_space.csv")
    gate_rows=read_csv(OUT/"family_data_feasibility.csv")
    gates={value(r,"family_id","family_key","id"):r for r in gate_rows}
    spaces={value(r,"family_id","family_key","id"):r for r in space_rows}
    tasks=[]; blocked=Counter(); family_status=Counter()
    for rawfam in family_rows:
        fam=normalize_family(rawfam)
        core_method_name=core_method(fam["core"])
        if not core_method_name:
            blocked["CORE_IMPLEMENTATION_NOT_REGISTERED"]+=1
            family_status[fam["family_id"]]="BLOCKED_CORE_NOT_IMPLEMENTED"
            continue
        if fam["confirmation"] not in SUPPORTED_CONFIRMS:
            blocked["CONFIRMATION_NOT_IMPLEMENTED"]+=1
            family_status[fam["family_id"]]="BLOCKED_CONFIRMATION_NOT_IMPLEMENTED"
            continue
        if fam["regime"] not in SUPPORTED_REGIMES:
            blocked["REGIME_NOT_IMPLEMENTED"]+=1
            family_status[fam["family_id"]]="BLOCKED_REGIME_NOT_IMPLEMENTED"
            continue
        gate=gates.get(fam["family_id"],{})
        if value(gate,"source_feasibility_status")=="BLOCKED_MISSING_INPUTS":
            blocked["SOURCE_INPUTS_MISSING"]+=1
            family_status[fam["family_id"]]="BLOCKED_SOURCE_INPUTS"
            continue
        space=spaces.get(fam["family_id"],{})
        axes=json_field(space,"axes_json",default={})
        if not axes:
            blocked["CONFIGURATION_MANIFEST_MISSING"]+=1
            family_status[fam["family_id"]]="BLOCKED_CONFIGURATION_MANIFEST"
            continue
        axis_names=list(axes)
        axis_values=[axes[k] for k in axis_names]
        count=1
        for values in axis_values:count*=len(values)
        family_status[fam["family_id"]]="ELIGIBLE_FOR_EOD_DIAGNOSTIC"
        for cfg_rank,combo in enumerate(product(*axis_values)):
            cfg=dict(zip(axis_names,combo))
            task_id=fam["family_id"]+"-"+str(cfg_rank).zfill(7)
            tasks.append({"task_id":task_id,"family":fam,"core_method":core_method_name,"axes":cfg,
                          "family_config_rank":cfg_rank,"registered_configurations":count})
        family_status[fam["family_id"]]=family_status[fam["family_id"]]
    tasks.sort(key=lambda x:(x["family"]["family_id"],x["family_config_rank"]))
    if max_configs>0: tasks=tasks[:max_configs]
    return tasks,blocked,family_status


def choose_contract(data,signal_date,entry_date,exit_date,symbol,side,strike_target):
    chain=data["contracts"].get(signal_date,{})
    spot=data["closes"][symbol].get(signal_date)
    if not spot:return None,"SIGNAL_SPOT_MISSING"
    d=0.005 if "0.5" in canonical(strike_target) else (0.0 if "ATM" in canonical(strike_target) else 0.01)
    target_name=canonical(strike_target)
    if target_name=="ATM":target=spot
    elif "ITM" in target_name: target=spot*(1-d if side=="CE" else 1+d)
    elif "OTM" in target_name: target=spot*(1+d if side=="CE" else 1-d)
    else:target=spot
    eligible=[]
    for (sym,expiry,strike,opt_side),r in chain.items():
        if sym!=symbol or opt_side!=side or expiry is None or strike is None:continue
        if expiry < exit_date+timedelta(days=2): continue
        # At signal close, choose a contract listed and traded on that day.
        if not r["volume"] or r["volume"]<=0 or not r["close"] or r["close"]<=0:continue
        eligible.append((expiry,abs(strike-target),-float(r["volume"] or 0),r))
    if not eligible:return None,"NO_SIGNAL_DATE_CONTRACT"
    eligible.sort(key=lambda z:(z[0],z[1],z[2]))
    r=eligible[0][3]
    return (symbol,r["expiry"],r["strike"],side),"OK"


def parse_risk_profile(risk):
    """Parse registered premium stop/target profiles; missing barriers stay None."""
    risk=canonical(risk)
    stop_match=re.search(r"STOP_(\d+)PCT",risk)
    target_match=re.search(r"TARGET_(\d+)PCT",risk)
    stop_pct=float(stop_match.group(1))/100.0 if stop_match else None
    target_pct=float(target_match.group(1))/100.0 if target_match else None
    return stop_pct,target_pct


def option_side_from_direction(direction):
    """Convert signed directional signal to the exact NSE option side."""
    try:
        value=float(direction)
    except (TypeError,ValueError):
        return None
    if value>0:return "CE"
    if value<0:return "PE"
    return None


def simulate_trade(data,dates,index_by_date,symbol,signal_idx,side,axes,sample="selection"):
    signal_date=dates[signal_idx]
    # The cost schedule begins 1 October 2024. Earlier rows are features/warm-up only.
    entry_idx=signal_idx+1
    holding=canonical(axes.get("holding_exit",axes.get("holding_horizon","SAME_SESSION_CLOSE")))
    hold_sessions=2 if ("2_SESSION" in holding or "2_DAY" in holding) else 1
    exit_idx=entry_idx+hold_sessions-1
    if entry_idx>=len(dates) or exit_idx>=len(dates): return None,"END_OF_SAMPLE"
    entry_date=dates[entry_idx]; exit_date=dates[exit_idx]
    if entry_date<FIRST_COST_DATE:return None,"COST_SCHEDULE_NOT_VERIFIED"
    # Cannot jump across a date where the option archive failed. Requires each selected session to be present.
    if entry_date not in data["option_dates"] or exit_date not in data["option_dates"]:return None,"OPTION_ARCHIVE_SESSION_MISSING"
    target=canonical(axes.get("strike_target","ATM"))
    direction=1 if float(side)>0 else (-1 if float(side)<0 else 0)
    option_side=option_side_from_direction(direction)
    if option_side is None:return None,"INVALID_DIRECTION_SIGNAL"
    contract,reason=choose_contract(data,signal_date,entry_date,exit_date,symbol,option_side,target)
    if contract is None:return None,reason
    entry_row=data["contracts"].get(entry_date,{}).get(contract)
    exit_row=data["contracts"].get(exit_date,{}).get(contract)
    if not entry_row or not exit_row:return None,"EXACT_CONTRACT_NOT_PRESENT_ON_ENTRY_OR_EXIT"
    if not entry_row["volume"] or entry_row["volume"]<=0 or not exit_row["volume"] or exit_row["volume"]<=0:
        return None,"ZERO_VOLUME_ENTRY_OR_EXIT"
    entry=entry_row["open"]
    if entry is None or entry<=0:return None,"INVALID_ENTRY_OPEN"
    qty=entry_row["lot"]
    if qty is None or qty<=0:return None,"HISTORICAL_LOT_SIZE_MISSING"
    risk=canonical(axes.get("risk_profile","NO_STOP_NO_TARGET"))
    exit_price=None; exit_reason="PLANNED_CLOSE"
    if risk!="NO_STOP_NO_TARGET":
        stop_pct,target_pct=parse_risk_profile(risk)
        for j in range(entry_idx,exit_idx+1):
            day=dates[j]
            bar=data["contracts"].get(day,{}).get(contract)
            if not bar or not bar["volume"] or bar["volume"]<=0:continue
            op,hi,lo,cl=bar["open"],bar["high"],bar["low"],bar["close"]
            stop=entry*(1-stop_pct) if stop_pct else None
            take=entry*(1+target_pct) if target_pct else None
            touched_stop=stop is not None and lo is not None and lo<=stop
            touched_take=take is not None and hi is not None and hi>=take
            # Daily OHLC cannot show barrier ordering: if both were touched, conservatively stop first.
            if touched_stop:
                exit_price=min(op,stop) if op is not None and op>0 else stop
                exit_reason="STOP_OR_STOP_FIRST_AMBIGUITY"
                break
            if touched_take:
                exit_price=max(op,take) if op is not None and op>0 else take
                exit_reason="TARGET"
                break
            if j==exit_idx:exit_price=cl
    else:
        exit_price=exit_row["close"]
    if exit_price is None or not math.isfinite(exit_price) or exit_price<=0:return None,"INVALID_EXIT_MARK"
    gross=(exit_price-entry)*qty
    return {
      "signal_date":signal_date.isoformat(),"entry_date":entry_date.isoformat(),"exit_date":exit_date.isoformat(),
      "symbol":symbol,"expiry":contract[1].isoformat(),"strike":contract[2],
      "side":option_side,"direction":direction,
      "entry_price_proxy":entry,"exit_price_proxy":exit_price,"lot_size":qty,
      "gross_pnl":gross,"exit_reason":exit_reason,"holding_sessions":hold_sessions,
      "execution_model":"signal-at-prior-close, next-session daily OPEN, exit at daily CLOSE or conservative stop/target using daily H/L; positive EOD volume required",
      "fill_model_warning":"Daily OHLC does not prove a quote, queue position, spread or actual fill; model is diagnostic only.",
    },"TRADE"


def compute_metrics(trades,cost_case,cost_model):
    net=[]; gross=[]; fees=[]; slip=[]; rows=[]
    for t in trades:
        entry_date=date.fromisoformat(t["entry_date"])
        fee,breakdown=call_cost_model(cost_model,entry_date,t["entry_price_proxy"],t["exit_price_proxy"],
             t["lot_size"],cost_case["brokerage_per_order"],cost_case["fee_multiplier"])
        slippage=2*cost_case["slippage_per_unit_per_side"]*t["lot_size"]
        netpnl=t["gross_pnl"]-fee-slippage
        net.append(netpnl);gross.append(t["gross_pnl"]);fees.append(fee);slip.append(slippage)
        rows.append((t,netpnl,fee,slippage,breakdown))
    equity=peak=0.0; maxdd=0.0
    for p in net:
        equity+=p;peak=max(peak,equity);maxdd=max(maxdd,peak-equity)
    n=len(net); wins=sum(x>0 for x in net); loss=sum(x<0 for x in net)
    return {
      "trades":n,"wins":wins,"losses":loss,"win_rate":wins/n if n else None,
      "gross_pnl":sum(gross),"net_pnl":sum(net),"statutory_and_brokerage_cost":sum(fees),
      "slippage_cost":sum(slip),"average_net_pnl_per_trade":sum(net)/n if n else None,
      "net_return_pct_on_premium_capital":100*sum(net)/sum(t["entry_price_proxy"]*t["lot_size"] for t in trades) if n else None,
      "max_drawdown_rupees":maxdd,"profit_factor":sum(x for x in net if x>0)/abs(sum(x for x in net if x<0)) if any(x<0 for x in net) else None,
      "nonpositive_trades":sum(x<=0 for x in net),
      "trade_rows":rows,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--start-config",type=int,default=0,help="Position in the sorted, source-feasible, implemented configuration list")
    ap.add_argument("--max-configs",type=int,default=5000)
    ap.add_argument("--shard-id",default="")
    ap.add_argument("--sample",choices=("selection","holdout"),default="selection")
    ap.add_argument("--config-list",default="",help="CSV containing task_id rows to evaluate; required for the untouched holdout")
    args=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    data=load_market()
    dates_for_features=data["dates"]
    chain_features_by_symbol=precompute_chain_features(data,dates_for_features)
    cost_model=load_cost_model()
    cost_fn_name,_=find_cost_function(cost_model)
    if not cost_fn_name: raise RuntimeError("Cost model API unresolved. No results emitted.")
    # Full registry is enumerated; unsupported/source-blocked families are explicitly accounted.
    all_tasks,blocked,family_status=load_tasks(max_configs=0)
    if args.sample=="holdout":
        if not args.config_list or not Path(args.config_list).exists():
            raise RuntimeError("Holdout evaluation requires the frozen validation_shortlist.csv; no all-grid holdout sweep is permitted.")
        selected_rows=read_csv(args.config_list)
        selected_ids={r.get("task_id","") for r in selected_rows if r.get("task_id")}
        if not selected_ids:
            raise RuntimeError("The validation shortlist is empty; holdout evaluation is not launched.")
        all_tasks=[t for t in all_tasks if t["task_id"] in selected_ids]
        missing=selected_ids-{t["task_id"] for t in all_tasks}
        if missing:
            raise RuntimeError("Shortlisted task IDs do not match the frozen registry: "+str(len(missing))+" unmatched IDs.")
        shortlist_hash=hashlib.sha256(Path(args.config_list).read_bytes()).hexdigest()
    else:
        shortlist_hash=""
    total_tasks=len(all_tasks)
    start=max(0,args.start_config); end=min(total_tasks,start+max(1,args.max_configs))
    tasks=all_tasks[start:end]
    cost_cases=load_cost_cases()
    results=[]; config_counts=Counter(); family_counts=Counter(); skip_counts=Counter()
    for n,task in enumerate(tasks,1):
        fam=task["family"]; method=task["core_method"]; axes=task["axes"]
        # Daily source series and market context.
        symbol="NIFTY" if "BANK" not in fam["core"] and "BANK" not in fam["family_name"].upper() else "BANKNIFTY"
        if symbol not in data["closes"] or not data["closes"][symbol]:
            skip_counts["UNDERLYING_SERIES_MISSING"]+=1;continue
        dates=data["dates"]; series=[data["closes"][symbol].get(d) for d in dates]
        other_symbol="BANKNIFTY" if symbol=="NIFTY" else "NIFTY"
        other=[data["closes"][other_symbol].get(d) for d in dates]
        # Fill only short gaps for feature warm-up; never fill a trade date / contract price.
        for arr in (series,other):
            last=None
            for i,x in enumerate(arr):
                if x is not None and x>0:last=x
                elif last is not None:arr[i]=last
        chain_features=chain_features_by_symbol.get(symbol,{})
        signals=[]; no_signal=Counter()
        for idx,d in enumerate(dates):
            if d<FIRST_COST_DATE-timedelta(days=45):continue
            other_values=other
            vix_series=data["vix"]
            side,reason=make_signal(method,fam["confirmation"],fam["regime"],series,other_values,
                         vix_series,idx,idx+1,axes,symbol,chain_features)
            if side:signals.append((idx,side))
            else:no_signal[reason]+=1
        trades=[]; reject_reasons=Counter()
        date_to_idx={d:i for i,d in enumerate(dates)}
        for signal_idx,side in signals:
            trade,reason=simulate_trade(data,dates,date_to_idx,symbol,signal_idx,side,axes,args.sample)
            if trade is None:reject_reasons[reason]+=1
            else:trades.append(trade)
        config_counts["attempted"]+=1
        family_counts[fam["family_id"]]+=1
        base={
          "engine_version":ENGINE_VERSION,"task_id":task["task_id"],"config_rank_global":start+n-1,
          "family_id":fam["family_id"],"family_name":fam["family_name"],"core_id":fam["core"],
          "confirmation_id":fam["confirmation"],"regime_id":fam["regime"],
          "core_method_implementation":method,
          "configuration_json":json.dumps(axes,sort_keys=True,separators=(",",":")),
          "signals":len(signals),"trades":len(trades),"signal_rejections_json":json.dumps(no_signal,sort_keys=True,separators=(",",":")),
          "trade_exclusions_json":json.dumps(reject_reasons,sort_keys=True,separators=(",",":")),
          "date_min":min((t["entry_date"] for t in trades),default=""),
          "date_max":max((t["exit_date"] for t in trades),default=""),
          "archive_date_count":len(data["option_dates"]),"raw_archives_loaded":data["raw_archive_count"],
          "duplicate_or_archive_parse_errors":len(data["archive_errors"]),
          "cost_model_callable":cost_fn_name,
          "execution_model":"prior-close signal, next-session open premium, same-session or second-session close; daily high/low barriers are stop-first",
          "sample":args.sample,
          "promotion_status":"HOLDOUT_DIAGNOSTIC_NO_PROMOTION" if args.sample=="holdout" else "SELECTION_DIAGNOSTIC_ONLY_MULTIPLE_TESTING_AND_HOLDOUT_GATE_NOT_PASSED",
        }
        for cost in cost_cases:
            metric=compute_metrics(trades,cost,cost_model)
            row=dict(base)
            row.update({"cost_case_id":cost["cost_case_id"],"brokerage_per_order":cost["brokerage_per_order"],
              "slippage_per_unit_per_side":cost["slippage_per_unit_per_side"],"fee_multiplier":cost["fee_multiplier"]})
            for k,v in metric.items():
                if k!="trade_rows":row[k]=v
            results.append(row)
        if n%100==0:
            print(json.dumps({"chunk_start":start,"processed_configs":n,"chunk_size":len(tasks),
                              "cost_rows":len(results),"global_config_cursor":start+n},sort_keys=True),flush=True)
    # Output only per-config, per-cost summary metrics: individual trade tapes/raw option records stay private.
    shard=args.shard_id or f"{start:09d}-{end:09d}"
    outdir=OUT/("holdout_shards" if args.sample=="holdout" else "evaluation_shards")
    path=outdir/shard_result_filename(args.sample,shard)
    path.parent.mkdir(parents=True,exist_ok=True)
    fields=sorted({k for r in results for k in r})
    with gzip.open(path,"wt",encoding="utf-8",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=fields,extrasaction="ignore");writer.writeheader();writer.writerows(results)
    summary={
      "engine_version":ENGINE_VERSION,"generated_utc":datetime.now(timezone.utc).isoformat(),
      "global_config_start":start,"global_config_end_exclusive":end,"total_supported_source_feasible_configs":total_tasks,
      "configs_requested":len(tasks),"configs_attempted":config_counts["attempted"],
      "cost_rows_generated":len(results),"cost_cases_per_config":len(cost_cases),
      "skipped_reasons":dict(sorted(skip_counts.items())),"blocked_families_reasons":dict(sorted(blocked.items())),
      "archive_parse_or_duplicate_warnings":len(data["archive_errors"]),
      "official_context_coverage":data["context_coverage"],
      "archive_count_loaded":data["raw_archive_count"],"unique_option_archive_dates":len(data["option_dates"]),
      "cost_model_callable":cost_fn_name,"first_cost_eligible_date":FIRST_COST_DATE.isoformat(),
      "sample":args.sample,
      "frozen_validation_shortlist_sha256":shortlist_hash if args.sample=="holdout" else "",
      "holdout_window": {"start":HOLDOUT_START.isoformat(),"end_exclusive":HOLDOUT_END_EXCLUSIVE.isoformat()} if args.sample=="holdout" else None,
      "cost_model_guard":"Net P&L starts only on entries >=2024-10-01; earlier prices are signal warm-up only.",
      "raw_trade_tapes_publicly_published":False,
      "result_path":str(path),"result_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
      "status":"PARTIAL_SHARD_COMPLETE" if end<total_tasks else ("COMPLETE_GRID_ATTEMPTED" if config_counts["attempted"]==len(tasks) else "COMPLETE_GRID_WITH_SKIPS"),
      "no_promotion":"All reported results are diagnostic until holdout, multiple testing, coverage, costs and execution evidence pass.",
    }
    progress_path=OUT/("holdout_progress.json" if args.sample=="holdout" else "evaluation_progress.json")
    previous=read_json(progress_path,{})
    if previous.get("engine_version")!=ENGINE_VERSION or previous.get("sample",args.sample)!=args.sample:
        previous={}
    completed=previous.get("completed_config_ranges",[])
    shard_record={"start":start,"end_exclusive":end,"configs_requested":len(tasks),"configs_attempted":config_counts["attempted"],
                  "cost_rows":len(results),"result_path":str(path),"result_sha256":summary["result_sha256"],
                  "status":summary["status"]}
    if not any(x.get("start")==start and x.get("end_exclusive")==end for x in completed):
        completed.append(shard_record)
    completed.sort(key=lambda x:x["start"])
    summary["completed_ranges_total"]=len(completed)
    summary["completed_configs_all_ranges"]=sum(int(x.get("configs_attempted",0)) for x in completed)
    summary["completed_cost_rows_all_ranges"]=sum(int(x.get("cost_rows",0)) for x in completed)
    summary["remaining_supported_configs"]=max(0,total_tasks-max((x.get("end_exclusive",0) for x in completed),default=0))
    checkpoint={"engine_version":ENGINE_VERSION,"sample":args.sample,"updated_utc":summary["generated_utc"],
      "total_supported_source_feasible_configs":total_tasks,"completed_config_ranges":completed,
      "next_config_cursor":max((x.get("end_exclusive",0) for x in completed),default=0),
      "configs_attempted_total":summary["completed_configs_all_ranges"],
      "cost_rows_generated_total":summary["completed_cost_rows_all_ranges"],
      "remaining_supported_configs":summary["remaining_supported_configs"],
      "latest_shard":shard_record}
    (OUT/"evaluation_shard_summary.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    progress_path.write_text(json.dumps(checkpoint,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    lines=[
      "# Phase 109 evaluation shard report","",
      "Status: **"+summary["status"]+"**","",
      f"- Config cursor range: [{start:,}, {end:,}); registry eligible-config denominator: {total_tasks:,}.",
      f"- Configs attempted in this shard: {config_counts['attempted']:,}; cost-adjusted rows generated: {len(results):,}; expected cost cases/config: 24.",
      f"- Completed shard ranges currently recorded: {len(completed):,}; cumulative attempted configs: {summary['completed_configs_all_ranges']:,}; cumulative cost rows: {summary['completed_cost_rows_all_ranges']:,}; remaining eligible configs: {summary['remaining_supported_configs']:,}.",
      f"- Archive dates loaded: {len(data['option_dates']):,}; source files loaded: {data['raw_archive_count']:,}; archive parse/duplicate warnings: {len(data['archive_errors']):,}.",
      f"- Official context coverage gate: {data['context_coverage']['observed_unique_dates']}; minimum required per series: {data['context_coverage']['minimum_unique_dates_per_series']:,} over {data['context_coverage']['window_start']}–{data['context_coverage']['window_end_inclusive']}.",
      f"- Cost model: `{cost_fn_name}`; P&L trade entries before {FIRST_COST_DATE.isoformat()} are blocked.",
      "- Sample: "+args.sample+". Selection mode uses development/validation only; holdout mode must load the frozen validation shortlist and scores only 2026-04-01 through 2026-10-08.",
      "- All net results remain diagnostic, use EOD OHLC execution proxies, and are exposed to selection/multiple-testing bias. No strategy is promoted.",
      "- Public outputs contain per-configuration/per-cost summary metrics only; raw options rows and trade tapes remain private.",
      "- Cost-row summary: `evaluation_shards/"+path.name+"`; machine-readable shard summary: `evaluation_shard_summary.json`; resumable ledger: `evaluation_progress.json`.",
    ]
    (OUT/"PHASE109_EVALUATION_SHARD_REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({k:summary[k] for k in ("status","global_config_start","global_config_end_exclusive","total_supported_source_feasible_configs",
      "configs_attempted","cost_rows_generated","remaining_supported_configs","result_sha256")},sort_keys=True))


if __name__=="__main__":main()
