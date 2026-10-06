import ast
import json
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path("results/phase43_vix")
TRADES = OUT / "strategy_trade_matrix_all_splits.csv"
if not TRADES.exists():
    raise FileNotFoundError(TRADES)

df = pd.read_csv(TRADES)
df["active_states"] = df["active_states"].map(ast.literal_eval)
defined = [
    "long_straddle", "short_straddle", "long_strangle", "short_strangle",
    "bull_call_debit", "bear_put_debit", "bull_put_credit", "bear_call_credit",
    "long_call_butterfly", "long_put_butterfly", "iron_butterfly", "iron_condor",
    "call_broken_wing", "put_broken_wing", "call_backspread", "put_backspread",
    "call_calendar", "put_calendar"
]
modes = ["LOW","NORMAL","HIGH","SPIKE","FALLING","RISING","HIGH_RISING"]

def drawdown(vals):
    a = np.asarray(vals, dtype=float)
    if a.size == 0:
        return 0.0
    c = np.cumsum(a)
    return float(np.max(np.maximum.accumulate(c) - c))

def permutation_p(a, b, seed=43043, n=10000):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) < 10 or len(b) < 10:
        return np.nan
    obs = a.mean() - b.mean()
    pooled = np.concatenate([a,b])
    rng = np.random.default_rng(seed)
    ge = 0
    for _ in range(n):
        perm = rng.permutation(pooled)
        x = perm[:len(a)].mean() - perm[len(a):].mean()
        if abs(x) >= abs(obs):
            ge += 1
    return (ge + 1) / (n + 1)

def bootstrap_diff(a,b,seed=43044,n=10000):
    a=np.asarray(a,dtype=float); b=np.asarray(b,dtype=float)
    a=a[np.isfinite(a)]; b=b[np.isfinite(b)]
    if len(a)<10 or len(b)<10:
        return {"n_regime":len(a),"n_complement":len(b),"mean_diff":np.nan,"ci_lo":np.nan,"ci_hi":np.nan,"p_perm":np.nan}
    rng=np.random.default_rng(seed)
    ia=rng.integers(0,len(a),size=(n,len(a)))
    ib=rng.integers(0,len(b),size=(n,len(b)))
    diffs=a[ia].mean(axis=1)-b[ib].mean(axis=1)
    return {
        "n_regime":int(len(a)),
        "n_complement":int(len(b)),
        "mean_diff":float(a.mean()-b.mean()),
        "ci_lo":float(np.quantile(diffs,0.025)),
        "ci_hi":float(np.quantile(diffs,0.975)),
        "p_perm":float(permutation_p(a,b,seed=seed+1,n=n)),
    }

rows=[]
for strategy in defined:
    z=df[(df.strategy==strategy) & (df.split.isin(["development","validation"]))]
    for mode in modes:
        regime=z[z.active_states.apply(lambda x: mode in x)]
        complement=z[z.active_states.apply(lambda x: mode not in x)]
        if len(regime)<10 or len(complement)<10:
            continue
        r=bootstrap_diff(regime.net_rupees.values,complement.net_rupees.values)
        rows.append({"strategy":strategy,"vix_mode":mode,**r,
                     "regime_mean":float(regime.net_rupees.mean()),
                     "complement_mean":float(complement.net_rupees.mean()),
                     "regime_cost50_mean":float(regime.net_plus50_cost_rupees.mean()),
                     "complement_cost50_mean":float(complement.net_plus50_cost_rupees.mean())})
inf=pd.DataFrame(rows)
if len(inf):
    p=inf.p_perm.fillna(1.0).to_numpy()
    order=np.argsort(p); adj=np.empty(len(p)); running=0.0; m=len(p)
    for rank,i in enumerate(order):
        running=max(running,min(1.0,(m-rank)*p[i])); adj[i]=running
    inf["p_holm"]=adj
inf.to_csv(OUT/"strategy_vix_corrected_inference.csv",index=False)

