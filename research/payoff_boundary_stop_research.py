import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from research.backtest_dynamic_n_corrected import (
    TZ,
    load,
    exec_px,
    charges,
)

OUT = Path(os.getenv("OUT_DIR", "results/dynamic_n_corrected/phase20_payoff_boundary"))
OUT.mkdir(parents=True, exist_ok=True)

TRAIN_END = pd.Timestamp("2023-12-31", tz=TZ)
VALIDATION_END = pd.Timestamp("2025-12-31", tz=TZ)
HOLDOUT_START = pd.Timestamp("2026-01-01", tz=TZ)

BOUNDARY_BUFFERS = [0.0, 50.0, 100.0, 200.0, 400.0]
CONFIRM_BARS = [1, 3]
CONDITION_FAMILIES = ["boundary_only", "negative_mtm", "negative_mtm_mfe50"]


def max_dd(values):
    s = 0.0
    peak = 0.0
    dd = 0.0
    for v in values:
        s += float(v)
        peak = max(peak, s)
        dd = max(dd, peak - s)
    return dd


def load_trade_ledgers():
    base = pd.read_csv("results/dynamic_n_corrected/phase10_primary/trades.csv")
    base["entry_ts"] = pd.to_datetime(base["entry_ts"])
    base["exit_ts"] = pd.to_datetime(base["exit_ts"])
    base["expiry"] = base["expiry"].astype(str)
    return base


def load_spot():
    spot = load("index/NIFTY.parquet")[["timestamp", "close"]].copy()
    spot["timestamp"] = pd.to_datetime(spot["timestamp"])
    if spot["timestamp"].dt.tz is None:
        spot["timestamp"] = spot["timestamp"].dt.tz_localize(TZ)
    else:
        spot["timestamp"] = spot["timestamp"].dt.tz_convert(TZ)
    return spot.rename(columns={"close": "spot"})


def build_boundary_metadata(base):
    rows = []
    for r in base.itertuples():
        ep = (
            exec_px(float(r.p_n_raw), "buy"),
            exec_px(float(r.p_n1_raw), "sell"),
            exec_px(float(r.p_n2_raw), "sell"),
        )
        credit = ep[1] + ep[2] - ep[0]
        base_level = float(r.k_n1) + float(r.k_n2) - float(r.k_n)
        if r.option_type == "CE":
            boundary = base_level + credit
            side = "upper"
        else:
            boundary = base_level - credit
            side = "lower"
        rows.append(
            {
                "expiry": r.expiry,
                "entry_ts": r.entry_ts,
                "exit_ts": r.exit_ts,
                "direction": r.direction,
                "option_type": r.option_type,
                "spot_entry": float(r.spot_entry),
                "n_selected": int(r.n_selected),
                "k_n": float(r.k_n),
                "k_n1": float(r.k_n1),
                "k_n2": float(r.k_n2),
                "lot": float(r.lot_size),
                "target": float(r.target_rupees),
                "base_net": float(r.net_rupees),
                "base_positive": bool(r.net_rupees > 0),
                "entry_credit_points": credit,
                "boundary": boundary,
                "boundary_side": side,
                "raw_entry": (
                    float(r.p_n_raw),
                    float(r.p_n1_raw),
                    float(r.p_n2_raw),
                ),
                "entry_exec": ep,
            }
        )
    return pd.DataFrame(rows)


