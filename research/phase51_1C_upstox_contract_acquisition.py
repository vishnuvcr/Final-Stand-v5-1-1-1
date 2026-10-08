import json, os, hashlib
from pathlib import Path
import requests

EXPIRIES=["2026-07-28","2026-08-04"]
BASE="https://api.upstox.com/v2"
TOKEN=os.environ.get("UPSTOX_ACCESS_TOKEN")
OUT=Path("data/phase51/upstox")
OUT.mkdir(parents=True,exist_ok=True)

if not TOKEN:
    Path("results/phase51").mkdir(parents=True,exist_ok=True)
    Path("results/phase51/upstox_access_gate.json").write_text(json.dumps({
        "status":"BLOCKED",
        "reason":"UPSTOX_ACCESS_TOKEN secret is not configured in the repository"
    },indent=2))
    raise SystemExit(2)

headers={"Authorization":f"Bearer {TOKEN}","Accept":"application/json"}
session=requests.Session()
session.headers.update(headers)

manifest={"source":"Upstox expired-instruments API","expiries":EXPIRIES,"contracts":[]}

for expiry in EXPIRIES:
    url=f"{BASE}/expired-instruments/option/contract"
    r=session.get(url,params={"instrument_key":"NSE_INDEX|Nifty 50","expiry_date":expiry},timeout=60)
    r.raise_for_status()
    payload=r.json()
    if payload.get("status")!="success":
        raise RuntimeError(f"Upstox contract API failed for {expiry}: {payload}")
    data=payload.get("data",[])
    if not data:
        raise RuntimeError(f"No expired NIFTY option contracts returned for {expiry}")
    p=OUT/f"contracts_{expiry}.json"
    p.write_text(json.dumps(data,indent=2))
    manifest["contracts"].append({
        "expiry":expiry,
        "rows":len(data),
        "sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
        "bytes":p.stat().st_size,
        "min_strike":min(float(x["strike_price"]) for x in data),
        "max_strike":max(float(x["strike_price"]) for x in data),
        "ce_count":sum(x.get("instrument_type")=="CE" for x in data),
        "pe_count":sum(x.get("instrument_type")=="PE" for x in data)
    })

manifest["status"]="PASS"
Path("results/phase51").mkdir(parents=True,exist_ok=True)
Path("results/phase51/upstox_contract_manifest.json").write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
