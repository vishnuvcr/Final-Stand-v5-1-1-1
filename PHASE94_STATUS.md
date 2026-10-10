# Phase 94 Status — Paper Method Replication Program

**Updated:** 2026-10-10  
**Branch:** `phase-94-paper-method-replication-program`  
**Status:** REGISTERED; execution phases defined; empirical replication NOT YET RUN in Phase 94  
**Promotion:** NONE

## Completed in this step
- Defined the research question, preregistered hypotheses, common methodology, statistical gates and finite stop boundary.
- Registered all 14 uploaded PDFs and 66 registered method/strategy rows across U01–U14, including the U04 SGD regressor and U07/U05 payoff structures.
- Split execution into five bounded downstream study phases plus this registry phase and final synthesis.
- Recorded why Phase 93's literature audit must not be mistaken for backtesting.
- Preserved prior negative/inconclusive/data-blocked results and sealed-holdout rule.

## Current outcomes
- Literature audit: 14/14 sources mapped in Phase 93.
- Empirical reproductions newly run by Phase 94: **0**.
- Paper-derived methods with completed independent replication verified by this phase: **0 newly verified**.
- Existing relevant evidence: Phase 66 CCI proxy reconstruction had zero completed trades and no estimable profitability; Phases 89–92 tested a different, tightly bounded IV/synthetic-proxy/OI predictor line; these results must not be extrapolated to every uploaded-paper model.
- Strategy promotion: NONE.

## Next phase
Phase 95: daily forecast model replication. Implement common chronological data/metric scaffolding, exact paper metric reconstruction where identifiable, naive persistence baselines, model families and aligned test dates. Any missing source inputs (historical FII/DII, FX, PCR, VIX, point-in-time news) are separately flagged; price-only ablations are not represented as full multimodal replications.

## Stop / quality gates
No positive result is assumed. No hidden-data access. No forced sample shortening, random shuffle split, leakage, synthetic fills, or rerun of unchanged CCI rules without better authorized data. Full costed option P&L is blocked until exact historical contract/entry/exit data and legally usable sources pass validation.

## Records
- [Research plan](PHASE94_RESEARCH_PLAN.md)
- [Error log](PHASE94_ERROR_LOG.md)
- [Research/decision log](PHASE94_RESEARCH_LOG.md)
- [Auditable chat/decision log](PHASE94_CHAT_LOG.md)
- [Narrative method register](results/phase94/PAPER_METHOD_REGISTER.md)
- [CSV registry](results/phase94/PAPER_METHOD_REGISTER.csv)
- [Validation workflow](.github/workflows/phase94-literature-replication-registry.yml)
