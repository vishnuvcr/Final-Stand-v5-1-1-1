from pathlib import Path
import hashlib, json, os
import pandas as pd
from huggingface_hub import hf_hub_download

ROOT=Path("data/phase51"); ROOT.mkdir(parents=True,exist_ok=True)
sources=[
("rissin/nse-options-intraday","upstox_intraday/NIFTY/NIFTY_2026.parquet","options_2026.parquet"),
("thetrademarkk/india-index-options-1m","index/NIFTY.parquet","spot_nifty.parquet")]
manifest={"sources":[],"oos_window":["2026-04-21","2026-08-04"]}
for repo_id,filename,outname in sources:
    path=hf_hub_download(repo_id=repo_id,filename=filename,repo_type="dataset",token=os.environ.get("HF_TOKEN"))
    target=ROOT/outname
    if not target.exists(): target.write_bytes(Path(path).read_bytes())
    manifest["sources"].append({"repo_id":repo_id,"filename":filename,"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"bytes":target.stat().st_size})
opt=pd.read_parquet(ROOT/"options_2026.parquet",columns=["date","timestamp","underlying","expiry","strike","option_type","open","high","low","close","volume","source","granularity"])
opt=opt[(opt.underlying=="NIFTY")&(opt.granularity=="1min")]
opt["date"]=pd.to_datetime(opt.date)
oos=opt[(opt.date>=pd.Timestamp("2026-04-21"))&(opt.date<=pd.Timestamp("2026-08-04"))]
manifest["option_rows_in_oos"]=int(len(oos))
manifest["option_min_date"]=str(oos.date.min().date())
manifest["option_max_date"]=str(oos.date.max().date())
manifest["option_expiries"]=sorted(pd.to_datetime(oos.expiry).dt.strftime("%Y-%m-%d").dropna().unique().tolist())
manifest["option_has_bid_ask"]=False
spot=pd.read_parquet(ROOT/"spot_nifty.parquet")
spot["timestamp"]=pd.to_datetime(spot.timestamp)
so=spot[(spot.timestamp.dt.date>=pd.Timestamp("2026-04-21").date())&(spot.timestamp.dt.date<=pd.Timestamp("2026-08-04").date())]
manifest["spot_rows_in_oos"]=int(len(so))
manifest["spot_min_ts"]=str(so.timestamp.min()); manifest["spot_max_ts"]=str(so.timestamp.max())
Path("results/phase51").mkdir(parents=True,exist_ok=True)
Path("results/phase51/data_manifest.json").write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
