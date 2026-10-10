#!/usr/bin/env python3
"""Bounded Phase 75 audit: do not infer exact contract expiry from rolling codes."""
import json
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
SOURCE_GATE = ROOT / "results/phase51/PHASE51_1_SOURCE_GATE_REFERENCE.json"
STITCH = ROOT / "results/phase74_fixed_strike_stitch/summary.json"
OUT = ROOT / "results/phase75_contract_identity"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    source = read(SOURCE_GATE)
    stitch = read(STITCH)
    gate = source.get("source_gate_reference", {})
    target_dates = gate.get("unresolved_missing_expiries", [])
    expected = ["2026-07-28", "2026-08-04"]
    date_format_ok = all(date.fromisoformat(d).isoformat() == d for d in target_dates)
    groups = stitch.get("groups", [])
    stitch_ok = len(groups) == 16 and all(
        g.get("offset_probes_passed") == 21 and g.get("expected_session_timestamps") == 375
        and g.get("full_coverage_strike_count", 0) > 0 and g.get("field_mismatches", 1) == 0
        for g in groups
    )
    # The Dhan rolling endpoint response schema returns timestamp/OHLC/IV/volume/OI/spot/strike,
    # but not an explicit expiry-date series per observation. expiryCode is a relative selector.
    identity_fields_available = False
    decision = "BLOCKED_EXACT_EXPIRY_IDENTITY_NOT_EXPOSED" if target_dates == expected and date_format_ok and stitch_ok and not identity_fields_available else "AUDIT_REQUIRES_REVIEW"
    report = {
      "phase": 75,
      "decision": decision,
      "target_expiry_dates_from_frozen_source_gate": target_dates,
      "source_gate_dates_match_expected": target_dates == expected and date_format_ok,
      "phase74_group_count": len(groups),
      "phase74_stitch_feasibility_pass": stitch_ok,
      "rolling_endpoint_returns_explicit_expiry_date_per_bar": identity_fields_available,
      "required_contract_identity_fields": ["trade_date", "expiry_date", "absolute_strike", "option_side", "timestamp"],
      "identity_audit": "BLOCKED: Phase 74 proves fixed absolute-strike bar continuity for some strikes, but its inputs use relative expiryCode/expiryFlag selectors. The documented rolling response fields do not include an explicit expiry date for each bar. Exact expiry cannot be inferred from timestamps, strike coverage, or row counts.",
      "next_action": "Use an authorized fixed-contract historical dataset or official contract-wise archive that explicitly identifies expiry date, strike and option type. Until then, do not replay affected frozen legs or report P&L for the missing expiry dates.",
      "source_references": {
        "frozen_source_gate": "results/phase51/PHASE51_1_SOURCE_GATE_REFERENCE.json",
        "phase74_summary": "results/phase74_fixed_strike_stitch/summary.json",
        "dhan_expired_options_docs": "https://dhanhq.co/docs/v2/expired-options-data/",
        "nse_historical_contract_wise_archive": "https://www.nseindia.com/all-reports-derivatives"
      },
      "data_rights_and_execution_gate": "Still open: confirm retention rights before caching raw data; OHLC is not bid/ask/depth. Any future replay must model Paytm Money charges and conservative slippage/spread stress."
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["# Phase 75 — Exact expiry and contract identity audit", "", f"Decision: **{decision}**", "",
      f"Frozen missing-expiry targets: {', '.join(target_dates) if target_dates else 'not found'}.",
      f"Phase 74 stitch-feasibility checks: {'PASS' if stitch_ok else 'NOT PASSED'} ({len(groups)} groups).", "",
      "## Finding", "", report["identity_audit"], "", "## Resolution", "", report["next_action"], "",
      "## Sources", "", f"- DhanHQ rolling expired-options documentation: {report['source_references']['dhan_expired_options_docs']}",
      f"- NSE historical contract-wise archive: {report['source_references']['nse_historical_contract_wise_archive']}", "",
      report["data_rights_and_execution_gate"]]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(decision)

if __name__ == "__main__":
    main()
