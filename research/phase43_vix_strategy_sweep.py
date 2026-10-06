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


def bootstrap(x, seed=4301):
    a = np.asarray(x, dtype=float)
    a = a[np.isfinite(a)]
    if len(a) < 5:
        return {"n": len(a), "mean": np.nan, "ci_lo": np.nan, "ci_hi": np.nan, "p": np.nan}
    rng = np.random.default_rng(seed)
    sample = a[rng.integers(0, len(a), size=(10000, len(a)))]
    means = sample.mean(axis=1)
    signs = rng.choice([-1.0, 1.0], size=(10000, len(a)))
    p = float(np.mean((a * signs).mean(axis=1) >= a.mean()))
    return {
        "n": int(len(a)),
        "mean": float(a.mean()),
        "ci_lo": float(np.quantile(means, 0.025)),
        "ci_hi": float(np.quantile(means, 0.975)),
        "p": p,
    }


def holm(p):
    p = np.asarray(p, float)
    order = np.argsort(np.nan_to_num(p, nan=1.0))
    out = np.empty(len(p), float)
    run = 0.0
    m = len(p)
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * (p[i] if np.isfinite(p[i]) else 1.0)))
        out[i] = run
    return out


def summarize_strategy(trades):
    rows = []
    for (strategy, split), z in trades.groupby(["strategy", "split"]):
        rows.append({
            "strategy": strategy,
            "split": split,
            "trades": len(z),
            "net_rupees": float(z["net_rupees"].sum()),
            "mean_net": float(z["net_rupees"].mean()),
            "win_rate": float((z["net_rupees"] > 0).mean()),
            "max_dd": drawdown(z.sort_values("expiry")["net_rupees"].to_numpy()),
            "cost_rupees": float(z["cost_rupees"].sum()),
        })
    return pd.DataFrame(rows)


def build_router(dev, criterion):
    regimes = ["LOW", "NORMAL", "HIGH", "SPIKE", "FALLING", "RISING", "HIGH_RISING"]
    mapping = {}
    eligible_all = dev[dev["strategy"].isin(DEFINED_RISK)]
    fallback = eligible_all.groupby("strategy")["net_rupees"].mean().sort_values(ascending=False).index[0]
    for mode in regimes:
        z = eligible_all[eligible_all["active_states"].apply(lambda a: mode in a)]
        counts = z.groupby("strategy").size()
        valid = counts[counts >= 15].index
        z = z[z["strategy"].isin(valid)]
        if z.empty:
            mapping[mode] = fallback
            continue
        if criterion == "mean":
            scores = z.groupby("strategy")["net_rupees"].mean()
        elif criterion == "median":
            scores = z.groupby("strategy")["net_rupees"].median()
        else:
            scores = z.groupby("strategy")["net_rupees"].agg(lambda x: x.mean() / x.std(ddof=1) if x.std(ddof=1) > 0 else -np.inf)
        mapping[mode] = scores.sort_values(ascending=False).index[0]
    return mapping


def pick_strategy(active, mapping):
    for mode in ["HIGH_RISING", "SPIKE", "RISING", "FALLING", "HIGH", "LOW", "NORMAL"]:
        if mode in active:
            return mapping.get(mode)
    return None


def make_figures(trades):
    expanded = trades.explode("active_states").rename(columns={"active_states": "vix_mode"})
    heat = expanded.pivot_table(
        index="strategy",
        columns="vix_mode",
        values="net_rupees",
        aggfunc="mean"
    )
    plt.figure(figsize=(13, 9))
    plt.imshow(heat.fillna(0).to_numpy(), aspect="auto")
    plt.yticks(range(len(heat.index)), heat.index)
    plt.xticks(range(len(heat.columns)), heat.columns, rotation=45, ha="right")
    plt.title("Phase 43 mean net P&L by strategy and India VIX state")
    plt.colorbar(label="Mean net P&L")
    plt.tight_layout()
    plt.savefig(OUT / "strategy_vix_heatmap.png", dpi=160)
    plt.close()


