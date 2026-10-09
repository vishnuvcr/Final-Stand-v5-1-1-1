# Phase 51-1J Free Source Recovery — Addendum

## Research question
Can a publicly accessible Hugging Face dataset supply trustworthy one-minute NIFTY option bars for 2026-07-28 and 2026-08-04 without purchasing data?

## Candidate discovery
- Dataset: https://huggingface.co/datasets/thetrademarkk/india-index-options-1m
- Public file history lists options/NIFTY/2026-07-28.parquet and options/NIFTY/2026-08-04.parquet.
- Dataset card license: CC BY-NC 4.0.
- Dataset card warns option coverage is partial; illiquid/far strikes may be absent.
- File presence is discovery evidence only, not accepted strategy data.
- The codepyx23 mirror says it duplicates the same source and is not independent corroboration.

## Finite audit steps
1. Download only the two exact Parquet files via the existing HF_TOKEN secret if needed; cache in Actions.
2. Record SHA-256, bytes, schema, timestamp bounds, target-date minute counts, sides, strikes, expiries, duplicates, nulls and invalid prices.
3. Compare the exact required strategy legs and expiry against the frozen Phase-51 rules.
4. Compare overlapping dates against the already audited primary RISSIN/Upstox file where available; record discrepancies without silent source substitution.
5. Keep raw Parquet out of the public repository. Publish only hashes, schemas, aggregate coverage and reports, subject to the dataset licence.
6. If accepted, rerun the frozen Phase-51 replay with existing cost/slippage rules. Do not tune during source recovery.

## Acceptance gates
Both sessions must have real timestamps and minute bars, verified timezone/session, required option contracts, zero unexplained duplicate contract-minute keys, documented provenance/licence, at least 95% strategy-opportunity coverage and zero data errors. No synthetic bars or forward fills.

## Stop condition
Stop after both target files and overlap checks. If inadequate, record the specific failure and move to the next bounded free-source candidate. Phase 51 stays blocked until accepted data is available.
