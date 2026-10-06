import itertools, json, os, sys
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
    try:
        tz = z.dt.tz
    except Exception:
        tz = None
    return z.dt.tz_localize(base.TZ) if tz is None else z.dt.tz_convert(base.TZ)

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
    z = z.copy()
    z["vix_close"] = [x[0] for x in a]
    z["vix_ret1"] = [x[1] for x in a]
    return z

def vix_thresholds():
    # Point-in-time development distribution from the existing feature matrix.
    p = Path("results/phase39_features/point_in_time_features.csv")
    f = pd.read_csv(p, usecols=["entry_ts","global_VIX","global_VIX_ret1"])
    f["entry_ts"] = tz_series(f["entry_ts"])
    d = f[f["entry_ts"] < pd.Timestamp("2024-01-01", tz=base.TZ)]
    r = pd.to_numeric(d["global_VIX_ret1"], errors="coerce").dropna().abs()
    lv = pd.to_numeric(d["global_VIX"], errors="coerce").dropna()
    if len(r) < 20 or len(lv) < 20:
        raise RuntimeError("development VIX history is insufficient")
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

def make_grid(z, thr):
    for i, row in z.iterrows():
        z.at[i, "VIX"] = vix_prob(row["vix_ret1"], thr["ret_q67"])
    z["VIX"] = pd.to_numeric(z["VIX"], errors="coerce").fillna(0.5)

    rows = []
    for mask in range(1, 1 << len(EXPERTS)):
        combo = tuple(EXPERTS[i] for i in range(len(EXPERTS)) if mask & (1 << i))
        for agg in ["mean","median","majority","confidence_weighted"]:
            for vm in ["OFF","EXPERT","HIGH","LOW","RISING","FALLING","HIGH_RISING"]:
                rows.append((combo, agg, vm))
    return rows

def score_prob(sub, combo, agg):
    a = sub.loc[:, list(combo)].to_numpy(float)
    if agg == "mean":
        return np.nanmean(a, axis=1)
    if agg == "median":
        return np.nanmedian(a, axis=1)
    if agg == "majority":
        return (np.nanmean(a >= 0.5, axis=1) >= 0.5).astype(float)
    w = np.abs(a - 0.5) + 1e-6
    num = np.nansum(w * a, axis=1)
    den = np.nansum(w, axis=1)
    return num / den

def apply_vix_gate(prob, sub, mode, thr):
    if mode == "OFF":
        return prob
    r = sub["vix_ret1"].to_numpy(float)
    lv = sub["vix_close"].to_numpy(float)
    base_dir = np.where(prob >= 0.5, 1, -1)  # +1 bullish, -1 bearish
    q = thr["ret_q67"]
    high = lv >= thr["level_q67"]
    low = lv <= thr["level_q33"]
    rising = r >= q
    falling = r <= -q
    allow = np.ones(len(sub), dtype=bool)
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
    # False means use canonical-control direction rather than ensemble direction.
    return np.where(allow, base_dir, 0)

def build_ref_directions(z, combo, agg, vm, thr):
    sub = z[(z["ref_ts"] >= START) & (z["ref_ts"] <= HOLD_END)].copy()
    p = score_prob(sub, combo, agg)
    routed = apply_vix_gate(p, sub, vm, thr)
    sub["ensemble_prob"] = p
    sub["bullish_signal"] = routed
    return sub[["expiry","ref_ts","ensemble_prob","bullish_signal"]]

def get_weekly_expiries():
    # Reuse the canonical calendar and restrict to the frozen study slice.
    dummy = pd.DataFrame({"timestamp": pd.to_datetime([], utc=False), "spot":[]})
    # Actual expected expiries require NIFTY data, loaded below by base.
    spot = base.load("index/NIFTY.parquet")[["timestamp","close"]].rename(columns={"close":"spot"})
    return [e for e in base.expected_weekly_expiries(spot) if START <= e <= HOLD_END]

