#!/usr/bin/env python3
"""Build strictly lagged NIFTY daily OI / EOD futures-basis factors from NSE F&O bhavcopy.

This supplement is not intraday futures data and cannot repair missing one-minute
option rows. It uses only the prior available trading session at a 10:00 entry.
Raw ZIPs live in the Actions cache; only normalized feature outputs and hashes are
persisted to the repository.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "results" / "phase52" / "base_replay"
BASE_MATRIX = BASE / "full_ready_made_trade_matrix.csv.gz"
BASE_MANIFEST = BASE / "manifest.json"
OUT = ROOT / "results" / "phase52" / "daily_bhavcopy"
CACHE = Path.home() / ".cache" / "phase52" / "nse_fno_bhavcopy"
HF_REPO = "thetrademarkk/india-index-options-1m"
NSE_REPO = "SantoshSrinivas79/NSE-FNO-Data-bank"
TZ = "Asia/Kolkata"
UA = "FinalStand-Phase52-Research/1.0 (source audit; no execution)"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": UA, "Accept": "application/vnd.github+json"})


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def api_get(url: str, token: str | None, timeout: int = 60) -> requests.Response:
    headers = {}
    if token:
        headers["Authorization"] = "Bearer " + token
    last = None
    for attempt in range(5):
        try:
            r = SESSION.get(url, headers=headers, timeout=timeout)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(min(2 ** attempt, 20))
                last = RuntimeError("HTTP " + str(r.status_code))
                continue
            r.raise_for_status()
            return r
        except Exception as exc:
            last = exc
            if attempt < 4:
                time.sleep(min(2 ** attempt, 20))
    raise RuntimeError(f"source request failed: {url}: {type(last).__name__ if last else 'unknown'}")


def session_dates_from_index(revision: str, token: str | None) -> tuple[pd.DataFrame, str]:
    path = hf_hub_download(
        repo_id=HF_REPO, filename="index/NIFTY.parquet", repo_type="dataset",
        revision=revision, token=token,
    )
    idx = pd.read_parquet(path, columns=["timestamp", "close"])
    ts = pd.to_datetime(idx["timestamp"], errors="coerce")
    idx["timestamp"] = ts.dt.tz_localize(TZ) if ts.dt.tz is None else ts.dt.tz_convert(TZ)
    idx["close"] = pd.to_numeric(idx["close"], errors="coerce")
    idx = idx.dropna(subset=["timestamp", "close"]).sort_values("timestamp")
    idx["session_date"] = idx["timestamp"].dt.strftime("%Y-%m-%d")
    closes = idx.groupby("session_date", sort=True).tail(1)[["session_date", "timestamp", "close"]]
    closes = closes.rename(columns={"close": "nifty_spot_eod"}).reset_index(drop=True)
    return closes, sha256_bytes(Path(path).read_bytes())


def _get_first(raw: pd.DataFrame, *names: str) -> pd.Series | None:
    for name in names:
        if name in raw.columns:
            return raw[name]
    return None


def _numeric(raw: pd.DataFrame, names: tuple[str, ...]) -> pd.Series:
    s = _get_first(raw, *names)
    return pd.to_numeric(s, errors="coerce") if s is not None else pd.Series(np.nan, index=raw.index)


def parse_bhavcopy(raw_bytes: bytes, session_date: str) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Normalize both NSE legacy and UDiFF daily F&O schemas."""
    with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
        csvs = [n for n in zf.namelist() if n.lower().endswith((".csv", ".txt"))]
        if not csvs:
            raise ValueError("ZIP has no CSV/TXT member")
        with zf.open(csvs[0]) as handle:
            raw = pd.read_csv(handle, low_memory=False)
    raw.columns = [str(c).strip() for c in raw.columns]
    if {"SYMBOL", "EXPIRY_DT", "STRIKE_PR", "OPTION_TYP", "CLOSE"}.issubset(raw.columns):
        symbol = raw["SYMBOL"].astype(str).str.upper().str.strip()
        expiry = pd.to_datetime(raw["EXPIRY_DT"], errors="coerce").dt.strftime("%Y-%m-%d")
        strike = _numeric(raw, ("STRIKE_PR",))
        typ = raw["OPTION_TYP"].astype(str).str.upper().str.strip()
        inst = raw["INSTRUMENT"].astype(str).str.upper().str.strip() if "INSTRUMENT" in raw else pd.Series("", index=raw.index)
        close = _numeric(raw, ("CLOSE",))
        volume = _numeric(raw, ("CONTRACTS",))
        oi = _numeric(raw, ("OPEN_INT",))
        underlying_mask = symbol.eq("NIFTY")
        option_mask = underlying_mask & typ.isin(["CE", "PE"])
        future_mask = underlying_mask & inst.str.contains("FUT", na=False)
    elif {"TckrSymb", "XpryDt", "ClsPric"}.issubset(raw.columns):
        symbol = raw["TckrSymb"].astype(str).str.upper().str.strip()
        expiry = pd.to_datetime(raw["XpryDt"], errors="coerce").dt.strftime("%Y-%m-%d")
        strike = _numeric(raw, ("StrkPric",))
        opt_source = raw["OptnTp"] if "OptnTp" in raw else pd.Series("", index=raw.index)
        typ = opt_source.astype(str).str.upper().str.strip()
        inst = raw["FinInstrmTp"].astype(str).str.upper().str.strip() if "FinInstrmTp" in raw else pd.Series("", index=raw.index)
        close = _numeric(raw, ("ClsPric",))
        volume = _numeric(raw, ("TtlTradgVol",))
        oi = _numeric(raw, ("OpnIntrst",))
        underlying_mask = symbol.eq("NIFTY")
        option_mask = underlying_mask & typ.isin(["CE", "PE"])
        future_mask = underlying_mask & inst.str.contains("FUT", na=False)
        if not future_mask.any() and "OptnTp" in raw:
            future_mask = underlying_mask & raw["OptnTp"].isna() & expiry.notna() & close.notna() & inst.str.contains("FUT", na=False)
    else:
        raise ValueError("Unrecognized NSE F&O bhavcopy schema")

    norm = pd.DataFrame({
        "session_date": session_date,
        "expiry": expiry,
        "strike": strike,
        "option_type": typ,
        "instrument": inst,
        "close": close,
        "volume": volume,
        "open_interest": oi,
    }, index=raw.index)
    opts = norm.loc[option_mask].dropna(subset=["expiry", "strike", "close"]).copy()
    opts = opts[(opts["expiry"] >= session_date) & (opts["close"] >= 0)]
    futs = norm.loc[future_mask].dropna(subset=["expiry", "close"]).copy()
    futs = futs[(futs["expiry"] >= session_date) & (futs["close"] > 0)]
    meta = {
        "raw_rows": int(len(raw)),
        "nifty_option_rows": int(len(opts)),
        "nifty_future_rows": int(len(futs)),
        "schema": "legacy" if "SYMBOL" in raw.columns else "udiff",
        "columns": list(raw.columns),
    }
    return opts.reset_index(drop=True), futs.reset_index(drop=True), meta