def load_candidate_paths(meta, spot):
    candidates = []

    for r in meta.itertuples():
        s = spot[
            (spot["timestamp"] > r.entry_ts)
            & (spot["timestamp"] <= r.exit_ts)
        ][["timestamp", "spot"]]
        if s.empty:
            continue

        try:
            option_df = load(f"options/NIFTY/{r.expiry}.parquet")
        except Exception as exc:
            candidates.append({
                "expiry": r.expiry,
                "error": repr(exc),
                "path": None,
            })
            continue

        q = option_df[
            (option_df["timestamp"] > r.entry_ts)
            & (option_df["timestamp"] <= r.exit_ts)
            & (option_df["option_type"] == r.option_type)
            & (
                option_df["strike"].isin([r.k_n, r.k_n1, r.k_n2])
            )
        ]

        piv = q.pivot_table(
            index="timestamp",
            columns="strike",
            values="close",
            aggfunc="last",
        ).dropna(subset=[r.k_n, r.k_n1, r.k_n2])

        if piv.empty:
            candidates.append({
                "expiry": r.expiry,
                "error": "no complete three-leg option path",
                "path": None,
            })
            continue

        merged = s.merge(
            piv.reset_index(),
            on="timestamp",
            how="inner",
        ).sort_values("timestamp")

        if merged.empty:
            candidates.append({
                "expiry": r.expiry,
                "error": "no exact common timestamp between NIFTY and all three option legs",
                "path": None,
            })
            continue

        path = []
        running_mfe = -np.inf
        ep = r.entry_exec

        for _, row in merged.iterrows():
            raw_exit = (
                float(row[r.k_n]),
                float(row[r.k_n1]),
                float(row[r.k_n2]),
            )
            xp = (
                exec_px(raw_exit[0], "sell"),
                exec_px(raw_exit[1], "buy"),
                exec_px(raw_exit[2], "buy"),
            )
            gross_points = (
                (xp[0] - ep[0])
                + (ep[1] - xp[1])
                + (ep[2] - xp[2])
            )
            gross = gross_points * r.lot
            running_mfe = max(running_mfe, gross)
            breached = (
                float(row["spot"]) >= r.boundary
                if r.boundary_side == "upper"
                else float(row["spot"]) <= r.boundary
            )
            path.append(
                {
                    "ts": pd.Timestamp(row["timestamp"]),
                    "spot": float(row["spot"]),
                    "gross": gross,
                    "mfe": running_mfe,
                    "breached": breached,
                    "raw_exit": raw_exit,
                }
            )

        candidates.append({
            "expiry": r.expiry,
            "error": None,
            "path": path,
        })

    return ({x["expiry"]: x["path"] for x in candidates},
            [x for x in candidates if x["error"]])


def first_stop(entry, path, buffer, family, confirm):
    if path is None:
        return None

    def cond(p):
        if entry.boundary_side == "upper":
            crossed = p["spot"] >= entry.boundary + buffer
        else:
            crossed = p["spot"] <= entry.boundary - buffer
        if not crossed:
            return False
        if family in ("negative_mtm", "negative_mtm_mfe50"):
            if p["gross"] >= 0:
                return False
        if family == "negative_mtm_mfe50":
            if p["mfe"] >= 0.50 * entry.target:
                return False
        return True

    if confirm == 1:
        for p in path:
            if cond(p):
                return p
        return None

    for i in range(len(path) - confirm + 1):
        window = path[i:i + confirm]
        if all(cond(p) for p in window):
            ok = True
            for j in range(1, len(window)):
                delta = (
                    pd.Timestamp(window[j]["ts"])
                    - pd.Timestamp(window[j - 1]["ts"])
                ).total_seconds()
                if delta != 60:
                    ok = False
                    break
            if ok:
                return window[0]
    return None


def phase19_fixed_mfe50_stop(entry, path):
    """Locked comparator: 13:30 expiry-day + negative MTM + MFE < 0.50x target."""
    if path is None:
        return None
    expiry_date = pd.Timestamp(entry.expiry, tz=TZ).date()
    for p in path:
        ts = pd.Timestamp(p["ts"])
        after_cut = (
            ts.date() == expiry_date
            and (ts.hour > 13 or (ts.hour == 13 and ts.minute >= 30))
        )
        if after_cut and p["gross"] < 0 and p["mfe"] < 0.50 * entry.target:
            return p
    return None


def net_at(entry, stop_point):
    raw_exit = stop_point["raw_exit"]
    xp = (
        exec_px(raw_exit[0], "sell"),
        exec_px(raw_exit[1], "buy"),
        exec_px(raw_exit[2], "buy"),
    )
    entry_orders = [
        (entry.entry_ts, "buy", entry.entry_exec[0]),
        (entry.entry_ts, "sell", entry.entry_exec[1]),
        (entry.entry_ts, "sell", entry.entry_exec[2]),
    ]
    exit_orders = [
        (stop_point["ts"], "sell", xp[0]),
        (stop_point["ts"], "buy", xp[1]),
        (stop_point["ts"], "buy", xp[2]),
    ]
    return float(stop_point["gross"]) - charges(
        entry_orders,
        exit_orders,
        entry.lot,
    )


