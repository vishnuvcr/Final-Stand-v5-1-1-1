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
OUT = ROOT / "spot_fallback.parquet"

REPO_ID = "Jitendra12421/AlargeDatabase"
FILENAME = "INDDEX FILES/NIFTY_minute.parquet"
token = os.environ.get("HF_TOKEN")
if not token:
    raise RuntimeError("HF_TOKEN is required for the frozen Phase-51 source acquisition")

src = hf_hub_download(
    repo_id=REPO_ID,
    filename=FILENAME,
    repo_type="dataset",
    token=token,
)
if not OUT.exists() or OUT.stat().st_size != Path(src).stat().st_size:
    OUT.write_bytes(Path(src).read_bytes())

df = pd.read_parquet(OUT)
if df.empty:
    raise AssertionError("Fallback spot dataset is empty")

ts_candidates = ["timestamp", "datetime", "Datetime", "date_time", "DateTime", "time", "Date", "date"]
price_candidates = ["close", "Close", "ltp", "LTP", "price", "Price", "index_close", "IndexClose"]
ts_col = next((c for c in ts_candidates if c in df.columns), None)
price_col = next((c for c in price_candidates if c in df.columns), None)
if ts_col is None:
    raise AssertionError(f"No timestamp column found. columns={df.columns.tolist()}")
if price_col is None:
    raise AssertionError(f"No spot close/price column found. columns={df.columns.tolist()}")

ts = pd.to_datetime(df[ts_col], errors="coerce")
if ts.isna().any():
    raise AssertionError(f"Timestamp parse failure count={int(ts.isna().sum())}")
if getattr(ts.dt, "tz", None) is None:
    ts = ts.dt.tz_localize("Asia/Kolkata")
else:
    ts = ts.dt.tz_convert("Asia/Kolkata")

px = pd.to_numeric(df[price_col], errors="coerce")
if px.isna().any():
    raise AssertionError(f"Price parse failure count={int(px.isna().sum())}")
if (px <= 0).any():
    raise AssertionError("Non-positive NIFTY spot prices found")

work = pd.DataFrame({"timestamp": ts, "close": px}).sort_values("timestamp")
dup = int(work["timestamp"].duplicated().sum())
if dup:
    raise AssertionError(f"Duplicate fallback timestamps={dup}")
if not work["timestamp"].is_monotonic_increasing:
    raise AssertionError("Fallback timestamps are not monotonic after normalization")

oos = work[(work.timestamp >= OOS_START) & (work.timestamp <= OOS_END)]
if oos.empty:
    raise AssertionError("Fallback contains no rows in frozen OOS window")

days = oos.assign(day=oos.timestamp.dt.date).groupby("day").size()
partial_days = days[days < 300]
short_session_audit = []
short_session_failures = []
gap_max = 0
gap_events = 0
for day, g in oos.groupby(oos.timestamp.dt.date):
    gs = g.timestamp.sort_values()
    diffs = gs.diff().dropna().dt.total_seconds().div(60)
    day_gap = int(diffs.max()) if len(diffs) else 0
    day_span = int((gs.max() - gs.min()).total_seconds() / 60) if len(gs) else 0
    row_count = int(len(gs))
    if row_count < 300:
        item = {
            "date": str(day),
            "rows": row_count,
            "first_timestamp": str(gs.min()),
            "last_timestamp": str(gs.max()),
            "span_minutes": day_span,
            "max_internal_gap_minutes": day_gap,
        }
        short_session_audit.append(item)
        # A legitimate shortened session can have fewer than 300 rows, but
        # it must still form a long contiguous intraday span. A tiny fragment
        # is treated as a source-coverage failure.
        if day_span < 240 or day_gap > 5 or row_count < 240:
            short_session_failures.append(item)
    if len(diffs):
        gap_max = max(gap_max, day_gap)
        gap_events += int((diffs > 5).sum())
if short_session_failures:
    raise AssertionError(f"Suspicious partial-session/source-gap dates: {short_session_failures}")
if gap_events:
    raise AssertionError(f"OOS internal timestamp gaps >5 minutes: {gap_events}")

assert work.timestamp.min() <= OOS_START, f"fallback starts after OOS start: {work.timestamp.min()}"
assert work.timestamp.max() >= OOS_END, f"fallback ends before OOS end: {work.timestamp.max()}"
assert len(oos) >= 18000, f"unexpectedly small OOS row count: {len(oos)}"

manifest = {
    "source": {"repo_id": REPO_ID, "filename": FILENAME},
    "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
    "bytes": OUT.stat().st_size,
    "columns": df.columns.tolist(),
    "resolved_timestamp_column": ts_col,
    "resolved_price_column": price_col,
    "full_min_timestamp": str(work.timestamp.min()),
    "full_max_timestamp": str(work.timestamp.max()),
    "oos_window": ["2026-04-21", "2026-08-04"],
    "oos_rows": int(len(oos)),
    "oos_first_timestamp": str(oos.timestamp.min()),
    "oos_last_timestamp": str(oos.timestamp.max()),
    "oos_distinct_days": int(days.size),
    "oos_min_rows_per_present_day": int(days.min()),
    "oos_max_rows_per_present_day": int(days.max()),
    "short_session_audit": short_session_audit,
    "oos_max_internal_gap_minutes": gap_max,
    "oos_gap_events_gt5min": gap_events,
    "duplicate_timestamps": dup,
}

Path("results/phase51").mkdir(parents=True, exist_ok=True)
Path("results/phase51/spot_fallback_manifest.json").write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2))
