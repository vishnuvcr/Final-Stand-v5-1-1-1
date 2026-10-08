from pathlib import Path
import hashlib
import json
import os
import pandas as pd
from huggingface_hub import hf_hub_download

OOS_START = pd.Timestamp("2026-04-21", tz="Asia/Kolkata")
OOS_END = pd.Timestamp("2026-08-04 23:59:59", tz="Asia/Kolkata")
ROOT = Path("data/phase51")
ROOT.mkdir(parents=True, exist_ok=True)
TOKEN = os.environ.get("HF_TOKEN")
if not TOKEN:
    raise RuntimeError("HF_TOKEN is required")

SOURCES = [
    ("thetrademarkk/india-index-options-1m", "index/NIFTY.parquet", ROOT / "spot_primary.parquet"),
    ("Jitendra12421/AlargeDatabase", "INDDEX FILES/NIFTY_minute.parquet", ROOT / "spot_fallback.parquet"),
]

def fetch(repo_id, filename, target):
    p = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset", token=TOKEN)
    if not target.exists() or target.stat().st_size != Path(p).stat().st_size:
        target.write_bytes(Path(p).read_bytes())
    return target

def normalize(path):
    df = pd.read_parquet(path)
    ts_candidates = ["timestamp", "datetime", "Datetime", "date_time", "DateTime", "time", "Date", "date"]
    px_candidates = ["close", "Close", "ltp", "LTP", "price", "Price", "index_close", "IndexClose"]
    ts_col = next((c for c in ts_candidates if c in df.columns), None)
    px_col = next((c for c in px_candidates if c in df.columns), None)
    if ts_col is None or px_col is None:
        raise AssertionError(f"Cannot resolve timestamp/price in {path}: {df.columns.tolist()}")
    ts = pd.to_datetime(df[ts_col], errors="coerce")
    if ts.isna().any():
        raise AssertionError(f"{path}: timestamp parse failures={int(ts.isna().sum())}")
    if getattr(ts.dt, "tz", None) is None:
        ts = ts.dt.tz_localize("Asia/Kolkata")
    else:
        ts = ts.dt.tz_convert("Asia/Kolkata")
    px = pd.to_numeric(df[px_col], errors="coerce")
    if px.isna().any() or (px <= 0).any():
        raise AssertionError(f"{path}: invalid price values")
    out = pd.DataFrame({"timestamp": ts, "close": px}).sort_values("timestamp")
    dup = int(out["timestamp"].duplicated().sum())
    if dup:
        raise AssertionError(f"{path}: duplicate timestamps={dup}")
    return out[(out.timestamp >= OOS_START) & (out.timestamp <= OOS_END)], ts_col, px_col, hashlib.sha256(path.read_bytes()).hexdigest()

primary, p_ts, p_px, p_sha = normalize(fetch(*SOURCES[0]))
fallback, f_ts, f_px, f_sha = normalize(fetch(*SOURCES[1]))

if primary.empty:
    raise AssertionError("Primary spot source has no OOS overlap rows")
if fallback.empty:
    raise AssertionError("Fallback spot source has no OOS rows")

j = primary.merge(fallback, on="timestamp", suffixes=("_primary", "_fallback"))
if len(j) < 10000:
    raise AssertionError(f"Insufficient overlap rows: {len(j)}")

j["abs_diff"] = (j.close_primary - j.close_fallback).abs()
j["rel_bp"] = j.abs_diff / j.close_primary * 10000
j["signed_diff"] = j.close_fallback - j.close_primary

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

gate = {
    "overlap_rows_ge_10000": stats["overlap_rows"] >= 10000,
    "median_abs_le_0_50": stats["median_abs_points"] <= 0.50,
    "p99_abs_le_3_00": stats["p99_abs_points"] <= 3.00,
    "p95_rel_bp_le_2_00": stats["p95_rel_bp"] <= 2.00,
    "abs_mean_signed_le_1_00": abs(stats["mean_signed_points"]) <= 1.00,
}
gate["PASS"] = all(gate.values())

out = {
    "primary_source": {
        "repo_id": SOURCES[0][0],
        "filename": SOURCES[0][1],
        "sha256": p_sha,
        "timestamp_column": p_ts,
        "price_column": p_px,
    },
    "fallback_source": {
        "repo_id": SOURCES[1][0],
        "filename": SOURCES[1][1],
        "sha256": f_sha,
        "timestamp_column": f_ts,
        "price_column": f_px,
    },
    "oos_window": ["2026-04-21", "2026-08-04"],
    "overlap_stats": stats,
    "gate": gate,
}

Path("results/phase51").mkdir(parents=True, exist_ok=True)
Path("results/phase51/spot_overlap_audit.json").write_text(json.dumps(out, indent=2))
if not gate["PASS"]:
    Path("results/phase51/spot_fallback_gate.json").write_text(
        json.dumps({"PASS": False, "reason": "overlap gate failed", "details": out}, indent=2)
    )
    raise SystemExit("FALLBACK_REJECTED: overlap discrepancy gate failed")

Path("results/phase51/spot_fallback_gate.json").write_text(
    json.dumps({"PASS": True, "details": out}, indent=2)
)
print(json.dumps(out, indent=2))
