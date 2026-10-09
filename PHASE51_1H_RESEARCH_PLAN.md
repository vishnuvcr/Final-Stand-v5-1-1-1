# Phase 51-1H — Current Public HF Byte Validation

## Purpose
Re-audit the current live bytes for the two unresolved Phase-51 option expiries before considering any authorized commercial source.

## Frozen targets
- 2026-07-28
- 2026-08-04

## Scientific rule
This phase may inspect source bytes, schema, timestamps, duplicates and provenance only. It must not inspect strategy P&L, tune parameters, shorten the OOS window, or select a source based on expected profitability.

## Gate
A target file passes only if:
1. It downloads successfully from the current public repository.
2. SHA-256 and byte size are recorded.
3. Required option OHLCV/OI schema is present.
4. Datetime and expiry parse without errors.
5. Contract-minute keys are unique.
6. The target expiry is actually represented.
7. The file's observed trading-date range contains the target date.
8. A subsequent common-expiry equivalence gate against the frozen RISSIN source passes before strategy replay.

## Stop rule
If the current public bytes fail the file-integrity gate, retain DATA-BLOCKED status and do not substitute StockMock/StockMojo simulator results for raw evidence.

## External-source audit context
StockMock documents 1-minute OHLC option backtesting and slippage/brokerage/tax simulation, while StockMojo advertises historical/expired option charts and a minute-level simulator. These are useful independent research/oracle sources, but their web tools do not provide a reproducible raw Parquet archive for ingestion into the Phase-51 evidence pipeline. Therefore they cannot replace a raw source in this gate.
