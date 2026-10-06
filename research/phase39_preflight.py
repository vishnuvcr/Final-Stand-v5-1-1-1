from pathlib import Path
import pandas as pd
import json
import hashlib

ROOT=Path(".")
required=[
    "PHASE39_RESEARCH_PLAN.md",
    "PHASE39_PRE_REGISTRATION.md",
    "PHASE39_LITERATURE_REVIEW.md",
    "results/phase39_candidate_method_registry.csv",
    "results/phase38_corrected_model_robustness/frozen_control_expiry.csv",
    "results/phase38_corrected_model_robustness/frozen_control_metadata.json",
]
for p in required:
    if not Path(p).exists():
        raise FileNotFoundError(p)

reg=pd.read_csv("results/phase39_candidate_method_registry.csv")
assert len(reg) >= 10
assert reg["method"].is_unique
assert (reg["novel_to_repo"].astype(str)=="True").all()

ctl=pd.read_csv("results/phase38_corrected_model_robustness/frozen_control_expiry.csv")
assert {"expiry","net_rupees"} <= set(ctl.columns)
assert ctl["expiry"].is_unique
assert len(ctl)==102

meta=json.loads(Path("results/phase38_corrected_model_robustness/frozen_control_metadata.json").read_text())
assert int(meta["trades"])==206
assert abs(float(meta["net_rupees"])-63672.57530171223)<1e-9

model_cache=Path("results/phase35_advanced_tree_prediction/model_predictions.csv")
cache_status="not_present_on_branch"
if model_cache.exists():
    z=pd.read_csv(model_cache)
    assert {"expiry","ref_ts","target_return","target_direction"} <= set(z.columns)
    ts=pd.to_datetime(z["ref_ts"],errors="coerce")
    exp=pd.to_datetime(z["expiry"],errors="coerce")
    assert (ts < exp).all()
    cache_status="present"

digest=hashlib.sha256(Path("results/phase38_corrected_model_robustness/frozen_control_expiry.csv").read_bytes()).hexdigest()

out={
  "status":"PASS",
  "candidate_methods":int(len(reg)),
  "frozen_control_expiries":int(len(ctl)),
  "frozen_control_trades":206,
  "frozen_control_net_rupees":63672.57530171223,
  "frozen_control_expiry_sha256":digest,
  "phase35_model_cache":cache_status
}
Path("results/phase39_preflight.json").write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
