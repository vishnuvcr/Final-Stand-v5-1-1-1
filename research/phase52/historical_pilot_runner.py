#!/usr/bin/env python3
"""Bounded historical BASELINE replay pilot for Phase 52.

This runner is deliberately not the production grid worker. It consumes the
pre-registered first_historical_pilot.json, selects exactly 40 deterministic
grid-v1.3 configurations, samples development/validation events without looking
at option-leg success or P&L, and replays only ATM_OFFSET + BASELINE + DTE=0 +
exact 15:15 same-day exits. Other selector modes, exits, hedges, delta and
futures-dependent strategies remain blocked elsewhere, not approximated here.

The source data declares CC BY-NC 4.0; this is research-only. All P&L from this
runner is exploratory, descriptive and unpromoted. It reads pinned market data
but never writes raw market data into the repository.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[2]
PHASE = ROOT / "research" / "phase52"
PILOT_PATH = PHASE / "first_historical_pilot.json"
SPACE_PATH = PHASE / "configuration_space.json"
REGISTRY_PATH = PHASE / "strategy_registry.csv"
SPECS_PATH = PHASE / "strategy_specifications.csv"
PROTOCOL_PATH = ROOT / "PHASE52_REPLAY_PROTOCOL.md"
RESOLVER_PATH = PHASE / "strategy_template_resolver.py"
KERNEL_PATH = PHASE / "replay_kernel.py"
VALIDATOR_PATH = PHASE / "validate_registry.py"
PHASE43_PATH = ROOT / "research" / "phase43_vix_strategy_sweep.py"
EVENTS_PATH = ROOT / "results" / "phase52" / "configuration_event_universe" / "expected_events.csv"
BASE_MANIFEST_PATH = ROOT / "results" / "phase52" / "base_replay" / "manifest.json"
OUT = ROOT / "results" / "phase52" / "historical_pilot"
HF_REPO = "thetrademarkk/india-index-options-1m"
TZ = "Asia/Kolkata"
EXPECTED_CONFIG_COUNT = 40

if str(PHASE) not in sys.path:
    sys.path.insert(0, str(PHASE))
import replay_kernel as kernel
import strategy_template_resolver as resolver
import validate_registry as grid


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def as_ist_series(series: pd.Series) -> pd.Series:
    x = pd.to_datetime(series, errors="coerce")
    if x.dt.tz is None:
        return x.dt.tz_localize(TZ)
    return x.dt.tz_convert(TZ)


def as_ist_timestamp(value: Any) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    return ts.tz_localize(TZ) if ts.tzinfo is None else ts.tz_convert(TZ)


def truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def canonical_expiry(value: Any) -> str:
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def grid_configuration_subset(
    rows: list[dict[str, str]], space: dict[str, Any], pilot: dict[str, Any]
) -> list[dict[str, Any]]:
    """Enumerate from v1.3's exact mixed-radix helper, then apply the frozen pilot filter."""
    f = pilot["configuration_filter"]
    wanted_families = set(f["family_ids"])
    selected_rows = {
        row["family_id"]: row for row in rows
        if row["family_id"] in wanted_families and row["selector_mode"] == f["selector_mode"]
    }
    missing_families = wanted_families - set(selected_rows)
    if missing_families:
        raise RuntimeError(f"Frozen pilot families missing BASELINE registry rows: {sorted(missing_families)}")

    width_families = {"BULL_CALL_SPREAD", "BEAR_CALL_SPREAD", "SHORT_IRON_CONDOR"}
    ratio_families = {"LONG_STRADDLE", "LONG_STRANGLE"}
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for family_id in f["family_ids"]:
        candidate = selected_rows[family_id]
        for dims in grid.branches_for(candidate, space):
            # Only the registered ATM_OFFSET branch.
            if not any(name == "strike_selection" and values == ["ATM_OFFSET"] for name, values in dims):
                continue
            n = grid.product_size(dims)
            for rank in range(n):
                config = grid.unrank_product(dims, rank)
                if int(config.get("entry_dte_calendar_days", -1)) != 0:
                    continue
                if config.get("entry_time_ist") not in f["entry_time_ist"]:
                    continue
                if config.get("exit_rule") != f["exit_rule"]:
                    continue
                if config.get("strike_selection") != f["strike_selection"]:
                    continue
                if int(config.get("atm_offset_steps", -999)) not in f["atm_offset_steps"]:
                    continue
                if int(config.get("reference_lots_per_leg", -1)) != 1:
                    continue
                if float(config.get("liquidity_max_spread_pct", -1)) != 2.0:
                    continue
                if "hedge_mode" in config and config["hedge_mode"] != "NONE":
                    continue
                if family_id in width_families and int(config.get("wing_width_steps", -1)) not in f["wing_width_steps"]["values"]:
                    continue
                # These templates do not use a wing-width parameter in their leg map.
                # Retain only width=1 as a non-redundant representative.
                if family_id not in width_families and "wing_width_steps" in config and int(config["wing_width_steps"]) != 1:
                    continue
                if family_id in ratio_families and tuple(config.get("leg_ratio", [])) != (1, 1):
                    continue
                if family_id not in ratio_families and "leg_ratio" in config:
                    # The selected families with ratio dimensions are the two cases above.
                    continue

                # Identity follows the original v1.3 algorithm and excludes the ID field itself.
                cfg_id = grid.config_id(space["grid_version"], candidate["candidate_id"], config)
                if cfg_id in seen:
                    raise RuntimeError(f"Duplicate pilot configuration ID: {cfg_id}")
                seen.add(cfg_id)
                out.append({
                    "grid_version": space["grid_version"],
                    "dataset_revision": pilot["market_data"]["revision"],
                    "configuration_id": cfg_id,
                    "candidate_id": candidate["candidate_id"],
                    "family_id": family_id,
                    "family_name": candidate["family_name"],
                    "selector_mode": candidate["selector_mode"],
                    "risk_class": candidate["risk_class"],
                    "configuration": config,
                    "canonical_configuration_json": json.dumps(config, sort_keys=True, separators=(",", ":"), ensure_ascii=True),
                    "geometry_width_applicable": family_id in width_families,
                })

    out.sort(key=lambda row: (row["family_id"], row["configuration"]["entry_time_ist"],
                              int(row["configuration"]["atm_offset_steps"]),
                              int(row["configuration"].get("wing_width_steps", 1))))
    if len(out) != int(f["expected_configuration_count"]) or len(out) != EXPECTED_CONFIG_COUNT:
        raise RuntimeError(f"Frozen pilot expected {EXPECTED_CONFIG_COUNT} configs, produced {len(out)}; refusing to run.")
    # Fail closed if a non-baseline candidate or unsupported parameter slipped through.
    if any(row["selector_mode"] != "BASELINE" for row in out):
        raise RuntimeError("Non-baseline candidate leaked into pilot config subset")
    return out


