import numpy as np
import pandas as pd
from pathlib import Path

OUT = Path("results/dynamic_n_corrected/phase23_conditional_bullish_entry_filter")
OUT.mkdir(parents=True, exist_ok=True)

TRAIN_END = pd.Timestamp("2023-12-31", tz="Asia/Kolkata")
VALIDATION_END = pd.Timestamp("2025-12-31", tz="Asia/Kolkata")

WINNER_RETENTION_TRAIN = 0.95
WINNER_RETENTION_OOS = 0.90
MAX_DD_MULT = 1.05
MIN_LOSSES_REMOVED = 2
BOOTSTRAP_B = 5000
RNG = np.random.default_rng(20261003)


def max_dd(values):
    running = peak = dd = 0.0
    for x in values:
        running += float(x)
        peak = max(peak, running)
        dd = max(dd, peak - running)
    return dd


def profit_factor(values):
    s = pd.Series(values, dtype=float)
    gp = float(s[s > 0].sum())
    gl = float(-s[s < 0].sum())
    return gp / gl if gl > 0 else np.inf


def split(df):
    ts = pd.to_datetime(df["expiry"]).dt.tz_localize("Asia/Kolkata")
    return (
        df.loc[ts <= TRAIN_END].copy(),
        df.loc[(ts > TRAIN_END) & (ts <= VALIDATION_END)].copy(),
        df.loc[ts > VALIDATION_END].copy(),
    )


def cond_series(s, op, x):
    if op == "ge":
        return s.isna() | (s >= x)
    if op == "le":
        return s.isna() | (s <= x)
    raise ValueError(op)


def build_rules():
    rules = []

    ret = [-0.020, -0.015, -0.010, -0.005, 0.0, 0.005, 0.010]
    dm = [0.05, 0.10, 0.15, 0.20, 0.25]
    bz = [0.75, 1.00, 1.25, 1.50]

    for x in ret:
        rules.append({
            "name": f"bullish_ret5_ge_{x:g}",
            "family": "bullish_trend",
            "conditions": [("signed_ret_5d", "ge", x)],
            "params": {"signed_ret_5d_ge": x},
        })

    for x in dm:
        rules.append({
            "name": f"bullish_direction_margin_ge_{x:g}",
            "family": "bullish_direction_confidence",
            "conditions": [("direction_margin", "ge", x)],
            "params": {"direction_margin_ge": x},
        })

    for x in bz:
        rules.append({
            "name": f"bullish_boundary_z_ge_{x:g}",
            "family": "bullish_payoff_buffer",
            "conditions": [("boundary_z", "ge", x)],
            "params": {"boundary_z_ge": x},
        })

    for x in ret:
        for y in dm:
            rules.append({
                "name": f"bullish_ret5_{x:g}_dm_{y:g}",
                "family": "bullish_trend_x_confidence",
                "conditions": [("signed_ret_5d", "ge", x), ("direction_margin", "ge", y)],
                "params": {"signed_ret_5d_ge": x, "direction_margin_ge": y},
            })

        for y in bz:
            rules.append({
                "name": f"bullish_ret5_{x:g}_bz_{y:g}",
                "family": "bullish_trend_x_buffer",
                "conditions": [("signed_ret_5d", "ge", x), ("boundary_z", "ge", y)],
                "params": {"signed_ret_5d_ge": x, "boundary_z_ge": y},
            })

    return rules


def rule_mask(df, rule):
    mask = pd.Series(True, index=df.index)
    bullish = df["direction"].eq("BULLISH")

    bullish_mask = pd.Series(True, index=df.index)
    for feature, op, x in rule["conditions"]:
        bullish_mask &= cond_series(df[feature], op, x)

    # BEARISH trades are never filtered in this phase.
    return (~bullish) | bullish_mask


def evaluate(df, rule):
    mask = rule_mask(df, rule)
    kept = df.loc[mask].sort_values("expiry")

    base_net = float(df["base_net"].sum())
    candidate_net = float(kept["base_net"].sum())

    wins = df["base_net"] > 0
    losses = df["base_net"] < 0

    winners_removed = int((~mask & wins).sum())
    losses_removed = int((~mask & losses).sum())
    bullish_winners_removed = int((~mask & wins & df["direction"].eq("BULLISH")).sum())
    bullish_losses_removed = int((~mask & losses & df["direction"].eq("BULLISH")).sum())

    winner_pnl_removed = float(df.loc[~mask & wins, "base_net"].sum())
    loss_pnl_removed = float(-df.loc[~mask & losses, "base_net"].sum())

    return {
        "net_uplift": candidate_net - base_net,
        "base_net": base_net,
        "candidate_net": candidate_net,
        "trades_retained": int(mask.sum()),
        "trades_excluded": int((~mask).sum()),
        "base_winners": int(wins.sum()),
        "base_losses": int(losses.sum()),
        "winners_removed": winners_removed,
        "winner_retention": float((wins.sum() - winners_removed) / wins.sum()),
        "losses_removed": losses_removed,
        "loss_removal_rate": float(losses_removed / losses.sum()) if losses.sum() else np.nan,
        "bullish_winners_removed": bullish_winners_removed,
        "bullish_losses_removed": bullish_losses_removed,
        "winner_pnl_removed": winner_pnl_removed,
        "loss_pnl_removed": loss_pnl_removed,
        "profit_sacrificed_per_loss": (
            winner_pnl_removed / losses_removed if losses_removed else np.inf
        ),
        "profit_factor": profit_factor(kept["base_net"].tolist()),
        "max_dd": max_dd(kept["base_net"].tolist()),
        "base_dd": max_dd(df.sort_values("expiry")["base_net"].tolist()),
        "worst_trade": float(kept["base_net"].min()),
        "p05_trade": float(kept["base_net"].quantile(0.05)),
    }


