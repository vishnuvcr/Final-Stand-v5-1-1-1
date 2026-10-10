import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research" / "phase101"))
import paper_strategy_replay as r

def test_u05_monthly_expected_target_uses_three_month_returns():
    target, mean = r.monthly_expected_target(100.0, [0.10, -0.02, 0.04])
    assert np.isclose(mean, 0.04)
    assert np.isclose(target, 104.0)

def test_u05_expected_target_rejects_missing_returns():
    try:
        r.monthly_expected_target(100.0, [0.1, np.nan, 0.2])
    except ValueError as exc:
        assert "three finite" in str(exc)
    else:
        raise AssertionError("missing monthly return must be rejected")

def test_u05_stop_and_target_thresholds():
    assert r.option_exit_decision(100, 121, 99, False) == "TARGET_20PCT"
    assert r.option_exit_decision(100, 105, 69, False) is None
    assert r.option_exit_decision(100, 105, 69, True) == "STOP_30PCT"
    assert r.option_exit_decision(100, 125, 65, True) == "AMBIGUOUS_BOTH_STOP_FIRST"

def test_u05_first_weekday_is_timezone_aware_ist():
    d = r._first_weekday(pd.Period("2024-01", freq="M"), 2)
    assert d.day == 3
    assert str(d.tz) == "Asia/Kolkata"

def test_zero_trade_statistics_are_not_fabricated_as_zero_pnl():
    result = r.net_trade_metrics([])
    assert result["completed_trades"] == 0
    assert result["status"] == "NOT_ESTIMABLE_ZERO_TRADES"
    assert result["net_pnl_rupees"] is None
    assert result["mean_net_per_trade"] is None

def test_u02_capital_is_registered_and_holdout_end_is_2025():
    assert r.CAPITAL_U02 == 100000.0
    assert str(r.VAL_END.date()) == "2025-12-31"
    assert r.PINNED_REVISION == "3eacf762d401efd9a08e804592fa7882b354c4a2"

def test_u05_entry_date_is_strictly_after_forecast_wednesday():
    wed, thu = r._u05_entry_dates(pd.Period("2021-07", freq="M"))
    assert wed.date().isoformat() == "2021-07-07"
    assert thu.date().isoformat() == "2021-07-08"
    assert thu > wed

def test_u05_entry_date_not_first_thursday_when_that_precedes_forecast():
    wed, thu = r._u05_entry_dates(pd.Period("2023-06", freq="M"))
    assert wed.date().isoformat() == "2023-06-07"
    assert thu.date().isoformat() == "2023-06-08"
    assert thu > wed

def test_block_bootstrap_only_runs_with_sufficient_trade_count():
    small = r.block_bootstrap_mean_ci(range(7))
    assert small["bootstrap_status"] == "SKIPPED_LT20_TRADES"
    large = r.block_bootstrap_mean_ci(range(100), replicates=200)
    assert large["bootstrap_status"] == "COMPUTED_CIRCULAR_MOVING_BLOCK_CI"
    assert large["mean_net_trade_ci95_low"] < large["mean_net_trade_ci95_high"]
