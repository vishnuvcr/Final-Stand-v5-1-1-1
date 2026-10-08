import json, os
from pathlib import Path

names=[
    "UPSTOX_ACCESS_TOKEN",
    "DHAN_ACCESS_TOKEN",
    "ICICI_BREEZE_API_KEY",
    "ICICI_BREEZE_API_SECRET",
    "ICICI_BREEZE_SESSION_TOKEN",
]
status={n: bool(os.environ.get(n)) for n in names}
recommended = (
    "UPSTOX" if status["UPSTOX_ACCESS_TOKEN"] else
    "ICICI_BREEZE" if status["ICICI_BREEZE_API_KEY"] and status["ICICI_BREEZE_SESSION_TOKEN"] else
    "DHAN" if status["DHAN_ACCESS_TOKEN"] else
    "OPTIONS_DATA_SHOP_OR_OTHER_AUTHORIZED_ARCHIVE"
)
out={"status":status,"next_route":recommended}
Path("results/phase51").mkdir(parents=True,exist_ok=True)
Path("results/phase51/authorized_access_inventory.json").write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
