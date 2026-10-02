import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

IN = Path("results/restarted_v2/trades.csv")
OUT = Path("results/restarted_v2/phase3")
OUT.mkdir(parents=True, exist_ok=True)
B = int(os.getenv("BOOTSTRAP_N", "10000"))
SEED = int(os.getenv("BOOTSTRAP_SEED", "20261002"))

df = pd.read_csv(IN, parse_dates=["entry_ts","exit_ts"])
df["year"] = pd.to_datetime(df["expiry"]).dt.year
df["duration_hours"] = (df["exit_ts"] - df["entry_ts"]).dt.total_seconds()/3600
df["credit_return"] = df["net_rupees"] / df["initial_credit_rupees_raw"]
df["cost_pct_of_abs_gross"] = np.where(df["gross_rupees"].abs()>0, df["cost_rupees"]/df["gross_rupees"].abs()*100, np.nan)

def max_dd(x):
    eq = np.cumsum(x)
    peak = np.maximum.accumulate(eq)
    dd = eq - peak
    return float(dd.min())

def profit_factor(x):
    wins = x[x>0].sum()
    losses = -x[x<0].sum()
    return float(wins/losses) if losses>0 else np.inf

def stats(g):
    x = g["net_rupees"].to_numpy(float)
    r = g["credit_return"].to_numpy(float)
    return pd.Series({
        "trades": len(g),
        "wins": int((x>0).sum()),
        "losses": int((x<=0).sum()),
        "win_rate": float((x>0).mean()),
        "mean_net_rupees": float(x.mean()),
        "median_net_rupees": float(np.median(x)),
        "std_net_rupees": float(x.std(ddof=1)) if len(x)>1 else np.nan,
        "sum_net_rupees": float(x.sum()),
        "mean_gross_rupees": float(g["gross_rupees"].mean()),
        "sum_gross_rupees": float(g["gross_rupees"].sum()),
        "sum_cost_rupees": float(g["cost_rupees"].sum()),
        "profit_factor": profit_factor(x),
        "expectancy_rupees": float(x.mean()),
        "max_drawdown_rupees": max_dd(x),
        "mean_credit_return": float(r.mean()),
        "median_credit_return": float(np.median(r)),
        "trade_sharpe_credit_normalized": float(r.mean()/r.std(ddof=1)) if len(r)>1 and r.std(ddof=1)>0 else np.nan,
        "trade_sortino_credit_normalized": float(r.mean()/r[r<0].std(ddof=1)) if (r<0).sum()>1 and r[r<0].std(ddof=1)>0 else np.nan,
        "target_exit_rate": float((g["exit_reason"]=="TARGET").mean()),
        "mean_duration_hours": float(g["duration_hours"].mean()),
    })

def bootstrap_mean(x, n=B, seed=SEED):
    rng=np.random.default_rng(seed)
    x=np.asarray(x,float)
    means=np.empty(n)
    for i in range(n):
        means[i]=rng.choice(x,size=len(x),replace=True).mean()
    return float(np.quantile(means,.025)),float(np.quantile(means,.975))

def bootstrap_winrate(x,n=B,seed=SEED+1):
    rng=np.random.default_rng(seed)
    x=np.asarray(x,float)
    vals=np.empty(n)
    for i in range(n):
        vals[i]=(rng.choice(x,size=len(x),replace=True)>0).mean()
    return float(np.quantile(vals,.025)),float(np.quantile(vals,.975))

overall=stats(df).to_frame().T
mlo,mhi=bootstrap_mean(df.net_rupees)
wlo,whi=bootstrap_winrate(df.net_rupees)
overall["bootstrap_mean_net_ci95_low"]=mlo
overall["bootstrap_mean_net_ci95_high"]=mhi
overall["bootstrap_win_rate_ci95_low"]=wlo
overall["bootstrap_win_rate_ci95_high"]=whi
overall.to_csv(OUT/"overall_statistics.csv",index=False)

for name, keys in [
    ("by_year", ["year"]),
    ("by_direction", ["direction"]),
    ("by_n", ["direction","n"]),
    ("by_exit_reason", ["exit_reason"])
]:
    rows=[]
    for key, g in df.groupby(keys, dropna=False):
        s=stats(g).to_dict()
        if not isinstance(key, tuple):
            key=(key,)
        s.update({k:v for k,v in zip(keys,key)})
        rows.append(s)
    pd.DataFrame(rows).to_csv(OUT/f"{name}.csv",index=False)

# Additional selection diagnostics
selection = df.groupby("direction").agg(
    trades=("n","size"),
    mean_x_call6=("x_call6","mean"),
    mean_x_put6=("x_put6","mean"),
    mean_selected_x=("x_raw","mean"),
    mean_xmax=("x_max_selected_side","mean"),
    mean_n=("n","mean"),
    median_n=("n","median")
).reset_index()
selection.to_csv(OUT/"selection_diagnostics.csv",index=False)

# Yearly bootstrap CIs
rows=[]
for y,g in df.groupby("year"):
    lo,hi=bootstrap_mean(g.net_rupees.to_numpy(),seed=SEED+int(y))
    w1,w2=bootstrap_winrate(g.net_rupees.to_numpy(),seed=SEED+100+int(y))
    s=stats(g).to_dict()
    s.update({"year":y,"bootstrap_mean_net_ci95_low":lo,"bootstrap_mean_net_ci95_high":hi,
              "bootstrap_win_rate_ci95_low":w1,"bootstrap_win_rate_ci95_high":w2})
    rows.append(s)
pd.DataFrame(rows).to_csv(OUT/"by_year_bootstrap.csv",index=False)

# Equity curve
eq=df.sort_values("exit_ts")[["exit_ts","net_rupees"]].copy()
eq["cumulative_net_rupees"]=eq.net_rupees.cumsum()
eq["running_peak"]=eq.cumulative_net_rupees.cummax()
eq["drawdown_rupees"]=eq.cumulative_net_rupees-eq.running_peak
eq.to_csv(OUT/"equity_curve.csv",index=False)

plt.figure(figsize=(10,5))
plt.plot(eq.exit_ts,eq.cumulative_net_rupees)
plt.axhline(0,linewidth=1)
plt.title("Restarted strategy cumulative net P&L")
plt.xlabel("Exit timestamp")
plt.ylabel("Cumulative net P&L (₹)")
plt.tight_layout()
plt.savefig(OUT/"equity_curve.png",dpi=160)
plt.close()

plt.figure(figsize=(9,5))
plt.hist(df.net_rupees,bins=30)
plt.axvline(0,linewidth=1)
plt.title("Distribution of trade-level net P&L")
plt.xlabel("Net P&L per trade (₹)")
plt.ylabel("Trades")
plt.tight_layout()
plt.savefig(OUT/"net_pnl_distribution.png",dpi=160)
plt.close()

plt.figure(figsize=(9,5))
df.groupby("year").net_rupees.sum().plot(kind="bar")
plt.axhline(0,linewidth=1)
plt.title("Annual net P&L")
plt.xlabel("Expiry year")
plt.ylabel("Net P&L (₹)")
plt.tight_layout()
plt.savefig(OUT/"annual_net_pnl.png",dpi=160)
plt.close()

print(overall.to_string(index=False))
print("\nSaved Phase 3 statistics and charts to",OUT)
