import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from payoff_replay import leg_payoff,payoff,structures

def test_long_call_source_style_arithmetic():
 assert leg_payoff(120,"call",1,100,8)==12
 assert leg_payoff(90,"call",1,100,8)==-8

def test_vertical_spread_limited_upside():
 legs=[{"right":"call","side":1,"strike":100,"premium":8},{"right":"call","side":-1,"strike":120,"premium":3}]
 assert payoff(90,legs)==-5
 assert payoff(150,legs)==15

def test_put_butterfly_label_conflict_is_preserved():
 x={name:note for name,legs,note in structures()}
 assert "Source labels this Short Butterfly" in x["Put butterfly — legs per source"]

def test_invalid_leg_rejected():
 try:
  leg_payoff(100,"call",0,100,2)
 except ValueError:
  return
 assert False,"invalid side must be rejected"
