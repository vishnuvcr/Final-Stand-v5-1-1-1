import json
import os
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE = REPO_ROOT / "results/phase51/PHASE51_1_SOURCE_GATE_REFERENCE.json"
OUT = Path("results/phase51/partial_oos") / (
    "d" + os.environ.get("TT03_DISTANCE", "300")
)
OUT.mkdir(parents=True, exist_ok=True)

PARTIAL_START = pd.Timestamp("2026-04-21", tz="Asia/Kolkata")
PARTIAL_END = pd.Timestamp("2026-07-21", tz="Asia/Kolkata")

# Reference artifact is verified in this branch before workflow execution.


def frozen_opportunity_audit():
    ref = json.loads(REFERENCE.read_text())
    observed = [
        pd.Timestamp(x, tz="Asia/Kolkata")
        for x in ref["source_gate_reference"]["observed_expiries"]
        if PARTIAL_START <= pd.Timestamp(x, tz="Asia/Kolkata") <= PARTIAL_END
    ]

    eligible = []
    exclusions = []
    for expiry in observed:
        scheduled_entry = (expiry - pd.Timedelta(days=3)).normalize()
        if scheduled_entry.weekday() >= 5:
            exclusions.append({
                "expiry": str(expiry.date()),
                "scheduled_entry_date": str(scheduled_entry.date()),
                "reason": "scheduled_three_calendar_day_entry_date_is_weekend",
            })
        else:
            eligible.append({
                "expiry": str(expiry.date()),
                "scheduled_entry_date": str(scheduled_entry.date()),
            })

    return ref, observed, eligible, exclusions


def main():
    ref, observed, eligible, exclusions = frozen_opportunity_audit()

    # This branch is explicitly a source-defined partial-OOS feasibility study.
    # The full Phase-51 OOS window remains frozen and blocked by the missing
    # 2026-07-28 and 2026-08-04 source blocks. Before any numerical P&L can be
    # produced, an eligible campaign must exist under the already-frozen TT-03
    # rule: entry exactly three calendar days before the listed expiry.
    if not eligible:
        audit = {
            "status": "NO_ELIGIBLE_CAMPAIGNS",
            "strategy": "TT-03 frozen source-faithful rule",
            "distance_points": int(os.environ.get("TT03_DISTANCE", "300")),
            "window": ["2026-04-21", "2026-07-21"],
            "source_repository": ref["source_gate_reference"]["original_options_source"]["repository"],
            "source_file": ref["source_gate_reference"]["original_options_source"]["file"],
            "source_sha256": ref["source_gate_reference"]["original_options_source"]["sha256"],
            "observed_expiries": [str(x.date()) for x in observed],
            "eligible_expiries": [],
            "ineligible_expiries": exclusions,
            "coverage_gate": "NOT_APPLICABLE_NO_ELIGIBLE_CAMPAIGNS",
            "pnl_interpretation_allowed": False,
            "reason": (
                "Every observed expiry in the available partial-OOS interval is a Tuesday. "
                "The frozen TT-03 rule schedules entry exactly three calendar days before expiry, "
                "which falls on Saturday for every observed expiry. Therefore no entry opportunity "
                "exists in the partial window. This is a protocol/calendar outcome, not a strategy P&L result."
            ),
        }
        (OUT / "opportunity_audit.json").write_text(json.dumps(audit, indent=2))
        summary = {
            "strategy": "TT-03",
            "status": "NO_ELIGIBLE_CAMPAIGNS",
            "engine_revision": "50B-TT03-WINDOW-V5",
            "trades": 0,
            "candidate_trades": 0,
            "coverage_exclusions": 0,
            "coverage_rate": None,
            "net": 0.0,
            "net50": 0.0,
            "net20": 0.0,
            "net20_50": 0.0,
            "eligible_expiries": [],
            "observed_expiries": [str(x.date()) for x in observed],
            "ineligible_expiries": exclusions,
            "coverage_gate": "NOT_APPLICABLE_NO_ELIGIBLE_CAMPAIGNS",
            "pnl_interpretation_allowed": False,
        }
        (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
        print(json.dumps(summary, indent=2))
        return

    # Numeric replay is deliberately fail-closed here. An eligible opportunity
    # would require a dedicated RISSIN-schema loader before P&L calculation;
    # falling back to the rejected supplemental source would violate Phase 51-1.
    raise RuntimeError(
        "Eligible campaigns detected, but the Phase-51-2 partial wrapper has no "
        "registered RISSIN loader. Do not substitute the rejected supplemental source."
    )


if __name__ == "__main__":
    main()
