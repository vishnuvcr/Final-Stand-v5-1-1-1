#!/usr/bin/env python3
"""Persist each bounded historical pilot workflow outcome to Phase52 logs/readmes."""
from __future__ import annotations
import json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BRANCH = os.environ.get("PHASE_BRANCH", "phase-52-factor-conditioned-strategy-discovery")
RUN_ID = os.environ.get("GITHUB_RUN_ID", "unknown")
JOB_STATUS = os.environ.get("JOB_STATUS", "unknown")
SELF_TEST = os.environ.get("SELF_TEST_OUTCOME", "unknown")
PLAN_STAGE = os.environ.get("PLAN_OUTCOME", "unknown")
REPLAY_STAGE = os.environ.get("REPLAY_OUTCOME", "unknown")
REPORT = ROOT / "results" / "phase52" / "historical_pilot" / "report.json"
MANIFEST = ROOT / "results" / "phase52" / "historical_pilot" / "pilot_manifest.json"
LOG_PATHS = ["PHASE52_STATUS.md", "PHASE52_ERROR_LOG.md", "PHASE52_RESEARCH_LOG.md", "PHASE52_CHAT_LOG.md", "README.md"]

def append(path: Path, block: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if f"run {RUN_ID}" in old or f"run_id: {RUN_ID}" in old:
        return
    path.write_text(old.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8")

def git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout.strip()

def persist_repo(cwd: Path, branch: str, paths: list[str], message: str) -> str:
    available: list[str] = []
    for item in paths:
        path = cwd / item
        if path.is_file():
            available.append(item)
        elif path.is_dir():
            available.extend(str(child.relative_to(cwd)) for child in path.rglob("*") if child.is_file())
    if not available:
        return "NO_FILES_TO_PERSIST"
    git(["config", "user.name", "github-actions[bot]"], cwd)
    git(["config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], cwd)
    git(["add", *sorted(set(available))], cwd)
    staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=cwd).returncode == 1
    if not staged:
        return "NO_CHANGES"
    git(["commit", "-m", message], cwd)
    git(["fetch", "origin", branch], cwd)
    subprocess.run(["git", "rebase", f"origin/{branch}"], cwd=cwd, check=True)
    git(["push", "origin", branch], cwd)
    return git(["rev-parse", "HEAD"], cwd)

def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    report: dict[str, Any] | None = None
    manifest: dict[str, Any] | None = None
    if REPORT.exists():
        try: report = json.loads(REPORT.read_text(encoding="utf-8"))
        except Exception: report = None
    if MANIFEST.exists():
        try: manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        except Exception: manifest = None
    accepted = bool(
        JOB_STATUS == "success" and report
        and report.get("historical_pnl_calculated")
        and int(report.get("replay_exception_count", 0)) == 0
        and int(report.get("source_file_errors", 0)) == 0
        and int(report.get("executed_event_rows", 0)) > 0
        and int(report.get("cost_scenario_rows", 0)) > 0
    )
    outcome = "PASS" if accepted else "FAILED_OR_INCOMPLETE"
    summary = (
        f"- **Run:** [{RUN_ID}](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/{RUN_ID}); job={JOB_STATUS}; "
        f"self-test={SELF_TEST}; plan-only={PLAN_STAGE}; replay={REPLAY_STAGE}.\n"
    )
    if report:
        summary += (
            f"- **Pilot result status:** {report.get('status')}; configs={report.get('configurations')}; "
            f"planned config-event rows={report.get('planned_config_event_rows')}; executed={report.get('executed_event_rows')}; "
            f"excluded/errors={report.get('excluded_or_error_event_rows')}; cost rows={report.get('cost_scenario_rows')}; "
            f"source file errors={report.get('source_file_errors')}.\n"
        )
    elif manifest:
        summary += (
            f"- **Frozen pilot preflight only:** configs={manifest.get('configuration_count')}; events={manifest.get('expected_event_rows')}; "
            f"planned config-event rows={manifest.get('planned_config_event_rows')}; historical replay report missing.\n"
        )
    else:
        summary += "- Pilot manifest/report is missing or unreadable; this run is not accepted as a historical result.\n"
    summary += "- **Interpretation:** bounded BASELINE engineering pilot only; no winner ranking/promotion. Holdout remains untouched. Queue enumeration is not a backtest count.\n"

    status_path = ROOT / "PHASE52_STATUS.md"
    status = status_path.read_text(encoding="utf-8")
    if f"run {RUN_ID}" not in status:
        line = next((x for x in status.splitlines() if x.startswith("**Overall:**")), "**Overall:** OPEN")
        if accepted:
            new_line = "**Overall:** OPEN — bounded historical BASELINE pilot completed; descriptive only, no promotion; factor routers/full grid remain gated"
        else:
            new_line = "**Overall:** OPEN — bounded historical pilot did not complete cleanly; see run-specific failure log; no result accepted"
        status = status.replace(line, new_line, 1)
        status_path.write_text(status.rstrip() + "\n\n## Bounded historical pilot checkpoint\n\n" + summary, encoding="utf-8")

    research_block = f"## {now} — Bounded historical pilot run {RUN_ID}\n\n" + summary + (
        "- Frozen plan: research/phase52/first_historical_pilot.json; runner: research/phase52/historical_pilot_runner.py.\n"
        "- No hidden reasoning or secret values are recorded. Workflow logs/artifacts preserve operational errors.\n"
    )
    append(ROOT / "PHASE52_RESEARCH_LOG.md", research_block)
    append(ROOT / "PHASE52_CHAT_LOG.md", f"## User continuation / automated action — run {RUN_ID}\n\n" + summary)
    append(ROOT / "README.md", f"## Phase 52 bounded historical pilot — run {RUN_ID}\n\n" + summary + (
        "- Event-level exclusions and six cost cases are in results/phase52/historical_pilot/.\n"
        "- Primary market data are CC BY-NC 4.0 and the pilot is not commercial/live evidence.\n"
    ))
    if not accepted:
        error_block = (
            f"## F52-HIST-{RUN_ID} — Bounded historical pilot failed or did not produce an accepted report\n\n"
            f"- **Date:** {now}\n- **Workflow:** https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/{RUN_ID}\n"
            f"- **Stage outcomes:** self-test={SELF_TEST}; plan-only={PLAN_STAGE}; replay={REPLAY_STAGE}; job={JOB_STATUS}.\n"
            f"- **Observation:** Historical pilot report missing or workflow non-success. Do not infer P&L from partial artifacts.\n"
            f"- **Impact:** No result from this run is accepted unless report.json exists, input/source hashes match the frozen manifest and the overall job succeeds.\n"
            f"- **Next:** inspect the failing step log, fix the root cause, rerun with a new run ID, and preserve this entry.\n"
            f"- **Status:** OPEN / FAILED RUN PRESERVED.\n"
        )
        append(ROOT / "PHASE52_ERROR_LOG.md", error_block)

    branch_commit = persist_repo(ROOT, BRANCH, LOG_PATHS + [
        "research/phase52/first_historical_pilot.json", "research/phase52/historical_pilot_runner.py",
        "research/phase52/persist_historical_pilot.py", "results/phase52/historical_pilot"
    ], f"Phase52 historical pilot checkpoint run {RUN_ID}")

    main_repo = ROOT / "main-docs"
    main_commit = "MAIN_CHECKOUT_MISSING"
    main_readme = main_repo / "README.md"
    if main_readme.exists():
        append(main_readme, f"## Phase 52 bounded historical pilot — run {RUN_ID}\n\n" + summary + (
            f"- Branch-local run details: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/{BRANCH}/results/phase52/historical_pilot\n"
            "- This is a bounded baseline engineering run, not a factor-router efficacy result.\n"
        ))
        main_commit = persist_repo(main_repo, "main", ["README.md"], f"Update Phase52 README for pilot run {RUN_ID}")

    print(json.dumps({
        "status": outcome, "run_id": RUN_ID, "job_status": JOB_STATUS,
        "branch_commit": branch_commit, "main_readme_commit": main_commit,
        "report_present": bool(report), "manifest_present": bool(manifest),
        "executed_event_rows": report.get("executed_event_rows") if report else None,
        "no_promotion": True
    }, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
