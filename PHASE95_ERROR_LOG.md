# Phase 95 Error / Limitation Log

## Initialization
No accepted empirical result exists before the first automated run. The runner appends data-block and model-failure errors after execution.

## L95-001 — Common NIFTY data versus source universe
U01 uses 12 companies and other papers use source-specific targets/splits. A NIFTY common dataset is a method-family replication, not exact source replication.

## L95-002 — External historical features
FII/DII, news sentiment, PCR, option Greeks and historical chain data are not guaranteed by the common data feed. These features are not silently substituted with price indicators; their absence is reported separately.

## L95-003 — 2025 test period overlap with later papers
The fixed 2025 test is chronological relative to this runner's train cutoff but may overlap data used in papers published in 2025/2026. It is not necessarily post-publication validation.

## E95-RUNTIME
No run-specific error recorded yet.
