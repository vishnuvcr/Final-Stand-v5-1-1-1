# Phase 112 Research Manuscript — Greek Stop-Loss Combinations

## Abstract
This fixed-rule experiment evaluated stop-loss triggers using Delta, Gamma, Vega, Theta and Rho for one-leg NIFTY weekly options selected from a daily ZigZag-style pivot. It tested 19 single-Greek threshold variants, all 52 multi-Greek subsets with OR/AND logic, a no-stop reference, and 24 cost scenarios. In validation, no single-Greek stop or multi-Greek combination generated positive paired net-P&L uplift versus no-stop across the registered cost cases. No candidate is promoted. The source signal is a Python causal proxy because the supplied Pine imports an external ZigLib library whose body was not included.

## Research question, aim and objectives
Determine whether additional Greeks improve after-cost results or drawdown beyond the existing Delta 0.50 stop, holding the entry rule fixed. Objectives were to estimate minute-level Greeks, normalize incompatible units, execute all pre-registered stop combinations, reconcile costs, compare matched outcomes and report development/validation/holdout without tuning on holdout.

## Scientific methodology

### Fixed entries and exit timing
The inherited Phase 111 rule remains fixed: the last confirmed daily HL/LL selects a put and HH/LH selects a call; select the valid contract closest to absolute model Delta 0.10 from the exact 09:59 completed bar; enter at the exact 10:00 open on the first observed session after the previous expiry. Scheduled exit is exact 10:00 on target expiry day. A completed-minute close can trigger a stop, which fills at the next exact observed market-minute open. Missing or invalid option/spot minutes are excluded rather than filled.

### Greeks and triggers
European Black–Scholes estimates use a fixed 6% rate and zero dividend. Delta uses absolute option Delta. Gamma is normalized to the entry-premium fraction estimated for a 0.5% spot shock. Vega is normalized to the entry-premium fraction for a 5-vol-point shift. Theta is the ratio of current short Theta to entry short Theta and breaches downward. Rho is normalized to entry-premium sensitivity for a 100-basis-point rate change.

The registered grid has 19 individual-Greek threshold variations and 52 OR/AND rules across every multi-Greek subset, plus no-stop baseline. The fixed combination thresholds were Delta 0.50, Gamma 0.20, Vega 0.20, Theta 0.25 and Rho 0.0005. The 24 cost cases vary brokerage (₹10/₹15/₹20 per order), adverse slippage (₹0/₹0.05/₹0.25/₹0.50 per option unit per side), and fee multiplier (1.0×/1.5×).

