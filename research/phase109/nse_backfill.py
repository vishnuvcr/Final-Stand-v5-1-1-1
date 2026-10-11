#!/usr/bin/env python3
"""Bounded NSE official index-option EOD backfill into workflow cache.

Raw ZIPs remain under data/cache (never git-added or uploaded as public artifacts).
Only date-level aggregates, hashes and error counts are emitted.
"""
import argparse, csv, hashlib, io, json, math, os, random, time, urllib.error, urllib.request, zipfile
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

CACHE_ROOT = Path("data/cache/phase109/nse_eod")
OUT = Path("results/phase109")
UA = "Mozilla/5.0 (compatible; FinalStandPhase109/1.0)"
INDEX_SYMBOLS = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"}
PRICE_FIELDS = ("open", "high", "low", "close")


def parse_number(v):
    try:
        x=float(str(v).strip())
        return x if math.isfinite(x) else None
    except (ValueError, TypeError, OverflowError):
        return None


def parse_date(v):
    s=str(v or "").strip()
    formats=("%Y-%m-%d", "%d-%b-%Y", "%d-%B-%Y", "%d/%m/%Y", "%d%m%Y", "%Y%m%d")
    for fmt in formats:
        try:
            return datetime.strptime(s[:10] if fmt=="%Y-%m-%d" else s, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def get_url(date_obj):
    if date_obj >= date(2024, 7, 8):
        name=f"BhavCopy_NSE_FO_0_0_0_{date_obj:%Y%m%d}_F_0000.csv.zip"
        return [
          f"https://nsearchives.nseindia.com/content/fo/{name}",
          f"https://archives.nseindia.com/content/fo/{name}",
        ]
    name=f"fo{date_obj:%d}{date_obj.strftime('%b').upper()}{date_obj.year}bhav.csv.zip"
    return [
      f"https://archives.nseindia.com/content/historical/DERIVATIVES/{date_obj.year}/{date_obj.strftime('%b').upper()}/{name}",
      f"https://nsearchives.nseindia.com/content/historical/DERIVATIVES/{date_obj.year}/{date_obj.strftime('%b').upper()}/{name}",
    ]


def read_archive(payload, expected):
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        names=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(names)!=1:
            raise ValueError("ZIP_CSV_MEMBER_COUNT_" + str(len(names)))
        member=names[0]
        raw=z.read(member)
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    fields=reader.fieldnames or []
    udiff=any(k in fields for k in ("FinInstrmTp","TckrSymb","OptnTp"))
    if udiff:
        aliases={
          "symbol":"TckrSymb","expiry":"FininstrmActlXpryDt","strike":"StrkPric","side":"OptnTp",
          "date":"BizDt","open":"OpnPric","high":"HghPric","low":"LwPric","close":"ClsPric",
          "volume":"TtlTradgVol","oi":"OpnIntrst","lot_size":"NewBrdLotQty","instrument":"FinInstrmTp",
          "underlying":"UndrlygPric",
        }
        schema="UDiFF"
    else:
        aliases={
          "symbol":"SYMBOL","expiry":"EXPIRY_DT","strike":"STRIKE_PR","side":"OPTION_TYP",
          "date":"TIMESTAMP","open":"OPEN","high":"HIGH","low":"LOW","close":"CLOSE",
          "volume":"CONTRACTS","oi":"OPEN_INT","lot_size":"","instrument":"INSTRUMENT","underlying":"",
        }
        schema="LEGACY"
    required=("symbol","expiry","strike","side","open","high","low","close","volume","oi","instrument")
    missing=[k for k in required if not aliases[k] or aliases[k] not in fields]
    if missing:
        raise ValueError("SCHEMA_MISSING_" + ",".join(missing))
    selected=identity=prices_ok=positive_vol=zero_vol=missing_vol=missing_oi=missing_lot=invalid_ohlc=0
    mismatch=0
    unique_keys=set()
    duplicates=0
    rows_by_symbol=Counter()
    expiries=[]
    for row in reader:
        symbol=str(row.get(aliases["symbol"],"")).strip().upper()
        side=str(row.get(aliases["side"],"")).strip().upper()
        instrument=str(row.get(aliases["instrument"],"")).strip().upper()
        if symbol not in INDEX_SYMBOLS or side not in {"CE","PE"}:
            continue
        if schema=="UDiFF" and instrument not in {"OPTIDX"}:
            continue
        if schema=="LEGACY" and instrument not in {"OPTIDX","OPTIDX "}:
            continue
        selected+=1
        rows_by_symbol[symbol]+=1
        row_date=parse_date(row.get(aliases["date"])) or expected.isoformat()
        if row_date != expected.isoformat():
            mismatch+=1
        expiry=parse_date(row.get(aliases["expiry"]))
        strike=parse_number(row.get(aliases["strike"]))
        p={name:parse_number(row.get(aliases[name])) for name in PRICE_FIELDS}
        volume=parse_number(row.get(aliases["volume"]))
        oi=parse_number(row.get(aliases["oi"]))
        lot_size=parse_number(row.get(aliases["lot_size"])) if aliases["lot_size"] else None
        identity_ok=(row_date==expected.isoformat() and expiry is not None and strike is not None and strike>0)
        if identity_ok:
            identity+=1
            key=(row_date,symbol,expiry,format(strike,".10g"),side)
            if key in unique_keys:
                duplicates+=1
            else:
                unique_keys.add(key)
            expiries.append(expiry)
        if all(v is not None for v in p.values()):
            prices_ok+=1
        if volume is None:
            missing_vol+=1
        elif volume>0:
            positive_vol+=1
            o,h,l,c=(p[k] for k in PRICE_FIELDS)
            if (any(v is None for v in (o,h,l,c)) or o<=0 or h<=0 or c<=0 or l<0 or
                l>min(o,c)+1e-9 or h+1e-9<max(o,c) or l>h+1e-9):
                invalid_ohlc+=1
        else:
            zero_vol+=1
        if oi is None: missing_oi+=1
        if lot_size is None or lot_size<=0: missing_lot+=1
    return {
      "status":"DOWNLOADED_AND_PARSED","schema":schema,"expected_date":expected.isoformat(),
      "compressed_bytes":len(payload),"csv_bytes":len(raw),"csv_member":member,"csv_rows":None,
      "archive_sha256":hashlib.sha256(payload).hexdigest(),"selected_index_option_rows":selected,
      "identity_complete_rows":identity,"price_complete_rows":prices_ok,
      "positive_volume_rows":positive_vol,"zero_volume_rows":zero_vol,"missing_volume_rows":missing_vol,
      "missing_oi_rows":missing_oi,"missing_lot_size_rows":missing_lot,
      "invalid_ohlc_positive_volume_rows":invalid_ohlc,"date_mismatch_rows":mismatch,
      "duplicate_daily_contract_keys":duplicates,"unique_daily_contract_keys":len(unique_keys),
      "rows_by_symbol_json":json.dumps(dict(sorted(rows_by_symbol.items())),sort_keys=True),
      "expiry_count":len(set(expiries)),"minimum_expiry":min(expiries) if expiries else "",
      "maximum_expiry":max(expiries) if expiries else "",
      "note":"Only aggregated audit is retained in public report; raw archive stays in Actions cache.",
    }


def attempt_download(day):
    last=[]
    for url in get_url(day):
        try:
            req=urllib.request.Request(url,headers={
              "User-Agent":UA,"Accept":"application/zip,application/octet-stream,*/*",
              "Referer":"https://www.nseindia.com/all-reports-derivatives",
            })
            with urllib.request.urlopen(req,timeout=30) as res:
                if res.status!=200: raise RuntimeError("HTTP_"+str(res.status))
                payload=res.read()
            # Inspect schema/data before caching as accepted file.
            parsed=read_archive(payload,day)
            return payload,parsed,url
        except urllib.error.HTTPError as e:
            last.append({"url":url,"status":"HTTP_"+str(e.code)})
            if e.code not in (404,403,429,500,502,503,504):
                break
        except Exception as e:
            last.append({"url":url,"status":type(e).__name__+":"+str(e)[:160]})
        time.sleep(0.25+random.random()*0.15)
    return None,{"status":"NO_ARCHIVE_OR_FETCH_ERROR","expected_date":day.isoformat(),
                 "error_summary":json.dumps(last,sort_keys=True)}, ""


def expected_weekdays(start,end):
    cur=start
    while cur<end:
        if cur.weekday()<5:
            yield cur
        cur+=timedelta(days=1)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--from-date",default="2023-10-01")
    ap.add_argument("--to-date",default="2026-10-09",help="exclusive")
    ap.add_argument("--max-days",type=int,default=0,help="Optional cap on weekday probes; 0 means all weekdays")
    ap.add_argument("--retry-failures",action="store_true")
    args=ap.parse_args()
    start=date.fromisoformat(args.from_date); end=date.fromisoformat(args.to_date)
    if end<=start: raise ValueError("to-date must be after from-date")
    CACHE_ROOT.mkdir(parents=True,exist_ok=True); OUT.mkdir(parents=True,exist_ok=True)
    dates=list(expected_weekdays(start,end))
    if args.max_days>0: dates=dates[:args.max_days]
    out_rows=[]
    failures=Counter()
    for ix,day in enumerate(dates,1):
        target=CACHE_ROOT/str(day.year)/(day.strftime("%Y%m%d")+".zip")
        target.parent.mkdir(parents=True,exist_ok=True)
        parsed=None; url=""; payload=None
        if target.exists() and target.stat().st_size:
            try:
                payload=target.read_bytes()
                parsed=read_archive(payload,day)
                parsed["status"]="CACHE_HIT_VALIDATED"
                url="cached-official-NSE-archive"
            except Exception:
                # A corrupt or schema-invalid cache object must be deleted so the
                # same workflow can recover it without a separate manual retry flag.
                target.unlink(missing_ok=True)
                payload=None; parsed=None
        if payload is None and (args.retry_failures or not target.exists()):
            payload,parsed,url=attempt_download(day)
            if payload is not None:
                target.write_bytes(payload)
        if parsed is None:
            row={"expected_date":day.isoformat(),"status":"NO_ARCHIVE_OR_FETCH_ERROR",
                 "error_summary":"cache invalid or retry disabled"}
        else:
            row=dict(parsed)
            row["source_url"]=url
            row["cache_path"]=str(target)
        out_rows.append(row)
        failures[row.get("status","UNKNOWN")]+=1
        if ix%25==0:
            print(json.dumps({"progress":ix,"total_weekdays":len(dates),"date":day.isoformat(),
                              "archives_parsed":sum(1 for r in out_rows if r["status"] in {"DOWNLOADED_AND_PARSED","CACHE_HIT_VALIDATED"}),
                              "no_archive_or_error":sum(1 for r in out_rows if r["status"]=="NO_ARCHIVE_OR_FETCH_ERROR")},sort_keys=True),flush=True)
        # Polite pacing even after cached items.
        time.sleep(0.05)
    csv_path=OUT/"nse_index_options_daily_coverage.csv"
    fields=sorted({k for r in out_rows for k in r})
    with csv_path.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields,extrasaction="ignore"); w.writeheader(); w.writerows(out_rows)
    good=[r for r in out_rows if r.get("status") in {"DOWNLOADED_AND_PARSED","CACHE_HIT_VALIDATED"}]
    summary={
      "generated_utc":datetime.now(timezone.utc).isoformat(),"from_date":start.isoformat(),"to_date_exclusive":end.isoformat(),
      "requested_weekdays":len(dates),"archive_dates_parsed":len(good),
      "no_archive_or_fetch_error":sum(r.get("status")=="NO_ARCHIVE_OR_FETCH_ERROR" for r in out_rows),
      "legacy_archive_count":sum(r.get("schema")=="LEGACY" for r in good),
      "udiff_archive_count":sum(r.get("schema")=="UDiFF" for r in good),
      "selected_index_option_rows":sum(int(r.get("selected_index_option_rows",0) or 0) for r in good),
      "identity_complete_rows":sum(int(r.get("identity_complete_rows",0) or 0) for r in good),
      "price_complete_rows":sum(int(r.get("price_complete_rows",0) or 0) for r in good),
      "positive_volume_rows":sum(int(r.get("positive_volume_rows",0) or 0) for r in good),
      "zero_volume_rows":sum(int(r.get("zero_volume_rows",0) or 0) for r in good),
      "invalid_ohlc_positive_volume_rows":sum(int(r.get("invalid_ohlc_positive_volume_rows",0) or 0) for r in good),
      "duplicate_daily_contract_keys":sum(int(r.get("duplicate_daily_contract_keys",0) or 0) for r in good),
      "date_mismatch_rows":sum(int(r.get("date_mismatch_rows",0) or 0) for r in good),
      "missing_lot_size_rows":sum(int(r.get("missing_lot_size_rows",0) or 0) for r in good),
      "compressed_cache_bytes":sum((CACHE_ROOT/str(r["expected_date"][:4])/(r["expected_date"].replace("-","")+".zip")).stat().st_size for r in good if (CACHE_ROOT/str(r["expected_date"][:4])/(r["expected_date"].replace("-","")+".zip")).exists()),
      "run_status_counts":dict(sorted(failures.items())),
      "interpretation":"Weekdays with no archive may be exchange holidays or fetch/URL errors; they are not automatically treated as sessions. A separate official calendar/coverage audit is required. This data gate does not mean any strategy was tested.",
      "raw_data_policy":"Raw ZIPs are stored only in the workflow cache and excluded from git and public artifacts.",
    }
    (OUT/"nse_index_options_backfill_summary.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    lines=[
      "# NSE index-options daily archive coverage report","",
      "Generated: "+summary["generated_utc"],
      "Window: "+summary["from_date"]+" through "+summary["to_date_exclusive"]+" (end exclusive)","",
      "**Data-acquisition audit only; no strategy/configuration P&L evaluated.**",
      "",
      "| Metric | Result |","|---|---:|",
    ]
    for label,key in [
      ("Weekdays requested","requested_weekdays"),("Valid archive dates parsed","archive_dates_parsed"),
      ("Legacy archives","legacy_archive_count"),("UDiFF archives","udiff_archive_count"),
      ("Selected option rows","selected_index_option_rows"),("Identity-complete rows","identity_complete_rows"),
      ("Price-complete rows","price_complete_rows"),("Positive-volume rows","positive_volume_rows"),
      ("Zero-volume rows","zero_volume_rows"),("Invalid positive-volume OHLC rows","invalid_ohlc_positive_volume_rows"),
      ("Duplicate daily contract keys","duplicate_daily_contract_keys"),("Date mismatch rows","date_mismatch_rows"),
      ("Rows missing/without lot size","missing_lot_size_rows"),("Raw cache bytes","compressed_cache_bytes"),
      ("Weekday no-archive/fetch failures","no_archive_or_fetch_error")]:
        lines.append("| "+label+" | "+format(summary[key],",")+" |")
    lines.extend(["","## Interpretation","",
      "The downloader caches original official NSE daily archives privately and publishes no raw option rows. Weekdays without a valid archive can include exchange holidays or source/network issues; this is not an authoritative exchange-calendar coverage count.",
      "Before using these data for strategy backtesting, Phase 109 still needs: (1) reconcile all actual exchange sessions using an official trading calendar; (2) verify exact expiry/strike/option-type identity and schema transitions; (3) confirm lot size and contract specifications per date (legacy files do not supply lot size); (4) exclude zero-volume and otherwise non-executable rows; (5) build development/validation/untouched chronological splits; and (6) prove cost/accounting reconciliation. EOD high/low cannot be used to claim exact stop/target execution or bid/ask fills.",
      "No profitable strategy or completed exhaustive grid is implied by this archive count."])
    (OUT/"NSE_INDEX_OPTIONS_BACKFILL_REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({k:summary[k] for k in ("requested_weekdays","archive_dates_parsed","legacy_archive_count","udiff_archive_count","selected_index_option_rows","positive_volume_rows","zero_volume_rows","invalid_ohlc_positive_volume_rows","duplicate_daily_contract_keys","no_archive_or_fetch_error","compressed_cache_bytes")},sort_keys=True))

if __name__=="__main__": main()
