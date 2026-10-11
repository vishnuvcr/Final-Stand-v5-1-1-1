#!/usr/bin/env python3
"""Probe NSE official F&O archives at the legacy/UDiFF boundary and recent date.

Raw bytes stay in memory. This is an access/schema check, not a bulk backfill
or strategy evaluation.
"""
import csv, hashlib, io, json, math, time, urllib.request, urllib.error, zipfile
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

OUT = Path("results/phase109")
UNDERLYINGS = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"}
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; FinalStandPhase109/1.0)",
           "Accept": "application/zip,application/octet-stream,*/*",
           "Referer": "https://www.nseindia.com/all-reports-derivatives"}

def num(v):
    try:
        x = float(str(v).strip())
        return x if math.isfinite(x) else None
    except (ValueError, TypeError, OverflowError):
        return None

def dayparse(v):
    s = str(v or "").strip()
    for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%d-%B-%Y", "%d/%m/%Y", "%d%m%Y", "%Y%m%d"):
        try:
            return datetime.strptime(s[:10] if fmt == "%Y-%m-%d" else s, fmt).date().isoformat()
        except ValueError:
            pass
    return None

def urls_for(d):
    if d >= date(2024, 7, 8):
        name = f"BhavCopy_NSE_FO_0_0_0_{d:%Y%m%d}_F_0000.csv.zip"
        return [("UDiFF", f"https://nsearchives.nseindia.com/content/fo/{name}"),
                ("UDiFF", f"https://archives.nseindia.com/content/fo/{name}")]
    mon = d.strftime("%b").upper()
    name = f"fo{d:%d}{mon}{d.year}bhav.csv.zip"
    folder = f"{d.year}/{mon}"
    return [("LEGACY", f"https://archives.nseindia.com/content/historical/DERIVATIVES/{folder}/{name}"),
            ("LEGACY", f"https://nsearchives.nseindia.com/content/historical/DERIVATIVES/{folder}/{name}")]

def request_bytes(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=35) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP_{resp.status}")
        return resp.read()

def pick(r, names):
    for n in names:
        if n in r and str(r[n]).strip() != "":
            return r[n]
    return None

def inspect(payload, expected, fmt):
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        names = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(names) != 1:
            raise ValueError("EXPECTED_ONE_CSV")
        member = names[0]
        raw = z.read(member)
    body = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(body))
    fields = reader.fieldnames or []
    aliases = {
      "symbol": ("TckrSymb", "SYMBOL", "Symbol"),
      "expiry": ("FininstrmActlXpryDt", "XpryDt", "EXPIRY_DT", "Expiry"),
      "strike": ("StrkPric", "STRIKE_PR", "Strike"),
      "side": ("OptnTp", "OPTION_TYP", "OptionType", "option_type"),
      "date": ("BizDt", "TradDt", "TIMESTAMP", "TradeDate"),
      "open": ("OpnPric", "OPEN", "Open", "open"),
      "high": ("HghPric", "HIGH", "High", "high"),
      "low": ("LwPric", "LOW", "Low", "low"),
      "close": ("ClsPric", "CLOSE", "Close", "close"),
      "volume": ("TtlTradgVol", "CONTRACTS", "Volume", "volume"),
      "oi": ("OpnIntrst", "OPEN_INT", "OpenInterest", "open_interest"),
      "instrument": ("FinInstrmTp", "INSTRUMENT", "InstrumentType"),
      "underlying": ("UndrlygPric", "UNDERLYING", "UnderlyingValue", "underlying"),
    }
    actual_fmt = "UDiFF" if any(x in fields for x in ("FinInstrmTp", "TckrSymb", "OptnTp")) else "LEGACY"
    if fmt == "UDiFF" and actual_fmt != "UDiFF":
        raise ValueError("UDIFF_ARCHIVE_SCHEMA_MISMATCH")
    source_fields = {k: next((n for n in ns if n in fields), "") for k, ns in aliases.items()}
    required = ("symbol", "expiry", "strike", "side", "open", "high", "low", "close", "volume", "oi")
    missing = [k for k in required if not source_fields[k]]
    if missing:
        raise ValueError("MISSING_FIELDS:" + ",".join(missing))
    count = 0
    selected_by_symbol = Counter()
    keys = Counter()
    identity = price_complete = positive_volume = zero_volume = invalid_positive = mismatch = 0
    for r in reader:
        sym = str(pick(r, aliases["symbol"]) or "").strip().upper()
        side = str(pick(r, aliases["side"]) or "").strip().upper()
        if sym not in UNDERLYINGS or side not in {"CE", "PE"}:
            continue
        count += 1
        selected_by_symbol[sym] += 1
        rd = dayparse(pick(r, aliases["date"])) or expected.isoformat()
        if rd != expected.isoformat():
            mismatch += 1
        expiry = dayparse(pick(r, aliases["expiry"]))
        strike = num(pick(r, aliases["strike"]))
        p = [num(pick(r, aliases[k])) for k in ("open", "high", "low", "close")]
        volume = num(pick(r, aliases["volume"]))
        ident = rd == expected.isoformat() and expiry and strike is not None and strike > 0
        if ident:
            identity += 1
            keys[(rd, sym, expiry, format(strike, ".10g"), side)] += 1
        if all(v is not None for v in p):
            price_complete += 1
        if volume is not None and volume > 0:
            positive_volume += 1
            o, h, lo, cl = p
            if any(v is None for v in p) or min(p) < 0 or o <= 0 or h <= 0 or cl <= 0 or lo > min(o, cl) + 1e-9 or h + 1e-9 < max(o, cl):
                invalid_positive += 1
        elif volume == 0:
            zero_volume += 1
    csv_rows = sum(1 for _ in io.StringIO(body)) - 1
    return {
      "status": "SCHEMA_AND_ROWS_PROBED", "format": actual_fmt,
      "expected_date": expected.isoformat(), "zip_sha256": hashlib.sha256(payload).hexdigest(),
      "archive_bytes": len(payload), "csv_member": member, "csv_bytes": len(raw),
      "csv_rows": csv_rows, "headers": fields, "field_aliases": source_fields,
      "selected_index_option_rows": count, "selected_rows_by_symbol": dict(sorted(selected_by_symbol.items())),
      "identity_complete_rows": identity, "price_complete_rows": price_complete,
      "positive_volume_rows": positive_volume, "zero_volume_rows": zero_volume,
      "invalid_ohlc_positive_volume_rows": invalid_positive, "date_mismatch_rows": mismatch,
      "duplicate_daily_contract_keys": sum(v - 1 for v in keys.values() if v > 1),
      "unique_daily_contract_keys": len(keys),
      "note": "One session only; this does not prove continuous history, source rights or achievable intraday fills."
    }

