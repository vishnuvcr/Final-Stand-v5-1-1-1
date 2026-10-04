import os
import re
from pathlib import Path

import numpy as np
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

REPO = "thetrademarkk/india-index-options-1m"
TZ = "Asia/Kolkata"

START = pd.Timestamp(os.getenv("START_DATE", "2021-05-27"), tz=TZ)
END = pd.Timestamp(os.getenv("END_DATE", "2026-09-30"), tz=TZ)

OUT = Path(os.getenv("OUT_DIR", "results/dynamic_n_corrected"))
OUT.mkdir(parents=True, exist_ok=True)

ENTRY_HOUR = int(os.getenv("ENTRY_HOUR", "10"))
ENTRY_MINUTE = int(os.getenv("ENTRY_MINUTE", "0"))
DTE_SESSIONS = int(os.getenv("DTE_SESSIONS", "4"))
SLIPPAGE_TICKS = float(os.getenv("SLIPPAGE_TICKS", "1"))
TICK = float(os.getenv("OPTION_TICK", "0.05"))
BROKERAGE_PER_ORDER = float(os.getenv("BROKERAGE_PER_ORDER", "10"))
TARGET_FRACTION = float(os.getenv("TARGET_FRACTION", "0.90"))
STRIKE_INTERVAL = float(os.getenv("NIFTY_STRIKE_INTERVAL", "50"))
N_MIN = 6
N_MAX = 15
HIGH_N_THRESHOLD = float(os.getenv("HIGH_N_THRESHOLD", "0.95"))
N_SELECTION_MODE = os.getenv("N_SELECTION_MODE", "dynamic")


def lot_size_for_expiry(expiry):
    if expiry < pd.Timestamp("2021-08-01", tz=TZ):
        return 75
    if expiry < pd.Timestamp("2024-05-02", tz=TZ):
        return 50
    if expiry < pd.Timestamp("2025-01-02", tz=TZ):
        return 25
    if expiry < pd.Timestamp("2026-01-06", tz=TZ):
        return 75
    return 65


def fee_rates(d):
    if d >= pd.Timestamp("2026-04-01", tz=TZ):
        stt = 0.0015
    elif d >= pd.Timestamp("2024-10-01", tz=TZ):
        stt = 0.0010
    else:
        stt = 0.000625

    if d >= pd.Timestamp("2026-03-01", tz=TZ):
        txn = 0.000355299
        ipft = 0.000000001
    elif d >= pd.Timestamp("2024-10-01", tz=TZ):
        txn = 0.0003503
        ipft = 0.000005
    else:
        txn = 0.000495
        ipft = 0.000005

    return stt, txn, 0.000001, ipft, 0.00003


def exec_px(px, action):
    slip = SLIPPAGE_TICKS * TICK
    return max(0.0, px + slip) if action == "buy" else max(0.0, px - slip)


def charges(entry_orders, exit_orders, lot):
    brokerage = BROKERAGE_PER_ORDER * 6.0
    exchange = sebi = ipft = stt = stamp = 0.0

    for d, side, px in entry_orders + exit_orders:
        stt_r, txn_r, sebi_r, ipft_r, stamp_r = fee_rates(d)
        turnover = px * lot
        exchange += txn_r * turnover
        sebi += sebi_r * turnover
        ipft += ipft_r * turnover
        if side == "sell":
            stt += stt_r * turnover
        else:
            stamp += stamp_r * turnover

    gst = 0.18 * (brokerage + exchange + sebi + ipft)
    return brokerage + exchange + sebi + ipft + stt + stamp + gst


def load(path):
    p = hf_hub_download(
        repo_id=REPO,
        filename=path,
        repo_type="dataset",
        token=os.getenv("HF_TOKEN") or None,
    )
    df = pd.read_parquet(p)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    if df["timestamp"].dt.tz is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize(TZ)
    else:
        df["timestamp"] = df["timestamp"].dt.tz_convert(TZ)
    return df


