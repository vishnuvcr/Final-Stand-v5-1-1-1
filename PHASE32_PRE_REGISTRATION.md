# Phase 32 Pre-Registration — Continuous Delta 6x6 Vertical Spread

## Research hypothesis
The supplied continuous delta-following 6x6 vertical spread may generate repeatable net returns by maintaining the direction after profitable exits and reversing after losing exits, with exits triggered directly by the short-leg delta.

## Null hypothesis
After realistic slippage, Paytm Money brokerage and applicable statutory transaction costs, the strategy does not generate a robust positive risk-adjusted historical edge.

## Frozen parameters
| Parameter | Frozen value |
|---|---|
| Underlying | NIFTY 50 |
| Starting direction | CALL |
| Position size | 6 lots per leg |
| Spread width | 50 points |
| Entry time | >= 09:20 IST |
| Weekly expiry | current weekly expiry |
| New entry on expiry day | blocked |
| CALL short delta | +0.25 |
| CALL long strike | short strike + 50 |
| CALL exit | short delta >= +0.50 OR <= +0.04 |
| PUT short delta | -0.25 |
| PUT long strike | short strike - 50 |
| PUT exit | short delta <= -0.50 OR >= -0.04 |
| Direction after win | unchanged |
| Direction after loss | flipped |
| Universal daily square-off | none |
| Rollover | none |
| Execution model | primary 1-minute historical resolution |
| Capital reference | ₹6,00,000 |

## Direction state machine
Initial state: CALL.

After each completed trade:
- net trade P&L > 0 -> same direction;
- net trade P&L < 0 -> flip direction;
- net trade P&L = 0 -> same direction.

## Data rules
- Use observed option prices only.
- No forward fill.
- No interpolation.
- Exact common timestamps are required for selected legs and the NIFTY spot series.
- Missing strike/expiry observations are logged, not synthesized.
- Delta must be calculated consistently with the frozen research engine and the option contract inputs available at that timestamp.

## Execution rules
The backtest must model both legs of the spread, all six lots, entry and exit slippage, brokerage and applicable statutory charges. Gross and net results must both be retained.

When an exit trigger is first observed on a minute bar, the engine must use the pre-registered executable-price convention for that observation and must not use information from later bars.

## Expiry termination rule
The supplied strategy explicitly blocks new entries on expiry day and has no universal daily square-off. Therefore any position still open when the current weekly contract terminates must be handled at contract termination using the repository's reproducible market/settlement convention. The exact implementation is an audited engine rule and must be stated in the numerical result.

## Primary evaluation
Primary sample: longest validated reproducible 1-minute NIFTY option history currently supported by the repository, expected approximately 2021-01-01 through 2026-09-30.

No training-driven parameter selection is permitted for the primary result.

## Robustness
After the frozen primary run, robustness checks may perturb:
- execution slippage;
- transaction-cost assumptions;
- subperiod/regime;
- validated delta calculation details.

No new exit threshold or direction rule may be selected after seeing the primary results within this phase.

## Evidence acceptance
Numerical evidence is accepted only from a successful GitHub Actions run that persists:
- trade-level ledger;
- summary statistics;
- error/data-coverage report;
- reproducibility metadata.