selection=[]
for mode in modes:
    dz=df[(df.split=="development") & (df.strategy.isin(defined)) &
          df.active_states.apply(lambda x: mode in x)]
    if dz.empty:
        continue
    counts=dz.groupby("strategy").size()
    eligible=counts[counts>=15].index
    dz=dz[dz.strategy.isin(eligible)]
    if dz.empty:
        continue
    ranked=dz.groupby("strategy").agg(dev_mean=("net_rupees","mean"),dev_net=("net_rupees","sum"),dev_n=("net_rupees","size")).sort_values("dev_mean",ascending=False)
    chosen=ranked.index[0]
    vz=df[(df.split=="validation")&(df.strategy==chosen)&df.active_states.apply(lambda x: mode in x)]
    hz=df[(df.split=="holdout")&(df.strategy==chosen)&df.active_states.apply(lambda x: mode in x)]
    selection.append({
        "vix_mode":mode,"selected_strategy":chosen,
        "development_n":int(ranked.loc[chosen,"dev_n"]),
        "development_mean":float(ranked.loc[chosen,"dev_mean"]),
        "development_net":float(ranked.loc[chosen,"dev_net"]),
        "validation_n":int(len(vz)),
        "validation_net":float(vz.net_rupees.sum()) if len(vz) else np.nan,
        "validation_mean":float(vz.net_rupees.mean()) if len(vz) else np.nan,
        "validation_cost50_net":float(vz.net_plus50_cost_rupees.sum()) if len(vz) else np.nan,
        "validation_dd":drawdown(vz.sort_values("expiry").net_rupees.values) if len(vz) else np.nan,
        "holdout_n":int(len(hz)),
        "holdout_net":float(hz.net_rupees.sum()) if len(hz) else np.nan,
        "holdout_cost50_net":float(hz.net_plus50_cost_rupees.sum()) if len(hz) else np.nan,
        "holdout_dd":drawdown(hz.sort_values("expiry").net_rupees.values) if len(hz) else np.nan
    })
sel=pd.DataFrame(selection)
sel.to_csv(OUT/"vix_regime_development_selected_strategies.csv",index=False)

# Produce a compact corrected conclusion.
summary=json.loads((OUT/"summary.json").read_text())
sig = inf[(inf.p_holm < 0.05) & (inf.mean_diff > 0)] if len(inf) else pd.DataFrame()
strong = sig[(sig.ci_lo > 0)] if len(sig) else sig
lines=[]
lines.append("# Phase 43 Corrected VIX Inference")
lines.append("")
lines.append("The first inference table was invalid because it compared a VIX-regime subset with the identical rows from the ALL sample, creating mechanically zero differences. This corrected layer compares each regime with its complementary non-regime expiry observations for the same strategy.")
lines.append("")
lines.append(f"- Strategy observations: {summary['trade_rows']}")
lines.append(f"- Corrected strategy×regime tests: {len(inf)}")
lines.append(f"- Holm-adjusted regime advantages with p<0.05 and positive mean difference: {len(sig)}")
lines.append(f"- Holm-adjusted advantages with 95% bootstrap CI entirely above zero: {len(strong)}")
lines.append("")
if len(strong):
    lines.append("## Robust positive regime effects")
    for _,r in strong.sort_values("mean_diff",ascending=False).head(20).iterrows():
        lines.append(f"- {r.strategy} / {r.vix_mode}: mean regime-minus-complement uplift ₹{r.mean_diff:,.2f}; 95% CI ₹{r.ci_lo:,.2f} to ₹{r.ci_hi:,.2f}; Holm p={r.p_holm:.4f}.")
else:
    lines.append("## Robust positive regime effects")
    lines.append("None survived the Holm-adjusted gate with a 95% bootstrap interval entirely above zero.")
lines.append("")
lines.append("## Development-frozen regime selectors")
if len(sel):
    for _,r in sel.iterrows():
        lines.append(f"- {r.vix_mode}: selected {r.selected_strategy}; validation net ₹{r.validation_net:,.2f} across {int(r.validation_n)} trades; +50% cost-stress net ₹{r.validation_cost50_net:,.2f}.")
lines.append("")
lines.append("## Promotion")
lines.append("The Phase-43 promotion gate remains closed because no single VIX-conditioned router passed the preregistered development + validation + cost-stress requirements. Holdout results are therefore diagnostic only.")
(OUT/"PHASE43_CORRECTED_INFERENCE.md").write_text("\n".join(lines))
print(json.dumps({"tests":len(inf),"holm_positive":len(sig),"robust_positive":len(strong),"regime_selectors":len(sel)},indent=2))
