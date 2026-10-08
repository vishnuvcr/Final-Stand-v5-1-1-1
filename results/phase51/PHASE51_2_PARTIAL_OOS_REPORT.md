# Phase 51-2 Partial OOS / Opportunity-Calendar Audit Report

## Executive conclusion

Phase 51-2 is **closed as non-informative for performance**, not as a strategy failure.

The available complete NIFTY option-source interval is **2026-04-21 through 2026-07-21**. The frozen Phase-51-1 source-gate record contains **14 observed expiries** in that interval, all Tuesdays. The frozen TT-03 specification requires entry **exactly three calendar days before expiry**. Therefore each scheduled entry date is a Saturday, so the available partial window contains **zero eligible TT-03 campaigns**.

This result is the consequence of the frozen strategy/calendar definition. No option P&L, cost comparison, slippage stress, broker scenario, statistical test, ranking, or promotion inference can be validly calculated from a zero-opportunity sample.

The complete Phase-51 OOS window remains **2026-04-21 through 2026-08-04**, with the 2026-07-28 and 2026-08-04 option blocks unresolved. Phase 51 therefore remains blocked at the full-window data gate.

## Research question

Can either of the two frozen Phase-50B TT-03 geometries produce a valid source-faithful fresh-OOS performance sample in the currently available Phase-51 option interval, without changing the pre-registered strategy rules or fabricating missing observations?

## Aim

Establish whether the currently available complete option-source endpoint contains any eligible fresh-OOS TT-03 campaigns under the already-frozen source-faithful entry and expiry calendar rules.

## Objectives

1. Preserve the full Phase-51 OOS window and its unresolved endpoint limitation.
2. Use only the frozen Phase-51-1 option-source evidence for the available partial interval.
3. Audit the exact expiry dates and deterministic three-calendar-day entry dates.
4. Test both frozen geometries without changing parameters.
5. Record a fail-closed outcome when no eligible campaign exists.
6. Prevent zero-opportunity intervals from being misclassified as zero-percent data coverage or as negative strategy evidence.

## Frozen candidates

- TT-03 BASE: **300 / 350 / 400** call/put ratio geometry.
- TT-03 OTM350: **350 / 400 / 450** call/put ratio geometry.

No parameter was selected, optimized, or tuned in Phase 51-2.

## Data provenance

Frozen primary options evidence from Phase 51-1:

- Repository: rissin/nse-options-intraday
- File: upstox_intraday/NIFTY/NIFTY_2026.parquet
- Recorded SHA-256: bae9943b2fa99ee9c1214fb7c695b84f9f661a050a5cd04d9c5c2ffc7bc59f73
- Available complete endpoint used for this audit: **2026-04-21 through 2026-07-21**
- Unresolved full-window expiries: **2026-07-28 and 2026-08-04**

The Phase-51-1 source gate is copied into PHASE51_1_SOURCE_GATE_REFERENCE.json so the partial branch uses an immutable research reference rather than reselecting a source after seeing results.

## Scientific methodology

The audit follows the frozen TT-03 replay contract:

- current-week expiry dates from the historical source calendar;
- entry date exactly **three calendar days before expiry**;
- non-trading entry dates are ineligible;
- 10:00–10:05 IST entry scan;
- frozen strike geometry for each candidate;
- no forward filling, interpolation, or synthetic prices;
- no parameter tuning;
- no selection based on partial-window P&L.

Because entry eligibility fails before quote inspection for every observed expiry, the workflow terminates before numerical execution.

## Deterministic eligibility calculation

| Expiry | Three-calendar-day entry date | Entry-day status |
|---|---|---|
| 2026-04-21 | 2026-04-18 | Saturday — ineligible |
| 2026-04-28 | 2026-04-25 | Saturday — ineligible |
| 2026-05-05 | 2026-05-02 | Saturday — ineligible |
| 2026-05-12 | 2026-05-09 | Saturday — ineligible |
| 2026-05-19 | 2026-05-16 | Saturday — ineligible |
| 2026-05-26 | 2026-05-23 | Saturday — ineligible |
| 2026-06-02 | 2026-05-30 | Saturday — ineligible |
| 2026-06-09 | 2026-06-06 | Saturday — ineligible |
| 2026-06-16 | 2026-06-13 | Saturday — ineligible |
| 2026-06-23 | 2026-06-20 | Saturday — ineligible |
| 2026-06-30 | 2026-06-27 | Saturday — ineligible |
| 2026-07-07 | 2026-07-04 | Saturday — ineligible |
| 2026-07-14 | 2026-07-11 | Saturday — ineligible |
| 2026-07-21 | 2026-07-18 | Saturday — ineligible |

Result: **14 observed expiries, 0 eligible expiries, 0 candidate campaigns.**

## Results

Both registered geometries returned the same deterministic outcome.

