#!/usr/bin/env python3
"""Extract exact-contract NSE index-futures rows from cached official daily F&O archives.

Raw price/OI/volume records are cached privately for later basis/cross-market tests.
Public files contain only per-date quality counts, coverage and cryptographic hashes.
"""
import csv, gzip, hashlib, io, json, math, zipfile
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

CACHE=Path("data/cache/phase109")
SOURCE=CACHE/"nse_eod"
FUTURES=CACHE/"futures_eod"
OUT=Path("results/phase109")
SYMBOLS={"NIFTY","BANKNIFTY","FINNIFTY","MIDCPNIFTY"}


def num(v):
    try:
        x=float(str(v).strip())
        return x if math.isfinite(x) else None
    except (TypeError,ValueError,OverflowError):
        return None


def parse_date(v):
    s=str(v or "").strip()
    for fmt in ("%Y-%m-%d","%d-%b-%Y","%d-%B-%Y","%d/%m/%Y","%d%m%Y","%Y%m%d"):
        try:
            return datetime.strptime(s[:10] if fmt=="%Y-%m-%d" else s,fmt).date().isoformat()
        except ValueError:
            pass
    return None


def pick(row,keys):
    for key in keys:
        if key in row and str(row[key]).strip()!="":
            return row[key]
    return None


