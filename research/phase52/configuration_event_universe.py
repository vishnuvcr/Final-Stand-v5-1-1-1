#!/usr/bin/env python3
"""Build a finite exact-timestamp event inventory for grid-v1.3; no P&L.

This audit enumerates target option-expiry files x DTE {0,7} x entry times
{09:45,13:00} IST. It checks the exact NIFTY index timestamp at entry, but it
does not claim that each selected option leg has a quote; leg-level availability
must be tested by the replay worker for each configuration. Never roll dates or
impute missing index bars.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

ROOT = Path(__file__).resolve().parents[2]
BASE_MANIFEST = ROOT / "results" / "phase52" / "base_replay" / "manifest.json"
OUT = ROOT / "results" / "phase52" / "configuration_event_universe"
HF_REPO = "thetrademarkk/india-index-options-1m"
TZ = "Asia/Kolkata"
ENTRY_TIMES = ("09:45", "13:00")
DTE_DAYS = (0, 7)
SCOPE_END = pd.Timestamp("2026-09-30", tz=TZ)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def split_for(expiry: pd.Timestamp) -> str:
    if expiry <= pd.Timestamp("2023-12-31", tz=TZ):
        return "development"
    if expiry <= pd.Timestamp("2025-12-31", tz=TZ):
        return "validation"
    return "holdout"


def expiry_dates(files: list[str]) -> list[tuple[pd.Timestamp, str]]:
    found = []
    for filename in files:
        match = re.fullmatch(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet", filename)
        if not match:
            continue
        expiry = pd.Timestamp(match.group(1), tz=TZ)
        if expiry <= SCOPE_END:
            found.append((expiry, filename))
    return sorted(found, key=lambda v: (v[0], v[1]))


def assemble_events(
    listed_files: list[str],
    index_timestamps: set[pd.Timestamp],
    index_dates: set[pd.Timestamp],
    index_max_ts: pd.Timestamp | None,
    revision: str,
) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    files = expiry_dates(listed_files)
    for expiry, path in files:
        for dte in DTE_DAYS:
            entry_date = expiry - pd.Timedelta(days=dte)
            for entry_time in ENTRY_TIMES:
                hour, minute = (int(x) for x in entry_time.split(":"))
                entry_ts = entry_date.normalize() + pd.Timedelta(hours=hour, minutes=minute)
                has_tick = entry_ts in index_timestamps
                has_date = entry_date.normalize() in index_dates
                if has_tick:
                    reason = "INDEX_TIMESTAMP_PASS_OPTION_LEG_AUDIT_PENDING"
                elif index_max_ts is not None and entry_ts > index_max_ts:
                    reason = "INDEX_SOURCE_ENDS_BEFORE_ENTRY_TIMESTAMP"
                elif not has_date:
                    reason = "NO_INDEX_ROWS_ON_EXACT_ENTRY_DATE"
                else:
                    reason = "EXACT_INDEX_ENTRY_TIMESTAMP_MISSING"
                records.append({
                    "event_id": hashlib.sha256(
                        f"{revision}|{expiry.date()}|{dte}|{entry_time}".encode("utf-8")
                    ).hexdigest()[:20],
                    "dataset_revision": revision,
                    "expiry": expiry.strftime("%Y-%m-%d"),
                    "split": split_for(expiry),
                    "entry_dte_calendar_days": int(dte),
                    "entry_date": entry_date.strftime("%Y-%m-%d"),
                    "entry_time_ist": entry_time,
                    "entry_ts": entry_ts.isoformat(),
                    "option_expiry_file": path,
                    "option_expiry_file_listed": True,
                    "index_has_exact_entry_timestamp": bool(has_tick),
                    "index_has_any_rows_on_entry_date": bool(has_date),
                    "index_source_max_timestamp": index_max_ts.isoformat() if index_max_ts is not None else None,
                    "entry_status": reason,
                    "option_leg_quote_status": "NOT_YET_CHECKED_CONFIGURATION_SPECIFIC",
                    "pnl_status": "NOT_BACKTESTED",
                })
    return pd.DataFrame(records)


def build() -> dict[str, Any]:
    if not BASE_MANIFEST.exists():
        raise FileNotFoundError("Pinned base replay manifest is required to freeze the dataset revision")
    base_manifest = json.loads(BASE_MANIFEST.read_text(encoding="utf-8"))
    revision = str(base_manifest["dataset_revision"])
    token = os.getenv("HF_TOKEN") or None
    api = HfApi(token=token)
    files = api.list_repo_files(HF_REPO, repo_type="dataset", revision=revision)
    scoped = expiry_dates(files)
    if not scoped:
        raise RuntimeError("No NIFTY option-expiry parquet files found at pinned revision")
    index_path = hf_hub_download(
        repo_id=HF_REPO, filename="index/NIFTY.parquet",
        repo_type="dataset", revision=revision, token=token
    )
    index = pd.read_parquet(index_path, columns=["timestamp"])
    ts = pd.to_datetime(index["timestamp"], errors="coerce")
    index["timestamp"] = ts.dt.tz_localize(TZ) if ts.dt.tz is None else ts.dt.tz_convert(TZ)
    index = index.dropna(subset=["timestamp"]).drop_duplicates("timestamp").sort_values("timestamp")
    timestamps = set(index["timestamp"].tolist())
    dates = set(index["timestamp"].dt.normalize().tolist())
    max_ts = pd.Timestamp(index["timestamp"].max()) if len(index) else None
    events = assemble_events(files, timestamps, dates, max_ts, revision)

    OUT.mkdir(parents=True, exist_ok=True)
    events_path = OUT / "expected_events.csv"
    events.to_csv(events_path, index=False)
    statuses = Counter(events["entry_status"].astype(str)) if len(events) else Counter()
    by_dte = {}
    for dte, group in events.groupby("entry_dte_calendar_days", sort=True):
        by_dte[str(int(dte))] = {
            "expected_events": int(len(group)),
            "exact_index_entries": int(group["index_has_exact_entry_timestamp"].sum()),
            "index_entry_missing": int((~group["index_has_exact_entry_timestamp"]).sum()),
        }
    by_time = {}
    for tm, group in events.groupby("entry_time_ist", sort=True):
        by_time[str(tm)] = {
            "expected_events": int(len(group)),
            "exact_index_entries": int(group["index_has_exact_entry_timestamp"].sum()),
            "index_entry_missing": int((~group["index_has_exact_entry_timestamp"]).sum()),
        }
    by_split = {}
    for split, group in events.groupby("split", sort=True):
        by_split[str(split)] = {
            "expected_events": int(len(group)),
            "exact_index_entries": int(group["index_has_exact_entry_timestamp"].sum()),
            "index_entry_missing": int((~group["index_has_exact_entry_timestamp"]).sum()),
        }
    summary = {
        "status": "CONFIGURATION_EVENT_UNIVERSE_BUILT_WITH_EXPLICIT_COVERAGE_GAPS",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": HF_REPO,
        "dataset_revision": revision,
        "index_file_sha256": sha256_file(Path(index_path)),
        "source_option_expiry_files": int(len(scoped)),
        "first_option_expiry": scoped[0][0].strftime("%Y-%m-%d") if scoped else None,
        "last_option_expiry": scoped[-1][0].strftime("%Y-%m-%d") if scoped else None,
        "dte_calendar_days": list(DTE_DAYS),
        "entry_times_ist": list(ENTRY_TIMES),
        "expected_event_count": int(len(events)),
        "unique_target_expiries_in_universe": int(events["expiry"].nunique()) if len(events) else 0,
        "exact_index_entry_timestamp_count": int(events["index_has_exact_entry_timestamp"].sum()) if len(events) else 0,
        "events_without_exact_index_entry_timestamp": int((~events["index_has_exact_entry_timestamp"]).sum()) if len(events) else 0,
        "index_timestamp_min": index["timestamp"].min().isoformat() if len(index) else None,
        "index_timestamp_max": max_ts.isoformat() if max_ts is not None else None,
        "counts_by_dte": by_dte,
        "counts_by_entry_time": by_time,
        "counts_by_split": by_split,
        "entry_status_counts": {str(k): int(v) for k, v in statuses.items()},
        "option_leg_quotes": "NOT AUDITED BY THIS FILE; exact strike/expiry/entry and exit quote eligibility must be checked per configuration by the replay worker.",
        "pnl_status": "NO PNL COMPUTED; THIS IS AN EVENT INVENTORY ONLY",
        "no_imputation_policy": "No calendar rolling, no nearest timestamp, no forward fill and no interpolation. Missing exact index ticks remain explicit.",
        "output_csv": str(events_path.relative_to(ROOT)),
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    (OUT / "summary.sha256").write_text(sha256_file(summary_path) + "  summary.json\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


def self_test() -> None:
    revision = "selftest-revision"
    files = ["options/NIFTY/2026-06-04.parquet"]
    timestamps = {
        pd.Timestamp("2026-06-04 09:45:00", tz=TZ),
        pd.Timestamp("2026-05-28 13:00:00", tz=TZ),
    }
    dates = {pd.Timestamp("2026-06-04", tz=TZ).normalize(), pd.Timestamp("2026-05-28", tz=TZ).normalize()}
    result = assemble_events(
        files, timestamps, dates, pd.Timestamp("2026-06-04 15:30:00", tz=TZ), revision
    )
    assert len(result) == 4, f"expected 4 expiry/DTE/time events, got {len(result)}"
    assert result["event_id"].nunique() == 4, "event IDs must be unique"
    assert bool(result.loc[result.entry_time_ist.eq("09:45") & result.entry_dte_calendar_days.eq(0),
                           "index_has_exact_entry_timestamp"].iloc[0])
    assert bool(result.loc[result.entry_time_ist.eq("13:00") & result.entry_dte_calendar_days.eq(7),
                           "index_has_exact_entry_timestamp"].iloc[0])
    assert not bool(result.loc[result.entry_time_ist.eq("13:00") & result.entry_dte_calendar_days.eq(0),
                               "index_has_exact_entry_timestamp"].iloc[0])
    assert set(result.pnl_status) == {"NOT_BACKTESTED"}
    print("SELF_TEST_PASS: exact event indexing, unique IDs, explicit missing ticks, no P&L")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test-only", action="store_true")
    args = parser.parse_args()
    if args.self_test_only:
        self_test()
        raise SystemExit(0)
    build()
