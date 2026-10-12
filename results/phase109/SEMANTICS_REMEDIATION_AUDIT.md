# Phase 109 semantic implementation audit

**Initial status:** Source defects confirmed; corrected Actions run pending.  
**v1 engine:** `phase109-eod-engine-v1`  
**v2 engine:** `phase109-eod-engine-v2-semantics`  
**Promotion:** None.

| Risk | v1 behavior | v2 correction |
|---|---|---|
| Strategy core identity | Name fragments could map another architecture to ROC/EMA/reversion methods | Exact allowlist only |
| EMA slope | Alias of ordinary price-return momentum | Normalized change in EMA from the previous signal observation |
| EMA crossover | Current EMA spread sign only | Requires a previous/current sign crossing and threshold |
| Cross-asset confirmation | Reused the opposite domestic index as generic cross-asset evidence | Unsupported confirmation families are blocked |
| Realised-volatility low/high | Computed a state but did not select a target state | Blocked until target state is explicitly preregistered |
| Risk-profile execution | Escaped stop/target regex could fail to parse registered premium barriers | Shared `parse_risk_profile()` helper and regression coverage |
| Resume reproducibility | Existing cursor could be reused by modified logic | Engine version bump resets cursor; v2 results separate from v1 |

## Rule coverage
The v2 allowlist consists of ROC momentum, EMA crossover, normalized EMA slope, return z-score fade, RSI rebound, Bollinger reversion, EMA-deviation fade, and relative strength. This describes coded rules, not profitable strategies. Other registered architectures remain visible as blocked pending actual inputs, rule cores and tests.

## Required costs and validation
Each evaluated eligible configuration must be costed at all 24 registered combinations: ₹10/₹15/₹20 brokerage per order, ₹0/₹0.05/₹0.25/₹0.50 per-option-unit-per-side adverse slippage, and 1.0×/1.5× modeled fees. The canonical date-effective charge model is retained. Development/validation only for selection; the 2026-04 onward holdout is reserved. Multiple-testing/session-cluster inference and execution validation are mandatory. Positive-volume EOD OHLC is not verified executable price evidence. No strategy is promoted.

## Additional source-validity finding — 2026-10-12

The official index/VIX context audit returned only 218 unique dates per series across the requested multi-year range, while 743 options archive dates were available. The source audit previously checked schema/duplicate/OHLC quality and nonempty data but did not check date density, so its PASS was not sufficient for VIX/regime research. The prior context and any v2 results using it are diagnostic only.

Current correction: source queries are now limited to 60-calendar-day windows and each of India VIX, NIFTY 50 and NIFTY BANK must cover at least 90% of weekdays in the requested window. The dispatch gate also validates archive/index date overlap; the evaluator has an independent v3 runtime coverage guard and refuses the old v2 cursor. Latest test evidence: [run 38225233888](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225233888), 32/32 passed. Updated source run [38225253211](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225253211) remains queued behind the earlier acquisition run [38224816723](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224816723). No corrected v3 empirical checkpoint is yet verified.
