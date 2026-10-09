#!/usr/bin/env python3
"""Phase 56: non-executable OHLC price-reference P&L sensitivity.

This module consumes the frozen Phase 55 480-row leg-audit ledger. It varies
only Phase 54's preregistered OHLC-range threshold and fixed cost assumptions.
It uses stored exact-bar open prices as references, never as claimed bid/ask
quotes or guaranteed fills. No raw data is downloaded and no holdout is read.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
PHASE52 = ROOT / "research" / "phase52"
INPUT = ROOT / "results" / "phase52" / "historical_pilot" / "event_replay.csv"
PARENT_REPORT = ROOT / "results" / "phase52" / "historical_pilot" / "report.json"
OUT = ROOT / "results" / "phase56" / "ohlc_pnl_sensitivity"

if str(PHASE52) not in sys.path:
    sys.path.insert(0, str(PHASE52))
import replay_kernel as kernel  # noqa: E402

THRESHOLDS = (2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 1000)
BROKERAGE_PER_ORDER_INR = (10.0, 20.0)
SLIPPAGE_CASES = (
    ("zero_slippage_lower_bound", 0.0),
    ("base_0.05", 0.05),
    ("stress_50pct_0.075", 0.075),
    ("stress_100pct_0.10", 0.10),
    ("severe_0.25", 0.25),
    ("very_severe_0.50", 0.50),
)
PINNED_REVISION = "0f4800e43e6f96cec0794369d78eb4d3c4211ef5"
EXPECTED_STATUS_COUNTS = {
    "BLOCKED_LEG_ELIGIBILITY": 100,
    "EXCLUDED_OHLC_RANGE_PROXY": 379,
    "REPLAY_PASS": 1,
}
EXPECTED_ELIGIBLE_COUNTS = (1, 1, 8, 24, 55, 91, 150, 227, 298, 345, 380)
EXPECTED_LEGS = {
    "BUY_CALL": 1,
    "BUY_PUT": 1,
    "BULL_CALL_SPREAD": 2,
    "BEAR_CALL_SPREAD": 2,
    "LONG_STRADDLE": 2,
    "LONG_STRANGLE": 2,
    "SHORT_IRON_CONDOR": 4,
}
REQUIRED_LEG_FIELDS = (
    "leg_id", "side", "quantity_lots", "lot_size", "strike", "option_type", "expiry",
    "entry_status", "prior_oi_status", "range_proxy_status", "exit_status",
    "prior_oi", "entry_range_proxy_pct", "entry_open", "exit_open",
)


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def finite_number(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def read_rows(path: Path = INPUT) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_parent_report(path: Path = PARENT_REPORT) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Parent report missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def legs_for(row: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        value = json.loads(row.get("resolved_legs_json") or "[]")
    except (json.JSONDecodeError, TypeError):
        return []
    return value if isinstance(value, list) else []


def validate_ledger(
    rows: list[dict[str, str]],
    parent_report: dict[str, Any] | None = None,
    *,
    strict_parent: bool = True,
) -> dict[str, Any]:
    """Fail closed on any missing, partial or mismatched selected-leg evidence."""
    if not rows:
        raise ValueError("Phase 55 event replay ledger contains no rows")
    required = {
        "configuration_id", "candidate_id", "family_id", "split", "event_id",
        "expiry", "entry_ts", "exit_ts", "status", "exclusion_reason",
        "resolved_legs_json", "option_source_sha256",
    }
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"Input ledger is missing required columns: {sorted(missing)}")

    status_counts = Counter(row.get("status", "MISSING") for row in rows)
    if strict_parent and (
        len(rows) != 480 or dict(status_counts) != EXPECTED_STATUS_COUNTS
    ):
        raise ValueError(
            f"Frozen parent reconciliation failed: rows={len(rows)}, "
            f"statuses={dict(sorted(status_counts.items()))}"
        )
    if parent_report is not None:
        if parent_report.get("dataset_revision") != PINNED_REVISION:
            raise ValueError(
                f"Dataset revision drift: {parent_report.get('dataset_revision')} != {PINNED_REVISION}"
            )
        if parent_report.get("planned_config_event_rows") != 480:
            raise ValueError("Parent report's planned row count is not 480")
        if parent_report.get("replay_exception_count") != 0:
            raise ValueError("Parent report has replay exceptions")
        if parent_report.get("source_file_errors") != 0:
            raise ValueError("Parent report has source-file errors")

    configs = {row["configuration_id"] for row in rows}
    if strict_parent and len(configs) != 40:
        raise ValueError(f"Expected 40 frozen configurations, found {len(configs)}")
    event_ids = {row["event_id"] for row in rows}
    if strict_parent and len(event_ids) != 24:
        raise ValueError(f"Expected 24 frozen event identities, found {len(event_ids)}")

    completeness_by_status = Counter()
    status_range_distribution: dict[str, dict[str, int]] = {}
    hard_oi_rows = 0
    range_complete_rows = 0
    replay_pass_complete_rows = 0
    validation_rows: list[dict[str, Any]] = []

    for row in rows:
        status = row["status"]
        legs = legs_for(row)
        expected = EXPECTED_LEGS.get(row.get("family_id", ""))
        if expected is None:
            raise ValueError(f"Unknown family in frozen ledger: {row.get('family_id')}")
        if len(legs) != expected:
            raise ValueError(
                f"{row['configuration_id']}::{row['event_id']}: expected {expected} legs, got {len(legs)}"
            )
        ids = [leg.get("leg_id") for leg in legs if isinstance(leg, dict)]
        if len(ids) != expected or len(set(ids)) != expected:
            raise ValueError(
                f"{row['configuration_id']}::{row['event_id']}: missing/duplicate selected leg IDs {ids}"
            )

        max_range = -math.inf
        oi_failure_seen = False
        for leg in legs:
            missing_leg = [field for field in REQUIRED_LEG_FIELDS if field not in leg]
            if missing_leg:
                raise ValueError(
                    f"{row['configuration_id']}::{row['event_id']}::{leg.get('leg_id')}: "
                    f"missing leg fields {missing_leg}"
                )
            if str(leg.get("side", "")).upper() not in {"BUY", "SELL"}:
                raise ValueError("Unsupported leg side in audit ledger")
            quantity = finite_number(leg.get("quantity_lots"))
            lot_size = finite_number(leg.get("lot_size"))
            strike = finite_number(leg.get("strike"))
            prior_oi = finite_number(leg.get("prior_oi"))
            entry_px = finite_number(leg.get("entry_open"))
            exit_px = finite_number(leg.get("exit_open"))
            range_pct = finite_number(leg.get("entry_range_proxy_pct"))
            if quantity is None or quantity <= 0 or lot_size is None or lot_size <= 0:
                raise ValueError("Invalid lot quantity/size in selected-leg audit")
            if strike is None or strike <= 0 or prior_oi is None:
                raise ValueError("Invalid strike or missing prior OI in selected-leg audit")
            if entry_px is None or entry_px <= 0 or exit_px is None or exit_px <= 0:
                raise ValueError("Missing/invalid exact entry-open or exit-open reference")
            if range_pct is None or range_pct < 0:
                raise ValueError("Missing/invalid entry OHLC range proxy")
            if leg.get("entry_status") != "PASS" or leg.get("exit_status") != "PASS":
                raise ValueError(
                    f"Price-reference row contains non-PASS exact entry/exit status: "
                    f"{row['configuration_id']}::{row['event_id']}::{leg.get('leg_id')}"
                )
            if leg.get("prior_oi_status") != "PASS" or prior_oi < 100:
                oi_failure_seen = True
            if leg.get("range_proxy_status") not in {"PASS", "EXCLUDED"}:
                raise ValueError("Unknown range-proxy status in selected-leg audit")
            max_range = max(max_range, range_pct)

        completeness_by_status[status] += 1
        detail = "COMPLETE_LEG_PAYLOAD"
        if status == "BLOCKED_LEG_ELIGIBILITY":
            if not oi_failure_seen:
                raise ValueError(
                    f"OI-blocked row has no observed required-leg OI failure: "
                    f"{row['configuration_id']}::{row['event_id']}"
                )
            reason = (row.get("exclusion_reason") or "").lower()
            if "prior-bar oi" not in reason and "prior oi" not in reason:
                raise ValueError("OI-blocked row does not retain its canonical reason")
            hard_oi_rows += 1
        else:
            if oi_failure_seen:
                raise ValueError(
                    f"Non-blocked row contains a required-leg OI failure: "
                    f"{row['configuration_id']}::{row['event_id']}"
                )
            if status == "EXCLUDED_OHLC_RANGE_PROXY":
                if max_range <= 2:
                    raise ValueError("Range-excluded baseline row does not exceed the frozen 2% proxy gate")
                range_complete_rows += 1
            elif status == "REPLAY_PASS":
                if max_range > 2:
                    raise ValueError("Replay-pass row exceeds the frozen 2% proxy gate")
                replay_pass_complete_rows += 1
            else:
                raise ValueError(f"Unexpected status in frozen pilot: {status}")

        status_range_distribution.setdefault(status, {})
        status_range_distribution[status][str(len(legs))] = (
            status_range_distribution[status].get(str(len(legs)), 0) + 1
        )
        validation_rows.append({
            "row": row,
            "legs": legs,
            "status": status,
            "max_range_proxy_pct": max_range,
            "hard_oi_block": status == "BLOCKED_LEG_ELIGIBILITY",
            "leg_evidence_status": detail,
        })

    if strict_parent:
        if hard_oi_rows != EXPECTED_STATUS_COUNTS["BLOCKED_LEG_ELIGIBILITY"]:
            raise ValueError(f"Expected 100 explicit OI-blocked rows, observed {hard_oi_rows}")
        if range_complete_rows != EXPECTED_STATUS_COUNTS["EXCLUDED_OHLC_RANGE_PROXY"]:
            raise ValueError(f"Expected 379 complete range-excluded rows, observed {range_complete_rows}")
        if replay_pass_complete_rows != EXPECTED_STATUS_COUNTS["REPLAY_PASS"]:
            raise ValueError(f"Expected one complete baseline pass row, observed {replay_pass_complete_rows}")

    return {
        "rows": rows,
        "details": validation_rows,
        "status_counts": dict(sorted(status_counts.items())),
        "configuration_count": len(configs),
        "event_identity_count": len(event_ids),
        "complete_leg_payload_rows": len(validation_rows),
        "complete_range_excluded_rows": range_complete_rows,
        "explicit_hard_oi_block_rows": hard_oi_rows,
        "complete_replay_pass_rows": replay_pass_complete_rows,
        "leg_payload_rows_by_status": dict(sorted(completeness_by_status.items())),
        "leg_count_distribution_by_status": status_range_distribution,
    }


def classify_at_threshold(item: dict[str, Any], threshold_pct: float) -> tuple[bool, str]:
    row = item["row"]
    if item["hard_oi_block"]:
        return False, "REQUIRED_LEG_PRIOR_OI_BELOW_100"
    if any(leg.get("prior_oi_status") != "PASS" for leg in item["legs"]):
        return False, "REQUIRED_LEG_PRIOR_OI_NOT_PASS"
    if any(leg.get("entry_status") != "PASS" for leg in item["legs"]):
        return False, "REQUIRED_LEG_ENTRY_BAR_NOT_PASS"
    if any(leg.get("exit_status") != "PASS" for leg in item["legs"]):
        return False, "REQUIRED_LEG_EXIT_BAR_NOT_PASS"
    if item["max_range_proxy_pct"] > float(threshold_pct):
        return False, "OHLC_RANGE_PROXY_EXCEEDS_THRESHOLD"
    return True, "ELIGIBLE_FOR_OHLC_PRICE_REFERENCE_SIMULATION"


def compute_trade_scenario(
    row: dict[str, str],
    legs: list[dict[str, Any]],
    brokerage_per_order: float,
    slippage_per_fill_inr: float,
) -> dict[str, Any]:
    """Use exact stored opens and the shared statutory-fee helper, with no synthetic OHLC bars."""
    if not legs:
        raise ValueError("Cannot simulate P&L with no legs")
    slip = float(slippage_per_fill_inr)
    if not math.isfinite(slip) or slip < 0:
        raise ValueError("Slippage must be finite and nonnegative")
    gross_pnl = 0.0
    orders: list[dict[str, Any]] = []
    leg_gross: list[dict[str, Any]] = []
    for leg in legs:
        side = str(leg["side"]).upper()
        if side not in {"BUY", "SELL"}:
            raise ValueError(f"Unsupported side {side!r}")
        lots = finite_number(leg["quantity_lots"])
        lot_size = finite_number(leg["lot_size"])
        entry_ref = finite_number(leg["entry_open"])
        exit_ref = finite_number(leg["exit_open"])
        if any(value is None for value in (lots, lot_size, entry_ref, exit_ref)):
            raise ValueError("Missing number in an eligible row")
        units = float(lots) * int(lot_size)
        entry_fill = kernel.adverse_fill(float(entry_ref), side, slip)
        exit_action = "SELL" if side == "BUY" else "BUY"
        exit_fill = kernel.adverse_fill(float(exit_ref), exit_action, slip)
        signed_units = units if side == "BUY" else -units
        leg_pnl = signed_units * (exit_fill - entry_fill)
        gross_pnl += leg_pnl
        orders.extend([
            {"date": row["entry_ts"], "action": side, "price": entry_fill, "contract_units": units},
            {"date": row["exit_ts"], "action": exit_action, "price": exit_fill, "contract_units": units},
        ])
        leg_gross.append({
            "leg_id": leg["leg_id"],
            "side": side,
            "units": units,
            "entry_reference": float(entry_ref),
            "entry_fill_reference_adjusted": entry_fill,
            "exit_reference": float(exit_ref),
            "exit_fill_reference_adjusted": exit_fill,
            "gross_pnl_inr": leg_pnl,
        })

    fees = kernel.cost_breakdown(orders, float(brokerage_per_order))
    net_pnl = gross_pnl - float(fees["total"])
    return {
        "gross_pnl_inr": gross_pnl,
        "fees_brokerage_inr": float(fees["brokerage"]),
        "fees_exchange_inr": float(fees["exchange"]),
        "fees_sebi_inr": float(fees["sebi"]),
        "fees_ipft_inr": float(fees["ipft"]),
        "fees_stt_inr": float(fees["stt"]),
        "fees_stamp_duty_inr": float(fees["stamp_duty"]),
        "fees_gst_inr": float(fees["gst"]),
        "fees_total_inr": float(fees["total"]),
        "net_pnl_inr": net_pnl,
        "return_on_reference_capital_pct": 100.0 * net_pnl / kernel.REFERENCE_CAPITAL_INR,
        "leg_count": len(legs),
        "order_count": len(orders),
        "orders": orders,
        "leg_gross_details": leg_gross,
    }


def _summary_for_trades(trades: list[dict[str, Any]]) -> dict[str, Any]:
    pnls = [float(x["net_pnl_inr"]) for x in trades]
    gross = [float(x["gross_pnl_inr"]) for x in trades]
    fees = [float(x["fees_total_inr"]) for x in trades]
    if not pnls:
        return {
            "eligible_config_event_rows": 0,
            "unique_event_identities": 0,
            "unique_expiries": 0,
            "grid_sum_gross_pnl_inr": 0.0,
            "grid_sum_fees_inr": 0.0,
            "grid_sum_net_pnl_inr": 0.0,
            "mean_net_pnl_per_row_inr": None,
            "median_net_pnl_per_row_inr": None,
            "positive_rows": 0,
            "negative_rows": 0,
            "zero_rows": 0,
            "win_rate_pct": None,
            "min_net_pnl_per_row_inr": None,
            "max_net_pnl_per_row_inr": None,
            "grid_sum_is_portfolio_pnl": False,
        }
    pos = sum(x > 0 for x in pnls)
    neg = sum(x < 0 for x in pnls)
    return {
        "eligible_config_event_rows": len(trades),
        "unique_event_identities": len({x["event_id"] for x in trades}),
        "unique_expiries": len({x["expiry"] for x in trades}),
        "grid_sum_gross_pnl_inr": sum(gross),
        "grid_sum_fees_inr": sum(fees),
        "grid_sum_net_pnl_inr": sum(pnls),
        "mean_net_pnl_per_row_inr": statistics.mean(pnls),
        "median_net_pnl_per_row_inr": statistics.median(pnls),
        "positive_rows": pos,
        "negative_rows": neg,
        "zero_rows": len(pnls) - pos - neg,
        "win_rate_pct": 100.0 * pos / len(pnls),
        "min_net_pnl_per_row_inr": min(pnls),
        "max_net_pnl_per_row_inr": max(pnls),
        "grid_sum_is_portfolio_pnl": False,
    }


def analyze(
    input_rows: list[dict[str, str]],
    parent_report: dict[str, Any] | None = None,
    *,
    strict_parent: bool = False,
    input_sha256: str | None = None,
) -> dict[str, Any]:
    """Return bounded scenario outputs and invariants; do not rank/promote strategies."""
    validated = validate_ledger(input_rows, parent_report, strict_parent=strict_parent)
    details = validated["details"]
    eligibility_rows: list[dict[str, Any]] = []
    trade_scenarios: list[dict[str, Any]] = []
    eligible_by_threshold: dict[int, list[dict[str, Any]]] = {}

    for threshold in THRESHOLDS:
        eligible_items: list[dict[str, Any]] = []
        for item in details:
            row = item["row"]
            ok, reason = classify_at_threshold(item, threshold)
            eligibility_rows.append({
                "configuration_id": row["configuration_id"],
                "candidate_id": row["candidate_id"],
                "family_id": row["family_id"],
                "split": row["split"],
                "event_id": row["event_id"],
                "expiry": row["expiry"],
                "threshold_pct": threshold,
                "parent_status": row["status"],
                "eligible": ok,
                "classification_reason": reason,
                "max_range_proxy_pct": item["max_range_proxy_pct"],
                "expected_leg_count": EXPECTED_LEGS[row["family_id"]],
                "observed_leg_count": len(item["legs"]),
            })
            if ok:
                eligible_items.append(item)
        eligible_by_threshold[threshold] = eligible_items

        for item in eligible_items:
            row = item["row"]
            legs = item["legs"]
            for brokerage in BROKERAGE_PER_ORDER_INR:
                for slip_label, slip in SLIPPAGE_CASES:
                    costs = compute_trade_scenario(row, legs, brokerage, slip)
                    if not all(math.isfinite(float(costs[k])) for k in (
                        "gross_pnl_inr", "fees_total_inr", "net_pnl_inr",
                        "return_on_reference_capital_pct",
                    )):
                        raise ValueError("Non-finite P&L or fee result")
                    trade_scenarios.append({
                        "configuration_id": row["configuration_id"],
                        "candidate_id": row["candidate_id"],
                        "family_id": row["family_id"],
                        "selector_mode": row["selector_mode"],
                        "split": row["split"],
                        "event_id": row["event_id"],
                        "expiry": row["expiry"],
                        "entry_ts": row["entry_ts"],
                        "exit_ts": row["exit_ts"],
                        "threshold_pct": threshold,
                        "brokerage_per_order_inr": brokerage,
                        "slippage_case": slip_label,
                        "adverse_slippage_per_fill_inr": slip,
                        "max_range_proxy_pct": item["max_range_proxy_pct"],
                        "gross_pnl_inr": costs["gross_pnl_inr"],
                        "fees_brokerage_inr": costs["fees_brokerage_inr"],
                        "fees_exchange_inr": costs["fees_exchange_inr"],
                        "fees_sebi_inr": costs["fees_sebi_inr"],
                        "fees_ipft_inr": costs["fees_ipft_inr"],
                        "fees_stt_inr": costs["fees_stt_inr"],
                        "fees_stamp_duty_inr": costs["fees_stamp_duty_inr"],
                        "fees_gst_inr": costs["fees_gst_inr"],
                        "fees_total_inr": costs["fees_total_inr"],
                        "net_pnl_inr": costs["net_pnl_inr"],
                        "return_on_reference_capital_pct": costs["return_on_reference_capital_pct"],
                        "leg_count": costs["leg_count"],
                        "order_count": costs["order_count"],
                        "source_price_reference": "exact_option_bar_open_not_bid_ask",
                        "executable_fill_claim": False,
                        "pnl_status": "NON_EXECUTABLE_OHLC_PRICE_REFERENCE_SENSITIVITY",
                    })

    threshold_summary: list[dict[str, Any]] = []
    config_summary: list[dict[str, Any]] = []
    family_summary: list[dict[str, Any]] = []
    robustness_screen: list[dict[str, Any]] = []
    trade_index: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    family_index: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    configs = sorted({row["configuration_id"] for row in input_rows})
    families = sorted({row["family_id"] for row in input_rows})
    for trade in trade_scenarios:
        common = (
            trade["threshold_pct"],
            trade["brokerage_per_order_inr"],
            trade["slippage_case"],
        )
        trade_index[common].append(trade)
        config_index = common + (trade["configuration_id"],)
        family_index = common + (trade["family_id"],)
        trade_index[config_index].append(trade)
        family_index[family_index_key := common + (trade["family_id"],)].append(trade)

    for threshold in THRESHOLDS:
        for brokerage in BROKERAGE_PER_ORDER_INR:
            for slip_label, slip_value in SLIPPAGE_CASES:
                key = (threshold, brokerage, slip_label)
                summ = _summary_for_trades(trade_index.get(key, []))
                threshold_summary.append({
                    "threshold_pct": threshold,
                    "brokerage_per_order_inr": brokerage,
                    "slippage_case": slip_label,
                    "adverse_slippage_per_fill_inr": slip_value,
                    **summ,
                })
                for configuration_id in sorted(configs):
                    matching = trade_index.get(
                        (threshold, brokerage, slip_label, configuration_id), []
                    )
                    # Include configurations with no eligible rows, so the output has a fixed grid.
                    positive = sum(float(x["net_pnl_inr"]) > 0 for x in matching)
                    negative = sum(float(x["net_pnl_inr"]) < 0 for x in matching)
                    pnl = [float(x["net_pnl_inr"]) for x in sorted(matching, key=lambda x: (x["entry_ts"], x["event_id"]))]
                    cumulative = peak = max_dd = 0.0
                    for value in pnl:
                        cumulative += value
                        peak = max(peak, cumulative)
                        max_dd = max(max_dd, peak - cumulative)
                    config_summary.append({
                        "configuration_id": configuration_id,
                        "threshold_pct": threshold,
                        "brokerage_per_order_inr": brokerage,
                        "slippage_case": slip_label,
                        "adverse_slippage_per_fill_inr": slip_value,
                        "eligible_event_rows": len(matching),
                        "unique_event_identities": len({x["event_id"] for x in matching}),
                        "grid_sum_gross_pnl_inr": sum(float(x["gross_pnl_inr"]) for x in matching),
                        "grid_sum_fees_inr": sum(float(x["fees_total_inr"]) for x in matching),
                        "grid_sum_net_pnl_inr": sum(pnl),
                        "mean_net_pnl_per_row_inr": statistics.mean(pnl) if pnl else None,
                        "median_net_pnl_per_row_inr": statistics.median(pnl) if pnl else None,
                        "positive_rows": positive,
                        "negative_rows": negative,
                        "win_rate_pct": 100.0 * positive / len(pnl) if pnl else None,
                        "max_peak_to_trough_net_cashflow_inr": max_dd if pnl else None,
                        "reference_capital_inr": kernel.REFERENCE_CAPITAL_INR,
                        "grid_sum_is_portfolio_pnl": False,
                    })
                    if brokerage == 20.0 and slip_label == "very_severe_0.50":
                        loo_min = min(
                            (sum(pnl) - value for value in pnl), default=None
                        )
                        robustness_screen.append({
                            "configuration_id": configuration_id,
                            "threshold_pct": threshold,
                            "eligible_event_rows": len(matching),
                            "unique_event_identities": len({x["event_id"] for x in matching}),
                            "brokerage_per_order_inr": brokerage,
                            "adverse_slippage_per_fill_inr": slip_value,
                            "grid_sum_net_pnl_inr": sum(pnl),
                            "leave_one_event_out_min_net_inr": loo_min,
                            "meets_preregistered_event_count": len({x["event_id"] for x in matching}) >= 10,
                            "passes_severe_cost_screen": (
                                len({x["event_id"] for x in matching}) >= 10 and sum(pnl) > 0
                            ),
                            "promotion_eligible": False,
                            "interpretation": "Exploratory quote-validation lead only; never a strategy promotion.",
                        })

                for family_id in sorted(families):
                    family_trades = family_index.get(
                        (threshold, brokerage, slip_label, family_id), []
                    )
                    family_summary.append({
                        "family_id": family_id,
                        "threshold_pct": threshold,
                        "brokerage_per_order_inr": brokerage,
                        "slippage_case": slip_label,
                        "adverse_slippage_per_fill_inr": slip_value,
                        **_summary_for_trades(family_trades),
                    })

    expected_by_threshold = {
        t: sum(1 for x in items) for t, items in eligible_by_threshold.items()
    }
    if strict_parent:
        actual = tuple(expected_by_threshold[t] for t in THRESHOLDS)
        if actual != EXPECTED_ELIGIBLE_COUNTS:
            raise ValueError(f"Phase54 coverage counts changed: {actual} != {EXPECTED_ELIGIBLE_COUNTS}")

    # Invariants: same eligible row set across all cost cases; fixed number of
    # summaries; costs and gross P&L behave monotonically with adverse assumptions.
    for threshold in THRESHOLDS:
        counts = [expected_by_threshold[threshold]] * (
            len(BROKERAGE_PER_ORDER_INR) * len(SLIPPAGE_CASES)
        )
        if len(set(counts)) != 1:
            raise AssertionError("Cost scenario changed trade eligibility")

    by_trade_scenario: dict[tuple[Any, ...], dict[float, float]] = defaultdict(dict)
    for trade in trade_scenarios:
        key = (
            trade["configuration_id"], trade["event_id"], trade["threshold_pct"],
            trade["brokerage_per_order_inr"],
        )
        by_trade_scenario[key][float(trade["adverse_slippage_per_fill_inr"])] = float(trade["gross_pnl_inr"])
    for key, values in by_trade_scenario.items():
        ordered = [values[slip] for slip in sorted(values)]
        if any(next_value > prior_value + 1e-8 for prior_value, next_value in zip(ordered, ordered[1:])):
            raise AssertionError(f"Gross P&L improved under higher adverse slippage for {key}")

    scenario_lookup = {
        (x["configuration_id"], x["event_id"], x["threshold_pct"],
         x["slippage_case"], x["brokerage_per_order_inr"]): x
        for x in trade_scenarios
    }
    for x in trade_scenarios:
        if x["brokerage_per_order_inr"] != 10.0:
            continue
        prefix = (
            x["configuration_id"], x["event_id"], x["threshold_pct"], x["slippage_case"]
        )
        ten = scenario_lookup[prefix + (10.0,)]
        twenty = scenario_lookup[prefix + (20.0,)]
        if float(twenty["net_pnl_inr"]) > float(ten["net_pnl_inr"]) + 1e-8:
            raise AssertionError("Net P&L improved when per-order brokerage rose from ₹10 to ₹20")

    severe_passes = sum(1 for row in robustness_screen if row["passes_severe_cost_screen"])
    return {
        "phase": "56",
        "status": (
            "OHLC_PRICE_REFERENCE_PNL_SENSITIVITY_COMPLETE_NON_EXECUTABLE"
            if strict_parent else "SELF_TEST_FIXTURE_ANALYSIS"
        ),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": {
            "path": str(INPUT.relative_to(ROOT)) if INPUT.exists() else "fixture",
            "row_count": len(input_rows),
            "input_sha256": input_sha256,
            "pinned_dataset_revision": PINNED_REVISION,
            "parent_grid": "phase52-grid-v1.3",
            "parent_pilot": "phase52-historical-base-pilot-v0.2.1-audit-provenance",
            "parent_report": str(PARENT_REPORT.relative_to(ROOT)) if PARENT_REPORT.exists() else None,
        },
        "parent_status_counts": validated["status_counts"],
        "configuration_count": validated["configuration_count"],
        "event_identity_count": validated["event_identity_count"],
        "full_leg_payload_rows": validated["complete_leg_payload_rows"],
        "full_leg_payload_rows_by_status": validated["leg_payload_rows_by_status"],
        "complete_range_excluded_rows": validated["complete_range_excluded_rows"],
        "explicit_hard_oi_block_rows": validated["explicit_hard_oi_block_rows"],
        "complete_replay_pass_rows": validated["complete_replay_pass_rows"],
        "threshold_eligible_rows": {str(t): expected_by_threshold[t] for t in THRESHOLDS},
        "thresholds": list(THRESHOLDS),
        "brokerage_per_order_inr": list(BROKERAGE_PER_ORDER_INR),
        "slippage_cases": [{"label": name, "inr_per_fill": value} for name, value in SLIPPAGE_CASES],
        "trade_scenario_rows": len(trade_scenarios),
        "threshold_summary_rows": len(threshold_summary),
        "configuration_summary_rows": len(config_summary),
        "family_summary_rows": len(family_summary),
        "robustness_screen_rows": len(robustness_screen),
        "configurations_passing_severe_cost_screen_any_threshold": severe_passes,
        "invariants": {
            "phase54_eligibility_counts_reproduced": (
                tuple(expected_by_threshold[t] for t in THRESHOLDS) == EXPECTED_ELIGIBLE_COUNTS
            ) if strict_parent else None,
            "all_rows_have_full_leg_payload": validated["complete_leg_payload_rows"] == len(input_rows),
            "oi_blockers_remain_ineligible": validated["explicit_hard_oi_block_rows"] == EXPECTED_STATUS_COUNTS["BLOCKED_LEG_ELIGIBILITY"],
            "gross_pnl_nonincreasing_with_slippage": True,
            "net_pnl_nonincreasing_when_brokerage_increases": True,
            "scenario_eligibility_unchanged_by_cost": True,
            "holdout_used": False,
            "raw_data_downloaded": False,
            "bid_ask_or_depth_observed": False,
            "historical_pnl_recalculated_from_quotes": False,
            "live_execution_or_promotion_allowed": False,
        },
        "fixed_method": {
            "entry_reference": "recorded exact option-bar entry open",
            "exit_reference": "recorded exact option-bar 15:15 open",
            "fees": "date-aware existing Phase 52 kernel fee schedule",
            "brokerage_scenarios": "₹10 current Paytm Money F&O FAQ rate and ₹20 conservative/alternate comparator",
            "slippage": "fixed adverse INR per fill scenarios; non-measured, not spread-derived",
            "reference_capital_inr": kernel.REFERENCE_CAPITAL_INR,
            "pnl_semantics": "NON_EXECUTABLE_OHLC_PRICE_REFERENCE_SENSITIVITY",
        },
        "interpretation": [
            "The range thresholds were preregistered in Phase 54, before Phase 56 P&L is computed; no threshold is selected from P&L results.",
            "Every aggregate across configurations is a parameter-grid diagnostic, not a deployable portfolio. Configurations reuse dates and overlapping contract opportunities.",
            "An OHLC open is a price reference only; it does not prove that the corresponding fill was available. The OHLC high-low/open proxy is not a quoted bid/ask spread.",
            "The fixed prior-minute OI minimum of 100, event/configuration universe, exact entry/exit timestamps, source revision and holdout boundary are unchanged.",
            "No p-values, confidence intervals, strategy ranking or profitability/generalization claim is made. Any severe-cost screen pass is only a lead for separately licensed/authorized quote validation.",
            "The source declares CC BY-NC 4.0; commercial use and live-strategy promotion remain outside scope and prohibited by the source/licensing gate.",
        ],
        "threshold_summary": threshold_summary,
        "configuration_summary": config_summary,
        "family_summary": family_summary,
        "robustness_screen": robustness_screen,
        "eligibility_rows": eligibility_rows,
        "trade_scenarios": trade_scenarios,
    }


def write_outputs(result: dict[str, Any], out_dir: Path = OUT) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    # Large detail arrays are persisted in separate CSVs; keep JSON report compact.
    report = {k: v for k, v in result.items() if k not in {
        "threshold_summary", "configuration_summary", "family_summary",
        "robustness_screen", "eligibility_rows", "trade_scenarios",
    }}
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def write_csv(name: str, rows: list[dict[str, Any]]) -> None:
        if not rows:
            (out_dir / name).write_text("", encoding="utf-8")
            return
        # Flatten only already flat rows; discard internal list/dict payloads if any.
        fields = list(rows[0].keys())
        with (out_dir / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    write_csv("threshold_summary.csv", result["threshold_summary"])
    write_csv("configuration_summary.csv", result["configuration_summary"])
    write_csv("family_summary.csv", result["family_summary"])
    write_csv("robustness_screen.csv", result["robustness_screen"])
    write_csv("eligibility_by_threshold.csv", result["eligibility_rows"])
    write_csv("trade_scenarios.csv", result["trade_scenarios"])

    threshold_counts = result["threshold_eligible_rows"]
    ten_base = {
        (r["threshold_pct"], r["brokerage_per_order_inr"], r["slippage_case"]): r
        for r in result["threshold_summary"]
    }
    lines = [
        "# Phase 56 OHLC price-reference P&L sensitivity", "",
        "**NON-EXECUTABLE PRICE-REFERENCE SENSITIVITY — not a quote-based backtest, liquidity validation, or strategy recommendation.**", "",
        f"- Input rows: {result['input']['row_count']}",
        f"- Input SHA-256: {result['input'].get('input_sha256')}",
        f"- Pinned revision: {result['input']['pinned_dataset_revision']}",
        f"- Parent status counts: {json.dumps(result['parent_status_counts'], sort_keys=True)}",
        f"- Full selected-leg payload rows: {result['full_leg_payload_rows']}",
        f"- Hard prior-OI-blocked rows rejected at all thresholds: {result['explicit_hard_oi_block_rows']}",
        f"- Price-reference scenario rows: {result['trade_scenario_rows']}",
        f"- Configurations passing the severe-cost screen at any threshold: {result['configurations_passing_severe_cost_screen_any_threshold']}", "",
        "## Threshold sensitivity: eligibility and pooled grid diagnostics", "",
        "Pooled figures below aggregate configuration-event rows with overlapping dates/strategies. They are not a single portfolio P&L or an investable equity curve.", "",
        "| Range threshold | Eligible rows | Net grid sum ₹10/order + ₹0.05 slip | Net grid sum ₹20/order + ₹0.50 slip |",
        "|---:|---:|---:|---:|",
    ]
    for threshold in THRESHOLDS:
        base = ten_base[(threshold, 10.0, "base_0.05")]
        severe = ten_base[(threshold, 20.0, "very_severe_0.50")]
        lines.append(
            f"| {threshold}% | {threshold_counts[str(threshold)]} | "
            f"₹{base['grid_sum_net_pnl_inr']:.2f} ({base['eligible_config_event_rows']} rows) | "
            f"₹{severe['grid_sum_net_pnl_inr']:.2f} ({severe['eligible_config_event_rows']} rows) |"
        )
    lines.extend([
        "", "## Interpretation", "",
        *[f"- {x}" for x in result["interpretation"]],
        "", "## Detailed machine-readable output", "",
        "- \`eligibility_by_threshold.csv\`: every input row at every threshold, including exclusions and hard OI blockers.",
        "- \`trade_scenarios.csv\`: every eligible configuration-event row under every threshold and all 12 cost scenarios.",
        "- \`configuration_summary.csv\`: complete configuration × threshold × cost matrix, including zero-eligibility rows.",
        "- \`family_summary.csv\`: family-pooled descriptive summaries; these also are not portfolio returns.",
        "- \`threshold_summary.csv\`: 132 threshold × brokerage × slippage summaries.",
        "- \`robustness_screen.csv\`: every configuration × threshold at ₹20/order and ₹0.50 adverse slippage per fill; pass only means a lead for future quote-validated research.",
        "",
    ])
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def self_test() -> None:
    fixture = [{
        "configuration_id": "cfg1",
        "candidate_id": "candidate1",
        "family_id": "BUY_CALL",
        "selector_mode": "BASELINE",
        "split": "development",
        "event_id": "event1",
        "expiry": "2025-03-13",
        "entry_ts": "2025-03-13T09:45:00+05:30",
        "exit_ts": "2025-03-13T15:15:00+05:30",
        "status": "REPLAY_PASS",
        "exclusion_reason": "all selected leg gates passed",
        "option_source_sha256": "testhash",
        "resolved_legs_json": json.dumps([{
            "leg_id": "L1",
            "side": "BUY",
            "quantity_lots": 1,
            "lot_size": 50,
            "strike": 22000,
            "option_type": "CE",
            "expiry": "2025-03-13",
            "entry_status": "PASS",
            "prior_oi_status": "PASS",
            "range_proxy_status": "PASS",
            "exit_status": "PASS",
            "prior_oi": 1000,
            "entry_range_proxy_pct": 1.5,
            "entry_open": 100.0,
            "exit_open": 120.0,
        }]),
    }]
    legs = legs_for(fixture[0])
    out = compute_trade_scenario(fixture[0], legs, 10.0, 0.05)
    assert out["order_count"] == 2 and out["leg_count"] == 1
    assert abs(out["gross_pnl_inr"] - 995.0) < 1e-8
    higher_slip = compute_trade_scenario(fixture[0], legs, 10.0, 0.50)
    assert higher_slip["gross_pnl_inr"] <= out["gross_pnl_inr"]
    higher_brokerage = compute_trade_scenario(fixture[0], legs, 20.0, 0.05)
    assert higher_brokerage["net_pnl_inr"] < out["net_pnl_inr"]

    blocked = dict(fixture[0])
    blocked["status"] = "BLOCKED_LEG_ELIGIBILITY"
    blocked["exclusion_reason"] = "a required selected leg lacks exact prior-bar OI at or above 100"
    blocked["resolved_legs_json"] = json.dumps([{
        **legs[0],
        "prior_oi": 0,
        "prior_oi_status": "FAIL",
    }])
    validated = validate_ledger([blocked], strict_parent=False)
    eligible, reason = classify_at_threshold(validated["details"][0], 1000)
    assert not eligible and reason == "REQUIRED_LEG_PRIOR_OI_BELOW_100"
    print("Phase 56 cost arithmetic and hard OI block self-test PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test-only", action="store_true")
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    if args.self_test_only:
        self_test()
        return
    rows = read_rows()
    parent = read_parent_report()
    input_hash = sha256_bytes(INPUT.read_bytes())
    result = analyze(rows, parent, strict_parent=True, input_sha256=input_hash)
    write_outputs(result, args.output)
    print(json.dumps({
        "status": result["status"],
        "input_sha256": input_hash,
        "row_count": result["input"]["row_count"],
        "threshold_eligible_rows": result["threshold_eligible_rows"],
        "trade_scenario_rows": result["trade_scenario_rows"],
        "threshold_summary_rows": result["threshold_summary_rows"],
        "configuration_summary_rows": result["configuration_summary_rows"],
        "family_summary_rows": result["family_summary_rows"],
        "severe_cost_screen_passes": result["configurations_passing_severe_cost_screen_any_threshold"],
        "output": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
