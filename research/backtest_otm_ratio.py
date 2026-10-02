import os, re

from pathlib import Path
import pandas as pd
import numpy as np
from huggingface_hub import HfApi, hf_hub_download

REPO = "thetrademarkk/india-index-options-1m"
START = pd.Timestamp(os.getenv("START_DATE", "2019-02-14"), tz="Asia/Kolkata")
END = pd.Timestamp(os.getenv("END_DATE", "2026-09-30"), tz="Asia/Kolkata")
OUT = Path("results")
OUT.mkdir(parents=True, exist_ok=True)

N_MIN, N_MAX = 6, 15
TARGET_FRACTION = 0.90
SLIPPAGE_TICKS = float(os.getenv("SLIPPAGE_TICKS", "1"))
TICK = float(os.getenv("OPTION_TICK", "0.05"))

def lot_size_for_expiry(expiry):
    # NSE NIFTY weekly lots for the primary 2024-2025 sample:
    # 25 before the April-2024 revision; 75 for weekly contracts from
    # the Nov-2024 revision through the Dec-2025 weekly expiries.
    if expiry < pd.Timestamp("2021-08-01", tz="Asia/Kolkata"):
        return 75
    if expiry < pd.Timestamp("2024-04-26", tz="Asia/Kolkata"):
        return 50
    if expiry < pd.Timestamp("2025-01-01", tz="Asia/Kolkata"):
        return 25
    if expiry < pd.Timestamp("2026-01-06", tz="Asia/Kolkata"):
        return 75
    return 65

def fee_model(d):
    # Date-aware Indian equity-derivatives charges used for research.
    # STT is applied to option sell turnover; rates are kept explicit so
    # later phases can sensitivity-test them.
    if d >= pd.Timestamp("2026-04-01", tz="Asia/Kolkata"):
        stt = 0.0015
    elif d >= pd.Timestamp("2024-10-01", tz="Asia/Kolkata"):
        stt = 0.0010
    else:
        stt = 0.000625

    txn = 0.0003503 if d >= pd.Timestamp("2024-10-01", tz="Asia/Kolkata") else 0.000495
    sebi = 0.000001
    ipft = 0.000001
    stamp = 0.00003
    return stt, txn, sebi, ipft, stamp

def exec_px(px, action):
    # Conservative one-tick adverse execution on every leg.
    if action == "buy":
        return max(0.0, px + SLIPPAGE_TICKS * TICK)
    return max(0.0, px - SLIPPAGE_TICKS * TICK)

def charges(entry, exit_, d, lot):
    stt, txn, sebi, ipft, stamp = fee_model(d)
    turnover = sum(p for _, p in entry + exit_) * lot
    sells = sum(p for side, p in entry + exit_ if side == "sell") * lot
    buys = sum(p for side, p in entry + exit_ if side == "buy") * lot

    # Paytm Money: Rs 10 per unique executed F&O order. Six orders for
    # a complete three-leg entry + three-leg exit.
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
        df["timestamp"] = df["timestamp"].dt.tz_localize("Asia/Kolkata")
    else:
        df["timestamp"] = df["timestamp"].dt.tz_convert("Asia/Kolkata")
    return df

def normalize_strikes(df):
    df = df.copy()
    df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
    df["option_type"] = df["option_type"].astype(str).str.upper()
    return df

