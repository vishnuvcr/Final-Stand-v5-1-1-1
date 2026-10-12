# Phase 109 semantic remediation error/limitation log

## 2026-10-12
- **E109-S01 — Core substitution:** v1 substring mapping could score a distinct registered strategy as ordinary price momentum. Corrective action: exact allowlist; unsupported strategies blocked.
- **E109-S02 — Confirmation provenance:** v1 mapped cross-asset confirmation to the other domestic index. Corrective action: block unimplemented confirmation families.
- **E109-S03 — Undefined volatility target:** v1 computed realised-volatility state without enforcing a preregistered target-state dimension. Corrective action: block that regime.
- **E109-S04 — Rule semantics:** EMA slope was return momentum and EMA crossover was spread sign, not a crossing event. Corrective action: explicit implementations with regression fixtures.
- **E109-S05 — Missing rule/input implementations:** futures basis, synthetic parity, IV/skew/Greeks, VWAP, opening-gap, volume, global, news/event, breadth and DII/FII families remain blocked; do not count as successful tests.
- **E109-S06 — Execution evidence:** EOD OHLC, even with positive volume, does not verify fills, spread, depth, latency or partial fills; user-specific Paytm Money contract-note charges remain unverified.
- **Parent sweep checkpoint:** at resume, the v1 cursor had completed 4,000 configurations / 96,000 cost rows and had 590,000 eligible configurations remaining. This is a count checkpoint only.
- No secret or authenticated raw response was copied to public logs.

## 2026-10-12 08:02 UTC — v2 evaluation workflow failure
- Run 38221168260 failed before a verified shard checkpoint. Inspect the Actions job log; do not infer performance results.

## 2026-10-12 — Root cause for first v2 evaluator failure

- Run [38221168260](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221168260) passed compilation and all 26 offline tests and resolved `start_config=0`, then failed in `load_market()` with `Private NSE data cache is missing; run the official NSE acquisition workflow first.`
- Cause: GitHub Actions caches are branch-scoped for this pipeline; the new remediation branch did not have the parent's private source archive cache. No strategy configuration was scored and no v2 metrics were emitted.
- Correction: enabled the official NSE acquisition workflow for the remediation branch, allowed safe aggregate report publication there, and added a cost-window/source-gated evaluator dispatch after acquisition completes. Run [38221333273](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221333273) is running. If row/lot-size/index-context gates fail, the evaluator must remain blocked rather than use partial rows.
- This is a source-cache setup issue, not evidence that the strategies won or lost. No raw response or token was published.