def normalize(df):
    out = df.copy()
    out["strike"] = pd.to_numeric(out["strike"], errors="coerce")
    out["option_type"] = out["option_type"].astype(str).str.upper()
    return out


def nearest_atm(entry_quotes, spot):
    strikes = sorted(entry_quotes["strike"].dropna().unique())
    if not strikes:
        return None
    return min(strikes, key=lambda x: abs(x - spot))


def prices_at(df, ts, typ, strikes):
    q = df[
        (df["timestamp"] == ts)
        & (df["option_type"] == typ)
        & (df["strike"].isin(strikes))
    ]
    return {float(r.strike): float(r.close) for _, r in q.iterrows()}


def pnl_points(entry_exec, exit_exec):
    e_n, e_n1, e_n2 = entry_exec
    x_n, x_n1, x_n2 = exit_exec
    return (x_n - e_n) + (e_n1 - x_n1) + (e_n2 - x_n2)


def expiry_files(api):
    all_expiries = []
    for f in api.list_repo_files(REPO, repo_type="dataset"):
        m = re.match(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet$", f)
        if not m:
            continue
        d = pd.Timestamp(m.group(1), tz=TZ)
        if START <= d <= END:
            all_expiries.append(d)

    expiry_set = sorted(set(all_expiries))
    monthly = set()
    for y, m in sorted({(d.year, d.month) for d in expiry_set}):
        month_expiries = [d for d in expiry_set if d.year == y and d.month == m]
        if month_expiries:
            monthly.add(max(month_expiries))

    return [d for d in expiry_set if d not in monthly]


def required_strikes(atm, typ):
    sign = 1 if typ == "CE" else -1
    return {
        n: atm + sign * n * STRIKE_INTERVAL
        for n in range(6, 18)
    }


def candidate_scores(side_prices):
    scores = []
    for n in range(N_MIN, N_MAX + 1):
        xn = (
            side_prices[n + 2]
            + side_prices[n + 1]
            - side_prices[n]
        )
        scores.append({"n": n, "x_n": float(xn)})
    return pd.DataFrame(scores)


def select_n(scores):
    x_max = float(scores["x_n"].max())
    if not np.isfinite(x_max) or x_max <= 0:
        return None, x_max, HIGH_N_THRESHOLD * x_max

    threshold = HIGH_N_THRESHOLD * x_max
    if N_SELECTION_MODE == "fixed6":
        selected_n = 6
    elif N_SELECTION_MODE == "fixed7":
        selected_n = 7
    elif N_SELECTION_MODE == "fixed15":
        selected_n = 15
    else:
        eligible = scores[scores["x_n"] >= threshold].copy()
        if eligible.empty:
            return None, x_max, threshold
        selected_n = int(eligible["n"].max())
    return selected_n, x_max, threshold


def main():
    spot = load("index/NIFTY.parquet")[["timestamp", "close"]].rename(
        columns={"close": "spot"}
    )

    api = HfApi(token=os.getenv("HF_TOKEN") or None)
    expiries = expiry_files(api)

    stage1 = []
    candidates = []
    missing = []
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
            missing.append([str(expiry.date()), "fewer than required pre-expiry trading sessions"])
            continue

        entry_date = pre_expiry[-DTE_SESSIONS]
        entry_ts = entry_date + pd.Timedelta(hours=ENTRY_HOUR, minutes=ENTRY_MINUTE)

        sr = spot[spot.timestamp == entry_ts]
        if sr.empty:
            missing.append([str(expiry.date()), "missing entry spot"])
            continue

        spot_entry = float(sr.iloc[0].spot)

        try:
            df = normalize(load(f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet"))
        except Exception as exc:
            missing.append([str(expiry.date()), f"download/read {exc!r}"])
            continue

        entry_quotes = df[df["timestamp"] == entry_ts]
        if entry_quotes.empty:
            missing.append([str(expiry.date()), "missing entry option snapshot"])
            continue

        atm = nearest_atm(entry_quotes, spot_entry)
        if atm is None:
            missing.append([str(expiry.date()), "missing ATM strike"])
            continue

        call_strikes = required_strikes(atm, "CE")
        put_strikes = required_strikes(atm, "PE")

        call_px = prices_at(df, entry_ts, "CE", tuple(call_strikes.values()))
        put_px = prices_at(df, entry_ts, "PE", tuple(put_strikes.values()))

        # Stage 1 must contain the exact OTM6, OTM7 and OTM8 prices on both sides.
        if any(call_px.get(call_strikes[n]) is None for n in (6, 7, 8)) or any(
            put_px.get(put_strikes[n]) is None for n in (6, 7, 8)
        ):
            missing.append([str(expiry.date()), "missing OTM6/7/8 direction strikes"])
            continue

        x_call_direction = (
            call_px[call_strikes[8]]
            + call_px[call_strikes[7]]
            - call_px[call_strikes[6]]
        )
        x_put_direction = (
            put_px[put_strikes[8]]
            + put_px[put_strikes[7]]
            - put_px[put_strikes[6]]
        )

        if x_call_direction > x_put_direction:
            direction = "BEARISH"
            typ = "CE"
            strike_map = call_strikes
            px_map = call_px
        elif x_call_direction < x_put_direction:
            direction = "BULLISH"
            typ = "PE"
            strike_map = put_strikes
            px_map = put_px
        else:
            stage1.append({
                "expiry": str(expiry.date()),
                "entry_ts": str(entry_ts),
                "spot_entry": spot_entry,
                "atm": atm,
                "x_call_direction": x_call_direction,
                "x_put_direction": x_put_direction,
                "direction": "NO_TRADE_TIE",
            })
            missing.append([str(expiry.date()), "Stage 1 exact X tie"])
            continue

        stage1.append({
            "expiry": str(expiry.date()),
            "entry_ts": str(entry_ts),
            "spot_entry": spot_entry,
            "atm": atm,
            "x_call_direction": x_call_direction,
            "x_put_direction": x_put_direction,
            "direction": direction,
        })

        # We need exact OTM6..17 on the selected side for complete n=6..15 evaluation.
        required_px = {n: px_map.get(strike_map[n]) for n in range(6, 18)}
        if any(v is None for v in required_px.values()):
            missing.append([str(expiry.date()), "incomplete selected-side OTM6..17 candidate set"])
            continue

        score_df = candidate_scores(required_px)
        selected_n, x_max, threshold = select_n(score_df)

        score_df["expiry"] = str(expiry.date())
        score_df["entry_ts"] = str(entry_ts)
        score_df["direction"] = direction
        score_df["x_max"] = x_max
        score_df["high_n_threshold"] = threshold
        score_df["eligible_95pct"] = score_df["x_n"] >= threshold
        score_df["selected"] = score_df["n"] == selected_n
        candidates.extend(score_df.to_dict("records"))

        if selected_n is None:
            missing.append([str(expiry.date()), "NO_POSITIVE_X_DYNAMIC_N"])
            continue

        n = selected_n
        x_selected = float(score_df.loc[score_df["n"] == n, "x_n"].iloc[0])
        k_n = strike_map[n]
        k_n1 = strike_map[n + 1]
        k_n2 = strike_map[n + 2]

        raw_entry = (required_px[n], required_px[n + 1], required_px[n + 2])
        ep_n = exec_px(raw_entry[0], "buy")
        ep_n1 = exec_px(raw_entry[1], "sell")
        ep_n2 = exec_px(raw_entry[2], "sell")

        lot = lot_size_for_expiry(expiry)
        target_rupees = TARGET_FRACTION * x_selected * lot

        end_ts = expiry.normalize() + pd.Timedelta(hours=15, minutes=29)

        q = df[
            (df["timestamp"] > entry_ts)
            & (df["timestamp"] <= end_ts)
            & (df["option_type"] == typ)
            & (df["strike"].isin([k_n, k_n1, k_n2]))
        ]
        piv = q.pivot_table(
            index="timestamp",
            columns="strike",
            values="close",
            aggfunc="last",
        ).dropna(subset=[k_n, k_n1, k_n2])

        if piv.empty:
            missing.append([str(expiry.date()), "no complete selected 3-leg minute series"])
            continue

        exit_ts = piv.index[-1]
        reason = "EXPIRY"
        target_reached = False
        mfe = -np.inf
        mae = np.inf
        exit_raw = None

        for ts, row in piv.iterrows():
            raw_exit = (
                float(row[k_n]),
                float(row[k_n1]),
                float(row[k_n2]),
            )
            ex_n = exec_px(raw_exit[0], "sell")
            ex_n1 = exec_px(raw_exit[1], "buy")
            ex_n2 = exec_px(raw_exit[2], "buy")
            gross = pnl_points((ep_n, ep_n1, ep_n2), (ex_n, ex_n1, ex_n2)) * lot
            mfe = max(mfe, gross)
            mae = min(mae, gross)

            if gross >= target_rupees:
                exit_ts = ts
                reason = "TARGET"
                target_reached = True
                exit_raw = raw_exit
                break

        if exit_raw is None:
            r = piv.loc[exit_ts]
            exit_raw = (
                float(r[k_n]),
                float(r[k_n1]),
                float(r[k_n2]),
            )

        xp_n = exec_px(exit_raw[0], "sell")
        xp_n1 = exec_px(exit_raw[1], "buy")
        xp_n2 = exec_px(exit_raw[2], "buy")

        gross_points = pnl_points(
            (ep_n, ep_n1, ep_n2),
            (xp_n, xp_n1, xp_n2),
        )
        gross_rupees = gross_points * lot

        entry_orders = [
            (entry_ts, "buy", ep_n),
            (entry_ts, "sell", ep_n1),
            (entry_ts, "sell", ep_n2),
        ]
        exit_orders = [
            (exit_ts, "sell", xp_n),
            (exit_ts, "buy", xp_n1),
            (exit_ts, "buy", xp_n2),
        ]
        cost_rupees = charges(entry_orders, exit_orders, lot)
        net_rupees = gross_rupees - cost_rupees

        trades.append({
            "expiry": str(expiry.date()),
            "entry_date": str(entry_date.date()),
            "entry_ts": str(entry_ts),
            "exit_ts": str(exit_ts),
            "direction": direction,
            "option_type": typ,
            "spot_entry": spot_entry,
            "atm": atm,
            "n_selected": n,
            "k_n": k_n,
            "k_n1": k_n1,
            "k_n2": k_n2,
            "p_n_raw": raw_entry[0],
            "p_n1_raw": raw_entry[1],
            "p_n2_raw": raw_entry[2],
            "x_call_direction": x_call_direction,
            "x_put_direction": x_put_direction,
            "x_max": x_max,
            "high_n_threshold": threshold,
            "x_selected": x_selected,
            "target_rupees": target_rupees,
            "lot_size": lot,
            "gross_points": gross_points,
            "gross_rupees": gross_rupees,
            "cost_rupees": cost_rupees,
            "net_rupees": net_rupees,
            "net_points": net_rupees / lot,
            "mfe_rupees": mfe,
            "mae_rupees": mae,
            "exit_reason": reason,
            "target_reached": target_reached,
            "slippage_ticks": SLIPPAGE_TICKS,
            "brokerage_per_order": BROKERAGE_PER_ORDER,
            "target_fraction": TARGET_FRACTION,
            "high_n_threshold_fraction": HIGH_N_THRESHOLD,
        "n_selection_mode": N_SELECTION_MODE,
            "n_selection_mode": N_SELECTION_MODE,
        })

    tr = pd.DataFrame(trades)
    pd.DataFrame(stage1).to_csv(OUT / "stage1_direction.csv", index=False)
    pd.DataFrame(candidates).to_csv(OUT / "candidate_n_scores.csv", index=False)
    pd.DataFrame(missing, columns=["expiry", "reason"]).to_csv(OUT / "missing.csv", index=False)
    tr.to_csv(OUT / "trades.csv", index=False)

    if tr.empty:
        pd.DataFrame([{"trades": 0}]).to_csv(OUT / "summary.csv", index=False)
        print("NO_TRADES")
        return

    profits = tr.loc[tr.net_rupees > 0, "net_rupees"].sum()
    losses = -tr.loc[tr.net_rupees < 0, "net_rupees"].sum()
    pf = profits / losses if losses else np.inf

    summary = pd.DataFrame([{
        "trades": len(tr),
        "win_rate_net": float((tr.net_rupees > 0).mean()),
        "mean_net_rupees": float(tr.net_rupees.mean()),
        "median_net_rupees": float(tr.net_rupees.median()),
        "sum_net_rupees": float(tr.net_rupees.sum()),
        "mean_gross_rupees": float(tr.gross_rupees.mean()),
        "sum_gross_rupees": float(tr.gross_rupees.sum()),
        "sum_cost_rupees": float(tr.cost_rupees.sum()),
        "profit_factor": float(pf),
        "target_exit_rate": float((tr.exit_reason == "TARGET").mean()),
        "expiry_exit_rate": float((tr.exit_reason == "EXPIRY").mean()),
        "mean_selected_n": float(tr.n_selected.mean()),
        "median_selected_n": float(tr.n_selected.median()),
        "mean_x_selected": float(tr.x_selected.mean()),
        "mean_lot_size": float(tr.lot_size.mean()),
        "slippage_ticks": SLIPPAGE_TICKS,
        "brokerage_per_order": BROKERAGE_PER_ORDER,
        "target_fraction": TARGET_FRACTION,
        "high_n_threshold_fraction": HIGH_N_THRESHOLD,
        "dte_sessions": DTE_SESSIONS,
        "entry_hour": ENTRY_HOUR,
        "entry_minute": ENTRY_MINUTE,
    }])

    direction = tr.groupby("direction").agg(
        trades=("expiry", "count"),
        net_rupees=("net_rupees", "sum"),
        mean_net=("net_rupees", "mean"),
        win_rate=("net_rupees", lambda x: float((x > 0).mean())),
        mean_n=("n_selected", "mean"),
    ).reset_index()

    exits = tr.groupby("exit_reason").agg(
        trades=("expiry", "count"),
        net_rupees=("net_rupees", "sum"),
        mean_net=("net_rupees", "mean"),
        win_rate=("net_rupees", lambda x: float((x > 0).mean())),
    ).reset_index()

    n_dist = (
        tr.groupby("n_selected")
        .agg(
            trades=("expiry", "count"),
            net_rupees=("net_rupees", "sum"),
            mean_net=("net_rupees", "mean"),
            win_rate=("net_rupees", lambda x: float((x > 0).mean())),
        )
        .reset_index()
        .sort_values("n_selected")
    )

    year = tr.assign(year=tr["expiry"].str[:4].astype(int)).groupby("year").agg(
        trades=("net_rupees", "size"),
        net_rupees=("net_rupees", "sum"),
        mean_net=("net_rupees", "mean"),
        win_rate=("net_rupees", lambda x: float((x > 0).mean())),
    ).reset_index()

    summary.to_csv(OUT / "summary.csv", index=False)
    direction.to_csv(OUT / "direction_statistics.csv", index=False)
    exits.to_csv(OUT / "exit_statistics.csv", index=False)
    n_dist.to_csv(OUT / "n_distribution.csv", index=False)
    year.to_csv(OUT / "yearly_statistics.csv", index=False)

    print(summary.to_string(index=False))
    print("\nDIRECTION\n", direction.to_string(index=False))
    print("\nEXIT\n", exits.to_string(index=False))
    print("\nN DISTRIBUTION\n", n_dist.to_string(index=False))
    print("\nYEAR\n", year.to_string(index=False))


if __name__ == "__main__":
    main()
