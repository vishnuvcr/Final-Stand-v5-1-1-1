#!/usr/bin/env python3
"""Bounded, preregistered Phase 89 study; never writes row-level raw market data to git."""
from __future__ import annotations
import csv, json, math, os, sys, time, urllib.error, urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(".")
CACHE = Path(".cache/phase89/raw")
OUT = Path("results/phase89")
START = date(2025, 1, 1)
STOP = date(2025, 12, 31)  # exclusive; no API request or sample row may include a 2026 date
FIELDS = ("open", "high", "low", "close", "iv", "volume", "strike", "oi", "spot", "timestamp")
SIDES = (("CALL", "ce"), ("PUT", "pe"))
TOKEN = os.environ.get("DHAN_ACCESS_TOKEN", "").strip()
IST = ZoneInfo("Asia/Kolkata")
REPO = os.environ.get("GITHUB_REPOSITORY", "vishnuvcr/Final-Stand-v5-1-1-1")
BRANCH = os.environ.get("GITHUB_REF_NAME", "phase-89-rolling-options-feature-study")
RUN_ID = os.environ.get("GITHUB_RUN_ID", "")
RUN_URL = f"https://github.com/{REPO}/actions/runs/{RUN_ID}" if RUN_ID else "(local run)"

PRIMARY = [
    ("P1", "iv_mean", "fwd15_abs_bps", "Mean ATM CALL/PUT IV → absolute next-15-minute NIFTY spot return"),
    ("P2", "iv_skew", "fwd15_bps", "PUT IV − CALL IV → signed next-15-minute NIFTY spot return"),
    ("P3", "oi_imbalance", "fwd15_bps", "(CALL OI − PUT OI)/(CALL OI + PUT OI) → signed next-15-minute NIFTY spot return"),
    ("P4", "oi_change_15m", "fwd15_bps", "Trailing 15-minute percentage change in total CALL+PUT OI → signed next-15-minute NIFTY spot return"),
]
SPLITS = [
    ("DEV", date(2025, 1, 1), date(2025, 7, 1)),
    ("VALIDATION", date(2025, 7, 1), date(2025, 10, 1)),
    ("CONFIRMATORY_OOS", date(2025, 10, 1), date(2025, 12, 31)),
]
ISSUES: list[str] = []
COVERAGE: list[dict] = []
QUALITY: dict = {}

def safe_float(value):
    try:
        x = float(value)
        return x if math.isfinite(x) else np.nan
    except (TypeError, ValueError):
        return np.nan

def cache_name(start: date, end: date, side: str) -> Path:
    return CACHE / f"{start.isoformat()}__{end.isoformat()}__{side.lower()}.json"

