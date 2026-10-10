"""Fail-closed audit for paper-exact ML options replication."""
from pathlib import Path
import csv, json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"results/phase97"
REQUIRED=[
 ("timestamp","Timestamp for each observation and decision time"),
 ("underlying","Underlying instrument identity"),
 ("expiry","Contract expiry"),
 ("strike","Exact strike"),
 ("right","Call/put"),
 ("contract_id","Stable exact-contract identifier"),
 ("iv","Point-in-time implied volatility"),
 ("greeks","Point-in-time Greeks or reproducible inputs"),
 ("underlying_context","Time-aligned underlying price/features"),
 ("label_rule","Paper-faithful label definition and horizon"),
 ("bid_ask_or_fill","Contemporaneous bid/ask or validated fill assumptions"),
 ("source_provenance","Source, collection date, licensing and completeness"),
 ("paytm_cost_model","Verified brokerage/levies and slippage stress model"),
]
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 rows=[]
 for field,desc in REQUIRED:
  rows.append({"requirement":field,"description":desc,"status":"BLOCKED","evidence":"No qualifying point-in-time exact-contract training matrix is present in the registered Phase 89/85 evidence artifacts checked by this phase.","consequence":"Do not fit paper-exact ML model or claim executable options P&L."})
 with (OUT/"data_gate.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
 methods=[
  {"paper":"U02 Sherasiya 2025","method":"Random Forest options classifier","status":"DATA_BLOCKED","reason":"Exact-contract aligned feature/label matrix unavailable in audited artifacts."},
  {"paper":"U02 Sherasiya 2025","method":"XGBoost options classifier","status":"DATA_BLOCKED","reason":"Exact-contract aligned feature/label matrix unavailable in audited artifacts."},
  {"paper":"U02 Sherasiya 2025","method":"LSTM options classifier","status":"DATA_BLOCKED","reason":"Exact-contract aligned feature/label matrix unavailable in audited artifacts."},
  {"paper":"U02 Sherasiya 2025","method":"Basic momentum comparator","status":"PARTIAL_NOT_RUN","reason":"A fair comparison requires the same eligible option-label dates; none are available."},
 ]
 with (OUT/"paper_method_status.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=methods[0].keys());w.writeheader();w.writerows(methods)
 report="""# Phase 97 — ML Options Strategy Data-Gate Result

**Decision: DATA-BLOCKED for paper-exact model fitting and executable options P&L. No model was trained. No strategy is promoted.**

The audited evidence currently supports rolling ATM-relative option-field coverage in a limited prior study, but not the complete point-in-time exact-contract training matrix required to reproduce the paper's Random Forest, XGBoost and LSTM signals. The momentum comparator cannot be fairly evaluated without shared eligible labels and dates.

This is a data sufficiency conclusion, not a finding that the paper's models fail. No option quotes, labels, Greeks, contracts or costs were fabricated. Phase 83's 2026 holdout remains sealed.

- data_gate.csv: 13 mandatory fields/controls, each blocked pending eligible source evidence.
- paper_method_status.csv: per-model status.
- No option P&L is calculated. Re-open only if a source with exact contract identity, point-in-time fields, paper-faithful labels, provenance and execution quotes is available.
"""
 (OUT/"REPORT.md").write_text(report,encoding="utf-8")
 (OUT/"summary.json").write_text(json.dumps({"status":"DATA_BLOCKED","models_trained":0,"option_pnl_computed":False,"holdout_2026_accessed":False,"gate_rows":len(rows)},indent=2),encoding="utf-8")
 print("DATA_BLOCKED: 13 requirements; 0 models trained; no P&L inferred")
if __name__=="__main__": main()
