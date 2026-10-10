#!/usr/bin/env python3
"""Aggregate-only DhanHQ timestamp and field-integrity audit; never writes raw market rows."""
import datetime as dt
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

API = "https://api.dhan.co/v2/charts/rollingoption"
OUT = Path("results/phase72_dhan_integrity_audit")
TARGETS = ["2026-07-28", "2026-08-04"]
IST = ZoneInfo("Asia/Kolkata")
FIELDS = ["open", "high", "low", "close", "iv", "volume", "oi", "spot", "strike"]


def parse_stamp(value):
    try:
        number = float(value)
        if number > 1e12:
            number /= 1000.0
        return dt.datetime.fromtimestamp(number, tz=dt.timezone.utc).astimezone(IST)
    except (ValueError, TypeError, OSError, OverflowError):
        if isinstance(value, str):
            try:
                parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=dt.timezone.utc)
                return parsed.astimezone(IST)
            except ValueError:
                return None
        return None


def find_side(data, side):
    if not isinstance(data, dict):
        return {}
    for key in (side.lower(), "ce" if side == "CALL" else "pe"):
        item = data.get(key)
        if isinstance(item, dict):
            return item
    return {}


def summarize(payload, day, flag, side):
    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    series = find_side(data, side)
    raw_ts = series.get("timestamp", [])
    timestamps = raw_ts if isinstance(raw_ts, list) else []
    parsed = [parse_stamp(x) for x in timestamps]
    valid = [x for x in parsed if x is not None]
    target = [x for x in valid if x.date().isoformat() == day]
    regular = [x for x in target if dt.time(9, 15) <= x.time().replace(tzinfo=None) < dt.time(15, 30)]
    epoch_keys = [x.timestamp() for x in valid]
    unique_keys = set(epoch_keys)
    duplicate_count = len(epoch_keys) - len(unique_keys)
    regular_unique = sorted(set(x.timestamp() for x in regular))
    gap_count = sum(1 for a, b in zip(regular_unique, regular_unique[1:]) if b - a > 60.5)
    lengths = {}
    for field in FIELDS:
        val = series.get(field)
        lengths[field] = len(val) if isinstance(val, list) else None
    aligned = {field: length == len(timestamps) for field, length in lengths.items() if length is not None}
    def nums(field):
        arr = series.get(field)
        if not isinstance(arr, list):
            return []
        out = []
        for x in arr:
            try:
                out.append(float(x))
            except (TypeError, ValueError):
                out.append(float("nan"))
        return out
    opens, highs, lows, closes = (nums(x) for x in ("open", "high", "low", "close"))
    n = min(map(len, (opens, highs, lows, closes))) if all((opens, highs, lows, closes)) else 0
    valid_ohlc = 0
    invalid_ohlc = 0
    inconsistent_ohlc = 0
    for i in range(n):
        o, h, l, c = opens[i], highs[i], lows[i], closes[i]
        good = all(map(lambda v: v == v and abs(v) != float("inf") and v > 0, (o, h, l, c)))
        if good:
            valid_ohlc += 1
            if h < max(o, c, l) or l > min(o, c, h):
                inconsistent_ohlc += 1
        else:
            invalid_ohlc += 1
    return {
        "target_date": day, "expiry_flag": flag, "side": side,
        "timestamp_count": len(timestamps), "parseable_timestamp_count": len(valid),
        "target_date_count": len(target), "regular_session_count": len(regular),
        "out_of_session_count": len(target) - len(regular),
        "unique_timestamp_count_all_dates": len(unique_keys), "duplicate_timestamp_count_all_dates": duplicate_count,
        "first_target_ist": min(target).isoformat() if target else None,
        "last_target_ist": max(target).isoformat() if target else None,
        "unique_regular_timestamp_count": len(regular_unique), "gaps_over_one_minute": gap_count,
        "field_lengths": lengths, "field_alignment": aligned,
        "valid_ohlc_rows": valid_ohlc, "invalid_ohlc_rows": invalid_ohlc,
        "ohlc_consistency_violations": inconsistent_ohlc,
        "status": "AUDIT_RECORDED"
    }


