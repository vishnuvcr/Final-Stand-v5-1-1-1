import json
from pathlib import Path
REG = Path('PHASE50B_STRATEGY_UNIVERSE.md')
assert REG.exists()
required_tt = ['Dynamic Ratio Reversals','0.20/0.10 Delta Calendar Hedge Spread v4','Corrected Dynamic-n NIFTY Weekly Options Strategy','Profit Breakout Premium Match Straddle','Simple Intraday Short Straddle','Intraday Asym Premium','Dynamic IC to Ratio']
required_repos = ['Iron-condor-to-ratio-v1','Iron-condor-to-ratio-v2','Option-intraday-v1','NoDip-Stage-1','MC-OPTIONS-INDEPENDENT-BACKTEST-MC1','MC-OPTIONS-MARGIN-REDUCTION-MC2','MC-OPTIONS-VERIFICATION-MC3','Daily-Options','Final-stand-v4','Final-stand-v2']
text=REG.read_text(encoding='utf-8')
for x in required_tt: assert x in text, x
for x in required_repos: assert x in text, x
out={'phase':'50B','seven_tradetron_strategies_registered':len(required_tt),'prior_github_lineages_registered':len(required_repos),'parent_phase50_workflow_run':37567632928,'status':'registry_validated'}
outdir=Path('results/phase50b'); outdir.mkdir(parents=True,exist_ok=True)
(outdir/'registry_validation.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
