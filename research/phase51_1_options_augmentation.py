from pathlib import Path
import hashlib, json, os
import pandas as pd
from huggingface_hub import hf_hub_download

OOS_START = "2026-04-21"
OOS_END = "2026-08-04"
EXPECTED_EXPIRIES = pd.to_datetime([
    "2026-04-21","2026-04-28","2026-05-05","2026-05-12","2026-05-19","2026-05-26",
    "2026-06-02","2026-06-09","2026-06-16","2026-06-23","2026-06-30",
    "2026-07-07","2026-07-14","2026-07-21","2026-07-28","2026-08-04"
]).strftime("%Y-%m-%d").tolist()

ROOT=Path("data/phase51/options_augmentation")
ROOT.mkdir(parents=True,exist_ok=True)
TOKEN=os.environ.get("HF_TOKEN")
if not TOKEN:
    raise RuntimeError("HF_TOKEN is required")

RISSIN=("rissin/nse-options-intraday","upstox_intraday/NIFTY/NIFTY_2026.parquet")
TMK_BASE="thetrademarkk/india-index-options-1m"
SUPP_EXPIRIES=["2026-07-28","2026-08-04"]
COMMON_EXPIRIES=["2026-07-07","2026-07-14","2026-07-21"]

def fetch(repo, filename, target):
    p=hf_hub_download(repo_id=repo,filename=filename,repo_type="dataset",token=TOKEN)
    if not target.exists() or target.stat().st_size != Path(p).stat().st_size:
        target.write_bytes(Path(p).read_bytes())
    return target

def normalize_rissin(path):
    df=pd.read_parquet(path)
    required={"timestamp","expiry","strike","option_type","close"}
    missing=required.difference(df.columns)
    if missing: raise AssertionError(f"rissin missing columns {sorted(missing)}")
    df=df[(df["underlying"]=="NIFTY") & (df["granularity"]=="1min")].copy()
    df["timestamp"]=pd.to_datetime(df["timestamp"],errors="coerce")
    df["expiry"]=pd.to_datetime(df["expiry"],errors="coerce").dt.strftime("%Y-%m-%d")
    if df["timestamp"].isna().any() or df["expiry"].isna().any():
        raise AssertionError("rissin timestamp/expiry parse failures")
    if getattr(df["timestamp"].dt,"tz",None) is None:
        df["timestamp"]=df["timestamp"].dt.tz_localize("Asia/Kolkata")
    else:
        df["timestamp"]=df["timestamp"].dt.tz_convert("Asia/Kolkata")
    df["close"]=pd.to_numeric(df["close"],errors="coerce")
    df["strike"]=pd.to_numeric(df["strike"],errors="coerce")
    if df["close"].isna().any() or df["strike"].isna().any():
        raise AssertionError("rissin numeric parse failure")
    return df

def normalize_tmk(path, expected_expiry=None):
    df=pd.read_parquet(path)
    required={"timestamp","expiry","strike","option_type","close"}
    missing=required.difference(df.columns)
    if missing: raise AssertionError(f"{path} missing columns {sorted(missing)}")
    df["timestamp"]=pd.to_datetime(df["timestamp"],errors="coerce")
    if getattr(df["timestamp"].dt,"tz",None) is None:
        df["timestamp"]=df["timestamp"].dt.tz_localize("Asia/Kolkata")
    else:
        df["timestamp"]=df["timestamp"].dt.tz_convert("Asia/Kolkata")
    df["expiry"]=pd.to_datetime(df["expiry"],errors="coerce").dt.strftime("%Y-%m-%d")
    df["strike"]=pd.to_numeric(df["strike"],errors="coerce")
    df["close"]=pd.to_numeric(df["close"],errors="coerce")
    if df["timestamp"].isna().any() or df["strike"].isna().any() or df["close"].isna().any():
        raise AssertionError(f"{path}: numeric/timestamp parse failure")
    if expected_expiry and set(df["expiry"].dropna().unique()) != {expected_expiry}:
        raise AssertionError(f"{path}: unexpected expiries {sorted(df['expiry'].dropna().unique())}")
    dup=int(df.duplicated(["timestamp","strike","option_type"]).sum())
    if dup:
        raise AssertionError(f"{path}: duplicate timestamp/strike/option_type rows={dup}")
    return df

def session_checks(df, expected_expiry):
    day = df[df["timestamp"].dt.strftime("%Y-%m-%d") == expected_expiry]
    if day.empty:
        return {
            "session_pass": False,
            "expiry_day_present": False,
            "expiry_day_unique_timestamps": 0,
            "expiry_day_first_time": None,
            "expiry_day_last_time": None,
            "reason": "no expiry-day observations",
        }
    ts = day["timestamp"].sort_values()
    unique_ts = int(ts.nunique())
    first = str(ts.min().time())
    last = str(ts.max().time())
    ok = unique_ts >= 375 and first <= "09:16:00" and last >= "15:29:00"
    return {
        "session_pass": bool(ok),
        "expiry_day_present": True,
        "expiry_day_unique_timestamps": unique_ts,
        "expiry_day_first_time": first,
        "expiry_day_last_time": last,
        "reason": None if ok else f"weak session coverage unique_ts={unique_ts} first={first} last={last}",
    }

rpath=fetch(RISSIN[0],RISSIN[1],ROOT/"rissin_NIFTY_2026.parquet")
r=normalize_rissin(rpath)
r_by_expiry={exp:r[r["expiry"]==exp].copy() for exp in COMMON_EXPIRIES}

