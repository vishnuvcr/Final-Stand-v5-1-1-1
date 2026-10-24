# Phase 112 Research Manuscript — Greek Stop-Loss Combinations

## Abstract
This fixed-rule experiment tests five Greek stop features for single-leg weekly NIFTY options chosen from a daily ZigZag-style pivot. It compares single-Greek thresholds and every multi-Greek subset with OR/AND triggers against Delta-only and no-stop references after modeled costs. The original TradingView ZigLib source is not embedded in the Pine provided; all results remain proxy-based and no candidate is promoted.

## Research question, aim and objectives
Determine whether Gamma, Vega, Theta or Rho adds value to the existing Delta stop. Keep entry, selection, timestamp rules and scheduled exit frozen. Test all 72 candidates with 24 fee/slippage cases and chronological splits.

## Methodology
Confirmed HL/LL sells a PE; HH/LH sells a CE. Select closest valid absolute delta 0.10 from the exact 09:59 close; enter exact 10:00 open next session after prior expiry. Exit scheduled expiry day at 10:00. A completed-minute close triggers a stop, filled on the next observed minute open. Greeks are inferred from European Black–Scholes at 6% rate and zero dividend. Gamma and Vega are normalized to entry premium and preset shocks; Theta is relative to initial short-theta; Rho is a 1-percentage-point rate sensitivity fraction. No interpolation or invented fill is permitted.

## Statistical analysis
Report development (through 2023), validation (2024–2025), and available holdout (2026 onward). Full candidate-by-cost outcomes and primary-cost trade ledger are machine-readable. Bootstrap CIs and p-values are descriptive, not proof; multiple comparisons and serial dependence limit inference. Holdout is not ranked.

## Results
See PHASE112_REPORT.md, candidate_cost_grid.csv, coverage.json and campaign_exclusions.csv. Empty estimates are null, not measured zero-return outcomes.

## Discussion
Additional Greeks can stop a losing option earlier but can also truncate profitable theta decay. Gamma/Vega shock proxies and Rho sensitivity are model definitions, not validated execution-risk quantities. Rho may rarely trigger on short weekly maturities. OHLC fills, constant volatility/rate assumptions, data coverage selection and the missing ZigLib source limit strategy-specific claims.

## Strengths and limitations
Strengths: frozen signal, exact time joins, five Greeks, all subsets, OR/AND logic, fixed thresholds, 24 cost scenarios and matched no-stop comparisons. Limitations: unverified indicator parity, model Greeks, partial option source, simulated fills, multiple-comparison risk and sparse holdout.

## Conclusion and future direction
Do not promote a stop rule from this exploratory replay alone. Any follow-up should be bounded and use confirmed TradingView label fixtures and stronger quote data without re-tuning against holdout.
