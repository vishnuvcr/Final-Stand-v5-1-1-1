import json
from pathlib import Path
import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, SplineTransformer
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.ensemble import ExtraTreesRegressor

ROOT = Path(".")
LEDGER = ROOT / "results/phase39_counterfactual/fixed_opportunity_ledger.csv"
FEATURES = ROOT / "results/phase39_features/point_in_time_features.csv"
VIX_FILE = ROOT / "data/phase40_vix/india_vix.csv"
OUT = ROOT / "results/phase41_regime_policy"
OUT.mkdir(parents=True, exist_ok=True)

FOCUS_FEATURES = [
    "nifty_ret_15m","nifty_ret_60m","nifty_ret_240m","nifty_rv_30m","nifty_rv_120m",
    "nifty_daily_rv_20d","nifty_drawdown_20d","nifty_gap_from_prev_close",
    "atm_iv_skew","atm_pcr_oi","atm_pcr_volume","candidate_iv_skew_25",
    "candidate_credit_diff_call_minus_put","global_SP500_ret1","global_NASDAQ_ret1",
    "global_NIKKEI_ret1","global_USDINR_ret1","global_GOLD_ret1","global_CRUDE_ret1",
    "flow_fii_net_z20","flow_dii_net_z20","flow_flow_sentiment"
]
STATE_FEATURES = [
    "india_vix_level","india_vix_ret1","india_vix_high","india_vix_rising",
    "global_VIX","global_VIX_ret1","nifty_daily_rv_20d","nifty_gap_from_prev_close",
    "atm_iv_skew","atm_pcr_oi"
]
MODELS = ["SPLINE_RIDGE_VIX","EXTRATREES_VIX"]
MARGINS = [0.0, 250.0, 500.0, 1000.0]
GATES = ["ALL","HIGH_VIX","HIGH_VIX_RISING"]
WARMUP = 100
UNCERTAINTY_WINDOW = 60
UNCERTAINTY_Z = 1.0
BOOT = 10000

def load():
    ledger = pd.read_csv(LEDGER)
    feat = pd.read_csv(FEATURES)
    for df in (ledger, feat):
        df["entry_ts"] = pd.to_datetime(df["entry_ts"], utc=True).dt.tz_convert("Asia/Kolkata")
    ledger = ledger.sort_values("entry_ts").reset_index(drop=True)
    feat = feat.sort_values("entry_ts").reset_index(drop=True)
    dropf = [c for c in ["split","control_direction","control_net_rupees","delta_pnl_call_minus_put"] if c in feat.columns]
    z = ledger.merge(feat.drop(columns=dropf), on=["entry_ts","expiry"], how="inner", suffixes=("","_feat"))
    assert len(z) == 477, f"expected 477 merged rows, got {len(z)}"
    assert z["delta_pnl_call_minus_put"].notna().all()
    v = pd.read_csv(VIX_FILE)
    v["date"] = pd.to_datetime(v["date"]).dt.normalize()
    v["close"] = pd.to_numeric(v["close"], errors="coerce")
    v = v.dropna(subset=["date","close"]).sort_values("date").drop_duplicates("date", keep="last")
    v["ret1"] = v["close"].pct_change()
    entry_dates = pd.to_datetime(z["entry_ts"]).dt.tz_localize(None).dt.normalize()
    vals = []
    for d in entry_dates:
        prior = v.loc[v["date"] < d]
        vals.append(prior.iloc[-1] if len(prior) else pd.Series({"close":np.nan,"ret1":np.nan}))
    vv = pd.DataFrame(vals).reset_index(drop=True)
    z["india_vix_level"] = pd.to_numeric(vv["close"], errors="coerce").to_numpy()
    z["india_vix_ret1"] = pd.to_numeric(vv["ret1"], errors="coerce").to_numpy()
    dev_vix = v.loc[v["date"] < pd.Timestamp("2024-01-01")]
    q67 = float(dev_vix["close"].quantile(.67))
    rq67 = float(dev_vix["ret1"].abs().quantile(.67))
    z["india_vix_high"] = (z["india_vix_level"] >= q67).astype(int)
    z["india_vix_rising"] = (z["india_vix_ret1"] >= rq67).astype(int)
    z["india_vix_high_rising"] = ((z["india_vix_high"] == 1) & (z["india_vix_rising"] == 1)).astype(int)
    z = z.sort_values("entry_ts").reset_index(drop=True)
    return z, {"vix_q67":q67, "vix_absret_q67":rq67}

