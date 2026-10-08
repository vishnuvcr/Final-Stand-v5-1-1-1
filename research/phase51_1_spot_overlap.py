from pathlib import Path
import pandas as pd
from huggingface_hub import hf_hub_download

root=Path("data/phase51"); root.mkdir(parents=True,exist_ok=True)
a=hf_hub_download(repo_id="thetrademarkk/india-index-options-1m",filename="index/NIFTY.parquet",repo_type="dataset")
b=hf_hub_download(repo_id="Jitendra12421/AlargeDatabase",filename="INDDEX FILES/NIFTY_minute.parquet",repo_type="dataset")
df1=pd.read_parquet(a); df2=pd.read_parquet(b)
print("source1",df1.columns.tolist()); print("source2",df2.columns.tolist())
