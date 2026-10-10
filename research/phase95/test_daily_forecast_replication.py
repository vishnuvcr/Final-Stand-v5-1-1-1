from __future__ import annotations
import numpy as np
import pandas as pd
from research.phase95.daily_forecast_replication import add_features, make_estimator, block_bootstrap_ci

def synthetic_data(n=350):
    idx=pd.bdate_range("2023-01-01",periods=n)
    close=18000+np.cumsum(np.sin(np.arange(n)/7.0)*12+2.0)
    return pd.DataFrame({"Open":close-2,"High":close+15,"Low":close-15,"Close":close,"Volume":np.full(n,100000.0)},index=idx)

def test_target_is_exactly_next_observed_session():
    raw=synthetic_data(); X,T=add_features(raw); idx=X.index[0]; pos=raw.index.get_loc(idx)
    assert T.loc[idx,"TargetDate"]==raw.index[pos+1]
    assert T.loc[idx,"target_close"]==raw.iloc[pos+1]["Close"]
    assert T.loc[idx,"target_close"]!=raw.iloc[pos]["Close"]

def test_features_are_asof_and_not_shifted_from_future():
    raw=synthetic_data(); X,T=add_features(raw); idx=X.index[-2]; pos=raw.index.get_loc(idx)
    assert X.loc[idx,"close_t"]==raw.loc[idx,"Close"]
    assert T.loc[idx,"TargetDate"]==raw.index[pos+1]

def test_registered_classical_estimators_construct():
    for name in ("linear_regression","lasso","ridge","elastic_net","sgd_regressor","svr","knn","decision_tree","random_forest","gradient_boosting","adaboost","xgboost","mlp","slp","rbf_network"):
        assert hasattr(make_estimator(name),"fit")

def test_block_bootstrap_is_reproducible():
    x=np.linspace(-1,1,100)
    assert block_bootstrap_ci(x,np.random.default_rng(90210),n_boot=100,block_len=5)==block_bootstrap_ci(x,np.random.default_rng(90210),n_boot=100,block_len=5)
