# Phase 103 Research Log

## 2026-10-11 — Initialization and preregistration

- Opened isolated branch `phase-103-novel-intraday-strategy-discovery` from the completed Phase 102 branch.
- Previous tests already covered generic indicators, VIX-stratified static structures and many direction-selection models. This phase registers three different rule/structure combinations based on opening-range continuation, failed-breakout reclaim, and low-range/low-VIX short-premium entry.
- Fixed all signal windows, strike widths, stops, fill handling, cost scenarios, development/validation split and inference before inspecting Phase 103 outcomes.
- Intended sample is 2024 development / 2025 validation. 2026 option data stay excluded.
- Existing source notes show point-in-time FII/DII values absent throughout the earlier 2024–2025 feature validation sample; the primary rules therefore do not depend on missing flows. FII/DII/news source coverage will be audited and reported. No unavailable Greeks, futures, bid/ask or depth values will be invented.
- Next: implement replay and regression tests, then let the phase workflow download only pinned data through the existing Hugging Face cache.


## Replay completed — run 38084107201

- Source revision pinned to 3eacf762d401efd9a08e804592fa7882b354c4a2; no 2026 option data loaded.
- Output artifacts and source/cost/coverage audit were generated. Validation status: PASS.
- Missing exits remain non-estimable, and conclusions apply only to this frozen sample/cost model.


## Replay completed — run 38084876846

- Source revision pinned to 3eacf762d401efd9a08e804592fa7882b354c4a2; no 2026 option data loaded.
- Output artifacts and source/cost/coverage audit were generated. Validation status: PASS.
- Missing exits remain non-estimable, and conclusions apply only to this frozen sample/cost model.
