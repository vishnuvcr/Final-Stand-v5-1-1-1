"""Phase-51 primary-source adapter.

This module is deliberately narrow: it changes only the frozen replay engines'
data/expiry dependencies. Strategy rules, execution semantics, costs and
parameters remain in the original Phase-50B engines.
"""
from __future__ import annotations
import glob, hashlib, os, re
from pathlib import Path
import pandas as pd
from huggingface_hub import hf_hub_download

TZ = "Asia/Kolkata"
OPTIONS_REPO = "rissin/nse-options-intraday"
OPTIONS_FILE = "upstox_intraday/NIFTY/NIFTY_2026.parquet"
EXPECTED_SHA256 = "bae9943b2fa99ee9c1214fb7c695b84f9f661a050a5cd04d9c5c2ffc7bc59f73"
EXPECTED_BYTES = 394805617
SPOT_ROOT = Path(os.environ.get("PHASE51_SPOT_ROOT", "data/validated_spot_source"))
WINDOW_START = pd.Timestamp("2026-04-21", tz=TZ)
WINDOW_END = pd.Timestamp("2026-07-21 23:59:59", tz=TZ)

def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def prepare():
    p = hf_hub_download(repo_id=OPTIONS_REPO, filename=OPTIONS_FILE,
                         repo_type="dataset", token=os.getenv("HF_TOKEN") or None)
    size = os.path.getsize(p)
    sha = _sha256(p)
    if size != EXPECTED_BYTES or sha != EXPECTED_SHA256:
        raise RuntimeError(f"Primary option source integrity mismatch: bytes={size}, sha256={sha}")
    spot_files = sorted(glob.glob(str(SPOT_ROOT / "nifty" / "1min" / "2026" / "*.csv")))
    if not spot_files:
        raise RuntimeError(f"No validated 2026 1-minute NIFTY spot files under {SPOT_ROOT}")
    return p, spot_files

_OPTIONS_PATH = None
_EXPIRIES = None
_SPOT = None

def _init():
    global _OPTIONS_PATH, _EXPIRIES, _SPOT
    if _OPTIONS_PATH is not None:
        return
    _OPTIONS_PATH, spot_files = prepare()
    # The primary RISSIN file is the only options source. Expiries are derived
    # from its observed NIFTY 1-minute rows, not from an old strategy matrix.
    e = pd.read_parquet(_OPTIONS_PATH, columns=["expiry", "underlying", "granularity"])
    e["expiry"] = pd.to_datetime(e["expiry"], errors="coerce")
    e = e[(e["underlying"].astype(str).str.upper()=="NIFTY") &
          (e["granularity"].astype(str).str.lower()=="1min")]
    ex = sorted(pd.Timestamp(x, tz=TZ) for x in e["expiry"].dropna().dt.date.unique()
                if pd.Timestamp(x, tz=TZ) >= WINDOW_START and pd.Timestamp(x, tz=TZ) <= WINDOW_END)
    if not ex:
        raise RuntimeError("Primary options source has no NIFTY 1-minute expiries in Phase-51-3 window")
    _EXPIRIES = ex

    frames=[]
    for f in spot_files:
        z=pd.read_csv(f)
        if "Timestamp" not in z.columns or "Close" not in z.columns:
            raise RuntimeError(f"Validated spot file missing Timestamp/Close: {f}")
        t=pd.to_datetime(z["Timestamp"], errors="coerce")
        if getattr(t.dt, "tz", None) is None:
            t=t.dt.tz_localize(TZ)
        else:
            t=t.dt.tz_convert(TZ)
        frames.append(pd.DataFrame({"timestamp":t, "close":pd.to_numeric(z["Close"],errors="coerce")}))
    spot=pd.concat(frames,ignore_index=True).dropna().drop_duplicates("timestamp").sort_values("timestamp")
    spot=spot[(spot.timestamp>=WINDOW_START)&(spot.timestamp<=WINDOW_END)]
    if spot.empty:
        raise RuntimeError("Validated spot source has no rows in Phase-51-3 window")
    _SPOT=spot.reset_index(drop=True)

def expiries():
    _init()
    return list(_EXPIRIES)

def load_parquet(name: str):
    _init()
    if name == "index/NIFTY.parquet":
        return _SPOT.copy()
    m=re.fullmatch(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet", name)
    if not m:
        raise ValueError(f"Unexpected frozen engine path: {name}")
    expiry=m.group(1)
    # PyArrow predicate pushdown keeps this source-faithful while avoiding a
    # full annual DataFrame copy for every weekly contract.
    z=pd.read_parquet(_OPTIONS_PATH, filters=[
        ("underlying","=","NIFTY"), ("granularity","=","1min"), ("expiry","=",expiry)
    ])
    if z.empty:
        raise FileNotFoundError(f"Primary RISSIN source has no NIFTY 1-minute rows for expiry {expiry}")
    z["timestamp"]=pd.to_datetime(z["timestamp"])
    if z["timestamp"].dt.tz is None: z["timestamp"]=z["timestamp"].dt.tz_localize(TZ)
    else: z["timestamp"]=z["timestamp"].dt.tz_convert(TZ)
    z["strike"]=pd.to_numeric(z["strike"],errors="coerce")
    z["option_type"]=z["option_type"].astype(str).str.upper()
    z["close"]=pd.to_numeric(z["close"],errors="coerce")
    z=z.dropna(subset=["timestamp","strike","close"]).sort_values(["timestamp","option_type","strike"])
    return z[["timestamp","strike","option_type","close","volume","oi"]].copy()

def source_manifest():
    _init()
    return {
        "options_repo":OPTIONS_REPO, "options_file":OPTIONS_FILE,
        "options_sha256":EXPECTED_SHA256, "options_bytes":EXPECTED_BYTES,
        "observed_expiries":[str(x.date()) for x in _EXPIRIES],
        "spot_root":str(SPOT_ROOT), "spot_rows":int(len(_SPOT)),
        "spot_first":str(_SPOT.timestamp.min()), "spot_last":str(_SPOT.timestamp.max()),
        "window":[str(WINDOW_START),str(WINDOW_END)]
    }
