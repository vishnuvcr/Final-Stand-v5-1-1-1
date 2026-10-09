import csv
import importlib
from pathlib import Path
import json, traceback
import phase51_3_primary_source_adapter as primary

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
    # Replace only the inherited Phase-43 data/expiry dependencies. The
    # strategy code, execution semantics, cost model and parameters stay frozen.
    primary._init()
    m.load_parquet = primary.load_parquet
    if hasattr(m, "get_expiries"):
        m.get_expiries = primary.expiries
    if hasattr(m, "expiry_list"):
        m.expiry_list = primary.expiries
    if hasattr(m, "exps"):
        m.exps = primary.expiries
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

    # Coverage and row-level data errors are candidate outcomes, not wrapper
    # exceptions. Record them explicitly so one failed candidate does not hide
    # the remaining diagnostics.
    error_file = out / "data_errors.csv"
    if error_file.exists():
        with error_file.open("r", newline="", encoding="utf-8") as fh:
            data_error_count = max(0, sum(1 for row in csv.reader(fh) if row) - 1)
    else:
        data_error_count = None
    coverage_rate = float(d.get("coverage_rate", 0.0) or 0.0)
    coverage_status = "PASS" if coverage_rate >= 0.95 else "FAIL_COVERAGE"
    data_error_status = (
        "PASS" if data_error_count == 0 else
        "FAIL_DATA_ERRORS" if data_error_count is not None else
        "FAIL_MISSING_DATA_ERROR_AUDIT"
    )
    d["phase51_3_gate"] = {
        "coverage_threshold": 0.95,
        "coverage_rate": coverage_rate,
        "coverage_status": coverage_status,
        "data_error_count": data_error_count,
        "data_error_status": data_error_status,
        "replay_quality_gate": "PASS" if coverage_status == "PASS" and data_error_status == "PASS" else "FAIL",
        "final_full_window_validation": False,
    }
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
    report = {
        "window": [START, END],
        "partial_oos_only": True,
        "expected_candidates": [name for name, _ in CANDIDATES],
        "source_manifest": primary.source_manifest(),
        "results": results,
        "errors": errors,
    }
    (OUTROOT/"sweep_summary.json").write_text(json.dumps(report, indent=2))
    # Print all captured tracebacks into Actions logs. The workflow also uploads
    # whatever diagnostics exist even when this command returns non-zero.
    print(json.dumps(report, indent=2), flush=True)
    if errors:
        raise SystemExit(f"{len(errors)} candidate engine(s) failed; traceback(s) are above and stored in sweep_summary.json")

if __name__ == "__main__":
    main()
