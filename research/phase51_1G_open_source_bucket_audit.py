import hashlib, json, os
from pathlib import Path
import pandas as pd
from huggingface_hub import hf_hub_download

REPO = "codepyx23/india-index-options-1m-bucket"
FILES = ["options/NIFTY/2026-07-21.parquet","options/NIFTY/2026-07-28.parquet","options/NIFTY/2026-08-04.parquet"]
OUT=Path("results/phase51/opensource_1g"); OUT.mkdir(parents=True,exist_ok=True)
manifest={"repo":REPO,"files":[],"status":"RUNNING"}

for fn in FILES:
    p=hf_hub_download(repo_id=REPO,filename=fn,repo_type="dataset",token=os.environ.get("HF_TOKEN"))
    b=Path(p).read_bytes()
    df=pd.read_parquet(p)
    ts=pd.to_datetime(df["timestamp"])
    rec={
      "filename":fn,
      "bytes":len(b),
      "sha256":hashlib.sha256(b).hexdigest(),
      "rows":len(df),
      "columns":list(df.columns),
      "min_timestamp":str(ts.min()),
      "max_timestamp":str(ts.max()),
      "unique_expiries":sorted(df["expiry"].astype(str).unique().tolist()) if "expiry" in df else [],
      "expiry_day_present":fn.rsplit("/",1)[1].split(".")[0] in set(ts.dt.strftime("%Y-%m-%d")),
    }
    manifest["files"].append(rec)

manifest["status"]="AUDITED"
(Path(OUT/"codepyx23_manifest.json")).write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