def request_segment(start: date, end: date, side: str, response_key: str):
    """Fetch <=28-calendar-day requests; cache successful payloads privately in Actions cache."""
    path = cache_name(start, end, side)
    if path.exists():
        try:
            obj = json.loads(path.read_text())
            payload = obj.get("payload", {})
            status = int(obj.get("http_status", 0))
            hit = True
            error_class = ""
        except Exception as exc:
            path.unlink(missing_ok=True)
            obj = {}
            payload, status, hit, error_class = {}, 0, False, type(exc).__name__
    else:
        payload, status, hit, error_class = {}, 0, False, ""
    if not hit:
        if not TOKEN:
            status, error_class = 0, "MissingSecret"
        else:
            body = {
                "exchangeSegment": "NSE_FNO",
                "interval": "5",
                "securityId": 13,
                "instrument": "OPTIDX",
                "expiryFlag": "MONTH",
                "expiryCode": 1,
                "strike": "ATM",
                "drvOptionType": side,
                "requiredData": ["open", "high", "low", "close", "iv", "volume", "strike", "oi", "spot"],
                "fromDate": start.isoformat(),
                "toDate": end.isoformat(),
            }
            req = urllib.request.Request(
                "https://api.dhan.co/v2/charts/rollingoption",
                data=json.dumps(body).encode("utf-8"),
                headers={"access-token": TOKEN, "Accept": "application/json", "Content-Type": "application/json"},
                method="POST",
            )
            for attempt in range(2):
                try:
                    with urllib.request.urlopen(req, timeout=12) as response:
                        status = response.status
                        payload = json.loads(response.read().decode("utf-8"))
                    error_class = ""
                    break
                except urllib.error.HTTPError as exc:
                    status, error_class = int(exc.code), "HTTPError"
                    payload = {}
                    if status not in (429, 500, 502, 503, 504) or attempt == 1:
                        break
                    time.sleep(2 ** attempt)
                except Exception as exc:
                    status, error_class, payload = 0, type(exc).__name__, {}
                    if attempt == 1:
                        break
                    time.sleep(2 ** attempt)
            # Cache only successful HTTP responses. No raw response is printed or committed.
            if 200 <= status < 300:
                CACHE.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({"http_status": status, "payload": payload}, separators=(",", ":")))
        if not TOKEN:
            ISSUES.append(f"{start}–{end} {side}: blocked because DHAN_ACCESS_TOKEN is unavailable.")
    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    block = data.get(response_key) if isinstance(data, dict) else None
    block = block if isinstance(block, dict) else {}
    arrays = [block.get(k) for k in FIELDS]
    lens = [len(v) for v in arrays if isinstance(v, list)]
    aligned = len(lens) == len(FIELDS) and len(set(lens)) == 1
    candles = len(block.get("timestamp", [])) if isinstance(block.get("timestamp", []), list) else 0
    ok = 200 <= status < 300 and aligned and candles > 0
    COVERAGE.append({
        "from_date": start.isoformat(), "to_date_exclusive_intended": end.isoformat(),
        "side": side, "http_status": status, "candles_reported": candles,
        "all_arrays_present": all(isinstance(v, list) for v in arrays),
        "array_lengths_aligned": aligned, "cache_hit": hit, "valid": ok,
        "error_class": error_class,
    })
    print(f"WINDOW from={start} to={end} side={side} status={status} candles={candles} aligned={aligned} cache_hit={hit} valid={ok}", flush=True)
    if not ok:
        label = f"{start}–{end} {side}: HTTP {status}, candles={candles}, aligned={aligned}, error={error_class or 'schema/empty'}"
        ISSUES.append(label)
    if not ok:
        return []
    rows = []
    for i, stamp in enumerate(block["timestamp"]):
        ts = normalize_timestamp(stamp)
        if pd.isna(ts):
            continue
        row = {"timestamp": ts}
        for key in FIELDS[:-1]:
            row[key] = safe_float(block[key][i])
        rows.append(row)
    return rows

def normalize_timestamp(value):
    try:
        if isinstance(value, (int, float)) or (isinstance(value, str) and value.strip().replace(".", "", 1).isdigit()):
            n = float(value)
            unit = "ms" if abs(n) > 1e12 else "s"
            ts = pd.to_datetime(n, unit=unit, utc=True, errors="coerce")
            if pd.isna(ts):
                return pd.NaT
            return ts.tz_convert(IST).tz_localize(None)
        ts = pd.Timestamp(value)
        if pd.isna(ts):
            return pd.NaT
        if ts.tzinfo is None:
            return ts.tz_localize(IST).tz_localize(None)
        return ts.tz_convert(IST).tz_localize(None)
    except Exception:
        return pd.NaT

def load_side(side: str, response_key: str) -> pd.DataFrame:
    rows = []
    cursor = START
    while cursor < STOP:
        end = min(cursor + timedelta(days=28), STOP)
        rows.extend(request_segment(cursor, end, side, response_key))
        cursor = end
        time.sleep(0.35)
    cols = ["timestamp"] + [f"{side.lower()}_{k}" for k in FIELDS[:-1]]
    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame(columns=cols)
    frame = frame.dropna(subset=["timestamp"]).sort_values("timestamp")
    duplicates = int(frame.duplicated("timestamp", keep="last").sum())
    QUALITY[f"{side.lower()}_duplicate_timestamps_removed"] = duplicates
    frame = frame.drop_duplicates("timestamp", keep="last")
    frame = frame.rename(columns={k: f"{side.lower()}_{k}" for k in FIELDS[:-1]})
    # Restrict again after timestamp conversion: Phase 89 may not inspect 2026 data.
    frame = frame[(frame["timestamp"] >= pd.Timestamp(START)) & (frame["timestamp"] < pd.Timestamp(STOP))]
    return frame[cols].sort_values("timestamp").reset_index(drop=True)

