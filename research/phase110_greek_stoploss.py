#!/usr/bin/env python3
"""Phase 110 Greek stop-loss engine: exact-minute NIFTY weekly short strangle."""
from __future__ import annotations

import gc
import hashlib
import itertools
import json
import math
import os
import re
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from huggingface_hub import HfApi, hf_hub_download
from scipy.stats import ttest_1samp

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "phase110"
HF_REPO = "thetrademarkk/india-index-options-1m"
TZ = "Asia/Kolkata"
RATE, DIVIDEND, YEAR_DAYS = 0.06, 0.0, 365.25
TARGET_ABS_DELTA, MIN_PRE_ENTRY_OI = 0.15, 100
BAR = pd.Timedelta(minutes=1)
EXPIRY_CLOSE, ENTRY_TIME, SELECTION_TIME, EXIT_TIME = "15:30:00", "10:00:00", "09:59:00", "14:00:00"
PRIMARY_COST = {"brokerage_per_order": 20.0, "slippage_per_unit": 0.25, "fee_multiplier": 1.0}
BROKERAGE, SLIPPAGE, FEE_MULTIPLIERS = (10.0, 15.0, 20.0), (0.0, 0.05, 0.25, 0.50), (1.0, 1.5)
NET_DELTA_THRESHOLDS, GROSS_DELTA_THRESHOLDS = (0.20, 0.30, 0.40, 0.50, 0.60, 0.80), (0.40, 0.50, 0.60, 0.80, 1.00)
GAMMA_THRESHOLDS, VEGA_THRESHOLDS, THETA_THRESHOLDS = (0.10, 0.20, 0.30, 0.40, 0.50), (0.10, 0.20, 0.30, 0.40, 0.50), (0.00, 0.25, 0.50, 0.75)
MAX_HOLDOUT_CANDIDATES, BOOTSTRAP_REPS, RNG_SEED = 20, 3000, 20261023


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def localize_series(values: pd.Series) -> pd.Series:
    x = pd.to_datetime(values, errors="coerce")
    return x.dt.tz_localize(TZ) if x.dt.tz is None else x.dt.tz_convert(TZ)


def valid_ohlc(row: Any) -> bool:
    try:
        o, h, l, c = (float(row[k]) for k in ("open", "high", "low", "close"))
    except (TypeError, ValueError, KeyError):
        return False
    return all(math.isfinite(x) and x > 0 for x in (o, h, l, c)) and l <= min(o, c) and h >= max(o, c) and h >= l


def cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def bs_price(spot: float, strike: float, tau: float, sigma: float, typ: str) -> float:
    intrinsic = max(spot - strike, 0.0) if typ == "CE" else max(strike - spot, 0.0)
    if not all(math.isfinite(z) for z in (spot, strike, tau, sigma)) or spot <= 0 or strike <= 0 or tau <= 0 or sigma <= 0:
        return intrinsic
    root_t = math.sqrt(tau)
    d1 = (math.log(spot / strike) + (RATE - DIVIDEND + 0.5 * sigma * sigma) * tau) / (sigma * root_t)
    d2 = d1 - sigma * root_t
    if typ == "CE":
        return spot * math.exp(-DIVIDEND * tau) * cdf(d1) - strike * math.exp(-RATE * tau) * cdf(d2)
    return strike * math.exp(-RATE * tau) * cdf(-d2) - spot * math.exp(-DIVIDEND * tau) * cdf(-d1)


def implied_vol(spot: float, strike: float, tau: float, premium: float, typ: str) -> float | None:
    """Bisection IV; model-inconsistent observed premiums are rejected, not patched."""
    if typ not in {"CE", "PE"} or not all(math.isfinite(x) for x in (spot, strike, tau, premium)):
        return None
    if spot <= 0 or strike <= 0 or tau <= 0 or premium <= 0:
        return None
    # European Black-Scholes no-arbitrage bounds, not American/intrinsic-payoff
    # bounds. In particular, a deep-ITM European put can trade below K-S because
    # the strike payment is discounted; using max(K-S, 0) incorrectly rejects it.
    disc_spot = spot * math.exp(-DIVIDEND * tau)
    disc_strike = strike * math.exp(-RATE * tau)
    model_lower = max(disc_spot - disc_strike, 0.0) if typ == "CE" else max(disc_strike - disc_spot, 0.0)
    upper = disc_spot if typ == "CE" else disc_strike
    tol = max(0.05, 1e-7 * max(spot, strike, premium))
    if premium < model_lower - tol or premium >= upper - tol:
        return None
    lo, hi = 1e-5, 5.0
    p_lo, p_hi = bs_price(spot, strike, tau, lo, typ), bs_price(spot, strike, tau, hi, typ)
    if premium < p_lo - tol or premium > p_hi + tol:
        return None
    for _ in range(64):
        mid = (lo + hi) / 2.0
        if bs_price(spot, strike, tau, mid, typ) < premium:
            lo = mid
        else:
            hi = mid
    sigma = (lo + hi) / 2.0
    if not math.isfinite(sigma) or sigma <= 0 or abs(bs_price(spot, strike, tau, sigma, typ) - premium) > max(0.05, tol):
        return None
    return sigma


def bs_greeks(spot: float, strike: float, tau: float, sigma: float, typ: str) -> dict[str, float] | None:
    """Delta per spot point; gamma per spot-point squared; vega per 1 IV point; theta/calendar day."""
    if not all(math.isfinite(x) for x in (spot, strike, tau, sigma)) or min(spot, strike, tau, sigma) <= 0:
        return None
    root_t = math.sqrt(tau)
    d1 = (math.log(spot / strike) + (RATE - DIVIDEND + 0.5 * sigma * sigma) * tau) / (sigma * root_t)
    d2 = d1 - sigma * root_t
    n1, n2 = cdf(d1), cdf(d2)
    disc_q, disc_r = math.exp(-DIVIDEND * tau), math.exp(-RATE * tau)
    delta = disc_q * n1 if typ == "CE" else disc_q * (n1 - 1.0)
    gamma = disc_q * pdf(d1) / (spot * sigma * root_t)
    vega = spot * disc_q * pdf(d1) * root_t / 100.0
    common = -spot * disc_q * pdf(d1) * sigma / (2.0 * root_t)
    if typ == "CE":
        theta_year = common - RATE * strike * disc_r * n2 + DIVIDEND * spot * disc_q * n1
    else:
        theta_year = common + RATE * strike * disc_r * cdf(-d2) - DIVIDEND * spot * disc_q * cdf(-d1)
    out = {"delta": delta, "gamma": gamma, "vega": vega, "theta": theta_year / YEAR_DAYS}
    return out if all(math.isfinite(v) for v in out.values()) else None


def historical_lot_size(expiry: str) -> int | None:
    """NIFTY weekly lot schedule from NSE transition circulars; gaps are deliberately blocked."""
    d = date.fromisoformat(expiry)
    if d < date(2021, 8, 1):
        return 75
    if date(2021, 8, 1) <= d <= date(2024, 4, 25):
        return 50
    # NSE FAOP61415: first weekly expiry with the 25-lot size was 02-May-2024.
    if date(2024, 5, 2) <= d <= date(2024, 12, 19):
        return 25
    # NSE FAOP64625: first weekly expiry with the new 75-lot size was 02-Jan-2025.
    if date(2025, 1, 2) <= d <= date(2025, 12, 23):
        return 75
    # NSE FAOP70616: first weekly expiry with the 65-lot size was 06-Jan-2026.
    if d >= date(2026, 1, 6):
        return 65
    return None


def make_cost_grid() -> list[dict[str, Any]]:
    return [{"cost_id": f"B{int(b)}_S{s:.2f}_F{f:.1f}", "brokerage_per_order": b,
             "slippage_per_unit": s, "fee_multiplier": f}
            for b, s, f in itertools.product(BROKERAGE, SLIPPAGE, FEE_MULTIPLIERS)]


