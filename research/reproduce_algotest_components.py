import os
import re
from pathlib import Path
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

REPO = "thetrademarkk/india-index-options-1m"
TZ = "Asia/Kolkata"
START = pd.Timestamp(os.getenv("START_DATE", "2021-05-27"), tz=TZ)
END = pd.Timestamp(os.getenv("END_DATE", "2026-09-30"), tz=TZ)
ENTRY_HOUR = int(os.getenv("ENTRY_HOUR", "9"))
ENTRY_MINUTE = int(os.getenv("ENTRY_MINUTE", "35"))
EXIT_HOUR = int(os.getenv("EXIT_HOUR", "15"))
EXIT_MINUTE = int(os.getenv("EXIT_MINUTE", "14"))
DTE_SESSIONS = int(os.getenv("DTE_SESSIONS", "4"))
LOT = int(os.getenv("FIXED_LOT", "65"))
STRIKE_INTERVAL = float(os.getenv("NIFTY_STRIKE_INTERVAL", "50"))

OUT = Path(os.getenv("OUT_DIR", "results/fixed_otm15_v3/phase9b"))
OUT.mkdir(parents=True, exist_ok=True)


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


def leg_pnl(direction, entry_prices, exit_prices):
    # Long OTM15 is closed with a sell: exit - entry.
    # Short OTM16/17 are closed with buys: entry - exit.
    e15, e16, e17 = entry_prices
    x15, x16, x17 = exit_prices
    return ((x15 - e15) + (e16 - x16) + (e17 - x17)) * LOT