def add_vix_features(df):
    missing = [c for c in FOCUS_FEATURES if c not in df.columns]
    assert not missing, f"missing pre-registered features: {missing}"
    X = df[FOCUS_FEATURES].copy()
    for c in ["india_vix_level","india_vix_ret1","india_vix_high","india_vix_rising","india_vix_high_rising"]:
        X[c] = df[c].to_numpy()
    for c in FOCUS_FEATURES:
        X[f"HIGHx_{c}"] = X[c].to_numpy() * X["india_vix_high"].to_numpy()
    return X

def build_model(name):
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
            ("model", ExtraTreesRegressor(
                n_estimators=150, max_depth=5, min_samples_leaf=8,
                random_state=4101, n_jobs=2
            ))
        ])
    raise ValueError(name)

def uncertainty_scale(residuals):
    x = np.asarray(residuals[-UNCERTAINTY_WINDOW:], dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < 10:
        return 500.0
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    return float(max(1.4826 * mad, 50.0))

def gate_ok(row, gate):
    if gate == "ALL":
        return True
    if gate == "HIGH_VIX":
        return bool(row["india_vix_high"])
    if gate == "HIGH_VIX_RISING":
        return bool(row["india_vix_high_rising"])
    raise ValueError(gate)

def expanding_predictions(z, model_name):
    preds = np.full(len(z), np.nan)
    uncs = np.full(len(z), np.nan)
    y = z["delta_pnl_call_minus_put"].to_numpy(float)
    Xall = add_vix_features(z)
    for i in range(len(z)):
        if i < WARMUP:
            continue
        idx = np.arange(i)
        model = build_model(model_name)
        model.fit(Xall.iloc[idx], y[idx])
        pred = float(model.predict(Xall.iloc[[i]])[0])
        fitted = np.asarray(model.predict(Xall.iloc[idx]), dtype=float)
        resid = y[idx] - fitted
        preds[i] = pred
        uncs[i] = uncertainty_scale(resid)
    return preds, uncs

def policy_from_predictions(z, preds, uncs, margin, gate):
    control = z["control_direction"].astype(str).to_numpy()
    call = z["call_net_rupees"].to_numpy(float)
    put = z["put_net_rupees"].to_numpy(float)
    ctl = z["control_net_rupees"].to_numpy(float)
    alt = np.where(control == "CALL", put, call)
    benefit = np.where(control == "CALL", -preds, preds)
    score = benefit - UNCERTAINTY_Z * uncs
    allowed = np.array([gate_ok(r, gate) for _, r in z.iterrows()])
    override = np.isfinite(score) & allowed & (score > margin)
    net = np.where(override, alt, ctl)
    cols = {
        "entry_ts":z["entry_ts"], "expiry":z["expiry"], "split":z["split"],
        "control_direction":z["control_direction"], "control_net_rupees":ctl,
        "alt_net_rupees":alt, "delta_pnl":z["delta_pnl_call_minus_put"],
        "pred_delta":preds, "uncertainty":uncs, "override_score":score,
        "override":override, "policy_net_rupees":net,
        "india_vix_level":z["india_vix_level"], "india_vix_ret1":z["india_vix_ret1"],
        "india_vix_high":z["india_vix_high"], "india_vix_rising":z["india_vix_rising"],
        "india_vix_high_rising":z["india_vix_high_rising"],
        "global_VIX":z["global_VIX"], "global_VIX_ret1":z["global_VIX_ret1"],
        "nifty_daily_rv_20d":z["nifty_daily_rv_20d"],
        "nifty_gap_from_prev_close":z["nifty_gap_from_prev_close"],
        "atm_iv_skew":z["atm_iv_skew"], "atm_pcr_oi":z["atm_pcr_oi"]
    }
    return pd.DataFrame(cols)

def max_dd(x):
    a = np.asarray(x, float)
    eq = np.cumsum(a)
    peak = np.maximum.accumulate(np.r_[0.0, eq])
    return float((peak[1:] - eq).max()) if len(eq) else 0.0

def stats(frame, split):
    d = frame[frame["split"] == split].copy()
    ctl = float(d["control_net_rupees"].sum())
    pol = float(d["policy_net_rupees"].sum())
    return {
        "split":split, "control_net_rupees":ctl, "policy_net_rupees":pol,
        "uplift_rupees":pol-ctl, "overrides":int(d["override"].sum()),
        "override_rate":float(d["override"].mean()) if len(d) else np.nan,
        "policy_max_drawdown_rupees":max_dd(d["policy_net_rupees"]),
        "control_max_drawdown_rupees":max_dd(d["control_net_rupees"])
    }

def bootstrap(diffs, seed):
    x = np.asarray(diffs, float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return {"n":0}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(BOOT, len(x)))
    means = x[idx].mean(axis=1)
    signs = rng.choice([-1.0, 1.0], size=(BOOT, len(x)))
    null = (x * signs).mean(axis=1)
    obs = float(x.mean())
    return {
        "n":int(len(x)), "mean":obs, "total":float(x.sum()),
        "ci_mean_low":float(np.quantile(means,.025)),
        "ci_mean_high":float(np.quantile(means,.975)),
        "ci_total_low":float(np.quantile(means*len(x),.025)),
        "ci_total_high":float(np.quantile(means*len(x),.975)),
        "p_one_sided":float((np.sum(null>=obs)+1)/(BOOT+1)),
        "positive_expiry_share":float(np.mean(x>0))
    }

def expiry_diff(frame, split):
    d = frame[frame["split"] == split].copy()
    d["expiry"] = pd.to_datetime(d["expiry"])
    p = d.groupby("expiry")["policy_net_rupees"].sum()
    c = d.groupby("expiry")["control_net_rupees"].sum()
    common = p.index.intersection(c.index)
    return (p.loc[common] - c.loc[common]).to_numpy(float)

def propensity_match(sc, split):
    d = sc[sc["split"] == split].copy()
    if d.empty or d["override"].sum() == 0:
        return {"split":split, "treated":0, "matched":0, "att":None}
    cols = [c for c in STATE_FEATURES if c in d.columns]
    X = d[cols].replace([np.inf,-np.inf], np.nan)
    X = X.fillna(X.median(numeric_only=True)).fillna(0.0)
    t = d["override"].astype(int).to_numpy()
    if t.sum() < 2 or (t == 0).sum() < 5:
        return {"split":split, "treated":int(t.sum()), "matched":0, "att":None, "common_support_fraction":0.0}
    scaler = StandardScaler().fit(X)
    lr = LogisticRegression(max_iter=2000, class_weight="balanced").fit(scaler.transform(X), t)
    ps = lr.predict_proba(scaler.transform(X))[:,1]
    d["ps"] = ps
    high = d["india_vix_high"].astype(int).to_numpy()
    treated = np.where(t == 1)[0]
    controls = np.where(t == 0)[0]
    used = set()
    diffs = []
    for i in treated:
        pool = [j for j in controls if j not in used and high[j] == high[i]]
        if not pool:
            continue
        j = min(pool, key=lambda k: abs(d.iloc[k]["ps"] - d.iloc[i]["ps"]))
        if abs(d.iloc[j]["ps"] - d.iloc[i]["ps"]) <= 0.05:
            diffs.append(float(d.iloc[i]["delta_pnl"] - d.iloc[j]["delta_pnl"]))
            used.add(j)
    if not diffs:
        return {"split":split, "treated":int(len(treated)), "matched":0, "att":None, "common_support_fraction":0.0}
    x = np.asarray(diffs, float)
    rng = np.random.default_rng(41041)
    sims = rng.choice(x, size=(10000, len(x)), replace=True).mean(axis=1)
    return {
        "split":split, "treated":int(len(treated)), "matched":int(len(diffs)),
        "att":float(x.mean()), "ci_lo":float(np.quantile(sims,.025)),
        "ci_hi":float(np.quantile(sims,.975)),
        "common_support_fraction":float(len(diffs)/len(treated))
    }

def ranking_diag(sc, split):
    d = sc[sc["split"] == split].copy()
    d = d[np.isfinite(d["override_score"])].sort_values("override_score", ascending=False)
    out = {"split":split, "rows":int(len(d))}
    for frac in (0.10,0.20,0.30):
        n = max(1, int(np.ceil(frac * len(d))))
        top = d.head(n)
        out[f"top_{int(frac*100)}_mean_delta"] = float(top["delta_pnl"].mean())
        out[f"top_{int(frac*100)}_positive_share"] = float((top["delta_pnl"] > 0).mean())
    return out

def main():
    z, thr = load()
    declared = len(MODELS) * len(MARGINS) * len(GATES)
    assert declared == 24
    screen = z[z["split"].isin(["development","validation"])].copy().reset_index(drop=True)
    grid_rows = []
    pred_cache = {}
    for model_name in MODELS:
        p, u = expanding_predictions(screen, model_name)
        pred_cache[model_name] = (p, u)
        for margin in MARGINS:
            for gate in GATES:
                pol = policy_from_predictions(screen, p, u, margin, gate)
                a = stats(pol, "development")
                b = stats(pol, "validation")
                grid_rows.append({
                    "model":model_name, "margin":margin, "gate":gate,
                    "development_uplift":a["uplift_rupees"],
                    "validation_uplift":b["uplift_rupees"],
                    "development_overrides":a["overrides"],
                    "validation_overrides":b["overrides"],
                    "validation_override_rate":b["override_rate"],
                    "validation_policy_dd":b["policy_max_drawdown_rupees"],
                    "validation_control_dd":b["control_max_drawdown_rupees"]
                })
    grid = pd.DataFrame(grid_rows).sort_values(["validation_uplift","development_uplift"], ascending=False).reset_index(drop=True)
    grid.to_csv(OUT/"fixed_grid_validation.csv", index=False)
    eligible = grid[
        (grid.development_uplift >= 0) &
        (grid.validation_uplift > 0) &
        (grid.validation_overrides >= 5) &
        (grid.validation_override_rate <= 0.25) &
        (grid.validation_policy_dd <= 1.25 * grid.validation_control_dd)
    ]
    top = eligible.head(3).copy()
    fallback_reason = ""
    if top.empty:
        top = grid.head(3).copy()
        fallback_reason = "No variant passed the registered development/validation safety screen; top three validation variants are diagnostic only."
    selected = top.to_dict(orient="records")

    z_predictions = {}
    diag_frames = []
    for rec in selected:
        mname = rec["model"]
        if mname not in z_predictions:
            z_predictions[mname] = expanding_predictions(z, mname)
        p,u = z_predictions[mname]
        pol = policy_from_predictions(z, p, u, float(rec["margin"]), str(rec["gate"]))
        diag_frames.append(pol)

    if diag_frames:
        leading = diag_frames[0]
        for split in ["validation","holdout"]:
            pm = propensity_match(leading, split)
            rk = ranking_diag(leading, split)
            (OUT/f"diagnostics_{split}.json").write_text(json.dumps({
                "model":selected[0]["model"], "margin":selected[0]["margin"], "gate":selected[0]["gate"],
                "propensity":pm, "ranking":rk
            }, indent=2, default=str))

    fixed_results = []
    for rank, rec in enumerate(selected, 1):
        p,u = z_predictions[rec["model"]]
        pol = policy_from_predictions(z, p, u, float(rec["margin"]), str(rec["gate"]))
        for split in ["development","validation","holdout"]:
            st = stats(pol, split)
            boot = bootstrap(expiry_diff(pol, split), 4100 + rank)
            fixed_results.append({"rank":rank, **rec, **st, **{f"boot_{k}":v for k,v in boot.items()}})
        if rank == 1:
            pol.to_csv(OUT/"leading_policy_fixed_ledger.csv", index=False)

    pd.DataFrame(fixed_results).to_csv(OUT/"frozen_top3_fixed_results.csv", index=False)
    selection = {
        "declared_variants":declared,
        "selection_gate":"development>=0, validation>0, validation_overrides>=5, validation_override_rate<=25%, validation_dd<=1.25x control",
        "eligible_count":int(len(eligible)),
        "fallback_reason":fallback_reason,
        "top3_frozen_before_holdout":selected,
        "vix_thresholds":thr
    }
    (OUT/"selection.json").write_text(json.dumps(selection, indent=2, default=str))
    (ROOT/"PHASE41_STATUS.md").write_text(
        "# Phase 41 Status — Regime-Conditional Counterfactual Policy Learning\n\n"
        "**STEP 1 COMPLETE — TOP 3 FROZEN; EXACT SEQUENTIAL REPLAY NEXT**\n\n"
        f"Declared variants: {declared}. Validation-eligible variants: {len(eligible)}.\n\n"
        f"{fallback_reason}\n\n"
        "The top three candidates are frozen using development/validation criteria only. "
        "The exact sequential replay is next.\n"
    )
    print(json.dumps(selection, indent=2, default=str))

if __name__ == "__main__":
    main()
