# Phase 40 Status — Ensemble Direction Selection with VIX

**COMPLETE — NO PROMOTION**

Branch: `phase-40-ensemble-direction-models`

## Research question
Can combinations of previously tested NIFTY direction selectors, conditioned by India VIX regime, outperform the canonical stateful Continuous Delta 6x6 strategy after realistic execution costs?

## Registered universe
- 6 experts: CATBOOST, DART, WAVELET_TREE, OOF_STACK, MARKOV_REGIME_TREE, India VIX.
- 63 non-empty subsets.
- 4 fixed aggregation rules.
- 7 VIX modes.
- **1,764 declared candidates**.
- **306 unique validation direction policies** after expiry-signal deduplication.
- **10 unique policies** frozen for holdout.

## Phase results

### Step 1 — Data/expert audit — COMPLETE
India VIX was point-in-time aligned and cached in `data/phase40_vix/india_vix.csv`.
Development-only thresholds:
- absolute VIX return q67: 0.03988018
- VIX level q33: 14.7474
- VIX level q67: 20.4300

### Step 2 — Exhaustive grid — COMPLETE
All 1,764 candidates completed successfully.
The strongest grid regime was **HIGH VIX**:
- 252 candidates;
- all 252 positive versus the common-expiry control;
- best validation uplift: **₹21,262.83**.

OFF and LOW modes had no positive validation candidates in the grid-level comparison.

### Step 3 — Validation selection — COMPLETE
The primary frozen policy was:
**Candidate 3 — CATBOOST + HIGH VIX gate + canonical fallback.**

Fixed/sequential validation:
- net P&L: **₹97,533.94**
- frozen control: **₹76,841.96**
- uplift: **₹20,691.98**
- mean uplift: **₹283.45/expiry**
- win rate by trade: approximately **70%** in the fixed-opportunity screen
- exact sequential sign-flip p-value: **0.2185**

### Step 4 — Fixed-opportunity statistical inference — COMPLETE
10,000 paired expiry bootstrap/sign-flip resamples were applied to the frozen top 10.
Candidate 3 holdout:
- net: **₹12,797.11**
- control: **-₹275.65**
- uplift: **₹13,072.75**
- mean uplift: **₹653.64/expiry**
- 95% CI for mean uplift: **approximately -₹183 to ₹2,144**
- one-sided p: **0.4006**

### Step 5 — Exact stateful sequential replay — COMPLETE
The top 10 were replayed through the canonical Phase-32 chronological state machine on the exact 93 prediction-covered expiry blocks. Direction state, delta exits, lot sizes, one-tick adverse slippage, brokerage and statutory charges were preserved.

Primary Candidate 3:
- validation uplift: **₹20,691.98**
- holdout uplift: **₹13,072.75**
- validation p-value: **0.2185**
- holdout p-value: **0.4006**

No candidate had a statistically significant validation incremental advantage at the 5% level.

### Step 6 — VIX routing robustness — COMPLETE
The grid-level and frozen-top-10 results both point to regime conditioning as the useful feature:
- HIGH VIX produced the strongest validation cluster.
- FALLING VIX policies were often positive in validation but did not carry into holdout.
- A VIX-only RISING policy (Candidate 873) had the best holdout uplift among the frozen top 10 (**₹14,294.32**), but selecting it after seeing holdout would violate the pre-registered selection rule.

### Step 7 — Final statistical/promotion gate — COMPLETE
No policy passed the required combination of:
- positive validation uplift;
- statistically credible incremental effect;
- untouched holdout confirmation;
- robustness under cost stress;
- protection against holdout re-selection.

### Step 8 — Manuscript/closeout — COMPLETE

Final corrected workflow run **37458310284** completed successfully, including verification and persistence. The accepted sequential artifact uses the exact 93 prediction-covered expiry blocks.
- [Phase 40 manuscript](PHASE40_MANUSCRIPT.md)
- [Research plan](PHASE40_RESEARCH_PLAN.md)
- [Pre-registration](PHASE40_PRE_REGISTRATION.md)
- [Literature review](PHASE40_LITERATURE_REVIEW.md)
- [Exhaustive grid](results/phase40_ensemble/grid_validation.csv)
- [Inference](results/phase40_ensemble/inference_top10.csv)
- [Sequential replay](results/phase40_ensemble/sequential_top10.csv)
- [Error log](ERROR_LOG.md)

## Final scientific conclusion

**Phase 40 does not establish a new production trading strategy.**

The most promising hypothesis is:
> CATBOOST direction information appears more useful when activated only during high India VIX conditions, with canonical stateful fallback outside that regime.

However, Candidate 3's untouched holdout incremental effect remains statistically inconclusive:
**+₹13,072.75 point estimate, 95% CI crossing zero, p ≈ 0.4006.**

The correct decision is:

**PROMISING / INCONCLUSIVE — NOT PROMOTED.**

The canonical stateful strategy remains the accepted benchmark. Phase 40 is closed without a production change.
