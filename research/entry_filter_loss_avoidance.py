import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from research.stop_loss_research import build_paths
from research.backtest_dynamic_n_corrected import (
    TZ,
    load,
    normalize,
    prices_at,
    required_strikes,
    exec_px,
    charges,
)

OUT = Path(os.getenv("OUT_DIR", "results/dynamic_n_corrected/phase22_entry_filter_loss_avoidance"))
OUT.mkdir(parents=True, exist_ok=True)

TRAIN_END = pd.Timestamp("2023-12-31", tz=TZ)
VALIDATION_END = pd.Timestamp("2025-12-31", tz=TZ)
HOLDOUT_START = pd.Timestamp("2026-01-01", tz=TZ)

WINNER_RETENTION_CAP_TRAIN = 0.95
WINNER_RETENTION_MIN_OOS = 0.90
MAX_DD_MULT = 1.05
MIN_TRAIN_LOSSES_REMOVED = 2
BOOTSTRAP_B = 5000
RNG = np.random.default_rng(20261003)


def max_dd(values):
    running = 0.0
    peak = 0.0
    dd = 0.0
    for x in values:
        running += float(x)
        peak = max(peak, running)
        dd = max(dd, peak - running)
    return dd


def profit_factor(values):
    s = pd.Series(values, dtype=float)
    gains = float(s[s > 0].sum())
    losses = float(-s[s < 0].sum())
    return gains / losses if losses > 0 else np.inf


def phase19_idx(t):
    expiry_date = pd.Timestamp(t["expiry"], tz=TZ).date()
    for i, p in enumerate(t["path"]):
        ts = pd.Timestamp(p["ts"])
        if (
            ts.date() == expiry_date
            and (ts.hour > 13 or (ts.hour == 13 and ts.minute >= 30))
            and p["gross"] < 0
            and p["mfe"] < 0.50 * t["target"]
        ):
            return i
    return len(t["path"]) - 1


def final_comparator_net(t):
    i = phase19_idx(t)
    p = t["path"][i]
    raw = p["raw_exit"]
    xp = (
        exec_px(raw[0], "sell"),
        exec_px(raw[1], "buy"),
        exec_px(raw[2], "buy"),
    )
    e = pd.Timestamp(t["entry_ts"])
    x = pd.Timestamp(p["ts"])
    oe = [
        (e, "buy", t["entry_exec"][0]),
        (e, "sell", t["entry_exec"][1]),
        (e, "sell", t["entry_exec"][2]),
    ]
    ox = [
        (x, "sell", xp[0]),
        (x, "buy", xp[1]),
        (x, "buy", xp[2]),
    ]
    return float(p["gross"]) - charges(oe, ox, t["lot"])


def load_spot():
    df = load("index/NIFTY.parquet")[["timestamp", "close"]].rename(columns={"close": "spot"})
    df = df.sort_values("timestamp").copy()
    df["date"] = df["timestamp"].dt.normalize()
    daily = df.groupby("date", sort=True)["spot"].last()
    return df, daily


def daily_features(daily, entry_date, entry_spot):
    prior = daily[daily.index < entry_date]
    if len(prior) == 0:
        return {}

    out = {}
    prev1 = float(prior.iloc[-1])
    out["ret_1d"] = float(np.log(entry_spot / prev1))

    for k in (3, 5):
        if len(prior) >= k:
            out[f"ret_{k}d"] = float(np.log(entry_spot / float(prior.iloc[-k])))
        else:
            out[f"ret_{k}d"] = np.nan

    for k in (5, 10, 20):
        closes = prior.iloc[-(k + 1):]
        if len(closes) >= k + 1:
            r = np.log(closes.astype(float)).diff().dropna().to_numpy()
            out[f"rv_{k}d"] = float(np.std(r, ddof=1) * np.sqrt(252)) if len(r) >= 2 else np.nan
        else:
            out[f"rv_{k}d"] = np.nan

    return out


