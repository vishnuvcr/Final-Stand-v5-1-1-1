import os, json, sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, "research")
import phase32_continuous_delta_6x6_backtest as base

TZ = base.TZ
START = pd.Timestamp((os.getenv("SAMPLE_START") or "2024-01-01"), tz=TZ)
END = pd.Timestamp((os.getenv("SAMPLE_END") or "2026-06-30"), tz=TZ)
SELECTOR = os.getenv("SELECTOR", "CATBOOST").upper()
OUT_ROOT = Path("results/phase37_model_direction_polarity_correction") / SELECTOR
OUT_ROOT.mkdir(parents=True, exist_ok=True)

MODEL_COLS = {
    "CATBOOST": "catboost_prob",
    "DART": "dart_prob",
    "WAVELET_TREE": "wavelet_tree_prob",
    "OOF_STACK": "stack_prob",
    "MARKOV_REGIME_TREE": "ms_regime_tree_prob",
}
VALID_SELECTORS = set(MODEL_COLS)


def load_cache():
    p = Path("data/phase36_selector_predictions.csv")
    if not p.exists():
        raise FileNotFoundError(p)
    z = pd.read_csv(p)
    z["expiry_date"] = pd.to_datetime(z["expiry"], errors="coerce").dt.tz_convert(TZ).dt.date
    return z


def choose_direction(selector, expiry, selector_map):
    row = selector_map.get(expiry.date())
    if row is None:
        return np.nan, "model_missing_expiry"
    p = float(row[MODEL_COLS[selector]])
    if not np.isfinite(p):
        return np.nan, "model_missing_probability"

    # Corrected economic polarity:
    # p >= 0.50 means NIFTY bullish/up -> PUT credit spread.
    # p < 0.50 means NIFTY bearish/down -> CALL credit spread.
    target_dir = -1 if p >= 0.50 else 1
    return target_dir, f"{selector.lower()}_expiry_frozen_corrected_polarity"


