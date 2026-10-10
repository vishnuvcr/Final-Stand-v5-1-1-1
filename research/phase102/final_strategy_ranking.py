#!/usr/bin/env python3
"""Validate Phase 102 scorecard against committed research artifacts.

Standard-library only. This is an evidence-integrity checker, not a backtester.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def load_json(root: Path, rel: str) -> Any:
    with (root / rel).open("r", encoding="utf-8") as stream:
        return json.load(stream)


def load_csv(root: Path, rel: str) -> list[dict[str, str]]:
    with (root / rel).open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def close(a: float, b: float, tolerance: float = 0.02) -> bool:
    return abs(a - b) <= tolerance


def build_validation(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, observed: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "observed": observed})

    tt03 = load_json(root, "results/phase50b/tt03_dynamic_n_replay/summary.json")
    tt03_decision = load_json(root, "results/phase50b/tt03_dynamic_n_replay/terminal_decision.json")
    tt03_splits = load_csv(root, "results/phase50b/tt03_dynamic_n_replay/split_summary.csv")
    hold = next((row for row in tt03_splits if row["split"].strip().upper() == "HOLD"), None)
    check(
        "TT03 coverage/trade-count contract",
        int(tt03["trades"]) == 200 and int(tt03["candidate_trades"]) == 201
        and float(tt03["coverage_rate"]) >= 0.95 and int(tt03["coverage_exclusions"]) == 1,
        f"trades={tt03['trades']}; candidates={tt03['candidate_trades']}; coverage={tt03['coverage_rate']}; exclusions={tt03['coverage_exclusions']}",
    )
    check(
        "TT03 positive registered cost scenarios",
        float(tt03["net"]) > 0 and float(tt03["net50"]) > 0
        and float(tt03["net20_50"]) > 0,
        f"net={tt03['net']}; +50% friction={tt03['net50']}; ₹20/order +50%={tt03['net20_50']}",
    )
    check(
        "TT03 limited HOLD sample explicitly retained",
        hold is not None and int(hold["trades"]) == 3
        and close(float(hold["net"]), 6201.7881),
        f"HOLD={hold}",
    )
    check(
        "TT03 terminal status not mistaken for promotion",
        tt03_decision.get("status") == "PASS"
        and bool(tt03_decision.get("promotion_eligible")) is True,
        f"source terminal status={tt03_decision.get('status')}; source promotion_eligible={tt03_decision.get('promotion_eligible')}; interpretation remains Phase-102 validation-only",
    )

    control_rows = load_csv(root, "results/phase38_corrected_model_robustness/risk_adjusted_summary.csv")
    control = next((r for r in control_rows if r["selector"] == "STATEFUL_CONTROL"), None)
    overlays = [r for r in control_rows if r["selector"] != "STATEFUL_CONTROL"]
    check(
        "Phase 38 control comparator",
        control is not None and int(control["trades"]) == 206
        and close(float(control["net_rupees"]), 63672.5753)
        and close(float(control["max_drawdown_rupees"]), 61960.8731),
        f"control={control}",
    )
    check(
        "No tested Phase 38 overlay outranks control full-sample net",
        control is not None and len(overlays) == 5
        and all(float(row["net_rupees"]) < float(control["net_rupees"]) for row in overlays),
        f"overlays={len(overlays)}; lower-net count={sum(float(row['net_rupees']) < float(control['net_rupees']) for row in overlays)}",
    )

    tt04 = load_json(root, "results/phase51/available_oos/tt04/summary.json")
    tt05 = load_json(root, "results/phase51/available_oos/tt05/summary.json")
    tt02 = load_json(root, "results/phase51/available_oos/tt02/summary.json")
    phase78 = (root / "results/phase78_temporal_stability/report.md").read_text(encoding="utf-8")
    phase79 = (root / "results/phase79_final_evidence_gate/report.md").read_text(encoding="utf-8")
    check(
        "TT04/TT05 partial positive and stress values",
        int(tt04["trades"]) == 62 and int(tt05["trades"]) == 62
        and close(float(tt04["net"]), 13271.5063)
        and close(float(tt04["net20_50"]), 5897.6595)
        and close(float(tt05["net"]), 17098.1466)
        and close(float(tt05["net20_50"]), 9850.1199),
        f"TT04 net/stress={tt04['net']}/{tt04['net20_50']}; TT05={tt05['net']}/{tt05['net20_50']}",
    )
    check(
        "TT04/TT05 temporal instability remains documented",
        "NO_PROMOTION_TEMPORAL_STABILITY_FAIL" in phase78
        and "-6456.2946" in phase78 and "-40244.6808" in phase78
        and "NO_GO_INSUFFICIENT_EVIDENCE" in phase79,
        "Phase 78 historical HOLD negative for both; Phase 79 final gate no-go",
    )
    check(
        "TT02 negative under registered costs",
        int(tt02["trades"]) == 13 and float(tt02["net"]) < 0
        and float(tt02["net50"]) < 0 and float(tt02["net20_50"]) < 0,
        f"trades={tt02['trades']}; net={tt02['net']}; stress={tt02['net20_50']}",
    )

    u02_rows = load_csv(root, "results/phase101_pdf_strategy_tests/u02_strategy_summary.csv")
    u05_rows = load_csv(root, "results/phase101_pdf_strategy_tests/u05_summary.csv")
    check(
        "U02 equity accounting reconciles and tested models depleted",
        len(u02_rows) == 3
        and all(row["equity_reconciliation_pass"].strip().lower() == "true" for row in u02_rows)
        and all(float(row["net_pnl_rupees"]) < 0 and float(row["ending_account_equity"]) < 100 for row in u02_rows),
        "; ".join(f"{row['model']}: net={row['net_pnl_rupees']}; ending={row['ending_account_equity']}" for row in u02_rows),
    )
    check(
        "U05 seven-trade negative proxy not generalised",
        len(u05_rows) == 1 and int(u05_rows[0]["completed_trades"]) == 7
        and float(u05_rows[0]["net_pnl_rupees"]) < 0
        and "modern-sample proxy" in (root / "results/phase101_pdf_strategy_tests/PHASE101_REPORT.md").read_text(encoding="utf-8"),
        f"trades={u05_rows[0]['completed_trades'] if u05_rows else 'missing'}; net={u05_rows[0]['net_pnl_rupees'] if u05_rows else 'missing'}",
    )

    gate_rows = load_csv(root, "results/phase83_final_manuscript/supplementary_candidate_gate.csv")
    check(
        "Phase 83 registered candidate gate",
        len(gate_rows) == 18 and all(row["passes_defined_risk_net_gate"].strip().lower() == "false" for row in gate_rows),
        f"rows={len(gate_rows)}; passed={sum(row['passes_defined_risk_net_gate'].strip().lower() == 'true' for row in gate_rows)}",
    )
    factor_text = (root / "results/phase92/CROSS_PHASE_FACTOR_SYNTHESIS.md").read_text(encoding="utf-8")
    check(
        "Phase 92 predictor results not labelled strategy profitability",
        "No options strategy is promoted" in factor_text and "not pooled" in factor_text and "strategy P&L" in factor_text,
        "feature/forecast evidence kept separate from executable strategy outcome",
    )

    scorecard = load_csv(root, "results/phase102/strategy_evidence_scorecard.csv")
    check(
        "Machine-readable scorecard complete and no candidate promoted",
        len(scorecard) == 10 and all(row["promotion_decision"] in {
            "NOT_PROMOTED", "NOT_NEWLY_PROMOTED"
        } for row in scorecard),
        f"rows={len(scorecard)}; promoted_rows={sum(row['promotion_decision'] not in {'NOT_PROMOTED', 'NOT_NEWLY_PROMOTED'} for row in scorecard)}",
    )

    failed = [entry for entry in checks if not entry["passed"]]
    return {
        "phase": 102,
        "status": "PASS" if not failed else "FAIL",
        "decision": "NO_STRATEGY_PROMOTED",
        "source_artifacts_only": True,
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "failed_checks": failed,
        "checks": checks,
        "caveat": "This script verifies consistency of committed evidence. It does not backtest or certify profitability.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output", default="results/phase102/validation.json")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    result = build_validation(root)
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "decision": result["decision"],
        "checks_passed": result["checks_passed"],
        "checks_total": result["checks_total"],
        "failed_checks": result["failed_checks"],
        "output": str(output),
    }, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
