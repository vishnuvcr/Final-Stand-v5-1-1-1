#!/usr/bin/env python3
"""Bounded DhanHQ expired stock-options data probe; never prints token or raw rows."""
import argparse, csv, hashlib, io, json, os, time, urllib.error, urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from expiry_crosscheck import audit_expiry_identity

MASTER = "https://images.dhan.co/api-data/api-scrip-master.csv"
ENDPOINT = "https://api.dhan.co/v2/charts/rollingoption"
SYMBOLS = ["HDFCBANK", "ICICIBANK", "RELIANCE", "SBIN", "INFY"]
DEFAULT_STRIKES = ["ATM", "ATM+1", "ATM+2", "ATM+3", "ATM-1", "ATM-2", "ATM-3"]
ALLOWED_STRIKES = set(DEFAULT_STRIKES)
# Panels that passed the first-session alignment screen; failed panels remain excluded until their gaps are resolved.
DEFAULT_PANELS = [("ICICIBANK", "CALL"), ("RELIANCE", "CALL"), ("RELIANCE", "PUT"), ("SBIN", "CALL")]
# The provider currently rejects code 0 as missing; use the documented sample value 1 (next expiry).
EXPIRY_CODE = 1
CONTRACT_IDENTITY_STATUS = "BLOCKED_EXPIRY_NOT_RETURNED"
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

