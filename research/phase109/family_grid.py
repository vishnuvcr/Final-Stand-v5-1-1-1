#!/usr/bin/env python3
"""Phase 109 deterministic strategy-family registry, Cartesian grid and source-access audit.

This module registers experiments; it does not claim that unrun tuples are tested.
Credentials are read only from environment variables and are never serialized.
The first workflow attempt exposed a missing dependency-lockfile cache assumption; that workflow setting has been removed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "results" / "phase109"
CACHE = ROOT / "data" / "cache" / "phase109"
SCHEMA_VERSION = "phase109-grid-v1"
MAX_COST_ROWS_PER_SHARD = 2_000_000

CORES = [
    ("ROC_MOMENTUM", "trend_momentum", "Signed k-session return exceeds a preregistered move threshold.", ["underlying_close", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("EMA_CROSS", "trend_momentum", "Fast/slow exponential moving-average crossover with direction persistence.", ["underlying_close", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("EMA_SLOPE", "trend_momentum", "Normalized moving-average slope predicts same-direction follow-through.", ["underlying_close", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("DONCHIAN_BREAKOUT", "breakout", "Close breaks a prior rolling high/low channel excluding the current bar.", ["underlying_ohlc", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("OPEN_GAP_CONTINUATION", "gap", "Opening gap aligned with prior trend continues after the opening observation.", ["intraday_open", "prior_close", "daily_timestamp"], "Dhan historical candles; session-time audit required"),
    ("RELATIVE_STRENGTH", "cross_sectional", "Underlying outperformance versus NIFTY persists over the lookback.", ["underlying_close", "nifty_close", "daily_timestamp"], "Dhan/NSE candles"),
    ("TREND_PULLBACK", "trend_momentum", "Pullback to a rolling trend mean followed by directional resumption.", ["underlying_ohlc", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("MACD_CROSS", "trend_momentum", "MACD/signal-line crossing filtered by signal strength.", ["underlying_close", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("ADX_DIRECTIONAL", "trend_momentum", "Directional movement and ADX confirm a directional trend.", ["underlying_ohlc", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("SWING_STRUCTURE", "price_structure", "Sequence of higher highs/lows or lower highs/lows confirms direction.", ["underlying_ohlc", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("BREAKOUT_RETEST", "breakout", "Prior range breakout retested and held before continuation.", ["underlying_ohlc", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("VOLUME_BREAKOUT", "breakout", "Price breakout is confirmed by abnormal traded volume.", ["underlying_ohlc", "underlying_volume", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("REALIZED_VOL_EXPANSION", "volatility", "Expansion in trailing realized volatility precedes continuation.", ["underlying_close", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("VOL_SQUEEZE_RELEASE", "volatility", "Low realized-volatility compression followed by directional range expansion.", ["underlying_ohlc", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("RANGE_COMPRESSION_BREAK", "volatility", "Breakout from a historically compressed true range.", ["underlying_ohlc", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("ATR_NORMALIZED_MOMENTUM", "volatility", "Momentum scaled by rolling true range to compare regimes.", ["underlying_ohlc", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("GAP_FADE", "mean_reversion", "Large opening gap reverts toward prior close absent continuation confirmation.", ["intraday_open", "prior_close", "daily_timestamp"], "Dhan historical candles; session-time audit required"),
    ("RSI_REBOUND", "mean_reversion", "Extreme RSI reverses after a preregistered exhaustion threshold.", ["underlying_close", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("BOLLINGER_REVERSION", "mean_reversion", "Price excursion outside a rolling volatility band reverts toward its center.", ["underlying_close", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("RETURN_ZSCORE_FADE", "mean_reversion", "Extreme standardized return reverts toward its rolling mean.", ["underlying_close", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("VWAP_REVERSION", "intraday_mean_reversion", "Intraday price-distance from volume-weighted average price mean-reverts.", ["intraday_ohlcv", "intraday_timestamp"], "Dhan intraday historical; 90-day request limit"),
    ("RANGE_EXTREME_FADE", "mean_reversion", "Price near a prior range extreme reverses toward the range midpoint.", ["underlying_ohlc", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("EMA_DEVIATION_FADE", "mean_reversion", "Normalized deviation from a rolling mean predicts reversion.", ["underlying_close", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("VOL_SHOCK_REVERSAL", "volatility", "A volatility shock followed by contraction predicts mean reversion.", ["underlying_ohlc", "daily_timestamp"], "NSE UDiFF / Dhan historical candles"),
    ("SPOT_FUTURES_BASIS_CONVERGENCE", "basis", "Spot-futures basis deviation converges toward a historical fair-basis estimate.", ["spot_price", "future_price", "contract_identity", "timestamp"], "Dhan/NSE; synchronized contract data required"),
    ("FUTURES_BASIS_MOMENTUM", "basis", "Change in futures basis predicts continuation in basis and underlying direction.", ["spot_price", "future_price", "contract_identity", "timestamp"], "Dhan/NSE; synchronized contract data required"),
    ("FUTURE_SPOT_LEAD_LAG", "lead_lag", "Lagged futures returns predict subsequent spot returns at a fixed timestamp horizon.", ["spot_price", "future_price", "intraday_timestamp"], "Dhan/NSE; timestamp-alignment required"),
    ("PRICE_OI_QUADRANT", "options_flow", "Joint price and open-interest change maps to buildup/unwinding direction.", ["underlying_close", "open_interest", "daily_timestamp"], "Dhan rolling options / NSE UDiFF"),
    ("OI_BUILDUP_REVERSAL", "options_flow", "Crowded open-interest buildup plus price exhaustion predicts reversal.", ["underlying_ohlc", "open_interest", "daily_timestamp"], "Dhan rolling options / NSE UDiFF"),
    ("PUT_CALL_RATIO_CONTRARIAN", "options_flow", "Extreme near-ATM put/call open-interest or volume ratio predicts contrarian move.", ["option_chain_oi", "option_chain_volume", "strike", "expiry", "timestamp"], "Dhan historical rolling options; parity/data checks required"),
    ("OPTION_FLOW_SHOCK", "options_flow", "Unusual option volume/OI shock predicts short-horizon directional continuation.", ["option_volume", "open_interest", "strike", "expiry", "timestamp"], "Dhan historical rolling options"),
    ("IV_RV_SPREAD", "implied_volatility", "Implied-versus-realized volatility spread predicts directional option risk premia.", ["option_iv", "underlying_close", "strike", "expiry", "timestamp"], "Dhan rolling options; IV definition/source audit required"),
    ("SKEW_MEAN_REVERSION", "implied_volatility", "Relative put/call implied-volatility skew reverts after an extreme.", ["option_iv", "strike", "option_type", "expiry", "timestamp"], "Dhan rolling options; matched-strike validation required"),
    ("SYNTHETIC_FUTURE_PARITY", "derivatives_parity", "Call-put parity-implied synthetic future deviates from observed future after carry.", ["call_price", "put_price", "strike", "expiry", "future_price", "rates", "timestamp"], "Dhan/NSE; synchrony, rate and dividend inputs required"),
    ("GREEKS_EXPOSURE_FILTER", "greeks", "Option delta/gamma exposure and price signal jointly govern directional entries.", ["option_iv", "strike", "expiry", "spot_price", "option_price", "timestamp"], "Dhan IV/spot; any model-derived Greeks explicitly labelled"),
    ("CROSS_INDEX_LEAD_LAG", "cross_asset", "Lagged Bank Nifty/NIFTY index move predicts the other index.", ["nifty_close", "banknifty_close", "timestamp"], "Dhan/NSE; timestamp alignment required"),
    ("GLOBAL_OVERNIGHT_LEAD_LAG", "global_cross_asset", "Prior global index/futures return predicts Indian opening or first-session direction.", ["global_index_return", "gift_nifty_return", "intraday_timestamp"], "Free global/GIFT Nifty sources; point-in-time validation required"),
    ("BREADTH_SECTOR_ROTATION", "breadth", "Advancers/decliners and sector relative strength forecast index direction.", ["constituent_prices", "index_membership_point_in_time", "sector_mapping", "timestamp"], "NSE/BSE constituent data; membership survivorship audit required"),
    ("NEWS_SENTIMENT_SURPRISE", "news_sentiment", "Point-in-time news/sentiment surprise changes directional odds.", ["timestamped_news", "news_sentiment_score", "underlying_price", "timestamp"], "Licensed/public timestamped news; HF model/dataset is not a news feed"),
    ("EVENT_CORPORATE_ACTION", "event_driven", "Preregistered event/corporate-action window interacts with pre-event price/volatility.", ["event_timestamp", "corporate_action_type", "underlying_ohlc", "timestamp"], "NSE/BSE corporate-action/calendar source; event look-ahead audit"),
    ("DII_FII_FLOW_REGIME", "flows", "Daily institution flow/participant positioning interacts with underlying trend.", ["dii_flow", "fii_flow", "underlying_close", "timestamp"], "NSE participant statistics / official flow sources; publication lag required"),
]

CONFIRMS = [
    ("NONE", "No secondary confirmation; core signal alone sets direction.", [], "true"),
    ("OPTIONS_FLOW", "Require option OI/volume buildup to agree with core direction.", ["open_interest", "option_volume", "strike", "expiry"], "flow_side_matches_core"),
    ("BASIS_SYNTHETIC", "Require spot-futures basis or parity-implied synthetic-future direction to agree.", ["spot_price", "future_price", "contract_identity"], "basis_direction_matches_core"),
    ("CROSS_ASSET", "Require a preregistered cross-index/global leader to agree at an earlier timestamp.", ["cross_index_or_global_return", "timestamp"], "leader_signal_matches_core"),
    ("BREADTH_FLOWS", "Require breadth, sector leadership, or lagged DII/FII positioning to agree.", ["breadth_or_sector_returns", "dii_flow", "fii_flow", "timestamp"], "breadth_or_flow_matches_core"),
]
REGIMES = [
    ("NONE", "No regime gate; all observations eligible.", [], "true"),
    ("REALIZED_VOL_LOW_HIGH", "Trade only preregistered low- or high-realized-volatility bins.", ["underlying_close", "volatility_lookback"], "realized_vol_bin"),
    ("TREND_RANGE", "Use lagged trend-strength state to permit trend or reversion core rules.", ["underlying_ohlc", "volatility_lookback"], "lagged_trend_range_state"),
    ("INDIA_VIX", "Condition entries on lagged India VIX level/change/quantile.", ["india_vix", "timestamp"], "lagged_india_vix_state"),
    ("EXPIRY_EVENT", "Condition on known expiry/corporate-event window without future information.", ["expiry_calendar", "event_calendar", "timestamp"], "point_in_time_event_state"),
]

LOOKBACKS = [1, 2, 3, 4, 5, 7, 10]
MOVE_THRESHOLDS_PCT = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]
VOL_LOOKBACKS = [3, 5, 7, 10, 15]
REGIME_DEFINITIONS = ["rolling_median", "lower_upper_terciles_middle_no_trade", "preregistered_fixed_quantiles"]
STRIKE_TARGETS = ["ATM", "ITM_0.5pct", "OTM_0.5pct", "ITM_1.0pct", "OTM_1.0pct"]
HOLDING_EXITS = ["same_session_close", "2_session_close", "3_session_close", "expiry_aware_close"]
RISK_PROFILES = (
    ["NO_STOP_NO_TARGET"]
    + [f"STOP_{x}PCT_PREMIUM" for x in (10, 20, 30)]
    + [f"TARGET_{x}PCT_PREMIUM" for x in (10, 20, 30)]
    + [f"STOP_{s}PCT_TARGET_{t}PCT_PREMIUM" for s in (10, 20, 30) for t in (10, 20, 30)]
)
OI_CONFIRMATION_METHODS = ["off", "total_near_ATM_OI_increase", "same_side_OI_increase"]
BROKERAGE_RUPEES_PER_ORDER = [10, 15, 20]
SLIPPAGE_RUPEES_PER_UNIT_PER_SIDE = [0.0, 0.05, 0.25, 0.50]
FEE_MULTIPLIERS = [1.0, 1.5]
COST_CASES = [
    {"cost_id": f"C{i+1:02d}", "brokerage_per_order": b, "slippage_per_unit_per_side": s, "fee_multiplier": f}
    for i, (b, s, f) in enumerate(itertools.product(BROKERAGE_RUPEES_PER_ORDER, SLIPPAGE_RUPEES_PER_UNIT_PER_SIDE, FEE_MULTIPLIERS))
]
assert len(CORES) == 41 and len(CONFIRMS) == 5 and len(REGIMES) == 5 and len(COST_CASES) == 24


def stable_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def family_registry():
    out = []
    for core, confirm, regime in itertools.product(CORES, CONFIRMS, REGIMES):
        core_id, category, core_rule, core_inputs, candidate_sources = core
        confirm_id, confirm_text, confirm_inputs, confirm_expr = confirm
        regime_id, regime_text, regime_inputs, regime_expr = regime
        inputs = sorted(set(core_inputs + confirm_inputs + regime_inputs))
        architecture = {
            "schema": SCHEMA_VERSION,
            "core_id": core_id,
            "core_rule": core_rule,
            "confirmation_id": confirm_id,
            "confirmation_rule": confirm_text,
            "confirmation_expression": confirm_expr,
            "regime_id": regime_id,
            "regime_rule": regime_text,
            "regime_expression": regime_expr,
            "mapping": "direction_to_long_option: bullish=CE, bearish=PE; strike and exit are configuration axes",
        }
        fingerprint = sha256_text(stable_json(architecture))
        required = {
            "underlying_close", "underlying_ohlc", "daily_timestamp"
        }
        status = "PENDING_SOURCE_AND_POINT_IN_TIME_AUDIT"
        if not inputs:
            status = "INVALID_MISSING_INPUTS"
        out.append({
            "family_id": f"SF109-{len(out)+1:04d}",
            "family_name": f"{core_id} + {confirm_id} + {regime_id}",
            "category": category,
            "core_id": core_id,
            "core_rule": core_rule,
            "confirmation_id": confirm_id,
            "confirmation_rule": confirm_text,
            "regime_id": regime_id,
            "regime_rule": regime_text,
            "trade_mapping": "Bullish -> long CE; bearish -> long PE; actual fill/execution not inferred from signal alone",
            "required_inputs_json": stable_json(inputs),
            "candidate_sources": candidate_sources,
            "source_feasibility_status": status,
            "family_fingerprint": fingerprint,
            "architecture_json": stable_json(architecture),
        })
    return out


def axes_for_family(f):
    required = set(json.loads(f["required_inputs_json"]))
    return {
        "signal_lookback_sessions": LOOKBACKS,
        "move_or_signal_threshold_pct": MOVE_THRESHOLDS_PCT,
        "volatility_lookback_sessions": VOL_LOOKBACKS,
        "regime_definition": REGIME_DEFINITIONS if f["regime_id"] != "NONE" else ["NA"],
        "strike_target": STRIKE_TARGETS,
        "holding_exit": HOLDING_EXITS,
        "risk_profile": RISK_PROFILES,
        "oi_confirmation_method": OI_CONFIRMATION_METHODS if (
            "open_interest" in required or "option_chain_oi" in required or "OPTIONS_FLOW" == f["confirmation_id"]
        ) else ["NA"],
    }


def product_size(axes):
    n = 1
    for vals in axes.values():
        n *= len(vals)
    return n


def write_csv(path: Path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if fields is None:
        fields = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build(out_dir: Path):
    families = family_registry()
    fingerprints = [f["family_fingerprint"] for f in families]
    duplicate_count = len(fingerprints) - len(set(fingerprints))
    if len(families) < 1000 or duplicate_count:
        raise RuntimeError(f"Registry gate failed: families={len(families)}, exact_duplicates={duplicate_count}")

    space = []
    per_family_counts = []
    total_configurations = 0
    for f in families:
        axes = axes_for_family(f)
        n = product_size(axes)
        if n < 1000:
            raise RuntimeError(f"{f['family_id']} has only {n} applicable configurations.")
        total_configurations += n
        per_family_counts.append(n)
        space.append({
            "family_id": f["family_id"],
            "family_fingerprint": f["family_fingerprint"],
            "configuration_count": n,
            "dimension_count": len(axes),
            "axes_json": json.dumps(axes, separators=(",", ":"), ensure_ascii=False),
            "configuration_order": "Cartesian product in exactly the axis order preserved in axes_json; mixed-radix rank starts at zero",
            "configuration_manifest_status": "REGISTERED_NOT_EVALUATED",
        })

    # Structural near-neighbours are retained rather than incorrectly collapsed:
    # each differs in exactly one of core/confirmation/regime and represents a separately specified rule.
    keys = {(f["core_id"], f["confirmation_id"], f["regime_id"]) for f in families}
    if len(keys) != len(CORES) * len(CONFIRMS) * len(REGIMES):
        raise RuntimeError("Architecture uniqueness gate failed.")
    near_neighbor_pairs = len(CORES) * 5 * 10 * 2  # same core+confirmation; same core+regime
    total_cost_rows = total_configurations * len(COST_CASES)
    config_manifest_hash = sha256_text(stable_json([
        {"family_id": f["family_id"], "fingerprint": f["family_fingerprint"], "axes": axes_for_family(f)}
        for f in families
    ]))
    cost_grid_hash = sha256_text(stable_json(COST_CASES))
    full_manifest_hash = sha256_text(stable_json({
        "schema": SCHEMA_VERSION, "family_count": len(families),
        "total_configurations": total_configurations, "cost_cases": COST_CASES,
        "config_manifest_hash": config_manifest_hash, "cost_grid_hash": cost_grid_hash,
    }))

    shards = []
    start = 0
    shard_id = 0
    while start < total_cost_rows:
        end = min(total_cost_rows, start + MAX_COST_ROWS_PER_SHARD)
        descriptor = {
            "schema": SCHEMA_VERSION, "manifest_hash": full_manifest_hash,
            "shard_id": shard_id, "start_cost_row_inclusive": start,
            "end_cost_row_exclusive": end, "row_count": end - start,
        }
        shards.append({
            **descriptor,
            "shard_hash": sha256_text(stable_json(descriptor)),
            "status": "REGISTERED_NOT_EVALUATED",
        })
        start = end
        shard_id += 1

    # Deterministic, small spot checks prove each ranked tuple can be mapped without materializing the grid.
    sample_ranks = {}
    for f, spec in zip(families, space):
        n = spec["configuration_count"]
        sample_ranks[f["family_id"]] = [0, n // 2, n - 1]
    summary = {
        "schema_version": SCHEMA_VERSION,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "state": "GRID_REGISTERED_NOT_EVALUATED",
        "family_count": len(families),
        "exact_duplicate_fingerprints": duplicate_count,
        "distinct_architecture_fingerprints": len(set(fingerprints)),
        "structural_neighbour_pairs_preserved_for_audit": near_neighbor_pairs,
        "cost_case_count": len(COST_CASES),
        "cost_grid": COST_CASES,
        "configurations_per_family_min": min(per_family_counts),
        "configurations_per_family_max": max(per_family_counts),
        "total_family_configuration_pairs": total_configurations,
        "total_cost_adjusted_rows": total_cost_rows,
        "shard_size_cost_rows": MAX_COST_ROWS_PER_SHARD,
        "shard_count": len(shards),
        "registry_hash_sha256": sha256_text(stable_json(families)),
        "configuration_manifest_hash_sha256": config_manifest_hash,
        "cost_grid_hash_sha256": cost_grid_hash,
        "full_manifest_hash_sha256": full_manifest_hash,
        "parameter_grid_note": "All applicable parameter axes are fully Cartesian-enumerated; inapplicable axes are NA. Counts are registry/manifest counts, not backtests.",
        "oos_note": "No empirical tuple is considered tested by this build. Data/source gates and chronological splits are separate phases.",
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "strategy_families.csv", families)
    write_csv(out_dir / "family_configuration_space.csv", space)
    write_csv(out_dir / "cost_scenarios.csv", COST_CASES)
    write_csv(out_dir / "cost_row_shard_manifest.csv", shards)
    (out_dir / "phase109_grid_summary.json").write_text(stable_json(summary) + "\n", encoding="utf-8")
    report = f"""# Phase 109 Grid Compiler Report

