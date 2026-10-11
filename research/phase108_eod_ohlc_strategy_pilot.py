#!/usr/bin/env python3
"""Bounded Phase 108 EOD OHLC options proxy pilot; publishes aggregates only. Frozen run."""
import argparse
import csv
import hashlib
import io
import json
import math
import os
import random
import sys
import time
import urllib.error
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import mean, median

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from research.phase104_eod_stock_options.nse_eod_audit import (  # noqa: E402
    INSTRUMENTS, NSE_URL, REQUIRED, SYMBOLS, check_window, fetch_bytes,
    parse_date, parse_number,
)
from research.phase104_eod_stock_options.cost_model import round_trip_cost  # noqa: E402

PHASE = "108"
DEFAULT_FROM = "2026-09-02"
DEFAULT_TO = "2026-10-02"  # exclusive
STRATEGIES = ("MOMENTUM_ATM", "REVERSAL_ATM", "MOMENTUM_OI_CONFIRM", "LARGE_MOVE_MOMENTUM", "SMALL_MOVE_REVERSAL", "LARGE_MOVE_REVERSAL", "LOW_VOL_MOMENTUM", "HIGH_VOL_MOMENTUM", "LOW_VOL_REVERSAL", "HIGH_VOL_REVERSAL")
BROKERAGE_LEVELS = (10.0, 15.0, 20.0)
SLIPPAGE_LEVELS = (0.0, 0.05, 0.25, 0.50)
FEE_MULTIPLIERS = (1.0, 1.5)
PRICE_FIELDS = ("OpnPric", "HghPric", "LwPric", "ClsPric")


def finite_positive(value):
    return value is not None and math.isfinite(float(value)) and float(value) > 0


def valid_ohlc(row):
    """True only for nonzero, internally consistent option OHLC bars."""
    o, h, low, close = (row.get(k) for k in ("open", "high", "low", "close"))
    if any(v is None or not math.isfinite(float(v)) for v in (o, h, low, close)):
        return False
    if o <= 0 or h <= 0 or low < 0 or close <= 0:
        return False
    return low <= min(o, close) + 1e-9 and h + 1e-9 >= max(o, close) and low <= h + 1e-9


def parse_strategy_archive(payload, expected_day):
    """Decode the official archive into ephemeral in-memory rows."""
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(names) != 1:
            raise ValueError("Expected exactly one CSV in the NSE daily archive ZIP.")
        body = archive.read(names[0]).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(body))
    if not reader.fieldnames or not REQUIRED.issubset(set(reader.fieldnames)):
        raise ValueError("NSE UDiFF schema missing required identity/OHLC fields.")

    rows = []
    selected_count = 0
    mismatch_count = 0
    for raw in reader:
        symbol = str(raw.get("TckrSymb", "")).strip().upper()
        instrument = str(raw.get("FinInstrmTp", "")).strip().upper()
        if symbol not in SYMBOLS or instrument not in INSTRUMENTS:
            continue
        selected_count += 1
        business_day = parse_date(raw.get("BizDt")) if "BizDt" in reader.fieldnames else expected_day
        if business_day and business_day != expected_day:
            mismatch_count += 1
        row_day = business_day or expected_day
        expiry = parse_date(raw.get("FininstrmActlXpryDt")) or parse_date(raw.get("XpryDt"))
        strike = parse_number(raw.get("StrkPric"))
        side = str(raw.get("OptnTp", "")).strip().upper()
        underlying = parse_number(raw.get("UndrlygPric")) if "UndrlygPric" in reader.fieldnames else None
        volume = parse_number(raw.get("TtlTradgVol"))
        oi = parse_number(raw.get("OpnIntrst"))
        lot_size = parse_number(raw.get("NewBrdLotQty")) if "NewBrdLotQty" in reader.fieldnames else None
        prices = {name: parse_number(raw.get(source)) for name, source in zip(("open", "high", "low", "close"), PRICE_FIELDS)}
        identity_ok = bool(row_day == expected_day and expiry and strike is not None and strike > 0 and side in {"CE", "PE"})
        rows.append({
            "trade_date": row_day, "symbol": symbol, "expiry": expiry,
            "strike": strike, "option_type": side, "identity_complete": identity_ok,
            "prices_complete": all(v is not None and math.isfinite(float(v)) for v in prices.values()),
            "volume": volume, "oi": oi, "underlying": underlying, "lot_size": lot_size,
            **prices,
        })
    return {"rows": rows, "selected_count": selected_count, "date_mismatch_count": mismatch_count}


def contract_key(row):
    return (row["trade_date"], row["symbol"], row["expiry"], format(float(row["strike"]), ".10g"), row["option_type"])


def exact_contract_key(row):
    return (row["expiry"], round(float(row["strike"]), 8), row["option_type"])


