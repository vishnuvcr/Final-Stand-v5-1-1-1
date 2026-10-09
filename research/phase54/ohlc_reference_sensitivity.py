#!/usr/bin/env python3
"""Phase 54: non-executable OHLC-reference eligibility sensitivity.

Reads frozen Phase 52 output. Does not change source data, grid, OI rule, holdout,
costs or trade outcomes, and does not calculate P&L. Candle range is not spread.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "results/phase52/historical_pilot/event_replay.csv"
OUT = ROOT / "results/phase54/ohlc_reference_sensitivity"
THRESHOLDS = (2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 1000)
MIN_PRIOR_OI = 100

def read_rows(path: Path = INPUT) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))

def legs_for(row: dict[str, str]) -> list[dict[str, Any]]:
    try:
        value = json.loads(row.get("resolved_legs_json") or "[]")
    except (json.JSONDecodeError, TypeError):
        return []
    return value if isinstance(value, list) else []

def number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None

def analyze(rows: list[dict[str, str]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("Phase 52 event_replay.csv contains no data rows")
    required = {"configuration_id", "event_id", "status", "resolved_legs_json", "split"}
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"Phase 52 event replay missing required columns: {sorted(missing)}")
    baseline_status = Counter(row.get("status", "MISSING") for row in rows)
    parsed = []
    for row in rows:
        legs = legs_for(row)
        if not legs:
            parsed.append((row, legs, False, False, None))
            continue
        prior_ok = all(
            leg.get("prior_oi_status") == "PASS" and (number(leg.get("prior_oi")) or 0) >= MIN_PRIOR_OI
            for leg in legs
        )
        entry_data_ok = all(
            leg.get("entry_status") == "PASS" and number(leg.get("entry_range_proxy_pct")) is not None
            for leg in legs
        )
        ranges = [number(leg.get("entry_range_proxy_pct")) for leg in legs]
        max_range = max((x for x in ranges if x is not None), default=None)
        parsed.append((row, legs, prior_ok, entry_data_ok, max_range))
    threshold_rows = []
    for threshold in THRESHOLDS:
        qualified = []
        rejected_oi = rejected_entry_data = rejected_range = 0
        for row, legs, prior_ok, entry_data_ok, max_range in parsed:
            if not legs or not prior_ok:
                rejected_oi += 1
            elif not entry_data_ok:
                rejected_entry_data += 1
            elif max_range is None or max_range > threshold:
                rejected_range += 1
            else:
                qualified.append(row)
        by_family = Counter(row.get("family_id", "UNKNOWN") for row in qualified)
        threshold_rows.append({
            "threshold_pct": threshold,
            "planned_config_event_rows": len(rows),
            "rows_meeting_prior_oi_entry_data_and_range_gate": len(qualified),
            "share_of_planned_pct": round(100 * len(qualified) / len(rows), 4),
            "rejected_for_prior_oi_or_missing_legs": rejected_oi,
            "rejected_for_entry_data": rejected_entry_data,
            "rejected_for_range_proxy": rejected_range,
            "families_with_at_least_one_qualified_row": len(by_family),
            "qualified_rows_by_family": dict(sorted(by_family.items())),
            "note": "Eligibility counts only; exits, executable quotes, fills, costs, and P&L are not evaluated.",
        })
    oi_fail_rows = [row for row, legs, prior_ok, _, _ in parsed if not legs or not prior_ok]
    status_split = defaultdict(Counter)
    for row in rows:
        status_split[row.get("split", "UNKNOWN")][row.get("status", "MISSING")] += 1
    return {
        "phase": "54",
        "status": "OHLC_REFERENCE_SENSITIVITY_COMPLETE_NON_EXECUTABLE",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": {
            "path": str(INPUT.relative_to(ROOT)), "row_count": len(rows),
            "source_revision": "0f4800e43e6f96cec0794369d78eb4d3c4211ef5",
            "input_sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest(),
            "parent_grid": "phase52-grid-v1.3",
            "parent_pilot": "phase52-historical-base-pilot-v0.2.1-audit-provenance",
        },
        "frozen_rules": {
            "baseline_range_proxy_pct": 2, "prior_minute_oi_minimum": MIN_PRIOR_OI,
            "thresholds_are_sensitivity_only": True, "holdout_used": False,
            "raw_data_downloaded": False, "historical_pnl_recalculated": False,
            "bid_ask_spread_observed": False, "live_execution_or_promotion_allowed": False,
        },
        "baseline_status_counts": dict(sorted(baseline_status.items())),
        "status_counts_by_split": {k: dict(sorted(v.items())) for k, v in sorted(status_split.items())},
        "strict_prior_oi_fail_row_count": len(oi_fail_rows),
        "threshold_sensitivity": threshold_rows,
        "interpretation": [
            "The OHLC high-low/open percentage is a candle-range proxy, not a quoted spread or executable liquidity measure.",
            "Relaxing this threshold changes only a diagnostic eligibility count; it does not establish valid exits, fills, profitability or strategy superiority.",
            "Rows blocked by missing/zero strictly prior-minute OI remain blocked under every threshold.",
            "This output is not a backtest and cannot be used to promote a strategy or tune a live selector.",
        ],
    }

def write_outputs(result: dict[str, Any], out_dir: Path = OUT) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    fields = ["threshold_pct", "planned_config_event_rows", "rows_meeting_prior_oi_entry_data_and_range_gate",
              "share_of_planned_pct", "rejected_for_prior_oi_or_missing_legs", "rejected_for_entry_data",
              "rejected_for_range_proxy", "families_with_at_least_one_qualified_row", "note"]
    with (out_dir / "threshold_sensitivity.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in result["threshold_sensitivity"]:
            writer.writerow({k: row[k] for k in fields})
    lines = [
        "# Phase 54 OHLC-reference sensitivity", "",
        "**Non-executable diagnostic only. No P&L was recalculated and no strategy was promoted.**", "",
        f"- Input rows: {result['input']['row_count']}",
        f"- Baseline statuses: {json.dumps(result['baseline_status_counts'], sort_keys=True)}",
        f"- Strict prior-minute OI failure rows: {result['strict_prior_oi_fail_row_count']}", "",
        "| OHLC range threshold (%) | Rows passing prior-OI + entry-data + range checks | % of 480 | Prior-OI/legs rejected | Entry-data rejected | Range rejected |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["threshold_sensitivity"]:
        lines.append(f"| {row['threshold_pct']} | {row['rows_meeting_prior_oi_entry_data_and_range_gate']} | "
                     f"{row['share_of_planned_pct']:.2f}% | {row['rejected_for_prior_oi_or_missing_legs']} | "
                     f"{row['rejected_for_entry_data']} | {row['rejected_for_range_proxy']} |")
    lines.extend(["", "## Interpretation", *[f"- {x}" for x in result["interpretation"]], ""])
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--self-test-only", action="store_true")
    args = parser.parse_args()
    if args.self_test_only:
        sample = [
            {"configuration_id":"c1","event_id":"e1","status":"EXCLUDED_OHLC_RANGE_PROXY","split":"development",
             "resolved_legs_json":json.dumps([{"prior_oi_status":"PASS","prior_oi":500,"entry_status":"PASS","entry_range_proxy_pct":2.5}])},
            {"configuration_id":"c2","event_id":"e1","status":"BLOCKED_LEG_ELIGIBILITY","split":"development",
             "resolved_legs_json":json.dumps([{"prior_oi_status":"FAIL","prior_oi":0,"entry_status":"PASS","entry_range_proxy_pct":1.0}])},
        ]
        result = analyze(sample)
        assert result["threshold_sensitivity"][0]["rows_meeting_prior_oi_entry_data_and_range_gate"] == 0
        assert result["threshold_sensitivity"][1]["rows_meeting_prior_oi_entry_data_and_range_gate"] == 1
        assert result["threshold_sensitivity"][0]["rejected_for_prior_oi_or_missing_legs"] == 1
        print("Phase 54 self-test PASS")
        return
    result = analyze(read_rows())
    write_outputs(result, args.output)
    print(json.dumps({"status":result["status"],"rows":result["input"]["row_count"],
      "baseline_status_counts":result["baseline_status_counts"],
      "sensitivity":[{"threshold_pct":x["threshold_pct"],"qualified":x["rows_meeting_prior_oi_entry_data_and_range_gate"]}
      for x in result["threshold_sensitivity"]],"output":str(args.output)}, indent=2))

if __name__ == "__main__":
    main()