def archive_path_map(tree: list[dict[str, Any]]) -> dict[str, str]:
    result: dict[str, str] = {}
    month_codes = {m.upper(): i for i, m in enumerate(
        ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], 1
    )}
    for item in tree:
        path = item.get("path", "")
        if not (path.startswith("data/") and path.endswith(".zip")):
            continue
        name = path.rsplit("/", 1)[-1]
        modern = re.fullmatch(r"BhavCopy_NSE_FO_0_0_0_(\d{8})_F_0000\.csv\.zip", name)
        legacy = re.fullmatch(r"fo(\d{2})([A-Z]{3})(\d{4})bhav\.csv\.zip", name)
        if modern:
            d = pd.to_datetime(modern.group(1), format="%Y%m%d", errors="coerce")
        elif legacy and legacy.group(2) in month_codes:
            d = pd.Timestamp(year=int(legacy.group(3)), month=month_codes[legacy.group(2)],
                             day=int(legacy.group(1)))
        else:
            continue
        if not pd.isna(d):
            result[pd.Timestamp(d).strftime("%Y-%m-%d")] = path
    return result


def download_zip(session_date: str, relative_path: str, commit_sha: str, github_token: str | None) -> tuple[bytes, str, bool]:
    CACHE.mkdir(parents=True, exist_ok=True)
    dest = CACHE / commit_sha / f"{session_date}.zip"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        b = dest.read_bytes()
        if b[:2] == b"PK":
            return b, sha256_bytes(b), True
        dest.unlink(missing_ok=True)
    url = f"https://raw.githubusercontent.com/{NSE_REPO}/{commit_sha}/{relative_path}"
    response = api_get(url, github_token)
    raw = response.content
    if raw[:2] != b"PK":
        raise ValueError("Downloaded daily archive is not a ZIP")
    digest = sha256_bytes(raw)
    tmp = dest.with_suffix(".tmp")
    tmp.write_bytes(raw)
    tmp.replace(dest)
    return raw, digest, False


