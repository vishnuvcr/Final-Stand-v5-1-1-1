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
    files = HfApi(token=token).list_repo_files(repo_id=REPO, repo_type="dataset")
    entries, errors = [], []
    for expiry in TARGETS:
        expected = f"options/NIFTY/{expiry}.parquet"
        candidates = [p for p in files if p == expected or (p.startswith("options/NIFTY/") and Path(p).stem == expiry)]
        if not candidates:
            entries.append({"target_expiry": expiry, "file_found": False, "decision": "BLOCKED_TARGET_FILE_ABSENT"})
            continue
        path = candidates[0]
        try:
            local = hf_hub_download(repo_id=REPO, repo_type="dataset", filename=path, token=token)
            frame = pd.read_parquet(local)
            cols = set(map(str, frame.columns))
            missing = sorted(REQUIRED - cols)
            if missing:
                entries.append({"target_expiry": expiry, "file_found": True, "file_path": path,
                    "row_count_file": int(len(frame)), "columns": sorted(cols), "missing_required_columns": missing,
                    "decision": "BLOCKED_SCHEMA_MISMATCH"})
                continue
            frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True).dt.tz_convert("Asia/Kolkata")
            frame["expiry_norm"] = pd.to_datetime(frame["expiry"], errors="coerce").dt.strftime("%Y-%m-%d")
            frame["option_type_norm"] = frame["option_type"].astype(str).str.upper().str.strip()
            frame["strike_num"] = pd.to_numeric(frame["strike"], errors="coerce")
            frame = frame[frame["timestamp"].notna()]
            exp_rows = frame[frame["expiry_norm"] == expiry]
            session = exp_rows[(exp_rows["timestamp"].dt.time >= time(9,15)) & (exp_rows["timestamp"].dt.time <= time(15,29,59))]
            contracts = []
            for (exp, strike, side, trading_day), g in session.groupby(["expiry_norm", "strike_num", "option_type_norm", "trading_day"], dropna=True):
                ts = g["timestamp"].drop_duplicates().sort_values()
                contracts.append({"expiry": str(exp), "strike": float(strike), "option_type": str(side), "trading_day": str(trading_day),
                    "row_count": int(len(g)), "unique_timestamps": int(ts.nunique()),
                    "first_timestamp_ist": ts.iloc[0].isoformat() if len(ts) else None,
                    "last_timestamp_ist": ts.iloc[-1].isoformat() if len(ts) else None,
                    "full_375_bar_session": int(ts.nunique()) == 375})
            trade_days = sorted(session["timestamp"].dt.strftime("%Y-%m-%d").dropna().unique().tolist())
            explicit_expiries = sorted(x for x in frame["expiry_norm"].dropna().unique().tolist())
            full_expiry_day = sum(c["full_375_bar_session"] and c["trading_day"] == expiry for c in contracts)
            expiry_day_rows = int((session["timestamp"].dt.strftime("%Y-%m-%d") == expiry).sum())
            expiry_session_present = expiry in trade_days
            entries.append({"target_expiry": expiry, "file_found": True, "file_path": path,
                "row_count_file": int(len(frame)), "columns": sorted(cols), "explicit_expiry_values": explicit_expiries,
                "rows_for_expiry_contracts": int(len(exp_rows)), "regular_session_rows_all_trade_days": int(len(session)),
                "trade_days_in_file": trade_days, "trade_day_count": len(trade_days),
                "first_trade_day": trade_days[0] if trade_days else None, "last_trade_day": trade_days[-1] if trade_days else None,
                "expiry_day_session_present": expiry_session_present, "expiry_day_session_rows": expiry_day_rows,
                "contract_side_strike_day_groups": len(contracts),
                "full_375_bar_contract_day_count_all_days": sum(c["full_375_bar_session"] for c in contracts),
                "full_375_bar_contract_count_on_expiry_day": full_expiry_day,
                "contracts": contracts,
                "decision": "CONTRACT_SCHEMA_AND_EXPIRY_SESSION_PASS" if expiry_session_present and full_expiry_day > 0 else "BLOCKED_INCOMPLETE_EXPIRY_SESSION"})
        except Exception as exc:
            entries.append({"target_expiry": expiry, "file_found": True, "file_path": path,
                            "decision": "BLOCKED_DOWNLOAD_OR_PARSE_ERROR", "error_type": type(exc).__name__})
            errors.append(f"{expiry}: {type(exc).__name__}")
    all_pass = len(entries) == len(TARGETS) and all(e.get("decision") == "CONTRACT_SCHEMA_AND_EXPIRY_SESSION_PASS" for e in entries)
    decision = "FIXED_CONTRACT_SOURCE_CANDIDATE" if all_pass else "BLOCKED_INCOMPLETE_FIXED_CONTRACT_HISTORY"
    result = {"phase": 76, "dataset": REPO, "license_as_published": "CC-BY-NC-4.0", "targets": TARGETS,
        "decision": decision, "entries": entries, "errors": errors, "raw_prices_persisted": False,
        "interpretation": "Exact expiry files and schema are not sufficient: the file must contain observations on the expiry session and at least one fixed contract with 375 regular-session bars on that expiry date. A file ending weeks before expiry is incomplete and cannot support expiry-day replay. Even a source pass would still require frozen-leg strike/side/window matching, license compliance and realistic execution costs."}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = ["# Phase 76 — HF fixed-contract source audit", "", f"Decision: **{decision}**", "", f"Dataset: `{REPO}`", "License listed on dataset card: CC-BY-NC-4.0", "",
        "| Expiry | File found | Trade days | Last trade day | Expiry session present | Expiry-session rows | Full 375-bar contracts on expiry | Decision |",
        "|---|---:|---:|---|---:|---:|---:|---|"]
    for e in entries:
        lines.append(f"| {e['target_expiry']} | {e.get('file_found', False)} | {e.get('trade_day_count', 0)} | {e.get('last_trade_day') or 'n/a'} | {e.get('expiry_day_session_present', False)} | {e.get('expiry_day_session_rows', 0)} | {e.get('full_375_bar_contract_count_on_expiry_day', 0)} | {e['decision']} |")
    lines += ["", "## Interpretation", "", result["interpretation"], "", "Only aggregate diagnostics are retained. Downloaded source files remain in ephemeral runner storage and are not committed."]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(decision)

if __name__ == "__main__":
    main()