def build_features(trades, spot_df, daily):
    option_cache = {}
    rows = []
    alignment_errors = []

    for t in trades:
        expiry = t["expiry"]
        entry_ts = pd.Timestamp(t["entry_ts"])
        entry_date = entry_ts.normalize()
        try:
            if expiry not in option_cache:
                option_cache[expiry] = normalize(load(f"options/NIFTY/{expiry}.parquet"))
            odf = option_cache[expiry]
        except Exception as exc:
            alignment_errors.append({"expiry": expiry, "error": repr(exc)})
            continue

        sr = spot_df[spot_df["timestamp"] == entry_ts]
        if sr.empty:
            alignment_errors.append({"expiry": expiry, "error": "missing exact entry spot"})
            continue
        spot_entry = float(sr.iloc[0]["spot"])

        n = int(t["n_selected"])
        typ = t["option_type"]
        selected_k = float(t["strikes"][0])
        atm = selected_k - n * 50 if typ == "CE" else selected_k + n * 50

        call_strikes = required_strikes(atm, "CE")
        put_strikes = required_strikes(atm, "PE")
        call_px = prices_at(odf, entry_ts, "CE", tuple(call_strikes.values()))
        put_px = prices_at(odf, entry_ts, "PE", tuple(put_strikes.values()))

        if any(call_px.get(call_strikes[i]) is None for i in (6, 7, 8)) or any(
            put_px.get(put_strikes[i]) is None for i in (6, 7, 8)
        ):
            alignment_errors.append({"expiry": expiry, "error": "missing exact entry OTM6..8 direction prices"})
            continue

        x_call = float(call_px[call_strikes[8]] + call_px[call_strikes[7]] - call_px[call_strikes[6]])
        x_put = float(put_px[put_strikes[8]] + put_px[put_strikes[7]] - put_px[put_strikes[6]])

        selected_x = x_call if t["direction"] == "BEARISH" else x_put
        opposite_x = x_put if t["direction"] == "BEARISH" else x_call

        side_prices = call_px if typ == "CE" else put_px
        side_strikes = call_strikes if typ == "CE" else put_strikes
        if any(side_prices.get(side_strikes[i]) is None for i in range(6, 18)):
            alignment_errors.append({"expiry": expiry, "error": "missing exact selected-side OTM6..17 prices"})
            continue

        scores = []
        for j in range(6, 16):
            scores.append(
                float(
                    side_prices[side_strikes[j + 2]]
                    + side_prices[side_strikes[j + 1]]
                    - side_prices[side_strikes[j]]
                )
            )
        scores = np.asarray(scores, dtype=float)
        x_max = float(np.max(scores))
        x_sorted = np.sort(scores)[::-1]
        x_second = float(x_sorted[1]) if len(x_sorted) > 1 else np.nan

        ep = (
            exec_px(float(t["raw_entry"][0]), "buy"),
            exec_px(float(t["raw_entry"][1]), "sell"),
            exec_px(float(t["raw_entry"][2]), "sell"),
        )
        credit = float(ep[1] + ep[2] - ep[0])

        k_n, k_n1, k_n2 = map(float, t["strikes"])
        if typ == "CE":
            boundary = k_n1 + k_n2 - k_n + credit
            boundary_distance = boundary - spot_entry
        else:
            boundary = k_n1 + k_n2 - k_n - credit
            boundary_distance = spot_entry - boundary

        df = daily_features(daily, entry_date, spot_entry)
        rv10 = df.get("rv_10d", np.nan)
        expected_move_4d = (
            spot_entry * rv10 * np.sqrt(4.0 / 252.0)
            if np.isfinite(rv10) and rv10 > 0 else np.nan
        )

        direction_sign = 1.0 if t["direction"] == "BULLISH" else -1.0
        signed_ret5 = direction_sign * df.get("ret_5d", np.nan)

        denom = abs(selected_x) + abs(opposite_x)
        direction_margin = (
            (selected_x - opposite_x) / denom if denom > 0 else np.nan
        )
        direction_ratio = (
            selected_x / opposite_x
            if np.isfinite(opposite_x) and opposite_x > 0
            else np.nan
        )
        long_premium = float(t["raw_entry"][0])
        x_to_long = selected_x / long_premium if long_premium > 0 else np.nan
        x_to_max = selected_x / x_max if x_max > 0 else np.nan
        boundary_z = (
            boundary_distance / expected_move_4d
            if np.isfinite(expected_move_4d) and expected_move_4d > 0
            else np.nan
        )

        base_net = final_comparator_net(t)

        rows.append({
            "expiry": expiry,
            "entry_ts": entry_ts,
            "spot_entry": spot_entry,
            "direction": t["direction"],
            "option_type": typ,
            "n_selected": n,
            "x_call": x_call,
            "x_put": x_put,
            "selected_x": selected_x,
            "opposite_x": opposite_x,
            "x_max": x_max,
            "x_second": x_second,
            "x_selected_xmax_ratio": x_to_max,
            "direction_margin": direction_margin,
            "direction_ratio": direction_ratio,
            "long_premium": long_premium,
            "x_to_long_premium": x_to_long,
            "entry_credit": credit,
            "boundary": boundary,
            "boundary_distance": boundary_distance,
            "expected_move_4d": expected_move_4d,
            "boundary_z": boundary_z,
            "ret_1d": df.get("ret_1d", np.nan),
            "ret_3d": df.get("ret_3d", np.nan),
            "ret_5d": df.get("ret_5d", np.nan),
            "signed_ret_5d": signed_ret5,
            "rv_5d": df.get("rv_5d", np.nan),
            "rv_10d": df.get("rv_10d", np.nan),
            "rv_20d": df.get("rv_20d", np.nan),
            "target": float(t["target"]),
            "lot": float(t["lot"]),
            "base_net": base_net,
        })

    out = pd.DataFrame(rows)
    out["base_positive"] = out["base_net"] > 0
    out["base_negative"] = out["base_net"] < 0
    return out, alignment_errors


