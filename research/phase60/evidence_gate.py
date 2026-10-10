#!/usr/bin/env python3
"""Deterministic Phase 60 evidence sufficiency gate; no downloads or P&L."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "research/phase59/source_registry.json"
REPORT = ROOT / "results/phase59/public_option_data_coverage/report.json"
OUT = ROOT / "results/phase60/evidence_sufficiency"


def evaluate() -> dict:
    if not REGISTRY.exists() or not REPORT.exists():
        raise FileNotFoundError("Required Phase59 source registry/report missing; fail closed")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    source_report = json.loads(REPORT.read_text(encoding="utf-8"))
    sources = registry.get("sources", [])
    if len(sources) != 10 or len({s.get("id") for s in sources}) != 10:
        raise AssertionError("Phase59 registry must contain 10 unique sources")
    if source_report.get("source_count") != 10:
        raise AssertionError("Unexpected Phase59 source count")
    if source_report.get("source_count") != 10:
        raise AssertionError("Phase59 report source count mismatch")
    oi = source_report.get("authorized_exact_intraday_oi_sources")
    quotes = source_report.get("authorized_exact_quote_depth_sources")
    if oi != 0 or quotes != 0:
        raise AssertionError(f"Phase59 acceptance counts changed: OI={oi}, quote/depth={quotes}")
    decisions = {
        "phase52_baseline": {
            "run": "37992542028",
            "planned_rows": 480,
            "status_counts": {"EXCLUDED_OHLC_RANGE_PROXY":379,"BLOCKED_LEG_ELIGIBILITY":100,"REPLAY_PASS":1},
            "executed_rows": 1,
            "interpretation": "One baseline row is insufficient for strategy ranking or statistical inference."
        },
        "phase54_coverage_sensitivity": {
            "run": "38018639487",
            "threshold_pct": [2,3,4,5,6,8,10,12,15,20,1000],
            "eligible_rows": [1,1,8,24,55,91,150,227,298,345,380],
            "interpretation": "Eligibility coverage only; OHLC range is not bid/ask spread."
        },
        "phase56_cost_reference": {
            "run": "38019323348",
            "modeled_scenario_rows": 18960,
            "severe_cost_screen_pairs_only_at_1000pct": 5,
            "interpretation": "Diagnostic OHLC model sensitivity; not executable fills or strategy winners."
        },
        "phase57_independent_reproduction": {
            "run": "38021314847",
            "common_scenarios": 2286,
            "mismatches": 0,
            "interpretation": "Reproduces the same OHLC reference model; does not validate market executability."
        },
        "phase59_source_feasibility": {
            "run": "38020729139",
            "candidates": 10,
            "accepted_exact_prior_minute_oi_sources": oi,
            "accepted_exact_quote_depth_sources": quotes,
            "interpretation": "No accepted free/license-clear source meets the frozen exact-timestamp requirements."
        }
    }
    gate = {
        "phase": 60,
        "status": "NO_GO_EMPIRICAL_FACTOR_STRATEGY_TESTING_DATA_EVIDENCE_INSUFFICIENT",
        "created_at_utc": "2026-10-10",
        "source_audit": {
            "registry_source_count": len(sources),
            "phase59_report_source_count": source_report.get("source_count"),
            "authorized_exact_prior_minute_oi_sources": oi,
            "authorized_exact_quote_depth_sources": quotes,
            "purchases": False,
            "data_downloaded": False,
            "credentials_used": False
        },
        "cross_phase_evidence": decisions,
        "frozen_rules": {
            "phase52_rows": 480,
            "prior_minute_oi_minimum": 100,
            "baseline_ohlc_range_pct": 2,
            "holdout_used": False,
            "grid_changed": False,
            "costs_changed": False,
            "strategy_promoted": False
        },
        "decision": "STOP new factor-conditioned profitability runs until the restart checklist is met.",
        "restart_requirements": [
            "Document explicit license, automated access, caching/storage and derived-result publication rights, or find a new source with clear rights.",
            "Verify a small exact target-date/contract sample at 09:44, 09:45, 12:59, 13:00 and 15:15 IST, with actual expiry, strike and CE/PE identity.",
            "Do not coerce missing OI to zero; preserve source values and distinguish missing, true zero, duplicate and conflicting rows.",
            "For execution-quality claims, verify historical bid price, ask price, bid quantity and ask quantity at required entry/exit times; OHLC/LTP is not a substitute.",
            "Demonstrate enough eligible development/validation events before inferential comparison; holdout stays untouched.",
            "Recalculate Paytm Money brokerage, statutory charges, adverse slippage and stress cases only after valid coverage is proven."
        ],
        "conclusion": "The current data supports reproducibility and eligibility-coverage diagnostics, not a defensible profitability conclusion for factor-conditioned option strategy selection. No candidate is promoted."
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "report.json").write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Phase 60 — Evidence sufficiency decision",
        "",
        "**NO-GO: insufficient source-verified data for further factor-conditioned profitability testing.**",
        "",
        f"- Phase 52: 1/480 rows executed under the frozen 2% OHLC range proxy.",
        f"- Phase 54: eligibility rose from 1/480 at 2% to 380/480 at the 1000% diagnostic threshold; this is coverage only.",
        f"- Phase 56: {decisions['phase56_cost_reference']['modeled_scenario_rows']:,} modeled scenarios; five configuration-threshold pairs passed the severe-cost screen only at 1000%.",
        f"- Phase 57: {decisions['phase57_independent_reproduction']['common_scenarios']:,} common scenarios reproduced with zero mismatches.",
        f"- Phase 59: {len(sources)} candidates; zero accepted free/license-clear exact prior-minute OI sources and zero accepted exact quote/depth sources.",
        "",
        "## What this does and does not establish",
        "",
        "- The OHLC reference model is reproducible under the pinned inputs and modeled cost scenarios.",
        "- A reproducible OHLC model is not proof of bid/ask executable fills or live profitability.",
        "- Relaxing the 2% candle-range gate mechanically increases eligible rows; the 1000% diagnostic endpoint is not a trading recommendation.",
        "- The baseline has only one passing row, so no meaningful factor-selector efficacy or strategy ranking is supported.",
        "- No holdout was used; no strategy or factor selector was promoted.",
        "",
        "## Restart condition",
        "",
        *[f"{i}. {item}" for i, item in enumerate(gate["restart_requirements"], 1)],
        "",
        "## Final decision",
        "",
        gate["conclusion"],
        ""
    ]
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status":gate["status"],"source_count":len(sources),"oi_sources":oi,"quote_depth_sources":quotes,"output":str(OUT)},indent=2))


if __name__ == "__main__":
    evaluate()
