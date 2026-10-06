import json
import os
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

HF_REPO = "thetrademarkk/india-index-options-1m"
TZ = "Asia/Kolkata"
START = pd.Timestamp("2021-05-27", tz=TZ)
END = pd.Timestamp("2026-09-30", tz=TZ)
DEV_END = pd.Timestamp("2023-12-31", tz=TZ)
VAL_END = pd.Timestamp("2025-12-31", tz=TZ)
TICK = 0.05
SLIPPAGE_TICKS = 1.0
BROKERAGE_PER_ORDER = 10.0
OUT = Path("results/phase43_vix")
OUT.mkdir(parents=True, exist_ok=True)

STRATEGIES = {
    "long_straddle": [("cur", "CE", 0, 1), ("cur", "PE", 0, 1)],
    "short_straddle": [("cur", "CE", 0, -1), ("cur", "PE", 0, -1)],
    "long_strangle": [("cur", "CE", 1, 1), ("cur", "PE", -1, 1)],
    "short_strangle": [("cur", "CE", 1, -1), ("cur", "PE", -1, -1)],
    "bull_call_debit": [("cur", "CE", 0, 1), ("cur", "CE", 1, -1)],
    "bear_put_debit": [("cur", "PE", 0, 1), ("cur", "PE", -1, -1)],
    "bull_put_credit": [("cur", "PE", -1, -1), ("cur", "PE", -3, 1)],
    "bear_call_credit": [("cur", "CE", 1, -1), ("cur", "CE", 3, 1)],
    "long_call_butterfly": [("cur", "CE", -1, 1), ("cur", "CE", 0, -2), ("cur", "CE", 1, 1)],
    "long_put_butterfly": [("cur", "PE", 1, 1), ("cur", "PE", 0, -2), ("cur", "PE", -1, 1)],
    "iron_butterfly": [("cur", "CE", 0, -1), ("cur", "PE", 0, -1), ("cur", "CE", 2, 1), ("cur", "PE", -2, 1)],
    "iron_condor": [("cur", "CE", 1, -1), ("cur", "CE", 3, 1), ("cur", "PE", -1, -1), ("cur", "PE", -3, 1)],
    "call_broken_wing": [("cur", "CE", -2, 1), ("cur", "CE", 0, -2), ("cur", "CE", 1, 1)],
    "put_broken_wing": [("cur", "PE", 2, 1), ("cur", "PE", 0, -2), ("cur", "PE", -1, 1)],
    "call_ratio_1x2": [("cur", "CE", 0, 1), ("cur", "CE", 1, -2)],
    "put_ratio_1x2": [("cur", "PE", 0, 1), ("cur", "PE", -1, -2)],
    "call_backspread": [("cur", "CE", 0, -1), ("cur", "CE", 1, 2)],
    "put_backspread": [("cur", "PE", 0, -1), ("cur", "PE", -1, 2)],
    "call_calendar": [("cur", "CE", 0, -1), ("next", "CE", 0, 1)],
    "put_calendar": [("cur", "PE", 0, -1), ("next", "PE", 0, 1)],
    "reverse_call_calendar": [("cur", "CE", 0, 1), ("next", "CE", 0, -1)],
    "reverse_put_calendar": [("cur", "PE", 0, 1), ("next", "PE", 0, -1)],
}
UNBOUNDED = {"short_straddle", "short_strangle", "call_ratio_1x2", "put_ratio_1x2"}
DEFINED_RISK = [x for x in STRATEGIES if x not in UNBOUNDED]


def lot_size_for_expiry(expiry):
    if expiry < pd.Timestamp("2021-07-29", tz=TZ):
        return 75
    if expiry < pd.Timestamp("2024-05-02", tz=TZ):
        return 50
    if expiry <= pd.Timestamp("2024-12-26", tz=TZ):
        return 25
    if expiry <= pd.Timestamp("2025-01-23", tz=TZ):
        return 75
    if expiry == pd.Timestamp("2025-01-30", tz=TZ):
        return 25
    if expiry < pd.Timestamp("2026-01-06", tz=TZ):
        return 75
    return 65


def fee_rates(d):
    if d >= pd.Timestamp("2026-04-01", tz=TZ):
        stt = 0.0015
    elif d >= pd.Timestamp("2024-10-01", tz=TZ):
        stt = 0.0010
    else:
        stt = 0.000625
    if d >= pd.Timestamp("2026-03-01", tz=TZ):
        txn, ipft = 0.000355299, 0.000000001
    elif d >= pd.Timestamp("2024-10-01", tz=TZ):
        txn, ipft = 0.0003503, 0.000005
    else:
        txn, ipft = 0.000495, 0.000005
    return stt, txn, 0.000001, ipft, 0.00003


