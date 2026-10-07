import json
from pathlib import Path
from phase43_vix_strategy_sweep import load_parquet
p=load_parquet("options/NIFTY/2026-01-29.parquet")
out={"columns":list(p.columns),"dtypes":{k:str(v) for k,v in p.dtypes.items()},"rows":int(len(p)),"head":p.head(3).to_dict("records")}
Path("results/phase50b/schema_probe.json").parent.mkdir(parents=True,exist_ok=True)
Path("results/phase50b/schema_probe.json").write_text(json.dumps(out,indent=2,default=str))
print(json.dumps(out,indent=2,default=str))
