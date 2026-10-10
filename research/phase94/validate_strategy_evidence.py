#!/usr/bin/env python3
"""Structural QA for the Phase 94 evidence register; does not run market tests."""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "results/phase94/strategy_evidence_register.csv"
REPORT_PATH = ROOT / "results/phase94/validation_report.json"
REQUIRED = [
    "candidate_id", "candidate_name", "source_phase", "source_path",
    "evidence_type", "period", "dev_val_oos_status", "completed_trades",
    "coverage_status", "gross_pnl", "net_pnl", "net_profit_per_trade",
    "return_denominator", "max_drawdown", "win_rate", "expectancy",
    "profit_factor", "cost_model", "execution_fidelity", "evidence_grade",
    "decision", "notes",
]

def main():
    errors = []
    rows = []
    if not CSV_PATH.exists():
        errors.append("missing strategy evidence register")
    else:
        with CSV_PATH.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            missing = sorted(set(REQUIRED) - set(reader.fieldnames or []))
            if missing:
                errors.append("missing columns: " + ", ".join(missing))
            rows = list(reader)
            ids = [r.get("candidate_id", "").strip() for r in rows]
            if not ids or any(not x for x in ids):
                errors.append("candidate_id must be nonempty for every row")
            if len(ids) != len(set(ids)):
                errors.append("candidate_id values must be unique")
            for i, row in enumerate(rows, start=2):
                for key in ("candidate_name", "source_phase", "source_path", "evidence_type", "evidence_grade", "decision", "notes"):
                    if not row.get(key, "").strip():
                        errors.append(f"row {i}: {key} must be nonempty")
                if row.get("evidence_grade") not in {"A", "B", "C", "D"}:
                    errors.append(f"row {i}: invalid evidence_grade")
                if row.get("evidence_type") in {"predictor_test", "predictor_association"}:
                    if row.get("net_pnl") not in {"NA", ""}:
                        errors.append(f"row {i}: predictor result must not claim strategy net_pnl")
                if row.get("completed_trades") == "0":
                    if row.get("net_profit_per_trade") not in {"NA", ""}:
                        errors.append(f"row {i}: zero-trade row must not report profit per trade")
                    if row.get("win_rate") not in {"NA", ""}:
                        errors.append(f"row {i}: zero-trade row must not report win rate")
    report = {
        "phase": 94,
        "status": "PASS" if not errors else "FAIL",
        "rows": len(rows),
        "required_columns": REQUIRED,
        "errors": errors,
        "market_or_model_tests_run": False,
        "phase83_2026_holdout_accessed": False,
        "strategy_promoted": False,
        "interpretation": "Structural register QA only; PASS does not certify profitability or completeness of historical strategy inventory."
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
