# Phase 59 status — public option-data coverage audit

**Overall:** ACTIVE — metadata-only public-source triage; no download, purchase or strategy test.

- **Branch:** `phase-59-public-option-data-coverage-audit`
- **Parent:** Phase 52–58 canonical data/coverage work; Phase 58 found no accepted free automated historical quote/depth source.
- **Source candidates:** 10 metadata entries frozen in `research/phase59/source_registry.json`.
- **Key gate:** exact contract/time coverage + required OI/quotes + permitted automation must all be verified; public availability is not a license grant.
- **Frozen:** Phase 52 event universe, OI minimum, thresholds, costs, splits and holdout.
- **Next:** run registry validator and tests; publish report and close if no candidate satisfies the hard requirements.

## Current candidate-level finding

- `rissin/nse-options-intraday` reports NaN OI on its intraday rows, so it cannot repair prior-minute OI.
- `artist-23/nifty-options-data` has an OI column but lacks a visible actual-expiry field and a dataset card/license grant, so contract matching/reuse rights are not established.
- `optionsdata.shop` advertises minute OHLC/OI but no bid/ask columns and is a commercial follow-up only.
- `TickBytes` and `OptionVault` advertise L1/L2 data but the full archives require licensing and exact target coverage is not verified.
- Status remains NO-GO until automated validation confirms the registry and report.

