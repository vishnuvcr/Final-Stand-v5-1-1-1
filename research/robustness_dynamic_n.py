import os
import subprocess
import sys
from pathlib import Path
import pandas as pd

base=Path("results/dynamic_n_corrected/phase12_robustness")
base.mkdir(parents=True,exist_ok=True)

scenarios=[]
for tf in [0.80,0.90,1.00]:
    for slip in [0,1,2]:
        scenarios.append((f"tf{tf:.2f}_slip{slip}",tf,slip,10,0,4,10.0,0.95))
for entry in [(9,45),(10,15)]:
    scenarios.append((f"entry{entry[0]:02d}{entry[1]:02d}",0.90,1,entry[0],entry[1],4,10.0,0.95))
for dte in [3,5]:
    scenarios.append((f"dte{dte}",0.90,1,10,0,dte,10.0,0.95))
for brok in [0,20]:
    scenarios.append((f"brok{int(brok)}",0.90,1,10,0,4,brok,0.95))
for thr in [0.90,0.975]:
    scenarios.append((f"highn{thr:.3f}",0.90,1,10,0,4,10.0,thr))

rows=[]
for name,tf,slip,h,m,dte,brok,thr in scenarios:
    out=f"results/dynamic_n_corrected/phase12_robustness/{name}"
    env=os.environ.copy()
    env.update({
        "OUT_DIR":out,
        "TARGET_FRACTION":str(tf),
        "SLIPPAGE_TICKS":str(slip),
        "ENTRY_HOUR":str(h),
        "ENTRY_MINUTE":str(m),
        "DTE_SESSIONS":str(dte),
        "BROKERAGE_PER_ORDER":str(brok),
        "HIGH_N_THRESHOLD":str(thr),
        "START_DATE":"2021-05-27",
        "END_DATE":"2026-09-30",
        "NIFTY_STRIKE_INTERVAL":"50",
    })
    r=subprocess.run([sys.executable,"research/backtest_dynamic_n_corrected.py"],env=env,text=True,capture_output=True)
    if r.returncode!=0:
        print(r.stdout)
        print(r.stderr,file=sys.stderr)
        raise SystemExit(r.returncode)
    s=pd.read_csv(Path(out)/"summary.csv").iloc[0].to_dict()
    s["scenario"]=name
    rows.append(s)

df=pd.DataFrame(rows)
df.to_csv(base/"robustness_summary.csv",index=False)
print(df[[
    "scenario","trades","sum_net_rupees","mean_net_rupees","win_rate_net",
    "target_exit_rate","mean_selected_n","high_n_threshold_fraction"
]].to_string(index=False))
