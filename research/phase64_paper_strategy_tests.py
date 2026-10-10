#!/usr/bin/env python3
"""Phase 64: preregistered paper-derived CCI NIFTY option strategy test.

Only DEV (through 2023) and VAL (2024-2025) are evaluated. 2026 option
files are deliberately excluded from the file manifest before any downloads.
Raw data stays in the runner/HF cache; only derived compact results are output.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))
from phase43_vix_strategy_sweep import charges, exec_px, lot_size_for_expiry, TZ, TICK  # noqa: E402

REPO = "thetrademarkk/india-index-options-1m"
REVISION = "3eacf762d401efd9a08e804592fa7882b354c4a2"
START = pd.Timestamp("2021-05-27", tz=TZ)
DEV_END = pd.Timestamp("2023-12-31 23:59:59", tz=TZ)
VAL_END = pd.Timestamp("2025-12-31 23:59:59", tz=TZ)
OUT = ROOT / "results" / "phase64_paper_strategy_tests"
SEED = 640021
VARIANTS = ("CCI_BASE", "CCI_EMA_FILTER")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def normalize_time(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    if "timestamp" not in out.columns:
        raise ValueError("required timestamp column is missing")
    ts = pd.to_datetime(out["timestamp"], errors="coerce")
    if ts.isna().any():
        raise ValueError(f"timestamp_parse_errors={int(ts.isna().sum())}")
    if ts.dt.tz is None:
        ts = ts.dt.tz_localize(TZ)
    else:
        ts = ts.dt.tz_convert(TZ)
    out["timestamp"] = ts
    return out.sort_values("timestamp", kind="stable").reset_index(drop=True)

def load_pinned(api: HfApi, token: str | None, filename: str):
    path = Path(hf_hub_download(repo_id=REPO, filename=filename,
        repo_type="dataset", revision=REVISION, token=token))
    return pd.read_parquet(path), {"path": filename, "sha256": sha256_file(path), "bytes": path.stat().st_size}

def source_manifest(api: HfApi, token: str | None):
    files = api.list_repo_files(repo_id=REPO, repo_type="dataset", revision=REVISION, token=token)
    rx = re.compile(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet$")
    expiries = []
    for name in files:
        m = rx.fullmatch(name)
        if not m:
            continue
        d = pd.Timestamp(m.group(1), tz=TZ)
        # Absolutely no 2026 option file is downloaded or inspected.
        if START.normalize() <= d <= VAL_END.normalize():
            expiries.append((d, name))
    if not expiries:
        raise RuntimeError("pinned revision has no NIFTY option expiry files in frozen DEV/VAL range")
    monthly = {}
    for d, name in sorted(expiries):
        key = d.strftime("%Y-%m")
        # Within this dataset, the latest listed expiry of a calendar month is
        # used as a *monthly-expiry proxy*. Exact historical monthly designation
        # may differ; it is logged as a limitation.
        monthly[key] = (d, name)
    return monthly, sorted(expiries)

def normalize_index(raw: pd.DataFrame):
    df = normalize_time(raw)
    required = {"open", "high", "low", "close"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"index OHLC columns missing: {sorted(missing)}")
    for c in required:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    bad = df[list(required)].isna().any(axis=1)
    if bad.any():
        df = df.loc[~bad].copy()
    # Keep only observations strictly inside the registered research interval
    # BEFORE constructing any daily features; 2026 is never used as a feature.
    df = df.loc[(df.timestamp >= START) & (df.timestamp <= VAL_END)].copy()
    keycols = ["timestamp"]
    dup = df.duplicated(keycols, keep=False)
    if dup.any():
        checkcols = ["open", "high", "low", "close"]
        conflicting = df.loc[dup].groupby(keycols)[checkcols].nunique().max(axis=1).gt(1)
        if conflicting.any():
            raise ValueError(f"conflicting duplicate NIFTY index timestamps={int(conflicting.sum())}")
        df = df.drop_duplicates(keycols, keep="first")
    if df.empty:
        raise RuntimeError("NIFTY index has no rows inside frozen DEV/VAL window")
    return df.sort_values("timestamp").reset_index(drop=True)

def daily_features(index: pd.DataFrame):
    z = index.copy()
    z["date"] = z.timestamp.dt.normalize()
    daily = z.groupby("date", sort=True).agg(
        open=("open", "first"), high=("high", "max"), low=("low", "min"),
        close=("close", "last"), minute_rows=("close", "size")).sort_index()
    tp = (daily.high + daily.low + daily.close) / 3.0
    mean_tp = tp.rolling(20, min_periods=20).mean()
    mean_dev = tp.rolling(20, min_periods=20).apply(
        lambda a: float(np.mean(np.abs(a - np.mean(a)))), raw=True)
    # Canonical CCI definition. The supplied paper's equation appears
    # typographically incomplete, so the standard denominator is used.
    daily["cci20"] = (tp - mean_tp) / (0.015 * mean_dev.replace(0, np.nan))
    daily["ema50"] = daily.close.ewm(span=50, adjust=False, min_periods=50).mean()
    daily["ema200"] = daily.close.ewm(span=200, adjust=False, min_periods=200).mean()
    daily["cci_prev"] = daily.cci20.shift(1)
    daily["call_cross"] = (daily.cci_prev <= -100) & (daily.cci20 > -100)
    daily["put_cross"] = (daily.cci_prev >= 100) & (daily.cci20 < 100)
    daily["call_trend"] = (daily.close > daily.ema50) & (daily.ema50 > daily.ema200)
    daily["put_trend"] = (daily.close < daily.ema50) & (daily.ema50 < daily.ema200)
    return daily

def normalize_chain(raw: pd.DataFrame):
    df = normalize_time(raw)
    aliases = {"right": "option_type", "optiontype": "option_type",
               "strike_price": "strike", "strikeprice": "strike"}
    for old, new in aliases.items():
        if old in df.columns and new not in df.columns:
            df = df.rename(columns={old: new})
    needed = {"option_type", "strike", "close"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"option chain schema missing: {sorted(missing)}")
    side = df.option_type.astype(str).str.upper().str.strip()
    side = side.replace({"CALL": "CE", "C": "CE", "PUT": "PE", "P": "PE"})
    df["option_type"] = side
    df["strike"] = pd.to_numeric(df.strike, errors="coerce")
    df["close"] = pd.to_numeric(df.close, errors="coerce")
    df = df.loc[df.option_type.isin(["CE", "PE"]) & df.strike.notna() & df.close.notna()].copy()
    df = df.loc[(df.timestamp >= START) & (df.timestamp <= VAL_END)].copy()
    keys = ["timestamp", "option_type", "strike"]
    duplicate = df.duplicated(keys, keep=False)
    if duplicate.any():
        # Exact duplicate rows are harmless and can be removed; conflicting
        # contract-minute records are ambiguous and fail closed.
        sub = df.loc[duplicate]
        value_cols = [c for c in ["open", "high", "low", "close", "volume", "open_interest", "oi"] if c in df.columns]
        conflicts = sub.groupby(keys)[value_cols].nunique(dropna=False).gt(1).any(axis=1)
        if conflicts.any():
            raise ValueError(f"conflicting duplicate option contract-minute keys={int(conflicts.sum())}")
        df = df.drop_duplicates(keys, keep="first")
    if df.empty:
        raise RuntimeError("option chain file contains no valid rows inside DEV/VAL window")
    return df.sort_values(["option_type", "strike", "timestamp"]).reset_index(drop=True)

def build_chain_map(chain: pd.DataFrame):
    result = {}
    for (typ, strike), g in chain.groupby(["option_type", "strike"], sort=False):
        result[(str(typ), float(strike))] = g.sort_values("timestamp").set_index("timestamp", drop=False)
    return result

def split_of(ts):
    return "DEV" if ts <= DEV_END else "VAL"

def make_signals(daily: pd.DataFrame, ym: str, expiry: pd.Timestamp, variant: str):
    y, m = map(int, ym.split("-"))
    rows = daily.loc[(daily.index.year == y) & (daily.index.month == m)
                     & (daily.index.day >= 3) & (daily.index.day <= 15)]
    signals = []
    for d, row in rows.iterrows():
        d = pd.Timestamp(d)
        if not np.isfinite(row.cci20) or not np.isfinite(row.cci_prev):
            continue
        if bool(row.call_cross):
            if variant == "CCI_BASE" or bool(row.call_trend):
                signals.append({"side": "CE", "signal_date": d, "level": float(row.high),
                    "cci": float(row.cci20), "signal_close": float(row.close),
                    "ema50": float(row.ema50) if np.isfinite(row.ema50) else np.nan,
                    "ema200": float(row.ema200) if np.isfinite(row.ema200) else np.nan})
        if bool(row.put_cross):
            if variant == "CCI_BASE" or bool(row.put_trend):
                signals.append({"side": "PE", "signal_date": d, "level": float(row.low),
                    "cci": float(row.cci20), "signal_close": float(row.close),
                    "ema50": float(row.ema50) if np.isfinite(row.ema50) else np.nan,
                    "ema200": float(row.ema200) if np.isfinite(row.ema200) else np.nan})
    return signals

def first_breakouts(index: pd.DataFrame, signals, ym: str):
    if not signals:
        return [], "no_qualified_cci_signal"
    y, m = map(int, ym.split("-"))
    events = []
    for sig in signals:
        t = index.loc[(index.timestamp.dt.year == y) & (index.timestamp.dt.month == m)
            & (index.timestamp.dt.day <= 15) & (index.timestamp.dt.normalize() > sig["signal_date"]),
            ["timestamp", "close"]]
        if sig["side"] == "CE":
            hits = t.loc[t.close >= sig["level"]]
        else:
            hits = t.loc[t.close <= sig["level"]]
        if not hits.empty:
            hit = hits.iloc[0]
            events.append({**sig, "trigger_ts": hit.timestamp, "trigger_spot": float(hit.close)})
    if not events:
        return [], "signal_without_later_breakout"
    earliest = min(x["trigger_ts"] for x in events)
    simultaneous = [x for x in events if x["trigger_ts"] == earliest]
    if len({x["side"] for x in simultaneous}) > 1:
        return [], "ambiguous_call_put_same_minute"
    # If multiple same-side signals break together, choose the earliest signal day.
    chosen = sorted(simultaneous, key=lambda x: x["signal_date"])[0]
    return [chosen], "breakout_found"

def exact_bar(series_map, key, ts):
    series = series_map.get(key)
    if series is None or ts not in series.index:
        return None
    row = series.loc[ts]
    if isinstance(row, pd.DataFrame):
        return None
    v = float(row.close)
    return v if np.isfinite(v) and v > 0 else None

def evaluate_trade(index: pd.DataFrame, chain_map, expiry: pd.Timestamp, candidate: dict):
    side = candidate["side"]
    trigger_ts = candidate["trigger_ts"]
    entry_ts = trigger_ts + pd.Timedelta(minutes=1)
    if entry_ts.day > 15 or entry_ts not in set(index.timestamp.values):
        return None, "entry_next_minute_missing_or_outside_window"
    entry_spot = float(index.loc[index.timestamp == trigger_ts, "close"].iloc[0])
    avail = sorted(k[1] for k in chain_map if k[0] == side)
    if side == "CE":
        itm = [k for k in avail if k < entry_spot]
        strike = max(itm) if itm else None
    else:
        itm = [k for k in avail if k > entry_spot]
        strike = min(itm) if itm else None
    if strike is None:
        return None, "no_strictly_itm_strike"
    key = (side, float(strike))
    entry_raw = exact_bar(chain_map, key, entry_ts)
    if entry_raw is None:
        return None, "missing_exact_next_minute_entry_option_bar"
    # Exit on the last trading session strictly before expiry (the paper's
    # second-last contract day), using only observed NIFTY trading sessions.
    all_days = sorted(index.timestamp.dt.normalize().unique())
    prior_days = [d for d in all_days if pd.Timestamp(d).date() < expiry.date()]
    if not prior_days:
        return None, "no_penultimate_trading_session"
    terminal_day = pd.Timestamp(prior_days[-1])
    series = chain_map[key]
    after = series.loc[(series.timestamp > entry_ts) &
        (series.timestamp.dt.normalize() <= terminal_day.normalize()) &
        (series.timestamp.dt.time <= pd.Timestamp("15:29").time())]
    if after.empty:
        return None, "no_option_observations_after_entry"
    trigger_exit = None
    for ts, row in after.iterrows():
        px = float(row.close)
        if px >= 2.0 * entry_raw:
            trigger_exit = (ts, "TARGET_100PCT")
            break
        if px <= 0.5 * entry_raw:
            trigger_exit = (ts, "STOP_50PCT")
            break
    if trigger_exit:
        exit_signal_ts, exit_reason = trigger_exit
        exit_ts = exit_signal_ts + pd.Timedelta(minutes=1)
        exit_raw = exact_bar(chain_map, key, exit_ts)
        if exit_raw is None or exit_ts > terminal_day.normalize() + pd.Timedelta(hours=15, minutes=29):
            return None, "target_stop_trigger_without_exact_next_minute_exit"
    else:
        terminal = series.loc[(series.timestamp.dt.normalize() == terminal_day.normalize()) &
            (series.timestamp.dt.time >= pd.Timestamp("15:24").time()) &
            (series.timestamp.dt.time <= pd.Timestamp("15:29").time())]
        if terminal.empty:
            return None, "missing_reliable_penultimate_day_exit_bar"
        exit_ts = terminal.timestamp.iloc[-1]
        exit_raw = float(terminal.close.iloc[-1])
        exit_reason = "PENULTIMATE_SESSION_CLOSE"
    # Primary adverse one-tick execution and registered cost/cost-stress cases.
    buy_px = float(exec_px(entry_raw, "buy"))
    sell_px = float(exec_px(exit_raw, "sell"))
    lot = int(lot_size_for_expiry(expiry))
    gross = (sell_px - buy_px) * lot
    orders = [(entry_ts, "buy", buy_px), (exit_ts, "sell", sell_px)]
    fee10 = float(charges(orders, lot, 1.0))
    fee20 = fee10 + 10.0 * len(orders)
    fee10_stress = float(charges(orders, lot, 1.5))
    # Existing accepted helper applies 1.5x to brokerage as well; add the
    # extra 15/order to turn its ₹15 stressed brokerage into ₹30/order.
    fee20_stress = fee10_stress + 15.0 * len(orders)
    # Paper-comparability stress: adverse 10% entry/exit price impact.
    buy10 = entry_raw * 1.10
    sell10 = max(0.0, exit_raw * 0.90)
    paper_orders = [(entry_ts, "buy", buy10), (exit_ts, "sell", sell10)]
    paper_gross = (sell10 - buy10) * lot
    paper_net10 = paper_gross - float(charges(paper_orders, lot, 1.0))
    rec = {
        "variant": candidate["variant"], "split": split_of(entry_ts),
        "expiry": expiry.strftime("%Y-%m-%d"), "signal_date": candidate["signal_date"].strftime("%Y-%m-%d"),
        "signal_side": side, "trigger_ts": str(trigger_ts), "entry_ts": str(entry_ts),
        "exit_ts": str(exit_ts), "exit_reason": exit_reason, "strike": float(strike),
        "entry_spot": entry_spot, "cci_at_signal": candidate["cci"],
        "ema50_at_signal": candidate["ema50"], "ema200_at_signal": candidate["ema200"],
        "entry_option_close": entry_raw, "exit_option_close": exit_raw, "lot_size": lot,
        "gross_after_1tick_slippage": gross, "fees_10_per_order": fee10,
        "net_10_per_order": gross - fee10, "net_10_order_50pct_stress": gross - fee10_stress,
        "net_20_per_order": gross - fee20, "net_20_order_50pct_stress": gross - fee20_stress,
        "net_10_per_order_10pct_price_slippage": paper_net10,
        "holding_minutes": int((exit_ts - entry_ts).total_seconds() // 60),
        "number_orders": len(orders)
    }
    return rec, "completed"

def summarize(trades: pd.DataFrame, opportunities: pd.DataFrame, variant: str, split: str):
    t = trades.loc[(trades.variant == variant) & (trades.split == split)].sort_values("exit_ts")
    o = opportunities.loc[(opportunities.variant == variant) & (opportunities.split == split)]
    n = len(t)
    net = t.net_10_per_order.astype(float).to_numpy() if n else np.array([])
    wins = net[net > 0]
    losses = net[net < 0]
    cum = np.cumsum(net) if n else np.array([])
    peak = np.maximum.accumulate(np.r_[0.0, cum])[1:] if n else np.array([])
    dd = float(np.max(peak - cum)) if n else 0.0
    trigger_rows = int((o.status == "breakout_found").sum())
    completed = int((o.status == "completed").sum())
    coverage = completed / trigger_rows if trigger_rows else np.nan
    return {
        "variant": variant, "split": split, "monthly_expiries_with_files": int(o.expiry.nunique()),
        "qualified_signal_months": int(o.qualified_signals.gt(0).sum()) if "qualified_signals" in o else 0,
        "breakout_months": trigger_rows, "completed_trades": n,
        "entry_or_exit_coverage": coverage, "coverage_failures": int(max(0, trigger_rows-completed)),
        "win_rate": float((net > 0).mean()) if n else None,
        "gross_after_slippage_rupees": float(t.gross_after_1tick_slippage.sum()) if n else 0.0,
        "net_10_per_order_rupees": float(t.net_10_per_order.sum()) if n else 0.0,
        "net_10_order_50pct_stress_rupees": float(t.net_10_order_50pct_stress.sum()) if n else 0.0,
        "net_20_per_order_rupees": float(t.net_20_per_order.sum()) if n else 0.0,
        "net_20_order_50pct_stress_rupees": float(t.net_20_order_50pct_stress.sum()) if n else 0.0,
        "net_10_order_paper_10pct_slippage_rupees": float(t.net_10_per_order_10pct_price_slippage.sum()) if n else 0.0,
        "mean_net_per_trade": float(np.mean(net)) if n else None,
        "median_net_per_trade": float(np.median(net)) if n else None,
        "profit_factor": float(wins.sum()/abs(losses.sum())) if len(losses) and len(wins) else (None if not len(wins) else float("inf")),
        "max_cumulative_trade_pnl_drawdown_rupees": dd,
        "median_holding_minutes": float(t.holding_minutes.median()) if n else None,
        "validation_gate_n20": bool(split == "VAL" and n >= 20),
        "validation_gate_coverage95": bool(split == "VAL" and np.isfinite(coverage) and coverage >= 0.95)
    }

def holm_adjust(pvals):
    p = np.asarray(pvals, dtype=float)
    order = np.argsort(p)
    out = np.empty(len(p), dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, min(1.0, (len(p)-rank)*p[idx]))
        out[idx] = running
    return out

def moving_block_bootstrap(monthly: pd.Series, nboot=10000, block=3, seed=SEED):
    """CI for mean net per completed trade, preserving adjacent 3-month blocks."""
    arr = monthly.to_numpy(dtype=float)
    active = np.isfinite(arr)
    if int(active.sum()) < 20:
        return {"n_trades": int(active.sum()), "block_months": block, "ci_low": None, "ci_high": None, "p_two_sided": None,
                "status": "SKIPPED_LT20_TRADES"}
    rng = np.random.default_rng(seed)
    nmonth = len(arr)
    nblocks = int(np.ceil(nmonth / block))
    reps = []
    null_reps = []
    # Center each block's mean under the null; sign-flip entire block sums.
    block_sums, block_counts = [], []
    for st in range(0, nmonth, block):
        sl = arr[st:min(st+block,nmonth)]
        finite = np.isfinite(sl)
        block_sums.append(float(np.nansum(sl)))
        block_counts.append(int(finite.sum()))
    block_sums = np.asarray(block_sums)
    block_counts = np.asarray(block_counts)
    observed = float(np.nansum(arr) / active.sum())
    for _ in range(nboot):
        starts = rng.integers(0, nmonth, size=nblocks)
        ids = np.concatenate([(np.arange(s, s+block) % nmonth) for s in starts])[:nmonth]
        sample = arr[ids]
        finite = np.isfinite(sample)
        if finite.any():
            reps.append(float(np.nansum(sample) / finite.sum()))
        signs = rng.choice([-1.0, 1.0], size=len(block_sums))
        denom = int(block_counts.sum())
        null_reps.append(float(np.sum(signs * block_sums) / denom) if denom else 0.0)
    lo, hi = np.quantile(reps, [0.025, 0.975])
    p = float((1 + np.sum(np.abs(null_reps) >= abs(observed))) / (1 + len(null_reps)))
    return {"n_trades": int(active.sum()), "block_months": block,
            "ci_low": float(lo), "ci_high": float(hi), "mean_net_per_trade": observed,
            "p_two_sided": p, "status": "COMPUTED"}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    token = os.getenv("HF_TOKEN") or None
    api = HfApi()
    monthly, expiry_files = source_manifest(api, token)
    index_raw, index_meta = load_pinned(api, token, "index/NIFTY.parquet")
    index = normalize_index(index_raw)
    daily = daily_features(index)
    index_lookup = index.set_index("timestamp", drop=False)
    all_days = sorted(index.timestamp.dt.normalize().unique())
    source_records = [index_meta]
    trades, audit = [], []
    for ym, (expiry, filename) in sorted(monthly.items()):
        # Expiry file date determines split; only <= 2025-12-31 files are present.
        split = "DEV" if expiry <= DEV_END else "VAL"
        chain_raw, meta = load_pinned(api, token, filename)
        source_records.append(meta)
        chain = normalize_chain(chain_raw)
        chain_map = build_chain_map(chain)
        for variant in VARIANTS:
            signals = make_signals(daily, ym, expiry, variant)
            events, status = first_breakouts(index, signals, ym)
            audit_row = {"variant": variant, "split": split, "expiry": expiry.strftime("%Y-%m-%d"),
                "source_file": filename, "qualified_signals": len(signals), "status": status,
                "signal_dates": ";".join(sorted({x["signal_date"].strftime("%Y-%m-%d") for x in signals})),
                "trigger_ts": "", "failure_reason": ""}
            if events:
                ev = {**events[0], "variant": variant}
                audit_row["trigger_ts"] = str(ev["trigger_ts"])
                rec, result = evaluate_trade(index, chain_map, expiry, ev)
                audit_row["status"] = result
                if result == "completed":
                    trades.append(rec)
                else:
                    audit_row["failure_reason"] = result
            audit.append(audit_row)
        del chain_raw, chain, chain_map
    trade_df = pd.DataFrame(trades)
    audit_df = pd.DataFrame(audit)
    if trade_df.empty:
        trade_df = pd.DataFrame(columns=["variant","split","expiry","entry_ts","exit_ts","net_10_per_order"])
    trade_df.to_csv(OUT / "trade_ledger.csv", index=False)
    audit_df.to_csv(OUT / "opportunity_audit.csv", index=False)
    summaries = []
    for variant in VARIANTS:
        for split in ["DEV", "VAL"]:
            summaries.append(summarize(trade_df, audit_df, variant, split))
    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(OUT / "summary.csv", index=False)
    infer = {}
    pvals, names = [], []
    for variant in VARIANTS:
        val = trade_df.loc[(trade_df.variant == variant) & (trade_df.split == "VAL")].copy()
        # Calendar-month series includes no-trade months as NaN, not zero profit.
        periods = pd.period_range("2024-01", "2025-12", freq="M")
        ret = pd.Series(np.nan, index=periods, dtype=float)
        for _, row in val.iterrows():
            ret[pd.Period(pd.Timestamp(row.entry_ts).strftime("%Y-%m"), freq="M")] = float(row.net_10_per_order)
        result = moving_block_bootstrap(ret)
        infer[variant] = result
        if result["p_two_sided"] is not None:
            pvals.append(result["p_two_sided"])
            names.append(variant)
    if pvals:
        adjusted = holm_adjust(pvals)
        for nm, val in zip(names, adjusted):
            infer[nm]["p_holm_2_candidates"] = float(val)
    manifest = {"dataset": REPO, "revision": REVISION, "license_note": "CC-BY-NC-4.0; attributed source; raw files not included",
        "index_file": index_meta, "options_source_files": source_records[1:],
        "count_source_files": len(source_records), "monthly_expiry_proxy_count": len(monthly),
        "expiry_files_in_DEV_VAL_count": len(expiry_files), "features_max_timestamp_used": str(index.timestamp.max()),
        "explicit_2026_option_files_downloaded": 0,
        "splits": {"DEV": ["2021-05-27", "2023-12-31"], "VAL": ["2024-01-01", "2025-12-31"], "HOLD": "2026 excluded"},
        "candidate_universe": list(VARIANTS), "statistics": infer}
    (OUT / "source_manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
    decision = []
    for variant in VARIANTS:
        v = next(x for x in summaries if x["variant"] == variant and x["split"] == "VAL")
        inf = infer[variant]
        economic = all(v[k] is not None and float(v[k]) > 0 for k in [
            "net_10_per_order_rupees", "net_10_order_50pct_stress_rupees",
            "net_20_per_order_rupees", "net_20_order_50pct_stress_rupees"])
        statistical = inf.get("status") == "COMPUTED" and inf.get("ci_low", -1) > 0 and inf.get("p_holm_2_candidates", 1) < 0.05
        decision.append({"variant": variant, "completed_trades": v["completed_trades"],
            "coverage": v["entry_or_exit_coverage"], "min20_trades": v["completed_trades"] >= 20,
            "coverage95": bool(v["entry_or_exit_coverage"] is not None and np.isfinite(v["entry_or_exit_coverage"]) and v["entry_or_exit_coverage"] >= 0.95),
            "positive_all_registered_cost_cases": economic, "statistical_gate": bool(statistical),
            "promotion_eligible": False, "reason": "Phase 64 is research-only; >=20 trades/coverage/cost/statistical gates are necessary but not sufficient"})
    (OUT / "decision.json").write_text(json.dumps({"phase":64,"decision":"RESEARCH_ONLY_NO_PROMOTION",
        "candidate_decisions":decision,"source_data_license":"CC-BY-NC-4.0",
        "limitations":["monthly expiry uses last option-file expiry of each calendar month as a proxy",
        "OHLC close execution with one-tick adverse slippage is not bid/ask/depth quote fidelity",
        "2008-2018 source-paper interval is unavailable in the pinned dataset",
        "2026 option files were not downloaded and holdout is excluded",
        "only two fixed variants were registered"]}, indent=2))
    print(json.dumps({"status":"COMPLETED","revision":REVISION,"monthly_expiries":len(monthly),
        "source_files":len(source_records),"summary":summary_df.to_dict(orient="records"),
        "audit_status_counts":audit_df.status.value_counts().to_dict(),"decision":decision}, default=str))
if __name__ == "__main__":
    main()