def candidate_table(strikes, atm, option_df, entry_ts):
    puts = sorted([x for x in strikes if x < atm], reverse=True)
    calls = sorted([x for x in strikes if x > atm])

    if len(puts) < N_MAX + 2 or len(calls) < N_MAX + 2:
        return None

    # Rank 1 is nearest OTM strike. n=15 therefore needs OTM17.
    rows = []
    for n in range(N_MIN, N_MAX + 1):
        pks = (puts[n-1], puts[n], puts[n+1])
        cks = (calls[n-1], calls[n], calls[n+1])

        for side, typ, ks in [
            ("PUT", "PE", pks),
            ("CALL", "CE", cks),
        ]:
            q = option_df[
                (option_df["timestamp"] == entry_ts)
                & (option_df["option_type"] == typ)
                & (option_df["strike"].isin(ks))
            ]
            vals = {float(r.strike): float(r.close) for _, r in q.iterrows()}
            if any(k not in vals for k in ks):
                continue

            x = vals[ks[1]] + vals[ks[2]] - vals[ks[0]]
            rows.append({
                "side": side,
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

def p_and_l(side, entry_exec, exit_exec):
    # Position: +long n, -short n+1, -short n+2.
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
            d = pd.Timestamp(m.group(1), tz="Asia/Kolkata")
            if START <= d <= END:
                expiries.append(d)

    expiry_set = sorted(set(expiries))
    monthly_expiries = set()
    for y, m in sorted({(d.year, d.month) for d in expiry_set}):
        month_dates = [d for d in expiry_set if d.year == y and d.month == m]
        if month_dates:
            monthly_expiries.add(max(month_dates))
    expiries = [d for d in expiry_set if d not in monthly_expiries]

    trades = []
    candidates = []
    missing = []

    for expiry in sorted(set(expiries)):
        # Base convention: count the expiry session as session 1.
        # Ordinary Thursday weekly expiries therefore enter Monday 10:00.
        week_start = expiry - pd.Timedelta(days=8)
        session_dates = sorted(
            pd.to_datetime(
                spot[
                    (spot.timestamp >= week_start)
                    & (spot.timestamp <= expiry)
                ].timestamp.dt.normalize().unique()
            )
        )
        if len(session_dates) < 4:
            missing.append([str(expiry.date()), "fewer than 4 trading sessions"])
            continue

        entry_date = session_dates[-4]
        entry_ts = entry_date + pd.Timedelta(hours=10)

        sr = spot[spot.timestamp == entry_ts]
        if sr.empty:
            missing.append([str(expiry.date()), "missing 10:00 spot"])
            continue

        s0 = float(sr.iloc[0].spot)

        try:
            df = normalize_strikes(load(
                f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet"
            ))
        except Exception as e:
            missing.append([str(expiry.date()), "download/read " + repr(e)])
            continue

        entry_quotes = df[df["timestamp"] == entry_ts]
        strikes = sorted(entry_quotes["strike"].dropna().unique())
        atm = min(strikes, key=lambda x: abs(x - s0))

        cand = candidate_table(strikes, atm, df, entry_ts)
        if cand is None:
            missing.append([str(expiry.date()), "fewer than OTM17 strikes"])
            continue

        cand.insert(0, "expiry", str(expiry.date()))
        cand["entry_ts"] = str(entry_ts)
        cand["spot_entry"] = s0
        cand["atm"] = atm
        candidates.append(cand)

        # Global maximum over all n=6..15 and both sides.
        # Deterministic tie-break: PUT before CALL, then smaller n.
        cand["_side_order"] = cand["side"].map({"PUT": 0, "CALL": 1})
        selected = cand.sort_values(
            ["x", "_side_order", "n"],
            ascending=[False, True, True]
        ).iloc[0]

        side = selected["side"]
        n = int(selected["n"])
        k6, k7, k8 = float(selected["k_n"]), float(selected["k_n1"]), float(selected["k_n2"])
        p6, p7, p8 = float(selected["p_n"]), float(selected["p_n1"]), float(selected["p_n2"])
        x_raw = float(selected["x"])
        lot = lot_size_for_expiry(expiry)

        # Entry execution includes slippage, but target definition remains
        # exactly 90% of the collected raw X credit as requested.
        ep6, ep7, ep8 = exec_px(p6, "buy"), exec_px(p7, "sell"), exec_px(p8, "sell")
        entry_credit_points_exec = ep7 + ep8 - ep6
        initial_credit_rupees = x_raw * lot
        target_rupees = TARGET_FRACTION * initial_credit_rupees

        typ = "PE" if side == "PUT" else "CE"
        end_ts = expiry.normalize() + pd.Timedelta(hours=15, minutes=29)
        q = df[
            (df["timestamp"] >= entry_ts)
            & (df["timestamp"] <= end_ts)
            & (df["option_type"] == typ)
            & (df["strike"].isin([k6, k7, k8]))
        ]

        piv = q.pivot_table(
            index="timestamp",
            columns="strike",
            values="close",
            aggfunc="last"
        ).dropna(subset=[k6, k7, k8])

        if piv.empty:
            missing.append([str(expiry.date()), "no complete selected 3-leg minute series"])
            continue

        exit_ts = piv.index[-1]
        reason = "EXPIRY"
        xp = None
        target_reached = False
        mfe_rupees = -np.inf
        mae_rupees = np.inf

        for ts, row in piv.iterrows():
            m6, m7, m8 = float(row[k6]), float(row[k7]), float(row[k8])
            ex6, ex7, ex8 = exec_px(m6, "sell"), exec_px(m7, "buy"), exec_px(m8, "buy")
            pnl_points = p_and_l(side, (ep6, ep7, ep8), (ex6, ex7, ex8))
            pnl_rupees = pnl_points * lot
            mfe_rupees = max(mfe_rupees, pnl_rupees)
            mae_rupees = min(mae_rupees, pnl_rupees)

            if pnl_rupees >= target_rupees:
                exit_ts = ts
                reason = "TARGET"
                xp = (m6, m7, m8)
                target_reached = True
                break

        if xp is None:
            r = piv.loc[exit_ts]
            xp = (float(r[k6]), float(r[k7]), float(r[k8]))

        xp6, xp7, xp8 = exec_px(xp[0], "sell"), exec_px(xp[1], "buy"), exec_px(xp[2], "buy")
        gross_points = p_and_l(side, (ep6, ep7, ep8), (xp6, xp7, xp8))
        gross_rupees = gross_points * lot

        cost_rupees = charges(
            [("buy", ep6), ("sell", ep7), ("sell", ep8)],
            [("sell", xp6), ("buy", xp7), ("buy", xp8)],
            entry_ts,
            lot,
        )
        net_rupees = gross_rupees - cost_rupees

        trades.append({
            "expiry": str(expiry.date()),
            "entry_ts": str(entry_ts),
            "exit_ts": str(exit_ts),
            "side": side,
            "n": n,
            "spot_entry": s0,
            "atm": atm,
            "k_n": k6,
            "k_n1": k7,
            "k_n2": k8,
            "x_raw": x_raw,
            "lot_size": lot,
            "initial_credit_rupees": initial_credit_rupees,
            "target_rupees": target_rupees,
            "entry_credit_points_exec": entry_credit_points_exec,
            "gross_points": gross_points,
            "gross_rupees": gross_rupees,
            "cost_rupees": cost_rupees,
            "net_rupees": net_rupees,
            "net_points": net_rupees / lot,
            "mfe_rupees": mfe_rupees,
            "mae_rupees": mae_rupees,
            "exit_reason": reason,
            "target_reached": target_reached,
        })

    tr = pd.DataFrame(trades)
    ca = pd.concat(candidates, ignore_index=True) if candidates else pd.DataFrame()
    tr.to_csv(OUT / "trades.csv", index=False)
    ca.to_csv(OUT / "all_candidates.csv", index=False)
    pd.DataFrame(missing, columns=["expiry", "reason"]).to_csv(OUT / "missing.csv", index=False)

    if not tr.empty:
        summary = pd.DataFrame([{
            "trades": len(tr),
            "win_rate": float((tr.net_rupees > 0).mean()),
            "mean_net_rupees": float(tr.net_rupees.mean()),
            "median_net_rupees": float(tr.net_rupees.median()),
            "sum_net_rupees": float(tr.net_rupees.sum()),
            "mean_gross_rupees": float(tr.gross_rupees.mean()),
            "sum_cost_rupees": float(tr.cost_rupees.sum()),
            "target_exit_rate": float((tr.exit_reason == "TARGET").mean()),
            "mean_x": float(tr.x_raw.mean()),
            "mean_n": float(tr.n.mean()),
        }])
        by_side = tr.groupby("side").agg(
            trades=("expiry", "count"),
            win_rate=("net_rupees", lambda x: float((x > 0).mean())),
            mean_net_rupees=("net_rupees", "mean"),
            median_net_rupees=("net_rupees", "median"),
            sum_net_rupees=("net_rupees", "sum"),
            target_exit_rate=("exit_reason", lambda x: float((x == "TARGET").mean())),
        ).reset_index()
        by_n = tr.groupby(["side", "n"]).agg(
            trades=("expiry", "count"),
            win_rate=("net_rupees", lambda x: float((x > 0).mean())),
            mean_net_rupees=("net_rupees", "mean"),
            sum_net_rupees=("net_rupees", "sum"),
        ).reset_index()

        summary.to_csv(OUT / "summary.csv", index=False)
        by_side.to_csv(OUT / "summary_by_side.csv", index=False)
        by_n.to_csv(OUT / "summary_by_n.csv", index=False)

        print(summary.to_string(index=False))
        print("\nBY SIDE")
        print(by_side.to_string(index=False))
        print("\nTRADES", len(tr), "NET_RUPEES", tr.net_rupees.sum())
    else:
        pd.DataFrame().to_csv(OUT / "summary.csv", index=False)
        print("NO_TRADES")

if __name__ == "__main__":
    main()
