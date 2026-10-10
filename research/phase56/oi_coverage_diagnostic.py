#!/usr/bin/env python3
"""Audit exact prior-minute OI source rows for Phase52 blocked contracts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
from huggingface_hub import hf_hub_download

REVISION = "0f4800e43e6f96cec0794369d78eb4d3c4211ef5"
DATASET = "thetrademarkk/india-index-options-1m"
EXPECTED_SHA = {
    "2025-03-13": "8118362cc9e58b646ac98cdd7eaf59675b995ba907a07cba8819b477fcc84f61",
    "2025-07-31": "64572ceb2a40e1cb45b7b688e6041e724ae034521ed82cfbd05d6b1a1c24941f",
    "2025-12-30": "5ed78461988ce2d90d56aa54afa032a72c7889cbfed73d8f7d8b2239ff580541",
}
TZ = "Asia/Kolkata"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ist_timestamp(value: Any) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        return ts.tz_localize(TZ)
    return ts.tz_convert(TZ)


def read_blocked_keys(ledger_path: Path) -> pd.DataFrame:
    ledger = pd.read_csv(ledger_path, dtype={"expiry": str, "entry_ts": str})
    required = {"status", "expiry", "resolved_legs_json", "entry_ts", "configuration_id"}
    missing = required - set(ledger.columns)
    if missing:
        raise ValueError(f"ledger missing columns: {sorted(missing)}")
    blocked = ledger.loc[ledger["status"].eq("BLOCKED_LEG_ELIGIBILITY")].copy()
    if len(blocked) != 100:
        raise ValueError(f"expected 100 blocked rows, found {len(blocked)}")
    items = []
    for row in blocked.to_dict("records"):
        legs = json.loads(row["resolved_legs_json"] or "[]")
        if not legs:
            raise ValueError(f"blocked row has empty leg payload: {row['configuration_id']}")
        for leg in legs:
            if not leg.get("option_type") or leg.get("strike") is None or not leg.get("prior_oi_timestamp"):
                raise ValueError(f"blocked leg lacks exact contract/time key: {row['configuration_id']}")
            items.append({
                "expiry": str(leg.get("expiry") or row["expiry"]),
                "prior_timestamp": ist_timestamp(leg["prior_oi_timestamp"]),
                "option_type": str(leg["option_type"]).upper().strip(),
                "strike": float(leg["strike"]),
                "configuration_id": str(row["configuration_id"]),
                "family_id": str(row.get("family_id", "")),
                "event_id": str(row.get("event_id", "")),
                "entry_ts": str(row["entry_ts"]),
                "leg_id": str(leg.get("leg_id", "")),
                "saved_prior_oi": leg.get("prior_oi"),
                "saved_prior_oi_status": str(leg.get("prior_oi_status", "")),
            })
    df = pd.DataFrame(items)
    df["expiry"] = df["expiry"].astype(str)
    return df


def normalize_source(path: Path, expiry: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    raw = pd.read_parquet(path)
    required = {"timestamp", "option_type", "strike", "open_interest"}
    missing = required - set(raw.columns)
    if missing:
        raise ValueError(f"{expiry} source partition missing columns: {sorted(missing)}")
    frame = raw.copy()
    frame["timestamp"] = frame["timestamp"].map(ist_timestamp)
    frame["option_type"] = frame["option_type"].astype(str).str.upper().str.strip()
    frame["strike"] = pd.to_numeric(frame["strike"], errors="coerce")
    frame["open_interest"] = pd.to_numeric(frame["open_interest"], errors="coerce")
    if "expiry" in frame.columns:
        frame["expiry"] = pd.to_datetime(frame["expiry"], errors="coerce").dt.strftime("%Y-%m-%d")
        if expiry not in set(frame["expiry"].dropna().astype(str)):
            raise ValueError(f"{expiry} partition expiry column does not include target expiry")
    else:
        frame["expiry"] = expiry
    frame = frame.dropna(subset=["timestamp", "strike"])
    before = len(frame)
    frame = frame.drop_duplicates(keep="first").reset_index(drop=True)
    meta = {"rows_before_exact_dedup": int(before), "rows_after_exact_dedup": int(len(frame)),
            "exact_duplicate_rows_removed": int(before - len(frame)), "sha256": sha256_file(path)}
    return frame, meta


def classify_source_row(count: int, values: list[float | None]) -> str:
    if count == 0:
        return "MISSING_EXACT_PRIOR_ROW"
    if count > 1:
        return "DUPLICATE_EXACT_PRIOR_ROWS"
    value = values[0]
    if value is None or pd.isna(value):
        return "NULL_OI"
    if float(value) == 0:
        return "ZERO_OI"
    if float(value) < 100:
        return "BELOW_GATE_OI"
    return "PASS_OI_GATE"


def audit(ledger_path: Path, out_dir: Path, token: str | None) -> dict[str, Any]:
    keys = read_blocked_keys(ledger_path)
    expiries = sorted(keys["expiry"].unique().tolist())
    if expiries != sorted(EXPECTED_SHA):
        raise ValueError(f"unexpected target expiries: {expiries}")
    rows = []
    source_meta = {}
    for expiry in expiries:
        name = f"options/NIFTY/{expiry}.parquet"
        local_path = Path(hf_hub_download(repo_id=DATASET, filename=name, repo_type="dataset",
                                          revision=REVISION, token=token))
        digest = sha256_file(local_path)
        if digest != EXPECTED_SHA[expiry]:
            raise ValueError(f"source hash mismatch for {expiry}: {digest}")
        frame, meta = normalize_source(local_path, expiry)
        source_meta[expiry] = {"source_path": name, "revision": REVISION, **meta}
        exp_keys = keys.loc[keys["expiry"].eq(expiry)]
        unique = exp_keys[["expiry", "prior_timestamp", "option_type", "strike"]].drop_duplicates()
        for key in unique.to_dict("records"):
            matched = frame.loc[
                frame["timestamp"].eq(key["prior_timestamp"])
                & frame["expiry"].eq(expiry)
                & frame["option_type"].eq(key["option_type"])
                & frame["strike"].eq(float(key["strike"]))
            ]
            values = [None if pd.isna(v) else float(v) for v in matched["open_interest"].tolist()]
            classification = classify_source_row(len(matched), values)
            saved = exp_keys.loc[
                exp_keys["prior_timestamp"].eq(key["prior_timestamp"])
                & exp_keys["option_type"].eq(key["option_type"])
                & exp_keys["strike"].eq(float(key["strike"]))
            ]
            rows.append({
                "expiry": expiry, "prior_timestamp_ist": key["prior_timestamp"].isoformat(),
                "option_type": key["option_type"], "strike": float(key["strike"]),
                "source_exact_rows": int(len(matched)), "source_oi_values": json.dumps(values),
                "source_classification": classification,
                "saved_oi_values": json.dumps(sorted({None if pd.isna(v) else float(v) for v in saved["saved_prior_oi"]}, key=lambda x: (x is None, x if x is not None else 0))),
                "saved_statuses": "|".join(sorted(set(saved["saved_prior_oi_status"].astype(str)))),
                "config_event_leg_references": int(len(saved)),
            })
    audit_df = pd.DataFrame(rows).sort_values(["expiry", "prior_timestamp_ist", "option_type", "strike"])
    if audit_df.duplicated(["expiry", "prior_timestamp_ist", "option_type", "strike"]).any():
        raise ValueError("duplicate audit keys in output")
    counts = {str(k): int(v) for k, v in audit_df["source_classification"].value_counts().sort_index().items()}
    if len(audit_df) == 0 or int(audit_df["config_event_leg_references"].sum()) != len(keys):
        raise ValueError("audit key/reference reconciliation failed")
    out_dir.mkdir(parents=True, exist_ok=True)
    audit_df.to_csv(out_dir / "contract_oi_audit.csv", index=False)
    report = {
        "phase": 56, "status": "PASS_SOURCE_ROW_DIAGNOSIS", "dataset": DATASET,
        "dataset_revision": REVISION, "blocked_configuration_event_rows": 100,
        "blocked_leg_references": int(len(keys)), "unique_contract_timestamp_keys": int(len(audit_df)),
        "source_classification_counts": counts, "source_partitions": source_meta,
        "row_reference_reconciliation": int(audit_df["config_event_leg_references"].sum()),
        "holdout_used": False, "pnl_recalculated": False, "raw_data_committed": False,
        "strategy_promotion_allowed": False,
        "interpretation": "Source-row diagnosis only; not strategy efficacy. The frozen OI >= 100 rule was not changed.",
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md = [
        "# Phase 56 — exact prior-minute OI source diagnosis", "",
        "**Source coverage diagnosis only; no P&L or strategy selection.**", "",
        f"- Dataset revision: `{REVISION}`",
        f"- Blocked configuration-event rows: {report['blocked_configuration_event_rows']}",
        f"- Blocked leg references: {report['blocked_leg_references']}",
        f"- Unique contract-time keys: {report['unique_contract_timestamp_keys']}",
        f"- Reference reconciliation: {report['row_reference_reconciliation']}",
        "", "## Exact source classifications", "",
        "| Classification | Contract-time keys |", "|---|---:|",
    ]
    md += [f"| {k} | {v} |" for k, v in sorted(counts.items())]
    md += ["", "## Source partitions", "", "| Expiry | SHA-256 | Rows after exact dedup | Exact duplicates removed |",
           "|---|---|---:|---:|"]
    md += [f"| {e} | `{m['sha256']}` | {m['rows_after_exact_dedup']} | {m['exact_duplicate_rows_removed']} |"
           for e, m in sorted(source_meta.items())]
    md += ["", "## Interpretation", "",
           "The classification is based on exact expiry, timestamp, option type and strike. No nearest-bar fallback, interpolation, or imputation is allowed.",
           "The source OI values are checked independently against the saved pilot payload. A numeric zero is not silently equated with a missing row.",
           "The fixed OI >= 100 gate remains unchanged. No P&L, holdout, strategy ranking, or promotion was performed.", ""]
    (out_dir / "report.md").write_text("\n".join(md))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", default="results/phase52/historical_pilot/event_replay.csv")
    parser.add_argument("--out", default="results/phase56/prior_oi_coverage")
    args = parser.parse_args()
    try:
        report = audit(Path(args.ledger), Path(args.out), os.environ.get("HF_TOKEN"))
    except Exception as exc:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        failure = {"phase": 56, "status": "ERROR_FAIL_CLOSED", "error_type": type(exc).__name__,
                   "error": str(exc)[:1000], "holdout_used": False, "strategy_promotion_allowed": False}
        (out / "report.json").write_text(json.dumps(failure, indent=2) + "\n")
        print(json.dumps(failure, sort_keys=True))
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
