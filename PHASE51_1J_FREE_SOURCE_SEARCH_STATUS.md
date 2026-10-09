# Phase 51-1J Free-source search status — 2026-10-09

**Status: NO ACCEPTED FREE SOURCE FOUND; Phase 51 remains DATA-BLOCKED.**

- Dhan expired-options endpoint exists, but its Data API costs ₹499 + GST/month; no subscription or purchase made.
- ICICI Breeze pipeline found on GitHub is code requiring the user's own API login, not a free raw archive, and published coverage reaches May 2026 only.
- thetrademarkk public HF files named for 2026-07-28 and 2026-08-04 were audited in run [37916601582](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37916601582): both stop at 2026-07-02, with zero target-session rows.
- codepyx23 is a duplicate/mirror; artist-23 coverage ends in 2025; RISSIN primary object ends 2026-07-21.
- Official NSE daily derivatives reports can cross-check settlement/EOD values but do not substitute for minute-level option candles.

The frozen OOS interval remains 2026-04-21 through 2026-08-04. Missing option blocks: 2026-07-28 and 2026-08-04. No full-window P&L, parameter tuning or strategy promotion is authorized until the data gate passes.

Sources:
- [Dhan expired-options API FAQ](https://dhan.co/support/platforms/dhanhq-api/do-dhan-provides-expired-options-data-via-the-api-s/)
- [Dhan Data API pricing](https://dhan.co/support/platforms/dhanhq-api/how-does-the-dhanhq-data-api-subscription-work/)
- [ICICI Breeze data pipeline](https://github.com/JATINDHURVE/Indian-market-data-pipeline)
- [RISSIN primary dataset](https://huggingface.co/datasets/rissin/nse-options-intraday)
- [NSE derivatives reports](https://www.nseindia.com/all-reports-derivatives)
