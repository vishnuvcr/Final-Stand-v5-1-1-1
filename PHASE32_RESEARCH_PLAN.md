# Phase 32 Research Plan — Continuous Delta 6x6 Vertical Spread

## 1. Purpose
Backtest the user-specified Tradetron strategy Continuous Delta 6x6 Vertical Spread (0.25 Delta) on NIFTY 50, independently of the canonical dynamic-n research. This phase is a separate strategy study and must not alter the Phase-20 canonical strategy.

## 2. Primary research question
Does the specified continuous direction-following delta vertical-spread strategy produce robust positive net performance after realistic NIFTY option execution costs, slippage and brokerage assumptions over the available historical sample?

## 3. Exact strategy under test
Underlying: NIFTY 50.
Capital reference: ₹6,00,000.
Position size: 6 lots per leg.
Spread width: 50 NIFTY points.
Contract: current weekly expiry.
Product intent: NRML.
Entry monitoring resolution: use the highest reproducible resolution supported by the repository data; the primary historical dataset is 1-minute, so the first backtest is minute-resolution unless a validated finer-resolution source is separately registered.

Initial direction:
- target_dir = +1 (CALL).

Direction update after a completed trade:
- trade_result = exit portfolio P&L − entry portfolio P&L.
- trade_result > 0: keep the same direction.
- trade_result < 0: flip direction.
- Do not change direction for an exact zero result.

CALL entry:
- target_dir = +1.
- No NIFTY 50 position open.
- NIFTY time >= 09:20 IST.
- Today is not the current weekly-expiry day.
- SELL 6 lots of the current-week CE at the exact +0.25-delta strike.
- BUY 6 lots of the current-week CE at the +0.25-delta strike + 50 points.

CALL exit:
- Exit the entire spread when the short CE delta >= +0.50 OR <= +0.04.
- Record the first timestamp satisfying either condition.
- If both are satisfied at the same observation, report the observation and apply a deterministic precedence rule documented in the engine.

PUT entry:
- target_dir = -1.
- No NIFTY 50 position open.
- NIFTY time >= 09:20 IST.
- Today is not the current weekly-expiry day.
- SELL 6 lots of the current-week PE at the exact -0.25-delta strike.
- BUY 6 lots of the current-week PE at the -0.25-delta strike - 50 points.

PUT exit:
- Exit the entire spread when the short PE delta <= -0.50 OR >= -0.04.
- Record the first timestamp satisfying either condition.

No discretionary daily square-off:
- No 15:25 universal exit.
- Existing positions are allowed to remain open across sessions.

Expiry handling:
- No new entry on expiry day.
- A position that remains open into contract expiry must be closed/settled at the contract-termination boundary using the best reproducible historical price/settlement convention supported by the source data. This is a contract-termination rule, not a discretionary strategy exit.
- The exact settlement implementation must be documented before numerical evidence is accepted.

Rollover:
- Do not roll an existing position to another weekly expiry.

## 4. Backtest construction
### Phase 32A — implementation audit
1. Freeze this plan and the exact strategy specification.
2. Inspect the available option-chain schema, weekly-expiry mapping and delta calculation already used by the research repository.
3. Reuse validated strike-selection and cost/slippage components where compatible.
4. Build an independent continuous-trade state machine: FLAT -> OPEN CALL/PUT -> EXIT -> P&L classification -> direction update -> FLAT.
5. Add deterministic tie-breaking for simultaneous triggers and missing observations.
6. Add an audit trail for every trade and every skipped entry.

### Phase 32B — execution-cost model
Use the repository's validated Paytm Money/NSE research cost model wherever it is appropriate to this strategy. Report separately:
- gross option P&L;
- slippage;
- brokerage;
- statutory transaction charges/fees;
- net P&L.
No candidate is considered successful on gross P&L alone.

### Phase 32C — primary historical run
Run over the validated available sample without look-ahead, forward fill or interpolation. Preserve missing-data diagnostics.
Primary sample should cover the longest validated source window currently supported by the repository, approximately 2021-01-01 through 2026-09-30 unless the data audit establishes a narrower reproducible window.

### Phase 32D — statistical analysis
Report:
- trade count;
- winning/losing trade count;
- win rate;
- mean/median net P&L per trade;
- profit factor;
- expectancy;
- cumulative P&L;
- maximum drawdown;
- drawdown duration;
- per-year and per-regime results;
- direction-switch statistics;
- holding-time distribution;
- expiry-day carry/termination statistics;
- cost contribution;
- exposure and turnover;
- consecutive wins/losses.

Where sample size permits, include bootstrap confidence intervals for mean trade P&L and aggregate P&L.

### Phase 32E — robustness checks
Pre-register and evaluate, without changing the primary result:
- one-minute timestamp/execution assumptions;
- small slippage perturbations;
- brokerage/fee perturbations;
- delta-calculation sensitivity where a validated alternative is available;
- missing-data sensitivity;
- subperiods and market regimes.
Any alternative that changes the strategy definition becomes a separately registered sub-test rather than silently replacing the primary specification.

### Phase 32F — conclusion
Classify the strategy as:
1. supported for further paper/forward validation;
2. promising but insufficiently robust;
3. rejected by the historical evidence.
A positive historical result is not treated as proof of live profitability.

## 5. Promotion standard
The primary strategy is not promoted merely because it is profitable. Evidence must also show:
- reproducible successful workflow execution;
- complete trade ledger;
- explicit execution-cost accounting;
- no material implementation gaps;
- stable results across meaningful subperiods;
- no unexplained dependence on missing data.
If the result is weak, the phase stops at the registered robustness checks rather than evolving into unrestricted optimization.

## 6. Required artifacts
- PHASE32_RESEARCH_PLAN.md
- PHASE32_PRE_REGISTRATION.md
- PHASE32_STRATEGY_SPEC.md
- PHASE32_STATUS.md
- research/phase32_continuous_delta_6x6_backtest.py
- .github/workflows/phase-32-continuous-delta-6x6-backtest.yml
- results/dynamic_strategy_phase32/ (created when numerical results exist)
- phase-specific research log/error entries
- updated branch README.md

## 7. Phase boundaries
This phase tests the supplied strategy as specified. It does not change:
- the canonical Phase-20 strategy;
- the historical dynamic-n result;
- prior phase conclusions.
Any proposed modification to the direction engine, delta thresholds, width, position size, expiry handling, or entry timing after observing results requires a new explicitly registered research phase.