def summarize_source(rows, selected_count, date_mismatches):
    keys = Counter(contract_key(r) for r in rows if r.get("identity_complete"))
    duplicates = sum(n - 1 for n in keys.values() if n > 1)
    n = len(rows)
    identity_n = sum(bool(r.get("identity_complete")) for r in rows)
    price_n = sum(bool(r.get("prices_complete")) for r in rows)
    positive_volume = sum(r.get("volume") is not None and r["volume"] > 0 for r in rows)
    zero_volume = sum(r.get("volume") == 0 for r in rows)
    missing_volume = sum(r.get("volume") is None for r in rows)
    missing_oi = sum(r.get("oi") is None for r in rows)
    missing_underlying = sum(not finite_positive(r.get("underlying")) for r in rows)
    missing_lot = sum(not finite_positive(r.get("lot_size")) for r in rows)
    invalid_ohlc_positive_volume = sum(
        r.get("volume") is not None and r["volume"] > 0 and not valid_ohlc(r)
        for r in rows if r.get("trade_date") and r.get("identity_complete")
    )
    return {
        "selected_rows": selected_count, "parsed_rows": n,
        "identity_complete_rows": identity_n,
        "identity_completeness_pct": round(100 * identity_n / n, 4) if n else 0.0,
        "ohlc_complete_rows": price_n,
        "ohlc_completeness_pct": round(100 * price_n / n, 4) if n else 0.0,
        "duplicate_daily_contract_keys": duplicates,
        "date_mismatch_rows": date_mismatches,
        "positive_volume_rows": positive_volume, "zero_volume_rows": zero_volume,
        "missing_volume_rows": missing_volume, "missing_oi_rows": missing_oi,
        "missing_underlying_rows": missing_underlying, "missing_lot_size_rows": missing_lot,
        "invalid_ohlc_positive_volume_rows": invalid_ohlc_positive_volume,
        "by_symbol_rows": dict(sorted(Counter(r["symbol"] for r in rows).items())),
    }


def signal_side(strategy, underlying_return, volatility_regime=None):
    """Map only the prior-session underlying return into a long-option side."""
    if underlying_return is None or not math.isfinite(underlying_return) or abs(underlying_return) < 1e-12:
        return None
    momentum_side = "CE" if underlying_return > 0 else "PE"
    if strategy.startswith("LOW_VOL_") and volatility_regime != "LOW":
        return None
    if strategy.startswith("HIGH_VOL_") and volatility_regime != "HIGH":
        return None
    if strategy in ("SMALL_MOVE_REVERSAL", "LARGE_MOVE_REVERSAL"):
        if strategy == "SMALL_MOVE_REVERSAL" and abs(underlying_return) >= 0.005:
            return None
        if strategy == "LARGE_MOVE_REVERSAL" and abs(underlying_return) < 0.005:
            return None
        return "PE" if momentum_side == "CE" else "CE"
    if strategy == "LARGE_MOVE_MOMENTUM" and abs(underlying_return) < 0.005:
        return None
    if strategy in ("MOMENTUM_ATM", "MOMENTUM_OI_CONFIRM", "LARGE_MOVE_MOMENTUM", "LOW_VOL_MOMENTUM", "HIGH_VOL_MOMENTUM"):
        return momentum_side
    if strategy in ("REVERSAL_ATM", "LOW_VOL_REVERSAL", "HIGH_VOL_REVERSAL"):
        return "PE" if momentum_side == "CE" else "CE"
    raise ValueError("Unknown frozen strategy: " + str(strategy))


def select_contract(prior_rows, signal_date, option_side, underlying):
    """Contract selection is limited to signal-date rows and their known EOD data."""
    if not finite_positive(underlying):
        return None
    day = date.fromisoformat(signal_date)
    eligible = []
    for row in prior_rows:
        if not row.get("identity_complete") or not row.get("prices_complete"):
            continue
        if row.get("option_type") != option_side or not row.get("expiry"):
            continue
        expiry = date.fromisoformat(row["expiry"])
        days_to_expiry = (expiry - day).days
        if not 7 <= days_to_expiry <= 35:
            continue
        if not finite_positive(row.get("volume")) or not finite_positive(row.get("oi")):
            continue
        if not finite_positive(row.get("lot_size")) or not valid_ohlc(row):
            continue
        eligible.append(row)
    if not eligible:
        return None
    nearest_expiry = min(row["expiry"] for row in eligible)
    same_expiry = [row for row in eligible if row["expiry"] == nearest_expiry]
    return min(
        same_expiry,
        key=lambda row: (
            abs(float(row["strike"]) - float(underlying)),
            -float(row["oi"]), -float(row["volume"]), float(row["strike"]),
        ),
    )


def oi_increased(current_rows, prior_rows, option_side, expiry, underlying):
    """Exploratory confirmation: same-side near-ATM OI rose by signal close."""
    if not finite_positive(underlying):
        return False
    lower, upper = float(underlying) * 0.97, float(underlying) * 1.03

    def total(rows):
        vals = [
            float(row["oi"]) for row in rows
            if row.get("identity_complete") and row.get("expiry") == expiry
            and row.get("option_type") == option_side
            and row.get("oi") is not None and row["oi"] >= 0
            and row.get("strike") is not None and lower <= float(row["strike"]) <= upper
        ]
        return sum(vals) if vals else None

    current, prior = total(current_rows), total(prior_rows)
    return current is not None and prior is not None and current > prior


