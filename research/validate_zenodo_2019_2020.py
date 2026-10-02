import sys, json, zipfile, io
from pathlib import Path

ROOT = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.parent.mkdir(parents=True, exist_ok=True)

manifest={"root":str(ROOT),"levels":[],"samples":[],"status":"DEEP_SCHEMA_DISCOVERY"}

def walk_zip(zdata, label, depth=0, max_depth=3):
    if depth>max_depth: return
    with zipfile.ZipFile(io.BytesIO(zdata)) as z:
        names=z.namelist()
        manifest["levels"].append({"label":label,"depth":depth,"member_count":len(names),"sample_members":names[:80]})
        for n in names:
            if n.endswith("/"): continue
            raw=z.read(n)
            low=n.lower()
            if low.endswith(".zip") and depth<max_depth:
                try:
                    walk_zip(raw, f"{label}!{n}", depth+1, max_depth)
                except Exception as e:
                    manifest["samples"].append({"label":label,"member":n,"zip_error":repr(e)})
            elif depth>=1 and len(manifest["samples"])<8:
                item={"label":label,"member":n,"size":len(raw)}
                if low.endswith((".csv",".txt")):
                    item["text_head"]=raw.decode("utf-8",errors="replace").splitlines()[:12]
                else:
                    item["signature"]=raw[:16].hex()
                manifest["samples"].append(item)

for p in ROOT.rglob("*.zip"):
    try:
        walk_zip(p.read_bytes(), str(p.relative_to(ROOT)), 0, 3)
    except Exception as e:
        manifest["samples"].append({"archive":str(p),"error":repr(e)})

OUT.write_text(json.dumps(manifest,indent=2),encoding="utf-8")
print(json.dumps(manifest,indent=2))
