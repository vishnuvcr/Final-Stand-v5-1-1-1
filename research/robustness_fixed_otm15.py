import os, subprocess, sys
from pathlib import Path
import pandas as pd

scenarios=[]
for tf in [0.80,0.90,1.00]:
    for slip in [0,1,2]:
        scenarios.append((f"tf{tf:.2f}_slip{slip}",tf,slip,10,0,4,10.0))
for entry in [(9,45),(10,15)]:
    scenarios.append((f"entry{entry[0]:02d}{entry[1]:02d}",0.90,1,entry[0],entry[1],4,10.0))
for dte in [3,5]:
    scenarios.append((f"dte{dte}",0.90,1,10,0,dte,10.0))
for brok in [0,20]:
    scenarios.append((f"brok{int(brok)}",0.90,1,10,0,4,brok))

out=Path("results/fixed_otm15_v3/phase9"); out.mkdir(parents=True,exist_ok=True)
rows=[]
for name,tf,slip,h,m,dte,brok in scenarios:
    env=os.environ.copy()
    env.update({"OUT_DIR":f"results/fixed_otm15_v3/phase9/{name}","TARGET_FRACTION":str(tf),
                "SLIPPAGE_TICKS":str(slip),"ENTRY_HOUR":str(h),"ENTRY_MINUTE":str(m),
                "DTE_SESSIONS":str(dte),"BROKERAGE_PER_ORDER":str(brok)})
    r=subprocess.run([sys.executable,"research/backtest_fixed_otm15.py"],env=env,text=True,capture_output=True)
    if r.returncode!=0:
        print(r.stdout); print(r.stderr,file=sys.stderr); raise SystemExit(r.returncode)
    s=pd.read_csv(f"results/fixed_otm15_v3/phase9/{name}/summary.csv").iloc[0].to_dict()
    s["scenario"]=name
    rows.append(s)
pd.DataFrame(rows).to_csv(out/"robustness_summary.csv",index=False)
print(pd.DataFrame(rows)[["scenario","trades","sum_net_rupees","mean_net_rupees","win_rate_net","target_exit_rate"]].to_string(index=False))
