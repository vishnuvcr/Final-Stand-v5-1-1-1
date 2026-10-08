import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OTM = ROOT / "results/phase50b/otm350_artifact/tt03_trades.csv"
BASE = ROOT / "results/phase50b/tt03_dynamic_n_replay/tt03_trades.csv"
OUT = ROOT / "results/phase50b/phase50b6_inference"
OUT.mkdir(parents=True, exist_ok=True)

SEED = 5062026
BOOT = 10000
MC = 100000
VAL_START = pd.Timestamp("2024-01-01")
VAL_END = pd.Timestamp("2025-12-31")
ENDPOINTS = {"net":"standard","net50":"plus50_stress","net20":"brokerage20","net20_50":"brokerage20_plus50_stress"}

def load(path):
    x = pd.read_csv(path)
    x["expiry"] = pd.to_datetime(x["expiry"]).dt.normalize()
    return x.sort_values("expiry").reset_index(drop=True)

def holm(pvals):
    order = sorted(pvals, key=lambda n: pvals[n])
    out = {}
    running = 0.0
    m = len(order)
    for i, n in enumerate(order):
        running = max(running, min(1.0, (m-i) * pvals[n]))
        out[n] = running
    return out

def paired_bootstrap(d, rng):
    idx = rng.integers(0, len(d), size=(BOOT, len(d)))
    return d[idx].mean(axis=1)

def signflip_p(d, rng):
    obs = float(np.mean(d))
    signs = rng.choice(np.array([-1.0, 1.0]), size=(MC, len(d)))
    means = (signs*d).mean(axis=1)
    return float((np.sum(means >= obs)+1)/(MC+1))

def main():
    if not OTM.exists() or not BASE.exists():
        raise FileNotFoundError("Required frozen OTM350 or BASE trade ledger is missing")
    otm, base = load(OTM), load(BASE)
    common = sorted(set(otm.expiry) & set(base.expiry))
    if len(common) != len(otm) or len(common) != len(base):
        raise RuntimeError("Campaign membership mismatch between OTM350 and BASE")
    merged = otm.merge(base, on="expiry", how="inner", suffixes=("_otm","_base"), validate="one_to_one")
    if len(merged) != len(common):
        raise RuntimeError("One-to-one expiry pairing failed")
    for field in ["entry_ts","exit_ts","direction"]:
        if not (merged[f"{field}_otm"].astype(str).values == merged[f"{field}_base"].astype(str).values).all():
            raise RuntimeError(f"Paired campaign identity mismatch in {field}")
    val = merged[(merged.expiry >= VAL_START) & (merged.expiry <= VAL_END)].copy()
    if len(val) != 76:
        raise RuntimeError(f"Unexpected validation campaign count: {len(val)}")

    rng = np.random.default_rng(SEED)
    results, secondary = {}, {}
    for col, label in ENDPOINTS.items():
        d = (val[f"{col}_otm"] - val[f"{col}_base"]).to_numpy(float)
        boot = paired_bootstrap(d, rng)
        p = signflip_p(d, rng)
        results[col] = {
            "endpoint":label, "n_expiries":len(d),
            "mean_difference":float(d.mean()), "median_difference":float(np.median(d)),
            "mean_bootstrap_ci_low":float(np.quantile(boot,0.025)),
            "mean_bootstrap_ci_high":float(np.quantile(boot,0.975)),
            "p_one_sided_signflip":p,
            "prob_otm_beats_base":float(np.mean(d>0)),
            "positive_expiry_count":int(np.sum(d>0)),
            "negative_expiry_count":int(np.sum(d<0))
        }
        if col != "net": secondary[col]=p
    for col,p in holm(secondary).items():
        results[col]["holm_adjusted_p"]=p
    results["net"]["holm_adjusted_p"]=None

    rows=[]
    for group_name, group in [
        ("2024",val[val.expiry.dt.year==2024]),
        ("2025",val[val.expiry.dt.year==2025]),
        ("CALL_RATIO_BEARISH",val[val.direction_otm=="CALL_RATIO_BEARISH"]),
        ("PUT_RATIO_BULLISH",val[val.direction_otm=="PUT_RATIO_BULLISH"])]:
        for col,label in ENDPOINTS.items():
            d=(group[f"{col}_otm"]-group[f"{col}_base"]).to_numpy(float)
            rows.append({"group":group_name,"endpoint":label,"n":len(d),
                         "mean_difference":float(d.mean()) if len(d) else np.nan,
                         "median_difference":float(np.median(d)) if len(d) else np.nan,
                         "prob_otm_beats_base":float(np.mean(d>0)) if len(d) else np.nan})
    pd.DataFrame(rows).to_csv(OUT/"subgroup_descriptives.csv",index=False)

    paired=val[["expiry","direction_otm"]+[f"{c}_{s}" for c in ENDPOINTS for s in ("otm","base")]].copy()
    for c in ENDPOINTS: paired[f"diff_{c}"]=paired[f"{c}_otm"]-paired[f"{c}_base"]
    paired.to_csv(OUT/"validation_paired_expiry.csv",index=False)
    pd.DataFrame([{"endpoint":x["endpoint"],**x} for x in results.values()]).to_csv(OUT/"statistical_endpoints.csv",index=False)

    primary=results["net"]
    primary_pass=(primary["mean_difference"]>0 and primary["mean_bootstrap_ci_low"]>0 and primary["p_one_sided_signflip"]<0.05)
    decision={"phase":"50B-6","status":"PASS" if primary_pass else "NO_PROMOTION",
              "treatment":"OTM350","control":"BASE",
              "primary_sample":"2024-01-01 through 2025-12-31",
              "primary_endpoint":"validation paired expiry-level net P&L difference",
              "primary_result":primary,"secondary_results":results,
              "holdout_used_for_selection_or_inference":False,
              "selection_reopened":False,"seed":SEED,"bootstrap_resamples":BOOT,"signflip_mc_resamples":MC}
    (OUT/"decision.json").write_text(json.dumps(decision,indent=2))
    p=paired.sort_values("expiry").copy()
    p["cumulative_diff_net"]=p["diff_net"].cumsum()
    p[["expiry","cumulative_diff_net"]].to_csv(OUT/"cumulative_paired_difference.csv",index=False)
    print(json.dumps(decision,indent=2))

if __name__=="__main__": main()
