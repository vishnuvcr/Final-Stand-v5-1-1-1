#!/usr/bin/env python3
"""Run frozen Phase 43/45 base structures at a pinned HF dataset revision.

This is a reproducible base-geometry replay, not the full v1.3/v1.4 configuration
search. It pins one data revision, records coverage, and retains a compressed
trade matrix for factor-conditioned selector tests.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parents[2]
HF_REPO = "thetrademarkk/india-index-options-1m"
OUT = ROOT / "results" / "phase52" / "base_replay"
MATRIX = OUT / "full_ready_made_trade_matrix.csv.gz"
MANIFEST = OUT / "manifest.json"
DATASET_LICENSE_EXPECTED = "cc-by-nc-4.0"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="force rerun at the specified or newest pinned source revision")
    parser.add_argument("--revision", default="", help="optional explicit immutable Hugging Face commit SHA")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    prior = {}
    if MANIFEST.exists():
        try:
            prior = json.loads(MANIFEST.read_text(encoding="utf-8"))
        except Exception:
            prior = {}

    revision = args.revision.strip()
    if not revision and prior.get("dataset_revision") and not args.force:
        revision = str(prior["dataset_revision"])
    if not revision:
        info = HfApi().dataset_info(HF_REPO, token=os.getenv("HF_TOKEN") or None)
        revision = str(info.sha)
        card = getattr(info, "card_data", None)
        license_id = getattr(card, "license", None) if card is not None else None
    else:
        info = HfApi().dataset_info(HF_REPO, revision=revision, token=os.getenv("HF_TOKEN") or None)
        card = getattr(info, "card_data", None)
        license_id = getattr(card, "license", None) if card is not None else None

    os.environ["PHASE52_HF_REVISION"] = revision
    if MATRIX.exists() and prior.get("dataset_revision") == revision and not args.force:
        check = sha256(MATRIX)
        if check == prior.get("trade_matrix_sha256"):
            print(json.dumps({"status": "REUSED_PINNED_BASE_REPLAY", "dataset_revision": revision,
                              "rows": prior.get("trade_rows"), "sha256": check, "path": str(MATRIX)}, indent=2))
            return 0

    # These imported accepted engines are called only after a single immutable
    # revision is resolved and injected into both engines.
    sys.path.insert(0, str(ROOT / "research"))
    p43 = importlib.import_module("phase43_vix_strategy_sweep")
    p45 = importlib.import_module("phase45_ready_made_sweep")
    p43.HF_REVISION = revision
    p45.HF_REVISION = revision
    p43.OUT = Path("results/phase43_vix")
    p45.OUT = Path("results/phase45_ready_made")
    p43.OUT.mkdir(parents=True, exist_ok=True)
    p45.OUT.mkdir(parents=True, exist_ok=True)

    print(json.dumps({"event": "BASE_REPLAY_START", "dataset": HF_REPO,
                      "dataset_revision": revision, "declared_license": license_id,
                      "started_at_utc": datetime.now(timezone.utc).isoformat()}, indent=2), flush=True)
    p43.main()
    p45.main()

    matrix_csv = Path("results/phase45_ready_made/full_ready_made_trade_matrix.csv")
    if not matrix_csv.exists() or matrix_csv.stat().st_size == 0:
        raise RuntimeError("Phase45 base replay did not create a non-empty full_ready_made_trade_matrix.csv")
    df = pd.read_csv(matrix_csv)
    required = {"expiry", "entry_ts", "split", "strategy", "net", "net50"}
    missing = required.difference(df.columns)
    if missing:
        raise RuntimeError(f"Trade matrix missing required columns: {sorted(missing)}")
    if df.duplicated(["expiry", "entry_ts", "strategy"]).any():
        raise RuntimeError("Duplicate (expiry, entry_ts, strategy) rows in base matrix")
    if df[["net", "net50"]].isna().any().any():
        raise RuntimeError("Base matrix contains null net or stressed net P&L values")

    # Store outcomes, not raw quoted market data. Compress them for durable
    # repository storage and reproduce the exact file hash.
    tmp = OUT / ".full_ready_made_trade_matrix.csv.gz.tmp"
    with matrix_csv.open("rb") as src, tmp.open("wb") as raw_dst:
        with gzip.GzipFile(fileobj=raw_dst, mode="wb", compresslevel=6, mtime=0) as dst:
            shutil.copyfileobj(src, dst)
    tmp.replace(MATRIX)

    split_counts = df.groupby("split").size().to_dict()
    strategy_counts = df.groupby("strategy").size().to_dict()
    expiry_dates = sorted(pd.to_datetime(df["expiry"], errors="coerce").dropna().dt.strftime("%Y-%m-%d").unique())
    entry_dates = sorted(pd.to_datetime(df["entry_ts"], errors="coerce").dropna().dt.strftime("%Y-%m-%d").unique())
    errors_path = Path("results/phase45_ready_made/data_errors.csv")
    errors_count = 0
    if errors_path.exists():
        try:
            errors_count = max(0, len(pd.read_csv(errors_path)))
        except Exception:
            errors_count = -1

    report = {
        "schema_version": "1.0",
        "status": "BASE_GEOMETRY_REPLAY_COMPLETE_NOT_FACTOR_PROMOTION",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": "vishnuvcr/Final-Stand-v5-1-1-1",
        "replay_engines": {
            "phase43_path": "research/phase43_vix_strategy_sweep.py",
            "phase43_source_git_commit": "9e8d10ed662baf941e7cb20edc8477dd5d5dad1b",
            "phase45_path": "research/phase45_ready_made_sweep.py",
            "phase45_source_git_commit": "5849ac8263c4b245138b58073a7703db462a1e33"
        },
        "dataset": HF_REPO,
        "dataset_revision": revision,
        "declared_license": license_id,
        "license_gate": "RESEARCH_ONLY_NONCOMMERCIAL_SOURCE" if str(license_id).lower() == DATASET_LICENSE_EXPECTED else "REVIEW_REQUIRED",
        "trade_matrix_path": str(MATRIX.relative_to(ROOT)),
        "trade_matrix_sha256": sha256(MATRIX),
        "trade_matrix_bytes": MATRIX.stat().st_size,
        "trade_rows": int(len(df)),
        "strategies": int(df["strategy"].nunique()),
        "unique_expiries": int(df["expiry"].nunique()),
        "first_expiry": min(expiry_dates) if expiry_dates else None,
        "last_expiry": max(expiry_dates) if expiry_dates else None,
        "first_entry_date": min(entry_dates) if entry_dates else None,
        "last_entry_date": max(entry_dates) if entry_dates else None,
        "rows_by_split": split_counts,
        "rows_by_strategy": strategy_counts,
        "phase45_data_error_rows": errors_count,
        "cost_semantics": "Inherited Phase45 net is after brokerage and date-aware charges; net50 is its legacy 1.5x-all-modeled-cost scenario. This is not a pure slippage-only stress. Phase52 confirmation must also report fixed statutory charges with adverse slippage stress.",
        "interpretation": "Base-geometry replay only. This does not enumerate or test the complete Phase52 configuration grid and does not promote any strategy. The source dataset declares CC BY-NC 4.0; do not use this source as sole evidence for any commercial deployment.",
    }
    write_json(MANIFEST, report)
    summary_path = Path("results/phase45_ready_made/summary.json")
    if summary_path.exists():
        shutil.copyfile(summary_path, OUT / "phase45_summary.json")
    for src_name, dst_name in [
        ("results/phase45_ready_made/strategy_vix_summary.csv", "strategy_vix_summary.csv"),
        ("results/phase45_ready_made/validation_regime_inference.csv", "validation_regime_inference.csv"),
        ("results/phase45_ready_made/validation_freeze_top3.csv", "validation_freeze_top3.csv"),
        ("results/phase45_ready_made/holdout_frozen_top3_confirmation.csv", "holdout_frozen_top3_confirmation.csv"),
        ("results/phase45_ready_made/data_errors.csv", "phase45_data_errors.csv"),
    ]:
        src = Path(src_name)
        if src.exists():
            shutil.copyfile(src, OUT / dst_name)

    print(json.dumps({
        "status": report["status"],
        "dataset_revision": revision,
        "trade_rows": report["trade_rows"],
        "strategies": report["strategies"],
        "unique_expiries": report["unique_expiries"],
        "first_expiry": report["first_expiry"],
        "last_expiry": report["last_expiry"],
        "matrix_sha256": report["trade_matrix_sha256"],
        "error_rows": errors_count,
        "declared_license": license_id
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
