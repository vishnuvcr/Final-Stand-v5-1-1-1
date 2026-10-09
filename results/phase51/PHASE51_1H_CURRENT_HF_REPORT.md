# Phase 51-1H — Current Public HF Byte Validation Report

## Decision

**CLOSED — DATA-BLOCKED / CURRENT PUBLIC HF FILES REJECTED FOR FROZEN OOS**

A final live-byte audit was executed against the current public Hugging Face repository for both unresolved Phase-51 expiry blocks.

No strategy P&L was calculated.

## Results

| Target | SHA-256 | Size | Rows | Schema | Observed datetime range | Target trade date present | Decision |
|---|---|---:|---:|---|---|---|---|
| 2026-07-28 | f9c3a6d1e4498274644ccbfeb8aeb3d545fc2ce1a12b908f450360a643e40d17 | 3,990,663 B | 320,359 | Canonically mappable | 2026-06-15 09:15 to 2026-07-02 15:30 IST | **No** | REJECT |
| 2026-08-04 | 8de2f08cef1456c448c4fc4be0d9d586a1b26af30bf67990171385361af92f9c | 58,248 B | 2,646 | Canonically mappable | 2026-06-24 10:08 to 2026-07-02 15:29 IST | **No** | REJECT |

Both files contain the requested expiry value, but neither contains the actual target trading date. This is decisive: filename/expiry metadata alone cannot establish the missing OOS block.

## Schema

The current source uses:

- timestamp
- open/high/low/close
- volume
- open_interest
- trading_day
- symbol
- strike
- option_type
- expiry

The following transparent validation mapping was applied without changing raw values:

- timestamp → datetime
- expiry → expiry_date
- strike → strike_price
- option_type → right

After mapping, required fields were present and there were zero duplicate contract-minute keys in the audited files.

This is a schema normalization, not synthetic data generation.

## Scientific consequence

The current public source still cannot supply the frozen 2026-07-28 and 2026-08-04 trading sessions.

Therefore:

- no source equivalence test against the frozen RISSIN source was started;
- no replay-entry/exit coverage test was started;
- no TT-03 P&L was calculated;
- no cost/slippage result was calculated;
- the OOS window was not shortened;
- no source was selected based on strategy performance.

## External platform audit

StockMock's public documentation states that its backtesting service uses 1-minute OHLC data and can model slippage, brokerage fees and taxes. StockMojo publicly advertises historical/expired option-chain replay and a minute-level option simulator.

These platforms are useful independent research/oracle sources, but no reproducible raw Parquet archive suitable for ingestion into the repository's evidence pipeline was established from their public interfaces. They therefore cannot replace a source-faithful raw-data gate.

## Reproducibility

Accepted audit workflow: **Actions run 37876719483**.

Audit artifact: **11591824558**.

The audit is source-only and contains no strategy-performance output.

## Conclusion

The live public Hugging Face repository was rechecked rather than relying on the previous rejection. The files have valid Parquet structure and canonically mappable fields, but their actual bytes terminate on **2026-07-02**, well before either frozen missing expiry session.

**Phase 51 remains DATA-BLOCKED.**

The next permitted route is the already-preregistered authorized-data recovery matrix, beginning with Upstox expired-instrument access if an authorized credential is available, followed by the other registered commercial/API routes. No P&L is permitted until the raw-data gate passes.
