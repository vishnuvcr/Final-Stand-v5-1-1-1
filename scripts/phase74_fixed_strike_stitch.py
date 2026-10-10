#!/usr/bin/env python3
"""Test whether Dhan rolling ATM-relative offsets can be stitched into fixed absolute-strike minute series."""
import datetime as dt, json, math, os, time, urllib.request, urllib.error
from collections import defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo
API="https://api.dhan.co/v2/charts/rollingoption"
OUT=Path("results/phase74_fixed_strike_stitch")
DATES=["2026-07-28","2026-08-04"]
IST=ZoneInfo("Asia/Kolkata")
FIELDS=["open","high","low","close","iv","volume","oi","spot","strike"]
OFFSETS=list(range(-10,11))
def parse_stamp(v):
    try:
        x=float(v)
        if x>1e12: x/=1000
        return dt.datetime.fromtimestamp(x,dt.timezone.utc).astimezone(IST)
    except (TypeError,ValueError,OSError,OverflowError): return None
def get_series(body,side):
    data=body.get("data",{}) if isinstance(body,dict) else {}
    for key in (side.lower(),"ce" if side=="CALL" else "pe"):
        if isinstance(data,dict) and isinstance(data.get(key),dict): return data[key]
    return {}
def emit(report):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"summary.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    lines=["# Phase 74 — Fixed-strike stitch feasibility audit","",f"Decision: **{report['decision']}**","",f"Checked UTC: {report['checked_at_utc']}","",
      "| Date | Flag | Code | Side | Offset probes passed | Session timestamps | Distinct strikes | Best strike coverage | Full 375-bar strikes |",
      "|---|---|---:|---|---:|---:|---:|---:|---:|"]
    for p in report.get("groups",[]):
        lines.append(f"| {p['date']} | {p['expiry_flag']} | {p['expiry_code']} | {p['side']} | {p['offset_probes_passed']}/21 | {p['expected_session_timestamps']} | {p['distinct_absolute_strikes']} | {p['best_strike_coverage']}/{p['expected_session_timestamps']} | {p['full_coverage_strike_count']} |")
    lines += ["","## Interpretation","",report["interpretation"],"","No raw market rows or credentials are stored. Full strike coverage here only demonstrates the mechanics of stitching rolling offsets; it does not establish the exact expiry date or execution-quality fills."]
    (OUT/"report.md").write_text("\n".join(lines)+"\n")
def main():
    token=os.environ.get("DHAN_ACCESS_TOKEN","").strip()
    checked=dt.datetime.now(dt.timezone.utc).isoformat()
    if not token:
        r={"checked_at_utc":checked,"decision":"BLOCKED_NO_DHAN_ACCESS_TOKEN","groups":[],"interpretation":"No authenticated requests were run."}
        emit(r); print(r["decision"]); return
    results=defaultdict(lambda:{"ok_offsets":0,"timestamps":set(),"strikes":defaultdict(set),"field_mismatches":0,"http_errors":0,"request_errors":0})
    errors=[]
    for day in DATES:
      end=(dt.date.fromisoformat(day)+dt.timedelta(days=1)).isoformat()
      for flag in ("WEEK","MONTH"):
       for code in (1,2):
        for side in ("CALL","PUT"):
         key=(day,flag,code,side)
         for offset in OFFSETS:
          strike="ATM" if offset==0 else f"ATM{offset:+d}"
          body={"exchangeSegment":"NSE_FNO","interval":"1","securityId":13,"instrument":"OPTIDX",
            "expiryFlag":flag,"expiryCode":code,"strike":strike,"drvOptionType":side,
            "requiredData":FIELDS,"fromDate":day,"toDate":end}
          req=urllib.request.Request(API,data=json.dumps(body).encode(),headers={"Accept":"application/json","Content-Type":"application/json","access-token":token},method="POST")
          try:
           with urllib.request.urlopen(req,timeout=45) as response: payload=json.loads(response.read().decode())
           s=get_series(payload,side); ts=s.get("timestamp",[]); strikes=s.get("strike",[])
           closes=s.get("close",[])
           if not all(isinstance(x,list) for x in (ts,strikes,closes)) or not (len(ts)==len(strikes)==len(closes)):
            results[key]["field_mismatches"]+=1
           else:
            results[key]["ok_offsets"]+=1
            for t,st,cl in zip(ts,strikes,closes):
             stamp=parse_stamp(t)
             try: absolute=float(st); close=float(cl)
             except (TypeError,ValueError): continue
             if not stamp or stamp.date().isoformat()!=day: continue
             if not (dt.time(9,15)<=stamp.time().replace(tzinfo=None)<dt.time(15,30)): continue
             if not (absolute>0 and close>0 and math.isfinite(absolute) and math.isfinite(close)): continue
             results[key]["timestamps"].add(stamp.timestamp())
             results[key]["strikes"][absolute].add(stamp.timestamp())
          except urllib.error.HTTPError as exc:
           results[key]["http_errors"]+=1
           errors.append(f"{day}/{flag}/{code}/{side}/{strike}: HTTP {exc.code}")
          except Exception as exc:
           results[key]["request_errors"]+=1
           errors.append(f"{day}/{flag}/{code}/{side}/{strike}: {type(exc).__name__}")
          time.sleep(0.22)
    groups=[]
    for (day,flag,code,side),r in sorted(results.items()):
      expected=375
      coverages=sorted((len(v) for v in r["strikes"].values()),reverse=True)
      groups.append({"date":day,"expiry_flag":flag,"expiry_code":code,"side":side,
        "offset_probes_passed":r["ok_offsets"],"http_errors":r["http_errors"],"request_errors":r["request_errors"],
        "field_mismatches":r["field_mismatches"],"expected_session_timestamps":len(r["timestamps"]),
        "distinct_absolute_strikes":len(r["strikes"]),"best_strike_coverage":max(coverages,default=0),
        "full_coverage_strike_count":sum(1 for v in r["strikes"].values() if len(v)>=expected),
        "top_strike_coverage_counts":coverages[:10]})
    complete=len(groups)==16 and all(g["offset_probes_passed"]==21 for g in groups)
    any_full=any(g["full_coverage_strike_count"]>0 for g in groups)
    decision="STITCH_FEASIBILITY_RECORDED_REVIEW_REQUIRED" if complete else "PARTIAL_OR_FAILED_STITCH_TEST"
    interpretation=(f"Completed all 16 date/expiry/side groups: {complete}. At least one absolute strike had all 375 regular-session timestamps in a group: {any_full}. "
      "Inspect group-level coverage and field mismatches. Even full strike continuity does not identify the exact expiry date for code 1/2; verify historical contract mapping independently before replay. No prices are persisted.")
    report={"checked_at_utc":checked,"decision":decision,"targets":DATES,"offsets":OFFSETS,"expiry_codes":[1,2],"groups":groups,
      "errors":errors[:100],"interpretation":interpretation}
    emit(report); print(decision)
if __name__=="__main__": main()
