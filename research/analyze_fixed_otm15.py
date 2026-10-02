import numpy as np
import pandas as pd
from pathlib import Path

BASE=Path("results/fixed_otm15_v3")
OUT=BASE/"phase8"
OUT.mkdir(parents=True,exist_ok=True)
tr=pd.read_csv(BASE/"trades.csv",parse_dates=["entry_ts","exit_ts"])
tr["year"]=tr["expiry"].str[:4].astype(int)
tr["win"]=tr.net_rupees>0
profits=tr.loc[tr.net_rupees>0,"net_rupees"].sum()
losses=-tr.loc[tr.net_rupees<0,"net_rupees"].sum()
pf=profits/losses if losses else np.inf
cum=tr.net_rupees.cumsum()
dd=(cum.cummax()-cum).max()
mean=tr.net_rupees.mean()
med=tr.net_rupees.median()
std=tr.net_rupees.std(ddof=1)
sharpe=mean/std if std else np.nan
rng=np.random.default_rng(20261003)
B=20000
means=np.empty(B); wins=np.empty(B)
x=tr.net_rupees.to_numpy()
for i in range(B):
    s=rng.choice(x,size=len(x),replace=True)
    means[i]=s.mean(); wins[i]=(s>0).mean()
overall=pd.DataFrame([{
"trades":len(tr),"mean_net_rupees":mean,"median_net_rupees":med,"std_net_rupees":std,
"sum_net_rupees":tr.net_rupees.sum(),"profit_factor":pf,"max_drawdown_rupees":dd,
"trade_level_sharpe_nonannualized":sharpe,"win_rate":tr.win.mean(),
"bootstrap_mean_net_ci_low":np.quantile(means,.025),"bootstrap_mean_net_ci_high":np.quantile(means,.975),
"bootstrap_win_rate_ci_low":np.quantile(wins,.025),"bootstrap_win_rate_ci_high":np.quantile(wins,.975)
}])
year=tr.groupby("year").agg(trades=("net_rupees","size"),net_rupees=("net_rupees","sum"),mean_net=("net_rupees","mean"),win_rate=("win","mean")).reset_index()
direction=tr.groupby("direction").agg(trades=("net_rupees","size"),net_rupees=("net_rupees","sum"),mean_net=("net_rupees","mean"),win_rate=("win","mean")).reset_index()
exit=tr.groupby("exit_reason").agg(trades=("net_rupees","size"),net_rupees=("net_rupees","sum"),mean_net=("net_rupees","mean"),win_rate=("win","mean")).reset_index()
overall.to_csv(OUT/"overall_statistics.csv",index=False)
year.to_csv(OUT/"yearly_statistics.csv",index=False)
direction.to_csv(OUT/"direction_statistics.csv",index=False)
exit.to_csv(OUT/"exit_statistics.csv",index=False)
print(overall.to_string(index=False))
print(year.to_string(index=False))
print(direction.to_string(index=False))
print(exit.to_string(index=False))
