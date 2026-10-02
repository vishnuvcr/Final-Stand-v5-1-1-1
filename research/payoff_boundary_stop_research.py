import os
from pathlib import Path

import numpy as np
import pandas as pd

from research.stop_loss_research import (
    TZ,
    END,
    build_paths,
    load,
    exec_px,
    charges,
)

OUT = Path(os.getenv("OUT_DIR", "results/dynamic_n_corrected/phase20_payoff_boundary"))
OUT.mkdir(parents=True, exist_ok=True)

TRAIN_END = pd.Timestamp("2023-12-31", tz=TZ)
VALIDATION_START = pd.Timestamp("2024-01-01", tz=TZ)
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


def exit_net(trade, point):
    raw_exit = point["raw_exit"]
    exit_exec = (
        exec_px(raw_exit[0], "sell"),
        exec_px(raw_exit[1], "buy"),
        exec_px(raw_exit[2], "buy"),
    )
    entry_ts = pd.Timestamp(trade["entry_ts"])
    entry_orders = [
        (entry_ts, "buy", trade["entry_exec"][0]),
        (entry_ts, "sell", trade["entry_exec"][1]),
        (entry_ts, "sell", trade["entry_exec"][2]),
    ]
    exit_orders = [
        (point["ts"], "sell", exit_exec[0]),
        (point["ts"], "buy", exit_exec[1]),
        (point["ts"], "buy", exit_exec[2]),
    ]
    return point["gross"] - charges(entry_orders, exit_orders, trade["lot"])


def prepare_paths(trades):
    spot = load("index/NIFTY.parquet")[["timestamp", "close"]].copy()
    spot["timestamp"] = pd.to_datetime(spot["timestamp"])
    if spot["timestamp"].dt.tz is None:
        spot["timestamp"] = spot["timestamp"].dt.tz_localize(TZ)
    else:
        spot["timestamp"] = spot["timestamp"].dt.tz_convert(TZ)
    spot_map = dict(zip(spot["timestamp"], spot["close"]))

    for t in trades:
        common = []
        for i, p in enumerate(t["path"]):
            q = dict(p)
            q["idx"] = i
            q["spot"] = spot_map.get(pd.Timestamp(p["ts"]))
            common.append(q)
        t["path_with_spot"] = common

        ep = t["entry_exec"]
        kn, kn1, kn2 = t["strikes"]
        credit = ep[1] + ep[2] - ep[0]
        base_level = kn1 + kn2 - kn
        if t["option_type"] == "CE":
            t["boundary"] = base_level + credit
            t["boundary_side"] = "upper"
        else:
            t["boundary"] = base_level - credit
            t["boundary_side"] = "lower"
        t["entry_credit_points"] = credit
        t["base_level"] = base_level
    return trades


def first_confirmed_boundary_stop(trade, buffer, condition_family, confirm):
    pts = [p for p in trade["path_with_spot"] if p["spot"] is not None]
    if not pts:
        return None

    def condition(p):
        if trade["boundary_side"] == "upper":
            breached = float(p["spot"]) >= trade["boundary"] + buffer
        else:
            breached = float(p["spot"]) <= trade["boundary"] - buffer
        if not breached:
            return False
        if condition_family in ("negative_mtm", "negative_mtm_mfe50"):
            if not (p["gross"] < 0):
                return False
        if condition_family == "negative_mtm_mfe50":
            if not (p["mfe"] < 0.50 * trade["target"]):
                return False
        return True

    if confirm <= 1:
        for p in pts:
            if condition(p):
                return p["idx"]
        return None

    for j in range(len(pts) - confirm + 1):
        window = pts[j:j + confirm]
        ok = True
        for k, p in enumerate(window):
            if not condition(p):
                ok = False
                break
            if k > 0:
                delta = (pd.Timestamp(window[k]["ts"]) - pd.Timestamp(window[k - 1]["ts"])).total_seconds()
                if delta != 60:
                    ok = False
                    break
        if ok:
            return window[0]["idx"]
    return None


def expiry_phase19_stop(trade):
    expiry_date = pd.Timestamp(trade["expiry"], tz=TZ).date()
    for p in trade["path"]:
        ts = pd.Timestamp(p["ts"])
        after_cut = (
            ts.date() == expiry_date
            and (ts.hour > 13 or (ts.hour == 13 and ts.minute >= 30))
        )
        if after_cut and p["gross"] < 0 and p["mfe"] < 0.50 * trade["target"]:
            return p["idx"]
    return None


