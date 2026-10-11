#!/usr/bin/env python3
"""Derive model-implied volatility/Greeks for exact NSE index-option contracts.

Source: official NSE daily option premium, spot, strike, expiry and option type.
Model: European Black-Scholes, continuously compounded flat r=6.5%, q=0%.
These are estimated values, not exchange-published IV/Greeks. They are generated
only on UDiFF dates >=2024-10-01 with positive volume and strictly valid inputs.
Every row remains in the private Actions cache; public reports contain aggregates.
"""
import csv, gzip, hashlib, io, json, math, zipfile
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

CACHE=Path("data/cache/phase109")
SOURCE=CACHE/"nse_eod"
DEST=CACHE/"options_model_greeks"
OUT=Path("results/phase109")
FIRST_EXECUTABLE_DATE=date(2024,10,1)
RISK_FREE=0.065
DIVIDEND_YIELD=0.0
MAX_VOL=5.0
SYMBOLS={"NIFTY","BANKNIFTY","FINNIFTY","MIDCPNIFTY"}


def parse_date(v):
    s=str(v or "").strip()
    for fmt in ("%Y-%m-%d","%d-%b-%Y","%d-%B-%Y","%d/%m/%Y","%d%m%Y","%Y%m%d"):
        try:
            return datetime.strptime(s[:10] if fmt=="%Y-%m-%d" else s,fmt).date()
        except ValueError:
            pass
    return None


def num(v):
    try:
        x=float(str(v).strip())
        return x if math.isfinite(x) else None
    except (TypeError,ValueError,OverflowError): return None


def cdf(x):
    return 0.5*(1.0+math.erf(x/math.sqrt(2.0)))


def pdf(x):
    return math.exp(-0.5*x*x)/math.sqrt(2.0*math.pi)


def bs_price(spot,strike,t,rate,vol,side,q=0.0):
    if t<=0 or spot<=0 or strike<=0 or vol<=0: return float("nan")
    sig=vol*math.sqrt(t)
    d1=(math.log(spot/strike)+(rate-q+0.5*vol*vol)*t)/sig
    d2=d1-sig
    discq=math.exp(-q*t)
    discr=math.exp(-rate*t)
    if side=="CE":
        return spot*discq*cdf(d1)-strike*discr*cdf(d2)
    return strike*discr*cdf(-d2)-spot*discq*cdf(-d1)


def lower_bound(spot,strike,t,rate,side,q=0.0):
    disc_s=spot*math.exp(-q*t)
    disc_k=strike*math.exp(-rate*t)
    return max(0.0,disc_s-disc_k) if side=="CE" else max(0.0,disc_k-disc_s)


def implied_vol(price,spot,strike,t,rate,side,q=0.0):
    if any(not math.isfinite(v) for v in (price,spot,strike,t,rate)) or price<=0 or spot<=0 or strike<=0 or t<=0:
        return None,"INVALID_INPUT"
    intrinsic=lower_bound(spot,strike,t,rate,side,q)
    if price < intrinsic-0.50:
        return None,"PREMIUM_BELOW_MODEL_LOWER_BOUND"
    at_max=bs_price(spot,strike,t,rate,MAX_VOL,side,q)
    at_min=bs_price(spot,strike,t,rate,1e-4,side,q)
    if not math.isfinite(at_max) or price>at_max+0.5:
        return None,"PREMIUM_ABOVE_MODEL_UPPER_BOUND"
    if price<=at_min+1e-8:
        return 1e-4,"AT_OR_NEAR_MIN_VOL"
    lo,hi=1e-4,MAX_VOL
    for _ in range(42):
        mid=(lo+hi)/2
        model=bs_price(spot,strike,t,rate,mid,side,q)
        if model<price: lo=mid
        else: hi=mid
    vol=(lo+hi)/2
    return vol,"OK"


