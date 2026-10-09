import importlib
from pathlib import Path
import json, traceback

START = "2026-04-21"
END = "2026-07-21"
OUTROOT = Path("results/phase51/available_oos")

CANDIDATES = [
    ("TT02", "phase50b_tt02_calendar_replay_v3"),
    ("TT04", "phase50b_tt04_premium_match_replay"),
    ("TT05", "phase50b_tt05_short_straddle_replay"),
]

def run_one(name, modname):
    m = importlib.import_module(modname)
    m.START = m.pd.Timestamp(START, tz=m.TZ)
    m.END = m.pd.Timestamp(END, tz=m.TZ)
    out = OUTROOT / name.lower()
    out.mkdir(parents=True, exist_ok=True)
    m.OUT = out
    # The imported frozen engine owns its own caches; this wrapper changes only
    # evaluation bounds and artifact location.
    m.main()
    summary_path = out / "summary.json"
    if not summary_path.exists():
        raise RuntimeError(f"{name}: missing summary.json")
    d = json.loads(summary_path.read_text())
    d["phase51_3_window"] = [START, END]
    d["partial_oos_only"] = True
    summary_path.write_text(json.dumps(d, indent=2))
    return d

def main():
    results = {}
    errors = {}
    for name, mod in CANDIDATES:
        try:
            results[name] = run_one(name, mod)
        except Exception:
            errors[name] = traceback.format_exc()
    OUTROOT.mkdir(parents=True, exist_ok=True)
    (OUTROOT/"sweep_summary.json").write_text(json.dumps({"window":[START,END],"results":results,"errors":errors}, indent=2))
    if errors:
        raise SystemExit("Candidate engine failures occurred; see sweep_summary.json")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