def stable_id(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()[:16]


def make_configs() -> list[dict[str, Any]]:
    """Register every Greek subset, threshold combination, delta definition, and simultaneous OR/AND logic."""
    domains = {
        "delta": [None, *NET_DELTA_THRESHOLDS],
        "gamma": [None, *GAMMA_THRESHOLDS],
        "vega": [None, *VEGA_THRESHOLDS],
        "theta": [None, *THETA_THRESHOLDS],
    }
    rows = [{"config_id": "NO_STOP_REFERENCE", "name": "NO_STOP_REFERENCE", "delta_mode": "NONE",
             "delta_threshold": None, "gamma_threshold": None, "vega_threshold": None, "theta_threshold": None,
             "aggregation": "NONE", "active_count": 0, "active_criteria": "NONE"}]
    # Signed-net-delta rules (and the non-delta subsets, only once).
    for d, g, v, t in itertools.product(domains["delta"], domains["gamma"], domains["vega"], domains["theta"]):
        if all(x is None for x in (d, g, v, t)):
            continue
        active_count = sum(x is not None for x in (d, g, v, t))
        aggregations = ["ANY"] if active_count == 1 else ["ANY", "ALL"]
        mode = "NET_ABS" if d is not None else "NONE"
        payload0 = {"delta_mode": mode, "delta_threshold": None if d is None else float(d),
                    "gamma_threshold": None if g is None else float(g),
                    "vega_threshold": None if v is None else float(v),
                    "theta_threshold": None if t is None else float(t)}
        active = [f"{k.upper()}={val:.2f}" for k, val in [
            ("delta", payload0["delta_threshold"]), ("gamma", payload0["gamma_threshold"]),
            ("vega", payload0["vega_threshold"]), ("theta", payload0["theta_threshold"])
        ] if val is not None]
        for agg in aggregations:
            p = {**payload0, "aggregation": agg}
            rows.append({"config_id": stable_id(p), "name": "|".join(active) + f"|{agg}",
                         **p, "active_count": active_count, "active_criteria": "+".join(a.split("=")[0] for a in active)})
    # Gross-absolute delta is an alternative only when delta is active.
    for d, g, v, t in itertools.product(GROSS_DELTA_THRESHOLDS, domains["gamma"], domains["vega"], domains["theta"]):
        active_count = 1 + sum(x is not None for x in (g, v, t))
        aggregations = ["ANY"] if active_count == 1 else ["ANY", "ALL"]
        p0 = {"delta_mode": "GROSS_ABS", "delta_threshold": float(d),
              "gamma_threshold": None if g is None else float(g),
              "vega_threshold": None if v is None else float(v),
              "theta_threshold": None if t is None else float(t)}
        active = [f"{k.upper()}={val:.2f}" for k, val in [
            ("delta", p0["delta_threshold"]), ("gamma", p0["gamma_threshold"]),
            ("vega", p0["vega_threshold"]), ("theta", p0["theta_threshold"])
        ] if val is not None]
        for agg in aggregations:
            p = {**p0, "aggregation": agg}
            rows.append({"config_id": stable_id(p), "name": "|".join(active) + f"|{agg}",
                         **p, "active_count": active_count, "active_criteria": "+".join(a.split("=")[0] for a in active)})
    ids = [r["config_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise AssertionError("Duplicate Phase110 strategy configuration IDs")
    return rows


def normalize_option_type(x: Any) -> str:
    s = str(x).upper().strip()
    return {"CALL": "CE", "C": "CE", "CE": "CE", "PUT": "PE", "P": "PE", "PE": "PE"}.get(s, s)


def load_index(path: Path) -> tuple[int, dict[pd.Timestamp, dict[str, float]], Counter]:
    df = pd.read_parquet(path)
    required = {"timestamp", "open", "high", "low", "close"}
    if not required.issubset(df.columns):
        raise RuntimeError(f"Index source missing columns: {sorted(required-set(df.columns))}")
    df = df[["timestamp", "open", "high", "low", "close"]].copy()
    df["timestamp"] = localize_series(df["timestamp"])
    for col in ("open", "high", "low", "close"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    dup = df["timestamp"].duplicated(keep=False)
    counts = Counter({"index_duplicate_timestamp_rows": int(dup.sum())})
    df = df.loc[~dup].copy()  # ambiguous timestamps are excluded rather than arbitrary-deduplicated
    records = {}
    for r in df.itertuples(index=False):
        row = {"open": float(r.open), "high": float(r.high), "low": float(r.low), "close": float(r.close)}
        if valid_ohlc(row):
            records[pd.Timestamp(r.timestamp)] = row
    valid_row_count = int(df["timestamp"].isin(records).sum())
    return valid_row_count, records, counts


def normalize_option_df(path: Path, target_expiry: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load only required fields and filter to the exact expiry/contract universe."""
    schema_names = set(pq.ParquetFile(path).schema.names)
    required = ["timestamp", "option_type", "strike", "open", "high", "low", "close", "open_interest"]
    missing = sorted(set(required) - schema_names)
    if missing:
        raise RuntimeError(f"Option parquet schema missing required columns: {missing}")
    # Preserve exact identity fields when present; expiry is mandatory for correctness.
    if "expiry" not in schema_names:
        raise RuntimeError("Option parquet has no expiry column; exact contract identity cannot be established")
    keep = required + ["expiry"] + ([ "symbol" ] if "symbol" in schema_names else [])
    df = pd.read_parquet(path, columns=keep)
    df["timestamp"] = localize_series(df["timestamp"])
    df["option_type"] = df["option_type"].map(normalize_option_type)
    df["expiry"] = pd.to_datetime(df["expiry"], errors="coerce").dt.strftime("%Y-%m-%d")
    for col in ("strike", "open", "high", "low", "close", "open_interest"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    rows_before_expiry_filter = int(len(df))
    df = df.loc[df["expiry"].eq(target_expiry)].copy()
    if df.empty:
        raise RuntimeError(f"No contracts with exact target expiry {target_expiry} in {path.name}")
    audit = {
        "rows_before_expiry_filter": rows_before_expiry_filter,
        "rows_for_target_expiry": int(len(df)),
        "rows_other_expiries_removed": rows_before_expiry_filter - int(len(df)),
        "schema_columns": sorted(schema_names),
        "symbol_column_available": "symbol" in schema_names,
    }
    return df.dropna(subset=["timestamp", "strike"]), audit


def select_entry_legs(df: pd.DataFrame, selection_ts: pd.Timestamp, entry_ts: pd.Timestamp,
                      spot_map: dict[pd.Timestamp, dict[str, float]], expiry: str) -> tuple[dict[str, Any] | None, str]:
    prior_spot = spot_map.get(selection_ts)
    snap = df.loc[df["timestamp"].eq(selection_ts)]
    if prior_spot is None or snap.empty:
        return None, "MISSING_EXACT_0959_SPOT_OR_OPTION_BAR"
    if not valid_ohlc(prior_spot):
        return None, "INVALID_0959_SPOT_OHLC"
    # Duplicate source rows can be repeated under different symbol labels. A row is
    # deduplicated only when all market/contract fields agree; conflicting prices,
    # volume or OI for the same contract-minute remain a hard exclusion.
    identity_fields = [x for x in (
        "timestamp", "expiry", "option_type", "strike", "open", "high", "low",
        "close", "volume", "open_interest", "trading_day"
    ) if x in snap.columns]
    snap = snap.drop_duplicates(subset=identity_fields, keep="first")
    if snap.duplicated(["option_type", "strike"], keep=False).any():
        return None, "DUPLICATE_SELECTION_CONTRACT_MINUTE"
    expiry_ts = pd.Timestamp(f"{expiry} {EXPIRY_CLOSE}", tz=TZ)
    tau = (expiry_ts - (selection_ts + BAR)).total_seconds() / (YEAR_DAYS * 86400.0)
    eligible = {"CE": [], "PE": []}
    spot = float(prior_spot["close"])
    for r in snap.itertuples(index=False):
        typ = str(r.option_type)
        if typ not in eligible:
            continue
        if not valid_ohlc({"open": r.open, "high": r.high, "low": r.low, "close": r.close}):
            continue
        if not math.isfinite(float(r.open_interest)) or float(r.open_interest) < MIN_PRE_ENTRY_OI:
            continue
        strike, premium = float(r.strike), float(r.close)
        iv = implied_vol(spot, strike, tau, premium, typ)
        if iv is None:
            continue
        g = bs_greeks(spot, strike, tau, iv, typ)
        if g is not None:
            eligible[typ].append({"type": typ, "strike": strike, "premium_prior": premium,
                "oi_prior": float(r.open_interest), "iv_prior": iv, "delta_prior": g["delta"],
                "distance_spot": abs(strike - spot)})
    selected = {}
    for typ in ("CE", "PE"):
        if not eligible[typ]:
            return None, f"NO_VALID_0_15_DELTA_{typ}_WITH_PRE_ENTRY_OI"
        selected[typ] = min(eligible[typ], key=lambda x: (abs(abs(x["delta_prior"])-TARGET_ABS_DELTA), x["distance_spot"], x["strike"]))
    entry_snap = df.loc[df["timestamp"].eq(entry_ts)]
    if entry_snap.empty:
        return None, "MISSING_EXACT_1000_ENTRY_BAR"
    for typ in ("CE", "PE"):
        mask = entry_snap["option_type"].eq(typ).to_numpy() & np.isclose(entry_snap["strike"].to_numpy(float), selected[typ]["strike"], rtol=0, atol=1e-9)
        matches = entry_snap.loc[mask]
        if len(matches) != 1 or not valid_ohlc(matches.iloc[0]):
            return None, f"ENTRY_BAR_MISSING_INVALID_OR_DUPLICATE_{typ}"
        r = matches.iloc[0]
        for col in ("open", "high", "low", "close"):
            selected[typ][f"entry_{col}"] = float(r[col])
    spot_entry = spot_map.get(entry_ts)
    if spot_entry is None or not valid_ohlc(spot_entry):
        return None, "MISSING_OR_INVALID_EXACT_1000_SPOT"
    entry_tau = (expiry_ts - entry_ts).total_seconds() / (YEAR_DAYS * 86400.0)
    entry_greeks = {}
    for typ in ("CE", "PE"):
        iv = implied_vol(float(spot_entry["open"]), selected[typ]["strike"], entry_tau, selected[typ]["entry_open"], typ)
        if iv is None:
            return None, f"ENTRY_OPEN_HAS_NO_VALID_MODEL_IV_{typ}"
        gr = bs_greeks(float(spot_entry["open"]), selected[typ]["strike"], entry_tau, iv, typ)
        if gr is None:
            return None, f"ENTRY_OPEN_HAS_NO_VALID_MODEL_GREEKS_{typ}"
        entry_greeks[typ] = gr
        selected[typ].update({"entry_iv": iv, "entry_delta": gr["delta"], "entry_gamma": gr["gamma"],
                              "entry_vega": gr["vega"], "entry_theta": gr["theta"]})
    return {"legs": selected, "spot_entry": float(spot_entry["open"]), "entry_greeks": entry_greeks}, "PASS"


def expected_market_minutes(entry_ts: pd.Timestamp, exit_ts: pd.Timestamp,
                            spot_map: dict[pd.Timestamp, dict[str, float]]) -> pd.DatetimeIndex:
    """Build observed-session minute OPEN timestamps, skipping nights/weekends/holidays."""
    first_day, last_day = entry_ts.date(), exit_ts.date()
    observed_sessions = sorted({
        ts.date() for ts in spot_map
        if first_day <= ts.date() <= last_day
        and datetime.strptime("09:15:00", "%H:%M:%S").time() <= ts.time()
        < datetime.strptime("15:30:00", "%H:%M:%S").time()
    })
    if first_day not in observed_sessions or last_day not in observed_sessions:
        return pd.DatetimeIndex([])
    pieces = []
    for day in observed_sessions:
        start = entry_ts if day == first_day else pd.Timestamp(f"{day.isoformat()} 09:15:00", tz=TZ)
        end = exit_ts if day == last_day else pd.Timestamp(f"{day.isoformat()} 15:29:00", tz=TZ)
        if start > end:
            continue
        pieces.append(pd.date_range(start, end, freq="min"))
    if not pieces:
        return pd.DatetimeIndex([])
    result = pieces[0]
    for piece in pieces[1:]:
        result = result.append(piece)
    if not result.is_monotonic_increasing or result.has_duplicates:
        raise ValueError("Invalid observed-session minute schedule")
    return result


def prepare_event(df: pd.DataFrame, spot_map: dict[pd.Timestamp, dict[str, float]],
                  expiry: str, previous_expiry: str, entry_date: date, split_name: str,
                  event_id: str, lot_size: int) -> tuple[dict[str, Any] | None, str]:
    entry_ts = pd.Timestamp(f"{entry_date.isoformat()} {ENTRY_TIME}", tz=TZ)
    select_ts = pd.Timestamp(f"{entry_date.isoformat()} {SELECTION_TIME}", tz=TZ)
    exit_ts = pd.Timestamp(f"{expiry} {EXIT_TIME}", tz=TZ)
    selection, status = select_entry_legs(df, select_ts, entry_ts, spot_map, expiry)
    if selection is None:
        return None, status
    legs = selection["legs"]
    cstrike, pstrike = legs["CE"]["strike"], legs["PE"]["strike"]
    expected = expected_market_minutes(entry_ts, exit_ts, spot_map)
    if len(expected) == 0 or entry_ts not in expected or exit_ts not in expected:
        return None, "INVALID_TRADING_SESSION_SCHEDULE"
    # The path deliberately spans active market minutes only. A missing expected
    # minute in a source leg/index will still exclude the entire campaign below.
    call = df.loc[df["option_type"].eq("CE") & np.isclose(df["strike"].to_numpy(float), cstrike, rtol=0, atol=1e-9)
                  & df["timestamp"].between(entry_ts, exit_ts)].copy()
    put = df.loc[df["option_type"].eq("PE") & np.isclose(df["strike"].to_numpy(float), pstrike, rtol=0, atol=1e-9)
                 & df["timestamp"].between(entry_ts, exit_ts)].copy()
    if call["timestamp"].duplicated(keep=False).any() or put["timestamp"].duplicated(keep=False).any():
        return None, "DUPLICATE_SELECTED_LEG_MINUTE"
    call = call.set_index("timestamp").reindex(expected)
    put = put.set_index("timestamp").reindex(expected)
    if call["open"].isna().any() or put["open"].isna().any():
        return None, f"INCOMPLETE_SELECTED_LEG_PATH_CALL_{int(call['open'].isna().sum())}_PUT_{int(put['open'].isna().sum())}"
    spot_rows = [spot_map.get(t) for t in expected]
    if any(x is None for x in spot_rows):
        return None, "INCOMPLETE_EXACT_SPOT_PATH"
    for i in range(len(expected)):
        if not valid_ohlc(call.iloc[i]) or not valid_ohlc(put.iloc[i]) or not valid_ohlc(spot_rows[i]):
            return None, "INVALID_OHLC_DURING_MONITORING_PATH"
    credit = float(legs["CE"]["entry_open"] + legs["PE"]["entry_open"])
    if not math.isfinite(credit) or credit <= 0:
        return None, "NONPOSITIVE_ENTRY_CREDIT"
    expiry_ts = pd.Timestamp(f"{expiry} {EXPIRY_CLOSE}", tz=TZ)
    eg = selection["entry_greeks"]
    entry_theta = -(eg["CE"]["theta"] + eg["PE"]["theta"])
    theta_valid = math.isfinite(entry_theta) and entry_theta > 0
    metrics = {k: [] for k in ("net_abs_delta", "gross_abs_delta", "gamma_risk", "vega_risk", "theta_ratio")}
    for i, ts in enumerate(expected[:-1]):
        tau = (expiry_ts - (ts + BAR)).total_seconds() / (YEAR_DAYS * 86400.0)
        spot_close = float(spot_rows[i]["close"])
        gs = {}
        for typ, frame, strike in (("CE", call, cstrike), ("PE", put, pstrike)):
            iv = implied_vol(spot_close, float(strike), tau, float(frame.iloc[i]["close"]), typ)
            if iv is None:
                return None, f"INVALID_GREEK_IV_{typ}_AT_{ts.strftime('%H:%M')}"
            g = bs_greeks(spot_close, float(strike), tau, iv, typ)
            if g is None:
                return None, f"INVALID_GREEKS_{typ}_AT_{ts.strftime('%H:%M')}"
            gs[typ] = g
        net_d = -(gs["CE"]["delta"] + gs["PE"]["delta"])
        net_g = -(gs["CE"]["gamma"] + gs["PE"]["gamma"])
        net_v = -(gs["CE"]["vega"] + gs["PE"]["vega"])
        net_t = -(gs["CE"]["theta"] + gs["PE"]["theta"])
        metrics["net_abs_delta"].append(abs(net_d))
        metrics["gross_abs_delta"].append(abs(gs["CE"]["delta"]) + abs(gs["PE"]["delta"]))
        metrics["gamma_risk"].append(max(0.0, -net_g) * 0.5 * (spot_close * 0.005) ** 2 / credit)
        metrics["vega_risk"].append(max(0.0, -net_v) / credit)
        metrics["theta_ratio"].append(net_t / entry_theta if theta_valid else math.nan)
    return {
        "event_id": event_id, "previous_expiry": previous_expiry, "expiry": expiry,
        "entry_date": entry_date.isoformat(), "entry_ts": entry_ts, "exit_ts": exit_ts,
        "split": split_name, "lot_size": lot_size, "call_strike": cstrike, "put_strike": pstrike,
        "call_delta_prior": legs["CE"]["delta_prior"], "put_delta_prior": legs["PE"]["delta_prior"],
        "call_entry": float(legs["CE"]["entry_open"]), "put_entry": float(legs["PE"]["entry_open"]),
        "entry_credit": credit, "spot_entry": selection["spot_entry"],
        "entry_net_delta": -(eg["CE"]["delta"] + eg["PE"]["delta"]),
        "entry_gross_delta": abs(eg["CE"]["delta"]) + abs(eg["PE"]["delta"]),
        "entry_net_theta": entry_theta, "theta_entry_valid": theta_valid,
        "signal_timestamps": list(expected[:-1]), "exit_timestamps": list(expected[1:]),
        "exit_call_open": call["open"].to_numpy(dtype=float)[1:],
        "exit_put_open": put["open"].to_numpy(dtype=float)[1:],
        "base_call_exit": float(call.iloc[-1]["open"]), "base_put_exit": float(put.iloc[-1]["open"]),
        "metrics": {k: np.asarray(v, dtype=float) for k, v in metrics.items()},
    }, "PASS"


def condition_matrix(event: dict[str, Any], cfg: dict[str, Any]) -> np.ndarray:
    checks = []
    if cfg["delta_threshold"] is not None:
        key = "net_abs_delta" if cfg["delta_mode"] == "NET_ABS" else "gross_abs_delta"
        checks.append(event["metrics"][key] >= float(cfg["delta_threshold"]))
    if cfg["gamma_threshold"] is not None:
        checks.append(event["metrics"]["gamma_risk"] >= float(cfg["gamma_threshold"]))
    if cfg["vega_threshold"] is not None:
        checks.append(event["metrics"]["vega_risk"] >= float(cfg["vega_threshold"]))
    if cfg["theta_threshold"] is not None:
        x = event["metrics"]["theta_ratio"]
        checks.append(np.isfinite(x) & (x <= float(cfg["theta_threshold"])))
    if not checks:
        return np.zeros(len(event["signal_timestamps"]), dtype=bool)
    x = np.vstack(checks)
    return np.any(x, axis=0) if cfg["aggregation"] == "ANY" else np.all(x, axis=0)


def find_exit(event: dict[str, Any], cfg: dict[str, Any]) -> tuple[float, float, pd.Timestamp, str, int | None]:
    if cfg["active_count"] == 0:
        return event["base_call_exit"], event["base_put_exit"], event["exit_ts"], "FIXED_14_00", None
    if cfg["theta_threshold"] is not None and not event["theta_entry_valid"]:
        raise ValueError("THETA_ENTRY_UNAVAILABLE")
    hit = np.flatnonzero(condition_matrix(event, cfg))
    if len(hit) == 0:
        return event["base_call_exit"], event["base_put_exit"], event["exit_ts"], "FIXED_14_00", None
    i = int(hit[0])
    return float(event["exit_call_open"][i]), float(event["exit_put_open"][i]), event["exit_timestamps"][i], "GREEK_STOP_NEXT_OPEN", i


def transaction_rates(trade_date: str) -> dict[str, float]:
    """Date-effective India index-options transaction charges (decimal rates)."""
    d = date.fromisoformat(trade_date)
    stt = 0.000625 if d < date(2024, 10, 1) else (0.001 if d < date(2026, 4, 1) else 0.0015)
    if d >= date(2026, 3, 1):
        exchange, ipft = 0.000355299, 0.000000001
    elif d >= date(2024, 10, 1):
        exchange, ipft = 0.0003503, 0.000005
    else:
        exchange, ipft = 0.000495, 0.000005
    return {"stt_sell_premium": stt, "exchange": exchange, "ipft": ipft,
            "sebi": 0.000001, "stamp_buy_premium": 0.00003}


def premium_fee_model(entry_call: float, entry_put: float, exit_call: float, exit_put: float,
                      lot: int, entry_date: str, exit_date: str, cost: dict[str, Any]) -> dict[str, float] | None:
    slip = float(cost["slippage_per_unit"])
    ec, ep, xc, xp = entry_call - slip, entry_put - slip, exit_call + slip, exit_put + slip
    if min(ec, ep, entry_call, entry_put, exit_call, exit_put) <= 0:
        return None
    gross = (entry_call + entry_put - exit_call - exit_put) * lot
    slippage_cost = 4.0 * slip * lot
    brokerage = 4.0 * float(cost["brokerage_per_order"])
    sell_turnover, buy_turnover = (ec + ep) * lot, (xc + xp) * lot
    entry_rates, exit_rates = transaction_rates(entry_date), transaction_rates(exit_date)
    stt_raw = sell_turnover * entry_rates["stt_sell_premium"]
    exchange_raw = sell_turnover * entry_rates["exchange"] + buy_turnover * exit_rates["exchange"]
    ipft_raw = sell_turnover * entry_rates["ipft"] + buy_turnover * exit_rates["ipft"]
    sebi_raw = (sell_turnover + buy_turnover) * entry_rates["sebi"]
    stamp_raw = buy_turnover * exit_rates["stamp_buy_premium"]
    fm = float(cost["fee_multiplier"])
    stt, exchange, ipft, sebi, stamp = (
        stt_raw * fm, exchange_raw * fm, ipft_raw * fm, sebi_raw * fm, stamp_raw * fm
    )
    gst = 0.18 * brokerage + 0.18 * (exchange_raw + ipft_raw + sebi_raw) * fm
    fees = stt + exchange + ipft + sebi + stamp + gst
    return {
        "gross_pnl_inr": gross, "slippage_cost_inr": slippage_cost, "brokerage_inr": brokerage,
        "stt_inr": stt, "exchange_ipft_inr": exchange + ipft, "exchange_fee_inr": exchange,
        "ipft_inr": ipft, "sebi_fee_inr": sebi, "stamp_duty_inr": stamp,
        "gst_inr": gst, "statutory_fees_inr": fees, "total_costs_inr": slippage_cost + brokerage + fees,
        "net_pnl_inr": gross - slippage_cost - brokerage - fees,
        "entry_credit_inr": (entry_call + entry_put) * lot,
        "entry_fill_turnover_inr": sell_turnover, "exit_fill_turnover_inr": buy_turnover,
    }


def summarize_trade_rows(rows: list[dict[str, Any]], expected: int) -> dict[str, Any]:
    if not rows:
        return {"expected_events": int(expected), "trades": 0, "coverage_pct": 0.0, "gross_pnl_inr": 0.0,
                "net_pnl_inr": 0.0, "net_return_on_credit_pct": math.nan, "win_rate_pct": math.nan,
                "mean_net_trade_inr": math.nan, "median_net_trade_inr": math.nan, "profit_factor": math.nan,
                "max_drawdown_inr": 0.0, "median_holding_minutes": math.nan}
    ordered = sorted(rows, key=lambda r: (r["expiry"], r.get("entry_date", "")))
    vals = np.asarray([r["net_pnl_inr"] for r in ordered], dtype=float)
    gross = np.asarray([r["gross_pnl_inr"] for r in ordered], dtype=float)
    credits = np.asarray([r["entry_credit_inr"] for r in ordered], dtype=float)
    profits, losses = float(vals[vals > 0].sum()), float(-vals[vals < 0].sum())
    cum = np.cumsum(vals)
    dd = np.maximum.accumulate(np.maximum(cum, 0)) - cum
    holds = [r.get("holding_minutes", math.nan) for r in ordered]
    return {"expected_events": int(expected), "trades": len(ordered),
            "coverage_pct": float(100 * len(ordered) / expected) if expected else 0.0,
            "gross_pnl_inr": float(gross.sum()), "net_pnl_inr": float(vals.sum()),
            "net_return_on_credit_pct": float(100 * vals.sum() / credits.sum()) if credits.sum() else math.nan,
            "win_rate_pct": float(100 * (vals > 0).mean()), "mean_net_trade_inr": float(vals.mean()),
            "median_net_trade_inr": float(np.median(vals)),
            "profit_factor": float(profits/losses) if losses > 0 else (math.inf if profits > 0 else math.nan),
            "max_drawdown_inr": float(dd.max()) if len(dd) else 0.0,
            "median_holding_minutes": float(np.nanmedian(holds)) if len(holds) else math.nan}


def test_pvalue(rows: list[dict[str, Any]]) -> float:
    a = np.asarray([r["net_pnl_inr"] for r in rows], dtype=float)
    if len(a) < 2 or not np.isfinite(a).all():
        return 1.0
    try:
        p = float(ttest_1samp(a, 0.0, alternative="greater").pvalue)
        return p if math.isfinite(p) else 1.0
    except Exception:
        return 1.0


def holm_adjust(pvals: dict[str, float]) -> dict[str, float]:
    rows, out, running = sorted(pvals.items(), key=lambda x: x[1]), {}, 0.0
    m = len(rows)
    for rank, (key, value) in enumerate(rows):
        running = max(running, min(1.0, (m - rank) * max(0.0, min(1.0, float(value)))))
        out[key] = running
    return out


def bootstrap_ci(values: list[float], seed: int) -> tuple[float, float]:
    a = np.asarray(values, dtype=float)
    if len(a) < 2 or not np.isfinite(a).all():
        return math.nan, math.nan
    rng, boot = np.random.default_rng(seed), []
    for start in range(0, BOOTSTRAP_REPS, 250):
        n = min(250, BOOTSTRAP_REPS - start)
        boot.extend(a[rng.integers(0, len(a), size=(n, len(a)))].mean(axis=1).tolist())
    return float(np.quantile(boot, .025)), float(np.quantile(boot, .975))


def write_svg_figures(validation: pd.DataFrame, full_grid: pd.DataFrame) -> list[str]:
    paths = []
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        d = OUT / "figures"
        d.mkdir(parents=True, exist_ok=True)
        top = validation.sort_values("net_pnl_inr", ascending=False).head(15).sort_values("net_pnl_inr")
        if len(top):
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.barh(top["name"].astype(str), top["paired_uplift_sum_inr"])
            ax.set_xlabel("Validation net uplift vs no-stop (INR, primary cost case, one lot)")
            ax.set_title("Top Greek-stop rules by validation uplift; not holdout-ranked")
            fig.tight_layout()
            p = d / "validation_top_rules.svg"
            fig.savefig(p, format="svg")
            plt.close(fig)
            paths.append(str(p.relative_to(ROOT)))
        d040 = full_grid.loc[
            full_grid["split"].eq("validation")
            & full_grid["name"].astype(str).str.contains("DELTA=0.40", regex=False)
            & (full_grid["brokerage_per_order"] == PRIMARY_COST["brokerage_per_order"])
            & (full_grid["fee_multiplier"] == PRIMARY_COST["fee_multiplier"])
        ]
        if len(d040):
            sens = d040.groupby("slippage_per_unit", as_index=False)["paired_uplift_sum_inr"].median()
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.plot(sens["slippage_per_unit"], sens["paired_uplift_sum_inr"], marker="o")
            ax.set_xlabel("Adverse slippage per option unit per side (INR)")
            ax.set_ylabel("Median paired uplift vs no-stop (INR)")
            ax.set_title("0.40 delta rules: paired uplift under slippage stress")
            fig.tight_layout()
            p = d / "delta040_slippage_sensitivity.svg"
            fig.savefig(p, format="svg")
            plt.close(fig)
            paths.append(str(p.relative_to(ROOT)))
    except Exception as exc:
        (OUT / "figure_generation_error.txt").write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
    return paths


def event_id_for(prev_expiry: str, expiry: str, entry_date: date) -> str:
    return f"{prev_expiry}_{expiry}_{entry_date.isoformat()}"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for p in OUT.glob("*"):
        if p.is_file() and p.suffix in {".csv", ".json", ".md"}:
            p.unlink()
    token = os.environ.get("HF_TOKEN")
    revision_request = os.environ.get("PHASE110_DATASET_REVISION", "main").strip() or "main"
    api = HfApi(token=token or None)
    info = api.dataset_info(HF_REPO, revision=revision_request)
    revision = str(info.sha)
    source_list = api.list_repo_files(repo_id=HF_REPO, repo_type="dataset", revision=revision)
    expiry_files = {}
    for name in source_list:
        m = re.fullmatch(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet", name)
        if m:
            expiry_files[m.group(1)] = name
    expiries = sorted(expiry_files)
    if len(expiries) < 3:
        raise RuntimeError(f"Too few option expiry files at resolved revision {revision}: {len(expiries)}")
    index_path = Path(hf_hub_download(repo_id=HF_REPO, filename="index/NIFTY.parquet", repo_type="dataset",
                                     revision=revision, token=token))
    index_sha = sha256_file(index_path)
    index_rows_valid, spot_map, index_counts = load_index(index_path)
    times = [datetime.strptime(s, "%H:%M:%S").time() for s in ("09:15:00", "15:30:00")]
    sessions = sorted({ts.date() for ts in spot_map if times[0] <= ts.time() <= times[1]})
    if not sessions:
        raise RuntimeError("No valid NIFTY session dates")
    session_set = set(sessions)
    exclusions, source_audit, source_errors, scheduled = [], [], [], []
    eligible_events = []
    long_gaps = 0
    for j in range(1, len(expiries)):
        prev_exp, expiry = expiries[j-1], expiries[j]
        gap = (date.fromisoformat(expiry) - date.fromisoformat(prev_exp)).days
        if gap < 4 or gap > 10:
            long_gaps += 1
            continue
        prev_date = date.fromisoformat(prev_exp)
        next_sessions = [d for d in sessions if d > prev_date]
        if not next_sessions:
            exclusions.append({"event_id": f"{prev_exp}_{expiry}", "previous_expiry": prev_exp, "expiry": expiry,
                               "split": "UNKNOWN", "reason": "NO_OBSERVED_SESSION_AFTER_PREVIOUS_EXPIRY"})
            continue
        entry_date = next_sessions[0]
        split = "development" if expiry <= "2023-12-31" else ("validation" if expiry <= "2025-12-31" else "holdout")
        eid = event_id_for(prev_exp, expiry, entry_date)
        scheduled.append({"event_id": eid, "previous_expiry": prev_exp, "expiry": expiry,
                          "entry_date": entry_date.isoformat(), "split": split, "expiry_gap_days": gap})
        lot = historical_lot_size(expiry)
        if lot is None:
            exclusions.append({"event_id": eid, "previous_expiry": prev_exp, "expiry": expiry, "split": split,
                               "reason": "UNSUPPORTED_HISTORICAL_LOT_SIZE_DATE"})
            continue
        try:
            path = Path(hf_hub_download(repo_id=HF_REPO, filename=expiry_files[expiry], repo_type="dataset",
                                        revision=revision, token=token))
            sha = sha256_file(path)
            df, parquet_audit = normalize_option_df(path, expiry)
            source_audit.append({"expiry": expiry, "file": expiry_files[expiry], "sha256": sha,
                                 "bytes": int(path.stat().st_size), "rows_after_timestamp_parse": int(len(df)),
                                 **parquet_audit, "status": "PASS"})
            event, status = prepare_event(df, spot_map, expiry, prev_exp, entry_date, split, eid, lot)
            if event is None:
                exclusions.append({"event_id": eid, "previous_expiry": prev_exp, "expiry": expiry, "split": split, "reason": status})
            else:
                eligible_events.append(event)
            del df
            gc.collect()
        except Exception as exc:
            error = f"{type(exc).__name__}: {str(exc)[:240]}"
            source_errors.append({"event_id": eid, "expiry": expiry, "error": error})
            source_audit.append({"expiry": expiry, "file": expiry_files.get(expiry, ""), "status": "ERROR",
                                 "error_type": type(exc).__name__})
            exclusions.append({"event_id": eid, "previous_expiry": prev_exp, "expiry": expiry,
                               "split": split, "reason": "SOURCE_OR_PROCESSING_ERROR"})
    pd.DataFrame(source_audit).to_csv(OUT / "source_files.csv", index=False)
    pd.DataFrame(exclusions, columns=["event_id","previous_expiry","expiry","split","reason"]).to_csv(OUT / "exclusions.csv", index=False)

    configs, costs = make_configs(), make_cost_grid()
    cost_primary = next(c for c in costs if c["brokerage_per_order"] == PRIMARY_COST["brokerage_per_order"]
                        and c["slippage_per_unit"] == PRIMARY_COST["slippage_per_unit"]
                        and c["fee_multiplier"] == PRIMARY_COST["fee_multiplier"])
    expected_by_split = {sp: sum(x["split"] == sp for x in scheduled) for sp in ("development","validation","holdout")}
    eligible_by_split = {sp: sum(x["split"] == sp for x in eligible_events) for sp in ("development","validation","holdout")}
    # Precompute same-event baseline P&L for every cost case; stop value is paired uplift.
    baseline_net_by_cost_event = {}
    for cost in costs:
        for ev in eligible_events:
            bf = premium_fee_model(ev["call_entry"], ev["put_entry"], ev["base_call_exit"], ev["base_put_exit"],
                                   ev["lot_size"], ev["entry_date"], ev["expiry"], cost)
            if bf is not None:
                baseline_net_by_cost_event[(cost["cost_id"], ev["event_id"])] = bf["net_pnl_inr"]
    grid_rows, pvals, val_metrics = [], {}, {}
    primary_val_rows = {}
    for idx, cfg in enumerate(configs, 1):
        if idx % 200 == 0:
            print(f"Phase110 progress {idx}/{len(configs)}; exact-path eligible campaigns={len(eligible_events)}", flush=True)
        exit_cache = {}
        for ev in eligible_events:
            if cfg["theta_threshold"] is not None and not ev["theta_entry_valid"]:
                continue
            try:
                exit_cache[ev["event_id"]] = (*find_exit(ev, cfg), ev)
            except ValueError:
                continue
        for cost in costs:
            for sp in ("development", "validation"):
                trades, uplift_values = [], []
                for eid, (xc, xp, xt, reason, hit_i, ev) in exit_cache.items():
                    if ev["split"] != sp:
                        continue
                    fee = premium_fee_model(ev["call_entry"], ev["put_entry"], xc, xp, ev["lot_size"], ev["entry_date"], xt.date().isoformat(), cost)
                    if fee is None:
                        continue
                    trade = {"event_id": eid, "entry_date": ev["entry_date"], "expiry": ev["expiry"],
                             "exit_ts": xt.isoformat(), "exit_reason": reason,
                             "holding_minutes": (xt - ev["entry_ts"]).total_seconds() / 60.0, **fee}
                    trades.append(trade)
                    bnet = baseline_net_by_cost_event.get((cost["cost_id"], eid))
                    if bnet is not None:
                        uplift_values.append(float(trade["net_pnl_inr"] - bnet))
                stats = summarize_trade_rows(trades, expected_by_split[sp])
                stats.update({"paired_events": int(len(uplift_values)),
                    "paired_uplift_sum_inr": float(np.sum(uplift_values)) if uplift_values else 0.0,
                    "paired_uplift_mean_net_inr": float(np.mean(uplift_values)) if uplift_values else math.nan,
                    "paired_uplift_median_net_inr": float(np.median(uplift_values)) if uplift_values else math.nan,
                    "paired_uplift_win_rate_pct": float(100*np.mean(np.asarray(uplift_values)>0)) if uplift_values else math.nan})
                grid_rows.append({"config_id": cfg["config_id"], "name": cfg["name"], "delta_mode": cfg["delta_mode"],
                                  "delta_threshold": cfg["delta_threshold"], "gamma_threshold": cfg["gamma_threshold"],
                                  "vega_threshold": cfg["vega_threshold"], "theta_threshold": cfg["theta_threshold"],
                                  "aggregation": cfg["aggregation"], "active_criteria": cfg["active_criteria"],
                                  "active_count": cfg["active_count"], "split": sp, **cost, **stats})
                if cost == cost_primary and sp == "validation":
                    primary_val_rows[cfg["config_id"]] = trades
                    pvals[cfg["config_id"]] = 1.0 if cfg["config_id"] == "NO_STOP_REFERENCE" else test_pvalue(
                        [{"net_pnl_inr": u} for u in uplift_values])
                    val_metrics[cfg["config_id"]] = stats
    adjusted = holm_adjust(pvals)
    grid = pd.DataFrame(grid_rows)
    if len(grid):
        grid["primary_cost_case"] = (
            (grid["brokerage_per_order"] == PRIMARY_COST["brokerage_per_order"])
            & (grid["slippage_per_unit"] == PRIMARY_COST["slippage_per_unit"])
            & (grid["fee_multiplier"] == PRIMARY_COST["fee_multiplier"])
        )
        grid["paired_uplift_p_value_validation"] = grid.apply(
            lambda r: pvals.get(r["config_id"], 1.0) if r["split"] == "validation" and r["primary_cost_case"] else math.nan, axis=1)
        grid["holm_p_adjusted_validation"] = grid.apply(
            lambda r: adjusted.get(r["config_id"], 1.0) if r["split"] == "validation" and r["primary_cost_case"] else math.nan, axis=1)
    grid.to_csv(OUT / "greek_stoploss_grid.csv.gz", index=False, compression="gzip")

    val = grid.loc[grid["split"].eq("validation") & grid["primary_cost_case"]].drop_duplicates("config_id").copy()
    val["holm_p_adjusted"] = val["config_id"].map(adjusted).fillna(1.0)
    val["validation_mean_paired_uplift_boot_low"], val["validation_mean_paired_uplift_boot_high"] = math.nan, math.nan
    cost_sensitivity = grid.loc[grid["split"].eq("validation")].groupby("config_id")["paired_uplift_sum_inr"].agg(
        positive_uplift_cost_scenarios=lambda x: int((x > 0).sum()),
        worst_case_paired_uplift_inr="min", median_paired_uplift_across_costs="median").reset_index()
    val = val.merge(cost_sensitivity, on="config_id", how="left")
    val["holdout_used_for_ranking"] = False
    val = val.sort_values(["paired_uplift_sum_inr", "positive_uplift_cost_scenarios", "net_pnl_inr", "max_drawdown_inr"],
                          ascending=[False, False, False, True])
    cfg_by_id = {c["config_id"]: c for c in configs}
    mandatory = [c["config_id"] for c in configs if c["active_count"] == 1 and
                 c["delta_threshold"] is not None and abs(float(c["delta_threshold"])-0.40) < 1e-9 and
                 c["delta_mode"] in ("NET_ABS","GROSS_ABS")]
    selected = []
    for cid in mandatory:
        if cid in set(val["config_id"]) and cid not in selected:
            selected.append(cid)
    for cid in val["config_id"].astype(str).tolist():
        if cid not in selected:
            selected.append(cid)
        if len(selected) >= MAX_HOLDOUT_CANDIDATES:
            break
    selected = selected[:MAX_HOLDOUT_CANDIDATES]
    # Bootstrap the baseline and frozen candidates only; interval concerns paired
    # event-level uplift, not the winner's absolute net P&L.
    for ridx, r in val.iterrows():
        cid = str(r["config_id"])
        if cid not in (set(selected) | {"NO_STOP_REFERENCE"}):
            continue
        diffs = []
        for trade in primary_val_rows.get(cid, []):
            bnet = baseline_net_by_cost_event.get((cost_primary["cost_id"], trade["event_id"]))
            if bnet is not None:
                diffs.append(float(trade["net_pnl_inr"] - bnet))
        seed = RNG_SEED if cid == "NO_STOP_REFERENCE" else RNG_SEED + int(cid[:6], 16)
        lo, hi = bootstrap_ci(diffs, seed)
        val.loc[ridx, "validation_mean_paired_uplift_boot_low"] = lo
        val.loc[ridx, "validation_mean_paired_uplift_boot_high"] = hi
    frozen = {"created_at_utc": utc_now(), "selection_split": "validation only",
              "primary_cost_case": PRIMARY_COST, "maximum_candidate_count": MAX_HOLDOUT_CANDIDATES,
              "candidate_count": len(selected), "baseline_tested_separately": True,
              "mandatory_preregistered_delta_configs": mandatory, "candidate_config_ids": selected,
              "selection_rule": "Mandatory net/gross single-delta 0.40 rules plus highest validation paired-uplift ranks; positive cost-case count is the tie-breaker. Holdout metrics are not inputs.",
              "code_sha256": sha256_file(Path(__file__)), "dataset_revision": revision}
    (OUT / "shortlist_frozen.json").write_text(json.dumps(frozen, indent=2) + "\n", encoding="utf-8")
    val.to_csv(OUT / "validation_candidates.csv", index=False)

    # Holdout is summarised only after frozen validation candidate IDs are persisted.
    holdout_ids = set(selected) | {"NO_STOP_REFERENCE"} | set(mandatory)
    holdout_rows, holdout_trade_rows, aggregate_ledger = [], [], []
    for cid in sorted(holdout_ids):
        cfg = cfg_by_id.get(cid)
        if cfg is None:
            continue
        exits = {}
        for ev in eligible_events:
            if ev["split"] != "holdout" or (cfg["theta_threshold"] is not None and not ev["theta_entry_valid"]):
                continue
            try:
                exits[ev["event_id"]] = (*find_exit(ev, cfg), ev)
            except ValueError:
                continue
        for cost in costs:
            tr = []
            for eid, (xc, xp, xt, reason, hit_i, ev) in exits.items():
                fee = premium_fee_model(ev["call_entry"], ev["put_entry"], xc, xp, ev["lot_size"], ev["entry_date"], xt.date().isoformat(), cost)
                if fee is None:
                    continue
                row = {"config_id": cid, "name": cfg["name"], "delta_mode": cfg["delta_mode"],
                       "delta_threshold": cfg["delta_threshold"], "gamma_threshold": cfg["gamma_threshold"],
                       "vega_threshold": cfg["vega_threshold"], "theta_threshold": cfg["theta_threshold"],
                       "aggregation": cfg["aggregation"], "active_criteria": cfg["active_criteria"],
                       "cost_id": cost["cost_id"], "brokerage_per_order": cost["brokerage_per_order"],
                       "slippage_per_unit": cost["slippage_per_unit"], "fee_multiplier": cost["fee_multiplier"],
                       "event_id": eid, "entry_date": ev["entry_date"], "expiry": ev["expiry"],
                       "exit_ts": xt.isoformat(), "exit_reason": reason,
                       "holding_minutes": (xt-ev["entry_ts"]).total_seconds()/60.0,
                       "baseline_net_pnl_inr": baseline_net_by_cost_event.get((cost["cost_id"], eid)),
                       "net_uplift_vs_no_stop_inr": (fee["net_pnl_inr"] - baseline_net_by_cost_event[(cost["cost_id"], eid)])
                           if (cost["cost_id"], eid) in baseline_net_by_cost_event else math.nan, **fee}
                tr.append(row)
                if cost == cost_primary:
                    aggregate_ledger.append({"config_id": cid, "name": cfg["name"], "event_id": eid,
                        "entry_date": ev["entry_date"], "expiry": ev["expiry"], "lot_size": ev["lot_size"],
                        "call_strike": ev["call_strike"], "put_strike": ev["put_strike"],
                        "call_delta_prior": ev["call_delta_prior"], "put_delta_prior": ev["put_delta_prior"],
                        "entry_net_delta": ev["entry_net_delta"], "entry_gross_delta": ev["entry_gross_delta"],
                        "exit_ts": xt.isoformat(), "exit_reason": reason,
                        "baseline_net_pnl_inr": baseline_net_by_cost_event.get((cost["cost_id"], eid)),
                        "net_uplift_vs_no_stop_inr": (fee["net_pnl_inr"] - baseline_net_by_cost_event[(cost["cost_id"], eid)])
                            if (cost["cost_id"], eid) in baseline_net_by_cost_event else math.nan, **fee})
            uplift = [float(x["net_uplift_vs_no_stop_inr"]) for x in tr
                      if math.isfinite(float(x["net_uplift_vs_no_stop_inr"]))]
            hstats = summarize_trade_rows(tr, expected_by_split["holdout"])
            hstats.update({"paired_events": len(uplift),
                "paired_uplift_sum_inr": float(np.sum(uplift)) if uplift else 0.0,
                "paired_uplift_mean_net_inr": float(np.mean(uplift)) if uplift else math.nan,
                "paired_uplift_win_rate_pct": float(100*np.mean(np.asarray(uplift)>0)) if uplift else math.nan})
            holdout_rows.append({"config_id": cid, "name": cfg["name"], "delta_mode": cfg["delta_mode"],
                "delta_threshold": cfg["delta_threshold"], "gamma_threshold": cfg["gamma_threshold"],
                "vega_threshold": cfg["vega_threshold"], "theta_threshold": cfg["theta_threshold"],
                "aggregation": cfg["aggregation"], "active_criteria": cfg["active_criteria"],
                "split": "holdout", **cost, **hstats})
            if cost == cost_primary:
                holdout_trade_rows.extend(tr)
    pd.DataFrame(holdout_rows).to_csv(OUT / "holdout_shortlist.csv", index=False)
    pd.DataFrame(holdout_trade_rows).to_csv(OUT / "holdout_trade_summary.csv", index=False)
    pd.DataFrame(aggregate_ledger).to_csv(OUT / "trade_ledger_aggregates.csv", index=False)

    reasons = dict(Counter(x["reason"] for x in exclusions))
    coverage = {"created_at_utc": utc_now(), "dataset": HF_REPO, "dataset_revision_requested": revision_request,
        "dataset_revision_resolved_sha": revision, "index_file_sha256": index_sha,
        "index_rows_valid": int(index_rows_valid), "index_observed_session_dates": len(sessions),
        "index_quality_counters": dict(index_counts), "option_expiry_files_discovered": len(expiries),
        "earliest_expiry_file": expiries[0], "latest_expiry_file": expiries[-1],
        "source_files_loaded": len(source_audit), "source_file_errors": len(source_errors),
        "weekly_pairs_scheduled": len(scheduled), "long_or_nonweekly_gaps_skipped": long_gaps,
        "eligible_campaigns": len(eligible_events), "eligible_by_split": eligible_by_split,
        "expected_by_split": expected_by_split, "exclusion_count": len(exclusions),
        "exclusion_reason_counts": reasons, "primary_source_license": "CC BY-NC 4.0 (research only)",
        "selection": "exact 09:59 close model delta, OI>=100, exact 10:00 open; absolute delta nearest 0.15",
        "exit": "exact 14:00 expiry-day open or next-minute open after completed-bar Greek stop",
        "no_forward_fill": True, "raw_market_rows_committed": False}
    (OUT / "coverage.json").write_text(json.dumps(coverage, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    primary_val = grid.loc[grid["split"].eq("validation") & grid["primary_cost_case"]].copy()
    positive = int((primary_val["net_pnl_inr"] > 0).sum()) if len(primary_val) else 0
    positive_uplift = int((primary_val["paired_uplift_sum_inr"] > 0).sum()) if len(primary_val) else 0
    corrected = int((primary_val["holm_p_adjusted_validation"] < 0.05).sum()) if len(primary_val) else 0
    best = primary_val.sort_values(["paired_uplift_sum_inr", "net_pnl_inr"], ascending=[False, False]).head(10)
    primary_ho = pd.DataFrame(holdout_rows)
    if len(primary_ho):
        primary_ho = primary_ho[(primary_ho["brokerage_per_order"] == PRIMARY_COST["brokerage_per_order"])
                                & (primary_ho["slippage_per_unit"] == PRIMARY_COST["slippage_per_unit"])
                                & (primary_ho["fee_multiplier"] == PRIMARY_COST["fee_multiplier"])]
    primary_ho.to_csv(OUT / "holdout_primary_cost_summary.csv", index=False)
    figures = write_svg_figures(val, grid)
    summary = {"status": "EMPIRICAL_SCREEN_COMPLETE_NO_PROMOTION" if eligible_events else "BLOCKED_NO_VALID_CAMPAIGNS",
        "created_at_utc": utc_now(), "branch": "phase-110-greek-stoploss-short-strangle", "dataset": HF_REPO,
        "dataset_revision_resolved_sha": revision, "source_first_expiry": expiries[0], "source_last_expiry": expiries[-1],
        "source_index_rows": int(index_rows_valid), "source_expiry_files_loaded": int(len(source_audit)),
        "scheduled_campaigns": len(scheduled), "valid_campaigns": len(eligible_events), "excluded_campaigns": len(exclusions),
        "exclusion_reason_counts": reasons, "configs_registered_including_no_stop": len(configs),
        "cost_scenarios": len(costs), "config_cost_pairs": len(configs)*len(costs),
        "grid_rows_completed_development_validation": len(grid_rows), "primary_cost_case": PRIMARY_COST,
        "validation_rule_count": int(len(primary_val)), "validation_positive_net_rule_count": positive,
        "validation_positive_paired_uplift_rule_count": positive_uplift,
        "validation_holm_adjusted_p_lt_0_05_rule_count": corrected,
        "validation_top_rules": best[["config_id","name","net_pnl_inr","paired_uplift_sum_inr",
                                     "max_drawdown_inr","trades","holm_p_adjusted_validation"]].to_dict("records") if len(best) else [],
        "holdout_candidate_count": len(selected), "holdout_rules_including_baseline": len(holdout_ids),
        "holdout_primary_cost_top5": primary_ho.sort_values("net_pnl_inr", ascending=False).head(5)[["config_id","name","net_pnl_inr","max_drawdown_inr","trades"]].to_dict("records") if len(primary_ho) else [],
        "holdout_used_for_ranking": False, "promotion": "NONE", "script_sha256": sha256_file(Path(__file__)),
        "figure_paths": figures, "outputs": ["summary.json","coverage.json","source_files.csv","exclusions.csv",
        "greek_stoploss_grid.csv.gz","validation_candidates.csv","shortlist_frozen.json","holdout_shortlist.csv",
        "holdout_primary_cost_summary.csv","holdout_trade_summary.csv","trade_ledger_aggregates.csv"],
        "limitations": ["Greeks are model estimates, not historical exchange Greeks.",
        "One-minute OHLC opens are execution proxies, not executable bid/ask fills; sub-minute moves can be missed.",
        "Primary data is CC BY-NC 4.0 non-commercial research only; no commercial conclusion is authorized.",
        "Exact selected-leg paths are required; missing bars or invalid model IV exclude an entire campaign.",
        "Source end date is data cutoff, not the current date; no outcomes are extrapolated.",
        "A multi-thousand-rule winner is exploratory until independent audit and out-of-sample gates pass."]}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    report = ["# Phase 110 — Greek Stop-Loss Screen", "", f"Generated: {summary['created_at_utc']}",
        f"Resolved dataset SHA: {revision}", f"Status: **{summary['status']}**", "", "## Coverage gate", "",
        f"- Observed expiry files: {len(expiries)} ({expiries[0]} through {expiries[-1]}).",
        f"- Weekly campaigns scheduled: {len(scheduled)}; exact-path eligible: {len(eligible_events)}; excluded: {len(exclusions)}.",
        f"- Exclusions: {json.dumps(reasons, sort_keys=True)}.", "", "## Registered sweep and costs", "",
        f"- Rules registered including no-stop: {len(configs)}.",
        f"- Each rule is evaluated under {len(costs)} cost combinations for development and validation.",
        f"- Brokerage per executed order ₹10/₹15/₹20; per-unit adverse slippage ₹0/₹0.05/₹0.25/₹0.50 per leg per side; fee stress 1.0×/1.5×.",
        f"- Primary comparison case: ₹{PRIMARY_COST['brokerage_per_order']:.0f}/order, ₹{PRIMARY_COST['slippage_per_unit']:.2f} slippage/unit/side, {PRIMARY_COST['fee_multiplier']:.1f}× fee model.",
        "- The requested 0.40 threshold is tested both as absolute signed net position delta and as the sum of absolute leg deltas.", "",
        "## Validation findings", "", f"- Rules with positive net validation P&L at primary costs: {positive}.",
        f"- Rules with positive paired uplift versus no-stop: {positive_uplift}.",
        f"- Rules with Holm-adjusted one-sided p < 0.05 for paired uplift: {corrected}.",
        "- Each stop is paired with the same campaign's no-stop result. Validation ranks rules; the frozen shortlist is persisted before holdout summarization.", "",
        "### Top validation rules by paired uplift (one lot, primary costs)", "",
        "| Rule | Trades | Net P&L (₹) | Paired uplift (₹) | Max drawdown (₹) | Holm-adjusted p |", "|---|---:|---:|---:|---:|---:|"]
    if len(best):
        for r in best.to_dict("records"):
            report.append(f"| {str(r['name']).replace('|',' / ')} | {int(r['trades'])} | {float(r['net_pnl_inr']):,.2f} | {float(r['paired_uplift_sum_inr']):,.2f} | {float(r['max_drawdown_inr']):,.2f} | {float(r['holm_p_adjusted_validation']):.4g} |")
    else:
        report.append("| No validation data | 0 | — | — | — |")
    report += ["", "## Frozen holdout (not used for selection)", "",
        "| Rule | Trades | Net P&L (₹) | Paired uplift (₹) | Max drawdown (₹) |", "|---|---:|---:|---:|"]
    if len(primary_ho):
        for r in primary_ho.sort_values("net_pnl_inr", ascending=False).head(10).to_dict("records"):
            report.append(f"| {str(r['name']).replace('|',' / ')} | {int(r['trades'])} | {float(r['net_pnl_inr']):,.2f} | {float(r['paired_uplift_sum_inr']):,.2f} | {float(r['max_drawdown_inr']):,.2f} |")
    else:
        report.append("| No eligible frozen holdout rows | 0 | — | — |")
    report += ["", "## Decision", "",
        "**No strategy is promoted from this screen.** Historical Greeks are Black–Scholes estimates, execution is a one-minute OHLC proxy, the dataset is CC BY-NC 4.0, and exact-path coverage can select a non-representative subset. The highest result from a multi-thousand-rule sweep is not sufficient evidence of executable profitability. Independent testing and the registered gates remain mandatory.", "",
        "## Files", "", "- summary.json: source and run provenance.", "- coverage.json / source_files.csv / exclusions.csv: coverage and failure reasons.",
        "- greek_stoploss_grid.csv.gz: complete development/validation rule sweep and 24 cost scenarios.",
        "- validation_candidates.csv: validation rank, Holm correction and bootstrap intervals.",
        "- shortlist_frozen.json: candidate list frozen before holdout output.", "- holdout_shortlist.csv: holdout cost grid for the frozen candidates.",
        "- holdout_primary_cost_summary.csv: primary cost comparison.", "- trade_ledger_aggregates.csv: campaign-level outcomes without raw minute rows.",
        *[f"- {p}" for p in figures], "", "## References", "",
        "- Dataset and license: https://huggingface.co/datasets/thetrademarkk/india-index-options-1m",
        "- Dhan expired-options docs: https://dhanhq.co/docs/v2/expired-options-data/",
        "- Paytm Money F&O FAQ: https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web",
        "- NSE levies: https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies",
        "- NSE Circular FA73061: https://nsearchives.nseindia.com/content/circulars/FA73061.pdf", ""]
    (OUT / "PHASE110_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    manuscript = [
        "# Greek-Conditioned Stop-Loss Rules for a NIFTY Weekly Short Strangle", "",
        "## Abstract", "",
        f"This preregistered historical screen tests {len(configs)} Greek-based stop configurations for a short NIFTY weekly strangle: sell a roughly 0.15-absolute-delta call and put at 10:00 IST on the first observed trading session after the previous listed weekly expiry, and cover at 14:00 IST on the target expiry day unless a Greek stop triggers. Source SHA: {revision}. Scheduled campaigns: {len(scheduled)}; strict exact-minute campaigns passing all gates: {len(eligible_events)}. Results are one-minute OHLC simulations with model-derived Greeks and not executable fills. No strategy is promoted.", "",
        "## Research questions", "",
        "The primary question is whether abs(signed net short-position delta) crossing 0.40 improves after-cost outcomes versus fixed 14:00 exit. Secondary questions compare gross absolute leg delta, gamma, vega and theta rules, all nonempty active-criterion combinations and contemporaneous ANY versus ALL triggers.", "",
        "## Methods", "",
        "### Sample and entry construction", "",
        f"Source: {HF_REPO} at resolved revision {revision}, declared CC BY-NC 4.0. Observed option-expiry files define the calendar; only consecutive listed expiries separated by 4–10 days enter the weekly event universe. Entry is the first index session after the previous expiry. Strike selection uses the exact completed 09:59 close, valid Black–Scholes IV, model delta closest to absolute 0.15 and prior OI at least 100. Entry fills use both exact 10:00 option-bar opens; fixed exit uses both exact 14:00 opens on the target expiry day.", "",
        "### Greek calculations and causal exit", "",
        "European Black–Scholes model: 6% continuously compounded rate, zero dividend yield, expiry 15:30 IST, 365.25 days/year. Net short portfolio Greeks equal negative call-plus-put long Greek sums. Net delta may cancel; gross delta is the sum of absolute leg deltas. Gamma risk is max(0,−net short gamma) × 0.5 × (0.5% × spot)^2 divided by initial credit. Vega risk is max(0,−short vega per one IV percentage point) divided by credit. Theta ratio is current short theta/day divided by positive entry theta. Signals use completed closes; exits execute at the following exact minute open.", "",
        "### Rule and cost grid", "",
        f"The finite sweep registered {len(configs)} distinct rules including the no-stop reference. Threshold domains: net delta 0.20–0.80, gross delta 0.40–1.00, gamma and vega normalized 10%–50% of credit, theta ratio 0.00/0.25/0.50/0.75. Test all nonempty subsets, active thresholds, and ANY/ALL simultaneous-trigger modes. Each development/validation rule is evaluated across {len(costs)} costs: ₹10/₹15/₹20 brokerage/order × ₹0/₹0.05/₹0.25/₹0.50 adverse per-unit slippage × 1.0×/1.5× modeled statutory charges. The 1.5× value is a stress scenario, not a claim about actual statutory charges.", "",
        "### Statistical design", "",
        "Development is target expiries through 2023-12-31; validation is 2024-01-01 through 2025-12-31; holdout starts 2026-01-01 and ends at the source cutoff. One-sided one-sample tests on event-paired net uplift versus the same campaigns' no-stop result are Holm-adjusted over the full rule sweep. Bootstrap 95% confidence intervals are calculated for mean paired uplift for the frozen validation shortlist only. The holdout shortlist is frozen from validation before holdout results are summarized. Holdout metrics do not rank or modify candidates.", "",
        "## Results", "",
        f"The first run checkpoint reports {len(scheduled)} scheduled and {len(eligible_events)} eligible campaigns; {len(exclusions)} are excluded for the reasons enumerated in exclusions.csv. Positive-net validation rules: {positive}; positive paired-uplift rules: {positive_uplift}; Holm-adjusted paired-uplift p<0.05 rules: {corrected}. Use PHASE110_REPORT.md and the CSV/JSON files for the complete grid, cost sensitivity and campaign-level results.", "",
        "## Discussion", "",
        "A stop can limit exposure to directional/volatility moves but may also realize losses earlier, cut profitable positions and increase costs. Signed net delta and gross leg delta answer different risk questions. Gamma is a local second-order spot-move proxy; vega assumes a one-volatility-point move; theta is a decay-edge guard. These are distinct measures and their normalized thresholds are hypotheses rather than interchangeable loss limits. A one-minute model can miss sub-minute triggers.", "",
        "## Strengths", "",
        "Pre-registered finite grid, exact point-in-time entry, prior OI guard, exact bar joins, no interpolation, signed short Greeks, next-open stop execution, date-effective lots/fees, all cost cases, validation multiple-testing correction, and frozen holdout shortlist.", "",
        "## Limitations", "",
        "Model-dependent Greeks, no historical exchange Greeks or bid/ask, OHLC fill proxy, exact-path exclusions, partial source history, potential sample attrition, fixed model rate/dividend assumptions, and a non-commercial data license. Any resulting rank is exploratory.", "",
        "## Conclusion", "",
        "No threshold is declared optimal solely from this sweep. A candidate requires positive after-cost validation and frozen holdout evidence, cost robustness, non-excessive drawdown, adequate coverage, appropriate source rights and independent tester approval before promotion.", "",
        "## Future directions", "",
        "If this finite phase ends with a coverage limitation, register a separate bounded phase to validate the free 2017–2020 Zenodo source or acquire/reconcile Dhan historical expired-option data for the missing recent period, then test against higher-frequency quotes if legitimately available. Do not tune new thresholds on this holdout.", "",
        "## References", "",
        "1. https://huggingface.co/datasets/thetrademarkk/india-index-options-1m",
        "2. https://dhanhq.co/docs/v2/expired-options-data/",
        "3. https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web",
        "4. https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies",
        "5. https://nsearchives.nseindia.com/content/circulars/FA73061.pdf", "",
        "## Supplementary material", "",
        "CSV/JSON files, figures, exclusion reasons, source file hashes and the frozen candidate manifest are stored under results/phase110."
    ]
    (OUT / "PHASE110_MANUSCRIPT.md").write_text("\n".join(manuscript), encoding="utf-8")
    print(json.dumps({"status": summary["status"], "dataset_revision": revision, "latest_expiry": expiries[-1],
        "scheduled": len(scheduled), "eligible": len(eligible_events), "excluded": len(exclusions),
        "registered_configs": len(configs), "grid_rows": len(grid_rows), "holdout_candidates": len(selected),
        "outputs": [str(p.relative_to(ROOT)) for p in OUT.rglob("*") if p.is_file()]}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "runtime_error.json").write_text(json.dumps({"status":"RUNTIME_ERROR","created_at_utc":utc_now(),
            "error_type":type(exc).__name__,"error":str(exc)[:2000]}, indent=2) + "\n", encoding="utf-8")
        raise
