import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(".")
POL=ROOT/"results/phase39_sequential_policy/sequential_trades.csv"
DEV=ROOT/"results/phase39_data/development_control_trades_2021_2023.csv"
FRZ=ROOT/"results/phase39_data/frozen_control_trades_2024_2026-06-30.csv"
OUT=ROOT/"results/phase39_symbolic_audit"
OUT.mkdir(parents=True,exist_ok=True)

def period(exp):
    y=pd.to_datetime(exp).dt.year
    return np.where(y<=2023,"development",np.where(y<=2025,"validation","holdout"))

def dd(x):
    x=np.asarray(x,float); e=np.cumsum(x); p=np.maximum.accumulate(np.r_[0.,e])
    return float(np.max(p[1:]-e)) if len(e) else 0.

p=pd.read_csv(POL); p["period"]=period(p.expiry)
d=pd.read_csv(DEV); f=pd.read_csv(FRZ); d["period"]="development"; f["period"]=period(f.expiry)
c=pd.concat([d,f],ignore_index=True)

assert len(c)==477
assert c.groupby("period").size().to_dict()=={"development":271,"validation":172,"holdout":34}
assert int(p.override.sum())==1
assert p.entry_ts.is_unique and p.exit_ts.gt(p.entry_ts).all()
assert not (p.exit_ts.shift(1)>p.entry_ts).fillna(False).any()

rows=[]
for per in ["development","validation","holdout"]:
    pp=p[p.period==per].copy(); cc=c[c.period==per].copy()
    row={"period":per,"policy_trades":len(pp),"control_trades":len(cc),
         "policy_net":float(pp.policy_net_rupees.sum()),"control_net":float(cc.net_rupees.sum()),
         "uplift":float(pp.policy_net_rupees.sum()-cc.net_rupees.sum()),
         "policy_dd":dd(pp.policy_net_rupees),"control_dd":dd(cc.net_rupees)}
    for mult in [1.25,1.50,2.0]:
        row[f"cost_{mult:.2f}_uplift"]=float((pp.policy_gross_rupees-mult*pp.policy_cost_rupees).sum()-(cc.gross_rupees-mult*cc.cost_rupees).sum())
    rows.append(row)
q=pd.DataFrame(rows)
p[p.override].to_csv(OUT/"override.csv",index=False)
q.to_csv(OUT/"period_cost_stress.csv",index=False)

# Exact validation/holdout frozen benchmark reconciliation.
frozen=float(c[c.period.isin(["validation","holdout"])].net_rupees.sum())
summary={
 "status":"PASS","control_split":c.groupby("period").size().to_dict(),
 "overrides":int(p.override.sum()),
 "validation_uplift":float(q.loc[q.period=="validation","uplift"].iloc[0]),
 "holdout_uplift":float(q.loc[q.period=="holdout","uplift"].iloc[0]),
 "holdout_policy_net":float(q.loc[q.period=="holdout","policy_net"].iloc[0]),
 "holdout_control_net":float(q.loc[q.period=="holdout","control_net"].iloc[0]),
 "holdout_policy_dd":float(q.loc[q.period=="holdout","policy_dd"].iloc[0]),
 "holdout_control_dd":float(q.loc[q.period=="holdout","control_dd"].iloc[0]),
 "validation_cost_x_1_50":float(q.loc[q.period=="validation","cost_1.50_uplift"].iloc[0]),
 "holdout_cost_x_1_50":float(q.loc[q.period=="holdout","cost_1.50_uplift"].iloc[0]),
 "validation_cost_x_2_00":float(q.loc[q.period=="validation","cost_2.00_uplift"].iloc[0]),
 "holdout_cost_x_2_00":float(q.loc[q.period=="holdout","cost_2.00_uplift"].iloc[0]),
 "frozen_control_validation_plus_holdout":frozen,
 "frozen_control_target":63672.57530171223,
 "promotion":"REJECTED",
 "reason":"Single override; negative development uplift; zero 2026 holdout uplift; no durable control-relative improvement."
}
assert abs(frozen-63672.57530171223)<1e-6
(ROOT/"results/phase39_symbolic_audit"/"audit.json").write_text(json.dumps(summary,indent=2))
(ROOT/"results/phase39_symbolic_audit"/"status.json").write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
print(q.to_string(index=False))
