import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, "research")
import phase40_ensemble_direction as eng

ROOT = Path("results/phase40_ensemble")
OUT = ROOT / "inference_top10.csv"
SUMMARY = ROOT / "inference_summary.json"
VIX_SUMMARY = ROOT / "vix_mode_summary.csv"
SIZE_SUMMARY = ROOT / "combo_size_summary.csv"

RNG = np.random.default_rng(20261006)
N_BOOT = 10000

def load_arm_cache():
    q = pd.read_parquet(ROOT / "arm_cache.parquet")
    cache = {}
    for (d, direction), g in q.groupby(["expiry","direction_arm"], sort=False):
        cache[(pd.Timestamp(d).date(), int(direction))] = g.drop(columns=["expiry","direction_arm"]).to_dict("records")
    return cache

def expiry_stream(z, combo, agg, vm, thr, cache, start, end):
    refs = eng.build_ref_directions(z, tuple(combo.split("+")) if isinstance(combo, str) else combo, agg, vm, thr)
    refs = refs[(refs["expiry"] >= start) & (refs["expiry"] <= end)].sort_values("expiry")
    rows = []
    for _, r in refs.iterrows():
        sig = int(r["bullish_signal"])
        arm = -1 if sig == 1 else 1
        trades = cache.get((pd.Timestamp(r["expiry"]).date(), arm), [])
        net = float(sum(float(t.get("net_rupees", 0.0)) for t in trades))
        gross = float(sum(float(t.get("gross_rupees", 0.0)) for t in trades))
        cost = float(sum(float(t.get("cost_rupees", 0.0)) for t in trades))
        rows.append({
            "expiry": pd.Timestamp(r["expiry"]).normalize(),
            "signal": sig,
            "net": net,
            "gross": gross,
            "cost": cost,
            "trades": len(trades),
        })
    return pd.DataFrame(rows)

