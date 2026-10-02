import numpy as np
import pandas as pd
from pathlib import Path

BASE=Path("results/dynamic_n_corrected/phase10_primary")
OUT=Path("results/dynamic_n_corrected/phase11_statistics")
OUT.mkdir(parents=True,exist_ok=True)

tr=pd.read_csv(BASE/"trades.csv")
tr["year"]=tr["expiry"].str[:4].astype(int)
tr["win"]=tr.net_rupees>0

profits=tr.loc[tr.net_rupees>0,"net_rupees"].sum()
losses=-tr.loc[tr.net_rupees<0,"net_rupees"].sum()
pf=profits/losses if losses else np.inf
cum=tr.net_rupees.cumsum()
dd=(cum.cummax()-cum).max()

rng=np.random.default_rng(20261003)
B=20000
x=tr.net_rupees.to_numpy()
means=np.empty(B); wins=np.empty(B)
for i in range(B):
    s=rng.choice(x,size=len(x),replace=True)
    means[i]=s.mean()
    wins[i]=(s>0).mean()

overall=pd.DataFrame([{
    "trades":len(tr),
    "mean_net_rupees":tr.net_rupees.mean(),
    "median_net_rupees":tr.net_rupees.median(),
    "std_net_rupees":tr.net_rupees.std(ddof=1),
    "sum_net_rupees":tr.net_rupees.sum(),
    "profit_factor":pf,
    "max_drawdown_rupees":dd,
    "trade_level_sharpe_nonannualized":tr.net_rupees.mean()/tr.net_rupees.std(ddof=1),
    "win_rate":tr.win.mean(),
    "bootstrap_mean_net_ci_low":np.quantile(means,.025),
    "bootstrap_mean_net_ci_high":np.quantile(means,.975),
    "bootstrap_win_rate_ci_low":np.quantile(wins,.025),
    "bootstrap_win_rate_ci_high":np.quantile(wins,.975),
}])

year=tr.groupby("year").agg(
    trades=("net_rupees","size"),
    net_rupees=("net_rupees","sum"),
    mean_net=("net_rupees","mean"),
    median_net=("net_rupees","median"),
    win_rate=("win","mean"),
).reset_index()

direction=tr.groupby("direction").agg(
    trades=("net_rupees","size"),
    net_rupees=("net_rupees","sum"),
    mean_net=("net_rupees","mean"),
    win_rate=("win","mean"),
    mean_n=("n_selected","mean"),
).reset_index()

exit_stats=tr.groupby("exit_reason").agg(
    trades=("net_rupees","size"),
    net_rupees=("net_rupees","sum"),
    mean_net=("net_rupees","mean"),
    win_rate=("win","mean"),
).reset_index()

n_stats=tr.groupby("n_selected").agg(
    trades=("net_rupees","size"),
    net_rupees=("net_rupees","sum"),
    mean_net=("net_rupees","mean"),
    median_net=("net_rupees","median"),
    win_rate=("win","mean"),
).reset_index().sort_values("n_selected")

# Compare the economic contribution of selected n against eligible candidates.
cand=pd.read_csv(BASE/"candidate_n_scores.csv")
cand_selected=cand[cand["selected"]].copy()
selected_share=cand_selected["n"].value_counts().sort_index().rename_axis("n").reset_index(name="selected_candidate_days")

overall.to_csv(OUT/"overall_statistics.csv",index=False)
year.to_csv(OUT/"yearly_statistics.csv",index=False)
direction.to_csv(OUT/"direction_statistics.csv",index=False)
exit_stats.to_csv(OUT/"exit_statistics.csv",index=False)
n_stats.to_csv(OUT/"n_statistics.csv",index=False)
selected_share.to_csv(OUT/"selection_counts.csv",index=False)

print(overall.to_string(index=False))
print("\nYEAR\n",year.to_string(index=False))
print("\nDIRECTION\n",direction.to_string(index=False))
print("\nEXIT\n",exit_stats.to_string(index=False))
print("\nN\n",n_stats.to_string(index=False))
print("\nSELECTION COUNTS\n",selected_share.to_string(index=False))
