from pathlib import Path
import hashlib
import io
import json
import urllib.request
import pandas as pd

OOS_START = pd.Timestamp("2026-04-21", tz="Asia/Kolkata")
OOS_END = pd.Timestamp("2026-08-04 23:59:59", tz="Asia/Kolkata")

RAW_BASE = "https://raw.githubusercontent.com/technovusin/nifty50-historical-data/main/1min/2026"
MONTHS = ["04", "05", "06", "07", "08"]
ROOT = Path("data/phase51/third_spot")
ROOT.mkdir(parents=True, exist_ok=True)

def fetch_month(mm):
    name = f"NIFTY50_1min_2026-{mm}.csv"
    target = ROOT / name
    if not target.exists():
        with urllib.request.urlopen(f"{RAW_BASE}/{name}", timeout=60) as resp:
            target.write_bytes(resp.read())
    return target

frames = []
source_manifest = []
for mm in MONTHS:
    p = fetch_month(mm)
    source_manifest.append({
        "filename": p.name,
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        "bytes": p.stat().st_size,
    })
    df = pd.read_csv(p)
    required = {"Timestamp", "Open", "High", "Low", "Close"}
    missing = sorted(required.difference(df.columns))
    if missing:
        raise AssertionError(f"{p}: missing required columns {missing}")
    ts = pd.to_datetime(df["Timestamp"], errors="coerce")
    if ts.isna().any():
        raise AssertionError(f"{p}: timestamp parse failures={int(ts.isna().sum())}")
    if getattr(ts.dt, "tz", None) is None:
        ts = ts.dt.tz_localize("Asia/Kolkata")
    else:
        ts = ts.dt.tz_convert("Asia/Kolkata")
    close = pd.to_numeric(df["Close"], errors="coerce")
    if close.isna().any() or (close <= 0).any():
        raise AssertionError(f"{p}: invalid close values")
    frames.append(pd.DataFrame({"timestamp": ts, "close": close}))

third = pd.concat(frames, ignore_index=True).sort_values("timestamp")
dup = int(third["timestamp"].duplicated().sum())
if dup:
    raise AssertionError(f"Third source duplicate timestamps={dup}")
third = third[(third.timestamp >= OOS_START) & (third.timestamp <= OOS_END)]
if third.empty:
    raise AssertionError("Third source contains no frozen OOS rows")

day_audit = []
bad_days = []
for day, g in third.groupby(third.timestamp.dt.date):
    gs = g.timestamp.sort_values()
    diffs = gs.diff().dropna().dt.total_seconds().div(60)
    span = int((gs.max() - gs.min()).total_seconds() / 60)
    max_gap = int(diffs.max()) if len(diffs) else 0
    rows = int(len(gs))
    item = {
        "date": str(day),
        "rows": rows,
        "first_timestamp": str(gs.min()),
        "last_timestamp": str(gs.max()),
        "span_minutes": span,
        "max_internal_gap_minutes": max_gap,
    }
    day_audit.append(item)
    # OOS dates are ordinary NSE trading days except 2026-05-01,
    # 2026-05-28 and 2026-06-26. For a present day, the published cleaned
    # source should normally contain the full 09:15–15:29 minute session.
    if rows < 300 or span < 360 or max_gap > 1:
        bad_days.append(item)

# Direct common-period comparison against the original frozen primary source.
from huggingface_hub import hf_hub_download
try:
    primary_path = ROOT.parent / "spot_primary.parquet"
    if not primary_path.exists():
        src_primary = hf_hub_download(
            repo_id="thetrademarkk/india-index-options-1m",
            filename="index/NIFTY.parquet",
            repo_type="dataset",
            token=os.environ.get("HF_TOKEN"),
        )
        primary_path.write_bytes(Path(src_primary).read_bytes())
    primary_raw = pd.read_parquet(primary_path)
    pts = pd.to_datetime(primary_raw["timestamp"], errors="coerce")
    if getattr(pts.dt, "tz", None) is None:
        pts = pts.dt.tz_localize("Asia/Kolkata")
    else:
        pts = pts.dt.tz_convert("Asia/Kolkata")
    primary_n = pd.DataFrame({
        "timestamp": pts,
        "close": pd.to_numeric(primary_raw["close"], errors="coerce"),
    })
    primary_n = primary_n[(primary_n.timestamp >= OOS_START) & (primary_n.timestamp <= OOS_END)]
    jp = third.merge(primary_n, on="timestamp", suffixes=("_third", "_primary"))
    if len(jp) < 10000:
        raise AssertionError(f"Insufficient third/primary overlap rows: {len(jp)}")
    jp["abs_diff"] = (jp.close_third - jp.close_primary).abs()
    jp["rel_bp"] = jp.abs_diff / jp.close_primary * 10000
    jp["signed_diff"] = jp.close_third - jp.close_primary
    primary_stats = {
        "overlap_rows": int(len(jp)),
        "overlap_first": str(jp.timestamp.min()),
        "overlap_last": str(jp.timestamp.max()),
        "median_abs_points": float(jp.abs_diff.median()),
        "p95_abs_points": float(jp.abs_diff.quantile(0.95)),
        "p99_abs_points": float(jp.abs_diff.quantile(0.99)),
        "max_abs_points": float(jp.abs_diff.max()),
        "median_rel_bp": float(jp.rel_bp.median()),
        "p95_rel_bp": float(jp.rel_bp.quantile(0.95)),
        "mean_signed_points": float(jp.signed_diff.mean()),
        "median_signed_points": float(jp.signed_diff.median()),
    }
    primary_overlap_gate = {
        "overlap_rows_ge_10000": primary_stats["overlap_rows"] >= 10000,
        "median_abs_le_0_50": primary_stats["median_abs_points"] <= 0.50,
        "p99_abs_le_3_00": primary_stats["p99_abs_points"] <= 3.00,
        "p95_rel_bp_le_2_00": primary_stats["p95_rel_bp"] <= 2.00,
        "abs_mean_signed_le_1_00": abs(primary_stats["mean_signed_points"]) <= 1.00,
    }
    primary_overlap_gate["PASS"] = all(primary_overlap_gate.values())
