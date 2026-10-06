import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path("results/phase43_vix")
TRADES = OUT / "strategy_trade_matrix_all_splits.csv"

MODES = ["ALL", "LOW", "NORMAL", "HIGH", "SPIKE", "FALLING", "RISING", "HIGH_RISING"]
UNBOUNDED = {"short_straddle", "short_strangle", "call_ratio_1x2", "put_ratio_1x2"}
CALENDAR = {"call_calendar", "put_calendar", "reverse_call_calendar", "reverse_put_calendar"}

def parse_states(x):
    if isinstance(x, list):
        return x
    try:
        return ast.literal_eval(str(x))
    except Exception:
        return []

def dd(z):
    if len(z) == 0:
        return 0.0
    x = np.asarray(z, float)
    c = np.cumsum(x)
    return float(np.max(np.maximum.accumulate(c) - c))

def bootstrap_diff(a, b, seed=43043, nboot=10000):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 10 or len(b) < 10:
        return {"n_a": len(a), "n_b": len(b), "mean_diff": np.nan, "ci_lo": np.nan, "ci_hi": np.nan, "p_perm": np.nan}
    rng = np.random.default_rng(seed)
    ia = rng.integers(0, len(a), size=(nboot, len(a)))
    ib = rng.integers(0, len(b), size=(nboot, len(b)))
    diffs = a[ia].mean(axis=1) - b[ib].mean(axis=1)
    pooled = np.concatenate([a, b])
    n_a = len(a)
    obs = float(a.mean() - b.mean())
    vals = np.empty(nboot, float)
    for i in range(nboot):
        perm = rng.permutation(pooled)
        vals[i] = perm[:n_a].mean() - perm[n_a:].mean()
    p = float(np.mean(np.abs(vals) >= abs(obs)))
    return {
        "n_a": int(len(a)),
        "n_b": int(len(b)),
        "mean_diff": obs,
        "ci_lo": float(np.quantile(diffs, 0.025)),
        "ci_hi": float(np.quantile(diffs, 0.975)),
        "p_perm": p,
    }

def holm(p):
    p = np.asarray(p, float)
    if len(p) == 0:
        return p
    order = np.argsort(np.nan_to_num(p, nan=1.0))
    out = np.ones(len(p), float)
    running = 0.0
    m = len(p)
    for rank, i in enumerate(order):
        val = (m - rank) * (p[i] if np.isfinite(p[i]) else 1.0)
        running = max(running, min(1.0, val))
        out[i] = running
    return out

def mode_rows(frame, mode):
    if mode == "ALL":
        return frame
    return frame[frame["active_states"].apply(lambda x: mode in x)]

def build_grid(dev, val):
    rows = []
    for strategy in sorted(val["strategy"].unique()):
        for mode in MODES:
            d = mode_rows(dev[dev["strategy"] == strategy], mode)
            v = mode_rows(val[val["strategy"] == strategy], mode)
            if len(d) < 10:
                continue
            rows.append({
                "strategy": strategy,
                "vix_mode": mode,
                "development_trades": len(d),
                "development_net": float(d["net_rupees"].sum()),
                "validation_trades": len(v),
                "validation_net": float(v["net_rupees"].sum()),
                "validation_mean": float(v["net_rupees"].mean()) if len(v) else np.nan,
                "validation_dd": dd(v.sort_values("expiry")["net_rupees"].to_numpy()) if len(v) else np.nan,
                "validation_cost50_net": float(v["net_plus50_cost_rupees"].sum()) if len(v) else np.nan,
            })
    return pd.DataFrame(rows)

def build_inference(val):
    rows = []
    for strategy in sorted(val["strategy"].unique()):
        s = val[val["strategy"] == strategy]
        for mode in MODES[1:]:
            treated = mode_rows(s, mode)
            control = s[~s["active_states"].apply(lambda x: mode in x)]
            if len(treated) < 20 or len(control) < 20:
                continue
            r = bootstrap_diff(treated["net_rupees"], control["net_rupees"], seed=43043 + len(rows))
            r.update({"strategy": strategy, "vix_mode": mode})
            rows.append(r)
    out = pd.DataFrame(rows)
    if len(out):
        out["p_holm"] = holm(out["p_perm"].to_numpy())
    return out

