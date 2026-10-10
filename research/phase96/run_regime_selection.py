#!/usr/bin/env python3
"""Preregistered regime-specific DEV->VAL strategy selection; holdout rows are discarded."""
import csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "results/phase45_ready_made/strategy_vix_summary.csv"
OUT = ROOT / "results/phase96"
EXPECTED_SOURCE_SHA = "4208da2e1189a68af697e11d03dd7d4ac937ddf7"
REGIMES = ("LOW", "NORMAL", "HIGH")
MIN_TRADES = 5

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + bytes([0]) + data).hexdigest()

def main():
    if not SOURCE.exists():
        raise SystemExit("Frozen Phase 45 source CSV is missing")
    raw = SOURCE.read_bytes()
    actual_sha = git_blob_sha(raw)
    if actual_sha != EXPECTED_SOURCE_SHA:
        raise SystemExit(f"Frozen source fingerprint mismatch: expected {EXPECTED_SOURCE_SHA}, got {actual_sha}")
    rows = []
    with SOURCE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"strategy", "split", "state", "trades", "net", "net50", "max_dd", "defined_risk"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise SystemExit("Source CSV missing required columns")
        for row in reader:
            # Critical holdout guard: never store or process fields from any other split.
            if row.get("split") not in {"development", "validation"}:
                continue
            if row.get("state") in REGIMES and row.get("defined_risk", "").strip().lower() == "true":
                rows.append(row)
    indexed = {}
    for row in rows:
        indexed.setdefault((row["strategy"], row["state"]), {})[row["split"]] = row
    selected = []
    for regime in REGIMES:
        eligible = []
        for (strategy, state), splits in indexed.items():
            if state != regime:
                continue
            dev, val = splits.get("development"), splits.get("validation")
            if not dev or not val:
                continue
            if int(float(dev["trades"])) < MIN_TRADES or int(float(val["trades"])) < MIN_TRADES:
                continue
            eligible.append({
                "regime": regime, "strategy": strategy,
                "dev_trades": int(float(dev["trades"])), "dev_net": float(dev["net"]),
                "dev_net50": float(dev["net50"]), "dev_max_dd": float(dev["max_dd"]),
                "val_trades": int(float(val["trades"])), "val_net": float(val["net"]),
                "val_net50": float(val["net50"]), "val_max_dd": float(val["max_dd"]),
            })
        if not eligible:
            raise SystemExit(f"No eligible candidate in frozen regime {regime}")
        eligible.sort(key=lambda r: (-r["dev_net50"], r["strategy"]))
        winner = eligible[0]
        winner["eligible_candidates_in_regime"] = len(eligible)
        winner["validation_net50_positive"] = winner["val_net50"] > 0
        selected.append(winner)
    OUT.mkdir(parents=True, exist_ok=True)
    fields = ["regime", "strategy", "eligible_candidates_in_regime", "dev_trades", "dev_net",
              "dev_net50", "dev_max_dd", "val_trades", "val_net", "val_net50", "val_max_dd",
              "validation_net50_positive"]
    with (OUT / "regime_selection_results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(selected)
    aggregate = round(sum(r["val_net50"] for r in selected), 2)
    report = {
        "phase": 96, "status": "PASS", "source_path": "results/phase45_ready_made/strategy_vix_summary.csv",
        "source_blob_sha": actual_sha, "regimes": list(REGIMES), "minimum_trades_per_split": MIN_TRADES,
        "selection_rule": "per regime: defined_risk=True; DEV and VAL trades >=5; maximize DEV net50; alphabetical tie-break",
        "primary_endpoint": "sum of selected LOW/NORMAL/HIGH validation net50 cells",
        "selected_regimes": [{"regime": r["regime"], "strategy": r["strategy"], "dev_net50": round(r["dev_net50"], 2),
                              "val_net50": round(r["val_net50"], 2), "val_trades": r["val_trades"],
                              "val_max_dd": round(r["val_max_dd"], 2), "eligible_candidates": r["eligible_candidates_in_regime"]}
                             for r in selected],
        "aggregate_validation_net50_inr": aggregate,
        "primary_endpoint_positive": aggregate > 0,
        "holdout_rows_retained_or_used": False, "phase83_2026_holdout_accessed": False,
        "new_market_data_or_strategy_replay": False, "strategy_promoted": False,
        "interpretation": "PASS means the frozen computation ran; positive aggregate is not proof of deployable portfolio performance because state-cell trade overlap and capital allocation are unavailable."
    }
    (OUT / "validation_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
if __name__ == "__main__":
    main()

# Registered source: frozen Phase 45 summary CSV; selection and split gates are defined above.
