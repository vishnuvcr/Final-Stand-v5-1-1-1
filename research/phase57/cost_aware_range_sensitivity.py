#!/usr/bin/env python3
"""Bounded Phase57 cost-aware modeled-P&L sweep over preregistered OHLC range thresholds."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "phase52"))
import historical_pilot_runner as runner  # noqa: E402

THRESHOLDS = [2, 1000]
REVISION = "0f4800e43e6f96cec0794369d78eb4d3c4211ef5"
OUT = ROOT / "results" / "phase57" / "cost_aware_range_sensitivity"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_float(values: pd.Series) -> list[float]:
    return [float(x) for x in pd.to_numeric(values, errors="coerce").dropna().tolist()]


def summarize_costs(costs: pd.DataFrame, outcomes: pd.DataFrame, group_columns: list[str]) -> pd.DataFrame:
    """Descriptive summaries; never interpret repeated configurations as independent portfolio trades."""
    if costs.empty:
        return pd.DataFrame()
    records = []
    for keys, group in costs.groupby(group_columns, dropna=False, sort=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        record = dict(zip(group_columns, keys))
        net = pd.to_numeric(group["net_pnl_inr"], errors="coerce").dropna()
        gross_profit = float(net[net > 0].sum())
        gross_loss = float(-net[net < 0].sum())
        record.update({
            "executed_configuration_event_rows": int(len(group)),
            "unique_event_ids": int(group["event_id"].astype(str).nunique()),
            "aggregate_config_event_net_pnl_inr_not_portfolio": float(net.sum()),
            "mean_net_pnl_per_executed_configuration_event_inr": float(net.mean()) if len(net) else None,
            "median_net_pnl_per_executed_configuration_event_inr": float(net.median()) if len(net) else None,
            "win_rate_per_configuration_event": float((net > 0).mean()) if len(net) else None,
            "profit_factor_per_configuration_event": gross_profit / gross_loss if gross_loss > 0 else (float("inf") if gross_profit > 0 else None),
            "positive_configuration_event_rows": int((net > 0).sum()),
            "negative_configuration_event_rows": int((net < 0).sum()),
            "zero_configuration_event_rows": int((net == 0).sum()),
            "interpretation": "DESCRIPTIVE_MODELED_PNL_NOT_EXECUTABLE_NOT_PORTFOLIO_NOT_FOR_SELECTION",
        })
        records.append(record)
    return pd.DataFrame(records)


def load_phase43():
    spec = importlib.util.spec_from_file_location("phase43_phase57", runner.PHASE43_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load existing Phase43 date-aware fee and lot-size helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_sweep() -> dict[str, Any]:
    pilot = json.loads(runner.PILOT_PATH.read_text(encoding="utf-8"))
    if pilot["market_data"]["revision"] != REVISION:
        raise RuntimeError("pilot revision differs from Phase57 frozen revision")
    rows, space, specs = runner.grid.read_inputs()
    errors = runner.grid.validate(rows, space, specs)
    if errors:
        raise RuntimeError("registry/grid validation failed: " + json.dumps(errors[:10]))
    configs = runner.grid_configuration_subset(rows, space, pilot)
    events = runner.select_events(pilot)
    if len(configs) != 40 or len(events) != 24:
        raise RuntimeError(f"frozen sample mismatch: configs={len(configs)}, events={len(events)}")
    if events["split"].astype(str).str.contains("holdout", case=False).any():
        raise RuntimeError("holdout contamination in selected event universe")
    expiry_files = events["expiry"].astype(str).unique().tolist()
    index, option_frames, source_audit = runner.load_cached_inputs(REVISION, expiry_files, os.environ.get("HF_TOKEN") or None)
    if any(x.get("status") != "PASS" for x in source_audit):
        raise RuntimeError("one or more pinned source files failed audit")
    option_hashes = {
        row["source_path"].replace("options/NIFTY/", "").replace(".parquet", ""): row["sha256"]
        for row in source_audit if row.get("source_type") == "OPTION_EXPIRY"
    }
    source_sha = {row["source_path"]: row["sha256"] for row in source_audit}
    template_manifest = runner.resolver.load_source_manifest()
    phase43 = load_phase43()
    registry = {row["candidate_id"]: row for row in rows}
    all_outcomes: list[dict[str, Any]] = []
    all_costs: list[dict[str, Any]] = []
    threshold_counts: dict[int, dict[str, int]] = {}

    for threshold in THRESHOLDS:
        outcomes_this: list[dict[str, Any]] = []
        costs_this: list[dict[str, Any]] = []
        for original in configs:
            conf = copy.deepcopy(original)
            conf["configuration"]["liquidity_max_spread_pct"] = float(threshold)
            matching_events = events[events["entry_time_ist"].astype(str).eq(str(conf["configuration"]["entry_time_ist"]))]
            for _, event in matching_events.iterrows():
                normalized = event.to_dict()
                normalized["entry_ts"] = runner.as_ist_timestamp(event["entry_ts"])
                normalized["expiry"] = runner.canonical_expiry(event["expiry"])
                try:
                    outcome, scenarios = runner.replay_one(
                        normalized, conf, index, option_frames, option_hashes, specs,
                        template_manifest, phase43, registry[conf["candidate_id"]]
                    )
                except Exception as exc:
                    outcome = runner.event_record(
                        normalized, conf, "ERROR_REPLAY_EXCEPTION",
                        f"{type(exc).__name__}: {str(exc)[:500]}"
                    )
                    scenarios = []
                outcome["threshold_pct"] = int(threshold)
                outcomes_this.append(outcome)
                for scenario in scenarios:
                    scenario["threshold_pct"] = int(threshold)
                    all_costs.append(scenario)
                    costs_this.append(scenario)
        counts = Counter(str(x["status"]) for x in outcomes_this)
        if len(outcomes_this) != 480:
            raise RuntimeError(f"threshold {threshold}: expected 480 outcomes, got {len(outcomes_this)}")
        if counts.get("ERROR_REPLAY_EXCEPTION", 0):
            raise RuntimeError(f"threshold {threshold}: replay exceptions {counts['ERROR_REPLAY_EXCEPTION']}")
        if len(costs_this) != counts.get("REPLAY_PASS", 0) * 6:
            raise RuntimeError(f"threshold {threshold}: expected six costs per pass; got {len(costs_this)}")
        threshold_counts[threshold] = dict(counts)
        all_outcomes.extend(outcomes_this)

    pass_counts = [threshold_counts[t].get("REPLAY_PASS", 0) for t in THRESHOLDS]
    if pass_counts != sorted(pass_counts):
        raise RuntimeError(f"replay-pass counts are not monotonic across thresholds: {pass_counts}")
    if pass_counts[0] != 1:
        raise RuntimeError(f"2% baseline does not reconcile to one pass: {pass_counts[0]}")

    outcome_df = pd.DataFrame(all_outcomes)
    cost_df = pd.DataFrame(all_costs)
    OUT.mkdir(parents=True, exist_ok=True)
    outcome_df.to_csv(OUT / "event_outcomes.csv", index=False)
    cost_df.to_csv(OUT / "cost_scenarios.csv", index=False)
    pd.DataFrame(source_audit).to_csv(OUT / "source_file_audit.csv", index=False)
    threshold_summary = summarize_costs(cost_df, outcome_df, ["threshold_pct", "split", "brokerage_per_order_inr", "slippage_stress_pct"])
    family_summary = summarize_costs(cost_df, outcome_df, ["threshold_pct", "family_id", "split", "brokerage_per_order_inr", "slippage_stress_pct"])
    config_summary = summarize_costs(cost_df, outcome_df, ["threshold_pct", "configuration_id", "candidate_id", "family_id", "split", "brokerage_per_order_inr", "slippage_stress_pct"])
    threshold_summary.to_csv(OUT / "threshold_summary.csv", index=False)
    family_summary.to_csv(OUT / "family_summary.csv", index=False)
    config_summary.to_csv(OUT / "configuration_summary.csv", index=False)

    base_ledger = runner.OUT / "event_replay.csv"
    report = {
        "phase": 57, "status": "COST_AWARE_RANGE_SENSITIVITY_COMPLETE",
        "pilot_version": pilot["pilot_version"], "grid_version": pilot["parent_grid_version"],
        "dataset": pilot["market_data"]["dataset"], "dataset_revision": REVISION,
        "declared_license": pilot["market_data"]["declared_license"],
        "configuration_count": len(configs), "selected_event_count": len(events),
        "planned_configuration_event_rows_per_threshold": 480,
        "thresholds_pct": THRESHOLDS,
        "replay_pass_counts_by_threshold": {str(t): threshold_counts[t].get("REPLAY_PASS", 0) for t in THRESHOLDS},
        "status_counts_by_threshold": {str(t): threshold_counts[t] for t in THRESHOLDS},
        "cost_scenario_rows": int(len(cost_df)),
        "expected_cost_scenario_rows": int(sum(threshold_counts[t].get("REPLAY_PASS", 0) * 6 for t in THRESHOLDS)),
        "brokerage_per_order_inr": [20, 10],
        "slippage_stress_pct": [0, 50, 100],
        "adverse_slippage_per_leg_fill_inr": 0.05,
        "statutory_charges": "existing date-aware Phase43/Phase52 fee helper",
        "input_event_ledger_sha256": sha256_file(base_ledger) if base_ledger.exists() else None,
        "source_file_hashes": source_sha,
        "holdout_used": False, "raw_data_committed": False,
        "bid_ask_spread_observed": False, "fills_are_executable_quotes": False,
        "statistical_inference_performed": False, "strategy_ranking_performed": False,
        "production_or_promotion_eligible": False,
        "limitations": [
            "OHLC high-low/open is a candle-range proxy, not bid/ask spread.",
            "Exact option-bar OPEN plus fixed adverse slippage is a modeled fill, not a quote/tick executable fill.",
            "The 40 configurations share the same event identities; configuration-event rows are not independent trades.",
            "Aggregates across configurations are not a realizable portfolio P&L.",
            "The source declares CC BY-NC 4.0; research-only, not commercial/live evidence.",
            "No holdout, p-values, confidence intervals, strategy selection or promotion.",
        ],
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    md = [
        "# Phase 57 — cost-aware OHLC-range sensitivity replay", "",
        "**Modeled P&L only. Not bid/ask, executable liquidity, portfolio returns, or a strategy recommendation.**", "",
        f"- Revision: `{REVISION}`",
        f"- Configurations: {len(configs)}; selected development/validation events: {len(events)}",
        "- Cost model: ₹20/order primary and ₹10/order sensitivity; date-aware statutory charges; ₹0.05 adverse slippage per leg fill at 0/50/100% stress.",
        "", "## Replay passes by threshold", "",
        "| OHLC range threshold (%) | Replay-pass configuration-event rows | Total planned rows |",
        "|---:|---:|---:|",
    ]
    md += [f"| {t} | {threshold_counts[t].get('REPLAY_PASS',0)} | 480 |" for t in THRESHOLDS]
    md += ["", "## Interpretation", "",
           "Results are descriptive sensitivity only. Increasing the threshold mechanically admits more high-range bars; this is not evidence of narrower spreads or better fills.",
           "Net P&L summaries aggregate configuration-event rows and must not be interpreted as a single deployable portfolio. The same event appears under multiple configurations.",
           "No strategy, configuration or threshold was selected. Holdout remains untouched, and CC BY-NC source licensing prohibits treating this as commercial/live evidence.", "",
           "See `threshold_summary.csv`, `family_summary.csv`, `configuration_summary.csv`, `event_outcomes.csv` and `cost_scenarios.csv` for complete ledgers.", ""]
    (OUT / "report.md").write_text("\n".join(md))
    return report


def main() -> int:
    report = run_sweep()
    print(json.dumps(report, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
