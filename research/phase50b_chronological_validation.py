import json
from pathlib import Path
import math
import pandas as pd
import numpy as np

ROOT=Path("results/phase50b")
OUT=ROOT/"phase50b5_chronological_validation"
OUT.mkdir(parents=True,exist_ok=True)

FILES={
    "TT03":"tt03_dynamic_n_replay/tt03_trades.csv",
    "TT03_OTM350":"tt03_far_otm/OTM350/tt03_trades.csv",
    "TT04":"tt04_premium_match_replay/tt04_trades.csv",
    "TT05":"tt05_short_straddle_replay/tt05_trades.csv",
}

def load(name, rel):
    p=ROOT/rel
    if not p.exists():
        raise FileNotFoundError(str(p))
    d=pd.read_csv(p)
    for c in ["net","net50","net20","net20_50"]:
        if c not in d.columns:
            raise AssertionError(f"{name}: missing {c}")
        d[c]=pd.to_numeric(d[c],errors="coerce")
    assert d[["net","net50","net20","net20_50"]].notna().all().all(), name
    if "expiry" not in d.columns:
        raise AssertionError(f"{name}: missing expiry")
    d["expiry_dt"]=pd.to_datetime(d["expiry"],utc=True)
    if "entry_ts" in d.columns:
        d["entry_dt"]=pd.to_datetime(d["entry_ts"],utc=True)
    else:
        d["entry_dt"]=d["expiry_dt"]
    return d.sort_values(["entry_dt","expiry_dt"]).reset_index(drop=True)

def split_of(exp):
    y=exp.year
    return "DEV" if y<=2023 else ("VAL" if y<=2025 else "HOLD")

def metrics(x, cost_col="net"):
    x=x.sort_values(["entry_dt","expiry_dt"]).copy()
    x["equity"]=x[cost_col].cumsum()
    x["peak"]=x["equity"].cummax()
    x["drawdown"]=x["equity"]-x["peak"]
    x["drawdown_pct"]=np.where(x["peak"]>0, x["drawdown"]/x["peak"]*100.0, np.nan)
    max_dd=float(x["drawdown"].min()) if len(x) else 0.0
    dd_pct=float(x["drawdown_pct"].min()) if len(x) and x["drawdown_pct"].notna().any() else np.nan
    return {
        "trades":int(len(x)),
        "net":float(x[cost_col].sum()),
        "profit_per_trade":float(x[cost_col].mean()) if len(x) else np.nan,
        "median_trade":float(x[cost_col].median()) if len(x) else np.nan,
        "win_rate":float((x[cost_col]>0).mean()) if len(x) else np.nan,
        "worst_trade":float(x[cost_col].min()) if len(x) else np.nan,
        "best_trade":float(x[cost_col].max()) if len(x) else np.nan,
        "max_drawdown_rupees":max_dd,
        "max_drawdown_pct_of_prior_equity_peak":dd_pct,
        "final_equity":float(x["equity"].iloc[-1]) if len(x) else 0.0,
    }

all_results=[]
equity_rows=[]
for name,rel in FILES.items():
    d=load(name,rel)
    d["split"]=d["expiry_dt"].apply(split_of)
    rec={"strategy":name}
    for cost in ["net","net50","net20","net20_50"]:
        m=metrics(d,cost)
        for k,v in m.items():
            rec[f"{cost}_{k}"]=v
    for split in ["DEV","VAL","HOLD","ALL"]:
        z=d if split=="ALL" else d[d["split"]==split]
        m=metrics(z,"net")
        for k,v in m.items():
            rec[f"{split.lower()}_{k}"]=v
    rec["coverage_gate_deferred_to_audit"] = name!="TT03_OTM350"
    all_results.append(rec)
    e=d[["entry_dt","expiry_dt","split","net","net50","net20","net20_50"]].copy()
    e.insert(0,"strategy",name)
    e["trade_index"]=range(1,len(e)+1)
    e["equity_net"]=e["net"].cumsum()
    e["peak_net"]=e["equity_net"].cummax()
    e["drawdown_net"]=e["equity_net"]-e["peak_net"]
    equity_rows.append(e)

summary=pd.DataFrame(all_results)
summary.to_csv(OUT/"chronological_strategy_summary.csv",index=False)
pd.concat(equity_rows,ignore_index=True).to_csv(OUT/"chronological_equity.csv",index=False)

# Cross-check finite accepted total P&L for TT03/TT04/TT05 where known from repository evidence.
expected={
    "TT03":{"net":89669.15,"net50":82074.11,"net20":75509.15,"net20_50":60834.11},
    "TT04":{"net":55582.71,"net50":11429.95,"net20":-1718.09,"net20_50":-74521.25},
    "TT05":{"net":52337.89,"net50":9429.09,"net20":-3546.91,"net20_50":-74398.11},
}
checks=[]
for name,vals in expected.items():
    r=summary[summary.strategy==name].iloc[0]
    ok=all(math.isclose(float(r[f"{k}"]),v,rel_tol=0,abs_tol=0.05) for k,v in vals.items())
    checks.append({"strategy":name,"accepted_total_crosscheck":ok,"observed":{k:float(r[k]) for k in vals},"expected":vals})
    assert ok,(name,r.to_dict())

(OUT/"cross_checks.json").write_text(json.dumps({"checks":checks,"holdout_protected":True,
    "capital_normalized_return_claim":False,
    "reason":"No consistent accepted capital/margin denominator exists in the trade-only artifacts; only chronological equity drawdown percentage is reported."},indent=2))
print(summary[["strategy","net_profit_per_trade","net20_50_profit_per_trade"]].to_string(index=False) if "net_profit_per_trade" in summary else summary[["strategy","net_profit_per_trade"]].to_string(index=False))
print(json.dumps({"strategies":list(FILES),"rows":len(summary),"crosschecks":checks},indent=2))