| Metric | TT-03 BASE | TT-03 OTM350 |
|---|---:|---:|
| Observed expiries | 14 | 14 |
| Eligible expiries | 0 | 0 |
| Candidate trades | 0 | 0 |
| Completed trades | 0 | 0 |
| Coverage exclusions | 0 | 0 |
| Coverage rate | N/A | N/A |
| ₹10/order net | Not applicable | Not applicable |
| ₹20/order net | Not applicable | Not applicable |
| +50% friction stress | Not applicable | Not applicable |
| Statistical inference | Not applicable | Not applicable |
| Promotion decision | No | No |

The stored artifacts use status = NO_ELIGIBLE_CAMPAIGNS and coverage_gate = NOT_APPLICABLE_NO_ELIGIBLE_CAMPAIGNS.

## Statistical analysis

No hypothesis test, confidence interval, bootstrap, permutation test, multiple-testing correction, or effect-size estimate is appropriate because the partial window contains no eligible observations.

Reporting a zero P&L or a zero-percent coverage rate as strategy evidence would be misleading. The absence of eligible observations is a calendar/protocol condition, not an economic outcome.

## Costs and execution stress

The Phase-51 registered cost model remains unchanged: Paytm Money ₹10/order and ₹20/order scenarios, statutory charges, adverse one-tick execution and +50% friction stress.

Those costs were **not applied** in the partial audit because there was no execution event to which costs could be assigned.

This is preferable to inventing trades or forcing a calendar interpretation that was not pre-registered.

## Discussion

The partial-OOS experiment revealed a boundary condition in the frozen TT-03 specification. The source-faithful rule is explicitly defined in calendar-time terms rather than trading-day terms. Once NIFTY weekly expiries fall on Tuesday, subtracting three calendar days lands on Saturday. In the observed 2026-04-21 through 2026-07-21 expiry set, this eliminates every possible entry.

This finding must not be interpreted as evidence that TT-03 is profitable or unprofitable. It only establishes that the currently available partial sample cannot evaluate the frozen strategy after the expiry-calendar transition.

A new rule such as “three trading days before expiry” could create entries, but making that change inside Phase 51 would constitute a strategy mutation and would invalidate the protected evaluation. Such a change belongs in a separately pre-registered future research phase.

## Strengths

- Full-window Phase-51 scope was not silently shortened for performance selection.
- The partial endpoint was tied to the frozen Phase-51-1 source record.
- Both frozen TT-03 geometries were checked symmetrically.
- The audit is deterministic and parameter-free.
- No synthetic prices, forward fills, or endpoint substitutions were introduced.
- Zero-opportunity status is now represented explicitly rather than as a misleading coverage failure.
- All superseded workflow failures are retained in the error log and are excluded from the evidence base.

## Limitations

- This partial window has no eligible campaigns, so it provides no performance evidence.
- The full Phase-51 OOS window still lacks the 2026-07-28 and 2026-08-04 option blocks.
- The result depends on the frozen calendar interpretation; it does not test an alternative trading-day interpretation.
- Bid/ask, liquidity and execution-cost sensitivity cannot be empirically evaluated without a valid trade universe.

## Inference

The only supported inference is:

> **The currently available 2026-04-21 through 2026-07-21 option interval cannot validate frozen TT-03 performance because the frozen three-calendar-day entry rule generates no eligible entry dates.**

No inference about profitability, drawdown, Sharpe ratio, win rate, expectancy, or production suitability is supported by this phase.

## Conclusion

**Phase 51-2: CLOSED — NO ELIGIBLE CAMPAIGNS / NON-INFORMATIVE FOR PERFORMANCE.**

No strategy is promoted or rejected on economic grounds from this phase.

The full Phase-51 decision remains pending and is still blocked by incomplete option-source coverage at the 2026-07-28 and 2026-08-04 expiries.

## Future research direction

A future, separately registered phase may test a calendar-normalized interpretation of the Tradetron condition (for example, three trading sessions before expiry) against the exact historical expiry calendar. That study must be treated as a new strategy specification, not as a continuation of this Phase-51 evidence, and must preserve development/validation/holdout separation.

The immediate Phase-51 requirement remains a full auditable option dataset covering **2026-04-21 through 2026-08-04** before any complete-window P&L or promotion decision.

## Reproducibility artifacts

- results/phase51/partial_oos/d300/opportunity_audit.json
- results/phase51/partial_oos/d300/summary.json
- results/phase51/partial_oos/d350/opportunity_audit.json
- results/phase51/partial_oos/d350/summary.json
- results/phase51/PHASE51_1_SOURCE_GATE_REFERENCE.json
- research/phase51_2_partial_oos.py
- .github/workflows/phase-51-2-available-data-partial-oos.yml
- results/phase51/PHASE51_2_ERROR_LOG.md
- results/phase51/PHASE51_2_CHAT_LOG.md
