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
