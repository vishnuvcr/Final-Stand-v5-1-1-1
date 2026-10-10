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

def test_u05_preserves_first_thursday_and_excludes_lookahead_months():
    wed, thu = r._u05_entry_dates(pd.Period("2021-07", freq="M"))
    assert wed.date().isoformat() == "2021-07-07"
    assert thu.date().isoformat() == "2021-07-01"
    assert thu < wed  # runner must exclude this opportunity, not slide to the second Thursday

def test_u05_first_thursday_after_forecast_is_eligible():
    wed, thu = r._u05_entry_dates(pd.Period("2024-06", freq="M"))
    assert wed.date().isoformat() == "2024-06-05"
    assert thu.date().isoformat() == "2024-06-06"
    assert thu > wed

def test_block_bootstrap_only_runs_with_sufficient_trade_count():
    small = r.block_bootstrap_mean_ci(range(7))
    assert small["bootstrap_status"] == "SKIPPED_LT20_TRADES"
    large = r.block_bootstrap_mean_ci(range(100), replicates=200)
    assert large["bootstrap_status"] == "COMPUTED_CIRCULAR_MOVING_BLOCK_CI"
    assert large["mean_net_trade_ci95_low"] < large["mean_net_trade_ci95_high"]


class _FakePhase66Costs:
    @staticmethod
    def exec_px(price, side):
        # A deterministic 0.05 tick grid; buys round upward and sells downward.
        x = float(price) / 0.05
        return (np.ceil(x) if side == "buy" else np.floor(x)) * 0.05

    @staticmethod
    def charges(orders, quantity, multiplier):
        # Stable synthetic charge helper for a unit test; not a broker fee schedule.
        return 123.0 * float(multiplier)


def test_adverse_impact_stress_includes_execution_and_baseline_charges():
    result = r._trade_costs(
        _FakePhase66Costs(),
        pd.Timestamp("2024-01-02 09:15", tz="Asia/Kolkata"),
        pd.Timestamp("2024-01-02 15:29", tz="Asia/Kolkata"),
        100.0,
        110.0,
        50,
    )
    impacted_buy = _FakePhase66Costs.exec_px(100.0 * 1.0025, "buy")
    impacted_sell = _FakePhase66Costs.exec_px(110.0 * 0.9975, "sell")
    expected = (impacted_sell - impacted_buy) * 50 - 123.0 - 50.0
    assert np.isclose(result["paper_025pct_each_side_plus_50_trade_cost_net"], expected)
    # Stress must be below the baseline net when both impact sides are adverse.
    assert result["paper_025pct_each_side_plus_50_trade_cost_net"] < result["net_10_per_order"]
