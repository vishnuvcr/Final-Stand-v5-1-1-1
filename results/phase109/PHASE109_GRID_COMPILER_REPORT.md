# Phase 109 Grid Compiler Report

Generated: 2026-10-12T04:16:23.160933+00:00

**State: GRID REGISTERED, NOT EVALUATED. No strategy promoted.**

| Audit item | Result |
|---|---:|
| Registered strategy architecture combinations | 1,025 |
| Exact duplicate fingerprints | 0 |
| Distinct architecture fingerprints | 1,025 |
| Structural one-component-neighbour pairs retained for audit | 4,100 |
| Minimum configurations per family | 1,080 |
| Maximum configurations per family | 19,440 |
| Total family-configuration tuples | 3,719,520 |
| Cost scenarios per tuple | 24 |
| Total cost-adjusted rows in registered universe | 89,268,480 |
| Cost-row shards | 45 |
| Rows per full shard (last shard may be smaller) | 2,000,000 |

## Interpretation

The registry is formed from 41 distinct core signal architectures, five confirmation architectures and five regime gates. Every family has an explicit input list, rule description, stable architecture fingerprint and a long-call/long-put mapping. Exact duplicate fingerprints are rejected. Near-neighbour architectures are reported and preserved for audit; they are not claimed to be statistically independent.

The full Cartesian configuration space applies all applicable lookback, signal-threshold, volatility-lookback, regime-definition, strike, exit and risk-profile values. OI method variants apply only where the registered family requires OI/option-flow input. The 24 declared cost cases combine brokerage ₹10/₹15/₹20 per order, adverse slippage ₹0/₹0.05/₹0.25/₹0.50 per option unit per side, and 1×/1.5× modeled fee multipliers.

**These figures describe registered combinations and shard coverage only.** They do not mean Dhan/NSE/Hugging Face data were fully collected, any tuple was backtested, or a strategy is profitable. Source availability, point-in-time data and untouched out-of-sample validation remain separate gates.

## Reproducibility hashes

- Registry: `7554ceceb9df6a403f409b9877b6ff0b57c9b0bca724e4ee2c8c25799dbdf60d`
- Configuration manifest: `3253d8df32e73d5b66208373d7ca2d9e30fc20f656dbed52776b71fb31f9941a`
- Cost grid: `0dc9f1792ba6b8eeec903577d3cfd83d122aaa36785248313982e7843a00e33f`
- Full manifest: `f5c0439bc9d9b994a4b5b5ca2bc2260e5b26b8346b91335b4eed894ff5cae6cc`
