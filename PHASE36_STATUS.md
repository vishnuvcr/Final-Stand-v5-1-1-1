# Phase 36 Status — Independent Per-Trade Direction Selector Overlay

## Current state
INITIALIZED — NUMERICAL EXECUTION PENDING

## Core interpretation locked
Phase 32 used prior trade P&L:
- win -> retain direction;
- loss -> flip;
- zero -> retain.

Phase 36 removes that dependency.

For every new entry, the selector is evaluated independently. The previous trade's status, P&L and direction cannot influence the next direction.

## Branch
phase-36-independent-direction-selector-overlay

## Base
Phase-32 accepted engine revision f89e1e5574aa26b69288ae93b9cf180bf9882242.

## Registered selectors
- OTM678_FRESH
- OTM789_FRESH
- CATBOOST
- DART
- WAVELET_TREE
- OOF_STACK
- MARKOV_REGIME_TREE

## Cached selector source
data/phase36_selector_predictions.csv contains the accepted Phase-35 event-level model probabilities used by the five model selectors.

## Evidence policy
No failed run will be used as numerical evidence. Every implementation error must be appended to ERROR_LOG.md, and the status is updated after each accepted workflow step.

## Current result
Not yet run.


## Step 1 — numerical execution audit
- Primary workflow run #1: 37427528243.
- CATBOOST, WAVELET_TREE and OOF_STACK reached the numerical loop and then failed during final skip-ledger DataFrame construction.
- No numerical output from failed jobs is accepted as evidence.
- Root cause: mixed skip-record widths: expiry-level records had 3 fields while entry-level records had 4 fields after expiry prefixing.
- Correction registered: normalize all skip records to [expiry, timestamp, reason, detail] before DataFrame creation.
- Remaining selector jobs were still running when the common error was identified; their output will not be accepted unless their complete artifacts pass the same audit.
