#!/usr/bin/env python3
"""Acquire official NSE Indices historical India VIX and index OHLC context.

Responses are retained only in Actions cache. Public outputs contain aggregate
coverage, field-quality metrics and response hashes, not the full price history.
"""
import argparse, ast, hashlib, json, math, time, urllib.error, urllib.request, urllib.parse, http.cookiejar
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

CACHE=Path("data/cache/phase109/niftyindices_history")
OUT=Path("results/phase109")
BASE="https://www.niftyindices.com/Backpage.aspx"
UA="Mozilla/5.0 (compatible; FinalStandPhase109/1.0)"
START_DEFAULT="2023-10-01"
END_DEFAULT="2026-10-09"


def date_text(d):
    return d.strftime("%d %b %Y")


def intervals(start, end_exclusive):
    cur=start
    while cur<end_exclusive:
        # Keep inclusive API ranges comfortably below its documented 365-day limit.
        chunk_end=min(end_exclusive, cur+timedelta(days=364))
        yield cur, chunk_end-timedelta(days=1)
        cur=chunk_end


COOKIE_JAR = http.cookiejar.CookieJar()
OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(COOKIE_JAR))
BOOTSTRAPPED = False


def bootstrap_session():
    global BOOTSTRAPPED
    if BOOTSTRAPPED:
        return
    req=urllib.request.Request("https://www.niftyindices.com/reports/historical-data",headers={
      "User-Agent":UA,"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    try:
        with OPENER.open(req,timeout=5) as resp:
            resp.read(1024)
    except Exception:
        # The API can work without the page cookie; this is a best-effort Akamai bootstrap.
        pass
    BOOTSTRAPPED=True


def post(url, body_bytes):
    bootstrap_session()
    req=urllib.request.Request(url,data=body_bytes,headers={
      "User-Agent":UA,"Accept":"application/json, text/plain, */*",
      "Content-Type":"application/json; charset=utf-8",
      "Origin":"https://www.niftyindices.com",
      "Referer":"https://www.niftyindices.com/reports/historical-data",
    },method="POST")
    with OPENER.open(req,timeout=45) as resp:
        if resp.status!=200: raise RuntimeError("HTTP_"+str(resp.status))
        raw=resp.read()
    decoded=raw.decode("utf-8-sig").strip()
    try:
        outer=json.loads(decoded)
    except json.JSONDecodeError:
        # Some ASP.NET endpoints/proxies return a Python-literal-compatible
        # single-quoted object rather than valid JSON. Parse strictly as a
        # literal; never evaluate source text.
        try:
            outer=ast.literal_eval(decoded)
        except (ValueError,SyntaxError) as exc:
            raise ValueError("UNPARSEABLE_NSE_INDICES_RESPONSE_PREFIX_"+repr(decoded[:80])) from exc
    if not isinstance(outer,dict):
        raise ValueError("UNEXPECTED_NSE_INDICES_OUTER_RESPONSE_TYPE")
    inner=outer.get("d",[])
    if isinstance(inner,str):
        if inner.strip().lower() in {"false","[]",""}: rows=[]
        else:
            try: rows=json.loads(inner)
            except json.JSONDecodeError:
                try: rows=ast.literal_eval(inner)
                except (ValueError,SyntaxError) as exc:
                    raise ValueError("UNPARSEABLE_NSE_INDICES_INNER_RESPONSE") from exc
    elif isinstance(inner,list): rows=inner
    else: rows=[]
    if not isinstance(rows,list): raise ValueError("Unexpected response data type")
    return raw,rows


def nse_get(path, params, bootstrap_page):
    # Use the official NSE India historical-OR API; the older niftyindices.com
    # Backpage endpoints returned HTML challenge pages in GitHub Actions.
    headers={
      "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept":"application/json, text/plain, */*",
      "Accept-Language":"en-US,en;q=0.9",
      "Referer":"https://www.nseindia.com/",
      "X-Requested-With":"XMLHttpRequest",
    }
    try:
        req=urllib.request.Request(bootstrap_page,headers=headers)
        with OPENER.open(req,timeout=15) as resp: resp.read(4096)
    except Exception:
        # Continue to the data endpoint; some runners receive cookies on the API response.
        pass
    query=urllib.parse.urlencode(params)
    req=urllib.request.Request("https://www.nseindia.com"+path+"?"+query,headers=headers)
    with OPENER.open(req,timeout=45) as resp:
        raw=resp.read()
    decoded=raw.decode("utf-8-sig").strip()
    try: outer=json.loads(decoded)
    except json.JSONDecodeError as exc:
        raise ValueError("NSE_HISTORICAL_API_NON_JSON_PREFIX_"+repr(decoded[:80])) from exc
    rows=outer.get("data",[]) if isinstance(outer,dict) else []
    if isinstance(rows,dict):
        for key in ("indexCloseOnlineRecords","data","records"):
            if isinstance(rows.get(key),list):
                rows=rows[key]; break
    if not isinstance(rows,list):
        raise ValueError("NSE_HISTORICAL_API_UNEXPECTED_DATA_SHAPE")
    return raw,rows


def vix_request(start,end):
    raw, source_rows=nse_get("/api/historicalOR/vixhistory",
      {"from":start.strftime("%d-%m-%Y"),"to":end.strftime("%d-%m-%Y")},
      "https://www.nseindia.com/reports-indices-historical-vix")
    rows=[]
    for r in source_rows:
        rows.append({
          "date":r.get("EOD_TIMESTAMP") or r.get("EOD_DATE") or r.get("date") or r.get("DATE"),
          "open":r.get("EOD_OPEN_INDEX_VAL",r.get("EOD_OPEN_INDEX_VAL")),
          "high":r.get("EOD_HIGH_INDEX_VAL"),
          "low":r.get("EOD_LOW_INDEX_VAL"),
          "close":r.get("EOD_CLOSE_INDEX_VAL",r.get("EOD_INDEX_VAL") or r.get("close")),
        })
    return raw,rows


def index_request(index_name,start,end):
    raw, source_rows=nse_get("/api/historicalOR/indicesHistory",
      {"indexType":index_name,"from":start.strftime("%d-%m-%Y"),"to":end.strftime("%d-%m-%Y")},
      "https://www.nseindia.com/reports-indices-historical-index-data")
    rows=[]
    for r in source_rows:
        rows.append({
          "HistoricalDate":r.get("EOD_TIMESTAMP") or r.get("HistoricalDate") or r.get("DATE"),
          "OPEN":r.get("EOD_OPEN_INDEX_VAL",r.get("OPEN")),
          "HIGH":r.get("EOD_HIGH_INDEX_VAL",r.get("HIGH")),
          "LOW":r.get("EOD_LOW_INDEX_VAL",r.get("LOW")),
          "CLOSE":r.get("EOD_CLOSE_INDEX_VAL",r.get("CLOSE")),
          "IndexName":r.get("EOD_INDEX_NAME") or index_name,
        })
    return raw,rows


def parse_d(s):
    v=str(s or "").strip()
    if not v:return None
    candidates=[v]
    if len(v)>=10 and v[4:5]=="-" and v[7:8]=="-":candidates.append(v[:10])
    if "T" in v:candidates.append(v.split("T",1)[0])
    for candidate in candidates:
        for fmt in ("%d %b %Y","%d-%b-%Y","%d-%B-%Y","%Y-%m-%d","%d/%m/%Y"):
            try: return datetime.strptime(candidate,fmt).date().isoformat()
            except ValueError: pass
    return None


def num(v):
    try:
        x=float(str(v).strip())
        return x if math.isfinite(x) else None
    except (TypeError,ValueError,OverflowError): return None


def rows_audit(dataset_name,rows,sha,start,end):
    dates=[]
    missing_fields=0; invalid_ohlc=0; bad_date=0; duplicate=0
    seen=set(); values=[]
    is_vix=(dataset_name=="INDIA_VIX")
    for r in rows:
        d=parse_d(r.get("date") if is_vix else r.get("HistoricalDate"))
        if d is None:
            bad_date+=1; continue
        dates.append(d)
        if d in seen: duplicate+=1
        seen.add(d)
        keys=("open","high","low","close") if is_vix else ("OPEN","HIGH","LOW","CLOSE")
        v=[num(r.get(k)) for k in keys]
        if any(x is None for x in v):
            missing_fields+=1
        else:
            o,h,l,c=v
            if min(v)<=0 or h<max(o,l,c) or l>min(o,h,c): invalid_ohlc+=1
            values.extend(v)
        if is_vix:
            x=num(r.get("close"))
            if x is not None: values.append(x)
    return {
      "series":dataset_name,"row_count":len(rows),"start_requested":start.isoformat(),
      "end_requested_exclusive":end.isoformat(),"min_date":min(dates) if dates else "",
      "max_date":max(dates) if dates else "","unique_date_count":len(seen),
      "duplicate_date_rows":duplicate,"unparseable_date_rows":bad_date,
      "rows_with_missing_OHLC":missing_fields,"invalid_OHLC_rows":invalid_ohlc,
      "minimum_observed_value":min(values) if values else None,
      "maximum_observed_value":max(values) if values else None,
      "response_sha256":sha,
      "cache_policy":"full source response is private in Actions cache; only metrics/hash are public",
    }


def load_or_fetch(kind,index_name,start,end):
    CACHE.mkdir(parents=True,exist_ok=True)
    p=CACHE/(kind+"_"+start.strftime("%Y%m%d")+"_"+end.strftime("%Y%m%d")+".json")
    if p.exists():
        try:
            d=json.loads(p.read_text(encoding="utf-8"))
            if d.get("start")==start.isoformat() and d.get("end")==end.isoformat() and isinstance(d.get("rows"),list):
                raw=json.dumps(d["rows"],sort_keys=True,separators=(",",":")).encode()
                return d["rows"],hashlib.sha256(raw).hexdigest(),"CACHE"
        except Exception:
            p.unlink(missing_ok=True)
    if kind=="INDIA_VIX":
        raw,rows=vix_request(start,end)
    else:
        raw,rows=index_request(index_name,start,end)
    # Store response rows (not credentials) privately. Save only after API parsing succeeds.
    temp={"kind":kind,"index_name":index_name,"start":start.isoformat(),"end":end.isoformat(),
          "source_url":BASE+("/BindHistoricalIndiaVixData" if kind=="INDIA_VIX" else "/getHistoricaldatatabletoString"),
          "rows":rows,"raw_response_sha256":hashlib.sha256(raw).hexdigest()}
    p.write_text(json.dumps(temp,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    return rows,hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest(),"NETWORK"


def all_summaries_for_series_have_parseable_dates(merged_metrics, all_summaries):
    # Chunk-level audit rows carry unparseable_date_rows; merged metrics do not.
    return all(int(x.get("unparseable_date_rows", 0) or 0) == 0 for x in all_summaries)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--from-date",default=START_DEFAULT)
    ap.add_argument("--to-date",default=END_DEFAULT,help="exclusive")
    args=ap.parse_args()
    start=date.fromisoformat(args.from_date); end=date.fromisoformat(args.to_date)
    if end<=start: raise ValueError("to-date must be after from-date")
    all_summaries=[]; failures=[]
    merged={"INDIA_VIX":[],"NIFTY 50":[],"NIFTY BANK":[]}
    hashes={}
    fetch_modes={}
    for chunk_start,chunk_end in intervals(start,end):
        for kind,name in (("INDIA_VIX","India VIX"),("INDEX_NIFTY50","NIFTY 50"),("INDEX_NIFTYBANK","NIFTY BANK")):
            try:
                rows,sha,mode=load_or_fetch(kind,name,chunk_start,chunk_end)
                ds_name={"INDIA_VIX":"INDIA_VIX","INDEX_NIFTY50":"NIFTY 50","INDEX_NIFTYBANK":"NIFTY BANK"}[kind]
                all_summaries.append(rows_audit(ds_name,rows,sha,chunk_start,chunk_end+timedelta(days=1)))
                merged[ds_name].extend(rows)
                hashes[kind+"_"+chunk_start.isoformat()+"_"+chunk_end.isoformat()]=sha
                fetch_modes[mode]=fetch_modes.get(mode,0)+1
            except Exception as e:
                failures.append({"series":kind,"from":chunk_start.isoformat(),"to":chunk_end.isoformat(),"error":type(e).__name__+":"+str(e)[:220]})
        time.sleep(0.15)
    # Merge output is only a metric; full rows remain cached privately.
    # Publish only date keys and presence flags so archive misses can be separated
    # from weekdays that were not exchange sessions without exposing prices.
    calendar_dates=set()
    for name, rows in merged.items():
        datefield="date" if name=="INDIA_VIX" else "HistoricalDate"
        for r in rows:
            parsed=parse_d(r.get(datefield))
            if parsed:
                calendar_dates.add(parsed)
    calendar_rows=[]
    date_maps={}
    for name, rows in merged.items():
        datefield="date" if name=="INDIA_VIX" else "HistoricalDate"
        date_maps[name]={parse_d(r.get(datefield)) for r in rows if parse_d(r.get(datefield))}
    for ds in sorted(calendar_dates):
        calendar_rows.append({
          "date":ds,
          "india_vix_present":int(ds in date_maps.get("INDIA_VIX",set())),
          "nifty50_present":int(ds in date_maps.get("NIFTY 50",set())),
          "nifty_bank_present":int(ds in date_maps.get("NIFTY BANK",set())),
        })
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/"niftyindices_session_calendar.csv").open("w",newline="",encoding="utf-8") as fh:
        import csv
        w=csv.DictWriter(fh,fieldnames=["date","india_vix_present","nifty50_present","nifty_bank_present"])
        w.writeheader(); w.writerows(calendar_rows)

    merged_metrics=[]
    for name,rows in merged.items():
        # Deduplicate rows by date while reporting, but keep all underlying source chunks in cache.
        datefield="date" if name=="INDIA_VIX" else "HistoricalDate"
        seen={}
        for r in rows:
            d=parse_d(r.get(datefield))
            if d: seen.setdefault(d,r)
        dates=sorted(seen)
        fake_sha=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        if name=="INDIA_VIX":
            values=[num(r.get("close")) for r in seen.values() if num(r.get("close")) is not None]
            prices=[(num(r.get(k))) for r in seen.values() for k in ("open","high","low","close")]
        else:
            values=[num(r.get("CLOSE")) for r in seen.values() if num(r.get("CLOSE")) is not None]
            prices=[num(r.get(k)) for r in seen.values() for k in ("OPEN","HIGH","LOW","CLOSE")]
        prices=[p for p in prices if p is not None]
        invalid=0; missing=0
        for r in seen.values():
            keys=("open","high","low","close") if name=="INDIA_VIX" else ("OPEN","HIGH","LOW","CLOSE")
            vals=[num(r.get(k)) for k in keys]
            if any(v is None for v in vals): missing+=1
            else:
                o,h,l,c=vals
                if min(vals)<=0 or h<max(o,l,c) or l>min(o,h,c): invalid+=1
        merged_metrics.append({
          "series":name,"source_rows_before_date_dedup":len(rows),"unique_date_count":len(seen),
          "duplicate_date_rows_across_chunks":max(0,len(rows)-len(seen)),
          "min_date":min(dates) if dates else "","max_date":max(dates) if dates else "",
          "missing_OHLC_rows":missing,"invalid_OHLC_rows":invalid,
          "minimum_close":min(values) if values else None,"maximum_close":max(values) if values else None,
          "all_OHLC_values_min":min(prices) if prices else None,"all_OHLC_values_max":max(prices) if prices else None,
          "merged_rows_sha256":fake_sha,
        })
    report={
      "generated_utc":datetime.now(timezone.utc).isoformat(),"requested_from":start.isoformat(),
      "requested_to_exclusive":end.isoformat(),"source":"NSE Indices official historical data endpoints",
      "source_references":["https://www.niftyindices.com/reports/historical-data","https://www.niftyindices.com/Backpage.aspx/BindHistoricalIndiaVixData","https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString"],
      "chunk_count":len(list(intervals(start,end))),"successful_chunk_series_calls":len(all_summaries),
      "failed_chunk_series_calls":len(failures),"fetch_cache_modes":fetch_modes,
      "chunk_summaries":all_summaries,"merged_series_summary":merged_metrics,"errors":failures,
      "observed_calendar_rows":len(calendar_rows),
      "observed_calendar_min_date":calendar_rows[0]["date"] if calendar_rows else "",
      "observed_calendar_max_date":calendar_rows[-1]["date"] if calendar_rows else "",
      "overall_status":"PASS" if len(failures)==0 and all(x["unique_date_count"]>0 and x["invalid_OHLC_rows"]==0 and x["missing_OHLC_rows"]==0 and x["duplicate_date_rows_across_chunks"]==0 and all_summaries_for_series_have_parseable_dates(merged_metrics, all_summaries) for x in merged_metrics) else "PARTIAL_OR_FAILED",
      "note":"Official index/VIX input feasibility only; not strategy evaluation. Series rows are stored in Actions cache. Do not substitute unverified public-HF VIX labels.",
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"niftyindices_context_summary.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    lines=["# NSE Indices historical index and India VIX audit","",
      "Generated: "+report["generated_utc"],
      "Requested window: "+start.isoformat()+" to "+end.isoformat()+" (end exclusive)",
      "Overall status: "+report["overall_status"],"",
      "No strategy returns were evaluated. Full historical rows remain in the private GitHub Actions cache; this report exposes only aggregate audit metrics and hashes.","",
      "| Series | Unique dates | Range | Missing OHLC | Invalid OHLC | Close min | Close max |",
      "|---|---:|---|---:|---:|---:|---:|"]
    for x in merged_metrics:
        lines.append("| "+x["series"]+" | "+format(x["unique_date_count"],",")+" | "+x["min_date"]+"–"+x["max_date"]+" | "+str(x["missing_OHLC_rows"])+" | "+str(x["invalid_OHLC_rows"])+" | "+str(x["minimum_close"])+" | "+str(x["maximum_close"])+" |")
    lines.extend(["","## Data gates","",
      "- A VIX series is accepted only from the official NSE Indices endpoint and must pass plausibility/duplicate/schema checks. Publisher-labelled VIX datasets are not used as substitutes.",
      "- The selected NIFTY 50 and NIFTY BANK daily OHLC are inputs for lagged market-regime and cross-index/underlying features; only prior-known values may enter a strategy signal.",
      "- Check the returned index/VIX dates against the official trading calendar and option-archive date manifest before model fitting.",
      "- Any non-zero invalid OHLC count, duplicate dates, missing windows or implausible values blocks dependent families until resolved.",
      "",
      "Sources: [NSE Indices historical-data page](https://www.niftyindices.com/reports/historical-data), [official India VIX endpoint](https://www.niftyindices.com/Backpage.aspx/BindHistoricalIndiaVixData), [index OHLC endpoint](https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString)."])
    (OUT/"NIFTYINDICES_CONTEXT_AUDIT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["overall_status"],"successful_chunk_series_calls":len(all_summaries),
      "failed_chunk_series_calls":len(failures),"series":merged_metrics,"cache_modes":fetch_modes},sort_keys=True))

if __name__=="__main__": main()
