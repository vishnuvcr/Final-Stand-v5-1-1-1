# Phase 51-1E frozen-gap gate; workflow trigger checkpoint.
from pathlib import Path
import hashlib, json
import pandas as pd

ROOT=Path("data/phase51/hf_options/options/NIFTY")
OUT=Path("results/phase51/hf_options_gate")
OUT.mkdir(parents=True,exist_ok=True)
targets=["2026-07-28","2026-08-04"]
required={"datetime","expiry_date","strike_price","right","open","high","low","close","volume","open_interest"}
report={"source":"thetrademarkk/india-index-options-1m","status":"FAIL","targets":{}}

for d in targets:
    p=ROOT/(d+".parquet")
    item={"path":str(p),"exists":p.exists()}
    if p.exists():
        raw=p.read_bytes()
        item["sha256"]=hashlib.sha256(raw).hexdigest()
        item["size_bytes"]=len(raw)
        df=pd.read_parquet(p)
        item["rows"]=len(df)
        item["columns"]=list(df.columns)
        item["missing_columns"]=sorted(required-set(df.columns))
        ts=pd.to_datetime(df["datetime"],errors="coerce")
        ex=pd.to_datetime(df["expiry_date"],errors="coerce")
        item["bad_datetime"]=int(ts.isna().sum())
        item["bad_expiry"]=int(ex.isna().sum())
        item["min_datetime"]=str(ts.min())
        item["max_datetime"]=str(ts.max())
        item["expiry_values"]=sorted({str(x.date()) for x in ex.dropna().unique()})
        item["duplicate_keys"]=int(df.duplicated(["datetime","expiry_date","strike_price","right"]).sum())
        item["schema_pass"]=not item["missing_columns"] and item["bad_datetime"]==0 and item["bad_expiry"]==0
        item["integrity_pass"]=item["duplicate_keys"]==0
        item["target_expiry_present"]=d in item["expiry_values"]
        item["endpoint_date_match"]=d in item["min_datetime"] and d in item["max_datetime"]
        item["pass"]=item["schema_pass"] and item["integrity_pass"] and item["target_expiry_present"] and item["endpoint_date_match"]
    report["targets"][d]=item

report["coverage_pass"]=all(x.get("pass",False) for x in report["targets"].values())
report["status"]="PASS_PRE_EQUIVALENCE" if report["coverage_pass"] else "FAIL"
report["pnl_eligible"]=False
report["next_gate"]="Compare these files against frozen RISSIN common-expiry rows before any OOS replay."
(OUT/"manifest.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
raise SystemExit(0 if report["coverage_pass"] else 1)
