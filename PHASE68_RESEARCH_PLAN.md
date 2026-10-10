# Phase 68 Research Plan — Fresh HF Target-Date Byte Audit

## Research question
Have the two previously missing NIFTY option files on the Hugging Face dataset changed since the last accepted audit, and do their actual bytes contain the required 2026-07-28 and 2026-08-04 session rows?

## Rationale / new lead
Current public dataset listings still show entries for both files. The prior Phase 51-1H/1J audits reported stale bytes ending 2026-07-02, so filenames or catalog entries are not enough. This phase performs one fresh byte-level revalidation using the repository's HF_TOKEN secret. It does not repeat metadata-only searches.

## Frozen scope
- Source: `thetrademarkk/india-index-options-1m`, path `options/NIFTY/{2026-07-28,2026-08-04}.parquet`.
- Do not change the frozen Phase 51 OOS window, candidate definitions, entry/exit rules, costs, or holdout.
- Do not treat file names, expiry metadata, nearby bars, or row existence as proof of target-session coverage.
- Never print or persist HF_TOKEN, signed URLs, raw rows, or raw data artifacts.
- Download to ephemeral runner storage only. Publish only aggregate schema, row counts, timestamps, contract coverage, SHA-256 and byte sizes.
- No paid data purchase. Do not use any 2026 data outside these two predeclared OOS gap sessions for strategy selection/tuning.
- Source is CC-BY-NC-4.0 per its dataset card; this audit does not grant rights to redistribute underlying market data.

## Steps
1. Read current repository state and pinned source identity.
2. Fetch both target Parquet objects using HF_TOKEN if available; record source revision, byte size and SHA-256.
3. Validate Parquet readability and inspect schema without printing raw rows.
4. Count rows whose actual timestamps fall on each requested IST session; report min/max timestamp, unique timestamps, expiry/strike/CE-PE counts, duplicate contract-minute keys, null OHLC/OI counts where schema permits.
5. Independently check target session coverage and contract-key completeness. Preserve missing OI versus true zero.
6. Publish aggregate-only JSON/Markdown. Raw data remains ephemeral.
7. Decision: PASS only if both exact sessions have nonzero rows and timestamp/schema/contract keys are plausible. Even a PASS only unlocks the existing frozen Phase 51 validation; it does not prove bid/ask/depth or profitability.

## Statistical analysis
None in this phase. This is a bounded source-integrity audit. No P&L, ranking, hypothesis test, strategy change, or promotion.

## Finite stopping rule
One fresh byte-level audit. If either file is unavailable, unchanged/stale, malformed, or lacks target-session rows, close as BLOCKED and do not repeat this audit without a new source revision or authorization. If both pass, proceed to the already-defined frozen exact-coverage gate.

## Deliverables
- `results/phase68_hf_target_date_audit/summary.json`
- `results/phase68_hf_target_date_audit/report.md`
- `PHASE68_STATUS.md`, `PHASE68_RESEARCH_LOG.md`, `PHASE68_ERROR_LOG.md`, `PHASE68_CHAT_LOG.md`

## Safety and costs
No trades are simulated. If later replay is valid, apply Paytm Money brokerage, statutory charges, adverse tick/slippage, and registered friction stress scenarios; OHLC-only results must not be called executable quote-level fills.