def select_events(pilot: dict[str, Any]) -> pd.DataFrame:
    if not EVENTS_PATH.exists():
        raise FileNotFoundError(f"Missing frozen event inventory: {EVENTS_PATH}")
    source = pd.read_csv(EVENTS_PATH, dtype={"event_id": str})
    required = {"event_id", "dataset_revision", "expiry", "split", "entry_dte_calendar_days",
                "entry_time_ist", "entry_ts", "index_has_exact_entry_timestamp"}
    missing = required - set(source.columns)
    if missing:
        raise ValueError(f"Event inventory missing fields: {sorted(missing)}")
    rows = source[
        pd.to_numeric(source["entry_dte_calendar_days"], errors="coerce").eq(0)
        & source["entry_time_ist"].astype(str).isin(pilot["event_sampling"]["entry_time_ist"])
        & source["split"].astype(str).isin(["development", "validation"])
        & source["index_has_exact_entry_timestamp"].map(truthy)
    ].copy()
    rows["expiry"] = rows["expiry"].map(canonical_expiry)
    rows["entry_ts"] = as_ist_series(rows["entry_ts"])
    selected: list[pd.Series] = []
    n_per = int(pilot["event_sampling"]["events_per_split_per_entry_time"])
    for split in ("development", "validation"):
        for entry_time in pilot["event_sampling"]["entry_time_ist"]:
            g = rows[(rows["split"].astype(str) == split) & (rows["entry_time_ist"].astype(str) == entry_time)]
            g = g.sort_values(["expiry", "event_id"]).drop_duplicates("expiry").reset_index(drop=True)
            if len(g) < n_per:
                raise RuntimeError(f"Insufficient exact-index event dates for {split}/{entry_time}: {len(g)} < {n_per}")
            idx = np.rint(np.linspace(0, len(g) - 1, n_per)).astype(int)
            idx = sorted(set(int(i) for i in idx))
            if len(idx) != n_per:
                raise RuntimeError(f"Even-spacing event sample produced duplicate indices for {split}/{entry_time}")
            selected.extend([g.iloc[i] for i in idx])
    result = pd.DataFrame(selected).sort_values(["expiry", "entry_time_ist", "event_id"]).reset_index(drop=True)
    expected = int(pilot["event_sampling"]["expected_event_rows"])
    if len(result) != expected:
        raise RuntimeError(f"Expected {expected} frozen event rows, got {len(result)}")
    if result["event_id"].nunique() != expected:
        raise RuntimeError("Pilot event IDs are not unique")
    if result["split"].astype(str).str.contains("holdout", case=False).any():
        raise RuntimeError("Holdout leaked into the bounded pilot sample")
    return result


def create_manifest(
    pilot: dict[str, Any], configs: list[dict[str, Any]], events: pd.DataFrame
) -> dict[str, Any]:
    rows, space, specs = grid.read_inputs()
    # The registry, specifications, grid, protocol and resolver manifest are fingerprinted.
    cfg_df = pd.DataFrame([{
        "grid_version": x["grid_version"],
        "configuration_id": x["configuration_id"],
        "candidate_id": x["candidate_id"],
        "family_id": x["family_id"],
        "family_name": x["family_name"],
        "selector_mode": x["selector_mode"],
        "risk_class": x["risk_class"],
        "configuration_json": x["canonical_configuration_json"],
        "geometry_width_applicable": x["geometry_width_applicable"],
    } for x in configs])
    cfg_csv = cfg_df.to_csv(index=False, lineterminator="\n")
    ev_csv = events.to_csv(index=False, lineterminator="\n")
    file_hashes = {
        "pilot_plan_sha256": sha256_file(PILOT_PATH),
        "grid_sha256": sha256_file(SPACE_PATH),
        "registry_sha256": sha256_file(REGISTRY_PATH),
        "specifications_sha256": sha256_file(SPECS_PATH),
        "template_manifest_sha256": sha256_file(resolver.MANIFEST_PATH),
        "replay_protocol_sha256": sha256_file(PROTOCOL_PATH),
        "resolver_sha256": sha256_file(RESOLVER_PATH),
        "kernel_sha256": sha256_file(KERNEL_PATH),
        "grid_enumerator_sha256": sha256_file(VALIDATOR_PATH),
        "historical_pilot_runner_sha256": sha256_file(Path(__file__)),
        "phase43_fee_and_lot_helper_sha256": sha256_file(PHASE43_PATH),
        "event_inventory_sha256": sha256_file(EVENTS_PATH),
        "configuration_manifest_sha256": sha256_text(cfg_csv),
        "selected_events_sha256": sha256_text(ev_csv),
    }
    return {
        "status": "FROZEN_PILOT_MANIFEST_BEFORE_HISTORICAL_REPLAY",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_branch_commit": subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip(),
        "pilot_version": pilot["pilot_version"],
        "grid_version": space["grid_version"],
        "historical_pnl_not_yet_computed_at_manifest_creation": True,
        "pinned_dataset": pilot["market_data"]["dataset"],
        "dataset_revision": pilot["market_data"]["revision"],
        "declared_license": pilot["market_data"]["declared_license"],
        "configuration_count": len(configs),
        "configuration_ids": [x["configuration_id"] for x in configs],
        "family_counts": {str(k): int(v) for k, v in cfg_df["family_id"].value_counts().items()},
        "candidate_ids": sorted(cfg_df["candidate_id"].unique().tolist()),
        "expected_event_rows": len(events),
        "event_ids": events["event_id"].astype(str).tolist(),
        "events_by_split_and_time": {
            f"{split}/{tm}": int(((events["split"].astype(str) == split) & (events["entry_time_ist"].astype(str) == tm)).sum())
            for split in ("development", "validation")
            for tm in pilot["event_sampling"]["entry_time_ist"]
        },
        "planned_config_event_rows": int(sum((events["entry_time_ist"].astype(str) == c["configuration"]["entry_time_ist"]).sum() for c in configs)),
        "holdout_used": False,
        "selector_scope": "BASELINE only; this pilot makes no factor-selector efficacy claim",
        "inference": "No candidate ranking, p-values, or promotion. Descriptive implementation and coverage pilot only.",
        "file_hashes": file_hashes,
    }


