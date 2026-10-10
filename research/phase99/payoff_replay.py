"""Analytical expiry payoff calculator for source-described option structures.
Illustrative payoff arithmetic only; not a historical trading backtest.
"""
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/"results/phase99"

def leg_payoff(spot, right, side, strike, premium):
    if right not in {"call","put"} or side not in {-1,1} or strike<0 or premium<0:
        raise ValueError("invalid option leg")
    intrinsic=max(spot-strike,0) if right=="call" else max(strike-spot,0)
    return side*(intrinsic-premium)

def payoff(spot, legs):
    return sum(leg_payoff(spot,**leg) for leg in legs)

def structures():
    # side +1 long, -1 short; premium is per underlying unit.
    return [
      ("Long call", [{"right":"call","side":1,"strike":100,"premium":8}], "U07 source-defined directional payoff"),
      ("Long put", [{"right":"put","side":1,"strike":100,"premium":7}], "U07 source-defined directional payoff"),
      ("Short call", [{"right":"call","side":-1,"strike":100,"premium":8}], "U07 source-defined; tail risk unbounded"),
      ("Short put", [{"right":"put","side":-1,"strike":100,"premium":7}], "U07 source-defined; downside liability substantial"),
      ("Bull call spread", [{"right":"call","side":1,"strike":100,"premium":8},{"right":"call","side":-1,"strike":120,"premium":3}], "Buy lower-strike call; sell higher-strike call"),
      ("Bull put spread", [{"right":"put","side":1,"strike":90,"premium":2},{"right":"put","side":-1,"strike":100,"premium":6}], "Buy lower-strike put; sell higher-strike put"),
      ("Bear put spread", [{"right":"put","side":1,"strike":120,"premium":9},{"right":"put","side":-1,"strike":100,"premium":4}], "Buy higher-strike put; sell lower-strike put"),
      ("Bear call spread", [{"right":"call","side":-1,"strike":100,"premium":8},{"right":"call","side":1,"strike":120,"premium":3}], "Sell lower-strike call; buy higher-strike call"),
      ("Long call butterfly", [{"right":"call","side":1,"strike":90,"premium":14},{"right":"call","side":-1,"strike":100,"premium":8},{"right":"call","side":-1,"strike":100,"premium":8},{"right":"call","side":1,"strike":110,"premium":4}], "Buy lower/higher strikes; sell two middle strikes"),
      ("Put butterfly — legs per source", [{"right":"put","side":1,"strike":90,"premium":4},{"right":"put","side":-1,"strike":100,"premium":8},{"right":"put","side":-1,"strike":100,"premium":8},{"right":"put","side":1,"strike":110,"premium":14}], "Source labels this Short Butterfly despite legs matching a long butterfly shape"),
      ("Long straddle", [{"right":"call","side":1,"strike":100,"premium":8},{"right":"put","side":1,"strike":100,"premium":7}], "Long call and long put at same strike"),
      ("Short straddle", [{"right":"call","side":-1,"strike":100,"premium":8},{"right":"put","side":-1,"strike":100,"premium":7}], "Short call and short put at same strike"),
      ("Long strangle", [{"right":"call","side":1,"strike":110,"premium":4},{"right":"put","side":1,"strike":90,"premium":4}], "Illustrative operationalization; exact strikes/premiums are not uniquely prescribed"),
    ]

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    spots=[70,80,90,95,100,105,110,120,130]
    rows=[]
    for name,legs,note in structures():
        for spot in spots:
            rows.append({"structure":name,"expiry_spot":spot,"net_payoff_per_unit":round(payoff(spot,legs),6),"legs_json":json.dumps(legs,separators=(",",":")),"source_note":note})
    with (OUT/"illustrative_payoffs.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    source=[
      {"paper":"U07","method":"Long call / put; short call / put","status":"ANALYTICAL_PAYOFF_REPLAY","limitation":"No market premiums or fills"},
      {"paper":"U07","method":"Bull/bear call and put spreads","status":"ANALYTICAL_PAYOFF_REPLAY","limitation":"Source examples are analytical, not historical signal tests"},
      {"paper":"U07","method":"Call butterfly","status":"ANALYTICAL_PAYOFF_REPLAY","limitation":"Generic illustrative strikes/premiums used for curve checks"},
      {"paper":"U07","method":"Put butterfly / Short Butterfly","status":"SOURCE_AMBIGUITY","limitation":"Heading conflicts with described legs; legs preserved"},
      {"paper":"U07","method":"Long/short straddle; long strangle","status":"ANALYTICAL_PAYOFF_REPLAY","limitation":"Generic premiums/strikes; not a paper-exact trade signal"},
      {"paper":"U05","method":"First Thursday; 3-year monthly average; 20% target; 30% stop; T+3 stop delay","status":"RULE_EXTRACTED_MARKET_REPLAY_BLOCKED","limitation":"Requires source-period exact-contract prices/liquidity and costed fills"},
    ]
    with (OUT/"source_method_status.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=source[0].keys());w.writeheader();w.writerows(source)
    report="""# Phase 99 — Options Payoff Taxonomy Replay

**Outcome: analytical payoff checks implemented; historical profitability backtest remains DATA-BLOCKED. No strategy is promoted.**

The payoff table calculates intrinsic payoff plus initial premium cash flow per underlying unit at expiry. The included premiums and most strike combinations are illustrative inputs to test the algebra, not historical NIFTY quotes and not recommendations. The results exclude brokerage, statutory charges, bid/ask, slippage, latency, margin funding and lot-specific execution.

Source extraction:
- U07 describes directional options, vertical spreads, butterflies and volatility structures. The source's put-butterfly section is internally inconsistent: its heading calls it “Short Butterfly”, while its example legs buy one lower-strike put, sell two middle-strike puts and buy one higher-strike put. The legs imply a long butterfly payoff; this is flagged, not silently corrected.
- U05 specifies first-Thursday entry, one-month European options, strike based on first-Wednesday price and prior three-year average monthly return, a 20% target, a 30% stop and delayed stop activation after T+3. The original market replay is blocked without point-in-time exact-contract prices/liquidity and credible early-exit fills.
- These payoff formulas are not evidence that any strategy predicts NIFTY or makes money after costs.

See illustrative_payoffs.csv and source_method_status.csv. Phase 83's 2026 holdout remains sealed.
"""
    (OUT/"REPORT.md").write_text(report,encoding="utf-8")
    (OUT/"summary.json").write_text(json.dumps({"status":"PAYOFF_ALGEBRA_CHECKED_MARKET_PNL_BLOCKED","structures":len(structures()),"illustrative_spot_grid":spots,"option_pnl_is_historical":False,"holdout_2026_accessed":False},indent=2),encoding="utf-8")
    print(f"PAYOFF_ALGEBRA_CHECKED: {len(structures())} structures; historical P&L blocked")
if __name__=="__main__": main()