def summarize_event(
    session_date: str, previous_date: str, event: Any, option_df: pd.DataFrame,
    future_df: pd.DataFrame, spot_map: dict[str, float],
) -> dict[str, Any]:
    target_expiry = pd.Timestamp(event.expiry).strftime("%Y-%m-%d")
    spot = spot_map.get(session_date, np.nan)
    out: dict[str, Any] = {
        "expiry": target_expiry,
        "entry_ts": str(event.entry_ts),
        "split": str(event.split),
        "factor_session_date": session_date,
        "pre_factor_session_date": previous_date,
        "nifty_spot_eod": spot,
    }
    opt = option_df[option_df.expiry == target_expiry].copy() if not option_df.empty else option_df
    if opt.empty or not np.isfinite(spot) or spot <= 0:
        out.update({
            "option_target_expiry_rows": int(len(opt)),
            "option_oi_pcr_near_atm_5steps": np.nan,
            "option_volume_pcr_near_atm_5steps": np.nan,
            "option_call_oi_near_atm": np.nan,
            "option_put_oi_near_atm": np.nan,
            "option_call_volume_near_atm": np.nan,
            "option_put_volume_near_atm": np.nan,
        })
    else:
        strikes = np.sort(pd.to_numeric(opt.strike, errors="coerce").dropna().unique())
        diffs = np.diff(strikes)
        diffs = np.round(diffs[diffs > 0], 8)
        step = float(pd.Series(diffs).mode().iloc[0]) if len(diffs) else np.nan
        atm = float(strikes[np.argmin(np.abs(strikes - spot))]) if len(strikes) else np.nan
        local = opt[(opt.strike.astype(float) - atm).abs() <= (5.01 * step)] if np.isfinite(step) and step > 0 else opt.iloc[0:0]
        def sum_min(series: pd.Series) -> float:
            return float(pd.to_numeric(series, errors="coerce").sum(min_count=1))
        call_oi = sum_min(local.loc[local.option_type == "CE", "open_interest"])
        put_oi = sum_min(local.loc[local.option_type == "PE", "open_interest"])
        call_vol = sum_min(local.loc[local.option_type == "CE", "volume"])
        put_vol = sum_min(local.loc[local.option_type == "PE", "volume"])
        out.update({
            "option_target_expiry_rows": int(len(opt)),
            "option_oi_pcr_near_atm_5steps": put_oi / call_oi if np.isfinite(put_oi) and np.isfinite(call_oi) and call_oi > 0 else np.nan,
            "option_volume_pcr_near_atm_5steps": put_vol / call_vol if np.isfinite(put_vol) and np.isfinite(call_vol) and call_vol > 0 else np.nan,
            "option_call_oi_near_atm": call_oi,
            "option_put_oi_near_atm": put_oi,
            "option_call_volume_near_atm": call_vol,
            "option_put_volume_near_atm": put_vol,
        })

    # Daily futures basis is strictly lagged EOD basis, not an intraday/traded
    # lead-lag measure. Keep futures expiry in the feature row for auditability.
    fut = future_df[future_df.expiry >= session_date].copy() if not future_df.empty else future_df
    if fut.empty or not np.isfinite(spot) or spot <= 0:
        out.update({"front_future_expiry": None, "front_future_close": np.nan,
                    "front_future_basis_points": np.nan, "front_future_basis_bps": np.nan,
                    "front_future_volume": np.nan, "front_future_open_interest": np.nan})
    else:
        fut["expiry_dt"] = pd.to_datetime(fut.expiry, errors="coerce")
        fut = fut.sort_values(["expiry_dt", "close"])
        row = fut.iloc[0]
        close = float(row.close)
        out.update({
            "front_future_expiry": str(row.expiry),
            "front_future_close": close,
            "front_future_basis_points": close - spot,
            "front_future_basis_bps": (close / spot - 1.0) * 10000.0,
            "front_future_volume": float(row.volume) if np.isfinite(row.volume) else np.nan,
            "front_future_open_interest": float(row.open_interest) if np.isfinite(row.open_interest) else np.nan,
        })
    return out


