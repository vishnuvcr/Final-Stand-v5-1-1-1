# Phase 51-4 — Available-window continuation plan

**State: ACTIVE — USER-AUTHORIZED PARTIAL-WINDOW ANALYSIS; NOT FULL-WINDOW OOS.**

## User scope decision
On 2026-10-09 the user explicitly authorized proceeding with available data while excluding the two unresolved expiry blocks (2026-07-28 and 2026-08-04). This creates an exploratory partial-window scope only. It does **not** overwrite the original Phase-51 preregistered full OOS window (2026-04-21 through 2026-08-04), and must not be reported as completion of full Phase 51.

## Research question
Within the validated available interval 2026-04-21 through 2026-07-21, what descriptive performance and robustness evidence is available for the already-frozen Phase-50B candidates, after the registered cost and friction scenarios?

## Aims and objectives
1. Reuse the source-hash-locked data and authoritative Phase 51-3 replay; do not redownload or mutate strategy logic unnecessarily.
2. Summarize the frozen candidates only, preserving the existing eligible set TT-02, TT-04 and TT-05.
3. Report net P&L, trade-level return distribution, win rate, cumulative trade-P&L drawdown, and cost/friction sensitivity with clear definitions.
4. Distinguish descriptive estimates from confirmatory inference; account for small sample, dependence, and regime/time-window limitations.
5. Preserve excluded candidates and their reasons; do not revive TT-03 when its frozen entry schedule yields no eligible campaign, or TT-06/TT-07 after terminal feasibility failures.
6. Keep full-window Phase 51 blocked and no strategy promotion until the original data and inference gates can be satisfied.

## Frozen data and scope
- Primary option object: `rissin/nse-options-intraday / upstox_intraday/NIFTY/NIFTY_2026.parquet`.
- SHA-256: `bae9943b2fa99ee9c1214fb7c695b84f9f661a050a5cd04d9c5c2ffc7bc59f73`.
- Size: 394,805,617 bytes.
- Available interval: 2026-04-21 through 2026-07-21 inclusive.
- Missing expiry blocks deliberately excluded from this *partial analysis*: 2026-07-28 and 2026-08-04.
- Canonical prior replay: [GitHub Actions run 37882057283](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37882057283).

## Methodology
- Reuse audited Phase 51-3 outputs and chronological trade ledgers.
- Keep strategy rules, lot sizes, entry/exit semantics and registered cost models frozen.
- Show Paytm Money ₹10/order and ₹20/order cases and +50% friction stress as already computed.
- No parameter search, strategy selection on a new holdout, synthetic data, forward fills, or inference from the two missing blocks.
- Treat the partial interval as exploratory/descriptive. Do not call it full OOS, a confirmatory test, or a live deployment authorization.
- If a new statistical estimate is added, predefine it and use expiry/session blocks to account for dependence; correct multiplicity where applicable. Otherwise explicitly state no new confirmatory hypothesis test is run.

## Stopping rules
This is a finite continuation. Close after:
1. source and output lineage are rechecked;
2. available-window summaries and limitations are published;
3. the no-promotion decision and remaining full-window data gate are logged;
4. README, status, error log and chat log are updated.

No further parameter tuning is authorized by this partial-data decision.
