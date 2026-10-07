# Phase 50B — 2026 Execution-Cost Audit

## Current external verification

Checked current public broker/exchange sources on 2026-10-07.

### Paytm Money
Paytm Money's current F&O FAQ states brokerage of **₹10 per unique executed order**. Its pricing page states statutory/regulatory/exchange charges are levied at actuals and that tariffs are subject to change. This supports the registered Phase-50B base assumption of ₹10/order, while the +50% monetary-cost stress remains the robustness control.

### NSE / statutory charges
NSE's current STT page states that from **1 April 2026**, sale of an option is charged **0.15% of option premium**. NSE's current levy page lists SEBI turnover fee at **0.0001%**, equity-option stamp duty at **0.003% on the buyer**, and confirms the 0.15% option-sale STT rate from 1 April 2026.

## Reconciliation with replay engine
The common-cost replay currently applies:
- brokerage ₹10/order;
- option-sale STT at 0.0625% before 2024-10-01, 0.10% from 2024-10-01 through 2026-03-31, and 0.15% from 2026-04-01;
- exchange transaction rate 0.0495% before 2024-10-01, 0.03503% from 2024-10-01 through 2026-02-28, and 0.0355299% from 2026-03-01;
- SEBI 0.0001%;
- IPFT 0.0005% before 2026-03-01 and 0.0000001% thereafter;
- buyer stamp duty 0.003%;
- GST at 18% on brokerage plus exchange/SEBI/IPFT components;
- adverse execution slippage of ₹0.05/option-point per execution in the primary replay;
- +50% monetary-cost stress.

The statutory inputs are therefore not left at the 2024 STT rate for 2026 trades.

## Important limitation
NSE's public pages provide statutory levies, while Paytm Money states that actual exchange/regulatory charges apply. Strategy promotion still requires the registered doubled-friction test; a positive result must survive that stress, not merely the base cost case.


## 2026-10-07 — Paytm Money current brokerage robustness audit
- Paytm Money's current public material is internally inconsistent: an F&O FAQ currently shows ₹10 per unique executed order, while Paytm Money's official 2025 pricing announcement states a flat ₹20 brokerage across segments from 15 January 2025. citeturn157124search0turn157124search2
- The canonical Phase-50B preregistered model remains **₹10/order** for comparability with the parent research program.
- A separate **₹20/order current-account robustness scenario** is now required for promotion sensitivity. It does not replace the primary model or permit post-result candidate selection.
- NSE's current statutory schedule confirms option-sale STT of 0.15% from 1 April 2026 and equity-option stamp duty of 0.003% on buyers. citeturn214286search0turn214286search3
