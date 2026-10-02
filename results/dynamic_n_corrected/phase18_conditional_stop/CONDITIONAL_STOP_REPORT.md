# Phase 18 Conditional Stop Refinement

Selected by development only: **mfe_cut_1330_mfe1_c1**

Development:
- net uplift: ₹8,907.46
- winner affected: 0
- loss reduction: ₹9,512.07

Validation:
- net uplift: ₹3,067.43
- winner affected: 0
- loss reduction: ₹17,867.69

Full:
- net uplift: ₹11,974.88
- winner affected: 0
- loss reduction: ₹27,379.76
- losses eliminated: 0

Interpretation: this refinement tests whether expiry-day negative MTM should be stopped only when the trade has also failed to generate sufficient earlier MFE, reducing the chance of cutting late-recovering trades.
