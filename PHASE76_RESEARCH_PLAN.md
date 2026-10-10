# Phase 76 — Fixed-contract historical source audit
Date opened: 2026-10-10
Status: PLAN FROZEN.

## Research question
Can the already-listed public Hugging Face dataset `thetrademarkk/india-index-options-1m` provide the two missing NIFTY expiry-date files (2026-07-28 and 2026-08-04) with explicit expiry, strike and option-type fields, allowing the Phase 51-1 legs to be mapped without relying on DhanHQ's relative expiry codes?

## Why this source
The dataset card documents `options/NIFTY/{EXPIRY}.parquet` and fields including timestamp, strike, option_type and expiry. Its published license is CC-BY-NC-4.0; use only for non-commercial research consistent with that license, cite attribution, and do not redistribute raw files. The files must be checked, not assumed present or complete.

## Frozen scope
- Exact files for expiry dates 2026-07-28 and 2026-08-04 only.
- Query repository metadata first; download only those exact files if present.
- Temporary runner storage only; no raw rows/prices or downloaded files committed to Git.
- Persist aggregate counts, schema, target expiry value, strike/side coverage and regular-session timestamp coverage only.
- No P&L calculation in this phase.

## Method
1. Enumerate the dataset repo file manifest and identify exact expiry-file paths.
2. If absent, record a bounded NO-GO and stop; do not download the full dataset.
3. If present, download only the two exact files using `HF_TOKEN` when available, and inspect schema/metadata.
4. Validate that rows explicitly identify the requested expiry date and include timestamp, strike, option_type, OHLC and any available volume/OI fields.
5. Count unique contracts and regular-session minute timestamps per expiry/strike/side. Do not interpolate missing bars.
6. Compare against actual frozen strategy leg requirements only after those are enumerated from canonical records.
7. Check license and retention limits; do not persist raw price data in the public repository.

## Decision gates
- PASS for source identity only if the exact files exist and explicit expiry/strike/side values validate.
- PASS for each leg only if that exact strike/side has sufficient observed timestamps for the frozen entry/exit window.
- Missing file or incomplete strike data means BLOCKED for that leg; do not synthesize.
- Any later replay must include Paytm Money charges and conservative slippage/spread; OHLC does not prove executable fills.

## Deliverables
- `PHASE76_STATUS.md`, `PHASE76_ERROR_LOG.md`
- `results/phase76_hf_fixed_contracts/summary.json` and `report.md`
- Manual GitHub Actions trigger and bounded automated metadata/data audit.
- README checkpoint updated after the result.
