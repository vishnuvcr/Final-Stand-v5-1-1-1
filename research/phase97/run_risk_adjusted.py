#!/usr/bin/env python3
"""Phase 97: DEV-only drawdown-normalized selection; excludes holdout rows."""
import csv, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"results/phase45_ready_made/strategy_vix_summary.csv"
OUT=ROOT/"results/phase97"
EXPECTED="4208da2e1189a68af697e11d03dd7d4ac937ddf7"
REGIMES=("LOW","NORMAL","HIGH")
MIN={"LOW":20,"NORMAL":20,"HIGH":3}

def blob_sha(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+bytes([0])+data).hexdigest()

def main():
    raw=SOURCE.read_bytes()
    sha=blob_sha(raw)
    if sha!=EXPECTED: raise SystemExit(f"Source fingerprint mismatch: {sha}")
    rows=[]
    with SOURCE.open(newline="",encoding="utf-8") as f:
        rd=csv.DictReader(f)
        needed={"strategy","split","state","trades","net","net50","max_dd","defined_risk"}
        if not rd.fieldnames or not needed.issubset(rd.fieldnames): raise SystemExit("Required columns missing")
        for r in rd:
            if r.get("split") not in {"development","validation"}: continue
            if r.get("state") in REGIMES and r.get("defined_risk","").lower()=="true": rows.append(r)
    index={}
    for r in rows: index.setdefault((r["state"],r["strategy"]),{})[r["split"]]=r
    selected=[]
    for regime in REGIMES:
        eligible=[]
        for (state,name),sp in index.items():
            if state!=regime or "development" not in sp or "validation" not in sp: continue
            d,v=sp["development"],sp["validation"]
            if int(float(d["trades"]))<MIN[regime] or int(float(v["trades"]))<MIN[regime]: continue
            dd=float(d["max_dd"]); n=float(d["net50"])
            if n<=0 or dd<=0: continue
            eligible.append({"regime":regime,"strategy":name,"dev_trades":int(float(d["trades"])),"dev_net50":n,
                "dev_max_dd":dd,"dev_score":n/dd,"val_trades":int(float(v["trades"])),"val_net":float(v["net"]),
                "val_net50":float(v["net50"]),"val_max_dd":float(v["max_dd"])})
        if not eligible: raise SystemExit(f"No eligible positive risk-adjusted candidate in {regime}")
        eligible.sort(key=lambda x:(-x["dev_score"],x["strategy"]))
        w=eligible[0]; w["eligible_candidates"]=len(eligible); w["validation_net50_positive"]=w["val_net50"]>0
        selected.append(w)
    OUT.mkdir(parents=True,exist_ok=True)
    fields=["regime","strategy","eligible_candidates","dev_trades","dev_net50","dev_max_dd","dev_score","val_trades","val_net","val_net50","val_max_dd","validation_net50_positive"]
    with (OUT/"risk_adjusted_results.csv").open("w",newline="",encoding="utf-8") as f:
        wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(selected)
    agg=round(sum(x["val_net50"] for x in selected),2)
    report={"phase":97,"status":"PASS","source_blob_sha":sha,"selection_score":"DEV net50 / DEV max_dd; require positive DEV net50 and positive DEV max_dd",
        "minimum_trades_by_regime":MIN,"selected_regimes":[{"regime":x["regime"],"strategy":x["strategy"],"dev_score":round(x["dev_score"],6),
        "dev_net50":round(x["dev_net50"],2),"val_net50":round(x["val_net50"],2),"val_trades":x["val_trades"],
        "val_max_dd":round(x["val_max_dd"],2),"eligible_candidates":x["eligible_candidates"]} for x in selected],
        "aggregate_validation_net50_inr":agg,"primary_endpoint_positive":agg>0,"holdout_rows_retained_or_used":False,
        "phase83_2026_holdout_accessed":False,"new_market_data_or_strategy_replay":False,"strategy_promoted":False,
        "interpretation":"Retrospective exploratory method on previously explored summary data; aggregate cells are not a deployable portfolio return."}
    (OUT/"validation_report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__": main()

# Frozen Phase 97 method; no validation-based selection.
