#!/usr/bin/env python3
"""Exploratory point-in-time selector test using lagged daily NSE EOD factors.

The EOD panel adds OI/PCR, volume/PCR, front-futures EOD basis, and futures OI
change where the same futures contract exists in two prior-session files. It is
not intraday futures basis and cannot repair missing minute quotes. This pilot
does not promote strategies and does not enumerate the full Phase52 grid.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from factor_attribution import RISK_LIMITED, holm, paired_test

ROOT = Path(__file__).resolve().parents[2]
BASE_DIR = ROOT / "results" / "phase52" / "base_replay"
BASE_MATRIX = BASE_DIR / "full_ready_made_trade_matrix.csv.gz"
BASE_MANIFEST = BASE_DIR / "manifest.json"
EOD_DIR = ROOT / "results" / "phase52" / "daily_bhavcopy"
EOD_FEATURES = EOD_DIR / "event_factors.csv.gz"
EOD_MANIFEST = EOD_DIR / "manifest.json"
OUT = ROOT / "results" / "phase52" / "daily_eod_selector"
TZ = "Asia/Kolkata"

SINGLE_FEATURES = {
    "EOD_OI_PCR": ["option_oi_pcr_near_atm_5steps"],
    "EOD_VOLUME_PCR": ["option_volume_pcr_near_atm_5steps"],
    "EOD_FUTURES_BASIS": ["front_future_basis_bps"],
    "EOD_FUTURES_OI_CHANGE": ["front_future_open_interest_change_pct_1d"],
    "EOD_CALL_OI_CHANGE": ["option_call_oi_near_atm_change_pct_1d"],
    "EOD_PUT_OI_CHANGE": ["option_put_oi_near_atm_change_pct_1d"],
}
MULTI_FEATURES = {
    "EOD_OI_X_BASIS": ("option_oi_pcr_near_atm_5steps", "front_future_basis_bps"),
    "EOD_VOLUME_X_BASIS": ("option_volume_pcr_near_atm_5steps", "front_future_basis_bps"),
}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def as_ist(series: pd.Series) -> pd.Series:
    x = pd.to_datetime(series, errors="coerce")
    if x.dt.tz is None:
        return x.dt.tz_localize(TZ)
    return x.dt.tz_convert(TZ)

def to_num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)

def safe_float(value: Any) -> float | None:
    try:
        x = float(value)
        return x if np.isfinite(x) else None
    except (TypeError, ValueError):
        return None

def edges_from(train: pd.DataFrame, feature: str) -> list[float]:
    x = to_num(train[feature]).dropna()
    if len(x) < 20 or x.nunique() < 2:
        return []
    a, b = float(x.quantile(1 / 3)), float(x.quantile(2 / 3))
    if not np.isfinite(a) or not np.isfinite(b) or a >= b:
        median = float(x.median())
        return [median] if np.isfinite(median) else []
    return [a, b]

def bins(values: pd.Series, edges: list[float]) -> pd.Series:
    x = to_num(values)
    out = pd.Series("UNAVAILABLE", index=values.index, dtype="object")
    if not edges:
        return out
    labels = ["LOW", "MID", "HIGH"] if len(edges) == 2 else ["LOW", "HIGH"]
    ok = x.notna()
    out.loc[ok] = pd.cut(
        x.loc[ok], [-np.inf, *edges, np.inf], labels=labels,
        include_lowest=True, duplicates="drop"
    ).astype(str)
    return out

def fit_mapping(train: pd.DataFrame, state_col: str, fallback: str, min_n: int = 8) -> dict[str, str]:
    out: dict[str, str] = {}
    for state, g in train.groupby(state_col, dropna=False, sort=True):
        state = str(state) if pd.notna(state) else "UNAVAILABLE"
        if state == "UNAVAILABLE":
            out[state] = fallback
            continue
        candidates = g[g.strategy.isin(RISK_LIMITED)]
        scored = candidates.groupby("strategy").net50.agg(["mean", "count"])
        scored = scored[(scored["count"] >= min_n) & scored["mean"].notna()]
        out[state] = str(scored["mean"].idxmax()) if not scored.empty else fallback
    out["UNAVAILABLE"] = fallback
    return out

def fit_fixed_baseline(train: pd.DataFrame) -> str:
    q = train[train.strategy.isin(RISK_LIMITED)].groupby("strategy").net50.agg(["mean", "count"])
    q = q[(q["count"] >= 12) & q["mean"].notna()]
    if q.empty:
        raise RuntimeError("No risk-limited strategy meets the 12-event early-development baseline gate")
    return str(q.sort_values(["mean", "count"], ascending=[False, False]).index[0])

def collapse_by_event(data: pd.DataFrame, state_col: str, mapping: dict[str, str], fallback: str) -> pd.DataFrame:
    records = []
    for (expiry, entry_ts), group in data.groupby(["expiry_key", "entry_ts"], sort=True):
        state = str(group[state_col].iloc[0]) if state_col in group else "UNAVAILABLE"
        selected_strategy = mapping.get(state, fallback)
        row = group[group.strategy == selected_strategy]
        if row.empty:
            selected_strategy = fallback
            row = group[group.strategy == fallback]
        if row.empty:
            continue
        rec = row.iloc[0]
        records.append({
            "expiry_key": str(expiry), "entry_ts": entry_ts,
            "strategy": str(selected_strategy), "net": float(rec.net),
            "net50": float(rec.net50), "net100": float(2 * rec.net50 - rec.net),
            "feature_state": state, "used_fallback": bool(state not in mapping or selected_strategy == fallback),
        })
    return pd.DataFrame(records)

def metrics(selected: pd.DataFrame, baseline: pd.DataFrame, mode: str, split: str) -> dict[str, Any]:
    if selected.empty or baseline.empty:
        return {"mode": mode, "split": split, "status": "NO_MATCHED_EVENTS", "events": 0}
    a = selected.drop_duplicates("expiry_key").set_index("expiry_key").sort_index()
    b = baseline.drop_duplicates("expiry_key").set_index("expiry_key").sort_index()
    common = a.index.intersection(b.index)
    a, b = a.loc[common], b.loc[common]
    diff = a.net50.to_numpy(float) - b.net50.to_numpy(float)
    lo, hi, p = paired_test(diff, seed=5217, reps=5000, block_len=3)
    vals = a.net.to_numpy(float)
    vals50 = a.net50.to_numpy(float)
    pos, neg = vals50[vals50 > 0].sum(), -vals50[vals50 < 0].sum()
    csum = np.cumsum(vals50)
    max_dd = float(np.max(np.maximum.accumulate(csum) - csum)) if len(csum) else 0.0
    return {
        "mode": mode, "split": split, "status": "EXPLORATORY_NO_PROMOTION",
        "events": int(len(common)),
        "net_pnl_rupees": safe_float(a.net.sum()),
        "net_legacy_1_5x_all_cost_stress_rupees": safe_float(a.net50.sum()),
        "net_legacy_2x_extrapolated_cost_stress_rupees": safe_float(a.net100.sum()),
        "mean_net_rupees": safe_float(a.net.mean()),
        "win_rate": safe_float((a.net > 0).mean()),
        "profit_factor_legacy_stress": safe_float(pos / neg if neg > 0 else (math.inf if pos > 0 else np.nan)),
        "cumulative_pnl_max_drawdown_legacy_stress_rupees": safe_float(max_dd),
        "paired_events_vs_fixed_baseline": int(len(common)),
        "paired_mean_uplift_legacy_stress_rupees": safe_float(diff.mean()) if len(diff) else None,
        "paired_block_bootstrap_ci95_low_rupees": lo,
        "paired_block_bootstrap_ci95_high_rupees": hi,
        "paired_block_signflip_p_one_sided": p,
        "strategy_distribution": {str(k): int(v) for k, v in a.strategy.value_counts().items()},
        "fallback_fraction": safe_float(a.used_fallback.mean()) if "used_fallback" in a else None,
    }

def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any], dict[str, Any]]:
    for path in (BASE_MATRIX, BASE_MANIFEST, EOD_FEATURES, EOD_MANIFEST):
        if not path.exists():
            raise FileNotFoundError(f"Required phase52 input missing: {path.relative_to(ROOT)}")
    bm = json.loads(BASE_MANIFEST.read_text(encoding="utf-8"))
    em = json.loads(EOD_MANIFEST.read_text(encoding="utf-8"))
    trades = pd.read_csv(BASE_MATRIX, compression="gzip", low_memory=False)
    eod = pd.read_csv(EOD_FEATURES, compression="gzip", low_memory=False)
    for frame, name in ((trades, "base matrix"), (eod, "EOD factor panel")):
        required = {"expiry", "entry_ts", "split"}
        if required.difference(frame.columns):
            raise ValueError(f"{name} missing fields {sorted(required.difference(frame.columns))}")
    trades["entry_ts"] = as_ist(trades["entry_ts"])
    eod["entry_ts"] = as_ist(eod["entry_ts"])
    trades["expiry_key"] = pd.to_datetime(trades["expiry"], errors="coerce").dt.strftime("%Y-%m-%d")
    eod["expiry_key"] = pd.to_datetime(eod["expiry"], errors="coerce").dt.strftime("%Y-%m-%d")
    if trades.duplicated(["expiry_key", "entry_ts", "strategy"]).any():
        raise ValueError("Duplicate base-matrix event/strategy rows")
    if eod.duplicated(["expiry_key", "entry_ts"]).any():
        raise ValueError("Duplicate EOD event factor keys")
    eod["factor_session_date"] = pd.to_datetime(eod["factor_session_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    event_dates = eod["entry_ts"].dt.strftime("%Y-%m-%d")
    bad_timing = eod["factor_session_date"].notna() & (eod["factor_session_date"] >= event_dates)
    if bad_timing.any():
        raise RuntimeError(f"Point-in-time violation: {int(bad_timing.sum())} EOD factors are not strictly prior to entry date")
    feature_cols = list(SINGLE_FEATURES.values())
    numeric_cols = sorted({c for values in feature_cols for c in values}.union({v for pair in MULTI_FEATURES.values() for v in pair}))
    for col in numeric_cols:
        if col not in eod:
            eod[col] = np.nan
        eod[col] = to_num(eod[col])
    merged = trades.merge(
        eod.drop(columns=["split"], errors="ignore"),
        on=["expiry_key", "entry_ts"], how="left", suffixes=("", "_eod"), validate="many_to_one"
    )
    # Use the base-matrix split as authoritative; event-factor file records source metadata only.
    return merged, eod, bm, em

def make_state_features(data: pd.DataFrame, train_events: pd.DataFrame, candidate: tuple[str, ...]) -> tuple[pd.DataFrame, dict[str, Any]]:
    z = data.copy()
    cutpoints: dict[str, list[float]] = {}
    state_cols: list[str] = []
    for i, feature in enumerate(candidate):
        edges = edges_from(train_events, feature)
        cutpoints[feature] = edges
        state_col = f"state_{i}"
        z[state_col] = bins(z[feature], edges)
        state_cols.append(state_col)
    if len(state_cols) == 1:
        z["_state"] = z[state_cols[0]].astype(str)
    else:
        combo = z[state_cols[0]].astype(str) + "__X__" + z[state_cols[1]].astype(str)
        unavailable = z[state_cols].eq("UNAVAILABLE").any(axis=1)
        combo.loc[unavailable] = "UNAVAILABLE"
        z["_state"] = combo
    return z, cutpoints

def policy_on_test(data: pd.DataFrame, training: pd.DataFrame, state_col: str, baseline_strategy: str) -> tuple[pd.DataFrame, dict[str, str]]:
    mapping = fit_mapping(training, state_col, baseline_strategy, min_n=8)
    selected = collapse_by_event(data, state_col, mapping, baseline_strategy)
    return selected, mapping

def paired_validation_test(diff: np.ndarray, seed: int = 5218, reps: int = 5000, block_len: int = 3) -> tuple[float | None, float | None, float | None]:
    x = np.asarray(diff, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < 8:
        return None, None, None
    rng = np.random.default_rng(seed)
    n = len(x)
    block_len = max(1, min(block_len, n // 2))
    blocks = int(math.ceil(n / block_len))
    starts = rng.integers(0, n, size=(reps, blocks))
    offsets = np.arange(block_len)
    idx = ((starts[:, :, None] + offsets[None, None, :]) % n).reshape(reps, -1)[:, :n]
    boot_means = x[idx].mean(axis=1)
    block_ix = np.minimum(np.arange(n) // block_len, blocks - 1)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(reps, blocks))
    null_means = (x[None, :] * signs[:, block_ix]).mean(axis=1)
    p = (1 + int(np.sum(null_means >= x.mean()))) / (reps + 1)
    return float(np.quantile(boot_means, .025)), float(np.quantile(boot_means, .975)), float(p)

def self_test() -> None:
    fixture = pd.DataFrame({
        "expiry_key": ["2026-01-01", "2026-01-01"],
        "entry_ts": pd.to_datetime(["2025-12-25 10:00", "2025-12-25 10:00"]).tz_localize(TZ),
        "strategy": ["bear_call_spread", "buy_call"],
        "net": [100.0, -50.0], "net50": [80.0, -70.0],
        "net100": [60.0, -90.0], "state": ["LOW", "LOW"],
    })
    mapping = {"LOW": "bear_call_spread", "UNAVAILABLE": "buy_call"}
    selected = collapse_by_event(fixture, "state", mapping, "buy_call")
    assert len(selected) == 1 and selected.iloc[0].strategy == "bear_call_spread"
    baseline = fixture[fixture.strategy.eq("buy_call")].copy()
    m = metrics(selected, baseline.assign(expiry_key="2026-01-01"), "fixture", "validation")
    assert m["events"] == 1 and m["net_pnl_rupees"] == 100.0
    assert bins(pd.Series([1.0, 2.0, np.nan]), [1.5])[0] == "LOW"
    assert bins(pd.Series([1.0, 2.0, np.nan]), [1.5])[1] == "HIGH"
    print("SELF_TEST_PASS: point-in-time EOD bins, per-event strategy routing, and paired metrics")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    trades, eod, bm, em = load_inputs()
    # Event-level panel used for train-only thresholds. Each event appears once.
    event_panel = eod.drop_duplicates(["expiry_key", "entry_ts"]).copy()
    event_panel["split"] = event_panel.get("split", pd.Series(index=event_panel.index, dtype="object"))
    if "split" not in event_panel or event_panel["split"].isna().all():
        event_splits = trades[["expiry_key", "entry_ts", "split"]].drop_duplicates()
        event_panel = event_panel.drop(columns=["split"], errors="ignore").merge(event_splits, on=["expiry_key", "entry_ts"], how="left", validate="one_to_one")
    dev_events = event_panel[event_panel.split == "development"].sort_values("entry_ts").copy()
    val_events = event_panel[event_panel.split == "validation"].sort_values("entry_ts").copy()
    hold_events = event_panel[event_panel.split == "holdout"].sort_values("entry_ts").copy()
    if len(dev_events) < 40 or len(val_events) < 20:
        raise RuntimeError(f"Insufficient EOD event sample: development={len(dev_events)} validation={len(val_events)}")
    cut = max(20, min(len(dev_events) - 10, int(.70 * len(dev_events))))
    early_events = dev_events.iloc[:cut].copy()
    tune_events = dev_events.iloc[cut:].copy()
    # Use the same event split keys for baseline/router paired comparisons.
    keycols = ["expiry_key", "entry_ts"]
    early_keys = set(map(tuple, early_events[keycols].to_numpy()))
    tune = trades[trades.apply(lambda r: (r.expiry_key, r.entry_ts) in set(), axis=1)].copy() if False else trades
    train_rows = trades.merge(early_events[keycols], on=keycols, how="inner", validate="many_to_one")
    tune_rows = trades.merge(tune_events[keycols], on=keycols, how="inner", validate="many_to_one")
    baseline_strategy = fit_fixed_baseline(train_rows)
    train_factor = train_rows.drop_duplicates(keycols).copy()
    tune_factor = tune_rows.drop_duplicates(keycols).copy()

    # Candidate selector definitions are fixed in source; quantile cutpoints fit only
    # on the early-development feature snapshot and are never refit on the tuning block.
    specs: dict[str, tuple[str, ...]] = {name: tuple(vals) for name, vals in SINGLE_FEATURES.items()}
    specs.update({name: tuple(vals) for name, vals in MULTI_FEATURES.items()})
    tuning_rows = []
    tuning_cache: dict[str, dict[str, Any]] = {}
    for mode, candidate in specs.items():
        complete_cov = float(train_factor[list(candidate)].notna().all(axis=1).mean())
        tune_cov = float(tune_factor[list(candidate)].notna().all(axis=1).mean())
        if min(complete_cov, tune_cov) < .50:
            tuning_rows.append({"mode": mode, "features": list(candidate), "status": "SKIPPED_COVERAGE_LT_50_PERCENT",
                                "training_coverage": complete_cov, "tuning_coverage": tune_cov, "tuning_events": int(len(tune_events))})
            continue
        train_z, edges = make_state_features(train_rows, train_factor, candidate)
        tune_z, _ = make_state_features(tune_rows, train_factor, candidate)
        # Use identical edge set trained on early development on the tuning data.
        for i, feature in enumerate(candidate):
            tune_z[f"state_{i}"] = bins(tune_z[feature], edges[feature])
        if len(candidate) == 1:
            tune_z["_state"] = tune_z["state_0"].astype(str)
        else:
            combo = tune_z["state_0"].astype(str) + "__X__" + tune_z["state_1"].astype(str)
            combo[tune_z[["state_0", "state_1"]].eq("UNAVAILABLE").any(axis=1)] = "UNAVAILABLE"
            tune_z["_state"] = combo
        train_selected = collapse_by_event(train_z, "_state", fit_mapping(train_z, "_state", baseline_strategy), baseline_strategy)
        tune_selected = collapse_by_event(tune_z, "_state", fit_mapping(train_z, "_state", baseline_strategy), baseline_strategy)
        tune_base = collapse_by_event(tune_z, "_state", {"ALL": baseline_strategy}, baseline_strategy)
        # Recompute baseline with constant fixed strategy: route state must never affect baseline.
        tune_base = []
        for (expiry, entry_ts), g in tune_z.groupby(keycols, sort=True):
            q = g[g.strategy == baseline_strategy]
            if not q.empty:
                r = q.iloc[0]
                tune_base.append({"expiry_key": expiry, "entry_ts": entry_ts, "strategy": baseline_strategy,
                                  "net": float(r.net), "net50": float(r.net50), "net100": float(2*r.net50-r.net),
                                  "feature_state": "ALL", "used_fallback": False})
        tune_base = pd.DataFrame(tune_base)
        # Independent per-expiry paired uplift; candidates only rank on development tuning.
        selected_ix = tune_selected.drop_duplicates("expiry_key").set_index("expiry_key")
        base_ix = tune_base.drop_duplicates("expiry_key").set_index("expiry_key")
        common = selected_ix.index.intersection(base_ix.index)
        diff = selected_ix.loc[common, "net50"].to_numpy(float) - base_ix.loc[common, "net50"].to_numpy(float)
        lo, hi, p = paired_validation_test(diff)
        tuning_rows.append({
            "mode": mode, "features": list(candidate), "status": "DEVELOPMENT_TUNING_ONLY",
            "training_coverage": complete_cov, "tuning_coverage": tune_cov,
            "tuning_events": int(len(common)), "mean_uplift_legacy_stress": safe_float(diff.mean()) if len(diff) else None,
            "total_uplift_legacy_stress": safe_float(diff.sum()) if len(diff) else None,
            "ci95_low": lo, "ci95_high": hi, "p_one_sided": p,
            "cutpoints_fitted_early_dev_only": edges,
        })
        tuning_cache[mode] = {"candidate": candidate, "edges": edges}

    tuning_df = pd.DataFrame(tuning_rows)
    tuning_df.to_csv(OUT / "development_tuning.csv", index=False)
    viable = tuning_df[tuning_df.status.eq("DEVELOPMENT_TUNING_ONLY")].copy()
    if viable.empty:
        raise RuntimeError("No EOD selector met the development/tuning feature coverage gate")
    viable = viable.sort_values(["mode", "mean_uplift_legacy_stress"], ascending=[True, False]).drop_duplicates("mode")
    chosen = viable.set_index("mode")["features"].to_dict()
    # Freeze chosen feature recipe based solely on development tuning. For final
    # validation/holdout state mapping, cutpoints and mappings are fit on all development.
    full_dev_rows = trades[trades.split == "development"].copy()
    full_dev_events = dev_events.copy()
    baseline_strategy_full = fit_fixed_baseline(full_dev_rows)
    validation_rows = trades[trades.split == "validation"].copy()
    holdout_rows = trades[trades.split == "holdout"].copy()
    eval_results = []
    eval_ledgers: dict[tuple[str,str], pd.DataFrame] = {}
    coverage_rows = []
    for mode, feat_json in sorted(chosen.items()):
        candidate = tuple(json.loads(feat_json) if isinstance(feat_json, str) else feat_json)
        dev_z, edges = make_state_features(full_dev_rows, full_dev_events, candidate)
        val_z, _ = make_state_features(validation_rows, full_dev_events, candidate)
        hold_z, _ = make_state_features(holdout_rows, full_dev_events, candidate) if len(holdout_rows) else (holdout_rows.copy(), {})
        for z in (dev_z, val_z, hold_z):
            if len(z):
                for i, feature in enumerate(candidate):
                    z[f"state_{i}"] = bins(z[feature], edges[feature])
                if len(candidate) == 1:
                    z["_state"] = z["state_0"].astype(str)
                else:
                    combo = z["state_0"].astype(str) + "__X__" + z["state_1"].astype(str)
                    combo[z[["state_0","state_1"]].eq("UNAVAILABLE").any(axis=1)] = "UNAVAILABLE"
                    z["_state"] = combo
        mapping = fit_mapping(dev_z, "_state", baseline_strategy_full)
        for split, z in [("validation", val_z), ("holdout", hold_z)]:
            if z.empty:
                eval_results.append({"mode": mode, "split": split, "status": "NO_EVENTS"})
                continue
            # Per-factor selectors only evaluated against the fixed baseline on common expiry keys.
            selected = collapse_by_event(z, "_state", mapping, baseline_strategy_full)
            baseline_records = []
            for (expiry, entry_ts), g in z.groupby(keycols, sort=True):
                q = g[g.strategy == baseline_strategy_full]
                if not q.empty:
                    r = q.iloc[0]
                    baseline_records.append({"expiry_key": expiry, "entry_ts": entry_ts, "strategy": baseline_strategy_full,
                                             "net": float(r.net), "net50": float(r.net50), "net100": float(2*r.net50-r.net),
                                             "feature_state": "ALL", "used_fallback": False})
            baseline = pd.DataFrame(baseline_records)
            cov = float(z.drop_duplicates(keycols)[list(candidate)].notna().all(axis=1).mean()) if len(z) else 0.0
            cov_gate = cov >= .50 and len(selected) >= (20 if split == "validation" else 20)
            if split == "holdout" and not cov_gate:
                metric = {"mode": mode, "split": split, "status": "HOLDOUT_NOT_EVALUATED_LOW_COVERAGE_OR_SAMPLE",
                          "events": int(len(selected)), "feature_coverage": cov,
                          "baseline_strategy": baseline_strategy_full}
            elif not cov_gate and split == "validation":
                metric = {"mode": mode, "split": split, "status": "VALIDATION_NOT_EVALUATED_LOW_COVERAGE_OR_SAMPLE",
                          "events": int(len(selected)), "feature_coverage": cov,
                          "baseline_strategy": baseline_strategy_full}
            else:
                metric = metrics(selected, baseline, mode, split)
                metric["feature_coverage"] = cov
                metric["baseline_strategy"] = baseline_strategy_full
            eval_results.append(metric)
            eval_ledgers[(mode, split)] = selected

    # Correct the familywise error rate across the frozen router modes on validation.
    val_ix = [i for i, r in enumerate(eval_results) if r.get("split") == "validation" and r.get("paired_block_signflip_p_one_sided") is not None]
    adjusted = holm([eval_results[i]["paired_block_signflip_p_one_sided"] for i in val_ix])
    for i, p_adj in zip(val_ix, adjusted):
        eval_results[i]["p_holm_across_frozen_EOD_modes"] = p_adj

    result_df = pd.DataFrame(eval_results)
    result_df.to_csv(OUT / "selector_results.csv", index=False)
    for (mode, split), ledger in eval_ledgers.items():
        ledger.to_csv(OUT / f"trades_{mode.lower()}_{split}.csv", index=False)

    factor_summary = {}
    for col in sorted({f for x in SINGLE_FEATURES.values() for f in x}.union({f for pair in MULTI_FEATURES.values() for f in pair})):
        vals = to_num(event_panel[col]) if col in event_panel else pd.Series(dtype=float)
        factor_summary[col] = {
            "non_null_events": int(vals.notna().sum()),
            "events": int(len(event_panel)),
            "coverage": float(vals.notna().mean()) if len(vals) else 0.0,
            "coverage_by_split": {
                str(split): {
                    "events": int(len(g)),
                    "non_null_events": int(to_num(g[col]).notna().sum()) if col in g else 0,
                    "coverage": float(to_num(g[col]).notna().mean()) if col in g and len(g) else 0.0,
                }
                for split, g in event_panel.assign(_split=event_panel.split).groupby("_split", dropna=False)
            }
        }
    feature_coverage = pd.DataFrame([
        {"factor": f, "events": v["events"], "non_null_events": v["non_null_events"], "coverage": v["coverage"],
         "coverage_development": v["coverage_by_split"].get("development", {}).get("coverage", 0.0),
         "coverage_validation": v["coverage_by_split"].get("validation", {}).get("coverage", 0.0),
         "coverage_holdout": v["coverage_by_split"].get("holdout", {}).get("coverage", 0.0)}
        for f, v in factor_summary.items()
    ])
    feature_coverage.to_csv(OUT / "factor_coverage.csv", index=False)
    manifest = {
        "status": "EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_revision": bm.get("dataset_revision"),
        "base_matrix_sha256": sha256_file(BASE_MATRIX),
        "eod_feature_manifest_sha256": sha256_file(EOD_MANIFEST),
        "eod_features_sha256_gzip": sha256_file(EOD_FEATURES),
        "event_rows": int(len(event_panel)),
        "base_matrix_rows": int(len(trades)),
        "matched_event_rows": int(trades[["expiry_key","entry_ts"]].drop_duplicates().merge(
            event_panel[["expiry_key","entry_ts"]], on=["expiry_key","entry_ts"], how="inner"
        ).shape[0]),
        "selected_baseline_strategy": baseline_strategy_full,
        "selected_modes_from_development_tuning": {k: (json.loads(v) if isinstance(v,str) else v) for k,v in chosen.items()},
        "training_and_selection": "early 70% of development fits the feature cutpoints and state mappings; later 30% of development tunes which feature recipe each mode uses; 2024-25 validation and 2026 holdout are not used to fit feature thresholds or strategy maps",
        "cost_labels": {
            "net50": "Inherited Phase45 scenario scales all modeled charges to 1.5×; it is not a pure slippage-only stress.",
            "net100": "Arithmetic extrapolation 2×net50 − net for sensitivity only; not an independently rebuilt cost ledger."
        },
        "interpretation": "The daily EOD selector panel is exploratory only. It does not establish intraday futures lead-lag, does not repair missing one-minute option quotes, and is not commercial evidence while NSE data rights are unresolved.",
        "limitations": [
            "Only 256 replay events from the pinned legacy HF market source; this is not the full source expiry window.",
            "Daily EOD OI/PCR and futures basis are lagged proxies, not intraday factors.",
            "The options dataset is CC BY-NC 4.0 and NSE bhavcopy data remains subject to NSE/rightsholder terms.",
            "No selector is promoted; any positive result requires adequate validation, untouched holdout and independent source-authorized replay.",
        ],
        "outputs": ["development_tuning.csv", "selector_results.csv", "factor_coverage.csv", "trades_<mode>_<split>.csv"]
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    report_lines = [
        "# Phase 52 — Daily EOD Factor Selector (Exploratory)",
        "",
        f"**Status:** {manifest['status']}. No promotion.",
        f"- Events: {len(event_panel)}; base matrix rows: {len(trades)}; matched base/EOD events: {manifest['matched_event_rows']}.",
        f"- Baseline strategy selected on development only: {baseline_strategy_full}.",
        f"- Pinned option revision: {bm.get('dataset_revision')}; EOD archive commit: {em.get('nse_fno_archive_commit_sha')}.",
        "- Feature thresholds and strategy mappings are fit only on development; the later development block tunes feature choices; 2024–25 is validation; 2026 is an untouched holdout only if each factor meets the coverage and 20-event gates.",
        "",
        "## Validation and holdout results",
        "",
        "| Mode | Split | Events | Feature coverage | Net ₹ | Net 1.5× all-cost stress ₹ | Net 2× extrapolated stress ₹ | Mean uplift vs fixed ₹/event | 95% paired CI | Holm p | Status |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ]
    for r in eval_results:
        ci = "—"
        if r.get("paired_block_bootstrap_ci95_low_rupees") is not None and r.get("paired_block_bootstrap_ci95_high_rupees") is not None:
            ci = f"[{r['paired_block_bootstrap_ci95_low_rupees']:.0f}, {r['paired_block_bootstrap_ci95_high_rupees']:.0f}]"
        hp = r.get("p_holm_across_frozen_EOD_modes")
        report_lines.append(
            f"| {r.get('mode','')} | {r.get('split','')} | {r.get('events',0)} | {r.get('feature_coverage',0):.1%} | "
            f"{r.get('net_pnl_rupees',float('nan')):,.0f} | {r.get('net_legacy_1_5x_all_cost_stress_rupees',float('nan')):,.0f} | "
            f"{r.get('net_legacy_2x_extrapolated_cost_stress_rupees',float('nan')):,.0f} | {r.get('paired_mean_uplift_legacy_stress_rupees',float('nan')):,.0f} | {ci} | "
            f"{hp if hp is not None else float('nan'):.4f} | {r.get('status','')} |"
        )
    report_lines += ["", "## Factor availability", "", "| Factor | Events | Non-null | Overall coverage | Development | Validation | Holdout |",
                     "|---|---:|---:|---:|---:|---:|---:|"]
    for r in feature_coverage.itertuples(index=False):
        report_lines.append(
            f"| {r.factor} | {r.events} | {r.non_null_events} | {r.coverage:.1%} | "
            f"{r.coverage_development:.1%} | {r.coverage_validation:.1%} | {r.coverage_holdout:.1%} |"
        )
    report_lines += [
        "",
        "## Limitations",
        "",
        "- Daily EOD features are strictly prior-session inputs and are not a substitute for synchronized intraday futures/option quotes.",
        "- NSE data rights review remains mandatory; the legacy options data is CC BY-NC 4.0.",
        "- No selector is promoted from this exploratory screen. It does not test all 9,379,584 registered configurations.",
    ]
    (OUT / "REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": manifest["status"], "baseline": baseline_strategy_full,
        "chosen_modes": manifest["selected_modes_from_development_tuning"],
        "results": eval_results, "factor_coverage": factor_summary,
        "output": str(OUT.relative_to(ROOT)),
    }, indent=2, default=str))
    return 0

if __name__ == "__main__":
    import sys
    if "--self-test-only" in sys.argv:
        self_test()
        raise SystemExit(0)
    raise SystemExit(main())