def exec_px(px, action, stress=1.0):
    slip = SLIPPAGE_TICKS * TICK * stress
    return max(0.0, float(px) + slip) if action == "buy" else max(0.0, float(px) - slip)


def charges(orders, lot_size, cost_mult=1.0):
    brokerage = BROKERAGE_PER_ORDER * cost_mult * len(orders)
    exchange = sebi = ipft = stt = stamp = 0.0
    for d, side, px in orders:
        sr, tx, se, ip, sd = fee_rates(d)
        turnover = float(px) * lot_size
        exchange += tx * turnover * cost_mult
        sebi += se * turnover * cost_mult
        ipft += ip * turnover * cost_mult
        if side == "sell":
            stt += sr * turnover * cost_mult
        else:
            stamp += sd * turnover * cost_mult
    gst = 0.18 * (brokerage + exchange + sebi + ipft)
    return brokerage + exchange + sebi + ipft + stt + stamp + gst


def load_parquet(name):
    p = hf_hub_download(repo_id=HF_REPO, filename=name, repo_type="dataset", token=os.getenv("HF_TOKEN") or None)
    df = pd.read_parquet(p)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    if df["timestamp"].dt.tz is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize(TZ)
    else:
        df["timestamp"] = df["timestamp"].dt.tz_convert(TZ)
    return df


