#!/usr/bin/env python3
"""Point-in-time model-delta selection audit; diagnostic only, no P&L.

Uses exact timestamp option-bar close and exact timestamp NIFTY index close,
a European Black-Scholes model, 6% continuously compounded rate, zero dividend
yield, and exact expiry time 15:30 IST. Minute-bar close is not a bid/ask quote;
outputs must not be called exchange Greeks or executable fills.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "results" / "phase52" / "base_replay" / "manifest.json"
EVENTS = ROOT / "results" / "phase52" / "configuration_event_universe" / "expected_events.csv"
OUT = ROOT / "results" / "phase52" / "delta_selection_audit"
HF_REPO = "thetrademarkk/india-index-options-1m"
TZ = "Asia/Kolkata"
RATE = 0.06
DIVIDEND_YIELD = 0.0
MIN_OI = 100
TARGET_ABS_DELTAS = (0.15, 0.30)
YEAR_SECONDS = 365.25 * 24 * 60 * 60


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bs_price(spot: float, strike: float, tau: float, sigma: float, rate: float, q: float, typ: str) -> float:
    if min(spot, strike, sigma) <= 0 or tau <= 0:
        intrinsic = max(spot - strike, 0.0) if typ == "CE" else max(strike - spot, 0.0)
        return intrinsic
    root_t = math.sqrt(tau)
    d1 = (math.log(spot / strike) + (rate - q + 0.5 * sigma * sigma) * tau) / (sigma * root_t)
    d2 = d1 - sigma * root_t
    if typ == "CE":
        return spot * math.exp(-q * tau) * cdf(d1) - strike * math.exp(-rate * tau) * cdf(d2)
    return strike * math.exp(-rate * tau) * cdf(-d2) - spot * math.exp(-q * tau) * cdf(-d1)


def bs_delta(spot: float, strike: float, tau: float, sigma: float, rate: float, q: float, typ: str) -> float:
    if min(spot, strike, sigma) <= 0 or tau <= 0:
        if typ == "CE":
            return 1.0 if spot > strike else (0.5 if spot == strike else 0.0)
        return -1.0 if spot < strike else (-0.5 if spot == strike else 0.0)
    d1 = (math.log(spot / strike) + (rate - q + 0.5 * sigma * sigma) * tau) / (sigma * math.sqrt(tau))
    if typ == "CE":
        return math.exp(-q * tau) * cdf(d1)
    return math.exp(-q * tau) * (cdf(d1) - 1.0)


def implied_vol(spot: float, strike: float, tau: float, premium: float, rate: float, q: float, typ: str) -> tuple[float | None, str]:
    typ = typ.upper()
    if typ not in {"CE", "PE"} or not all(math.isfinite(x) for x in (spot, strike, tau, premium, rate, q)):
        return None, "INVALID_INPUT"
    if spot <= 0 or strike <= 0 or tau <= 0 or premium <= 0:
        return None, "NONPOSITIVE_INPUT_OR_EXPIRED"
    intrinsic = max(spot - strike, 0.0) if typ == "CE" else max(strike - spot, 0.0)
    upper = spot * math.exp(-q * tau) if typ == "CE" else strike * math.exp(-rate * tau)
    tol = max(1e-6, 1e-7 * max(spot, strike, premium))
    if premium < intrinsic - tol:
        return None, "PREMIUM_BELOW_INTRINSIC"
    if premium >= upper - tol:
        return None, "PREMIUM_AT_OR_ABOVE_MODEL_UPPER_BOUND"
    lo, hi = 1e-5, 5.0
    p_lo = bs_price(spot, strike, tau, lo, rate, q, typ)
    p_hi = bs_price(spot, strike, tau, hi, rate, q, typ)
    if premium < p_lo - tol or premium > p_hi + tol:
        return None, "PREMIUM_OUTSIDE_IV_BRACKET"
    for _ in range(70):
        mid = (lo + hi) / 2.0
        value = bs_price(spot, strike, tau, mid, rate, q, typ)
        if value < premium:
            lo = mid
        else:
            hi = mid
    sigma = (lo + hi) / 2.0
    if not math.isfinite(sigma) or sigma <= 0:
        return None, "IV_SOLVER_NONFINITE"
    return sigma, "PASS"


def valid_ohlc(row: pd.Series) -> bool:
    try:
        o, h, l, c = (float(row[k]) for k in ("open", "high", "low", "close"))
    except (TypeError, ValueError, KeyError):
        return False
    return all(math.isfinite(x) and x > 0 for x in (o, h, l, c)) and l <= min(o, c) and h >= max(o, c) and h >= l


def _self_test() -> None:
    s, k, t, v, r, q = 22000.0, 22100.0, 7 / 365.25, 0.18, RATE, DIVIDEND_YIELD
    for typ in ("CE", "PE"):
        premium = bs_price(s, k, t, v, r, q, typ)
        iv, status = implied_vol(s, k, t, premium, r, q, typ)
        assert status == "PASS" and iv is not None and abs(iv - v) < 1e-7, (typ, iv, status)
        delta = bs_delta(s, k, t, iv, r, q, typ)
        assert 0 <= delta <= 1 if typ == "CE" else -1 <= delta <= 0
    assert implied_vol(22000, 22100, t, 0.01, r, q, "CE")[1] == "PREMIUM_BELOW_INTRINSIC"
    assert implied_vol(22000, 22100, 0, 5, r, q, "CE")[1] == "NONPOSITIVE_INPUT_OR_EXPIRED"


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        print("point-in-time IV/delta resolver self-test PASS")
        return 0

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    revision = manifest["dataset_revision"]
    token = os.environ.get("HF_TOKEN")
    events = pd.read_csv(EVENTS, dtype={"event_id": str})
    index_path = Path(hf_hub_download(repo_id=HF_REPO, filename="index/NIFTY.parquet", repo_type="dataset", revision=revision, token=token))
    index = pd.read_parquet(index_path, columns=["timestamp", "close"])
    ix = pd.to_datetime(index["timestamp"], errors="coerce")
    index["timestamp"] = ix.dt.tz_localize(TZ) if ix.dt.tz is None else ix.dt.tz_convert(TZ)
    index["close"] = pd.to_numeric(index["close"], errors="coerce")
    index = index.dropna(subset=["timestamp", "close"]).drop_duplicates("timestamp", keep="last")
    spot_map = dict(zip(index["timestamp"].map(lambda x: x.isoformat()), index["close"].astype(float)))

    rows: list[dict[str, Any]] = []
    file_audit: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for expiry, group in events.groupby("expiry", sort=True):
        filename = f"options/NIFTY/{expiry}.parquet"
        try:
            p = Path(hf_hub_download(repo_id=HF_REPO, filename=filename, repo_type="dataset", revision=revision, token=token))
            digest = sha256_file(p)
            df = pd.read_parquet(p, columns=["timestamp", "option_type", "strike", "open", "high", "low", "close", "open_interest"])
            ts = pd.to_datetime(df["timestamp"], errors="coerce")
            df["timestamp"] = ts.dt.tz_localize(TZ) if ts.dt.tz is None else ts.dt.tz_convert(TZ)
            for col in ("strike", "open", "high", "low", "close", "open_interest"):
                df[col] = pd.to_numeric(df[col], errors="coerce")
            df["option_type"] = df["option_type"].astype(str).str.upper().str.strip()
            df = df.dropna(subset=["timestamp", "strike"])
            by_ts = {stamp: frame for stamp, frame in df.groupby("timestamp", sort=False)}
            empty = df.iloc[0:0]
            file_audit.append({"expiry": expiry, "file": filename, "sha256": digest, "bytes": int(p.stat().st_size), "rows": int(len(df)), "status": "PASS"})
        except Exception as exc:
            errors.append({"expiry": str(expiry), "error_type": type(exc).__name__})
            file_audit.append({"expiry": expiry, "file": filename, "status": "SOURCE_ERROR", "error_type": type(exc).__name__})
            continue

        expiry_ts = pd.Timestamp(expiry, tz=TZ) + pd.Timedelta(hours=15, minutes=30)
        for ev in group.itertuples(index=False):
            entry_ts = pd.Timestamp(ev.entry_ts)
            if entry_ts.tzinfo is None:
                entry_ts = entry_ts.tz_localize(TZ)
            else:
                entry_ts = entry_ts.tz_convert(TZ)
            spot = spot_map.get(entry_ts.isoformat(), math.nan)
            entry = by_ts.get(entry_ts, empty)
            tau = (expiry_ts - entry_ts).total_seconds() / YEAR_SECONDS
            eligible: list[dict[str, Any]] = []
            for contract in entry.itertuples(index=False):
                typ = str(contract.option_type).upper()
                strike = float(contract.strike) if pd.notna(contract.strike) else math.nan
                premium = float(contract.close) if pd.notna(contract.close) else math.nan
                oi = float(contract.open_interest) if pd.notna(contract.open_interest) else math.nan
                if typ not in {"CE", "PE"} or not math.isfinite(spot) or not math.isfinite(strike) or not math.isfinite(premium):
                    continue
                if not valid_ohlc(pd.Series({"open":contract.open,"high":contract.high,"low":contract.low,"close":contract.close})):
                    continue
                iv, iv_status = implied_vol(spot, strike, tau, premium, RATE, DIVIDEND_YIELD, typ)
                if iv is None:
                    continue
                delta = bs_delta(spot, strike, tau, iv, RATE, DIVIDEND_YIELD, typ)
                eligible.append({"type":typ,"strike":strike,"premium":premium,"oi":oi,"iv":iv,"delta":delta,"iv_status":iv_status})
            for typ in ("CE", "PE"):
                contracts = [x for x in eligible if x["type"] == typ]
                for target in TARGET_ABS_DELTAS:
                    selected = min(contracts, key=lambda x: (abs(abs(x["delta"])-target), x["strike"])) if contracts else None
                    if selected is None:
                        rows.append({"event_id":str(ev.event_id),"expiry":expiry,"split":str(ev.split),"entry_ts":entry_ts.isoformat(),"dte_calendar_days":int(ev.entry_dte_calendar_days),"entry_time_ist":str(ev.entry_time_ist),"option_type":typ,"target_abs_delta":target,"selected_strike":None,"spot":spot if math.isfinite(spot) else None,"premium_close":None,"implied_vol":None,"model_delta":None,"entry_oi":None,"entry_oi_ge_100":False,"status":"NO_VALID_IV_CONTRACT","model_rate":RATE,"dividend_yield":DIVIDEND_YIELD,"pnl_status":"NOT_BACKTESTED"})
                        continue
                    rows.append({"event_id":str(ev.event_id),"expiry":expiry,"split":str(ev.split),"entry_ts":entry_ts.isoformat(),"dte_calendar_days":int(ev.entry_dte_calendar_days),"entry_time_ist":str(ev.entry_time_ist),"option_type":typ,"target_abs_delta":target,"selected_strike":selected["strike"],"spot":spot,"premium_close":selected["premium"],"implied_vol":selected["iv"],"model_delta":selected["delta"],"entry_oi":selected["oi"],"entry_oi_ge_100":math.isfinite(selected["oi"]) and selected["oi"]>=MIN_OI,"status":"MODEL_DELTA_SELECTED" if math.isfinite(selected["oi"]) and selected["oi"]>=MIN_OI else "MODEL_DELTA_SELECTED_OI_GATE_FAIL","model_rate":RATE,"dividend_yield":DIVIDEND_YIELD,"pnl_status":"NOT_BACKTESTED"})
    OUT.mkdir(parents=True, exist_ok=True)
    detail = pd.DataFrame(rows)
    detail.to_csv(OUT/"delta_selection.csv", index=False)
    pd.DataFrame(file_audit).to_csv(OUT/"source_file_audit.csv", index=False)
    pd.DataFrame(errors, columns=["expiry","error_type"]).to_csv(OUT/"source_errors.csv", index=False)
    summary = {
        "status":"MODEL_DELTA_AUDIT_COMPLETE" if not errors else "MODEL_DELTA_AUDIT_WITH_SOURCE_ERRORS",
        "created_at_utc":datetime.now(timezone.utc).isoformat(),"dataset":HF_REPO,"dataset_revision":revision,
        "index_file_sha256":sha256_file(index_path),"source_expiry_files_expected":int(events["expiry"].nunique()),
        "source_expiry_files_audited":int(len(file_audit)),"source_file_errors":len(errors),
        "expected_selection_rows":int(events["event_id"].nunique()*len(TARGET_ABS_DELTAS)*2),
        "selection_rows":int(len(detail)),"selected_rows":int(detail["status"].isin(["MODEL_DELTA_SELECTED","MODEL_DELTA_SELECTED_OI_GATE_FAIL"]).sum()),
        "no_valid_iv_rows":int((detail["status"]=="NO_VALID_IV_CONTRACT").sum()),
        "oi_qualified_rows":int(detail["entry_oi_ge_100"].sum()),
        "model":{"type":"European Black-Scholes","rate_continuous":RATE,"dividend_yield":DIVIDEND_YIELD,"expiry_timestamp":"15:30 Asia/Kolkata","premium_input":"same-timestamp minute OHLC close, not bid/ask","delta_source":"model-estimated, not exchange-published"},
        "limitations":["Model estimates are not exchange Greeks.","Minute-bar closes are not executable bid/ask quotes; no slippage-adjusted P&L is computed.","Model assumptions (6% rate, zero dividend yield, expiry at 15:30 IST) must be stress-tested before strategy replay.","Same-pivot multi-leg structures must follow the frozen replay protocol and use call-side delta anchor where specified.","This is strike-selection coverage only; no P&L or strategy promotion."],
        "outputs":{"detail":"results/phase52/delta_selection_audit/delta_selection.csv","source_audit":"results/phase52/delta_selection_audit/source_file_audit.csv","source_errors":"results/phase52/delta_selection_audit/source_errors.csv"}
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