def load_cached_inputs(revision: str, expiries: Sequence[str], token: str | None) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], list[dict[str, Any]]]:
    index_name = "index/NIFTY.parquet"
    index_path = Path(hf_hub_download(repo_id=HF_REPO, filename=index_name, repo_type="dataset",
                                     revision=revision, token=token))
    index_sha = sha256_file(index_path)
    index = pd.read_parquet(index_path, columns=["timestamp", "open", "high", "low", "close"])
    index["timestamp"] = as_ist_series(index["timestamp"])
    for column in ("open", "high", "low", "close"):
        index[column] = pd.to_numeric(index[column], errors="coerce")
    index = index.dropna(subset=["timestamp"]).sort_values("timestamp", kind="stable")

    option_frames: dict[str, pd.DataFrame] = {}
    source_audit: list[dict[str, Any]] = [{
        "source_type": "INDEX",
        "source_path": index_name,
        "revision": revision,
        "sha256": index_sha,
        "bytes": int(index_path.stat().st_size),
        "rows": int(len(index)),
        "timestamp_min": index["timestamp"].min().isoformat() if len(index) else None,
        "timestamp_max": index["timestamp"].max().isoformat() if len(index) else None,
        "status": "PASS",
    }]
    need_cols = ["timestamp", "option_type", "strike", "open", "high", "low", "close", "open_interest"]
    unique_expiries = sorted(set(map(canonical_expiry, expiries)))
    print(json.dumps({"event":"PILOT_SOURCE_LOAD_START","revision":revision,"option_expiry_files":len(unique_expiries)}),flush=True)
    for file_no, expiry in enumerate(unique_expiries, start=1):
        name = f"options/NIFTY/{expiry}.parquet"
        path = Path(hf_hub_download(repo_id=HF_REPO, filename=name, repo_type="dataset", revision=revision, token=token))
        digest = sha256_file(path)
        frame = pd.read_parquet(path)
        missing = set(need_cols) - set(frame.columns)
        if missing:
            raise ValueError(f"{name} is missing required columns {sorted(missing)}")
        frame["timestamp"] = as_ist_series(frame["timestamp"])
        frame["option_type"] = frame["option_type"].astype(str).str.upper().str.strip()
        frame["strike"] = pd.to_numeric(frame["strike"], errors="coerce")
        for column in ("open", "high", "low", "close", "open_interest"):
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        if "expiry" in frame.columns:
            frame["expiry"] = pd.to_datetime(frame["expiry"], errors="coerce").dt.strftime("%Y-%m-%d")
            exact_expiries = set(frame["expiry"].dropna().astype(str).unique().tolist())
            if exact_expiries and exact_expiries != {expiry}:
                # Multi-expiry files are allowed only when target rows are present;
                # resolver will still select the exact target contract.
                if expiry not in exact_expiries:
                    raise ValueError(f"{name} expiry column does not contain its path expiry")
        else:
            # The dataset's immutable file path is the expiry key for this partition.
            frame["expiry"] = expiry
        frame = frame.dropna(subset=["timestamp", "strike"]).sort_values(["timestamp", "option_type", "strike"], kind="stable")
        rows_before_exact_dedup = int(len(frame))
        # Remove only rows identical across every source column after canonical
        # timestamp/type/numeric normalization. Conflicting rows for the same
        # timestamp/expiry/type/strike are deliberately retained and fail closed
        # in exact_rows()/select_exact_bar(); never average or pick one.
        frame = frame.drop_duplicates(keep="first").reset_index(drop=True)
        exact_duplicate_rows_removed = rows_before_exact_dedup - int(len(frame))
        option_frames[expiry] = frame
        source_audit.append({
            "source_type": "OPTION_EXPIRY",
            "source_path": name,
            "revision": revision,
            "sha256": digest,
            "bytes": int(path.stat().st_size),
            "rows_source_after_normalization": rows_before_exact_dedup,
            "exact_duplicate_rows_removed": exact_duplicate_rows_removed,
            "rows": int(len(frame)),
            "timestamp_min": frame["timestamp"].min().isoformat() if len(frame) else None,
            "timestamp_max": frame["timestamp"].max().isoformat() if len(frame) else None,
            "status": "PASS",
        })
        if file_no % 3 == 0 or file_no == len(unique_expiries):
            print(json.dumps({"event":"PILOT_SOURCE_LOAD_PROGRESS","files_done":file_no,"files_total":len(unique_expiries),"expiry":expiry,"rows":int(len(frame))}),flush=True)
    return index, option_frames, source_audit


