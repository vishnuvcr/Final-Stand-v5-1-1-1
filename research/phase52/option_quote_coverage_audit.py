#!/usr/bin/env python3
"""Audit exact option entry/exit bar availability for every grid event.

This is a source-coverage scan only. It emits counts and hashes, never raw
market rows or strategy P&L. It cannot prove a selected multi-leg config fills;
the replay worker still checks every selected strike/expiry/type exactly.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "results" / "phase52" / "base_replay" / "manifest.json"
EVENTS_PATH = ROOT / "results" / "phase52" / "configuration_event_universe" / "expected_events.csv"
OUT = ROOT / "results" / "phase52" / "option_quote_coverage"
HF_REPO = "thetrademarkk/india-index-options-1m"
TZ = "Asia/Kolkata"
MIN_OI = 100


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def to_ist_timestamp(series: pd.Series) -> pd.Series:
    x = pd.to_datetime(series, errors="coerce")
    return x.dt.tz_localize(TZ) if x.dt.tz is None else x.dt.tz_convert(TZ)


def valid_contract_counts(frame: pd.DataFrame) -> dict[str, int]:
    if frame.empty:
        return {"rows": 0, "ce_contracts": 0, "pe_contracts": 0,
                "oi_eligible_contracts": 0, "valid_ohlc_contracts": 0}
    z = frame.copy()
    z["option_type"] = z["option_type"].astype(str).str.upper()
    z["strike"] = pd.to_numeric(z["strike"], errors="coerce")
    z["open"] = pd.to_numeric(z["open"], errors="coerce")
    z["open_interest"] = pd.to_numeric(z["open_interest"], errors="coerce")
    unique = z.dropna(subset=["option_type", "strike"]).drop_duplicates(["option_type", "strike"])
    oi_ok = unique[unique["open_interest"].ge(MIN_OI) & unique["open"].gt(0)]
    ohlc_ok = unique[unique["open"].gt(0) &
                     pd.to_numeric(unique["high"], errors="coerce").ge(unique["open"]) &
                     pd.to_numeric(unique["low"], errors="coerce").le(unique["open"])]
    return {
        "rows": int(len(frame)),
        "ce_contracts": int(unique["option_type"].eq("CE").sum()),
        "pe_contracts": int(unique["option_type"].eq("PE").sum()),
        "oi_eligible_contracts": int(len(oi_ok)),
        "valid_ohlc_contracts": int(len(ohlc_ok)),
    }


def audit_one_expiry(
    expiry: str, entry_events: pd.DataFrame, revision: str, token: str | None
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    filename = f"options/NIFTY/{expiry}.parquet"
    path = hf_hub_download(
        repo_id=HF_REPO, filename=filename, repo_type="dataset",
        revision=revision, token=token
    )
    file_path = Path(path)
    # Read just columns needed for timestamp-coverage and basic data eligibility.
    columns = ["timestamp", "option_type", "strike", "open", "high", "low", "close", "volume", "open_interest"]
    df = pd.read_parquet(file_path, columns=columns)
    df["timestamp"] = to_ist_timestamp(df["timestamp"])
    df["option_type"] = df["option_type"].astype(str).str.upper()
    df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
    df["open"] = pd.to_numeric(df["open"], errors="coerce")
    df["open_interest"] = pd.to_numeric(df["open_interest"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df = df.sort_values(["timestamp", "option_type", "strike"], kind="stable")
    target_day = pd.Timestamp(expiry, tz=TZ).normalize()
    target_rows = df[(df["timestamp"] >= target_day) &
                     (df["timestamp"] <= target_day + pd.Timedelta(hours=15, minutes=29))]
    # Latest timestamp on the expiry day with any option bars and with both CE/PE available.
    any_counts = target_rows.groupby("timestamp").size()
    any_exit = any_counts.index.max() if len(any_counts) else None
    both_exit = None
    if not target_rows.empty:
        counts = target_rows.pivot_table(index="timestamp", columns="option_type",
                                        values="strike", aggfunc="count", fill_value=0)
        if "CE" in counts and "PE" in counts:
            eligible = counts[(counts["CE"] > 0) & (counts["PE"] > 0)]
            both_exit = eligible.index.max() if len(eligible) else None
    rows = []
    for ev in entry_events.itertuples(index=False):
        entry_ts = pd.Timestamp(ev.entry_ts)
        if entry_ts.tzinfo is None:
            entry_ts = entry_ts.tz_localize(TZ)
        else:
            entry_ts = entry_ts.tz_convert(TZ)
        entry = df[df["timestamp"].eq(entry_ts)]
        entry_counts = valid_contract_counts(entry)
        entry_day = entry_ts.normalize()
        tp_window = df[(df["timestamp"] > entry_ts) &
                       (df["timestamp"] <= entry_day + pd.Timedelta(hours=15, minutes=29))]
        tp_times = pd.Index(tp_window["timestamp"].drop_duplicates()).sort_values()
        next_open_candidates = []
        if len(tp_times):
            for stamp in tp_times:
                next_stamp = stamp + pd.Timedelta(minutes=1)
                if next_stamp in set(df["timestamp"].tolist()):
                    next_open_candidates.append(next_stamp)
        exit_1515_ts = entry_day + pd.Timedelta(hours=15, minutes=15)
        exit_1515 = df[df["timestamp"].eq(exit_1515_ts)]
        exit_1515_counts = valid_contract_counts(exit_1515)
        rows.append({
            "event_id": str(ev.event_id),
            "dataset_revision": revision,
            "expiry": expiry,
            "split": str(ev.split),
            "entry_dte_calendar_days": int(ev.entry_dte_calendar_days),
            "entry_date": str(ev.entry_date),
            "entry_time_ist": str(ev.entry_time_ist),
            "entry_ts": entry_ts.isoformat(),
            "index_has_exact_entry_timestamp": bool(ev.index_has_exact_entry_timestamp),
            "option_file_sha256": sha256_file(file_path),
            "option_file_bytes": int(file_path.stat().st_size),
            "entry_option_row_count": entry_counts["rows"],
            "entry_ce_contracts": entry_counts["ce_contracts"],
            "entry_pe_contracts": entry_counts["pe_contracts"],
            "entry_contracts_oi_ge_100": entry_counts["oi_eligible_contracts"],
            "entry_contracts_valid_ohlc": entry_counts["valid_ohlc_contracts"],
            "entry_option_quote_status": "OPTION_ROWS_PRESENT" if entry_counts["rows"] else "NO_OPTION_ROWS_AT_EXACT_ENTRY",
            "entry_exact_timestamp_needs_config_specific_leg_check": True,
            "exit_1515_option_row_count": exit_1515_counts["rows"],
            "exit_1515_ce_contracts": exit_1515_counts["ce_contracts"],
            "exit_1515_pe_contracts": exit_1515_counts["pe_contracts"],
            "expiry_last_any_option_timestamp": any_exit.isoformat() if any_exit is not None else None,
            "expiry_last_both_ce_pe_timestamp": both_exit.isoformat() if both_exit is not None else None,
            "target_expiry_has_exit_bar": bool(any_exit is not None),
            "target_expiry_has_both_option_types_at_common_timestamp": bool(both_exit is not None),
            "post_entry_option_timestamps": int(len(tp_times)),
            "post_bar_next_minute_any_quote_count": int(len(next_open_candidates)),
            "pnl_status": "NOT_BACKTESTED",
        })
    metadata = {
        "expiry": expiry,
        "file": filename,
        "sha256": sha256_file(file_path),
        "bytes": int(file_path.stat().st_size),
        "rows": int(len(df)),
        "timestamp_min": df["timestamp"].min().isoformat() if len(df) else None,
        "timestamp_max": df["timestamp"].max().isoformat() if len(df) else None,
        "target_expiry_rows": int(len(target_rows)),
        "target_expiry_last_any_option_timestamp": any_exit.isoformat() if any_exit is not None else None,
        "target_expiry_last_both_ce_pe_timestamp": both_exit.isoformat() if both_exit is not None else None,
    }
    return rows, metadata


def main() -> int:
    if not MANIFEST_PATH.exists() or not EVENTS_PATH.exists():
        raise FileNotFoundError("Pinned base manifest and configuration event universe are required")
    base = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    revision = str(base["dataset_revision"])
    token = os.getenv("HF_TOKEN") or None
    events = pd.read_csv(EVENTS_PATH)
    expected = int(len(events))
    records: list[dict[str, Any]] = []
    source_records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    files = sorted(events["expiry"].drop_duplicates().astype(str).tolist())
    for i, expiry in enumerate(files, 1):
        group = events[events["expiry"].astype(str).eq(expiry)]
        try:
            rows, meta = audit_one_expiry(expiry, group, revision, token)
            records.extend(rows)
            source_records.append({"status": "PASS", **meta})
        except Exception as exc:
            errors.append({"expiry": expiry, "error_type": type(exc).__name__})
            source_records.append({"expiry": expiry, "file": f"options/NIFTY/{expiry}.parquet",
                                   "status": "ERROR", "error_type": type(exc).__name__})
        if i % 25 == 0 or i == len(files):
            print(json.dumps({"event": "OPTION_QUOTE_AUDIT_PROGRESS", "expiry_files_done": i,
                              "expiry_files_total": len(files), "event_rows_audited": len(records),
                              "source_file_errors": len(errors)}), flush=True)

    OUT.mkdir(parents=True, exist_ok=True)
    event_path = OUT / "entry_exit_quote_coverage.csv"
    source_path = OUT / "source_file_audit.csv"
    errors_path = OUT / "source_errors.csv"
    pd.DataFrame(records).to_csv(event_path, index=False)
    pd.DataFrame(source_records).to_csv(source_path, index=False)
    pd.DataFrame(errors, columns=["expiry", "error_type"]).to_csv(errors_path, index=False)

    audited = pd.DataFrame(records)
    event_key_coverage = int(audited["event_id"].nunique()) if len(audited) else 0
    entry_present = int(audited["entry_option_row_count"].gt(0).sum()) if len(audited) else 0
    entry_both_types = int((audited["entry_ce_contracts"].gt(0) & audited["entry_pe_contracts"].gt(0)).sum()) if len(audited) else 0
    entry_oi_eligible = int(audited["entry_contracts_oi_ge_100"].gt(0).sum()) if len(audited) else 0
    exit_1515_present = int(audited["exit_1515_option_row_count"].gt(0).sum()) if len(audited) else 0
    expiry_exit_present = int(audited["target_expiry_has_exit_bar"].sum()) if len(audited) else 0
    exact_common_exit = int(audited["target_expiry_has_both_option_types_at_common_timestamp"].sum()) if len(audited) else 0
    report = {
        "status": "OPTION_QUOTE_COVERAGE_AUDIT_WITH_EXPLICIT_GAPS" if errors or event_key_coverage != expected else "OPTION_QUOTE_COVERAGE_AUDIT_COMPLETE",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": HF_REPO,
        "dataset_revision": revision,
        "expected_event_rows": expected,
        "audited_event_rows": int(len(audited)),
        "event_rows_with_audit_results": event_key_coverage,
        "option_expiry_files_expected": int(len(files)),
        "option_expiry_files_audited": int(len([r for r in source_records if r.get("status") == "PASS"])),
        "source_file_errors": int(len(errors)),
        "events_with_any_option_row_at_exact_entry": entry_present,
        "events_with_both_ce_and_pe_at_exact_entry": entry_both_types,
        "events_with_any_oi_eligible_contract_at_entry": entry_oi_eligible,
        "events_with_any_option_row_at_exact_15_15_entry_day_exit": exit_1515_present,
        "events_with_any_option_row_at_target_expiry_exit": expiry_exit_present,
        "events_with_both_option_types_at_common_target_expiry_timestamp": exact_common_exit,
        "interpretation": "This is timestamp and broad contract-universe coverage only. It does not establish that every configured strike has a valid entry/exit quote. The replay worker must verify every selected contract/strike/expiry/time, OI and OHLC-range gate. No P&L is calculated.",
        "outputs": {
            "event_coverage": str(event_path.relative_to(ROOT)),
            "source_audit": str(source_path.relative_to(ROOT)),
            "source_errors": str(errors_path.relative_to(ROOT)),
        },
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    (OUT / "summary.sha256").write_text(sha256_file(summary_path) + "  summary.json\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
