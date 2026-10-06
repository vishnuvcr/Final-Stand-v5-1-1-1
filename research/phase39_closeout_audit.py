import json
from pathlib import Path
import pandas as pd

required=[
"PHASE39_RESEARCH_PLAN.md","PHASE39_PRE_REGISTRATION.md","PHASE39_LITERATURE_REVIEW.md",
"PHASE39_STATUS.md","ERROR_LOG.md","README.md","manuscript/PHASE39_RESEARCH_MANUSCRIPT.md",
"results/phase39_counterfactual/fixed_opportunity_ledger.csv",
"results/phase39_models/model_comparison.csv",
"results/phase39_sequential_policy/summary.json",
"results/phase39_sequential_policy_audit/audit.json",
"results/phase39_advanced_screen/advanced_model_comparison.csv",
"results/phase39_final_exploratory/summary.json"
]
for p in required: assert Path(p).exists(), p
ledger=pd.read_csv("results/phase39_counterfactual/fixed_opportunity_ledger.csv")
assert len(ledger)==477 and ledger.entry_ts.nunique()==477
assert ledger.split.value_counts().to_dict()=={"development":271,"validation":172,"holdout":34}
m=pd.read_csv("results/phase39_models/model_comparison.csv")
assert len(m)==7 and (m.features>0).all()
seq=json.load(open("results/phase39_sequential_policy/summary.json"))
audit=json.load(open("results/phase39_sequential_policy_audit/audit.json"))
adv=json.load(open("results/phase39_advanced_screen/status.json"))
fin=json.load(open("results/phase39_final_exploratory/summary.json"))
assert seq["control_period_counts"]=={"development":271,"validation":172,"holdout":34}
assert audit["status"]=="PASS"
assert adv["status"]=="COMPLETE" and adv["holdout_evaluated"] is False
assert fin["status"]=="COMPLETE" and fin["holdout_evaluated"] is False
assert fin["decision"]=="NO_HOLDOUT_OR_PROMOTION"
out={
 "status":"PASS",
 "decision":"CLOSE_PHASE_39_NO_PROMOTION",
 "panel":{"development":271,"validation":172,"holdout":34},
 "sequential_candidate":"Sparse_GAM_margin",
 "validation_uplift_rupees":audit["validation_uplift_rupees"],
 "holdout_uplift_rupees":audit["holdout_uplift_rupees"],
 "development_uplift_rupees":-18175.068968249994,
 "overrides":seq["overrides"],
 "cost_stress_plus_50_validation":audit["validation_uplift_cost_x_1_50"],
 "cost_stress_plus_50_holdout":audit["holdout_uplift_cost_x_1_50"],
 "manuscript":"manuscript/PHASE39_RESEARCH_MANUSCRIPT.md",
 "canonical_strategy_unchanged":True
}
Path("results/phase39_closeout").mkdir(parents=True,exist_ok=True)
Path("results/phase39_closeout/closeout.json").write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
