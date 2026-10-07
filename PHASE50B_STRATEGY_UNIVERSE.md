# Phase 50B Strategy Universe

## A. Seven supplied Tradetron strategies

| ID | Strategy | User link | Latest resolved account report | Role |
| TT-01 | Dynamic Ratio Reversals | https://tradetron.tech/bt/view/d164b781832c2202116c72af0d6dc76d | https://tradetron.tech/bt/view/0368b504cde88a76136b8fcfb5ad0019 | Primary dynamic-ratio control |
| TT-02 | 0.20/0.10 Delta Calendar Hedge Spread v4 | https://tradetron.tech/bt/view/57d2b9ddc507843ad486a5323316622a | https://tradetron.tech/bt/view/31f7d793641e03d118ffad9c2103a77b | Calendar control |
| TT-03 | Corrected Dynamic-n NIFTY Weekly Options Strategy | https://tradetron.tech/bt/view/79b5f5977342301347e82a8175e9ddf8 | https://tradetron.tech/bt/view/0bc9dbe746525bfffdafb58ed7e4b405 | Ratio candidate |
| TT-04 | Profit Breakout Premium Match Straddle | https://tradetron.tech/bt/view/b83f1f24a8b677c67f472d5189902130 | https://tradetron.tech/bt/view/ee93f4482e77939f1fc30903d86e3593 | Straddle control |
| TT-05 | Simple Intraday Short Straddle | https://tradetron.tech/bt/view/667be6a22e2caa8866b7476065a68120 | https://tradetron.tech/bt/view/f79fd3c6b65919f32a517a21fcdaf934 | Straddle / VIX control |
| TT-06 | Intraday Asym Premium | https://tradetron.tech/bt/view/bc0e67d112845360381bd736f9f98e2d | https://tradetron.tech/bt/view/0600afa7e3e5622999efec27c5c3dd4c | Cross-expiry premium control |
| TT-07 | Dynamic IC to Ratio | https://tradetron.tech/bt/view/ade954a4a6aed2bb03b57462d71dd406 | https://tradetron.tech/bt/view/97fe7a2833f711f4e31ab041aa6f513c | Highest-priority VIX/tail candidate |

The seven ASB exports are the rule source. The export format states that JSON-backed condition and leg fields are the authoritative representations. fileciteturn373file0L5-L8

## B. Prior GitHub strategy lineages

| ID | Repository | Strategy / lineage | Role |
| GH-ICR-01 | Iron-condor-to-ratio-v1 | 0.30/0.10 Iron Condor; transition near 0.10 short-leg delta; directional ratio; continuation and reversal resets | High-priority independent control |
| GH-ICR-02 | Iron-condor-to-ratio-v2 | Independent governed implementation of the same source strategy | Independent provenance |
| GH-IAP-01 | Option-intraday-v1 | 09:30 current-week CE + next-week PE; 50% premium trigger; roll to matching premium; combined 100-point stop; 15:15 exit | High-priority control |
| GH-NODIP-01 | NoDip-Stage-1 | Four-leg NIFTY calendar using near/far weekly expiries | Calendar control |
| GH-BATMAN-01 | MC-OPTIONS-INDEPENDENT-BACKTEST-MC1 | D3, 09:30, 756-session MC, P20/P35/P65/P80 strike mapping, +1/-2/+1/-2 legs | Tail-geometry control |
| GH-BATMAN-02 | MC-OPTIONS-MARGIN-REDUCTION-MC2 | BATMAN strike and capital-reduction variants | Parameter-sensitivity control |
| GH-BATMAN-03 | MC-OPTIONS-VERIFICATION-MC3 | Exact MC-method verification and frozen validation lineage | Method control |
| GH-FINAL4-01 | Final-stand-v4 | Premium-direction / full-chain-OI research | Selector overlay only |
| GH-FINAL2-01 | Final-stand-v2 | Earlier regime-aware option-direction research with a planned new information set including VIX, option-implied skew/IV term structure, FII/DII, breadth and global cross-market variables | Selector/provenance lineage |
| GH-FINAL2-02 | Final-stand-v2 | Monte-Carlo weekly directional three-leg OTM4/OTM5/OTM6 structure: 1 long OTM4 + 1 short OTM5 + 1 short OTM6 on predicted side, entered 4 DTE 10:00 and exited at expiry | High-priority prior strategy candidate / selector downstream |

## C. Daily-Options / Equity Income hypotheses

Registered source hypotheses:
- VIX expected-range Air Defense
- Low-VIX weekly survival structure
- Low-VIX calendar
- Low-VIX diagonal
- Bear-put spread adjustment framework
- Set & Strike / iron-fly weekly structure
- NIFTY Jade Lizard
- Enhanced monthly OTM call debit-spread + short-call overlay
- Falcon Spread 5:3 ratio-diagonal strangle

These are hypothesis records until exact deterministic rules are frozen.

## D. Deduplication

TT-06 is likely the same strategy lineage as Option-intraday-v1.
TT-07 is likely overlapping the Iron-condor-to-ratio lineage.
BATMAN MC1/MC2/MC3 are one methodological lineage.
TT-02 and NoDip are both calendar-like but remain separate because their leg/expiry logic differs.

No results are pooled until exact rule differences are documented.

## E. Inclusion rule

A candidate enters numerical testing only after a deterministic specification and execution model are frozen. Older backtest performance is never treated as prospective validation evidence.

## E. Previously tested Daily-Options families retained as controls

- **Air Defense / VIX expected-range**: Phase 30.1 Base + Stress completed with 0/24 cells passing the fixed weekly gate; retained as negative historical control, not a new promotion candidate.
- **Falcon Spread**: Phase 30.2/Phase 24 lineage; independent-source coverage was insufficient in at least one corrected run, so it remains a source-faithful data-limited control until an executable validation sample is demonstrated.
- **Phase 19 short-strangle / iron-condor regime family**: registered historically as a prior NIFTY short-volatility lineage; only results that pass the current Final Stand evidence hierarchy can be reused.
