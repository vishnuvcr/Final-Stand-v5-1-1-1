# Phase 50B — TT-06 Replay Specification

## Status
Source-faithful replay contract frozen before numerical execution. No result exists yet.

## Source strategy
Intraday Asym Premium.

## Frozen entry
- Monday sessions are excluded.
- While flat and with no prior trade that day, scan 09:30–15:10 IST.
- Sell one current-week ATM CE.
- Sell one next-week ATM PE.
- ATM is the nearest listed strike to the point-in-time NIFTY spot at the selected entry timestamp.
- Entry occurs at the earliest timestamp in the source window for which both required option quotes are simultaneously observed.

## Frozen repair logic
At each observed minute after entry:
1. CE repair trigger: current-week CE LTP <= 50% of current next-week PE LTP.
   - Buy back the current CE.
   - Select a current-week CE whose observed LTP exactly matches the contemporaneous next-week PE LTP.
   - If no exact observed premium match exists, do not invent/substitute a strike; leave the position unchanged and continue monitoring.
2. PE repair trigger: next-week PE LTP <= 50% of current-week CE LTP.
   - Buy back the current PE.
   - Select a next-week PE whose observed LTP exactly matches the contemporaneous current-week CE LTP.
   - If no exact observed premium match exists, do not invent/substitute a strike; leave the position unchanged and continue monitoring.
3. Matching uses observed quotes at the same timestamp only. No forward fill and no future quote is allowed.
4. A successful repair changes only the repaired leg; the other leg remains on its original expiry/strike.
5. The source does not document a repair-count cap, so no artificial cap is introduced. Every successful trigger is recorded as a separate close/open event, subject to the source state remaining valid.

## Frozen exit
- Exit when portfolio P&L <= -₹4,000, evaluated only from simultaneously observed quotes for both live legs.
- Otherwise exit at the earliest observed timestamp at or after 15:15 IST with complete quotes for all live legs.
- Never require an exact 15:15 quote and never impute a missing quote.

## Execution/cost model
- Historical NIFTY lot size for the target expiry.
- Adverse 0.05-point option slippage on every option execution using the parent research execution model.
- Primary brokerage ₹10/order plus date-aware statutory charges.
- Robustness scenario ₹20/order.
- +50% monetary cost/charge stress.
- No look-ahead; all strike/price decisions use contemporaneous observations.

## Coverage/accounting
- Every opened position must end as either a completed trade or an explicit coverage exclusion.
- coverage_rate = completed trades / opened positions.
- Minimum feasibility threshold: 95%.
- Coverage exclusions are never imputed and are retained in coverage_gaps.csv.
- data_errors.csv must be empty for evidence acceptance.

## Chronology
- DEV: expiry dates through 2023-12-31.
- VAL: 2024-01-01 through 2025-12-31.
- HOLD: 2026-01-01 onward, protected from tuning/selection.

## VIX
VIX is an external attribution/selection variable only. It is not used to alter the baseline entry, repair, stop or exit rules. Baseline execution must be completed before VIX-conditioned analysis.

## Determinism
If multiple exact premium matches exist at the same timestamp, choose the strike with the smallest absolute strike distance from spot; if still tied, choose the smaller strike. This tie-break only resolves otherwise identical source matches and is not a parameter search.