def extract_zip(path, expected):
    raw=path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(names)!=1:
            raise ValueError("ZIP_CSV_MEMBER_COUNT_"+str(len(names)))
        member=names[0]; csv_bytes=z.read(member)
    rows=csv.DictReader(io.StringIO(csv_bytes.decode("utf-8-sig")))
    fields=rows.fieldnames or []
    if any(k in fields for k in ("FinInstrmTp","TckrSymb","OptnTp")):
        names={
          "instrument":("FinInstrmTp",),"symbol":("TckrSymb",),
          "date":("BizDt","TradDt"),"expiry":("FininstrmActlXpryDt","XpryDt"),
          "open":("OpnPric",),"high":("HghPric",),"low":("LwPric",),"close":("ClsPric",),
          "volume":("TtlTradgVol",),"oi":("OpnIntrst",),"lot_size":("NewBrdLotQty",),
          "underlying":("UndrlygPric",),"settlement":("SttlmPric",),
        }
        schema="UDiFF"
    else:
        names={
          "instrument":("INSTRUMENT",),"symbol":("SYMBOL",),
          "date":("TIMESTAMP","TRADE_DATE"),"expiry":("EXPIRY_DT",),
          "open":("OPEN",),"high":("HIGH",),"low":("LOW",),"close":("CLOSE",),
          "volume":("CONTRACTS","VOLUME"),"oi":("OPEN_INT","OPEN_INTEREST"),
          "lot_size":("BOARD_LOT","LOT_SIZE"),"underlying":(),"settlement":("SETTLE_PR",),
        }
        schema="LEGACY"
    required=("instrument","symbol","date","expiry","open","high","low","close","volume","oi")
    missing=[k for k in required if not any(alias in fields for alias in names[k])]
    if missing:
        raise ValueError("MISSING_FIELDS_"+",".join(missing))
    output=[]; selected=identity=complete=positive=zero=invalid=badvolume=badoi=badlot=0
    mismatches=duplicates=0; seen=set(); per_symbol=Counter(); expiry_values=[]
    for row in rows:
        inst=str(pick(row,names["instrument"]) or "").strip().upper()
        sym=str(pick(row,names["symbol"]) or "").strip().upper()
        if inst!="FUTIDX" or sym not in SYMBOLS:
            continue
        selected+=1; per_symbol[sym]+=1
        dt=parse_date(pick(row,names["date"])) or expected
        if dt!=expected: mismatches+=1
        expiry=parse_date(pick(row,names["expiry"]))
        prices={k:num(pick(row,names[k])) for k in ("open","high","low","close")}
        volume=num(pick(row,names["volume"])); oi=num(pick(row,names["oi"]))
        lot=num(pick(row,names["lot_size"])) if names["lot_size"] else None
        underlying=num(pick(row,names["underlying"])) if names["underlying"] else None
        identity_ok=(dt==expected and bool(expiry) and expiry>=dt)
        if identity_ok:
            identity+=1
            key=(dt,sym,expiry)
            if key in seen: duplicates+=1
            seen.add(key); expiry_values.append(expiry)
        if all(v is not None for v in prices.values()):
            complete+=1
        if volume is None or volume<0: badvolume+=1
        elif volume>0:
            positive+=1
            o,h,l,c=(prices[k] for k in ("open","high","low","close"))
            if any(v is None for v in (o,h,l,c)) or min(o,h,l,c)<0 or o<=0 or h<=0 or c<=0 or l>min(o,c)+1e-9 or h+1e-9<max(o,c) or l>h:
                invalid+=1
        elif volume==0: zero+=1
        if oi is None or oi<0: badoi+=1
        if lot is None or lot<=0: badlot+=1
        output.append({
          "trade_date":dt,"symbol":sym,"expiry":expiry or "",
          "open":prices["open"],"high":prices["high"],"low":prices["low"],"close":prices["close"],
          "volume":volume,"oi":oi,"lot_size":lot,"underlying_close":underlying,
          "settlement":num(pick(row,names["settlement"])) if names["settlement"] else None,
        })
    output.sort(key=lambda r:(r["trade_date"],r["symbol"],r["expiry"]))
    payload=json.dumps(output,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return {
      "status":"PARSED","date":expected,"schema":schema,"source_archive_sha256":hashlib.sha256(raw).hexdigest(),
      "future_rows_sha256":hashlib.sha256(payload).hexdigest(),"selected_futures_rows":selected,
      "identity_complete_rows":identity,"price_complete_rows":complete,"positive_volume_rows":positive,
      "zero_volume_rows":zero,"invalid_ohlc_positive_volume_rows":invalid,"invalid_or_missing_volume_rows":badvolume,
      "invalid_or_missing_oi_rows":badoi,"missing_or_nonpositive_lot_size_rows":badlot,
      "date_mismatch_rows":mismatches,"duplicate_daily_contract_keys":duplicates,
      "unique_daily_contract_keys":len(seen),"rows_by_symbol_json":json.dumps(dict(sorted(per_symbol.items())),sort_keys=True),
      "expiry_count":len(set(expiry_values)),"minimum_expiry":min(expiry_values) if expiry_values else "",
      "maximum_expiry":max(expiry_values) if expiry_values else "",
    },output


def main():
    OUT.mkdir(parents=True,exist_ok=True); FUTURES.mkdir(parents=True,exist_ok=True)
    audits=[]
    for path in sorted(SOURCE.glob("*/*.zip")):
        expected=path.stem
        try:
            dt=datetime.strptime(expected,"%Y%m%d").date().isoformat()
        except ValueError:
            continue
        target=FUTURES/path.parent.name/(path.stem+".json.gz")
        target.parent.mkdir(parents=True,exist_ok=True)
        try:
            summary,rows=extract_zip(path,dt)
            packed={"date":dt,"rows":rows,"source_archive_sha256":summary["source_archive_sha256"],
                    "future_rows_sha256":summary["future_rows_sha256"]}
            with gzip.open(target,"wt",encoding="utf-8",compresslevel=6) as fh:
                json.dump(packed,fh,separators=(",",":"),ensure_ascii=False)
            summary["private_cache_path"]=str(target)
        except Exception as exc:
            summary={"status":"FAILED","date":dt,"schema":"","source_archive_sha256":"",
                     "selected_futures_rows":0,"error_summary":type(exc).__name__+":"+str(exc)[:200]}
        audits.append(summary)
        if len(audits)%50==0:
            print(json.dumps({"processed_dates":len(audits),"with_futures":sum(int(x.get("selected_futures_rows",0)>0) for x in audits)},sort_keys=True),flush=True)
    fields=sorted({k for r in audits for k in r})
    with (OUT/"nse_index_futures_daily_coverage.csv").open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields,extrasaction="ignore"); w.writeheader(); w.writerows(audits)
    parsed=[r for r in audits if r.get("status")=="PARSED"]
    summary={
      "generated_utc":datetime.now(timezone.utc).isoformat(),"source":"Official NSE daily F&O archives",
      "option_archive_files_seen":len(audits),"futures_dates_parsed":len(parsed),
      "dates_with_selected_index_futures":sum(int(r.get("selected_futures_rows",0)>0) for r in parsed),
      "selected_futures_rows":sum(int(r.get("selected_futures_rows",0) or 0) for r in parsed),
      "identity_complete_rows":sum(int(r.get("identity_complete_rows",0) or 0) for r in parsed),
      "price_complete_rows":sum(int(r.get("price_complete_rows",0) or 0) for r in parsed),
      "positive_volume_rows":sum(int(r.get("positive_volume_rows",0) or 0) for r in parsed),
      "zero_volume_rows":sum(int(r.get("zero_volume_rows",0) or 0) for r in parsed),
      "invalid_ohlc_positive_volume_rows":sum(int(r.get("invalid_ohlc_positive_volume_rows",0) or 0) for r in parsed),
      "duplicate_daily_contract_keys":sum(int(r.get("duplicate_daily_contract_keys",0) or 0) for r in parsed),
      "missing_or_nonpositive_lot_size_rows":sum(int(r.get("missing_or_nonpositive_lot_size_rows",0) or 0) for r in parsed),
      "failed_dates":sum(1 for r in audits if r.get("status")!="PARSED"),
      "private_cache_bytes":sum(p.stat().st_size for p in FUTURES.glob("*/*.json.gz")),
      "interpretation":"Futures rows are extracted for feature/basis research only; daily OHLC/settlement is not an intraday fill model.",
    }
    (OUT/"nse_index_futures_summary.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    lines=[
      "# Official NSE index-futures extraction audit","",
      "Generated: "+summary["generated_utc"],"",
      "| Metric | Count |","|---|---:|",
      "| Option archives inspected | "+format(summary["option_archive_files_seen"],",")+" |",
      "| Archive dates parsed | "+format(summary["futures_dates_parsed"],",")+" |",
      "| Dates with selected index futures | "+format(summary["dates_with_selected_index_futures"],",")+" |",
      "| Futures rows | "+format(summary["selected_futures_rows"],",")+" |",
      "| Identity-complete rows | "+format(summary["identity_complete_rows"],",")+" |",
      "| Positive-volume rows | "+format(summary["positive_volume_rows"],",")+" |",
      "| Zero-volume rows | "+format(summary["zero_volume_rows"],",")+" |",
      "| Invalid positive-volume OHLC rows | "+format(summary["invalid_ohlc_positive_volume_rows"],",")+" |",
      "| Duplicate date-symbol-expiry keys | "+format(summary["duplicate_daily_contract_keys"],",")+" |",
      "| Rows missing/nonpositive lot size | "+format(summary["missing_or_nonpositive_lot_size_rows"],",")+" |",
      "| Failed date parses | "+format(summary["failed_dates"],",")+" |","",
      "Futures prices, OI and volume are stored only in private Actions cache; public outputs contain date-level aggregates and hashes. Futures close/settlement is not an intraday executable-fill claim. Spot-futures basis strategies are not eligible until futures are synchronized against the underlying index close, maturity days are checked, contract sizes validated and point-in-time rates/corporate actions are applied if the rule requires them."
    ]
    (OUT/"NSE_INDEX_FUTURES_AUDIT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(summary,sort_keys=True))


if __name__=="__main__": main()
