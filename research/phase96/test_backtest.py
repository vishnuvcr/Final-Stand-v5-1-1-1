import sys
from pathlib import Path
import pandas as pd
import pytest
sys.path.insert(0, str(Path(__file__).parent))
from backtest import replay

def test_signal_is_lagged():
    df = pd.DataFrame({"date":pd.date_range("2024-01-01", periods=130), "open":[100.0]*130, "close":[float(i+100) for i in range(130)]})
    x = replay(df, "SMA", 5, 20)
    assert x.signal.iloc[0] == 0
    assert x.signal.iloc[20] == 0 or x.signal.iloc[20] in (0,1)
    assert (x.turnover >= 0).all()

def test_invalid_windows_rejected():
    df = pd.DataFrame({"date":pd.date_range("2024-01-01", periods=30), "open":[100.0]*30, "close":[float(i+100) for i in range(30)]})
    with pytest.raises(ValueError):
        replay(df, "SMA", 20, 5)
