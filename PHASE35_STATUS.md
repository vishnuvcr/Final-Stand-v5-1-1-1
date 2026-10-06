# Phase 35 Status — Advanced Tree and Adaptive Prediction Search

## Current state
**LITERATURE/RESEARCH DESIGN COMPLETE — NUMERICAL TESTING NOT STARTED**

### Why this phase exists
Phase 34 showed that tree-based models are currently the most promising model family. Phase 35 therefore keeps trees central instead of expanding generic deep-learning architectures.

### Literature search complete
Reviewed:
- LightGBM
- CatBoost
- DART
- NGBoost
- BART
- quantile boosting
- EMD/CEEMDAN/VMD + tree models
- wavelet + tree models
- OOF stacking
- forecast pooling/winsorization
- adaptive rolling trees and dynamic ensemble selection
- score-driven Markov-switching NIFTY volatility models
- probability calibration
- temporal conformal prediction

### Numerical evidence
None from Phase 35 has been accepted.

### Proposed numerical order
1. LightGBM + CatBoost + DART.
2. NGBoost + quantile tree forecasts.
3. BART.
4. Decomposition + tree features.
5. Adaptive/rolling tree models.
6. Leakage-safe OOF stacking.
7. Regime-gated tree ensemble.
8. Calibration/conformal diagnostics.
9. Final decision and stop.

### Canonical control
Phase 20 remains canonical.
Phase 34 remains the immediate prediction-model control.
No new model is promoted from literature alone.
