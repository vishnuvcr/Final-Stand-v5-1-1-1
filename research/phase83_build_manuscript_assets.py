#!/usr/bin/env python3
"""Build figures and supplementary tables for Phase 83 from persisted aggregate CSVs only."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

P81 = Path("results/phase81_intraday_overnight")
P82 = Path("results/phase82_expiry_cluster_inference")
OUT = Path("results/phase83_final_manuscript")
FIG = Path("figures")
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

def main():
    perf = pd.read_csv(P81 / "summary_by_split_variant_window.csv")
    inf = pd.read_csv(P82 / "cluster_inference.csv")
    cand = pd.read_csv(P82 / "candidate_gate.csv")
    s82 = json.loads((P82 / "summary.json").read_text(encoding="utf-8"))
    required_perf = {"split","variant","window","trades","total_net_1tick","total_net_2tick","mean_net_1tick","median_net_1tick","win_rate_1tick","profit_factor_1tick","max_drawdown_trade_order","total_fees_1tick"}
    required_inf = {"split","variant","n_pairs","n_expiry_clusters","mean_inr_per_pair","expiry_cluster_bootstrap_ci95_low","expiry_cluster_bootstrap_ci95_high","p_value_raw","p_value_holm_family20"}
    if required_perf.difference(perf.columns):
        raise ValueError(f"Phase 81 performance CSV lacks {sorted(required_perf.difference(perf.columns))}")
    if required_inf.difference(inf.columns):
        raise ValueError(f"Phase 82 inference CSV lacks {sorted(required_inf.difference(inf.columns))}")
    if len(perf) != 40 or len(inf) != 20 or len(cand) != 18:
        raise ValueError(f"Unexpected registered table sizes: perf={len(perf)}, inference={len(inf)}, candidate={len(cand)}")
    perf.sort_values(["variant","split","window"]).to_csv(OUT / "supplementary_performance_ledger.csv", index=False, float_format="%.8f")
    inf.sort_values(["split","variant"]).to_csv(OUT / "supplementary_inference_ledger.csv", index=False, float_format="%.8f")
    cand.sort_values(["variant","candidate_window"]).to_csv(OUT / "supplementary_candidate_gate.csv", index=False)

    # Figure 1: paired effect forest plot with expiry-cluster bootstrap percentile intervals.
    variant_order = sorted(inf["variant"].unique(), key=lambda z: (z != "short_atm_straddle", z))
    labels = [v.replace("_", " ") for v in variant_order]
    fig, axes = plt.subplots(1, 2, figsize=(16, 9), sharey=True)
    for ax, split in zip(axes, ["development", "validation"]):
        d = inf[inf["split"] == split].set_index("variant")
        ys = np.arange(len(variant_order))
        means = np.asarray([float(d.loc[v, "mean_inr_per_pair"]) for v in variant_order])
        lows = np.asarray([float(d.loc[v, "expiry_cluster_bootstrap_ci95_low"]) for v in variant_order])
        highs = np.asarray([float(d.loc[v, "expiry_cluster_bootstrap_ci95_high"]) for v in variant_order])
        ax.errorbar(means, ys, xerr=np.vstack([means - lows, highs - means]), fmt="o", capsize=3, linewidth=1.2)
        ax.axvline(0, linestyle="--", linewidth=1)
        ax.set_title(split.title())
        ax.set_xlabel("Overnight − intraday net P&L (₹ per paired observation)")
        ax.grid(axis="x", alpha=0.25)
    axes[0].set_yticks(np.arange(len(labels)), labels)
    axes[0].invert_yaxis()
    fig.suptitle("Figure 1. Paired holding-window effect with expiry-cluster bootstrap 95% intervals")
    fig.tight_layout(rect=[0,0,1,0.95])
    fig.savefig(FIG / "phase83_forest_plot.svg", bbox_inches="tight")
    fig.savefig(FIG / "phase83_forest_plot.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Figure 2: absolute net P&L per split and window at the primary one-tick costs.
    columns = [("development","intraday"),("development","overnight"),("validation","intraday"),("validation","overnight")]
    matrix = np.zeros((len(variant_order), len(columns)), dtype=float)
    for i, variant in enumerate(variant_order):
        for j, (split, window) in enumerate(columns):
            r = perf[(perf["variant"] == variant) & (perf["split"] == split) & (perf["window"] == window)]
            if len(r) != 1:
                raise ValueError(f"Expected one performance row for {(variant,split,window)}, got {len(r)}")
            matrix[i,j] = float(r.iloc[0]["total_net_1tick"])
    bound = max(float(np.nanmax(np.abs(matrix))), 1.0)
    fig, ax = plt.subplots(figsize=(12, 8))
    im = ax.imshow(matrix, aspect="auto", cmap="RdYlGn", vmin=-bound, vmax=bound)
    ax.set_yticks(np.arange(len(variant_order)), labels)
    ax.set_xticks(np.arange(4), ["DEV / intraday", "DEV / overnight", "VAL / intraday", "VAL / overnight"])
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i,j]/1000:+.1f}k", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="Total net P&L (₹, one-tick model)")
    ax.set_title("Figure 2. Absolute net P&L by structure, split and holding window")
    fig.tight_layout()
    fig.savefig(FIG / "phase83_net_pnl_heatmap.svg", bbox_inches="tight")
    fig.savefig(FIG / "phase83_net_pnl_heatmap.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    counts = {
        "phase": 83,
        "build": "from Phase 81/82 derived aggregate summaries only",
        "raw_market_data_loaded": False,
        "2026_holdout_loaded_or_scored": False,
        "performance_rows": int(len(perf)),
        "inference_tests": int(len(inf)),
        "defined_risk_horizon_gates": int(len(cand)),
        "defined_risk_candidates_passing": int(cand["passes_defined_risk_net_gate"].sum()),
        "all_defined_risk_totals_negative_in_all_split_horizon_cost_cases": bool(
            (perf[perf["variant"] != "short_atm_straddle"]["total_net_1tick"] < 0).all()
            and (perf[perf["variant"] != "short_atm_straddle"]["total_net_2tick"] < 0).all()
        ),
        "holm_significant_primary_tests": int(inf["holm_significant_alpha_0_05"].astype(bool).sum()),
        "phase82_decision": s82["decision"],
        "figures": [
            "figures/phase83_forest_plot.svg",
            "figures/phase83_forest_plot.png",
            "figures/phase83_net_pnl_heatmap.svg",
            "figures/phase83_net_pnl_heatmap.png"
        ]
    }
    (OUT / "build_summary.json").write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(counts, indent=2))

if __name__ == "__main__":
    main()
