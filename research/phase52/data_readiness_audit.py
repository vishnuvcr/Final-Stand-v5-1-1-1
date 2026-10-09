#!/usr/bin/env python3
"""Inspect point-in-time feature availability and licensing before selector replay."""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq
from huggingface_hub import HfApi, hf_hub_download

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "phase52" / "data_readiness"
HF_OLD = "thetrademarkk/india-index-options-1m"
HF_PRIMARY = "rissin/nse-options-intraday"
KNOWN_PRIMARY_FILE = "upstox_intraday/NIFTY/NIFTY_2026.parquet"
KNOWN_PRIMARY_SHA256 = "bae9943b2fa99ee9c1214fb7c695b84f9f661a050a5cd04d9c5c2ffc7bc59f73"


def sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_license(info: Any) -> str | None:
    try:
        return getattr(getattr(info, "card_data", None), "license", None)
    except Exception:
        return None


def inspect_parquet(repo_id: str, revision: str, filename: str, token: str | None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "repo": repo_id, "revision": revision, "filename": filename,
        "status": "NOT_STARTED",
    }
    try:
        path = hf_hub_download(
            repo_id=repo_id, filename=filename, repo_type="dataset",
            revision=revision, token=token,
        )
        pf = pq.ParquetFile(path)
        result["status"] = "PASS_SCHEMA_READ"
        result["cache_path_not_persisted"] = True
        result["bytes"] = Path(path).stat().st_size
        result["sha256"] = sha256(path)
        result["columns"] = list(pf.schema_arrow.names)
        result["total_rows_metadata"] = int(pf.metadata.num_rows)
        result["row_groups_total"] = int(pf.num_row_groups)
        usecols = [c for c in [
            "timestamp", "date", "expiry", "strike", "option_type", "close",
            "volume", "open_interest", "oi", "underlying", "granularity", "source"
        ] if c in pf.schema_arrow.names]
        # Sample row groups rather than materialising the full multi-year index
        # history in Actions memory. Option expiry files with modest row counts
        # may still be fully covered by these first/middle/last row groups.
        if pf.num_row_groups:
            sample_groups = sorted(set([0, pf.num_row_groups // 2, pf.num_row_groups - 1]))
            frames = [pf.read_row_group(g, columns=usecols).to_pandas() for g in sample_groups]
            frame = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=usecols)
        else:
            sample_groups = []
            frame = pd.DataFrame(columns=usecols)
        result["sample_row_groups_read"] = sample_groups
        result["sample_rows_read"] = int(len(frame))
        result["timestamp_sample_min"] = None
        result["timestamp_sample_max"] = None
        result["timestamp_metadata_min"] = None
        result["timestamp_metadata_max"] = None
        if "timestamp" in frame.columns and len(frame):
            ts = pd.to_datetime(frame["timestamp"], errors="coerce")
            result["timestamp_sample_min"] = str(ts.min())
            result["timestamp_sample_max"] = str(ts.max())
        # Row-group statistics, when present, provide full-file min/max without
        # reading every row. Keep the sample and metadata facts distinct.
        if "timestamp" in pf.schema_arrow.names:
            col_index = pf.schema_arrow.names.index("timestamp")
            mins, maxs = [], []
            for rg_idx in range(pf.num_row_groups):
                stats = pf.metadata.row_group(rg_idx).column(col_index).statistics
                if stats is not None and stats.has_min_max:
                    mins.append(stats.min)
                    maxs.append(stats.max)
            if mins:
                result["timestamp_metadata_min"] = str(min(mins))
                result["timestamp_metadata_max"] = str(max(maxs))
        for col in ("open_interest", "oi", "volume", "close"):
            if col in frame.columns:
                vals = pd.to_numeric(frame[col], errors="coerce")
                result[col + "_nonnull_fraction"] = float(vals.notna().mean()) if len(vals) else None
                if col in ("open_interest", "oi", "volume"):
                    result[col + "_positive_fraction"] = float((vals > 0).mean()) if len(vals) else None
        if "underlying" in frame.columns:
            result["underlyings_observed"] = sorted(frame["underlying"].dropna().astype(str).str.upper().unique().tolist())[:20]
        if "granularity" in frame.columns:
            result["granularities_observed"] = sorted(frame["granularity"].dropna().astype(str).str.lower().unique().tolist())[:20]
        # Never retain market data rows in the report.
        del frame
    except Exception as exc:
        result["status"] = "ERROR"
        result["error_type"] = type(exc).__name__
    return result


def main() -> int:
    token = os.environ.get("HF_TOKEN") or None
    OUT.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "DATA_READINESS_AUDIT_NOT_BACKTEST",
        "credentials_present": {"HF_TOKEN": bool(token)},
        "sources": [],
    }
    api = HfApi(token=token)
    errors = []
    try:
        requested_revision = os.environ.get("PHASE52_HF_REVISION", "").strip()
        old = api.dataset_info(HF_OLD, revision=requested_revision or None)
        old_rev = str(old.sha)
        old_files = set(api.list_repo_files(HF_OLD, repo_type="dataset", revision=old_rev))
        old_license = safe_license(old)
        option_paths = sorted(
            p for p in old_files
            if re.fullmatch(r"options/NIFTY/\d{4}-\d{2}-\d{2}\.parquet", p)
        )
        years: dict[int, list[str]] = {}
        for path in option_paths:
            year = int(path.split("/")[-1][:4])
            years.setdefault(year, []).append(path)
        preferred_years = [2021, 2023, 2025, 2026]
        sample_files = []
        for year in preferred_years:
            options = years.get(year, [])
            if not options:
                continue
            # Sample the middle available expiry for each selected year.
            sample_files.append(options[len(options) // 2])
        latest_options = [p for p in option_paths if p.endswith("2026-07-21.parquet")]
        if latest_options and latest_options[0] not in sample_files:
            sample_files.append(latest_options[0])
        index_path = "index/NIFTY.parquet"
        old_source = {
            "repo": HF_OLD,
            "revision": old_rev,
            "license": old_license,
            "license_gate": "RESEARCH_ONLY_NONCOMMERCIAL" if str(old_license).lower() == "cc-by-nc-4.0" else "REVIEW_REQUIRED",
            "file_count": len(old_files),
            "nifty_option_expiry_file_count": len(option_paths),
            "first_option_file": option_paths[0] if option_paths else None,
            "last_option_file": option_paths[-1] if option_paths else None,
            "nifty_futures_intraday_files": [p for p in old_files if re.search(r"(^|/)(futures|future)/NIFTY(/|_)", p, re.I)][:30],
            "sample_files": [inspect_parquet(HF_OLD, old_rev, p, token) for p in sample_files],
        }
        if index_path in old_files:
            old_source["index_sample"] = inspect_parquet(HF_OLD, old_rev, index_path, token)
        else:
            old_source["index_sample"] = {"status": "NOT_FOUND", "filename": index_path}
        if not old_source["nifty_futures_intraday_files"]:
            old_source["nifty_futures_intraday_status"] = "NO_NIFTY_FUTURES_FILE_FOUND_IN_THIS_DATASET"
        report["sources"].append(old_source)
    except Exception as exc:
        errors.append({"source": HF_OLD, "error_type": type(exc).__name__})
        report["sources"].append({"repo": HF_OLD, "status": "METADATA_ERROR", "error_type": type(exc).__name__})

    try:
        primary = api.dataset_info(HF_PRIMARY)
        primary_rev = str(primary.sha)
        primary_files = set(api.list_repo_files(HF_PRIMARY, repo_type="dataset", revision=primary_rev))
        primary_license = safe_license(primary)
        exists = KNOWN_PRIMARY_FILE in primary_files
        report["sources"].append({
            "repo": HF_PRIMARY,
            "revision": primary_rev,
            "license": primary_license,
            "file_count": len(primary_files),
            "primary_2026_nifty_intraday_file_present": exists,
            "primary_2026_file": KNOWN_PRIMARY_FILE if exists else None,
            "prior_audited_sha256": KNOWN_PRIMARY_SHA256,
            "prior_audited_bytes": 394805617,
            "intraday_open_interest_status": "DOCUMENTED_NAN_FOR_UPSTOX_INTRADAY; not eligible for OI selection in this track without a separately validated alternative",
            "schema_source": "https://huggingface.co/datasets/rissin/nse-options-intraday",
            "coverage_scope": "1-minute Upstox option candles; source-gated Phase 51-3 is complete only through 2026-07-21",
            "note": "Metadata-only on this run: do not download/commit the full annual source merely to restate a schema already documented and audited in Phase 51-3."
        })
    except Exception as exc:
        errors.append({"source": HF_PRIMARY, "error_type": type(exc).__name__})
        report["sources"].append({"repo": HF_PRIMARY, "status": "METADATA_ERROR", "error_type": type(exc).__name__})

    # Explicit source-capability inventory: absence is a real result, not zero.
    report["factor_capability"] = {
        "nifty_spot_1m": "AVAILABLE_FROM_HISTORICAL_INDEX_FILE; exact timestamp matching required",
        "option_ltp_ohlcv": "AVAILABLE_ON_SAMPLED_OPTION_EXPIRY_FILES; coverage must be measured at each event/leg",
        "historical_oi": "SAMPLED_ON_LEGACY_DATASET; only if open_interest nonnull coverage passes and the noncommercial source license is respected",
        "oi_on_rissin_2026_intraday": "UNAVAILABLE_DOCUMENTED_NAN; must not treat as zero or neutral",
        "india_vix": "AVAILABLE_AS_CACHED_DAILY_CLOSE; only use prior published observation",
        "exchange_published_greeks": "NOT_PRESENT_IN_THE_TWO_DOCUMENTED_SCHEMAS; any option Greeks are model-estimated, not exchange-supplied",
        "greeks_estimation": "POSSIBLE_FROM_SYNCHRONIZED_OPTION_LTP_AND_SPOT_USING_A_FROZEN_MODEL; flag stale/invalid premiums and report model/rate assumptions",
        "synthetic_future": "DERIVABLE_AS_AN_ESTIMATE_FROM_SYNCHRONIZED_MATCHED_CALL_PUT_PAIRS; distinguish from traded futures, include carry/fees and mark LTP/quote uncertainty",
        "nifty_futures_intraday": "NOT_FOUND_IN_LEGACY_HF_REPO_FILE_PATHS; use separate validated futures source if available",
        "nifty_futures_eod": "SOURCE_CANDIDATE_EXISTS_IN_USER_REPOSITORY_vishnuvcr/Iron_condor/scripts/download_nifty_history.py; a prior-session EOD basis proxy is not intraday basis",
        "bid_ask_spread": "NOT_PRESENT_IN_THE_DOCUMENTED_BAR_SCHEMAS; do not fabricate, use volume/OI only as liquidity proxies and perform adverse-slippage stresses",
        "global_cross_market_flows_news_corporate_actions": "NOT_YET_AUDITED_FOR_POINT_IN_TIME_COVERAGE",
    }
    report["errors"] = errors
    report["status"] = "PASS_METADATA_AND_SAMPLE_AUDIT_WITH_REVIEW_GATES" if not errors else "PARTIAL_WITH_SOURCE_METADATA_ERRORS"
    out = OUT / "source_capability_audit.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "source_capability_audit.sha256").write_text(sha256(out) + "  source_capability_audit.json\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "sources": [{k: s.get(k) for k in ("repo", "revision", "license", "file_count", "nifty_option_expiry_file_count", "nifty_futures_intraday_status")} for s in report["sources"]],
        "errors": errors,
        "output": str(out),
    }, indent=2))
    return 0 if report["sources"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
