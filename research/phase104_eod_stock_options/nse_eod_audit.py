#!/usr/bin/env python3
"""Bounded NSE UDiFF EOD stock-options data-quality audit. Raw rows remain ephemeral."""
import argparse
import csv
import hashlib
import io
import json
import os
import time
import urllib.error
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

NSE_URL = "https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{date}_F_0000.csv.zip"
SYMBOLS = ("HDFCBANK", "ICICIBANK", "RELIANCE", "SBIN", "INFY")
REQUIRED = {
    "FinInstrmTp", "TckrSymb", "XpryDt", "StrkPric", "OptnTp",
    "OpnPric", "HghPric", "LwPric", "ClsPric", "TtlTradgVol", "OpnIntrst",
}
PRICE_FIELDS = ("OpnPric", "HghPric", "LwPric", "ClsPric")
INSTRUMENTS = {"STO", "OPTSTK"}


def parse_date(value):
    value = str(value or "").strip()
    for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%d-%B-%Y", "%Y%m%d"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def parse_number(value):
    try:
        n = float(str(value).strip())
        if n != n or abs(n) == float("inf"):
            return None
        return n
    except (ValueError, TypeError, OverflowError):
        return None


def check_window(start, end):
    days = (date.fromisoformat(end) - date.fromisoformat(start)).days
    if days < 1 or days > 30:
        raise ValueError("Window must be 1–30 calendar days, with an exclusive end date.")
    return days


def parse_nse_archive(payload, expected_day, symbols=SYMBOLS):
    """Parse selected stock-option rows into ephemeral memory; never write or return raw bytes."""
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        csv_names = [n for n in archive.namelist() if n.lower().endswith(".csv")]
        if len(csv_names) != 1:
            raise ValueError("Expected exactly one CSV in the NSE daily archive ZIP.")
        body = archive.read(csv_names[0]).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(body))
    if not reader.fieldnames or not REQUIRED.issubset(set(reader.fieldnames)):
        raise ValueError("NSE UDiFF schema is missing required stock-option identity/OHLC columns.")
    chosen = {s.upper() for s in symbols}
    rows = []
    count_selected = 0
    date_mismatch = 0
    for raw in reader:
        sym = str(raw.get("TckrSymb", "")).strip().upper()
        instrument = str(raw.get("FinInstrmTp", "")).strip().upper()
        if sym not in chosen or instrument not in INSTRUMENTS:
            continue
        count_selected += 1
        biz_day = parse_date(raw.get("BizDt")) if "BizDt" in raw else expected_day
        if biz_day and biz_day != expected_day:
            date_mismatch += 1
        expiry = parse_date(raw.get("FininstrmActlXpryDt")) or parse_date(raw.get("XpryDt"))
        side = str(raw.get("OptnTp", "")).strip().upper()
        strike = parse_number(raw.get("StrkPric"))
        identity_ok = bool(biz_day == expected_day and expiry and strike is not None and side in {"CE", "PE"})
        rows.append({
            "trade_date": biz_day or expected_day,
            "symbol": sym,
            "expiry": expiry,
            "strike": strike,
            "option_type": side,
            "identity_complete": identity_ok,
            "prices_complete": all(parse_number(raw.get(k)) is not None for k in PRICE_FIELDS),
            "volume": parse_number(raw.get("TtlTradgVol")),
            "oi": parse_number(raw.get("OpnIntrst")),
            "underlying": parse_number(raw.get("UndrlygPric")) if "UndrlygPric" in raw else None,
            "lot_size": parse_number(raw.get("NewBrdLotQty")) if "NewBrdLotQty" in raw else None,
        })
    return {"rows": rows, "selected_rows": count_selected, "date_mismatch_rows": date_mismatch}


