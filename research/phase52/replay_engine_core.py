#!/usr/bin/env python3
"""Pure replay primitives and hand-checked tests for Phase 52 configuration replay.

No data downloading, model fitting or P&L backtest occurs here. Given a fully
resolved set of exact-time leg bars, this module tests time/quote/OI eligibility,
adverse open fills, lot ratios, and date-aware Paytm Money charge scenarios.
The statutory rate schedule is delegated to the accepted Phase43 helper so it
does not silently drift. All outputs are diagnostic until integrated and audited.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TZ = "Asia/Kolkata"
PHASE43_SCRIPT = ROOT / "research" / "phase43_vix_strategy_sweep.py"
PROTOCOL = ROOT / "PHASE52_REPLAY_PROTOCOL.md"
BASE_SLIPPAGE_RUPEES = 0.05
SLIPPAGE_STRESSES_PCT = (0, 50, 100)
BROKERAGE_SCENARIOS = (20.0, 10.0)  # ₹20 primary; ₹10 legacy tariff sensitivity
MIN_OPEN_INTEREST = 100


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


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


def as_ist(value: Any) -> pd.Timestamp:
    stamp = pd.Timestamp(value)
    if stamp.tzinfo is None:
        return stamp.tz_localize(TZ)
    return stamp.tz_convert(TZ)


def valid_ohlc(bar: dict[str, Any]) -> bool:
    try:
        o, h, l, c = (float(bar[k]) for k in ("open", "high", "low", "close"))
    except (TypeError, ValueError, KeyError):
        return False
    return (
        all(math.isfinite(x) and x > 0 for x in (o, h, l, c))
        and l <= min(o, c)
        and h >= max(o, c)
        and h >= l
    )


def range_proxy_pct(bar: dict[str, Any]) -> float | None:
    if not valid_ohlc(bar):
        return None
    o, h, l = float(bar["open"]), float(bar["high"]), float(bar["low"])
    return (h - l) / o * 100.0


def adverse_open_fill(open_price: float, action: str, slip_rupees: float) -> float:
    p, slip = float(open_price), float(slip_rupees)
    if not math.isfinite(p) or p <= 0 or not math.isfinite(slip) or slip < 0:
        raise ValueError("Fill price must be positive finite and slippage non-negative")
    action = action.lower()
    if action == "buy":
        return p + slip
    if action == "sell":
        return max(0.0, p - slip)
    raise ValueError(f"Unknown action {action!r}")


def leg_gate(
    leg: dict[str, Any],
    min_oi: float = MIN_OPEN_INTEREST,
    max_range_pct: float | None = None,
) -> tuple[bool, str, dict[str, Any]]:
    """Require exact matching entry/exit bars and strictly prior OI; never impute."""
    try:
        entry_ts = as_ist(leg["entry_ts"])
        exit_ts = as_ist(leg["exit_ts"])
        entry_bar, exit_bar = leg["entry_bar"], leg["exit_bar"]
    except Exception:
        return False, "MISSING_TIMESTAMP_OR_BAR", {}
    try:
        if as_ist(entry_bar["timestamp"]) != entry_ts:
            return False, "ENTRY_TIMESTAMP_MISMATCH", {}
        if as_ist(exit_bar["timestamp"]) != exit_ts:
            return False, "EXIT_TIMESTAMP_MISMATCH", {}
    except Exception:
        return False, "MISSING_BAR_TIMESTAMP", {}
    if not valid_ohlc(entry_bar):
        return False, "INVALID_ENTRY_OHLC", {}
    if not valid_ohlc(exit_bar):
        return False, "INVALID_EXIT_OHLC", {}
    try:
        prior_ts = as_ist(leg["prior_oi_ts"])
        prior_oi = float(leg["prior_oi"])
    except Exception:
        return False, "MISSING_PRIOR_OI", {}
    if prior_ts != entry_ts - pd.Timedelta(minutes=1):
        return False, "PRIOR_OI_TIMESTAMP_NOT_EXACTLY_ONE_MINUTE_BEFORE_ENTRY", {
            "prior_oi_ts": prior_ts.isoformat(),
            "expected_prior_oi_ts": (entry_ts - pd.Timedelta(minutes=1)).isoformat(),
        }
    if not math.isfinite(prior_oi) or prior_oi < min_oi:
        return False, "PRIOR_OI_BELOW_THRESHOLD_OR_MISSING", {
            "prior_oi": prior_oi if math.isfinite(prior_oi) else None,
            "min_oi": min_oi,
        }
    proxy = range_proxy_pct(entry_bar)
    if max_range_pct is not None and (proxy is None or proxy > float(max_range_pct) + 1e-12):
        return False, "ENTRY_OHLC_RANGE_PROXY_ABOVE_LIMIT", {
            "entry_ohlc_range_proxy_pct": proxy,
            "max_range_proxy_pct": float(max_range_pct),
        }
    return True, "PASS", {
        "entry_ts": entry_ts.isoformat(),
        "exit_ts": exit_ts.isoformat(),
        "prior_oi_ts": prior_ts.isoformat(),
        "prior_oi": prior_oi,
        "entry_ohlc_range_proxy_pct": proxy,
    }


def calculate_fill_and_cost_scenarios(
    legs: list[dict[str, Any]],
    lot_size: int,
    reference_lots_per_leg: int = 1,
    max_range_proxy_pct: float | None = None,
    brokerage_scenarios: tuple[float, ...] = BROKERAGE_SCENARIOS,
    slippage_stresses_pct: tuple[int, ...] = SLIPPAGE_STRESSES_PCT,
    fee_module=None,
) -> dict[str, Any]:
    """Replay already-resolved exact leg quotes; blocked trades have no P&L."""
    if not legs:
        return {"status": "BLOCKED_NO_LEGS", "reason": "No resolved legs", "scenarios": {}}
    if int(lot_size) <= 0 or int(reference_lots_per_leg) <= 0:
        return {"status": "BLOCKED_INVALID_POSITION_SIZE", "reason": "lot_size and lots must be positive", "scenarios": {}}
    entry_times, exit_times = set(), set()
    leg_diag = []
    for leg in legs:
        okay, reason, diag = leg_gate(leg, MIN_OPEN_INTEREST, max_range_proxy_pct)
        leg_diag.append({"leg_id": leg.get("leg_id"), "status": reason, **diag})
        if not okay:
            return {
                "status": "BLOCKED_LEG_ELIGIBILITY",
                "reason": reason,
                "leg_diagnostics": leg_diag,
                "scenarios": {},
                "pnl_computed": False,
            }
        entry_times.add(as_ist(leg["entry_ts"]).isoformat())
        exit_times.add(as_ist(leg["exit_ts"]).isoformat())
        try:
            q = int(leg["quantity"])
        except Exception:
            return {"status": "BLOCKED_INVALID_LEG_QUANTITY", "reason": "Each leg quantity must be a nonzero signed integer", "scenarios": {}, "pnl_computed": False}
        if q == 0 or float(leg["quantity"]) != q:
            return {"status": "BLOCKED_INVALID_LEG_QUANTITY", "reason": "Each leg quantity must be a nonzero signed integer", "scenarios": {}, "pnl_computed": False}
    if len(entry_times) != 1:
        return {"status": "BLOCKED_NON_SYNCHRONIZED_ENTRY", "reason": "All leg entries must share one exact timestamp", "leg_diagnostics": leg_diag, "scenarios": {}, "pnl_computed": False}
    if len(exit_times) != 1:
        return {"status": "BLOCKED_NON_SYNCHRONIZED_EXIT", "reason": "All legs must exit at one exact timestamp", "leg_diagnostics": leg_diag, "scenarios": {}, "pnl_computed": False}

    if fee_module is None:
        fee_module = load_phase43()
    entry_ts = as_ist(next(iter(entry_times)))
    exit_ts = as_ist(next(iter(exit_times)))
    lot = int(lot_size)
    lots = int(reference_lots_per_leg)
    raw_gross = 0.0
    resolved = []
    for leg in legs:
        q = int(leg["quantity"]) * lots
        entry_open = float(leg["entry_bar"]["open"])
        exit_open = float(leg["exit_bar"]["open"])
        raw_gross += q * (exit_open - entry_open) * lot
        entry_action = "buy" if q > 0 else "sell"
        exit_action = "sell" if q > 0 else "buy"
        resolved.append({
            "leg_id": str(leg.get("leg_id", "LEG")),
            "signed_quantity": q,
            "abs_quantity": abs(q),
            "entry_open": entry_open,
            "exit_open": exit_open,
            "entry_action": entry_action,
            "exit_action": exit_action,
        })

    scenarios = {}
    for stress_pct in slippage_stresses_pct:
        if stress_pct not in SLIPPAGE_STRESSES_PCT:
            raise ValueError(f"Unregistered slippage stress {stress_pct}")
        slip = BASE_SLIPPAGE_RUPEES * (1.0 + stress_pct / 100.0)
        fills, order_records = [], []
        pnl_after_slippage = 0.0
        for leg, item in zip(legs, resolved):
            entry_fill = adverse_open_fill(item["entry_open"], item["entry_action"], slip)
            exit_fill = adverse_open_fill(item["exit_open"], item["exit_action"], slip)
            pnl_after_slippage += (
                item["signed_quantity"] * (exit_fill - entry_fill) * lot
            )
            entry_record = {
                "leg_id": item["leg_id"], "time": entry_ts, "side": item["entry_action"],
                "price": entry_fill, "lots": item["abs_quantity"],
            }
            exit_record = {
                "leg_id": item["leg_id"], "time": exit_ts, "side": item["exit_action"],
                "price": exit_fill, "lots": item["abs_quantity"],
            }
            order_records.extend([entry_record, exit_record])
            fills.append({
                "leg_id": item["leg_id"],
                "quantity": item["signed_quantity"],
                "entry_action": item["entry_action"],
                "entry_open": item["entry_open"],
                "entry_fill": entry_fill,
                "exit_action": item["exit_action"],
                "exit_open": item["exit_open"],
                "exit_fill": exit_fill,
                "gross_pnl_before_slippage": item["signed_quantity"] * (item["exit_open"] - item["entry_open"]) * lot,
                "pnl_after_slippage_before_fees": item["signed_quantity"] * (exit_fill - entry_fill) * lot,
            })
        slippage_cost = raw_gross - pnl_after_slippage
        for brokerage in brokerage_scenarios:
            key = f"BROKERAGE_{int(brokerage)}_SLIPPAGE_{stress_pct}PCT"
            costs = calculate_fees(order_records, lot, brokerage, fee_module)
            net = pnl_after_slippage - costs["total_charges"]
            scenarios[key] = {
                "brokerage_per_order_inr": float(brokerage),
                "slippage_stress_pct": int(stress_pct),
                "slippage_per_leg_per_fill_inr": slip,
                "gross_pnl_before_slippage_inr": round(raw_gross, 8),
                "slippage_cost_inr": round(slippage_cost, 8),
                "pnl_after_slippage_before_fees_inr": round(pnl_after_slippage, 8),
                **{k: round(v, 8) for k, v in costs.items()},
                "net_pnl_inr": round(net, 8),
                "return_on_600000_capital_pct": round(net / 600000.0 * 100.0, 8),
                "fill_orders": len(order_records),
            }
    return {
        "status": "REPLAY_PRIMITIVES_PASS_NO_PROMOTION",
        "pnl_computed": True,
        "entry_ts": entry_ts.isoformat(),
        "exit_ts": exit_ts.isoformat(),
        "lot_size": lot,
        "reference_lots_per_leg": lots,
        "leg_count": len(legs),
        "raw_gross_pnl_before_slippage_inr": round(raw_gross, 8),
        "leg_fills": fills,
        "leg_diagnostics": leg_diag,
        "scenarios": scenarios,
        "limitations": [
            "Caller must resolve leg types/strikes/expiries from point-in-time inputs before this function is used.",
            "The entry OHLC range is only a liquidity proxy, not observed bid/ask spread.",
            "Open prices are OHLC simulation references, not proof of tick-level execution.",
            "The fee schedule is delegated to the accepted Phase43 function; statutory schedule and the actual Paytm Money account tariff remain subject to source/account audit.",
            "This core does not calculate max-profit paths, rebalances, assignment, margin or tail-risk controls.",
        ],
    }


def calculate_fees(order_records: list[dict[str, Any]], lot_size: int, brokerage_per_order: float, fee_module=None) -> dict[str, float]:
    if fee_module is None:
        fee_module = load_phase43()
    brokerage = float(brokerage_per_order) * len(order_records)
    exchange = sebi = ipft = stt = stamp = 0.0
    for order in order_records:
        rate_stt, rate_txn, rate_sebi, rate_ipft, rate_stamp = fee_module.fee_rates(as_ist(order["time"]))
        turnover = float(order["price"]) * int(lot_size) * int(order["lots"])
        exchange += rate_txn * turnover
        sebi += rate_sebi * turnover
        ipft += rate_ipft * turnover
        if order["side"] == "sell":
            stt += rate_stt * turnover
        elif order["side"] == "buy":
            stamp += rate_stamp * turnover
        else:
            raise ValueError(f"Unknown order side {order['side']!r}")
    gst = 0.18 * (brokerage + exchange + sebi + ipft)
    return {
        "brokerage_inr": brokerage,
        "exchange_transaction_charge_inr": exchange,
        "sebi_charge_inr": sebi,
        "ipft_charge_inr": ipft,
        "stt_inr": stt,
        "stamp_duty_inr": stamp,
        "gst_inr": gst,
        "total_charges": brokerage + exchange + sebi + ipft + stt + stamp + gst,
    }


def fixture_leg(leg_id: str, quantity: int, entry_open: float, exit_open: float,
                entry_ts: str, exit_ts: str, prior_oi: float = 200,
                entry_high: float | None = None, entry_low: float | None = None) -> dict[str, Any]:
    return {
        "leg_id": leg_id,
        "quantity": quantity,
        "prior_oi_ts": (as_ist(entry_ts) - pd.Timedelta(minutes=1)).isoformat(),
        "prior_oi": prior_oi,
        "entry_ts": entry_ts,
        "exit_ts": exit_ts,
        "entry_bar": {
            "timestamp": entry_ts, "open": entry_open,
            "high": entry_high if entry_high is not None else entry_open * 1.01,
            "low": entry_low if entry_low is not None else entry_open * 0.99,
            "close": entry_open,
        },
        "exit_bar": {
            "timestamp": exit_ts, "open": exit_open,
            "high": exit_open * 1.01, "low": exit_open * 0.99,
            "close": exit_open,
        },
    }


def self_test() -> dict[str, Any]:
    phase43 = load_phase43()
    entry_ts = "2026-04-15T09:45:00+05:30"
    exit_ts = "2026-04-15T15:15:00+05:30"

    # Hand-check: long option open 100 -> 125; one lot = 65 units.
    single = [fixture_leg("LONG_CE", +1, 100.0, 125.0, entry_ts, exit_ts)]
    one = calculate_fill_and_cost_scenarios(single, lot_size=65, max_range_proxy_pct=2.0, fee_module=phase43)
    assert one["status"] == "REPLAY_PRIMITIVES_PASS_NO_PROMOTION", one
    assert abs(one["raw_gross_pnl_before_slippage_inr"] - 1625.0) < 1e-8
    assert abs(one["scenarios"]["BROKERAGE_20_SLIPPAGE_0PCT"]["slippage_cost_inr"] - 6.5) < 1e-8
    assert abs(one["scenarios"]["BROKERAGE_20_SLIPPAGE_50PCT"]["slippage_cost_inr"] - 9.75) < 1e-8
    assert abs(one["scenarios"]["BROKERAGE_20_SLIPPAGE_100PCT"]["slippage_cost_inr"] - 13.0) < 1e-8
    assert abs(one["scenarios"]["BROKERAGE_20_SLIPPAGE_0PCT"]["pnl_after_slippage_before_fees_inr"] - 1618.5) < 1e-8

    # Hand-check a two-leg short call vertical: (100-25) + (4-30) = 49 points.
    # 49 * 65 = ₹3,185 gross; two legs x two adverse fills x ₹0.05 x 65 = ₹13 slippage.
    spread = [
        fixture_leg("SHORT_CE", -1, 100.0, 25.0, entry_ts, exit_ts),
        fixture_leg("LONG_CE_WING", +1, 30.0, 4.0, entry_ts, exit_ts,
                    entry_high=30.3, entry_low=29.7),
    ]
    two = calculate_fill_and_cost_scenarios(spread, lot_size=65, max_range_proxy_pct=2.0, fee_module=phase43)
    assert two["status"] == "REPLAY_PRIMITIVES_PASS_NO_PROMOTION", two
    assert abs(two["raw_gross_pnl_before_slippage_inr"] - 3185.0) < 1e-8
    assert abs(two["scenarios"]["BROKERAGE_20_SLIPPAGE_0PCT"]["slippage_cost_inr"] - 13.0) < 1e-8
    assert abs(two["scenarios"]["BROKERAGE_20_SLIPPAGE_0PCT"]["pnl_after_slippage_before_fees_inr"] - 3172.0) < 1e-8
    assert two["scenarios"]["BROKERAGE_20_SLIPPAGE_0PCT"]["fill_orders"] == 4
    assert two["scenarios"]["BROKERAGE_20_SLIPPAGE_0PCT"]["brokerage_inr"] == 80.0

    # Fee parity against Phase43 for quantity 1: same two fill orders, effective date rates.
    scen = one["scenarios"]["BROKERAGE_20_SLIPPAGE_0PCT"]
    bfill = one["leg_fills"][0]
    phase43_orders = [
        (as_ist(entry_ts), "buy", bfill["entry_fill"]),
        (as_ist(exit_ts), "sell", bfill["exit_fill"]),
    ]
    reference_cost = phase43.charges(phase43_orders, 65, cost_mult=1.0, brokerage_per_order=20.0)
    assert abs(scen["total_charges"] - reference_cost) < 1e-8, (scen["total_charges"], reference_cost)

    # Fail closed on stale/missing OI, timestamp mismatch, and OHLC-range gate.
    bad_oi = [fixture_leg("NO_OI", +1, 100.0, 125.0, entry_ts, exit_ts, prior_oi=99)]
    assert calculate_fill_and_cost_scenarios(bad_oi, 65)["status"] == "BLOCKED_LEG_ELIGIBILITY"
    missing = [fixture_leg("NO_PRIOR", +1, 100.0, 125.0, entry_ts, exit_ts, prior_oi=float("nan"))]
    assert calculate_fill_and_cost_scenarios(missing, 65)["status"] == "BLOCKED_LEG_ELIGIBILITY"
    mismatch = [fixture_leg("WRONG_TS", +1, 100.0, 125.0, entry_ts, exit_ts)]
    mismatch[0]["entry_bar"]["timestamp"] = "2026-04-15T09:46:00+05:30"
    assert calculate_fill_and_cost_scenarios(mismatch, 65)["reason"] == "ENTRY_TIMESTAMP_MISMATCH"
    wide = [fixture_leg("WIDE_RANGE", +1, 100.0, 125.0, entry_ts, exit_ts, entry_high=103.0, entry_low=97.0)]
    assert calculate_fill_and_cost_scenarios(wide, 65, max_range_proxy_pct=2.0)["reason"] == "ENTRY_OHLC_RANGE_PROXY_ABOVE_LIMIT"

    # Flat brokerage is one charge per physical leg-order, not per lot.
    one_two_lots = calculate_fill_and_cost_scenarios(single, lot_size=65, reference_lots_per_leg=2,
                                                      max_range_proxy_pct=2.0, fee_module=phase43)
    assert one_two_lots["scenarios"]["BROKERAGE_20_SLIPPAGE_0PCT"]["brokerage_inr"] == 40.0
    assert abs(one_two_lots["raw_gross_pnl_before_slippage_inr"] - 3250.0) < 1e-8

    return {
        "status": "PASS",
        "tests": [
            "single-long gross/slippage hand calculation",
            "two-leg vertical gross/slippage hand calculation",
            "date-aware statutory-fee parity against Phase43 at quantity one",
            "₹20 primary/₹10 sensitivity brokerage scenarios",
            "slippage-only 0/50/100 stress semantics",
            "flat brokerage is per order, not per lot",
            "strict one-minute prior OI eligibility",
            "exact entry/exit timestamp matching",
            "fail-closed missing OI and invalid quote handling",
            "OHLC-range liquidity proxy gate",
        ],
        "single_long_gross_rupees": 1625.0,
        "single_long_slippage_cost_base_rupees": one["scenarios"]["BROKERAGE_20_SLIPPAGE_0PCT"]["slippage_cost_inr"],
        "vertical_gross_rupees": 3185.0,
        "vertical_slippage_cost_base_rupees": two["scenarios"]["BROKERAGE_20_SLIPPAGE_0PCT"]["slippage_cost_inr"],
        "fee_parity_phase43_rupees": reference_cost,
        "phase43_fee_helper_sha256": sha256_file(PHASE43_SCRIPT),
        "engine_sha256": sha256_file(Path(__file__)),
        "protocol_sha256": sha256_file(PROTOCOL),
        "note": "Unit tests only. No historical market event was replayed and no strategy is promoted.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not args.self_test:
        raise SystemExit("This module is test-only; production replay integration requires a later explicit gate.")
    report = self_test()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