def greeks(spot,strike,t,rate,vol,side,q=0.0):
    if t<=0 or min(spot,strike,vol)<=0:
        return None
    root=math.sqrt(t)
    sig=vol*root
    d1=(math.log(spot/strike)+(rate-q+0.5*vol*vol)*t)/sig
    d2=d1-sig
    discq=math.exp(-q*t); discr=math.exp(-rate*t)
    density=pdf(d1)
    delta=discq*cdf(d1) if side=="CE" else discq*(cdf(d1)-1.0)
    gamma=discq*density/(spot*sig)
    vega=spot*discq*density*root/100.0
    if side=="CE":
        theta_day=(-spot*discq*density*vol/(2*root)-rate*strike*discr*cdf(d2)+q*spot*discq*cdf(d1))/365.0
    else:
        theta_day=(-spot*discq*density*vol/(2*root)+rate*strike*discr*cdf(-d2)-q*spot*discq*cdf(-d1))/365.0
    return {"delta":delta,"gamma":gamma,"vega_per_vol_point":vega,"theta_per_calendar_day":theta_day}


def pick(row,keys):
    for k in keys:
        if k in row and str(row[k]).strip()!="": return row[k]
    return None


def derive_day(path, trade_date):
    raw=path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        members=[x for x in z.namelist() if x.lower().endswith(".csv")]
        if len(members)!=1: raise ValueError("CSV_MEMBER_COUNT_"+str(len(members)))
        csv_raw=z.read(members[0])
    reader=csv.DictReader(io.StringIO(csv_raw.decode("utf-8-sig")))
    fields=reader.fieldnames or []
    if not all(x in fields for x in ("FinInstrmTp","TckrSymb","FininstrmActlXpryDt","StrkPric","OptnTp","ClsPric","TtlTradgVol","UndrlygPric")):
        return {"status":"BLOCKED_NON_UDIFF_OR_MISSING_SPOT","trade_date":trade_date.isoformat(),
                "archive_sha256":hashlib.sha256(raw).hexdigest(),"source_rows":0,"valid_model_rows":0},[]
    candidates=valid=volume_zero=missing=below_bound=upper_bound=other_fail=near_min=0
    per_symbol=Counter(); out=[]
    for row in reader:
        if str(row.get("FinInstrmTp","")).strip().upper()!="OPTIDX": continue
        symbol=str(row.get("TckrSymb","")).strip().upper()
        side=str(row.get("OptnTp","")).strip().upper()
        if symbol not in SYMBOLS or side not in {"CE","PE"}: continue
        volume=num(row.get("TtlTradgVol"))
        if volume is None or volume<=0:
            volume_zero+=1; continue
        candidates+=1
        expiry=parse_date(row.get("FininstrmActlXpryDt"))
        strike=num(row.get("StrkPric")); premium=num(row.get("ClsPric")); spot=num(row.get("UndrlygPric"))
        oi=num(row.get("OpnIntrst"))
        if not expiry or not strike or strike<=0 or not premium or premium<=0 or not spot or spot<=0:
            missing+=1; continue
        if expiry<=trade_date:
            other_fail+=1; continue
        t=(expiry-trade_date).days/365.0
        vol,status=implied_vol(premium,spot,strike,t,RISK_FREE,side,DIVIDEND_YIELD)
        if vol is None:
            if status=="PREMIUM_BELOW_MODEL_LOWER_BOUND": below_bound+=1
            elif status=="PREMIUM_ABOVE_MODEL_UPPER_BOUND": upper_bound+=1
            else: other_fail+=1
            continue
        g=greeks(spot,strike,t,RISK_FREE,vol,side,DIVIDEND_YIELD)
        if not g or not all(math.isfinite(v) for v in g.values()):
            other_fail+=1; continue
        if status=="AT_OR_NEAR_MIN_VOL": near_min+=1
        valid+=1; per_symbol[symbol]+=1
        out.append({
          "trade_date":trade_date.isoformat(),"symbol":symbol,"expiry":expiry.isoformat(),
          "strike":strike,"side":side,"premium_close":premium,"spot_close":spot,
          "volume":volume,"open_interest":oi,"lot_size":num(row.get("NewBrdLotQty")),
          "time_to_expiry_years":t,"risk_free_rate":RISK_FREE,"dividend_yield_assumption":DIVIDEND_YIELD,
          "iv_model_estimate":vol,"delta_model":g["delta"],"gamma_model":g["gamma"],
          "vega_per_vol_point_model":g["vega_per_vol_point"],"theta_per_calendar_day_model":g["theta_per_calendar_day"],
          "iv_status":status,
        })
    out.sort(key=lambda r:(r["symbol"],r["expiry"],r["strike"],r["side"]))
    packed=json.dumps(out,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return {
      "status":"PARSED_UDIFF","trade_date":trade_date.isoformat(),"schema":"UDiFF",
      "archive_sha256":hashlib.sha256(raw).hexdigest(),"source_rows":candidates,
      "valid_model_rows":valid,"zero_or_invalid_volume_rows":volume_zero,"missing_contract_price_or_spot_rows":missing,
      "premium_below_model_bound_rows":below_bound,"premium_above_model_bound_rows":upper_bound,
      "other_solver_failures":other_fail,"near_minimum_vol_rows":near_min,
      "valid_rows_by_symbol_json":json.dumps(dict(sorted(per_symbol.items())),sort_keys=True),
      "model_rows_sha256":hashlib.sha256(packed).hexdigest(),
      "model":"European Black-Scholes, flat r=6.5% and q=0; estimate from EOD closing premium and UDiFF spot",
    },out


def main():
    DEST.mkdir(parents=True,exist_ok=True); OUT.mkdir(parents=True,exist_ok=True)
    summaries=[]
    for path in sorted(SOURCE.glob("*/*.zip")):
        try: trade_date=datetime.strptime(path.stem,"%Y%m%d").date()
        except ValueError: continue
        if trade_date<FIRST_EXECUTABLE_DATE: continue
        target=DEST/path.parent.name/(path.stem+".json.gz")
        target.parent.mkdir(parents=True,exist_ok=True)
        try:
            if target.exists():
                with gzip.open(target,"rt",encoding="utf-8") as fh:
                    cached=json.load(fh)
                if cached.get("source_archive_sha256")==hashlib.sha256(path.read_bytes()).hexdigest():
                    row=dict(cached.get("summary",{})); row["cache_state"]="HIT"
                    summaries.append(row); continue
            summary,rows=derive_day(path,trade_date)
            with gzip.open(target,"wt",encoding="utf-8",compresslevel=6) as fh:
                json.dump({"summary":summary,"rows":rows},fh,separators=(",",":"),ensure_ascii=False)
            summary["cache_state"]="COMPUTED"
        except Exception as exc:
            summary={"status":"FAILED","trade_date":trade_date.isoformat(),"error_summary":type(exc).__name__+":"+str(exc)[:220]}
        summaries.append(summary)
        if len(summaries)%25==0:
            print(json.dumps({"processed_dates":len(summaries),"valid_model_rows":sum(int(x.get("valid_model_rows",0) or 0) for x in summaries)},sort_keys=True),flush=True)
    fields=sorted({k for r in summaries for k in r})
    with (OUT/"options_model_greeks_daily_audit.csv").open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields,extrasaction="ignore"); w.writeheader();w.writerows(summaries)
    parsed=[r for r in summaries if r.get("status")=="PARSED_UDIFF"]
    report={
      "generated_utc":datetime.now(timezone.utc).isoformat(),
      "first_date":min((r.get("trade_date","") for r in parsed),default=""),
      "last_date":max((r.get("trade_date","") for r in parsed),default=""),
      "source":"Official NSE UDiFF exact-contract EOD option records",
      "risk_free_rate_assumption":RISK_FREE,"dividend_yield_assumption":DIVIDEND_YIELD,
      "model":"European Black-Scholes, flat continuously compounded 6.5% risk-free rate and 0% dividend yield; model-implied IV is solved from closing premium, UDiFF spot, strike and expiry. Greeks are calculated at that IV.",
      "archive_dates_attempted":len(summaries),"udiff_dates_parsed":len(parsed),
      "valid_model_greek_rows":sum(int(r.get("valid_model_rows",0) or 0) for r in parsed),
      "positive_volume_contract_rows_considered":sum(int(r.get("source_rows",0) or 0) for r in parsed),
      "zero_volume_rows_excluded":sum(int(r.get("zero_or_invalid_volume_rows",0) or 0) for r in parsed),
      "missing_contract_price_or_spot_rows":sum(int(r.get("missing_contract_price_or_spot_rows",0) or 0) for r in parsed),
      "premium_below_model_bound_rows":sum(int(r.get("premium_below_model_bound_rows",0) or 0) for r in parsed),
      "premium_above_model_bound_rows":sum(int(r.get("premium_above_model_bound_rows",0) or 0) for r in parsed),
      "other_solver_failures":sum(int(r.get("other_solver_failures",0) or 0) for r in parsed),
      "near_minimum_vol_rows":sum(int(r.get("near_minimum_vol_rows",0) or 0) for r in parsed),
      "failed_dates":sum(1 for r in summaries if r.get("status")=="FAILED"),
      "blocked_non_udiff_dates":sum(1 for r in summaries if r.get("status")=="BLOCKED_NON_UDIFF_OR_MISSING_SPOT"),
      "private_cache_bytes":sum(p.stat().st_size for p in DEST.glob("*/*.json.gz")),
      "raw_greeks_publicly_published":False,
      "execution_warning":"Exact contract IDs are preserved but marks are EOD closes and can be stale. Model IV/Greeks are not direct market Greeks; no bid/ask/depth or achieved fills.",
      "status":"PASS" if parsed and not any(int(r.get("failed_dates",0) or 0) for r in summaries) and sum(int(r.get("valid_model_rows",0) or 0) for r in parsed)>0 else "PARTIAL_OR_FAILED",
    }
    (OUT/"options_model_greeks_summary.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    lines=[
      "# Exact-contract model-derived IV and Greeks audit","",
      "Status: **"+report["status"]+"**",
      "Window: "+report["first_date"]+" through "+report["last_date"],
      "Model: European Black-Scholes, flat r=6.5%, q=0%; only the UDiFF sample from 1 October 2024 onward is used for model features.",
      "",
      "| Metric | Count |","|---|---:|",
      "| UDiFF archive dates parsed | "+format(report["udiff_dates_parsed"],",")+" |",
      "| Positive-volume contract rows considered | "+format(report["positive_volume_contract_rows_considered"],",")+" |",
      "| Valid model IV/Greeks rows | "+format(report["valid_model_greek_rows"],",")+" |",
      "| Zero/invalid-volume rows excluded | "+format(report["zero_volume_rows_excluded"],",")+" |",
      "| Missing contract price/spot/expiry rows | "+format(report["missing_contract_price_or_spot_rows"],",")+" |",
      "| Premium below model lower bound | "+format(report["premium_below_model_bound_rows"],",")+" |",
      "| Premium above model upper bound | "+format(report["premium_above_model_bound_rows"],",")+" |",
      "| Other solver/Greek failures | "+format(report["other_solver_failures"],",")+" |",
      "| Near-minimum IV fits | "+format(report["near_minimum_vol_rows"],",")+" |",
      "| Failed dates | "+format(report["failed_dates"],",")+" |",
      "| Private model-feature cache bytes | "+format(report["private_cache_bytes"],",")+" |","",
      "## Important modelling limits","",
      "These IV and Greeks are *model-estimated*, not exchange-published. Constant 6.5% interest and zero dividend yield are assumptions; future work must stress the rate, cross-check against Dhan's rolling ATM IV, reject implausible estimates, and assess sensitivity to stale EOD marks. Contracts with zero volume are excluded; positive volume does not prove an executable fill or bid/ask quality. The public report deliberately excludes contract-level premiums/Greeks; detailed records remain in the private Actions cache.",
    ]
    (OUT/"OPTIONS_MODEL_GREEKS_AUDIT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({k:report[k] for k in ("status","udiff_dates_parsed","valid_model_greek_rows",
      "positive_volume_contract_rows_considered","premium_below_model_bound_rows","premium_above_model_bound_rows",
      "near_minimum_vol_rows","failed_dates","blocked_non_udiff_dates","private_cache_bytes")},sort_keys=True))


if __name__=="__main__": main()
