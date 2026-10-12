# Phase 109 family-by-family data-feasibility gate

Generated: 2026-10-12T05:28:34.318673+00:00

**This is an input availability gate, not a backtest.** Family counts and candidate configurations are not performance-tested observations.

| State | Families |
|---|---:|
| BLOCKED_MISSING_INPUTS | 923 |
| INPUTS_PRESENT_EXECUTION_AND_SPLIT_GATES_PENDING | 48 |
| INPUTS_PRESENT_WITH_PROXY_OR_EXECUTION_GATES | 54 |

## Aggregate
- Registered architecture combinations: 1,025.
- Total registered configurations under current grid: 3,719,520.
- Candidate configurations whose declared fields are present (before date, symbol and execution gates): 642,600.
- Data-gated families: 923.
- Families with proxy or execution conditions: 54.
- Families with source fields present but execution/split gates pending: 48.

## Interpretation
- Official NSE EOD index-option archives support exact symbol/expiry/strike/side, OHLC, volume and OI, subject to session coverage and positive-volume filters.
- Dhan historical rolling ATM IV/OI is a feature candidate only; rolling contracts are not fixed-contract entries/exits.
- Futures EOD may support a basis feature after spot/expiry/lot-size checks, not intraday fills.
- India VIX is usable only if official NSE Indices series passes range/schema/time alignment checks.
- Greek-dependent families may use the separately labelled exact-contract Black-Scholes estimates only as model-derived features with explicit r=6.5%/q=0% sensitivity gates; directly observed Greeks and matched IV skew remain unavailable. Global-, FII/DII-, event-, news-, breadth- and corporate-action-dependent families stay blocked until their respective audited sources are present. Never substitute unlabeled or unverified proxies.
- All P&L rows before 2024-10-01 remain blocked under the currently verified transaction-cost model. Earlier price history may serve as indicator warm-up, not as a net-return sample, until an approved pre-October-2024 cost schedule is implemented.

See family_data_feasibility.csv and family_data_feasibility_summary.json for the full list of missing inputs and eligibility decisions.
