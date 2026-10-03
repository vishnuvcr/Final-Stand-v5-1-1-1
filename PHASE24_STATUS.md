# Phase 24 Status

**Status:** registered / implementation

**Control:** Phase-20 canonical dynamic-n strategy.

**Objective:** test a targeted entry-only reversal trigger using the fixed Phase-23 loss-risk and reverse-superiority scores.

## Current state

- [x] Phase-23 results reviewed before starting.
- [x] New branch created from Phase 23.
- [x] Research question registered.
- [x] Threshold grid registered.
- [x] Training/OOS promotion gate registered.
- [x] Reversal engine implemented.
- [ ] Automated workflow execution
- [ ] Training selection
- [ ] Validation
- [ ] 2026 holdout
- [ ] Statistical analysis
- [ ] Conclusion
- [ ] Strategy decision

## Non-negotiable controls

- Exact 190-trade canonical universe.
- Same execution cost model as Phase 20/23.
- No post-entry features.
- No new features after seeing results.
- No holdout tuning.
- Phase 20 remains the canonical comparator unless the promotion gate passes.