def simulate_trade(trade, brokerage, slippage_per_unit, fee_multiplier):
    raw_open, raw_close, quantity = trade["open"], trade["close"], trade["lot_size"]
    buy = raw_open + slippage_per_unit
    sell = max(0.0, raw_close - slippage_per_unit)
    fee_detail = round_trip_cost(
        buy_premium=buy, sell_premium=sell, quantity=quantity,
        trade_date=trade["entry_date"], brokerage_per_order=brokerage,
    )
    fees = float(fee_detail["total_reported_fees"]) * fee_multiplier
    gross = (raw_close - raw_open) * quantity
    slippage_cost = ((buy - raw_open) + (raw_close - sell)) * quantity
    executed_price_pnl = (sell - buy) * quantity
    net = executed_price_pnl - fees
    # Accounting invariant: gross less adverse execution adjustment less fees equals net.
    if abs((gross - slippage_cost - fees) - net) > 0.02:
        raise AssertionError("Net accounting does not reconcile.")
    return {
        "gross_pnl_rupees": gross, "slippage_cost_rupees": slippage_cost,
        "fees_rupees": fees, "net_pnl_rupees": net,
        "premium_deployed_rupees": buy * quantity,
    }


def percentile(values, q):
    if not values:
        return None
    vals = sorted(values)
    if len(vals) == 1:
        return vals[0]
    pos = (len(vals) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    return vals[lo] + (vals[hi] - vals[lo]) * (pos - lo)


def bootstrap_mean_daily_ci(daily_values, seed=106, draws=2000):
    """Deterministic percentile bootstrap of whole-session P&L aggregates."""
    vals = list(daily_values)
    if len(vals) < 3:
        return {"n_sessions": len(vals), "mean_rupees": round(mean(vals), 6) if vals else None,
                "ci95_low_rupees": None, "ci95_high_rupees": None, "draws": 0}
    rng = random.Random(seed)
    boot = []
    for _ in range(draws):
        sample = [vals[rng.randrange(len(vals))] for _ in vals]
        boot.append(mean(sample))
    return {
        "n_sessions": len(vals), "mean_rupees": round(mean(vals), 6),
        "ci95_low_rupees": round(percentile(boot, 0.025), 6),
        "ci95_high_rupees": round(percentile(boot, 0.975), 6), "draws": draws,
    }


def max_drawdown_rupees(daily_net):
    equity, peak, max_dd = 0.0, 0.0, 0.0
    for value in daily_net:
        equity += value
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    return max_dd


def summarize_trades(trades, scenario, all_sessions):
    brokerage, slip, fee_mult = scenario
    by_day = defaultdict(float)
    gross_total = fee_total = slip_total = net_total = premium_total = 0.0
    trade_n = 0
    net_values = []
    for trade in trades:
        result = simulate_trade(trade, brokerage, slip, fee_mult)
        by_day[trade["entry_date"]] += result["net_pnl_rupees"]
        gross_total += result["gross_pnl_rupees"]
        fee_total += result["fees_rupees"]
        slip_total += result["slippage_cost_rupees"]
        net_total += result["net_pnl_rupees"]
        premium_total += result["premium_deployed_rupees"]
        net_values.append(result["net_pnl_rupees"])
        trade_n += 1
    daily = [by_day.get(day, 0.0) for day in all_sessions]
    wins = sum(v > 0 for v in net_values)
    losses = sum(v < 0 for v in net_values)
    positive_sum = sum(v for v in net_values if v > 0)
    negative_sum = -sum(v for v in net_values if v < 0)
    return {
        "brokerage_per_order": brokerage, "slippage_per_unit_per_side": slip,
        "fee_multiplier": fee_mult, "trade_count": trade_n,
        "gross_pnl_rupees": round(gross_total, 2),
        "fees_rupees": round(fee_total, 2),
        "slippage_cost_rupees": round(slip_total, 2),
        "net_pnl_rupees": round(net_total, 2),
        "premium_deployed_rupees": round(premium_total, 2),
        "net_return_on_premium_pct": round(100 * net_total / premium_total, 4) if premium_total > 0 else None,
        "win_rate_pct": round(100 * wins / trade_n, 3) if trade_n else None,
        "average_net_per_trade_rupees": round(mean(net_values), 2) if net_values else None,
        "median_net_per_trade_rupees": round(median(net_values), 2) if net_values else None,
        "profit_factor": round(positive_sum / negative_sum, 5) if negative_sum > 0 else (None if not positive_sum else "INF"),
        "max_drawdown_rupees": round(max_drawdown_rupees(daily), 2),
        "bootstrap_mean_daily_pnl": bootstrap_mean_daily_ci(daily),
    }


def write_chart(stats, out_dir):
    """Small pure-SVG plot, no plotting dependency and no per-trade observations."""
    width, height = 900, 520
    left, right, top, bottom = 90, 40, 70, 90
    plot_w, plot_h = width - left - right, height - top - bottom
    slips = list(SLIPPAGE_LEVELS)
    strategy_colors = {"MOMENTUM_ATM": "#2864dc", "REVERSAL_ATM": "#d85b31", "MOMENTUM_OI_CONFIRM": "#26865b", "LARGE_MOVE_MOMENTUM": "#8e44ad", "SMALL_MOVE_REVERSAL": "#16a085", "LARGE_MOVE_REVERSAL": "#c0392b"}
    base_values = [
        row["net_pnl_rupees"] for row in stats
        if row["brokerage_per_order"] == 20.0 and row["fee_multiplier"] == 1.0
    ]
    ymin = min([0.0] + base_values) if base_values else -1.0
    ymax = max([0.0] + base_values) if base_values else 1.0
    if math.isclose(ymin, ymax):
        ymin, ymax = ymin - 1, ymax + 1
    pad = (ymax - ymin) * 0.08
    ymin -= pad
    ymax += pad
    def x_at(idx):
        return left + idx * plot_w / max(1, len(slips) - 1)
    def y_at(value):
        return top + (ymax - value) * plot_h / (ymax - ymin)
    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="450" y="32" font-family="Arial" font-size="20" text-anchor="middle" fill="#222">Net P&amp;L vs adverse slippage (₹20/order, model fees 1.0×)</text>',
    ]
    for tick in range(5):
        val = ymin + tick * (ymax - ymin) / 4
        y = y_at(val)
        pieces.append(f'<line x1="{left}" y1="{y:.2f}" x2="{width-right}" y2="{y:.2f}" stroke="#dddddd"/>')
        pieces.append(f'<text x="{left-12}" y="{y+4:.2f}" font-family="Arial" font-size="12" text-anchor="end" fill="#444">{val:,.0f}</text>')
    pieces.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#333"/>')
    pieces.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#333"/>')
    for i, slip in enumerate(slips):
        x = x_at(i)
        pieces.append(f'<text x="{x:.2f}" y="{height-bottom+24}" font-family="Arial" font-size="12" text-anchor="middle" fill="#444">₹{slip:.2f}</text>')
    for strategy in STRATEGIES:
        found = []
        for slip in slips:
            row = next((r for r in stats if r["strategy"] == strategy and r["brokerage_per_order"] == 20.0
                        and r["fee_multiplier"] == 1.0 and r["slippage_per_unit_per_side"] == slip), None)
            if row:
                found.append((slip, row["net_pnl_rupees"]))
        if found:
            points = " ".join(f"{x_at(slips.index(slip)):.2f},{y_at(value):.2f}" for slip, value in found)
            color = strategy_colors[strategy]
            pieces.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
            for slip, value in found:
                x, y = x_at(slips.index(slip)), y_at(value)
                pieces.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="{color}"/>')
    legend_x = left + 10
    for idx, strategy in enumerate(STRATEGIES):
        x = legend_x + idx * 250
        color = strategy_colors[strategy]
        pieces.append(f'<line x1="{x}" y1="{height-28}" x2="{x+24}" y2="{height-28}" stroke="{color}" stroke-width="3"/>')
        pieces.append(f'<text x="{x+30}" y="{height-24}" font-family="Arial" font-size="12" fill="#222">{strategy}</text>')
    pieces.append(f'<text x="18" y="{height/2}" transform="rotate(-90 18 {height/2})" font-family="Arial" font-size="13" text-anchor="middle" fill="#222">Net P&amp;L (₹)</text>')
    pieces.append('<text x="450" y="493" font-family="Arial" font-size="12" text-anchor="middle" fill="#555">Each slippage value is applied adversely to both entry and exit; OHLC marks remain proxies.</text>')
    pieces.append("</svg>")
    (out_dir / "figures").mkdir(parents=True, exist_ok=True)
    (out_dir / "figures" / "net_pnl_by_slippage.svg").write_text("\n".join(pieces) + "\n", encoding="utf-8")


