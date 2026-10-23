# Phase 111 Status — ZigZag Weekly Expiry Options

Updated: 2026-10-24 (Asia/Kolkata)  
Branch: `phase-111-zigzag-weekly-expiry-options`  
Research state: **registered; source/replay workflow not yet verified**  
Promotion status: **NONE**

## Current checkpoint
- [x] Reviewed the current main README and the relevant Phase 110 plan, status, source engine, workflow, logs, and published report.
- [x] Recorded the Phase 110 status/report count discrepancy; neither conflicting count is adopted as evidence for this test.
- [x] Created an isolated Phase 111 branch from main; no prior phase branch is modified.
- [x] Froze signal labels, no-repaint rule, one-leg side mapping, entry/exit times, target delta and universal stop.
- [ ] Resolve the current dataset revision, file listing, source hashes and latest covered expiry.
- [ ] Validate daily candle completeness and causal ZigZag prefix invariance.
- [ ] Run regression tests for Greek signs, selected delta, stop trigger/fill time, P&L signs and costs.
- [ ] Run the fixed strategy on all source-supported weekly campaigns and log each exclusion.
- [ ] Reconcile all 24 cost scenarios and paired no-stop outputs.
- [ ] Publish chronological split results, figures, manuscript and inference.
- [ ] Update branch status, research/error/chat logs, phase README, and main README.
- [ ] Stop at the registered finite gates; no strategy promotion without sufficient evidence.

## Locked operational rules
- Daily chart signal. Depth 12, Deviation 5, Backstep 2.
- Non-repainting only: use last confirmed HL/LL → sell PE; HH/LH → sell CE.
- Entry: next observed trading session after previous expiry, exact 10:00 IST. Selection from exact 09:59 data, target absolute delta 0.10.
- Exit: target weekly expiry, exact 10:00 IST unless absolute model delta reaches 0.50 first, with the stop filling at the next exact minute open.
- Historical data: actual coverage cutoff only. Missing observations are exclusions; no forward-fill/interpolation.
- Costs: 24 registered combinations of ₹10/15/20 brokerage, ₹0/0.05/0.25/0.50 per-unit slippage, 1.0×/1.5× fees. Include the project's date-effective lot sizes, taxes and exchange charges.
- Tester review: waived explicitly for this phase.

## Phase gates
| Gate | State |
|---|---|
| 111.0 Plan registration | COMPLETE |
| 111.1 Source/coverage audit | PENDING |
| 111.2 Mathematical/timestamp regression | PENDING |
| 111.3 Fixed-rule replay | PENDING |
| 111.4 Costs/no-stop benchmark | PENDING |
| 111.5 Statistics/manuscript | PENDING |
| 111.6 Repository publication/stop | PENDING |

## Prior-phase discrepancy carried forward
Phase 110's status checkpoints included a 259 scheduled / 0 eligible result, while its published `results/phase110/PHASE110_REPORT.md` reported 130 eligible and 133 excluded. This inconsistency is a logged data/documentation issue and is not silently reconciled here.

## Developer next instruction
Finish the source audit and exact one-rule replay. Preserve the registered split/stop/cost definitions. Do not loosen coverage requirements to manufacture trades; if the source is incomplete or the ZigLib port cannot be independently matched, publish the limitation and do not promote.

## Failed or blocked execution — run 40035215935 (2026-10-23T22:41:51.256128+00:00)
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/40035215935
- Outcomes: {"COMPILE_OUTCOME": "success", "JOB_STATUS": "failure", "REPLAY_OUTCOME": "skipped", "TEST_OUTCOME": "failure"}
- Error: No summary was produced; inspect the first failed Actions step. No P&L result is inferred.
- No accepted strategy result or promotion claim.
