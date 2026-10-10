# Phase 102 — Final Strategy Ranking and Evidence Reconciliation

**Status at publication:** ranking drafted; automated validation pending.  
**Decision:** no strategy promoted.  
**Scope:** evidence from existing committed repository outputs only; no new market data or strategy tuning.

## Executive decision

**TT-03 dynamic-N V5 is the highest-priority candidate for one further independent validation, but not a validated profitable or deployable strategy.** It reports 200 completed trades from 201 candidates (99.50% coverage), zero data errors, ₹89,669.15 net at its base cost scenario, ₹82,074.11 under +50% friction, and ₹60,834.11 at ₹20/order plus +50% friction. Its DEV/VAL results are positive (121 trades/₹50,041.37; 76 trades/₹33,426.00), but the HOLD split has only 3 trades (₹6,201.79). This sample imbalance is decisive: the full-sample result is not independent confirmation.

The Phase-32 stateful control remains the historical comparator: 206 trades, net ₹63,672.58, gross ₹84,054.00, costs ₹20,381.42, 65.53% win rate, profit factor 1.203, and max drawdown ₹61,960.87. Five model selectors have lower full-sample net than the frozen control, negative point-estimate paired differences on 93 common expiry blocks, and bootstrap intervals crossing zero. The separate replay mismatch (205 trades/103 expiry blocks/+₹65,945.47 versus frozen 206/102/+₹63,672.58) remains an explicit reproducibility limitation.

TT-04 and TT-05 were positive in the short Phase 51-3 sample from 2026-04-21 through 2026-07-21, but older historical HOLD samples are negative. Phase 78 reports TT-04 HOLD −₹6,456.29 and TT-05 HOLD −₹40,244.68 (base scenario); both fail the temporal-stability gate. The missing 2026-07-28 and 2026-08-04 option blocks prevent completion of the registered target window. TT-02 was negative across all four partial-window cost/friction scenarios.

Phase 101 materially weakens the tested U02/U05 implementations: RF, XGBoost and LSTM5 each lost approximately 99.99% of a ₹100,000 account, while U05's seven completed trades lost ₹283,669.90 from ₹300,000. The ML models' block-bootstrap intervals for mean trade P&L cross zero, and U05's sample is too small for an inferential claim. These are implementation-specific findings, not proof that the original papers or all variants are unprofitable.

Phase 83's 18 preregistered defined-risk candidate/horizon variants all failed the candidate gate (0/18). Phase 92 did not establish strategy profitability: a very small 2024 IV forecast gain failed 2023 replication, while the combined synthetic-forward proxy/OI feature block worsened absolute next-15-minute spot-movement prediction in the fixed 2022 sample. Phases 95/96 are forecasting and underlying index screens; they do not establish options P&L.

## 1. Research questions and decision framework

- Which existing evidence is most credible after costs, coverage and temporal checks?
- Which candidate should get the next finite validation allocation?
- What stops the current research from promoting a strategy?

The scorecard ranks **next-action priority by evidence grade**, not universal returns. It deliberately does not calculate a single cross-study metric because date windows, trade objects, capital, risk units and fill assumptions differ.

## 2. Consolidated scorecard

See [strategy_evidence_scorecard.csv](strategy_evidence_scorecard.csv). “Stress net” is only compared within the same source's own scenario model.

| Priority | Method | Committed numerical evidence | Evidence status | Decision |
|---:|---|---|---|---|
| 1 | TT-03 dynamic-N V5 | 200/201 trades; 99.50% coverage; ₹89,669.15 base net; ₹82,074.11 +50% friction; ₹60,834.11 ₹20/order +50%; only 3 HOLD trades | Positive costed baseline but tiny HOLD split | Revalidate first only |
| 2 | Phase-32 stateful control | 206 trades; +₹63,672.58 net; PF 1.203; max DD ₹61,960.87 | Accepted historical comparator; reproduction discrepancy; overlays fail paired comparison | Keep as comparator; no fresh promotion |
| 3 | TT-05 | 62 partial-window trades; +₹17,098.15 base, +₹9,850.12 ₹20/order +50%; historical HOLD −₹40,244.68 | Temporal instability; two target option dates missing | No promotion; do not retune |
| 4 | TT-04 | 62 partial-window trades; +₹13,271.51 base, +₹5,897.66 ₹20/order +50%; historical HOLD −₹6,456.29 | Temporal instability; two target option dates missing | No promotion; do not retune |
| 5 | TT-02 | 13 partial trades; −₹1,341.12 base, −₹6,476.31 ₹20/order +50% | Negative in all four registered cases | Not supported |
| 6 | U02 RF/XGBoost/LSTM5 | 49/53/62 trades; net about −₹99,991 to −₹99,982 per ₹100,000 initial account | Severe simulated account depletion; OHLC proxy and missing fills | Reject tested implementations |
| 7 | U05 monthly seasonality proxy | 7 completed trades from 56 opportunities; net −₹283,669.90 on ₹300,000 | Strong negative signal, n<20; modern-sample proxy | Do not promote; insufficient to disprove paper |
| 8 | Phase 83 static defined-risk structures | 0 of 18 candidate/window gates passed | Registered gate failure; 11,163 comparisons / 238 expiry clusters | Close that frozen universe |
| 9 | VIX/IV/OI/synthetic-forward predictors | 2024 IV gain tiny, not replicated in 2023; 2022 combined proxy/OI block worsened MAE | Predictor association only, not strategy P&L | No strategy conclusion |
| 10 | Forecast/SMA/EMA screens | Phase 96 total-return sensitivities below buy-and-hold; Phase 95 forecast gains depend on target and are not options trading | Benchmark/proxy evidence only | Do not label as profitable options strategies |