def summarize_rows(rows, selected_row_count=None, date_mismatch_rows=0):
    """Return only aggregate contract-identity and field-completeness diagnostics."""
    selected_row_count = len(rows) if selected_row_count is None else selected_row_count
    key_counts = Counter()
    by_symbol = defaultdict(lambda: {
        "rows": 0, "identity_complete_rows": 0, "price_complete_rows": 0,
        "positive_volume_rows": 0, "zero_volume_rows": 0, "missing_volume_rows": 0,
        "missing_oi_rows": 0, "missing_underlying_rows": 0, "missing_lot_size_rows": 0,
        "unique_contract_keys": 0, "trade_dates": set(), "expiries": set(),
    })
    for row in rows:
        sym = row["symbol"]
        s = by_symbol[sym]
        s["rows"] += 1
        s["trade_dates"].add(row["trade_date"])
        if row["identity_complete"]:
            s["identity_complete_rows"] += 1
            key = (row["trade_date"], sym, row["expiry"], format(row["strike"], ".10g"), row["option_type"])
            key_counts[key] += 1
            s["expiries"].add(row["expiry"])
        if row["prices_complete"]:
            s["price_complete_rows"] += 1
        vol = row["volume"]
        if vol is None:
            s["missing_volume_rows"] += 1
        elif vol > 0:
            s["positive_volume_rows"] += 1
        else:
            s["zero_volume_rows"] += 1
        if row["oi"] is None:
            s["missing_oi_rows"] += 1
        if row["underlying"] is None:
            s["missing_underlying_rows"] += 1
        if row["lot_size"] is None or row["lot_size"] <= 0:
            s["missing_lot_size_rows"] += 1
    duplicate_count = sum(n - 1 for n in key_counts.values() if n > 1)
    for symbol, s in by_symbol.items():
        s["unique_contract_keys"] = sum(
            1 for key in key_counts if key[1] == symbol
        )
        s["trade_dates"] = len(s["trade_dates"])
        s["expiries"] = len(s["expiries"])
    n = len(rows)
    identity_n = sum(r["identity_complete"] for r in rows)
    price_n = sum(r["prices_complete"] for r in rows)
    return {
        "selected_rows": selected_row_count,
        "parsed_rows": n,
        "identity_complete_rows": identity_n,
        "identity_completeness_pct": round(100 * identity_n / n, 4) if n else 0.0,
        "price_complete_rows": price_n,
        "price_completeness_pct": round(100 * price_n / n, 4) if n else 0.0,
        "positive_volume_rows": sum((r["volume"] is not None and r["volume"] > 0) for r in rows),
        "zero_volume_rows": sum((r["volume"] == 0) for r in rows),
        "missing_volume_rows": sum((r["volume"] is None) for r in rows),
        "missing_oi_rows": sum((r["oi"] is None) for r in rows),
        "missing_underlying_rows": sum((r["underlying"] is None) for r in rows),
        "missing_lot_size_rows": sum((r["lot_size"] is None or r["lot_size"] <= 0) for r in rows),
        "duplicate_daily_contract_keys": duplicate_count,
        "date_mismatch_rows": date_mismatch_rows,
        "unique_contract_keys": sum(1 for nkey in key_counts.values()),
        "by_symbol": {k: v for k, v in sorted(by_symbol.items())},
        "matched_expiry_counts": dict(sorted(Counter(r["expiry"] for r in rows if r["identity_complete"]).items())),
    }