def router_map(dev, criterion, candidates):
    regimes = MODES[1:]
    mapping = {}
    for mode in regimes:
        z = mode_rows(dev[dev["strategy"].isin(candidates)], mode)
        counts = z.groupby("strategy").size()
        valid = counts[counts >= 15].index
        z = z[z["strategy"].isin(valid)]
        if z.empty:
            mapping[mode] = None
            continue
        if criterion == "mean":
            score = z.groupby("strategy")["net_rupees"].mean()
        elif criterion == "median":
            score = z.groupby("strategy")["net_rupees"].median()
        else:
            score = z.groupby("strategy")["net_rupees"].agg(lambda x: x.mean() / x.std(ddof=1) if x.std(ddof=1) > 0 else -np.inf)
        mapping[mode] = str(score.sort_values(ascending=False).index[0])
    return mapping

def route_strategy(active, mapping):
    for mode in ["HIGH_RISING", "SPIKE", "RISING", "FALLING", "HIGH", "LOW", "NORMAL"]:
        if mode in active and mapping.get(mode):
            return mapping[mode]
    return None

def route_eval(frame, mapping):
    picks = []
    for _, z in frame.groupby(["expiry", "entry_ts"], sort=True):
        st = route_strategy(z["active_states"].iloc[0], mapping)
        zz = z[z["strategy"] == st]
        if len(zz):
            picks.append(zz.iloc[0])
    return pd.DataFrame(picks)