def build_panel(calls: pd.DataFrame, puts: pd.DataFrame) -> pd.DataFrame:
    if calls.empty or puts.empty:
        return pd.DataFrame()
    merged = calls.merge(puts, on="timestamp", how="inner", validate="one_to_one")
    QUALITY["call_rows_unique"] = int(len(calls))
    QUALITY["put_rows_unique"] = int(len(puts))
    QUALITY["paired_timestamp_rows_before_spot_check"] = int(len(merged))
    spot_diff = (merged["call_spot"] - merged["put_spot"]).abs() / merged[["call_spot", "put_spot"]].abs().max(axis=1).replace(0, np.nan)
    mismatch = spot_diff > 0.0002
    QUALITY["call_put_spot_mismatch_rows_excluded"] = int(mismatch.sum())
    merged = merged.loc[~mismatch].copy()
    strike_pair_ok = np.isclose(merged["call_strike"], merged["put_strike"], rtol=0.0, atol=1e-9)
    QUALITY["call_put_atm_strike_mismatch_rows_excluded"] = int((~strike_pair_ok).sum())
    merged = merged.loc[strike_pair_ok].copy()
    merged["spot"] = (merged["call_spot"] + merged["put_spot"]) / 2
    merged = merged[(merged["spot"] > 0) & merged["timestamp"].notna()].copy()
    merged["session"] = merged["timestamp"].dt.strftime("%Y-%m-%d")
    merged = merged.sort_values("timestamp").reset_index(drop=True)
    derived = []
    for session, g in merged.groupby("session", sort=True):
        g = g.sort_values("timestamp").copy()
        # Rolling series feature levels available at t.
        g["iv_mean"] = (g["call_iv"] + g["put_iv"]) / 2.0
        g["iv_skew"] = g["put_iv"] - g["call_iv"]
        oi_sum = g["call_oi"] + g["put_oi"]
        g["oi_imbalance"] = (g["call_oi"] - g["put_oi"]) / oi_sum.replace(0, np.nan)
        lag3_minutes = (g["timestamp"] - g["timestamp"].shift(3)).dt.total_seconds() / 60
        oi_change = oi_sum / oi_sum.shift(3) - 1.0
        # OI is comparable across t-15m only if both rolling ATM strikes stayed fixed.
        stable_contract_pair = (
            g["call_strike"].eq(g["call_strike"].shift(3))
            & g["put_strike"].eq(g["put_strike"].shift(3))
            & g["call_strike"].eq(g["put_strike"])
        )
        g["oi_change_15m"] = oi_change.where((lag3_minutes == 15.0) & stable_contract_pair)
        future_minutes = (g["timestamp"].shift(-3) - g["timestamp"]).dt.total_seconds() / 60
        future_return = g["spot"].shift(-3) / g["spot"] - 1.0
        g["fwd15_bps"] = (future_return * 10000).where(future_minutes == 15.0)
        g["fwd15_abs_bps"] = g["fwd15_bps"].abs()
        # Only retain the registered timestamp-safe target; never bridge a missing candle/session.
        derived.append(g)
    panel = pd.concat(derived, ignore_index=True) if derived else pd.DataFrame()
    if not panel.empty:
        panel = panel.replace([np.inf, -np.inf], np.nan)
    QUALITY["paired_panel_rows_after_spot_check"] = int(len(panel))
    QUALITY["sessions_with_paired_data"] = int(panel["session"].nunique()) if not panel.empty else 0
    return panel

