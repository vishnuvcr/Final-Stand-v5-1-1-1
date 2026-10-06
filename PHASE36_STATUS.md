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
Model-selector treatments are reproducibly complete and net-negative on the primary sample. OTM678_FRESH and OTM789_FRESH are undergoing a corrective rerun because eight expiry files were skipped by a duplicate-quote parsing exception in run #3. No final phase decision is made until the corrected fresh-selector run completes.


## Step 1 — numerical execution audit
- Primary workflow run #1: 37427528243.
- CATBOOST, WAVELET_TREE and OOF_STACK reached the numerical loop and then failed during final skip-ledger DataFrame construction.
- No numerical output from failed jobs is accepted as evidence.
- Root cause: mixed skip-record widths: expiry-level records had 3 fields while entry-level records had 4 fields after expiry prefixing.
- Correction registered: normalize all skip records to [expiry, timestamp, reason, detail] before DataFrame creation.
- Remaining selector jobs were still running when the common error was identified; their output will not be accepted unless their complete artifacts pass the same audit.


## Step 2 — fresh-selector audit
- Run #3 (37428195471) reproduced all seven treatments successfully at the workflow level and persisted artifacts.
- CATBOOST, DART, WAVELET_TREE, OOF_STACK and MARKOV_REGIME_TREE artifacts are accepted evidence.
- OTM678_FRESH and OTM789_FRESH had eight expiry-level exceptions caused by duplicate strike rows producing a Pandas Series where a scalar premium was expected.
- Correction: collapse duplicate same-timestamp strike rows deterministically using the last observed close per option type/strike.
- The fresh-selector results from run #3 are non-final and will be replaced by the corrected rerun.