def replay_expiry(expiry, direction):
    api = base.HfApi(token=os.getenv("HF_TOKEN") or None)
    od = base.load(f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet")
    od["option_type"] = od.option_type.astype(str).str.upper()
    od["strike"] = pd.to_numeric(od.strike, errors="coerce")
    od = od.dropna(subset=["timestamp","strike","close"])
    spot = base.load("index/NIFTY.parquet")[["timestamp","close"]].rename(columns={"close":"spot"})
    expected = [e for e in base.expected_weekly_expiries(spot) if START <= e <= HOLD_END]
    idx = expected.index(expiry)
    window_start = expiry - pd.Timedelta(days=7) if idx == 0 else expected[idx-1] + pd.Timedelta(hours=15, minutes=30)
    sd = spot[(spot.timestamp > window_start) & (spot.timestamp <= expiry + pd.Timedelta(hours=15, minutes=29))].copy()
    tr, sk, _ = base.run_expiry(expiry, od, sd, int(direction), window_start)
    return tr

def build_arm_cache(expiries):
    cache = {}
    for expiry in expiries:
        cache[(expiry.date(), 1)] = replay_expiry(expiry, 1)
        cache[(expiry.date(), -1)] = replay_expiry(expiry, -1)
    with open(ROOT / "arm_cache.json", "w") as fh:
        json.dump({f"{k[0]}|{k[1]}": v for k,v in cache.items()}, fh)
    return cache

def direction_pnl(sub, combo, agg, vm, thr, arm_cache):
    refs = build_ref_directions(sub, combo, agg, vm, thr)
    by_exp = {pd.Timestamp(r.expiry).date(): int(r.bullish_signal) for _,r in refs.iterrows()}
    parts = []
    for d, sig in by_exp.items():
        arm = 0 if sig == 0 else (-1 if sig == 1 else 1)  # bullish -> PUT; bearish -> CALL
        if arm == 0:
            continue
        tr = arm_cache.get((d, arm))
        if tr:
            parts.extend(tr)
    if not parts:
        return pd.DataFrame()
    t = pd.DataFrame(parts)
    t["exit_ts"] = pd.to_datetime(t["exit_ts"])
    t = t.sort_values(["exit_ts","entry_ts"]).reset_index(drop=True)
    return t

def metrics(t):
    if t.empty:
        return {"trades":0,"net":0.0,"wins":0.0,"win_rate":np.nan,"max_dd":0.0}
    t = t.copy()
    t["cum"] = t["net_rupees"].cumsum()
    t["dd"] = t["cum"].cummax() - t["cum"]
    wins = int((t["net_rupees"] > 0).sum())
    return {
        "trades": int(len(t)),
        "net": float(t["net_rupees"].sum()),
        "wins": wins,
        "win_rate": float(wins/len(t)),
        "max_dd": float(t["dd"].max()),
        "profit_factor": float(t.loc[t.net_rupees > 0,"net_rupees"].sum() / max(1e-12, -t.loc[t.net_rupees < 0,"net_rupees"].sum())),
    }

def main():
    global THR
    z = load_experts()
    v = load_vix()
    z = add_vix(z, v)
    THR = vix_thresholds()
    grid = make_grid(z, THR)
    expiries = get_weekly_expiries()
    arm_cache = build_arm_cache(expiries)

    # Fixed opportunity / expiry screen on validation.
    val_rows = []
    for combo, agg, vm in grid:
        refs = build_ref_directions(z, combo, agg, vm, THR)
        refs = refs[(refs["expiry"] >= pd.Timestamp("2024-01-11")) & (refs["expiry"] <= VAL_END)]
        for _, r in refs.iterrows():
            sig = int(r["bullish_signal"])
            if sig == 0:
                continue
            arm = -1 if sig == 1 else 1
            tr = arm_cache.get((pd.Timestamp(r["expiry"]).date(), arm), [])
            val_rows.extend(tr)
        m = metrics(pd.DataFrame(val_rows[-100000:])) if val_rows else metrics(pd.DataFrame())
        val_rows = []
        # Cheap validation score is calculated from the precomputed arm streams.
        rows_arm = []
        for _,r in refs.iterrows():
            sig=int(r["bullish_signal"])
            if sig==0: continue
            arm=-1 if sig==1 else 1
            rows_arm.extend(arm_cache.get((pd.Timestamp(r["expiry"]).date(),arm), []))
        mm=metrics(pd.DataFrame(rows_arm))
        val_rows.append({"combo":"+".join(combo),"aggregator":agg,"vix_mode":vm,**mm})

    grid_df = pd.DataFrame(val_rows)
    if len(grid_df) != 1764:
        raise AssertionError(f"grid rows {len(grid_df)} != 1764")
    # Frozen top 10, validation only.
    grid_df = grid_df.sort_values(["net","profit_factor"], ascending=[False,False]).reset_index(drop=True)
    top = grid_df.head(10).copy()
    top.to_csv(ROOT / "grid_validation.csv", index=False)
    top10 = []
    for _,r in top.iterrows():
        combo=tuple(r["combo"].split("+"))
        top10.append({
            "combo":r["combo"],"aggregator":r["aggregator"],"vix_mode":r["vix_mode"],
            "validation_net":float(r["net"]),"validation_max_dd":float(r["max_dd"])
        })
    with open(ROOT / "selection.json","w") as fh:
        json.dump({"grid_candidates":1764,"top10_count":len(top10),"vix_thresholds":THR,"top10":top10},fh,indent=2)

    hold_rows=[]
    for c in top10:
        refs=build_ref_directions(z, tuple(c["combo"].split("+")), c["aggregator"], c["vix_mode"], THR)
        refs=refs[(refs["expiry"] >= HOLD_START) & (refs["expiry"] <= HOLD_END)]
        rows_arm=[]
        for _,r in refs.iterrows():
            sig=int(r["bullish_signal"])
            if sig==0: continue
            arm=-1 if sig==1 else 1
            rows_arm.extend(arm_cache.get((pd.Timestamp(r["expiry"]).date(),arm), []))
        mm=metrics(pd.DataFrame(rows_arm))
        hold_rows.append({**c,"holdout_net":mm["net"],"holdout_trades":mm["trades"],"holdout_win_rate":mm["win_rate"],"holdout_max_dd":mm["max_dd"]})
    pd.DataFrame(hold_rows).to_csv(ROOT / "holdout_top10.csv", index=False)

    print(json.dumps({"grid_candidates":len(grid_df),"top10":top10,"holdout":hold_rows},indent=2))

if __name__=="__main__":
    main()
