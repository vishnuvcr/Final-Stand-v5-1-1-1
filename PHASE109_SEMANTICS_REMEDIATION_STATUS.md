# Phase 109 semantic remediation status

Updated: 2026-10-12  
Branch: `phase-109-strategy-semantics-remediation`  
State: **CODED; AUTOMATED WORKFLOW VERIFICATION PENDING**  
Promotion: **NONE**

## Remediation
- [x] Inspected Phase 109 plan/status/log/error/chat, evaluator workflow, checkpoint and source audits.
- [x] Created isolated branch to leave the parent sweep untouched.
- [x] Replaced substring-based core mapping with an exact allowlist.
- [x] Changed EMA slope to measure normalized EMA change and EMA crossover to require a sign crossing.
- [x] Blocked unsupported confirmation and unparameterized realised-volatility target regimes.
- [x] Bumped engine to `phase109-eod-engine-v2-semantics` so v1 cursor state is not reused.
- [x] Added semantic regression tests.
- [ ] Dedicated test workflow passes.
- [ ] Corrected evaluator starts at cursor zero and publishes a v2 shard.
- [ ] Reconcile 24 cost rows/config, blockers, cursor and result SHA.
- [ ] Update final statistical report only after validation/holdout/multiple-testing gates.

## Latest checkpoint
<!-- SEMANTICS_LIVE_CHECKPOINT_START -->
V2 Actions results are not yet verified at initial log creation. Inspect GitHub Actions and do not infer profitability from code/test success.
<!-- SEMANTICS_LIVE_CHECKPOINT_END -->

## Links
- [Plan](PHASE109_SEMANTICS_REMEDIATION_PLAN.md)
- [Audit](results/phase109/SEMANTICS_REMEDIATION_AUDIT.md)
- [Semantic tests](research/phase109/test_phase109_strategy_semantics.py)
- [Semantic test workflow](.github/workflows/phase109-implementation-tests.yml)
- [Resumable evaluator workflow](.github/workflows/phase109-evaluate-grid.yml)