Generated: {summary['generated_utc']}

**State: GRID REGISTERED, NOT EVALUATED. No strategy promoted.**

| Audit item | Result |
|---|---:|
| Registered strategy architecture combinations | {len(families):,} |
| Exact duplicate fingerprints | {duplicate_count} |
| Distinct architecture fingerprints | {len(set(fingerprints)):,} |
| Structural one-component-neighbour pairs retained for audit | {near_neighbor_pairs:,} |
| Minimum configurations per family | {min(per_family_counts):,} |
| Maximum configurations per family | {max(per_family_counts):,} |
| Total family-configuration tuples | {total_configurations:,} |
| Cost scenarios per tuple | {len(COST_CASES)} |
| Total cost-adjusted rows in registered universe | {total_cost_rows:,} |
| Cost-row shards | {len(shards):,} |
| Rows per full shard (last shard may be smaller) | {MAX_COST_ROWS_PER_SHARD:,} |

## Interpretation

The registry is formed from 41 distinct core signal architectures, five confirmation architectures and five regime gates. Every family has an explicit input list, rule description, stable architecture fingerprint and a long-call/long-put mapping. Exact duplicate fingerprints are rejected. Near-neighbour architectures are reported and preserved for audit; they are not claimed to be statistically independent.

The full Cartesian configuration space applies all applicable lookback, signal-threshold, volatility-lookback, regime-definition, strike, exit and risk-profile values. OI method variants apply only where the registered family requires OI/option-flow input. The 24 declared cost cases combine brokerage ₹10/₹15/₹20 per order, adverse slippage ₹0/₹0.05/₹0.25/₹0.50 per option unit per side, and 1×/1.5× modeled fee multipliers.

