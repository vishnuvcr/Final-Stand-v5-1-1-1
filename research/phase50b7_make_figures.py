from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path("results/phase50b"); OUT=ROOT/"final_manuscript"; OUT.mkdir(parents=True,exist_ok=True)
chron=pd.read_csv(ROOT/"phase50b5_chronological_validation/chronological_equity.csv")
hyp=pd.read_csv(ROOT/"phase50b6_statistical_inference/hypothesis_results.csv")
for s,g in chron.groupby("strategy"):
    g=g.sort_values("trade_index")
    plt.figure(figsize=(9,5)); plt.plot(g["trade_index"],g["equity_net"]); plt.axhline(0,linewidth=1)
    plt.title(f"{s}: chronological cumulative equity"); plt.xlabel("Completed trade index"); plt.ylabel("Cumulative net P&L (₹)")
    plt.tight_layout(); plt.savefig(OUT/f"{s}_equity.png",dpi=160); plt.close()
pivot=hyp.pivot(index="strategy",columns="cost_model",values="mean")
ax=pivot.plot(kind="bar",figsize=(10,5)); ax.set_title("Mean P&L per trade by registered cost model"); ax.set_xlabel("Strategy"); ax.set_ylabel("Mean net P&L per trade (₹)"); ax.axhline(0,linewidth=1)
plt.tight_layout(); plt.savefig(OUT/"mean_pnl_cost_sensitivity.png",dpi=160); plt.close()
plt.figure(figsize=(9,5))
for s,g in hyp.groupby("strategy"):
    order=["net","net50","net20","net20_50"]; g=g.set_index("cost_model").reindex(order)
    plt.plot(order,g["mean"],marker="o",label=s)
plt.axhline(0,linewidth=1); plt.title("Cost sensitivity of mean trade P&L"); plt.xlabel("Registered cost model"); plt.ylabel("Mean net P&L per trade (₹)"); plt.legend()
plt.tight_layout(); plt.savefig(OUT/"cost_sensitivity_lines.png",dpi=160); plt.close()
print("final figures generated")
