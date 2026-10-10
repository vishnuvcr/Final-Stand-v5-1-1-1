#!/usr/bin/env python3
"""Deterministic Phase 59 source metadata audit; no network or source-data download."""
from __future__ import annotations
import csv, json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REGISTRY=ROOT/"research/phase59/source_registry.json"
OUT=ROOT/"results/phase59/public_option_data_coverage"
REQUIRED_FIELDS={"date","timestamp_ist","underlying","expiry","strike","option_type","open_interest"}
QUOTE_FIELDS={"bid_price","ask_price","bid_quantity","ask_quantity"}


def load_registry(path:Path=REGISTRY)->dict:
    return json.loads(path.read_text(encoding="utf-8"))


def audit(registry:dict)->dict:
    if registry.get("phase")!=59:
        raise ValueError("registry phase mismatch")
    req=registry.get("target_requirements",{})
    if not req.get("entry_times_ist") or not req.get("prior_minute_times_ist") or not req.get("exit_time_ist"):
        raise ValueError("frozen target timestamp requirements missing")
    sources=registry.get("sources",[])
    if len(sources)<8:
        raise ValueError(f"expected at least 8 source candidates, found {len(sources)}")
    ids=[s.get("id") for s in sources]
    if any(not x for x in ids) or len(ids)!=len(set(ids)):
        raise ValueError("source IDs must be non-empty and unique")
    required={"id","name","url","evidence_url","source_type","published_claims","target_coverage",
              "has_intraday_oi","has_expiry_and_strike","has_bid_ask_depth",
              "license_clear_for_automation","exact_target_contract_coverage_verified","decision","evidence_limit"}
    rows=[]
    for s in sources:
        missing=required-set(s)
        if missing:
            raise ValueError(f"{s.get('id')}: missing fields {sorted(missing)}")
        meets_oi=(s["has_intraday_oi"] and s["has_expiry_and_strike"]
                  and s["license_clear_for_automation"] and s["exact_target_contract_coverage_verified"])
        meets_quotes=(s["has_bid_ask_depth"] and s["has_expiry_and_strike"]
                      and s["license_clear_for_automation"] and s["exact_target_contract_coverage_verified"])
        acceptable=bool(meets_oi and meets_quotes)
        if acceptable:
            raise ValueError(f"source unexpectedly meets all gates; requires separate human review: {s['id']}")
        rows.append({
            **s,
            "eligible_for_prior_minute_oi_replay":bool(meets_oi),
            "eligible_for_quote_depth_replay":bool(meets_quotes),
            "accepted_for_automated_replay":False,
        })
    decisions=Counter(s["decision"] for s in sources)
    return {
        "phase":59,
        "status":"SOURCE_TRIAGE_COMPLETE_NO_GO_FOR_FREE_AUTOMATED_OI_AND_QUOTES",
        "as_of":registry["as_of"],
        "audit_mode":registry["audit_mode"],
        "source_count":len(rows),
        "authorized_exact_intraday_oi_sources":sum(r["eligible_for_prior_minute_oi_replay"] for r in rows),
        "authorized_exact_quote_depth_sources":sum(r["eligible_for_quote_depth_replay"] for r in rows),
        "accepted_for_automated_replay":[],
        "licensed_followup_candidates":[r["id"] for r in rows if r["id"] in {"optionsdata_shop_minute_chain","optionvault","tickbytes"}],
        "source_decision_counts":dict(sorted(decisions.items())),
        "requirements":registry["target_requirements"],
        "data_downloaded":False,
        "raw_data_committed":False,
        "purchase_made":False,
        "credentials_used":False,
        "terms_violating_automation_used":False,
        "holdout_used":False,
        "strategy_promotion_allowed":False,
        "sources":rows,
        "conclusion":[
            "No candidate is verified to satisfy both exact-contract prior-minute OI coverage and permitted intraday bid/ask/depth at the frozen Phase 52 timestamps.",
            "The rissin dataset's published notes state that OI is NaN on Upstox intraday rows; daily bhavcopy OI is not a replacement for prior-minute OI.",
            "The artist-23 dataset's visible schema does not identify actual expiry and the page has no dataset card/license grant; it is not accepted without provenance and permission review.",
            "OptionsData.shop may be a licensed source for minute OHLC/OI, but its guide says it does not include bid/ask. No purchase was made.",
            "TickBytes and OptionVault remain licensed quote/depth follow-up candidates; exact target coverage and reuse/storage terms remain unverified.",
            "A public GitHub pipeline is code, not a guarantee of data rights or a complete, contract-matched archive.",
            "Stop this bounded audit here. Only reopen if explicit source access/license authorization and exact target-date/contract sample evidence become available."
        ]
    }


def write_report(report:dict,out_dir:Path=OUT)->None:
    out_dir.mkdir(parents=True,exist_ok=True)
    (out_dir/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    fields=["id","name","url","source_type","has_intraday_oi","has_expiry_and_strike","has_bid_ask_depth",
            "license_clear_for_automation","exact_target_contract_coverage_verified","eligible_for_prior_minute_oi_replay",
            "eligible_for_quote_depth_replay","accepted_for_automated_replay","decision","evidence_limit"]
    with (out_dir/"source_decisions.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        w.writeheader();w.writerows(report["sources"])
    lines=[
        "# Phase 59 — Public option-data coverage audit","",
        "**NO-GO for free, license-clear automated exact-contract prior-minute OI plus quote/depth. Metadata-only; no source data downloaded.**","",
        f"- Sources reviewed: {report['source_count']}",
        f"- Free/license-clear exact intraday OI sources accepted: {report['authorized_exact_intraday_oi_sources']}",
        f"- Free/license-clear exact quote/depth sources accepted: {report['authorized_exact_quote_depth_sources']}",
        "- Purchases: none; credentials used: no; raw market data committed: no.","",
        "| Candidate | OI at exact prior minute | Exact expiry/strike identity | Bid/ask/depth | Automation/license cleared | Decision |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for s in report["sources"]:
        lines.append("| {name} | {oi} | {idok} | {quotes} | {license} | {decision} |".format(
            name=s["name"],oi="Yes" if s["has_intraday_oi"] else "No/unknown",
            idok="Yes" if s["has_expiry_and_strike"] else "No/unknown",
            quotes="Yes (claim)" if s["has_bid_ask_depth"] else "No",
            license="Yes" if s["license_clear_for_automation"] else "No/unverified",
            decision=s["decision"]))
    lines.extend(["","## Conclusion",*[f"- {x}" for x in report["conclusion"]],""])
    (out_dir/"report.md").write_text("\n".join(lines),encoding="utf-8")


def main()->int:
    report=audit(load_registry())
    write_report(report)
    print(json.dumps({k:v for k,v in report.items() if k not in {"sources","requirements","conclusion"}},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
