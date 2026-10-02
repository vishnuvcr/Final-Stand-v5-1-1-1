import sys, json, re, zipfile, csv
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "data/zenodo_2017_2020")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "results/zenodo_2019_2020_manifest.json")
OUT.parent.mkdir(parents=True, exist_ok=True)

manifest = {
    "root": str(ROOT),
    "outer_files": [],
    "nested_archives": [],
    "sample_files": [],
    "validation_status": "SCHEMA_DISCOVERY"
}

for p in ROOT.rglob("*"):
    if p.is_file():
        manifest["outer_files"].append(str(p.relative_to(ROOT)))

for p in ROOT.rglob("*.zip"):
    with zipfile.ZipFile(p) as z:
        names = z.namelist()
        info = {
            "archive": str(p.relative_to(ROOT)),
            "member_count": len(names),
            "sample_members": names[:50],
            "extensions": sorted({Path(n).suffix.lower() for n in names if "." in Path(n).name})
        }
        manifest["nested_archives"].append(info)

        # Inspect a few likely option text/spreadsheet-like members.
        candidates = [n for n in names if Path(n).suffix.lower() in {".csv",".txt",".xlsx",".xls"}]
        for n in candidates[:10]:
            item = {"archive": str(p.relative_to(ROOT)), "member": n}
            if n.lower().endswith(".csv") or n.lower().endswith(".txt"):
                try:
                    raw = z.read(n)
                    item["size_bytes"] = len(raw)
                    lines = raw.decode("utf-8", errors="replace").splitlines()
                    item["first_lines"] = lines[:5]
                except Exception as e:
                    item["read_error"] = repr(e)
            manifest["sample_files"].append(item)

manifest["validation_status"] = "NESTED_ARCHIVE_SCHEMA_DISCOVERED"
OUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps(manifest, indent=2))
