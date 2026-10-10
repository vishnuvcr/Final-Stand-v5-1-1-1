# Phase 61 — New-source restart audit

**Decision: NO_GO_NO_NEW_SOURCE_MEETS_RESTART_GATE**

- Candidates reviewed: 5
- Decision counts: `{"FOLLOW_UP_ONLY": 3, "REJECT_FOR_FROZEN_REPLAY": 2}`
- Accepted for sample validation: None
- Mode: public metadata only; no credentials, purchases, downloads or scraping.

| Candidate | Decision | Key blocker |
|---|---|---|
| [MoneyTicks historical options archive](https://moneyticks.com/) | FOLLOW_UP_ONLY | Most promising OHLC/OI candidate, but access/licensing rights and exact sample validation remain unverified; no quote/depth fields established. |
| [DhanHQ expired options historical API](https://dhanhq.co/) | FOLLOW_UP_ONLY | Potential licensed OHLC/OI route, but account access, exact timestamp schema, target coverage and reuse rights are unresolved. |
| [ICICI Direct Breeze historical F&O API](https://api.icicidirect.com/) | FOLLOW_UP_ONLY | Unverified API/data schema and access rights; not enough evidence for acceptance. |
| [BarathGB007 NSE options data collector](https://github.com/BarathGB007/nse-options-data-collector) | REJECT_FOR_FROZEN_REPLAY | A forward collector is not a source for historical target events, and the 15-minute cadence does not guarantee frozen exact timestamps. |
| [Nifty spot/futures/options one-minute dataset 2017–2020](https://zenodo.org/records/10899828) | REJECT_FOR_FROZEN_REPLAY | Period and required OI/quote fields do not meet frozen replay needs. |

## Conclusion

Stop empirical factor/strategy testing. None of the newly surfaced leads has verified data-use rights plus exact target sample/schema evidence.

## Restart action

Obtain written rights/access and a provider-approved exact sample first. Do not create another source-search phase unless a genuinely new lead or authorization arrives.

No P&L, fill quality, statistical inference, strategy ranking or promotion was performed.
