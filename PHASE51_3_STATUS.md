# Phase 51-3 Status

**State:** SOURCE-FAITHFUL RETRY IN PROGRESS — orchestrator run 37882057283 uses the hardened recursive spot-source discovery.

The prior green workflow run [37879953815](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37879953815) was rejected after self-audit because the inherited engines used the rejected Phase-43 options source and stale expiry registry. No P&L from that run is accepted.

## Correction implemented

A new `research/phase51_3_primary_source_adapter.py` now injects, without changing strategy logic:

- frozen RISSIN NIFTY 1-minute options: `rissin/nse-options-intraday / upstox_intraday/NIFTY/NIFTY_2026.parquet`;
- expected SHA-256 `bae9943b2fa99ee9c1214fb7c695b84f9f661a050a5cd04d9c5c2ffc7bc59f73`;
- expected byte size 394,805,617;
- NIFTY 1-minute spot from the previously validated `technovusin/nifty50-historical-data` source;
- expiry universe derived directly from observed NIFTY 1-minute rows in the primary options file.

The adapter maps only the existing canonical fields used by the frozen engines. It does not synthesize, interpolate, forward-fill, or alter option prices.

The main orchestrator now caches the validated spot repository and passes its path to the adapter. It also audits the source manifest before accepting results.

## Coverage protection

The diagnostic interval remains 2026-04-21 through 2026-07-21. The missing 2026-07-28 and 2026-08-04 blocks remain outside this partial interval and unresolved for the final Phase-51 window.

The candidate gate remains >=95% completed candidate executions and zero row-level data errors. In addition, the next run must show source-faithful expiry coverage and a trade/evidence span consistent with the declared window; a high local coverage percentage cannot rescue an incomplete candidate universe.

## Current evidence

**Accepted Phase-51-3 P&L: NONE.**

No statistical inference, tuning, ranking or live promotion is permitted until the corrected replay passes the source, candidate, coverage and data-error gates.
