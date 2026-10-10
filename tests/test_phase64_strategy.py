import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research"))
import phase64_paper_strategy_tests as p64

TZ = "Asia/Kolkata"

def synthetic_index():
    days = pd.date_range("2021-06-01", periods=240, freq="B", tz=TZ)
    rows = []
    last = 15000.0
    for i, day in enumerate(days):
        close = last + (2.0 if i % 3 else -1.0)
        rows.append({"timestamp": day + pd.Timedelta(hours=10), "open": last,
                     "high": close + 10.0, "low": close - 10.0, "close": close})
        last = close
    # It must be excluded before feature generation.
    rows.append({"timestamp": pd.Timestamp("2026-02-02 10:00", tz=TZ),
                 "open": 999999, "high": 1000000, "low": 999998, "close": 999999})
    return pd.DataFrame(rows)

def test_holdout_rows_removed_before_features():
    idx = p64.normalize_index(synthetic_index())
    assert idx.timestamp.max() <= p64.VAL_END
    assert not (idx.timestamp.dt.year == 2026).any()

def test_feature_lookbacks_are_causal_and_defined():
    idx = p64.normalize_index(synthetic_index())
    d = p64.daily_features(idx)
    assert d.cci20.iloc[:19].isna().all()
    assert np.isfinite(d.cci20.iloc[25])
    assert d.ema50.iloc[:49].isna().all()
    assert np.isfinite(d.ema50.iloc[60])
    assert d.ema200.iloc[:199].isna().all()
    assert np.isfinite(d.ema200.iloc[220])

def test_breakout_never_uses_signal_day_itself():
    idx = pd.DataFrame([
        {"timestamp": pd.Timestamp("2021-06-03 10:00", tz=TZ), "close": 15010.0},
        {"timestamp": pd.Timestamp("2021-06-04 10:00", tz=TZ), "close": 15100.0},
        {"timestamp": pd.Timestamp("2021-06-07 10:00", tz=TZ), "close": 15200.0},
    ])
    signal = [{"side":"CE", "signal_date":pd.Timestamp("2021-06-03", tz=TZ),
               "level":15050.0, "cci":-95.0, "signal_close":15010.0,
               "ema50":np.nan, "ema200":np.nan}]
    events, reason = p64.first_breakouts(idx, signal, "2021-06")
    assert reason == "breakout_found"
    assert events[0]["trigger_ts"] == pd.Timestamp("2021-06-04 10:00", tz=TZ)

def test_same_minute_call_put_breakout_is_ambiguous():
    idx = pd.DataFrame([
        {"timestamp": pd.Timestamp("2021-06-04 10:00", tz=TZ), "close": 15000.0},
    ])
    signals = [
        {"side":"CE","signal_date":pd.Timestamp("2021-06-03",tz=TZ),"level":14950.0,
         "cci":-95.,"signal_close":14900.,"ema50":np.nan,"ema200":np.nan},
        {"side":"PE","signal_date":pd.Timestamp("2021-06-03",tz=TZ),"level":15050.0,
         "cci":99.,"signal_close":15100.,"ema50":np.nan,"ema200":np.nan},
    ]
    events, reason = p64.first_breakouts(idx, signals, "2021-06")
    assert not events
    assert reason == "ambiguous_call_put_same_minute"

def test_holm_adjustment_is_monotone():
    got = p64.holm_adjust(np.array([0.01, 0.04]))
    assert np.allclose(got, [0.02, 0.04])

def test_bootstrap_skips_underpowered_sample():
    periods = pd.period_range("2024-01", periods=12, freq="M")
    series = pd.Series(np.arange(12, dtype=float), index=periods)
    out = p64.moving_block_bootstrap(series)
    assert out["status"] == "SKIPPED_LT20_TRADES"
    assert out["p_two_sided"] is None
