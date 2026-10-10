# Phase 102 Research Plan — Final Evidence-Based Strategy Ranking

**Branch:** `phase-102-final-strategy-ranking`  
**Parent:** `phase-101-full-pdf-strategy-replication`  
**Mode:** bounded synthesis of already-committed results; no new market data acquisition  
**Decision rule:** do not promote a strategy unless evidence supports positive net expectancy, temporal robustness, feasible execution, sufficient coverage, and independent out-of-sample validation.

## 1. Research questions

1. Which already-tested strategy implementations have the strongest *quality of evidence*, after separating raw net P&L from sample size, temporal stability, uncertainty, coverage and cost assumptions?
2. Which one, if any, merits the next finite validation run before other candidates consume more compute?
3. Which apparently positive outcomes are contradicted by earlier holdout results, and which outcomes are only forecasting/feature evidence rather than strategy P&L?
4. What exact data, execution and statistical gates still prevent a live-use conclusion?

## 2. Aim and objectives

Produce a reproducible ranked evidence register across the canonical stateful control; TT-02/03/04/05; Phase 83 static structures; Phase 92 factor-prediction work; Phase 95 forecasting; Phase 96 moving averages; and Phase 101 paper-derived U02/U05 options proxies.

Objectives:
- retain each experiment's native sample, costs, date range and metric units;
- use broker-aware cost and adverse-friction scenarios where the original run recorded them;
- flag incomplete coverage, very small holdouts, negative historical hold results, and unavailable quote/depth data;
- use committed audit artifacts rather than rerunning or repeatedly probing unchanged sources;
- recommend one next candidate or close the empirical path if no candidate clears all gates;
- publish a report, machine-readable scorecard, validation output, phase status, research log, error log and README links.

## 3. Scope and non-goals

This phase is a synthesis/reconciliation phase. It will **not** download new raw data, access the protected 2026 holdout beyond data already explicitly included in committed reports, alter strategy parameters, combine returns across incompatible samples, claim executable fills from OHLC/LTP, or treat prediction accuracy/expiry-payoff algebra as profitable strategy evidence.

No individual model score will be presented as a universal cross-study return ranking. Samples differ in dates, trade selection, account sizing, capital base, instrument exposure, cost models and drawdown definition.

## 4. Source artifacts to re-check

- Phase 38: `PHASE38_STATUS.md`, `results/phase38_corrected_model_robustness/risk_adjusted_summary.csv`; frozen canonical control and paired selector inference.
- Phase 50B TT-03: `results/phase50b/tt03_dynamic_n_replay/summary.json`, `terminal_decision.json`, `split_summary.csv`.
- Phase 51-3 / 77 / 78 / 79: partial-window costed TT-02/04/05 results, expiry-cluster uncertainty, temporal-stability reconciliation and final data gate.
- Phase 83: `results/phase83_final_manuscript/supplementary_candidate_gate.csv` and performance ledger.
- Phase 92: `results/phase92/CROSS_PHASE_FACTOR_SYNTHESIS.md`.
- Phases 95–100: forecast/indicator screens, paper source/method register, blocked-data decisions, analytical payoff checks and manuscript synthesis.
- Phase 101: `results/phase101_pdf_strategy_tests/PHASE101_REPORT.md`, U02 model summary and U05 summary.

## 5. Evidence grading and ranking procedure

Priority order is *next-action priority*, not a claim that returns from different experiments are directly comparable.

- **Tier A — highest revalidation priority:** positive baseline and named stress scenarios, reasonable data/coverage audit, but a still-material confirmatory blocker.
- **Tier B — retained comparator:** useful benchmark with a documented costed history, but either no incremental method beat it or it has not passed the current independent executable validation gate.
- **Tier C — provisional descriptive result contradicted by time stability:** partial-window net profits cannot outweigh a negative historical hold split.
- **Tier D — tested implementation rejected / serious negative signal:** the specific tested implementation lost money, suffered severe equity depletion, or was negative in every registered cost case.
- **Tier E — not a strategy-P&L result:** data-blocked methods, forecasting metrics, feature association tests and analytical expiry-payoff formulas.

No aggregate composite score is calculated. Reasons: different outcomes, sample windows, capital, data coverage and risk accounting make a numerical single score arbitrary. Ranking is based on explicit evidence gates, not raw P&L alone.

## 6. Mandatory checks

1. All source artifacts exist and parse.
2. TT-03 net values are reconciled to its JSON; coverage and split counts are explicit; note the hold split sample.
3. TT-04/TT-05 partial positive results and Phase 78 historical negative hold results are both retained.
4. TT-02 costed partial results are retained as negative evidence.
5. Phase 38 control and the five rejected overlays remain separate.
6. All Phase 83 registered defined-risk candidate gates remain failed.
7. U02 ending equity reconciles to a severe near-total loss, and U05 remains a seven-trade negative proxy—not exact proof the source paper fails.
8. The Phase 92 factor study is not misreported as executable strategy P&L.
9. No conclusion labels the present evidence as a validated profitable strategy.

## 7. Planned phases and stop rules

- **102-A — artifact ingestion:** read pinned committed summaries only. Stop if artifacts are missing or internally contradictory; log a blocker rather than infer.
- **102-B — ranking and temporal reconciliation:** construct the evidence matrix and action priority list. No parameter tuning.
- **102-C — automated audit:** run Python standard-library validator and tests via GitHub Actions. Fix code/data contract errors and log each actual error.
- **102-D — publication and closeout:** publish scorecard, report, validation, links, root README checkpoint and status/log updates.
- **Finite stop:** Phase 102 closes after checks pass and scorecard/report are published. If a workflow or source inconsistency remains, phase stays blocked until repaired. No endless repeated search loop is permitted.

## 8. Primary outcomes

Primary outcome: number of candidate strategies that pass *all* defined promotion gates (positive net after cost stress; credible temporal stability; adequate event/expiry sample; uncertainty not compatible with no edge; exact contract identity and defensible execution assumptions; no unresolved accounting/coverage blocker).

Secondary outcomes: next-action priority, cost-stressed net results where reported, completed-trade count, coverage, drawdown, and status of missing data/rights.

## 9. Current pre-registered expectation

Based on the committed prior evidence, expected number of promotion-eligible strategies is zero. This is a testable phase expectation, not a predetermined numerical result: the validator may reveal a contradiction, in which case it must record it. A failed evidence gate means “not validated,” not “all strategies are unprofitable.”

## 10. Reproducibility

The standard-library script `research/phase102/final_strategy_ranking.py` reads existing versioned JSON/CSV/Markdown outputs, checks key invariants, and writes `results/phase102/validation.json` when run. Unit tests live in `tests/phase102/`. Workflow `.github/workflows/phase102-final-strategy-ranking.yml` supports both `workflow_dispatch` and pushes to this phase branch. No raw market data is duplicated.