def fit_one(data: pd.DataFrame, feature: str, target: str):
    needed = data[["session", feature, target]].replace([np.inf, -np.inf], np.nan).dropna()
    n_sessions = int(needed["session"].nunique())
    result = {"n": int(len(needed)), "sessions": n_sessions, "beta_bps_per_sd": None,
              "se_clustered": None, "ci95_low": None, "ci95_high": None, "p_value": None}
    if len(needed) < 100 or n_sessions < 8 or needed[feature].nunique() < 2:
        return result
    x = needed[feature].astype(float)
    sd = float(x.std(ddof=0))
    if not math.isfinite(sd) or sd <= 0:
        return result
    z = (x - float(x.mean())) / sd
    y = needed[target].astype(float)
    model = sm.OLS(y.to_numpy(), sm.add_constant(z.to_numpy())).fit(
        cov_type="cluster", cov_kwds={"groups": needed["session"].to_numpy(), "use_correction": True}
    )
    ci = model.conf_int(alpha=0.05)[1]
    result.update({
        "beta_bps_per_sd": float(model.params[1]),
        "se_clustered": float(model.bse[1]),
        "ci95_low": float(ci[0]), "ci95_high": float(ci[1]),
        "p_value": float(model.pvalues[1]),
    })
    return result

def holm_adjust(pvalues):
    """Holm step-down adjusted p values; missing tests are not treated as passed."""
    if any(p is None or not math.isfinite(float(p)) for p in pvalues):
        return [None for _ in pvalues]
    order = sorted(range(len(pvalues)), key=lambda i: float(pvalues[i]))
    adjusted = [None] * len(pvalues)
    running = 0.0
    m = len(pvalues)
    for rank, i in enumerate(order):
        raw = min(1.0, (m - rank) * float(pvalues[i]))
        running = max(running, raw)
        adjusted[i] = running
    return adjusted

def fmt(x, digits=4):
    if x is None:
        return "NA"
    try:
        if not math.isfinite(float(x)):
            return "NA"
        return f"{float(x):.{digits}f}"
    except (TypeError, ValueError):
        return "NA"

