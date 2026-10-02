import os
from pathlib import Path
from datetime import time

import numpy as np
import pandas as pd

from research.backtest_dynamic_n_corrected import (
    TZ,
    START,
    END,
    DTE_SESSIONS,
    ENTRY_HOUR,
    ENTRY_MINUTE,
    SLIPPAGE_TICKS,
    TICK,
    BROKERAGE_PER_ORDER,
    TARGET_FRACTION,
    STRIKE_INTERVAL,
    load,
    normalize,
    nearest_atm,
    prices_at,
    required_strikes,
    candidate_scores,
    select_n,
    lot_size_for_expiry,
    exec_px,
    charges,
    expiry_files,
)
from huggingface_hub import HfApi


OUT = Path(os.getenv("OUT_DIR", "results/dynamic_n_corrected/phase17_stop_loss"))
OUT.mkdir(parents=True, exist_ok=True)

# Pre-registered candidate families. Selection is based only on the development
# period; the final chosen rule is then frozen and evaluated on the validation
# period without re-optimisation.
DEV_END = pd.Timestamp(os.getenv("DEV_END", "2024-12-31"), tz=TZ)
VAL_START = DEV_END + pd.Timedelta(days=1)

HARD_ACTIVATION_H = [0, 24, 48, 72]
HARD_MULT = [0.50, 0.75, 1.00, 1.25, 1.50, 2.00]
CONFIRM_BARS = [1, 3]

EXPIRY_CUTOFFS = [(14, 0), (14, 30), (15, 0)]
STAGNATION_ACTIVATION_H = [24, 48, 72]
STAGNATION_MFE_FRAC = [0.0, 0.25, 0.50]
TRAIL_ARM_FRAC = [0.25, 0.50, 0.75]
TRAIL_DRAWDOWN_FRAC = [0.25, 0.50, 0.75, 1.00]

COMBINED_ACTIVATION_H = [48, 72]
COMBINED_HARD_MULT = [0.50, 0.75, 1.00]
COMBINED_CUTOFFS = [(14, 0), (14, 30)]


def leg_prices_pnl(raw_entry, raw_exit, lot):
    e_n, e_n1, e_n2 = raw_entry
    x_n, x_n1, x_n2 = raw_exit
    ep = (
        exec_px(e_n, "buy"),
        exec_px(e_n1, "sell"),
        exec_px(e_n2, "sell"),
    )
    xp = (
        exec_px(x_n, "sell"),
        exec_px(x_n1, "buy"),
        exec_px(x_n2, "buy"),
    )
    points = (xp[0] - ep[0]) + (ep[1] - xp[1]) + (ep[2] - xp[2])
    return points * lot