def evaluate(trades, stop_index_fn, variant_name):
    rows = []
    for t in trades:
        idx = stop_index_fn(t)
        if idx is None:
            exit_idx = len(t["path"]) - 1
            reason = t["base_exit_reason"]
        else:
            exit_idx = min(idx, len(t["path"]) - 1)
            reason = "STOP"
        p = t["path"][exit_idx]
        candidate_net = exit_net(t, p)

        rows.append({
            "expiry": t["expiry"],
            "direction": t["direction"],
            "option_type": t["option_type"],
            "n_selected": t["n_selected"],
            "spot_entry": t.get("spot_entry", np.nan),
            "boundary": t["boundary"],
            "boundary_side": t["boundary_side"],
            "entry_credit_points": t["entry_credit_points"],
            "target": t["target"],
            "base_net": t["base_net"],
            "candidate_net": candidate_net,
            "net_uplift": candidate_net - t["base_net"],
            "base_positive": t["base_net"] > 0,
            "changed_before_base": p["ts"] < t["base_exit_ts"],
            "winner_affected": (t["base_net"] > 0) and (p["ts"] < t["base_exit_ts"]),
            "loss_reduction": max(candidate_net - t["base_net"], 0.0) if t["base_net"] < 0 else 0.0,
            "loss_eliminated": (t["base_net"] < 0) and (candidate_net >= 0),
            "stop_ts": p["ts"],
            "stop_reason": reason,
            "boundary_distance_at_stop": (
                (float(p["spot"]) - t["boundary"]) if t["boundary_side"] == "upper"
                else (t["boundary"] - float(p["spot"]))
            ) if p.get("spot") is not None else np.nan,
            "variant": variant_name,
        })
    return pd.DataFrame(rows)


def summarize(df):
    if df.empty:
        return {
            "trades": 0,
            "base_net": 0.0,
            "candidate_net": 0.0,
            "net_uplift": 0.0,
            "winner_affected": 0,
            "loss_reduction": 0.0,
            "losses_eliminated": 0,
            "stops": 0,
            "base_dd": 0.0,
            "candidate_dd": 0.0,
        }
    return {
        "trades": int(len(df)),
        "base_net": float(df["base_net"].sum()),
        "candidate_net": float(df["candidate_net"].sum()),
        "net_uplift": float(df["net_uplift"].sum()),
        "winner_affected": int(df["winner_affected"].sum()),
        "loss_reduction": float(df["loss_reduction"].sum()),
        "losses_eliminated": int(df["loss_eliminated"].sum()),
        "stops": int(df["changed_before_base"].sum()),
        "base_dd": max_dd(df["base_net"].tolist()),
        "candidate_dd": max_dd(df["candidate_net"].tolist()),
    }


def split_trades(trades):
    train, validation, holdout = [], [], []
    for t in trades:
        d = pd.Timestamp(t["expiry"], tz=TZ)
        if d <= TRAIN_END:
            train.append(t)
        elif d <= VALIDATION_END:
            validation.append(t)
        else:
            holdout.append(t)
    return train, validation, holdout


def make_boundary_rules():
    rules = []
    for buffer in BOUNDARY_BUFFERS:
        for confirm in CONFIRM_BARS:
            for family in CONDITION_FAMILIES:
                rules.append({
                    "name": f"boundary_b{buffer:g}_c{confirm}_{family}",
                    "buffer": buffer,
                    "confirm": confirm,
                    "condition_family": family,
                })
    return rules


def run_rule_set(trades, rules):
    records = []
    details = {}
    for rule in rules:
        df = evaluate(
            trades,
            lambda t, r=rule: first_confirmed_boundary_stop(
                t, r["buffer"], r["condition_family"], r["confirm"]
            ),
            rule["name"],
        )
        details[rule["name"]] = df
        s = summarize(df)
        records.append({**rule, **s})
    return pd.DataFrame(records), details


def combined_stop(trade, boundary_rule):
    b = first_confirmed_boundary_stop(
        trade,
        boundary_rule["buffer"],
        boundary_rule["condition_family"],
        boundary_rule["confirm"],
    )
    e = expiry_phase19_stop(trade)
    choices = [x for x in (b, e) if x is not None]
    return min(choices) if choices else None