def save_csv(path: Path, rows, fieldnames=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else ["no_data"]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def update_docs(status: str, summary: dict, primary_rows: list, split_rows: list):
    OUT.mkdir(parents=True, exist_ok=True)
    valid_coverage = sum(bool(x["valid"]) for x in COVERAGE)
    total_coverage = len(COVERAGE)
    oos_sessions = summary.get("oos_sessions", 0)
    oos_rows = summary.get("oos_complete_rows", 0)
    adequate = oos_sessions >= 30 and oos_rows >= 1000
    inference_allowed = adequate and all(x.get("p_value") is not None for x in primary_rows)
    result_rows = []
    for row in primary_rows:
        result_rows.append(
            f"| {row['id']} | {row['feature']} | {row['target']} | {row.get('n','NA')} | {row.get('sessions','NA')} | "
            f"{fmt(row.get('beta_bps_per_sd'),3)} | {fmt(row.get('ci95_low'),3)} to {fmt(row.get('ci95_high'),3)} | "
            f"{fmt(row.get('p_value'))} | {fmt(row.get('holm_p'))} |"
        )
    split_md = []
    by_id = {p["id"]: p for p in primary_rows}
    for p in PRIMARY:
        pid, feature, target, label = p
        pieces = []
        for split_name in ("DEV", "VALIDATION", "CONFIRMATORY_OOS"):
            rr = next((r for r in split_rows if r["id"] == pid and r["split"] == split_name), {})
            pieces.append(f"{split_name}: beta={fmt(rr.get('beta_bps_per_sd'),3)} bps/SD, n={rr.get('n','NA')}, sessions={rr.get('sessions','NA')}")
        split_md.append(f"- **{pid} — {label}.** " + "; ".join(pieces) + ".")
    issue_md = "\n".join(f"- {x}" for x in ISSUES) if ISSUES else "- No API/network/schema failures were observed."
    result_md = f"""# Phase 89 Results — rolling-options feature study

Run: {RUN_URL}  
Status: **{status}**  
Data period requested: 2025-01-01 through 2025-12-31 exclusive. Protected 2026 Phase 83 holdout not requested or loaded.

## Data-quality and sample summary
- Valid API window/side responses: {valid_coverage}/{total_coverage}.
- Unique CALL timestamps: {QUALITY.get('call_rows_unique', 0)}; unique PUT timestamps: {QUALITY.get('put_rows_unique', 0)}.
- Exact timestamp pairs before spot-consistency check: {QUALITY.get('paired_timestamp_rows_before_spot_check', 0)}.
- Spot-mismatch pairs excluded: {QUALITY.get('call_put_spot_mismatch_rows_excluded', 0)}.\n- CALL/PUT ATM-strike mismatches excluded: {QUALITY.get('call_put_atm_strike_mismatch_rows_excluded', 0)}.
- Paired rows after spot check: {QUALITY.get('paired_panel_rows_after_spot_check', 0)} across {QUALITY.get('sessions_with_paired_data', 0)} sessions.
- Confirmatory OOS complete observations: {oos_rows} across {oos_sessions} sessions.
- OOS inferential gate (at least 1,000 complete rows and 30 sessions): **{'PASS' if adequate else 'FAIL — descriptive only'}**.

## Four preregistered OOS tests
| ID | Feature | Target | N | Sessions | Beta (bps per 1 SD feature) | 95% clustered CI | Raw p | Holm-adjusted p |
|---|---|---|---:|---:|---:|---|---:|---:|
{chr(10).join(result_rows) if result_rows else '| — | — | — | 0 | 0 | NA | NA | NA | NA |'}

Interpret these only as predictive associations in an ATM-relative data representation. They are not causality, options P&L, or an executable strategy. All four tests are two-sided; standard errors are clustered by trading session/date. Holm correction applies only to this frozen four-test OOS family.

## Chronological sign replication
{chr(10).join(split_md) if split_md else '- No estimable split coefficients.'}

## API/data issues
{issue_md}

## Main interpretation rule
- A feature is only considered a candidate for further independent replication if its OOS Holm-adjusted p-value is below 0.05 and its effect direction is consistent in DEV and VALIDATION. This still does **not** approve a trading strategy.
- If the sample gate fails, p-values and signs are descriptive and no confirmatory inference is made.
- No transaction-cost-adjusted strategy P&L is possible from these fields. Exact listed contracts, historical bid/ask/depth, executable fills, Greek data, futures/synthetic futures and VIX are not covered by this endpoint study.
- Paytm Money brokerage/statutory charges, spread, slippage and latency must be frozen before any separate execution-quality replay.
"""
    (OUT / "PHASE89_RESULTS.md").write_text(result_md)
    save_csv(OUT / "coverage.csv", COVERAGE, [
        "from_date","to_date_exclusive_intended","side","http_status","candles_reported",
        "all_arrays_present","array_lengths_aligned","cache_hit","valid","error_class"])
    # Publish per-session observation counts only, never market prices/features.
    daily_rows = []
    if summary.get("daily_counts"):
        daily_rows = summary["daily_counts"]
    save_csv(OUT / "daily_coverage.csv", daily_rows, ["session","paired_rows","complete_primary_rows"])
    save_csv(OUT / "split_tests.csv", split_rows, [
        "id","feature","target","split","n","sessions","beta_bps_per_sd","se_clustered","ci95_low","ci95_high","p_value"])
    save_csv(OUT / "primary_tests.csv", primary_rows, [
        "id","feature","target","label","n","sessions","beta_bps_per_sd","se_clustered","ci95_low","ci95_high","p_value","holm_p","oos_inference_gate"])
    compact = {
        "phase": 89, "run_url": RUN_URL, "status": status, "requested_period": ["2025-01-01","2025-12-31_exclusive"],
        "holdout_2026_requested": False, "valid_api_windows": valid_coverage, "total_api_windows": total_coverage,
        "quality": QUALITY, "oos_sessions": oos_sessions, "oos_complete_rows": oos_rows,
        "oos_inferential_gate": bool(adequate), "confirmatory_inference_allowed": bool(inference_allowed),
        "primary_tests": [{k: v for k, v in x.items() if k in ("id","feature","target","n","sessions","beta_bps_per_sd","ci95_low","ci95_high","p_value","holm_p")} for x in primary_rows],
        "api_issue_count": len(ISSUES),
    }
    (OUT / "summary.json").write_text(json.dumps(compact, indent=2, allow_nan=False) + "\n")

    status_md = f"""# Phase 89 Status

Date: 2026-10-10  
Status: **{status}**  
Latest workflow run: [{RUN_ID}]({RUN_URL})  
Decision: No options strategy is promoted by Phase 89.

## Registered evidence boundary
- [Preregistered plan](PHASE89_RESEARCH_PLAN.md)
- [Error log](PHASE89_ERROR_LOG.md)
- [Auditable chat/decision log](PHASE89_CHAT_LOG.md)
- [Workflow](.github/workflows/phase89-rolling-options-feature-study.yml)
- [Detailed results](results/phase89/PHASE89_RESULTS.md)
- [Aggregate primary test table](results/phase89/primary_tests.csv)
- [API coverage ledger](results/phase89/coverage.csv)
- [Daily row-count ledger](results/phase89/daily_coverage.csv)
- [Split-by-split estimates](results/phase89/split_tests.csv)
- [Summary JSON](results/phase89/summary.json)

## Results
- Valid API windows/sides: {valid_coverage}/{total_coverage}.
- Paired rows: {QUALITY.get('paired_panel_rows_after_spot_check',0)}; paired sessions: {QUALITY.get('sessions_with_paired_data',0)}.
- Confirmatory OOS sample: {oos_rows} complete rows over {oos_sessions} sessions.
- OOS inference gate: **{'PASS' if adequate else 'FAIL — results descriptive only'}**.
- Confirmatory inference allowed: **{'YES for the registered four-test association family only' if inference_allowed else 'NO'}**.
- This is a feature-association study, not strategy P&L or execution simulation. The 2026 Phase 83 holdout remains unopened.
"""
    (ROOT / "PHASE89_STATUS.md").write_text(status_md)

    old_error = (ROOT / "PHASE89_ERROR_LOG.md").read_text() if (ROOT / "PHASE89_ERROR_LOG.md").exists() else "# Phase 89 Error Log\n"
    error_runtime = f"""<!-- PHASE89_RUNTIME_START -->
## Runtime summary — {RUN_ID or 'local'}
- Status: {status}
- API requests passing schema/alignment: {valid_coverage}/{total_coverage}
- Paired rows after timestamp and spot consistency checks: {QUALITY.get('paired_panel_rows_after_spot_check',0)}
- OOS complete observations/sessions: {oos_rows}/{oos_sessions}
- Issues:
{issue_md}
- No credential, raw response body, or raw price is recorded here.
<!-- PHASE89_RUNTIME_END -->"""
    import re
    if "<!-- PHASE89_RUNTIME_START -->" in old_error:
        old_error = re.sub(r"<!-- PHASE89_RUNTIME_START -->.*?<!-- PHASE89_RUNTIME_END -->", error_runtime, old_error, flags=re.S)
    else:
        old_error = old_error.rstrip() + "\n\n" + error_runtime + "\n"
    (ROOT / "PHASE89_ERROR_LOG.md").write_text(old_error)

    old_chat = (ROOT / "PHASE89_CHAT_LOG.md").read_text() if (ROOT / "PHASE89_CHAT_LOG.md").exists() else "# Phase 89 Chat / Decision Log\n"
    chat_runtime = f"""<!-- PHASE89_RUNTIME_START -->
## Automated execution record — {RUN_ID or 'local'}
- Workflow: {RUN_URL}
- Study status: {status}
- Valid API windows/sides: {valid_coverage}/{total_coverage}.
- Paired rows after validation: {QUALITY.get('paired_panel_rows_after_spot_check',0)}; confirmatory OOS complete rows: {oos_rows} across {oos_sessions} sessions.
- Main results and complete aggregate tables are in [PHASE89_RESULTS.md](results/phase89/PHASE89_RESULTS.md) and [primary_tests.csv](results/phase89/primary_tests.csv).
- Raw payloads and row-level prices were not printed, committed, or uploaded as artifacts. The 2026 Phase 83 holdout was not requested or loaded.
<!-- PHASE89_RUNTIME_END -->"""
    if "<!-- PHASE89_RUNTIME_START -->" in old_chat:
        old_chat = re.sub(r"<!-- PHASE89_RUNTIME_START -->.*?<!-- PHASE89_RUNTIME_END -->", chat_runtime, old_chat, flags=re.S)
    else:
        old_chat = old_chat.rstrip() + "\n\n" + chat_runtime + "\n"
    (ROOT / "PHASE89_CHAT_LOG.md").write_text(old_chat)

    readme = (ROOT / "README.md").read_text() if (ROOT / "README.md").exists() else "# Final Stand v5 1-1-1\n"
    block = f"""<!-- PHASE89_START -->
# Resume checkpoint — Phase 89 rolling-options feature study

**Status: {status}.** Automated run [{RUN_ID}]({RUN_URL}) requested 2025-only Dhan rolling ATM-relative CALL/PUT data and tested the four preregistered IV/OI associations. The protected Phase 83 2026 holdout was not requested or loaded.

- [Phase 89 research plan](PHASE89_RESEARCH_PLAN.md)
- [Phase 89 status](PHASE89_STATUS.md)
- [Phase 89 error log](PHASE89_ERROR_LOG.md)
- [Phase 89 auditable chat/decision log](PHASE89_CHAT_LOG.md)
- [Phase 89 detailed results](results/phase89/PHASE89_RESULTS.md)
- [Primary tests CSV](results/phase89/primary_tests.csv)
- [Coverage ledger](results/phase89/coverage.csv)
- [Daily coverage ledger](results/phase89/daily_coverage.csv)
- [Split estimates](results/phase89/split_tests.csv)
- [Summary JSON](results/phase89/summary.json)
- [Automated workflow](.github/workflows/phase89-rolling-options-feature-study.yml)

**Interpretation boundary:** feature association is not options-strategy profitability. No fixed-contract execution, bid/ask/depth, Greeks, VIX/futures, Paytm Money cost-adjusted fills or live orders were evaluated. No strategy has been promoted.
<!-- PHASE89_END -->"""
    if "<!-- PHASE89_START -->" in readme:
        readme = re.sub(r"<!-- PHASE89_START -->.*?<!-- PHASE89_END -->\n*", "", readme, flags=re.S)
    (ROOT / "README.md").write_text(block + "\n\n" + readme.lstrip())

def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    if not TOKEN:
        ISSUES.append("DHAN_ACCESS_TOKEN missing; no API requests were sent.")
        summary = {"oos_sessions": 0, "oos_complete_rows": 0, "daily_counts": []}
        update_docs("BLOCKED_SECRET_MISSING", summary, [], [])
        print("PHASE89_STATUS=BLOCKED_SECRET_MISSING")
        return 2
    calls_rows, puts_rows = [], []
    cursor = START
    intervals = []
    while cursor < STOP:
        end = min(cursor + timedelta(days=28), STOP)
        intervals.append((cursor, end))
        cursor = end
    for start, end in intervals:
        for side, key in SIDES:
            rows = request_segment(start, end, side, key)
            if side == "CALL":
                calls_rows.extend(rows)
            else:
                puts_rows.extend(rows)
            time.sleep(0.4)
    calls = pd.DataFrame(calls_rows)
    puts = pd.DataFrame(puts_rows)
    side_columns = ["timestamp"] + [f"{side.lower()}_{k}" for k in FIELDS[:-1]]
    for side, df in (("CALL", calls), ("PUT", puts)):
        if df.empty:
            if side == "CALL":
                calls = pd.DataFrame(columns=side_columns)
            else:
                puts = pd.DataFrame(columns=side_columns)
    for side in ("CALL", "PUT"):
        if side == "CALL":
            df = calls
        else:
            df = puts
        if not df.empty:
            df = df.dropna(subset=["timestamp"]).sort_values("timestamp").drop_duplicates("timestamp", keep="last")
            df = df[(df["timestamp"] >= pd.Timestamp(START)) & (df["timestamp"] < pd.Timestamp(STOP))]
            df = df.rename(columns={k: f"{side.lower()}_{k}" for k in FIELDS[:-1]})
            if side == "CALL":
                calls = df
            else:
                puts = df
    if calls.empty or puts.empty:
        panel = pd.DataFrame()
    else:
        panel = build_panel(calls, puts)
    split_rows = []
    primary_oos = []
    daily_counts = []
    if not panel.empty:
        for session, d in panel.groupby("session", sort=True):
            complete = d[[x[1] for x in PRIMARY] + [x[2] for x in PRIMARY]].replace([np.inf,-np.inf],np.nan).dropna()
            daily_counts.append({"session":session,"paired_rows":int(len(d)),"complete_primary_rows":int(len(complete))})
        panel_dates = pd.to_datetime(panel["session"]).dt.date
    else:
        panel_dates = pd.Series([], dtype=object)
    for split_name, split_start, split_end in SPLITS:
        if panel.empty:
            part = pd.DataFrame()
        else:
            part = panel[(panel_dates >= split_start) & (panel_dates < split_end)].copy()
        for pid, feature, target, label in PRIMARY:
            res = fit_one(part, feature, target) if not part.empty else {
                "n":0,"sessions":0,"beta_bps_per_sd":None,"se_clustered":None,
                "ci95_low":None,"ci95_high":None,"p_value":None}
            split_rows.append({"id":pid,"feature":feature,"target":target,"split":split_name,**res})
            if split_name == "CONFIRMATORY_OOS":
                primary_oos.append({"id":pid,"feature":feature,"target":target,"label":label,**res})
    oos_panel = panel[(panel_dates >= date(2025,10,1)) & (panel_dates < date(2026,1,1))] if not panel.empty else pd.DataFrame()
    complete_oos = oos_panel[[x[1] for x in PRIMARY] + [x[2] for x in PRIMARY]].replace([np.inf,-np.inf],np.nan).dropna() if not oos_panel.empty else pd.DataFrame()
    oos_sessions = int(oos_panel.loc[complete_oos.index, "session"].nunique()) if not complete_oos.empty else 0
    oos_rows = int(len(complete_oos))
    pvals = [x.get("p_value") for x in primary_oos]
    holm = holm_adjust(pvals) if len(pvals) == 4 else [None] * len(primary_oos)
    for row, hp in zip(primary_oos, holm):
        row["holm_p"] = hp
    sufficient = oos_sessions >= 30 and oos_rows >= 1000 and all(x.get("p_value") is not None for x in primary_oos)
    valid_windows = sum(bool(x["valid"]) for x in COVERAGE)
    total_windows = len(COVERAGE)
    if sufficient and valid_windows == total_windows:
        status = "COMPLETE — OOS sample gate passed; interpret only the four Holm-controlled feature associations"
    elif sufficient:
        status = "COMPLETE WITH DATA-COVERAGE CAVEAT — OOS sample gate passed on available aligned records"
    elif not panel.empty:
        status = "INCONCLUSIVE — OOS sample gate failed; all statistical outputs descriptive only"
    else:
        status = "FAILED DATA GATE — insufficient usable paired CALL/PUT data; no confirmatory inference"
    summary = {
        "oos_sessions":oos_sessions, "oos_complete_rows":oos_rows, "daily_counts":daily_counts,
    }
    update_docs(status, summary, primary_oos, split_rows)
    print(f"PHASE89_STATUS={status}")
    print(f"API_WINDOWS_VALID={valid_windows}/{total_windows}")
    print(f"PAIRED_ROWS={QUALITY.get('paired_panel_rows_after_spot_check',0)}")
    print(f"PAIRED_SESSIONS={QUALITY.get('sessions_with_paired_data',0)}")
    print(f"OOS_COMPLETE_ROWS={oos_rows}")
    print(f"OOS_SESSIONS={oos_sessions}")
    print(f"PRIMARY_HOLM_TESTS={sum(x.get('holm_p') is not None for x in primary_oos)}/4")
    print("RAW_PAYLOADS_PRINTED_OR_COMMITTED=false")
    print("PHASE83_2026_HOLDOUT_REQUESTED_OR_LOADED=false")
    if ISSUES:
        print(f"DATA_QUALITY_ISSUES={len(ISSUES)} (sanitized detail in PHASE89_ERROR_LOG.md)")
    else:
        print("DATA_QUALITY_ISSUES=0")
    # A failed sample gate is a scientific outcome, not an automation crash.
    return 0

if __name__ == "__main__":
    sys.exit(main())
