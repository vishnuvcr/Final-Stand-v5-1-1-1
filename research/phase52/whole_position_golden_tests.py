#!/usr/bin/env python3
"""End-to-end synthetic whole-position golden tests for Phase 52.

Connects source-bound strategy-template resolution to exact entry/exit contract
bars, prior completed-minute OI, a single common portfolio exit timestamp, the
canonical replay kernel, and all six brokerage/slippage scenarios. Uses only a
deterministic synthetic chain. No historical rows or candidate P&L are read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

import replay_kernel as kernel
import strategy_template_resolver as resolver

ROOT = Path(__file__).resolve().parents[2]
OUT_DEFAULT = ROOT / "results" / "phase52" / "whole_position_golden" / "report.json"
ENTRY_TS = pd.Timestamp("2026-04-15T09:45:00+05:30")
PRIOR_TS = ENTRY_TS - pd.Timedelta(minutes=1)
EXIT_1515 = pd.Timestamp("2026-04-15T15:15:00+05:30")
EXPIRY_EXIT = pd.Timestamp("2026-04-16T15:29:00+05:30")
LOT_SIZE_SYNTHETIC = 65
BASE_CONFIG = {
    "strike_selection": "ATM_OFFSET",
    "atm_offset_steps": 2,
    "wing_width_steps": 3,
    "leg_ratio": [1, 1],
    "reference_lots_per_leg": 1,
    "exit_rule": "15:15_IST",
    "hedge_mode": "NONE",
    "liquidity_max_spread_pct": 2.0,
    "expiry_pairing": "WEEKLY_WEEKLY",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def make_synthetic_chains() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any], list[str]]:
    entry, prior, event, expiries = resolver.synthetic_fixture()
    # Tight but valid ranges let the protocol's OHLC-range liquidity proxy pass.
    entry = entry.copy()
    entry["high"] = pd.to_numeric(entry["open"]) + 0.75
    entry["low"] = pd.to_numeric(entry["open"]) - 0.25
    entry["close"] = pd.to_numeric(entry["open"]) + 0.50
    event = dict(event)
    event["entry_ts"] = kernel.as_ist(event["entry_ts"])
    event["spot_timestamp"] = kernel.as_ist(event["spot_timestamp"])
    entry["timestamp"] = pd.to_datetime(entry["timestamp"], errors="coerce")
    entry["timestamp"] = entry["timestamp"].dt.tz_localize(kernel.TZ) if entry["timestamp"].dt.tz is None else entry["timestamp"].dt.tz_convert(kernel.TZ)
    prior = prior.copy()
    prior["timestamp"] = pd.to_datetime(prior["timestamp"], errors="coerce")
    prior["timestamp"] = prior["timestamp"].dt.tz_localize(kernel.TZ) if prior["timestamp"].dt.tz is None else prior["timestamp"].dt.tz_convert(kernel.TZ)
    # Deterministic entry-day close bars: a distinct price by expiry/type/strike.
    exit_rows = []
    exp_rank = {x: i for i, x in enumerate(sorted(expiries))}
    for row in entry.to_dict("records"):
        strike = float(row["strike"])
        typ = str(row["option_type"]).upper()
        exp = str(pd.Timestamp(row["expiry"]).strftime("%Y-%m-%d"))
        price = 70.0 + abs(strike - 22000.0) / 100.0 + (5.0 if typ == "CE" else 7.0) + 0.5 * exp_rank.get(exp, 0)
        exit_rows.append({
            "timestamp": EXIT_1515, "expiry": exp, "option_type": typ, "strike": strike,
            "open": price, "high": price + 0.75, "low": price - 0.25,
            "close": price + 0.25, "open_interest": float(row.get("open_interest", 500.0)),
        })
    exit_chain = pd.DataFrame(exit_rows)
    return entry, prior, exit_chain, event, list(expiries)


def exact_row_count(frame: pd.DataFrame, timestamp: Any, expiry: Any, option_type: str, strike: float) -> pd.DataFrame:
    ts = kernel.as_ist(timestamp)
    exp = pd.Timestamp(expiry).strftime("%Y-%m-%d")
    stamps = pd.to_datetime(frame["timestamp"], errors="coerce")
    stamps = stamps.dt.tz_localize(kernel.TZ) if stamps.dt.tz is None else stamps.dt.tz_convert(kernel.TZ)
    dates = pd.to_datetime(frame["expiry"], errors="coerce").dt.strftime("%Y-%m-%d")
    mask = (
        stamps.eq(ts)
        & dates.eq(exp)
        & frame["option_type"].astype(str).str.upper().eq(str(option_type).upper())
        & pd.to_numeric(frame["strike"], errors="coerce").eq(float(strike))
    )
    return frame.loc[mask]


def resolve_position(
    family_id: str, config: Mapping[str, Any], event: Mapping[str, Any],
    entry: pd.DataFrame, prior: pd.DataFrame, expiries: Sequence[str]
) -> dict[str, Any]:
    return resolver.resolve_template(
        family_id, config, event, entry, prior, expiries,
        resolver.load_csv(resolver.SPECS_PATH), resolver.load_source_manifest()
    )


def replay_synthetic_position(
    resolved: Mapping[str, Any], config: Mapping[str, Any],
    entry: pd.DataFrame, prior: pd.DataFrame, exit_chain: pd.DataFrame,
    exit_timestamp: Any = EXIT_1515,
) -> dict[str, Any]:
    """Fail closed on any leg error before generating a single portfolio cost scenario."""
    status = str(resolved.get("status", ""))
    if status not in {"TEMPLATE_RESOLVED_ENTRY_GATES_PASS", "DIAGNOSTIC_ONLY_TEMPLATE_RESOLVED"}:
        return {"status": "BLOCKED_TEMPLATE", "reason": status, "scenarios": [], "pnl_computed": False}
    legs = list(resolved.get("legs", []))
    if not legs:
        return {"status": "BLOCKED_EMPTY_POSITION", "scenarios": [], "pnl_computed": False}

    inputs = []
    per_leg_timestamps = []
    used_entry_rows = []
    used_exit_rows = []
    for leg in legs:
        e = kernel.select_exact_bar(entry, resolved["entry_ts"], leg["expiry"], leg["option_type"], float(leg["strike"]))
        if e.status != "PASS" or e.row is None:
            return {"status": "BLOCKED_ENTRY_LEG_ELIGIBILITY", "failed_leg": leg.get("leg_id"), "detail": e.detail, "scenarios": [], "pnl_computed": False}
        prior_matches = exact_row_count(prior, kernel.as_ist(resolved["entry_ts"]) - pd.Timedelta(minutes=1),
                                        leg["expiry"], leg["option_type"], float(leg["strike"]))
        if len(prior_matches) != 1:
            return {"status": "BLOCKED_PRIOR_OI_ROW", "failed_leg": leg.get("leg_id"), "match_count": int(len(prior_matches)), "scenarios": [], "pnl_computed": False}
        oi_ok, oi = kernel.prior_oi_eligible(prior_matches.iloc[0].to_dict(), 100.0)
        if not oi_ok:
            return {"status": "BLOCKED_PRIOR_OI", "failed_leg": leg.get("leg_id"), "prior_oi": oi, "scenarios": [], "pnl_computed": False}
        range_ok, range_proxy = kernel.passes_range_proxy_gate(e.row, float(config.get("liquidity_max_spread_pct", 2.0)))
        if not range_ok:
            return {"status": "BLOCKED_OHLC_RANGE_PROXY", "failed_leg": leg.get("leg_id"), "range_proxy_pct": range_proxy, "scenarios": [], "pnl_computed": False}

        exit_rows = exact_row_count(exit_chain, exit_timestamp, leg["expiry"], leg["option_type"], float(leg["strike"]))
        if len(exit_rows) != 1:
            return {"status": "BLOCKED_EXIT_LEG_ELIGIBILITY", "failed_leg": leg.get("leg_id"), "match_count": int(len(exit_rows)), "scenarios": [], "pnl_computed": False}
        x = kernel.select_exact_bar(exit_chain, exit_timestamp, leg["expiry"], leg["option_type"], float(leg["strike"]))
        if x.status != "PASS" or x.row is None:
            return {"status": "BLOCKED_EXIT_LEG_ELIGIBILITY", "failed_leg": leg.get("leg_id"), "detail": x.detail, "scenarios": [], "pnl_computed": False}

        bars = exit_chain.loc[
            (pd.to_datetime(exit_chain["expiry"], errors="coerce").dt.strftime("%Y-%m-%d") == str(leg["expiry"]))
            & (exit_chain["option_type"].astype(str).str.upper() == str(leg["option_type"]).upper())
            & (pd.to_numeric(exit_chain["strike"], errors="coerce") == float(leg["strike"]))
        ]
        per_leg_timestamps.append([kernel.as_ist(t) for t in bars["timestamp"].tolist()])
        used_entry_rows.append(e.row)
        used_exit_rows.append(x.row)
        inputs.append({
            "side": str(leg["side"]),
            "quantity_lots": float(leg["quantity_lots"]),
            "lot_size": LOT_SIZE_SYNTHETIC,
            "entry_bar": e.row,
            "exit_bar": x.row,
            "exit_price_field": "open",
        })

    common = kernel.latest_common_timestamp(per_leg_timestamps, cutoff=exit_timestamp, not_before=resolved["entry_ts"])
    expected_exit = kernel.as_ist(exit_timestamp)
    if common is None or common != expected_exit:
        return {"status": "BLOCKED_NO_COMMON_EXIT_TIMESTAMP", "common_exit_timestamp": common.isoformat() if common is not None else None, "scenarios": [], "pnl_computed": False}

    scenarios = kernel.evaluate_cost_scenarios(inputs)
    if len(scenarios) != 6:
        raise AssertionError(f"expected six cost scenarios, got {len(scenarios)}")
    expected_order_count = 2 * len(legs)
    if any(int(x["order_count"]) != expected_order_count for x in scenarios):
        raise AssertionError("each leg must have exactly entry and exit orders")
    return {
        "status": "SYNTHETIC_WHOLE_POSITION_PASS",
        "family_id": str(resolved["family_id"]),
        "leg_count": len(legs),
        "lot_quantities": [int(x["quantity_lots"]) for x in legs],
        "common_exit_timestamp": common.isoformat(),
        "entry_timestamp": kernel.as_ist(resolved["entry_ts"]).isoformat(),
        "order_count_per_scenario": expected_order_count,
        "scenarios": scenarios,
        "pnl_computed": True,
        "historical_pnl": False,
        "promotable": False,
    }


def _self_test() -> dict[str, Any]:
    entry, prior, exit_chain, event, expiries = make_synthetic_chains()
    specs = resolver.load_csv(resolver.SPECS_PATH)
    manifest = resolver.load_source_manifest()
    cfg = dict(BASE_CONFIG)
    supported = sorted(resolver.RULES)
    position_rows = []
    for family in supported:
        resolved = resolver.resolve_template(family, cfg, event, entry, prior, expiries, specs, manifest)
        if resolved["status"] not in {"TEMPLATE_RESOLVED_ENTRY_GATES_PASS", "DIAGNOSTIC_ONLY_TEMPLATE_RESOLVED"}:
            raise AssertionError(f"{family} did not resolve in synthetic chain: {resolved}")
        replay = replay_synthetic_position(resolved, cfg, entry, prior, exit_chain)
        if replay["status"] != "SYNTHETIC_WHOLE_POSITION_PASS":
            raise AssertionError(f"{family} end-to-end whole-position test failed: {replay}")
        position_rows.append({
            "family_id": family, "resolver_status": resolved["status"],
            "leg_count": len(resolved["legs"]), "resolved_strikes": [float(x["strike"]) for x in resolved["legs"]],
            "resolved_expiries": [str(x["expiry"]) for x in resolved["legs"]],
            "quantity_lots": [int(x["quantity_lots"]) for x in resolved["legs"]],
            "common_exit_timestamp": replay["common_exit_timestamp"],
            "order_count_per_scenario": replay["order_count_per_scenario"],
            "scenario_count": len(replay["scenarios"]),
            "net_scenarios_inr": [round(float(x["net_pnl_inr"]), 6) for x in replay["scenarios"]],
            "diagnostic_only": resolved["status"] == "DIAGNOSTIC_ONLY_TEMPLATE_RESOLVED",
            "pnl_is_synthetic_only": True,
        })

    # Exercise reference-lot multiplier combined with a ratio override.
    ratio_cfg = dict(BASE_CONFIG, leg_ratio=[2, 1], reference_lots_per_leg=2)
    ratio_resolved = resolve_position("CALL_RATIO_SPREAD", ratio_cfg, event, entry, prior, expiries)
    ratio_position = replay_synthetic_position(ratio_resolved, ratio_cfg, entry, prior, exit_chain)
    assert ratio_position["status"] == "SYNTHETIC_WHOLE_POSITION_PASS", ratio_position
    assert ratio_position["lot_quantities"] == [4, 2], ratio_position["lot_quantities"]

    butterfly_cfg = dict(BASE_CONFIG, leg_ratio=[1, 1], reference_lots_per_leg=2)
    butterfly_resolved = resolve_position("BULL_BUTTERFLY", butterfly_cfg, event, entry, prior, expiries)
    butterfly_position = replay_synthetic_position(butterfly_resolved, butterfly_cfg, entry, prior, exit_chain)
    assert butterfly_position["lot_quantities"] == [2, 4, 2], butterfly_position["lot_quantities"]

    # Missing exit quote on any selected leg must block the entire position and yield zero scenario rows.
    condor_resolved = resolve_position("SHORT_IRON_CONDOR", cfg, event, entry, prior, expiries)
    missing_leg = condor_resolved["legs"][1]
    missing_exit = exit_chain.loc[~(
        (pd.to_datetime(exit_chain["expiry"], errors="coerce").dt.strftime("%Y-%m-%d") == str(missing_leg["expiry"]))
        & (exit_chain["option_type"].astype(str).str.upper() == str(missing_leg["option_type"]).upper())
        & (pd.to_numeric(exit_chain["strike"], errors="coerce") == float(missing_leg["strike"]))
    )].copy()
    blocked_missing_exit = replay_synthetic_position(condor_resolved, cfg, entry, prior, missing_exit)
    assert blocked_missing_exit["status"] == "BLOCKED_EXIT_LEG_ELIGIBILITY", blocked_missing_exit
    assert not blocked_missing_exit["scenarios"] and blocked_missing_exit["pnl_computed"] is False

    # Individually valid exit bars at different timestamps are not a valid synchronized portfolio exit.
    one_contract = condor_resolved["legs"][0]
    skewed_exit = exit_chain.copy()
    mask = (
        (pd.to_datetime(skewed_exit["expiry"], errors="coerce").dt.strftime("%Y-%m-%d") == str(one_contract["expiry"]))
        & (skewed_exit["option_type"].astype(str).str.upper() == str(one_contract["option_type"]).upper())
        & (pd.to_numeric(skewed_exit["strike"], errors="coerce") == float(one_contract["strike"]))
    )
    skewed_exit.loc[mask, "timestamp"] = pd.Timestamp("2026-04-15T15:14:00+05:30")
    blocked_skew = replay_synthetic_position(condor_resolved, cfg, entry, prior, skewed_exit)
    assert blocked_skew["status"] == "BLOCKED_EXIT_LEG_ELIGIBILITY", blocked_skew
    assert not blocked_skew["scenarios"]

    # Missing selected entry bar and low prior OI are fail-closed through resolver and position stage.
    entry_missing, prior2, ev2, exp2 = resolver.synthetic_fixture(remove_entry=("2026-04-16","CE",22100.0))
    entry_missing["high"] = pd.to_numeric(entry_missing["open"]) + 0.75
    entry_missing["low"] = pd.to_numeric(entry_missing["open"]) - 0.25
    entry_missing["close"] = pd.to_numeric(entry_missing["open"]) + 0.50
    blocked_entry = resolver.resolve_template("BUY_CALL",cfg,ev2,entry_missing,prior2,exp2,specs,manifest)
    assert blocked_entry["status"] == "BLOCKED_LEG_ELIGIBILITY"
    low_entry, low_prior, ev3, exp3 = resolver.synthetic_fixture(prior_oi_override=("2026-04-16","CE",22100.0))
    low_entry["high"] = pd.to_numeric(low_entry["open"]) + 0.75
    low_entry["low"] = pd.to_numeric(low_entry["open"]) - 0.25
    low_entry["close"] = pd.to_numeric(low_entry["open"]) + 0.50
    blocked_oi = resolver.resolve_template("BUY_CALL",cfg,ev3,low_entry,low_prior,exp3,specs,manifest)
    assert blocked_oi["status"] == "BLOCKED_LEG_ELIGIBILITY"

    report = {
        "status": "PASS",
        "test_version": "phase52-whole-position-golden-v0.1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "supported_option_templates_tested": len(supported),
        "whole_positions_costed_synthetically": len(position_rows),
        "ratio_plus_reference_lot_test": {"status": "PASS", "quantities": ratio_position["lot_quantities"]},
        "base_template_scale_test": {"status": "PASS", "quantities": butterfly_position["lot_quantities"]},
        "fail_closed_missing_exit_test": {"status": "PASS", "pnl_computed": False, "scenario_count": 0},
        "fail_closed_noncommon_timestamp_test": {"status": "PASS", "pnl_computed": False, "scenario_count": 0},
        "fail_closed_missing_entry_test": {"status": "PASS", "resolver_status": blocked_entry["status"]},
        "fail_closed_low_prior_oi_test": {"status": "PASS", "resolver_status": blocked_oi["status"]},
        "scenario_shape": {"brokerage_scenarios_inr": [20,10], "slippage_stress_pct": [0,50,100], "scenarios_per_position": 6},
        "positions": position_rows,
        "template_manifest_sha256": sha256_file(resolver.MANIFEST_PATH),
        "specifications_sha256": sha256_file(resolver.SPECS_PATH),
        "resolver_sha256": sha256_file(Path(resolver.__file__)),
        "kernel_sha256": sha256_file(Path(kernel.__file__)),
        "protocol_sha256": sha256_file(resolver.PROTOCOL_PATH),
        "no_historical_market_data_used": True,
        "no_historical_pnl_computed": True,
        "all_promotable_flags_false": True,
        "note": "The net P&L values in positions are synthetic fixture arithmetic only; no historical trades were simulated.",
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--report", type=Path, default=OUT_DEFAULT)
    args = parser.parse_args()
    if not args.self_test:
        raise SystemExit("Synthetic whole-position golden tests only; historical configuration replay is not enabled.")
    report = _self_test()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
