#!/usr/bin/env python3
"""Audit replay event coverage against source option-expiry filenames and exact 10:00 index ticks.

This is a coverage audit only. It does not calculate P&L and never fills missing
index/option timestamps. An expiry filename is not proof that usable intraday
quotes or an exact entry-time spot observation exist.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "results" / "phase52" / "base_replay"
MANIFEST = BASE / "manifest.json"
MATRIX = BASE / "full_ready_made_trade_matrix.csv.gz"
OUT = ROOT / "results" / "phase52" / "coverage_audit"
HF_REPO = "thetrademarkk/india-index-options-1m"
TZ = "Asia/Kolkata"
START = pd.Timestamp("2021-05-27", tz=TZ)
END = pd.Timestamp("2026-09-30", tz=TZ)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    if not MANIFEST.exists() or not MATRIX.exists():
        raise FileNotFoundError("Pinned base replay outputs are required before coverage audit")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    revision = str(manifest["dataset_revision"])
    token = os.getenv("HF_TOKEN") or None
    api = HfApi(token=token)
    files = api.list_repo_files(HF_REPO, repo_type="dataset", revision=revision)
    expiry_files = []
    for path in files:
        m = re.fullmatch(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet", path)
        if not m:
            continue
        d = pd.Timestamp(m.group(1), tz=TZ)
        if START <= d <= END:
            expiry_files.append((d, path))
    expiry_files.sort(key=lambda x: x[0])

    index_path = hf_hub_download(repo_id=HF_REPO, filename="index/NIFTY.parquet",
                                 repo_type="dataset", revision=revision, token=token)
    index = pd.read_parquet(index_path, columns=["timestamp"])
    ts = pd.to_datetime(index["timestamp"], errors="coerce")
    index["timestamp"] = ts.dt.tz_localize(TZ) if ts.dt.tz is None else ts.dt.tz_convert(TZ)
    index = index.dropna(subset=["timestamp"]).drop_duplicates("timestamp").sort_values("timestamp")
    exact_ticks = set(index["timestamp"].tolist())
    session_days = sorted(index["timestamp"].dt.normalize().unique().tolist())
    latest_index_session = max(session_days) if session_days else None

    trades = pd.read_csv(MATRIX, compression="gzip", usecols=["expiry", "entry_ts", "strategy"])
    trades["expiry_date"] = pd.to_datetime(trades["expiry"], errors="coerce").dt.strftime("%Y-%m-%d")
    trades["entry_ts"] = pd.to_datetime(trades["entry_ts"], errors="coerce")
    if len(trades) and trades["entry_ts"].dt.tz is None:
        trades["entry_ts"] = trades["entry_ts"].dt.tz_localize(TZ)
    elif len(trades):
        trades["entry_ts"] = trades["entry_ts"].dt.tz_convert(TZ)
    grouped = trades.groupby("expiry_date").agg(
        matrix_rows=("strategy", "size"),
        strategies_present=("strategy", "nunique"),
        matrix_entry_ts=("entry_ts", "first"),
    ).reset_index()
    grouped_map = {r.expiry_date: r for r in grouped.itertuples(index=False)}

    records: list[dict[str, Any]] = []
    for expiry, path in expiry_files:
        prior = [d for d in session_days if d < expiry.normalize()]
        record = {
            "expiry": str(expiry.date()),
            "source_path": path,
            "dataset_revision": revision,
            "prior_index_session_count": len(prior),
            "expected_entry_ts": None,
            "source_index_has_exact_10am": False,
            "matrix_rows": 0,
            "strategies_present": 0,
            "matrix_entry_ts": None,
            "coverage_status": None,
            "coverage_reason": None,
        }
        if latest_index_session is not None and expiry.normalize() > latest_index_session:
            # Do not use the fourth-from-last date in an outdated index series
            # as though it were the fourth prior session to a later expiry.
            record["coverage_status"] = "UNREPLAYABLE_INDEX_SERIES_ENDS_BEFORE_EXPIRY"
            record["coverage_reason"] = (
                f"Index series ends {latest_index_session.date()}, before expiry {expiry.date()}; "
                "the last four prior sessions cannot be established from this source. No extrapolation."
            )
        elif len(prior) < 4:
            record["coverage_status"] = "EXCLUDED"
            record["coverage_reason"] = "FEWER_THAN_FOUR_PRIOR_INDEX_SESSIONS"
        else:
            entry_day = prior[-4]
            entry_ts = pd.Timestamp(entry_day) + pd.Timedelta(hours=10)
            record["expected_entry_ts"] = str(entry_ts)
            exact = entry_ts in exact_ticks
            record["source_index_has_exact_10am"] = bool(exact)
            row = grouped_map.get(str(expiry.date()))
            if row is not None:
                record["matrix_rows"] = int(row.matrix_rows)
                record["strategies_present"] = int(row.strategies_present)
                record["matrix_entry_ts"] = str(row.matrix_entry_ts)
            if not exact:
                record["coverage_status"] = "UNREPLAYABLE_MISSING_EXACT_ENTRY_SPOT"
                record["coverage_reason"] = "NO_EXACT_10AM_INDEX_TIMESTAMP; no nearest-row substitution allowed"
            elif row is not None:
                record["coverage_status"] = "MATRIX_ROWS_PRESENT"
                record["coverage_reason"] = "EXACT_ENTRY_SPOT_AND_AT_LEAST_ONE_TRADE_MATRIX_ROW"
                if pd.Timestamp(row.matrix_entry_ts).tzinfo is None:
                    actual_ts = pd.Timestamp(row.matrix_entry_ts).tz_localize(TZ)
                else:
                    actual_ts = pd.Timestamp(row.matrix_entry_ts).tz_convert(TZ)
                if actual_ts != entry_ts:
                    record["coverage_status"] = "MATRIX_TIMESTAMP_MISMATCH"
                    record["coverage_reason"] = "MATRIX_ENTRY_TS_DIFFERS_FROM_EXPECTED_ENTRY_TS"
            else:
                record["coverage_status"] = "UNREPLAYABLE_NO_MATRIX_ROWS"
                record["coverage_reason"] = "EXACT_ENTRY_SPOT_EXISTS_BUT_NO_EXPIRY_ROWS_IN_BASE_MATRIX"
        records.append(record)

    result = pd.DataFrame(records)
    OUT.mkdir(parents=True, exist_ok=True)
    result_path = OUT / "expiry_coverage.csv"
    result.to_csv(result_path, index=False)
    counts = result.coverage_status.value_counts(dropna=False).to_dict()
    first_expiry = min((r[0] for r in expiry_files), default=None)
    last_expiry = max((r[0] for r in expiry_files), default=None)
    observed_matrix_dates = sorted(trades.expiry_date.dropna().unique())
    has_exact = int(result.source_index_has_exact_10am.sum()) if len(result) else 0
    matrix_rows = int((result.coverage_status == "MATRIX_ROWS_PRESENT").sum()) if len(result) else 0
    non_full = int((~result.coverage_status.eq("MATRIX_ROWS_PRESENT")).sum()) if len(result) else 0
    report = {
        "status": "COVERAGE_AUDIT_COMPLETE_WINDOW_GATE_REVIEW_REQUIRED" if non_full else "COVERAGE_AUDIT_COMPLETE_ALL_SOURCE_EXPIRIES_PRESENT",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": HF_REPO,
        "dataset_revision": revision,
        "index_file_sha256": sha256_file(Path(index_path)),
        "base_trade_matrix_sha256": sha256_file(MATRIX),
        "option_expiry_files_in_scope": int(len(expiry_files)),
        "first_source_option_expiry": str(first_expiry.date()) if first_expiry is not None else None,
        "last_source_option_expiry": str(last_expiry.date()) if last_expiry is not None else None,
        "unique_expiries_in_base_matrix": int(trades.expiry_date.nunique()),
        "first_matrix_expiry": min(observed_matrix_dates) if observed_matrix_dates else None,
        "last_matrix_expiry": max(observed_matrix_dates) if observed_matrix_dates else None,
        "index_timestamp_min": str(index.timestamp.min()) if len(index) else None,
        "index_timestamp_max": str(index.timestamp.max()) if len(index) else None,
        "latest_index_session_date": str(pd.Timestamp(latest_index_session).date()) if latest_index_session is not None else None,
        "sessions_with_exact_10am_ticks": int(sum(1 for d in session_days if d + pd.Timedelta(hours=10) in exact_ticks)),
        "source_expiry_rows_with_exact_entry_tick": has_exact,
        "source_expiry_rows_with_matrix_outcome": matrix_rows,
        "source_expiry_rows_not_fully_replayed": non_full,
        "coverage_status_counts": {str(k): int(v) for k, v in counts.items()},
        "latest_missing_or_unreplayed_expiries": result.loc[result.coverage_status.ne("MATRIX_ROWS_PRESENT"), "expiry"].tail(30).tolist(),
        "interpretation": "A listed expiry file is not treated as a tested opportunity unless the exact prior-session-derived 10:00 IST index tick exists and at least one trade-matrix row was produced. No quote interpolation, timestamp substitution or forward filling is allowed.",
        "output_csv": str(result_path.relative_to(ROOT)),
    }
    (OUT / "summary.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    (OUT / "summary.sha256").write_text(sha256_file(OUT / "summary.json") + "  summary.json\n", encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