def main() -> int:
    if not BASE_MATRIX.exists() or not BASE_MANIFEST.exists():
        raise FileNotFoundError("Pinned base replay is missing; run research/phase52/base_replay.py first")
    base_manifest = json.loads(BASE_MANIFEST.read_text(encoding="utf-8"))
    hf_revision = str(base_manifest["dataset_revision"])
    token = os.getenv("HF_TOKEN") or None
    github_token = os.getenv("GITHUB_TOKEN") or None
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)

    # Freeze the source code SHA and tree at execution start.
    commit = api_get(f"https://api.github.com/repos/{NSE_REPO}/commits/main", github_token)
    commit_data = commit.json()
    source_commit = commit_data.get("sha")
    if not source_commit:
        raise RuntimeError("Could not resolve immutable NSE F&O archive commit")
    tree_json = api_get(f"https://api.github.com/repos/{NSE_REPO}/git/trees/{source_commit}?recursive=1", github_token).json()
    if tree_json.get("truncated"):
        raise RuntimeError("NSE archive tree API response was truncated; refuse incomplete session coverage")
    paths = archive_path_map(tree_json.get("tree", []))

    closes, index_sha = session_dates_from_index(hf_revision, token)
    closes["date_dt"] = pd.to_datetime(closes.session_date)
    sorted_dates = list(closes.session_date)
    spot_map = dict(zip(closes.session_date, closes.nifty_spot_eod.astype(float)))
    base = pd.read_csv(BASE_MATRIX, compression="gzip", usecols=["expiry", "entry_ts", "split"])
    base["entry_ts"] = pd.to_datetime(base.entry_ts, errors="coerce")
    events = base.dropna(subset=["expiry", "entry_ts", "split"]).drop_duplicates(["expiry", "entry_ts", "split"])
    event_rows = []
    required_dates: set[str] = set()
    for ev in events.itertuples(index=False):
        date_str = pd.Timestamp(ev.entry_ts).strftime("%Y-%m-%d")
        prior_dates = [d for d in sorted_dates if d < date_str]
        if len(prior_dates) < 2:
            event_rows.append({"expiry": str(ev.expiry), "entry_ts": str(ev.entry_ts), "split": str(ev.split),
                               "reason": "insufficient_prior_index_sessions"})
            continue
        factor_date, pre_factor_date = prior_dates[-1], prior_dates[-2]
        required_dates.update([factor_date, pre_factor_date])
        event_rows.append({"expiry": str(ev.expiry), "entry_ts": str(ev.entry_ts), "split": str(ev.split),
                           "factor_date": factor_date, "pre_factor_date": pre_factor_date})
    dates = sorted(required_dates)
    cache_hits = downloaded = missing_paths = failed_files = 0
    daily: dict[str, tuple[pd.DataFrame, pd.DataFrame]] = {}
    source_records = []
    for i, d in enumerate(dates, 1):
        rel = paths.get(d)
        if rel is None:
            missing_paths += 1
            source_records.append({"session_date": d, "status": "SOURCE_PATH_MISSING"})
            continue
        try:
            content, digest, hit = download_zip(d, rel, source_commit, github_token)
            opts, futs, meta = parse_bhavcopy(content, d)
            cache_hits += int(hit)
            downloaded += int(not hit)
            daily[d] = (opts, futs)
            source_records.append({
                "session_date": d, "path": rel, "sha256": digest,
                "cache_hit": hit, "status": "PASS",
                "schema": meta["schema"], "raw_rows": meta["raw_rows"],
                "nifty_option_rows": meta["nifty_option_rows"], "nifty_future_rows": meta["nifty_future_rows"],
                "archive_commit": source_commit,
            })
        except Exception as exc:
            failed_files += 1
            source_records.append({"session_date": d, "path": rel, "status": "ERROR",
                                   "error_type": type(exc).__name__, "archive_commit": source_commit})
        if i % 25 == 0 or i == len(dates):
            print(json.dumps({"event": "BHAVCOPY_PROGRESS", "sessions_done": i, "sessions_total": len(dates),
                              "cache_hits": cache_hits, "downloaded": downloaded,
                              "missing_paths": missing_paths, "failed_files": failed_files}), flush=True)

    # Build event features with prior-session EOD values; report no-data gaps explicitly.
    feature_rows = []
    gaps = []
    for ev in event_rows:
        if "factor_date" not in ev:
            gaps.append(ev)
            continue
        d, prev = ev["factor_date"], ev["pre_factor_date"]
        if d not in daily:
            gaps.append({**ev, "reason": "prior_session_bhavcopy_unavailable"})
            continue
        opts, futs = daily[d]
        row = summarize_event(d, prev, type("Event", (), {"expiry": ev["expiry"], "entry_ts": ev["entry_ts"], "split": ev["split"]}),
                              opts, futs, spot_map)
        # Previous-session OI changes only when the same factor fields exist for both sessions.
        prev_opts, prev_futs = daily.get(prev, (pd.DataFrame(), pd.DataFrame()))
        prev_row = summarize_event(prev, "", type("Event", (), {"expiry": ev["expiry"], "entry_ts": ev["entry_ts"], "split": ev["split"]}),
                                   prev_opts, prev_futs, spot_map)
        for col in ("option_call_oi_near_atm", "option_put_oi_near_atm", "front_future_open_interest"):
            now_val, prev_val = row.get(col, np.nan), prev_row.get(col, np.nan)
            row[col + "_change_pct_1d"] = (now_val / prev_val - 1.0) * 100.0 if np.isfinite(now_val) and np.isfinite(prev_val) and prev_val > 0 else np.nan
        row["archive_commit"] = source_commit
        feature_rows.append(row)
    features = pd.DataFrame(feature_rows)
    source_audit = pd.DataFrame(source_records)
    audit_path = OUT / "archive_source_audit.csv"
    feature_path = OUT / "event_factors.csv.gz"
    gaps_path = OUT / "coverage_gaps.csv"
    source_audit.to_csv(audit_path, index=False)
    features.to_csv(feature_path, index=False, compression="gzip")
    pd.DataFrame(gaps).to_csv(gaps_path, index=False)

    report = {
        "status": "DAILY_EOD_FACTOR_BUILD_WITH_COVERAGE_AUDIT",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "hf_option_dataset_revision": hf_revision,
        "hf_index_file_sha256": index_sha,
        "nse_fno_archive_repo": NSE_REPO,
        "nse_fno_archive_commit_sha": source_commit,
        "nse_fno_archive_repository_code_license": "MIT; does not grant rights to bundled NSE market data",
        "nse_market_data_rights": "NSE terms/rightsholder review required; data is daily EOD only and not an intraday quote feed",
        "expected_event_rows": int(len(event_rows)),
        "feature_rows": int(len(features)),
        "feature_event_coverage": float(len(features) / len(event_rows)) if event_rows else 0.0,
        "unique_prior_sessions_required": int(len(dates)),
        "archive_downloaded_sessions": int(downloaded),
        "archive_cache_hit_sessions": int(cache_hits),
        "missing_archive_paths": int(missing_paths),
        "archive_file_errors": int(failed_files),
        "gap_rows": int(len(gaps)),
        "futures_basis_type": "prior-session front-month NIFTY futures EOD close minus same-session NIFTY index EOD close; not intraday lead-lag",
        "feature_timing": "strictly prior available index session to the event entry date; feature session is at least one trading session before entry; no fills from event-day EOD",
        "outputs": {
            "features": str(feature_path.relative_to(ROOT)),
            "archive_audit": str(audit_path.relative_to(ROOT)),
            "coverage_gaps": str(gaps_path.relative_to(ROOT)),
        }
    }
    write_json(OUT / "manifest.json", report)
    (OUT / "manifest.sha256").write_text(sha256_bytes((OUT / "manifest.json").read_bytes()) + "  manifest.json\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


def _self_test() -> None:
    # Tiny legacy-format fixture proves distinct option/futures detection and OI parsing.
    csv = (
        "INSTRUMENT,SYMBOL,EXPIRY_DT,STRIKE_PR,OPTION_TYP,OPEN,CLOSE,CONTRACTS,OPEN_INT\n"
        "OPTIDX,NIFTY,29-Oct-2026,25000,CE,100,110,1000,5000\n"
        "OPTIDX,NIFTY,29-Oct-2026,25000,PE,90,95,1200,7000\n"
        "FUTIDX,NIFTY,29-Oct-2026,0,XX,25010,25020,5000,90000\n"
    ).encode()
    opts, futs, meta = parse_bhavcopy(zip_bytes(csv), "2026-10-08")
    assert len(opts) == 2, f"expected 2 option rows, got {len(opts)}"
    assert len(futs) == 1, f"expected 1 futures row, got {len(futs)}"
    assert float(opts.loc[opts.option_type.eq("CE"), "open_interest"].iloc[0]) == 5000
    print("SELF_TEST_PASS: legacy bhavcopy option/OI/futures schema")


def zip_bytes(csv: bytes) -> bytes:
    out = io.BytesIO()
    with zipfile.ZipFile(out, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("fixture.csv", csv)
    return out.getvalue()


if __name__ == "__main__":
    if "--self-test" in os.sys.argv:
        _self_test()
        os.sys.argv.remove("--self-test")
    if "--self-test-only" in os.sys.argv:
        raise SystemExit(0)
    raise SystemExit(main())
