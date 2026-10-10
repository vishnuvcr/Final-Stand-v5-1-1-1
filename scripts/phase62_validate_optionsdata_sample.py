#!/usr/bin/env python3
"""Ephemeral smoke test for the public OptionsData NIFTY sample.

Raw data is downloaded only to the runner's temporary directory. It is never
printed, committed, or uploaded as an artifact. Only aggregate metadata is emitted.
"""
from __future__ import annotations
import hashlib, json, os, tempfile, urllib.request, zipfile
from pathlib import Path
from datetime import datetime

SAMPLE_URL = "https://optionsdata.shop/sample/download"
REQUIRED_LAYOUT_A = {"datetime", "stock_code", "exchange_code", "product_type",
                     "expiry_date", "strike_price", "right", "open", "high",
                     "low", "close", "volume", "open_interest"}
REQUIRED_LAYOUT_B = {"timestamp", "open", "high", "low", "close", "volume",
                     "oi", "strike", "option_type", "expiry"}
TARGET_DATES = {"2026-07-28", "2026-08-04"}

def main():
    report = {
        "phase": 62,
        "checked_at_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "source": "OptionsData.shop free NIFTY options sample",
        "raw_data_persisted": False,
        "raw_data_uploaded": False,
        "target_sessions": sorted(TARGET_DATES),
        "target_sessions_in_free_sample": [],
        "target_session_gate": "BLOCKED_SAMPLE_DOES_NOT_COVER_TARGET_DATES",
        "files": [],
        "errors": [],
    }
    try:
        import pandas as pd
        import pyarrow.parquet as pq
    except Exception as exc:
        report["errors"].append("Missing parquet dependencies: " + type(exc).__name__)
        return finish(report, 2)

    with tempfile.TemporaryDirectory(prefix="phase62-") as tmp:
        archive = Path(tmp) / "sample.zip"
        request = urllib.request.Request(SAMPLE_URL, headers={"User-Agent": "FinalStand-Research/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=90) as response, archive.open("wb") as out:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk: break
                    out.write(chunk)
        except Exception as exc:
            report["errors"].append("Sample download failed: " + type(exc).__name__)
            return finish(report, 1)
        report["archive_sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
        try:
            with zipfile.ZipFile(archive) as zf:
                members = [n for n in zf.namelist() if n.lower().endswith(".parquet") and not n.endswith("/")]
                if not members:
                    report["errors"].append("No Parquet members found in sample archive")
                    return finish(report, 1)
                for member in members:
                    # Extract each file only within the temporary runner directory.
                    dest = Path(tmp) / Path(member).name
                    with zf.open(member) as src, dest.open("wb") as out:
                        while True:
                            chunk = src.read(1024 * 1024)
                            if not chunk: break
                            out.write(chunk)
                    schema = set(pq.read_schema(dest).names)
                    layout = "A" if REQUIRED_LAYOUT_A.issubset(schema) else ("B" if REQUIRED_LAYOUT_B.issubset(schema) else "UNKNOWN")
                    item = {"file": Path(member).name, "schema_layout": layout,
                            "columns": sorted(schema), "rows": None, "min_timestamp": None,
                            "max_timestamp": None, "contract_key_nulls": None,
                            "duplicate_contract_minute_keys": None, "oi_nulls": None,
                            "oi_zero_rows": None}
                    if layout == "UNKNOWN":
                        report["errors"].append("Unrecognized schema in " + Path(member).name)
                    df = pd.read_parquet(dest)
                    item["rows"] = int(len(df))
                    time_col = "datetime" if layout == "A" else "timestamp"
                    strike_col = "strike_price" if layout == "A" else "strike"
                    side_col = "right" if layout == "A" else "option_type"
                    expiry_col = "expiry_date" if layout == "A" else "expiry"
                    oi_col = "open_interest" if layout == "A" else "oi"
                    if time_col in df:
                        ts = pd.to_datetime(df[time_col], errors="coerce")
                        item["min_timestamp"] = None if ts.isna().all() else str(ts.min())
                        item["max_timestamp"] = None if ts.isna().all() else str(ts.max())
                        dates = set(ts.dropna().dt.strftime("%Y-%m-%d"))
                        report["target_sessions_in_free_sample"] = sorted(set(report["target_sessions_in_free_sample"]) | (dates & TARGET_DATES))
                    keys = [time_col, strike_col, side_col, expiry_col]
                    if all(k in df for k in keys):
                        item["contract_key_nulls"] = int(df[keys].isna().any(axis=1).sum())
                        item["duplicate_contract_minute_keys"] = int(df.duplicated(keys, keep=False).sum())
                    if oi_col in df:
                        item["oi_nulls"] = int(df[oi_col].isna().sum())
                        item["oi_zero_rows"] = int((df[oi_col] == 0).sum())
                    report["files"].append(item)
        except Exception as exc:
            report["errors"].append("Archive/schema audit failed: " + type(exc).__name__)
            return finish(report, 1)

    if report["files"] and not report["errors"]:
        report["sample_schema_gate"] = "PASS"
    else:
        report["sample_schema_gate"] = "FAIL"
    # Public sample dates are 2026-09-15 through 2026-09-17; never infer target coverage.
    report["target_session_gate"] = "PASS_EXACT_TARGET_DATES_PRESENT_IN_SAMPLE" if TARGET_DATES.issubset(set(report["target_sessions_in_free_sample"])) else "BLOCKED_EXACT_TARGET_SAMPLE_REQUIRED"
    return finish(report, 0 if report["sample_schema_gate"] == "PASS" else 1)

def finish(report, exit_code):
    out = os.environ.get("PHASE62_REPORT", "phase62_sample_audit.json")
    Path(out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k != "files"}, indent=2, sort_keys=True))
    print("Per-file schema/aggregate diagnostics written to", out)
    return exit_code

if __name__ == "__main__":
    raise SystemExit(main())