def list_expiry_files():
    api = HfApi()
    dates = []
    for f in api.list_repo_files(HF_REPO, repo_type="dataset"):
        m = re.fullmatch(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet", f)
        if m:
            d = pd.Timestamp(m.group(1), tz=TZ)
            if START <= d <= END:
                dates.append(d)
    return sorted(set(dates))


def load_vix():
    p = Path("data/phase40_vix/india_vix.csv")
    if not p.exists():
        raise FileNotFoundError("Missing cached VIX: data/phase40_vix/india_vix.csv")
    df = pd.read_csv(p)
    date_col = [c for c in df.columns if c.lower() == "date"][0]
    close_col = [c for c in df.columns if c.lower() == "close"][0]
    df["date"] = pd.to_datetime(df[date_col]).dt.tz_localize(TZ)
    df["vix"] = pd.to_numeric(df[close_col], errors="coerce")
    df = df[["date", "vix"]].dropna().drop_duplicates("date").sort_values("date").reset_index(drop=True)
    df["dvix"] = df["vix"].diff()
    return df


def vix_state(vix, entry_ts):
    prior = vix[vix["date"] < entry_ts.normalize()]
    if len(prior) < 60:
        return None
    cur = prior.iloc[-1]
    hist = prior.iloc[:-1]
    q25 = hist["vix"].quantile(0.25)
    q75 = hist["vix"].quantile(0.75)
    d = hist["dvix"].dropna()
    pos = d[d > 0]
    q10 = d.quantile(0.10) if len(d) >= 20 else np.nan
    q90 = d.quantile(0.90) if len(d) >= 20 else np.nan
    q90pos = pos.quantile(0.90) if len(pos) >= 20 else np.nan
    level = "LOW" if cur["vix"] <= q25 else "HIGH" if cur["vix"] >= q75 else "NORMAL"
    dv = float(cur["dvix"]) if np.isfinite(cur["dvix"]) else np.nan
    return {
        "vix": float(cur["vix"]),
        "dvix": dv,
        "level_state": level,
        "SPIKE": bool(np.isfinite(dv) and np.isfinite(q90pos) and dv >= q90pos),
        "RISING": bool(np.isfinite(dv) and np.isfinite(q90) and dv >= q90),
        "FALLING": bool(np.isfinite(dv) and np.isfinite(q10) and dv <= q10),
    }


def active_states(v):
    out = ["ALL", v["level_state"]]
    if v["SPIKE"]:
        out.append("SPIKE")
    if v["RISING"]:
        out.append("RISING")
    if v["FALLING"]:
        out.append("FALLING")
    if v["level_state"] == "HIGH" and v["RISING"]:
        out.append("HIGH_RISING")
    return sorted(set(out))


def prepare_chain(df):
    df = df.copy()
    df["option_type"] = df["option_type"].astype(str).str.upper()
    df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    return df.dropna(subset=["timestamp", "option_type", "strike", "close"]).sort_values(["timestamp", "option_type", "strike"], kind="stable")


def modal_step(snapshot):
    steps = []
    for typ in ["CE", "PE"]:
        s = np.sort(snapshot.loc[snapshot["option_type"] == typ, "strike"].unique())
        d = np.diff(s)
        d = np.round(d[d > 0], 8)
        if len(d):
            vals, counts = np.unique(d, return_counts=True)
            steps.append(float(vals[np.argmax(counts)]))
    return steps[0] if steps else None


def strike_for(atm, step, typ, offset):
    return float(atm + offset * step)


def expiry_common_timestamp(series, start, cutoff):
    idx = None
    for s in series:
        z = s.index[(s.index >= start) & (s.index <= cutoff)]
        idx = z if idx is None else idx.intersection(z)
        if len(idx) == 0:
            return None
    return idx.max() if len(idx) else None


def risk_proxy(strategy, legs, entry_prices, atm, step, lot):
    if strategy in UNBOUNDED:
        return np.nan
    if any(x[0] != "cur" for x in legs):
        return float(sum(abs(p * q) for p, (_, _, _, q) in zip(entry_prices, legs)) * lot)
    entry_cash = 0.0
    for p, (_, _, _, q) in zip(entry_prices, legs):
        entry_cash -= q * exec_px(p, "buy" if q > 0 else "sell")
    grid = np.linspace(max(1.0, atm - 60 * step), atm + 60 * step, 601)
    profits = []
    for spot in grid:
        value = 0.0
        for _, typ, off, q in legs:
            k = strike_for(atm, step, typ, off)
            intrinsic = max(spot - k, 0.0) if typ == "CE" else max(k - spot, 0.0)
            value += q * intrinsic
        profits.append((entry_cash + value) * lot)
    return float(max(0.0, -min(profits)))


def evaluate(strategy, legs, cur, nxt, entry_ts, expiry, atm, step, lot):
    frames = {"cur": cur, "next": nxt}
    entry = []
    series = []
    for exp_key, typ, off, q in legs:
        df = frames.get(exp_key)
        if df is None:
            return None
        k = strike_for(atm, step, typ, off)
        x = df[(df["timestamp"] == entry_ts) & (df["option_type"] == typ) & (df["strike"] == k)]
        if x.empty:
            return None
        entry.append(float(x.iloc[-1]["close"]))
        day_start = expiry.normalize()
        cutoff = expiry.normalize() + pd.Timedelta(hours=15, minutes=29)
        s = df[(df["option_type"] == typ) & (df["strike"] == k) & (df["timestamp"] >= day_start) & (df["timestamp"] <= cutoff)]
        if s.empty:
            return None
        series.append(s.drop_duplicates("timestamp").set_index("timestamp")["close"])
    exit_ts = expiry_common_timestamp(series, expiry.normalize(), expiry.normalize() + pd.Timedelta(hours=15, minutes=29))
    if exit_ts is None:
        return None
    exits = [float(s.loc[exit_ts]) for s in series]
    gross = 0.0
    orders = []
    for leg, ep, xp in zip(legs, entry, exits):
        q = leg[3]
        ep_exec = exec_px(ep, "buy" if q > 0 else "sell")
        xp_exec = exec_px(xp, "buy" if q < 0 else "sell")
        gross += q * (xp_exec - ep_exec) * lot
        orders.append((entry_ts, "buy" if q > 0 else "sell", ep_exec * abs(q)))
        orders.append((exit_ts, "buy" if q < 0 else "sell", xp_exec * abs(q)))
    cost = charges(orders, lot, 1.0)
    cost50 = charges(orders, lot, 1.5)
    return {
        "gross_rupees": gross,
        "cost_rupees": cost,
        "net_rupees": gross - cost,
        "net_plus50_cost_rupees": gross - cost50,
        "risk_proxy_rupees": risk_proxy(strategy, legs, entry, atm, step, lot),
        "exit_ts": str(exit_ts),
    }


def load_index():
    x = load_parquet("index/NIFTY.parquet")
    return x[["timestamp", "close"]].rename(columns={"close": "spot"}).drop_duplicates("timestamp").sort_values("timestamp")


def make_opportunities(index, expiries):
    trading_days = sorted(index["timestamp"].dt.normalize().unique())
    rows = []
    for expiry in expiries:
        prior = [d for d in trading_days if d < expiry.normalize()]
        if len(prior) < 4:
            continue
        entry_day = prior[-4]
        entry_ts = entry_day + pd.Timedelta(hours=10)
        z = index[index["timestamp"] == entry_ts]
        if not z.empty:
            rows.append({"expiry": expiry, "entry_ts": entry_ts, "entry_spot": float(z.iloc[-1]["spot"])})
    return pd.DataFrame(rows)


def drawdown(vals):
    if len(vals) == 0:
        return 0.0
    c = np.cumsum(vals)
    return float(np.max(np.maximum.accumulate(c) - c))
