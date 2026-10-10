# Phase 96 Error / Limitation Log

## Known limitations at phase start
- Phase 95 latest reconciliation workflow was still running at last check; do not assume generated claim ledger/status updates exist until run completion is verified.
- Daily Yahoo Finance index data are suitable for price-signal screening but are not historical listed option contract quotes and do not support executable options P&L.
- Some paper-specific MA windows, seasonality definitions, option strikes, expiry conventions, stop-loss triggers, exits and fills may not be uniquely specified. Those methods must be labelled partial, not identifiable or data-blocked.
- Precise historical Paytm Money fee schedules and bid/ask/slippage may be unavailable for the entire sample; do not fabricate them.

## Runtime errors
- None recorded yet; workflow/runtime errors must be appended with date, step, concise cause, fix and rerun outcome.

- 2026-10-10, CI run 38072517459: pytest collection failed because a source edit inserted literal `\\n` characters into the test-window equity reset, causing SyntaxError. The subsequent commit step also failed because `results/phase96/` did not yet exist. Fixed by restoring real newlines and creating the results directory before staging. Superseded run output is not accepted.
- 2026-10-10, CI runs 38072553416–38072564869: retries were still based on the broken syntax while fixes were being committed; superseded and not accepted. Latest source fix is commit `5aec17399b7ef34ae88b57b5a4e7daf9f679dd79`; a fresh workflow run is expected.
