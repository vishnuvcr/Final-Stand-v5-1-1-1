#!/usr/bin/env python3
"""Aggregate-only revalidation of two predeclared Hugging Face Parquet files."""
import os, json, hashlib, sys
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download
import pyarrow.parquet as pq
import pandas as pd

token = os.environ.get("HF_TOKEN")
if not token:
    raise SystemExit("HF_TOKEN secret unavailable; no anonymous fallback.")
repo_id = "thetrademarkk/india-index-options-1m"
targets = ["2026-07-28", "2026-08-04"]
api = HfApi(token=token)
revision = api.dataset_info(repo_id).sha
out = Path("results/phase68_hf_target_date_audit")
out.mkdir(parents=True, exist_ok=True)
result = {"phase": 68, "source": repo_id, "revision": revision, "targets": []}
for day in targets:
    rec = {"date": day, "available": False}
    filename = f"options/NIFTY/{day}.parquet"
    try:
        path = Path(hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset", revision=revision, token=token))
        raw = path.read_bytes()
        table = pq.read_table(path)
        rec.update({"available": True, "path": filename, "bytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(), "rows": table.num_rows,
                    "columns": table.column_names})
        lower = {c.lower(): c for c in table.column_names}
        tscol = next((lower[k] for k in ("timestamp","datetime","date_time","time","date") if k in lower), None)
        if tscol:
            ts = pd.to_datetime(table[tscol].to_pandas(), errors="coerce")
            if ts.dt.tz is None:
                ts = ts.dt.tz_localize("Asia/Kolkata", ambiguous="NaT", nonexistent="NaT")
            else:
                ts = ts.dt.tz_convert("Asia/Kolkata")
            mask = ts.dt.date == pd.Timestamp(day).date()
            rec.update({"timestamp_column": tscol, "target_session_rows": int(mask.sum()),
                        "unique_target_minutes": int(ts[mask].nunique()),
                        "min_timestamp_ist": str(ts.min()), "max_timestamp_ist": str(ts.max())})
            for aliases, label in [(("strike","strike_price"),"strike"),(("option_type","right","type","side"),"option_type"),(("expiry","expiry_date","expiration"),"expiry"),(("oi","open_interest"),"open_interest")]:
                col = next((lower[k] for k in aliases if k in lower), None)
                if col:
                    values = table[col].to_pandas()
                    rec[label+"_non_null"] = int(values.notna().sum())
                    if label != "open_interest":
                        rec[label+"_unique"] = int(values.nunique(dropna=True))
        else:
            rec["schema_error"] = "timestamp column not recognized"
    except Exception as exc:
        rec["error_type"] = type(exc).__name__
        rec["error"] = str(exc)[:300]
    result["targets"].append(rec)
passed = all(x.get("available") and x.get("target_session_rows",0)>0 and x.get("timestamp_column") for x in result["targets"])
result["decision"] = "TARGET_ROWS_PRESENT_REQUIRES_FROZEN_COVERAGE_REVIEW" if passed else "BLOCKED_STALE_OR_MISSING_TARGET_ROWS"
(out/"summary.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
print(json.dumps({"phase":68,"revision":revision,"decision":result["decision"],"targets":[{k:v for k,v in x.items() if k not in ("columns","error")} for x in result["targets"]]}, indent=2))
if not passed:
    sys.exit(1)