def event_record(event: Mapping[str, Any], conf: Mapping[str, Any], status: str, reason: str,
                 spot: float | None = None, lot: int | None = None, legs: Sequence[Mapping[str, Any]] = (),
                 source_hash: str | None = None, exit_ts: Any | None = None) -> dict[str, Any]:
    cfg = conf["configuration"]
    return {
        "pilot_version": "phase52-historical-base-pilot-v0.2",
        "grid_version": conf["grid_version"],
        "configuration_id": conf["configuration_id"],
        "candidate_id": conf["candidate_id"],
        "family_id": conf["family_id"],
        "selector_mode": conf["selector_mode"],
        "split": str(event.get("split", "")),
        "event_id": str(event.get("event_id", "")),
        "expiry": canonical_expiry(event.get("expiry")),
        "entry_ts": as_ist_timestamp(event.get("entry_ts")).isoformat(),
        "entry_time_ist": str(cfg["entry_time_ist"]),
        "entry_dte_calendar_days": int(cfg["entry_dte_calendar_days"]),
        "configuration_json": conf["canonical_configuration_json"],
        "status": status,
        "exclusion_reason": reason,
        "spot_open": spot,
        "lot_size": lot,
        "exit_ts": as_ist_timestamp(exit_ts).isoformat() if exit_ts is not None else None,
        "resolved_legs_json": json.dumps(list(legs), sort_keys=True, separators=(",", ":"), default=str),
        "option_source_sha256": source_hash,
        "historical_pnl_used_for_selection": False,
        "promotable": False,
    }


def exact_rows(frame: pd.DataFrame, timestamp: Any, expiry: str, option_type: str, strike: float) -> pd.DataFrame:
    ts = as_ist_timestamp(timestamp)
    mask = (
        frame["timestamp"].eq(ts)
        & frame["expiry"].astype(str).eq(canonical_expiry(expiry))
        & frame["option_type"].astype(str).str.upper().eq(str(option_type).upper())
        & pd.to_numeric(frame["strike"], errors="coerce").eq(float(strike))
    )
    return frame.loc[mask]


