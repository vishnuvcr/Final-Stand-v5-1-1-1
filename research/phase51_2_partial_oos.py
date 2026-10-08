import os
import pandas as pd
import research.phase50b_tt03_otm_distance_replay as base

# Partial-OOS study: use only the currently complete frozen-source endpoint.
# This is deliberately NOT the full Phase-51 OOS validation.
base.START = pd.Timestamp("2026-04-21", tz=base.TZ)
base.END = pd.Timestamp("2026-07-21", tz=base.TZ)

if __name__ == "__main__":
    base.main()
