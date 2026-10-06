import json, os, sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, "research")
import phase40_ensemble_direction as eng
import phase32_continuous_delta_6x6_backtest as base

ROOT = Path("results/phase40_ensemble")
OUT = ROOT / "sequential_top10.csv"
EXPIRY_OUT = ROOT / "sequential_top10_expiry.csv"
SUMMARY = ROOT / "sequential_summary.json"

N_BOOT = 10000
RNG = np.random.default_rng(20261006)

def load_frozen_control():
    fc = pd.read_csv("results/phase38_corrected_model_robustness/frozen_control_expiry.csv")
    fc["expiry"] = pd.to_datetime(fc["expiry"], errors="coerce")
    fc["expiry"] = fc["expiry"].dt.tz_localize(base.TZ)
    fc["net_rupees"] = pd.to_numeric(fc["net_rupees"], errors="coerce")
    return fc.dropna(subset=["expiry","net_rupees"]).set_index("expiry")["net_rupees"]

def point_signal_map(z, combo, agg, vm, thr):
    r = eng.build_ref_directions(z, tuple(combo.split("+")), agg, vm, thr).copy()
    return {pd.Timestamp(x.expiry).date(): int(x.bullish_signal) for _, x in r.iterrows()}

def study_expiries_with_data(spot):
    ex = eng.study_expiries()
    expected = base.expected_weekly_expiries(spot)
    expected_set = set(expected)
    out = [x for x in ex if x in expected_set]
    if len(out) != len(ex):
        missing = [str(x.date()) for x in ex if x not in expected_set]
        raise RuntimeError(f"study expiries absent from canonical calendar: {missing}")
    return out, expected

def load_spot():
    return base.load("index/NIFTY.parquet")[["timestamp","close"]].rename(columns={"close":"spot"})