def run(args):
    check_window(args.from_date, args.to_date)
    start, end = date.fromisoformat(args.from_date), date.fromisoformat(args.to_date)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    all_rows, selected_total, date_mismatches = [], 0, 0
    archive_hashes, daily_archives, fetch_errors, no_archive_dates = {}, [], [], []
    for i in range((end - start).days):
        day = (start + timedelta(days=i)).isoformat()
        url = NSE_URL.format(date=day.replace("-", ""))
        try:
            payload = fetch_bytes(url)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                no_archive_dates.append(day)
                daily_archives.append({"date": day, "status": "NO_ARCHIVE_OR_NONTRADING_DATE"})
            else:
                fetch_errors.append({"date": day, "type": "HTTPError", "status": exc.code})
                daily_archives.append({"date": day, "status": "HTTP_ERROR", "http_status": exc.code})
            continue
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            fetch_errors.append({"date": day, "type": type(exc).__name__})
            daily_archives.append({"date": day, "status": "NETWORK_ERROR"})
            continue
        digest = hashlib.sha256(payload).hexdigest()
        archive_hashes[day] = digest
        try:
            parsed = parse_strategy_archive(payload, day)
        except Exception as exc:
            fetch_errors.append({"date": day, "type": type(exc).__name__, "message": " ".join(str(exc).split())[:160]})
            daily_archives.append({"date": day, "status": "SCHEMA_OR_PARSE_ERROR"})
            continue
        all_rows.extend(parsed["rows"])
        selected_total += parsed["selected_count"]
        date_mismatches += parsed["date_mismatch_count"]
        daily_archives.append({"date": day, "status": "ARCHIVE_PARSED", "selected_rows": parsed["selected_count"], "sha256": digest})
        time.sleep(0.1)

    source = summarize_source(all_rows, selected_total, date_mismatches)
    parsed_days = sum(item["status"] == "ARCHIVE_PARSED" for item in daily_archives)
    source_gate = (
        not fetch_errors and parsed_days >= 10 and source["identity_completeness_pct"] >= 99.9
        and source["ohlc_completeness_pct"] >= 99.0 and source["duplicate_daily_contract_keys"] == 0
        and source["date_mismatch_rows"] == 0 and source["invalid_ohlc_positive_volume_rows"] == 0
        and source["missing_underlying_rows"] == 0 and source["missing_lot_size_rows"] == 0
    )
    raw_by_day_symbol = defaultdict(list)
    for row in all_rows:
        if row.get("identity_complete") and row.get("trade_date") in archive_hashes:
            raw_by_day_symbol[(row["trade_date"], row["symbol"])].append(row)
    underlying = {}
    for key, rows in raw_by_day_symbol.items():
        values = [float(row["underlying"]) for row in rows if finite_positive(row.get("underlying"))]
        if values:
            underlying[key] = median(values)
    archive_dates_with_data = sorted({day for day, _ in raw_by_day_symbol})
    sessions = [
        day for day in archive_dates_with_data
        if all((day, symbol) in underlying for symbol in SYMBOLS)
    ]
    source["sessions_with_all_five_underlyings"] = len(sessions)
    source["first_research_session"] = sessions[0] if sessions else None
    source["last_research_session"] = sessions[-1] if sessions else None

    decision = {
        "phase": PHASE, "registered_window": {"from_inclusive": args.from_date, "to_exclusive": args.to_date},
        "source_gate": "PASS" if source_gate else "FAIL",
        "strategy_replay": "NOT_RUN_SOURCE_GATE_FAILED" if not source_gate else "PENDING",
        "promotion": "NONE", "interpretation": "OHLC_EXECUTION_PROXY_NOT_VERIFIED_FILLS",
        "reasons": [],
    }
    if not source_gate:
        decision["reasons"].append("The bounded source integrity gate did not pass; strategy P&L was blocked.")
    if len(sessions) < 6:
        decision["reasons"].append("Fewer than six common sessions have underlying coverage for all five symbols.")
        decision["strategy_replay"] = "NOT_RUN_INSUFFICIENT_COMMON_SESSIONS"
    if not source_gate or len(sessions) < 6:
        result = {
            "phase": PHASE, "run_id": os.getenv("GITHUB_RUN_ID", "local"),
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "window": {"from_inclusive": args.from_date, "to_exclusive": args.to_date},
            "source": "NSE official daily UDiFF F&O archive", "symbols": list(SYMBOLS),
            "archive_hashes": archive_hashes, "daily_archives": daily_archives,
            "no_archive_dates": no_archive_dates, "fetch_errors": fetch_errors,
            "raw_rows_persisted": False, "raw_rows_in_artifact": False, "source_aggregate": source,
            "scenario_results": [], "strategy_coverage": [], "decision": decision,
        }
        (out / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        (out / "decision.json").write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
        (out / "summary.csv").write_text("strategy,brokerage_per_order,slippage_per_unit_per_side,fee_multiplier,trade_count,net_pnl_rupees\n", encoding="utf-8")
        (out / "PHASE108_REPORT.md").write_text(make_report(result), encoding="utf-8")
        return result

    rows_by_day_symbol = defaultdict(list)
    rows_by_day_symbol_contract = {}
    for row in all_rows:
        if not row.get("identity_complete"):
            continue
        rows_by_day_symbol[(row["trade_date"], row["symbol"])].append(row)
        key = (row["trade_date"], row["symbol"], exact_contract_key(row))
        # Source duplicate-key gate above guarantees this is unique.
        rows_by_day_symbol_contract[key] = row

    coverage = {s: {"strategy": s, "signal_checks": 0, "signals": 0, "oi_filter_rejections": 0,
                    "contracts_selected": 0, "completed_price_proxy_trades": 0, "no_prior_contract": 0,
                    "missing_entry_contract": 0, "invalid_target_ohlc": 0, "zero_volume_target": 0,
                    "lot_size_mismatch": 0, "no_direction_signal": 0}
                for s in STRATEGIES}
    trades_by_strategy = {s: [] for s in STRATEGIES}
    for idx in range(2, len(sessions)):
        prior_date, signal_date, entry_date = sessions[idx - 2], sessions[idx - 1], sessions[idx]
        for symbol in SYMBOLS:
            prev_underlying = underlying.get((prior_date, symbol))
            signal_underlying = underlying.get((signal_date, symbol))
            if not finite_positive(prev_underlying) or not finite_positive(signal_underlying):
                continue
            underlying_return = signal_underlying / prev_underlying - 1.0
            decision_rows = rows_by_day_symbol.get((signal_date, symbol), [])
            earlier_rows = rows_by_day_symbol.get((prior_date, symbol), [])
            target_rows = rows_by_day_symbol.get((entry_date, symbol), [])
            for strategy in STRATEGIES:
                c = coverage[strategy]
                c["signal_checks"] += 1
                side = signal_side(strategy, underlying_return, regime)
                if side is None:
                    c["no_direction_signal"] += 1
                    continue
                if strategy == "MOMENTUM_OI_CONFIRM":
                    # Determine a candidate expiry from current information before OI comparison.
                    provisional = select_contract(decision_rows, signal_date, side, signal_underlying)
                    if provisional is None:
                        c["no_prior_contract"] += 1
                        continue
                    if not oi_increased(decision_rows, earlier_rows, side, provisional["expiry"], signal_underlying):
                        c["oi_filter_rejections"] += 1
                        continue
                c["signals"] += 1
                selected = select_contract(decision_rows, signal_date, side, signal_underlying)
                if selected is None:
                    c["no_prior_contract"] += 1
                    continue
                c["contracts_selected"] += 1
                identity = exact_contract_key(selected)
                target = rows_by_day_symbol_contract.get((entry_date, symbol, identity))
                if target is None:
                    c["missing_entry_contract"] += 1
                    continue
                if not finite_positive(target.get("volume")):
                    c["zero_volume_target"] += 1
                    continue
                if not valid_ohlc(target) or not target.get("prices_complete"):
                    c["invalid_target_ohlc"] += 1
                    continue
                lot_size = int(round(float(selected["lot_size"])))
                if lot_size <= 0 or not finite_positive(target.get("lot_size")) or int(round(float(target["lot_size"])) ) != lot_size:
                    c["lot_size_mismatch"] += 1
                    continue
                trade = {
                    "entry_date": entry_date, "symbol": symbol, "strategy": strategy,
                    "open": float(target["open"]), "close": float(target["close"]),
                    "lot_size": lot_size,
                }
                trades_by_strategy[strategy].append(trade)
                c["completed_price_proxy_trades"] += 1

    scenario_results = []
    for strategy in STRATEGIES:
        trades = trades_by_strategy[strategy]
        for brokerage in BROKERAGE_LEVELS:
            for slip in SLIPPAGE_LEVELS:
                for fee_mult in FEE_MULTIPLIERS:
                    result = summarize_trades(trades, (brokerage, slip, fee_mult), sessions[2:])
                    result["strategy"] = strategy
                    scenario_results.append(result)

    summary_csv = out / "summary.csv"
    with summary_csv.open("w", encoding="utf-8", newline="") as handle:
        columns = ["strategy", "brokerage_per_order", "slippage_per_unit_per_side", "fee_multiplier",
                   "trade_count", "gross_pnl_rupees", "fees_rupees", "slippage_cost_rupees",
                   "net_pnl_rupees", "premium_deployed_rupees", "net_return_on_premium_pct",
                   "win_rate_pct", "average_net_per_trade_rupees", "median_net_per_trade_rupees",
                   "profit_factor", "max_drawdown_rupees"]
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in scenario_results:
            writer.writerow({key: row.get(key) for key in columns})

    # The primary registered case is 20/order, ₹0.25 adverse slippage each side, 1.0× fees.
    primary = [r for r in scenario_results if r["brokerage_per_order"] == 20.0
               and r["slippage_per_unit_per_side"] == 0.25 and r["fee_multiplier"] == 1.0]
    severe = [r for r in scenario_results if r["brokerage_per_order"] == 20.0
              and r["slippage_per_unit_per_side"] == 0.50 and r["fee_multiplier"] == 1.5]
    scenario_results = sorted(scenario_results, key=lambda r: (STRATEGIES.index(r["strategy"]), r["brokerage_per_order"],
                                                               r["slippage_per_unit_per_side"], r["fee_multiplier"]))
    decision["strategy_replay"] = "COMPLETE_ACCOUNTING_CHECKS_PASS"
    decision["primary_cost_case"] = {"brokerage_per_order": 20.0, "slippage_per_unit_per_side": 0.25, "fee_multiplier": 1.0}
    decision["strict_stress_case"] = {"brokerage_per_order": 20.0, "slippage_per_unit_per_side": 0.50, "fee_multiplier": 1.5}
    decision["promotion"] = "NONE"
    decision["reasons"].append("This is a short, previously inspected OHLC proxy sample; no strategy is promoted irrespective of simulated returns.")
    decision["reasons"].append("Daily open/close marks do not verify executable fills, spread, depth, latency, partial fills or market impact.")

    result = {
        "phase": PHASE, "run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "window": {"from_inclusive": args.from_date, "to_exclusive": args.to_date, "calendar_days": (end-start).days},
        "source": "NSE official daily UDiFF F&O archive", "symbols": list(SYMBOLS),
        "archive_hashes": archive_hashes, "daily_archives": daily_archives,
        "no_archive_dates": no_archive_dates, "fetch_errors": fetch_errors,
        "raw_rows_persisted": False, "raw_rows_in_artifact": False,
        "source_aggregate": source, "strategy_coverage": list(coverage.values()),
        "scenario_results": scenario_results,
        "primary_case": primary, "strict_stress_case": severe, "decision": decision,
    }

    # Verify trade counts are invariant across cost scenarios and net reconciles for each strategy.
    checks = []
    for strategy in STRATEGIES:
        group = [r for r in scenario_results if r["strategy"] == strategy]
        if len(group) != len(BROKERAGE_LEVELS) * len(SLIPPAGE_LEVELS) * len(FEE_MULTIPLIERS):
            checks.append("wrong scenario count for " + strategy)
        if len({r["trade_count"] for r in group}) > 1:
            checks.append("trade count changed across cost scenarios for " + strategy)
        for row in group:
            if row["gross_pnl_rupees"] is not None and abs(
                row["gross_pnl_rupees"] - row["slippage_cost_rupees"] - row["fees_rupees"] - row["net_pnl_rupees"]
            ) > 0.10:
                checks.append("aggregate P&L does not reconcile for " + strategy)
    if any(c["completed_price_proxy_trades"] != len(trades_by_strategy[c["strategy"]]) for c in coverage.values()):
        checks.append("coverage count does not match internal completed proxy trades")
    result["accounting_checks"] = {"status": "PASS" if not checks else "FAIL", "failures": checks,
                                    "scenario_rows": len(scenario_results)}
    if checks:
        decision["strategy_replay"] = "FAILED_ACCOUNTING_INVARIANT"
        decision["promotion"] = "NONE"
        decision["reasons"].extend(checks)
    elif not scenario_results or len(scenario_results) != 240:
        decision["strategy_replay"] = "FAILED_SCENARIO_COMPLETENESS"
        decision["reasons"].append("Expected 240 fixed strategy-cost scenario rows.")

    (out / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (out / "decision.json").write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    write_chart(scenario_results, out)
    (out / "PHASE108_REPORT.md").write_text(make_report(result), encoding="utf-8")
    return result


def money(value):
    if value is None:
        return "not estimable"
    if isinstance(value, str):
        return value
    return f"₹{value:,.2f}"


def make_report(result):
    decision = result["decision"]
    source = result["source_aggregate"]
    lines = [
        "# Phase 108 — EOD OHLC Options Strategy Pilot",
        "",
        f"**Run:** {result.get('run_id', 'unknown')}  ",
        f"**Window:** {result['window']['from_inclusive']} inclusive to {result['window']['to_exclusive']} exclusive  ",
        f"**Interpretation:** OHLC execution proxy only; not verified fills.  ",
        f"**Decision:** {decision.get('strategy_replay', 'NOT_RUN')}; promotion: NONE.",
        "",
        "## Source gate",
        "",
        f"- NSE archive sessions parsed: {sum(item.get('status') == 'ARCHIVE_PARSED' for item in result.get('daily_archives', []))}",
        f"- Selected/parsed rows: {source.get('selected_rows', 0)} / {source.get('parsed_rows', 0)}",
        f"- Identity completeness: {source.get('identity_completeness_pct', 0)}%",
        f"- OHLC completeness: {source.get('ohlc_completeness_pct', 0)}%",
        f"- Duplicate daily keys / date mismatches: {source.get('duplicate_daily_contract_keys', 0)} / {source.get('date_mismatch_rows', 0)}",
        f"- Invalid positive-volume OHLC rows: {source.get('invalid_ohlc_positive_volume_rows', 0)}",
        f"- Common sessions with all five underlying values: {source.get('sessions_with_all_five_underlyings', 0)}",
        f"- Raw market rows persisted or uploaded: {result.get('raw_rows_persisted', False)} / {result.get('raw_rows_in_artifact', False)}",
        "",
    ]
    if decision.get("strategy_replay", "").startswith("NOT_RUN"):
        lines += ["## Strategy replay blocked", "", *[f"- {reason}" for reason in decision.get("reasons", [])], ""]
        return "\n".join(lines)
    lines += [
        "## Coverage and proxy fills",
        "",
        "| Strategy | Signals | Contracts selected | Completed OHLC proxy trades | OI filter rejected | Missing next-session contract | Zero-volume target | Invalid target OHLC |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result.get("strategy_coverage", []):
        lines.append(f"| {row['strategy']} | {row['signals']} | {row['contracts_selected']} | {row['completed_price_proxy_trades']} | {row['oi_filter_rejections']} | {row['missing_entry_contract']} | {row['zero_volume_target']} | {row['invalid_target_ohlc']} |")
    lines += [
        "", "## Primary registered cost case",
        "",
        "Brokerage ₹20 per order, ₹0.25 adverse slippage per option unit on both sides, 1.0× modelled fees.",
        "",
        "| Strategy | Trades | Gross P&L | Model fees | Slippage cost | Net P&L | Net return on premium | Win rate | Profit factor | Max drawdown (₹) | Mean daily P&L 95% session-bootstrap CI |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in result.get("primary_case", []):
        ci = row.get("bootstrap_mean_daily_pnl", {})
        ci_text = "not estimable"
        if ci.get("ci95_low_rupees") is not None:
            ci_text = f"{money(ci['ci95_low_rupees'])} to {money(ci['ci95_high_rupees'])}"
        lines.append(
            f"| {row['strategy']} | {row['trade_count']} | {money(row['gross_pnl_rupees'])} | {money(row['fees_rupees'])} | {money(row['slippage_cost_rupees'])} | {money(row['net_pnl_rupees'])} | "
            f"{row.get('net_return_on_premium_pct', None)}% | {row.get('win_rate_pct', None)}% | {row.get('profit_factor', None)} | {money(row['max_drawdown_rupees'])} | {ci_text} |"
        )
    lines += [
        "", "## Strict stress case",
        "",
        "Brokerage ₹20 per order, ₹0.50 adverse slippage per option unit on both sides, 1.5× modelled fees.",
        "",
        "| Strategy | Trades | Net P&L | Net return on premium | Max drawdown (₹) |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in result.get("strict_stress_case", []):
        lines.append(f"| {row['strategy']} | {row['trade_count']} | {money(row['net_pnl_rupees'])} | {row.get('net_return_on_premium_pct', None)}% | {money(row['max_drawdown_rupees'])} |")
    lines += [
        "", "## Cost sensitivity chart",
        "",
        "![Net P&L sensitivity to assumed adverse slippage](figures/net_pnl_by_slippage.svg)",
        "",
        "## Interpretation and limits",
        "",
        "- The signal is formed using only the two prior sessions' underlying values. Contract selection uses only signal-session contract records, prior-session volume/OI, strike/expiry and lot size. The target session is used only to evaluate the registered open-to-close price proxy.",
        "- The six rules are prespecified exploratory candidates, not an optimized search. The 0.5% one-session return threshold is a fixed screening threshold, not optimized on this sample. OI is not intrinsically bullish or bearish; the OI rule is only a simple confirmation filter.",
        "- A price-proxy trade is counted only when the same expiry/strike/side appears on the target date with a positive-volume bar, internally consistent OHLC and matching lot size. Exclusions are enumerated; no price is interpolated.",
        "- Brokerage, statutory levies and GST are model estimates. Brokerage tiers are sensitivities, not confirmation of the user's Paytm Money account tier. The 1.5× case is a stress overlay, not a tax rule.",
        "- Applied slippage is an assumption, not observed bid/ask spread, queue/depth, latency, partial-fill or impact data. Bar open/close are not guaranteed order fills; the backtest cannot support execution or live-profitability claims.",
        "- This is one month of already-inspected data, with few independent sessions and correlated same-day stock trades. Bootstrap intervals are descriptive and do not validate a trading edge. Net return is divided by premium deployed, not total account equity. Drawdown is reported in rupees because no funded portfolio sizing rule was preregistered.",
        "- No strategy is promoted irrespective of the printed results. Further work requires a longer, independently frozen sample across multiple expiries/regimes and an execution evidence/licensing review.",
        "",
        "## Accounting and decision",
        "",
        f"- Accounting check: {result.get('accounting_checks', {}).get('status', 'NOT_RUN')}.",
        f"- Scenario rows: {result.get('accounting_checks', {}).get('scenario_rows', 0)} (expected 240).",
        "- Raw market rows and per-trade records are not published; aggregate summaries only.",
        *[f"- {reason}" for reason in decision.get("reasons", [])],
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-date", default=os.getenv("PHASE108_FROM_DATE", DEFAULT_FROM))
    parser.add_argument("--to-date", default=os.getenv("PHASE108_TO_DATE", DEFAULT_TO), help="exclusive")
    parser.add_argument("--out-dir", default="results/phase108")
    args = parser.parse_args()
    result = run(args)
    print(json.dumps({
        "phase": result["phase"], "run_id": result["run_id"],
        "source_gate": result["decision"]["source_gate"],
        "strategy_replay": result["decision"]["strategy_replay"],
        "promotion": result["decision"]["promotion"],
        "parsed_rows": result["source_aggregate"].get("parsed_rows"),
        "scenario_rows": result.get("accounting_checks", {}).get("scenario_rows", 0),
    }, sort_keys=True))
    if result["decision"]["source_gate"] != "PASS":
        raise SystemExit(2)
    if result["decision"]["strategy_replay"] not in ("COMPLETE_ACCOUNTING_CHECKS_PASS",):
        raise SystemExit(3)


if __name__ == "__main__":
    main()
