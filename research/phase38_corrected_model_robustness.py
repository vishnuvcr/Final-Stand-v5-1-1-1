import os, json
from pathlib import Path
import numpy as np, pandas as pd

ROOT=Path("results/phase37_model_direction_polarity_correction")
OUT=Path("results/phase38_corrected_model_robustness"); OUT.mkdir(parents=True,exist_ok=True)
SELECTORS=["CATBOOST","MARKOV_REGIME_TREE","WAVELET_TREE","OOF_STACK","DART"]
rng=np.random.default_rng(38001)

def load_trades(path):
    z=pd.read_csv(path)
    z["expiry"]=pd.to_datetime(z["expiry"]).dt.date.astype(str)
    z["exit_ts"]=pd.to_datetime(z["exit_ts"], errors="coerce")
    return z

def aggregate_expiry(z):
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
        "selector_common_net":float(x.net_sel.sum()),
        "control_common_net":float(x.net_ctl.sum()),
        "total_difference":float(d.sum()),
    }

def stress(trades):
    gross=trades.gross_rupees.sum(); cost=trades.cost_rupees.sum()
    return {
      "base_net":float(trades.net_rupees.sum()),
      "plus_25pct_cost_net":float(gross-cost*1.25),
      "plus_50pct_cost_net":float(gross-cost*1.50),
      "plus_100pct_cost_net":float(gross-cost*2.00),
    }

def summary(trades, selector):
    net=trades.net_rupees
    gp=float(net[net>0].sum()); gl=float(-net[net<0].sum())
    dd=float(abs(trades.drawdown.min())) if "drawdown" in trades.columns else float("nan")
    return {
        "selector":selector,
        "trades":int(len(trades)),
        "net":float(net.sum()),
        "gross":float(trades.gross_rupees.sum()),
        "costs":float(trades.cost_rupees.sum()),
        "win_rate":float((net>0).mean()),
        "profit_factor":float(gp/gl) if gl else float("inf"),
        "max_drawdown":dd,
    }

def main():
    control_path=Path("results/dynamic_strategy_phase32/trades.csv")
    if not control_path.exists():
        raise FileNotFoundError(control_path)
    ctl=load_trades(control_path)
    ctl_exp=aggregate_expiry(ctl)
    ctl_year=ctl.groupby(ctl.exit_ts.dt.year).net_rupees.sum().to_dict()
    ctl_summary=summary(ctl,"STATEFUL_CONTROL")

    rows=[]; stress_rows=[]; summary_rows=[ctl_summary]; yearly_rows=[]; direction_rows=[]
    for y,v in ctl_year.items():
        yearly_rows.append({"selector":"STATEFUL_CONTROL","year":int(y),"trades":int((ctl.exit_ts.dt.year==y).sum()),"net":float(v)})

    for s in SELECTORS:
        tr=load_trades(ROOT/s/"trades.csv")
        sel=aggregate_expiry(tr)
        boot=bootstrap(sel,ctl_exp); boot["selector"]=s; rows.append(boot)
        ss=stress(tr); ss["selector"]=s; stress_rows.append(ss)
        summary_rows.append(summary(tr,s))
        for y,g in tr.groupby(tr.exit_ts.dt.year):
            yearly_rows.append({"selector":s,"year":int(y),"trades":int(len(g)),"net":float(g.net_rupees.sum())})
        for d,g in tr.groupby("direction"):
            yearly_rows.append({"selector":s,"year":"ALL_"+d,"trades":int(len(g)),"net":float(g.net_rupees.sum())})
            direction_rows.append({"selector":s,"direction":d,"trades":int(len(g)),"net":float(g.net_rupees.sum()),"share_of_trades":float(len(g)/len(tr))})
        print(s,boot,ss,flush=True)

    pd.DataFrame(rows).to_csv(OUT/"paired_bootstrap.csv",index=False)
    pd.DataFrame(stress_rows).to_csv(OUT/"cost_stress.csv",index=False)
    pd.DataFrame(summary_rows).to_csv(OUT/"selector_summary.csv",index=False)
    pd.DataFrame(yearly_rows).to_csv(OUT/"yearly_results.csv",index=False)
    pd.DataFrame(direction_rows).to_csv(OUT/"direction_asymmetry.csv",index=False)
    with open(OUT/"control_yearly.json","w") as f:
        json.dump({str(k):float(v) for k,v in ctl_year.items()},f,indent=2)

if __name__=="__main__":
    main()