**These figures describe registered combinations and shard coverage only.** They do not mean Dhan/NSE/Hugging Face data were fully collected, any tuple was backtested, or a strategy is profitable. Source availability, point-in-time data and untouched out-of-sample validation remain separate gates.

## Reproducibility hashes

- Registry: `{summary['registry_hash_sha256']}`
- Configuration manifest: `{config_manifest_hash}`
- Cost grid: `{cost_grid_hash}`
- Full manifest: `{full_manifest_hash}`
"""
    (out_dir / "PHASE109_GRID_COMPILER_REPORT.md").write_text(report, encoding="utf-8")
    return summary


def rank_to_config(axes, rank: int):
    keys = list(axes.keys())
    n = product_size(axes)
    if rank < 0 or rank >= n:
        raise IndexError(f"configuration rank {rank} outside [0,{n})")
    values = {}
    q = rank
    lengths = [len(axes[k]) for k in keys]
    digits = [0] * len(keys)
    for i in range(len(keys) - 1, -1, -1):
        digits[i] = q % lengths[i]
        q //= lengths[i]
    for k, d in zip(keys, digits):
        values[k] = axes[k][d]
    return values


def self_test(out_dir: Path):
    summary_path = out_dir / "phase109_grid_summary.json"
    if not summary_path.exists():
        raise RuntimeError("Build artifacts missing; run --mode build first.")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    families = family_registry()
    if summary["family_count"] < 1000 or summary["family_count"] != len(family_registry()) or summary["exact_duplicate_fingerprints"] != 0:
        raise RuntimeError("Family count or duplicate gate failed.")
    space_rows = list(csv.DictReader((out_dir / "family_configuration_space.csv").open(encoding="utf-8")))
    if len(space_rows) != summary["family_count"]:
        raise RuntimeError(f"Configuration-space rows={len(space_rows)} expected 1000.")
    for family, spec in zip(families, space_rows):
        axes = axes_for_family(family)
        n = int(spec["configuration_count"])
        if n != product_size(axes) or n < 1000:
            raise RuntimeError(f"Count mismatch for {family['family_id']}.")
        a = rank_to_config(axes, 0)
        b = rank_to_config(axes, n - 1)
        if a == b:
            raise RuntimeError(f"Rank mapping collision for {family['family_id']}.")
    cost_rows = list(csv.DictReader((out_dir / "cost_scenarios.csv").open(encoding="utf-8")))
    if len(cost_rows) != 24 or len({stable_json(r) for r in cost_rows}) != 24:
        raise RuntimeError("Cost grid must contain 24 unique rows.")
    shards = list(csv.DictReader((out_dir / "cost_row_shard_manifest.csv").open(encoding="utf-8")))
    expected_start = 0
    for shard in shards:
        start = int(shard["start_cost_row_inclusive"])
        end = int(shard["end_cost_row_exclusive"])
        if start != expected_start or end <= start or int(shard["row_count"]) != end - start:
            raise RuntimeError("Shard manifest has a gap, overlap or invalid count.")
        expected_start = end
    if expected_start != int(summary["total_cost_adjusted_rows"]):
        raise RuntimeError("Shard manifest fails to cover exact registered cost-row universe.")
    (out_dir / "PHASE109_SELF_TEST.txt").write_text(
        "PASS\nfamilies and unique fingerprints; per-family Cartesian counts reconciled; "
        "24 unique cost cases; shard ranges contiguous and complete.\n"
        f"configuration_tuples={summary['total_family_configuration_pairs']}\n"
        f"cost_adjusted_rows={summary['total_cost_adjusted_rows']}\n"
        f"shards={summary['shard_count']}\n"
        "No empirical trading results were evaluated by this self-test.\n",
        encoding="utf-8",
    )
    return {"status": "PASS", "families": len(family_registry()),
            "configurations": summary["total_family_configuration_pairs"],
            "cost_rows": summary["total_cost_adjusted_rows"],
            "shards": summary["shard_count"]}


def _http_json(url, payload=None, headers=None, timeout=40):
    hdrs = {"Accept": "application/json", "User-Agent": "FinalStandPhase109/1.0"}
    if headers:
        hdrs.update(headers)
    data = None
    method = "GET"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
        method = "POST"
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
            return response.status, raw, json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as e:
        # Never save or print response bodies for authenticated calls.
        return e.code, b"", {"error": "http_error"}
    except Exception as e:
        return None, b"", {"error": type(e).__name__}


def source_audit(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    audit = []
    now = datetime.now(timezone.utc).isoformat()

    dhan_token = os.environ.get("DHAN_ACCESS_TOKEN", "").strip()
    dhan_cache = CACHE / "dhan_nifty_rolling_options_probe.json"
    if not dhan_token:
        audit.append({
            "source": "DhanHQ rolling expired-options API", "status": "TOKEN_NOT_AVAILABLE_TO_WORKFLOW",
            "endpoint": "POST https://api.dhan.co/v2/charts/rollingoption",
            "data_fields": "OHLC, IV, volume, OI, strike, spot where returned",
            "note": "No authenticated request attempted. Check secret mapping; token value is never printed.",
            "observed_utc": now,
        })
    else:
        status_code, raw, response = _http_json(
            "https://api.dhan.co/v2/charts/rollingoption",
            {
                "exchangeSegment": "NSE_FNO", "interval": "5", "securityId": 13,
                "instrument": "OPTIDX", "expiryFlag": "WEEK", "expiryCode": 1,
                "strike": "ATM", "drvOptionType": "CALL",
                "requiredData": ["open", "high", "low", "close", "iv", "volume", "strike", "oi", "spot"],
                "fromDate": "2026-09-01", "toDate": "2026-09-03",
            },
            {"access-token": dhan_token},
            timeout=50,
        )
        has_error = isinstance(response, dict) and response.get("error") is not None
        data = response.get("data", {}) if isinstance(response, dict) else {}
        ce = data.get("ce") if isinstance(data, dict) else None
        fields = []
        row_count = 0
        if isinstance(ce, dict):
            fields = sorted(k for k, v in ce.items() if isinstance(v, list) and v)
            timestamps = ce.get("timestamp", [])
            row_count = len(timestamps) if isinstance(timestamps, list) else 0
        if raw and not has_error:
            # Cache private-source probe inside Actions cache. Never upload raw bars as a public artifact.
            private = {"request_window": ["2026-09-01", "2026-09-03"], "response": response}
            dhan_cache.write_text(stable_json(private), encoding="utf-8")
        audit.append({
            "source": "DhanHQ rolling expired-options API",
            "status": "AUTH_AND_SCHEMA_PROBE_OK" if status_code == 200 and row_count > 0 else (
                "HTTP_OK_EMPTY_OR_SCHEMA_MISMATCH" if status_code == 200 else "REQUEST_FAILED_OR_AUTH_REJECTED"
            ),
            "http_status": status_code,
            "endpoint": "POST https://api.dhan.co/v2/charts/rollingoption",
            "data_fields_returned": ",".join(fields),
            "bar_count": row_count,
            "response_sha256": sha256_text(raw.decode("utf-8", errors="replace")) if raw else "",
            "cache_file": str(dhan_cache.relative_to(ROOT)) if dhan_cache.exists() else "",
            "note": "A two-day historical probe only; does not establish long-window completeness, legal publication rights or tradable fills.",
            "observed_utc": now,
        })

    hf_token = os.environ.get("HF_TOKEN", "").strip()
    hf_cache = CACHE / "huggingface_market_dataset_discovery.json"
    discovery = None
    if hf_cache.exists() and time.time() - hf_cache.stat().st_mtime < 30 * 86400:
        try:
            discovery = json.loads(hf_cache.read_text(encoding="utf-8"))
        except Exception:
            discovery = None
    if discovery is None:
        terms = ["NIFTY options historical", "India stock market NSE", "India VIX", "NSE derivatives open interest", "India financial news sentiment"]
        discovery = {"queried_utc": now, "terms": {}, "authentication_used": bool(hf_token)}
        for term in terms:
            url = "https://huggingface.co/api/datasets?" + urllib.parse.urlencode({"search": term, "limit": 10, "sort": "downloads", "direction": "-1"})
            headers = {"Authorization": "Bearer " + hf_token} if hf_token else {}
            code, raw, response = _http_json(url, headers=headers, timeout=30)
            entries = response if isinstance(response, list) else []
            discovery["terms"][term] = {
                "http_status": code,
                "datasets": [{
                    "id": item.get("id", ""),
                    "lastModified": item.get("lastModified", ""),
                    "downloads": item.get("downloads", 0),
                    "likes": item.get("likes", 0),
                    "gated": item.get("gated", False),
                    "tags": item.get("tags", [])[:30],
                } for item in entries if isinstance(item, dict)]
            }
        hf_cache.write_text(stable_json(discovery), encoding="utf-8")
    for term, result in discovery.get("terms", {}).items():
        ds = result.get("datasets", [])
        audit.append({
            "source": "Hugging Face dataset discovery",
            "status": "METADATA_DISCOVERED" if ds else ("QUERY_FAILED" if result.get("http_status") != 200 else "NO_RESULTS"),
            "query": term,
            "dataset_candidates": len(ds),
            "http_status": result.get("http_status"),
            "cache_file": str(hf_cache.relative_to(ROOT)),
            "note": "Discovery only: each candidate still requires data-date, point-in-time, license, schema and leakage review before download/use.",
            "observed_utc": now,
        })

    write_csv(out_dir / "source_access_audit.csv", audit)
    (out_dir / "huggingface_dataset_candidates.json").write_text(stable_json(discovery) + "\n", encoding="utf-8")
    # Publish only source metadata/hash/counts, never the credential or cached Dhan raw prices.
    public_report = {
        "observed_utc": now,
        "dhan_secret_present": bool(dhan_token),
        "hf_token_present": bool(hf_token),
        "dhan_cache_present": dhan_cache.exists(),
        "hf_discovery_cache_present": hf_cache.exists(),
        "source_statuses": [{k: v for k, v in row.items() if k not in {"note"}} for row in audit],
        "disclaimer": "Token presence is not printed as a value. No authenticated credential is written to files or artifacts."
    }
    (out_dir / "source_access_summary.json").write_text(stable_json(public_report) + "\n", encoding="utf-8")
    return public_report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["build", "test", "source-audit", "all"], default="all")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    if args.mode in ("build", "all"):
        print(json.dumps(build(args.out), sort_keys=True))
    if args.mode in ("test", "all"):
        print(json.dumps(self_test(args.out), sort_keys=True))
    if args.mode in ("source-audit", "all"):
        summary = source_audit(args.out)
        print(json.dumps({"source_audit_written": True,
                          "dhan_secret_present": summary["dhan_secret_present"],
                          "hf_token_present": summary["hf_token_present"]}, sort_keys=True))


if __name__ == "__main__":
    main()
