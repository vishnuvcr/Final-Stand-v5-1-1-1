import json, hashlib
from pathlib import Path

REGISTRY = Path("PHASE50B_STRATEGY_REGISTRY.md")
PRE = Path("PHASE50B_PRE_REGISTRATION.md")
PLAN = Path("PHASE50B_RESEARCH_PLAN.md")

def main():
    assert REGISTRY.exists() and PRE.exists() and PLAN.exists()
    text = REGISTRY.read_text()
    required = [
        "Dynamic_Ratio_Reversals.json",
        "020010_Delta_Calendar_Hedge_Spread_v4.json",
        "Corrected_Dynamic-n_NIFTY_Weekly_Options_Strategy.json",
        "Profit_Breakout_Premium_Match_Straddle.json",
        "Simple_Intraday_Short_Straddle.json",
        "Intraday_Asym_Premium.json",
        "Dynamic_IC_to_Ratio.json",
        "Iron-condor-to-ratio-v1",
        "NoDip-Stage-1",
        "MC-OPTIONS-INDEPENDENT-BACKTEST-MC1",
        "Final-stand-v4",
        "Daily-Options",
        "Naked-option-v1",
    ]
    missing=[x for x in required if x not in text]
    if missing:
        raise SystemExit(f"F50B-001 missing registry entries: {missing}")
    urls=[line for line in text.splitlines() if "tradetron.tech/bt/view/" in line]
    # Seven source URLs are frozen in the plan/registry.
    assert len(urls) == 7, f"expected 7 Tradetron URLs, got {len(urls)}"
    print("Phase 50B source registry audit PASS")
    print("registry_sha256", hashlib.sha256(text.encode()).hexdigest())
    print("tradetron_urls", len(urls))

if __name__ == "__main__":
    main()