def main():
    expiry_files = list_expiry_files()
    index = load_index()
    opportunities = make_opportunities(index, expiry_files)
    vix = load_vix()
    cache = {}
    rows = []
    errors = []

    for i, op in opportunities.iterrows():
        expiry = pd.Timestamp(op["expiry"])
        entry_ts = pd.Timestamp(op["entry_ts"])
        entry_spot = float(op["entry_spot"])
        state = vix_state(vix, entry_ts)
        if state is None:
            errors.append({"expiry": str(expiry.date()), "stage": "vix", "reason": "insufficient_history"})
            continue
        try:
            if expiry not in cache:
                cache[expiry] = prepare_chain(load_parquet(f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet"))
            cur = cache[expiry]
            pos = expiry_files.index(expiry)
            nxt = None
            if pos + 1 < len(expiry_files):
                ne = expiry_files[pos + 1]
                if ne not in cache:
                    cache[ne] = prepare_chain(load_parquet(f"options/NIFTY/{ne.strftime('%Y-%m-%d')}.parquet"))
                nxt = cache.get(ne)
        except Exception as exc:
            errors.append({"expiry": str(expiry.date()), "stage": "load", "reason": repr(exc)})
            continue

        snap = cur[cur["timestamp"] == entry_ts]
        step = modal_step(snap)
        if step is None or step <= 0:
            errors.append({"expiry": str(expiry.date()), "stage": "strike_step", "reason": "missing"})
            continue
        strikes = snap["strike"].unique()
        atm = float(min(strikes, key=lambda k: abs(k - entry_spot)))
        lot = lot_size_for_expiry(expiry)
        split = "development" if expiry <= DEV_END else "validation" if expiry <= VAL_END else "holdout"
        active = active_states(state)

        for strategy, legs in STRATEGIES.items():
            r = evaluate(strategy, legs, cur, nxt, entry_ts, expiry, atm, step, lot)
            if r is None:
                continue
            rows.append({
                "expiry": str(expiry.date()),
                "entry_ts": str(entry_ts),
                "split": split,
                "strategy": strategy,
                "entry_spot": entry_spot,
                "lot_size": lot,
                "step": step,
                "vix": state["vix"],
                "dvix": state["dvix"],
                "active_states": active,
                **r,
                "return_on_risk": r["net_rupees"] / r["risk_proxy_rupees"] if np.isfinite(r["risk_proxy_rupees"]) and r["risk_proxy_rupees"] > 0 else np.nan,
            })
        if i % 10 == 0:
            pd.DataFrame(rows).to_csv(OUT / "progress_trade_matrix.csv", index=False)

    trades = pd.DataFrame(rows)
    if trades.empty:
        raise RuntimeError("No strategy observations were produced")
    trades.to_csv(OUT / "strategy_trade_matrix_all_splits.csv", index=False)
    pd.DataFrame(errors).to_csv(OUT / "data_errors.csv", index=False)
    summarize_strategy(trades).to_csv(OUT / "strategy_summary_by_split.csv", index=False)

    dev = trades[trades["split"] == "development"].copy()
    val = trades[trades["split"] == "validation"].copy()
    hold = trades[trades["split"] == "holdout"].copy()

    grid = []
    tests = []
    for strategy in STRATEGIES:
        for mode in ["ALL", "LOW", "NORMAL", "HIGH", "SPIKE", "FALLING", "RISING", "HIGH_RISING"]:
            zd = dev[dev["strategy"] == strategy]
            zv = val[val["strategy"] == strategy]
            if mode != "ALL":
                zd = zd[zd["active_states"].apply(lambda a: mode in a)]
                zv = zv[zv["active_states"].apply(lambda a: mode in a)]
            if len(zd) < 10:
                continue
            grid.append({
                "strategy": strategy,
                "vix_mode": mode,
                "development_trades": len(zd),
                "development_net": float(zd["net_rupees"].sum()),
                "validation_trades": len(zv),
                "validation_net": float(zv["net_rupees"].sum()),
                "validation_mean": float(zv["net_rupees"].mean()) if len(zv) else np.nan,
                "validation_dd": drawdown(zv.sort_values("expiry")["net_rupees"].to_numpy()) if len(zv) else np.nan,
                "validation_cost50_net": float(zv["net_plus50_cost_rupees"].sum()) if len(zv) else np.nan,
            })
            if mode != "ALL" and len(zv) >= 20:
                base = val[val["strategy"] == strategy][["expiry", "net_rupees"]].rename(columns={"net_rupees": "base"})
                cand = zv[["expiry", "net_rupees"]].rename(columns={"net_rupees": "cand"})
                common = base.merge(cand, on="expiry", how="inner")
                b = bootstrap(common["cand"] - common["base"])
                tests.append({
                    "strategy": strategy,
                    "vix_mode": mode,
                    **b,
                })

    grid_df = pd.DataFrame(grid)
    grid_df.to_csv(OUT / "strategy_vix_validation_grid.csv", index=False)
    inf_df = pd.DataFrame(tests)
    if len(inf_df):
        inf_df["p_holm"] = holm(inf_df["p"].to_numpy())
    inf_df.to_csv(OUT / "strategy_vix_inference.csv", index=False)

    eligible = grid_df[
        grid_df["vix_mode"].ne("ALL")
        & grid_df["development_net"].ge(0)
        & grid_df["validation_net"].gt(0)
        & grid_df["validation_trades"].ge(20)
        & grid_df["strategy"].isin(DEFINED_RISK)
    ].sort_values(["validation_net", "validation_mean"], ascending=False).head(10)
    eligible.to_csv(OUT / "frozen_top10_strategy_vix_candidates.csv", index=False)

    router_devval = []
    router_maps = {}
    for criterion in ["mean", "median", "sharpe"]:
        mapping = build_router(dev, criterion)
        router_maps[criterion] = mapping
        for split_name, frame in [("development", dev), ("validation", val)]:
            picked = []
            for _, z in frame.groupby(["expiry", "entry_ts"], sort=True):
                strategy = pick_strategy(z["active_states"].iloc[0], mapping)
                zz = z[z["strategy"] == strategy]
                if len(zz):
                    picked.append(zz.iloc[0])
            rt = pd.DataFrame(picked)
            router_devval.append({
                "router": criterion,
                "split": split_name,
                "trades": len(rt),
                "net_rupees": float(rt["net_rupees"].sum()) if len(rt) else np.nan,
                "mean_net": float(rt["net_rupees"].mean()) if len(rt) else np.nan,
                "max_dd": drawdown(rt.sort_values("expiry")["net_rupees"].to_numpy()) if len(rt) else np.nan,
                "cost50_net": float(rt["net_plus50_cost_rupees"].sum()) if len(rt) else np.nan,
            })

    rv = pd.DataFrame(router_devval)
    rv.to_csv(OUT / "router_dev_validation.csv", index=False)
    frozen = []
    for criterion in ["mean", "median", "sharpe"]:
        d = rv[(rv["router"] == criterion) & (rv["split"] == "development")].iloc[0]
        v = rv[(rv["router"] == criterion) & (rv["split"] == "validation")].iloc[0]
        if d["net_rupees"] >= 0 and v["net_rupees"] > 0 and v["trades"] >= 20 and v["cost50_net"] > 0:
            frozen.append((criterion, v["net_rupees"]))
    frozen = [x[0] for x in sorted(frozen, key=lambda x: x[1], reverse=True)[:3]]

    best_all = dev[dev["strategy"].isin(DEFINED_RISK)].groupby("strategy")["net_rupees"].mean().sort_values(ascending=False).index[0]
    hold_rows = []
    for criterion in frozen:
        mapping = router_maps[criterion]
        picked = []
        for _, z in hold.groupby(["expiry", "entry_ts"], sort=True):
            strategy = pick_strategy(z["active_states"].iloc[0], mapping)
            zz = z[z["strategy"] == strategy]
            if len(zz):
                picked.append(zz.iloc[0])
        rt = pd.DataFrame(picked)
        bench = hold[hold["strategy"] == best_all][["expiry", "net_rupees"]].rename(columns={"net_rupees": "base"})
        cand = rt[["expiry", "net_rupees"]].rename(columns={"net_rupees": "cand"}) if len(rt) else pd.DataFrame(columns=["expiry", "cand"])
        common = bench.merge(cand, on="expiry", how="left").fillna({"cand": 0.0})
        b = bootstrap(common["cand"] - common["base"])
        hold_rows.append({
            "router": criterion,
            "holdout_trades": len(rt),
            "holdout_net_rupees": float(rt["net_rupees"].sum()) if len(rt) else 0.0,
            "holdout_cost50_net": float(rt["net_plus50_cost_rupees"].sum()) if len(rt) else 0.0,
            "holdout_dd": drawdown(rt.sort_values("expiry")["net_rupees"].to_numpy()) if len(rt) else 0.0,
            "benchmark_strategy": best_all,
            "benchmark_holdout_net": float(hold[hold["strategy"] == best_all]["net_rupees"].sum()),
            "mean_uplift_vs_benchmark": b["mean"],
            "ci_lo": b["ci_lo"],
            "ci_hi": b["ci_hi"],
            "p_signflip": b["p"],
        })

    hold_df = pd.DataFrame(hold_rows)
    if len(hold_df):
        hold_df["p_holm"] = holm(hold_df["p_signflip"].to_numpy())
    hold_df.to_csv(OUT / "frozen_router_holdout.csv", index=False)

    hold_candidates = []
    for _, c in eligible.iterrows():
        z = hold[hold["strategy"] == c["strategy"]]
        if c["vix_mode"] != "ALL":
            z = z[z["active_states"].apply(lambda a: c["vix_mode"] in a)]
        base = hold[hold["strategy"] == c["strategy"]]
        hold_candidates.append({
            "strategy": c["strategy"],
            "vix_mode": c["vix_mode"],
            "holdout_trades": len(z),
            "holdout_net": float(z["net_rupees"].sum()) if len(z) else 0.0,
            "holdout_cost50_net": float(z["net_plus50_cost_rupees"].sum()) if len(z) else 0.0,
            "benchmark_all_net": float(base["net_rupees"].sum()),
            "holdout_dd": drawdown(z.sort_values("expiry")["net_rupees"].to_numpy()) if len(z) else 0.0,
        })
    hold_candidates_df = pd.DataFrame(hold_candidates)
    hold_candidates_df.to_csv(OUT / "frozen_top10_holdout.csv", index=False)

    make_figures(trades)

    stage5 = "REQUIRED" if len(frozen) else "SKIPPED_NO_ROUTER_PASSED"
    decision = "PENDING_STAGE5_ACTIVE_EXIT" if frozen else "NO_PROMOTION"

    summary = {
        "phase": 43,
        "status": "STRUCTURAL_COMPLETE_STAGE5_PENDING" if frozen else "COMPLETE_NO_ROUTER_PROMOTED",
        "strategies_declared": len(STRATEGIES),
        "defined_risk_strategies": len(DEFINED_RISK),
        "expiry_files": len(expiry_files),
        "opportunities": int(len(opportunities)),
        "trade_rows": int(len(trades)),
        "development_rows": int(len(dev)),
        "validation_rows": int(len(val)),
        "holdout_rows": int(len(hold)),
        "frozen_top10_count": int(len(eligible)),
        "frozen_router_count": int(len(frozen)),
        "best_defined_risk_development_benchmark": str(best_all),
        "data_errors": int(len(errors)),
        "stage5": stage5,
        "decision": decision,
    }

    (OUT / "frozen_router_maps.json").write_text(json.dumps({"benchmark": best_all, "maps": router_maps, "frozen": frozen}, indent=2))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