### Data and coverage
Dataset revision SHA is \`0f4800e43e6f96cec0794369d78eb4d3c4211ef5\`, with observed expiry files from 2021-05-27 through 2026-08-04. There were 259 scheduled campaigns, 139 eligible and 124 excluded. Eligible counts were development 93, validation 45 and holdout 1. The source is partial and declared CC BY-NC 4.0. The option selection uses the inherited minimum pre-entry OI gate of 100 units at the exact 09:59 bar.

## Statistical analyses
For each candidate, split and cost scenario the results report gross/net P&L, per-trade outcomes, return on entry premium, win rate, profit factor, max drawdown, stop-hit percentage and paired uplift against no-stop and Delta 0.50. Campaign-bootstrap intervals and one-sided p-values are descriptive; the grid creates multiple-comparison risk and campaign outcomes may be serially dependent. Holdout is not used to rank candidates.

## Results

### Matched no-stop comparison
At the primary cost case (₹20 per order, ₹0.25 per-unit adverse slippage per side, 1.0× modeled fees), no-stop returned ₹24,244.61 over 93 eligible development campaigns and ₹10,854.87 over 45 validation campaigns. Delta 0.50 returned ₹7,116.47 in development and ₹7,066.39 in validation, underperforming the matched no-stop benchmark by ₹17,128.13 and ₹3,788.48, respectively.

Gamma 0.30 returned ₹17,210.24 in development and ₹7,567.34 in validation. It reduced max drawdown versus no-stop in both splits (development ₹4,596.78 vs ₹7,192.71; validation ₹3,154.76 vs ₹3,663.00) but still sacrificed net P&L by ₹7,034.37 and ₹3,287.53. In validation it outperformed Delta 0.50 by roughly ₹500.95 in net P&L, but that relative advantage does not beat no-stop.

Theta 0.50 returned ₹23,691.76 in development and ₹10,367.11 in validation; it modestly underperformed no-stop. Theta thresholds 0 and 0.25 did not trigger, so their results are just the no-stop reference. Delta+Gamma OR (Delta 0.50, Gamma 0.20) reduced validation max drawdown to ₹1,963.18, but net P&L dropped to ₹2,669.21 with paired uplift of -₹8,185.66.

### Combination and threshold findings
Across validation:
- **0 of 52 multi-Greek combinations produced positive paired uplift versus no-stop across any of the 24 cost settings.** For every cost scenario, 37 combinations were negative and 15 were exactly equal to no-stop because they never triggered.
- **0 of 19 individual-Greek threshold variants produced positive paired uplift across any cost case.** Seventeen were negative across all 24 scenarios; the two inactive Theta rules were exactly equal to no-stop.
- Vega and Rho variants each stopped 100% of the 45 validation campaigns at the registered normalization/threshold scales, with net P&L -₹3,186.70 and paired uplift -₹14,041.57.
- Gamma 0.05 and 0.10 stopped 97.8% and 95.6% of validation campaigns, respectively, and both lost money. Gamma 0.20 stopped 73.3% and Gamma 0.30 42.2%.
- The holdout contained just one eligible campaign. No stop fired for the no-stop, Delta 0.50 or Gamma 0.30 candidates on that event. Those holdout rows are not meaningful evidence of generalization.

## Discussion
The stop conditions as registered often either did not fire (therefore behaving exactly like no-stop) or fired too aggressively (Vega, Rho and lower Gamma thresholds), truncating the premium collection and generating poor outcomes. Gamma 0.30 provides a useful illustration of the risk/return trade-off: it lowered observed drawdown but did not produce better net P&L than no-stop. No multi-Greek interaction demonstrated a repeatable profit improvement over the matched no-stop exit in validation, including under the cost stresses.

The results do not imply that Greeks have no predictive information in general. They indicate only that these pre-specified normalized metrics and thresholds, on this proxy signal and this incomplete historical dataset, failed to demonstrate a net-return improvement over no-stop. Thresholds must not be retuned on the same validation/holdout sample and then described as independently validated.

## Strengths and limitations
**Strengths:** fixed entry signal; explicit causal timing; all multi-Greek subsets; OR/AND logic; normalized thresholds; 24 cost scenarios; next-minute fills; matched no-stop and Delta references; exclusion accounting; chronological splits.

**Limitations:** exact parity with TradingView ZigLib is unverified; model-estimated Greeks use fixed rate/yield; partial strike and minute coverage may create selection bias; prices are OHLC simulated fills, not bid/ask order-book executions; charges are approximations and not verified against an individual Paytm Money contract note; only one holdout campaign qualifies; and the wide candidate grid creates multiple-comparison risk.

## Conclusion
**No tested stop-loss candidate is promoted.** The Delta 0.50 stop, Gamma/Theta alternatives and all tested Greek combinations failed to improve validation net P&L over the matched no-stop exit across registered costs. Some combinations reduced drawdown but at material net-P&L cost. The holdout is too small to validate any candidate.

## Future direction
Any additional study should be a separate, bounded phase: first verify confirmed labels against actual TradingView/ZigLib output; then, only if needed, pre-register alternative economically grounded threshold scales or use better bid/ask/depth data. Do not tune on the holdout or promote a rule based on this exploratory sweep alone.

## Appendices and artifacts
- \`PHASE112_RESEARCH_PLAN.md\`: full research questions, candidate thresholds and gate definitions.
- \`PHASE112_REPORT.md\`: concise results and primary-cost comparison.
- \`summary.json\`, \`coverage.json\`, \`candidate_registry.json\`: run and scope metadata.
- \`candidate_cost_grid.csv\`: all 5,184 candidate × cost × split rows.
- \`campaign_ledger_primary.csv\`, \`campaign_exclusions.csv\`, \`source_manifest.csv\`: event-level audit trail and source hashes.
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/40072066860
