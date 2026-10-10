import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from cci_gate import ROWS
def test_gate_does_not_promote_rolling_data_to_exact_contract():
 assert any("rolling ATM-relative" in " ".join(r) for r in ROWS)
 assert any("bid/ask/depth" in " ".join(r) for r in ROWS)
def test_no_new_replay_without_new_source():
 assert any(r[2]=="EXISTING_BLOCKER" for r in ROWS)
