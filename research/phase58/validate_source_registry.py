#!/usr/bin/env python3
"""Validate the evidence-based source registry without scraping source websites."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REGISTRY=ROOT/"research"/"phase58"/"sources.json"
OUT=ROOT/"results"/"phase58"/"quote_source_feasibility"
REQUIRED={"timestamp","expiry","strike","option_type","bid_price","ask_price","bid_quantity","ask_quantity"}


def build_report(registry: dict) -> dict:
    sources=registry.get("sources",[])
    if len(sources)<5:
        raise ValueError(f"expected at least five source candidates, got {len(sources)}")
    ids=[s.get("id") for s in sources]
    if len(ids)!=len(set(ids)) or any(not x for x in ids):
        raise ValueError("source IDs must be unique and non-empty")
    for s in sources:
        for field in ("name","url","evidence_url","data_fields","granularity","history_coverage","access","automation_eligible","historical_bid_ask_depth_verified","exact_timestamps_verified","decision","limitations"):
            if field not in s:
                raise ValueError(f"{s.get('id')}: missing required field {field}")
    eligible=[s["id"] for s in sources if s["automation_eligible"] and s["historical_bid_ask_depth_verified"] and s["exact_timestamps_verified"]]
    counts=dict(sorted(Counter(s["decision"] for s in sources).items()))
    return {
        "phase":58,
        "status":"SOURCE_FEASIBILITY_PASS_NO_GO_FOR_FREE_AUTOMATED_QUOTES" if not eligible else "SOURCE_CANDIDATE_REQUIRES_VALIDATION",
        "decision":registry["decision"],
        "required_timestamps_ist":registry["required_timestamps_ist"],
        "required_fields":registry["required_fields"],
        "source_count":len(sources),
        "sources_with_verified_full_history_bid_ask_depth":sum(bool(s["historical_bid_ask_depth_verified"]) for s in sources),
        "sources_with_verified_exact_timestamps":sum(bool(s["exact_timestamps_verified"]) for s in sources),
        "sources_eligible_for_automated_replay":eligible,
        "source_decision_counts":counts,
        "licensed_followup_candidates":[s["id"] for s in sources if s["id"] in {"tickbytes","optionvault"}],
        "manual_only_candidates":[s["id"] for s in sources if not s["automation_eligible"] and "MANUAL" in s["decision"]],
        "purchase_made":bool(registry.get("purchase_made",False)),
        "scraping_against_terms":bool(registry.get("scraping_against_terms",False)),
        "holdout_used":False,
        "pnl_recalculated":False,
        "strategy_promotion_allowed":False,
        "limitations":[
            "This report validates a documented evidence registry; it does not crawl sites or independently verify vendor claims.",
            "Public sample files do not prove full historical coverage for the Phase52 target dates/contracts.",
            "OHLC/LTP and end-of-day bid/ask do not replace exact intraday bid/ask/depth at the frozen timestamps.",
            "No purchase or license acceptance was made; licensed sources require explicit user authorization.",
            "StockMojo's published terms prohibit automated extraction; it is not used in GitHub Actions."
        ]
    }


def main() -> int:
    registry=json.loads(REGISTRY.read_text(encoding="utf-8"))
    report=build_report(registry)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    lines=[
        "# Phase 58 — quote/depth source feasibility",
        "",
        f"**Decision: {report['decision']}**",
        "",
        f"- Source candidates audited: {report['source_count']}",
        f"- Full historical bid/ask/depth sources verified for target dates: {report['sources_with_verified_full_history_bid_ask_depth']}",
        f"- Sources with exact 09:45/13:00/15:15 timestamps verified: {report['sources_with_verified_exact_timestamps']}",
        f"- Sources eligible for automated replay: {report['sources_eligible_for_automated_replay']}",
        f"- Purchases made: {report['purchase_made']}",
        "",
        "## Source decisions",
        "",
        "| Source | Decision | Automation | Full quote/depth history verified | Exact timestamps verified |",
        "|---|---|---:|---:|---:|"
    ]
    for s in registry["sources"]:
        lines.append(f"| [{s['name']}]({s['url']}) | {s['decision']} | {s['automation_eligible']} | {s['historical_bid_ask_depth_verified']} | {s['exact_timestamps_verified']} |")
    lines += [
        "",
        "## Conclusion",
        "",
        "No free, legally cleared, automated source has been verified for full historical bid/ask/depth at the frozen entry and exit timestamps. StockMojo is manual-only under its published terms; NiftyTrader's documented intraday snapshot times do not match the frozen times; TickBytes and OptionVault have promising quote/depth sample schemas but full historical target-date coverage requires licensed access. NSE live data and daily archives do not establish a free exact historical quote series.",
        "",
        "No purchase was made, no site was scraped against terms, and no P&L or strategy selection was performed. The next gate is explicit user authorization for a licensed sample and reuse/storage terms, or a newly verified free source.",
        ""
    ]
    (OUT/"report.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(report,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
