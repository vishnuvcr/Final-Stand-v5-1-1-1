import json, math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import binomtest
from statsmodels.stats.multitest import multipletests

ROOT=Path("results/phase50b")
OUT=ROOT/"phase50b6_statistical_inference"
OUT.mkdir(parents=True, exist_ok=True)

FILES={
 "TT03":"tt03_dynamic_n_replay/tt03_trades.csv",
 "TT03_OTM350":"tt03_far_otm/OTM350/tt03_trades.csv",
 "TT04":"tt04_premium_match_replay/tt04_trades.csv",
 "TT05":"tt05_short_straddle_replay/tt05_trades.csv",
}
COSTS=["net","net50","net20","net20_50"]
SEED=5062026
N_BOOT=10000
N_PERM=10000
ALPHA=.05

def load(rel):
    d=pd.read_csv(ROOT/rel)
    d["expiry_dt"]=pd.to_datetime(d["expiry"],utc=True)
    d["entry_dt"]=pd.to_datetime(d.get("entry_ts",d["expiry"]),utc=True)
    return d.sort_values(["entry_dt","expiry_dt"]).reset_index(drop=True)

def split(y):
    return "DEV" if y<=2023 else ("VAL" if y<=2025 else "HOLD")

def grouped_block_bootstrap(x, rng, B=N_BOOT):
    # Resample expiry-day blocks, preserving all trades from each expiry together.
    x=x.copy()
    x["block"]=x["expiry_dt"].dt.strftime("%Y-%m-%d")
    blocks=[g.values for _,g in x.groupby("block",sort=True)]
    if not blocks: return np.array([])
    vals=np.concatenate([b for b in blocks])
    idx=np.arange(len(blocks))
    means=np.empty(B)
    for i in range(B):
        chosen=rng.choice(idx,size=len(idx),replace=True)
        sample=np.concatenate([blocks[j] for j in chosen])
        means[i]=float(np.mean(sample))
    return means

def paired_sign_permutation(x, rng, B=N_PERM):
    # Exact-null sign randomization: trade magnitudes fixed, signs randomized.
    x=np.asarray(x,dtype=float)
    obs=float(x.mean())
    n=len(x)
    if n==0: return np.nan
    ge=0
    for _ in range(B):
        signs=rng.choice(np.array([-1.0,1.0]),size=n)
        stat=float(np.mean(np.abs(x)*signs))
        if stat>=obs-1e-15: ge+=1
    return (ge+1)/(B+1)

rows=[]
rng=np.random.default_rng(SEED)
for strategy,rel in FILES.items():
    d=load(rel)
    d["split"]=d["expiry_dt"].dt.year.map(split)
    d=d[d["split"].isin(["DEV","VAL"])].copy()
    for cost in COSTS:
        x=pd.to_numeric(d[cost],errors="coerce").dropna().to_numpy(float)
        n=len(x)
        mean=float(x.mean()) if n else np.nan
        median=float(np.median(x)) if n else np.nan
        wins=int((x>0).sum())
        sign_p=float(binomtest(wins,n,.5,alternative="greater").pvalue) if n else np.nan
        perm_p=paired_sign_permutation(x,rng) if n else np.nan
        # Independent seeded stream per hypothesis for reproducibility.
        b=grouped_block_bootstrap(d[[cost,"expiry_dt"]].rename(columns={cost:"v"}).assign(v=pd.to_numeric(d[cost],errors="coerce")),rng)
        lo=float(np.quantile(b,.025)) if len(b) else np.nan
        hi=float(np.quantile(b,.975)) if len(b) else np.nan
        rows.append(dict(strategy=strategy,cost_model=cost,n=n,mean=mean,median=median,
                         wins=wins,win_rate=wins/n if n else np.nan,
                         sign_test_p=sign_p,permutation_p=perm_p,
                         block_bootstrap_ci_low=lo,block_bootstrap_ci_high=hi))
res=pd.DataFrame(rows)
# Primary multiplicity family: all 16 strategy x cost hypotheses, fixed before seeing results.
rej,q,_,_=multipletests(res["permutation_p"].fillna(1).to_numpy(),alpha=ALPHA,method="holm")
res["holm_reject"]=rej
res["holm_q"]=q
res["primary_positive"]=(res["mean"]>0)&(res["block_bootstrap_ci_low"]>0)&res["holm_reject"]

# A stricter robustness flag requires every cost model to pass the primary gate.
robust=[]
for s,g in res.groupby("strategy"):
    robust.append({"strategy":s,
                   "all_four_costs_primary_positive":bool(g["primary_positive"].all()),
                   "all_four_holm_reject":bool(g["holm_reject"].all()),
                   "min_holm_q":float(g["holm_q"].min()),
                   "min_bootstrap_ci_low":float(g["block_bootstrap_ci_low"].min())})
rob=pd.DataFrame(robust)
res.to_csv(OUT/"hypothesis_results.csv",index=False)
rob.to_csv(OUT/"strategy_robustness_summary.csv",index=False)

# Protected holdout is descriptive only; no test statistic from HOLD is used.
hold=[]
for strategy,rel in FILES.items():
    d=load(rel); d["split"]=d["expiry_dt"].dt.year.map(split); d=d[d.split=="HOLD"]
    for cost in COSTS:
        x=pd.to_numeric(d[cost],errors="coerce").dropna()
        hold.append({"strategy":strategy,"cost_model":cost,"n":len(x),"net":float(x.sum()) if len(x) else 0.0,
                      "mean":float(x.mean()) if len(x) else np.nan})
pd.DataFrame(hold).to_csv(OUT/"holdout_descriptive.csv",index=False)

meta={
 "phase":"50B-6",
 "inference_population":"DEV+VAL only (2021-2025)",
 "protected_holdout":"2026 descriptive only; excluded from hypothesis testing, Holm correction and selection",
 "hypotheses":"H0: expected trade-level net P&L <= 0; H1: > 0",
 "primary_test":"10,000 sign-randomization permutations of fixed trade magnitudes",
 "dependence_robustness":"10,000 expiry-day block bootstrap confidence intervals",
 "secondary":"one-sided binomial sign test",
 "multiplicity":"Holm correction across fixed 16 strategy x cost hypotheses",
 "promotion_statistical_gate":"positive mean AND 95% expiry-block bootstrap lower bound > 0 AND Holm-adjusted permutation p < 0.05; robustness additionally requires this at all four registered cost models",
 "cost_models":COSTS,
 "seed":SEED,
 "bootstrap_replicates":N_BOOT,
 "permutation_replicates":N_PERM,
 "capital_normalized_return_claim":False,
 "no_new_selection_or_tuning":True
}
(OUT/"methodology.json").write_text(json.dumps(meta,indent=2))
summary={"strategies":list(FILES),"hypotheses":len(res),"robust_positive_strategies":rob.loc[rob.all_four_costs_primary_positive,"strategy"].tolist(),
         "any_primary_positive":bool(res.primary_positive.any()),"holdout_protected":True}
(OUT/"inference_summary.json").write_text(json.dumps(summary,indent=2))
print(res.to_string(index=False))
print(json.dumps(summary,indent=2))
