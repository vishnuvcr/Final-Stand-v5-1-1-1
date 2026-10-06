import json, os
from pathlib import Path
import numpy as np
import pandas as pd

import phase39_sequential_policy as p39
from phase39_counterfactual_engine import nearest_delta_strike, run_arm
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, SplineTransformer
from sklearn.linear_model import Ridge
from sklearn.ensemble import ExtraTreesRegressor

ROOT = Path(".")
OUT = ROOT / "results/phase41_regime_policy"
SELECTION = OUT / "selection.json"
CONTROL_DEV = Path("results/phase39_data/development_control_trades_2021_2023.csv")
CONTROL_FROZEN = Path("results/phase39_data/frozen_control_trades_2024_2026-06-30.csv")
FOCUS_FEATURES = [
    "nifty_ret_15m","nifty_ret_60m","nifty_ret_240m","nifty_rv_30m","nifty_rv_120m",
    "nifty_daily_rv_20d","nifty_drawdown_20d","nifty_gap_from_prev_close",
    "atm_iv_skew","atm_pcr_oi","atm_pcr_volume","candidate_iv_skew_25",
    "candidate_credit_diff_call_minus_put","global_SP500_ret1","global_NASDAQ_ret1",
    "global_NIKKEI_ret1","global_USDINR_ret1","global_GOLD_ret1","global_CRUDE_ret1",
    "flow_fii_net_z20","flow_dii_net_z20","flow_flow_sentiment"
]
TZ = p39.TZ
WARMUP = 100
UNCERTAINTY_WINDOW = 60
UNCERTAINTY_Z = 1.0
WIDTH = 50.0
BOOT = 10000

def load_vix():
    v = pd.read_csv("data/phase40_vix/india_vix.csv")
    v["date"] = pd.to_datetime(v["date"]).dt.normalize()
    v["close"] = pd.to_numeric(v["close"], errors="coerce")
    v = v.dropna(subset=["date","close"]).sort_values("date").drop_duplicates("date", keep="last")
    v["ret1"] = v["close"].pct_change()
    return v

def prior_vix(v, ts):
    d = pd.Timestamp(ts).tz_localize(None).normalize()
    j = v[v["date"] < d]
    if j.empty:
        return np.nan, np.nan
    r = j.iloc[-1]
    return float(r["close"]), (float(r["ret1"]) if pd.notna(r["ret1"]) else np.nan)

def enrich_row(entry, expiry, snap, spot_value, spot_hist, daily, global_d, flows, sentiment,
               option_cache, expiries, vix, high_thr, rise_thr):
    row = p39.build_feature_row(entry, expiry, snap, spot_value, spot_hist, daily, global_d, flows,
                                sentiment, option_cache, expiries)
    level, ret1 = prior_vix(vix, entry)
    row["india_vix_level"] = level
    row["india_vix_ret1"] = ret1
    row["india_vix_high"] = int(np.isfinite(level) and level >= high_thr)
    row["india_vix_rising"] = int(np.isfinite(ret1) and ret1 >= rise_thr)
    row["india_vix_high_rising"] = int(row["india_vix_high"] and row["india_vix_rising"])
    return row

def model(name):
    if name == "SPLINE_RIDGE_VIX":
        return Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("spline", SplineTransformer(n_knots=4, degree=2, include_bias=False)),
            ("ridge", Ridge(alpha=10.0))
        ])
    if name == "EXTRATREES_VIX":
        return Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("model", ExtraTreesRegressor(n_estimators=150, max_depth=5, min_samples_leaf=8,
                                          random_state=4101, n_jobs=2))
        ])
    raise ValueError(name)

def Xify(frame):
    # Live point-in-time feature construction can legitimately leave some
    # auxiliary sources unavailable. Reindexing preserves the fixed feature
    # schema and lets the registered imputer handle missing values.
    x = frame.reindex(columns=FOCUS_FEATURES).copy()
    for c in ["india_vix_level","india_vix_ret1","india_vix_high","india_vix_rising","india_vix_high_rising"]:
        x[c] = frame[c].to_numpy() if c in frame.columns else np.nan
    for c in FOCUS_FEATURES:
        x[f"HIGHx_{c}"] = x[c].to_numpy() * x["india_vix_high"].to_numpy()
    return x

