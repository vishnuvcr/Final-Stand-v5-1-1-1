#!/usr/bin/env python3
"""Append a safe Phase 104 checkpoint; never publish raw market rows."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "results/phase104/nse_eod_data_audit.json"
STATUS = ROOT / "PHASE104_STATUS.md"
RESEARCH = ROOT / "PHASE104_RESEARCH_LOG.md"
ERROR = ROOT / "PHASE104_ERROR_LOG.md"
RUN = os.getenv("GITHUB_RUN_ID", "local")
ATTEMPT = os.getenv("GITHUB_RUN_ATTEMPT", "1")
REPO = os.getenv("GITHUB_REPOSITORY", "vishnuvcr/Final-Stand-v5-1-1-1")


def append_once(path, marker, text):
    current = path.read_text(encoding="utf-8")
    if marker not in current:
        path.write_text(current.rstrip() + "\n\n" + marker + "\n" + text.rstrip() + "\n", encoding="utf-8")


def main():
    marker = f"<!-- PHASE104_RUN_{RUN}_ATTEMPT_{ATTEMPT} -->"
    now = datetime.now(timezone.utc).isoformat()
    if RESULT.exists():
        try:
            data = json.loads(RESULT.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
    else:
        data = {}
    if str(data.get("run_id")) == RUN:
        a = data.get("aggregate", {})
        block = f"""### Phase 104.1 EOD audit — run {RUN}, attempt {ATTEMPT} — {now}

- Result: {data.get("status", "UNKNOWN")}
- Target window: {data.get("window", {}).get("from_inclusive")} inclusive to {data.get("window", {}).get("to_exclusive")} exclusive.
- Official daily archives parsed: {sum(1 for item in data.get("daily_archives", []) if item.get("status") == "ARCHIVE_PARSED")}.
- Source/schema errors: {len(data.get("archive_fetch_errors", []))}; no-archive dates: {len(data.get("no_archive_dates", []))}.
- Selected five-stock stock-option rows: {a.get("selected_rows", 0)}; parsed rows: {a.get("parsed_rows", 0)}.
- Identity completeness: {a.get("identity_completeness_pct", 0)}%; OHLC completeness: {a.get("price_completeness_pct", 0)}%.
- Unique daily contract keys: {a.get("unique_contract_keys", 0)}; duplicate keys: {a.get("duplicate_daily_contract_keys", 0)}.
- Raw rows persisted/uploaded: no. Raw price values and row-level contract records are not written to artifacts.
- Report: results/phase104/NSE_EOD_DATA_AUDIT.md; machine summary: results/phase104/nse_eod_data_audit.json.
"""
        append_once(STATUS, marker, block)
        append_once(RESEARCH, marker, block)
        current = STATUS.read_text(encoding="utf-8")
        state = "PHASE 104.1 EOD CONTRACT IDENTITY PASS; EXECUTION/COST GATES PENDING" if data.get("status") == "PASS_EOD_CONTRACT_IDENTITY" else "PHASE 104.1 EOD AUDIT COMPLETED; DATA/IDENTITY QUALITY GATE NOT PASSED"
        import re
        current = re.sub(r"\*\*State:\*\* [^\n]+", f"**State:** {state}", current, count=1)
        STATUS.write_text(current, encoding="utf-8")
        return
    block = f"""### E104-RUN-{RUN} — no fresh, run-matched EOD audit — {now}

Tests, network requests or audit generation did not produce an aggregate JSON whose run_id matches this Actions run. Prior output is not accepted as fresh evidence.
Run: https://github.com/{REPO}/actions/runs/{RUN}
"""
    append_once(ERROR, marker, block)
    append_once(STATUS, marker, f"### No fresh Phase 104 EOD result — run {RUN}\nNo current-run aggregate JSON was produced; prior results were not accepted.")
    append_once(RESEARCH, marker, f"## Phase 104 EOD audit no result — run {RUN}\nNo run-matched result was produced; no strategy inference is accepted.")


if __name__ == "__main__":
    main()
