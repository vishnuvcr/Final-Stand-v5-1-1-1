#!/usr/bin/env python3
"""Bounded DhanHQ expired-options availability probe; never writes raw market rows."""
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

API = "https://api.dhan.co/v2/charts/rollingoption"
OUT = Path("results/phase71_dhan_pilot")
TARGETS = ["2026-07-28", "2026-08-04"]
IST = ZoneInfo("Asia/Kolkata")


def emit(payload):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Phase 71 — DhanHQ bounded historical-options pilot",
        "",
        f"Decision: **{payload['decision']}**",
        "",
        f"Checked at UTC: {payload['checked_at_utc']}",
        "",
        "## Aggregate results",
        "",
        "| Target session | Expiry flag | Side | Returned rows | Target-session rows | Decision |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in payload.get("probes", []):
        lines.append(f"| {row['target_date']} | {row['expiry_flag']} | {row['side']} | {row.get('rows', 0)} | {row.get('target_session_rows', 0)} | {row['status']} |")
    lines += [
        "",
        "## Interpretation",
        "",
        payload["interpretation"],
        "",
        "No raw market rows or credentials are stored in this report. A passing target-date probe only confirms that some ATM-relative rows exist; it does not establish full-chain coverage, executable bid/ask fills, complete expiry mapping, or profitability.",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def rows_from_side(data, side):
    if not isinstance(data, dict):
        return []
    candidates = [side.lower(), "ce" if side == "CALL" else "pe"]
    for key in candidates:
        val = data.get(key)
        if isinstance(val, dict):
            timestamps = val.get("timestamp", [])
            if isinstance(timestamps, list):
                return timestamps
    return []


def main():
    token = os.environ.get("DHAN_ACCESS_TOKEN", "").strip()
    checked = dt.datetime.now(dt.timezone.utc).isoformat()
    if not token:
        emit({
            "checked_at_utc": checked,
            "decision": "BLOCKED_NO_DHAN_ACCESS_TOKEN",
            "probes": [],
            "interpretation": "The authenticated API probe was not run because repository secret DHAN_ACCESS_TOKEN is absent. No purchase was made. Configure the secret only after confirming an active DhanHQ Data API subscription and permitted research/data-retention terms.",
        })
        print("BLOCKED_NO_DHAN_ACCESS_TOKEN")
        return 0

    probes = []
    errors = []
    for day in TARGETS:
        next_day = (dt.date.fromisoformat(day) + dt.timedelta(days=1)).isoformat()
        for flag in ("WEEK", "MONTH"):
            for side in ("CALL", "PUT"):
                payload = {
                    "exchangeSegment": "NSE_FNO",
                    "interval": "1",
                    "securityId": 13,
                    "instrument": "OPTIDX",
                    "expiryFlag": flag,
                    "expiryCode": 1,
                    "strike": "ATM",
                    "drvOptionType": side,
                    "requiredData": ["open", "high", "low", "close", "iv", "volume", "oi", "spot", "strike"],
                    "fromDate": day,
                    "toDate": next_day,
                }
                request = urllib.request.Request(
                    API,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "access-token": token,
                    },
                    method="POST",
                )
                item = {"target_date": day, "expiry_flag": flag, "side": side}
                try:
                    with urllib.request.urlopen(request, timeout=45) as response:
                        body = json.loads(response.read().decode("utf-8"))
                    data = body.get("data", {}) if isinstance(body, dict) else {}
                    timestamps = rows_from_side(data, side)
                    target_count = 0
                    for value in timestamps:
                        try:
                            stamp = dt.datetime.fromtimestamp(float(value), tz=dt.timezone.utc).astimezone(IST)
                            if stamp.date().isoformat() == day:
                                target_count += 1
                        except (ValueError, TypeError, OSError, OverflowError):
                            continue
                    item.update({
                        "rows": len(timestamps),
                        "target_session_rows": target_count,
                        "status": "ROWS_FOUND" if target_count else "NO_TARGET_ROWS",
                    })
                    if not target_count:
                        errors.append(f"{day}/{flag}/{side}: no target rows")
                except urllib.error.HTTPError as exc:
                    # Do not store response bodies; they can contain account/provider details.
                    item.update({"rows": 0, "target_session_rows": 0, "status": f"HTTP_{exc.code}"})
                    errors.append(f"{day}/{flag}/{side}: HTTP {exc.code}")
                except Exception as exc:
                    item.update({"rows": 0, "target_session_rows": 0, "status": "REQUEST_OR_PARSE_ERROR"})
                    errors.append(f"{day}/{flag}/{side}: {type(exc).__name__}")
                probes.append(item)
                time.sleep(0.15)

    any_rows = any(p.get("target_session_rows", 0) > 0 for p in probes)
    all_have_rows = all(p.get("target_session_rows", 0) > 0 for p in probes)
    decision = "PILOT_ROWS_FOUND_PARTIAL_COVERAGE" if any_rows and not all_have_rows else (
        "PILOT_TARGET_ROWS_FOUND" if all_have_rows else "BLOCKED_NO_TARGET_ROWS"
    )
    emit({
        "checked_at_utc": checked,
        "decision": decision,
        "targets": TARGETS,
        "probes": probes,
        "errors": errors,
        "interpretation": (
            "At least one configured ATM-relative probe returned target-session rows. Inspect per-probe coverage and expiry-code semantics before expanding the pull."
            if any_rows else
            "No configured ATM-relative probe returned target-session rows. Do not buy a larger dataset or infer strategy P&L from this result; diagnose token, API access, endpoint parameters and historical availability first."
        ),
    })
    print(decision)
    return 0


if __name__ == "__main__":
    sys.exit(main())
