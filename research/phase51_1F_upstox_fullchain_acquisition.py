import concurrent.futures
import gzip, hashlib, json, os, time
from pathlib import Path
import requests

EXPIRIES = ["2026-07-28", "2026-08-04"]
OOS_START = "2026-04-21"
BASE = "https://api.upstox.com/v2"
TOKEN = os.environ.get("UPSTOX_ACCESS_TOKEN")
ROOT = Path("data/phase51/upstox_1f")
RESULT = Path("results/phase51/upstox_1f")
ROOT.mkdir(parents=True, exist_ok=True)
RESULT.mkdir(parents=True, exist_ok=True)

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2))

if not TOKEN:
    write_json(RESULT / "access_gate.json", {
        "status": "BLOCKED",
        "reason": "UPSTOX_ACCESS_TOKEN is not configured",
        "required_plan": "Upstox Plus for expired historical candle API",
        "expiries": EXPIRIES,
    })
    raise SystemExit(2)

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json",
})

contract_manifest = {"status": "RUNNING", "expiries": []}

def get_contracts(expiry):
    r = session.get(
        f"{BASE}/expired-instruments/option/contract",
        params={"instrument_key": "NSE_INDEX|Nifty 50", "expiry_date": expiry},
        timeout=60,
    )
    r.raise_for_status()
    p = r.json()
    if p.get("status") != "success":
        raise RuntimeError(f"contract API failure {expiry}: {p}")
    rows = p.get("data") or []
    if not rows:
        raise RuntimeError(f"no contracts returned for {expiry}")
    out = ROOT / f"contracts_{expiry}.json"
    write_json(out, rows)
    return rows

for expiry in EXPIRIES:
    rows = get_contracts(expiry)
    contract_manifest["expiries"].append({
        "expiry": expiry,
        "contracts": len(rows),
        "sha256": hashlib.sha256((ROOT / f"contracts_{expiry}.json").read_bytes()).hexdigest(),
        "bytes": (ROOT / f"contracts_{expiry}.json").stat().st_size,
        "ce": sum(x.get("instrument_type") == "CE" for x in rows),
        "pe": sum(x.get("instrument_type") == "PE" for x in rows),
        "min_strike": min(float(x["strike_price"]) for x in rows),
        "max_strike": max(float(x["strike_price"]) for x in rows),
    })

contract_manifest["status"] = "PASS"
write_json(RESULT / "contract_manifest.json", contract_manifest)

def candle_request(item, expiry):
    key = item.get("expired_instrument_key") or item.get("instrument_key")
    if not key:
        raise RuntimeError(f"missing expired instrument key: {item}")
    url_key = key.replace("|", "%7C")
    url = f"{BASE}/expired-instruments/historical-candle/{url_key}/1minute/{expiry}/{OOS_START}"
    for attempt in range(5):
        r = session.get(url, timeout=60)
        if r.status_code == 429 and attempt < 4:
            time.sleep(2 ** attempt)
            continue
        if r.status_code != 200:
            raise RuntimeError(f"candle failure {expiry} {key}: {r.status_code} {r.text[:500]}")
        p = r.json()
        if p.get("status") != "success":
            raise RuntimeError(f"candle API non-success {expiry} {key}: {p}")
        candles = (p.get("data") or {}).get("candles") or []
        return key, candles
    raise RuntimeError(f"unreachable candle retry state {expiry} {key}")

all_stats = {}
for expiry in EXPIRIES:
    rows = json.loads((ROOT / f"contracts_{expiry}.json").read_text())
    failures = []
    total = 0
    nonempty = 0
    outdir = ROOT / f"candles_{expiry}"
    outdir.mkdir(parents=True, exist_ok=True)

    def worker(item):
        key, candles = candle_request(item, expiry)
        safe = hashlib.sha1(key.encode()).hexdigest()
        path = outdir / f"{safe}.json.gz"
        with gzip.open(path, "wt", encoding="utf-8") as fh:
            json.dump({"expired_instrument_key": key, "candles": candles}, fh, separators=(",", ":"))
        return {"key": key, "rows": len(candles), "file": str(path)}

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futures = [ex.submit(worker, item) for item in rows]
        results = []
        for fut in concurrent.futures.as_completed(futures):
            try:
                res = fut.result()
                results.append(res)
                total += res["rows"]
                nonempty += int(res["rows"] > 0)
            except Exception as exc:
                failures.append(str(exc))

    manifest = {
        "expiry": expiry,
        "contracts": len(rows),
        "contracts_with_candles": nonempty,
        "candle_rows": total,
        "failures": failures[:100],
        "failure_count": len(failures),
    }
    write_json(RESULT / f"candle_manifest_{expiry}.json", manifest)
    all_stats[expiry] = manifest

status = "PASS_ACQUIRED" if all(v["failure_count"] == 0 and v["contracts_with_candles"] > 0 for v in all_stats.values()) else "FAIL_ACQUISITION"
write_json(RESULT / "acquisition_summary.json", {"status": status, "expiries": all_stats})
print(json.dumps({"status": status, "expiries": all_stats}, indent=2))

if status != "PASS_ACQUIRED":
    raise SystemExit(1)
