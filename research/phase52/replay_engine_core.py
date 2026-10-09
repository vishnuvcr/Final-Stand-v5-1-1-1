#!/usr/bin/env python3
"""Cross-check the canonical Phase52 replay kernel against Phase43 cost code.

This is a test harness, not a second execution engine. All exact-bar, prior-OI,
common-exit, slippage and leg-level calculations are delegated to
research/phase52/replay_kernel.py. This harness adds independently checked
single-/multi-leg fixtures and fee parity against Phase43. No market rows or
historical strategy P&L are calculated.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TZ = "Asia/Kolkata"
PHASE43_SCRIPT = ROOT / "research" / "phase43_vix_strategy_sweep.py"
PROTOCOL = ROOT / "PHASE52_REPLAY_PROTOCOL.md"
KERNEL_PATH = ROOT / "research" / "phase52" / "replay_kernel.py"
if str(KERNEL_PATH.parent) not in sys.path:
    sys.path.insert(0, str(KERNEL_PATH.parent))
import replay_kernel as kernel


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def as_ist(value: Any) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    return ts.tz_localize(TZ) if ts.tzinfo is None else ts.tz_convert(TZ)


def load_phase43():
    if not PHASE43_SCRIPT.exists():
        raise FileNotFoundError(f"Missing accepted Phase43 fee helper: {PHASE43_SCRIPT}")
    name = "_phase52_phase43_fee_helper"
    spec = importlib.util.spec_from_file_location(name, PHASE43_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load Phase43 fee helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def fixture_bar(timestamp: str, open_price: float, high: float, low: float, close: float) -> dict[str, Any]:
    return {"timestamp": timestamp, "open": open_price, "high": high, "low": low, "close": close}


def self_test() -> dict[str, Any]:
    # Re-run the canonical kernel tests to ensure this harness is pinned to the same behavior.
    kernel.self_test()
    phase43 = load_phase43()
    entry_ts = "2026-04-15T09:45:00+05:30"
    exit_ts = "2026-04-15T15:15:00+05:30"
    entry = fixture_bar(entry_ts, 100.0, 101.0, 99.0, 100.5)
    exit_long = fixture_bar(exit_ts, 125.0, 126.0, 124.0, 125.0)

    # Hand-check single long: raw P&L = (125-100)*65 = ₹1,625.
    # Two adverse ₹0.05 fills remove 0.10*65 = ₹6.50, giving ₹1,618.50 before fees.
    single = kernel.evaluate_leg_fill("BUY", 1, 65, entry, exit_long, "open", 0.05)
    assert abs(single["gross_pnl"] - 1618.5) < 1e-8, single
    raw_single = (125.0 - 100.0) * 65.0
    assert abs((raw_single - single["gross_pnl"]) - 6.5) < 1e-8

    # Fee parity: exact same base-stress filled orders passed through each schedule.
    kernel_fees = kernel.cost_breakdown(single["orders"], 20.0)
    phase43_orders = [
        (as_ist(o["date"]), str(o["action"]).lower(), float(o["price"]))
        for o in single["orders"]
    ]
    phase43_fees = phase43.charges(
        phase43_orders, 65, cost_mult=1.0, brokerage_per_order=20.0
    )
    assert abs(kernel_fees["total"] - phase43_fees) < 1e-8, (
        kernel_fees["total"], phase43_fees
    )

    # Hand-check 2-leg bear-call vertical: (100-25)+(4-30)=49 points; 49*65=₹3,185 raw.
    # Two legs each have entry and exit fills; ₹0.05 per fill reduces combined P&L by ₹13.
    entry_short = fixture_bar(entry_ts, 100.0, 101.0, 99.0, 100.0)
    exit_short = fixture_bar(exit_ts, 25.0, 25.5, 24.5, 25.0)
    entry_wing = fixture_bar(entry_ts, 30.0, 30.3, 29.7, 30.0)
    exit_wing = fixture_bar(exit_ts, 4.0, 4.1, 3.9, 4.0)
    vertical_inputs = [
        {"side": "SELL", "quantity_lots": 1, "lot_size": 65,
         "entry_bar": entry_short, "exit_bar": exit_short, "exit_price_field": "open"},
        {"side": "BUY", "quantity_lots": 1, "lot_size": 65,
         "entry_bar": entry_wing, "exit_bar": exit_wing, "exit_price_field": "open"},
    ]
    vertical_scenarios = kernel.evaluate_cost_scenarios(
        vertical_inputs, brokerage_scenarios=(20.0,), slippage_stresses_pct=(0, 50, 100)
    )
    base_vertical = vertical_scenarios[0]
    assert abs(base_vertical["gross_pnl_inr"] - 3172.0) < 1e-8, base_vertical
    assert base_vertical["order_count"] == 4
    assert base_vertical["fees_brokerage_inr"] == 80.0
    assert abs(3185.0 - base_vertical["gross_pnl_inr"] - 13.0) < 1e-8

    # All brokerage/slippage cases remain side-by-side for identical quote references.
    six = kernel.evaluate_cost_scenarios([
        {"side":"BUY","quantity_lots":1,"lot_size":65,
         "entry_bar":entry,"exit_bar":exit_long,"exit_price_field":"open"}
    ])
    assert len(six) == 6
    assert {r["brokerage_per_order_inr"] for r in six} == {10.0,20.0}
    assert {r["slippage_stress_pct"] for r in six} == {0,50,100}
    assert {r["order_count"] for r in six} == {2}

    # Flat brokerage is charged per executed order, not per lot.
    two_lot = kernel.evaluate_cost_scenarios([
        {"side":"BUY","quantity_lots":2,"lot_size":65,
         "entry_bar":entry,"exit_bar":exit_long,"exit_price_field":"open"}
    ], brokerage_scenarios=(20.0,), slippage_stresses_pct=(0,))
    assert two_lot[0]["fees_brokerage_inr"] == 40.0
    assert abs(two_lot[0]["gross_pnl_inr"] - 3237.0) < 1e-8

    return {
        "status": "PASS",
        "tests": [
            "canonical deterministic kernel self-tests",
            "single-long fill and slippage hand calculation",
            "two-leg vertical fill/slippage hand calculation",
            "statutory charge and GST parity against Phase43",
            "₹20 primary and ₹10 legacy brokerage scenarios",
            "0/50/100 percent slippage-only stress levels",
            "flat brokerage per order, not per lot",
        ],
        "single_long_raw_gross_rupees": raw_single,
        "single_long_base_after_slippage_before_fees_rupees": single["gross_pnl"],
        "single_long_slippage_cost_rupees": raw_single - single["gross_pnl"],
        "vertical_raw_gross_rupees": 3185.0,
        "vertical_base_after_slippage_before_fees_rupees": base_vertical["gross_pnl_inr"],
        "vertical_slippage_cost_rupees": 3185.0 - base_vertical["gross_pnl_inr"],
        "phase43_fee_parity_rupees": phase43_fees,
        "kernel_sha256": sha256_file(KERNEL_PATH),
        "phase43_fee_helper_sha256": sha256_file(PHASE43_SCRIPT),
        "harness_sha256": sha256_file(Path(__file__)),
        "protocol_sha256": sha256_file(PROTOCOL),
        "note": "Synthetic fixture tests only. No historical market event was replayed and no strategy is promoted.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not args.self_test:
        raise SystemExit("Test harness only; production replay remains blocked until explicit integration gate.")
    report = self_test()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
