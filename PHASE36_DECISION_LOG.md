# Phase 36 Decision Log — Independent Direction Selector Overlay

## User requirement
The previous trade's status, P&L, win/loss state and prior direction must not determine the next trade's direction. A new direction decision is made before each eligible trade; all other rules remain frozen.

## Registered treatments
OTM678_FRESH, OTM789_FRESH, CATBOOST, DART, WAVELET_TREE, OOF_STACK, MARKOV_REGIME_TREE.

## Control
Phase-32 stateful direction control:
- win -> retain direction
- loss -> flip direction
- zero -> retain direction

## Independence implementation
The Phase-36 direction-selection function does not receive prior trade P&L, prior trade result, prior direction or cumulative strategy P&L. The chronological cursor only prevents overlap and enforces re-entry after the realized exit.

## Evidence history
- Run #1: 37427528243, rejected because audit-row widths were inconsistent.
- Run #2: 37427816293, successful after the audit fix; superseded by later final evidence.
- Run #3: 37428195471, successful and published; fresh-selector evidence later superseded because duplicate quote rows caused eight expiry-level parser skips.
- Run #4: 37428502722, final corrected run; all seven selector jobs and artifact publication succeeded.

## Final decision
The independent-direction overlay is rejected for promotion. Every selector was net negative over the primary window and every selector was negative in the 2026 holdout. The stateful control outperformed all selectors.


## Final reproducibility checkpoint
Run #18 (37429748933) reproduced all seven numerical selector jobs successfully and the rebase-safe publication job succeeded. No change to the Phase-36 decision.
