#!/usr/bin/env python3
"""Update Phase 105 durable status/logs after each GitHub Actions attempt."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results" / "phase105" / "summary.json"
RUN_ID = os.getenv("GITHUB_RUN_ID", "local")
RUN_URL = f"https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/{RUN_ID}"
TEST_OUTCOME = os.getenv("PHASE105_TEST_OUTCOME", "unknown")
PILOT_OUTCOME = os.getenv("PHASE105_PILOT_OUTCOME", "unknown")
STAMP = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

def load_result():
    try:
        return json.loads(RESULT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

def append_once(path, marker, body):
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + marker + "\n" + body.rstrip() + "\n", encoding="utf-8")

def main():
    result = load_result()
    decision = (result or {}).get("decision", {})
    source = (result or {}).get("source_aggregate", {})
    checks = (result or {}).get("accounting_checks", {})
    accounting = checks.get("status", "NOT_RUN")
    source_gate = decision.get("source_gate", "NOT_VERIFIED")
    replay = decision.get("strategy_replay", "NOT_RUN")
    if TEST_OUTCOME == "success" and PILOT_OUTCOME == "success" and accounting == "PASS" and replay == "COMPLETE_ACCOUNTING_CHECKS_PASS":
        state = "COMPLETE — EXPLORATORY OHLC PROXY PILOT; NO STRATEGY PROMOTED"
    elif source_gate == "FAIL":
        state = "BLOCKED — SOURCE DATA GATE FAILED; NO STRATEGY CONCLUSION"
    else:
        state = "INCOMPLETE / FAILED AUTOMATED GATE — SEE ERROR LOG"
    status = f"""# Phase 105 Status — EOD OHLC Strategy Pilot

**Updated:** {STAMP}  
**Branch:** \`phase-105-eod-ohlc-strategy-pilot\`  
**Latest workflow:** [{RUN_ID}]({RUN_URL})  
**State:** {state}  
**Unit tests:** {TEST_OUTCOME}  
**Strategy runner:** {PILOT_OUTCOME}  
**Source gate:** {source_gate}  
**Accounting gate:** {accounting}  
**Promotion:** NONE

## Frozen scope

- Universe: HDFCBANK, ICICIBANK, INFY, RELIANCE and SBIN.
- Sample: 2026-08-03 inclusive to 2026-09-02 exclusive.
- Three fixed candidates: MOMENTUM_ATM, REVERSAL_ATM and MOMENTUM_OI_CONFIRM.
- Prior-session selection, next-session-open to same-session-close EOD OHLC execution proxy only.
- Paytm Money brokerage sensitivity ₹10/₹15/₹20 per order; date-effective modelled charges; adverse slippage ₹0/₹0.05/₹0.25/₹0.50 per option unit per side; fee multiplier 1.0×/1.5×.
- Raw source rows, raw option prices and per-trade files remain unpublished.

## Latest verified counts

- Selected rows: {source.get("selected_rows", "not available")}
- Parsed rows: {source.get("parsed_rows", "not available")}
- Identity completeness: {source.get("identity_completeness_pct", "not available")}%
- OHLC completeness: {source.get("ohlc_completeness_pct", "not available")}%
- Duplicate keys / date mismatches: {source.get("duplicate_daily_contract_keys", "not available")} / {source.get("date_mismatch_rows", "not available")}
- Common sessions with all five underlying values: {source.get("sessions_with_all_five_underlyings", "not available")}
- Aggregate strategy scenario rows: {checks.get("scenario_rows", 0)}

## Bounded phase state

- [x] 105.0 Registration and scope freeze.
- [{'x' if source_gate == 'PASS' else ' '}] 105.1 Source/schema/identity/OHLC data gate.
- [{'x' if TEST_OUTCOME == 'success' else ' '}] 105.2 Unit tests and chronology/leakage checks.
- [{'x' if replay == 'COMPLETE_ACCOUNTING_CHECKS_PASS' and accounting == 'PASS' else ' '}] 105.3 Frozen strategy replay and registered cost stress.
- [{'x' if TEST_OUTCOME == 'success' and PILOT_OUTCOME == 'success' and accounting == 'PASS' else ' '}] 105.4 Accounting review and closeout artifacts.

## Interpretation boundary

The sample is a short, previously inspected one-month pilot. EOD open/close marks and assumed slippage do not prove actual fills or executable profitability. No strategy is promoted irrespective of simulated returns.
"""
    (ROOT / "PHASE105_STATUS.md").write_text(status, encoding="utf-8")

    research = ROOT / "PHASE105_RESEARCH_LOG.md"
    append_once(research, f"<!-- PHASE105_RUN_{RUN_ID} -->", f"""### Workflow run {RUN_ID} — {STAMP}

- Workflow: {RUN_URL}
- Unit tests: {TEST_OUTCOME}; runner: {PILOT_OUTCOME}.
- Source gate: {source_gate}; strategy replay: {replay}; accounting gate: {accounting}.
- Rows selected/parsed: {source.get('selected_rows', 'not available')} / {source.get('parsed_rows', 'not available')}.
- Identity/OHLC completeness: {source.get('identity_completeness_pct', 'not available')}% / {source.get('ohlc_completeness_pct', 'not available')}%.
- Raw rows and per-trade price records published: no.
- Promotion: NONE. Full aggregate evidence is in \`results/phase105/\`.
""")
    if TEST_OUTCOME != "success" or PILOT_OUTCOME != "success" or source_gate != "PASS" or accounting != "PASS":
        err = ROOT / "PHASE105_ERROR_LOG.md"
        append_once(err, f"<!-- PHASE105_ERROR_RUN_{RUN_ID} -->", f"""### Run {RUN_ID} — gate failure or blocker ({STAMP})

- Workflow: {RUN_URL}
- Unit tests: {TEST_OUTCOME}; runner: {PILOT_OUTCOME}; source gate: {source_gate}; accounting gate: {accounting}.
- Recorded state: {state}.
- The run is not accepted as a profitability result. Inspect the workflow logs and \`results/phase105/summary.json\`; fix the root cause or preserve the blocker rather than inventing fills.
""")
    chat = ROOT / "PHASE105_CHAT_LOG.md"
    append_once(chat, f"<!-- PHASE105_VISIBLE_RUN_{RUN_ID} -->", f"""### Automated continuation result — {STAMP}

- The visible user instruction was “Continue”; the bounded Phase 105 plan was followed on its isolated branch.
- Workflow: {RUN_URL}.
- Current state: {state}; promotion: NONE.
- Results are OHLC execution proxies, not verified real-world fills.
""")

if __name__ == "__main__":
    main()