in_window=r[r["expiry"].isin(EXPECTED_EXPIRIES)]
observed=sorted(in_window["expiry"].dropna().unique().tolist())
missing=[e for e in EXPECTED_EXPIRIES if e not in observed]
assert missing==SUPP_EXPIRIES, f"Unexpected missing expiry blocks: {missing}"

manifest={"original_source":{"repo_id":RISSIN[0],"filename":RISSIN[1],"sha256":hashlib.sha256(rpath.read_bytes()).hexdigest(),"bytes":rpath.stat().st_size},
          "expected_expiries":EXPECTED_EXPIRIES,"observed_expiries":observed,"missing_expiries":missing,
          "supplemental_source":{"repo_id":TMK_BASE,"files":[]},
          "common_expiry_comparisons":[]}

for exp in SUPP_EXPIRIES:
    p=fetch(TMK_BASE,f"options/NIFTY/{exp}.parquet",ROOT/f"tmk_{exp}.parquet")
    d=normalize_tmk(p,exp)
    if d.empty: raise AssertionError(f"Supplemental expiry {exp} is empty")
    sess=session_checks(d,exp)
    manifest["supplemental_source"]["files"].append({"expiry":exp,"filename":f"options/NIFTY/{exp}.parquet","sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size,"rows":int(len(d)),"expiry_values":sorted(d["expiry"].dropna().unique().tolist()),"trading_days":sorted(d["timestamp"].dt.strftime("%Y-%m-%d").unique().tolist()),"min_timestamp":str(d.timestamp.min()),"max_timestamp":str(d.timestamp.max()),**sess})
    if not sess["session_pass"]:
        manifest.setdefault("quality_failures",[]).append({"expiry":exp,"reason":sess["reason"]})

# Common-expiry source-equivalence audit, performed before any OOS P&L.
for exp in COMMON_EXPIRIES:
    rp=ROOT/f"rissin_common_{exp}.parquet"
    tp=fetch(TMK_BASE,f"options/NIFTY/{exp}.parquet",ROOT/f"tmk_common_{exp}.parquet")
    rr=r[r["expiry"]==exp].copy()
    tt=normalize_tmk(tp,exp)
    key=["timestamp","strike","option_type"]
    a=rr[key+["close"]].rename(columns={"close":"close_rissin"})
    b=tt[key+["close"]].rename(columns={"close":"close_tmk"})
    j=a.merge(b,on=key,how="inner")
    insufficient = len(j) < 10000
    if insufficient:
        manifest.setdefault("quality_failures",[]).append({"expiry":exp,"reason":f"insufficient common quote rows {len(j)}"})
    j["abs_diff"]=(j.close_rissin-j.close_tmk).abs()
    j["rel_bp"]=j.abs_diff/j.close_rissin.replace(0,pd.NA)*10000
    j=j.dropna(subset=["rel_bp"])
    stats={
        "expiry":exp,"matched_rows":int(len(j)),"rissin_rows":int(len(a)),"tmk_rows":int(len(b)),
        "coverage_vs_rissin":float(len(j)/len(a)) if len(a) else 0,
        "median_abs_points":float(j.abs_diff.median()),
        "p95_abs_points":float(j.abs_diff.quantile(.95)),
        "p99_abs_points":float(j.abs_diff.quantile(.99)),
        "max_abs_points":float(j.abs_diff.max()),
        "p95_rel_bp":float(j.rel_bp.quantile(.95)),
        "mean_signed_points":float((j.close_tmk-j.close_rissin).mean()),
    }
    gate={
        "matched_rows_ge_10000":stats["matched_rows"]>=10000,
        "coverage_vs_rissin_ge_0_80":stats["coverage_vs_rissin"]>=0.80,
        "median_abs_le_0_05":stats["median_abs_points"]<=0.05,
        "p99_abs_le_1_00":stats["p99_abs_points"]<=1.00,
        "p95_rel_bp_le_10":stats["p95_rel_bp"]<=10.0,
        "abs_mean_signed_le_0_05":abs(stats["mean_signed_points"])<=0.05,
    }
    gate["PASS"]=all(gate.values())
    manifest["common_expiry_comparisons"].append({"stats":stats,"gate":gate})

overall=all(x["gate"]["PASS"] for x in manifest["common_expiry_comparisons"]) and not manifest.get("quality_failures")
# Validate supplemental files have only their intended expiry and at least one full OOS session.
for f in manifest["supplemental_source"]["files"]:
    if not (f["min_timestamp"] < f["max_timestamp"]):
        manifest.setdefault("quality_failures",[]).append({"expiry":f["expiry"],"reason":"non-increasing timestamp bounds"})
    if not f["max_timestamp"].startswith(f["expiry"]):
        manifest.setdefault("quality_failures",[]).append({"expiry":f["expiry"],"reason":"file does not extend through named expiry"})
overall = all(x["gate"]["PASS"] for x in manifest["common_expiry_comparisons"]) and not manifest.get("quality_failures")
manifest["PASS"]=bool(overall)
Path("results/phase51").mkdir(parents=True,exist_ok=True)
Path("results/phase51/options_augmentation_audit.json").write_text(json.dumps(manifest,indent=2))
Path("results/phase51/validated_option_source.json").write_text(json.dumps({
    "status":"PASS" if overall else "FAIL",
    "original_source":manifest["original_source"],
    "missing_expiries":manifest["missing_expiries"],
    "supplemental_source":manifest["supplemental_source"],
    "common_expiry_comparisons":manifest["common_expiry_comparisons"],
    "selection_basis":"data-quality evidence only; no OOS strategy P&L was inspected"
},indent=2))
print(json.dumps(manifest,indent=2))
if not overall:
    raise SystemExit(1)
