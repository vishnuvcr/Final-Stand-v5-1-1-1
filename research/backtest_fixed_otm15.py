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
OUT = Path(os.getenv("OUT_DIR", "results/fixed_otm15_v3"))
OUT.mkdir(parents=True, exist_ok=True)

ENTRY_HOUR = int(os.getenv("ENTRY_HOUR", "10"))
ENTRY_MINUTE = int(os.getenv("ENTRY_MINUTE", "0"))
DTE_SESSIONS = int(os.getenv("DTE_SESSIONS", "4"))
SLIPPAGE_TICKS = float(os.getenv("SLIPPAGE_TICKS", "1"))
TICK = float(os.getenv("OPTION_TICK", "0.05"))
BROKERAGE_PER_ORDER = float(os.getenv("BROKERAGE_PER_ORDER", "10"))
TARGET_FRACTION = float(os.getenv("TARGET_FRACTION", "0.90"))
STRIKE_INTERVAL = float(os.getenv("NIFTY_STRIKE_INTERVAL", "50"))


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
    txn = 0.0003503 if d >= pd.Timestamp("2024-10-01", tz=TZ) else 0.000495
    return stt, txn, 0.000001, 0.000001, 0.00003


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
    df = df.copy()
    df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
    df["option_type"] = df["option_type"].astype(str).str.upper()
    return df


def nearest_atm_strike(entry_quotes, spot):
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
    e15, e16, e17 = entry_exec
    x15, x16, x17 = exit_exec
    return (e15 - x15) + (x16 - e16) + (x17 - e17)