def make_rows(meta, path_map, stop_function, variant):
    rows = []
    for entry in meta.itertuples():
        stop = stop_function(entry, path_map.get(entry.expiry))
        if stop is None:
            candidate_net = entry.base_net
            stop_ts = entry.exit_ts
            reason = "BASELINE"
            distance = np.nan
        else:
            candidate_net = net_at(entry, stop)
            stop_ts = stop["ts"]
            reason = "STOP"
            distance = (
                float(stop["spot"]) - entry.boundary
                if entry.boundary_side == "upper"
                else entry.boundary - float(stop["spot"])
            )

        changed = pd.Timestamp(stop_ts) < entry.exit_ts
        rows.append(
            {
                "expiry": entry.expiry,
                "base_net": entry.base_net,
                "candidate_net": candidate_net,
                "net_uplift": candidate_net - entry.base_net,
                "base_positive": entry.base_positive,
                "changed_before_base": changed,
                "winner_affected": entry.base_positive and changed,
                "loss_reduction": (
                    max(candidate_net - entry.base_net, 0.0)
                    if entry.base_net < 0
                    else 0.0
                ),
                "loss_eliminated": entry.base_net < 0 and candidate_net >= 0,
                "stop_ts": stop_ts,
                "stop_reason": reason,
                "boundary": entry.boundary,
                "boundary_side": entry.boundary_side,
                "boundary_distance": distance,
                "variant": variant,
            }
        )
    return pd.DataFrame(rows)


def summarize(df):
    return {
        "trades": int(len(df)),
        "base_net": float(df.base_net.sum()),
        "candidate_net": float(df.candidate_net.sum()),
        "net_uplift": float(df.net_uplift.sum()),
        "winner_affected": int(df.winner_affected.sum()),
        "loss_reduction": float(df.loss_reduction.sum()),
        "losses_eliminated": int(df.loss_eliminated.sum()),
        "stops": int(df.changed_before_base.sum()),
        "base_dd": max_dd(df.base_net.tolist()),
        "candidate_dd": max_dd(df.candidate_net.tolist()),
    }


def split(df):
    exp = pd.to_datetime(df["expiry"]).dt.tz_localize(TZ)
    train = df[exp <= TRAIN_END].copy()
    validation = df[(exp > TRAIN_END) & (exp <= VALIDATION_END)].copy()
    holdout = df[exp >= HOLDOUT_START].copy()
    return train, validation, holdout


