"""Finite evidence reconciliation for the previously blocked CCI options method."""
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"results/phase98"
ROWS=[
 ("Phase 66 CCI replay","zero completed trades","EXISTING_BLOCKER","No estimable trade-level profitability; identical rerun prohibited."),
 ("Phase 85 source audit","no-go on then-verified free sources for execution-quality replay","EXISTING_BLOCKER","No qualified new exact-contract source is established by the registered evidence."),
 ("Phase 87 probe","150 rolling ATM-relative five-minute candles on one date","LIMITED_COVERAGE_ONLY","Field shape does not establish fixed-contract historical execution."),
 ("Phase 88 audit","608 rolling ATM-relative candles across four series","LIMITED_COVERAGE_ONLY","No broad fixed-contract bid/ask/depth coverage proved."),
 ("Phase 89 study","2025 rolling ATM-relative feature coverage","LIMITED_COVERAGE_ONLY","Feature association sample is not the paper's source-period CCI trade ledger."),
 ("Original-period exact contract mapping","not present in audited evidence summary","BLOCKED","Cannot reconstruct source-faithful option entries/exits."),
 ("Historical bid/ask/depth or validated fills","not established by audited evidence","BLOCKED","Cannot estimate executable option P&L and slippage."),
 ("Paytm Money full historical cost model","not verified across paper period","BLOCKED","No definitive net P&L claim."),
]
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with (OUT/"evidence_gate.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.writer(f);w.writerow(["evidence_item","observed_state","status","consequence"]);w.writerows(ROWS)
 status="DATA_BLOCKED_NO_NEW_ELIGIBLE_SOURCE"
 report="""# Phase 98 — CCI Options Replication Gate

**Decision: DATA-BLOCKED. Do not rerun the same CCI proxy with the same zero-coverage inputs.**

The registered evidence does not establish a materially improved authorized source with original-period exact-contract identity, full CCI input bars and executable quotes/fills. Phase 66's zero completed trades remain a data-coverage result, not a negative profitability estimate. Phase 87–89 rolling ATM-relative samples are limited field-coverage evidence and do not close the fixed-contract execution gap.

No new trade ledger was generated and no options P&L was computed. The CCI method remains not reproduced / data-blocked. This does not establish that the paper's method is unprofitable. Re-open only if eligible source data close the listed blockers. Phase 83's 2026 holdout remains sealed.
"""
 (OUT/"REPORT.md").write_text(report,encoding="utf-8")
 (OUT/"summary.json").write_text(json.dumps({"status":status,"new_replay_run":False,"reason":"No newly qualified source data","option_pnl_computed":False,"holdout_2026_accessed":False,"evidence_rows":len(ROWS)},indent=2),encoding="utf-8")
 print(status)
if __name__=="__main__":main()