def apply_condition(feature, op, threshold):
    if op == "ge":
        return feature.isna() | (feature >= threshold)
    if op == "le":
        return feature.isna() | (feature <= threshold)
    if op == "eq":
        return feature == threshold
    return pd.Series(True, index=feature.index)


def build_rules(train_df):
    rules = []

    def add(name, family, conditions, params):
        rules.append({"name": name, "family": family, "conditions": conditions, "params": params})

    for x in [0, 50, 100, 150, 200, 300, 400]:
        add(
            f"boundary_dist_ge_{x:g}",
            "boundary_distance",
            [("boundary_distance", "ge", x)],
            {"threshold": x},
        )

    for x in [0.50, 0.75, 1.00, 1.25, 1.50, 2.00]:
        add(
            f"boundary_z_ge_{x:g}",
            "boundary_z",
            [("boundary_z", "ge", x)],
            {"threshold": x},
        )

    for x in [0.05, 0.10, 0.15, 0.20, 0.30]:
        add(
            f"direction_margin_ge_{x:g}",
            "direction_margin",
            [("direction_margin", "ge", x)],
            {"threshold": x},
        )

    for x in [1.05, 1.10, 1.20, 1.30, 1.50]:
        add(
            f"direction_ratio_ge_{x:g}",
            "direction_ratio",
            [("direction_ratio", "ge", x)],
            {"threshold": x},
        )

    for x in [1, 2, 3, 5, 8]:
        add(
            f"selected_x_ge_{x:g}",
            "selected_x",
            [("selected_x", "ge", x)],
            {"threshold": x},
        )

    for x in [0.10, 0.20, 0.30, 0.40, 0.50, 0.75]:
        add(
            f"x_to_long_ge_{x:g}",
            "x_to_long_premium",
            [("x_to_long_premium", "ge", x)],
            {"threshold": x},
        )

    for x in [0.97, 0.98, 0.99, 1.00]:
        add(
            f"x_selected_xmax_ge_{x:g}",
            "x_selected_xmax_ratio",
            [("x_selected_xmax_ratio", "ge", x)],
            {"threshold": x},
        )

    add("n_selected_eq_6", "n_selected", [("n_selected", "eq", 6)], {"value": 6})
    add("n_selected_le_7", "n_selected", [("n_selected", "le", 7)], {"value": 7})

    for sign_name, op, vals in [
        ("ge", "ge", [0.0, 0.005, 0.010, 0.015]),
        ("le", "le", [0.0, -0.005, -0.010, -0.015]),
    ]:
        for x in vals:
            add(
                f"signed_ret5_{sign_name}_{x:g}",
                "signed_ret5",
                [("signed_ret_5d", op, x)],
                {"threshold": x, "op": op},
            )

    for col in ["rv_5d", "rv_10d", "rv_20d"]:
        vals = train_df[col].dropna().quantile([0.20, 0.40, 0.60, 0.80]).to_dict()
        for q, x in vals.items():
            add(
                f"{col}_le_q{int(q*100)}",
                "volatility_low",
                [(col, "le", float(x))],
                {"quantile": q, "threshold": float(x)},
            )
            add(
                f"{col}_ge_q{int(q*100)}",
                "volatility_high",
                [(col, "ge", float(x))],
                {"quantile": q, "threshold": float(x)},
            )

    # Controlled two-feature combinations.
    boundary_z = [0.75, 1.00, 1.25, 1.50, 2.00]
    direction_margin = [0.05, 0.10, 0.15, 0.20, 0.30]
    x_to_long = [0.20, 0.30, 0.40, 0.50, 0.75]
    signed_ge = [0.0, 0.005, 0.010]
    signed_le = [0.0, -0.005, -0.010]

    for bz in boundary_z:
        for dm in direction_margin:
            add(
                f"combo_bz{bz:g}_dm{dm:g}",
                "combo_boundary_direction",
                [("boundary_z", "ge", bz), ("direction_margin", "ge", dm)],
                {"boundary_z": bz, "direction_margin": dm},
            )
        for sr in signed_ge:
            add(
                f"combo_bz{bz:g}_srge{sr:g}",
                "combo_boundary_trend",
                [("boundary_z", "ge", bz), ("signed_ret_5d", "ge", sr)],
                {"boundary_z": bz, "signed_ret_5d_ge": sr},
            )
        for sr in signed_le:
            add(
                f"combo_bz{bz:g}_srle{sr:g}",
                "combo_boundary_trend",
                [("boundary_z", "ge", bz), ("signed_ret_5d", "le", sr)],
                {"boundary_z": bz, "signed_ret_5d_le": sr},
            )
        for xr in x_to_long:
            add(
                f"combo_bz{bz:g}_xlp{xr:g}",
                "combo_boundary_structure",
                [("boundary_z", "ge", bz), ("x_to_long_premium", "ge", xr)],
                {"boundary_z": bz, "x_to_long_premium": xr},
            )

    for dm in direction_margin:
        for sr in signed_ge:
            add(
                f"combo_dm{dm:g}_srge{sr:g}",
                "combo_direction_trend",
                [("direction_margin", "ge", dm), ("signed_ret_5d", "ge", sr)],
                {"direction_margin": dm, "signed_ret_5d_ge": sr},
            )
        for sr in signed_le:
            add(
                f"combo_dm{dm:g}_srle{sr:g}",
                "combo_direction_trend",
                [("direction_margin", "ge", dm), ("signed_ret_5d", "le", sr)],
                {"direction_margin": dm, "signed_ret_5d_le": sr},
            )

    return rules