def scale_uncertainty(residuals):
    x = np.asarray(residuals[-UNCERTAINTY_WINDOW:], dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < 10:
        return 500.0
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    return float(max(1.4826 * mad, 50.0))

def gate_ok(fr, gate):
    if gate == "ALL":
        return True
    if gate == "HIGH_VIX":
        return bool(fr["india_vix_high"])
    if gate == "HIGH_VIX_RISING":
        return bool(fr["india_vix_high_rising"])
    raise ValueError(gate)

def shadow_direction(control, ts):
    i = control["entry_ts"].searchsorted(ts, side="right") - 1
    return str(control.iloc[i]["direction"]) if i >= 0 else "CALL"

def paired_bootstrap(policy, control, seed):
    p = policy.groupby("expiry")["policy_net_rupees"].sum()
    c = control.groupby("expiry")["net_rupees"].sum()
    keys = sorted(set(p.index).intersection(c.index))
    d = np.asarray([p[k] - c[k] for k in keys], dtype=float)
    if len(d) == 0:
        return {"n":0}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(BOOT, len(d)))
    means = d[idx].mean(axis=1)
    signs = rng.choice([-1.0,1.0], size=(BOOT, len(d)))
    null = (d * signs).mean(axis=1)
    obs = float(d.mean())
    return {
        "n":int(len(d)), "mean_uplift_per_expiry":obs, "total_uplift":float(d.sum()),
        "ci_mean_low":float(np.quantile(means,.025)),
        "ci_mean_high":float(np.quantile(means,.975)),
        "ci_total_low":float(np.quantile(means*len(d),.025)),
        "ci_total_high":float(np.quantile(means*len(d),.975)),
        "p_one_sided":float((np.sum(null>=obs)+1)/(BOOT+1)),
        "positive_expiry_share":float(np.mean(d>0)),
        "positive_expiries":int(np.sum(d>0))
    }

def drawdown(x):
    a = np.asarray(x, float)
    if len(a) == 0:
        return 0.0
    eq = np.cumsum(a)
    return float((np.maximum.accumulate(np.r_[0.0, eq])[1:] - eq).max())

def cost_stress(policy, control, mult):
    pg = float(policy["gross_rupees"].sum())
    pc = float(policy["cost_rupees"].sum())
    if {"gross_rupees","cost_rupees"}.issubset(control.columns):
        cg = float(control["gross_rupees"].sum())
        cc = float(control["cost_rupees"].sum())
        return (pg - mult*pc) - (cg - mult*cc)
    return np.nan

