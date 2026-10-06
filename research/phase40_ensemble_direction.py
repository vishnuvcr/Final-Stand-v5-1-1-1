import json, os, sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, "research")
import phase32_continuous_delta_6x6_backtest as base

ROOT = Path("results/phase40_ensemble")
ROOT.mkdir(parents=True, exist_ok=True)
DATA = Path("data/phase36_selector_predictions.csv")
VIX_CACHE = Path("data/phase40_vix/india_vix.csv")

MODELS = ["CATBOOST","DART","WAVELET_TREE","OOF_STACK","MARKOV_REGIME_TREE"]
MODEL_COLS = {
    "CATBOOST":"catboost_prob",
    "DART":"dart_prob",
    "WAVELET_TREE":"wavelet_tree_prob",
    "OOF_STACK":"stack_prob",
    "MARKOV_REGIME_TREE":"ms_regime_tree_prob",
}
EXPERTS = MODELS + ["VIX"]

START = pd.Timestamp("2024-01-11", tz=base.TZ)
VAL_END = pd.Timestamp("2025-12-30", tz=base.TZ)
HOLD_START = pd.Timestamp("2026-01-06", tz=base.TZ)
HOLD_END = pd.Timestamp("2026-05-19", tz=base.TZ)

def tz_series(x):
    z = pd.to_datetime(x, errors="coerce")
    tz = getattr(z.dt, "tz", None)
    if tz is None:
        return z.dt.tz_localize(base.TZ)
    return z.dt.tz_convert(base.TZ)

def load_experts():
    z = pd.read_csv(DATA)
    z["expiry"] = pd.to_datetime(z["expiry"], errors="coerce")
    z["ref_ts"] = tz_series(z["ref_ts"])
    for m, c in MODEL_COLS.items():
        z[m] = pd.to_numeric(z[c], errors="coerce")
    return z

def load_vix():
    v = pd.read_csv(VIX_CACHE)
    v["date"] = pd.to_datetime(v["date"], errors="coerce").dt.date
    v["close"] = pd.to_numeric(v["close"], errors="coerce")
    v = v.dropna(subset=["date","close"]).sort_values("date").drop_duplicates("date", keep="last")
    v["ret1"] = v["close"].pct_change()
    return v

def previous_vix(vix, ref_ts):
    d = ref_ts.date()
    q = vix[vix["date"] < d]
    if len(q) < 2:
        return np.nan, np.nan
    row = q.iloc[-1]
    return float(row["close"]), float(row["ret1"])

def add_vix(z, vix):
    a = [previous_vix(vix, t) for t in z["ref_ts"]]
    out = z.copy()
    out["vix_close"] = [x[0] for x in a]
    out["vix_ret1"] = [x[1] for x in a]
    return out

def vix_thresholds(vix):
    # All thresholds are frozen from pre-2024 India VIX observations.
    d = vix[pd.to_datetime(vix["date"]) < pd.Timestamp("2024-01-01")]
    r = pd.to_numeric(d["ret1"], errors="coerce").dropna().abs()
    lv = pd.to_numeric(d["close"], errors="coerce").dropna()
    if len(r) < 20 or len(lv) < 20:
        raise RuntimeError("insufficient development India VIX history")
    return {
        "ret_q67": float(r.quantile(0.67)),
        "level_q33": float(lv.quantile(0.33)),
        "level_q67": float(lv.quantile(0.67)),
    }

def vix_prob(r, q):
    if not np.isfinite(r):
        return 0.50
    if r >= q:
        return 0.25
    if r <= -q:
        return 0.75
    return 0.50

def combo_grid():
    out = []
    for mask in range(1, 1 << len(EXPERTS)):
        combo = tuple(EXPERTS[i] for i in range(len(EXPERTS)) if mask & (1 << i))
        for agg in ["mean","median","majority","confidence_weighted"]:
            for vm in ["OFF","EXPERT","HIGH","LOW","RISING","FALLING","HIGH_RISING"]:
                out.append((combo, agg, vm))
    return out