except Exception as exc:
    primary_stats = {}
    primary_overlap_gate = {"PASS": False, "error": repr(exc)}

# Reuse the independently cached fallback source when present. If the file
# is not present locally, fetch it directly from Hugging Face only for audit.
try:
    import os
    from huggingface_hub import hf_hub_download
    token = os.environ.get("HF_TOKEN")
    p = ROOT.parent / "spot_fallback.parquet"
    if not p.exists():
        src = hf_hub_download(
            repo_id="Jitendra12421/AlargeDatabase",
            filename="INDDEX FILES/NIFTY_minute.parquet",
            repo_type="dataset",
            token=token,
        )
        p.write_bytes(Path(src).read_bytes())
    fallback = pd.read_parquet(p)
    ts_candidates = ["timestamp", "datetime", "Datetime", "date_time", "DateTime", "time", "Date", "date"]
    ts_col = next((c for c in ts_candidates if c in fallback.columns), None)
    if ts_col is None:
        raise AssertionError(f"Fallback timestamp column unresolved: {fallback.columns.tolist()}")
    fts = pd.to_datetime(fallback[ts_col], errors="coerce")
    if getattr(fts.dt, "tz", None) is None:
        fts = fts.dt.tz_localize("Asia/Kolkata")
    else:
        fts = fts.dt.tz_convert("Asia/Kolkata")
    fallback_n = pd.DataFrame({"timestamp": fts, "close": pd.to_numeric(fallback["close"], errors="coerce")})
    fallback_n = fallback_n[(fallback_n.timestamp >= OOS_START) & (fallback_n.timestamp <= OOS_END)]
except Exception as exc:
    fallback_n = pd.DataFrame(columns=["timestamp","close"])
    fallback_error = repr(exc)

j = third.merge(fallback_n, on="timestamp", suffixes=("_third", "_fallback"))
if len(j) < 10000:
    raise AssertionError(f"Insufficient third/fallback overlap rows: {len(j)}")

j["abs_diff"] = (j.close_third - j.close_fallback).abs()
j["rel_bp"] = j.abs_diff / j.close_third * 10000
j["signed_diff"] = j.close_fallback - j.close_third

stats = {
    "overlap_rows": int(len(j)),
    "overlap_first": str(j.timestamp.min()),
    "overlap_last": str(j.timestamp.max()),
    "median_abs_points": float(j.abs_diff.median()),
    "p95_abs_points": float(j.abs_diff.quantile(0.95)),
    "p99_abs_points": float(j.abs_diff.quantile(0.99)),
    "max_abs_points": float(j.abs_diff.max()),
    "median_rel_bp": float(j.rel_bp.median()),
    "p95_rel_bp": float(j.rel_bp.quantile(0.95)),
    "mean_signed_points": float(j.signed_diff.mean()),
    "median_signed_points": float(j.signed_diff.median()),
}

overlap_gate = {
    "overlap_rows_ge_10000": stats["overlap_rows"] >= 10000,
    "median_abs_le_0_50": stats["median_abs_points"] <= 0.50,
    "p99_abs_le_3_00": stats["p99_abs_points"] <= 3.00,
    "p95_rel_bp_le_2_00": stats["p95_rel_bp"] <= 2.00,
    "abs_mean_signed_le_1_00": abs(stats["mean_signed_points"]) <= 1.00,
}
overlap_gate["PASS"] = all(overlap_gate.values())

out = {
    "source": {
        "repository": "technovusin/nifty50-historical-data",
        "raw_base": RAW_BASE,
        "months": MONTHS,
        "files": source_manifest,
    },
    "oos_window": ["2026-04-21", "2026-08-04"],
    "oos_rows": int(len(third)),
    "oos_first_timestamp": str(third.timestamp.min()),
    "oos_last_timestamp": str(third.timestamp.max()),
    "duplicate_timestamps": dup,
    "bad_days": bad_days,
    "day_audit": day_audit,
    "fallback_overlap": stats,
    "fallback_overlap_gate": overlap_gate,
    "primary_overlap": primary_stats,
    "primary_overlap_gate": primary_overlap_gate,
}
if 'fallback_error' in locals():
    out["fallback_error"] = fallback_error

Path("results/phase51").mkdir(parents=True, exist_ok=True)
Path("results/phase51/third_spot_audit.json").write_text(json.dumps(out, indent=2))
Path("results/phase51/third_spot_gate.json").write_text(json.dumps({
    "PASS": bool(len(bad_days) == 0 and overlap_gate["PASS"] and primary_overlap_gate["PASS"]),
    "third_source_session_gate": len(bad_days) == 0,
    "fallback_overlap_gate": overlap_gate,
}, indent=2))

if len(bad_days) or not overlap_gate["PASS"]:
    raise SystemExit("THIRD_SPOT_TRIANGULATION_REJECTED: inspect third_spot_audit.json")

print(json.dumps(out, indent=2))
