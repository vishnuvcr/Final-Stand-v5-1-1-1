import pandas as pd
import pytest
from pathlib import Path
import importlib.util
p=Path(__file__).resolve().parents[1]/"research"/"phase65_cci_data_coverage_audit.py"
spec=importlib.util.spec_from_file_location("phase65audit",p); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def test_naive_timestamp_localizes_to_exchange_timezone():
    d=mod.norm(pd.DataFrame({"timestamp":["2025-01-02 09:15:00"],"close":[100]}))
    assert str(d.timestamp.iloc[0].tz)=="Asia/Kolkata"
    assert d.timestamp.iloc[0].hour==9

def test_aware_timestamp_converts_to_exchange_timezone():
    d=mod.norm(pd.DataFrame({"timestamp":["2025-01-02T03:45:00Z"]}))
    assert str(d.timestamp.iloc[0].tz)=="Asia/Kolkata"
    assert d.timestamp.iloc[0].hour==9 and d.timestamp.iloc[0].minute==15

def test_invalid_timestamp_fails_closed():
    with pytest.raises(ValueError,match="timestamp parse failures"):
        mod.norm(pd.DataFrame({"timestamp":["not-a-time"]}))