def load_option(expiry):
    od = base.load(f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet")
    od["option_type"] = od.option_type.astype(str).str.upper()
    od["strike"] = pd.to_numeric(od.strike, errors="coerce")
    return od.dropna(subset=["timestamp","strike","close"]).copy()

def expiry_window(expected, expiry, spot):
    idx = expected.index(expiry)
    start = expiry - pd.Timedelta(days=7) if idx == 0 else expected[idx-1] + pd.Timedelta(hours=15, minutes=30)
    last = expiry + pd.Timedelta(hours=15, minutes=29)
    return spot[(spot.timestamp > start) & (spot.timestamp <= last)].copy(), start

def run_candidate(candidate, z, vix, thr, expiries, expected, spot):
    signals = point_signal_map(
        z, candidate["combo"], candidate["aggregator"], candidate["vix_mode"], thr
    )
    target_dir = 1
    all_trades = []
    expiry_rows = []

    for i, expiry in enumerate(expiries, 1):
        od = load_option(expiry)
        sd, window_start = expiry_window(expected, expiry, spot)
        signal = int(signals.get(expiry.date(), target_dir))

        # signal=+1 bullish -> PUT arm inside canonical engine (-1)
        # signal=-1 bearish -> CALL arm inside canonical engine (+1)
        model_dir = signal
        if model_dir == 1:
            requested = -1
        elif model_dir == -1:
            requested = 1
        else:
            requested = target_dir

        # The policy supplies the initial direction for the expiry. Once an
        # entry is made, the canonical Phase-32 state machine takes over and
        # flips after losing trades exactly as in the control.
        tr, _, target_dir = base.run_expiry(
            expiry, od, sd, int(requested), window_start
        )
        all_trades.extend(tr)
        expiry_rows.append({
            "candidate_id": int(candidate["candidate_id"]),
            "expiry": str(expiry.date()),
            "input_signal": signal,
            "requested_direction": "PUT" if requested == -1 else "CALL",
            "final_state_direction": "PUT" if target_dir == -1 else "CALL",
            "state_after_expiry": "PUT" if target_dir == -1 else "CALL",
            "net_rupees": float(sum(float(t["net_rupees"]) for t in tr)),
            "gross_rupees": float(sum(float(t["gross_rupees"]) for t in tr)),
            "cost_rupees": float(sum(float(t["cost_rupees"]) for t in tr)),
            "trades": int(len(tr)),
        })
        if i % 25 == 0:
            print(f"candidate={candidate['candidate_id']} expiry={i}/{len(expiries)}", flush=True)

    t = pd.DataFrame(all_trades)
    e = pd.DataFrame(expiry_rows)
    return t, e

def bootstrap(diff):
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
    null = (x * signs).mean(axis=1)
    p = float((np.sum(null >= obs) + 1) / (N_BOOT + 1))
    return {
        "n": int(n),
        "mean": obs,
        "total": float(x.sum()),
        "ci_mean_low": float(np.quantile(means, .025)),
        "ci_mean_high": float(np.quantile(means, .975)),
        "ci_total_low": float(np.quantile(means * n, .025)),
        "ci_total_high": float(np.quantile(means * n, .975)),
        "p_one_sided": p,
        "p_positive_expiry": float(np.mean(x > 0)),
        "positive_expiries": int(np.sum(x > 0)),
    }

def period_stats(expiry_df, control, start, end):
    x = expiry_df.copy()
    x["expiry"] = pd.to_datetime(x["expiry"]).dt.tz_localize(base.TZ)
    x = x[x["expiry"].between(start, end)]
    a = x.groupby("expiry")["net_rupees"].sum().sort_index()
    c = control.loc[control.index.intersection(a.index)].sort_index()
    common = a.index.intersection(c.index)
    diff = (a.loc[common] - c.loc[common]).to_numpy(float)
    b = bootstrap(diff)
    aa = a.loc[common]
    cc = c.loc[common]
    cum_a = aa.cumsum()
    cum_c = cc.cumsum()
    dd_a = float((cum_a.cummax() - cum_a).max()) if len(aa) else np.nan
    dd_c = float((cum_c.cummax() - cum_c).max()) if len(cc) else np.nan
    return {
        **b,
        "candidate_net": float(aa.sum()),
        "control_net": float(cc.sum()),
        "candidate_drawdown_by_expiry": dd_a,
        "control_drawdown_by_expiry": dd_c,
        "common_expiries": int(len(common)),
    }

def stress(expiry_df, start, end, mult):
    x = expiry_df.copy()
    x["expiry"] = pd.to_datetime(x["expiry"]).dt.tz_localize(base.TZ)
    x = x[x["expiry"].between(start, end)]
    return float(x["gross_rupees"].sum() - mult * x["cost_rupees"].sum())

def main():
    selection = json.load(open(ROOT / "selection.json"))
    top = selection["top10"]
    z = eng.load_experts()
    vix = eng.load_vix()
    z = eng.add_vix(z, vix)
    thr = eng.vix_thresholds(vix)
    z["VIX"] = [eng.vix_prob(x, thr["ret_q67"]) for x in z["vix_ret1"]]
    spot = load_spot()
    expiries, expected = study_expiries_with_data(spot)
    # Restrict the sequential replay to the exact prediction-covered study
    # universe used by the frozen Phase-40 validation grid.
    pred_dates = set(z["expiry"].dt.date.dropna())
    expiries = [e for e in expiries if e.date() in pred_dates]
    if len(expiries) != 93:
        raise AssertionError(f"Phase-40 replay universe changed: expected 93 prediction-covered expiries, got {len(expiries)}")
    control = load_frozen_control()

    all_results = []
    all_expiry = []
    for candidate in top:
        t, e = run_candidate(candidate, z, vix, thr, expiries, expected, spot)
        e["candidate_id"] = int(candidate["candidate_id"])
        all_expiry.append(e)

        for period, start, end in [
            ("validation", eng.START, eng.VAL_END),
            ("holdout", eng.HOLD_START, eng.HOLD_END),
        ]:
            m = period_stats(e, control, start, end)
            row = {
                "candidate_id": int(candidate["candidate_id"]),
                "combo": candidate["combo"],
                "aggregator": candidate["aggregator"],
                "vix_mode": candidate["vix_mode"],
                "period": period,
                **m,
                "net_cost_x1.25": stress(e, start, end, 1.25),
                "net_cost_x1.50": stress(e, start, end, 1.50),
                "net_cost_x2.00": stress(e, start, end, 2.00),
            }
            all_results.append(row)

    out = pd.DataFrame(all_results)
    ex = pd.concat(all_expiry, ignore_index=True)
    out.to_csv(OUT, index=False)
    ex.to_csv(EXPIRY_OUT, index=False)

    val = out[out.period == "validation"]
    hold = out[out.period == "holdout"]
    best_val = val.sort_values("mean", ascending=False).iloc[0]
    best_hold = hold.sort_values("candidate_net", ascending=False).iloc[0]

    summary = {
        "status": "SEQUENTIAL_REPLAY_COMPLETE",
        "top10_count": len(top),
        "study_expiries": len(expiries),
        "validation_positive_pvalue_candidates": int((val["p_one_sided"] < 0.05).sum()),
        "validation_candidates_positive_mean": int((val["mean"] > 0).sum()),
        "holdout_candidates_positive_mean": int((hold["mean"] > 0).sum()),
        "holdout_candidates_positive_total": int((hold["candidate_net"] > hold["control_net"]).sum()),
        "best_validation_candidate_id": int(best_val["candidate_id"]),
        "best_validation_mean_uplift": float(best_val["mean"]),
        "best_holdout_candidate_id": int(best_hold["candidate_id"]),
        "best_holdout_total_uplift": float(best_hold["candidate_net"] - best_hold["control_net"]),
        "n_bootstrap": N_BOOT,
    }
    json.dump(summary, open(SUMMARY, "w"), indent=2)
    print(json.dumps(summary, indent=2), flush=True)

if __name__ == "__main__":
    main()