def score_prob(sub, combo, agg):
    a = sub.loc[:, list(combo)].to_numpy(float)
    if agg == "mean":
        return np.nanmean(a, axis=1)
    if agg == "median":
        return np.nanmedian(a, axis=1)
    if agg == "majority":
        vote = np.sign(a - 0.5)
        pos = np.nansum(vote > 0, axis=1)
        neg = np.nansum(vote < 0, axis=1)
        return np.where(pos > neg, 1.0, np.where(neg > pos, 0.0, 0.5))
    w = np.abs(a - 0.5)
    num = np.nansum(w * a, axis=1)
    den = np.nansum(w, axis=1)
    return np.where(den > 0, num / den, 0.5)

def route_vix(prob, sub, combo, mode, thr):
    r = sub["vix_ret1"].to_numpy(float)
    lv = sub["vix_close"].to_numpy(float)
    base_dir = np.where(prob >= 0.5, 1, -1)
    q = thr["ret_q67"]
    high = lv >= thr["level_q67"]
    low = lv <= thr["level_q33"]
    rising = r >= q
    falling = r <= -q

    if mode == "EXPERT" and "VIX" not in combo:
        vp = sub["VIX"].to_numpy(float)
        prob = 0.5 * (prob + vp)
        base_dir = np.where(prob >= 0.5, 1, -1)

    if mode == "OFF" or mode == "EXPERT":
        return base_dir
    if mode == "HIGH":
        allow = high
    elif mode == "LOW":
        allow = low
    elif mode == "RISING":
        allow = rising
    elif mode == "FALLING":
        allow = falling
    elif mode == "HIGH_RISING":
        allow = high & rising
    else:
        allow = np.zeros(len(sub), dtype=bool)
    return np.where(allow, base_dir, 0)

def build_ref_directions(z, combo, agg, vm, thr):
    sub = z[(z["ref_ts"] >= START) & (z["ref_ts"] <= HOLD_END)].copy()
    p = score_prob(sub, combo, agg)
    routed = route_vix(p, sub, combo, vm, thr)
    sub["ensemble_prob"] = p
    sub["bullish_signal"] = routed
    return sub[["expiry","ref_ts","ensemble_prob","bullish_signal"]]

def expected_expiries(spot):
    return [e for e in base.expected_weekly_expiries(spot) if START <= e <= HOLD_END]

