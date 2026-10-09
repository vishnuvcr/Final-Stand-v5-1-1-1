#!/usr/bin/env python3
"""Audit two free Hugging Face NIFTY option files; never commit raw Parquet."""
import hashlib, json, os, pathlib, sys
from datetime import datetime, timezone
import pandas as pd
from huggingface_hub import hf_hub_download
REPO = "thetrademarkk/india-index-options-1m"
TARGETS = ["2026-07-28", "2026-08-04"]
OUT = pathlib.Path("results/phase51/phase51_1J_free_hf_audit")
OUT.mkdir(parents=True, exist_ok=True)
results = []
for day in TARGETS:
    name = f"options/NIFTY/{day}.parquet"
    item = {"date": day, "repo_id": REPO, "path": name, "status": "UNKNOWN"}
    try:
        path = pathlib.Path(hf_hub_download(repo_id=REPO, filename=name, repo_type="dataset",
            token=os.environ.get("HF_TOKEN") or None, cache_dir=os.environ.get("HF_HOME", "/tmp/hf-cache")))
        df = pd.read_parquet(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        cols = list(df.columns); lower = {c.lower(): c for c in cols}
        item.update({"status":"DOWNLOADED","file_bytes":path.stat().st_size,"sha256":digest,
                     "rows":int(len(df)),"columns":cols})
        tcol = next((lower[k] for k in ("timestamp","datetime","date_time","time") if k in lower), None)
        dcol = next((lower[k] for k in ("trading_day","date","trade_date") if k in lower), None)
        scol = next((lower[k] for k in ("strike","strike_price") if k in lower), None)
        ocol = next((lower[k] for k in ("option_type","right","type","side") if k in lower), None)
        ecol = next((lower[k] for k in ("expiry","expiry_date") if k in lower), None)
        if tcol:
            ts = pd.to_datetime(df[tcol], errors="coerce")
            item.update({"timestamp_column":tcol,"timestamp_valid_rows":int(ts.notna().sum()),
                "timestamp_min":str(ts.min()) if ts.notna().any() else None,
                "timestamp_max":str(ts.max()) if ts.notna().any() else None,
                "unique_timestamps":int(ts.nunique())})
            if ts.notna().any():
                targetmask = ts.dt.strftime("%Y-%m-%d") == day
                item["rows_on_target_date"] = int(targetmask.sum())
                item["timestamps_on_target_date"] = int(ts[targetmask].nunique())
                item["target_minutes"] = sorted(ts[targetmask].dt.strftime("%H:%M").unique().tolist())
        elif dcol:
            item["date_column"] = dcol
            item["rows_on_target_date"] = int((df[dcol].astype(str).str[:10] == day).sum())
        if scol:
            item.update({"strike_column":scol,"unique_strikes":int(df[scol].nunique(dropna=True)),
                "strike_min":float(df[scol].min()) if df[scol].notna().any() else None,
                "strike_max":float(df[scol].max()) if df[scol].notna().any() else None})
        if ocol: item.update({"option_type_column":ocol,"option_types":sorted(df[ocol].dropna().astype(str).unique().tolist())})
        if ecol: item.update({"expiry_column":ecol,"expiries":sorted(df[ecol].dropna().astype(str).unique().tolist())[:50]})
        item["invalid_or_nonpositive_close_rows"] = int((pd.to_numeric(df[lower["close"]],errors="coerce") <= 0).sum()) if "close" in lower else None
        keycols = [c for c in (tcol,scol,ocol,ecol) if c]
        item["duplicate_contract_timestamp_keys"] = int(df.duplicated(keycols).sum()) if len(keycols)>=3 else None
        item["warning"] = "Dataset card warns option coverage is partial; exact strategy-leg coverage must be checked."
    except Exception as exc:
        item.update({"status":"FAILED","error_type":type(exc).__name__,"error":str(exc)[:1000]})
    results.append(item)
manifest = {"audit":"Phase 51-1J free Hugging Face candidate audit",
 "created_utc":datetime.now(timezone.utc).isoformat(),"repo_id":REPO,"targets":TARGETS,
 "raw_parquet_committed":False,"results":results,"decision":"PENDING_REVIEW"}
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,default=str)+"\n")
lines=["# Free Hugging Face candidate audit","",f"Audit UTC: {manifest['created_utc']}","",
 f"Dataset: https://huggingface.co/datasets/{REPO}","","Raw Parquet files are not committed to this repository.",""]
for x in results:
    lines += [f"## {x['date']}","",f"- Status: {x['status']}"]
    for k in ("file_bytes","sha256","rows","timestamp_column","timestamp_min","timestamp_max",
        "rows_on_target_date","timestamps_on_target_date","unique_strikes","strike_min","strike_max",
        "option_types","expiries","duplicate_contract_timestamp_keys","invalid_or_nonpositive_close_rows","error"):
        if k in x: lines.append(f"- {k}: {x[k]}")
    lines += ["","File presence does not prove required strike/expiry coverage.",""]
(OUT/"REPORT.md").write_text("\n".join(lines)+"\n")
print(json.dumps({"manifest":str(OUT/"manifest.json"),"results":results},indent=2,default=str))
if any(x["status"] != "DOWNLOADED" for x in results): sys.exit(2)