def main():
    base = load_trade_ledgers()
    meta = build_boundary_metadata(base)
    spot = load_spot()
    paths, path_errors = load_candidate_paths(meta, spot)

    rules = [
        {
            "name": f"boundary_b{b:g}_c{c}_{fam}",
            "buffer": b,
            "confirm": c,
            "family": fam,
        }
        for b in BOUNDARY_BUFFERS
        for c in CONFIRM_BARS
        for fam in CONDITION_FAMILIES
    ]

    grid = []
    rule_detail = {}
    for rule in rules:
        df = make_rows(
            meta,
            paths,
            lambda entry, path, r=rule: first_stop(
                entry, path, r["buffer"], r["family"], r["confirm"]
            ),
            rule["name"],
        )
        rule_detail[rule["name"]] = df
        s = summarize(df)
        grid.append({**rule, **s})

    grid_df = pd.DataFrame(grid)
    eligible = grid_df[grid_df.winner_affected == 0].copy()
    if eligible.empty:
        raise RuntimeError("No training-safe boundary rule existed.")

    # Selection is training-only.
    grid_df["period"] = "full"
    train_grid = []
    for rule in rules:
        df_train, _, _ = split(rule_detail[rule["name"]])
        s = summarize(df_train)
        train_grid.append({**rule, **s})
    train_grid = pd.DataFrame(train_grid)

    train_safe = train_grid[train_grid.winner_affected == 0].copy()
    if train_safe.empty:
        raise RuntimeError("No boundary rule preserved all training winners.")

    selected = train_safe.sort_values(
        ["net_uplift", "loss_reduction", "stops"],
        ascending=[False, False, True],
    ).iloc[0].to_dict()
    selected_rule = next(r for r in rules if r["name"] == selected["name"])

    selected_all = rule_detail[selected_rule["name"]]
    selected_train, selected_validation, selected_holdout = split(selected_all)

    p19_all = make_rows(
        meta,
        paths,
        lambda entry, path: phase19_fixed_mfe50_stop(entry, path),
        "phase19_expiry_stop_mfe50",
    )
    p19_train, p19_validation, p19_holdout = split(p19_all)

    phase19_expected = {
        "train_net_uplift": 1963.6676450499945,
        "validation_net_uplift": 1923.593403995007,
        "holdout_net_uplift": 6305.147862968499,
        "full_stops": 5,
    }
    phase19_crosscheck = {
        "train_net_uplift": summarize(p19_train)["net_uplift"],
        "validation_net_uplift": summarize(p19_validation)["net_uplift"],
        "holdout_net_uplift": summarize(p19_holdout)["net_uplift"],
        "full_stops": summarize(p19_all)["stops"],
    }
    phase19_crosscheck_ok = (
        abs(phase19_crosscheck["train_net_uplift"] - phase19_expected["train_net_uplift"]) < 1e-6
        and abs(phase19_crosscheck["validation_net_uplift"] - phase19_expected["validation_net_uplift"]) < 1e-6
        and abs(phase19_crosscheck["holdout_net_uplift"] - phase19_expected["holdout_net_uplift"]) < 1e-6
        and phase19_crosscheck["full_stops"] == phase19_expected["full_stops"]
    )
    if not phase19_crosscheck_ok:
        raise RuntimeError(
            "Phase-19 0.50x MFE comparator failed cross-check: "
            + repr(phase19_crosscheck)
        )

    def combined_rows(period_df, p19_df):
        boundary = period_df.set_index("expiry")
        phase19 = p19_df.set_index("expiry")
        rows = []
        for expiry, b in boundary.iterrows():
            p = phase19.loc[expiry]
            if b["changed_before_base"] and pd.Timestamp(b["stop_ts"]) <= pd.Timestamp(p["stop_ts"]):
                rows.append(b.to_dict())
            else:
                rows.append(p.to_dict())
        return pd.DataFrame(rows)

    combined_train = combined_rows(selected_train, p19_train)
    combined_validation = combined_rows(selected_validation, p19_validation)
    combined_holdout = combined_rows(selected_holdout, p19_holdout)
    combined_full = pd.concat([combined_train, combined_validation, combined_holdout], ignore_index=True)

    baseline_rows = base.rename(
        columns={"net_rupees": "base_net", "exit_ts": "stop_ts"}
    )[["expiry", "base_net", "stop_ts"]].copy()
    baseline_rows["candidate_net"] = baseline_rows["base_net"]
    baseline_rows["net_uplift"] = 0.0
    baseline_rows["base_positive"] = baseline_rows["base_net"] > 0
    baseline_rows["changed_before_base"] = False
    baseline_rows["winner_affected"] = False
    baseline_rows["loss_reduction"] = 0.0
    baseline_rows["loss_eliminated"] = False
    baseline_rows["variant"] = "baseline_no_stop"

    variants = pd.DataFrame([
        {"variant": "baseline_no_stop", **summarize(baseline_rows)},
        {"variant": "phase19_expiry_stop", **summarize(p19_all)},
        {"variant": "selected_boundary_stop", **summarize(selected_all)},
        {"variant": "combined_boundary_or_phase19", **summarize(combined_full)},
    ])

    train_compare = pd.DataFrame([
        {"variant": "phase19_expiry_stop", **summarize(p19_train)},
        {"variant": "selected_boundary_stop", **summarize(selected_train)},
        {"variant": "combined_boundary_or_phase19", **summarize(combined_train)},
    ])
    validation_compare = pd.DataFrame([
        {"variant": "phase19_expiry_stop", **summarize(p19_validation)},
        {"variant": "selected_boundary_stop", **summarize(selected_validation)},
        {"variant": "combined_boundary_or_phase19", **summarize(combined_validation)},
    ])
    holdout_compare = pd.DataFrame([
        {"variant": "phase19_expiry_stop", **summarize(p19_holdout)},
        {"variant": "selected_boundary_stop", **summarize(selected_holdout)},
        {"variant": "combined_boundary_or_phase19", **summarize(combined_holdout)},
    ])

    OUT.mkdir(parents=True, exist_ok=True)
    grid_df.to_csv(OUT / "boundary_rule_full_grid.csv", index=False)
    train_grid.to_csv(OUT / "boundary_rule_training_grid.csv", index=False)
    variants.to_csv(OUT / "variant_full_sample_summary.csv", index=False)
    train_compare.to_csv(OUT / "variant_train_summary.csv", index=False)
    validation_compare.to_csv(OUT / "variant_validation_summary.csv", index=False)
    holdout_compare.to_csv(OUT / "variant_holdout_summary.csv", index=False)
    selected_all.to_csv(OUT / "selected_boundary_full_trade_level.csv", index=False)
    selected_train.to_csv(OUT / "selected_boundary_train_trade_level.csv", index=False)
    selected_validation.to_csv(OUT / "selected_boundary_validation_trade_level.csv", index=False)
    selected_holdout.to_csv(OUT / "selected_boundary_holdout_trade_level.csv", index=False)
    p19_all.to_csv(OUT / "phase19_expiry_stop_full_trade_level.csv", index=False)
    combined_full.to_csv(OUT / "combined_boundary_or_phase19_full_trade_level.csv", index=False)

    safe_train = train_grid[train_grid.winner_affected == 0].sort_values(
        ["net_uplift", "loss_reduction"], ascending=[False, False]
    )
    safe_train.to_csv(OUT / "zero_winner_training_rules.csv", index=False)

    val_s = summarize(selected_validation)
    hold_s = summarize(selected_holdout)
    boundary_pass = (
        val_s["winner_affected"] == 0
        and hold_s["winner_affected"] == 0
        and val_s["net_uplift"] > 0
        and hold_s["net_uplift"] > 0
        and val_s["candidate_dd"] <= val_s["base_dd"] * 1.05
        and hold_s["candidate_dd"] <= hold_s["base_dd"] * 1.05
    )

    report = f"""# Phase 20 — Payoff-Boundary Stop Research

## Question

What happens when NIFTY moves materially beyond the green/profit region of the entry-time payoff chart before expiry?

## Structural boundary

Using the actual selected strikes and the same one-tick entry slippage as the locked backtest, define the entry net credit in points as:

short-leg executed premiums - long-leg executed premium.

The expiry zero-P&L stress boundary is:

- call-side upper boundary = K_(n+1) + K_(n+2) - K_n + credit;
- put-side lower boundary = K_(n+1) + K_(n+2) - K_n - credit.

This boundary is calculated entirely from entry information.

## Pre-registered search

Buffers: 0, 50, 100, 200 and 400 NIFTY points.  
Confirmation: 1 or 3 exact consecutive minutes.  
Conditions: boundary-only; boundary + negative MTM; boundary + negative MTM + MFE < 0.50× target.

Selection used training only, requiring zero baseline-positive trades affected and then maximizing training net uplift.

## Selected boundary rule

**{selected_rule["name"]}**

Buffer: {selected_rule["buffer"]:.0f} NIFTY points  
Confirmation: {selected_rule["confirm"]} minute(s)  
Condition: {selected_rule["family"]}

## Walk-forward comparison

### Training
{train_compare.to_string(index=False)}

### Validation
{validation_compare.to_string(index=False)}

### Holdout
{holdout_compare.to_string(index=False)}

### Full sample
{variants.to_string(index=False)}

## Phase-19 comparator

The fixed comparator remains:

**13:30 IST on expiry day + combined MTM < 0 + running MFE < 0.50× original target.**

## Boundary promotion screen

Boundary candidate passes the pre-registered screen: **{boundary_pass}**

Required:
- zero baseline-positive trades affected in validation and holdout;
- positive net uplift in validation and holdout;
- no more than 5% deterioration in maximum drawdown;
- exact minute-level execution costs retained.

## Interpretation guard

The expiry payoff boundary is an expiry-time structural stress level. An intraday breach does not mean the option position is already at its expiry loss; time value can allow recovery. This is why the research explicitly tested negative-MTM and MFE-filtered variants.

Spot/option alignment uses exact common timestamps only. No forward filling, interpolation or unobserved crossing is assumed.
"""

    (OUT / "BOUNDARY_STOP_CONCLUSION.md").write_text(report, encoding="utf-8")
    pd.DataFrame([{
        "selected_rule": selected_rule["name"],
        "boundary_pass": boundary_pass,
        "train_net_uplift": summarize(selected_train)["net_uplift"],
        "validation_net_uplift": val_s["net_uplift"],
        "holdout_net_uplift": hold_s["net_uplift"],
        "validation_winner_affected": val_s["winner_affected"],
        "holdout_winner_affected": hold_s["winner_affected"],
        "validation_candidate_dd": val_s["candidate_dd"],
        "holdout_candidate_dd": hold_s["candidate_dd"],
        "phase19_crosscheck_ok": phase19_crosscheck_ok,
        "phase19_train_uplift": phase19_crosscheck["train_net_uplift"],
        "phase19_validation_uplift": phase19_crosscheck["validation_net_uplift"],
        "phase19_holdout_uplift": phase19_crosscheck["holdout_net_uplift"],
        "phase19_full_stops": phase19_crosscheck["full_stops"],
    }]).to_csv(OUT / "phase20_status.csv", index=False)

    if path_errors:
        pd.DataFrame(path_errors).to_csv(OUT / "data_alignment_errors.csv", index=False)

    print("SELECTED_BOUNDARY_RULE", selected_rule["name"])
    print("BOUNDARY_PASS", boundary_pass)
    print("\nTRAIN\n", train_compare.to_string(index=False))
    print("\nVALIDATION\n", validation_compare.to_string(index=False))
    print("\nHOLDOUT\n", holdout_compare.to_string(index=False))
    print("\nFULL\n", variants.to_string(index=False))


if __name__ == "__main__":
    main()

# Final Phase 20 execution trigger: persistence workflow is now rebasing before push.
