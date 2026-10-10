# Phase 56 — exact prior-minute OI source diagnosis

**Source coverage diagnosis only; no P&L or strategy selection.**

- Dataset revision: `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`
- Blocked configuration-event rows: 100
- Blocked leg references: 220
- Unique contract-time keys: 60
- Reference reconciliation: 220

## Exact source classifications

| Classification | Contract-time keys |
|---|---:|
| ZERO_OI | 60 |

## Source partitions

| Expiry | SHA-256 | Rows after exact dedup | Exact duplicates removed |
|---|---|---:|---:|
| 2025-03-13 | `8118362cc9e58b646ac98cdd7eaf59675b995ba907a07cba8819b477fcc84f61` | 341673 | 0 |
| 2025-07-31 | `64572ceb2a40e1cb45b7b688e6041e724ae034521ed82cfbd05d6b1a1c24941f` | 370959 | 0 |
| 2025-12-30 | `5ed78461988ce2d90d56aa54afa032a72c7889cbfed73d8f7d8b2239ff580541` | 270118 | 4585 |

## Interpretation

The classification is based on exact expiry, timestamp, option type and strike. No nearest-bar fallback, interpolation, or imputation is allowed.
The source OI values are checked independently against the saved pilot payload. A numeric zero is not silently equated with a missing row.
The fixed OI >= 100 gate remains unchanged. No P&L, holdout, strategy ranking, or promotion was performed.
