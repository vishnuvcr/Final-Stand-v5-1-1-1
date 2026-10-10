#!/usr/bin/env python3
"""Append a Dhan audit checkpoint to Phase 103 logs without exposing credentials."""
import json, os
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RESULT=ROOT/"results/phase103/dhan_data_api_audit.json"
RUN=os.getenv("GITHUB_RUN_ID","local")
ATTEMPT=os.getenv("GITHUB_RUN_ATTEMPT","1")

def append_once(path, marker, text):
    old=path.read_text(encoding="utf-8")
    if marker not in old:
        path.write_text(old.rstrip()+"\n\n"+text.rstrip()+"\n",encoding="utf-8")

def main():
    if not RESULT.exists():
        raise SystemExit("Dhan audit JSON missing; refusing to publish guessed status.")
    data=json.loads(RESULT.read_text(encoding="utf-8"))
    marker=f"DHAN_API_RUN_{RUN}_ATTEMPT_{ATTEMPT}"
    status=data.get("status","UNKNOWN")
    probes=data.get("probes",[])
    returned=sum(int(v.get("rows",0) or 0)>0 for v in probes)
    summary=(
      f"## Dhan Data API audit — run {RUN}, attempt {ATTEMPT} — {datetime.now(timezone.utc).isoformat()}\n\n"
      f"- **Result:** {status}.\n"
      f"- Window: {data.get('window',{}).get('from_inclusive')} inclusive to {data.get('window',{}).get('to_exclusive')} exclusive.\n"
      f"- Underlying IDs resolved: {sum(1 for m in data.get('underlying_map',{}).values() if m.get('security_id'))}/5.\n"
      f"- API probes returning rows: {returned}/{len(probes)}.\n"
      f"- Raw rows committed/uploaded: no. Token value printed/logged: no.\n"
      f"- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.\n"
    )
    append_once(ROOT/"PHASE103_RESEARCH_LOG.md",marker,f"<!-- {marker} -->\n"+summary)
    append_once(ROOT/"PHASE103_STATUS.md",marker,f"<!-- {marker} -->\n### Latest Dhan API data gate\n\n"+summary)
    if status!="PASS_API_DATA_RETURNED_FOR_ALL_10_PROBES":
        error=(f"### E103-DHAN-{RUN} — Dhan API access/data gate did not fully pass\n"
          f"**Type:** runtime/access/data-availability gate.\n"
          f"**Status:** {status}; rows returned by {returned}/{len(probes)} probes.\n"
          f"**Handling:** no raw rows or secret values were logged. Do not start strategy P&L testing until access, entitlement, mapping and coverage issues are resolved.\n"
          f"**Run:** https://github.com/{os.getenv('GITHUB_REPOSITORY','vishnuvcr/Final-Stand-v5-1-1-1')}/actions/runs/{RUN}\n")
        append_once(ROOT/"PHASE103_ERROR_LOG.md",marker,f"<!-- {marker} -->\n"+error)
    print(f"Published Dhan audit status {status} for run {RUN}; token not printed.")

if __name__=="__main__":
    main()
