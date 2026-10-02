import os
import subprocess
from pathlib import Path
import pandas as pd

scenarios = []
for th in [0.90,0.95,0.975]:
    for slip in [0,1,2]:
        scenarios.append((f"threshold_{th}_slip_{slip}", {"HIGH_N_THRESHOLD":th,"SLIPPAGE_TICKS":slip,"ENTRY_HOUR":10,"ENTRY_MINUTE":0,"DTE_SESSIONS":4,"BROKERAGE_PER_ORDER":10}))
for label,h,m in [("entry_0945",9,45),("entry_1000",10,0),("entry_1015",10,15)]:
    scenarios.append((label, {"HIGH_N_THRESHOLD":0.95,"SLIPPAGE_TICKS":1,"ENTRY_HOUR":h,"ENTRY_MINUTE":m,"DTE_SESSIONS":4,"BROKERAGE_PER_ORDER":10}))
for dte in [3,4,5]:
    scenarios.append((f"dte_{dte}", {"HIGH_N_THRESHOLD":0.95,"SLIPPAGE_TICKS":1,"ENTRY_HOUR":10,"ENTRY_MINUTE":0,"DTE_SESSIONS":dte,"BROKERAGE_PER_ORDER":10}))

root=Path("results/restarted_v2/phase4")
root.mkdir(parents=True,exist_ok=True)
rows=[]
for label,envv in scenarios:
    out=root/label
    out.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy()
    env.update({k:str(v) for k,v in envv.items()})
    env["OUT_DIR"]=str(out)
    env["START_DATE"]="2021-05-27"
    env["END_DATE"]="2026-09-30"
    p=subprocess.run(["python","research/backtest_restarted_v2.py"],env=env,text=True,capture_output=True)
    (out/"run_stdout.txt").write_text(p.stdout+"\nSTDERR\n"+p.stderr)
    sfile=out/"summary.csv"
    if sfile.exists():
        s=pd.read_csv(sfile).iloc[0].to_dict()
        s["scenario"]=label
        s["returncode"]=int(p.returncode)
        s.update(envv)
        rows.append(s)
    else:
        rows.append({"scenario":label,"returncode":p.returncode,**envv})
summary=pd.DataFrame(rows)
summary.to_csv(root/"robustness_summary.csv",index=False)

# Brokerage sensitivity is an exact arithmetic re-costing of the primary trade set,
# because only fixed brokerage changes; all other modeled costs remain unchanged.
tr=pd.read_csv("results/restarted_v2/trades.csv")
base=tr["net_rupees"]
for br in [0,10,20]:
    delta=(br-10)*6
    x=base-delta
    rows.append({
        "scenario":f"brokerage_{br}_per_order_from_primary",
        "BROKERAGE_PER_ORDER":br,
        "trades":len(x),
        "win_rate_net":float((x>0).mean()),
        "mean_net_rupees":float(x.mean()),
        "median_net_rupees":float(x.median()),
        "sum_net_rupees":float(x.sum()),
        "sum_cost_rupees_adjusted":float(tr.cost_rupees.sum()+delta*len(x))
    })
pd.DataFrame(rows).to_csv(root/"robustness_summary_with_brokerage.csv",index=False)
print(pd.DataFrame(rows).to_string(index=False))