def evaluate_rule(df, rule):
    mask = pd.Series(True, index=df.index)
    for feature, op, threshold in rule["conditions"]:
        mask &= apply_condition(df[feature], op, threshold)

    kept = df.loc[mask].sort_values("expiry")
    excluded = df.loc[~mask].sort_values("expiry")

    base_total = float(df["base_net"].sum())
    candidate_total = float(kept["base_net"].sum())
    uplift = candidate_total - base_total

    base_wins = int(df["base_positive"].sum())
    base_losses = int(df["base_negative"].sum())
    winners_removed = int((~mask & df["base_positive"]).sum())
    losses_removed = int((~mask & df["base_negative"]).sum())

    winner_pnl_removed = float(df.loc[(~mask) & df["base_positive"], "base_net"].sum())
    loss_pnl_removed = float(-df.loc[(~mask) & df["base_negative"], "base_net"].sum())

    return {
        "candidate_net": candidate_total,
        "base_net": base_total,
        "net_uplift": uplift,
        "trades_retained": int(mask.sum()),
        "trades_excluded": int((~mask).sum()),
        "base_winners": base_wins,
        "base_losses": base_losses,
        "winners_removed": winners_removed,
        "winner_retention": (base_wins - winners_removed) / base_wins if base_wins else np.nan,
        "losses_removed": losses_removed,
        "loss_removal_rate": losses_removed / base_losses if base_losses else np.nan,
        "winner_pnl_removed": winner_pnl_removed,
        "loss_pnl_removed": loss_pnl_removed,
        "loss_capture_per_winner": loss_pnl_removed / winner_pnl_removed if winner_pnl_removed > 0 else np.inf,
        "profit_sacrificed_per_loss_removed": winner_pnl_removed / losses_removed if losses_removed else np.inf,
        "profit_factor": profit_factor(kept["base_net"].tolist()),
        "max_dd": max_dd(kept["base_net"].tolist()),
        "base_dd": max_dd(df.sort_values("expiry")["base_net"].tolist()),
        "worst_trade": float(kept["base_net"].min()) if not kept.empty else np.nan,
        "p05_trade": float(kept["base_net"].quantile(0.05)) if not kept.empty else np.nan,
    }


