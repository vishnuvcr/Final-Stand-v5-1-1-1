#!/usr/bin/env python3
"""Bounded aggregate-only comparison of Dhan rolling-option expiry codes and strike series."""
import datetime as dt, json, os, time, urllib.request, urllib.error
from pathlib import Path
from zoneinfo import ZoneInfo
API="https://api.dhan.co/v2/charts/rollingoption"
OUT=Path("results/phase73_expiry_strike_mapping")
DATES=["2026-07-28","2026-08-04"]
IST=ZoneInfo("Asia/Kolkata")
FIELDS=["open","high","low","close","iv","volume","oi","spot","strike"]
def stamp(v):
    try:
        x=float(v)
        if x>1e12: x/=1000
        return dt.datetime.fromtimestamp(x,dt.timezone.utc).astimezone(IST)
    except (TypeError,ValueError,OSError,OverflowError): return None
def series_of(body,side):
    data=body.get("data",{}) if isinstance(body,dict) else {}
    for k in (side.lower(),"ce" if side=="CALL" else "pe"):
        if isinstance(data,dict) and isinstance(data.get(k),dict): return data[k]
    return {}
def audit(body,day,flag,code,side):
    s=series_of(body,side)
    ts=s.get("timestamp",[]) if isinstance(s.get("timestamp",[]),list) else []
    parsed=[stamp(x) for x in ts]; valid=[x for x in parsed if x]
    target=[x for x in valid if x.date().isoformat()==day]
    regular=[x for x in target if dt.time(9,15)<=x.time().replace(tzinfo=None)<dt.time(15,30)]
    strikes=s.get("strike",[]) if isinstance(s.get("strike",[]),list) else []
    nums=[]
    for x in strikes:
        try:
            v=float(x)
            if v>0: nums.append(v)
        except (TypeError,ValueError): pass
    lengths={f:(len(s[f]) if isinstance(s.get(f),list) else None) for f in FIELDS}
    aligned={f:n==len(ts) for f,n in lengths.items() if n is not None}
    return {"date":day,"expiry_flag":flag,"expiry_code":code,"side":side,
      "timestamp_count":len(ts),"target_date_count":len(target),"regular_session_count":len(regular),
      "off_session_count":len(target)-len(regular),
      "first_target_ist":min(target).isoformat() if target else None,
      "last_target_ist":max(target).isoformat() if target else None,
      "duplicate_timestamp_count":len(valid)-len(set(x.timestamp() for x in valid)),
      "strike_array_length":len(strikes),"strike_unique_count":len(set(nums)),
      "strike_min":min(nums) if nums else None,"strike_max":max(nums) if nums else None,
      "field_alignment":aligned,"status":"AUDIT_RECORDED"}
def main():
    token=os.environ.get("DHAN_ACCESS_TOKEN","").strip()
    checked=dt.datetime.now(dt.timezone.utc).isoformat()
    if not token:
        result={"checked_at_utc":checked,"decision":"BLOCKED_NO_DHAN_ACCESS_TOKEN","probes":[],"interpretation":"No authenticated requests were run."}
        emit(result); print(result["decision"]); return
    probes=[]; errors=[]
    for day in DATES:
      end=(dt.date.fromisoformat(day)+dt.timedelta(days=1)).isoformat()
      for flag in ("WEEK","MONTH"):
       for code in (0,1,2):
        for side in ("CALL","PUT"):
         body={"exchangeSegment":"NSE_FNO","interval":"1","securityId":13,"instrument":"OPTIDX",
          "expiryFlag":flag,"expiryCode":code,"strike":"ATM","drvOptionType":side,
          "requiredData":FIELDS,"fromDate":day,"toDate":end}
         req=urllib.request.Request(API,data=json.dumps(body).encode(),headers={"Accept":"application/json","Content-Type":"application/json","access-token":token},method="POST")
         try:
          with urllib.request.urlopen(req,timeout=45) as response: payload=json.loads(response.read().decode())
          row=audit(payload,day,flag,code,side); probes.append(row)
          if not row["timestamp_count"]: errors.append(f"{day}/{flag}/{code}/{side}: empty timestamp series")
         except urllib.error.HTTPError as exc:
          probes.append({"date":day,"expiry_flag":flag,"expiry_code":code,"side":side,"status":f"HTTP_{exc.code}"})
          errors.append(f"{day}/{flag}/{code}/{side}: HTTP {exc.code}")
         except Exception as exc:
          probes.append({"date":day,"expiry_flag":flag,"expiry_code":code,"side":side,"status":"REQUEST_OR_PARSE_ERROR"})
          errors.append(f"{day}/{flag}/{code}/{side}: {type(exc).__name__}")
         time.sleep(0.25)
    done=[p for p in probes if p.get("status")=="AUDIT_RECORDED"]
    result={"checked_at_utc":checked,"decision":"COMPARISON_RECORDED_REVIEW_REQUIRED" if len(done)==24 else "PARTIAL_OR_FAILED_COMPARISON",
      "targets":DATES,"expiry_code_reference":{"0":"current/near expiry","1":"next expiry","2":"far expiry"},
      "probes":probes,"errors":errors,
      "interpretation":f"Recorded {len(done)}/24 probes. This compares rolling ATM strike-series metadata and counts; the endpoint does not establish the exact expiry date from these aggregates. Map target contracts independently before replay. Rolling ATM strikes are not absolute-strike history; no executable quote/depth data or profitability inference is available."}
    emit(result); print(result["decision"])
def emit(r):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"summary.json").write_text(json.dumps(r,indent=2,allow_nan=False)+"\n")
    lines=["# Phase 73 — DhanHQ expiry-code and strike mapping audit","",f"Decision: **{r['decision']}**","",f"Checked UTC: {r['checked_at_utc']}","",
      "| Date | Flag | Code | Side | Total rows | Target rows | Regular | Off-session | Strike unique | Strike range | Aligned |",
      "|---|---|---:|---|---:|---:|---:|---:|---:|---|---|"]
    for p in r.get("probes",[]):
      aligned=all(p.get("field_alignment",{}).values()) if p.get("field_alignment") else False
      rng=f"{p.get('strike_min')}–{p.get('strike_max')}" if p.get("strike_min") is not None else "n/a"
      lines.append(f"| {p.get('date')} | {p.get('expiry_flag')} | {p.get('expiry_code')} | {p.get('side')} | {p.get('timestamp_count',0)} | {p.get('target_date_count',0)} | {p.get('regular_session_count',0)} | {p.get('off_session_count',0)} | {p.get('strike_unique_count',0)} | {rng} | {aligned} |")
    lines += ["","## Interpretation","",r["interpretation"],"","Only aggregate metadata is stored; raw market rows and credentials are not committed."]
    (OUT/"report.md").write_text("\n".join(lines)+"\n")
if __name__=="__main__": main()
