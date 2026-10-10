# Phase 80 — Expanded strategy and source audit

> **Decision: the prior search did not test every possible combination. The finite, registered next experiment is same-structure intraday vs overnight exposure.**

## What is already covered

- Phase 45 explicitly tested 20 previously uncovered ready-made structures and combined them with 22 Phase-43 families.
- Earlier work covered VIX regime/candidate sweeps, selector/features/symbolic/ensemble policies, ratio geometry, entry filters and stop exits.
- The main Phase-45 entry/exit geometry (10:00 four sessions before expiry to expiry-day last common bar) does not answer how the same structure behaves when held intraday versus overnight.

## New leads and rights boundary

- **Bhat et al. (2024), Journal of Futures Markets** — [peer-reviewed literature](https://doi.org/10.1002/fut.22512). Delta-hedged short NIFTY options; overnight/intraday return asymmetry. Decision: hypothesis source; static structures differ.
- **Zenodo 10899828** — [minute OHLC dataset](https://zenodo.org/records/10899828). NIFTY spot, futures and options, 2017-2020. Decision: license unclear; no raw data retained.
- **artist-23/nifty-options-data** — [HF dataset](https://huggingface.co/datasets/artist-23/nifty-options-data). OHLC, IV, OI, spot and strike labels, 2020-2025. Decision: license and exact expiry identity need validation.
- **rissin/nse-options-intraday** — [HF dataset](https://huggingface.co/datasets/rissin/nse-options-intraday). explicit contract OHLC; 1m Upstox data 2024-2026 plus EOD history. Decision: license other; source terms/retention review needed; intraday OI absent.
- **thetrademarkk/india-index-options-1m** — [HF dataset](https://huggingface.co/datasets/thetrademarkk/india-index-options-1m). existing primary 1-minute OHLCV(+OI), 2021-2026. Decision: CC-BY-NC-4.0; partial coverage; no quotes/depth.
- **QuantDev-stack/OptionVault** — [code and dataset samples](https://github.com/QuantDev-stack/OptionVault). sample options/Greeks/futures/depth files. Decision: full coverage requires separately licensed data.
- **sahilempire/nifty-options-research-lab** — [open code/literature corpus](https://github.com/sahilempire/nifty-options-research-lab). strategy structures, realistic costs, backtest methods. Decision: MIT repo; third-party empirical claims not independently verified.
- **Bailey & López de Prado (2014) — Deflated Sharpe Ratio** — [statistical methodology](https://doi.org/10.3905/jpm.2014.40.5.094). selection bias/multiple testing/non-normality. Decision: include multiplicity and non-normal returns in inference.

## Frozen Phase 81 basket

| Family | Variants | Risk/use |
|---|---:|---|
| short_atm_straddle | 1 | unbounded; diagnostic-only |
| short_iron_fly_w100 | 1 | defined |
| short_iron_fly_w200 | 1 | defined |
| short_iron_fly_w300 | 1 | defined |
| long_iron_fly_w100_200_300 | 1 | debit-limited |
| short_iron_condor_100_300 | 1 | defined |
| bull_put_credit_100_300 | 1 | defined |
| bear_call_credit_100_300 | 1 | defined |

Primary paired contrast: 09:20 open to 15:20 open versus 15:20 open to next eligible 09:20 open; derive ATM using prior minute close and keep exact contracts fixed. Do not trade expiry dates or carry contracts into expiry. Require positive prices and nonzero volume at each leg's entry/exit timestamps; no forward filling or synthetic prices.

## Costs and inference

Frozen cost model: assumed Paytm Money ₹10 per executed order, statutory/transaction fees per date and one adverse ₹0.05 tick per leg per fill. This is an OHLC reference model, not proof of actual fills due to missing historical bid/ask/depth. Use lagged VIX only. Freeze shortlist from DEV/VAL; keep 2026 holdout sealed until confirmation. Use paired session/expiry-cluster inference, Holm correction, drawdown and tail risk; report all exclusions and the number of tested variants.

## Core literature

- Bhat et al. (2024), DOI 10.1002/fut.22512: delta-hedged option-return asymmetry motivates separating clock exposures but is not evidence static spreads will profit. [Wiley/DOI](https://doi.org/10.1002/fut.22512).
- Bailey & López de Prado (2014), Deflated Sharpe Ratio: selection bias grows with the number of tried variants; the full historical trial count is imperfectly enumerated and must remain a limitation. [DOI](https://doi.org/10.3905/jpm.2014.40.5.094).

## Finite end

Phase 80: inventory and source audit. Phase 81: registered DEV/VAL temporal sweep. Phase 82: frozen shortlist, inference and holdout confirmation only if data/coverage passes. Phase 83: complete manuscript with figures/tables/appendices and limitations. No rolling parameter search.
