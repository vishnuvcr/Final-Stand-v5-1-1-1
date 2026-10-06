# Phase 37 Manuscript — Corrected Model Direction Polarity

## Abstract
Phase 37 re-tested five frozen predictive direction selectors after an implementation audit found that Phase 36 mapped an NIFTY up/bullish probability to the wrong Continuous Delta 6x6 spread. Phase 35's target is the sign of expiry-close relative to reference spot, so the economically consistent mapping is bullish/up -> PUT credit spread and bearish/down -> CALL credit spread. No model, threshold, feature set, execution parameter or transaction-cost assumption was retuned.

Across 2024-01-01 to 2026-06-30, all five corrected selectors were post-cost profitable. CatBoost produced ₹57,874.80 net, Markov-regime tree ₹53,060.31, Wavelet-tree ₹31,294.89, OOF stack ₹24,765.71 and DART ₹19,372.11. The untouched 2026 holdout was positive for all five: CatBoost +₹49,054.33, Wavelet-tree +₹50,776.68, OOF stack +₹48,345.59, Markov-regime tree +₹41,969.35 and DART +₹39,053.96.

The Phase-36 model-selector conclusion is therefore invalid for the intended hypothesis because the polarity was reversed. Phase 37 does not yet establish superiority over the stateful control because the required common-expiry paired bootstrap has not been regenerated in this branch. The evidence supports advancing the strongest corrected selectors to a dedicated robustness phase, not immediate live promotion.

## Research question
Does mapping a model's NIFTY bullish/up probability to the PUT credit spread, and bearish/down probability to the CALL credit spread, improve the Continuous Delta 6x6 strategy with all other rules frozen?

## Methodology
The only intervention was the model-to-spread polarity:
- p >= 0.50 (up/bullish) -> PUT;
- p < 0.50 (down/bearish) -> CALL.

Previous trade P&L, previous direction, win/loss and cumulative strategy P&L are excluded from direction selection.

Frozen execution: NIFTY 50 current weekly expiry; 6 lots per leg; 50-point vertical; entry from 09:20 IST; no expiry-day new entries; last entry before 15:28 IST; short leg nearest ±0.25 delta; protective leg 50 points away; exits at ±0.50 or ±0.04; chronological non-overlap; no discretionary rollover; identical Phase-32/36 slippage, brokerage and statutory charges.

Primary sample: 2024-01-01 through 2026-06-30. There were 128 expected expiries, 104 corresponding option files available and 103 processed after completeness checks. The Phase-35 selector cache contains 117 event forecasts.

## Results

| Selector | Trades | Net P&L | Costs | Win rate | PF | Max DD | 2026 holdout |
|---|---:|---:|---:|---:|---:|---:|---:|
| CatBoost | 203 | ₹57,874.80 | ₹19,075.20 | 64.04% | 1.186 | ₹49,337.02 | ₹49,054.33 |
| Markov-regime tree | 197 | ₹53,060.31 | ₹19,082.19 | 63.96% | 1.174 | ₹40,547.67 | ₹41,969.35 |
| Wavelet-tree | 195 | ₹31,294.89 | ₹19,010.61 | 63.59% | 1.100 | ₹54,085.53 | ₹50,776.68 |
| OOF stack | 198 | ₹24,765.71 | ₹19,362.79 | 63.64% | 1.081 | ₹62,024.82 | ₹48,345.59 |
| DART | 198 | ₹19,372.11 | ₹19,894.89 | 62.12% | 1.060 | ₹52,629.57 | ₹39,053.96 |

All five are positive after costs, and all five are positive on the 2026 holdout.

### Temporal behavior
2024 was profitable for all five. 2025 was negative for all five. 2026 was strongly positive for all five. This creates a clear regime dependence and makes rolling validation essential before any promotion.

### Direction asymmetry
CALL-side trades contributed strongly to aggregate profitability:
- CatBoost CALL +₹64,964.67; PUT -₹7,089.87.
- DART CALL +₹45,575.41; PUT -₹26,203.30.
- Wavelet CALL +₹52,715.78; PUT -₹21,420.89.
- OOF stack CALL +₹43,059.97; PUT -₹18,294.25.
- Markov-regime CALL +₹72,182.19; PUT -₹19,121.88.

This asymmetry must be stress-tested rather than treated as universal model calibration.

## Statistical status
The preregistered common-expiry selector-minus-stateful-control bootstrap was not regenerated in Phase 37. Therefore no formal superiority claim versus the canonical stateful control is made.

The accepted evidence establishes:
1. positive post-cost full-sample P&L for every corrected model;
2. PF > 1 for every corrected model;
3. positive 2026 holdout P&L for every corrected model;
4. complete trade, skip, summary and coverage artifacts;
5. exact corrected polarity in every summary.

## Discussion
The polarity correction reverses the Phase-36 model result. This is consistent with the economic structure of the strategy: the predictive target describes NIFTY direction, while the selected credit-spread side has the opposite option exposure. The correction was registered without model retraining or threshold tuning.

The 2026 result is particularly important because it was retained as a holdout. Nevertheless, the negative 2025 period and strong CALL-side contribution mean the apparent edge could be regime- or side-specific.

CatBoost has the highest full-sample net P&L. Markov-regime tree has the lowest maximum drawdown. Wavelet-tree has the strongest 2026 holdout P&L. These rankings are descriptive, not statistically significant rankings.

## Strengths
- single registered polarity correction;
- frozen cached forecasts;
- no post-result tuning;
- realistic historical slippage and transaction costs;
- untouched 2026 holdout;
- complete selector ledgers;
- reproducible GitHub Actions workflow;
- explicit error log.

## Limitations
- incomplete historical option coverage;
- no Phase-37 paired bootstrap against the stateful control yet;
- historical fills do not model full order-book queue/latency;
- expiry-level forecasts are frozen rather than intraday-updated;
- pronounced CALL/PUT asymmetry;
- positive backtest performance does not prove live profitability.

## Conclusion
**Phase 37 correction validated the direction-polarity implementation and materially changes the model-selector conclusion.**

All five corrected models are post-cost profitable and positive on the 2026 holdout. However, none is promoted directly to live trading. The next phase must establish control-relative statistical robustness and execution realism.

## Future research
Phase 38 should test:
1. paired common-expiry bootstrap versus the canonical stateful control;
2. rolling/walk-forward validation;
3. CALL/PUT asymmetry;
4. slippage and transaction-cost stress;
5. model agreement/ensemble stability;
6. full bid/ask, latency and fill-probability assumptions where data permit.

## Appendix
Each selector directory contains trades.csv, skips.csv, summary.csv, yearly_statistics.csv, direction_statistics.csv, selector_usage.csv, coverage.json and run.log. F36-006 records the original polarity mismatch and Phase 37 is the registered correction.
