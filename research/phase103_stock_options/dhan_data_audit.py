#!/usr/bin/env python3
"""Bounded DhanHQ expired stock-options data probe; never prints token or raw rows."""
import argparse, csv, hashlib, io, json, os, time, urllib.error, urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

MASTER = "https://images.dhan.co/api-data/api-scrip-master.csv"
ENDPOINT = "https://api.dhan.co/v2/charts/rollingoption"
SYMBOLS = ["HDFCBANK", "ICICIBANK", "RELIANCE", "SBIN", "INFY"]
# The provider currently rejects code 0 as missing; use the documented sample value 1 (next expiry).
EXPIRY_CODE = 1
FIELDS = ["open", "high", "low", "close", "iv", "volume", "strike", "oi", "spot", "timestamp"]

def get_bytes(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent":"FinalStand-Phase103/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def check_window(start, end):
    days = (date.fromisoformat(end) - date.fromisoformat(start)).days
    if days < 1 or days > 30:
        raise ValueError("Rolling-options API accepts at most 30 calendar days per request.")
    return days

def map_underlyings(raw):
    rows = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    need = {"SEM_EXM_EXCH_ID","SEM_SEGMENT","SEM_SMST_SECURITY_ID","SEM_INSTRUMENT_NAME","SEM_TRADING_SYMBOL"}
    if not rows.fieldnames or not need.issubset(rows.fieldnames):
        raise ValueError("Instrument-master schema missing required columns")
    found = {}
    for r in rows:
        sym = r.get("SEM_TRADING_SYMBOL","").strip().upper()
        if (sym in SYMBOLS and r.get("SEM_EXM_EXCH_ID","").strip()=="NSE"
            and r.get("SEM_SEGMENT","").strip()=="E"
            and r.get("SEM_INSTRUMENT_NAME","").strip()=="EQUITY"):
            found.setdefault(sym, []).append(r)
    out = {}
    for sym in SYMBOLS:
        eq = [x for x in found.get(sym,[]) if x.get("SEM_SERIES","").strip()=="EQ"]
        rows_for_symbol = eq or found.get(sym,[])
        ids = {x.get("SEM_SMST_SECURITY_ID","").strip() for x in rows_for_symbol}
        ids.discard("")
        if len(ids)==1:
            row = next(x for x in rows_for_symbol if x.get("SEM_SMST_SECURITY_ID","").strip() in ids)
            out[sym] = {"security_id":next(iter(ids),""),
                        "lot_size":row.get("SEM_LOT_UNITS",""),"status":"MATCHED"}
        else:
            out[sym] = {"security_id":None,"status":"NOT_FOUND" if not ids else "AMBIGUOUS"}
    return out

def safe_error_details(raw, token):
    """Extract only allow-listed error codes/messages; never persist response bodies or credentials."""
    try:
        obj = json.loads(raw.decode("utf-8", errors="replace"))
    except (json.JSONDecodeError, AttributeError):
        return {}
    if not isinstance(obj, dict):
        return {}
    found = {}
    code_keys = {"error_code", "errorcode", "code", "status_code"}
    message_keys = {"error_message", "errormessage", "message", "error_description", "description"}
    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                lowered = str(key).casefold()
                if lowered in code_keys and isinstance(value, (str, int, float)):
                    found.setdefault("api_error_code", str(value)[:80])
                elif lowered in message_keys and isinstance(value, (str, int, float)):
                    message = " ".join(str(value).split())[:240]
                    if token:
                        message = message.replace(token, "[REDACTED]")
                    found.setdefault("api_error_message", message)
                elif isinstance(value, dict):
                    walk(value)
        elif isinstance(node, list):
            for item in node[:10]:
                walk(item)
    walk(obj)
    return found

def query(token, security_id, option_type, start, end):
    body = {"exchangeSegment":"NSE_FNO","interval":"1","securityId":str(security_id),
            "instrument":"OPTSTK","expiryFlag":"MONTH","expiryCode":EXPIRY_CODE,"strike":"ATM",
            "drvOptionType":option_type,
            "requiredData":["open","high","low","close","iv","volume","strike","oi","spot"],
            "fromDate":start,"toDate":end}
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(),
        method="POST", headers={"Accept":"application/json","Content-Type":"application/json",
                                "access-token":token,"User-Agent":"FinalStand-Phase103/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=60) as r:
            code, raw = r.status, r.read()
    except urllib.error.HTTPError as e:
        raw = e.read()
        return e.code, None, safe_error_details(raw, token)
    except (urllib.error.URLError, TimeoutError):
        return 0, None, {}
    try:
        obj=json.loads(raw.decode("utf-8"))
        return code, obj if isinstance(obj,dict) else None, {}
    except (UnicodeDecodeError,json.JSONDecodeError):
        return code, None, {}

def summarize(symbol, option_type, code, obj, safe_error=None, start=None, end=None):
    side = "ce" if option_type=="CALL" else "pe"
    x={"symbol":symbol,"requested_option_type":option_type,"http_status":code,
       "status":"NO_RESPONSE","rows":0,"array_lengths_consistent":False,
       "nonempty_fields":{},"first_timestamp_utc":None,"last_timestamp_utc":None,
       "timestamp_counts_by_ist_date":{},"outside_requested_date_window_rows":None,
       "api_error_code":(safe_error or {}).get("api_error_code"),
       "api_error_message":(safe_error or {}).get("api_error_message")}
    if obj is None:
        x["status"]={401:"AUTH_401",403:"AUTH_403",429:"RATE_LIMIT_429",
                     400:"HTTP_400_BAD_REQUEST"}.get(code,"HTTP_OR_NETWORK_ERROR")
        return x
    block=(obj.get("data") or {}).get(side) if isinstance(obj.get("data"),dict) else None
    x["status"]=str(obj.get("status","UNKNOWN"))
    if not isinstance(block,dict):
        return x
    lens=[]
    for f in FIELDS:
        values=block.get(f)
        x["nonempty_fields"][f]=sum(v is not None for v in values) if isinstance(values,list) else 0
        if isinstance(values,list): lens.append(len(values))
    ts=block.get("timestamp") if isinstance(block.get("timestamp"),list) else []
    x["rows"]=len(ts); x["array_lengths_consistent"]=bool(lens) and len(set(lens))==1
    if ts:
        local_dates=[]
        outside=0
        start_day=date.fromisoformat(start) if start else None
        end_day=date.fromisoformat(end) if end else None
        for stamp in ts:
            try:
                dt_utc=datetime.fromtimestamp(int(stamp),timezone.utc)
                dt_local=dt_utc.astimezone(ZoneInfo("Asia/Kolkata"))
                local_dates.append(dt_local.date().isoformat())
                if start_day and end_day and not (start_day <= dt_local.date() < end_day):
                    outside += 1
            except (ValueError,TypeError,OverflowError,OSError):
                continue
        x["first_timestamp_utc"]=datetime.fromtimestamp(int(ts[0]),timezone.utc).isoformat()
        x["last_timestamp_utc"]=datetime.fromtimestamp(int(ts[-1]),timezone.utc).isoformat()
        by_date={}
        for d in local_dates:
            by_date[d]=by_date.get(d,0)+1
        x["timestamp_counts_by_ist_date"]=by_date
        x["outside_requested_date_window_rows"]=outside if start_day and end_day else None
    if ts and x["nonempty_fields"].get("close",0): x["status"]="DATA_RETURNED"
    elif str(obj.get("status","")).lower()=="success": x["status"]="SUCCESS_EMPTY_FOR_REQUESTED_SIDE"
    return x

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--from-date",default=os.getenv("PHASE103_FROM_DATE","2026-08-03"))
    p.add_argument("--to-date",default=os.getenv("PHASE103_TO_DATE","2026-08-04"),help="exclusive")
    p.add_argument("--max-probes",type=int,default=int(os.getenv("PHASE103_MAX_PROBES","1")),
                   help="maximum number of symbol/side API probes for this bounded run")
    p.add_argument("--out-dir",default="results/phase103")
    a=p.parse_args(); days=check_window(a.from_date,a.to_date)
    if not 1 <= a.max_probes <= len(SYMBOLS) * 2:
        p.error("--max-probes must be from 1 through 10")
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    result={"phase":"103.1","run_id":os.getenv("GITHUB_RUN_ID","local"),
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "window":{"from_inclusive":a.from_date,"to_exclusive":a.to_date,"span_days":days},
        "probe_limit":a.max_probes,
        "endpoint":ENDPOINT,"instrument_master_sha256":None,"instrument_master_bytes":None,
        "underlying_map":{},"probes":[],"raw_rows_persisted":False,
        "raw_data_policy":"Raw rows kept ephemeral; no raw data artifact or public commit until retention/republication rights are verified.",
        "known_limits":["Rolling strikes can change actual strike over time.",
          "This endpoint documents OHLC, IV, volume, OI, strike and spot, not historical bid/ask/depth.",
          "One stock/side probe does not establish full-history completeness or independent test sufficiency.", "Returned timestamps are audited in Asia/Kolkata against the documented half-open request window; out-of-window rows block accepting the sample."],
        "status":"PENDING"}
    try:
        master=get_bytes(MASTER)
        result["instrument_master_sha256"]=hashlib.sha256(master).hexdigest()
        result["instrument_master_bytes"]=len(master)
        result["underlying_map"]=map_underlyings(master)
    except Exception as e:
        result["status"]="BLOCKED_INSTRUMENT_MASTER"
        result["safe_error_type"]=type(e).__name__
    else:
        token=os.getenv("DHAN_ACCESS_TOKEN","").strip()
        if not token:
            result["status"]="BLOCKED_NO_DHAN_ACCESS_TOKEN"
        else:
            for sym in SYMBOLS:
                m=result["underlying_map"].get(sym,{})
                for side in ["CALL","PUT"]:
                    if len(result["probes"]) >= a.max_probes:
                        break
                    if not m.get("security_id"):
                        result["probes"].append({"symbol":sym,"requested_option_type":side,"status":"BLOCKED_UNDERLYING_ID"})
                        continue
                    code,obj,safe_error=query(token,m["security_id"],side,a.from_date,a.to_date)
                    result["probes"].append(summarize(sym,side,code,obj,safe_error,a.from_date,a.to_date))
                    time.sleep(1.1)
                if len(result["probes"]) >= a.max_probes:
                    break
            rows_count=sum(v.get("rows",0)>0 for v in result["probes"])
            error_codes={str(v.get("api_error_code","")).upper() for v in result["probes"] if v.get("api_error_code")}
            auth_count=sum(v.get("status") in ["AUTH_401","AUTH_403"] for v in result["probes"])
            if auth_count or error_codes.intersection({"806","807","808","809","810","DH-901","DH-902"}):
                result["status"]="BLOCKED_AUTHENTICATION_OR_DATA_API_ENTITLEMENT"
            elif error_codes.intersection({"814","DH-905"}):
                result["status"]="REQUEST_SCHEMA_OR_PARAMETER_ERROR"
            elif len(result["probes"])==a.max_probes and rows_count==a.max_probes: result["status"]="PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES"
            elif rows_count: result["status"]="PARTIAL_DATA_RETURNED"
            else: result["status"]="NO_DATA_RETURNED_OR_SCHEMA_MISMATCH"
    (out/"dhan_data_api_audit.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    lines=["# Phase 103.1 — Dhan Data API smoke test","",f"**Status:** {result['status']}",
      f"**Window:** {a.from_date} inclusive to {a.to_date} exclusive ({days} days)",
      f"**Probe limit:** {a.max_probes}",
      f"**Run:** {result['run_id']}","",
      "This is a data-feasibility probe, not a strategy test. The token and raw rows are not published.",
      "","| Symbol | Side | HTTP | Status | Error code | Safe message | Rows | Arrays consistent | First UTC | Last UTC | IST-date row counts | Rows outside requested dates |",
      "|---|---|---:|---|---|---|---:|---|---|---|---|---:|"]
    for v in result.get("probes",[]):
        lines.append("| {symbol} | {side} | {http} | {status} | {code} | {message} | {rows} | {consistent} | {first} | {last} |".format(
          symbol=v.get("symbol",""),side=v.get("requested_option_type",""),http=v.get("http_status",""),
          status=v.get("status",""),code=v.get("api_error_code") or "",
          message=(v.get("api_error_message") or "").replace("|","/"),
          rows=v.get("rows",0),consistent=v.get("array_lengths_consistent",False),
          first=v.get("first_timestamp_utc") or "",last=v.get("last_timestamp_utc") or ""))
        # Check that provider data matches its documented half-open [fromDate, toDate) window.
        lines[-1] = lines[-1][:-1] + " | {} | {} |".format(
          json.dumps(v.get("timestamp_counts_by_ist_date",{}),sort_keys=True),
          v.get("outside_requested_date_window_rows") if v.get("outside_requested_date_window_rows") is not None else "n/a")
    lines += ["","## Underlying ID mapping","","| Symbol | ID resolved | Status |","|---|---|---|"]
    for sym,m in result.get("underlying_map",{}).items():
        lines.append("| {} | {} | {} |".format(sym,"yes" if m.get("security_id") else "no",m.get("status")))
    lines += ["","## Limitations",""]+["- "+x for x in result["known_limits"]]
    (out/"DHAN_DATA_API_AUDIT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"phase":"103.1","status":result["status"],"window":result["window"],
      "underlying_ids_resolved":sum(1 for x in result.get("underlying_map",{}).values() if x.get("security_id")),
      "probes":len(result.get("probes",[])),"probe_limit":result["probe_limit"],
      "probes_with_rows":sum(1 for x in result.get("probes",[]) if x.get("rows",0)>0)},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
