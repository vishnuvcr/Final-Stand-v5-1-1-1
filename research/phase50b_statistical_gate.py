"""
Phase 50B statistical gate.

Execution-only after source-faithful strategy artifacts pass feasibility.
No candidate tuning is performed here.

For each available Phase-50B trade table:
- compares preregistered VIX regime subset vs complementary observations;
- computes mean-difference bootstrap CI;
- computes two-sided randomization/permutation p-value;
- applies Holm correction across all tested strategy × regime hypotheses;
- reports development/validation/holdout splits without selecting on holdout.

The script is intentionally generic and consumes only persisted result CSVs.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path("results/phase50b/statistical_gate")
OUT.mkdir(parents=True, exist_ok=True)

MODES = ["LOW","NORMAL","HIGH","SPIKE","FALLING","RISING","HIGH_RISING"]
SPLITS = {"DEV": lambda d: d <= pd.Timestamp("2023-12-31"),
          "VAL": lambda d: (d > pd.Timestamp("2023-12-31")) & (d <= pd.Timestamp("2025-12-31")),
          "HOLD": lambda d: d > pd.Timestamp("2025-12-31")}

def bootstrap_diff(a, b, seed=505001, n=10000):
    a=np.asarray(a,dtype=float); b=np.asarray(b,dtype=float)
    a=a[np.isfinite(a)]; b=b[np.isfinite(b)]
    if len(a)<10 or len(b)<10:
        return {"n_regime":int(len(a)),"n_complement":int(len(b)),
                "mean_diff":np.nan,"ci_lo":np.nan,"ci_hi":np.nan,"p_perm":np.nan}
    rng=np.random.default_rng(seed)
    ia=rng.integers(0,len(a),size=(n,len(a)))
    ib=rng.integers(0,len(b),size=(n,len(b)))
    diffs=a[ia].mean(axis=1)-b[ib].mean(axis=1)
    pooled=np.concatenate([a,b])
    ge=0
    obs=float(a.mean()-b.mean())
    for _ in range(n):
        perm=rng.permutation(pooled)
        stat=perm[:len(a)].mean()-perm[len(a):].mean()
        if abs(stat)>=abs(obs): ge+=1
    return {"n_regime":int(len(a)),"n_complement":int(len(b)),
            "mean_diff":obs,"ci_lo":float(np.quantile(diffs,0.025)),
            "ci_hi":float(np.quantile(diffs,0.975)),
            "p_perm":float((ge+1)/(n+1))}

def holm(p):
    p=np.asarray(p,dtype=float)
    out=np.ones(len(p))
    order=np.argsort(p)
    running=0.0
    m=len(p)
    for rank,i in enumerate(order):
        running=max(running,min(1.0,(m-rank)*p[i]))
        out[i]=running
    return out

def load_strategy_csv(path):
    if not path.exists():
        return pd.DataFrame()
    z=pd.read_csv(path)
    if z.empty:
        return z
    date_col=next((c for c in ["expiry","entry_ts","date"] if c in z.columns),None)
    if date_col is None:
        raise ValueError(f"{path}: no chronology column")
    z["_date"]=pd.to_datetime(z[date_col],errors="coerce")
    if z["_date"].dt.tz is not None:
        z["_date"]=z["_date"].dt.tz_localize(None)
    required={"net","net50","net20","net20_50"}
    missing=required-set(z.columns)
    if missing:
        raise ValueError(f"{path}: missing required cost fields {sorted(missing)}; fail closed")
    return z.dropna(subset=["_date","net","net50"]).copy()

STRATEGIES = {
    "TT01": Path("results/phase50b/tt01_dynamic_ratio_replay/tt01_trades.csv"),
    "TT02": Path("results/phase50b/tt02_calendar_replay/tt02_trades.csv"),
    "TT03": Path("results/phase50b/tt03_dynamic_n_replay/tt03_trades.csv"),
    "TT04": Path("results/phase50b/tt04_premium_match_replay/tt04_trades.csv"),
    "TT05": Path("results/phase50b/tt05_short_straddle_replay/tt05_trades.csv"),
    "TT06": Path("results/phase50b/tt06_intraday_asym_replay/tt06_trades.csv"),
    "TT07": Path("results/phase50b/tt07_dynamic_ic_ratio_replay/tt07_trades.csv"),
}

rows=[]
coverage_rows=[]
for strategy,path in STRATEGIES.items():
    z=load_strategy_csv(path)
    if z.empty: continue
    summary_path=path.parent/"summary.json"
    coverage=np.nan
    if summary_path.exists():
        s=json.loads(summary_path.read_text())
        coverage=float(s.get("coverage_rate",np.nan))
    coverage_rows.append({"strategy":strategy,"coverage_rate":coverage})
    if "vix_state" not in z.columns:
        continue
    # Protect the 2026 holdout from inferential hypothesis testing.
    # The registered inference universe is pre-holdout DEV+VAL only.
    infer_z=z[z["_date"]<=pd.Timestamp("2025-12-31")].copy()
    for mode in MODES:
        regime=infer_z[infer_z.vix_state.astype(str)==mode]
        complement=infer_z[infer_z.vix_state.astype(str)!=mode]
        r=bootstrap_diff(regime.net.values,complement.net.values,seed=505001+len(rows))
        r.update({"strategy":strategy,"vix_mode":mode,"inference_sample":"DEV+VAL","holdout_excluded":True,
                  "regime_cost50_mean":float(regime.net50.mean()) if len(regime) else np.nan,
                  "complement_cost50_mean":float(complement.net50.mean()) if len(complement) else np.nan,
                  "regime_current20_mean":float(regime.net20.mean()) if len(regime) else np.nan,
                  "complement_current20_mean":float(complement.net20.mean()) if len(complement) else np.nan,
                  "regime_current20_stress_mean":float(regime.net20_50.mean()) if len(regime) else np.nan,
                  "complement_current20_stress_mean":float(complement.net20_50.mean()) if len(complement) else np.nan})
        rows.append(r)

inf=pd.DataFrame(rows)
if len(inf):
    inf["p_holm"]=holm(inf.p_perm.fillna(1.0).to_numpy())
    inf["robust_positive"]=(inf.p_holm<0.05)&(inf.mean_diff>0)&(inf.ci_lo>0)
else:
    inf=pd.DataFrame(columns=["strategy","vix_mode","n_regime","n_complement","mean_diff","ci_lo","ci_hi","p_perm","p_holm","robust_positive"])
inf.to_csv(OUT/"vix_regime_inference.csv",index=False)
pd.DataFrame(coverage_rows).to_csv(OUT/"coverage_summary.csv",index=False)

split_rows=[]
for strategy,path in STRATEGIES.items():
    z=load_strategy_csv(path)
    if z.empty: continue
    for split,fn in SPLITS.items():
        q=z[fn(z["_date"])]
        split_rows.append({"strategy":strategy,"split":split,"trades":len(q),
                           "net":float(q.net.sum()) if len(q) else 0.0,
                           "net50":float(q.net50.sum()) if len(q) else 0.0,
                           "net20":float(q.net20.sum()) if len(q) else 0.0,
                           "net20_50":float(q.net20_50.sum()) if len(q) else 0.0,
                           "mean":float(q.net.mean()) if len(q) else np.nan,
                           "win_rate":float((q.net>0).mean()) if len(q) else np.nan})
pd.DataFrame(split_rows).to_csv(OUT/"chronological_summary.csv",index=False)

summary={
    "hypotheses_tested":int(len(inf)),
    "holm_positive":int(inf.robust_positive.sum()) if len(inf) else 0,
    "promotion_requires": [
        "positive validation net",
        "positive +50% cost-stress validation net",
        ">=95% execution coverage",
        "Holm-adjusted regime effect with bootstrap CI above zero",
        "protected 2026 holdout confirmation"
    ],
    "holdout_is_protected":True,
    "inference_excludes_holdout":True,
    "inference_sample":"DEV+VAL only",
    "cost_fields_fail_closed":True,
    "registered_strategies":list(STRATEGIES.keys())
}
(OUT/"summary.json").write_text(json.dumps(summary,indent=2))