def parse_expiry_code(value):
    try:
        code = int(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError("Expiry code must be 0, 1 or 2.")
    if code not in (0, 1, 2):
        raise argparse.ArgumentTypeError("Expiry code must be 0, 1 or 2.")
    return code

def parse_panels(raw):
    """Parse a bounded list of registered SYMBOL:CALL/PUT panels."""
    panels=[]
    for item in raw.split(","):
        token=item.strip().upper()
        if not token:
            continue
        parts=token.split(":")
        if len(parts)!=2 or parts[0] not in SYMBOLS or parts[1] not in {"CALL","PUT"}:
            raise ValueError("Panels must be comma-separated SYMBOL:CALL or SYMBOL:PUT values from the registered universe.")
        panels.append((parts[0],parts[1]))
    if not panels:
        raise ValueError("At least one stock/option-side panel is required.")
    if len(set(panels)) != len(panels):
        raise ValueError("Panel list contains duplicates.")
    return panels

def response_envelope_summary(obj, option_type, token=""):
    """Capture response shape only; never retain raw values or request credentials."""
    side_key="ce" if option_type=="CALL" else "pe"
    data=obj.get("data") if isinstance(obj,dict) else None
    block=data.get(side_key) if isinstance(data,dict) else None
    provider_status=obj.get("status") if isinstance(obj,dict) else None
    if isinstance(provider_status,str):
        status_text=" ".join(provider_status.split()).casefold()[:80]
        if token:
            status_text=status_text.replace(token.casefold(),"[redacted]")
        if status_text not in {"success","successful","ok","error","failed","failure","pending"}:
            status_text="other_or_unrecognized"
    elif provider_status is None:
        status_text="missing"
    else:
        status_text=type(provider_status).__name__
    shapes={}
    if isinstance(block,dict):
        for field in FIELDS:
            value=block.get(field)
            shapes[field]={"type":"null" if value is None else type(value).__name__,
                           "length":len(value) if isinstance(value,list) else None}
    return {
        "top_level_keys":sorted(str(k) for k in obj.keys()) if isinstance(obj,dict) else [],
        "provider_status_class":status_text,
        "data_type":"null" if data is None else type(data).__name__,
        "data_keys":sorted(str(k) for k in data.keys()) if isinstance(data,dict) else [],
        "requested_side_key":side_key,
        "requested_side_key_present":isinstance(data,dict) and side_key in data,
        "requested_side_type":"missing" if not isinstance(data,dict) or side_key not in data else ("null" if block is None else type(block).__name__),
        "requested_side_keys":sorted(str(k) for k in block.keys()) if isinstance(block,dict) else [],
        "field_shapes":shapes
    }

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
    """Aggregate relative-strike and exact-strike coverage; raw rows remain in runner memory only."""
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
        # Relative offsets can map to different actual strikes as spot moves. Report
        # coverage for each actual strike separately rather than interpreting cross-offset
        # timestamp alignment as a fixed-contract continuity test.
        strike_coverage = []
        for actual_strike, times in sorted(all_strikes.items(), key=lambda kv: float(kv[0])):
            by_date = {}
            for stamp in times:
                day = datetime.fromtimestamp(stamp, timezone.utc).astimezone(ZoneInfo("Asia/Kolkata")).date().isoformat()
                by_date[day] = by_date.get(day, 0) + 1
            strike_coverage.append({
                "actual_strike": actual_strike,
                "observed_minutes": len(times),
                "union_timestamp_coverage_pct": round(100.0 * len(times) / len(union_ts), 3) if union_ts else 0.0,
                "ist_date_minutes": by_date,
                "first_timestamp_utc": datetime.fromtimestamp(min(times), timezone.utc).isoformat() if times else None,
                "last_timestamp_utc": datetime.fromtimestamp(max(times), timezone.utc).isoformat() if times else None
            })
        exact_strike_diagnostic = "PASS_UNIQUE_TIMESTAMP_STRIKE_KEYS" if bool(union_ts) and duplicates == 0 else "FAIL_DUPLICATE_OR_EMPTY_KEYS"
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
            "exact_strike_diagnostic":exact_strike_diagnostic,
            "actual_strike_coverage":strike_coverage,
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

def query(token, security_id, option_type, relative_strike, start, end, expiry_code=EXPIRY_CODE):
    body = {"exchangeSegment":"NSE_FNO","interval":"1","securityId":str(security_id),
            "instrument":"OPTSTK","expiryFlag":"MONTH","expiryCode":expiry_code,"strike":relative_strike,
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
    x["response_envelope"]=response_envelope_summary(obj,option_type,os.getenv("DHAN_ACCESS_TOKEN","").strip())
    data_obj=obj.get("data")
    block=data_obj.get(side) if isinstance(data_obj,dict) else None
    provider_status=obj.get("status")
    provider_status_norm=provider_status.casefold() if isinstance(provider_status,str) else ""
    if not isinstance(block,dict):
        if provider_status_norm in {"success","successful","ok"}:
            x["status"]="SUCCESS_EMPTY_FOR_REQUESTED_SIDE"
        else:
            x["status"]="REQUESTED_SIDE_PAYLOAD_MISSING"
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
    elif provider_status_norm in {"success","successful","ok"}: x["status"]="SUCCESS_EMPTY_FOR_REQUESTED_SIDE"
    else: x["status"]="EMPTY_OR_UNRECOGNIZED_RESPONSE_ENVELOPE"
    return x

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--from-date",default=os.getenv("PHASE103_FROM_DATE","2026-08-03"))
    p.add_argument("--to-date",default=os.getenv("PHASE103_TO_DATE","2026-08-10"),help="exclusive")
    p.add_argument("--panels",default=os.getenv("PHASE103_PANELS",",".join(f"{s}:{o}" for s,o in DEFAULT_PANELS)),
                   help="comma-separated registered SYMBOL:CALL/PUT panels")
    p.add_argument("--max-probes",type=int,default=int(os.getenv("PHASE103_MAX_PROBES","70")),
                   help="maximum number of symbol/side/strike API probes for this bounded run")
    p.add_argument("--strikes",default=os.getenv("PHASE103_STRIKES",",".join(DEFAULT_STRIKES)),
                   help="comma-separated Dhan relative strikes; allowed offsets are ATM and ATM +/- 1..3")
    p.add_argument("--expiry-code",type=parse_expiry_code,
                   default=parse_expiry_code(os.getenv("PHASE103_EXPIRY_CODE",str(EXPIRY_CODE))),
                   help="Dhan expiry selector: 0 near/current, 1 next, 2 far")
    p.add_argument("--out-dir",default="results/phase103")
    a=p.parse_args(); days=check_window(a.from_date,a.to_date)
    api_to_date=provider_to_date(a.from_date,a.to_date)
    try:
        strikes=parse_strikes(a.strikes)
        panels=parse_panels(a.panels)
    except ValueError as exc:
        p.error(str(exc))
    max_possible=len(panels)*len(strikes)
    if not 1 <= a.max_probes <= max_possible:
        p.error(f"--max-probes must be from 1 through {max_possible} for the selected relative strikes")
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    result={"phase":"103.1","run_id":os.getenv("GITHUB_RUN_ID","local"),
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "window":{"from_inclusive":a.from_date,"to_exclusive":a.to_date,"span_days":days,
                  "request_mode":"half_open_target_window_with_inclusive_provider_toDate_adjustment"},
        "provider_request_window":{"fromDate":a.from_date,"toDate_inclusive":provider_to_date(a.from_date,a.to_date)},
        "probe_limit":a.max_probes,
        "requested_panels":[f"{sym}:{side}" for sym,side in panels],
        "requested_relative_strikes":strikes,
        "endpoint":ENDPOINT,"requested_expiry_code":a.expiry_code,"contract_identity_status":CONTRACT_IDENTITY_STATUS,
        "expiry_identity_audit":{"status":"BLOCKED_CROSSCHECK_NOT_RUN","raw_rows_persisted":False},
        "instrument_master_sha256":None,"instrument_master_bytes":None,
        "underlying_map":{},"probes":[],"surface_audit":[],"probe_abort_reason":None,"raw_rows_persisted":False,
        "raw_data_policy":"Raw minute rows kept ephemeral; publish only aggregate audit metadata and derived findings; do not commit raw rows or put them in Actions artifacts.",
        "known_limits":["Rolling strikes can change actual strike over time.",
          "This endpoint documents OHLC, IV, volume, OI, strike and spot, not historical bid/ask/depth.",
          "Observed response schema does not return contract expiry date or immutable option contract ID; expiryFlag/expiryCode are request selectors, not an audited returned identity.",
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
            for sym,side in panels:
                m=result["underlying_map"].get(sym,{})
                for relative_strike in strikes:
                    if len(result["probes"]) >= a.max_probes:
                        break
                    if not m.get("security_id"):
                        result["probes"].append({"symbol":sym,"requested_option_type":side,
                            "requested_relative_strike":relative_strike,"status":"BLOCKED_UNDERLYING_ID"})
                        continue
                    code,obj,safe_error=query(token,m["security_id"],side,relative_strike,a.from_date,api_to_date,a.expiry_code)
                    probe_summary = summarize(sym,side,relative_strike,code,obj,safe_error,a.from_date,a.to_date)
                    result["probes"].append(probe_summary)
                    # Missing/empty requested-side data is an explicit coverage result; continue to other selected offsets.
                    # HTTP failures and malformed non-empty arrays remain fatal to this bounded panel audit.
                    if code != 200 or (probe_summary.get("rows",0)>0 and not probe_summary.get("array_lengths_consistent",False)):
                        result["probe_abort_reason"] = "stopped after the first HTTP error or malformed non-empty arrays"
                        abort_probes = True
                    # Raw timestamps and actual strikes exist only in memory to audit the cross-offset panel.
                    side_key = "ce" if side == "CALL" else "pe"
                    if obj and isinstance(obj.get("data"), dict) and isinstance(obj["data"].get(side_key), dict):
                        data_block=obj["data"][side_key]
                        if isinstance(data_block.get("timestamp"), list) and isinstance(data_block.get("strike"), list):
                            surface_blocks.append({"symbol":sym,"option_type":side,
                                "relative_strike":relative_strike,
                                "timestamps":data_block["timestamp"],"strikes":data_block["strike"],
                                "bars":{field:data_block.get(field,[]) for field in ["timestamp","strike","open","high","low","close","volume","oi"]}})
                    if abort_probes:
                        break
                    time.sleep(1.1)
                if abort_probes or len(result["probes"]) >= a.max_probes:
                    break
            result["surface_audit"]=summarize_surface(surface_blocks, strikes)
            # Independent expiry cross-check: raw Dhan/NSE rows remain in memory only.
            expiry_audit = audit_expiry_identity(surface_blocks, get_bytes, expiry_code=a.expiry_code)
            result["expiry_identity_audit"] = expiry_audit
            result["contract_identity_status"] = (
                "PASS_EOD_RECONCILED_EXPIRY_CODE_" + str(a.expiry_code)
                if expiry_audit.get("status") == "PASS_EOD_RECONCILED_EXPIRY_CODE_" + str(a.expiry_code)
                else "BLOCKED_EXPIRY_EOD_CROSSCHECK"
            )
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
      f"**Panels:** {', '.join(result['requested_panels'])}",
      f"**Relative strikes:** {', '.join(strikes)}",
      f"**Probe limit:** {a.max_probes}",
      f"**Run:** {result['run_id']}",
      f"**Exact contract identity:** {result['contract_identity_status']} (request expiry selectors do not supply a returned expiry date or immutable contract ID)", "",
      "This is a multi-session data-feasibility audit, not a strategy P&L test. Panels were selected from the prior one-session alignment screen. The token and raw rows are not published.",
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
    lines += ["","### Exact actual-strike coverage (diagnostic only)","","This is the deduplicated union of timestamp/actual-strike observations across rolling offsets. It does not establish expiry identity or executable quotes.","",
      "| Symbol | Side | Actual strike | Observed minutes | Union coverage % | First UTC | Last UTC | IST-date counts |",
      "|---|---|---:|---:|---:|---|---|---|"]
    for panel in result.get("surface_audit",[]):
        for row in panel.get("actual_strike_coverage",[]):
            lines.append("| {symbol} | {side} | {strike} | {minutes} | {coverage} | {first} | {last} | {dates} |".format(
              symbol=panel.get("symbol",""), side=panel.get("option_type",""), strike=row.get("actual_strike",""),
              minutes=row.get("observed_minutes",0), coverage=row.get("union_timestamp_coverage_pct",0),
              first=row.get("first_timestamp_utc") or "", last=row.get("last_timestamp_utc") or "",
              dates=json.dumps(row.get("ist_date_minutes",{}),sort_keys=True)))
    exp = result.get("expiry_identity_audit", {})
    lines += ["","## Independent expiry identity cross-check","",
      f"**Result:** {exp.get('status','NOT_RUN')}",
      f"**NSE trade dates downloaded:** {exp.get('trade_dates_downloaded',0)}/{exp.get('trade_dates_requested',0)}",
      f"**Eligible full-session exact-strike profiles:** {exp.get('eligible_full_session_profiles',0)}",
      f"**Profiles with exact symbol/side/strike EOD candidates:** {exp.get('profiles_with_eod_contract_candidates',0)}",
      f"**OHLC field match counts across candidate contracts:** {json.dumps(exp.get('price_field_match_counts',{}),sort_keys=True)}",
      f"**Profiles by number of matching OHLC fields (0–4):** {json.dumps(exp.get('price_field_match_histogram',{}),sort_keys=True)}",
      f"**Unique exact OHLC matches:** {exp.get('unique_exact_contract_matches',0)}",
      f"**Matches to expected expiryCode={result.get('requested_expiry_code',1)} selection:** {exp.get('expiry_code_matches',0)}",
      f"**Selector mismatches / ambiguous / unmatched:** {exp.get('expiry_selector_mismatches',0)} / {exp.get('ambiguous_profile_count',0)} / {exp.get('unmatched_profile_count',0)}",
      f"**Supporting volume/OI agreement counts:** {exp.get('supporting_volume_matches',0)} / {exp.get('supporting_oi_matches',0)}",
      f"**Aggregate matched expiry counts:** {json.dumps(exp.get('matched_expiry_counts',{}),sort_keys=True)}",
      f"**Aggregate matched expiry ranks:** {json.dumps(exp.get('matched_expiry_rank_counts',{}),sort_keys=True)}",
      f"**Duplicate keys deduplicated / conflicting duplicate keys:** {exp.get('duplicate_timestamp_strike_rows_deduplicated',0)} / {exp.get('conflicting_duplicate_key_count',0)}",
      f"**Raw row persistence:** {exp.get('raw_rows_persisted',False)}",
      "Only aggregate counts and expiry dates are published; raw minute bars and NSE row-level data remain ephemeral.",
      ""]
    for err in exp.get("safe_source_errors", []):
        lines.append(f"- NSE EOD source error for {err.get('date')}: {err.get('error_type')}")
    lines += ["","## Underlying ID mapping","","| Symbol | ID resolved | Status |","|---|---|---|"]
    for sym,m in result.get("underlying_map",{}).items():
        lines.append("| {} | {} | {} |".format(sym,"yes" if m.get("security_id") else "no",m.get("status")))
    lines += ["","## Limitations",""]+["- "+x for x in result["known_limits"]]
    (out/"DHAN_DATA_API_AUDIT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"phase":"103.1","status":result["status"],"probe_abort_reason":result.get("probe_abort_reason"),"window":result["window"],
      "underlying_ids_resolved":sum(1 for x in result.get("underlying_map",{}).values() if x.get("security_id")),
      "probes":len(result.get("probes",[])),"probe_limit":result["probe_limit"],"panels":result["requested_panels"],"relative_strikes":strikes,
      "probes_with_rows":sum(1 for x in result.get("probes",[]) if x.get("rows",0)>0),
      "contract_identity_status":result["contract_identity_status"],
      "requested_expiry_code":result.get("requested_expiry_code"),
      "expiry_identity_audit_status":result.get("expiry_identity_audit",{}).get("status"),
      "expiry_identity_unique_matches":result.get("expiry_identity_audit",{}).get("unique_exact_contract_matches",0),
      "expiry_identity_code_matches":result.get("expiry_identity_audit",{}).get("expiry_code_matches",0),
      "surface_groups":len(result.get("surface_audit",[])),
      "surface_gates_passed":sum(1 for x in result.get("surface_audit",[]) if x.get("relative_surface_alignment_gate")=="PASS"),
      "rows_outside_requested_date_window_total":result.get("rows_outside_requested_date_window_total",0)},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
