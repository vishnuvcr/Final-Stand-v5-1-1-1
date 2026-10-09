from pathlib import Path
import hashlib,json,os
import pandas as pd
from huggingface_hub import hf_hub_download

ROOT=Path("data/phase51/phase51_1H_hf")
OUT=Path("results/phase51/phase51_1H")
OUT.mkdir(parents=True,exist_ok=True)
targets=["2026-07-28","2026-08-04"]
required={"datetime","expiry_date","strike_price","right","open","high","low","close","volume","open_interest"}
report={"source":"thetrademarkk/india-index-options-1m","status":"FAIL","targets":{},"pnl_eligible":False}

for d in targets:
    p=Path(hf_hub_download(repo_id="thetrademarkk/india-index-options-1m",repo_type="dataset",
                           filename=f"options/NIFTY/{d}.parquet",
                           token=os.environ.get("HF_TOKEN") or None,local_dir=str(ROOT)))
    raw=p.read_bytes()
    item={"path":str(p),"sha256":hashlib.sha256(raw).hexdigest(),"size_bytes":len(raw)}
    df=pd.read_parquet(p)
    item["rows"]=len(df); item["columns"]=list(df.columns)
    item["missing_columns"]=sorted(required-set(df.columns))
    ts=pd.to_datetime(df["datetime"],errors="coerce"); ex=pd.to_datetime(df["expiry_date"],errors="coerce")
    item["bad_datetime"]=int(ts.isna().sum()); item["bad_expiry"]=int(ex.isna().sum())
    item["min_datetime"]=str(ts.min()); item["max_datetime"]=str(ts.max())
    item["expiry_values"]=sorted({str(x.date()) for x in ex.dropna().unique()})
    item["duplicate_keys"]=int(df.duplicated(["datetime","expiry_date","strike_price","right"]).sum())
    item["target_expiry_present"]=d in item["expiry_values"]
    item["target_trade_date_present"]=d in {str(x.date()) for x in ts.dropna().unique()}
    item["pass"]=not item["missing_columns"] and item["bad_datetime"]==0 and item["bad_expiry"]==0 and item["duplicate_keys"]==0 and item["target_expiry_present"] and item["target_trade_date_present"]
    report["targets"][d]=item

report["coverage_pass"]=all(x["pass"] for x in report["targets"].values())
report["status"]="PASS_PRE_EQUIVALENCE" if report["coverage_pass"] else "FAIL"
(OUT/"manifest.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
raise SystemExit(0 if report["coverage_pass"] else 1)
