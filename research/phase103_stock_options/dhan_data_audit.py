#!/usr/bin/env python3
"""Bounded DhanHQ expired stock-options data probe; never prints token or raw rows."""
import argparse, csv, hashlib, io, json, os, time, urllib.error, urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

MASTER = "https://images.dhan.co/api-data/api-scrip-master.csv"
ENDPOINT = "https://api.dhan.co/v2/charts/rollingoption"
SYMBOLS = ["HDFCBANK", "ICICIBANK", "RELIANCE", "SBIN", "INFY"]
DEFAULT_STRIKES = ["ATM", "ATM+1", "ATM+2", "ATM+3", "ATM-1", "ATM-2", "ATM-3"]
ALLOWED_STRIKES = set(DEFAULT_STRIKES)
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
        raise ValueError("The target window must be 1–30 calendar days; end date is exclusive.")
    return days

def provider_to_date(start, target_end_exclusive):
    """Dhan empirically includes toDate; map [start, end) to inclusive provider dates."""
    check_window(start, target_end_exclusive)
    return (date.fromisoformat(target_end_exclusive) - timedelta(days=1)).isoformat()

def parse_strikes(raw):
    values = [x.strip().upper() for x in raw.split(",") if x.strip()]
    if not values:
        raise ValueError("At least one relative strike is required.")
    if len(set(values)) != len(values):
        raise ValueError("Relative strike list contains duplicates.")
    invalid = [x for x in values if x not in ALLOWED_STRIKES]
    if invalid:
        raise ValueError("Unsupported relative strike(s): " + ", ".join(invalid))
    return values

def normalize_strike(value):
    if value is None:
        return None
    try:
        number = float(value)
        if number != number or abs(number) == float("inf"):
            return None
        return format(number, ".10g")
    except (ValueError, TypeError, OverflowError):
        return None

def summarize_surface(surface_blocks, requested_strikes):
    """Aggregate relative-strike alignment; raw rows remain in runner memory only."""
    groups = {}
    for block in surface_blocks:
        groups.setdefault((block["symbol"], block["option_type"]), []).append(block)
    summaries = []
    for (symbol, option_type), blocks in sorted(groups.items()):
        by_offset = {}
        for block in blocks:
            records = {}
            stamps, strikes = block.get("timestamps", []), block.get("strikes", [])
            for i in range(min(len(stamps), len(strikes))):
                try: ts = int(stamps[i])
                except (ValueError, TypeError, OverflowError): continue
                strike = normalize_strike(strikes[i])
                if strike is not None: records[ts] = strike
            vals = list(records.values())
            by_offset[block["relative_strike"]] = {
                "records": records, "timestamp_count": len(records),
                "distinct_actual_strikes": len(set(vals)),
                "actual_strike_changes": sum(vals[i] != vals[i-1] for i in range(1,len(vals))),
                "first_actual_strike": vals[0] if vals else None,
                "last_actual_strike": vals[-1] if vals else None}
        record_sets = [v["records"] for v in by_offset.values()]
        timestamp_sets = [set(x) for x in record_sets]
        union_ts = set().union(*timestamp_sets) if timestamp_sets else set()
        common_ts = set.intersection(*timestamp_sets) if timestamp_sets and all(timestamp_sets) else set()
        strike_per_ts, key_counts, all_strikes = {}, {}, {}
        for records in record_sets:
            for ts, strike in records.items():
                strike_per_ts.setdefault(ts, set()).add(strike)
                key_counts[(ts,strike)] = key_counts.get((ts,strike),0)+1
                all_strikes.setdefault(strike,set()).add(ts)
        unique_counts = [len(x) for x in strike_per_ts.values()]
        duplicates = sum(1 for n in key_counts.values() if n>1)
        complete_strikes = sum(1 for times in all_strikes.values() if union_ts and len(times)==len(union_ts))
        passed = (len(by_offset)==len(requested_strikes) and all(x in by_offset and by_offset[x]["timestamp_count"]>0 for x in requested_strikes)
                  and bool(union_ts) and len(common_ts)==len(union_ts)
                  and all(len(strike_per_ts.get(ts,set()))==len(requested_strikes) for ts in union_ts) and duplicates==0)
        summaries.append({
            "symbol":symbol,"option_type":option_type,"requested_relative_strikes":requested_strikes,
            "offset_series_returned":len(by_offset),"common_timestamp_count_across_offsets":len(common_ts),
            "union_timestamp_count":len(union_ts),
            "minimum_distinct_actual_strikes_per_timestamp":min(unique_counts) if unique_counts else 0,
            "maximum_distinct_actual_strikes_per_timestamp":max(unique_counts) if unique_counts else 0,
            "distinct_actual_strikes_in_surface":len(all_strikes),
            "actual_strikes_observed_at_every_union_timestamp":complete_strikes,
            "duplicate_timestamp_actual_strike_keys_across_offsets":duplicates,
            "per_offset":{k:{kk:vv for kk,vv in v.items() if kk!="records"} for k,v in by_offset.items()},
            "relative_surface_alignment_gate":"PASS" if passed else "FAIL",
            "interpretation":"Seven offset tapes align in time and expose distinct actual strikes at each timestamp; fixed-strike paths may be reconstructed from their in-memory union, subject to expiry identity and rights." if passed else "Do not calculate fixed-strike P&L until missing timestamps, strike overlap or incomplete offset tapes are resolved."})
    return summaries

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

