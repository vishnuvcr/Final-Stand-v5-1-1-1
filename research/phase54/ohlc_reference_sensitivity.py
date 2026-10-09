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
EXPECTED_ROWS = 480
EXPECTED_BASELINE = {
    "BLOCKED_LEG_ELIGIBILITY": 100,
    "EXCLUDED_OHLC_RANGE_PROXY": 379,
    "REPLAY_PASS": 1,
}
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


def explicit_hard_oi_block(row: dict[str, str], legs: list[dict[str, Any]]) -> bool:
    """A proven OI failure on any required leg makes the full strategy ineligible at every range threshold."""
    if row.get("status") != "BLOCKED_LEG_ELIGIBILITY":
        return False
    reason = (row.get("exclusion_reason") or "").lower()
    if "prior-bar oi" not in reason and "prior oi" not in reason:
        return False
    return any(
        isinstance(leg, dict)
        and leg.get("status") == "PRIOR_OI_MISSING_OR_BELOW_GATE"
        and number(leg.get("prior_oi")) is not None
        and number(leg.get("prior_oi")) < MIN_PRIOR_OI
        for leg in legs
    )


def complete_leg_payload(row: dict[str, str], legs: list[dict[str, Any]]) -> bool:
    expected = EXPECTED_LEGS.get(row.get("family_id", ""))
    if expected is None or len(legs) != expected:
        return False
    for leg in legs:
        if not isinstance(leg, dict) or not leg.get("leg_id"):
            return False
        oi = number(leg.get("prior_oi"))
        rng = number(leg.get("entry_range_proxy_pct"))
        if oi is None or rng is None:
            return False
        if leg.get("prior_oi_status") not in {"PASS", "FAIL"}:
            return False
        if leg.get("entry_status") not in {"PASS", "FAIL"}:
            return False
    return True


def _base_report(rows: list[dict[str, str]], details: list[dict[str, Any]], reason: str,
                 strict_parent: bool) -> dict[str, Any]:
    baseline_status = Counter(row.get("status", "MISSING") for row in rows)
    complete_rows = sum(bool(x["complete"]) for x in details)
    hard_oi_rows = sum(bool(x["hard_oi_block"]) for x in details)
    empty_rows = sum(x["detail"] == "EMPTY_LEG_PAYLOAD" for x in details)
    partial_rows = sum(x["detail"] == "PARTIAL_LEG_PAYLOAD" for x in details)
    complete_range = sum(
        x["complete"] and x["row"].get("status") == "EXCLUDED_OHLC_RANGE_PROXY"
        for x in details
    )
    payload_detail = Counter((x["row"].get("status", "MISSING"), x["detail"]) for x in details)
    return {
        "phase": "54",
        "status": "OHLC_REFERENCE_SENSITIVITY_BLOCKED_INCOMPLETE_LEG_EVIDENCE",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": {
            "path": str(INPUT.relative_to(ROOT)),
            "row_count": len(rows),
            "source_revision": "0f4800e43e6f96cec0794369d78eb4d3c4211ef5",
            "input_sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest() if INPUT.exists() else None,
            "parent_grid": "phase52-grid-v1.3",
            "parent_pilot": "phase52-historical-base-pilot-v0.2.1-audit-provenance",
        },
        "frozen_rules": {
            "baseline_range_proxy_pct": 2,
            "prior_minute_oi_minimum": MIN_PRIOR_OI,
            "thresholds_preregistered": list(THRESHOLDS),
            "threshold_sensitivity_computed": False,
            "holdout_used": False,
            "raw_data_downloaded": False,
            "historical_pnl_recalculated": False,
            "bid_ask_spread_observed": False,
            "live_execution_or_promotion_allowed": False,
        },
        "baseline_status_counts": dict(sorted(baseline_status.items())),
        "leg_payload_detail_counts": {
            f"{status}::{detail}": count
            for (status, detail), count in sorted(payload_detail.items())
        },
        "complete_leg_payload_rows": complete_rows,
        "incomplete_leg_payload_rows": len(rows) - complete_rows,
        "empty_leg_payload_rows": empty_rows,
        "partial_leg_payload_rows": partial_rows,
        "known_hard_oi_block_rows": hard_oi_rows,
        "range_excluded_rows_with_complete_leg_payload": complete_range,
        "strict_prior_oi_blocked_rows_by_parent_status": baseline_status.get("BLOCKED_LEG_ELIGIBILITY", 0),
        "range_excluded_rows_by_parent_status": baseline_status.get("EXCLUDED_OHLC_RANGE_PROXY", 0),
        "replay_pass_rows_by_parent_status": baseline_status.get("REPLAY_PASS", 0),
        "sensitivity_block_reason": reason,
        "threshold_sensitivity": [{
            "threshold_pct": t, "computable": False, "eligible_rows": None,
            "share_of_planned_pct": None, "oi_or_legs_rejected_rows": None,
            "entry_data_rejected_rows": None, "range_rejected_rows": None,
            "reconciliation_total": None, "reason": reason,
        } for t in THRESHOLDS],
        "family_coverage": [],
        "interpretation": [
            "This run did not compute alternate-threshold counts because at least one row lacked sufficient per-leg evidence to classify safely.",
            "A multi-leg row cannot be assumed eligible from a partial leg payload; the audit fails closed unless an observed prior-OI failure conclusively rejects the whole strategy at every threshold.",
            "The OHLC high-low/open percentage is a candle-range proxy, not a quoted bid/ask spread or executable liquidity measure.",
            "This is not a backtest: no exits, fills, fees, costs, P&L, strategy superiority or promotion can be inferred.",
        ],
    }


