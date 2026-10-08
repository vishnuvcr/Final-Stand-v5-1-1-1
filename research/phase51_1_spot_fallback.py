from pathlib import Path
import pandas as pd
from huggingface_hub import hf_hub_download

out=Path("data/phase51/spot_fallback.parquet")
p=hf_hub_download(
    repo_id="Jitendra12421/AlargeDatabase",
    filename="INDDEX FILES/NIFTY_minute.parquet",
    repo_type="dataset",
)
out.parent.mkdir(parents=True,exist_ok=True)
out.write_bytes(Path(p).read_bytes())
df=pd.read_parquet(out)
print(df.columns.tolist())
print(df.tail())
