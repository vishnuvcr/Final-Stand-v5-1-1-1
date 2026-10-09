#!/usr/bin/env python3
"""Bounded, non-promotable OpenChart source probe for Phase 52.

This script deliberately stores only coverage/HTTP diagnostics, never raw OHLCV
bars, full symbol dumps, or token values. A green workflow is not source
acceptance or evidence of strategy profitability.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
from openchart import NSEData, __version__ as OPENCHART_VERSION

IST = ZoneInfo("Asia/Kolkata")
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO_ROOT / "results" / "phase52" / "openchart_probe" / "local"
OLD_TARGETS = [
    {
        "label": "phase51_missing_2026_07_28",
        "query": "NIFTY26JUL",
        "start": datetime(2026, 7, 27, 9, 15, tzinfo=IST),
        "end": datetime(2026, 7, 29, 15, 30, tzinfo=IST),
    },
    {
        "label": "phase51_missing_2026_08_04",
        "query": "NIFTY26AUG",
        "start": datetime(2026, 8, 3, 9, 15, tzinfo=IST),
        "end": datetime(2026, 8, 5, 15, 30, tzinfo=IST),
    },
]


def _jsonable(value: Any) -> Any:
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value


def summarize_bars(
    frame: pd.DataFrame,
    requested_start: datetime,
    requested_end: datetime,
) -> dict[str, Any]:
    """Return aggregate quality diagnostics; do not persist price rows."""
    if frame is None or frame.empty:
        return {
            "rows": 0,
            "empty": True,
            "timestamp_first": None,
            "timestamp_last": None,
            "duplicate_timestamps": None,
            "invalid_ohlc_rows": None,
            "nonpositive_volume_rows": None,
            "timestamp_clock_convention": "UNVERIFIED_NAIVE_INDEX",
        }

    df = frame.copy()
    index = pd.to_datetime(df.index, errors="coerce")
    valid_index = index[~pd.isna(index)]
    has_ohlc = {"Open", "High", "Low", "Close"}.issubset(df.columns)
    duplicate_ts = int(pd.Index(valid_index).duplicated(keep=False).sum())
    invalid_ohlc = None
    if has_ohlc:
        o = pd.to_numeric(df["Open"], errors="coerce")
        h = pd.to_numeric(df["High"], errors="coerce")
        l = pd.to_numeric(df["Low"], errors="coerce")
        c = pd.to_numeric(df["Close"], errors="coerce")
        bad = (
            o.isna() | h.isna() | l.isna() | c.isna()
            | (h < l) | (h < o) | (h < c) | (l > o) | (l > c)
        )
        invalid_ohlc = int(bad.sum())

    vol_bad = None
    if "Volume" in df.columns:
        vol = pd.to_numeric(df["Volume"], errors="coerce")
        vol_bad = int((vol.isna() | (vol < 0)).sum())

    # The library returns a timezone-naive Timestamp index after stripping tz.
    # Report the observed clock range without assuming IST/UTC conversion.
    times_in_ist_clock = None
    if len(valid_index):
        try:
            time_of_day = pd.Series(valid_index).dt.time
            start_clock = pd.Timestamp("09:15:00").time()
            end_clock = pd.Timestamp("15:30:00").time()
            times_in_ist_clock = float(
                ((time_of_day >= start_clock) & (time_of_day <= end_clock)).mean()
            )
        except Exception:
            pass

    try:
        span = {
            "first": _jsonable(valid_index.min()),
            "last": _jsonable(valid_index.max()),
        }
    except Exception:
        span = {"first": None, "last": None}

    return {
        "rows": int(len(df)),
        "empty": False,
        "timestamp_first": span["first"],
        "timestamp_last": span["last"],
        "duplicate_timestamps": duplicate_ts,
        "invalid_ohlc_rows": invalid_ohlc,
        "nonpositive_volume_rows": vol_bad,
        "fraction_timestamp_clock_between_09_15_and_15_30": times_in_ist_clock,
        "requested_start_ist": requested_start.isoformat(),
        "requested_end_ist": requested_end.isoformat(),
        "columns": [str(c) for c in df.columns],
        "timestamp_clock_convention": (
            "UNVERIFIED_NAIVE_INDEX: OpenChart removes timezone metadata; "
            "compare timestamps with an independent known-session anchor before use"
        ),
    }


def _is_option_row(row: dict[str, Any]) -> bool:
    symbol = str(row.get("symbol", "")).strip().upper()
    instrument_type = str(row.get("type", "")).strip().lower()
    # Be tolerant to singular/plural type labels and exchange suffix spacing.
    return ("option" in instrument_type) or bool(
        re.search(r"(?:^|[\s:_-])(CE|PE)\s*$", symbol)
    )


def _is_future_row(row: dict[str, Any]) -> bool:
    symbol = str(row.get("symbol", "")).strip().upper()
    instrument_type = str(row.get("type", "")).strip().lower()
    return ("future" in instrument_type) or bool(re.search(r"FUT\s*$", symbol))


def _safe_search_metadata(frame: pd.DataFrame, query: str) -> dict[str, Any]:
    if frame is None or frame.empty:
        return {
            "query": query,
            "returned_rows": 0,
            "columns": [str(c) for c in frame.columns] if frame is not None else [],
            "instrument_type_counts": {},
            "option_rows": 0,
            "future_rows": 0,
            "option_suffix_rows": 0,
            "future_suffix_rows": 0,
            "target_month_contract_rows": 0,
            "status": "EMPTY_OR_REQUEST_FAILED",
        }
    records = frame.fillna("").to_dict(orient="records")
    options = [r for r in records if _is_option_row(r)]
    futures = [r for r in records if _is_future_row(r)]
    type_col = frame["type"] if "type" in frame.columns else pd.Series(dtype=str)
    type_counts = {
        (str(key) if str(key).strip() else "<blank>"): int(value)
        for key, value in type_col.fillna("").astype(str).value_counts(dropna=False).items()
    }
    symbols = frame["symbol"].fillna("").astype(str) if "symbol" in frame.columns else pd.Series(dtype=str)
    option_suffix_rows = int(symbols.str.upper().str.contains(r"(?:CE|PE)\s*$", regex=True).sum())
    future_suffix_rows = int(symbols.str.upper().str.contains(r"FUT\s*$", regex=True).sum())
    return {
        "query": query,
        "returned_rows": int(len(frame)),
        "columns": [str(c) for c in frame.columns],
        "instrument_type_counts": type_counts,
        "option_rows": int(len(options)),
        "future_rows": int(len(futures)),
        "option_suffix_rows": option_suffix_rows,
        "future_suffix_rows": future_suffix_rows,
        "target_month_contract_rows": int(sum(
            1 for r in options if query.upper() in str(r.get("symbol", "")).upper()
        )),
        # Do not save contract symbols, scripcodes/tokens, or raw search listings.
        "blank_symbol_rows": int((symbols.str.strip() == "").sum()) if len(symbols) else None,
        "rows_with_scripcode": int(frame["scripcode"].notna().sum()) if "scripcode" in frame.columns else None,
        "status": "SYMBOLS_RETURNED",
    }


def attach_http_trace(client: NSEData, minimum_interval_seconds: float = 1.25) -> list[dict[str, Any]]:
    """Trace status metadata and rate-limit requests; never capture response bodies."""
    trace: list[dict[str, Any]] = []
    original_send = client.session.send
    last_request_at = [0.0]

    def traced_send(request, *args, **kwargs):
        elapsed = time.monotonic() - last_request_at[0]
        if last_request_at[0] and elapsed < minimum_interval_seconds:
            time.sleep(minimum_interval_seconds - elapsed)
        started = time.monotonic()
        try:
            response = original_send(request, *args, **kwargs)
            last_request_at[0] = time.monotonic()
            trace.append({
                "host": re.sub(r"^https?://", "", request.url).split("/")[0],
                "path": "/" + "/".join(re.sub(r"^https?://[^/]+", "", request.url).split("/")[1:3]),
                "method": request.method,
                "http_status": int(response.status_code),
                "content_type": response.headers.get("Content-Type"),
                "content_length_bytes": response.headers.get("Content-Length"),
                "retry_after": response.headers.get("Retry-After"),
                "elapsed_seconds": round(time.monotonic() - started, 3),
            })
            return response
        except Exception as exc:
            last_request_at[0] = time.monotonic()
            trace.append({
                "host": re.sub(r"^https?://", "", request.url).split("/")[0],
                "method": request.method,
                "transport_error_type": type(exc).__name__,
                "transport_error": str(exc)[:300],
                "elapsed_seconds": round(time.monotonic() - started, 3),
            })
            raise

    client.session.send = traced_send
    return trace


def self_test() -> None:
    ix = pd.to_datetime(["2026-10-01 09:15:00", "2026-10-01 09:16:00"])
    sample = pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.0, 102.0],
            "Volume": [10, 11],
        },
        index=ix,
    )
    summary = summarize_bars(
        sample,
        datetime(2026, 10, 1, 9, 15, tzinfo=IST),
        datetime(2026, 10, 1, 9, 16, tzinfo=IST),
    )
    assert summary["rows"] == 2
    assert summary["duplicate_timestamps"] == 0
    assert summary["invalid_ohlc_rows"] == 0
    assert summary["nonpositive_volume_rows"] == 0
    assert _is_option_row({"symbol": "NIFTY26OCT25000CE", "type": "Options"})
    assert _is_option_row({"symbol": "NIFTY26OCT25000 PE", "type": "Option"})
    assert _is_future_row({"symbol": "NIFTY26OCTFUT", "type": "Futures"})
    assert not _is_option_row({"symbol": "NIFTY26OCTFUT", "type": "Futures"})
    print("OPENCHART_SELF_TEST_PASS")


def run_probe(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    client = NSEData()
    http_trace = attach_http_trace(client)
    report: dict[str, Any] = {
        "schema_version": "phase52-openchart-probe-v1",
        "created_at_ist": datetime.now(IST).isoformat(),
        "source": {
            "repository": "https://github.com/marketcalls/openchart",
            "upstream_commit": "a207108890c96a9830b35a8d15442c896ea0a9d6",
            "openchart_package_version": OPENCHART_VERSION,
        },
        "purpose": "Bounded data-discovery/coverage probe only; not strategy P&L",
        "raw_market_data_persisted": False,
        "api_request_trace": http_trace,
        "search_probes": [],
        "historical_probes": [],
        "limitations": [
            "A single short probe cannot establish complete contract/expiry coverage or oldest backfill date.",
            "The package exposes OHLCV only; OI, bid/ask, trade prints, depth and Greeks are not returned by its documented DataFrame schema.",
            "Symbol-search failure and no-result responses can both become empty DataFrames in the upstream library; inspect HTTP trace before interpreting empty results.",
            "Returned timestamps are timezone-naive after upstream processing; verify clock convention against authoritative session anchors.",
            "No raw OHLCV, full symbol dump or token values are saved to the repository.",
            "NSE data usage/storage/redistribution terms must be checked separately from the MIT license of this client library.",
        ],
    }
    frames: dict[str, pd.DataFrame] = {}

    query_plan = [("current_nifty_fo", "NIFTY")] + [
        (target["label"], target["query"]) for target in OLD_TARGETS
    ]
    for label, query in query_plan:
        try:
            frame = client.search(query, "FO")
            frames[label] = frame if frame is not None else pd.DataFrame()
            metadata = _safe_search_metadata(frames[label], query)
            metadata["label"] = label
            report["search_probes"].append(metadata)
        except Exception as exc:
            report["search_probes"].append({
                "label": label,
                "query": query,
                "status": "EXCEPTION",
                "exception_type": type(exc).__name__,
                "exception": str(exc)[:300],
            })

    now_ist = datetime.now(IST)
    recent_end = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)
    if recent_end > now_ist:
        recent_end -= timedelta(days=1)
    recent_start = recent_end - timedelta(days=10)
    current_frame = frames.get("current_nifty_fo", pd.DataFrame())
    current_rows = (
        current_frame.fillna("").to_dict(orient="records")
        if current_frame is not None and not current_frame.empty else []
    )
    current_options = [r for r in current_rows if _is_option_row(r)]
    current_options.sort(key=lambda r: str(r.get("symbol", "")))
    probes_to_fetch: list[dict[str, Any]] = []
    if current_options:
        probes_to_fetch.append({
            "label": "recent_listed_nifty_option",
            "record": current_options[0],
            "start": recent_start,
            "end": recent_end,
        })

    for target in OLD_TARGETS:
        frame = frames.get(target["label"], pd.DataFrame())
        records = (
            frame.fillna("").to_dict(orient="records")
            if frame is not None and not frame.empty else []
        )
        options = [r for r in records if _is_option_row(r)]
        options.sort(key=lambda r: str(r.get("symbol", "")))
        if options:
            probes_to_fetch.append({
                "label": target["label"],
                "record": options[0],
                "start": target["start"],
                "end": target["end"],
            })

    for probe in probes_to_fetch:
        record = probe["record"]
        try:
            bars = client.historical_direct(
                token=str(record.get("scripcode", "")),
                symbol=str(record.get("symbol", "")),
                symbol_type=str(record.get("type", "Options")),
                start=probe["start"],
                end=probe["end"],
                interval="1m",
            )
            report["historical_probes"].append({
                "label": probe["label"],
                "interval": "1m",
                "data": summarize_bars(bars, probe["start"], probe["end"]),
            })
        except Exception as exc:
            report["historical_probes"].append({
                "label": probe["label"],
                "interval": "1m",
                "status": "EXCEPTION",
                "exception_type": type(exc).__name__,
                "exception": str(exc)[:300],
            })

    statuses = [x.get("http_status") for x in http_trace if x.get("http_status") is not None]
    report["http_summary"] = {
        "requests_observed": len(http_trace),
        "http_status_counts": {
            str(code): sum(1 for seen in statuses if seen == code)
            for code in sorted(set(statuses))
        },
        "http_errors_or_rate_limits": sum(1 for seen in statuses if seen >= 400),
        "response_bodies_saved": False,
    }
    target_hits = {
        p["label"]: p.get("data", {}).get("rows", 0)
        for p in report["historical_probes"]
        if p["label"] in {t["label"] for t in OLD_TARGETS}
    }
    recent_hits = any(
        p["label"] == "recent_listed_nifty_option" and p.get("data", {}).get("rows", 0) > 0
        for p in report["historical_probes"]
    )
    target_dates_returned = sum(1 for n in target_hits.values() if n > 0)
    report["decision"] = {
        "primary_source_eligible": False,
        "status": (
            "AUXILIARY_SOURCE_CANDIDATE_NEEDS_FURTHER_VALIDATION"
            if recent_hits else "SOURCE_PROBE_INCONCLUSIVE_OR_NO_RECENT_OPTION_BARS"
        ),
        "recent_option_bars_returned": recent_hits,
        "target_date_windows_with_any_bars": target_dates_returned,
        "target_date_windows_tested": len(OLD_TARGETS),
        "interpretation": (
            "Even a positive result only justifies a larger contract/time coverage audit. "
            "Do not use this source as sole backtest data or fill missing records yet."
        ),
    }

    output = out_dir / "probe_report.json"
    output.write_text(json.dumps(report, indent=2, default=_jsonable) + "\n", encoding="utf-8")
    print(json.dumps({
        "report_path": str(output),
        "decision": report["decision"],
        "search_probes": report["search_probes"],
        "historical_probes": report["historical_probes"],
        "http_summary": report["http_summary"],
    }, indent=2, default=_jsonable))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test-only", action="store_true")
    parser.add_argument("--output-dir", default=os.environ.get("OPENCHART_OUTPUT_DIR", str(DEFAULT_OUT)))
    args = parser.parse_args()
    if args.self_test_only:
        self_test()
        return 0
    self_test()
    run_probe(Path(args.output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
