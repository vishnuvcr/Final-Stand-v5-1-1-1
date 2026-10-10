#!/usr/bin/env python3
"""Validate Phase 103.0 stock universe registration without downloading market data."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import date


EXPECTED = ["HDFCBANK", "ICICIBANK", "RELIANCE", "SBIN", "INFY"]


def validate(repo_root: Path) -> dict:
    manifest_path = repo_root / "research/phase103_stock_options/stock_universe.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    stocks = data.get("stocks", [])
    checks = []

    checks.append(("exactly_five_stocks", len(stocks) == 5))
    symbols = [s.get("symbol") for s in stocks]
    checks.append(("unique_symbols", len(set(symbols)) == len(symbols)))
    checks.append(("expected_initial_universe", symbols == EXPECTED))
    checks.append(("weights_have_snapshot_date", all(s.get("weight_snapshot_date") == "2026-02-27" for s in stocks)))
    checks.append(("weights_are_numeric", all(isinstance(s.get("nifty50_weight_pct"), (int, float)) for s in stocks)))
    checks.append(("nonempty_company_and_sector", all(s.get("company") and s.get("sector") for s in stocks)))
    checks.append(("option_discovery_urls_present", all(str(s.get("option_discovery_url", "")).startswith("https://") for s in stocks)))
    checks.append(("prior_results_not_reused_as_evidence", data.get("freeze_policy", {}).get("nifty_index_options_results_reused_as_stock_options_evidence") is False))
    checks.append(("prior_artifacts_marked_unmodified", data.get("freeze_policy", {}).get("prior_phase_artifacts_mutated") is False))
    checks.append(("source_audit_gate_registered", "licence/retention/caching/derived-publication permissions" in data.get("phase_103_1_required_common_window_metrics", [])))
    failures = [name for name, ok in checks if not ok]
    return {
        "phase": "103.0",
        "status": "PASS" if not failures else "FAIL",
        "as_of_date": data.get("as_of_date"),
        "stock_count": len(stocks),
        "symbols": symbols,
        "checks_passed": len(checks) - len(failures),
        "checks_total": len(checks),
        "checks": [{"name": name, "passed": bool(ok)} for name, ok in checks],
        "failures": failures,
        "research_findings": "Universe registration only; no market data acquired and no strategies tested.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    result = validate(root)
    output = root / "results/phase103/registration_validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
