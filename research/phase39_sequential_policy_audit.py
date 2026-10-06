import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(".")
POLICY=ROOT/"results/phase39_sequential_policy/sequential_trades.csv"
SUMMARY=ROOT/"results/phase39_sequential_policy/summary.json"
CONTROL_DEV=ROOT/"results/phase39_data/development_control_trades_2021_2023.csv"
CONTROL_FROZEN=ROOT/"results/phase39_data/frozen_control_trades_2024_2026-06-30.csv"
OUT=ROOT/"results/phase39_sequential_policy_audit"
OUT.mkdir(parents=True,exist_ok=True)

def max_dd(x):
    x=np.asarray(x,float)
    eq=np.cumsum(x); peak=np.maximum.accumulate(np.r_[0.0,eq])
    return float(np.max(peak[1:]-eq)) if len(x) else 0.0

def period_by_expiry(df):
    y=pd.to_datetime(df["expiry"]).dt.year
    return np.where(y<=2023,"development",np.where(y<=2025,"validation","holdout"))

def load():
    p=pd.read_csv(POLICY)
    d=pd.read_csv(CONTROL_DEV); f=pd.read_csv(CONTROL_FROZEN)
    d["period"]="development"
    f["period"]=period_by_expiry(f)
    c=pd.concat([d,f],ignore_index=True)
    return p,c

def main():
    p,c=load()
    p["entry_ts"]=pd.to_datetime(p.entry_ts)
    p["exit_ts"]=pd.to_datetime(p.exit_ts)
    p["period"]=period_by_expiry(p)

    control_counts=c.period.value_counts().to_dict()
    assert control_counts=={"development":271,"validation":172,"holdout":34}
    assert len(c)==477 and c.entry_ts.nunique()==477
    assert len(p)>0 and p.entry_ts.nunique()==len(p)
    assert (p.exit_ts>p.entry_ts).all()
    assert not (p.entry_ts.shift(-1)<p.exit_ts).any(), "Sequential positions overlap"
    assert int(p.override.sum())==7
    assert bool((p.loc[p.override,"pred_delta"].notna()).all())
    assert bool((p.loc[p.override,"pred_unc"].notna()).all())

    # Model predictions must begin only after warm-up and must use uncertainty.
    first_pred=p[p.pred_delta.notna()].iloc[0]
    assert first_pred.entry_ts>=p.entry_ts.iloc[99]
    assert p.iloc[:100].pred_delta.isna().all()
    assert p.iloc[:100].override.eq(False).all()

    # Canonical control audit.
    control_base=float(c.net_rupees.sum())
    frozen_base=float(c[c.period.isin(["validation","holdout"])].net_rupees.sum())
    expected=63672.57530171223
    assert abs(frozen_base-expected)<1e-6

    results=[]
    for period in ["development","validation","holdout","all"]:
        pp=p if period=="all" else p[p.period==period]
        cc=c if period=="all" else c[c.period==period]
        base_policy=float(pp.policy_net_rupees.sum())
        base_control=float(cc.net_rupees.sum())
        row={"period":period,"policy_trades":len(pp),"control_trades":len(cc),
             "base_policy_net":base_policy,"base_control_net":base_control,
             "base_uplift":base_policy-base_control,
             "policy_drawdown":max_dd(pp.policy_net_rupees),
             "control_drawdown":max_dd(cc.net_rupees)}

        for mult in [1.25,1.50,2.00]:
            # Stored gross/cost allow deterministic additive cost stress.
            stress_policy=float((pp.policy_gross_rupees-mult*pp.policy_cost_rupees).sum())
            stress_control=float((cc.gross_rupees-mult*cc.cost_rupees).sum())
            row[f"cost_x_{mult:.2f}_policy"]=stress_policy
            row[f"cost_x_{mult:.2f}_control"]=stress_control
            row[f"cost_x_{mult:.2f}_uplift"]=stress_policy-stress_control
        results.append(row)

    q=pd.DataFrame(results)
    q.to_csv(OUT/"audit_periods.csv",index=False)

    # Override-level audit for reproducibility.
    ov=p[p.override].copy()
    ov.to_csv(OUT/"override_audit.csv",index=False)

    hold=q[q.period=="holdout"].iloc[0]
    val=q[q.period=="validation"].iloc[0]
    allr=q[q.period=="all"].iloc[0]
    audit={
      "status":"PASS",
      "control_counts":control_counts,
      "policy_trades":len(p),
      "policy_unique_entries":int(p.entry_ts.nunique()),
      "overrides":int(p.override.sum()),
      "warmup_rows":100,
      "validation_uplift_rupees":float(val.base_uplift),
      "holdout_uplift_rupees":float(hold.base_uplift),
      "validation_policy_drawdown":float(val.policy_drawdown),
      "validation_control_drawdown":float(val.control_drawdown),
      "holdout_policy_drawdown":float(hold.policy_drawdown),
      "holdout_control_drawdown":float(hold.control_drawdown),
      "validation_uplift_cost_x_1_50":float(val["cost_x_1.50_uplift"]),
      "holdout_uplift_cost_x_1_50":float(hold["cost_x_1.50_uplift"]),
      "validation_uplift_cost_x_2_00":float(val["cost_x_2.00_uplift"]),
      "holdout_uplift_cost_x_2_00":float(hold["cost_x_2.00_uplift"]),
      "frozen_control_validation_plus_holdout":frozen_base,
      "frozen_control_target":expected,
      "promotion_gate_status":"NOT_YET_PROMOTABLE",
      "reason":"Development uplift is negative and a sequential model-family comparison is still required; this audit only establishes data/chronology/cost-stress validity."
    }
    (OUT/"audit.json").write_text(json.dumps(audit,indent=2))
    (OUT/"status.json").write_text(json.dumps(audit,indent=2))
    print(json.dumps(audit,indent=2))
    print(q.to_string(index=False))

if __name__=="__main__":
    main()