def run_expiry(expiry, option_df, spot_df, selector_map, selector, window_start):
    df = option_df.copy()
    expiry_ts = expiry + pd.Timedelta(hours=15, minutes=30)
    df["expiry_ts"] = expiry_ts

    timeline = (
        spot_df[
            (spot_df.timestamp > window_start)
            & (spot_df.timestamp <= expiry + pd.Timedelta(hours=15, minutes=29))
        ]
        .drop_duplicates("timestamp")
        .reset_index(drop=True)
    )

    trades, skips, cursor = [], [], 0

    while cursor < len(timeline):
        ts = pd.Timestamp(timeline.at[cursor, "timestamp"])
        day = ts.normalize()

        if day == expiry.normalize():
            break

        if ts.hour < base.ENTRY_HOUR or (
            ts.hour == base.ENTRY_HOUR and ts.minute < base.ENTRY_MINUTE
        ):
            cursor += 1
            continue

        if ts.hour > base.LAST_ENTRY_HOUR or (
            ts.hour == base.LAST_ENTRY_HOUR and ts.minute >= base.LAST_ENTRY_MINUTE
        ):
            cursor += 1
            continue

        snap = df[df.timestamp == ts]
        if snap.empty:
            cursor += 1
            continue

        target_dir, source = choose_direction(selector, expiry, selector_map)
        if not np.isfinite(target_dir):
            skips.append([str(ts), "missing_direction_selector", source])
            cursor += 1
            continue

        spot = float(timeline.at[cursor, "spot"])
        typ = "CE" if target_dir == 1 else "PE"
        target = 0.25 if typ == "CE" else -0.25

        found = base.nearest_delta_strike(snap, spot, ts, typ, target)
        if found is None:
            skips.append([str(ts), "no_entry_delta", ""])
            cursor += 1
            continue

        short_k, entry_delta = found
        long_k = short_k + base.WIDTH if typ == "CE" else short_k - base.WIDTH

        legs = df[
            (df.timestamp == ts)
            & (df.option_type == typ)
            & (df.strike.isin([short_k, long_k]))
        ]
        if len(legs) < 2:
            skips.append([str(ts), "missing_entry_legs", ""])
            cursor += 1
            continue

        q = {}
        for _, x in legs.iterrows():
            q[float(x.strike)] = float(x.close)

        if short_k not in q or long_k not in q:
            skips.append([str(ts), "missing_entry_prices", ""])
            cursor += 1
            continue

        short_entry = q[short_k]
        long_entry = q[long_k]
        lot = base.lot_size_for_expiry(expiry)

        path = (
            df[
                (df.timestamp > ts)
                & (df.timestamp <= expiry + pd.Timedelta(hours=15, minutes=29))
                & (df.option_type == typ)
                & (df.strike.isin([short_k, long_k]))
            ]
            .pivot_table(
                index="timestamp",
                columns="strike",
                values="close",
                aggfunc="last",
            )
            .dropna(subset=[short_k, long_k])
        )

        if path.empty:
            skips.append([str(ts), "no_complete_exit_path", ""])
            break

        path = (
            path.reset_index()
            .merge(timeline[["timestamp", "spot"]], on="timestamp", how="inner")
            .sort_values("timestamp")
            .reset_index(drop=True)
        )

        tleft = np.maximum(
            (expiry_ts - pd.to_datetime(path.timestamp))
            .dt.total_seconds()
            .to_numpy(float)
            / 31557600.0,
            1e-10,
        )

        deltas = base.implied_delta(
            path[short_k].to_numpy(float),
            path.spot.to_numpy(float),
            np.full(len(path), short_k, float),
            tleft,
            typ,
        )

        if typ == "CE":
            hit = (deltas >= 0.50) | (deltas <= 0.04)
        else:
            hit = (deltas <= -0.50) | (deltas >= -0.04)

        hit_idx = np.flatnonzero(np.isfinite(deltas) & hit)
        if len(hit_idx):
            eidx = int(hit_idx[0])
            exit_row = path.iloc[eidx]
            exit_delta = float(deltas[eidx])
            exit_reason = "DELTA_EXIT"
        else:
            exit_row = path.iloc[-1]
            exit_delta = np.nan
            exit_reason = "CONTRACT_EXPIRY"

        exit_ts = pd.Timestamp(exit_row.timestamp)

        ep_long = base.exec_px(long_entry, "buy")
        ep_short = base.exec_px(short_entry, "sell")
        xp_short = base.exec_px(float(exit_row[short_k]), "buy")
        xp_long = base.exec_px(float(exit_row[long_k]), "sell")

        gross = ((ep_short - xp_short) + (xp_long - ep_long)) * lot * base.LOTS
        orders = [
            (ts, "sell", ep_short),
            (ts, "buy", ep_long),
            (exit_ts, "buy", xp_short),
            (exit_ts, "sell", xp_long),
        ]
        cost = base.charges(orders, lot)
        net = gross - cost

        trades.append(
            {
                "expiry": str(expiry.date()),
                "entry_ts": str(ts),
                "exit_ts": str(exit_ts),
                "direction": "CALL" if typ == "CE" else "PUT",
                "selector": selector,
                "selector_probability": float(
                    selector_map[expiry.date()][MODEL_COLS[selector]]
                ),
                "selector_source": source,
                "short_delta_entry": entry_delta,
                "short_delta_exit": exit_delta,
                "short_strike": short_k,
                "long_strike": long_k,
                "lot_size": lot,
                "gross_rupees": gross,
                "cost_rupees": cost,
                "net_rupees": net,
                "exit_reason": exit_reason,
            }
        )

        future_idx = np.flatnonzero(timeline.timestamp.to_numpy() == exit_ts)
        if len(future_idx) == 0:
            break
        cursor = int(future_idx[0]) + 1

    return trades, skips