def replay_one(
    event: Mapping[str, Any],
    conf: Mapping[str, Any],
    index: pd.DataFrame,
    option_frames: Mapping[str, pd.DataFrame],
    option_hashes: Mapping[str, str],
    spec_rows: list[dict[str, str]],
    template_manifest: Mapping[str, Any],
    phase43: Any,
    registry_row: Mapping[str, str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    cfg = conf["configuration"]
    expiry = canonical_expiry(event["expiry"])
    entry_ts = as_ist_timestamp(event["entry_ts"])
    option_frame = option_frames.get(expiry)
    source_hash = option_hashes.get(expiry)
    if option_frame is None or option_frame.empty:
        return event_record(event, conf, "EXCLUDED_SOURCE_FILE_UNAVAILABLE", "target expiry parquet missing or empty", source_hash=source_hash), []

    idx_rows = index.loc[index["timestamp"].eq(entry_ts)]
    if len(idx_rows) != 1:
        return event_record(event, conf, "EXCLUDED_INDEX_ENTRY", f"expected one exact index row at entry, found {len(idx_rows)}", source_hash=source_hash), []
    spot_open = float(idx_rows.iloc[0]["open"]) if pd.notna(idx_rows.iloc[0]["open"]) else math.nan
    if not math.isfinite(spot_open) or spot_open <= 0:
        return event_record(event, conf, "EXCLUDED_INDEX_ENTRY", "exact index open is absent/nonpositive", source_hash=source_hash), []

    entry_event = {
        "expiry": expiry,
        "entry_ts": entry_ts,
        "spot_open": spot_open,
        "spot_timestamp": entry_ts,
    }
    result = resolver.resolve_template(
        conf["family_id"], cfg, entry_event, option_frame, option_frame,
        sorted(option_frames.keys()), spec_rows, template_manifest,
        risk_class=registry_row["risk_class"],
    )
    if result.get("status") not in {"TEMPLATE_RESOLVED_ENTRY_GATES_PASS", "DIAGNOSTIC_ONLY_TEMPLATE_RESOLVED"}:
        return event_record(event, conf, result.get("status", "BLOCKED_TEMPLATE"),
                            str(result.get("reason", result.get("gate_reason", "template resolver blocked"))),
                            spot_open, source_hash=source_hash, legs=result.get("leg_exclusions", [])), []

    exit_ts = entry_ts.normalize() + pd.Timedelta(hours=15, minutes=15)
    lot_size = int(phase43.lot_size_for_expiry(pd.Timestamp(expiry, tz=TZ)))
    leg_inputs: list[dict[str, Any]] = []
    resolved_leg_rows: list[dict[str, Any]] = []
    per_leg_timestamps = []
    for leg in result["legs"]:
        entry_result = kernel.select_exact_bar(
            option_frame, entry_ts, leg["expiry"], leg["option_type"], float(leg["strike"])
        )
        if entry_result.status != "PASS" or entry_result.row is None:
            return event_record(event, conf, "EXCLUDED_ENTRY_LEG", f"{leg['leg_id']}: {entry_result.status}: {entry_result.detail}",
                                spot_open, lot_size, resolved_leg_rows, source_hash), []
        prior_ts = entry_ts - pd.Timedelta(minutes=1)
        prior = exact_rows(option_frame, prior_ts, leg["expiry"], leg["option_type"], float(leg["strike"]))
        if len(prior) != 1:
            return event_record(event, conf, "EXCLUDED_PRIOR_OI", f"{leg['leg_id']}: expected one exact prior-minute OI row, found {len(prior)}",
                                spot_open, lot_size, resolved_leg_rows, source_hash), []
        oi_ok, oi_val = kernel.prior_oi_eligible(prior.iloc[0].to_dict(), 100.0)
        if not oi_ok:
            return event_record(event, conf, "EXCLUDED_PRIOR_OI", f"{leg['leg_id']}: prior-minute OI missing/below 100; value={oi_val}",
                                spot_open, lot_size, resolved_leg_rows, source_hash), []
        range_ok, range_value = kernel.passes_range_proxy_gate(
            entry_result.row, float(cfg["liquidity_max_spread_pct"])
        )
        if not range_ok:
            return event_record(event, conf, "EXCLUDED_OHLC_RANGE_PROXY",
                                f"{leg['leg_id']}: OHLC high-low/open proxy {range_value} exceeds gate {cfg['liquidity_max_spread_pct']}",
                                spot_open, lot_size, resolved_leg_rows, source_hash), []
        exit_rows = exact_rows(option_frame, exit_ts, leg["expiry"], leg["option_type"], float(leg["strike"]))
        if len(exit_rows) != 1:
            return event_record(event, conf, "EXCLUDED_EXIT_LEG",
                                f"{leg['leg_id']}: expected one exact 15:15 exit bar, found {len(exit_rows)}",
                                spot_open, lot_size, resolved_leg_rows, source_hash, exit_ts), []
        exit_result = kernel.select_exact_bar(
            option_frame, exit_ts, leg["expiry"], leg["option_type"], float(leg["strike"])
        )
        if exit_result.status != "PASS" or exit_result.row is None:
            return event_record(event, conf, "EXCLUDED_EXIT_LEG",
                                f"{leg['leg_id']}: {exit_result.status}: {exit_result.detail}",
                                spot_open, lot_size, resolved_leg_rows, source_hash, exit_ts), []
        # Common-time check across all bars for this contract. The protocol requires exact 15:15,
        # not a latest-common fallback; this also rejects inconsistent data timestamps.
        contract_bars = option_frame.loc[
            option_frame["expiry"].astype(str).eq(canonical_expiry(leg["expiry"]))
            & option_frame["option_type"].astype(str).str.upper().eq(str(leg["option_type"]).upper())
            & pd.to_numeric(option_frame["strike"], errors="coerce").eq(float(leg["strike"]))
        ]
        per_leg_timestamps.append(contract_bars["timestamp"].tolist())
        resolved_leg_rows.append({
            "leg_id": leg["leg_id"], "side": leg["side"], "option_type": leg["option_type"],
            "strike": float(leg["strike"]), "expiry": canonical_expiry(leg["expiry"]),
            "quantity_lots": int(leg["quantity_lots"]), "lot_size": lot_size,
            "entry_open": float(entry_result.row["open"]), "exit_open": float(exit_result.row["open"]),
            "prior_oi": float(oi_val), "prior_oi_timestamp": prior_ts.isoformat(),
            "entry_range_proxy_pct": range_value, "entry_status": "PASS", "exit_status": "PASS",
        })
        leg_inputs.append({
            "side": leg["side"],
            "quantity_lots": int(leg["quantity_lots"]),
            "lot_size": lot_size,
            "entry_bar": entry_result.row,
            "exit_bar": exit_result.row,
            "exit_price_field": "open",
        })

    common = kernel.latest_common_timestamp(
        per_leg_timestamps, cutoff=exit_ts, not_before=entry_ts
    )
    if common is None or common != exit_ts:
        return event_record(event, conf, "EXCLUDED_NO_COMMON_EXIT", f"no exact common 15:15 exit; common={common}",
                            spot_open, lot_size, resolved_leg_rows, source_hash, exit_ts), []

    scenarios = kernel.evaluate_cost_scenarios(leg_inputs)
    if len(scenarios) != 6:
        raise RuntimeError(f"Expected six cost scenarios but received {len(scenarios)}")
    for row in scenarios:
        row.update({
            "configuration_id": conf["configuration_id"],
            "candidate_id": conf["candidate_id"],
            "family_id": conf["family_id"],
            "selector_mode": conf["selector_mode"],
            "split": str(event["split"]),
            "event_id": str(event["event_id"]),
            "expiry": expiry,
            "entry_ts": entry_ts.isoformat(),
            "exit_ts": exit_ts.isoformat(),
            "lot_size": lot_size,
            "source_revision": conf["dataset_revision"],
            "source_file_sha256": source_hash,
        })
    record = event_record(event, conf, "REPLAY_PASS",
                          "all resolved legs passed exact entry/prior-OI/OHLC-range/exact common 15:15 exit gates",
                          spot_open, lot_size, resolved_leg_rows, source_hash, exit_ts)
    record["resolver_status"] = result["status"]
    record["net_scenarios_count"] = len(scenarios)
    return record, scenarios


def summarize(replay: pd.DataFrame, costs: pd.DataFrame) -> pd.DataFrame:
    if replay.empty:
        return pd.DataFrame()
    if costs.empty:
        # A run with zero executed events must still emit a report and exclusions,
        # rather than crash while trying to index absent scenario columns.
        costs = pd.DataFrame(columns=[
            "configuration_id","split","event_id","entry_ts",
            "brokerage_per_order_inr","slippage_stress_pct","net_pnl_inr"
        ])
    records = []
    for config_id in replay["configuration_id"].drop_duplicates():
        cfg = replay[replay["configuration_id"].eq(config_id)]
        for split in ("development", "validation"):
            sr = cfg[cfg["split"].astype(str).eq(split)]
            passed_ids = set(sr.loc[sr["status"].eq("REPLAY_PASS"), "event_id"].astype(str))
            for brokerage in (20.0, 10.0):
                for stress in (0, 50, 100):
                    cost = costs[
                        costs["configuration_id"].eq(config_id)
                        & costs["split"].astype(str).eq(split)
                        & pd.to_numeric(costs["brokerage_per_order_inr"], errors="coerce").eq(brokerage)
                        & pd.to_numeric(costs["slippage_stress_pct"], errors="coerce").eq(stress)
                    ].sort_values(["entry_ts", "event_id"])
                    net = pd.to_numeric(cost["net_pnl_inr"], errors="coerce").dropna()
                    positive = float(net[net > 0].sum())
                    negative = float(-net[net < 0].sum())
                    cumulative = net.cumsum().to_numpy(float)
                    dd = float(np.max(np.maximum.accumulate(cumulative) - cumulative)) if len(cumulative) else 0.0
                    records.append({
                        "configuration_id": config_id,
                        "candidate_id": str(cfg["candidate_id"].iloc[0]),
                        "family_id": str(cfg["family_id"].iloc[0]),
                        "entry_time_ist": str(cfg["entry_time_ist"].iloc[0]),
                        "split": split,
                        "expected_events": int(len(sr)),
                        "executed_events": int(len(cost)),
                        "eligible_fraction": float(len(cost) / len(sr)) if len(sr) else 0.0,
                        "excluded_events": int((~sr["status"].eq("REPLAY_PASS")).sum()),
                        "brokerage_per_order_inr": brokerage,
                        "slippage_stress_pct": stress,
                        "net_pnl_rupees": float(net.sum()) if len(net) else None,
                        "mean_net_per_executed_event_rupees": float(net.mean()) if len(net) else None,
                        "win_rate_net": float((net > 0).mean()) if len(net) else None,
                        "profit_factor_net": positive / negative if negative > 0 else (math.inf if positive > 0 else None),
                        "max_drawdown_net_rupees": dd,
                        "return_on_reference_capital_pct": 100.0 * float(net.sum()) / kernel.REFERENCE_CAPITAL_INR if len(net) else None,
                        "interpretation": "DESCRIPTIVE_ENGINEERING_PILOT_ONLY_NOT_FOR_SELECTION_OR_PROMOTION",
                    })
    return pd.DataFrame(records)


def build_outputs(
    pilot: dict[str, Any], configs: list[dict[str, Any]], events: pd.DataFrame,
    manifest: dict[str, Any], index: pd.DataFrame, option_frames: dict[str, pd.DataFrame],
    source_audit: list[dict[str, Any]], source_hashes: dict[str, str]
) -> dict[str, Any]:
    rows, space, specs = grid.read_inputs()
    template_manifest = resolver.load_source_manifest()
    p43spec = importlib.util.spec_from_file_location("phase43_for_historical_pilot", PHASE43_PATH)
    if p43spec is None or p43spec.loader is None:
        raise RuntimeError("Could not load Phase43 date-aware lot-size and charge module")
    phase43 = importlib.util.module_from_spec(p43spec)
    p43spec.loader.exec_module(phase43)

    registry = {row["candidate_id"]: row for row in rows}
    event_rows: list[dict[str, Any]] = []
    cost_rows: list[dict[str, Any]] = []
    for config_no, config in enumerate(configs, start=1):
        candidate = registry[config["candidate_id"]]
        print(json.dumps({"event":"PILOT_CONFIG_START","config_no":config_no,"config_total":len(configs),
                          "configuration_id":config["configuration_id"],"family_id":config["family_id"],
                          "entry_time_ist":config["configuration"]["entry_time_ist"]}),flush=True)
        matching_events = events[events["entry_time_ist"].astype(str).eq(config["configuration"]["entry_time_ist"])]
        for _, event in matching_events.iterrows():
            normalized_event = event.to_dict()
            normalized_event["entry_ts"] = as_ist_timestamp(event["entry_ts"])
            normalized_event["expiry"] = canonical_expiry(event["expiry"])
            if not truthy(event["index_has_exact_entry_timestamp"]):
                outcome = event_record(normalized_event, config, "EXCLUDED_INDEX_ENTRY", "frozen event record lacks exact index entry timestamp")
                scenarios = []
            else:
                try:
                    outcome, scenarios = replay_one(normalized_event, config, index, option_frames,
                                                    source_hashes, specs, template_manifest, phase43, registry[config["candidate_id"]])
                except Exception as exc:
                    reason = f"{type(exc).__name__}: {str(exc)[:500]}"
                    print(json.dumps({"event":"PILOT_REPLAY_EXCEPTION","configuration_id":config["configuration_id"],
                                      "event_id":str(event.get("event_id","")),"reason":reason}),flush=True)
                    outcome = event_record(normalized_event, config, "ERROR_REPLAY_EXCEPTION", reason)
                    scenarios = []
            event_rows.append(outcome)
            cost_rows.extend(scenarios)

    replay_df = pd.DataFrame(event_rows)
    cost_df = pd.DataFrame(cost_rows)
    OUT.mkdir(parents=True, exist_ok=True)
    # Persist event outcomes and exclusions before summary aggregation. If the
    # summary stage itself has a programming defect, these ledgers remain visible.
    replay_df.to_csv(OUT / "event_replay.csv", index=False)
    cost_df.to_csv(OUT / "cost_scenarios.csv", index=False)
    pd.DataFrame(source_audit).to_csv(OUT / "source_file_audit.csv", index=False)
    exclusions = replay_df[~replay_df["status"].eq("REPLAY_PASS")].copy()
    exclusions.to_csv(OUT / "excluded_events.csv", index=False)
    summary_df = summarize(replay_df, cost_df)
    summary_df.to_csv(OUT / "config_split_summary.csv", index=False)

    counts = replay_df["status"].value_counts(dropna=False).to_dict() if not replay_df.empty else {}
    replay_error_rows = int(replay_df["status"].astype(str).str.startswith("ERROR_").sum()) if len(replay_df) else 0
    report_status = "HISTORICAL_BASELINE_PILOT_WITH_REPLAY_ERRORS" if replay_error_rows else "HISTORICAL_BASELINE_PILOT_COMPLETE_WITH_EXPLICIT_EXCLUSIONS"
    report = {
        "status": report_status,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "pilot_version": pilot["pilot_version"],
        "historical_pnl_calculated": bool(not cost_df.empty and replay_error_rows == 0),
        "production_or_promotion_eligible": False,
        "pinned_dataset": HF_REPO,
        "dataset_revision": manifest["dataset_revision"],
        "declared_license": pilot["market_data"]["declared_license"],
        "configurations": len(configs),
        "selected_event_rows": len(events),
        "planned_config_event_rows": len(replay_df),
        "executed_event_rows": int(replay_df["status"].eq("REPLAY_PASS").sum()) if len(replay_df) else 0,
        "excluded_or_error_event_rows": len(exclusions),
        "replay_exception_count": replay_error_rows,
        "cost_scenario_rows": len(cost_df),
        "cost_scenarios_per_executed_event": 6,
        "status_counts": {str(k): int(v) for k, v in counts.items()},
        "configs_by_family": {str(k): int(v) for k, v in pd.DataFrame(configs)["family_id"].value_counts().items()},
        "executed_by_split": {str(k): int(v) for k, v in replay_df[replay_df["status"].eq("REPLAY_PASS")].groupby("split").size().items()},
        "selector_scope": "BASELINE only; no factor selector efficacy test",
        "holdout_used": False,
        "no_outcome_based_event_selection": True,
        "source_files_audited": len(source_audit),
        "source_file_errors": int(sum(1 for x in source_audit if x.get("status") != "PASS")),
        "input_fingerprints": manifest["file_hashes"],
        "source_file_hashes": source_hashes,
        "limitations": [
            "Non-commercial CC BY-NC 4.0 options data; this is not commercial/live evidence.",
            "Historical index series ends 2026-07-02; July 28/August 4 records remain unresolved.",
            "Only development and validation split events are included; 2026 holdout is untouched.",
            "The pilot samples 40 baseline configurations and 24 target events; it is not the full v1.3 grid.",
            "One-minute OHLC-open fills plus fixed adverse slippage are modeled references, not tick-level/bid-ask executable fills.",
            "No significance testing, configuration ranking, router selection or promotion is performed.",
        ],
        "outputs": {
            "event_replay": "results/phase52/historical_pilot/event_replay.csv",
            "cost_scenarios": "results/phase52/historical_pilot/cost_scenarios.csv",
            "config_split_summary": "results/phase52/historical_pilot/config_split_summary.csv",
            "exclusions": "results/phase52/historical_pilot/excluded_events.csv",
            "source_audit": "results/phase52/historical_pilot/source_file_audit.csv",
        },
    }
    write_json(OUT / "report.json", report)
    write_json(OUT / "pilot_manifest.json", manifest)
    report_md = [
        "# Phase 52 — Bounded historical baseline pilot",
        "",
        f"**Status:** {report['status']}; no candidate promoted.",
        f"- Dataset revision: `{manifest['dataset_revision']}` (declared licence: {report['declared_license']}).",
        f"- Configurations: {report['configurations']}; frozen event rows: {report['selected_event_rows']}; config-event rows: {report['planned_config_event_rows']}.",
        f"- Replay passes: {report['executed_event_rows']}; exclusions/errors: {report['excluded_or_error_event_rows']}; six-cost scenario rows: {report['cost_scenario_rows']}.",
        f"- Cost schedule: ₹20 primary / ₹10 legacy sensitivity × 0/50/100% adverse-slippage stress; date-aware statutory fees separate.",
        "- Selector mode is BASELINE only. Results are engineering diagnostics, not a test of VIX/Greeks/OI router uplift.",
        "- Event selection was fixed without inspecting option-leg success or P&L. No holdout was used.",
        "",
        "## Config/split summaries",
        "",
        "| Family | Config ID | Split | Executed / expected | Eligibility | Brokerage/order ₹ | Slippage stress % | Net P&L ₹ | Mean/trade ₹ | Win rate | Max DD ₹ |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    if not summary_df.empty:
        for r in summary_df.itertuples(index=False):
            net = f"{r.net_pnl_rupees:,.0f}" if pd.notna(r.net_pnl_rupees) else "NA"
            mean = f"{r.mean_net_per_executed_event_rupees:,.0f}" if pd.notna(r.mean_net_per_executed_event_rupees) else "NA"
            wr = f"{100*r.win_rate_net:.1f}%" if pd.notna(r.win_rate_net) else "NA"
            dd = f"{r.max_drawdown_net_rupees:,.0f}" if pd.notna(r.max_drawdown_net_rupees) else "NA"
            report_md.append(f"| {r.family_id} | `{r.configuration_id}` | {r.split} | {r.executed_events}/{r.expected_events} | {r.eligible_fraction:.1%} | {r.brokerage_per_order_inr:.0f} | {r.slippage_stress_pct} | {net} | {mean} | {wr} | {dd} |")
    report_md += [
        "",
        "## Interpretation limits",
        "",
        "- Descriptive per-configuration outputs are not a strategy ranking; do not choose a winner from this pilot.",
        "- Source license is non-commercial. All open/close fills are OHLC simulation references, not observed bid/ask.",
        "- The finite v1.3 grid remains separate; this bounded pilot does not mean any large fraction of the 9,379,584 configurations was tested.",
        "- Exclusions are kept explicit in `excluded_events.csv`; no missing bar is filled or interpolated.",
    ]
    (OUT / "report.md").write_text("\n".join(report_md) + "\n", encoding="utf-8")
    return report


def prepare_plan_only() -> dict[str, Any]:
    pilot = json.loads(PILOT_PATH.read_text(encoding="utf-8"))
    rows, space, specs = grid.read_inputs()
    errors = grid.validate(rows, space, specs)
    if errors:
        raise RuntimeError(f"Grid/registry validation errors: {errors}")
    configs = grid_configuration_subset(rows, space, pilot)
    events = select_events(pilot)
    manifest = create_manifest(pilot, configs, events)
    OUT.mkdir(parents=True, exist_ok=True)
    config_df = pd.DataFrame([{
        "grid_version": x["grid_version"], "configuration_id": x["configuration_id"],
        "candidate_id": x["candidate_id"], "family_id": x["family_id"], "family_name": x["family_name"],
        "selector_mode": x["selector_mode"], "risk_class": x["risk_class"],
        "configuration_json": x["canonical_configuration_json"],
        "geometry_width_applicable": x["geometry_width_applicable"],
    } for x in configs])
    config_df.to_csv(OUT / "configuration_manifest.csv", index=False)
    events.to_csv(OUT / "selected_events.csv", index=False)
    write_json(OUT / "pilot_manifest.json", manifest)
    print(json.dumps({
        "status": manifest["status"],
        "configuration_count": len(configs),
        "family_counts": manifest["family_counts"],
        "event_count": len(events),
        "event_counts": manifest["events_by_split_and_time"],
        "planned_config_event_rows": manifest["planned_config_event_rows"],
        "holdout_used": False,
        "file_hashes": manifest["file_hashes"],
        "note": "No historical option data were loaded and no P&L was computed in plan-only mode.",
    }, indent=2))
    return manifest


def run_historical() -> dict[str, Any]:
    pilot = json.loads(PILOT_PATH.read_text(encoding="utf-8"))
    rows, space, specs = grid.read_inputs()
    errs = grid.validate(rows, space, specs)
    if errs:
        raise RuntimeError(f"registry/grid validation gate failed: {errs}")
    configs = grid_configuration_subset(rows, space, pilot)
    events = select_events(pilot)
    manifest_now = create_manifest(pilot, configs, events)
    manifest_path = OUT / "pilot_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError("Frozen pilot_manifest.json missing; run --plan-only before --run")
    frozen = json.loads(manifest_path.read_text(encoding="utf-8"))
    compare = ["pilot_version", "grid_version", "dataset_revision", "configuration_ids", "event_ids",
               "file_hashes", "configuration_count", "expected_event_rows"]
    drift = [field for field in compare if frozen.get(field) != manifest_now.get(field)]
    if drift:
        raise RuntimeError(f"Frozen pilot manifest drift after plan stage in fields: {drift}")
    # Capture data input revision from the pinned base manifest and require it to match the preregistration.
    base_manifest = json.loads(BASE_MANIFEST_PATH.read_text(encoding="utf-8"))
    revision = str(base_manifest["dataset_revision"])
    if revision != pilot["market_data"]["revision"]:
        raise RuntimeError(f"Base replay manifest revision {revision} differs from frozen pilot revision")
    token = os.getenv("HF_TOKEN") or None
    print(json.dumps({"event":"PILOT_REPLAY_START","configurations":len(configs),"events":len(events),
                      "config_event_rows":int(sum((events["entry_time_ist"].astype(str)==c["configuration"]["entry_time_ist"]).sum() for c in configs)),
                      "revision":revision}),flush=True)
    expiry_files = events["expiry"].astype(str).unique().tolist()
    index, option_frames, source_audit = load_cached_inputs(revision, expiry_files, token)
    option_hashes = {
        row["source_path"].replace("options/NIFTY/", "").replace(".parquet", ""): row["sha256"]
        for row in source_audit if row.get("source_type") == "OPTION_EXPIRY" and row.get("status") == "PASS"
    }
    data_report = build_outputs(pilot, configs, events, manifest_now, index, option_frames, source_audit, option_hashes)
    print(json.dumps(data_report, indent=2, default=str))
    return data_report


def self_test() -> None:
    pilot = json.loads(PILOT_PATH.read_text(encoding="utf-8"))
    rows, space, specs = grid.read_inputs()
    errors = grid.validate(rows, space, specs)
    assert not errors, errors
    configs = grid_configuration_subset(rows, space, pilot)
    assert len(configs) == EXPECTED_CONFIG_COUNT
    assert len({x["configuration_id"] for x in configs}) == EXPECTED_CONFIG_COUNT
    assert set(x["selector_mode"] for x in configs) == {"BASELINE"}
    assert set(x["family_id"] for x in configs) == set(pilot["configuration_filter"]["family_ids"])
    assert all(x["configuration"]["exit_rule"] == "15:15_IST" for x in configs)
    assert all(x["configuration"]["entry_dte_calendar_days"] == 0 for x in configs)
    assert all(x["configuration"]["strike_selection"] == "ATM_OFFSET" for x in configs)
    events = select_events(pilot)
    assert len(events) == pilot["event_sampling"]["expected_event_rows"] == 24
    assert not events["split"].astype(str).str.contains("holdout", case=False).any()
    assert all(truthy(x) for x in events["index_has_exact_entry_timestamp"])
    p = kernel.passes_range_proxy_gate({"open":100,"high":101,"low":99,"close":100.5},2.0)
    assert p[0] is True
    # Duplicate normalization removes only rows identical across all columns.
    dup_fixture = pd.DataFrame([
        {"timestamp":"2024-01-04T09:44:00+05:30","expiry":"2024-01-04","option_type":"CE","strike":22000,"open":100.0,"open_interest":500},
        {"timestamp":"2024-01-04T09:44:00+05:30","expiry":"2024-01-04","option_type":"CE","strike":22000,"open":100.0,"open_interest":500},
        {"timestamp":"2024-01-04T09:44:00+05:30","expiry":"2024-01-04","option_type":"CE","strike":22000,"open":101.0,"open_interest":500},
    ])
    dedup_fixture = dup_fixture.drop_duplicates(keep="first")
    assert len(dup_fixture) == 3 and len(dedup_fixture) == 2
    assert dedup_fixture.iloc[0]["open"] == 100.0 and dedup_fixture.iloc[1]["open"] == 101.0
    missing = kernel.select_exact_bar(pd.DataFrame(columns=["timestamp","expiry","option_type","strike","open","high","low","close"]),
                                     "2024-01-04T09:45:00+05:30","2024-01-04","CE",22000)
    assert missing.status in {"BLOCKED_SCHEMA","NO_EXACT_CONTRACT_BAR"}
    print(json.dumps({
        "status":"SELF_TEST_PASS",
        "configurations":len(configs),
        "configuration_ids_sha256":sha256_text("\n".join(x["configuration_id"] for x in configs)),
        "event_count":len(events),
        "event_ids_sha256":sha256_text("\n".join(events["event_id"].astype(str))),
        "checks":["exact v1.3 enumerator identities","pilot config filter","event sample fixed before P&L","holdout excluded","exact whole-row duplicate removal only","conflicting duplicate contract bars fail closed","OHLC range-proxy gate","missing exact contract fails closed"],
        "historical_data_downloaded":False,
        "pnl_computed":False,
    },indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test-only", action="store_true")
    mode.add_argument("--plan-only", action="store_true")
    mode.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.self_test_only:
        self_test()
        return 0
    if args.plan_only:
        prepare_plan_only()
        return 0
    run_historical()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
