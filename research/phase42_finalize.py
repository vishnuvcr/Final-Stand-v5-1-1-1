import json
from pathlib import Path
import numpy as np
import pandas as pd
O=Path("results/phase42_confidence_calibration")
sel=json.load(open(O/"selection.json")); s=pd.read_csv(O/"sequential_summary.csv")
top=sel["top3_frozen_before_holdout"]
def get(r,p):
 x=s[(s["rank"]==r)&(s["period"]==p)]
 return x.iloc[0].to_dict() if len(x) else {}
checks=[]
for r in range(1,len(top)+1):
 v=get(r,"validation"); h=get(r,"holdout")
 checks.append({"rank":r,"model":v.get("model"),"calibration":v.get("calibration"),"margin":v.get("margin"),"gate":v.get("gate"),
 "promotion_pass":bool(v.get("uplift_rupees",0)>0 and h.get("uplift_rupees",0)>0 and h.get("overrides",0)>=5 and
 v.get("policy_drawdown_rupees",1e99)<=1.25*v.get("control_drawdown_rupees",1) and
 h.get("policy_drawdown_rupees",1e99)<=1.25*h.get("control_drawdown_rupees",1) and
 v.get("boot_ci_low",-1e99)>=0 and h.get("boot_ci_low",-1e99)>=0),
 "validation":v,"holdout":h})
decision="PROMOTION CANDIDATE — REQUIRES FINAL HUMAN/REPOSITORY REVIEW" if checks and all(x["promotion_pass"] for x in checks) else "NO PROMOTION — CANONICAL STRATEGY UNCHANGED"
res={"phase":42,"status":"COMPLETE","declared_variants":72,"eligible_count":int(sel["eligible_count"]),"decision":decision,"top3_frozen":top,"checks":checks}
(O/"final_decision.json").write_text(json.dumps(res,indent=2,default=str))
lines=["# Phase 42 Manuscript — Confidence Calibration and Selective Counterfactual Routing","","## Abstract","Phase 42 tested whether the Phase-41 uncertainty layer was too conservative. Seventy-two preregistered variants were screened chronologically; the holdout was untouched until the top three validation candidates were frozen. Exact sequential replay and paired-expiry inference were then completed.","","## Results","See the complete 72-variant grid in results/phase42_confidence_calibration/fixed_grid_validation.csv.","","|Rank|Model|Calibration|Margin|Gate|Validation uplift|Holdout uplift|Holdout overrides|","|---:|---|---|---:|---|---:|---:|---:|"]
for r in range(1,len(top)+1):
 v=get(r,"validation"); h=get(r,"holdout")
 lines.append(f"|{r}|{v.get('model')}|{v.get('calibration')}|{v.get('margin')}|{v.get('gate')}|{v.get('uplift_rupees',0):.2f}|{h.get('uplift_rupees',0):.2f}|{int(h.get('overrides',0))}|")
lines+=["","## Statistical inference","Paired-expiry bootstrap and sign-flip results are persisted in sequential_summary.csv.","","## Discussion","A ranking signal is not sufficient for promotion unless it converts into robust sequential control-relative P&L after costs. Conformal-style calibration is treated as a selective decision layer; no formal exchangeability-based guarantee is claimed for financial time series.","","## Strengths","- bounded preregistration;","- strict chronology;","- untouched holdout;","- exact execution-cost model.","","## Limitations","- small independent holdout;","- financial dependence weakens formal conformal guarantees;","- historical fills do not reproduce live latency/queue effects.","","## Conclusion",decision,"","## Future research","Require materially new information or prospective broker-quality validation rather than endless threshold tuning.",""]
Path("PHASE42_MANUSCRIPT.md").write_text("\n".join(lines))
Path("PHASE42_STATUS.md").write_text("# Phase 42 Status\n\n**COMPLETE — "+decision+"**\n\n72 preregistered variants; validation-eligible: "+str(sel["eligible_count"])+".\n")
print(json.dumps(res,indent=2,default=str))