def emit(report):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = [
        "# Phase 72 — DhanHQ target-date integrity audit", "",
        f"Decision: **{report['decision']}**", "",
        f"Checked UTC: {report['checked_at_utc']}", "",
        "| Date | Flag | Side | Timestamps | Target date | Regular session | Duplicates | Gaps >1m | OHLC valid/invalid | Alignment |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for p in report.get("probes", []):
        lines.append(f"| {p['target_date']} | {p['expiry_flag']} | {p['side']} | {p['timestamp_count']} | {p['target_date_count']} | {p['regular_session_count']} | {p['duplicate_timestamp_count_all_dates']} | {p['gaps_over_one_minute']} | {p['valid_ohlc_rows']}/{p['invalid_ohlc_rows']} | {all(p['field_alignment'].values()) if p['field_alignment'] else 'unavailable'} |")
    lines += ["", "## Interpretation", "", report["interpretation"], "", "Only aggregate diagnostics are retained. No raw market rows, tokens, or provider response bodies are stored."]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    token = os.environ.get("DHAN_ACCESS_TOKEN", "").strip()
    checked = dt.datetime.now(dt.timezone.utc).isoformat()
    if not token:
        emit({"checked_at_utc": checked, "decision": "BLOCKED_NO_DHAN_ACCESS_TOKEN", "probes": [],
              "interpretation": "No authenticated audit was run because DHAN_ACCESS_TOKEN is absent. No raw data were downloaded."})
        print("BLOCKED_NO_DHAN_ACCESS_TOKEN")
        return
    probes, errors = [], []
    for day in TARGETS:
        next_day = (dt.date.fromisoformat(day) + dt.timedelta(days=1)).isoformat()
        for flag in ("WEEK", "MONTH"):
            for side in ("CALL", "PUT"):
                payload = {
                    "exchangeSegment": "NSE_FNO", "interval": "1", "securityId": 13,
                    "instrument": "OPTIDX", "expiryFlag": flag, "expiryCode": 1,
                    "strike": "ATM", "drvOptionType": side, "requiredData": FIELDS,
                    "fromDate": day, "toDate": next_day,
                }
                request = urllib.request.Request(API, data=json.dumps(payload).encode(),
                    headers={"Accept": "application/json", "Content-Type": "application/json", "access-token": token},
                    method="POST")
                try:
                    with urllib.request.urlopen(request, timeout=45) as response:
                        body = json.loads(response.read().decode("utf-8"))
                    row = summarize(body, day, flag, side)
                    if not row["timestamp_count"]:
                        errors.append(f"{day}/{flag}/{side}: empty timestamp series")
                    probes.append(row)
                except urllib.error.HTTPError as exc:
                    probes.append({"target_date": day, "expiry_flag": flag, "side": side, "status": f"HTTP_{exc.code}"})
                    errors.append(f"{day}/{flag}/{side}: HTTP {exc.code}")
                except Exception as exc:
                    probes.append({"target_date": day, "expiry_flag": flag, "side": side, "status": "REQUEST_OR_PARSE_ERROR"})
                    errors.append(f"{day}/{flag}/{side}: {type(exc).__name__}")
                time.sleep(0.15)
    good = [p for p in probes if p.get("status") == "AUDIT_RECORDED"]
    aligned = all(all(p.get("field_alignment", {}).values()) for p in good if p.get("field_alignment"))
    no_duplicates = all(p.get("duplicate_timestamp_count_all_dates", 0) == 0 for p in good)
    decision = "AUDIT_RECORDED_REVIEW_REQUIRED" if len(good) == 8 else "PARTIAL_OR_FAILED_AUDIT"
    interpretation = (
        f"Recorded {len(good)}/8 probe audits. Field arrays all aligned: {aligned}; duplicate-free timestamps: {no_duplicates}. "
        "Review per-probe date/session counts, first/last timestamps, gaps, expiry semantics and data-use rights. "
        "This diagnostic does not establish full strike coverage, exact contract identity, executable fills, or profitability."
    )
    emit({"checked_at_utc": checked, "decision": decision, "targets": TARGETS, "probes": probes,
          "errors": errors, "interpretation": interpretation})
    print(decision)


if __name__ == "__main__":
    main()
