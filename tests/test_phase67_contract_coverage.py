import pandas as pd


def test_exact_next_minute_is_distinct_from_nearby_bar():
    trigger = pd.Timestamp('2021-07-09 09:15:00', tz='Asia/Kolkata')
    observed = pd.DatetimeIndex([trigger, trigger + pd.Timedelta(minutes=2)])
    assert bool((observed == trigger).any())
    assert not bool((observed == trigger + pd.Timedelta(minutes=1)).any())


def test_timezone_conversion_preserves_instant():
    ts = pd.Timestamp('2021-07-09 03:45:00', tz='UTC').tz_convert('Asia/Kolkata')
    assert ts.hour == 9 and ts.minute == 15
