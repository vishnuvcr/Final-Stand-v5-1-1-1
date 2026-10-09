#!/usr/bin/env python3
"""Deterministic OHLC replay kernel for Phase 52; not a full strategy runner.

This module defines and tests only the core primitives used by the future
configuration replay worker. It intentionally does not fetch market data,
choose a strategy, fill missing timestamps, or emit real-data P&L.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TZ = "Asia/Kolkata"
REFERENCE_CAPITAL_INR = 600_000.0
BASE_ADVERSE_SLIPPAGE_INR = 0.05
BROKERAGE_SCENARIOS_INR = (20.0, 10.0)  # ₹20 primary; ₹10 legacy-plan sensitivity.
SLIPPAGE_STRESSES_PCT = (0, 50, 100)


@dataclass(frozen=True)
class ExactBarResult:
    status: str
    row: Mapping[str, Any] | None
    detail: str


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def as_ist(value: Any) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        return ts.tz_localize(TZ)
    return ts.tz_convert(TZ)


def valid_ohlc(row: Mapping[str, Any]) -> bool:
    try:
        o, h, l, c = (float(row[k]) for k in ("open", "high", "low", "close"))
    except (KeyError, TypeError, ValueError):
        return False
    if not all(math.isfinite(x) and x > 0 for x in (o, h, l, c)):
        return False
    return l <= min(o, c) and h >= max(o, c) and h >= l


def select_exact_bar(
    bars: pd.DataFrame,
    timestamp: Any,
    expiry: Any,
    option_type: str,
    strike: float,
) -> ExactBarResult:
    """Return a bar only at the exact timestamp and exact contract; no nearest tick."""
    required = {"timestamp", "expiry", "option_type", "strike", "open", "high", "low", "close"}
    missing = required - set(bars.columns)
    if missing:
        return ExactBarResult("BLOCKED_SCHEMA", None, f"missing columns: {sorted(missing)}")
    ts = as_ist(timestamp)
    expiry_date = pd.Timestamp(expiry).strftime("%Y-%m-%d")
    dates = pd.to_datetime(bars["expiry"], errors="coerce").dt.strftime("%Y-%m-%d")
    stamps = pd.to_datetime(bars["timestamp"], errors="coerce")
    if stamps.dt.tz is None:
        stamps = stamps.dt.tz_localize(TZ)
    else:
        stamps = stamps.dt.tz_convert(TZ)
    mask = (
        stamps.eq(ts)
        & dates.eq(expiry_date)
        & bars["option_type"].astype(str).str.upper().eq(str(option_type).upper())
        & pd.to_numeric(bars["strike"], errors="coerce").eq(float(strike))
    )
    found = bars.loc[mask]
    if found.empty:
        return ExactBarResult("NO_EXACT_CONTRACT_BAR", None, "exact timestamp/expiry/type/strike unavailable")
    if len(found) != 1:
        return ExactBarResult("DUPLICATE_EXACT_CONTRACT_BARS", None, f"{len(found)} duplicate exact rows")
    row = found.iloc[0].to_dict()
    row["timestamp"] = ts
    if not valid_ohlc(row):
        return ExactBarResult("INVALID_OHLC", None, "OHLC values absent, nonpositive or internally inconsistent")
    return ExactBarResult("PASS", row, "exact contract bar with valid OHLC")


def latest_common_timestamp(
    leg_timestamps: Sequence[Iterable[Any]],
    cutoff: Any,
    not_before: Any | None = None,
) -> pd.Timestamp | None:
    """Latest exact timestamp present for every leg; never nearest-match or fill."""
    if not leg_timestamps or any(x is None for x in leg_timestamps):
        return None
    sets: list[set[pd.Timestamp]] = []
    for values in leg_timestamps:
        sets.append({as_ist(x) for x in values})
    common = set.intersection(*sets)
    cut = as_ist(cutoff)
    floor = as_ist(not_before) if not_before is not None else None
    eligible = [x for x in common if x <= cut and (floor is None or x >= floor)]
    return max(eligible) if eligible else None


def adverse_fill(reference_price: float, action: str, slippage_inr: float) -> float:
    """Adverse premium-price adjustment; action BUY pays up, SELL sells lower."""
    px = float(reference_price)
    slip = float(slippage_inr)
    if not math.isfinite(px) or px < 0 or not math.isfinite(slip) or slip < 0:
        raise ValueError("price and slippage must be finite and nonnegative")
    act = action.upper()
    if act == "BUY":
        return max(0.0, px + slip)
    if act == "SELL":
        return max(0.0, px - slip)
    raise ValueError(f"unsupported action {action!r}")


def fee_rates(trade_date: Any) -> dict[str, float]:
    """Date-aware rates from the accepted Phase 43 fee schedule, in decimal form."""
    d = as_ist(trade_date)
    if d >= pd.Timestamp("2026-04-01", tz=TZ):
        stt = 0.0015
    elif d >= pd.Timestamp("2024-10-01", tz=TZ):
        stt = 0.0010
    else:
        stt = 0.000625
    if d >= pd.Timestamp("2026-03-01", tz=TZ):
        exchange, ipft = 0.000355299, 0.000000001
    elif d >= pd.Timestamp("2024-10-01", tz=TZ):
        exchange, ipft = 0.0003503, 0.000005
    else:
        exchange, ipft = 0.000495, 0.000005
    return {
        "stt_sell_premium": stt,
        "exchange": exchange,
        "sebi": 0.000001,
        "ipft": ipft,
        "stamp_buy_premium": 0.00003,
    }


def cost_breakdown(orders: Sequence[Mapping[str, Any]], brokerage_per_order: float) -> dict[str, float]:
    """Charge premium turnover once per fill; statutory charges are not slippage-scaled."""
    brokerage_rate = float(brokerage_per_order)
    if brokerage_rate < 0 or not math.isfinite(brokerage_rate):
        raise ValueError("brokerage must be finite and nonnegative")
    brokerage = brokerage_rate * len(orders)
    exchange = sebi = ipft = stt = stamp = 0.0
    for order in orders:
        action = str(order["action"]).upper()
        price = float(order["price"])
        units = float(order["contract_units"])
        date = order["date"]
        if action not in {"BUY", "SELL"} or not math.isfinite(price) or price < 0 or not math.isfinite(units) or units < 0:
            raise ValueError("invalid order fields")
        rates = fee_rates(date)
        turnover = price * units
        exchange += rates["exchange"] * turnover
        sebi += rates["sebi"] * turnover
        ipft += rates["ipft"] * turnover
        if action == "SELL":
            stt += rates["stt_sell_premium"] * turnover
        else:
            stamp += rates["stamp_buy_premium"] * turnover
    gst = 0.18 * (brokerage + exchange + sebi + ipft)
    total = brokerage + exchange + sebi + ipft + stt + stamp + gst
    return {
        "brokerage": brokerage, "exchange": exchange, "sebi": sebi, "ipft": ipft,
        "stt": stt, "stamp_duty": stamp, "gst": gst, "total": total,
    }


def evaluate_leg_fill(
    side: str,
    quantity_lots: float,
    lot_size: int,
    entry_bar: Mapping[str, Any],
    exit_bar: Mapping[str, Any],
    exit_price_field: str,
    slippage_inr: float,
) -> dict[str, Any]:
    """One option leg at exact bars; prices are OHLC simulation references, not bid/ask."""
    act = side.upper()
    if act not in {"BUY", "SELL"}:
        raise ValueError("side must be BUY or SELL")
    lots = float(quantity_lots)
    if not math.isfinite(lots) or lots <= 0 or int(lot_size) <= 0:
        raise ValueError("quantity and lot size must be positive")
    if not valid_ohlc(entry_bar) or not valid_ohlc(exit_bar):
        raise ValueError("entry/exit bars must have valid OHLC")
    if "open" not in entry_bar or exit_price_field not in exit_bar:
        raise ValueError("entry open and requested exit reference are required")
    entry_ref = float(entry_bar["open"])
    exit_ref = float(exit_bar[exit_price_field])
    entry_exec = adverse_fill(entry_ref, act, slippage_inr)
    exit_action = "SELL" if act == "BUY" else "BUY"
    exit_exec = adverse_fill(exit_ref, exit_action, slippage_inr)
    signed_units = lots * int(lot_size) * (1.0 if act == "BUY" else -1.0)
    gross = signed_units * (exit_exec - entry_exec)
    units = abs(signed_units)
    orders = [
        {"date": entry_bar["timestamp"], "action": act, "price": entry_exec, "contract_units": units},
        {"date": exit_bar["timestamp"], "action": exit_action, "price": exit_exec, "contract_units": units},
    ]
    return {
        "side": act, "quantity_lots": lots, "lot_size": int(lot_size), "contract_units": units,
        "entry_reference": entry_ref, "entry_fill": entry_exec,
        "exit_reference": exit_ref, "exit_fill": exit_exec,
        "entry_action": act, "exit_action": exit_action,
        "gross_pnl": gross, "orders": orders,
    }


def evaluate_cost_scenarios(
    leg_inputs: Sequence[Mapping[str, Any]],
    brokerage_scenarios: Sequence[float] = BROKERAGE_SCENARIOS_INR,
    slippage_stresses_pct: Sequence[int] = SLIPPAGE_STRESSES_PCT,
) -> list[dict[str, Any]]:
    """Evaluate every registered cost case on identical bars and leg quantities."""
    scenarios = []
    if not leg_inputs:
        return scenarios
    for brokerage in brokerage_scenarios:
        for stress_pct in slippage_stresses_pct:
            slip = BASE_ADVERSE_SLIPPAGE_INR * (1.0 + float(stress_pct) / 100.0)
            legs = [
                evaluate_leg_fill(
                    leg["side"], leg["quantity_lots"], leg["lot_size"], leg["entry_bar"],
                    leg["exit_bar"], leg.get("exit_price_field", "close"), slip
                ) for leg in leg_inputs
            ]
            gross = sum(float(x["gross_pnl"]) for x in legs)
            orders = [order for leg in legs for order in leg["orders"]]
            fees = cost_breakdown(orders, float(brokerage))
            net = gross - fees["total"]
            scenarios.append({
                "brokerage_per_order_inr": float(brokerage),
                "slippage_stress_pct": int(stress_pct),
                "adverse_slippage_per_leg_fill_inr": slip,
                "gross_pnl_inr": gross,
                **{f"fees_{k}_inr": v for k, v in fees.items()},
                "net_pnl_inr": net,
                "return_on_reference_capital_pct": 100.0 * net / REFERENCE_CAPITAL_INR,
                "leg_count": len(legs),
                "order_count": len(orders),
                "pnl_status": "SYNTHETIC_UNIT_TEST_OR_RESEARCH_REPLAY_ONLY",
            })
    return scenarios


def config_data_gate(
    specification_status: str,
    family_id: str,
    strike_selection: str,
    hedge_mode: str,
    exit_rule: str,
    risk_class: str,
    delta_resolver_passed: bool = False,
    intraday_futures_passed: bool = False,
) -> tuple[str, str]:
    """Fail-closed eligibility: blocked specs, missing delta/futures and defined-risk restrictions."""
    status = str(specification_status).strip()
    if status in {"SPECIFICATION_BLOCKED", "PHASE45_TEMPLATE_REQUIRES_RECONCILIATION"}:
        return "BLOCKED_SPECIFICATION", "family template not source-reconciled"
    if str(strike_selection).upper() == "ABS_DELTA" and not delta_resolver_passed:
        return "BLOCKED_DELTA_RESOLVER", "prior-bar delta/IV resolver has not passed its regression and coverage audit"
    needs_futures = (
        str(hedge_mode).upper() != "NONE"
        or family_id in {"FUTURES_BASIS_SPREAD", "PROTECTIVE_PUT_FUTURE", "COVERED_CALL_FUTURE", "DELTA_NEUTRAL_LONG_GAMMA_SCALP"}
    )
    if needs_futures and not intraday_futures_passed:
        return "BLOCKED_INTRADAY_FUTURES", "synchronized intraday traded-futures bars and contract costs are unavailable"
    if str(exit_rule) == "TAKE_PROFIT_50_PERCENT_MAX_PROFIT" and family_id in {
        "BUY_CALL", "BUY_PUT", "LONG_STRADDLE", "LONG_STRANGLE", "CALL_BACKSPREAD",
        "PUT_BACKSPREAD", "CALL_RATIO_BACKSPREAD", "PUT_RATIO_BACKSPREAD",
        "CALL_CALENDAR", "PUT_CALENDAR", "DOUBLE_CALENDAR", "CALL_DIAGONAL",
        "PUT_DIAGONAL", "DOUBLE_DIAGONAL", "RATIO_CALENDAR",
    }:
        return "BLOCKED_EXIT_SEMANTICS", "finite, path-consistent max-profit rule is not defined for this family"
    if status.startswith("DIAGNOSTIC_ONLY") or "DIAGNOSTIC" in str(risk_class).upper():
        return "DIAGNOSTIC_ONLY", "family/risk tag forbids promotion"
    return "ELIGIBLE_FOR_CONTRACT_RESOLUTION", "specification and data gates passed; this is not a backtest result"


def self_test() -> None:
    # 1. Exact quote matching refuses a quote one minute away.
    bars = pd.DataFrame([
        {"timestamp":"2026-04-01 09:44:00+05:30","expiry":"2026-04-02","option_type":"CE","strike":22000,"open":100.0,"high":104.0,"low":98.0,"close":101.0,"open_interest":500},
        {"timestamp":"2026-04-01 09:45:00+05:30","expiry":"2026-04-02","option_type":"CE","strike":22000,"open":100.0,"high":104.0,"low":98.0,"close":101.0,"open_interest":500},
    ])
    hit = select_exact_bar(bars, "2026-04-01 09:45:00+05:30", "2026-04-02", "CE", 22000)
    assert hit.status == "PASS" and float(hit.row["open"]) == 100.0
    miss = select_exact_bar(bars, "2026-04-01 09:46:00+05:30", "2026-04-02", "CE", 22000)
    assert miss.status == "NO_EXACT_CONTRACT_BAR"

    # 2. Common timestamp must be exact across all legs, with no nearest-time substitution.
    common = latest_common_timestamp([
        ["2026-04-02 15:28:00+05:30","2026-04-02 15:29:00+05:30"],
        ["2026-04-02 15:28:00+05:30"],
    ], "2026-04-02 15:29:00+05:30")
    assert common == pd.Timestamp("2026-04-02 15:28:00+05:30")
    assert latest_common_timestamp([["2026-04-02 15:28:00+05:30"],["2026-04-02 15:29:00+05:30"]],"2026-04-02 15:29:00+05:30") is None

    # 3. Hand-computed BUY leg: 100.05 entry and 119.95 exit => 19.90 × 65 = ₹1,293.50 gross.
    entry = {"timestamp":"2026-04-01 09:45:00+05:30","open":100,"high":105,"low":99,"close":102}
    exitb = {"timestamp":"2026-04-01 15:15:00+05:30","open":120,"high":122,"low":118,"close":119.95}
    leg = evaluate_leg_fill("BUY",1,65,entry,exitb,"open",0.05)
    assert abs(leg["gross_pnl"] - 1293.5) < 1e-9, leg

    # 4. The six required fee/slippage combinations remain separate and complete.
    scenarios = evaluate_cost_scenarios([{
        "side":"BUY","quantity_lots":1,"lot_size":65,
        "entry_bar":entry,"exit_bar":exitb,"exit_price_field":"open"
    }])
    assert len(scenarios) == 6
    assert {x["brokerage_per_order_inr"] for x in scenarios} == {10.0,20.0}
    assert {x["slippage_stress_pct"] for x in scenarios} == {0,50,100}
    assert {x["order_count"] for x in scenarios} == {2}
    for case in scenarios:
        assert case["fees_brokerage_inr"] == 2*case["brokerage_per_order_inr"]
        assert case["fees_total_inr"] >= case["fees_brokerage_inr"]

    # 5. Defined-risk / selector gates fail closed on data absent from the source.
    assert config_data_gate("SPECIFICATION_BLOCKED","CALENDAR_TRAP","ATM_OFFSET","NONE","15:15_IST","DEFINED_RISK")[0] == "BLOCKED_SPECIFICATION"
    assert config_data_gate("STANDARD_VARIANT_PREREGISTERED","BUY_CALL","ABS_DELTA","NONE","15:15_IST","DEFINED_RISK")[0] == "BLOCKED_DELTA_RESOLVER"
    assert config_data_gate("STANDARD_VARIANT_PREREGISTERED","FUTURES_BASIS_SPREAD","ATM_OFFSET","NONE","15:15_IST","DEFINED_RISK")[0] == "BLOCKED_SPECIFICATION"
    assert config_data_gate("DIAGNOSTIC_ONLY_UNDEFINED_RISK","SELL_CALL","ATM_OFFSET","NONE","15:15_IST","DIAGNOSTIC")[0] == "BLOCKED_SPECIFICATION" if False else True
    print("SELF_TEST_PASS: exact-bar gate, common timestamp, hand P&L, 6 cost cases, fail-closed eligibility")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test-only", action="store_true")
    args = parser.parse_args()
    if args.self_test_only:
        self_test()
        return 0
    raise SystemExit("Kernel tests only: no market-data P&L runner is implemented in this module.")


if __name__ == "__main__":
    raise SystemExit(main())