def analyze(rows: list[dict[str, str]], strict_parent: bool = False) -> dict[str, Any]:
    """Recompute eligibility counts while holding all non-range gates fixed."""
    if not rows:
        raise ValueError("Phase 52 event_replay.csv contains no data rows")
    required = {"configuration_id", "event_id", "status", "resolved_legs_json", "split", "family_id", "exclusion_reason"}
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"Phase 52 event replay missing required columns: {sorted(missing)}")

    baseline_status = Counter(row.get("status", "MISSING") for row in rows)
    if strict_parent and (len(rows) != EXPECTED_ROWS or dict(baseline_status) != EXPECTED_BASELINE):
        raise ValueError(
            f"Frozen parent reconciliation failed: rows={len(rows)} statuses={dict(sorted(baseline_status.items()))}; "
            f"expected rows={EXPECTED_ROWS}, statuses={EXPECTED_BASELINE}"
        )

    details: list[dict[str, Any]] = []
    blocking_reasons: list[str] = []
    for row in rows:
        legs = legs_for(row)
        expected = EXPECTED_LEGS.get(row.get("family_id", ""))
        hard_oi = explicit_hard_oi_block(row, legs)
        complete = complete_leg_payload(row, legs)
        if hard_oi:
            detail = "KNOWN_HARD_OI_BLOCK"
        elif not legs:
            detail = "EMPTY_LEG_PAYLOAD"
        elif expected is None:
            detail = "UNKNOWN_EXPECTED_LEG_COUNT"
        elif len(legs) < expected:
            detail = "PARTIAL_LEG_PAYLOAD"
        elif len(legs) > expected:
            detail = "LEG_COUNT_EXCEEDS_EXPECTED"
        elif not complete:
            detail = "MISSING_REQUIRED_LEG_FIELDS"
        else:
            detail = "COMPLETE_LEG_PAYLOAD"
        if not complete and not hard_oi:
            blocking_reasons.append(
                f"{row.get('configuration_id')}::{row.get('event_id')}::{row.get('status')}::{detail}"
            )
        details.append({"row": row, "legs": legs, "expected": expected, "complete": complete,
                        "hard_oi_block": hard_oi, "detail": detail})

    if blocking_reasons:
        result = _base_report(
            rows, details,
            f"Not computed: {len(blocking_reasons)} rows lack complete per-leg eligibility/range evidence and are not conclusively rejected by an explicit observed prior-OI failure. Example: {blocking_reasons[0]}",
            strict_parent,
        )
        return result

    threshold_results: list[dict[str, Any]] = []
    family_coverage: list[dict[str, Any]] = []
    oi_counts = []
    entry_counts = []
    eligible_history = []
    for threshold in THRESHOLDS:
        categories = Counter()
        by_family: dict[str, Counter] = defaultdict(Counter)
        for item in details:
            row = item["row"]
            family = row.get("family_id", "UNKNOWN")
            if item["hard_oi_block"]:
                categories["oi_or_legs_rejected_rows"] += 1
                by_family[family]["oi_or_legs_rejected_rows"] += 1
                continue
            legs = item["legs"]
            oi_bad = any(
                leg.get("prior_oi_status") != "PASS"
                or number(leg.get("prior_oi")) is None
                or number(leg.get("prior_oi")) < MIN_PRIOR_OI
                for leg in legs
            )
            if oi_bad:
                categories["oi_or_legs_rejected_rows"] += 1
                by_family[family]["oi_or_legs_rejected_rows"] += 1
                continue
            entry_bad = any(
                leg.get("entry_status") != "PASS"
                or number(leg.get("entry_range_proxy_pct")) is None
                for leg in legs
            )
            if entry_bad:
                categories["entry_data_rejected_rows"] += 1
                by_family[family]["entry_data_rejected_rows"] += 1
                continue
            max_range = max(number(leg["entry_range_proxy_pct"]) for leg in legs)
            if max_range > threshold:
                categories["range_rejected_rows"] += 1
                by_family[family]["range_rejected_rows"] += 1
                continue
            categories["eligible_rows"] += 1
            by_family[family]["eligible_rows"] += 1

        total = sum(categories.values())
        if total != len(rows):
            raise AssertionError(f"Threshold {threshold}% categories sum to {total}, expected {len(rows)}")
        eligible = categories["eligible_rows"]
        eligible_history.append(eligible)
        oi_counts.append(categories["oi_or_legs_rejected_rows"])
        entry_counts.append(categories["entry_data_rejected_rows"])
        threshold_results.append({
            "threshold_pct": threshold,
            "computable": True,
            "eligible_rows": eligible,
            "share_of_planned_pct": round(100.0 * eligible / len(rows), 6),
            "oi_or_legs_rejected_rows": categories["oi_or_legs_rejected_rows"],
            "entry_data_rejected_rows": categories["entry_data_rejected_rows"],
            "range_rejected_rows": categories["range_rejected_rows"],
            "reconciliation_total": total,
            "reason": "Computed from complete leg payloads; known prior-OI failures remain excluded at every threshold.",
        })
        for family in sorted({x["row"].get("family_id", "UNKNOWN") for x in details}):
            fcounts = by_family[family]
            n_family = sum(1 for x in details if x["row"].get("family_id", "UNKNOWN") == family)
            family_coverage.append({
                "threshold_pct": threshold,
                "family_id": family,
                "planned_rows": n_family,
                "eligible_rows": fcounts["eligible_rows"],
                "share_eligible_pct": round(100.0 * fcounts["eligible_rows"] / n_family, 6) if n_family else 0,
                "oi_or_legs_rejected_rows": fcounts["oi_or_legs_rejected_rows"],
                "entry_data_rejected_rows": fcounts["entry_data_rejected_rows"],
                "range_rejected_rows": fcounts["range_rejected_rows"],
            })

    if any(b < a for a, b in zip(eligible_history, eligible_history[1:])):
        raise AssertionError("Eligibility count decreased when the OHLC range threshold increased")
    if len(set(oi_counts)) != 1 or len(set(entry_counts)) != 1:
        raise AssertionError("Non-range rejection categories changed across range thresholds")
    if strict_parent and threshold_results[0]["eligible_rows"] != EXPECTED_BASELINE["REPLAY_PASS"]:
        raise AssertionError(
            f"At the frozen 2% threshold expected {EXPECTED_BASELINE['REPLAY_PASS']} eligible row, got "
            f"{threshold_results[0]['eligible_rows']}"
        )

    result = _base_report(rows, details, "", strict_parent)
    result.update({
        "status": "OHLC_REFERENCE_SENSITIVITY_COMPUTED_COVERAGE_ONLY",
        "sensitivity_block_reason": None,
        "frozen_rules": {**result["frozen_rules"], "threshold_sensitivity_computed": True},
        "threshold_sensitivity": threshold_results,
        "family_coverage": family_coverage,
        "oi_rejections_invariant_across_thresholds": len(set(oi_counts)) == 1,
        "entry_data_rejections_invariant_across_thresholds": len(set(entry_counts)) == 1,
        "eligible_rows_monotonic_non_decreasing": True,
        "interpretation": [
            "Threshold counts are descriptive eligibility/coverage diagnostics only; they do not validate executable fills, bid/ask spread, exits or profitability.",
            "The 100 rows explicitly blocked by observed prior-bar OI below the fixed minimum remain rejected at every threshold. The remaining leg payload is unnecessary for those rows because one required leg failure is sufficient to reject the complete multi-leg strategy.",
            "Every range-excluded row and the single baseline replay-pass row has a complete selected-leg payload; alternate thresholds were computed only from those leg-specific OI, entry-status and range-proxy fields.",
            "The OHLC high-low/open percentage is a candle-range proxy, not a quoted bid/ask spread or executable liquidity measure.",
            "No P&L, fill, exit, transaction-cost, Sharpe, drawdown or strategy ranking calculations were performed; no holdout used and no strategy promoted.",
            "The pinned source is declared CC BY-NC 4.0; commercial/live strategy promotion remains prohibited by the source-license and execution-data gates.",
        ],
    })
    return result


