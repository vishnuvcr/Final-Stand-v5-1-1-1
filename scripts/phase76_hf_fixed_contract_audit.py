#!/usr/bin/env python3
"""Bounded, aggregate-only audit of two fixed-expiry files from a public HF dataset."""
import json, os
from pathlib import Path
from datetime import time
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

REPO = "thetrademarkk/india-index-options-1m"
TARGETS = ["2026-07-28", "2026-08-04"]
OUT = Path("results/phase76_hf_fixed_contracts")
REQUIRED = {"timestamp", "strike", "option_type", "expiry", "open", "high", "low", "close"}

def main():
    token = os.environ.get("HF_TOKEN", "").strip() or None
    api = HfApi(token=token)
    files = api.list_repo_files(repo_id=REPO, repo_type="dataset")
    entries = []
    errors = []
    for expiry in TARGETS:
        expected = f"options/NIFTY/{expiry}.parquet"
        candidates = [p for p in files if p == expected or (p.startswith("options/NIFTY/") and Path(p).stem == expiry)]
        if not candidates:
            entries.append({"target_expiry": expiry, "file_found": False, "decision": "BLOCKED_TARGET_FILE_ABSENT"})
            continue
        # Do not fetch a whole dataset or neighboring expiry files.
        path = candidates[0]
        try:
            local = hf_hub_download(repo_id=REPO, repo_type="dataset", filename=path, token=token)
            frame = pd.read_parquet(local)
            cols = set(map(str, frame.columns))
            missing = sorted(REQUIRED - cols)
            if missing:
                entries.append({"target_expiry": expiry, "file_found": True, "file_path": path,
                                "row_count": int(len(frame)), "columns": sorted(cols), "missing_required_columns": missing,
                                "decision": "BLOCKED_SCHEMA_MISMATCH"})
                continue
            frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True).dt.tz_convert("Asia/Kolkata")
            frame["expiry_norm"] = pd.to_datetime(frame["expiry"], errors="coerce").dt.strftime("%Y-%m-%d")
            frame["option_type_norm"] = frame["option_type"].astype(str).str.upper().str.strip()
            frame["strike_num"] = pd.to_numeric(frame["strike"], errors="coerce")
            frame = frame[frame["timestamp"].notna()]
            target = frame[frame["timestamp"].dt.strftime("%Y-%m-%d") == expiry]
            session = target[(target["timestamp"].dt.time >= time(9,15)) & (target["timestamp"].dt.time <= time(15,29,59))]
            contracts = []
            for (exp, strike, side), g in session.groupby(["expiry_norm", "strike_num", "option_type_norm"], dropna=True):
                ts = g["timestamp"].drop_duplicates().sort_values()
                contracts.append({"expiry": str(exp), "strike": float(strike), "option_type": str(side),
                                  "row_count": int(len(g)), "unique_timestamps": int(ts.nunique()),
                                  "first_timestamp_ist": ts.iloc[0].isoformat() if len(ts) else None,
                                  "last_timestamp_ist": ts.iloc[-1].isoformat() if len(ts) else None,
                                  "full_375_bar_session": int(ts.nunique()) == 375})
            entries.append({"target_expiry": expiry, "file_found": True, "file_path": path,
                "row_count_file": int(len(frame)), "columns": sorted(cols),
                "explicit_expiry_values": sorted(x for x in frame["expiry_norm"].dropna().unique().tolist()),
                "target_date_rows": int(len(target)), "regular_session_rows": int(len(session)),
                "contracts_on_target_date": len(contracts),
                "full_375_bar_contract_count": sum(c["full_375_bar_session"] for c in contracts),
                "contracts": contracts, "decision": "CONTRACT_SCHEMA_AUDITED"})
        except Exception as exc:
            entries.append({"target_expiry": expiry, "file_found": True, "file_path": path,
                            "decision": "BLOCKED_DOWNLOAD_OR_PARSE_ERROR", "error_type": type(exc).__name__})
            errors.append(f"{expiry}: {type(exc).__name__}")
    all_files = all(x.get("file_found") for x in entries)
    schema_ok = all(x.get("decision") == "CONTRACT_SCHEMA_AUDITED" and x.get("target_expiry") in x.get("explicit_expiry_values", []) for x in entries)
    decision = "FIXED_CONTRACT_SOURCE_CANDIDATE" if all_files and schema_ok else "PARTIAL_OR_BLOCKED_SOURCE_AUDIT"
    result = {"phase": 76, "dataset": REPO, "license_as_published": "CC-BY-NC-4.0",
              "targets": TARGETS, "decision": decision, "entries": entries, "errors": errors,
              "raw_prices_persisted": False,
              "interpretation": "This audit only checks fixed-expiry file/schema/coverage. Exact strategy-leg replay still requires matching the frozen strike/side/window and confirming license compliance. OHLC does not establish executable bid/ask or depth."}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = ["# Phase 76 — HF fixed-contract source audit", "", f"Decision: **{decision}**", "", f"Dataset: `{REPO}`", "License listed on dataset card: CC-BY-NC-4.0", "",
             "| Target expiry | File found | Rows on target date | Session rows | Contracts | Full 375-bar contracts | Decision |", "|---|---:|---:|---:|---:|---:|---|"]
    for e in entries:
        lines.append(f"| {e['target_expiry']} | {e.get('file_found', False)} | {e.get('target_date_rows', 0)} | {e.get('regular_session_rows', 0)} | {e.get('contracts_on_target_date', 0)} | {e.get('full_375_bar_contract_count', 0)} | {e['decision']} |")
    lines += ["", "## Interpretation", "", result["interpretation"], "", "Only aggregate diagnostics are retained. Downloaded source files remain in ephemeral runner storage and are not committed."]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(decision)

if __name__ == "__main__":
    main()
