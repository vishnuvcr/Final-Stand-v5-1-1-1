import sys
from pathlib import Path
import zipfile
import csv
import json
import re
from datetime import datetime

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "data/zenodo_2017_2020")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "results/zenodo_2019_2020_manifest.json")
OUT.parent.mkdir(parents=True, exist_ok=True)

files = []
for p in ROOT.rglob("*"):
    if p.is_file():
        files.append(str(p.relative_to(ROOT)))

ext_counts = {}
for f in files:
    ext = Path(f).suffix.lower()
    ext_counts[ext] = ext_counts.get(ext, 0) + 1

expiry_like = []
for f in files:
    m = re.search(r"(20\d{2})[-_]?([A-Z][a-z]{2})[-_]?([0-3]?\d)", f)
    if m:
        expiry_like.append(f)

manifest = {
    "root": str(ROOT),
    "file_count": len(files),
    "extension_counts": ext_counts,
    "expiry_like_paths": expiry_like[:100],
    "validation_status": "STRUCTURE_ONLY",
    "notes": [
        "This validator intentionally does not merge the source into the primary backtest.",
        "2017-2018 data are excluded from the weekly-options strategy because NIFTY weekly options began in Feb-2019.",
        "A subsequent parser validation must establish exact schema, timestamps, expiry mapping, weekly/monthly separation, and OTM17 availability."
    ]
}

# If the source is still a zip rather than extracted, inspect its names.
zip_candidates = list(ROOT.glob("*.zip"))
if len(zip_candidates) == 1:
    z = zip_candidates[0]
    with zipfile.ZipFile(z) as zh:
        names = zh.namelist()
        manifest["zip_name"] = z.name
        manifest["zip_member_count"] = len(names)
        manifest["zip_extensions"] = sorted({Path(n).suffix.lower() for n in names})
        manifest["zip_sample_members"] = names[:100]

OUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps(manifest, indent=2))
