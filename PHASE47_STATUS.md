# Phase 47 Status — VIX Source-Strategy Numerical Backtest

**CLOSED — DATA-SOURCE FEASIBILITY / NO PROMOTION**

## Accepted conclusion

Phase 47 was designed to numerically test three YouTube-derived structures while retaining the full VIX panel.

The self-audit process correctly prevented invalid evidence from entering the research record.

- S1 Double Calendar Straddle: not numerically feasible on the current Phase-45/46 cached option dataset for most months because the next-month contract has no observed entry-time quotes on the current-month entry date.
- S2 Monthly Wide-Range Hedge: same multi-expiry data limitation. The focused diagnostic found only isolated feasible months; the dataset cannot support a complete historical evaluation of the strategy/adjustment mechanism.
- S3 Covered Call 2.0 proxy: only 20 accepted trade rows were generated. It is explicitly a futures-replacement proxy and does not meet the project's minimum evidence threshold.

## Rejected numerical attempts

- Run 37520391271: numerical rows=14, all S3; artifact self-audit failed; NON-EVIDENCE.
- Run 37521447694: numerical rows=20 (S1/S3), artifact self-audit failed because some VIX states had no observations; NON-EVIDENCE.
- Focused diagnostics themselves passed after corrections and established the cross-expiry quote-availability limitation.

## Self-audit corrections recorded

Timezone normalization, multi-window cache keys, variant accounting, deterministic statistical seeds, per-expiry ATM strike handling, stratified monthly diagnostics, and diagnostic workflow schema were all audited and corrected before accepting any numerical evidence.

## Research conclusion

The limiting factor is data structure, not necessarily strategy quality. The currently cached thetrademarkk/india-index-options-1m source is adequate for same-expiry strategies but is not adequate for systematic historical calendar/next-expiry strategy research.

No source-derived strategy is promoted.

## Next phase

A separate data-bridge phase will use an independent historical NIFTY intraday source containing multiple expiries on the same trade date. The first candidate is the public Hugging Face rissin/nse-options-intraday dataset (intraday NIFTY coverage from Oct 2024 onward). This will be treated as a supplemental 2024Q4/2025/2026 study with stricter exploratory interpretation and will not rewrite the earlier 2021–2025 evidence.