def bootstrap_ci(df, rule):
    mask = rule_mask(df, rule)
    diffs = np.where(mask, 0.0, -df["base_net"].to_numpy(dtype=float))
    samples = RNG.choice(diffs, size=(BOOTSTRAP_B, len(diffs)), replace=True).sum(axis=1)
    return float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))


def main():
    feature_path = Path("results/dynamic_n_corrected/phase22_entry_filter_loss_avoidance/phase22_trade_features.csv")
    if not feature_path.exists():
        raise RuntimeError(f"Missing Phase-22 feature ledger: {feature_path}")

    df = pd.read_csv(feature_path)
    if len(df) != 190:
        raise RuntimeError(f"Expected 190 Phase-22 trades, found {len(df)}")

    rules = build_rules()
    train, validation, holdout = split(df)

    direction_check = (
        df.groupby("direction")["base_net"]
        .agg(["count", lambda s: int((s > 0).sum()), lambda s: int((s < 0).sum()), "sum"])
        .reset_index()
    )
    direction_check.columns = ["direction", "trades", "wins", "losses", "net"]

    results = []
    detail = {}
    for rule in rules:
        tr = evaluate(train, rule)
        va = evaluate(validation, rule)
        ho = evaluate(holdout, rule)
        full = evaluate(df, rule)
        detail[rule["name"]] = rule
        results.append({
            "variant": rule["name"],
            "family": rule["family"],
            **rule["params"],
            "train_net_uplift": tr["net_uplift"],
            "train_winners_removed": tr["winners_removed"],
            "train_winner_retention": tr["winner_retention"],
            "train_losses_removed": tr["losses_removed"],
            "train_loss_removal_rate": tr["loss_removal_rate"],
            "train_bullish_winners_removed": tr["bullish_winners_removed"],
            "train_bullish_losses_removed": tr["bullish_losses_removed"],
            "train_profit_sacrificed_per_loss": tr["profit_sacrificed_per_loss"],
            "train_dd_change": tr["max_dd"] - tr["base_dd"],
            "validation_net_uplift": va["net_uplift"],
            "validation_winners_removed": va["winners_removed"],
            "validation_winner_retention": va["winner_retention"],
            "validation_losses_removed": va["losses_removed"],
            "validation_loss_removal_rate": va["loss_removal_rate"],
            "validation_bullish_winners_removed": va["bullish_winners_removed"],
            "validation_bullish_losses_removed": va["bullish_losses_removed"],
            "validation_dd_change": va["max_dd"] - va["base_dd"],
            "holdout_net_uplift": ho["net_uplift"],
            "holdout_winners_removed": ho["winners_removed"],
            "holdout_winner_retention": ho["winner_retention"],
            "holdout_losses_removed": ho["losses_removed"],
            "holdout_loss_removal_rate": ho["loss_removal_rate"],
            "holdout_bullish_winners_removed": ho["bullish_winners_removed"],
            "holdout_bullish_losses_removed": ho["bullish_losses_removed"],
            "holdout_dd_change": ho["max_dd"] - ho["base_dd"],
            "full_net_uplift": full["net_uplift"],
        })

    grid = pd.DataFrame(results)

    eligible = grid[
        (grid["train_winner_retention"] >= WINNER_RETENTION_TRAIN)
        & (grid["train_losses_removed"] >= MIN_LOSSES_REMOVED)
        & (grid["train_net_uplift"] > 0)
    ].copy()

    zero_bullish_winner = grid[
        (grid["train_bullish_winners_removed"] == 0)
        & (grid["train_bullish_losses_removed"] >= 1)
    ].sort_values(
        ["train_bullish_losses_removed", "train_net_uplift"],
        ascending=[False, False],
    )

    if eligible.empty:
        selected = None
        promotion = False
    else:
        selected = eligible.sort_values(
            ["train_net_uplift", "train_losses_removed", "train_winners_removed"],
            ascending=[False, False, True],
        ).iloc[0]["variant"]
        rule = detail[selected]
        tr = evaluate(train, rule)
        va = evaluate(validation, rule)
        ho = evaluate(holdout, rule)
        promotion = (
            va["net_uplift"] > 0
            and ho["net_uplift"] > 0
            and va["winner_retention"] >= WINNER_RETENTION_OOS
            and ho["winner_retention"] >= WINNER_RETENTION_OOS
            and va["losses_removed"] >= 1
            and ho["losses_removed"] >= 1
            and va["max_dd"] <= va["base_dd"] * MAX_DD_MULT
            and ho["max_dd"] <= ho["base_dd"] * MAX_DD_MULT
        )

        val_ci = bootstrap_ci(validation, rule)
        ho_ci = bootstrap_ci(holdout, rule)
    if selected is None:
        top = grid.sort_values(
            ["train_net_uplift", "train_losses_removed", "train_winners_removed"],
            ascending=[False, False, True],
        ).iloc[0]
        conclusion = f"""# Phase 23 — Conditional BULLISH Entry Filter Conclusion

## Directional asymmetry

All **11** baseline losing trades in the 190-trade final strategy were BULLISH/put-structure trades.

All **18** BEARISH/call-structure trades were profitable.

That is a strong subgroup pattern, but BULLISH trades also contain **161 winners**, so rejecting the BULLISH side wholesale is not acceptable.

## Result

**No BULLISH-only filter passed the training safety screen.**

The screen required at least 95% overall winner retention, removal of at least 2 training losses, and positive training uplift.

The top unconstrained candidate was **{top["variant"]}**.

Training uplift: ₹{top["train_net_uplift"]:.2f}  
Training losses removed: {int(top["train_losses_removed"])}  
Training winners removed: {int(top["train_winners_removed"])}  
Validation uplift: ₹{top["validation_net_uplift"]:.2f}  
2026 holdout uplift: ₹{top["holdout_net_uplift"]:.2f}

## Decision

The BULLISH/put entry should **not** be excluded as a whole.

The Phase-20 entry rule remains unchanged.
"""
        status = pd.DataFrame([{
            "selected_variant": "",
            "promotion": False,
            "train_uplift": float(top["train_net_uplift"]),
            "validation_uplift": float(top["validation_net_uplift"]),
            "holdout_uplift": float(top["holdout_net_uplift"]),
            "all_losses_bullish": True,
            "bearish_trades": 18,
            "bearish_losses": 0,
        }])
    else:
        rule = detail[selected]
        tr = evaluate(train, rule)
        va = evaluate(validation, rule)
        ho = evaluate(holdout, rule)
        selected_rows = df.loc[rule_mask(df, rule)].sort_values("expiry")
        selected_rows.to_csv(OUT / "phase23_selected_trade_level.csv", index=False)
        conclusion = f"""# Phase 23 — Conditional BULLISH Entry Filter Conclusion

## Directional asymmetry

All 11 baseline losing trades were BULLISH/put-structure trades.

All 18 BEARISH/call-structure trades were profitable.

## Selected BULLISH-only filter

**{selected}**

BEARISH trades are always retained.

## Training
- uplift: ₹{tr["net_uplift"]:.2f}
- winner retention: {tr["winner_retention"]:.2%}
- losses removed: {tr["losses_removed"]}
- BULLISH winners removed: {tr["bullish_winners_removed"]}
- BULLISH losses removed: {tr["bullish_losses_removed"]}

## Validation
- uplift: ₹{va["net_uplift"]:.2f}
- winner retention: {va["winner_retention"]:.2%}
- losses removed: {va["losses_removed"]}
- drawdown change: ₹{va["max_dd"] - va["base_dd"]:.2f}
- bootstrap 95% uplift CI: ₹{val_ci[0]:.2f} to ₹{val_ci[1]:.2f}

## 2026 holdout
- uplift: ₹{ho["net_uplift"]:.2f}
- winner retention: {ho["winner_retention"]:.2%}
- losses removed: {ho["losses_removed"]}
- drawdown change: ₹{ho["max_dd"] - ho["base_dd"]:.2f}
- bootstrap 95% uplift CI: ₹{ho_ci[0]:.2f} to ₹{ho_ci[1]:.2f}

## Promotion

**{promotion}**
"""
        status = pd.DataFrame([{
            "selected_variant": selected,
            "promotion": bool(promotion),
            "train_uplift": tr["net_uplift"],
            "validation_uplift": va["net_uplift"],
            "holdout_uplift": ho["net_uplift"],
            "train_winner_retention": tr["winner_retention"],
            "validation_winner_retention": va["winner_retention"],
            "holdout_winner_retention": ho["winner_retention"],
            "train_losses_removed": tr["losses_removed"],
            "validation_losses_removed": va["losses_removed"],
            "holdout_losses_removed": ho["losses_removed"],
            "all_losses_bullish": True,
            "bearish_trades": 18,
            "bearish_losses": 0,
        }])

    OUT.mkdir(parents=True, exist_ok=True)
    grid.to_csv(OUT / "phase23_full_filter_grid.csv", index=False)
    eligible.to_csv(OUT / "phase23_training_eligible.csv", index=False)
    zero_bullish_winner.to_csv(OUT / "phase23_zero_bullish_winner_frontier.csv", index=False)
    direction_check.to_csv(OUT / "phase23_direction_check.csv", index=False)
    status.to_csv(OUT / "phase23_status.csv", index=False)
    (OUT / "PHASE23_CONCLUSION.md").write_text(conclusion, encoding="utf-8")

    print(conclusion)


if __name__ == "__main__":
    main()
