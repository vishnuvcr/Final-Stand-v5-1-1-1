# Current research status — 2026-10-10 (Phase 67 contract/minute coverage diagnostic)

**Current decision: Phase 67 diagnostic complete; no strategy is approved for live trading.** The diagnostic workflow is reproducible and published, but exact-minute source coverage and unresolved event-to-contract mapping do not support a rule-faithful replay or profitability inference.

## Latest completed phase — Phase 67

[GitHub Actions run 38033174754](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38033174754) completed setup, dependencies, tests, bounded audit, output validation and publication successfully.

| Audit metric | Result |
|---|---:|
| Frozen DEV/VAL trigger rows | 30 |
| Rows with exact trigger-minute observation | 8 |
| Rows with exact next-minute observation | 5 |
| Rows with ±2-minute context | 8 |

These counts describe timestamp coverage only. Nearby bars are never substituted as fills. The source has OHLC, volume, OI, symbol, strike, option type and expiry fields, but the phase did not prove reliable event-level ITM/side/expiry eligibility or execution-grade liquidity. No P&L is calculated and no strategy is promoted.

- [Phase 67 plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-67-contract-coverage-diagnostic/PHASE67_RESEARCH_PLAN.md)
- [Phase 67 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-67-contract-coverage-diagnostic/PHASE67_STATUS.md)
- [Aggregate summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-67-contract-coverage-diagnostic/results/phase67_contract_coverage/summary.json)
- [Diagnostic report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-67-contract-coverage-diagnostic/results/phase67_contract_coverage/report.md)
- [Event-level diagnostics](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-67-contract-coverage-diagnostic/results/phase67_contract_coverage/event_diagnostics.csv)
- [Schema audit](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-67-contract-coverage-diagnostic/results/phase67_contract_coverage/schema_audit.json)
- [Error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-67-contract-coverage-diagnostic/PHASE67_ERROR_LOG.md)
- [Research log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-67-contract-coverage-diagnostic/PHASE67_RESEARCH_LOG.md)
- [Chat/continuation log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-67-contract-coverage-diagnostic/PHASE67_CHAT_LOG.md)

## Previous source-sufficiency gate — Phase 61

**NO-GO for new empirical factor-conditioned strategy testing until source rights and exact target samples are verified.** Phase 61 assessed five newly surfaced leads: three follow-up-only, two unsuitable for the frozen historical replay, and none accepted for exact-sample validation. Do not repeat the same source search, treat exclusions as losses, relax filters, or use the holdout.

- [Phase 61 plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-61-new-source-restart-audit/PHASE61_RESEARCH_PLAN.md) · [Status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-61-new-source-restart-audit/PHASE61_STATUS.md) · [Source registry](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-61-new-source-restart-audit/research/phase61/source_registry.json) · [Decision report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-61-new-source-restart-audit/results/phase61/source_restart_audit/report.md)
- [Phase 60 evidence sufficiency gate](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-60-evidence-sufficiency-gate)
- [Phase 59 public option data coverage audit](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-59-public-option-data-coverage-audit/results/phase59/public_option_data_coverage/report.md)

## Strategy replay caveats carried forward

- **Phase 52 baseline:** 480 planned configuration-event rows; 379 excluded by the frozen 2% OHLC range proxy, 100 blocked by prior-minute OI eligibility, and only 1 replay pass. One executed row is not a meaningful profitability sample.
- **Phase 54:** preregistered OHLC-range coverage counts at 2/3/4/5/6/8/10/12/15/20/1000% were 1/1/8/24/55/91/150/227/298/345/380. Coverage only; candle range is not bid/ask spread.
- **Phase 56/57:** 18,960 modeled OHLC-reference scenarios; independent reproduction matched 2,286 common scenarios with zero mismatches. This validates reproducibility of the same model, not executable fills.
- **Phase 59–61:** no accepted free/license-clear exact prior-minute OI source or historical quote/depth source for the frozen target sample.
- **Phase 64–66:** CCI paper-derived strategies had zero completed trades in the tested DEV/VAL replay; coverage failure is not evidence of negative expectancy. Phase 67 confirms sparse exact-time observations but does not prove full contract mapping.
- All future valid replays must include Paytm Money brokerage/statutory charges, adverse slippage and stress-cost scenarios. No live deployment until data validity, execution assumptions, sample sufficiency and out-of-sample robustness pass.

## Phase 67 workflow failures and fixes

- [Run 38032877348](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38032877348): setup-python failed; pip cache configuration removed.
- [Run 38033032907](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38033032907): audit passed but publication failed; exact git error unavailable.
- [Run 38033174754](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38033174754): end-to-end success after rebase-before-push repair.
