#!/usr/bin/env python3
"""Selected-strike OHLC/OI coverage audit for ATM-offset legs; no P&L.

Audits exact contract bars for strike-rank offsets -6..+6 around nearest ATM
for every preregistered event. ABS_DELTA resolution is deliberately not inferred
from minute close prices; it needs a separate validated point-in-time IV/delta
method. This audit is not a substitute for per-configuration fill replay.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "results" / "phase52" / "base_replay" / "manifest.json"
EVENTS = ROOT / "results" / "phase52" / "configuration_event_universe" / "expected_events.csv"
OUT = ROOT / "results" / "phase52" / "selected_strike_coverage"
HF_REPO = "thetrademarkk/india-index-options-1m"
TZ = "Asia/Kolkata"
OFFSETS = tuple(range(-6, 7))
MIN_OI = 100


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def to_ist(series: pd.Series) -> pd.Series:
    x = pd.to_datetime(series, errors="coerce")
    return x.dt.tz_localize(TZ) if x.dt.tz is None else x.dt.tz_convert(TZ)


def valid_ohlc(frame: pd.DataFrame) -> pd.Series:
    cols = ["open", "high", "low", "close"]
    vals = frame[cols].apply(pd.to_numeric, errors="coerce")
    finite = np.isfinite(vals).all(axis=1)
    positive = (vals > 0).all(axis=1)
    ordered = (vals["low"] <= vals[["open", "close"]].min(axis=1)) & (vals["high"] >= vals[["open", "close"]].max(axis=1)) & (vals["high"] >= vals["low"])
    return finite & positive & ordered


def select_ranked_strikes(strikes: list[float], spot: float) -> tuple[list[float], int]:
    """Nearest listed strike is rank 0; ties deterministically choose lower strike."""
    ordered = sorted({float(x) for x in strikes if np.isfinite(float(x))})
    if not ordered or not np.isfinite(spot):
        return [], -1
    atm_idx = min(range(len(ordered)), key=lambda i: (abs(ordered[i] - spot), ordered[i]))
    return ordered, atm_idx


def _self_test() -> None:
    strikes, idx = select_ranked_strikes([22000, 22100, 22200, 22300], 22150)
    assert strikes[idx] == 22100  # deterministic lower-strike tie break
    assert strikes[idx + 1] == 22200
    frame = pd.DataFrame({"open":[10, 10], "high":[12, 9], "low":[8, 11], "close":[11, 10]})
    assert valid_ohlc(frame).tolist() == [True, False]
    assert select_ranked_strikes([], 22000) == ([], -1)


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        print("selected-strike coverage self-test PASS")
        return 0

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    revision = manifest["dataset_revision"]
    token = os.environ.get("HF_TOKEN")
    events = pd.read_csv(EVENTS, dtype={"event_id": str})
    index_path = Path(hf_hub_download(
        repo_id=HF_REPO, filename="index/NIFTY.parquet", repo_type="dataset",
        revision=revision, token=token
    ))
    index = pd.read_parquet(index_path, columns=["timestamp", "close"])
    index["timestamp"] = to_ist(index["timestamp"])
    index["close"] = pd.to_numeric(index["close"], errors="coerce")
    index = index.dropna(subset=["timestamp", "close"]).drop_duplicates("timestamp", keep="last")
    spot_map = dict(zip(index["timestamp"].map(lambda x: x.isoformat()), index["close"].astype(float)))

    out_rows: list[dict[str, Any]] = []
    file_audit: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for expiry, group in events.groupby("expiry", sort=True):
        filename = f"options/NIFTY/{expiry}.parquet"
        try:
            p = Path(hf_hub_download(repo_id=HF_REPO, filename=filename, repo_type="dataset", revision=revision, token=token))
            digest = sha256_file(p)
            df = pd.read_parquet(p, columns=["timestamp","option_type","strike","open","high","low","close","volume","open_interest"])
            df["timestamp"] = to_ist(df["timestamp"])
            df["option_type"] = df["option_type"].astype(str).str.upper().str.strip()
            for col in ["strike","open","high","low","close","volume","open_interest"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            df = df.dropna(subset=["timestamp","strike"])
            df["valid_ohlc"] = valid_ohlc(df)
            strikes, _ = select_ranked_strikes(df["strike"].dropna().unique().tolist(), 1.0)
            strikes = sorted(strikes)
            target_day = pd.Timestamp(expiry, tz=TZ).normalize()
            expiry_rows = df[(df["timestamp"] >= target_day) & (df["timestamp"] <= target_day + pd.Timedelta(hours=15, minutes=29))]
            if expiry_rows.empty:
                expiry_exit = None
            else:
                counts = expiry_rows.pivot_table(index="timestamp", columns="option_type", values="strike", aggfunc="count", fill_value=0)
                both = counts[(counts.get("CE", 0) > 0) & (counts.get("PE", 0) > 0)] if "CE" in counts and "PE" in counts else counts.iloc[0:0]
                expiry_exit = both.index.max() if len(both) else None
            file_audit.append({"expiry":expiry,"file":filename,"sha256":digest,"bytes":int(p.stat().st_size),"rows":int(len(df)),"strike_count":len(strikes),"expiry_exit_common_ts":expiry_exit.isoformat() if expiry_exit is not None else None,"status":"PASS"})
        except Exception as exc:
            failures.append({"expiry":str(expiry),"error_type":type(exc).__name__})
            file_audit.append({"expiry":expiry,"file":filename,"status":"SOURCE_ERROR","error_type":type(exc).__name__})
            continue

        for ev in group.itertuples(index=False):
            entry_ts = pd.Timestamp(ev.entry_ts)
            if entry_ts.tzinfo is None: entry_ts = entry_ts.tz_localize(TZ)
            else: entry_ts = entry_ts.tz_convert(TZ)
            spot = spot_map.get(str(entry_ts), np.nan)
            ordered, atm_idx = select_ranked_strikes(strikes, spot)
            entry = df[df["timestamp"].eq(entry_ts)]
            exit_1515_ts = entry_ts.normalize() + pd.Timedelta(hours=15, minutes=15)
            exit_1515 = df[df["timestamp"].eq(exit_1515_ts)]
            expiry_exit_ts = pd.Timestamp(expiry_exit) if expiry_exit is not None else None
            exit_expiry = df[df["timestamp"].eq(expiry_exit_ts)] if expiry_exit_ts is not None else df.iloc[0:0]
            for offset in OFFSETS:
                rank = atm_idx + offset
                strike = ordered[rank] if 0 <= rank < len(ordered) else np.nan
                for typ in ("CE","PE"):
                    er = entry[(entry["option_type"] == typ) & (entry["strike"] == strike)] if np.isfinite(strike) else entry.iloc[0:0]
                    r15 = exit_1515[(exit_1515["option_type"] == typ) & (exit_1515["strike"] == strike)] if np.isfinite(strike) else exit_1515.iloc[0:0]
                    rexp = exit_expiry[(exit_expiry["option_type"] == typ) & (exit_expiry["strike"] == strike)] if np.isfinite(strike) else exit_expiry.iloc[0:0]
                    entry_ok = len(er) == 1 and bool(er.iloc[0]["valid_ohlc"]) and pd.notna(er.iloc[0]["open_interest"]) and er.iloc[0]["open_interest"] >= MIN_OI
                    exit15_ok = len(r15) == 1 and bool(r15.iloc[0]["valid_ohlc"])
                    exit_exp_ok = len(rexp) == 1 and bool(rexp.iloc[0]["valid_ohlc"])
                    out_rows.append({
                        "event_id":str(ev.event_id),"expiry":expiry,"split":str(ev.split),"entry_ts":entry_ts.isoformat(),
                        "entry_dte_calendar_days":int(ev.entry_dte_calendar_days),"entry_time_ist":str(ev.entry_time_ist),
                        "spot_at_entry":float(spot) if np.isfinite(spot) else np.nan,"atm_strike":ordered[atm_idx] if 0 <= atm_idx < len(ordered) else np.nan,
                        "strike_rank_offset":offset,"selected_strike":float(strike) if np.isfinite(strike) else np.nan,"option_type":typ,
                        "index_exact_entry":bool(ev.index_has_exact_entry_timestamp),"entry_row_count":len(er),
                        "entry_ohlc_valid":bool(len(er)==1 and er.iloc[0]["valid_ohlc"]),"entry_oi":float(er.iloc[0]["open_interest"]) if len(er)==1 and pd.notna(er.iloc[0]["open_interest"]) else np.nan,
                        "entry_oi_ge_100":bool(entry_ok),"exit_1515_ohlc_valid":bool(exit15_ok),
                        "expiry_exit_ts":expiry_exit_ts.isoformat() if expiry_exit_ts is not None else None,"expiry_exit_ohlc_valid":bool(exit_exp_ok),
                        "abs_delta_selection_status":"BLOCKED_NO_VALIDATED_POINT_IN_TIME_DELTA_RESOLVER","pnl_status":"NOT_BACKTESTED"
                    })
    OUT.mkdir(parents=True, exist_ok=True)
    detail = pd.DataFrame(out_rows)
    detail_path = OUT / "atm_offset_leg_coverage.csv.gz"
    detail.to_csv(detail_path, index=False, compression="gzip")
    pd.DataFrame(file_audit).to_csv(OUT / "source_file_audit.csv", index=False)
    pd.DataFrame(failures, columns=["expiry","error_type"]).to_csv(OUT / "source_errors.csv", index=False)
    summary = {
        "status":"SELECTED_STRIKE_ATM_OFFSET_COVERAGE_AUDIT_COMPLETE" if not failures else "SELECTED_STRIKE_ATM_OFFSET_COVERAGE_WITH_SOURCE_ERRORS",
        "created_at_utc":datetime.now(timezone.utc).isoformat(),"dataset":HF_REPO,"dataset_revision":revision,
        "index_file_sha256":sha256_file(index_path),"expected_events":int(len(events)),"audited_events":int(events["event_id"].nunique()),
        "source_expiry_files_expected":int(events["expiry"].nunique()),"source_expiry_files_audited":int(len(file_audit)),
        "source_file_errors":len(failures),"strike_offsets":list(OFFSETS),"option_type_rows":int(len(detail)),
        "entry_oi_ge_100_rows":int(detail["entry_oi_ge_100"].sum()),
        "entry_oi_ge_100_and_exact_index_rows":int((detail["entry_oi_ge_100"] & detail["index_exact_entry"]).sum()),
        "expiry_exit_ohlc_valid_rows":int(detail["expiry_exit_ohlc_valid"].sum()),
        "exact_entry_and_expiry_exit_rows":int((detail["entry_oi_ge_100"] & detail["index_exact_entry"] & detail["expiry_exit_ohlc_valid"]).sum()),
        "abs_delta":"BLOCKED: no validated point-in-time delta/IV resolver; do not proxy delta from close without separate methodology.",
        "interpretation":"Selected strike rank coverage only; a complete strategy still needs per-config leg combination, sizing, execution-price/slippage and path-dependent exit replay. No P&L.",
        "outputs":{"detail":str(detail_path.relative_to(ROOT)),"source_audit":"results/phase52/selected_strike_coverage/source_file_audit.csv","source_errors":"results/phase52/selected_strike_coverage/source_errors.csv"}
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