def get_weekly_expiries(api):
    expiries = []
    for f in api.list_repo_files(REPO, repo_type="dataset"):
        m = re.match(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet$", f)
        if m:
            d = pd.Timestamp(m.group(1), tz=TZ)
            if START <= d <= END:
                expiries.append(d)
    expiry_set = sorted(set(expiries))
    # Include every expiry file, including month-end weekly/monthly expiry dates.
    return expiry_set


def run_component(spot, expiry_list, typ, label):
    trades = []
    missing = []
    for expiry in expiry_list:
        window_start = expiry - pd.Timedelta(days=14)
        session_dates = sorted(pd.to_datetime(
            spot[
                (spot.timestamp >= window_start) &
                (spot.timestamp <= expiry)
            ].timestamp.dt.normalize().unique()
        ))
        pre_expiry = [d for d in session_dates if d < expiry.normalize()]
        if len(pre_expiry) < DTE_SESSIONS:
            missing.append([str(expiry.date()), "fewer than required pre-expiry sessions"])
            continue

        entry_date = pre_expiry[-DTE_SESSIONS]
        entry_ts = entry_date + pd.Timedelta(hours=ENTRY_HOUR, minutes=ENTRY_MINUTE)
        exit_deadline = expiry.normalize() + pd.Timedelta(hours=EXIT_HOUR, minutes=EXIT_MINUTE)

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

        entry_quotes = df[df.timestamp == entry_ts]
        if entry_quotes.empty:
            missing.append([str(expiry.date()), "missing entry option snapshot"])
            continue

        atm = nearest_atm_strike(entry_quotes, s0)
        if atm is None:
            missing.append([str(expiry.date()), "missing ATM strike at entry snapshot"])
            continue

        if typ == "CE":
            k15, k16, k17 = atm + 15 * STRIKE_INTERVAL, atm + 16 * STRIKE_INTERVAL, atm + 17 * STRIKE_INTERVAL
        else:
            k15, k16, k17 = atm - 15 * STRIKE_INTERVAL, atm - 16 * STRIKE_INTERVAL, atm - 17 * STRIKE_INTERVAL

        # Match AlgoTest's fixed OTM15/16/17 semantics on the NIFTY ₹50 strike ladder.
        px = prices_at(df, entry_ts, typ, (k15, k16, k17))
        if len(px) < 3:
            missing.append([str(expiry.date()), "missing one or more entry leg prices"])
            continue

        e15, e16, e17 = px[k15], px[k16], px[k17]

        q = df[
            (df.timestamp >= entry_ts) &
            (df.timestamp <= exit_deadline) &
            (df.option_type == typ) &
            (df.strike.isin([k15, k16, k17]))
        ]
        piv = q.pivot_table(index="timestamp", columns="strike", values="close", aggfunc="last")
        piv = piv.dropna(subset=[k15, k16, k17])
        if piv.empty:
            missing.append([str(expiry.date()), "no complete 3-leg series through 15:14"])
            continue

        # AlgoTest report uses the fixed 15:14 expiry-day exit when available.
        eligible = piv[piv.index <= exit_deadline]
        if eligible.empty:
            missing.append([str(expiry.date()), "no complete observation at or before 15:14"])
            continue
        exit_ts = eligible.index[-1]
        r = eligible.loc[exit_ts]
        x15, x16, x17 = float(r[k15]), float(r[k16]), float(r[k17])
        pnl = leg_pnl(label, (e15, e16, e17), (x15, x16, x17))

        trades.append({
            "expiry": str(expiry.date()),
            "entry_date": str(entry_date.date()),
            "entry_ts": str(entry_ts),
            "exit_ts": str(exit_ts),
            "side": label,
            "option_type": typ,
            "spot_entry": s0,
            "atm": atm,
            "k15": k15, "k16": k16, "k17": k17,
            "e15": e15, "e16": e16, "e17": e17,
            "x15": x15, "x16": x16, "x17": x17,
            "lot": LOT,
            "gross_pnl_rupees": pnl,
        })

    tr = pd.DataFrame(trades)
    miss = pd.DataFrame(missing, columns=["expiry", "reason"])
    tr.to_csv(OUT / f"{label.lower()}_trades.csv", index=False)
    miss.to_csv(OUT / f"{label.lower()}_missing.csv", index=False)

    summary = {
        "side": label,
        "trades": len(tr),
        "sum_gross_pnl_rupees": float(tr.gross_pnl_rupees.sum()) if not tr.empty else 0.0,
        "mean_gross_pnl_rupees": float(tr.gross_pnl_rupees.mean()) if not tr.empty else 0.0,
        "median_gross_pnl_rupees": float(tr.gross_pnl_rupees.median()) if not tr.empty else 0.0,
        "win_rate": float((tr.gross_pnl_rupees > 0).mean()) if not tr.empty else 0.0,
        "loss_rate": float((tr.gross_pnl_rupees < 0).mean()) if not tr.empty else 0.0,
        "start": str(START.date()),
        "end": str(END.date()),
        "entry": f"{ENTRY_HOUR:02d}:{ENTRY_MINUTE:02d}",
        "exit": f"{EXIT_HOUR:02d}:{EXIT_MINUTE:02d}",
        "dte_sessions": DTE_SESSIONS,
        "fixed_lot": LOT,
        "slippage": 0.0,
        "brokerage": 0.0,
    }
    return tr, miss, summary


def main():
    spot = load("index/NIFTY.parquet")[["timestamp", "close"]].rename(columns={"close": "spot"})
    api = HfApi(token=os.getenv("HF_TOKEN") or None)
    expiry_list = get_weekly_expiries(api)

    put_tr, put_miss, put_sum = run_component(spot, expiry_list, "PE", "PUT")
    call_tr, call_miss, call_sum = run_component(spot, expiry_list, "CE", "CALL")

    # Store aggregate summary and a direct report-vs-overlap benchmark.
    report = pd.DataFrame([
        {**put_sum, "algotest_reported_trades": 218, "algotest_reported_profit": 138258.25, "algotest_reported_win_rate": 0.9954},
        {**call_sum, "algotest_reported_trades": 218, "algotest_reported_profit": 43267.25, "algotest_reported_win_rate": 0.9908},
    ])
    report.to_csv(OUT / "component_comparison.csv", index=False)

    meta = pd.DataFrame([{
        "hf_start_used": str(START.date()),
        "hf_end_used": str(END.date()),
        "weekly_expiries_tested": len(expiry_list),
        "put_completed": len(put_tr),
        "call_completed": len(call_tr),
        "put_missing_expiries": len(put_miss),
        "call_missing_expiries": len(call_miss),
        "note": "AlgoTest report covers 2021-01-01 through 2026-10-03; this reproduction uses the validated HF executable overlap 2021-05-27 through 2026-09-30.",
    }])
    meta.to_csv(OUT / "reproduction_metadata.csv", index=False)

    print(report.to_string(index=False))
    print(meta.to_string(index=False))


if __name__ == "__main__":
    main()