def replay_expiry(expiry, direction, spot, expected):
    od = base.load(f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet")
    od["option_type"] = od.option_type.astype(str).str.upper()
    od["strike"] = pd.to_numeric(od.strike, errors="coerce")
    od = od.dropna(subset=["timestamp","strike","close"])
    idx = expected.index(expiry)
    window_start = expiry - pd.Timedelta(days=7) if idx == 0 else expected[idx-1] + pd.Timedelta(hours=15, minutes=30)
    sd = spot[(spot.timestamp > window_start) & (spot.timestamp <= expiry + pd.Timedelta(hours=15, minutes=29))].copy()
    tr, _, _ = base.run_expiry(expiry, od, sd, int(direction), window_start)
    return tr

def build_arm_cache(expiries, spot):
    cache = {}
    for i, expiry in enumerate(expiries, 1):
        cache[(expiry.date(), 1)] = replay_expiry(expiry, 1, spot, expiries)
        cache[(expiry.date(), -1)] = replay_expiry(expiry, -1, spot, expiries)
        print(f"precomputed expiry {i}/{len(expiries)} {expiry.date()}", flush=True)
    return cache

def metrics(t):
    if t is None or t.empty:
        return {"trades":0,"net":0.0,"win_rate":np.nan,"max_dd":0.0,"profit_factor":np.nan}
    x = t.copy()
    x["cum"] = x.net_rupees.cumsum()
    x["dd"] = x.cum.cummax() - x.cum
    wins = float((x.net_rupees > 0).mean())
    gains = float(x.loc[x.net_rupees > 0, "net_rupees"].sum())
    losses = float(-x.loc[x.net_rupees < 0, "net_rupees"].sum())
    return {
        "trades": int(len(x)),
        "net": float(x.net_rupees.sum()),
        "win_rate": wins,
        "max_dd": float(x.dd.max()),
        "profit_factor": gains / losses if losses > 0 else np.nan,
    }

def candidate_trades(z, combo, agg, vm, thr, arm_cache, start, end):
    refs = build_ref_directions(z, combo, agg, vm, thr)
    refs = refs[(refs["expiry"] >= start) & (refs["expiry"] <= end)]
    rows = []
    for _, r in refs.iterrows():
        sig = int(r["bullish_signal"])
        if sig == 0:
            continue
        # bullish -> PUT arm (-1), bearish -> CALL arm (+1)
        arm = -1 if sig == 1 else 1
        rows.extend(arm_cache.get((pd.Timestamp(r["expiry"]).date(), arm), []))
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(["exit_ts","entry_ts"]).reset_index(drop=True)

def main():
    z = load_experts()
    vix = load_vix()
    z = add_vix(z, vix)
    thr = vix_thresholds(vix)
    z["VIX"] = [vix_prob(x, thr["ret_q67"]) for x in z["vix_ret1"]]
    grid = combo_grid()
    if len(grid) != 1764:
        raise AssertionError(len(grid))

    spot = base.load("index/NIFTY.parquet")[["timestamp","close"]].rename(columns={"close":"spot"})
    expiries = expected_expiries(spot)
    # Only expiries for which an expert prediction exists are required.
    pred_dates = set(z["expiry"].dt.date.dropna())
    expiries = [e for e in expiries if e.date() in pred_dates]
    arm_cache = build_arm_cache(expiries, spot)

    validation_rows = []
    for k, (combo, agg, vm) in enumerate(grid, 1):
        tr = candidate_trades(z, combo, agg, vm, thr, arm_cache, START, VAL_END)
        m = metrics(tr)
        validation_rows.append({
            "candidate_id": k,
            "combo": "+".join(combo),
            "aggregator": agg,
            "vix_mode": vm,
            **m,
        })
        if k % 100 == 0:
            print(f"screened {k}/{len(grid)}", flush=True)

    full_grid = pd.DataFrame(validation_rows)
    control_net = 63948.222105380155
    full_grid["validation_uplift_vs_frozen_control"] = full_grid["net"] - control_net
    full_grid = full_grid.sort_values(["validation_uplift_vs_frozen_control","profit_factor"], ascending=[False,False]).reset_index(drop=True)
    full_grid.to_csv(ROOT / "grid_validation.csv", index=False)

    # Freeze top 10 only on validation.
    top = full_grid.head(10).copy()
    top10 = top.to_dict(orient="records")
    with open(ROOT / "selection.json","w") as fh:
        json.dump({"grid_candidates":len(full_grid),"top10_count":len(top10),"vix_thresholds":thr,"frozen_control_validation_net":control_net,"top10":top10},fh,indent=2)

    holdout_rows = []
    for row in top10:
        combo = tuple(row["combo"].split("+"))
        tr = candidate_trades(z, combo, row["aggregator"], row["vix_mode"], thr, arm_cache, HOLD_START, HOLD_END)
        m = metrics(tr)
        holdout_rows.append({
            "candidate_id": int(row["candidate_id"]),
            "combo": row["combo"],
            "aggregator": row["aggregator"],
            "vix_mode": row["vix_mode"],
            "validation_net": float(row["net"]),
            "validation_uplift": float(row["validation_uplift_vs_frozen_control"]),
            **{f"holdout_{k}":v for k,v in m.items()},
        })
    pd.DataFrame(holdout_rows).to_csv(ROOT / "holdout_top10.csv", index=False)

    with open(ROOT / "status.json","w") as fh:
        json.dump({"status":"GRID_COMPLETE","grid_candidates":len(full_grid),"holdout_candidates":len(holdout_rows),"vix_cache_rows":len(vix),"validation_start":str(START.date()),"validation_end":str(VAL_END.date()),"holdout_start":str(HOLD_START.date()),"holdout_end":str(HOLD_END.date())},fh,indent=2)

if __name__ == "__main__":
    main()
