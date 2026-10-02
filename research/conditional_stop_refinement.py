import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from research.stop_loss_research import (
    END,
    DEV_END,
    VAL_START,
    TZ,
    OUT as P17_OUT,
    build_paths,
    evaluate_rule,
    first_confirmed_stop,
)
from research.backtest_dynamic_n_corrected import exec_px, charges


OUT = Path(os.getenv("OUT_DIR", "results/dynamic_n_corrected/phase18_conditional_stop"))
CUTOFFS = [(13, 30), (14, 0), (14, 30), (15, 0)]
MFE_FRACS = [0.0, 0.10, 0.25, 0.50, 0.75, 1.00]
CONFIRM = [1, 3]


def candidate_rules():
    rules = []
    for hh, mm in CUTOFFS:
        for mf in MFE_FRACS:
            for c in CONFIRM:
                rules.append(
                    {
                        "name": f"mfe_cut_{hh:02d}{mm:02d}_mfe{mf:g}_c{c}",
                        "family": "expiry_mfe_negative_cutoff",
                        "cutoff": (hh, mm),
                        "mfe_frac": mf,
                        "confirm": c,
                    }
                )
    return rules


def stop_index(trade, rule):
    expiry_date = pd.Timestamp(trade["expiry"], tz=TZ).date()
    hh, mm = rule["cutoff"]
    mf = rule["mfe_frac"]

    def pred(p):
        after_cut = (
            p["ts"].date() == expiry_date
            and (
                p["ts"].hour > hh
                or (p["ts"].hour == hh and p["ts"].minute >= mm)
            )
        )
        return (
            after_cut
            and p["gross"] < 0
            and p["mfe"] < mf * trade["target"]
        )

    return first_confirmed_stop(trade["path"], pred, rule["confirm"])


def evaluate(trades, rule):
    rows = []
    for t in trades:
        idx = stop_index(t, rule)
        if idx is None:
            exit_idx = len(t["path"]) - 1
            reason = t["base_exit_reason"]
        else:
            exit_idx = idx
            reason = "STOP"

        p = t["path"][exit_idx]
        raw_exit = p["raw_exit"]
        exit_exec = (
            exec_px(raw_exit[0], "sell"),
            exec_px(raw_exit[1], "buy"),
            exec_px(raw_exit[2], "buy"),
        )
        entry_ts = pd.Timestamp(t["entry_ts"])
        entry_orders = [
            (entry_ts, "buy", t["entry_exec"][0]),
            (entry_ts, "sell", t["entry_exec"][1]),
            (entry_ts, "sell", t["entry_exec"][2]),
        ]
        exit_orders = [
            (p["ts"], "sell", exit_exec[0]),
            (p["ts"], "buy", exit_exec[1]),
            (p["ts"], "buy", exit_exec[2]),
        ]
        candidate_net = p["gross"] - charges(entry_orders, exit_orders, t["lot"])

        rows.append(
            {
                "expiry": t["expiry"],
                "base_net": t["base_net"],
                "base_reason": t["base_exit_reason"],
                "candidate_net": candidate_net,
                "net_uplift": candidate_net - t["base_net"],
                "stop_ts": p["ts"],
                "stop_reason": reason,
                "base_positive": t["base_net"] > 0,
                "changed_before_base": p["ts"] < t["base_exit_ts"],
            }
        )

    out = pd.DataFrame(rows)
    out["winner_affected"] = out["base_positive"] & out["changed_before_base"]
    out["loss_reduction"] = np.where(
        out["base_net"] < 0,
        np.maximum(out["candidate_net"] - out["base_net"], 0.0),
        0.0,
    )
    out["loss_eliminated"] = (out["base_net"] < 0) & (out["candidate_net"] >= 0)
    return out