def query(token, security_id, option_type, relative_strike, start, end):
    body = {"exchangeSegment":"NSE_FNO","interval":"1","securityId":str(security_id),
            "instrument":"OPTSTK","expiryFlag":"MONTH","expiryCode":EXPIRY_CODE,"strike":relative_strike,
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

def summarize(symbol, option_type, relative_strike, code, obj, safe_error=None, start=None, end=None):
    side = "ce" if option_type=="CALL" else "pe"
    x={"symbol":symbol,"requested_option_type":option_type,"requested_relative_strike":relative_strike,"http_status":code,
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
    strike_values = block.get("strike") if isinstance(block.get("strike"), list) else []
    normalized_strikes = [normalize_strike(v) for v in strike_values]
    normalized_strikes = [v for v in normalized_strikes if v is not None]
    x["distinct_actual_strikes"] = len(set(normalized_strikes))
    x["actual_strike_changes"] = sum(normalized_strikes[i] != normalized_strikes[i-1] for i in range(1,len(normalized_strikes)))
    x["first_actual_strike"] = normalized_strikes[0] if normalized_strikes else None
    x["last_actual_strike"] = normalized_strikes[-1] if normalized_strikes else None
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
    p.add_argument("--max-probes",type=int,default=int(os.getenv("PHASE103_MAX_PROBES","70")),
                   help="maximum number of symbol/side/strike API probes for this bounded run")
    p.add_argument("--strikes",default=os.getenv("PHASE103_STRIKES",",".join(DEFAULT_STRIKES)),
                   help="comma-separated Dhan relative strikes; allowed offsets are ATM and ATM +/- 1..3")
    p.add_argument("--out-dir",default="results/phase103")
    a=p.parse_args(); days=check_window(a.from_date,a.to_date)
    api_to_date=provider_to_date(a.from_date,a.to_date)
    try:
        strikes=parse_strikes(a.strikes)
    except ValueError as exc:
        p.error(str(exc))
    max_possible=len(SYMBOLS)*2*len(strikes)
    if not 1 <= a.max_probes <= max_possible:
        p.error(f"--max-probes must be from 1 through {max_possible} for the selected relative strikes")
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    result={"phase":"103.1","run_id":os.getenv("GITHUB_RUN_ID","local"),
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "window":{"from_inclusive":a.from_date,"to_exclusive":a.to_date,"span_days":days,
                  "request_mode":"half_open_target_window_with_inclusive_provider_toDate_adjustment"},
        "provider_request_window":{"fromDate":a.from_date,"toDate_inclusive":provider_to_date(a.from_date,a.to_date)},
        "probe_limit":a.max_probes,
        "requested_relative_strikes":strikes,
        "endpoint":ENDPOINT,"instrument_master_sha256":None,"instrument_master_bytes":None,
        "underlying_map":{},"probes":[],"surface_audit":[],"probe_abort_reason":None,"raw_rows_persisted":False,
        "raw_data_policy":"Raw rows kept ephemeral; no raw data artifact or public commit until retention/republication rights are verified.",
        "known_limits":["Rolling strikes can change actual strike over time.",
          "This endpoint documents OHLC, IV, volume, OI, strike and spot, not historical bid/ask/depth.",
          "One stock/side probe does not establish full-history completeness or independent test sufficiency.",
          "Empirical diagnostic showed Dhan included toDate in returned rows despite documentation describing it as non-inclusive; requests therefore pass target_end_exclusive minus one day and still audit every timestamp in the original half-open target window."],
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
            surface_blocks = []
            abort_probes = False
            for sym in SYMBOLS:
                m=result["underlying_map"].get(sym,{})
                for side in ["CALL","PUT"]:
                    for relative_strike in strikes:
                        if len(result["probes"]) >= a.max_probes:
                            break
                        if not m.get("security_id"):
                            result["probes"].append({"symbol":sym,"requested_option_type":side,
                                "requested_relative_strike":relative_strike,"status":"BLOCKED_UNDERLYING_ID"})
                            continue
                        code,obj,safe_error=query(token,m["security_id"],side,relative_strike,a.from_date,api_to_date)
                        probe_summary = summarize(sym,side,relative_strike,code,obj,safe_error,a.from_date,a.to_date)
                        result["probes"].append(probe_summary)
                        if code != 200 or probe_summary.get("rows",0) == 0 or not probe_summary.get("array_lengths_consistent",False):
                            result["probe_abort_reason"] = "stopped after the first HTTP error, empty requested-side payload, or inconsistent arrays"
                            abort_probes = True
                        # Raw timestamps and actual strikes exist only in memory to audit the cross-offset panel.
                        side_key = "ce" if side == "CALL" else "pe"
                        if obj and isinstance(obj.get("data"), dict) and isinstance(obj["data"].get(side_key), dict):
                            data_block=obj["data"][side_key]
                            if isinstance(data_block.get("timestamp"), list) and isinstance(data_block.get("strike"), list):
                                surface_blocks.append({"symbol":sym,"option_type":side,
                                    "relative_strike":relative_strike,
                                    "timestamps":data_block["timestamp"],"strikes":data_block["strike"]})
                        if abort_probes:
                            break
                        time.sleep(1.1)
                    if abort_probes or len(result["probes"]) >= a.max_probes:
                        break
                if abort_probes or len(result["probes"]) >= a.max_probes:
                    break
            result["surface_audit"]=summarize_surface(surface_blocks, strikes)
            rows_count=sum(v.get("rows",0)>0 for v in result["probes"])
            error_codes={str(v.get("api_error_code","")).upper() for v in result["probes"] if v.get("api_error_code")}
            auth_count=sum(v.get("status") in ["AUTH_401","AUTH_403"] for v in result["probes"])
            outside_count=sum(int(v.get("outside_requested_date_window_rows",0) or 0) for v in result["probes"])
            result["rows_outside_requested_date_window_total"]=outside_count
            if result.get("probe_abort_reason"):
                result["status"]="PROBE_ABORTED_AFTER_FIRST_INVALID_RELATIVE_STRIKE"
            elif auth_count or error_codes.intersection({"806","807","808","809","810","DH-901","DH-902"}):
                result["status"]="BLOCKED_AUTHENTICATION_OR_DATA_API_ENTITLEMENT"
            elif error_codes.intersection({"814","DH-905"}):
                result["status"]="REQUEST_SCHEMA_OR_PARAMETER_ERROR"
            elif outside_count > 0:
                result["status"]="DATA_RETURNED_WITH_OUT_OF_WINDOW_ROWS"
            elif any(v.get("rows",0)>0 and not v.get("array_lengths_consistent",False) for v in result["probes"]):
                result["status"]="ARRAY_LENGTH_INTEGRITY_FAIL"
            elif len(result["probes"])==a.max_probes and rows_count==a.max_probes: result["status"]="PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES"
            elif rows_count: result["status"]="PARTIAL_DATA_RETURNED"
            else: result["status"]="NO_DATA_RETURNED_OR_SCHEMA_MISMATCH"
    (out/"dhan_data_api_audit.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    lines=["# Phase 103.1 — Dhan Data API smoke test","",f"**Status:** {result['status']}",
      f"**Target window (IST):** {a.from_date} inclusive to {a.to_date} exclusive ({days} days)",
      f"**Dhan request dates:** fromDate={a.from_date}; toDate={api_to_date} (empirically inclusive; target end remains exclusive)",
      f"**Relative strikes:** {', '.join(strikes)}",
      f"**Probe limit:** {a.max_probes}",
      f"**Run:** {result['run_id']}","",
      "This is a data-feasibility probe, not a strategy test. The token and raw rows are not published.",
      "","| Symbol | Side | Offset | HTTP | Status | Error code | Safe message | Rows | Arrays consistent | Distinct actual strikes | Strike changes | First strike | Last strike | First UTC | Last UTC | IST-date row counts | Rows outside dates |",
      "|---|---|---|---:|---|---|---|---:|---|---:|---:|---|---|---|---|---|---:|"]
    for v in result.get("probes",[]):
        lines.append("| {symbol} | {side} | {offset} | {http} | {status} | {code} | {message} | {rows} | {consistent} | {distinct} | {changes} | {first_strike} | {last_strike} | {first} | {last} |".format(
          symbol=v.get("symbol",""),side=v.get("requested_option_type",""),offset=v.get("requested_relative_strike",""),
          http=v.get("http_status",""),status=v.get("status",""),code=v.get("api_error_code") or "",
          message=(v.get("api_error_message") or "").replace("|","/"),
          rows=v.get("rows",0),consistent=v.get("array_lengths_consistent",False),
          distinct=v.get("distinct_actual_strikes",0),changes=v.get("actual_strike_changes",0),
          first_strike=v.get("first_actual_strike") or "",last_strike=v.get("last_actual_strike") or "",
          first=v.get("first_timestamp_utc") or "",last=v.get("last_timestamp_utc") or ""))
        # Append IST date-bin and out-of-window audit columns without shifting the table.
        lines[-1] = lines[-1].rstrip()[:-1] + " | {} | {} |".format(
          json.dumps(v.get("timestamp_counts_by_ist_date",{}),sort_keys=True),
          v.get("outside_requested_date_window_rows") if v.get("outside_requested_date_window_rows") is not None else "n/a")
    lines += ["","## Relative-strike surface / fixed-contract continuity audit","",
      "| Symbol | Side | Offsets returned | Common timestamps | Union timestamps | Min distinct strikes/minute | Max distinct strikes/minute | Distinct actual strikes | Strikes seen every minute | Duplicate timestamp-strike keys | Surface gate |",
      "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for v in result.get("surface_audit",[]):
        lines.append("| {symbol} | {side} | {n} | {common} | {union} | {minv} | {maxv} | {distinct} | {complete} | {dupes} | {gate} |".format(
          symbol=v.get("symbol",""),side=v.get("option_type",""),n=v.get("offset_series_returned",0),
          common=v.get("common_timestamp_count_across_offsets",0),union=v.get("union_timestamp_count",0),
          minv=v.get("minimum_distinct_actual_strikes_per_timestamp",0),
          maxv=v.get("maximum_distinct_actual_strikes_per_timestamp",0),
          distinct=v.get("distinct_actual_strikes_in_surface",0),
          complete=v.get("actual_strikes_observed_at_every_union_timestamp",0),
          dupes=v.get("duplicate_timestamp_actual_strike_keys_across_offsets",0),
          gate=v.get("relative_surface_alignment_gate","NOT_ESTIMABLE")))
    lines += ["","## Underlying ID mapping","","| Symbol | ID resolved | Status |","|---|---|---|"]
    for sym,m in result.get("underlying_map",{}).items():
        lines.append("| {} | {} | {} |".format(sym,"yes" if m.get("security_id") else "no",m.get("status")))
    lines += ["","## Limitations",""]+["- "+x for x in result["known_limits"]]
    (out/"DHAN_DATA_API_AUDIT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"phase":"103.1","status":result["status"],"probe_abort_reason":result.get("probe_abort_reason"),"window":result["window"],
      "underlying_ids_resolved":sum(1 for x in result.get("underlying_map",{}).values() if x.get("security_id")),
      "probes":len(result.get("probes",[])),"probe_limit":result["probe_limit"],"relative_strikes":strikes,
      "probes_with_rows":sum(1 for x in result.get("probes",[]) if x.get("rows",0)>0),
      "surface_groups":len(result.get("surface_audit",[])),
      "surface_gates_passed":sum(1 for x in result.get("surface_audit",[]) if x.get("relative_surface_alignment_gate")=="PASS"),
      "rows_outside_requested_date_window_total":result.get("rows_outside_requested_date_window_total",0)},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
