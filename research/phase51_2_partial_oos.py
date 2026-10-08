import os
import sys
from pathlib import Path

import pandas as pd

# Executed as `python research/phase51_2_partial_oos.py`, Python puts the
# research/ directory on sys.path but not the repository root. Add both
# explicitly so the inherited Phase-50B engine can be imported using its
# existing absolute-import convention without changing that frozen engine.
REPO_ROOT = Path(__file__).resolve().parents[1]
RESEARCH_ROOT = REPO_ROOT / "research"
for _p in (str(REPO_ROOT), str(RESEARCH_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import research.phase50b_tt03_otm_distance_replay as base

# Partial-OOS study: use only the currently complete frozen-source endpoint.
# This is deliberately NOT the full Phase-51 OOS validation.
base.START = pd.Timestamp("2026-04-21", tz=base.TZ)
base.END = pd.Timestamp("2026-07-21", tz=base.TZ)

# The inherited engine's expiry_dates() reads the Phase-43 trade matrix, which
# predates this fresh OOS interval. Phase-51-2 must enumerate expiry files from
# the frozen option source itself; this changes only opportunity discovery, not
# the frozen trade rules or candidate parameters.
base.expiry_dates = base.list_expiry_files

# Publish into the Phase-51-2 namespace rather than the inherited Phase-50B
# result tree. This prevents cross-phase artifact collisions and makes the
# workflow validation path deterministic.
base.OUT = Path("results/phase51/partial_oos") / (
    "d" + os.environ.get("TT03_DISTANCE", "300")
)
base.OUT.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    base.main()
