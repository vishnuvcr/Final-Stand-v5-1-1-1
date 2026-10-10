import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from research.phase98_opening_range_spread import (
    TZ, opening_range_signal, select_vertical, vix_filter_state,
    run_scenario, fee_components, apply_slippage, holm
)

def test_first_strict_opening_range_breakout_is_selected():
    day = "2024-01-02"
    ts = pd.date_range(f"{day} 09:15", f"{day} 14:45", freq="min", tz=TZ)
    df = pd.DataFrame({"timestamp": ts, "open": 95.0, "high": 100.0, "low": 90.0, "close": 95.0})
    df.loc[df.timestamp == pd.Timestamp(f"{day} 09:31", tz=TZ), "close"] = 101.0
    df.loc[df.timestamp == pd.Timestamp(f"{day} 09:32", tz=TZ), "close"] = 89.0
    out = opening_range_signal(df)
    assert out["status"] == "SIGNAL"
    assert out["direction"] == "BULLISH"
    assert out["signal_ts"] == pd.Timestamp(f"{day} 09:31", tz=TZ)
    assert out["or_high"] == 100.0
    assert out["or_low"] == 90.0

def test_opening_range_scan_missing_minute_fails_closed():
    day = "2024-01-02"
    ts = pd.date_range(f"{day} 09:15", f"{day} 14:45", freq="min", tz=TZ)
    df = pd.DataFrame({"timestamp": ts, "high": 100.0, "low": 90.0, "close": 95.0})
    df = df[df.timestamp != pd.Timestamp(f"{day} 10:07", tz=TZ)]
    assert opening_range_signal(df)["status"] == "INDEX_SIGNAL_SCAN_INCOMPLETE"

def test_vertical_uses_common_atm_and_two_strike_steps():
    ts = pd.Timestamp("2024-01-02 09:31", tz=TZ)
    rows = []
    for typ in ("CE", "PE"):
        for k in (10000, 10050, 10100, 10150):
            rows.append({"timestamp": ts, "option_type": typ, "strike": k, "open": 10., "close": 10.})
    chain = pd.DataFrame(rows)
    v = select_vertical(chain, ts, 10048.0, "BULLISH")
    assert v["status"] == "OK"
    assert v["atm"] == 10050.0
    assert v["step"] == 50.0
    assert v["short_strike"] == 10150.0

def test_vix_filter_uses_only_prior_close_and_prior_252_threshold():
    dates = pd.date_range("2023-01-01", periods=253, freq="D", tz=TZ)
    vix = pd.DataFrame({"date": dates, "vix": [10.0] * 252 + [50.0]})
    out = vix_filter_state(vix, (dates[-1] + pd.Timedelta(days=1)).date())
    assert out["available"] is True
    assert out["prior_close"] == 50.0
    assert out["threshold"] == 10.0
    assert out["skip"] is True

def test_next_minute_exit_and_all_in_costs_are_applied():
    day = pd.Timestamp("2024-01-02").date()
    entry = pd.Timestamp("2024-01-02 09:31", tz=TZ)
    exit_ts = entry + pd.Timedelta(minutes=1)
    chain = pd.DataFrame([
        {"timestamp": entry, "option_type": "CE", "strike": 10000., "open": 40., "close": 150.},
        {"timestamp": entry, "option_type": "CE", "strike": 10200., "open": 10., "close": 5.},
        {"timestamp": exit_ts, "option_type": "CE", "strike": 10000., "open": 150., "close": 150.},
        {"timestamp": exit_ts, "option_type": "CE", "strike": 10200., "open": 5., "close": 5.},
    ])
    v = {"option_type": "CE", "long_strike": 10000., "short_strike": 10200., "width": 200.}
    out = run_scenario(chain, day, entry, "BULLISH", v, 25, 1, 10., 1.)
    assert out["status"] == "COMPLETE"
    assert out["trigger"] == "TARGET"
    assert out["exit_ts"] == str(exit_ts)
    assert out["path_coverage"] == 1.0
    assert out["fees"]["brokerage"] == 40.0
    assert out["net"] < out["gross_after_slippage_before_fees"]

def test_adverse_slippage_and_holm_are_monotone():
    assert apply_slippage(10.0, "buy", 2) == 10.10
    assert apply_slippage(10.0, "sell", 2) == 9.90
    adjusted = holm([0.01, 0.03, 0.20])
    assert adjusted[0] <= adjusted[1] <= adjusted[2]
