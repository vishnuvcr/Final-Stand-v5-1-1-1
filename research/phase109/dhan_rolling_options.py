#!/usr/bin/env python3
"""Dhan rolling weekly ATM historical options data: feature-only acquisition.

Important: rolling ATM observations can change strike/contract over time. These
rows are supplementary point-in-time IV/OI/volume signals only; never use them as
a fixed-contract option entry/exit series or claim fill realism.
Raw rows live only under data/cache/phase109 and are not public artifacts.
"""
import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import random
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

CACHE=Path("data/cache/phase109/dhan_rolling")
OUT=Path("results/phase109")
API="https://api.dhan.co/v2/charts/rollingoption"
SECURITY_ID=13  # NIFTY index security ID used in successful Phase 109 auth/schema probe.
FIELDS=["open","high","low","close","iv","volume","strike","oi","spot"]
START_DEFAULT="2024-10-01"
END_DEFAULT="2026-10-09"  # exclusive


def chunks(start,end_exclusive):
    cur=start
    while cur<end_exclusive:
        last=min(end_exclusive-timedelta(days=1),cur+timedelta(days=29))
        yield cur,last
        cur=last+timedelta(days=1)


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False)


def digest_bytes(b):
    return hashlib.sha256(b).hexdigest()


def request_rows(token, side, start, end):
    request_body={
      "exchangeSegment":"NSE_FNO",
      "interval":"5",
      "securityId":SECURITY_ID,
      "instrument":"OPTIDX",
      "expiryFlag":"WEEK",
      "expiryCode":1,
      "strike":"ATM",
      "drvOptionType":"CALL" if side=="ce" else "PUT",
      "requiredData":FIELDS,
      "fromDate":start.isoformat(),
      "toDate":end.isoformat(),
    }
    last_error=""
    for attempt in range(3):
        req=urllib.request.Request(API,data=json.dumps(request_body).encode("utf-8"),headers={
          "Accept":"application/json",
          "Content-Type":"application/json",
          "access-token":token,
          "User-Agent":"FinalStandPhase109/1.0",
        },method="POST")
        try:
            with urllib.request.urlopen(req,timeout=60) as response:
                status=response.status
                raw=response.read()
            parsed=json.loads(raw.decode("utf-8-sig"))
            data=parsed.get("data",{}) if isinstance(parsed,dict) else {}
            result=data.get(side,{}) if isinstance(data,dict) else {}
            if not isinstance(result,dict):
                raise ValueError("unexpected side payload type")
            array_fields={k:v for k,v in result.items() if isinstance(v,list)}
            lengths=[len(v) for v in array_fields.values()]
            n=len(result.get("timestamp",[])) if isinstance(result.get("timestamp"),list) else (max(lengths) if lengths else 0)
            rows=[]
            for idx in range(n):
                row={}
                for key,values in array_fields.items():
                    if idx<len(values):
                        row[key]=values[idx]
                rows.append(row)
            if not rows and isinstance(parsed,dict) and parsed.get("status") is False:
                raise ValueError("Dhan API status=false")
            return status,rows,digest_bytes(raw),""
        except urllib.error.HTTPError as exc:
            # Do not inspect or publish response text for authenticated requests.
            last_error="HTTP_"+str(exc.code)
        except Exception as exc:
            last_error=type(exc).__name__+":"+str(exc)[:160]
        time.sleep((attempt+1)*1.5+random.random())
    return None,[], "", last_error


def numeric(v):
    try:
        x=float(v)
        return x if math.isfinite(x) else None
    except (TypeError,ValueError,OverflowError):
        return None


