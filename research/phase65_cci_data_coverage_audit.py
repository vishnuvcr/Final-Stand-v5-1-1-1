#!/usr/bin/env python3
"""Bounded Phase 65 timestamp/contract coverage diagnostics; no P&L replay."""
from __future__ import annotations
import hashlib, json, os, re, sys
from pathlib import Path
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results"/"phase65_cci_data_coverage_audit"
REPO="thetrademarkk/india-index-options-1m"
REVISION="3eacf762d401efd9a08e804592fa7882b354c4a2"
TZ="Asia/Kolkata"
END=pd.Timestamp("2025-12-31 23:59:59",tz=TZ)

def norm(df):
    df=df.copy(); df.columns=[str(c).strip().lower() for c in df.columns]
    ts=pd.to_datetime(df["timestamp"],errors="coerce")
    if ts.isna().any(): raise ValueError(f"timestamp parse failures: {int(ts.isna().sum())}")
    df["timestamp"]=ts.dt.tz_localize(TZ) if ts.dt.tz is None else ts.dt.tz_convert(TZ)
    return df

def load(api,token,name):
    p=Path(hf_hub_download(repo_id=REPO,filename=name,repo_type="dataset",revision=REVISION,token=token))
    return pd.read_parquet(p),{"path":name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}

def run():
    OUT.mkdir(parents=True,exist_ok=True); token=os.getenv("HF_TOKEN") or None
    api=HfApi(); files=api.list_repo_files(repo_id=REPO,repo_type="dataset",revision=REVISION,token=token)
    idxraw,idxmeta=load(api,token,"index/NIFTY.parquet"); idx=norm(idxraw)
    idx=idx.loc[idx.timestamp<=END]
    idx=idx.drop_duplicates("timestamp").set_index("timestamp",drop=False).sort_index()
    audit=pd.read_csv(ROOT/"results"/"phase64_paper_strategy_tests"/"opportunity_audit.csv")
    audit=audit.loc[audit["trigger_ts"].notna() & audit["trigger_ts"].astype(str).ne("")].copy()
    rx=re.compile(r"options/NIFTY/(\\d{4}-\\d{2}-\\d{2})\\.parquet$")
    names=set(files); cache={}; rows=[]
    for _,ev in audit.iterrows():
        try: trigger=pd.Timestamp(ev["trigger_ts"])
        except Exception: continue
        if trigger.tzinfo is None: trigger=trigger.tz_localize(TZ)
        else: trigger=trigger.tz_convert(TZ)
        if trigger>END: continue
        entry=trigger+pd.Timedelta(minutes=1)
        spotrow=idx.loc[trigger] if trigger in idx.index else None
        spot=float(spotrow["close"]) if spotrow is not None else None
        expiry=str(ev["expiry"]); source=str(ev["source_file"])
        if source not in names: 
            rows.append({"variant":ev["variant"],"split":ev["split"],"expiry":expiry,"trigger_ts":str(trigger),"entry_ts":str(entry),"trigger_index_exact":spot is not None,"entry_index_exact":entry in idx.index,"option_file_found":False,"side_trigger_any":False,"side_entry_any":False,"strict_itm_trigger_count":0,"nearest_side_offset_seconds":None,"status":"source_file_missing"}); continue
        if source not in cache:
            raw,meta=load(api,token,source); chain=norm(raw)
            aliases={"right":"option_type","optiontype":"option_type","strike_price":"strike","strikeprice":"strike"}
            for old,new in aliases.items():
                if old in chain and new not in chain: chain=chain.rename(columns={old:new})
            if "option_type" not in chain or "strike" not in chain: raise ValueError(f"missing option columns in {source}")
            chain["option_type"]=chain["option_type"].astype(str).str.upper().replace({"CALL":"CE","C":"CE","PUT":"PE","P":"PE"})
            chain["strike"]=pd.to_numeric(chain["strike"],errors="coerce")
            chain=chain.loc[chain.timestamp<=END]
            cache[source]=chain
        chain=cache[source]; side="CE" if str(ev.get("signal_side","")).upper() in ("CE","CALL") else "PE"
        sidechain=chain.loc[chain.option_type.eq(side)]
        trig=sidechain.loc[sidechain.timestamp.eq(trigger)]
        ent=sidechain.loc[sidechain.timestamp.eq(entry)]
        itm=trig.loc[(trig.strike<spot) if side=="CE" and spot is not None else (trig.strike>spot) if spot is not None else pd.Series(False,index=trig.index)]
        allts=sidechain.timestamp.drop_duplicates()
        near=None if allts.empty else float((allts-trigger).abs().dt.total_seconds().min())
        rows.append({"variant":ev["variant"],"split":ev["split"],"expiry":expiry,"trigger_ts":str(trigger),"entry_ts":str(entry),"trigger_index_exact":spot is not None,"entry_index_exact":entry in idx.index,"option_file_found":True,"side_trigger_any":not trig.empty,"side_entry_any":not ent.empty,"strict_itm_trigger_count":int(itm.strike.nunique()),"nearest_side_offset_seconds":near,"status":str(ev.get("failure_reason",""))})
    detail=pd.DataFrame(rows)
    if detail.empty: raise RuntimeError("No breakout trigger rows found in Phase 64 opportunity audit")
    detail.to_csv(OUT/"event_coverage.csv",index=False)
    agg=detail.groupby(["variant","split"],dropna=False).agg(events=("trigger_ts","size"),trigger_index_exact=("trigger_index_exact","sum"),entry_index_exact=("entry_index_exact","sum"),option_file_found=("option_file_found","sum"),side_trigger_any=("side_trigger_any","sum"),side_entry_any=("side_entry_any","sum"),events_with_strict_itm_trigger_contract=("strict_itm_trigger_count",lambda s:int((s>0).sum())),median_nearest_side_offset_seconds=("nearest_side_offset_seconds","median")).reset_index()
    agg.to_csv(OUT/"aggregate_coverage.csv",index=False)
    status_counts=detail.status.value_counts(dropna=False).to_dict()
    result={"phase":65,"status":"COMPLETED_DIAGNOSTIC_NO_PROMOTION","dataset_revision":REVISION,"index_file":idxmeta,"event_count":len(detail),"aggregate":agg.to_dict(orient="records"),"status_counts":{str(k):int(v) for k,v in status_counts.items()},"raw_data_published":False,"holdout_2026_files_downloaded":0,"interpretation":"Timestamp and contract coverage only; nearest offsets are diagnostics, not executable fills. No strategy P&L or gate changes."}
    (OUT/"diagnostic.json").write_text(json.dumps(result,indent=2,default=str))
    lines=["# Phase 65 — CCI timestamp and contract-coverage audit","","**Decision: diagnostic complete; no strategy promotion.**","",f"- Pinned dataset revision: `{REVISION}`",f"- Breakout event rows audited: **{len(detail)}**","- 2026 option data was not queried or downloaded; all event timestamps are bounded through 2025-12-31.","- No P&L was computed. Nearest timestamps are diagnostic only and are not treated as fills.","","## Aggregate exact coverage","",agg.to_markdown(index=False),"","## Event status counts",""]
    lines += [f"- `{k}`: {v}" for k,v in status_counts.items()]
    lines += ["","## Interpretation","","This phase isolates timestamp and observed-contract coverage. If the exact next-minute bar is absent, it remains a missing observation; no interpolation, forward-fill, or proxy fill is allowed. Results do not establish whether the CCI strategy is profitable or unprofitable.",""]
    (OUT/"aggregate_report.md").write_text("\n".join(lines))
    print(json.dumps(result,default=str))
if __name__=="__main__": run()