def main():
    trades = pd.read_csv(TRADES)
    trades["active_states"] = trades["active_states"].apply(parse_states)
    dev = trades[trades["split"] == "development"].copy()
    val = trades[trades["split"] == "validation"].copy()
    hold = trades[trades["split"] == "holdout"].copy()

    grid = build_grid(dev, val)
    grid.to_csv(OUT / "corrected_strategy_vix_validation_grid.csv", index=False)

    inf = build_inference(val)
    inf.to_csv(OUT / "corrected_strategy_vix_inference.csv", index=False)

    strategy_summary = (
        trades.groupby(["strategy", "split"])
        .agg(
            trades=("net_rupees", "size"),
            net_rupees=("net_rupees", "sum"),
            mean_net=("net_rupees", "mean"),
            win_rate=("net_rupees", lambda x: float((x > 0).mean())),
            cost_rupees=("cost_rupees", "sum"),
        )
        .reset_index()
    )
    dd_rows = []
    for (strategy, split), z in trades.groupby(["strategy", "split"]):
        dd_rows.append({"strategy": strategy, "split": split, "max_dd": dd(z.sort_values("expiry")["net_rupees"].to_numpy())})
    strategy_summary = strategy_summary.merge(pd.DataFrame(dd_rows), on=["strategy", "split"], how="left")
    strategy_summary.to_csv(OUT / "corrected_strategy_summary_by_split.csv", index=False)

    dev_counts = dev.groupby("strategy").size()
    candidates = sorted(set(dev_counts[dev_counts >= 20].index) - CALENDAR)
    benchmark_scores = dev[dev["strategy"].isin(candidates)].groupby("strategy")["net_rupees"].mean().sort_values(ascending=False)
    benchmark = str(benchmark_scores.index[0]) if len(benchmark_scores) else None
    bench_val = val[val["strategy"] == benchmark]
    bench_dd = dd(bench_val.sort_values("expiry")["net_rupees"].to_numpy()) if len(bench_val) else np.inf

    candidate_rows = []
    for _, row in grid.iterrows():
        strategy = row["strategy"]
        mode = row["vix_mode"]
        if mode == "ALL" or strategy not in candidates:
            continue
        v = mode_rows(val[val["strategy"] == strategy], mode)
        if len(v) < 20:
            continue
        cost50 = float(v["net_plus50_cost_rupees"].sum())
        vdd = dd(v.sort_values("expiry")["net_rupees"].to_numpy())
        eligible = (
            row["development_net"] >= 0
            and row["validation_net"] > 0
            and row["validation_trades"] >= 20
            and cost50 > 0
            and vdd <= 1.25 * bench_dd
        )
        candidate_rows.append({
            **row.to_dict(),
            "benchmark_strategy": benchmark,
            "benchmark_validation_dd": bench_dd,
            "promotion_gate_dd": 1.25 * bench_dd,
            "eligible": bool(eligible),
        })
    candidate_df = pd.DataFrame(candidate_rows)
    candidate_df.to_csv(OUT / "corrected_frozen_strategy_vix_candidates.csv", index=False)
    frozen_candidates = candidate_df[candidate_df["eligible"]].sort_values(["validation_net", "validation_mean"], ascending=False).head(10) if len(candidate_df) else pd.DataFrame()
    frozen_candidates.to_csv(OUT / "corrected_frozen_top10_strategy_vix_candidates.csv", index=False)

    routers = []
    frozen = []
    maps = {}
    for criterion in ["mean", "median", "sharpe"]:
        mapping = router_map(dev, criterion, candidates)
        maps[criterion] = mapping
        for split_name, frame in [("development", dev), ("validation", val)]:
            rt = route_eval(frame, mapping)
            routers.append({
                "router": criterion,
                "split": split_name,
                "trades": len(rt),
                "net_rupees": float(rt["net_rupees"].sum()) if len(rt) else np.nan,
                "mean_net": float(rt["net_rupees"].mean()) if len(rt) else np.nan,
                "max_dd": dd(rt.sort_values("expiry")["net_rupees"].to_numpy()) if len(rt) else np.nan,
                "cost50_net": float(rt["net_plus50_cost_rupees"].sum()) if len(rt) else np.nan,
            })
        dv = [x for x in routers if x["router"] == criterion and x["split"] == "development"][0]
        vv = [x for x in routers if x["router"] == criterion and x["split"] == "validation"][0]
        gate = (
            dv["net_rupees"] >= 0
            and vv["net_rupees"] > 0
            and vv["trades"] >= 20
            and vv["cost50_net"] > 0
            and vv["max_dd"] <= 1.25 * bench_dd
        )
        if gate:
            frozen.append((criterion, vv["net_rupees"]))
    router_df = pd.DataFrame(routers)
    router_df.to_csv(OUT / "corrected_router_dev_validation.csv", index=False)
    frozen = [x[0] for x in sorted(frozen, key=lambda x: x[1], reverse=True)[:3]]

    hold_rows = []
    for criterion in frozen:
        rt = route_eval(hold, maps[criterion])
        base = hold[hold["strategy"] == benchmark]
        common = base[["expiry", "net_rupees"]].rename(columns={"net_rupees":"benchmark"}).merge(
            rt[["expiry","net_rupees"]].rename(columns={"net_rupees":"router"}) if len(rt) else pd.DataFrame(columns=["expiry","router"]),
            on="expiry", how="left"
        ).fillna({"router":0.0})
        hold_rows.append({
            "router": criterion,
            "holdout_trades": len(rt),
            "holdout_net_rupees": float(rt["net_rupees"].sum()) if len(rt) else 0.0,
            "holdout_cost50_net": float(rt["net_plus50_cost_rupees"].sum()) if len(rt) else 0.0,
            "holdout_dd": dd(rt.sort_values("expiry")["net_rupees"].to_numpy()) if len(rt) else 0.0,
            "benchmark_strategy": benchmark,
            "benchmark_holdout_net": float(base["net_rupees"].sum()),
            "mean_uplift_vs_benchmark": float((common["router"] - common["benchmark"]).mean()) if len(common) else np.nan,
        })
    hold_router = pd.DataFrame(hold_rows)
    hold_router.to_csv(OUT / "corrected_frozen_router_holdout.csv", index=False)

    raw = json.loads((OUT / "summary.json").read_text())
    corrected = {
        "phase": 43,
        "status": "COMPLETE_CORRECTED_POSTPROCESS",
        "strategies_declared": int(raw["strategies_declared"]),
        "defined_risk_strategies": int(raw["defined_risk_strategies"]),
        "expiry_files": int(raw["expiry_files"]),
        "opportunities": int(raw["opportunities"]),
        "trade_rows": int(raw["trade_rows"]),
        "development_rows": int(raw["development_rows"]),
        "validation_rows": int(raw["validation_rows"]),
        "holdout_rows": int(raw["holdout_rows"]),
        "frozen_top10_count": int(len(frozen_candidates)),
        "frozen_router_count": int(len(frozen)),
        "development_unconditional_benchmark": benchmark,
        "development_benchmark_mean": float(benchmark_scores.iloc[0]) if len(benchmark_scores) else np.nan,
        "benchmark_validation_dd": bench_dd,
        "data_errors": int(raw["data_errors"]),
        "decision": "NO_PROMOTION" if len(frozen) == 0 else "PENDING_HOLDOUT_AUDIT",
        "inference_fix": "regime versus non-regime validation expiry groups; previous same-row paired inference invalidated",
    }
    (OUT / "corrected_summary.json").write_text(json.dumps(corrected, indent=2, default=str))
    (OUT / "corrected_router_maps.json").write_text(json.dumps({"benchmark": benchmark, "maps": maps, "frozen": frozen}, indent=2))

    print(json.dumps(corrected, indent=2))

if __name__ == "__main__":
    main()
