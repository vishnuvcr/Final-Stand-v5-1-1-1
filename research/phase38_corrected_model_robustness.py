import os, json
from pathlib import Path
import numpy as np, pandas as pd

ROOT=Path("results/phase37_model_direction_polarity_correction")
OUT=Path("results/phase38_corrected_model_robustness"); OUT.mkdir(parents=True,exist_ok=True)
SELECTORS=["CATBOOST","MARKOV_REGIME_TREE","WAVELET_TREE","OOF_STACK","DART"]
rng=np.random.default_rng(38001)

def load_net(path):
    z=pd.read_csv(path)
    z["expiry"]=pd.to_datetime(z["expiry"]).dt.date.astype(str)
    return z.groupby("expiry",as_index=False).net_rupees.sum().rename(columns={"net_rupees":"net"})

def bootstrap(a,b,n=10000):
    x=a.merge(b,on="expiry",suffixes=("_sel","_ctl"),how="inner")
    d=(x.net_sel-x.net_ctl).to_numpy(float)
    if len(d)==0: raise RuntimeError("No common expiries")
    idx=rng.integers(0,len(d),size=(n,len(d)))
    means=d[idx].mean(axis=1)
    return {
        "common_expiries":int(len(d)),
        "mean_difference":float(d.mean()),
        "median_difference":float(np.median(d)),
        "ci_2_5":float(np.quantile(means,.025)),
        "ci_97_5":float(np.quantile(means,.975)),
        "prob_selector_beats_control":float((means>0).mean()),
        "expiry_block_win_rate":float((d>0).mean()),
    }

def stress(trades):
    gross=trades.gross_rupees.sum(); cost=trades.cost_rupees.sum()
    return {
      "base_net":float(trades.net_rupees.sum()),
      "plus_25pct_cost_net":float(gross-cost*1.25),
      "plus_50pct_cost_net":float(gross-cost*1.50),
      "plus_100pct_cost_net":float(gross-cost*2.00),
    }

def main():
    control=Path("results/dynamic_strategy_phase32/trades.csv")
    if not control.exists(): raise FileNotFoundError(control)
    ctl=pd.read_csv(control)
    ctl["expiry"]=pd.to_datetime(ctl["expiry"]).dt.date.astype(str)
    ctl_year=ctl.assign(year=pd.to_datetime(ctl.exit_ts).dt.year).groupby("year").net_rupees.sum().to_dict()

    rows=[]; stress_rows=[]
    for s in SELECTORS:
        p=ROOT/s/"trades.csv"
        if not p.exists(): raise FileNotFoundError(p)
        tr=pd.read_csv(p)
        tr["expiry"]=pd.to_datetime(tr["expiry"]).dt.date.astype(str)
        sel=tr.groupby("expiry",as_index=False).net_rupees.sum().rename(columns={"net_rupees":"net"})
        ctl2=ctl.groupby("expiry",as_index=False).net_rupees.sum().rename(columns={"net_rupees":"net"})
        boot=bootstrap(sel,ctl2)
        boot["selector"]=s
        rows.append(boot)
        ss=stress(tr); ss["selector"]=s; stress_rows.append(ss)
        yr=tr.assign(year=pd.to_datetime(tr.exit_ts).dt.year).groupby("year").net_rupees.sum().to_dict()
        print(s,boot,ss,yr,flush=True)

    pd.DataFrame(rows).to_csv(OUT/"paired_bootstrap.csv",index=False)
    pd.DataFrame(stress_rows).to_csv(OUT/"cost_stress.csv",index=False)
    with open(OUT/"control_yearly.json","w") as f: json.dump({str(k):float(v) for k,v in ctl_year.items()},f,indent=2)

if __name__=="__main__": main()