def main():
    spot = load("index/NIFTY.parquet")[["timestamp", "close"]].rename(columns={"close": "spot"})
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

    trades, stage1, missing = [], [], []

    for expiry in expiries:
        window_start = expiry - pd.Timedelta(days=14)
        session_dates = sorted(pd.to_datetime(
            spot[(spot.timestamp >= window_start) & (spot.timestamp <= expiry)].timestamp.dt.normalize().unique()
        ))
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
        s0 = float(sr.iloc[0].spot)

        try:
            df = normalize(load(f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet"))
        except Exception as e:
            missing.append([str(expiry.date()), "download/read " + repr(e)])
            continue

        entry_quotes = df[df["timestamp"] == entry_ts]
        if entry_quotes.empty:
            missing.append([str(expiry.date()), "missing entry option snapshot"])
            continue

        atm = nearest_atm_strike(entry_quotes, s0)
        if atm is None:
            missing.append([str(expiry.date()), "missing ATM strike at entry snapshot"])
            continue

        put_strikes = (atm - 15 * STRIKE_INTERVAL, atm - 16 * STRIKE_INTERVAL, atm - 17 * STRIKE_INTERVAL)
        call_strikes = (atm + 15 * STRIKE_INTERVAL, atm + 16 * STRIKE_INTERVAL, atm + 17 * STRIKE_INTERVAL)

        p = prices_at(df, entry_ts, "PE", put_strikes)
        c = prices_at(df, entry_ts, "CE", call_strikes)
        if len(p) < 3 or len(c) < 3:
            missing.append([str(expiry.date()), "missing one or more exact OTM15/16/17 entry prices"])
            continue

        x_put = p[put_strikes[2]] + p[put_strikes[1]] - p[put_strikes[0]]
        x_call = c[call_strikes[2]] + c[call_strikes[1]] - c[call_strikes[0]]

        if x_call > x_put:
            direction, typ, side = "BEARISH", "CE", "CALL"
            strikes = call_strikes
            raw_prices = (c[call_strikes[0]], c[call_strikes[1]], c[call_strikes[2]])
            x = x_call
        elif x_call < x_put:
            direction, typ, side = "BULLISH", "PE", "PUT"
            strikes = put_strikes
            raw_prices = (p[put_strikes[0]], p[put_strikes[1]], p[put_strikes[2]])
            x = x_put
        else:
            stage1.append({"expiry": str(expiry.date()), "entry_ts": str(entry_ts), "spot_entry": s0,
                           "atm": atm, "x_call": x_call, "x_put": x_put, "direction": "NO_TRADE_TIE"})
            missing.append([str(expiry.date()), "Stage 1 exact X tie"])
            continue

        stage1.append({"expiry": str(expiry.date()), "entry_ts": str(entry_ts), "spot_entry": s0,
                       "atm": atm, "x_call": x_call, "x_put": x_put, "direction": direction})

        if x <= 0:
            missing.append([str(expiry.date()), "NO_POSITIVE_X"])
            continue

        lot = lot_size_for_expiry(expiry)
        target_rupees = TARGET_FRACTION * x * lot

        k15, k16, k17 = strikes
        q15, q16, q17 = raw_prices
        ep15 = exec_px(q15, "buy")
        ep16 = exec_px(q16, "sell")
        ep17 = exec_px(q17, "sell")

        end_ts = expiry.normalize() + pd.Timedelta(hours=15, minutes=29)
        q = df[
            (df["timestamp"] >= entry_ts)
            & (df["timestamp"] <= end_ts)
            & (df["option_type"] == typ)
            & (df["strike"].isin([k15, k16, k17]))
        ]
        piv = q.pivot_table(index="timestamp", columns="strike", values="close", aggfunc="last")
        piv = piv.dropna(subset=[k15, k16, k17])
        if piv.empty:
            missing.append([str(expiry.date()), "no complete selected 3-leg minute series"])
            continue

        exit_ts = piv.index[-1]
        reason = "EXPIRY"
        target_reached = False
        xp_raw = None
        mfe = -np.inf
        mae = np.inf

        for ts, row in piv.iterrows():
            if ts <= entry_ts:
                continue
            m15, m16, m17 = float(row[k15]), float(row[k16]), float(row[k17])
            ex15, ex16, ex17 = exec_px(m15, "sell"), exec_px(m16, "buy"), exec_px(m17, "buy")
            gross = pnl_points((ep15, ep16, ep17), (ex15, ex16, ex17)) * lot
            mfe = max(mfe, gross)
            mae = min(mae, gross)
            if gross >= target_rupees:
                exit_ts = ts
                reason = "TARGET"
                target_reached = True
                xp_raw = (m15, m16, m17)
                break

        if xp_raw is None:
            r = piv.loc[exit_ts]
            xp_raw = (float(r[k15]), float(r[k16]), float(r[k17]))

        xp15, xp16, xp17 = exec_px(xp_raw[0], "sell"), exec_px(xp_raw[1], "buy"), exec_px(xp_raw[2], "buy")
        gross_points = pnl_points((ep15, ep16, ep17), (xp15, xp16, xp17))
        gross_rupees = gross_points * lot

        entry_orders = [
            (entry_ts, "buy", ep15), (entry_ts, "sell", ep16), (entry_ts, "sell", ep17)
        ]
        exit_orders = [
            (exit_ts, "sell", xp15), (exit_ts, "buy", xp16), (exit_ts, "buy", xp17)
        ]
        cost_rupees = charges(entry_orders, exit_orders, lot)
        net_rupees = gross_rupees - cost_rupees

        trades.append({
            "expiry": str(expiry.date()), "entry_ts": str(entry_ts), "exit_ts": str(exit_ts),
            "direction": direction, "side": side, "x_call": x_call, "x_put": x_put, "x_selected": x,
            "spot_entry": s0, "atm": atm, "k15": k15, "k16": k16, "k17": k17,
            "p15_raw": q15, "p16_raw": q16, "p17_raw": q17, "lot_size": lot,
            "target_rupees": target_rupees, "gross_points": gross_points, "gross_rupees": gross_rupees,
            "cost_rupees": cost_rupees, "net_rupees": net_rupees, "net_points": net_rupees / lot,
            "mfe_rupees": mfe, "mae_rupees": mae, "exit_reason": reason, "target_reached": target_reached,
            "slippage_ticks": SLIPPAGE_TICKS, "brokerage_per_order": BROKERAGE_PER_ORDER,
            "target_fraction": TARGET_FRACTION
        })

    tr = pd.DataFrame(trades)
    pd.DataFrame(stage1).to_csv(OUT / "stage1_direction.csv", index=False)
    pd.DataFrame(missing, columns=["expiry", "reason"]).to_csv(OUT / "missing.csv", index=False)
    tr.to_csv(OUT / "trades.csv", index=False)

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
        "expiry_exit_rate": float((tr.exit_reason == "EXPIRY").mean()),
        "mean_x_selected": float(tr.x_selected.mean()),
        "mean_lot_size": float(tr.lot_size.mean()),
        "slippage_ticks": SLIPPAGE_TICKS,
        "brokerage_per_order": BROKERAGE_PER_ORDER,
        "target_fraction": TARGET_FRACTION,
        "dte_sessions": DTE_SESSIONS,
        "entry_hour": ENTRY_HOUR,
        "entry_minute": ENTRY_MINUTE
    }])
    by_direction = tr.groupby("direction").agg(
        trades=("expiry", "count"),
        win_rate_net=("net_rupees", lambda x: float((x > 0).mean())),
        mean_net_rupees=("net_rupees", "mean"),
        sum_net_rupees=("net_rupees", "sum"),
        target_exit_rate=("exit_reason", lambda x: float((x == "TARGET").mean())),
        mean_x=("x_selected", "mean")
    ).reset_index()
    by_exit = tr.groupby("exit_reason").agg(
        trades=("expiry", "count"),
        mean_net_rupees=("net_rupees", "mean"),
        sum_net_rupees=("net_rupees", "sum"),
        win_rate_net=("net_rupees", lambda x: float((x > 0).mean()))
    ).reset_index()

    summary.to_csv(OUT / "summary.csv", index=False)
    by_direction.to_csv(OUT / "summary_by_direction.csv", index=False)
    by_exit.to_csv(OUT / "summary_by_exit_reason.csv", index=False)
    print(summary.to_string(index=False))
    print("\nBY DIRECTION\n", by_direction.to_string(index=False))
    print("\nBY EXIT\n", by_exit.to_string(index=False))


if __name__ == "__main__":
    main()
