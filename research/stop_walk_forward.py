import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from research.stop_loss_research import (
    TZ,
    END,
    first_confirmed_stop,
    build_paths,
)
from research.backtest_dynamic_n_corrected import exec_px, charges

OUT = Path(os.getenv("OUT_DIR", "results/dynamic_n_corrected/phase19_walk_forward"))
TRAIN_END = pd.Timestamp("2023-12-31", tz=TZ)
VALIDATION_START = pd.Timestamp("2024-01-01", tz=TZ)
VALIDATION_END = pd.Timestamp("2025-12-31", tz=TZ)
HOLDOUT_START = pd.Timestamp("2026-01-01", tz=TZ)

CUTOFFS = [(13, 30), (14, 0), (14, 30), (15, 0)]
MFE_FRACS = [0.0, 0.25, 0.50, 0.75, 1.0]
CONFIRM = [1, 3]


def rules():
    out = []
    for hh, mm in CUTOFFS:
        for mf in MFE_FRACS:
            for c in CONFIRM:
                out.append(
                    {
                        "name": f"mfe_cut_{hh:02d}{mm:02d}_mfe{mf:g}_c{c}",
                        "cutoff": (hh, mm),
                        "mfe_frac": mf,
                        "confirm": c,
                    }
                )
    return out


def stop_idx(t, rule):
    expiry_date = pd.Timestamp(t["expiry"], tz=TZ).date()
    hh, mm = rule["cutoff"]

    def pred(p):
        return (
            p["ts"].date() == expiry_date
            and (
                p["ts"].hour > hh
                or (p["ts"].hour == hh and p["ts"].minute >= mm)
            )
            and p["gross"] < 0
            and p["mfe"] < rule["mfe_frac"] * t["target"]
        )

    return first_confirmed_stop(t["path"], pred, rule["confirm"])


def eval_rule(trades, rule):
    rows = []
    for t in trades:
        idx = stop_idx(t, rule)
        exit_idx = len(t["path"]) - 1 if idx is None else idx
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
                "candidate_net": candidate_net,
                "net_uplift": candidate_net - t["base_net"],
                "base_positive": t["base_net"] > 0,
                "changed_before_base": p["ts"] < t["base_exit_ts"],
                "winner_affected": (t["base_net"] > 0) and (p["ts"] < t["base_exit_ts"]),
                "loss_reduction": max(candidate_net - t["base_net"], 0.0) if t["base_net"] < 0 else 0.0,
                "loss_eliminated": (t["base_net"] < 0) and (candidate_net >= 0),
                "stop_ts": p["ts"],
                "stop_reason": "STOP" if idx is not None else t["base_exit_reason"],
            }
        )
    return pd.DataFrame(rows)


def max_dd(values):
    s = 0.0
    peak = 0.0
    dd = 0.0
    for v in values:
        s += float(v)
        peak = max(peak, s)
        dd = max(dd, peak - s)
    return dd


def summarize(df):
    return {
        "trades": len(df),
        "base_net": float(df.base_net.sum()),
        "candidate_net": float(df.candidate_net.sum()),
        "net_uplift": float(df.net_uplift.sum()),
        "winner_affected": int(df.winner_affected.sum()),
        "loss_reduction": float(df.loss_reduction.sum()),
        "losses_eliminated": int(df.loss_eliminated.sum()),
        "base_dd": max_dd(df.base_net.tolist()),
        "candidate_dd": max_dd(df.candidate_net.tolist()),
        "stops": int(df.changed_before_base.sum()),
    }


def main():
    trades = build_paths()
    train = [t for t in trades if pd.Timestamp(t["expiry"], tz=TZ) <= TRAIN_END]
    validation = [
        t for t in trades
        if VALIDATION_START <= pd.Timestamp(t["expiry"], tz=TZ) <= VALIDATION_END
    ]
    holdout = [t for t in trades if pd.Timestamp(t["expiry"], tz=TZ) >= HOLDOUT_START]

    records = []
    detail = {}
    for rule in rules():
        tr = eval_rule(train, rule)
        va = eval_rule(validation, rule)
        ho = eval_rule(holdout, rule)
        detail[rule["name"]] = {"train": tr, "validation": va, "holdout": ho}
        records.append(
            {
                **rule,
                **{f"train_{k}": v for k, v in summarize(tr).items()},
                **{f"validation_{k}": v for k, v in summarize(va).items()},
                **{f"holdout_{k}": v for k, v in summarize(ho).items()},
            }
        )

    grid = pd.DataFrame(records)
    eligible = grid[grid.train_winner_affected == 0].copy()
    selected = eligible.sort_values(
        ["train_net_uplift", "train_loss_reduction"],
        ascending=[False, False],
    ).iloc[0]
    selected_name = selected["name"]

    OUT.mkdir(parents=True, exist_ok=True)
    grid.to_csv(OUT / "walk_forward_grid.csv", index=False)

    tr = detail[selected_name]["train"]
    va = detail[selected_name]["validation"]
    ho = detail[selected_name]["holdout"]
    full = pd.concat([tr, va, ho], ignore_index=True)

    tr.to_csv(OUT / "selected_train_trade_level.csv", index=False)
    va.to_csv(OUT / "selected_validation_trade_level.csv", index=False)
    ho.to_csv(OUT / "selected_holdout_trade_level.csv", index=False)
    full.to_csv(OUT / "selected_full_trade_level.csv", index=False)

    summary = {
        "selected_rule": selected_name,
        "train": summarize(tr),
        "validation": summarize(va),
        "holdout": summarize(ho),
        "full": summarize(full),
    }
    (OUT / "WALK_FORWARD_SUMMARY.md").write_text(
        f"""# Phase 19 Walk-Forward Stop Confirmation

Selected only on train data (through 2023-12-31): **{selected_name}**

## Train
{summary["train"]}

## Validation (2024-2025)
{summary["validation"]}

## Holdout (2026-01-01 onward)
{summary["holdout"]}

## Full
{summary["full"]}

Promotion condition:
- zero baseline-positive trades affected in validation and holdout;
- positive net-P&L uplift in validation and holdout;
- no materially worse maximum drawdown;
- exact minute-level fees retained.
""",
        encoding="utf-8",
    )
    pd.DataFrame([{
        "selected_rule": selected_name,
        **{f"train_{k}": v for k, v in summary["train"].items()},
        **{f"validation_{k}": v for k, v in summary["validation"].items()},
        **{f"holdout_{k}": v for k, v in summary["holdout"].items()},
        **{f"full_{k}": v for k, v in summary["full"].items()},
    }]).to_csv(OUT / "selected_summary.csv", index=False)

    safe = grid[
        (grid.train_winner_affected == 0)
        & (grid.validation_winner_affected == 0)
        & (grid.holdout_winner_affected == 0)
    ].copy()
    safe.to_csv(OUT / "zero_winner_all_periods.csv", index=False)

    print("SELECTED", selected_name)
    print(pd.DataFrame([summary]).to_string())
    print("\nZERO WINNER ALL PERIODS\n", safe.sort_values("holdout_net_uplift", ascending=False).head(20).to_string(index=False))


if __name__ == "__main__":
    main()
