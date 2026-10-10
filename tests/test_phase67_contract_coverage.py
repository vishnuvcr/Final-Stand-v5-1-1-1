import pandas as pd


def test_exact_next_minute_is_distinct_from_nearby_bar():
    trigger = pd.Timestamp('2021-07-09 09:15:00', tz='Asia/Kolkata')
    observed = pd.DatetimeIndex([trigger, trigger + pd.Timedelta(minutes=2)])
    assert bool((observed == trigger).any())
    assert not bool((observed == trigger + pd.Timedelta(minutes=1)).any())


def test_timezone_conversion_preserves_instant():
    ts = pd.Timestamp('2021-07-09 03:45:00', tz='UTC').tz_convert('Asia/Kolkata')
    assert ts.hour == 9 and ts.minute == 15


def test_missing_exact_minute_is_not_replaced_by_context():
    trigger = pd.Timestamp('2021-07-09 09:15:00', tz='Asia/Kolkata')
    observed = pd.DatetimeIndex([trigger - pd.Timedelta(minutes=1), trigger + pd.Timedelta(minutes=2)])
    exact_next = trigger + pd.Timedelta(minutes=1)
    context = observed[observed.to_series().between(trigger - pd.Timedelta(minutes=2), trigger + pd.Timedelta(minutes=2)).to_numpy()]
    assert len(context) == 2
    assert not bool((observed == exact_next).any())


def test_utc_to_ist_date_boundary_is_explicit():
    ts = pd.Timestamp('2021-07-08 18:45:00', tz='UTC').tz_convert('Asia/Kolkata')
    assert ts.strftime('%Y-%m-%d %H:%M') == '2021-07-09 00:15'
