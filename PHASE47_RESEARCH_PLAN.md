# Phase 47 Research Plan — VIX Source-Strategy Numerical Backtest

## Research question

Do mechanically reconstructable strategies discovered from YouTube/public video sources—especially the user-designated Profit Breakout channel—produce economically robust NIFTY option results conditional on India-VIX state, including both the previously populated LOW/NORMAL states and the currently sparse RISING/HIGH/SPIKE/HIGH_RISING states?

## Self-audit rule

This phase is deliberately staged to reduce avoidable errors:
1. Preflight audit of definitions, source files, expiry linkage, timestamp availability, option-leg availability, lot sizes and fee/slippage functions.
2. Numerical execution only after preflight passes.
3. Artifact audit checks row counts, duplicate trade keys, missing legs, state labels, split boundaries and holdout protection.
4. Statistical audit checks minimum sample sizes, bootstrap/permutation outputs, Holm correction and validation-only candidate freezing.
5. Holdout audit verifies that no holdout result is used in candidate selection or parameter changes.

Any audit failure makes the affected numerical output non-evidence and is logged in ERROR_LOG.md before correction/re-run.

## Source-derived strategy registry

Only mechanically reconstructable candidates are tested in Phase 47.

### S1 — Double Calendar Straddle
A four-leg calendar constructed from a current-month ATM short straddle and next-month ATM long straddle. This is a mechanical proxy for the Calendar/Calendar-Trap family discussed by Profit Breakout and other video sources.
Entry: four trading sessions before the selected monthly NIFTY expiry, 10:00 IST.
Current month: sell ATM CE + ATM PE.
Next month: buy the same ATM strike CE + PE.
Exit: latest complete observation <=15:29 IST on the current-month expiry day.

### S2 — Monthly Wide-Range Hedge
A mechanical reconstruction of the Profit Breakout monthly wide-range hedge described in the indexed transcript: current-month ~30-delta call + put sold, next-month ATM call + put bought.
Entry: first trading session after the preceding monthly expiry, 10:00 IST, for the next monthly expiry cycle.
Short legs: current monthly CE and PE selected nearest |delta|=0.30 using a point-in-time Black-Scholes delta proxy with prior-session India VIX as volatility input.
Long hedge: next monthly CE + PE at the strike where their entry premiums are closest (ATM/parity proxy).
Exit: latest complete observation <=15:29 IST on the current-month expiry day.
Because the source relies on platform greeks that are not stored in the option dataset, the delta rule is explicitly reconstructed and sensitivity-audited rather than claimed to be an exact platform replication.

### S3 — Covered Call 2.0 (Synthetic-Future Proxy)
Profit Breakout describes: buy future, buy ~0.30-delta protective put, sell current-week ~0.30-delta call, sell next-week ~0.30-delta call.
The available cached option dataset has no authoritative futures series in the Phase-45 workflow, so Phase 47 tests an explicitly labelled option-only proxy:
- +ATM CE and -ATM PE at current weekly expiry as the long-future synthetic;
- +0.30-delta protective PE at current expiry;
- -0.30-delta CE at current expiry;
- -0.30-delta CE at next weekly expiry.
This is diagnostic until future-price equivalence is independently verified.

## VIX regime panel

Every candidate is evaluated across: ALL, LOW, NORMAL, FALLING, RISING, HIGH, SPIKE, HIGH_RISING.
No strategy is assumed to belong to only HIGH/RISING VIX. LOW/NORMAL/FALLING remain active opportunity and comparator states.
The VIX state is point-in-time and is computed only from observations strictly before the entry date using the accepted Phase-43/45 expanding-threshold convention.

## Execution model

- Historical NIFTY lot sizes.
- ₹10 Paytm Money F&O brokerage per executed order.
- Date-aware STT, exchange transaction charge, SEBI fee, IPFT, stamp duty and GST.
- One adverse ₹0.05 option tick per leg at entry and exit.
- No forward filling, interpolation or synthetic quote substitution.
- For S3 only, a synthetic position is used because the source strategy requires a future; this is not synthetic price data and is explicitly flagged as a proxy.
- Entry/exit must use actual observed option quotes.

## Statistical design

Development: through 2023-12-31.
Validation: 2024-01-01 through 2025-12-31.
Protected holdout: 2026.

For each strategy × VIX state report: trade count; net P&L; +50% fee/charge stress; mean net/trade; win rate; maximum drawdown; profit factor; active-vs-complement mean difference; 10,000 bootstrap confidence interval; 10,000 permutation/sign-flip style one-sided p-value; Holm-adjusted p-value across the complete Phase-47 strategy×VIX family.

The +50% stress multiplier applies to monetary fee/charge calculations. The existing ₹0.05 adverse tick remains fixed in this implementation; this distinction is explicitly reported to avoid overstating the stress.

## Candidate screen

A validation state is a working candidate only if:
- at least 20 active trades;
- positive validation net;
- positive validation +50% charge stress;
- positive mean active-vs-complement advantage.

Formal promotion additionally requires the registered statistical gate and unchanged 2026 confirmation.

## Stop conditions

Phase 47 closes after all three registered candidates are tested where data permits; validation ranking and statistical inference are complete; frozen validation candidates are confirmed on protected 2026; and source/proxy limitations are documented.
Adaptive management systems, futures-exact implementation of Covered Call 2.0, skew/IV-divergence routers and broader VIX state transitions become separate follow-up phases rather than being added opportunistically.

## Phase-47 closeout amendment

The numerical objective could not be completed with the cached source because multi-expiry entry-time observations are absent for most candidate dates. This is recorded as a data-feasibility result, not evidence that the source-derived strategies fail.

No changed strategy definition is accepted. A follow-up data-bridge phase is required before multi-expiry strategies can be evaluated scientifically.