def probe(day_s):
    d = date.fromisoformat(day_s)
    attempts = []
    for fmt, url in urls_for(d):
        try:
            result = inspect(request_bytes(url), d, fmt)
            result.update({"source": "Official NSE F&O archive", "url": url, "http_status": 200})
            return result
        except urllib.error.HTTPError as e:
            attempts.append({"url": url, "status": "HTTP_" + str(e.code)})
        except Exception as e:
            attempts.append({"url": url, "status": type(e).__name__ + ":" + str(e)[:220]})
        time.sleep(0.3)
    return {"source": "Official NSE F&O archive", "status": "FAILED", "expected_date": day_s,
            "attempts": attempts, "note": "Do not silently replace a failed official source with an unaudited mirror."}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    probes = [probe("2024-07-05"), probe("2024-07-08"), probe("2026-10-08")]
    report = {
      "generated_utc": datetime.now(timezone.utc).isoformat(),
      "purpose": "Official NSE F&O archive source/schema gate; no strategy performance is evaluated.",
      "overall_status": "PASS" if all(p["status"] == "SCHEMA_AND_ROWS_PROBED" for p in probes) else "PARTIAL_OR_FAILED",
      "url_patterns": {
        "legacy": "https://archives.nseindia.com/content/historical/DERIVATIVES/{YYYY}/{MON}/fo{DDMONYYYY}bhav.csv.zip",
        "UDiFF": "https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{YYYYMMDD}_F_0000.csv.zip",
      },
      "probes": probes
    }
    (OUT / "nse_archive_source_feasibility.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    lines = [
      "# Official NSE archive access and schema feasibility", "",
      "Generated: " + report["generated_utc"],
      "Overall probe: " + report["overall_status"], "",
      "Three schema-boundary dates are sampled: last pre-UDiFF session (5 July 2024), first UDiFF session (8 July 2024), and a recent session (8 October 2026). ZIP bytes were parsed in memory and not saved or published. This is not a historical backfill or performance test.", ""
    ]
    for p in probes:
        lines.extend([
          "## " + p["expected_date"] + " — " + p["status"], "",
          "Format: " + str(p.get("format", "unknown")) + "; HTTP: " + str(p.get("http_status", "n/a")) + ".",
          "Index-option rows: " + str(p.get("selected_index_option_rows", "n/a")) + "; exact daily contract keys: " + str(p.get("unique_daily_contract_keys", "n/a")) + "; duplicate keys: " + str(p.get("duplicate_daily_contract_keys", "n/a")) + ".",
          "Identity complete: " + str(p.get("identity_complete_rows", "n/a")) + "; price-complete: " + str(p.get("price_complete_rows", "n/a")) + "; positive volume: " + str(p.get("positive_volume_rows", "n/a")) + "; invalid OHLC with positive volume: " + str(p.get("invalid_ohlc_positive_volume_rows", "n/a")) + ".",
          "Source URL: " + str(p.get("url", "n/a")),
          "Details: " + p.get("note", ""), ""
        ])
        if p.get("attempts"):
            lines.append("Failed attempts: " + json.dumps(p["attempts"], ensure_ascii=False) + "\n")
    lines.extend([
      "## Source-policy gate", "",
      "If schema and data-quality gates pass, use official NSE daily archives as primary exact-contract EOD options data. Store raw archives only in private workflow cache/working storage; publish aggregate coverage reports and hashes. EOD OHLC is not bid/ask/depth or proof of achievable fills.",
      "Before any strategy result, bulk coverage must reconcile expected trading sessions, missing files, duplicate contract keys, lot-size changes, positive volume, contract expiry and chronology. This probe alone does not establish development/validation/untouched-test coverage."
    ])
    (OUT / "NSE_ARCHIVE_SOURCE_FEASIBILITY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["overall_status"], "probes": [
      {"date": p["expected_date"], "status": p["status"], "rows": p.get("selected_index_option_rows"), "format": p.get("format")}
      for p in probes
    ]}, sort_keys=True))

if __name__ == "__main__":
    main()