def audit_rows(rows):
    timestamps=[]
    strikes=[]
    bad_ohlc=bad_iv=bad_vol=bad_oi=bad_spot=0
    duplicate_ts=0
    seen=set()
    iv_values=[]
    by_day=set()
    for r in rows:
        ts=str(r.get("timestamp",""))
        if ts:
            timestamps.append(ts)
            day=ts[:10]
            if len(day)==10 and day[4]=="-" and day[7]=="-":
                by_day.add(day)
            key=(ts,str(r.get("strike","")))
            if key in seen: duplicate_ts+=1
            seen.add(key)
        strike=numeric(r.get("strike"))
        if strike is not None and strike>0: strikes.append(strike)
        vals=[numeric(r.get(k)) for k in ("open","high","low","close")]
        if any(v is None for v in vals):
            bad_ohlc+=1
        else:
            o,h,l,c=vals
            if min(vals)<=0 or h<max(o,l,c) or l>min(o,h,c):
                bad_ohlc+=1
        iv=numeric(r.get("iv"))
        if iv is not None and iv>0: iv_values.append(iv)
        if iv is None or iv<=0: bad_iv+=1
        vol=numeric(r.get("volume"))
        if vol is None or vol<0: bad_vol+=1
        oi=numeric(r.get("oi"))
        if oi is None or oi<0: bad_oi+=1
        spot=numeric(r.get("spot"))
        if spot is None or spot<=0: bad_spot+=1
    strikes_unique=sorted(set(strikes))
    return {
      "rows":len(rows),"unique_observed_dates":len(by_day),
      "min_timestamp":min(timestamps) if timestamps else "",
      "max_timestamp":max(timestamps) if timestamps else "",
      "positive_unique_strikes":len(strikes_unique),
      "strike_transition_count":sum(1 for a,b in zip(rows,rows[1:]) if a.get("strike")!=b.get("strike")),
      "duplicate_timestamp_strike_keys":duplicate_ts,
      "invalid_ohlc_rows":bad_ohlc,"invalid_or_missing_iv_rows":bad_iv,
      "invalid_or_missing_volume_rows":bad_vol,"invalid_or_missing_oi_rows":bad_oi,
      "invalid_or_missing_spot_rows":bad_spot,
      "iv_minimum_observed":min(iv_values) if iv_values else None,
      "iv_maximum_observed":max(iv_values) if iv_values else None,
      "raw_rows_sha256":digest_bytes(canonical(rows).encode()),
      "series_label":"Dhan rolling weekly ATM selector; may switch strike/contract through time; feature-only",
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--from-date",default=START_DEFAULT)
    ap.add_argument("--to-date",default=END_DEFAULT,help="exclusive")
    ap.add_argument("--force",action="store_true")
    args=ap.parse_args()
    start=date.fromisoformat(args.from_date); end=date.fromisoformat(args.to_date)
    if end<=start: raise ValueError("to-date must be after from-date")
    token=os.environ.get("DHAN_ACCESS_TOKEN","").strip()
    if not token:
        raise RuntimeError("No Dhan token was mapped from repository secrets; token values are never printed.")
    CACHE.mkdir(parents=True,exist_ok=True); OUT.mkdir(parents=True,exist_ok=True)
    summaries=[]; failures=[]
    raw_total_bytes=0
    for left,right in chunks(start,end):
        for side in ("ce","pe"):
            cache_file=CACHE/f"nifty_weekly_atm_{side}_{left:%Y%m%d}_{right:%Y%m%d}.json.gz"
            entry={"window_start":left.isoformat(),"window_end":right.isoformat(),"side":side.upper(),
                   "security_id":SECURITY_ID,"cache_file":str(cache_file)}
            rows=None; cache_digest=""
            if cache_file.exists() and not args.force:
                try:
                    with gzip.open(cache_file,"rt",encoding="utf-8") as fh:
                        cached=json.load(fh)
                    if cached.get("window_start")==left.isoformat() and cached.get("window_end")==right.isoformat() and isinstance(cached.get("rows"),list):
                        rows=cached["rows"]; cache_digest=cached.get("response_sha256","")
                        entry["cache_state"]="HIT"
                except Exception:
                    cache_file.unlink(missing_ok=True)
                    rows=None
            if rows is None:
                status,rows,response_sha,error=request_rows(token,side,left,right)
                entry["http_status"]=status
                if status==200 and rows:
                    packed={"window_start":left.isoformat(),"window_end":right.isoformat(),
                            "side":side,"security_id":SECURITY_ID,"rows":rows,
                            "response_sha256":response_sha}
                    with gzip.open(cache_file,"wt",encoding="utf-8",compresslevel=6) as fh:
                        json.dump(packed,fh,separators=(",",":"),ensure_ascii=False)
                    cache_digest=response_sha
                    entry["cache_state"]="DOWNLOADED"
                elif status==200 and not rows:
                    entry["cache_state"]="HTTP_OK_EMPTY_OR_SCHEMA_MISMATCH"
                    entry["error_summary"]="empty side payload or returned field names need inspection"
                    failures.append({k:entry.get(k) for k in ("window_start","window_end","side","http_status","cache_state","error_summary")})
                else:
                    entry["cache_state"]="FAILED"
                    entry["error_summary"]=error or "unknown_error"
                    failures.append({k:entry.get(k) for k in ("window_start","window_end","side","http_status","cache_state","error_summary")})
                    rows=[]
            audit=audit_rows(rows)
            entry.update(audit)
            entry["response_or_cache_sha256"]=cache_digest
            if cache_file.exists(): raw_total_bytes+=cache_file.stat().st_size
            summaries.append(entry)
            print(json.dumps({"window_start":left.isoformat(),"window_end":right.isoformat(),"side":side,
                              "cache_state":entry.get("cache_state"),"bars":len(rows)},sort_keys=True),flush=True)
            time.sleep(1.1)
    merged={
      "from_date":start.isoformat(),"to_date_exclusive":end.isoformat(),
      "rows":sum(x.get("rows",0) for x in summaries),
      "call_rows":sum(x.get("rows",0) for x in summaries if x["side"]=="CE"),
      "put_rows":sum(x.get("rows",0) for x in summaries if x["side"]=="PE"),
      "unique_dates":len(set(x for s in summaries for x in ())),
      "invalid_ohlc_rows":sum(x.get("invalid_ohlc_rows",0) for x in summaries),
      "invalid_iv_rows":sum(x.get("invalid_or_missing_iv_rows",0) for x in summaries),
      "invalid_volume_rows":sum(x.get("invalid_or_missing_volume_rows",0) for x in summaries),
      "invalid_oi_rows":sum(x.get("invalid_or_missing_oi_rows",0) for x in summaries),
      "invalid_spot_rows":sum(x.get("invalid_or_missing_spot_rows",0) for x in summaries),
      "duplicate_timestamp_strike_keys":sum(x.get("duplicate_timestamp_strike_keys",0) for x in summaries),
      "private_cache_compressed_bytes":raw_total_bytes,
      "failure_count":len(failures),
      "attempt_count":len(summaries),
      "successful_chunks":sum(1 for x in summaries if x.get("rows",0)>0),
      "status":"PASS" if summaries and not failures and all(x.get("rows",0)>0 and x.get("invalid_ohlc_rows",0)==0 for x in summaries) else "PARTIAL_OR_FAILED",
      "note":"Rolling ATM feature data only. Strike/contract can change across time. Not a fixed-contract premium series; not used as entry/exit fills.",
    }
    report={
      "generated_utc":datetime.now(timezone.utc).isoformat(),
      "source":"Dhan rolling expired-options API",
      "endpoint":API,
      "contract_mapping":"NIFTY index securityId=13; weekly expiry code 1, ATM selector; CALL and PUT queried separately",
      "field_set":FIELDS,
      "summary":merged,"chunk_audits":summaries,"errors":failures,
    }
    (OUT/"dhan_rolling_options_audit.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    lines=[
      "# Dhan rolling weekly ATM historical-options audit","",
      "Generated: "+report["generated_utc"],
      "Requested: "+start.isoformat()+" through "+end.isoformat()+" (end exclusive).",
      "Status: **"+merged["status"]+"**","",
      "| Metric | Value |","|---|---:|",
      "| Chunks attempted | "+format(merged["attempt_count"],",")+" |",
      "| Successful non-empty chunks | "+format(merged["successful_chunks"],",")+" |",
      "| Five-minute bars, call side | "+format(merged["call_rows"],",")+" |",
      "| Five-minute bars, put side | "+format(merged["put_rows"],",")+" |",
      "| Invalid OHLC rows | "+format(merged["invalid_ohlc_rows"],",")+" |",
      "| Invalid/missing IV rows | "+format(merged["invalid_iv_rows"],",")+" |",
      "| Invalid/missing volume rows | "+format(merged["invalid_volume_rows"],",")+" |",
      "| Invalid/missing OI rows | "+format(merged["invalid_oi_rows"],",")+" |",
      "| Invalid/missing spot rows | "+format(merged["invalid_spot_rows"],",")+" |",
      "| Duplicate timestamp-strike keys | "+format(merged["duplicate_timestamp_strike_keys"],",")+" |",
      "| Private compressed-cache bytes | "+format(merged["private_cache_compressed_bytes"],",")+" |",
      "| Failed/empty chunk-side calls | "+format(merged["failure_count"],",")+" |","",
      "## Interpretation","",
      "The data are rolling weekly ATM observations, not a fixed-strike or fixed-expiry price series. Strike transitions are explicitly measured per chunk. Use these fields only for lagged features/confirmation after timestamp, IV units, OI semantics and release-time alignment are validated. Do not score any entry/exit from these records, and do not claim executable fills.",
      "Raw authenticated rows remain in private Actions cache; public output contains aggregate quality checks and hashes only. No token or authenticated raw-response body is committed.",
    ]
    (OUT/"DHAN_ROLLING_OPTIONS_AUDIT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(merged,sort_keys=True))


if __name__=="__main__": main()
