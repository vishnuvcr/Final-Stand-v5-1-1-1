import json, os
from pathlib import Path
import pandas as pd
from huggingface_hub import hf_hub_download

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results/phase67_contract_coverage"
REV="3eacf762d401efd9a08e804592fa7882b354c4a2"
SRC="thetrademarkk/india-index-options-1m"

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    audit=pd.read_csv(ROOT/"results/phase66_paper_strategy_tests/opportunity_audit.csv")
    audit=audit[audit.trigger_ts.notna() & (audit.trigger_ts.astype(str)!="")].copy()
    manifest=json.loads((ROOT/"results/phase66_paper_strategy_tests/source_manifest.json").read_text())
    if manifest.get("revision")!=REV: raise ValueError("Pinned source revision mismatch")
    allowed={x["path"] for x in manifest["options_source_files"]}
    token=os.getenv("HF_TOKEN") or None
    events=[]; schemas={}
    for _,e in audit.iterrows():
        ts=pd.Timestamp(e.trigger_ts)
        ts=ts.tz_localize("Asia/Kolkata") if ts.tzinfo is None else ts.tz_convert("Asia/Kolkata")
        path=str(e.source_file)
        row={"variant":e.variant,"split":e.split,"expiry":e.expiry,"source_file":path,"trigger_ts":ts.isoformat()}
        if path not in allowed:
            row.update(status="source_file_not_in_manifest",trigger_exact=False,next_minute_exact=False,context_bars=0)
            events.append(row); continue
        f=Path(hf_hub_download(repo_id=SRC,filename=path,repo_type="dataset",revision=REV,token=token))
        df=pd.read_parquet(f); df.columns=[str(c).strip().lower() for c in df.columns]
        tc=next((c for c in ("timestamp","datetime","time","date_time","date") if c in df.columns),None)
        row["columns"]=",".join(df.columns)
        if not tc:
            row.update(status="timestamp_column_unrecognized",trigger_exact=False,next_minute_exact=False,context_bars=0)
            events.append(row); schemas[path]={"columns":list(df.columns)}; continue
        t=pd.to_datetime(df[tc],errors="coerce")
        t=t.dt.tz_localize("Asia/Kolkata") if t.dt.tz is None else t.dt.tz_convert("Asia/Kolkata")
        good=t.notna()
        row.update(status="audited_diagnostic_only",timestamp_column=tc,source_rows=int(len(df)),
                   trigger_exact=bool((t[good]==ts).any()),next_minute_exact=bool((t[good]==ts+pd.Timedelta(minutes=1)).any()),
                   context_bars=int(t[good].between(ts-pd.Timedelta(minutes=2),ts+pd.Timedelta(minutes=2)).sum()))
        schemas[path]={"columns":list(df.columns),"dtypes":{c:str(df[c].dtype) for c in df.columns},
                       "timestamp_min":str(t[good].min()),"timestamp_max":str(t[good].max()),"rows":int(len(df))}
        events.append(row)
    ed=pd.DataFrame(events); ed.to_csv(OUT/"event_diagnostics.csv",index=False)
    (OUT/"schema_audit.json").write_text(json.dumps(schemas,indent=2)+"\n")
    summary={"phase":67,"source":SRC,"revision":REV,"trigger_rows":len(ed),
      "exact_trigger_minute_rows":int(ed.trigger_exact.sum()) if "trigger_exact" in ed else 0,
      "exact_next_minute_rows":int(ed.next_minute_exact.sum()) if "next_minute_exact" in ed else 0,
      "rows_with_pm2_context":int((ed.context_bars>0).sum()) if "context_bars" in ed else 0,
      "decision":"DIAGNOSTIC_ONLY_NO_STRATEGY_PROMOTION"}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    (OUT/"report.md").write_text("# Phase 67 Contract/Minute Coverage\n\n**Decision: diagnostic only; no strategy promotion.**\n\n"+json.dumps(summary,indent=2)+"\n\nNearby bars are diagnostic context only and are never substituted as fills. This audit does not prove ITM mapping or executable liquidity; no entry rules are relaxed.\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()