def run_candidate(cand, spot, daily, global_d, flows, sentiment, vix, expected_all, option_cache_base, control):
    model_name = cand["model"]
    margin = float(cand["margin"])
    gate = str(cand["gate"])
    high_thr = float(vix.loc[vix["date"] < pd.Timestamp("2024-01-01"),"close"].quantile(.67))
    rise_thr = float(vix.loc[vix["date"] < pd.Timestamp("2024-01-01"),"ret1"].abs().quantile(.67))
    history = []
    trades = []
    option_cache = dict(option_cache_base)

    def get_option(expiry):
        if expiry not in option_cache:
            d = p39.load_option(expiry)
            d["expiry_ts"] = expiry + pd.Timedelta(hours=15, minutes=30)
            option_cache[expiry] = d
        return option_cache[expiry]

    for expiry in expected_all:
        od = get_option(expiry)
        expiry_day = expiry.normalize()
        end_ts = expiry + pd.Timedelta(hours=15, minutes=29)
        idx_exp = expected_all.index(expiry)
        window_start = (expected_all[idx_exp-1] + pd.Timedelta(hours=15, minutes=30)) if idx_exp > 0 else p39.START
        timeline = spot[(spot.timestamp > window_start) & (spot.timestamp <= end_ts)].copy()
        timeline = timeline[timeline.timestamp < expiry_day].sort_values("timestamp").reset_index(drop=True)
        cursor = 0
        while cursor < len(timeline):
            entry = p39.norm_scalar_ts(timeline.iloc[cursor].timestamp)
            if entry.normalize() == expiry_day:
                break
            if entry.hour < 9 or (entry.hour == 9 and entry.minute < 20):
                cursor += 1
                continue
            if entry.hour > 15 or (entry.hour == 15 and entry.minute >= 28):
                cursor += 1
                continue
            snap = od[od.timestamp == entry]
            sr = spot[spot.timestamp == entry]
            if snap.empty or sr.empty:
                cursor += 1
                continue
            s = float(sr.iloc[0]["close"])
            shadow = shadow_direction(control, entry)
            fr = enrich_row(entry, expiry, snap, s, spot, daily, global_d, flows, sentiment,
                            option_cache, expected_all, vix, high_thr, rise_thr)
            fdf = pd.DataFrame([fr])

            if len(history) < WARMUP:
                action = shadow
                pred = np.nan
                unc = np.nan
                score = np.nan
                override = False
            else:
                hist = pd.DataFrame(history)
                m = model(model_name)
                m.fit(Xify(hist), hist["delta_pnl"].to_numpy(float))
                pred = float(m.predict(Xify(fdf))[0])
                fitted = np.asarray(m.predict(Xify(hist)), dtype=float)
                resid = hist["delta_pnl"].to_numpy(float) - fitted
                unc = scale_uncertainty(resid)
                benefit = (-pred) if shadow == "CALL" else pred
                score = benefit - UNCERTAINTY_Z * unc
                override = bool(gate_ok(fr, gate) and score > margin)
                action = ("PUT" if shadow == "CALL" else "CALL") if override else shadow

            typ = "CE" if action == "CALL" else "PE"
            target = 0.25 if typ == "CE" else -0.25
            chosen = nearest_delta_strike(snap, s, entry, typ, target)
            if chosen is None:
                cursor += 1
                continue
            short_k, _ = chosen
            long_k = short_k + WIDTH if typ == "CE" else short_k - WIDTH
            arm = run_arm(od, spot, entry, expiry, typ, short_k, long_k, p39.lot_size_for_expiry(expiry))

            alt_typ = "PE" if typ == "CE" else "CE"
            alt_target = -0.25 if alt_typ == "PE" else 0.25
            alt_sel = nearest_delta_strike(snap, s, entry, alt_typ, alt_target)
            if alt_sel is None:
                cursor += 1
                continue
            alt_k, _ = alt_sel
            alt_long_k = alt_k - WIDTH if alt_typ == "PE" else alt_k + WIDTH
            alt = run_arm(od, spot, entry, expiry, alt_typ, alt_k, alt_long_k, p39.lot_size_for_expiry(expiry))

            call_put_delta = float(arm["net_rupees"] - alt["net_rupees"]) if action == "CALL" else float(alt["net_rupees"] - arm["net_rupees"])
            true_delta_call_minus_put = float(arm["net_rupees"] - alt["net_rupees"]) if action == "CALL" else float(alt["net_rupees"] - arm["net_rupees"])

            trades.append({
                "entry_ts":str(entry), "expiry":str(expiry.date()),
                "shadow_control":shadow, "action":action, "override":bool(override),
                "pred_delta":pred, "uncertainty":unc, "override_score":score,
                "policy_net_rupees":float(arm["net_rupees"]),
                "gross_rupees":float(arm["gross_rupees"]),
                "cost_rupees":float(arm["cost_rupees"]),
                "call_put_delta":true_delta_call_minus_put,
                "exit_ts":str(arm["exit_ts"]), "exit_reason":arm["exit_reason"],
                "short_strike":float(short_k), "long_strike":float(long_k),
                "lot_size":int(p39.lot_size_for_expiry(expiry))
            })

            history_row = {k:fr.get(k,np.nan) for k in FOCUS_FEATURES}
            history_row.update({
                "india_vix_level":fr["india_vix_level"],
                "india_vix_ret1":fr["india_vix_ret1"],
                "india_vix_high":fr["india_vix_high"],
                "india_vix_rising":fr["india_vix_rising"],
                "india_vix_high_rising":fr["india_vix_high_rising"],
                "delta_pnl":float(arm["net_rupees"] - alt["net_rupees"]) if action == "CALL" else float(alt["net_rupees"] - arm["net_rupees"])
            })
            history.append(history_row)

            exit_ts = p39.norm_scalar_ts(arm["exit_ts"])
            nxt = np.flatnonzero(timeline.timestamp.to_numpy() == exit_ts)
            if len(nxt) == 0:
                break
            cursor = int(nxt[0]) + 1

    t = pd.DataFrame(trades)
    if t.empty:
        raise RuntimeError("candidate produced zero sequential trades")
    t["entry_ts"] = p39.norm_ts(t["entry_ts"])
    t["exit_ts"] = p39.norm_ts(t["exit_ts"])
    t["expiry_dt"] = pd.to_datetime(t["expiry"]).dt.tz_localize(TZ)
    t["period"] = np.where(t["expiry_dt"].dt.year <= 2023, "development",
                           np.where(t["expiry_dt"].dt.year <= 2025, "validation", "holdout"))
    return t

