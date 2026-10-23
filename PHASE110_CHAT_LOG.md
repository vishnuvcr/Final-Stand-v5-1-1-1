# Phase 110 Visible Conversation / Decision Log

This log records the user's visible instruction and the operational decisions needed to reproduce the project work. It does not contain private internal reasoning.

## 2026-10-23 — User request

> Can you test a strategy?
>
> Entry 10 am on the next trading day to the previous weekly expiry
>
> Sell 0.15 delta call and put current weekly
>
> Exit at 2 pm on expiry day
>
> I want you to find a stop loss criteria based on the greeks - delta, gamma, vega, theta
>
> Start by testing SL when combined delta moves beyond 0.4. but test all combination

## Visible execution commitments

- Use a separate branch and bounded phases with automated and manual workflow invocation.
- Start with NIFTY weekly options, as inferred from the repository's prior research and available source. Log this assumption.
- Use exact 09:59 selection inputs and exact 10:00 entry bar; a stop decided on a completed bar can execute only at the next exact minute open.
- Test both signed-net and gross-absolute combined delta interpretations.
- Sweep all preregistered active Greek subsets and thresholds, including OR/AND logic, and all 24 brokerage/slippage/modelled-fee scenarios.
- Append every step and failure to the phase log. No results or conclusions are to be stated until the result files and run logs are inspected.
- Use validation for candidate selection and reserve holdout for a frozen shortlist. No strategy promotion without the independent tester gate.