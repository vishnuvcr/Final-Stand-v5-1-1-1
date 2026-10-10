import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit_gate import REQUIRED
def test_gate_has_execution_and_provenance_controls():
 names={x[0] for x in REQUIRED}
 assert {"timestamp","contract_id","expiry","strike","right","label_rule","bid_ask_or_fill","source_provenance","paytm_cost_model"} <= names
def test_no_paper_exact_model_without_full_gate():
 assert len(REQUIRED) >= 10
