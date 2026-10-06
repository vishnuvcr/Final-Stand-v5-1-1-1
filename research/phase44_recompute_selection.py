import json
from pathlib import Path
import pandas as pd
import numpy as np

from phase44_vix_tuning import (
    OUT, load_vix, profile_defs, profile_active,
    paired_stats, max_dd
)

BASE = OUT / "stage1_structure_time_matrix.csv"

def main():
    if not BASE.exists():
        raise FileNotFoundError(BASE)
    base = pd.read_csv(BASE)
    vix = load_vix()
    rows = []

    # Precompute each VIX profile's active status by exact registered entry timestamp.
    unique_entries = pd.unique(base["entry_ts"])
    activity = {}
    for pid, mode, par in profile_defs():
        for ets in unique_entries:
            activity[(pid, mode, str(ets))] = profile_active(vix, pd.Timestamp(ets), par, mode)

    for pid, mode, par in profile_defs():
        for (family, geom, entry_time), g in base.groupby(["family", "geom", "entry_time"], sort=False):
            g = g.copy()
            if len(g) < 15:
                continue
            active = np.array(
                [activity.get((pid, mode, str(x)), False) for x in g["entry_ts"]],
                dtype=bool,
            )
            if int(active.sum()) < 10:
                continue

            g = g.sort_values("expiry").reset_index(drop=True)
            active = np.array(
                [activity.get((pid, mode, str(x)), False) for x in g["entry_ts"]],
                dtype=bool,
            )

            cand_net = np.where(active, g["net"].to_numpy(float), 0.0)
            cand_net50 = np.where(active, g["net50"].to_numpy(float), 0.0)
            uplift = cand_net - g["net"].to_numpy(float)
            st = paired_stats(uplift)
            pos = uplift[uplift > 0]
            concentration = float(pos.max() / pos.sum()) if len(pos) and pos.sum() > 0 else 0.0

            rows.append({
                "family": family,
                "geom": geom,
                "entry_time": int(entry_time),
                "profile_id": pid,
                "mode": mode,
                "dev_n": int(active.sum()),
                "dev_total_expiries": int(len(g)),
                "dev_net": float(cand_net.sum()),
                "dev_net50": float(cand_net50.sum()),
                "dev_dd": max_dd(cand_net),
                "base_dev_net": float(g["net"].sum()),
                "base_dev_dd": max_dd(g["net"].to_numpy(float)),
                "dev_uplift": float(uplift.sum()),
                "dev_uplift_mean": st["mean"],
                "dev_ci_lo": st["ci_lo"],
                "dev_ci_hi": st["ci_hi"],
                "dev_p": st["p"],
                "max_positive_uplift_share": concentration,
            })

    all_df = pd.DataFrame(rows)
    if all_df.empty:
        raise RuntimeError("no corrected development profile rows")

    all_df.to_csv(OUT / "stage1_all_dev_profiles.csv", index=False)

    eligible = all_df[
        (all_df["dev_n"] >= 10)
        & (all_df["dev_net"] >= 0)
        & (all_df["dev_net50"] > 0)
        & (all_df["dev_uplift"] > 0)
    ].copy()

    picked = []
    per_family = {}
    for r in eligible.sort_values(
        ["dev_uplift_mean", "dev_net", "dev_n"],
        ascending=[False, False, False]
    ).itertuples(index=False):
        if per_family.get(r.family, 0) >= 5:
            continue
        picked.append(r._asdict())
        per_family[r.family] = per_family.get(r.family, 0) + 1
        if len(picked) >= 30:
            break

    frozen = pd.DataFrame(picked)
    if frozen.empty:
        frozen = pd.DataFrame(columns=all_df.columns)

    frozen.to_csv(OUT / "stage1_candidates.csv", index=False)
    frozen.to_csv(OUT / "frozen_dev_shortlist.csv", index=False)
    frozen.to_csv(OUT / "frozen_stage1.csv", index=False)

    decision = "DEVELOPMENT_FROZEN_VALIDATION_PENDING" if len(frozen) else "NO_STAGE1_CANDIDATES"
    summary = {
        "status": "COMPLETE_STAGE1_DEVELOPMENT_CORRECTED",
        "stage1_rows": int(len(base)),
        "development_profile_rows": int(len(all_df)),
        "candidate_rows": int(len(eligible)),
        "frozen_candidates": int(len(frozen)),
        "holm_survivors": 0,
        "holdout_opened_after_validation_freeze": False,
        "decision": decision,
        "correction": "F44-016_zero_uplift_control_comparison",
    }
    (OUT / "stage1_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