The ordering after the top candidates is for triage only. Rows below TT-05 are different categories; no pairwise total-P&L comparison is implied.

## 3. Methodology and statistical analysis

- Preserved source-specific date windows, candidate rules, capital and cost scenario definitions.
- Reviewed chronological DEV/VAL/HOLD splits and temporal reconciliation where available.
- Retained the Phase 77 expiry-cluster bootstrap interpretation: with only 13–14 clusters, bootstrap fractions/intervals remain unstable and descriptive, not future probabilities.
- Retained the Phase 38 paired expiry-block comparison: 93 shared expiry blocks, all model-selector mean deltas negative, every CI crosses zero.
- Retained Phase 101 circular moving-block bootstrap for U02 (3,000 resamples; five-trade blocks). All model mean-trade net P&L intervals cross zero. U05 with seven trades did not meet the n≥20 bootstrap rule.
- No additional inferential test was run in this synthesis. This avoids double-using holdout data and prevents spurious significance from ranking many strategies.

## 4. Candidate gate and recommended next step

TT-03 is selected **only** for a new, separately preregistered independent validation because it has the strongest combination of cost stress retention and audited coverage among the reviewed current candidates. The 3-trade HOLD split means it must not pass automatically.

The next phase should proceed only if the repository can meet the following gates without repeating unchanged data-source probes:

1. **Independent sample:** acquire a materially new, authorized exact-contract sample with enough independent expiry/event clusters; protect it from all strategy selection and tuning.
2. **Data/rights:** verify automated-use, retention and allowed derived-result publication, as well as exact expiry/strike/right/time identity.
3. **Execution:** incorporate realistic bid/ask or conservative executable-price proxy, liquidity/depth/latency sensitivity, date-effective lot sizes, Paytm Money brokerage, statutory levies and slippage.
4. **Preregistration:** freeze TT-03 rule, primary endpoint, sample and exclusion handling, cluster bootstrap, multiplicity family, drawdown/ruin guardrails and failure boundary before the test.
5. **Promotion criteria:** require positive net results through registered cost stresses, adequate independent-cluster coverage, no unresolved accounting errors, acceptable equity-normalized drawdown, and uncertainty evidence inconsistent with no edge. If any gate fails, stop and log the reason; do not tune the holdout.

This phase does not initiate that numerical validation because this ranking workflow is limited to evidence reconciliation. The separate next phase will need its own plan and source gates.

## 5. Strengths and limitations

**Strengths:** committed source artifacts, explicit costs and stress scenarios, audit of contradictory time splits, paper-method status separation, no new holdout access, no blended arbitrary score, machine-readable scorecard and automated invariant checks.

**Limitations:** several source strategies use minute OHLC/LTP rather than executable quote/depth data; Paytm Money costs are simulated rather than verified contract-note fees; cross-phase sample windows and accounting differ; TT-03 hold is only three trades; TT-04/TT-05 lack two target sessions; U05 has seven completed trades; and one canonical control reconstruction mismatch remains. This is a synthesis, not independent raw-data replication.

## 6. Final conclusion

The evidence supports **one next candidate for further independent testing (TT-03 dynamic-N V5)**, but **zero strategies validated for live deployment**. The next finite experiment should focus on TT-03 only if genuinely new authorized exact-contract data and realistic execution assumptions pass preflight. TT-04/TT-05 should not be tuned against their contradictory hold results; U02/U05 paper proxies should not be promoted; and Phase 83's closed candidate universe should not be repeatedly searched. If no authorized independent sample becomes available, the scientifically correct endpoint is a documented no-go rather than an endless backtest loop.

## 7. Reproducibility and links

- [Phase 50B TT-03 evidence](../phase50b/tt03_dynamic_n_replay/summary.json)
- [Phase 38 control status](../../../PHASE38_STATUS.md)
- [Phase 51-3 partial-window report](../phase51/available_oos/PHASE51_3_AVAILABLE_OOS_REPORT.md)
- [Phase 77 cluster inference](../phase77_partial_oos_inference/report.md)
- [Phase 78 temporal stability](../phase78_temporal_stability/report.md)
- [Phase 79 final evidence gate](../phase79_final_evidence_gate/report.md)
- [Phase 83 candidate gate](../phase83_final_manuscript/supplementary_candidate_gate.csv)
- [Phase 92 factor synthesis](../phase92/CROSS_PHASE_FACTOR_SYNTHESIS.md)
- [Phase 95 forecast report](../phase95/REPORT.md)
- [Phase 96 indicator report](../phase96/REPORT.md)
- [Phase 100 manuscript](../phase100/MANUSCRIPT.md)
- [Phase 101 options report](../phase101_pdf_strategy_tests/PHASE101_REPORT.md)
- [Phase 102 validation script](../../research/phase102/final_strategy_ranking.py)
