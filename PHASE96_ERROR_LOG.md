# Phase 96 Error / Limitation Log

## Known limitations at phase start
- Phase 95 latest reconciliation workflow was still running at last check; do not assume generated claim ledger/status updates exist until run completion is verified.
- Daily Yahoo Finance index data are suitable for price-signal screening but are not historical listed option contract quotes and do not support executable options P&L.
- Some paper-specific MA windows, seasonality definitions, option strikes, expiry conventions, stop-loss triggers, exits and fills may not be uniquely specified. Those methods must be labelled partial, not identifiable or data-blocked.
- Precise historical Paytm Money fee schedules and bid/ask/slippage may be unavailable for the entire sample; do not fabricate them.

## Runtime errors
- None recorded yet; workflow/runtime errors must be appended with date, step, concise cause, fix and rerun outcome.