def bootstrap_uplift(df, mask, B=BOOTSTRAP_B):
    diffs = np.where(mask, 0.0, -df["base_net"].to_numpy(dtype=float))
    n = len(diffs)
    if n == 0:
        return np.nan, np.nan, np.nan
    samples = RNG.choice(diffs, size=(B, n), replace=True).sum(axis=1)
    return (
        float(np.mean(diffs)),
        float(np.quantile(samples, 0.025)),
        float(np.quantile(samples, 0.975)),
    )


def period_split(df):
    ts = pd.to_datetime(df["expiry"]).dt.tz_localize(TZ)
    return (
        df.loc[ts <= TRAIN_END].copy(),
        df.loc[(ts > TRAIN_END) & (ts <= VALIDATION_END)].copy(),
        df.loc[ts >= HOLDOUT_START].copy(),
    )


def rule_mask(df, rule):
    mask = pd.Series(True, index=df.index)
    for feature, op, threshold in rule["conditions"]:
        mask &= apply_condition(df[feature], op, threshold)
    return mask


def main():
    trades = build_paths()
    if not trades:
        raise RuntimeError("No corrected dynamic-n trades reconstructed")

    spot_df, daily = load_spot()
    features, errors = build_features(trades, spot_df, daily)
    if len(features) != len(trades):
        raise RuntimeError(f"Feature build lost trades: {len(features)} of {len(trades)}")

    train, validation, holdout = period_split(features)
    rules = build_rules(train)

    rows = []
    detail = {}

    for rule in rules:
        name = rule["name"]
        train_eval = evaluate_rule(train, rule)
        val_eval = evaluate_rule(validation, rule)
        hold_eval = evaluate_rule(holdout, rule)
        full_eval = evaluate_rule(features, rule)

        rows.append({
            "variant": name,
            "family": rule["family"],
            **rule["params"],
            "train_net_uplift": train_eval["net_uplift"],
            "train_winners_removed": train_eval["winners_removed"],
            "train_winner_retention": train_eval["winner_retention"],
            "train_losses_removed": train_eval["losses_removed"],
            "train_loss_removal_rate": train_eval["loss_removal_rate"],
            "train_loss_pnl_removed": train_eval["loss_pnl_removed"],
            "train_winner_pnl_removed": train_eval["winner_pnl_removed"],
            "train_profit_sacrificed_per_loss": train_eval["profit_sacrificed_per_loss_removed"],
            "train_dd_change": train_eval["max_dd"] - train_eval["base_dd"],
            "validation_net_uplift": val_eval["net_uplift"],
            "validation_winners_removed": val_eval["winners_removed"],
            "validation_winner_retention": val_eval["winner_retention"],
            "validation_losses_removed": val_eval["losses_removed"],
            "validation_loss_removal_rate": val_eval["loss_removal_rate"],
            "validation_dd_change": val_eval["max_dd"] - val_eval["base_dd"],
            "holdout_net_uplift": hold_eval["net_uplift"],
            "holdout_winners_removed": hold_eval["winners_removed"],
            "holdout_winner_retention": hold_eval["winner_retention"],
            "holdout_losses_removed": hold_eval["losses_removed"],
            "holdout_loss_removal_rate": hold_eval["loss_removal_rate"],
            "holdout_dd_change": hold_eval["max_dd"] - hold_eval["base_dd"],
            "full_net_uplift": full_eval["net_uplift"],
        })

        mask_all = rule_mask(features, rule)
        detail[name] = mask_all

    grid = pd.DataFrame(rows)

    eligible = grid[
        (grid["train_winner_retention"] >= WINNER_RETENTION_CAP_TRAIN)
        & (grid["train_losses_removed"] >= MIN_TRAIN_LOSSES_REMOVED)
        & (grid["train_net_uplift"] > 0)
    ].copy()

    safe_zero_winner = grid[
        (grid["train_winners_removed"] == 0)
        & (grid["train_losses_removed"] >= 1)
    ].sort_values(
        ["train_losses_removed", "train_net_uplift"],
        ascending=[False, False],
    )

    if eligible.empty:
        selected_name = None
        selected_rule = None
        promotion = False
        selected_stats = None
    else:
        selected_row = eligible.sort_values(
            ["train_net_uplift", "train_losses_removed", "train_winners_removed"],
            ascending=[False, False, True],
        ).iloc[0]
        selected_name = selected_row["variant"]
        selected_rule = next(r for r in rules if r["name"] == selected_name)
        selected_mask = detail[selected_name]

        tr = features.loc[selected_mask & features.index.isin(train.index)]
        va = features.loc[selected_mask & features.index.isin(validation.index)]
        ho = features.loc[selected_mask & features.index.isin(holdout.index)]

        full_eval = evaluate_rule(features, selected_rule)
        val_eval = evaluate_rule(validation, selected_rule)
        hold_eval = evaluate_rule(holdout, selected_rule)
        train_eval = evaluate_rule(train, selected_rule)

        promotion = (
            val_eval["net_uplift"] > 0
            and hold_eval["net_uplift"] > 0
            and val_eval["winner_retention"] >= WINNER_RETENTION_MIN_OOS
            and hold_eval["winner_retention"] >= WINNER_RETENTION_MIN_OOS
            and val_eval["losses_removed"] >= 1
            and hold_eval["losses_removed"] >= 1
            and val_eval["max_dd"] <= val_eval["base_dd"] * MAX_DD_MULT
            and hold_eval["max_dd"] <= hold_eval["base_dd"] * MAX_DD_MULT
        )

        diff_val = np.where(
            rule_mask(validation, selected_rule),
            0.0,
            -validation["base_net"].to_numpy(dtype=float),
        )
        diff_hold = np.where(
            rule_mask(holdout, selected_rule),
            0.0,
            -holdout["base_net"].to_numpy(dtype=float),
        )

        def ci(arr):
            if len(arr) == 0:
                return (np.nan, np.nan)
            samples = RNG.choice(arr, size=(BOOTSTRAP_B, len(arr)), replace=True).sum(axis=1)
            return float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))

        val_ci = ci(diff_val)
        hold_ci = ci(diff_hold)
        selected_stats = {
            "train": train_eval,
            "validation": val_eval,
            "holdout": hold_eval,
            "full": full_eval,
            "validation_uplift_ci_low": val_ci[0],
            "validation_uplift_ci_high": val_ci[1],
            "holdout_uplift_ci_low": hold_ci[0],
            "holdout_uplift_ci_high": hold_ci[1],
        }

    features.sort_values("expiry").to_csv(OUT / "phase22_trade_features.csv", index=False)
    grid.to_csv(OUT / "phase22_full_filter_grid.csv", index=False)
    eligible.sort_values(
        ["train_net_uplift", "train_losses_removed", "train_winners_removed"],
        ascending=[False, False, True],
    ).to_csv(OUT / "phase22_training_eligible.csv", index=False)
    safe_zero_winner.to_csv(OUT / "phase22_zero_winner_frontier.csv", index=False)

    if selected_name is not None:
        selected_features = features.loc[detail[selected_name]].copy()
        selected_features.sort_values("expiry").to_csv(
            OUT / "phase22_selected_filter_trade_level.csv", index=False
        )

    if errors:
        pd.DataFrame(errors).to_csv(OUT / "data_alignment_errors.csv", index=False)

    if selected_name is None:
        top = grid.sort_values(
            ["train_net_uplift", "train_losses_removed", "train_winners_removed"],
            ascending=[False, False, True],
        ).iloc[0]
        conclusion = f"""# Phase 22 — Entry Filter Research Conclusion

## Result

**No candidate passed the pre-registered training safety screen.**

The screen required at least 95% winner retention, removal of at least 2 training losses and positive training net-P&L uplift.

The top unconstrained training candidate was **{top["variant"]}**, but it is diagnostic only and is not promoted.

The original Phase-20 entry rule therefore remains unchanged.

## Top diagnostic
- Training uplift: ₹{top["train_net_uplift"]:.2f}
- Training winners removed: {int(top["train_winners_removed"])}
- Training losses removed: {int(top["train_losses_removed"])}
- Validation uplift: ₹{top["validation_net_uplift"]:.2f}
- 2026 holdout uplift: ₹{top["holdout_net_uplift"]:.2f}
"""
        status = {
            "selected_variant": "",
            "promotion": False,
            "train_uplift": float(top["train_net_uplift"]),
            "validation_uplift": float(top["validation_net_uplift"]),
            "holdout_uplift": float(top["holdout_net_uplift"]),
        }
    else:
        s = selected_stats
        conclusion = f"""# Phase 22 — Entry Filter Research Conclusion

## Selected training candidate

**{selected_name}**

## Training
- net uplift: ₹{s["train"]["net_uplift"]:.2f}
- winners removed: {s["train"]["winners_removed"]} / {s["train"]["base_winners"]}
- winner retention: {s["train"]["winner_retention"]:.2%}
- losses removed: {s["train"]["losses_removed"]} / {s["train"]["base_losses"]}
- loss capture: {s["train"]["loss_removal_rate"]:.2%}

## Validation
- net uplift: ₹{s["validation"]["net_uplift"]:.2f}
- winners removed: {s["validation"]["winners_removed"]} / {s["validation"]["base_winners"]}
- winner retention: {s["validation"]["winner_retention"]:.2%}
- losses removed: {s["validation"]["losses_removed"]} / {s["validation"]["base_losses"]}
- loss capture: {s["validation"]["loss_removal_rate"]:.2%}
- maximum drawdown change: ₹{s["validation"]["max_dd"] - s["validation"]["base_dd"]:.2f}
- bootstrap 95% uplift CI: ₹{s["validation_uplift_ci_low"]:.2f} to ₹{s["validation_uplift_ci_high"]:.2f}

## 2026 holdout
- net uplift: ₹{s["holdout"]["net_uplift"]:.2f}
- winners removed: {s["holdout"]["winners_removed"]} / {s["holdout"]["base_winners"]}
- winner retention: {s["holdout"]["winner_retention"]:.2%}
- losses removed: {s["holdout"]["losses_removed"]} / {s["holdout"]["base_losses"]}
- loss capture: {s["holdout"]["loss_removal_rate"]:.2%}
- maximum drawdown change: ₹{s["holdout"]["max_dd"] - s["holdout"]["base_dd"]:.2f}
- bootstrap 95% uplift CI: ₹{s["holdout_uplift_ci_low"]:.2f} to ₹{s["holdout_uplift_ci_high"]:.2f}

## Promotion

**{promotion}**

## Interpretation

The selected rule was chosen using training data only. Validation and 2026 holdout were not used to choose its threshold.

The final strategy entry rule changes only if the promotion screen is passed.
"""
        status = {
            "selected_variant": selected_name,
            "promotion": bool(promotion),
            "train_uplift": float(s["train"]["net_uplift"]),
            "validation_uplift": float(s["validation"]["net_uplift"]),
            "holdout_uplift": float(s["holdout"]["net_uplift"]),
            "train_winner_retention": float(s["train"]["winner_retention"]),
            "validation_winner_retention": float(s["validation"]["winner_retention"]),
            "holdout_winner_retention": float(s["holdout"]["winner_retention"]),
            "train_losses_removed": int(s["train"]["losses_removed"]),
            "validation_losses_removed": int(s["validation"]["losses_removed"]),
            "holdout_losses_removed": int(s["holdout"]["losses_removed"]),
        }

    (OUT / "PHASE22_CONCLUSION.md").write_text(conclusion, encoding="utf-8")
    pd.DataFrame([status]).to_csv(OUT / "phase22_status.csv", index=False)

    print(conclusion)


if __name__ == "__main__":
    main()