def main():
    if SELECTOR not in VALID_SELECTORS:
        raise ValueError(f"Unknown SELECTOR={SELECTOR}; valid={sorted(VALID_SELECTORS)}")

    cache = load_cache()
    selector_map = {
        pd.Timestamp(r.expiry).date(): r for _, r in cache.iterrows()
    }

    api = base.HfApi(token=os.getenv("HF_TOKEN") or None)
    spot = base.load("index/NIFTY.parquet")[["timestamp", "close"]].rename(
        columns={"close": "spot"}
    )

    expected = [
        e for e in base.expected_weekly_expiries(spot) if START <= e <= END
    ]
    available = base.available_expiry_files(api)

    all_trades, all_skips, processed = [], [], 0

    for expiry in expected:
        if expiry not in available:
            all_skips.append(
                [str(expiry.date()), "", "missing_expiry_file", ""]
            )
            continue

        try:
            od = base.load(f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet")
            od["option_type"] = od.option_type.astype(str).str.upper()
            od["strike"] = pd.to_numeric(od.strike, errors="coerce")
            od = od.dropna(subset=["strike", "timestamp", "close"])

            option_max = od.timestamp.max()
            required_last = expiry + pd.Timedelta(hours=15, minutes=29)
            if pd.isna(option_max) or option_max < required_last:
                all_skips.append(
                    [
                        str(expiry.date()),
                        "",
                        "incomplete_expiry_data",
                        f"last={option_max}",
                    ]
                )
                continue

            idx = expected.index(expiry)
            window_start = (
                expiry - pd.Timedelta(days=7)
                if idx == 0
                else expected[idx - 1] + pd.Timedelta(hours=15, minutes=30)
            )

            sd = spot[
                (spot.timestamp > window_start)
                & (spot.timestamp <= required_last)
            ].copy()

            if sd.empty or sd.timestamp.max() < required_last:
                all_skips.append(
                    [str(expiry.date()), "", "incomplete_spot_data", ""]
                )
                continue

            tr, sk = run_expiry(
                expiry, od, sd, selector_map, SELECTOR, window_start
            )
            all_trades.extend(tr)
            all_skips.extend(
                [[str(expiry.date()), *x] for x in sk]
            )
            processed += 1
            print(
                f"expiry={expiry.date()} trades={len(tr)} selector={SELECTOR}",
                flush=True,
            )
        except Exception as e:
            all_skips.append(
                [str(expiry.date()), "", "exception", repr(e)]
            )
            print(
                f"ERROR expiry={expiry.date()} {repr(e)}",
                flush=True,
            )

    tr = pd.DataFrame(all_trades)
    sk = pd.DataFrame(
        all_skips,
        columns=["expiry", "timestamp", "reason", "detail"],
    )

    if tr.empty:
        sk.to_csv(OUT_ROOT / "skips.csv", index=False)
        raise RuntimeError("Phase 37 produced zero trades")

    tr["cum_net"] = tr.net_rupees.cumsum()
    tr["peak"] = tr.cum_net.cummax()
    tr["drawdown"] = tr.peak - tr.cum_net
    tr["year"] = pd.to_datetime(tr.exit_ts).dt.year
    tr["hold_minutes"] = (
        pd.to_datetime(tr.exit_ts) - pd.to_datetime(tr.entry_ts)
    ).dt.total_seconds() / 60.0

    tr.to_csv(OUT_ROOT / "trades.csv", index=False)
    sk.to_csv(OUT_ROOT / "skips.csv", index=False)

    yearly = (
        tr.groupby("year")
        .agg(
            trades=("net_rupees", "size"),
            net=("net_rupees", "sum"),
            win_rate=("net_rupees", lambda x: (x > 0).mean()),
            mean_net=("net_rupees", "mean"),
            gross=("gross_rupees", "sum"),
            costs=("cost_rupees", "sum"),
        )
        .reset_index()
    )

    direction = (
        tr.groupby("direction")
        .agg(
            trades=("net_rupees", "size"),
            net=("net_rupees", "sum"),
            win_rate=("net_rupees", lambda x: (x > 0).mean()),
            mean_net=("net_rupees", "mean"),
        )
        .reset_index()
    )

    usage = (
        tr.groupby(["selector", "selector_source"])
        .size()
        .reset_index(name="entries")
    )

    profits = tr.loc[tr.net_rupees > 0, "net_rupees"].sum()
    losses = -tr.loc[tr.net_rupees < 0, "net_rupees"].sum()

    summary = {
        "selector": SELECTOR,
        "sample_start": str(START.date()),
        "sample_end": str(END.date()),
        "trades": int(len(tr)),
        "net_pnl": float(tr.net_rupees.sum()),
        "gross_pnl": float(tr.gross_rupees.sum()),
        "costs": float(tr.cost_rupees.sum()),
        "win_rate": float((tr.net_rupees > 0).mean()),
        "profit_factor": float(profits / losses) if losses else None,
        "max_drawdown": float(tr.drawdown.max()),
        "call_trades": int((tr.direction == "CALL").sum()),
        "put_trades": int((tr.direction == "PUT").sum()),
        "delta_exit_trades": int(
            (tr.exit_reason == "DELTA_EXIT").sum()
        ),
        "expiry_termination_trades": int(
            (tr.exit_reason == "CONTRACT_EXPIRY").sum()
        ),
        "mean_net": float(tr.net_rupees.mean()),
        "median_net": float(tr.net_rupees.median()),
        "mean_hold_minutes": float(tr.hold_minutes.mean()),
        "processed_expiries": processed,
        "selector_cache_expiries": len(selector_map),
        "corrected_mapping": "bullish_up_to_put_bearish_down_to_call",
    }

    pd.DataFrame([summary]).to_csv(
        OUT_ROOT / "summary.csv", index=False
    )
    yearly.to_csv(OUT_ROOT / "yearly_statistics.csv", index=False)
    direction.to_csv(OUT_ROOT / "direction_statistics.csv", index=False)
    usage.to_csv(OUT_ROOT / "selector_usage.csv", index=False)

    with open(OUT_ROOT / "coverage.json", "w", encoding="utf-8") as fh:
        json.dump(
            {
                "selector": SELECTOR,
                "requested_start": str(START.date()),
                "requested_end": str(END.date()),
                "expected_expiries": len(expected),
                "available_expected_expiries": sum(
                    e in available for e in expected
                ),
                "processed_expiries": processed,
                "selector_cache_expiries": len(selector_map),
                "model_selector_cache_min": str(min(selector_map))
                if selector_map
                else None,
                "model_selector_cache_max": str(max(selector_map))
                if selector_map
                else None,
            },
            fh,
            indent=2,
        )

    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
