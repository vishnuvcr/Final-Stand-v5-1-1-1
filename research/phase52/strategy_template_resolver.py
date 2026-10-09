#!/usr/bin/env python3
"""Source-guarded strategy template resolver for Phase 52; no P&L.

This module maps a frozen strategy-family specification to explicit option legs,
resolves those legs against exact entry-time contract rows, and enforces exact
prior-completed-bar OI eligibility. It never fills missing bars or substitutes
nearest strikes/timestamps. Futures-hedge families are fail-closed because this
source has no synchronized intraday traded-futures feed.

The exact source text, family status and resolver rule are bound by
template_resolver_manifest.json. If the source specification changes, the
resolver blocks rather than applying an out-of-date geometry.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from replay_kernel import as_ist, config_data_gate, select_exact_bar, valid_ohlc, prior_oi_eligible

ROOT = Path(__file__).resolve().parents[2]
SPECS_PATH = ROOT / "research" / "phase52" / "strategy_specifications.csv"
MANIFEST_PATH = ROOT / "research" / "phase52" / "template_resolver_manifest.json"
PROTOCOL_PATH = ROOT / "PHASE52_REPLAY_PROTOCOL.md"
RESOLVER_VERSION = "phase52-template-resolver-v0.1"
TZ = "Asia/Kolkata"
MIN_OI = 100.0
DELTA_TARGETS_AUDITED = (0.15, 0.30)


@dataclass(frozen=True)
class LegRule:
    side: str
    option_type: str
    quantity: int
    anchor: str
    fixed_steps: int = 0
    width_steps: int = 0
    expiry_role: str = "near"


def _leg(side: str, typ: str, quantity: int, anchor: str,
         fixed: int = 0, width: int = 0, expiry_role: str = "near") -> LegRule:
    if side not in {"BUY", "SELL"} or typ not in {"CE", "PE"}:
        raise ValueError(f"invalid leg side/type: {side}/{typ}")
    if quantity < 1 or anchor not in {"CENTER", "CALL", "PUT"}:
        raise ValueError(f"invalid leg quantity/anchor: {quantity}/{anchor}")
    if expiry_role not in {"near", "far"}:
        raise ValueError(f"invalid expiry role: {expiry_role}")
    return LegRule(side, typ, quantity, anchor, fixed, width, expiry_role)


# Offset semantics are tied to the preregistered rule descriptions. "CALL" and
# "PUT" use separate OTM anchors. "CENTER" uses one shared pivot (for straddles,
# strip/strap, iron butterflies and option synthetics). Offsets are in modal
# strike-gap units; parameterized width is resolved only from the frozen grid.
RULES: dict[str, tuple[LegRule, ...]] = {
    "BUY_CALL": (_leg("BUY","CE",1,"CALL"),),
    "BUY_PUT": (_leg("BUY","PE",1,"PUT"),),
    "SELL_CALL": (_leg("SELL","CE",1,"CALL"),),
    "SELL_PUT": (_leg("SELL","PE",1,"PUT"),),
    "BULL_CALL_SPREAD": (_leg("BUY","CE",1,"CALL"), _leg("SELL","CE",1,"CALL",width=1)),
    "BEAR_PUT_SPREAD": (_leg("BUY","PE",1,"PUT"), _leg("SELL","PE",1,"PUT",width=-1)),
    "BULL_PUT_SPREAD": (_leg("SELL","PE",1,"PUT"), _leg("BUY","PE",1,"PUT",width=-1)),
    "BEAR_CALL_SPREAD": (_leg("SELL","CE",1,"CALL"), _leg("BUY","CE",1,"CALL",width=1)),
    "LONG_STRADDLE": (_leg("BUY","CE",1,"CENTER"), _leg("BUY","PE",1,"CENTER")),
    "SHORT_STRADDLE": (_leg("SELL","CE",1,"CENTER"), _leg("SELL","PE",1,"CENTER")),
    "LONG_STRANGLE": (_leg("BUY","CE",1,"CALL"), _leg("BUY","PE",1,"PUT")),
    "SHORT_STRANGLE": (_leg("SELL","CE",1,"CALL"), _leg("SELL","PE",1,"PUT")),
    # Condor anchors are separate OTM short strikes; the long wings are further OTM.
    "SHORT_IRON_CONDOR": (
        _leg("BUY","PE",1,"PUT",width=-1), _leg("SELL","PE",1,"PUT"),
        _leg("SELL","CE",1,"CALL"), _leg("BUY","CE",1,"CALL",width=1)),
    "LONG_IRON_CONDOR": (
        _leg("BUY","PE",1,"PUT"), _leg("BUY","CE",1,"CALL"),
        _leg("SELL","PE",1,"PUT",width=-1), _leg("SELL","CE",1,"CALL",width=1)),
    "SHORT_IRON_BUTTERFLY": (
        _leg("SELL","CE",1,"CENTER"), _leg("SELL","PE",1,"CENTER"),
        _leg("BUY","PE",1,"CENTER",width=-1), _leg("BUY","CE",1,"CENTER",width=1)),
    "LONG_IRON_BUTTERFLY": (
        _leg("BUY","CE",1,"CENTER"), _leg("BUY","PE",1,"CENTER"),
        _leg("SELL","PE",1,"CENTER",width=-1), _leg("SELL","CE",1,"CENTER",width=1)),
    "BULL_CONDOR": (
        _leg("BUY","CE",1,"CALL"), _leg("SELL","CE",1,"CALL",width=1),
        _leg("SELL","CE",1,"CALL",width=2), _leg("BUY","CE",1,"CALL",width=3)),
    "BEAR_CONDOR": (
        _leg("BUY","PE",1,"PUT"), _leg("SELL","PE",1,"PUT",width=-1),
        _leg("SELL","PE",1,"PUT",width=-2), _leg("BUY","PE",1,"PUT",width=-3)),
    "BULL_BUTTERFLY": (
        _leg("BUY","CE",1,"CALL"), _leg("SELL","CE",2,"CALL",width=1),
        _leg("BUY","CE",1,"CALL",width=2)),
    "BEAR_BUTTERFLY": (
        _leg("BUY","PE",1,"PUT"), _leg("SELL","PE",2,"PUT",width=-1),
        _leg("BUY","PE",1,"PUT",width=-2)),
    "CALL_BUTTERFLY": (
        _leg("BUY","CE",1,"CENTER",width=-1), _leg("SELL","CE",2,"CENTER"),
        _leg("BUY","CE",1,"CENTER",width=1)),
    "PUT_BUTTERFLY": (
        _leg("BUY","PE",1,"CENTER",width=1), _leg("SELL","PE",2,"CENTER"),
        _leg("BUY","PE",1,"CENTER",width=-1)),
    # W1 is fixed at one modal step; W2 is the registered width. width=1 is
    # symmetric; width=3 is the tested broken-wing boundary.
    "CALL_BROKEN_WING_BUTTERFLY": (
        _leg("BUY","CE",1,"CALL"), _leg("SELL","CE",2,"CALL",fixed=1),
        _leg("BUY","CE",1,"CALL",fixed=1,width=1)),
    "PUT_BROKEN_WING_BUTTERFLY": (
        _leg("BUY","PE",1,"PUT"), _leg("SELL","PE",2,"PUT",fixed=-1),
        _leg("BUY","PE",1,"PUT",fixed=-1,width=-1)),
    "CALL_RATIO_SPREAD": (_leg("BUY","CE",1,"CALL"), _leg("SELL","CE",1,"CALL",width=1)),
    "PUT_RATIO_SPREAD": (_leg("BUY","PE",1,"PUT"), _leg("SELL","PE",1,"PUT",width=-1)),
    "CALL_RATIO_BACKSPREAD": (_leg("SELL","CE",1,"CALL"), _leg("BUY","CE",1,"CALL",width=1)),
    "PUT_RATIO_BACKSPREAD": (_leg("SELL","PE",1,"PUT"), _leg("BUY","PE",1,"PUT",width=-1)),
    "JADE_LIZARD": (
        _leg("SELL","PE",1,"PUT"), _leg("SELL","CE",1,"CALL"),
        _leg("BUY","CE",1,"CALL",width=2)),
    "REVERSE_JADE_LIZARD": (
        _leg("SELL","CE",1,"CALL"), _leg("SELL","PE",1,"PUT"),
        _leg("BUY","PE",1,"PUT",width=-2)),
    "RANGE_FORWARD": (_leg("BUY","CE",1,"CALL"), _leg("SELL","PE",1,"PUT")),
    "BEAR_RISK_REVERSAL": (_leg("BUY","PE",1,"PUT"), _leg("SELL","CE",1,"CALL")),
    "STRIP": (_leg("BUY","CE",1,"CENTER"), _leg("BUY","PE",2,"CENTER")),
    "STRAP": (_leg("BUY","CE",2,"CENTER"), _leg("BUY","PE",1,"CENTER")),
    "BATMAN": (
        _leg("BUY","CE",1,"CALL"), _leg("SELL","CE",2,"CALL",width=1),
        _leg("BUY","PE",1,"PUT"), _leg("SELL","PE",2,"PUT",width=-1)),
    "DOUBLE_PLATEAU": (
        _leg("BUY","PE",1,"PUT"), _leg("SELL","PE",2,"PUT",width=-1),
        _leg("BUY","PE",1,"PUT",width=-2), _leg("BUY","CE",1,"CALL"),
        _leg("SELL","CE",2,"CALL",width=1), _leg("BUY","CE",1,"CALL",width=2)),
    "CALL_CALENDAR": (
        _leg("SELL","CE",1,"CALL",expiry_role="near"),
        _leg("BUY","CE",1,"CALL",expiry_role="far")),
    "PUT_CALENDAR": (
        _leg("SELL","PE",1,"PUT",expiry_role="near"),
        _leg("BUY","PE",1,"PUT",expiry_role="far")),
    "DOUBLE_CALENDAR": (
        _leg("SELL","CE",1,"CENTER",expiry_role="near"),
        _leg("SELL","PE",1,"CENTER",expiry_role="near"),
        _leg("BUY","CE",1,"CENTER",expiry_role="far"),
        _leg("BUY","PE",1,"CENTER",expiry_role="far")),
    "CALL_DIAGONAL": (
        _leg("SELL","CE",1,"CALL",width=1,expiry_role="near"),
        _leg("BUY","CE",1,"CALL",expiry_role="far")),
    "PUT_DIAGONAL": (
        _leg("SELL","PE",1,"PUT",width=-1,expiry_role="near"),
        _leg("BUY","PE",1,"PUT",expiry_role="far")),
    "DOUBLE_DIAGONAL": (
        _leg("SELL","CE",1,"CALL",width=1,expiry_role="near"),
        _leg("SELL","PE",1,"PUT",width=-1,expiry_role="near"),
        _leg("BUY","CE",1,"CALL",expiry_role="far"),
        _leg("BUY","PE",1,"PUT",expiry_role="far")),
    "RATIO_CALENDAR": (
        _leg("SELL","CE",2,"CALL",expiry_role="near"),
        _leg("BUY","CE",1,"CALL",expiry_role="far")),
    "LONG_SYNTHETIC_FUTURE": (_leg("BUY","CE",1,"CENTER"), _leg("SELL","PE",1,"CENTER")),
    "SHORT_SYNTHETIC_FUTURE": (_leg("SELL","CE",1,"CENTER"), _leg("BUY","PE",1,"CENTER")),
}
FUTURES_REQUIRED_FAMILIES = {
    "DELTA_NEUTRAL_LONG_GAMMA_SCALP", "PROTECTIVE_PUT_FUTURE", "COVERED_CALL_FUTURE",
    "FUTURES_BASIS_SPREAD",
}
RISK_UNBOUNDED = {"SELL_CALL", "SELL_PUT", "SHORT_STRADDLE", "SHORT_STRANGLE"}
PATH_DEPENDENT_TP_BLOCK = {
    "CALL_CALENDAR", "PUT_CALENDAR", "DOUBLE_CALENDAR", "CALL_DIAGONAL",
    "PUT_DIAGONAL", "DOUBLE_DIAGONAL", "RATIO_CALENDAR",
}
INFINITE_OR_UNDEFINED_TP_BLOCK = {
    "BUY_CALL", "LONG_STRADDLE", "LONG_STRANGLE", "CALL_RATIO_BACKSPREAD", "PUT_RATIO_BACKSPREAD",
}
SUPPORTED_RULE_IDS = set(RULES)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_source_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def validate_spec_binding(
    spec: Mapping[str, Any], manifest: Mapping[str, Any]
) -> tuple[bool, str]:
    fam = str(spec.get("family_id", ""))
    bound = manifest.get("families", {}).get(fam)
    if not bound:
        return False, "FAMILY_ABSENT_FROM_TEMPLATE_MANIFEST"
    for field in ("family_name", "leg_template", "specification_status", "source_ref", "risk_notes"):
        if str(spec.get(field, "")) != str(bound.get(field, "")):
            return False, f"TEMPLATE_MANIFEST_DRIFT:{field}"
    rule_id = str(bound.get("resolver_rule_id", "UNSUPPORTED"))
    if rule_id not in SUPPORTED_RULE_IDS and not rule_id.startswith("BLOCKED_"):
        return False, "BLOCKED_UNSUPPORTED_TEMPLATE"
    return True, rule_id


def modal_step(snapshot: pd.DataFrame) -> float | None:
    """Exact Phase43 convention: use CE strike-gap mode first, PE only if CE gaps absent."""
    if snapshot.empty:
        return None
    for typ in ("CE", "PE"):
        strikes = np.sort(pd.to_numeric(
            snapshot.loc[snapshot["option_type"].astype(str).str.upper().eq(typ), "strike"],
            errors="coerce"
        ).dropna().unique())
        diffs = np.round(np.diff(strikes), 8)
        diffs = diffs[diffs > 0]
        if len(diffs):
            vals, counts = np.unique(diffs, return_counts=True)
            return float(vals[np.argmax(counts)])
    return None


def nearest_listed_strike(strikes: Sequence[float], spot: float) -> float | None:
    vals = sorted({float(x) for x in strikes if math.isfinite(float(x))})
    if not vals or not math.isfinite(float(spot)):
        return None
    return min(vals, key=lambda k: (abs(k - float(spot)), k))


def select_far_expiry(
    target_expiry: Any, listed_expiries: Sequence[Any], pairing: str
) -> str | None:
    target = pd.Timestamp(target_expiry).normalize()
    later = sorted({
        pd.Timestamp(x).normalize() for x in listed_expiries
        if pd.Timestamp(x).normalize() > target
    })
    if not later:
        return None
    mode = str(pairing).upper()
    if mode == "WEEKLY_WEEKLY":
        return later[0].strftime("%Y-%m-%d")
    if mode == "WEEKLY_MONTHLY":
        if target.month == 12:
            y, m = target.year + 1, 1
        else:
            y, m = target.year, target.month + 1
        next_month = [x for x in later if x.year == y and x.month == m]
        return max(next_month).strftime("%Y-%m-%d") if next_month else None
    return None


def exact_prior_oi(
    prior_chain: pd.DataFrame,
    entry_ts: Any,
    expiry: Any,
    option_type: str,
    strike: float,
    min_oi: float = MIN_OI,
) -> tuple[bool, float | None, str]:
    """Find one exact target-contract row at T−1 minute; no nearest prior row."""
    if prior_chain is None or prior_chain.empty:
        return False, None, "MISSING_PRIOR_CHAIN"
    required = {"timestamp", "expiry", "option_type", "strike", "open_interest"}
    if required.difference(prior_chain.columns):
        return False, None, "PRIOR_CHAIN_SCHEMA_MISSING"
    expected = as_ist(entry_ts) - pd.Timedelta(minutes=1)
    times = pd.to_datetime(prior_chain["timestamp"], errors="coerce")
    if times.dt.tz is None:
        times = times.dt.tz_localize(TZ)
    else:
        times = times.dt.tz_convert(TZ)
    expiries = pd.to_datetime(prior_chain["expiry"], errors="coerce").dt.strftime("%Y-%m-%d")
    mask = (
        times.eq(expected)
        & expiries.eq(pd.Timestamp(expiry).strftime("%Y-%m-%d"))
        & prior_chain["option_type"].astype(str).str.upper().eq(option_type.upper())
        & pd.to_numeric(prior_chain["strike"], errors="coerce").eq(float(strike))
    )
    found = prior_chain.loc[mask]
    if found.empty:
        return False, None, "NO_EXACT_PRIOR_CONTRACT_ROW"
    if len(found) != 1:
        return False, None, "DUPLICATE_PRIOR_CONTRACT_ROWS"
    okay, oi = prior_oi_eligible(found.iloc[0].to_dict(), min_oi)
    if not okay:
        return False, oi, "PRIOR_OI_MISSING_OR_BELOW_GATE"
    return True, oi, "PASS"


def _anchor_strike(
    anchor: str,
    atm: float,
    step: float,
    config: Mapping[str, Any],
    entry_ts: pd.Timestamp,
    expiry: str,
    delta_selections: Sequence[Mapping[str, Any]] | None,
    delta_resolver_passed: bool,
) -> tuple[float | None, str]:
    selector = str(config.get("strike_selection", "ATM_OFFSET")).upper()
    if selector == "ATM_OFFSET":
        offset = int(config.get("atm_offset_steps", 1))
        direction = -1 if anchor == "PUT" else 1
        return atm + direction * offset * step, "ATM_OFFSET"
    if selector != "ABS_DELTA":
        return None, "BLOCKED_UNKNOWN_STRIKE_SELECTOR"
    if not delta_resolver_passed:
        return None, "BLOCKED_DELTA_RESOLVER"
    target = float(config.get("absolute_delta", math.nan))
    if target not in DELTA_TARGETS_AUDITED:
        return None, "BLOCKED_DELTA_TARGET_NOT_AUDITED"
    wanted_type = "PE" if anchor == "PUT" else "CE"  # CENTER uses call-side delta anchor.
    candidates = [
        x for x in (delta_selections or [])
        if str(x.get("expiry")) == expiry
        and as_ist(x.get("entry_ts")) == entry_ts
        and str(x.get("option_type", "")).upper() == wanted_type
        and abs(float(x.get("target_abs_delta", math.nan)) - target) < 1e-10
    ]
    if len(candidates) != 1:
        return None, "BLOCKED_DELTA_SELECTION_MISSING_OR_DUPLICATE"
    x = candidates[0]
    if (
        x.get("status") != "MODEL_DELTA_SELECTED_ENTRY_BAR_PASS"
        or str(x.get("entry_fill_bar_available")).lower() != "true"
        or str(x.get("predecision_oi_ge_100")).lower() != "true"
        or x.get("selected_strike") is None
    ):
        return None, "BLOCKED_DELTA_SELECTION_NOT_ENTRY_ELIGIBLE"
    try:
        strike = float(x["selected_strike"])
        if not math.isfinite(strike):
            return None, "BLOCKED_DELTA_STRIKE_NONFINITE"
    except (TypeError, ValueError):
        return None, "BLOCKED_DELTA_STRIKE_INVALID"
    return strike, "ABS_DELTA_PRIOR_BAR_MODEL_ESTIMATE"


def _resolved_expiry(
    role: str,
    target_expiry: str,
    listed_expiries: Sequence[Any],
    pairing: str,
) -> tuple[str | None, str]:
    if role == "near":
        return target_expiry, "PASS"
    far = select_far_expiry(target_expiry, listed_expiries, pairing)
    if far is None:
        return None, "BLOCKED_FAR_EXPIRY_UNAVAILABLE"
    return far, "PASS"


def resolve_template(
    family_id: str,
    config: Mapping[str, Any],
    event: Mapping[str, Any],
    entry_chain: pd.DataFrame,
    prior_chain: pd.DataFrame,
    listed_expiries: Sequence[Any],
    specs: Sequence[Mapping[str, Any]] | None = None,
    manifest: Mapping[str, Any] | None = None,
    delta_selections: Sequence[Mapping[str, Any]] | None = None,
    delta_resolver_passed: bool = False,
    intraday_futures_passed: bool = False,
    risk_class: str = "",
) -> dict[str, Any]:
    """Resolve one family/config to exact, source-bound legs; never calculates P&L."""
    spec_map = {str(s.get("family_id")): dict(s) for s in (specs if specs is not None else load_csv(SPECS_PATH))}
    frozen = manifest if manifest is not None else load_source_manifest()
    spec = spec_map.get(str(family_id))
    if spec is None:
        return blocked("BLOCKED_SPECIFICATION_MISSING", family_id, "family not found in CSV specification registry")
    bound, rule_or_error = validate_spec_binding(spec, frozen)
    if not bound:
        return blocked("BLOCKED_TEMPLATE_MANIFEST_DRIFT", family_id, rule_or_error)
    rule_id = rule_or_error
    if rule_id.startswith("BLOCKED_"):
        return blocked(rule_id, family_id, "family is explicitly blocked by the frozen source/specification manifest")
    if family_id not in RULES:
        return blocked("BLOCKED_UNSUPPORTED_TEMPLATE", family_id, "no executable rule map")

    target_expiry = pd.Timestamp(event.get("expiry")).strftime("%Y-%m-%d") if event.get("expiry") is not None else ""
    if not target_expiry:
        return blocked("BLOCKED_MISSING_TARGET_EXPIRY", family_id, "target expiry is required")
    try:
        entry_ts = as_ist(event["entry_ts"])
        spot = float(event["spot_open"])
        spot_ts = as_ist(event["spot_timestamp"])
    except Exception:
        return blocked("BLOCKED_MISSING_ENTRY_SPOT_OR_TIMESTAMP", family_id, "exact entry timestamp, index open and its timestamp are required")
    if not math.isfinite(spot) or spot <= 0 or spot_ts != entry_ts:
        return blocked("BLOCKED_INDEX_ENTRY_TIMESTAMP_OR_PRICE", family_id, "strike selection requires positive exact-time NIFTY index open")
    if entry_chain is None or entry_chain.empty:
        return blocked("BLOCKED_EMPTY_ENTRY_CHAIN", family_id, "no exact-time option chain rows supplied")
    needed = {"timestamp","expiry","option_type","strike","open","high","low","close"}
    if needed.difference(entry_chain.columns):
        return blocked("BLOCKED_ENTRY_CHAIN_SCHEMA", family_id, f"missing fields: {sorted(needed.difference(entry_chain.columns))}")
    t = pd.to_datetime(entry_chain["timestamp"], errors="coerce")
    t = t.dt.tz_localize(TZ) if t.dt.tz is None else t.dt.tz_convert(TZ)
    exp = pd.to_datetime(entry_chain["expiry"], errors="coerce").dt.strftime("%Y-%m-%d")
    exact_all = entry_chain.loc[t.eq(entry_ts)].copy()
    if exact_all.empty:
        return blocked("BLOCKED_NO_EXACT_ENTRY_CHAIN", family_id, "no option rows at the exact configured entry timestamp")
    exact_all["option_type"] = exact_all["option_type"].astype(str).str.upper()
    exact_all["strike"] = pd.to_numeric(exact_all["strike"], errors="coerce")
    exact_all["_expiry_key"] = exp.loc[exact_all.index]
    near_snapshot = exact_all.loc[exact_all["_expiry_key"].eq(target_expiry)].copy()
    if near_snapshot.empty:
        return blocked("BLOCKED_NO_TARGET_EXPIRY_SNAPSHOT", family_id, "target expiry has no rows at entry timestamp")
    step = modal_step(near_snapshot)
    if step is None or not math.isfinite(step) or step <= 0:
        return blocked("BLOCKED_INVALID_MODAL_STRIKE_STEP", family_id, "cannot determine a positive strike step from exact-time target-expiry snapshot")
    atm = nearest_listed_strike(
        pd.to_numeric(near_snapshot["strike"], errors="coerce").dropna().tolist(), spot
    )
    if atm is None:
        return blocked("BLOCKED_NO_ATM_STRIKE", family_id, "no listed strike to anchor at exact timestamp")

    # Fail closed for unresolved input/family/cost semantics before leg calculations.
    risk = risk_class or spec.get("specification_status", "")
    gate, gate_reason = config_data_gate(
        str(spec["specification_status"]), family_id,
        str(config.get("strike_selection", "ATM_OFFSET")),
        str(config.get("hedge_mode", "NONE")),
        str(config.get("exit_rule", "15:15_IST")),
        risk,
        delta_resolver_passed=delta_resolver_passed,
        intraday_futures_passed=intraday_futures_passed,
    )
    if gate not in {"ELIGIBLE_FOR_CONTRACT_RESOLUTION", "DIAGNOSTIC_ONLY"}:
        return blocked(gate, family_id, gate_reason)
    if family_id in FUTURES_REQUIRED_FAMILIES:
        return blocked("BLOCKED_INTRADAY_FUTURES", family_id, "this resolver has no actual futures-contract/quote mapping even when a future feed is flagged present")
    if str(config.get("exit_rule")) == "TAKE_PROFIT_50_PERCENT_MAX_PROFIT" and family_id in INFINITE_OR_UNDEFINED_TP_BLOCK | PATH_DEPENDENT_TP_BLOCK:
        return blocked("BLOCKED_EXIT_SEMANTICS", family_id, "finite path-consistent maximum profit is not defined under protocol v1.0")
    pairing = str(config.get("expiry_pairing", "WEEKLY_WEEKLY"))
    width = int(config.get("wing_width_steps", 1))
    if width <= 0:
        return blocked("BLOCKED_INVALID_WING_WIDTH", family_id, "wing width must be positive")
    rules = RULES[family_id]

    # Bind the strike anchors. For ABS_DELTA, the source audit covered only 0.15/0.30;
    # every selected leg still must pass its own exact entry-bar and prior-OI gates.
    anchors: dict[str, float] = {}
    for anchor in ("CENTER", "CALL", "PUT"):
        used = any(x.anchor == anchor for x in rules)
        if not used:
            continue
        value, anchor_status = _anchor_strike(
            anchor, atm, step, config, entry_ts, target_expiry,
            delta_selections, delta_resolver_passed
        )
        if value is None:
            return blocked(anchor_status, family_id, f"could not resolve {anchor} anchor from the registered selection mode")
        anchors[anchor] = float(value)

    # Compute every raw leg strike/expiry first. Ratio parameters, if present,
    # replace magnitudes for the first and second template legs only (protocol).
    far_expiry = None
    leg_drafts = []
    for i, rule in enumerate(rules):
        expiry, expiry_status = _resolved_expiry(rule.expiry_role, target_expiry, listed_expiries, pairing)
        if expiry is None:
            return blocked(expiry_status, family_id, "required listed far expiry is unavailable")
        if rule.expiry_role == "far":
            far_expiry = expiry
        strike = anchors[rule.anchor] + (rule.fixed_steps + rule.width_steps * width) * step
        strike = float(round(strike, 8))
        leg_drafts.append({
            "leg_id": f"L{i+1}",
            "side": rule.side,
            "option_type": rule.option_type,
            "base_quantity_lots": int(rule.quantity),
            "quantity_lots": int(rule.quantity),
            "anchor": rule.anchor,
            "relative_offset_steps": int(rule.fixed_steps + rule.width_steps * width),
            "strike": strike,
            "expiry_role": rule.expiry_role,
            "expiry": expiry,
        })
    ratio = config.get("leg_ratio")
    if ratio is not None:
        if not isinstance(ratio, (list, tuple)) or len(ratio) != 2:
            return blocked("BLOCKED_INVALID_LEG_RATIO", family_id, "leg_ratio must have exactly two positive integer magnitudes")
        try:
            r1, r2 = int(ratio[0]), int(ratio[1])
        except (TypeError, ValueError):
            return blocked("BLOCKED_INVALID_LEG_RATIO", family_id, "leg_ratio values must be integer magnitudes")
        if r1 < 1 or r2 < 1 or float(ratio[0]) != r1 or float(ratio[1]) != r2:
            return blocked("BLOCKED_INVALID_LEG_RATIO", family_id, "leg_ratio values must be positive integers")
        if len(leg_drafts) >= 1:
            leg_drafts[0]["quantity_lots"] = r1
        if len(leg_drafts) >= 2:
            leg_drafts[1]["quantity_lots"] = r2

    # Resolve every exact entry bar and prior completed-minute OI record for the
    # actual strike/expiry/type; no nearest strike, interpolation, or OI fill.
    resolved_legs = []
    exclusions = []
    for draft in leg_drafts:
        bar_result = select_exact_bar(
            entry_chain, entry_ts, draft["expiry"], draft["option_type"], draft["strike"]
        )
        if bar_result.status != "PASS" or bar_result.row is None:
            exclusions.append({"leg_id": draft["leg_id"], "status": bar_result.status, "detail": bar_result.detail, **draft})
            return {
                "status": "BLOCKED_LEG_ELIGIBILITY",
                "family_id": family_id,
                "template_rule_id": rule_id,
                "reason": "a required exact selected-strike entry bar is unavailable or invalid",
                "leg_exclusions": exclusions,
                "legs": [],
                "pnl_computed": False,
                "promotable": False,
            }
        oi_ok, oi, oi_status = exact_prior_oi(
            prior_chain, entry_ts, draft["expiry"], draft["option_type"], draft["strike"], MIN_OI
        )
        if not oi_ok:
            exclusions.append({"leg_id": draft["leg_id"], "status": oi_status, "prior_oi": oi, **draft})
            return {
                "status": "BLOCKED_LEG_ELIGIBILITY",
                "family_id": family_id,
                "template_rule_id": rule_id,
                "reason": "a required selected leg lacks exact prior-bar OI at or above 100",
                "leg_exclusions": exclusions,
                "legs": [],
                "pnl_computed": False,
                "promotable": False,
            }
        resolved_legs.append({
            **draft,
            "entry_ts": entry_ts.isoformat(),
            "entry_open": float(bar_result.row["open"]),
            "entry_ohlc": {
                key: float(bar_result.row[key]) for key in ("open","high","low","close")
            },
            "prior_oi_ts": (entry_ts - pd.Timedelta(minutes=1)).isoformat(),
            "prior_open_interest": float(oi),
            "prior_oi_status": "PASS",
        })
    diagnostic = gate == "DIAGNOSTIC_ONLY"
    return {
        "status": "DIAGNOSTIC_ONLY_TEMPLATE_RESOLVED" if diagnostic else "TEMPLATE_RESOLVED_ENTRY_GATES_PASS",
        "resolver_version": RESOLVER_VERSION,
        "template_manifest_version": frozen.get("manifest_version"),
        "family_id": family_id,
        "family_name": spec.get("family_name"),
        "template_rule_id": rule_id,
        "specification_status": spec.get("specification_status"),
        "source_ref": spec.get("source_ref"),
        "risk_notes": spec.get("risk_notes"),
        "grid_version": "phase52-grid-v1.3",
        "entry_ts": entry_ts.isoformat(),
        "target_expiry": target_expiry,
        "far_expiry": far_expiry,
        "strike_selection": str(config.get("strike_selection", "ATM_OFFSET")).upper(),
        "spot_open": spot,
        "spot_timestamp": spot_ts.isoformat(),
        "atm_reference_strike": float(atm),
        "modal_strike_step": float(step),
        "anchors": anchors,
        "wing_width_steps": width,
        "leg_ratio": list(ratio) if ratio is not None else None,
        "reference_lots_per_leg": int(config.get("reference_lots_per_leg", 1)),
        "legs": resolved_legs,
        "pnl_computed": False,
        "promotable": False,
        "gate_status": gate,
        "gate_reason": gate_reason,
        "limitations": [
            "This resolves a template and verifies entry bars/prior OI only; exit-bar/common-time resolution and costed P&L are not performed.",
            "Minute OHLC open prices are simulation references, not observed bid/ask or tick-level execution.",
            "Every leg is individually checked at exact expiry/type/strike/time with strictly prior-bar OI>=100.",
            "Diagnostic-only family results can never be promoted.",
        ],
    }


def blocked(status: str, family_id: str, reason: str) -> dict[str, Any]:
    return {
        "status": status, "family_id": family_id, "reason": reason,
        "legs": [], "pnl_computed": False, "promotable": False,
    }


def synthetic_fixture(
    expiries: Sequence[str] = ("2026-04-16","2026-04-23","2026-05-28","2026-06-25"),
    remove_entry: tuple[str,str,float] | None = None,
    prior_oi_override: tuple[str,str,float] | None = None,
) -> tuple[pd.DataFrame,pd.DataFrame,dict[str,Any],list[str]]:
    entry_ts = pd.Timestamp("2026-04-15T09:45:00+05:30")
    prior_ts = entry_ts - pd.Timedelta(minutes=1)
    strikes = list(range(21000, 23001, 50))
    entry_rows, prior_rows = [], []
    for exp in expiries:
        for typ in ("CE","PE"):
            for strike in strikes:
                entry_bar = {
                    "timestamp": entry_ts, "expiry": exp, "option_type": typ, "strike": float(strike),
                    "open": 100.0 + abs(strike - 22000) / 100.0,
                    "high": 102.0 + abs(strike - 22000) / 100.0,
                    "low": 99.0 + abs(strike - 22000) / 100.0,
                    "close": 100.5 + abs(strike - 22000) / 100.0,
                    "open_interest": 999.0,
                }
                prior_oi = 500.0
                if prior_oi_override and (exp,typ,float(strike)) == prior_oi_override:
                    prior_oi = 99.0
                prior_rows.append({
                    "timestamp": prior_ts, "expiry": exp, "option_type": typ,
                    "strike": float(strike), "open_interest": prior_oi,
                })
                if remove_entry and (exp,typ,float(strike)) == remove_entry:
                    continue
                entry_rows.append(entry_bar)
    entry_chain = pd.DataFrame(entry_rows)
    prior_chain = pd.DataFrame(prior_rows)
    event = {"expiry":expiries[0],"entry_ts":entry_ts,"spot_open":22000.0,"spot_timestamp":entry_ts}
    return entry_chain, prior_chain, event, list(expiries)


def synthetic_delta_rows(expiry: str, entry_ts: Any, target: float = 0.15) -> list[dict[str,Any]]:
    ts = as_ist(entry_ts).isoformat()
    return [
        {"expiry":expiry,"entry_ts":ts,"option_type":"CE","target_abs_delta":target,
         "selected_strike":22050.0,"status":"MODEL_DELTA_SELECTED_ENTRY_BAR_PASS",
         "entry_fill_bar_available":True,"predecision_oi_ge_100":True},
        {"expiry":expiry,"entry_ts":ts,"option_type":"PE","target_abs_delta":target,
         "selected_strike":21950.0,"status":"MODEL_DELTA_SELECTED_ENTRY_BAR_PASS",
         "entry_fill_bar_available":True,"predecision_oi_ge_100":True},
    ]


def self_test() -> dict[str, Any]:
    specs = load_csv(SPECS_PATH)
    manifest = load_source_manifest()
    spec_by = {x["family_id"]:x for x in specs}
    assert set(spec_by) == set(manifest["families"]), "manifest family set differs from source spec CSV"
    assert len(specs) == manifest["family_count"] == 52, (len(specs), manifest["family_count"])
    supported_count = 0
    blocked_count = 0
    diagnostic_count = 0
    for fam, spec in spec_by.items():
        bound, rule = validate_spec_binding(spec, manifest)
        assert bound, (fam, rule)
        if rule in RULES:
            supported_count += 1
        elif rule.startswith("BLOCKED_"):
            blocked_count += 1
        else:
            raise AssertionError(f"family {fam} has no explicit rule or blocked status: {rule}")
    assert supported_count == len(RULES), (supported_count,len(RULES))
    assert blocked_count + supported_count == 52, (blocked_count,supported_count)

    entry, prior, event, expiry_list = synthetic_fixture()
    base = {"strike_selection":"ATM_OFFSET","atm_offset_steps":2,"wing_width_steps":3,
            "reference_lots_per_leg":1,"exit_rule":"15:15_IST","hedge_mode":"NONE",
            "liquidity_max_spread_pct":2.0,"expiry_pairing":"WEEKLY_WEEKLY"}
    resolved = {}
    expected_legs = {
        "BUY_CALL":1,"BUY_PUT":1,"SELL_CALL":1,"SELL_PUT":1,
        "BULL_CALL_SPREAD":2,"BEAR_PUT_SPREAD":2,"BULL_PUT_SPREAD":2,"BEAR_CALL_SPREAD":2,
        "LONG_STRADDLE":2,"SHORT_STRADDLE":2,"LONG_STRANGLE":2,"SHORT_STRANGLE":2,
        "SHORT_IRON_CONDOR":4,"LONG_IRON_CONDOR":4,"SHORT_IRON_BUTTERFLY":4,"LONG_IRON_BUTTERFLY":4,
        "BULL_CONDOR":4,"BEAR_CONDOR":4,"BULL_BUTTERFLY":3,"BEAR_BUTTERFLY":3,"CALL_BUTTERFLY":3,"PUT_BUTTERFLY":3,
        "CALL_BROKEN_WING_BUTTERFLY":3,"PUT_BROKEN_WING_BUTTERFLY":3,"CALL_RATIO_SPREAD":2,"PUT_RATIO_SPREAD":2,
        "CALL_RATIO_BACKSPREAD":2,"PUT_RATIO_BACKSPREAD":2,"JADE_LIZARD":3,"REVERSE_JADE_LIZARD":3,
        "RANGE_FORWARD":2,"BEAR_RISK_REVERSAL":2,"STRIP":2,"STRAP":2,"BATMAN":4,"DOUBLE_PLATEAU":6,
        "CALL_CALENDAR":2,"PUT_CALENDAR":2,"DOUBLE_CALENDAR":4,"CALL_DIAGONAL":2,"PUT_DIAGONAL":2,
        "DOUBLE_DIAGONAL":4,"RATIO_CALENDAR":2,"LONG_SYNTHETIC_FUTURE":2,"SHORT_SYNTHETIC_FUTURE":2
    }
    for fam, expected_n in expected_legs.items():
        conf = dict(base)
        if fam in {"CALL_RATIO_SPREAD","PUT_RATIO_SPREAD","CALL_RATIO_BACKSPREAD","PUT_RATIO_BACKSPREAD",
                   "JADE_LIZARD","REVERSE_JADE_LIZARD","RANGE_FORWARD","BEAR_RISK_REVERSAL","STRIP","STRAP",
                   "BATMAN","CALL_CALENDAR","PUT_CALENDAR","DOUBLE_CALENDAR","CALL_DIAGONAL","PUT_DIAGONAL",
                   "DOUBLE_DIAGONAL","RATIO_CALENDAR","LONG_STRANGLE","SHORT_STRANGLE","LONG_STRADDLE","SHORT_STRADDLE"}:
            conf["leg_ratio"] = [1,2]
        result = resolve_template(fam, conf, event, entry, prior, expiry_list, specs, manifest)
        assert result["status"] in {"TEMPLATE_RESOLVED_ENTRY_GATES_PASS","DIAGNOSTIC_ONLY_TEMPLATE_RESOLVED"}, (fam,result)
        assert len(result["legs"]) == expected_n, (fam,len(result["legs"]),expected_n)
        assert all(x["prior_oi_status"]=="PASS" and x["entry_ohlc"]["open"] > 0 for x in result["legs"]), fam
        assert result["pnl_computed"] is False and result["promotable"] is False
        resolved[fam] = result
        if result["status"] == "DIAGNOSTIC_ONLY_TEMPLATE_RESOLVED":
            diagnostic_count += 1

    # Ratio override is literal for the first two template legs.
    ratio_conf = dict(base, leg_ratio=[2,1])
    ratio = resolve_template("CALL_RATIO_SPREAD",ratio_conf,event,entry,prior,expiry_list,specs,manifest)
    assert [x["quantity_lots"] for x in ratio["legs"]] == [2,1]

    # Center structures share the call-side strike for CE+PE; OTM anchors split.
    straddle = resolved["LONG_STRADDLE"]
    assert straddle["legs"][0]["strike"] == straddle["legs"][1]["strike"] == 22100.0
    condor = resolved["SHORT_IRON_CONDOR"]
    put_short = next(x for x in condor["legs"] if x["option_type"]=="PE" and x["side"]=="SELL")
    call_short = next(x for x in condor["legs"] if x["option_type"]=="CE" and x["side"]=="SELL")
    assert put_short["strike"] == 21900.0 and call_short["strike"] == 22100.0

    # Expiry-pairing is based on actual listed expiries.
    far_weekly = select_far_expiry(event["expiry"],expiry_list,"WEEKLY_WEEKLY")
    far_monthly = select_far_expiry(event["expiry"],expiry_list,"WEEKLY_MONTHLY")
    assert far_weekly == "2026-04-23", far_weekly
    assert far_monthly == "2026-05-28", far_monthly
    monthly = resolve_template("CALL_CALENDAR",dict(base,expiry_pairing="WEEKLY_MONTHLY"),event,entry,prior,expiry_list,specs,manifest)
    assert monthly["legs"][1]["expiry"] == "2026-05-28"

    # No silent substitutions: a missing selected strike, missing prior OI or low OI blocks the whole position.
    missing_entry, p2, e2, xs = synthetic_fixture(remove_entry=("2026-04-16","CE",22100.0))
    missing_result = resolve_template("BUY_CALL",base,e2,missing_entry,p2,xs,specs,manifest)
    assert missing_result["status"] == "BLOCKED_LEG_ELIGIBILITY", missing_result
    low_entry, low_prior, e3, xs3 = synthetic_fixture(prior_oi_override=("2026-04-16","CE",22100.0))
    low_oi_result = resolve_template("BUY_CALL",base,e3,low_entry,low_prior,xs3,specs,manifest)
    assert low_oi_result["status"] == "BLOCKED_LEG_ELIGIBILITY", low_oi_result

    # Every unregistered delta target and any ABS_DELTA config without the full audit gate blocks.
    delta_block = resolve_template("BUY_CALL",dict(base,strike_selection="ABS_DELTA",absolute_delta=0.15),
        event,entry,prior,expiry_list,specs,manifest)
    assert delta_block["status"] == "BLOCKED_DELTA_RESOLVER", delta_block
    delta_out_of_grid = resolve_template("BUY_CALL",dict(base,strike_selection="ABS_DELTA",absolute_delta=0.4),
        event,entry,prior,expiry_list,specs,manifest,synthetic_delta_rows(event["expiry"],event["entry_ts"],0.4),True)
    assert delta_out_of_grid["status"] == "BLOCKED_DELTA_TARGET_NOT_AUDITED", delta_out_of_grid
    delta_pass = resolve_template("BUY_CALL",dict(base,strike_selection="ABS_DELTA",absolute_delta=0.15),
        event,entry,prior,expiry_list,specs,manifest,synthetic_delta_rows(event["expiry"],event["entry_ts"],0.15),True)
    assert delta_pass["status"] == "TEMPLATE_RESOLVED_ENTRY_GATES_PASS", delta_pass

    # Missing listed far expiry, missing exact spot, unsupported exits, futures and spec drift all fail closed.
    only_near = resolve_template("CALL_CALENDAR",base,event,entry,prior,[event["expiry"]],specs,manifest)
    assert only_near["status"] == "BLOCKED_FAR_EXPIRY_UNAVAILABLE", only_near
    bad_spot = resolve_template("BUY_CALL",base,dict(event,spot_timestamp=event["entry_ts"]-pd.Timedelta(minutes=1)),entry,prior,expiry_list,specs,manifest)
    assert bad_spot["status"] == "BLOCKED_INDEX_ENTRY_TIMESTAMP_OR_PRICE"
    tp_block = resolve_template("BUY_CALL",dict(base,exit_rule="TAKE_PROFIT_50_PERCENT_MAX_PROFIT"),event,entry,prior,expiry_list,specs,manifest)
    assert tp_block["status"] == "BLOCKED_EXIT_SEMANTICS"
    spec_mutated = [dict(x) for x in specs]
    spec_mutated[0]["leg_template"] += " (mutated)"
    drift = resolve_template("BUY_CALL",base,event,entry,prior,expiry_list,spec_mutated,manifest)
    assert drift["status"] == "BLOCKED_TEMPLATE_MANIFEST_DRIFT", drift
    blocked_specs = [x for x in specs if x["specification_status"] == "SPECIFICATION_BLOCKED"]
    for s in blocked_specs:
        result = resolve_template(s["family_id"],base,event,entry,prior,expiry_list,specs,manifest)
        assert result["status"] == "BLOCKED_SPECIFICATION", (s["family_id"],result)
    for fam in FUTURES_REQUIRED_FAMILIES:
        if fam in spec_by:
            result=resolve_template(fam,base,event,entry,prior,expiry_list,specs,manifest,intraday_futures_passed=True)
            assert result["status"]=="BLOCKED_INTRADAY_FUTURES", (fam,result)

    return {
        "status":"PASS",
        "resolver_version":RESOLVER_VERSION,
        "source_spec_family_count":len(specs),
        "supported_option_template_count":supported_count,
        "explicitly_blocked_template_count":blocked_count,
        "families_tested_with_synthetic_chain":len(expected_legs),
        "resolved_templates_tested":len(resolved),
        "diagnostic_only_templates_in_test_set":diagnostic_count,
        "tests":[
            "source spec exact-binding to frozen manifest for all families",
            "all 45 option-only source-reconciled templates resolve against a synthetic exact-time chain",
            "exact contract/time/expiry selection and prior T-1 OI>=100 for every leg",
            "no nearest strike substitution and no OI forward-fill",
            "first-two-leg ratio semantics as frozen in protocol",
            "shared center vs independent call/put OTM anchors",
            "actual listed far-expiry pairing",
            "fail-closed missing target leg, prior OI, exact spot, far expiry, unresolved spec and manifest drift",
            "ABS_DELTA blocks until audit gate; only audited target deltas allowed",
            "futures templates remain blocked without a futures-contract resolver",
            "resolver never computes P&L or promotes a candidate"
        ],
        "manifest_sha256":sha256_file(MANIFEST_PATH),
        "specification_csv_sha256":sha256_file(SPECS_PATH),
        "resolver_sha256":sha256_file(Path(__file__)),
        "protocol_sha256":sha256_file(PROTOCOL_PATH),
        "no_historical_market_data_used":True,
        "no_pnl_computed":True
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--report", type=Path)
    args=parser.parse_args()
    if not args.self_test:
        raise SystemExit("Synthetic resolver tests only; no historical strategy P&L worker is integrated.")
    report=self_test()
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
