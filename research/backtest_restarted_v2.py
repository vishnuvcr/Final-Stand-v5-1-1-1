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
OUT = Path(os.getenv("OUT_DIR", "results/restarted_v2"))
OUT.mkdir(parents=True, exist_ok=True)

N_MIN, N_MAX = 6, 15
HIGH_N_THRESHOLD = float(os.getenv("HIGH_N_THRESHOLD", "0.95"))
TARGET_FRACTION = 0.90
SLIPPAGE_TICKS = float(os.getenv("SLIPPAGE_TICKS", "1"))
TICK = float(os.getenv("OPTION_TICK", "0.05"))


def lot_size_for_expiry(expiry):
    # NSE circular boundaries:
    # 75 through July-2021 weekly contracts; 50 from Aug-2021 weekly;
    # 25 from May-02-2024 weekly; 75 from Jan-02-2025 weekly;
    # 65 from Jan-06-2026 weekly.
    if expiry < pd.Timestamp("2021-08-01", tz=TZ):
        return 75
    if expiry < pd.Timestamp("2024-05-02", tz=TZ):
        return 50
    if expiry < pd.Timestamp("2025-01-02", tz=TZ):
        return 25
    if expiry < pd.Timestamp("2026-01-06", tz=TZ):
        return 75
    return 65


def fee_model(d):
    if d >= pd.Timestamp("2026-04-01", tz=TZ):
        stt = 0.0015
    elif d >= pd.Timestamp("2024-10-01", tz=TZ):
        stt = 0.0010
    else:
        stt = 0.000625
    txn = 0.0003503 if d >= pd.Timestamp("2024-10-01", tz=TZ) else 0.000495
    sebi = 0.000001
    ipft = 0.000001
    stamp = 0.00003
    return stt, txn, sebi, ipft, stamp


def exec_px(px, action):
    slip = SLIPPAGE_TICKS * TICK
    return max(0.0, px + slip) if action == "buy" else max(0.0, px - slip)


def charges(entry, exit_, d, lot):
    stt, txn, sebi, ipft, stamp = fee_model(d)
    turnover = sum(p for _, p in entry + exit_) * lot
    sells = sum(p for side, p in entry + exit_ if side == "sell") * lot
    buys = sum(p for side, p in entry + exit_ if side == "buy") * lot
    brokerage = 10.0 * 6.0
    exchange = txn * turnover
    sebi_fee = sebi * turnover
    ipft_fee = ipft * turnover
    stt_fee = stt * sells
    stamp_fee = stamp * buys
    gst = 0.18 * (brokerage + exchange + sebi_fee + ipft_fee)
    return brokerage + exchange + sebi_fee + ipft_fee + stt_fee + stamp_fee + gst


def load(path):
    p = hf_hub_download(
        repo_id=REPO,
        filename=path,
        repo_type="dataset",
        token=(os.getenv("HF_TOKEN") or None),
    )
    df = pd.read_parquet(p)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    if df["timestamp"].dt.tz is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize(TZ)
    else:
        df["timestamp"] = df["timestamp"].dt.tz_convert(TZ)
    return df


def normalize(df):
    df = df.copy()
    df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
    df["option_type"] = df["option_type"].astype(str).str.upper()
    return df


def rank_strikes(entry_quotes, spot):
    strikes = sorted(entry_quotes["strike"].dropna().unique())
    if not strikes:
        return None, None, None
    atm = min(strikes, key=lambda x: abs(x - spot))
    puts = sorted([x for x in strikes if x < atm], reverse=True)
    calls = sorted([x for x in strikes if x > atm])
    return atm, puts, calls


def price_map(option_df, entry_ts, typ, strikes):
    q = option_df[
        (option_df["timestamp"] == entry_ts)
        & (option_df["option_type"] == typ)
        & (option_df["strike"].isin(strikes))
    ]
    return {float(r.strike): float(r.close) for _, r in q.iterrows()}


