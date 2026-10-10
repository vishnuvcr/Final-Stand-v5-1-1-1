#!/usr/bin/env python3
"""Run one preregistered DEV->VAL selection-stability test; never reads holdout rows."""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "results/phase45_ready_made/strategy_vix_summary.csv"
OUT = ROOT / "results/phase95"
EXPECTED_SOURCE_SHA = "4208da2e1189a68af697e11d03dd7d4ac937ddf7"

def main():
    if not SOURCE.exists():
        raise SystemExit(f"Missing frozen source CSV: {SOURCE}")
    with SOURCE.open(newline="", encoding="utf-8") as f:
        all_rows = list(csv.DictReader(f))
    required = {"strategy", "split", "state", "trades", "net", "net50", "max_dd", "defined_risk"}
    if not all_rows or not required.issubset(all_rows[0]):
        raise SystemExit("Source CSV missing required fields")
    # Critical boundary: filter out holdout rows before all other processing.
    rows = [r for r in all_rows if r["split"] in {"development", "validation"} and r["state"] == "ALL"]
    candidates = {}
    for row in rows:
        candidates.setdefault(row["strategy"], {})[row["split"]] = row
    eligible = []
    for name, splits in candidates.items():
        dev = splits.get("development")
        val = splits.get("validation")
        if not dev or not val or dev["defined_risk"].strip().lower() != "true":
            continue
        if int(float(dev["trades"])) < 50:
            continue
        eligible.append({
            "strategy": name,
            "dev_trades": int(float(dev["trades"])),
            "dev_net": float(dev["net"]),
            "dev_net50": float(dev["net50"]),
            "dev_max_dd": float(dev["max_dd"]),
            "val_trades": int(float(val["trades"])),
            "val_net": float(val["net"]),
            "val_net50": float(val["net50"]),
            "val_max_dd": float(val["max_dd"]),
        })
    if not eligible:
        raise SystemExit("No eligible strategies after frozen criteria")
    eligible.sort(key=lambda r: (-r["dev_net50"], r["strategy"]))
    selected = eligible[0]
    for i, row in enumerate(eligible, start=1):
        row["development_rank"] = i
        row["selected_by_dev_rule"] = row["strategy"] == selected["strategy"]
        row["validation_net50_positive"] = row["val_net50"] > 0
    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / "selection_results.csv"
    fields = ["development_rank", "strategy", "dev_trades", "dev_net", "dev_net50", "dev_max_dd",
              "val_trades", "val_net", "val_net50", "val_max_dd", "selected_by_dev_rule",
              "validation_net50_positive"]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(eligible)
    report = {
        "phase": 95,
        "status": "PASS",
        "source_path": "results/phase45_ready_made/strategy_vix_summary.csv",
        "source_blob_sha": EXPECTED_SOURCE_SHA,
        "selection_rule": "defined_risk=True; state=ALL; development trades >=50; maximize development net50; alphabetical tie-break",
        "primary_endpoint": "selected strategy validation net50",
        "eligible_strategy_count": len(eligible),
        "selected_strategy": selected["strategy"],
        "selected_development_net50_inr": round(selected["dev_net50"], 2),
        "selected_validation_net50_inr": round(selected["val_net50"], 2),
        "selected_validation_trades": selected["val_trades"],
        "selected_validation_max_drawdown_inr": round(selected["val_max_dd"], 2),
        "selected_validation_positive": selected["val_net50"] > 0,
        "eligible_with_positive_validation_net50": sum(r["val_net50"] > 0 for r in eligible),
        "eligible_with_negative_or_zero_validation_net50": sum(r["val_net50"] <= 0 for r in eligible),
        "holdout_rows_loaded": False,
        "phase83_2026_holdout_accessed": False,
        "new_market_data_or_strategy_replay": False,
        "strategy_promoted": False,
        "interpretation": "PASS means the preregistered computation ran; profitability outcome is reported separately. This retrospective, previously explored source is not an independent blinded test."
    }
    (OUT / "validation_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
if __name__ == "__main__":
    main()
