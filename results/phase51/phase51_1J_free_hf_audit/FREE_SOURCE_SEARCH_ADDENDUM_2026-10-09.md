# Phase 51-1J — Free-source search addendum (2026-10-09)

## Question
Can a genuinely free, independent source provide complete NIFTY option minute bars for 2026-07-28 and 2026-08-04 without buying a data pack or subscribing to a paid Data API?

## Findings
1. **DhanHQ expired-options API — not free.** Official Dhan support says expired option data is provided through its dedicated endpoint, but Dhan Data APIs cost ₹499 + applicable taxes monthly and include expired options. The project previously found no Dhan credentials configured. No subscription was purchased or enabled. Sources: https://dhan.co/support/platforms/dhanhq-api/do-dhan-provides-expired-options-data-via-the-api-s/ ; https://dhan.co/support/platforms/dhanhq-api/how-does-the-dhanhq-data-api-subscription-work/ ; https://dhanhq.co/docs/v2/releases/
2. **Independent GitHub code pipeline using ICICI Breeze — not an independent free dataset.** https://github.com/JATINDHURVE/Indian-market-data-pipeline explains that it downloads data using the user's own Breeze API login; the repository contains code/manifests, not the underlying market data. It reports options coverage through May 2026, so it does not establish coverage of either target session.
3. **Kaggle/Hugging Face public datasets found — not adequate for the target sessions.** The previous audit of the public future-expiry filenames from thetrademarkk dataset showed both files ended on 2026-07-02 and contained zero rows on their named target sessions. The codepyx23 dataset is a mirror/duplicate and is not independent corroboration. The artist-23 dataset's described coverage ends in 2025, so it cannot cover the target dates.
4. **RISSIN/Hugging Face primary public dataset — already audited; insufficient.** Its NIFTY intraday object ends at expiry 2026-07-21. Daily NSE bhavcopy data can support EOD checks but cannot replace minute-level option replay.
5. **DhanHQ official pricing.** Trading API is free, but Data API is separately priced at ₹499 + GST/month; do not confuse free order APIs with free historical data.

## Decision
No verified free, independent source has been found that establishes full, timestamped, contract-complete minute data for both 2026-07-28 and 2026-08-04. Keep Phase 51 full-window OOS **DATA-BLOCKED**. Do not shorten the frozen OOS window, synthesize/forward-fill bars, use EOD data as intraday data, or calculate full-window P&L from incomplete data.

## Bounded next step
Finish this free-source sweep by checking any additional public archive only if it is genuinely independent and exposes downloadable raw timestamps for the exact target dates. Otherwise close the free-source recovery subphase as **NO FREE SOURCE FOUND**, preserve the partial-OOS diagnostics, and wait for user-provided authorized data or credentials. No purchase and no request for credentials are made here.

## Error and evidence discipline
The prior stale-file issue is logged in `PHASE51_1J_ERROR_LOG.md` as T51-1J-006. Dataset filenames and expiry metadata must never be treated as proof of timestamp coverage.
