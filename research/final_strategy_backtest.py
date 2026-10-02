import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from research.payoff_boundary_stop_research import (
    load_trade_ledgers,
    build_boundary_metadata,
    load_spot,
    load_candidate_paths,
    phase19_fixed_mfe50_stop,
    make_rows,
    summarize,
)

OUT = Path(os.getenv("OUT_DIR", "results/final_strategy"))
OUT.mkdir(parents=True, exist_ok=True)


def main():
    base = load_trade_ledgers()
    meta = build_boundary_metadata(base)
    spot = load_spot()
    paths, path_errors = load_candidate_paths(meta, spot)

    final = make_rows(
        meta,
        paths,
        lambda entry, path: phase19_fixed_mfe50_stop(entry, path),
        "final_strategy",
    )

    summary = summarize(final)

    final.to_csv(OUT / "final_trade_level.csv", index=False)
    pd.DataFrame([summary]).to_csv(OUT / "final_summary.csv", index=False)
    if path_errors:
        pd.DataFrame(path_errors).to_csv(OUT / "data_alignment_errors.csv", index=False)

    report = f"""# Final Strategy Backtest Result

The final historical strategy applies the corrected dynamic-n entry rules plus:

1. target exit;
2. 13:30 IST expiry-day stop when combined MTM < 0 and running MFE < 0.50×original target;
3. 15:29 expiry fallback;
4. no payoff-boundary stop.

## Result

{summary}

This wrapper reuses the audited Phase-20 minute-level reconstruction and the same execution/cost model.
"""
    (OUT / "FINAL_STRATEGY_RESULT.md").write_text(report, encoding="utf-8")

    print(report)


if __name__ == "__main__":
    main()