def main():
    selection = json.load(open(SELECTION))
    candidates = selection["top3_frozen_before_holdout"]
    if not candidates:
        raise RuntimeError("No frozen candidate list")
    vix = load_vix()
    spot = p39.load_spot()
    daily = p39.load_daily_source("nifty_daily.parquet")
    global_d = p39.load_daily_source("global_daily.parquet")
    flows = p39.load_daily_source("fii_dii_daily.parquet")
    sentiment = p39.load_daily_source("sentiment_daily.parquet")
    expected_all = p39.expected_expiries(spot)

    from huggingface_hub import HfApi
    api = HfApi(token=os.getenv("HF_TOKEN") or None)
    repo_files = set(api.list_repo_files(p39.HF_REPO, repo_type="dataset"))
    expected_all = [e for e in expected_all if f"options/NIFTY/{e.strftime('%Y-%m-%d')}.parquet" in repo_files]
    option_cache_base = {}

    control = pd.concat([pd.read_csv(CONTROL_DEV).assign(period="development"),
                         pd.read_csv(CONTROL_FROZEN)], ignore_index=True)
    control["entry_ts"] = p39.norm_ts(control["entry_ts"])
    control["expiry_dt"] = pd.to_datetime(control["expiry"]).dt.tz_localize(TZ)
    control["period"] = np.where(control["expiry_dt"].dt.year <= 2023, "development",
                                 np.where(control["expiry_dt"].dt.year <= 2025, "validation", "holdout"))

    summaries = []
    for rank, cand in enumerate(candidates, 1):
        print(f"Running frozen candidate rank {rank}: {cand}", flush=True)
        t = run_candidate(cand, spot, daily, global_d, flows, sentiment, vix,
                          expected_all, option_cache_base, control)
        t.to_csv(OUT/f"sequential_candidate_{rank}.csv", index=False)

        for per in ["development","validation","holdout"]:
            a = t[t.period == per].copy()
            c = control[control.period == per].copy()
            boot = paired_bootstrap(a, c, 5100 + rank)
            row = {
                "rank":rank, "model":cand["model"], "margin":float(cand["margin"]), "gate":cand["gate"],
                "period":per, "policy_trades":int(len(a)), "control_trades":int(len(c)),
                "policy_net_rupees":float(a.policy_net_rupees.sum()),
                "control_net_rupees":float(c.net_rupees.sum()),
                "uplift_rupees":float(a.policy_net_rupees.sum()-c.net_rupees.sum()),
                "overrides":int(a.override.sum()),
                "override_rate":float(a.override.mean()) if len(a) else 0.0,
                "policy_drawdown_rupees":drawdown(a.policy_net_rupees),
                "control_drawdown_rupees":drawdown(c.net_rupees),
                "uplift_concentration_max_expiry":float((a.groupby("expiry").policy_net_rupees.sum()-c.groupby("expiry").net_rupees.sum()).abs().max()) if len(a) else 0.0
            }
            row.update({f"boot_{k}":v for k,v in boot.items()})
            for mult in [1.25,1.5,2.0]:
                row[f"cost_stress_{int(mult*100)}pct_uplift"] = cost_stress(a,c,mult)
            summaries.append(row)

    s = pd.DataFrame(summaries)
    s.to_csv(OUT/"sequential_summary.csv", index=False)
    (OUT/"sequential_summary.json").write_text(json.dumps(
        {"status":"SEQUENTIAL_COMPLETE","candidates":candidates},
        indent=2, default=str
    ))
    (ROOT/"PHASE41_STATUS.md").write_text(
        "# Phase 41 Status — Regime-Conditional Counterfactual Policy Learning\n\n"
        "**STEP 2 COMPLETE — EXACT SEQUENTIAL REPLAY FINISHED**\n\n"
        "The frozen top three candidates were replayed through the exact chronological engine. "
        "Cost stress and paired-expiry inference were also calculated.\n\n"
        "Final closeout and promotion decision are next.\n"
    )
    print(s.to_string(index=False))

if __name__ == "__main__":
    main()
