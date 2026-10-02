import os, subprocess, pandas as pd
from pathlib import Path
BASE=Path("results/fixed_otm15_v3/phase7c")
OUT=Path("results/fixed_otm15_v3/phase9e"); OUT.mkdir(parents=True,exist_ok=True)
scenarios=[]
# 9 target/slippage combinations
for target in [0.80,0.90,1.00]:
    for slip in [0,1,2]:
        scenarios.append(("target_slippage",target,slip,10,0,4))
# timing sensitivity at primary target/slippage/DTE
for h,m in [(9,45),(10,0),(10,15)]:
    scenarios.append(("timing",0.90,1,h,m,4))
# DTE sensitivity
for dte in [3,4,5]:
    scenarios.append(("dte",0.90,1,10,0,dte))
rows=[]
for i,(kind,target,slip,h,m,dte) in enumerate(scenarios,1):
    out=OUT/f"scenario_{i:02d}"
    env=os.environ.copy()
    env.update({"OUT_DIR":str(out),"TARGET_FRACTION":str(target),"SLIPPAGE_TICKS":str(slip),
                "ENTRY_HOUR":str(h),"ENTRY_MINUTE":str(m),"DTE_SESSIONS":str(dte)})
    r=subprocess.run(["python","research/backtest_fixed_otm15.py"],env=env,text=True,capture_output=True)
    summ=out/"summary.csv"
    if r.returncode!=0 or not summ.exists():
        rows.append({"scenario":i,"kind":kind,"target_fraction":target,"slippage_ticks":slip,
                     "entry_hour":h,"entry_minute":m,"dte_sessions":dte,"status":"FAILED",
                     "error":(r.stderr[-1000:] if r.stderr else "summary missing")})
        continue
    s=pd.read_csv(summ).iloc[0].to_dict()
    s.update({"scenario":i,"kind":kind,"status":"OK"})
    rows.append(s)
    (out/"run_stdout.txt").write_text(r.stdout)
    if r.stderr: (out/"run_stderr.txt").write_text(r.stderr)
res=pd.DataFrame(rows)
res.to_csv(OUT/"robustness_summary.csv",index=False)
# Brokerage sensitivity can be calculated exactly by re-costing the locked primary trades.
tr=pd.read_csv(BASE/"trades.csv")
broker=[]
for b in [0,10,20]:
    nb=tr["net_rupees"] + (10-b)*6
    broker.append({"brokerage_per_order":b,"trades":len(tr),"mean_net_rupees":nb.mean(),
                   "sum_net_rupees":nb.sum(),"win_rate_net":(nb>0).mean()})
pd.DataFrame(broker).to_csv(OUT/"brokerage_sensitivity.csv",index=False)
print(res.to_string(index=False))
print(pd.DataFrame(broker).to_string(index=False))
