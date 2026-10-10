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


## Run reconciliation — 2026-10-10T18:23:56Z
- Workflow 38075221554 completed aggregate validation. No runner exception was raised; inspect report and model status CSV for explicit data/model blockers.


## 2026-10-10 — Review of first successful output set (not accepted)

- **E101-003 — U05 temporal leakage.** Runtime report `results/phase101_pdf_strategy_tests/PHASE101_REPORT.md` showed months where `thursday_date` preceded `wednesday_date` (e.g., July 2021 forecast Wednesday 7 July but entry Thursday 1 July). These trades used a future forecast. Corrected `_u05_entry_dates()` now selects the first calendar Thursday strictly after the first forecast Wednesday; deterministic tests added for July 2021 and June 2023. All earlier U05 numeric results are invalidated pending rerun.
- **E101-004 — U02 capital was reused independently for each trade.** The first trade simulator sized every daily position from the initial ₹1 lakh and summed losses across hundreds of trades, which is not a viable single-account path. Corrected the simulator to track a separate sequential ₹1 lakh equity path per model, cap premium deployment at 95% of current equity, reserve 5% for fees, and block entries when one lot cannot be funded. Earlier U02 aggregate P&L and drawdown figures are invalidated pending rerun.
- **M101-001 — Trade-return uncertainty.** Added deterministic circular moving-block bootstrap 95% CI for mean net P&L/trade when sample size is at least 20; samples below 20 are explicitly marked not estimable. This interval complements, but does not prove, account-level profitability.

## Automated run failure — 2026-10-10T18:29:26Z
- Workflow run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38075877344
- Commit: 8094b67f45f85e670ef972e5cfb467378852f042
- Job failed before the output contract was validated. Numerical outputs from this run are not accepted.
- Check results/phase101_pdf_strategy_tests/phase101_runtime_error.json if present, then fix root cause without relaxing frozen strategy rules.


## Automated failure — 2026-10-10T18:31:15Z
- Workflow run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38076023537
- Commit: 73faaf0acb43c2f621d184d2c30469101ccd5aef
- Numerical outputs from the failed run are not accepted. See `results/phase101_pdf_strategy_tests/phase101_runtime_error.json` when produced and inspect the Actions log.
- Correct the root cause without weakening frozen strategy rules or opening 2026 data.


## Automated failure — 2026-10-10T18:32:46Z
- Workflow run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38076142986
- Commit: 4f2ce8dec6de777eb28ede874a34d028adade632
- Numerical outputs from the failed run are not accepted. See `results/phase101_pdf_strategy_tests/phase101_runtime_error.json` when produced and inspect the Actions log.
- Correct the root cause without weakening frozen strategy rules or opening 2026 data.


## Automated failure — 2026-10-10T18:33:59Z
- Workflow run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38076173622
- Commit: 8abf66077650abc29c8fe75e1f372ec0dcb9d3a3
- Numerical outputs from the failed run are not accepted. See `results/phase101_pdf_strategy_tests/phase101_runtime_error.json` when produced and inspect the Actions log.
- Correct the root cause without weakening frozen strategy rules or opening 2026 data.


## Run reconciliation — 2026-10-10T18:37:17Z
- Workflow 38076280351 completed aggregate validation. No runner exception was raised; inspect report and model status CSV for explicit data/model blockers.


## Corrected replay result — 2026-10-10T18:37:18Z
- Workflow run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38076280351
- Previous U05 look-ahead and U02 repeated-capital figures are superseded. The corrected workflow completed output validation; review the report and per-opportunity/coverage ledgers before interpreting performance.
