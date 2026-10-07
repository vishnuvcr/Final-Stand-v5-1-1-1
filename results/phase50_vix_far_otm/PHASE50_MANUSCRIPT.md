# Phase 50 Manuscript — VIX × Far-OTM Tail Geometry

## Research question

Do genuinely far-out-of-the-money strike distances improve VIX-conditioned NIFTY option strategies, particularly in HIGH/RISING/SPIKE VIX regimes, relative to the near-ATM geometries already tested?

## Methods

The preregistered study evaluated nine executable defined-risk strategy families across LOW, NORMAL, HIGH, RISING, FALLING, SPIKE and HIGH_RISING VIX labels and tail distances of 2, 3, 4, 5, 6, 8, 10 and 12 listed strike steps. Development used 2021–2023, validation 2024–2025 and a protected 2026 holdout. The execution model used historical NIFTY lot sizes, ₹10/order brokerage, date-aware statutory/exchange charges, one adverse ₹0.05 option tick per leg and +50% monetary-cost stress. Missing farther strikes were never replaced by nearer strikes.

## Primary result

No confirmatory candidate survived the registered development gate. HIGH VIX had only six development opportunities under the fixed 10:00 IST / four-trading-session control, below the minimum observation requirement. The gate was not weakened.

## Sparse-HIGH exploratory result

Five fixed HIGH-VIX cells were carried forward without mutation.

Development leaders:
- Put BWB distance 3: +₹13,253.63 net; +₹12,950.45 stressed; 6 trades.
- Put BWB distance 2: +₹12,751.78 net; +₹12,436.42 stressed; 6 trades.
- Iron Condor distance 2: +₹10,608.03 net; +₹10,199.55 stressed; 6 trades.
- Iron Condor distance 3: +₹10,439.44 net; +₹10,046.67 stressed; 6 trades.
- Put BWB distance 4: +₹9,803.78 net; +₹9,510.67 stressed; 6 trades.

These development figures are too sparse to establish an edge.

## Out-of-sample diagnostics

The 2024–2025 validation diagnostic contained only three trades per fixed HIGH-VIX candidate:
- Put BWB distance 2: +₹696.52 net; +₹525.40 stressed.
- Put BWB distance 3: +₹253.49 net; +₹88.36 stressed.
- Put BWB distance 4: −₹134.14 net; −₹293.72 stressed.
- Iron Condor distance 2: −₹3,432.40 net; −₹3,693.60 stressed.
- Iron Condor distance 3: −₹4,246.90 net; −₹4,497.85 stressed.

The protected 2026 holdout contained four trades per candidate:
- Put BWB distance 2: +₹5,088.84 net; +₹4,768.39 stressed; 75% wins.
- Put BWB distance 3: +₹7,661.54 net; +₹7,355.06 stressed; 75% wins.
- Put BWB distance 4: +₹9,814.49 net; +₹9,521.73 stressed; 100% wins.
- Iron Condor distance 2: −₹4,982.47 net; −₹5,440.83 stressed; 0% wins.
- Iron Condor distance 3: −₹5,482.72 net; −₹5,914.95 stressed; 0% wins.

The holdout results are descriptive only because the candidates did not clear the confirmatory development/validation gate.

## Conclusion

Phase 50 does not disprove high-VIX strategies. It demonstrates that, within the present exact-quote dataset and preregistered design, HIGH-VIX opportunities are too sparse for a statistically defensible promotion decision. The most interesting unresolved hypothesis is a far-OTM Put BWB, but it needs an independently powered prospective validation study rather than further tuning inside Phase 50.

Phase 50 closes with **NO PROMOTION**. Phase 50B continues with the user's previously developed strategies and the seven supplied Tradetron strategy lineages.