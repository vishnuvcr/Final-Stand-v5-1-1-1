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
EXPECTED_LEGS = {
    "BUY_CALL": 1, "BUY_PUT": 1, "BULL_CALL_SPREAD": 2, "BEAR_CALL_SPREAD": 2,
    "SHORT_IRON_CONDOR": 4, "LONG_STRADDLE": 2, "LONG_STRANGLE": 2,
}

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
    """Audit whether stored rows contain enough complete leg evidence for a valid sensitivity."""
    if not rows:
        raise ValueError("Phase 52 event_replay.csv contains no data rows")
    required = {"configuration_id", "event_id", "status", "resolved_legs_json", "split", "family_id"}
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"Phase 52 event replay missing required columns: {sorted(missing)}")
    baseline_status = Counter(row.get("status", "MISSING") for row in rows)
    detail_status = Counter()
    details = []
    for row in rows:
        legs = legs_for(row)
        expected = EXPECTED_LEGS.get(row.get("family_id", ""))
        complete = bool(legs) and expected is not None and len(legs) == expected and all(
            isinstance(leg, dict) and leg.get("leg_id") for leg in legs
        )
        if not legs:
            detail = "EMPTY_LEG_PAYLOAD"
        elif expected is None:
            detail = "UNKNOWN_EXPECTED_LEG_COUNT"
        elif len(legs) < expected:
            detail = "PARTIAL_LEG_PAYLOAD"
        elif len(legs) > expected:
            detail = "LEG_COUNT_EXCEEDS_EXPECTED"
        else:
            detail = "COMPLETE_LEG_PAYLOAD"
        detail_status[(row.get("status", "MISSING"), detail)] += 1
        details.append({"row": row, "legs": legs, "expected": expected, "complete": complete, "detail": detail})

    complete_rows = [x for x in details if x["complete"]]
    incomplete_rows = [x for x in details if not x["complete"]]
    complete_range_exclusions = sum(
        x["row"].get("status") == "EXCLUDED_OHLC_RANGE_PROXY" for x in complete_rows
    )
    missing_leg_payload = sum(x["detail"] == "EMPTY_LEG_PAYLOAD" for x in details)
    partial_leg_payload = sum(x["detail"] == "PARTIAL_LEG_PAYLOAD" for x in details)
    oi_blocked = baseline_status.get("BLOCKED_LEG_ELIGIBILITY", 0)
    range_excluded = baseline_status.get("EXCLUDED_OHLC_RANGE_PROXY", 0)
    replay_pass = baseline_status.get("REPLAY_PASS", 0)

    threshold_rows = [{
        "threshold_pct": threshold,
        "computable": False,
        "eligible_rows": None,
        "share_of_planned_pct": None,
        "reason": "Not computed: parent event_replay output does not preserve complete per-leg evidence for every row. Replaying the threshold from partial payload would invent leg coverage.",
    } for threshold in THRESHOLDS]

    return {
        "phase": "54",
        "status": "OHLC_REFERENCE_SENSITIVITY_BLOCKED_INCOMPLETE_LEG_EVIDENCE",
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
            "thresholds_preregistered": list(THRESHOLDS),
            "threshold_sensitivity_computed": False,
            "holdout_used": False, "raw_data_downloaded": False,
            "historical_pnl_recalculated": False, "bid_ask_spread_observed": False,
            "live_execution_or_promotion_allowed": False,
        },
        "baseline_status_counts": dict(sorted(baseline_status.items())),
        "leg_payload_detail_counts": {
            f"{status}::{detail}": count
            for (status, detail), count in sorted(detail_status.items())
        },
        "complete_leg_payload_rows": len(complete_rows),
        "incomplete_leg_payload_rows": len(incomplete_rows),
        "empty_leg_payload_rows": missing_leg_payload,
        "partial_leg_payload_rows": partial_leg_payload,
        "range_excluded_rows_with_complete_leg_payload": complete_range_exclusions,
        "strict_prior_oi_blocked_rows_by_parent_status": oi_blocked,
        "range_excluded_rows_by_parent_status": range_excluded,
        "replay_pass_rows_by_parent_status": replay_pass,
        "threshold_sensitivity": threshold_rows,
        "interpretation": [
            "The 480-row parent status reconciliation is retained: 100 BLOCKED_LEG_ELIGIBILITY, 379 EXCLUDED_OHLC_RANGE_PROXY, and 1 REPLAY_PASS.",
            "A 373-row empty leg payload and partial payloads on range-excluded multi-leg strategies prevent faithful recalculation at alternate thresholds.",
            "The exclusion reason may identify one failing leg, but the persisted payload does not necessarily include every leg's OHLC/OI values. That is insufficient to determine whether a row would pass a different threshold.",
            "No alternative threshold eligibility counts are reported. The correct next step is to repair the Phase 52 audit output to preserve all selected legs for every exclusion, then rerun this preregistered sensitivity.",
            "The OHLC high-low/open percentage is a candle-range proxy, not a quoted spread or executable liquidity measure.",
            "This is not a backtest; no exits, fills, costs, P&L, strategy superiority or promotion can be inferred.",
        ],
    }


def write_outputs(result: dict[str, Any], out_dir: Path = OUT) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    with (out_dir / "threshold_sensitivity.csv").open("w", newline="", encoding="utf-8") as fh:
        fields = ["threshold_pct", "computable", "eligible_rows", "share_of_planned_pct", "reason"]
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(result["threshold_sensitivity"])
    lines = [
        "# Phase 54 OHLC-reference sensitivity feasibility audit", "",
        "**BLOCKED: alternate-threshold eligibility is not computable from the stored parent output. No P&L was recalculated.**", "",
        f"- Input rows: {result['input']['row_count']}",
        f"- Baseline statuses: {json.dumps(result['baseline_status_counts'], sort_keys=True)}",
        f"- Complete per-leg payload rows: {result['complete_leg_payload_rows']}",
        f"- Incomplete per-leg payload rows: {result['incomplete_leg_payload_rows']}",
        f"- Empty leg payload rows: {result['empty_leg_payload_rows']}",
        f"- Partial leg payload rows: {result['partial_leg_payload_rows']}",
        f"- Range-excluded rows with complete leg payload: {result['range_excluded_rows_with_complete_leg_payload']}", "",
        "| Threshold (%) | Sensitivity computable? | Result |",
        "|---:|:---:|---|",
    ]
    for row in result["threshold_sensitivity"]:
        lines.append(f"| {row['threshold_pct']} | No | {row['reason']} |")
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
        assert result["threshold_sensitivity"][0]["rejected_for_prior_oi"] == 1
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