def main():
    trades = prepare_paths(build_paths())
    if not trades:
        raise RuntimeError("No reconstructed trades")

    train, validation, holdout = split_trades(trades)
    rules = make_boundary_rules()

    train_grid, train_details = run_rule_set(train, rules)
    eligible = train_grid[train_grid["winner_affected"] == 0].copy()

    if eligible.empty:
        raise RuntimeError("No boundary rule preserved all training baseline-positive trades")

    selected = eligible.sort_values(
        ["net_uplift", "loss_reduction", "stops"],
        ascending=[False, False, True],
    ).iloc[0].to_dict()
    selected_name = selected["name"]

    selected_train = train_details[selected_name]
    selected_rule = next(r for r in rules if r["name"] == selected_name)

    validation_selected = evaluate(
        validation,
        lambda t: first_confirmed_boundary_stop(
            t,
            selected_rule["buffer"],
            selected_rule["condition_family"],
            selected_rule["confirm"],
        ),
        selected_name,
    )
    holdout_selected = evaluate(
        holdout,
        lambda t: first_confirmed_boundary_stop(
            t,
            selected_rule["buffer"],
            selected_rule["condition_family"],
            selected_rule["confirm"],
        ),
        selected_name,
    )

    # Fixed Phase-19 comparator.
    expiry_stop_train = evaluate(train, expiry_phase19_stop, "phase19_expiry_stop")
    expiry_stop_validation = evaluate(validation, expiry_phase19_stop, "phase19_expiry_stop")
    expiry_stop_holdout = evaluate(holdout, expiry_phase19_stop, "phase19_expiry_stop")

    # Combined rule: selected payoff-boundary stop OR fixed Phase-19 stop.
    combined_train = evaluate(
        train,
        lambda t: combined_stop(t, selected_rule),
        "combined_boundary_or_phase19",
    )
    combined_validation = evaluate(
        validation,
        lambda t: combined_stop(t, selected_rule),
        "combined_boundary_or_phase19",
    )
    combined_holdout = evaluate(
        holdout,
        lambda t: combined_stop(t, selected_rule),
        "combined_boundary_or_phase19",
    )

    full_train = pd.concat([selected_train], ignore_index=True)
    full_boundary = pd.concat([selected_train, validation_selected, holdout_selected], ignore_index=True)
    full_phase19 = pd.concat([expiry_stop_train, expiry_stop_validation, expiry_stop_holdout], ignore_index=True)
    full_combined = pd.concat([combined_train, combined_validation, combined_holdout], ignore_index=True)
    baseline = pd.DataFrame([{
        "variant": "baseline_no_stop",
        **summarize(pd.concat([
            evaluate(train, lambda t: None, "baseline_no_stop"),
            evaluate(validation, lambda t: None, "baseline_no_stop"),
            evaluate(holdout, lambda t: None, "baseline_no_stop"),
        ], ignore_index=True)),
    }])

    variant_rows = []
    for variant, df in [
        ("phase19_expiry_stop", full_phase19),
        ("selected_boundary_stop", full_boundary),
        ("combined_boundary_or_phase19", full_combined),
    ]:
        variant_rows.append({"variant": variant, **summarize(df)})
    variant_rows.insert(0, baseline.iloc[0].to_dict())
    variants = pd.DataFrame(variant_rows)

    train_compare = pd.DataFrame([
        {"variant": "phase19_expiry_stop", **summarize(expiry_stop_train)},
        {"variant": "selected_boundary_stop", **summarize(selected_train)},
        {"variant": "combined_boundary_or_phase19", **summarize(combined_train)},
    ])
    validation_compare = pd.DataFrame([
        {"variant": "phase19_expiry_stop", **summarize(expiry_stop_validation)},
        {"variant": "selected_boundary_stop", **summarize(validation_selected)},
        {"variant": "combined_boundary_or_phase19", **summarize(combined_validation)},
    ])
    holdout_compare = pd.DataFrame([
        {"variant": "phase19_expiry_stop", **summarize(expiry_stop_holdout)},
        {"variant": "selected_boundary_stop", **summarize(holdout_selected)},
        {"variant": "combined_boundary_or_phase19", **summarize(combined_holdout)},
    ])

    OUT.mkdir(parents=True, exist_ok=True)
    train_grid.to_csv(OUT / "boundary_rule_train_grid.csv", index=False)
    variants.to_csv(OUT / "variant_full_sample_summary.csv", index=False)
    train_compare.to_csv(OUT / "variant_train_summary.csv", index=False)
    validation_compare.to_csv(OUT / "variant_validation_summary.csv", index=False)
    holdout_compare.to_csv(OUT / "variant_holdout_summary.csv", index=False)
    selected_train.to_csv(OUT / "selected_boundary_train_trade_level.csv", index=False)
    validation_selected.to_csv(OUT / "selected_boundary_validation_trade_level.csv", index=False)
    holdout_selected.to_csv(OUT / "selected_boundary_holdout_trade_level.csv", index=False)
    full_boundary.to_csv(OUT / "selected_boundary_full_trade_level.csv", index=False)
    full_phase19.to_csv(OUT / "phase19_expiry_stop_full_trade_level.csv", index=False)
    full_combined.to_csv(OUT / "combined_boundary_or_phase19_full_trade_level.csv", index=False)

    safe_all = train_grid[train_grid["winner_affected"] == 0].sort_values(
        ["net_uplift", "loss_reduction"], ascending=[False, False]
    )
    safe_all.to_csv(OUT / "zero_winner_training_rules.csv", index=False)

    formal_promotion = (
        summarize(validation_selected)["winner_affected"] == 0
        and summarize(holdout_selected)["winner_affected"] == 0
        and summarize(validation_selected)["net_uplift"] > 0
        and summarize(holdout_selected)["net_uplift"] > 0
        and summarize(validation_selected)["candidate_dd"] <= summarize(validation_selected)["base_dd"] * 1.05
        and summarize(holdout_selected)["candidate_dd"] <= summarize(holdout_selected)["base_dd"] * 1.05
    )

    boundary_status = "PASS" if formal_promotion else "FAIL"

    report = f"""# Phase 20 — Payoff-Boundary Stop Research

## Research question

Does the entry-time expiry zero-P&L boundary from the payoff chart provide a robust early-warning stop when NIFTY moves beyond the green/profit region before expiry, and does it add information beyond the fixed Phase-19 expiry-day stop?

## Boundary definition

The selected position is known at entry. Using the same entry execution slippage as the backtest, the net entry credit in option points is:

credit = short-leg executed premiums - long-leg executed premium.

The expiry zero-P&L boundary is:

- call-side upper boundary = K_(n+1) + K_(n+2) - K_n + credit;
- put-side lower boundary = K_(n+1) + K_(n+2) - K_n - credit.

A boundary breach is therefore a **structural expiry risk signal**, not a claim that the intraday position is already losing. That is why MTM/MFE-filtered variants were pre-registered.

## Pre-registered boundary grid

Buffers: 0, 50, 100, 200 and 400 NIFTY points.

Confirmation: 1 or 3 exact consecutive minute observations.

Condition families:
- boundary-only;
- boundary + current combined MTM < 0;
- boundary + MTM < 0 + MFE < 0.50× target.

Selection was frozen using training data only, requiring zero baseline-positive trades affected and then maximizing training net uplift.

## Selected boundary rule

**{selected_name}**

Boundary buffer: {selected_rule["buffer"]:.0f} points  
Confirmation: {selected_rule["confirm"]} minute(s)  
Condition: {selected_rule["condition_family"]}

## Walk-forward comparison

Training: through 2023-12-31  
Validation: 2024-01-01 to 2025-12-31  
Holdout: 2026-01-01 to 2026-09-30

### Training
{train_compare.to_string(index=False)}

### Validation
{validation_compare.to_string(index=False)}

### Holdout
{holdout_compare.to_string(index=False)}

### Full sample
{variants.to_string(index=False)}

## Phase-19 comparator

The Phase-19 comparator is fixed and not re-optimised:

**13:30 IST on expiry day + combined MTM < 0 + MFE < 0.50× original target.**

## Boundary promotion screen

Result: **{boundary_status}**

The screen requires:
- zero baseline-positive trades affected in validation and holdout;
- positive net-P&L uplift in validation and holdout;
- no material maximum-drawdown deterioration (5% tolerance used as a research screen);
- exact minute-level costs retained.

## Interpretation

An expiry payoff boundary is useful only as an early structural stress marker. Because option time value remains before expiry, a boundary crossing can recover; the MTM/MFE-filtered variants explicitly test whether requiring present loss and insufficient prior favourable excursion makes the signal more selective.

This phase does not claim the boundary rule is guaranteed to improve live execution. Exact common timestamps are required for both NIFTY spot and all three option legs, and crossings between observations are not observed.

## Complete-strategy decision

The final strategy specification should include the Phase-19 expiry-day rule only if the boundary comparison does not provide a robust incremental improvement under the locked screen. The repository will record the exact final decision after the workflow completes.
"""

    (OUT / "BOUNDARY_STOP_CONCLUSION.md").write_text(report, encoding="utf-8")
    pd.DataFrame([{
        "selected_rule": selected_name,
        "boundary_status": boundary_status,
        "train_net_uplift": summarize(selected_train)["net_uplift"],
        "validation_net_uplift": summarize(validation_selected)["net_uplift"],
        "holdout_net_uplift": summarize(holdout_selected)["net_uplift"],
        "validation_winner_affected": summarize(validation_selected)["winner_affected"],
        "holdout_winner_affected": summarize(holdout_selected)["winner_affected"],
        "validation_candidate_dd": summarize(validation_selected)["candidate_dd"],
        "holdout_candidate_dd": summarize(holdout_selected)["candidate_dd"],
    }]).to_csv(OUT / "phase20_status.csv", index=False)

    print("SELECTED_BOUNDARY_RULE", selected_name)
    print("BOUNDARY_STATUS", boundary_status)
    print("\nTRAIN\n", train_compare.to_string(index=False))
    print("\nVALIDATION\n", validation_compare.to_string(index=False))
    print("\nHOLDOUT\n", holdout_compare.to_string(index=False))
    print("\nFULL\n", variants.to_string(index=False))


if __name__ == "__main__":
    main()
