# Phase 51-1H Status

**State: PRIOR AUDIT DATA-BLOCKED; FRESHNESS RE-AUDIT REQUESTED (not yet accepted).**

## Frozen missing blocks
- 2026-07-28
- 2026-08-04

## Prior accepted audit
Actions run 37876719483.

## Prior findings (still authoritative until new raw-byte audit passes)
- 2026-07-28 file: 3,990,663 bytes; 320,359 rows; actual data ends 2026-07-02 15:30 IST.
- 2026-08-04 file: 58,248 bytes; 2,646 rows; actual data ends 2026-07-02 15:29 IST.
- Both contained the requested expiry value but not the requested trading session.
- Zero duplicate contract-minute keys after transparent schema mapping.
- No OOS P&L was calculated.

## Freshness signal
The current public Hugging Face index displays a newer visible commit `51ca58c` with an `options/NIFTY/2026-08-04.parquet` path. This may reflect a dataset update but does not itself prove that the file contains target-date trading observations. A fresh Actions audit was requested by updating `trigger/phase51_1H.start` to `rerun-4 public dataset freshness audit 2026-10-09`.

## Acceptance requirements
The new run must verify exact downloaded bytes, schema mapping, valid timestamps/expiry values, target trading date present for both files, zero duplicate contract-minute keys, and full target-session coverage before the data gate can change. Until then, the phase remains data-blocked and no P&L is authorized.

## External source context
StockMock and StockMojo remain research/oracle context only; no reproducible raw archive has been accepted from them.