def summarize(dev_trades, val_trades):
    recs = []
    detail = {}
    for rule in candidate_rules():
        dev = evaluate(dev_trades, rule)
        val = evaluate(val_trades, rule)
        detail[rule["name"]] = (dev, val)
        recs.append(
            {
                **rule,
                "dev_net_uplift": float(dev.net_uplift.sum()),
                "dev_winner_affected": int(dev.winner_affected.sum()),
                "dev_loss_reduction": float(dev.loss_reduction.sum()),
                "dev_losses_eliminated": int(dev.loss_eliminated.sum()),
                "val_net_uplift": float(val.net_uplift.sum()),
                "val_winner_affected": int(val.winner_affected.sum()),
                "val_loss_reduction": float(val.loss_reduction.sum()),
                "val_losses_eliminated": int(val.loss_eliminated.sum()),
            }
        )
    grid = pd.DataFrame(recs)

    eligible = grid[grid.dev_winner_affected == 0].copy()
    selected = eligible.sort_values(
        ["dev_net_uplift", "dev_loss_reduction"],
        ascending=[False, False],
    ).iloc[0]
    name = selected["name"]
    return grid, name, detail[name][0], detail[name][1]


def main():
    trades = build_paths()
    dev = [t for t in trades if pd.Timestamp(t["expiry"], tz=TZ) <= DEV_END]
    val = [t for t in trades if pd.Timestamp(t["expiry"], tz=TZ) >= VAL_START]

    grid, name, dev_out, val_out = summarize(dev, val)
    full_out = pd.concat([dev_out, val_out], ignore_index=True)

    OUT.mkdir(parents=True, exist_ok=True)
    grid.to_csv(OUT / "conditional_stop_grid.csv", index=False)
    dev_out.to_csv(OUT / "selected_dev_trade_level.csv", index=False)
    val_out.to_csv(OUT / "selected_validation_trade_level.csv", index=False)
    full_out.to_csv(OUT / "selected_full_trade_level.csv", index=False)

    s = grid.loc[grid["name"] == name].iloc[0]
    full_summary = {
        "selected_rule": name,
        "base_net": float(full_out.base_net.sum()),
        "candidate_net": float(full_out.candidate_net.sum()),
        "net_uplift": float(full_out.net_uplift.sum()),
        "winner_affected": int(full_out.winner_affected.sum()),
        "loss_reduction": float(full_out.loss_reduction.sum()),
        "losses_eliminated": int(full_out.loss_eliminated.sum()),
    }
    pd.DataFrame([full_summary]).to_csv(OUT / "selected_full_summary.csv", index=False)

    safe = grid[(grid.dev_winner_affected == 0) & (grid.val_winner_affected == 0)].copy()
    safe = safe.sort_values("val_net_uplift", ascending=False)
    safe.to_csv(OUT / "zero_winner_both_periods.csv", index=False)

    report = f"""# Phase 18 Conditional Stop Refinement

Selected by development only: **{name}**

Development:
- net uplift: ₹{s.dev_net_uplift:,.2f}
- winner affected: {int(s.dev_winner_affected)}
- loss reduction: ₹{s.dev_loss_reduction:,.2f}

Validation:
- net uplift: ₹{s.val_net_uplift:,.2f}
- winner affected: {int(s.val_winner_affected)}
- loss reduction: ₹{s.val_loss_reduction:,.2f}

Full:
- net uplift: ₹{full_summary["net_uplift"]:,.2f}
- winner affected: {full_summary["winner_affected"]}
- loss reduction: ₹{full_summary["loss_reduction"]:,.2f}
- losses eliminated: {full_summary["losses_eliminated"]}

Interpretation: this refinement tests whether expiry-day negative MTM should be stopped only when the trade has also failed to generate sufficient earlier MFE, reducing the chance of cutting late-recovering trades.
"""
    (OUT / "CONDITIONAL_STOP_REPORT.md").write_text(report, encoding="utf-8")
    print(grid.sort_values(["dev_winner_affected", "dev_net_uplift"], ascending=[True, False]).head(40).to_string(index=False))
    print("SELECTED", name)
    print("SAFE BOTH", safe.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
