# Phase 39 Step 2b — feature schema and leakage audit
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(".")
FEATURES=ROOT/"results/phase39_features/point_in_time_features.csv"
OUT=ROOT/"results/phase39_features"
LABELS={"control_direction","control_net_rupees","delta_pnl_call_minus_put","expiry","entry_ts","split"}
EXCLUDE_EXACT={"nifty_gap_from_prev_close","nifty_volume_ratio_30m","nifty_volume_ratio_60m","nifty_volume_ratio_120m"}
SOURCE_PREFIXES={
    "nifty_":"NIFTY spot/intraday or daily",
    "entry_spot":"NIFTY spot/intraday",
    "prev_session_":"NIFTY daily",
    "atm_":"current-week option chain",
    "call_":"current-week option chain",
    "put_":"current-week option chain",
    "candidate_":"current-week option chain",
    "near_atm_":"current-week option chain",
    "next_":"next-current-week option chain",
    "iv_":"option-chain derived",
    "global_":"previous global session",
    "flow_":"previous FII/DII publication",
    "sent_":"previous sentiment date",
    "dte_":"contract calendar",
    "entry_":"entry timestamp calendar",
}

def source_for(c):
    for p,s in SOURCE_PREFIXES.items():
        if c.startswith(p): return s
    return "manual review"

z=pd.read_csv(FEATURES)
if len(z)!=477 or z["entry_ts"].nunique()!=477:
    raise AssertionError("feature matrix identity mismatch")
numeric=[c for c in z.columns if pd.api.types.is_numeric_dtype(z[c])]
model_candidates=[c for c in numeric if c not in LABELS and c not in EXCLUDE_EXACT and z[c].notna().any()]
fully_missing=[c for c in numeric if z[c].notna().sum()==0]
label_numeric=[c for c in numeric if c in LABELS]
unexpected=[c for c in numeric if c not in LABELS and c in {"delta_pnl_call_minus_put"}]
if any(c in model_candidates for c in LABELS):
    raise AssertionError("label leaked into model candidate schema")
if set(fully_missing) != set(EXCLUDE_EXACT):
    raise AssertionError(f"unexpected fully missing numeric columns: {fully_missing}")
rows=[]
for c in model_candidates:
    rows.append({
        "feature":c,
        "source":source_for(c),
        "missing_pct":float(z[c].isna().mean()),
        "development_missing_pct":float(z.loc[z.split=="development",c].isna().mean()),
        "validation_missing_pct":float(z.loc[z.split=="validation",c].isna().mean()),
        "holdout_missing_pct":float(z.loc[z.split=="holdout",c].isna().mean()),
        "n_unique":int(z[c].nunique(dropna=True)),
        "usable_for_primary_models":True,
    })
mf=pd.DataFrame(rows).sort_values("feature")
mf.to_csv(OUT/"model_feature_manifest.csv",index=False)
summary={
    "status":"PASS",
    "rows":len(z),
    "raw_numeric_columns":len(numeric),
    "label_or_control_columns_excluded":[c for c in LABELS if c in z.columns],
    "fully_missing_columns_excluded":fully_missing,
    "model_candidate_columns":len(model_candidates),
    "source_groups":sorted(mf.source.unique().tolist()),
    "point_in_time_rules":{
        "option_chain":"exact entry timestamp",
        "intraday_nifty":"timestamp <= entry timestamp",
        "daily_and_external":"strictly prior available session/date",
        "interpolation":"forbidden",
        "forward_fill":"forbidden",
        "control_direction_as_feature":"forbidden",
        "counterfactual_target_as_feature":"forbidden"
    },
    "known_unavailable_data_blocks":[
        "NSE/BSE breadth",
        "NIFTY futures basis/OI/volume",
        "point-in-time corporate-action feed",
        "timestamp-verified intraday news feed"
    ]
}
(OUT/"leakage_audit_v2.json").write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