def fetch_bytes(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "FinalStand-Phase104/1.0", "Accept": "application/zip"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-date", default=os.getenv("PHASE104_FROM_DATE", "2026-08-03"))
    parser.add_argument("--to-date", default=os.getenv("PHASE104_TO_DATE", "2026-09-02"), help="exclusive")
    parser.add_argument("--out-dir", default="results/phase104")
    args = parser.parse_args()
    days = check_window(args.from_date, args.to_date)
    start, end = date.fromisoformat(args.from_date), date.fromisoformat(args.to_date)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    result = {
        "phase": "104.1",
        "run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "window": {"from_inclusive": args.from_date, "to_exclusive": args.to_date, "calendar_days": days},
        "source": "NSE official daily UDiFF F&O bhavcopy archive",
        "source_url_template": NSE_URL,
        "symbols": list(SYMBOLS),
        "raw_rows_persisted": False,
        "raw_rows_in_artifact": False,
        "daily_archives": [],
        "archive_sha256": {},
        "archive_fetch_errors": [],
        "no_archive_dates": [],
        "aggregate": {},
        "status": "PENDING",
        "known_limits": [
            "Daily OHLC bars do not provide historical bid/ask, depth, queue position, latency or verified executable fills.",
            "Daily archive schema and technical access do not prove rights to cache or redistribute raw exchange data; this workflow publishes aggregates only.",
            "Corporate-action and point-in-time universe adjustments are separate required inputs for multi-year strategy research.",
            "Paytm Money brokerage and statutory/exchange costs must be date-effective before strategy P&L.",
        ],
    }
    all_rows, selected_total, date_mismatch_total = [], 0, 0
    for i in range(days):
        day = (start + timedelta(days=i)).isoformat()
        url = NSE_URL.format(date=day.replace("-", ""))
        try:
            payload = fetch_bytes(url)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                result["no_archive_dates"].append(day)
                result["daily_archives"].append({"date": day, "status": "NO_ARCHIVE_OR_NONTRADING_DATE"})
            else:
                result["archive_fetch_errors"].append({"date": day, "error_type": "HTTPError", "http_status": exc.code})
                result["daily_archives"].append({"date": day, "status": "HTTP_ERROR", "http_status": exc.code})
            continue
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            result["archive_fetch_errors"].append({"date": day, "error_type": type(exc).__name__})
            result["daily_archives"].append({"date": day, "status": "NETWORK_ERROR"})
            continue
        digest = hashlib.sha256(payload).hexdigest()
        result["archive_sha256"][day] = digest
        try:
            parsed = parse_nse_archive(payload, day)
        except Exception as exc:
            result["archive_fetch_errors"].append({"date": day, "error_type": type(exc).__name__, "safe_message": " ".join(str(exc).split())[:180]})
            result["daily_archives"].append({"date": day, "status": "SCHEMA_OR_PARSE_ERROR"})
            continue
        all_rows.extend(parsed["rows"])
        selected_total += parsed["selected_rows"]
        date_mismatch_total += parsed["date_mismatch_rows"]
        result["daily_archives"].append({
            "date": day, "status": "ARCHIVE_PARSED",
            "selected_stock_option_rows": parsed["selected_rows"],
            "identity_complete_rows": sum(r["identity_complete"] for r in parsed["rows"]),
            "sha256": digest,
        })
        time.sleep(0.15)
    result["aggregate"] = summarize_rows(all_rows, selected_total, date_mismatch_total)
    parsed_days = sum(r["status"] == "ARCHIVE_PARSED" for r in result["daily_archives"])
    a = result["aggregate"]
    if result["archive_fetch_errors"]:
        result["status"] = "BLOCKED_SOURCE_FETCH_OR_SCHEMA_ERROR"
    elif parsed_days < 10 or a["parsed_rows"] == 0:
        result["status"] = "BLOCKED_INSUFFICIENT_ARCHIVE_COVERAGE"
    elif (a["identity_completeness_pct"] >= 99.9 and a["duplicate_daily_contract_keys"] == 0
          and a["date_mismatch_rows"] == 0 and a["price_completeness_pct"] >= 99.0):
        result["status"] = "PASS_EOD_CONTRACT_IDENTITY"
    else:
        result["status"] = "FAIL_EOD_DATA_QUALITY_GATE"

    (out / "nse_eod_data_audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Phase 104.1 — NSE EOD Stock-Options Data Audit", "",
        f"**Run:** {result['run_id']}",
        f"**Status:** {result['status']}",
        f"**Target window:** {args.from_date} inclusive to {args.to_date} exclusive ({days} calendar days)",
        f"**Official NSE daily archives parsed:** {parsed_days}",
        f"**No-archive dates (weekend/holiday/absent file not distinguished automatically):** {len(result['no_archive_dates'])}",
        f"**Source/schema errors:** {len(result['archive_fetch_errors'])}",
        f"**Selected five-stock stock-option rows:** {a['selected_rows']}",
        f"**Parsed rows:** {a['parsed_rows']}",
        f"**Identity completeness:** {a['identity_complete_rows']}/{a['parsed_rows']} ({a['identity_completeness_pct']}%)",
        f"**OHLC completeness:** {a['price_complete_rows']}/{a['parsed_rows']} ({a['price_completeness_pct']}%)",
        f"**Unique daily contract keys:** {a['unique_contract_keys']}",
        f"**Duplicate daily contract keys:** {a['duplicate_daily_contract_keys']}",
        f"**Rows with positive volume / zero volume / missing volume:** {a['positive_volume_rows']} / {a['zero_volume_rows']} / {a['missing_volume_rows']}",
        f"**Missing OI / underlying / lot-size rows:** {a['missing_oi_rows']} / {a['missing_underlying_rows']} / {a['missing_lot_size_rows']}",
        f"**Date-mismatch rows:** {a['date_mismatch_rows']}",
        f"**Aggregate expiry-date counts:** {json.dumps(a['matched_expiry_counts'], sort_keys=True)}",
        f"**Raw rows persisted or uploaded:** {result['raw_rows_persisted']} / {result['raw_rows_in_artifact']}",
        "",
        "## Coverage by stock", "",
        "| Symbol | Rows | Dates | Unique daily contracts | Positive-volume rows | Zero-volume rows | Missing OI | Missing underlying | Missing lot size |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for sym, vals in a["by_symbol"].items():
        lines.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
            sym, vals["rows"], vals["trade_dates"], vals["unique_contract_keys"],
            vals["positive_volume_rows"], vals["zero_volume_rows"], vals["missing_oi_rows"],
            vals["missing_underlying_rows"], vals["missing_lot_size_rows"]))
    lines += ["", "## Daily file checkpoints", "", "| Date | Status | Selected rows | Identity-complete rows | Archive SHA-256 |", "|---|---|---:|---:|---|"]
    for d in result["daily_archives"]:
        lines.append("| {} | {} | {} | {} | {} |".format(
            d["date"], d["status"], d.get("selected_stock_option_rows", 0),
            d.get("identity_complete_rows", 0), d.get("sha256", "")))
    lines += ["", "## Interpretation", ""]
    if result["status"] == "PASS_EOD_CONTRACT_IDENTITY":
        lines.append("Technical daily contract identity and OHLC integrity passed this bounded sample. This does not establish data-use/caching rights, executable prices, strategy profitability or suitability for intraday fills.")
    else:
        lines.append("The EOD contract/data-quality gate did not pass. Do not run strategy P&L from this result; diagnose only the logged source/coverage issue within the registered bound.")
    lines += ["", "## Limitations", ""] + ["- " + item for item in result["known_limits"]]
    (out / "NSE_EOD_DATA_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "phase": result["phase"], "run_id": result["run_id"], "status": result["status"],
        "calendar_days": days, "archives_parsed": parsed_days, "source_errors": len(result["archive_fetch_errors"]),
        "selected_stock_option_rows": a["selected_rows"], "parsed_rows": a["parsed_rows"],
        "identity_completeness_pct": a["identity_completeness_pct"], "price_completeness_pct": a["price_completeness_pct"],
        "unique_daily_contract_keys": a["unique_contract_keys"],
        "duplicate_daily_contract_keys": a["duplicate_daily_contract_keys"],
        "raw_rows_persisted": False, "raw_rows_in_artifact": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
