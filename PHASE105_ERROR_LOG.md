# Phase 105 Error and Limitation Log

## Known limitations at registration

- The sample covers one already-inspected 30-calendar-day window, not a fresh independent test and not all regimes.
- Daily OHLC are bar marks, not bid/ask quotes, book depth or verified fills. The registered slippage values are assumed adverse-price sensitivities, not estimated spreads.
- Paytm Money account-specific brokerage and contract notes are unverified; the ₹10/₹15/₹20 per-order values are scenario assumptions.
- Fees are estimates from Phase 104's date-effective model; exact contract-note treatment of IPFT/GST and user-specific charges is not independently reconciled.
- A daily total-volume field does not establish executable quantity at the open or close. Zero-volume/invalid target-session bars will be counted as exclusions, not assumed fills.
- The short sample cannot support a live-trading recommendation; all statistics are exploratory.

## Runtime errors and corrections

No run-time error has been observed yet. The recorder will append specific failed tests, source/schema errors, accounting mismatches and corrective actions here. No failed attempt will be treated as evidence.
