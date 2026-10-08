import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results/phase50b/tt03_otm_distance"
BASE=ROOT/"results/phase50b/tt03_dynamic_n_replay/summary.json"


def load_distance(d):
    p=OUT/f"d{d}"
    s=json.loads((p/"summary.json").read_text())
    return s


def main():
    base=json.loads(BASE.read_text())
    candidates=[]
    for d in (350,400):
        s=load_distance(d)
        dev=[x for x in pd.read_csv(OUT/f"d{d}"/"split_summary.csv").to_dict("records") if x["split"]=="DEV"]
        dev=dev[0] if dev else {"net":0.0,"net50":0.0,"trades":0}
        qualifying=(float(s["coverage_rate"])>=0.95 and float(dev["net"])>0 and float(dev["net50"])>0)
        candidates.append({"distance":d,"coverage_rate":float(s["coverage_rate"]),"dev_net":float(dev["net"]),"dev_net50":float(dev["net50"]),"dev_trades":int(dev["trades"]),"qualifies":qualifying})

    qualified=[x for x in candidates if x["qualifies"]]
    selected=max(qualified,key=lambda x:x["dev_net50"]) if qualified else None

    comparison=[]
    for label,s in [("BASE",base),("OTM350",load_distance(350)),("OTM400",load_distance(400))]:
        for row in s.get("splits",[]):
            comparison.append({"geometry":label,**row})

    decision={
        "status":"PASS",
        "base":{"geometry":"BASE","coverage_rate":float(base["coverage_rate"]),"net":float(base["net"]),"net50":float(base["net50"])},
        "mutation_candidates":candidates,
        "selected_mutation":selected,
        "selection_rule":"Among OTM350/OTM400: >=95% coverage, positive DEV net and positive DEV net50; highest DEV net50 wins.",
        "validation_holdout_are_post_selection":True,
    }

    (OUT/"development_selection.json").write_text(json.dumps(decision,indent=2))
    pd.DataFrame(comparison).to_csv(OUT/"geometry_split_comparison.csv",index=False)
    print(json.dumps(decision,indent=2))

if __name__=="__main__":
    main()
