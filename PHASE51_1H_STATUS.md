# Phase 51-1H Status

**CLOSED — DATA-BLOCKED / PUBLIC HF SOURCE REJECTED; FRESHNESS RE-AUDIT COMPLETED.**

## Frozen missing blocks
- 2026-07-28
- 2026-08-04

## Latest accepted byte audit
[Actions run 37912433753](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37912433753) re-downloaded both files after a current public index showed a newer visible commit. The downloaded hashes and sizes were unchanged from the prior audit.

| Target expiry file | Bytes | Rows | Actual timestamp range | Target trading date present? |
|---|---:|---:|---|---|
| 2026-07-28 | 3,990,663 | 320,359 | 2026-06-15 09:15 to 2026-07-02 15:30 IST | No |
| 2026-08-04 | 58,248 | 2,646 | 2026-06-24 10:08 to 2026-07-02 15:29 IST | No |

- 2026-07-28 SHA-256: `f9c3a6d1e4498274644ccbfeb8aeb3d545fc2ce1a12b908f450360a643e40d17`
- 2026-08-04 SHA-256: `8de2f08cef1456c448c4fc4be0d9d586a1b26af30bf67990171385361af92f9c`
- Both schema mappings passed; bad timestamp/expiry counts and duplicate contract-minute keys were zero.
- Both files contain the target expiry value, but neither contains the target trade date. No P&L was calculated.

## Decision
**DATA-BLOCKED remains in force.** The current public HF index/file listing did not translate into new target-session observations. The full Phase-51 OOS window must not be shortened and missing prices must not be synthesized or forward-filled.

## Next viable routes
1. Configure an authorized Upstox Plus, Dhan or ICICI Breeze API credential and rerun the preregistered raw-data recovery workflow; or
2. Obtain an authorized archive containing both target sessions from a vendor such as [OptionsData.shop NIFTY 1-minute full-chain archive](https://optionsdata.shop/data/nifty-options-historical-data), then validate exact raw bytes, timestamps, contract coverage and provenance before use.

No paid data has been purchased and no credentials were added. StockMock/StockMojo remain oracle/context platforms only, not accepted raw data.
