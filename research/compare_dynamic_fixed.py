import pandas as pd
import numpy as np
from pathlib import Path

DYN=Path("results/dynamic_n_corrected/phase10_primary")
FIX=Path("results/fixed_otm15_v3/phase7d")
OUT=Path("results/dynamic_n_corrected/phase13_comparison")
OUT.mkdir(parents=True,exist_ok=True)

dyn=pd.read_csv(DYN/"trades.csv")
fix=pd.read_csv(FIX/"trades.csv")

def metrics(df,label):
    profits=df.loc[df.net_rupees>0,"net_rupees"].sum()
    losses=-df.loc[df.net_rupees<0,"net_rupees"].sum()
    return {
        "strategy":label,
        "trades":len(df),
        "net_rupees":df.net_rupees.sum(),
        "gross_rupees":df.gross_rupees.sum(),
        "cost_rupees":df.cost_rupees.sum(),
        "mean_net":df.net_rupees.mean(),
        "median_net":df.net_rupees.median(),
        "win_rate":(df.net_rupees>0).mean(),
        "profit_factor":profits/losses if losses else np.inf,
        "max_drawdown":(df.net_rupees.cumsum().cummax()-df.net_rupees.cumsum()).max(),
        "target_exit_rate":(df.exit_reason=="TARGET").mean(),
        "expiry_exit_rate":(df.exit_reason=="EXPIRY").mean(),
    }

overall=pd.DataFrame([metrics(dyn,"DYNAMIC_N"),metrics(fix,"FIXED_OTM15")])

dcommon=dyn[dyn.expiry.isin(set(fix.expiry))]
fcommon=fix[fix.expiry.isin(set(dyn.expiry))]

paired=dcommon.merge(
    fcommon[["expiry","net_rupees","gross_rupees","cost_rupees","exit_reason","direction"]],
    on="expiry",
    how="inner",
    suffixes=("_dynamic","_fixed"),
)
paired["net_difference_dynamic_minus_fixed"]=paired.net_rupees_dynamic-paired.net_rupees_fixed
paired["gross_difference_dynamic_minus_fixed"]=paired.gross_rupees_dynamic-paired.gross_rupees_fixed
paired["cost_difference_dynamic_minus_fixed"]=paired.cost_rupees_dynamic-paired.cost_rupees_fixed
paired["dynamic_better_net"]=paired.net_difference_dynamic_minus_fixed>0
paired.to_csv(OUT/"paired_expiry_comparison.csv",index=False)

common_summary=pd.DataFrame([{
    "common_expiries":len(paired),
    "dynamic_net_common":paired.net_rupees_dynamic.sum(),
    "fixed_net_common":paired.net_rupees_fixed.sum(),
    "dynamic_gross_common":paired.gross_rupees_dynamic.sum(),
    "fixed_gross_common":paired.gross_rupees_fixed.sum(),
    "dynamic_cost_common":paired.cost_rupees_dynamic.sum(),
    "fixed_cost_common":paired.cost_rupees_fixed.sum(),
    "net_advantage_dynamic":paired.net_difference_dynamic_minus_fixed.sum(),
    "dynamic_positive_vs_fixed_share":paired.dynamic_better_net.mean(),
    "mean_net_difference_per_common_expiry":paired.net_difference_dynamic_minus_fixed.mean(),
}])

coverage=pd.DataFrame([{
    "dynamic_trade_count":len(dyn),
    "fixed_trade_count":len(fix),
    "common_expiry_count":len(paired),
    "dynamic_only_expiries":len(set(dyn.expiry)-set(fix.expiry)),
    "fixed_only_expiries":len(set(fix.expiry)-set(dyn.expiry)),
}])

n_mix=dyn.groupby("n_selected").agg(
    trades=("expiry","size"),
    net_rupees=("net_rupees","sum"),
    mean_net=("net_rupees","mean"),
).reset_index()

direction_mix=pd.concat([
    dyn.groupby("direction").net_rupees.agg(["count","sum","mean"]).reset_index().assign(strategy="DYNAMIC_N"),
    fix.groupby("direction").net_rupees.agg(["count","sum","mean"]).reset_index().assign(strategy="FIXED_OTM15"),
], ignore_index=True)

overall.to_csv(OUT/"overall_comparison.csv",index=False)
common_summary.to_csv(OUT/"common_sample_comparison.csv",index=False)
coverage.to_csv(OUT/"coverage_comparison.csv",index=False)
n_mix.to_csv(OUT/"dynamic_n_mix.csv",index=False)
direction_mix.to_csv(OUT/"direction_mix.csv",index=False)

print("OVERALL\n",overall.to_string(index=False))
print("\nCOMMON SAMPLE\n",common_summary.to_string(index=False))
print("\nCOVERAGE\n",coverage.to_string(index=False))
print("\nN MIX\n",n_mix.to_string(index=False))
