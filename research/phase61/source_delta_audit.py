#!/usr/bin/env python3
"""Deterministic metadata-only Phase 61 source restart audit."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "research/phase61/source_registry.json"
OUT = ROOT / "results/phase61/source_restart_audit"


def evaluate(registry):
    candidates = registry["candidates"]
    if len(candidates) != 5:
        raise ValueError(f"Expected exactly five new source leads, found {len(candidates)}")
    ids = [x["id"] for x in candidates]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate source IDs")
    accepted = [x for x in candidates if x["decision"] == "ACCEPT_FOR_SAMPLE_VALIDATION"]
    for x in accepted:
        required = ("rights_cleared", "sample_validated", "exact_contract_schema_verified")
        if not all(x.get(key) is True for key in required):
            raise AssertionError(f"Unsafe acceptance without rights and exact sample/schema validation: {x['id']}")
    status_counts = {}
    for x in candidates:
        status_counts[x["decision"]] = status_counts.get(x["decision"], 0) + 1
    no_go = not accepted
    return {
        "phase": 61,
        "status": "NO_GO_NO_NEW_SOURCE_MEETS_RESTART_GATE" if no_go else "SOURCE_CANDIDATE_ACCEPTED_FOR_SAMPLE_VALIDATION",
        "as_of": registry["as_of"],
        "audit_mode": registry["mode"],
        "candidate_count": len(candidates),
        "decision_counts": status_counts,
        "accepted_source_ids": [x["id"] for x in accepted],
        "candidates": candidates,
        "frozen_rules": {
            "prior_oi_minimum": registry["frozen_target"]["prior_oi_minimum"],
            "baseline_ohlc_range_pct": registry["frozen_target"]["baseline_ohlc_range_pct"],
            "holdout_used": False,
            "data_downloaded": False,
            "credentials_used": False,
            "purchases": False,
            "strategy_promoted": False,
            "pnl_recalculated": False,
        },
        "decision": (
            "Stop empirical factor/strategy testing. None of the newly surfaced leads has verified data-use rights plus exact target sample/schema evidence."
            if no_go else
            "Only the listed source may proceed to a separately preregistered small-sample validation; no bulk download or strategy run is authorized."
        ),
        "restart_next_step": (
            "Obtain written rights/access and a provider-approved exact sample first. Do not create another source-search phase unless a genuinely new lead or authorization arrives."
            if no_go else
            "Run the bounded exact-contract/timestamp sample validation defined in the Phase 60 restart checklist."
        ),
    }


def write_report(report):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Phase 61 — New-source restart audit",
        "",
        f"**Decision: {report['status']}**",
        "",
        f"- Candidates reviewed: {report['candidate_count']}",
        f"- Decision counts: `{json.dumps(report['decision_counts'], sort_keys=True)}`",
        f"- Accepted for sample validation: {', '.join(report['accepted_source_ids']) if report['accepted_source_ids'] else 'None'}",
        "- Mode: public metadata only; no credentials, purchases, downloads or scraping.",
        "",
        "| Candidate | Decision | Key blocker |",
        "|---|---|---|",
    ]
    for c in report["candidates"]:
        lines.append(f"| [{c['name']}]({c['url']}) | {c['decision']} | {c['reason']} |")
    lines += [
        "",
        "## Conclusion",
        "",
        report["decision"],
        "",
        "## Restart action",
        "",
        report["restart_next_step"],
        "",
        "No P&L, fill quality, statistical inference, strategy ranking or promotion was performed.",
        "",
    ]
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    report = evaluate(registry)
    write_report(report)
    print(json.dumps({k: report[k] for k in ("status", "candidate_count", "decision_counts", "accepted_source_ids", "decision")}, indent=2))
