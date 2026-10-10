#!/usr/bin/env python3
"""Phase 82: preregistered expiry-cluster inference for Phase 81 paired windows."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import t as student_t

BASE = Path("results/phase81_intraday_overnight")
OUT = Path("results/phase82_expiry_cluster_inference")
OUT.mkdir(parents=True, exist_ok=True)
BOOTSTRAPS, SEED, ALPHA = 10_000, 820_102, 0.05
SPLITS = ("development", "validation")
PRIMARY = "overnight_minus_intraday_1tick"
STRESS = "overnight_minus_intraday_2tick"

def holm_adjust(pvalues):
    order = np.argsort(np.asarray(pvalues, dtype=float))
    adjusted = np.empty(len(pvalues), dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, min(1.0, (len(pvalues) - rank) * float(pvalues[idx])))
        adjusted[idx] = running
    return adjusted.tolist()

def cluster_inference(frame, column, seed):
    x = frame[["expiry", column]].copy()
    x[column] = pd.to_numeric(x[column], errors="coerce")
    x = x.dropna()
    clusters = [g[column].to_numpy(float) for _, g in x.groupby("expiry", sort=True) if len(g)]
    G, N = len(clusters), sum(len(v) for v in clusters)
    if G < 3 or N < 10:
        raise ValueError(f"Insufficient clusters for {column}: G={G}, N={N}")
    vals = x[column].to_numpy(float)
    mean, median = float(vals.mean()), float(np.median(vals))
    sums = np.asarray([a.sum() for a in clusters], float)
    ns = np.asarray([len(a) for a in clusters], float)
    residual_sums = sums - mean * ns
    variance = (G / (G - 1.0)) * float(np.sum(residual_sums**2)) / N**2
    se = float(np.sqrt(max(variance, 0.0)))
    if se:
        statistic = mean / se
        pvalue = float(2 * student_t.sf(abs(statistic), df=G - 1))
        crit = float(student_t.ppf(0.975, df=G - 1))
        lo, hi = mean - crit * se, mean + crit * se
    else:
        statistic, pvalue, lo, hi = (0.0, 1.0, mean, mean) if mean == 0 else (float("inf"), 0.0, mean, mean)
    rng = np.random.default_rng(seed)
    boot = np.empty(BOOTSTRAPS, float)
    for b in range(BOOTSTRAPS):
        picked = rng.integers(0, G, size=G)
        boot[b] = sums[picked].sum() / ns[picked].sum()
    ci_lo, ci_hi = np.quantile(boot, [0.025, 0.975])
    cluster_means = np.asarray([a.mean() for a in clusters], float)
    return {
        "n_pairs": int(N), "n_expiry_clusters": int(G),
        "mean_inr_per_pair": mean, "median_inr_per_pair": median,
        "mean_cluster_mean_inr": float(cluster_means.mean()),
        "positive_expiry_cluster_fraction": float(np.mean(cluster_means > 0)),
        "cluster_robust_se": se, "cluster_robust_t": statistic, "p_value_raw": pvalue,
        "cr1_t_ci95_low": float(lo), "cr1_t_ci95_high": float(hi),
        "expiry_cluster_bootstrap_ci95_low": float(ci_lo),
        "expiry_cluster_bootstrap_ci95_high": float(ci_hi),
        "mean_two_tick_inr_per_pair": float(pd.to_numeric(frame[STRESS], errors="coerce").dropna().mean()),
        "two_tick_median_inr_per_pair": float(pd.to_numeric(frame[STRESS], errors="coerce").dropna().median()),
    }

def main():
    pair_path = BASE / "paired_window_differences.csv"
    perf_path = BASE / "summary_by_split_variant_window.csv"
    if not pair_path.is_file() or not perf_path.is_file():
        raise FileNotFoundError("Required Phase 81 derived CSVs missing; no download/fallback is allowed.")
    pairs = pd.read_csv(pair_path)
    required = {"date", "expiry", "split", "variant", PRIMARY, STRESS}
    if required.difference(pairs.columns):
        raise ValueError(f"Paired CSV missing fields: {sorted(required.difference(pairs.columns))}")
    pairs = pairs[pairs["split"].isin(SPLITS)].copy()
    pairs["expiry"] = pairs["expiry"].astype(str)
    for col in (PRIMARY, STRESS):
        pairs[col] = pd.to_numeric(pairs[col], errors="coerce")
    invalid = pairs[[PRIMARY, STRESS]].isna().any(axis=1)
    dropped = int(invalid.sum())
    pairs = pairs.loc[~invalid].copy()
    dup = pairs.duplicated(["date", "expiry", "split", "variant"], keep=False)
    if dup.any():
        raise ValueError(f"Duplicate paired date/expiry/split/variant rows: {int(dup.sum())}")
    results = []
    variants = sorted(pairs["variant"].unique())
    for si, split in enumerate(SPLITS):
        for vi, variant in enumerate(variants):
            frame = pairs[(pairs["split"] == split) & (pairs["variant"] == variant)].copy()
            if frame.empty:
                continue
            primary = cluster_inference(frame, PRIMARY, SEED + si * 10_000 + vi * 37)
            stress = cluster_inference(frame, STRESS, SEED + 500_000 + si * 10_000 + vi * 37)
            row = {"split": split, "variant": variant, **primary}
            row["two_tick_bootstrap_ci95_low"] = stress["expiry_cluster_bootstrap_ci95_low"]
            row["two_tick_bootstrap_ci95_high"] = stress["expiry_cluster_bootstrap_ci95_high"]
            row["two_tick_raw_p_value_diagnostic"] = stress["p_value_raw"]
            results.append(row)
    if len(results) != 20:
        raise ValueError(f"Expected 20 registered split×variant tests; found {len(results)}.")
    adjusted = holm_adjust([float(r["p_value_raw"]) for r in results])
    for r, p_adj in zip(results, adjusted):
        r["p_value_holm_family20"] = p_adj
        r["holm_significant_alpha_0_05"] = bool(p_adj < ALPHA)
    inference = pd.DataFrame(results).sort_values(["split", "p_value_holm_family20", "variant"])
    inference.to_csv(OUT / "cluster_inference.csv", index=False, float_format="%.8f")

    perf = pd.read_csv(perf_path)
    req_perf = {"split", "variant", "window", "total_net_1tick", "total_net_2tick"}
    if req_perf.difference(perf.columns):
        raise ValueError(f"Performance summary missing fields: {sorted(req_perf.difference(perf.columns))}")
    risk = perf[perf["variant"] != "short_atm_straddle"]
    candidate_rows = []
    # Candidate is a defined-risk structure paired with one fixed horizon.
    # That horizon must be net-positive in both DEV and VAL at both cost levels.
    for variant in sorted(risk["variant"].unique()):
        for window in ("intraday", "overnight"):
            group = risk[(risk["variant"] == variant) & (risk["window"] == window)]
            ok = True
            for split in SPLITS:
                z = group[group["split"] == split]
                if len(z) != 1 or not (float(z.iloc[0]["total_net_1tick"]) > 0 and float(z.iloc[0]["total_net_2tick"]) > 0):
                    ok = False
            candidate_rows.append({"variant": variant, "candidate_window": window, "passes_defined_risk_net_gate": bool(ok)})
    candidates = pd.DataFrame(candidate_rows)
    candidates.to_csv(OUT / "candidate_gate.csv", index=False)
    passing = int(candidates["passes_defined_risk_net_gate"].sum())

    summary = {
        "phase": 82,
        "decision": "NO_CANDIDATE_PASSES_PREDECLARED_GATE" if passing == 0 else "CANDIDATES_REQUIRE_REVIEW",
        "input": {"paired_csv": str(pair_path), "performance_csv": str(perf_path),
                  "raw_market_data_loaded": False, "2026_holdout_loaded_or_scored": False,
                  "invalid_numeric_pairs_dropped": dropped,
                  "duplicate_policy": "fail closed on duplicate date/expiry/split/variant key"},
        "method": {"primary_effect": "overnight minus intraday net P&L per matched date×variant pair in INR",
                   "primary_cost_case": "one adverse tick, Paytm Money ₹10/order and frozen Phase 81 date-aware statutory fees",
                   "stress_cost_case": "two adverse ticks; reported as robustness, not a separate primary testing family",
                   "cluster_unit": "expiry",
                   "inference": "CR1 expiry-cluster-robust t test (df=clusters−1); 10,000 expiry-cluster bootstrap percentile 95% CI",
                   "multiplicity": "Holm adjustment across 20 primary hypotheses (10 variants × DEV/VAL)",
                   "seed": SEED, "bootstrap_replicates": BOOTSTRAPS, "alpha": ALPHA},
        "coverage": {"variants": int(pairs["variant"].nunique()), "splits": sorted(pairs["split"].unique().tolist()),
                     "paired_rows": int(len(pairs)), "unique_expiry_clusters_overall": int(pairs["expiry"].nunique()),
                     "tests": len(results)},
        "candidate_gate": {"criterion": "defined-risk variant-window pair net-positive for the same horizon in both DEV and VAL at one-tick and two-tick costs",
                           "defined_risk_variants_checked": int(len(candidates)), "passing_variants": passing,
                           "holdout_action": "do not open 2026 holdout unless a variant-window candidate passes this gate and its paired effect favors that window with Holm alpha below 0.05 in both DEV and VAL"},
        "limitations": ["Inference is conditional on Phase 81 OHLC-open estimates; it does not establish executable fills.",
                        "Expiry clustering does not address every possible cross-expiry/session dependency.",
                        "A significant holding-window difference is not the same as profitable strategy returns.",
                        "The unbounded short ATM straddle is ineligible for promotion.",
                        "No 2026 holdout rows were accessed; no strategy was promoted."]
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Phase 82 — Expiry-cluster inference", "",
        f"**Decision: {summary['decision'].replace('_', ' ').lower()}. No strategy is promoted.**", "",
        f"- Paired rows: {len(pairs):,}; registered primary tests: {len(results)} (10 variants × DEV/VAL).",
        f"- Unique expiry clusters: {pairs['expiry'].nunique():,}; invalid numeric pairs dropped: {dropped}.",
        "- Primary inference: one-tick overnight-minus-intraday effect, expiry-cluster robust t test plus 10,000 cluster-bootstrap replicates.",
        "- Multiplicity: Holm correction across all 20 primary tests; two-tick stress is robustness only.",
        f"- Defined-risk variants passing the frozen profitability gate: {passing} of {len(candidates)}.",
        "- The 2026 holdout was not loaded, scored, or ranked because candidate eligibility is the prerequisite.", "",
        "## Inference results", "",
        "| Split | Variant | N pairs | Expiry clusters | Mean difference (₹/pair) | Cluster-bootstrap 95% CI | Raw p | Holm p (20 tests) | Two-tick mean (₹/pair) |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for r in inference.to_dict("records"):
        lines.append(f"| {r['split']} | {r['variant']} | {r['n_pairs']} | {r['n_expiry_clusters']} | {r['mean_inr_per_pair']:.2f} | [{r['expiry_cluster_bootstrap_ci95_low']:.2f}, {r['expiry_cluster_bootstrap_ci95_high']:.2f}] | {r['p_value_raw']:.5f} | {r['p_value_holm_family20']:.5f} | {r['mean_two_tick_inr_per_pair']:.2f} |")
    lines += ["", "## Candidate gate", "", "| Defined-risk variant / window | Passes profitability gate |", "|---|---|"]
    for r in candidates.to_dict("records"):
        lines.append(f"| {r['variant']} / {r['candidate_window']} | {'YES' if r['passes_defined_risk_net_gate'] else 'NO'} |")
    lines += ["", "## Interpretation boundary", "",
              "The estimated difference describes whether overnight net P&L differs from intraday net P&L in the registered historical OHLC-open proxy. It does not by itself identify a profitable strategy. Candidate eligibility separately requires positive net results in DEV and VAL, across both windows and both friction levels. Even positive results would need execution-grade quote/fill evidence.", "",
              "## Files", "", "- cluster_inference.csv: 20 primary tests and two-tick sensitivity.",
              "- candidate_gate.csv: frozen defined-risk profitability gate.", "- summary.json: machine-readable methods, coverage, decision and limitations.", ""]
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print((OUT / "report.md").read_text(encoding="utf-8"))

if __name__ == "__main__":
    main()