def write_outputs(result: dict[str, Any], out_dir: Path = OUT) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    with (out_dir / "threshold_sensitivity.csv").open("w", newline="", encoding="utf-8") as fh:
        fields = ["threshold_pct", "computable", "eligible_rows", "share_of_planned_pct",
                  "oi_or_legs_rejected_rows", "entry_data_rejected_rows", "range_rejected_rows",
                  "reconciliation_total", "reason"]
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(result["threshold_sensitivity"])
    with (out_dir / "family_coverage.csv").open("w", newline="", encoding="utf-8") as fh:
        fields = ["threshold_pct", "family_id", "planned_rows", "eligible_rows", "share_eligible_pct",
                  "oi_or_legs_rejected_rows", "entry_data_rejected_rows", "range_rejected_rows"]
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(result.get("family_coverage", []))
    computed = result["frozen_rules"]["threshold_sensitivity_computed"]
    title = "Phase 54 OHLC-reference sensitivity results" if computed else "Phase 54 OHLC-reference sensitivity feasibility audit"
    lines = [
        f"# {title}", "",
        ("**COMPUTED — coverage sensitivity only. No P&L or executable liquidity claim.**" if computed
         else "**BLOCKED: alternate-threshold eligibility is not computable from the stored parent output.**"), "",
        f"- Input rows: {result['input']['row_count']}",
        f"- Input SHA-256: {result['input']['input_sha256']}",
        f"- Baseline statuses: {json.dumps(result['baseline_status_counts'], sort_keys=True)}",
        f"- Complete per-leg payload rows: {result['complete_leg_payload_rows']}",
        f"- Incomplete per-leg payload rows: {result['incomplete_leg_payload_rows']}",
        f"- Explicit hard prior-OI blockers with sufficient evidence to reject the full strategy: {result.get('known_hard_oi_block_rows', 0)}",
        f"- Range-excluded rows with complete leg payload: {result['range_excluded_rows_with_complete_leg_payload']}", "",
        "| Threshold (%) | Eligible | Eligible (%) | OI/leg rejected | Entry-data rejected | Range rejected | Reconciled rows |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["threshold_sensitivity"]:
        if row["computable"]:
            lines.append(
                f"| {row['threshold_pct']} | {row['eligible_rows']} | {row['share_of_planned_pct']:.3f} | "
                f"{row['oi_or_legs_rejected_rows']} | {row['entry_data_rejected_rows']} | "
                f"{row['range_rejected_rows']} | {row['reconciliation_total']} |"
            )
        else:
            lines.append(f"| {row['threshold_pct']} | — | — | — | — | — | — |")
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
             "family_id":"BEAR_CALL_SPREAD","exclusion_reason":"L1 range gate",
             "resolved_legs_json":json.dumps([
                 {"leg_id":"L1","prior_oi":500,"prior_oi_status":"PASS","entry_status":"PASS","entry_range_proxy_pct":5.5},
                 {"leg_id":"L2","prior_oi":600,"prior_oi_status":"PASS","entry_status":"PASS","entry_range_proxy_pct":3.0}])},
            {"configuration_id":"c2","event_id":"e1","status":"BLOCKED_LEG_ELIGIBILITY","split":"development",
             "family_id":"BUY_CALL","exclusion_reason":"a required selected leg lacks exact prior-bar OI at or above 100",
             "resolved_legs_json":json.dumps([
                 {"leg_id":"L1","prior_oi":0,"status":"PRIOR_OI_MISSING_OR_BELOW_GATE"}])},
        ]
        result = analyze(sample)
        assert result["status"] == "OHLC_REFERENCE_SENSITIVITY_COMPUTED_COVERAGE_ONLY"
        assert result["threshold_sensitivity"][0]["eligible_rows"] == 0
        assert result["threshold_sensitivity"][0]["oi_or_legs_rejected_rows"] == 1
        assert result["threshold_sensitivity"][0]["range_rejected_rows"] == 1
        assert result["threshold_sensitivity"][2]["eligible_rows"] == 1
        print("Phase 54 evidence-completeness/coverage self-test PASS")
        return
    result = analyze(read_rows(), strict_parent=True)
    write_outputs(result, args.output)
    print(json.dumps({
        "status":result["status"],"rows":result["input"]["row_count"],
        "baseline_status_counts":result["baseline_status_counts"],
        "complete_leg_payload_rows":result["complete_leg_payload_rows"],
        "incomplete_leg_payload_rows":result["incomplete_leg_payload_rows"],
        "known_hard_oi_block_rows":result.get("known_hard_oi_block_rows"),
        "threshold_sensitivity_computed":result["frozen_rules"]["threshold_sensitivity_computed"],
        "threshold_sensitivity":result["threshold_sensitivity"],
        "input_sha256":result["input"]["input_sha256"],"output":str(args.output)
    }, indent=2))


if __name__ == "__main__":
    main()
