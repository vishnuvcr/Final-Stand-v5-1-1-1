# Phase 101 Error and Limitation Log

Append entries; never overwrite earlier failures.

## Initialization — 2026-10-10

- **E101-001 — Repo fetch attempt used an ambiguous multi-path request.** The first parallel fetch returned 404 because at least one requested path/ref did not exist. Resolved by querying each file individually and verifying the Phase 100 branch and repository identity. No research data or prior result was changed.
- **L101-001 — Exact PDF replication is not uniformly identifiable.** U02 omits complete reproducible feature/model details; U05 has a dimensionally ambiguous expected-price equation and no numeric liquidity threshold; source-period option records are unavailable in the current pinned sample. These are to be preserved as limitations, not silently guessed away.
- **L101-002 — Existing option archive limitations.** The accepted source revision is CC-BY-NC-4.0, has OHLCV/OI-style historical bars rather than bid/ask/depth, and does not cover the original U14 (2008–2018) or U05 historical period. Raw files must not be committed.
- **L101-003 — Costs.** Brokerage scenarios and date-effective statutory/exchange fees are modelling assumptions supported by public rate schedules; tick/percentage slippage cannot reconstruct queue position, market impact or actual Paytm Money contract notes.

## Automated run failure — 2026-10-10T18:16:12Z
- Workflow run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38074995935
- Commit: 309c00d0b5534d9da1414c4a370315240df8c061
- Job failed before the output contract was validated. Numerical outputs from this run are not accepted.
- Check results/phase101_pdf_strategy_tests/phase101_runtime_error.json if present, then fix root cause without relaxing frozen strategy rules.

- **E101-002 — Parquet engine runtime import failed.** Workflow run [38074995935](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38074995935) installed a PyArrow 26.0.0 wheel successfully, but pandas could not load it during the first Parquet read. This occurred before any U02/U05 backtest and no numerical strategy result was accepted. Corrective action: pin PyArrow to 18.1.0 (compatible with the registered NumPy 1.26 range) and add an explicit pyarrow.parquet import gate before data acquisition. Root-cause verification remains pending the next workflow.