def bootstrap_stats(diff):
    x = np.asarray(diff, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n == 0:
        return {"n":0,"mean":np.nan,"total":np.nan,"ci_mean_low":np.nan,"ci_mean_high":np.nan,
                "ci_total_low":np.nan,"ci_total_high":np.nan,"p_one_sided":np.nan,
                "p_positive_expiry":np.nan,"positive_expiries":0}
    idx = RNG.integers(0, n, size=(N_BOOT, n))
    means = x[idx].mean(axis=1)
    obs = float(x.mean())
    signs = RNG.choice(np.array([-1.0, 1.0]), size=(N_BOOT, n))
    null_means = (x * signs).mean(axis=1)
    p = float((np.sum(null_means >= obs) + 1) / (N_BOOT + 1))
    return {
        "n": int(n),
        "mean": obs,
        "total": float(x.sum()),
        "ci_mean_low": float(np.quantile(means, 0.025)),
        "ci_mean_high": float(np.quantile(means, 0.975)),
        "ci_total_low": float(np.quantile(means * n, 0.025)),
        "ci_total_high": float(np.quantile(means * n, 0.975)),
        "p_one_sided": p,
        "p_positive_expiry": float(np.mean(x > 0)),
        "positive_expiries": int(np.sum(x > 0)),
    }

def period_metrics(stream, control):
    a = stream.set_index("expiry")["net"]
    c = control.copy()
    c.index = pd.to_datetime(c.index)
    if c.index.tz is None:
        c.index = c.index.tz_localize(eng.base.TZ)
    else:
        c.index = c.index.tz_convert(eng.base.TZ)
    common = a.index.intersection(c.index)
    dif = (a.loc[common] - c.loc[common]).to_numpy(float)
    b = bootstrap_stats(dif)

    ordered = a.loc[common].sort_index()
    cum_a = ordered.cumsum()
    dd_a = float((cum_a.cummax() - cum_a).max()) if len(cum_a) else np.nan
    ordered_c = c.loc[common].sort_index()
    cum_c = ordered_c.cumsum()
    dd_c = float((cum_c.cummax() - cum_c).max()) if len(cum_c) else np.nan

    return {
        **b,
        "candidate_net": float(a.loc[common].sum()),
        "control_net": float(c.loc[common].sum()),
        "candidate_drawdown_by_expiry": dd_a,
        "control_drawdown_by_expiry": dd_c,
        "common_expiries": int(len(common)),
    }

def stressed_net(stream, multiplier):
    return float(stream["gross"].sum() - multiplier * stream["cost"].sum())

def main():
    grid = pd.read_csv(ROOT / "grid_validation.csv")
    selection = json.load(open(ROOT / "selection.json"))
    top = pd.DataFrame(selection["top10"])

    z = eng.load_experts()
    vix = eng.load_vix()
    z = eng.add_vix(z, vix)
    thr = eng.vix_thresholds(vix)
    z["VIX"] = [eng.vix_prob(x, thr["ret_q67"]) for x in z["vix_ret1"]]

    spot = eng.base.load("index/NIFTY.parquet")[["timestamp","close"]].rename(columns={"close":"spot"})
    expiries = eng.study_expiries()
    expected = eng.base.expected_weekly_expiries(spot)
    pred_dates = set(z["expiry"].dt.date.dropna())
    expiries = [e for e in expiries if e.date() in pred_dates]
    cache = load_arm_cache()

    fc = pd.read_csv("results/phase38_corrected_model_robustness/frozen_control_expiry.csv")
    fc["expiry"] = pd.to_datetime(fc["expiry"], errors="coerce").dt.tz_localize(eng.base.TZ)
    fc["net_rupees"] = pd.to_numeric(fc["net_rupees"], errors="coerce")
    fc = fc.dropna(subset=["expiry","net_rupees"]).set_index("expiry")

    results = []
    candidate_expiry_tables = []
    for _, row in top.iterrows():
        combo = row["combo"]
        agg = row["aggregator"]
        vm = row["vix_mode"]
        val = expiry_stream(z, combo, agg, vm, thr, cache, eng.START, eng.VAL_END)
        hold = expiry_stream(z, combo, agg, vm, thr, cache, eng.HOLD_START, eng.HOLD_END)
        # Store a compact audit table for every shortlisted policy.
        for period, stream in [("validation", val), ("holdout", hold)]:
            if stream.empty:
                continue
            x = stream.copy()
            x["candidate_id"] = int(row["candidate_id"])
            x["period"] = period
            candidate_expiry_tables.append(x)
        for period, stream in [("validation", val), ("holdout", hold)]:
            m = period_metrics(stream, fc["net_rupees"])
            results.append({
                "candidate_id": int(row["candidate_id"]),
                "combo": combo,
                "aggregator": agg,
                "vix_mode": vm,
                "period": period,
                **m,
                "candidate_cost_x1.25_net": stressed_net(stream, 1.25),
                "candidate_cost_x1.50_net": stressed_net(stream, 1.50),
                "candidate_cost_x2.00_net": stressed_net(stream, 2.00),
            })

    out = pd.DataFrame(results)
    out.to_csv(OUT, index=False)
    pd.concat(candidate_expiry_tables, ignore_index=True).to_csv(ROOT / "top10_expiry_streams.csv", index=False)

    vm = (
        grid.groupby("vix_mode")
        .agg(candidates=("candidate_id","count"),
             positive_validation=("validation_uplift_vs_sequential_control", lambda x: int((x > 0).sum())),
             median_uplift=("validation_uplift_vs_sequential_control","median"),
             best_uplift=("validation_uplift_vs_sequential_control","max"))
        .reset_index()
    )
    vm.to_csv(VIX_SUMMARY, index=False)

    gs = grid.copy()
    gs["combo_size"] = gs["combo"].astype(str).str.count("\\+") + 1
    sm = (
        gs.groupby("combo_size")
        .agg(candidates=("candidate_id","count"),
             positive_validation=("validation_uplift_vs_sequential_control", lambda x: int((x > 0).sum())),
             median_uplift=("validation_uplift_vs_sequential_control","median"),
             best_uplift=("validation_uplift_vs_sequential_control","max"))
        .reset_index()
    )
    sm.to_csv(SIZE_SUMMARY, index=False)

    # Two primary figures: validation uplift by VIX mode and holdout top policies.
    fig, ax = plt.subplots(figsize=(9,5))
    ax.bar(vm["vix_mode"], vm["best_uplift"])
    ax.axhline(0, linewidth=1)
    ax.set_ylabel("Best validation uplift vs common-expiry control (₹)")
    ax.set_title("Phase 40 validation: effect of VIX routing mode")
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    fig.savefig(ROOT / "validation_uplift_by_vix_mode.png", dpi=160)
    plt.close(fig)

    h = out[out["period"]=="holdout"].copy().sort_values("candidate_net", ascending=False)
    fig, ax = plt.subplots(figsize=(10,5))
    labels = [f'{int(x)}:{v}' for x,v in zip(h["candidate_id"], h["vix_mode"])]
    ax.bar(labels, h["candidate_net"])
    ax.set_ylabel("Holdout net P&L (₹)")
    ax.set_title("Phase 40 frozen top-10 holdout replay")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(ROOT / "holdout_top10.png", dpi=160)
    plt.close(fig)

    summary = {
        "status":"INFERENCE_COMPLETE",
        "grid_candidates": int(len(grid)),
        "unique_validation_policies": int(grid["signal_signature"].nunique()),
        "top10_unique": int(len(top)),
        "validation_positive_candidate_count": int((grid["validation_uplift_vs_sequential_control"] > 0).sum()),
        "validation_best_uplift": float(grid["validation_uplift_vs_sequential_control"].max()),
        "validation_best_candidate_id": int(grid.iloc[grid["validation_uplift_vs_sequential_control"].argmax()]["candidate_id"]),
        "vix_thresholds": thr,
        "n_bootstrap": N_BOOT,
        "results_file": str(OUT),
    }
    with open(SUMMARY,"w") as fh:
        json.dump(summary,fh,indent=2)

if __name__ == "__main__":
    main()