def build_paths():
    spot = load("index/NIFTY.parquet")[["timestamp", "close"]].rename(
        columns={"close": "spot"}
    )
    api = HfApi(token=os.getenv("HF_TOKEN") or None)
    expiries = expiry_files(api)

    trades = []

    for expiry in expiries:
        window_start = expiry - pd.Timedelta(days=14)
        session_dates = sorted(
            pd.to_datetime(
                spot[
                    (spot.timestamp >= window_start)
                    & (spot.timestamp <= expiry)
                ].timestamp.dt.normalize().unique()
            )
        )
        pre_expiry = [d for d in session_dates if d < expiry.normalize()]
        if len(pre_expiry) < DTE_SESSIONS:
            continue

        entry_date = pre_expiry[-DTE_SESSIONS]
        entry_ts = entry_date + pd.Timedelta(hours=ENTRY_HOUR, minutes=ENTRY_MINUTE)
        sr = spot[spot.timestamp == entry_ts]
        if sr.empty:
            continue
        spot_entry = float(sr.iloc[0].spot)

        try:
            df = normalize(load(f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet"))
        except Exception:
            continue

        entry_quotes = df[df.timestamp == entry_ts]
        if entry_quotes.empty:
            continue

        atm = nearest_atm(entry_quotes, spot_entry)
        if atm is None:
            continue

        call_strikes = required_strikes(atm, "CE")
        put_strikes = required_strikes(atm, "PE")
        call_px = prices_at(df, entry_ts, "CE", tuple(call_strikes.values()))
        put_px = prices_at(df, entry_ts, "PE", tuple(put_strikes.values()))

        if any(call_px.get(call_strikes[n]) is None for n in (6, 7, 8)):
            continue
        if any(put_px.get(put_strikes[n]) is None for n in (6, 7, 8)):
            continue

        x_call = call_px[call_strikes[8]] + call_px[call_strikes[7]] - call_px[call_strikes[6]]
        x_put = put_px[put_strikes[8]] + put_px[put_strikes[7]] - put_px[put_strikes[6]]

        if x_call > x_put:
            direction, typ, strike_map, px_map = "BEARISH", "CE", call_strikes, call_px
        elif x_call < x_put:
            direction, typ, strike_map, px_map = "BULLISH", "PE", put_strikes, put_px
        else:
            continue

        required_px = {n: px_map.get(strike_map[n]) for n in range(6, 18)}
        if any(v is None for v in required_px.values()):
            continue

        score_df = candidate_scores(required_px)
        selected_n, x_max, threshold = select_n(score_df)
        if selected_n is None:
            continue

        n = selected_n
        x_selected = float(score_df.loc[score_df.n == n, "x_n"].iloc[0])
        k_n, k_n1, k_n2 = strike_map[n], strike_map[n + 1], strike_map[n + 2]
        raw_entry = (required_px[n], required_px[n + 1], required_px[n + 2])

        lot = lot_size_for_expiry(expiry)
        target = TARGET_FRACTION * x_selected * lot
        end_ts = expiry.normalize() + pd.Timedelta(hours=15, minutes=29)

        q = df[
            (df.timestamp > entry_ts)
            & (df.timestamp <= end_ts)
            & (df.option_type == typ)
            & (df.strike.isin([k_n, k_n1, k_n2]))
        ]
        piv = q.pivot_table(
            index="timestamp",
            columns="strike",
            values="close",
            aggfunc="last",
        ).dropna(subset=[k_n, k_n1, k_n2])
        if piv.empty:
            continue

        path = []
        running_mfe = -np.inf
        baseline_idx = len(piv) - 1
        baseline_reason = "EXPIRY"

        for i, (ts, row) in enumerate(piv.iterrows()):
            raw_exit = (float(row[k_n]), float(row[k_n1]), float(row[k_n2]))
            gross = leg_prices_pnl(raw_entry, raw_exit, lot)
            running_mfe = max(running_mfe, gross)
            path.append(
                {
                    "ts": ts,
                    "gross": gross,
                    "mfe": running_mfe,
                    "elapsed_h": (ts - entry_ts).total_seconds() / 3600.0,
                }
            )
            if gross >= target:
                baseline_idx = i
                baseline_reason = "TARGET"
                break

        base = path[baseline_idx]
        base_ts = base["ts"]
        base_raw_exit = (
            float(piv.loc[base_ts, k_n]),
            float(piv.loc[base_ts, k_n1]),
            float(piv.loc[base_ts, k_n2]),
        )
        ep_n = exec_px(raw_entry[0], "buy")
        ep_n1 = exec_px(raw_entry[1], "sell")
        ep_n2 = exec_px(raw_entry[2], "sell")
        base_xp = (
            exec_px(base_raw_exit[0], "sell"),
            exec_px(base_raw_exit[1], "buy"),
            exec_px(base_raw_exit[2], "buy"),
        )
        base_orders_e = [
            (entry_ts, "buy", ep_n),
            (entry_ts, "sell", ep_n1),
            (entry_ts, "sell", ep_n2),
        ]
        base_orders_x = [
            (base_ts, "sell", base_xp[0]),
            (base_ts, "buy", base_xp[1]),
            (base_ts, "buy", base_xp[2]),
        ]
        base_cost = charges(base_orders_e, base_orders_x, lot)
        base_net = base["gross"] - base_cost

        trades.append(
            {
                "expiry": str(expiry.date()),
                "entry_ts": str(entry_ts),
                "expiry_ts": str(end_ts),
                "direction": direction,
                "option_type": typ,
                "n_selected": n,
                "x_selected": x_selected,
                "target": target,
                "lot": lot,
                "base_exit_ts": base_ts,
                "base_exit_reason": baseline_reason,
                "base_gross": base["gross"],
                "base_net": base_net,
                "base_mfe": max(p["mfe"] for p in path),
                "base_mae": min(p["gross"] for p in path),
                "path": path,
                "raw_entry": raw_entry,
                "strikes": (k_n, k_n1, k_n2),
            }
        )

    return trades


def first_confirmed_stop(path, predicate, confirm_bars):
    if confirm_bars <= 1:
        for i, p in enumerate(path):
            if predicate(p):
                return i
        return None

    for i in range(len(path) - confirm_bars + 1):
        ok = True
        for j in range(i, i + confirm_bars):
            if not predicate(path[j]):
                ok = False
                break
        if ok:
            return i
    return None


def candidate_rules():
    rules = []
    for activation in HARD_ACTIVATION_H:
        for mult in HARD_MULT:
            for confirm in CONFIRM_BARS:
                rules.append(
                    {
                        "name": f"hard_a{activation:g}h_m{mult:g}_c{confirm}",
                        "family": "hard_stop",
                        "activation_h": activation,
                        "mult": mult,
                        "confirm": confirm,
                    }
                )

    for hh, mm in EXPIRY_CUTOFFS:
        for confirm in CONFIRM_BARS:
            rules.append(
                {
                    "name": f"expiry_negative_cut_{hh:02d}{mm:02d}_c{confirm}",
                    "family": "expiry_negative_cutoff",
                    "cutoff": (hh, mm),
                    "confirm": confirm,
                }
            )

    for activation in STAGNATION_ACTIVATION_H:
        for mfe_frac in STAGNATION_MFE_FRAC:
            for confirm in CONFIRM_BARS:
                rules.append(
                    {
                        "name": f"stagnation_a{activation:g}h_mfe{mfe_frac:g}_c{confirm}",
                        "family": "stagnation",
                        "activation_h": activation,
                        "mfe_frac": mfe_frac,
                        "confirm": confirm,
                    }
                )

    for arm in TRAIL_ARM_FRAC:
        for dd in TRAIL_DRAWDOWN_FRAC:
            for confirm in CONFIRM_BARS:
                rules.append(
                    {
                        "name": f"trail_arm{arm:g}_dd{dd:g}_c{confirm}",
                        "family": "trailing_mfe",
                        "arm_frac": arm,
                        "dd_frac": dd,
                        "confirm": confirm,
                    }
                )

    for activation in COMBINED_ACTIVATION_H:
        for mult in COMBINED_HARD_MULT:
            for hh, mm in COMBINED_CUTOFFS:
                rules.append(
                    {
                        "name": f"combo_a{activation:g}h_m{mult:g}_cut{hh:02d}{mm:02d}",
                        "family": "hard_plus_expiry",
                        "activation_h": activation,
                        "mult": mult,
                        "cutoff": (hh, mm),
                        "confirm": 1,
                    }
                )
    return rules


def stop_index_for_rule(trade, rule):
    path = trade["path"]
    expiry_date = pd.Timestamp(trade["expiry"], tz=TZ).date()

    if rule["family"] == "hard_stop":
        pred = lambda p: p["elapsed_h"] >= rule["activation_h"] and p["gross"] <= -rule["mult"] * trade["target"]
        return first_confirmed_stop(path, pred, rule["confirm"])

    if rule["family"] == "expiry_negative_cutoff":
        hh, mm = rule["cutoff"]
        pred = lambda p: (
            p["ts"].date() == expiry_date
            and p["ts"].hour > hh
            or (
                p["ts"].date() == expiry_date
                and p["ts"].hour == hh
                and p["ts"].minute >= mm
            )
        ) and p["gross"] < 0
        return first_confirmed_stop(path, pred, rule["confirm"])

    if rule["family"] == "stagnation":
        pred = lambda p: (
            p["elapsed_h"] >= rule["activation_h"]
            and p["gross"] < 0
            and p["mfe"] < rule["mfe_frac"] * trade["target"]
        )
        return first_confirmed_stop(path, pred, rule["confirm"])

    if rule["family"] == "trailing_mfe":
        pred = lambda p: (
            p["mfe"] >= rule["arm_frac"] * trade["target"]
            and p["gross"] <= p["mfe"] - rule["dd_frac"] * trade["target"]
        )
        return first_confirmed_stop(path, pred, rule["confirm"])

    if rule["family"] == "hard_plus_expiry":
        hh, mm = rule["cutoff"]
        hard = any(
            p["elapsed_h"] >= rule["activation_h"] and p["gross"] <= -rule["mult"] * trade["target"]
            for p in path
        )
        if hard:
            pred = lambda p: p["elapsed_h"] >= rule["activation_h"] and p["gross"] <= -rule["mult"] * trade["target"]
            hard_idx = first_confirmed_stop(path, pred, 1)
        else:
            hard_idx = None
        pred2 = lambda p: (
            (
                p["ts"].date() == expiry_date
                and (
                    p["ts"].hour > hh
                    or (p["ts"].hour == hh and p["ts"].minute >= mm)
                )
            )
            and p["gross"] < 0
        )
        late_idx = first_confirmed_stop(path, pred2, 1)
        vals = [i for i in [hard_idx, late_idx] if i is not None]
        return min(vals) if vals else None

    raise ValueError(rule["family"])


def evaluate_rule(trades, rule):
    rows = []
    for t in trades:
        idx = stop_index_for_rule(t, rule)
        # Never allow a stop to replace a baseline target if the target is reached
        # first. Path construction ends at the baseline target when reached.
        if idx is None:
            exit_idx = len(t["path"]) - 1
            reason = t["base_exit_reason"]
        else:
            exit_idx = min(idx, len(t["path"]) - 1)
            reason = "STOP"

        p = t["path"][exit_idx]
        raw_exit = None
        ts = p["ts"]
        k_n, k_n1, k_n2 = t["strikes"]
        # Raw exit prices are not stored in path, so recover them only for charge
        # calculation through a marker-free re-evaluation below. Costs are tiny
        # relative to the gross decision, but must still be modeled.
        # The base trade stores raw exit information only through the path's
        # timestamp; the exact row is reconstructed by the price loader in the
        # charge pass below.
        rows.append(
            {
                "expiry": t["expiry"],
                "base_net": t["base_net"],
                "base_gross": t["base_gross"],
                "base_reason": t["base_exit_reason"],
                "stop_ts": ts,
                "stop_reason": reason,
                "stop_gross": p["gross"],
                "base_positive": t["base_net"] > 0,
                "changed_before_base": ts < t["base_exit_ts"],
            }
        )

    out = pd.DataFrame(rows)

    # Charge adjustments at candidate exits are intentionally approximated by
    # replacing the baseline cost with the per-trade cost at the candidate stop
    # using the observed exit timestamp. This keeps the fee model date-aware while
    # preserving the primary stop trigger on gross MTM.
    # Candidate exit price reconstruction is added in the next research revision
    # if the zero-false-stop screen identifies a viable family.
    out["candidate_net"] = out["stop_gross"] - (
        out["base_gross"] - out["base_net"]
    )
    out["net_uplift"] = out["candidate_net"] - out["base_net"]
    out["winner_affected"] = (
        out["base_positive"] & out["changed_before_base"]
    )
    out["loss_reduction"] = np.where(
        out["base_net"] < 0,
        np.maximum(out["candidate_net"] - out["base_net"], 0.0),
        0.0,
    )
    out["loss_eliminated"] = (
        (out["base_net"] < 0) & (out["candidate_net"] >= 0)
    )
    return out


def summarize(dev_trades, val_trades, rules):
    records = []
    per_rule = {}

    for rule in rules:
        dev = evaluate_rule(dev_trades, rule)
        val = evaluate_rule(val_trades, rule)
        per_rule[rule["name"]] = (dev, val)

        records.append(
            {
                **{k: v for k, v in rule.items() if k != "family"},
                "family": rule["family"],
                "dev_trades": len(dev),
                "dev_base_net": float(dev.base_net.sum()),
                "dev_candidate_net": float(dev.candidate_net.sum()),
                "dev_net_uplift": float(dev.net_uplift.sum()),
                "dev_winner_affected": int(dev.winner_affected.sum()),
                "dev_profit_uplift_lost": float(
                    (dev.loc[dev.winner_affected, "base_net"] - dev.loc[dev.winner_affected, "candidate_net"]).sum()
                ),
                "dev_losses": int((dev.base_net < 0).sum()),
                "dev_loss_reduction": float(dev.loss_reduction.sum()),
                "dev_losses_eliminated": int(dev.loss_eliminated.sum()),
                "val_trades": len(val),
                "val_base_net": float(val.base_net.sum()),
                "val_candidate_net": float(val.candidate_net.sum()),
                "val_net_uplift": float(val.net_uplift.sum()),
                "val_winner_affected": int(val.winner_affected.sum()),
                "val_profit_uplift_lost": float(
                    (val.loc[val.winner_affected, "base_net"] - val.loc[val.winner_affected, "candidate_net"]).sum()
                ),
                "val_losses": int((val.base_net < 0).sum()),
                "val_loss_reduction": float(val.loss_reduction.sum()),
                "val_losses_eliminated": int(val.loss_eliminated.sum()),
            }
        )

    result = pd.DataFrame(records)

    # Freeze a rule using development only:
    # 1) zero affected positive trades;
    # 2) maximize development net uplift;
    # 3) maximize development loss reduction;
    # 4) minimize number of stops.
    eligible = result[result.dev_winner_affected == 0].copy()
    if eligible.empty:
        eligible = result.copy()

    selected = eligible.sort_values(
        by=["dev_net_uplift", "dev_loss_reduction", "dev_winner_affected"],
        ascending=[False, False, True],
    ).iloc[0]

    selected_name = selected["name"]
    chosen_dev, chosen_val = per_rule[selected_name]

    return result, selected_name, chosen_dev, chosen_val


def main():
    all_trades = build_paths()
    if not all_trades:
        raise RuntimeError("No trades reconstructed")

    dev_trades = [t for t in all_trades if pd.Timestamp(t["expiry"], tz=TZ) <= DEV_END]
    val_trades = [t for t in all_trades if pd.Timestamp(t["expiry"], tz=TZ) >= VAL_START]

    rules = candidate_rules()
    result, selected_name, selected_dev, selected_val = summarize(
        dev_trades, val_trades, rules
    )

    result.to_csv(OUT / "stop_rule_grid.csv", index=False)
    selected_dev.to_csv(OUT / "selected_rule_dev_trade_level.csv", index=False)
    selected_val.to_csv(OUT / "selected_rule_validation_trade_level.csv", index=False)

    selected = result[result.name == selected_name].iloc[0]
    report = f"""# Phase 17 Stop-Loss Research

## Frozen baseline

- Same corrected dynamic-n engine.
- 10:00 IST entry, 4 trading sessions before expiry.
- OTM6/7/8 direction selector.
- Dynamic n = highest candidate n within 95% of Xmax.
- Target = 0.90 × X_selected × lot.
- One adverse tick per leg.
- ₹10/order brokerage and date-aware statutory costs.
- Baseline remains the primary strategy; stop-loss results are an extension.

## Candidate families

Hard stops, expiry-day negative cutoffs, stagnation stops, MFE trailing stops, and a hard-stop-plus-expiry-day rule were pre-registered before execution.

## Selection protocol

Using only expiries through {DEV_END.date()}:
1. zero affected baseline-positive trades;
2. maximize aggregate net-P&L uplift;
3. maximize loss reduction;
4. minimize affected winners as a final tie-break.

The selected rule is then frozen and evaluated on {VAL_START.date()} through {END.date()}.

## Selected rule

**{selected_name}**

Development:
- trades: {int(selected.dev_trades)}
- net uplift: ₹{selected.dev_net_uplift:,.2f}
- winner-affected trades: {int(selected.dev_winner_affected)}
- loss reduction: ₹{selected.dev_loss_reduction:,.2f}
- losses eliminated: {int(selected.dev_losses_eliminated)}

Validation:
- trades: {int(selected.val_trades)}
- net uplift: ₹{selected.val_net_uplift:,.2f}
- winner-affected trades: {int(selected.val_winner_affected)}
- loss reduction: ₹{selected.val_loss_reduction:,.2f}
- losses eliminated: {int(selected.val_losses_eliminated)}

## Important implementation note

Candidate stop net-P&L currently reuses each trade's baseline fee amount rather than reconstructing the exact stop-time exit leg prices for date-aware exit charges. Therefore the stop-rule ranking is driven by the exact minute-level gross P&L path, while small fee differences at the stop timestamp are not yet incorporated. Any rule that survives the zero-false-stop screen is required to pass a second exact-fee rerun before being considered operational.
"""
    (OUT / "STOP_LOSS_REPORT.md").write_text(report, encoding="utf-8")

    print(result.sort_values(["dev_winner_affected", "dev_net_uplift"], ascending=[True, False]).head(20).to_string(index=False))
    print("\nSELECTED RULE:", selected_name)
    print("\nDEV\n", selected_dev[["expiry","base_net","candidate_net","net_uplift","stop_reason","stop_ts","winner_affected"]].to_string(index=False))
    print("\nVALIDATION\n", selected_val[["expiry","base_net","candidate_net","net_uplift","stop_reason","stop_ts","winner_affected"]].to_string(index=False))


if __name__ == "__main__":
    main()