def x_candidates(option_df, entry_ts, strikes, typ):
    rows = []
    for n in range(N_MIN, N_MAX + 1):
        ks = (strikes[n - 1], strikes[n], strikes[n + 1])
        vals = price_map(option_df, entry_ts, typ, ks)
        if any(k not in vals for k in ks):
            continue
        x = vals[ks[1]] + vals[ks[2]] - vals[ks[0]]
        rows.append({
            "n": n,
            "k_n": ks[0],
            "k_n1": ks[1],
            "k_n2": ks[2],
            "p_n": vals[ks[0]],
            "p_n1": vals[ks[1]],
            "p_n2": vals[ks[2]],
            "x": x,
        })
    return pd.DataFrame(rows)


def pnl_points(entry_exec, exit_exec):
    e6, e7, e8 = entry_exec
    x6, x7, x8 = exit_exec
    return (e6 - x6) + (x7 - e7) + (x8 - e8)


def main():
    spot = load("index/NIFTY.parquet")[["timestamp", "close"]].rename(
        columns={"close": "spot"}
    )

    api = HfApi(token=os.getenv("HF_TOKEN") or None)
    files = api.list_repo_files(REPO, repo_type="dataset")

    expiries = []
    for f in files:
        m = re.match(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet$", f)
        if m:
            d = pd.Timestamp(m.group(1), tz=TZ)
            if START <= d <= END:
                expiries.append(d)

    expiry_set = sorted(set(expiries))
    monthly = set()
    for y, m in sorted({(d.year, d.month) for d in expiry_set}):
        md = [d for d in expiry_set if d.year == y and d.month == m]
        if md:
            monthly.add(max(md))
    expiries = [d for d in expiry_set if d not in monthly]

    trades = []
    stage1 = []
    candidates = []
    missing = []

    for expiry in expiries:
        # Need at least four sessions BEFORE expiry. Search a sufficiently
        # wide calendar window and exclude the expiry session itself.
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
        if len(pre_expiry) < 4:
            missing.append([str(expiry.date()), "fewer than 4 pre-expiry trading sessions"])
            continue

        entry_date = pre_expiry[-4]
        entry_ts = entry_date + pd.Timedelta(hours=10)

        sr = spot[spot.timestamp == entry_ts]
        if sr.empty:
            missing.append([str(expiry.date()), "missing 10:00 spot"])
            continue
        s0 = float(sr.iloc[0].spot)

        try:
            df = normalize(load(f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet"))
        except Exception as e:
            missing.append([str(expiry.date()), "download/read " + repr(e)])
            continue

        entry_quotes = df[df["timestamp"] == entry_ts]
        if entry_quotes.empty:
            missing.append([str(expiry.date()), "missing 10:00 option-chain snapshot"])
            continue

        atm, puts, calls = rank_strikes(entry_quotes, s0)
        if atm is None:
            missing.append([str(expiry.date()), "no strikes at 10:00"])
            continue

        # Stage 1 requires OTM8 on both sides.
        if len(puts) < 8 or len(calls) < 8:
            missing.append([str(expiry.date()), "fewer than OTM8 strikes for Stage 1"])
            continue

        p6 = price_map(df, entry_ts, "PE", (puts[5], puts[6], puts[7]))
        c6 = price_map(df, entry_ts, "CE", (calls[5], calls[6], calls[7]))
        if len(p6) < 3 or len(c6) < 3:
            missing.append([str(expiry.date()), "missing OTM6/7/8 price for Stage 1"])
            continue

        x_put6 = p6[puts[6]] + p6[puts[7]] - p6[puts[5]]
        x_call6 = c6[calls[6]] + c6[calls[7]] - c6[calls[5]]

        if x_call6 > x_put6:
            direction, typ, side_label = "BEARISH", "CE", "CALL"
        elif x_call6 < x_put6:
            direction, typ, side_label = "BULLISH", "PE", "PUT"
        else:
            stage1.append({
                "expiry": str(expiry.date()), "entry_ts": str(entry_ts),
                "spot_entry": s0, "atm": atm,
                "x_call6": x_call6, "x_put6": x_put6,
                "direction": "NO_TRADE_TIE"
            })
            missing.append([str(expiry.date()), "Stage 1 exact X tie"])
            continue

        stage1.append({
            "expiry": str(expiry.date()), "entry_ts": str(entry_ts),
            "spot_entry": s0, "atm": atm,
            "x_call6": x_call6, "x_put6": x_put6,
            "direction": direction
        })

        side_strikes = calls if typ == "CE" else puts
        if len(side_strikes) < N_MAX + 2:
            missing.append([str(expiry.date()), "fewer than OTM17 strikes for Stage 2"])
            continue

        cand = x_candidates(df, entry_ts, side_strikes, typ)
        if cand.empty:
            missing.append([str(expiry.date()), "no complete Stage 2 candidates"])
            continue

        cand.insert(0, "expiry", str(expiry.date()))
        cand["entry_ts"] = str(entry_ts)
        cand["direction"] = direction
        cand["side"] = side_label
        cand["spot_entry"] = s0
        cand["atm"] = atm
        cand["x_call6"] = x_call6
        cand["x_put6"] = x_put6
        candidates.append(cand)

        x_max = float(cand["x"].max())
        if x_max <= 0:
            missing.append([str(expiry.date()), "NO_POSITIVE_X"])
            continue

        threshold_x = HIGH_N_THRESHOLD * x_max
        eligible = cand[cand["x"] >= threshold_x]
        selected = eligible.sort_values("n", ascending=False).iloc[0]

        n = int(selected["n"])
        k6, k7, k8 = float(selected["k_n"]), float(selected["k_n1"]), float(selected["k_n2"])
        q6, q7, q8 = float(selected["p_n"]), float(selected["p_n1"]), float(selected["p_n2"])
        x_raw = float(selected["x"])
        lot = lot_size_for_expiry(expiry)

        # User target is exactly 0.90 * raw X * lot.
        target_rupees = TARGET_FRACTION * x_raw * lot

        ep6 = exec_px(q6, "buy")
        ep7 = exec_px(q7, "sell")
        ep8 = exec_px(q8, "sell")
        entry_credit_exec = ep7 + ep8 - ep6

        end_ts = expiry.normalize() + pd.Timedelta(hours=15, minutes=29)
        q = df[
            (df["timestamp"] >= entry_ts)
            & (df["timestamp"] <= end_ts)
            & (df["option_type"] == typ)
            & (df["strike"].isin([k6, k7, k8]))
        ]
        piv = q.pivot_table(
            index="timestamp", columns="strike", values="close", aggfunc="last"
        ).dropna(subset=[k6, k7, k8])

        if piv.empty:
            missing.append([str(expiry.date()), "no complete selected 3-leg minute series"])
            continue

        exit_ts = piv.index[-1]
        reason = "EXPIRY"
        target_reached = False
        xp = None
        mfe = -np.inf
        mae = np.inf

        for ts, row in piv.iterrows():
            m6, m7, m8 = float(row[k6]), float(row[k7]), float(row[k8])
            ex6, ex7, ex8 = exec_px(m6, "sell"), exec_px(m7, "buy"), exec_px(m8, "buy")
            gp = pnl_points((ep6, ep7, ep8), (ex6, ex7, ex8))
            gr = gp * lot
            mfe = max(mfe, gr)
            mae = min(mae, gr)
            if gr >= target_rupees:
                exit_ts = ts
                reason = "TARGET"
                target_reached = True
                xp = (m6, m7, m8)
                break

        if xp is None:
            r = piv.loc[exit_ts]
            xp = (float(r[k6]), float(r[k7]), float(r[k8]))

        xp6, xp7, xp8 = exec_px(xp[0], "sell"), exec_px(xp[1], "buy"), exec_px(xp[2], "buy")
        gross_points = pnl_points((ep6, ep7, ep8), (xp6, xp7, xp8))
        gross_rupees = gross_points * lot

        cost_rupees = charges(
            [("buy", ep6), ("sell", ep7), ("sell", ep8)],
            [("sell", xp6), ("buy", xp7), ("buy", xp8)],
            entry_ts, lot
        )
        net_rupees = gross_rupees - cost_rupees

        trades.append({
            "expiry": str(expiry.date()),
            "entry_ts": str(entry_ts),
            "exit_ts": str(exit_ts),
            "direction": direction,
            "side": side_label,
            "n": n,
            "x_call6": x_call6,
            "x_put6": x_put6,
            "x_max_selected_side": x_max,
            "high_n_threshold": HIGH_N_THRESHOLD,
            "high_n_threshold_x": threshold_x,
            "x_raw": x_raw,
            "spot_entry": s0,
            "atm": atm,
            "k_n": k6, "k_n1": k7, "k_n2": k8,
            "lot_size": lot,
            "initial_credit_rupees_raw": x_raw * lot,
            "entry_credit_points_exec": entry_credit_exec,
            "target_rupees": target_rupees,
            "gross_points": gross_points,
            "gross_rupees": gross_rupees,
            "cost_rupees": cost_rupees,
            "net_points": net_rupees / lot,
            "net_rupees": net_rupees,
            "mfe_rupees": mfe,
            "mae_rupees": mae,
            "exit_reason": reason,
            "target_reached": target_reached
        })

    tr = pd.DataFrame(trades)
    s1 = pd.DataFrame(stage1)
    ca = pd.concat(candidates, ignore_index=True) if candidates else pd.DataFrame()
    miss = pd.DataFrame(missing, columns=["expiry", "reason"])

    tr.to_csv(OUT / "trades.csv", index=False)
    s1.to_csv(OUT / "stage1_direction.csv", index=False)
    ca.to_csv(OUT / "stage2_candidates.csv", index=False)
    miss.to_csv(OUT / "missing.csv", index=False)

    if tr.empty:
        pd.DataFrame([{"trades": 0}]).to_csv(OUT / "summary.csv", index=False)
        print("NO_TRADES")
        return

    summary = pd.DataFrame([{
        "trades": len(tr),
        "win_rate_net": float((tr.net_rupees > 0).mean()),
        "mean_net_rupees": float(tr.net_rupees.mean()),
        "median_net_rupees": float(tr.net_rupees.median()),
        "sum_net_rupees": float(tr.net_rupees.sum()),
        "mean_gross_rupees": float(tr.gross_rupees.mean()),
        "sum_gross_rupees": float(tr.gross_rupees.sum()),
        "sum_cost_rupees": float(tr.cost_rupees.sum()),
        "target_exit_rate": float((tr.exit_reason == "TARGET").mean()),
        "mean_x_raw": float(tr.x_raw.mean()),
        "mean_selected_n": float(tr.n.mean()),
        "mean_x_call6": float(tr.x_call6.mean()),
        "mean_x_put6": float(tr.x_put6.mean()),
    }])
    by_direction = tr.groupby("direction").agg(
        trades=("expiry", "count"),
        win_rate_net=("net_rupees", lambda x: float((x > 0).mean())),
        mean_net_rupees=("net_rupees", "mean"),
        sum_net_rupees=("net_rupees", "sum"),
        target_exit_rate=("exit_reason", lambda x: float((x == "TARGET").mean())),
        mean_n=("n", "mean"),
        mean_x=("x_raw", "mean")
    ).reset_index()
    by_n = tr.groupby(["direction", "n"]).agg(
        trades=("expiry", "count"),
        win_rate_net=("net_rupees", lambda x: float((x > 0).mean())),
        mean_net_rupees=("net_rupees", "mean"),
        sum_net_rupees=("net_rupees", "sum")
    ).reset_index()

    summary.to_csv(OUT / "summary.csv", index=False)
    by_direction.to_csv(OUT / "summary_by_direction.csv", index=False)
    by_n.to_csv(OUT / "summary_by_n.csv", index=False)

    print(summary.to_string(index=False))
    print("\nBY DIRECTION")
    print(by_direction.to_string(index=False))
    print("\nBY N")
    print(by_n.to_string(index=False))


if __name__ == "__main__":
    main()
