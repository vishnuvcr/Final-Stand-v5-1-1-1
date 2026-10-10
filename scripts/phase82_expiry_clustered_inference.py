#!/usr/bin/env python3
"""Phase 82: expiry-clustered inference on frozen Phase 81 derived data."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import t as student_t

BASE = Path("results/phase81_intraday_overnight")
OUT = Path("results/phase82_inference")
FIG = OUT / "figures"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)
SEED = 820026
BOOTSTRAPS = 20000
DEV_END = pd.Timestamp("2023-12-31")
VAL_END = pd.Timestamp("2025-12-31")
UNBOUNDED = {"short_atm_straddle"}

def holm_adjust(items):
    """Holm step-down adjustment for a complete family of raw p-values."""
    n=len(items)
    order=sorted(range(n),key=lambda i: float(items[i]["p_raw"]))
    out=[1.0]*n
    running=0.0
    for rank,idx in enumerate(order):
        candidate=min(1.0,(n-rank)*float(items[idx]["p_raw"]))
        running=max(running,candidate)
        out[idx]=running
    for i,x in enumerate(items):
        x["p_holm_60"]=float(out[i])
    return items

def cluster_stats(df, value_col, seed, test_kind="profitability"):
    """Equal-weight expiry-cluster mean, t-test on independent expiry means, percentile cluster bootstrap."""
    z=df[["expiry",value_col]].dropna().copy()
    z["expiry"]=pd.to_datetime(z["expiry"],errors="coerce")
    clusters=[g[value_col].to_numpy(float) for _,g in z.groupby("expiry",sort=True)]
    clusters=[x for x in clusters if len(x)>0]
    if len(clusters)<2:
        return {"n_trades":int(len(z)),"n_expiry_clusters":len(clusters),
                "mean_per_trade":float(z[value_col].mean()) if len(z) else np.nan,
                "median_per_trade":float(z[value_col].median()) if len(z) else np.nan,
                "mean_expiry_cluster":np.nan,"ci95_lo":np.nan,"ci95_hi":np.nan,
                "p_raw":1.0,"cluster_se":np.nan}
    cl=np.asarray([float(x.mean()) for x in clusters],dtype=float)
    k=len(cl)
    obs=float(cl.mean())
    sd=float(cl.std(ddof=1))
    se=sd/np.sqrt(k)
    if se>0 and np.isfinite(se):
        stat=obs/se
        p=float(student_t.sf(stat,k-1)) if test_kind=="profitability" else float(2*student_t.sf(abs(stat),k-1))
    else:
        p=1.0 if ((obs<=0) if test_kind=="profitability" else obs==0) else (0.0 if test_kind=="profitability" else 1.0)
    rng=np.random.default_rng(seed)
    # Resample independent expiry-cluster means (equal weight per expiry cycle).
    boot=np.empty(BOOTSTRAPS,dtype=float)
    batch=2000
    for start in range(0,BOOTSTRAPS,batch):
        stop=min(BOOTSTRAPS,start+batch)
        ix=rng.integers(0,k,size=(stop-start,k))
        boot[start:stop]=cl[ix].mean(axis=1)
    lo,hi=np.quantile(boot,[0.025,0.975])
    return {"n_trades":int(len(z)),"n_expiry_clusters":k,
            "mean_per_trade":float(z[value_col].mean()),
            "median_per_trade":float(z[value_col].median()),
            "mean_expiry_cluster":obs,"ci95_lo":float(lo),"ci95_hi":float(hi),
            "p_raw":p,"cluster_se":float(se)}

def validate_inputs():
    ledger=pd.read_csv(BASE/"paired_trade_ledger.csv")
    pairs=pd.read_csv(BASE/"paired_window_differences.csv")
    for label,df in [("ledger",ledger),("pairs",pairs)]:
        date_col="date"
        dates=pd.to_datetime(df[date_col],errors="coerce")
        if dates.isna().any():
            raise RuntimeError(f"{label} contains invalid dates")
        if (dates>VAL_END).any():
            raise RuntimeError(f"{label} includes dates after 2025-12-31; holdout boundary violated")
        if not set(df["split"].dropna().unique()).issubset({"development","validation"}):
            raise RuntimeError(f"{label} includes non-DEV/VAL rows")
    ledger["date"]=pd.to_datetime(ledger["date"])
    ledger["expiry"]=pd.to_datetime(ledger["expiry"])
    pairs["date"]=pd.to_datetime(pairs["date"])
    pairs["expiry"]=pd.to_datetime(pairs["expiry"])
    if "next_date" in ledger:
        nxt=pd.to_datetime(ledger["next_date"],errors="coerce")
        if nxt.isna().any() or (nxt>VAL_END).any():
            raise RuntimeError("ledger next_date crosses the registered sample boundary")
    return ledger,pairs

def main():
    ledger,pairs=validate_inputs()
    tests=[]
    pnl_records=[]
    split_results=[]
    # Outcome hypotheses: ten structures x two windows x two friction levels = 40 p-values.
    for split in ["development","validation"]:
        sub=ledger[ledger["split"]==split].copy()
        for variant in sorted(sub["variant"].unique()):
            for window in ["intraday","overnight"]:
                g=sub[(sub["variant"]==variant)&(sub["window"]==window)].copy()
                if g.empty: continue
                for ticks,col in [(1,"net_1tick"),(2,"net_2tick")]:
                    st=cluster_stats(g,"net_1tick" if ticks==1 else "net_2tick",
                                     SEED+len(pnl_records)*17,
                                     test_kind="profitability")
                    total=float(g[col].sum())
                    rec={"split":split,"variant":variant,"window":window,
                         "friction_ticks":ticks,"risk_class":"unbounded_diagnostic_only" if variant in UNBOUNDED else "defined_risk",
                         "trades":int(len(g)),"total_net":total,"win_rate":float((g[col]>0).mean()),
                         "profit_factor":float(g.loc[g[col]>0,col].sum()/(-g.loc[g[col]<0,col].sum()))
                            if (g[col]<0).any() else None}
                    rec.update(st)
                    rec["test_id"]=f"net:{variant}:{window}:{ticks}tick"
                    rec["p_raw"]=float(st["p_raw"]) if split=="validation" else np.nan
                    rec["p_holm_60"]=np.nan
                    pnl_records.append(rec)
                    if split=="validation":
                        tests.append({"test_id":rec["test_id"],"family":"net_profitability",
                                      "hypothesis":"positive mean expiry-cluster net P&L",
                                      "p_raw":float(st["p_raw"]),"source_index":len(pnl_records)-1,
                                      "target":"pnl"})
    pnl=pd.DataFrame(pnl_records)
    horizon_records=[]
    # Horizon contrasts: ten structures x two registered friction levels = 20 p-values.
    for split in ["development","validation"]:
        sub=pairs[pairs["split"]==split].copy()
        for variant in sorted(sub["variant"].unique()):
            for ticks,col in [(1,"overnight_minus_intraday_1tick"),(2,"overnight_minus_intraday_2tick")]:
                g=sub[sub["variant"]==variant].copy()
                if g.empty: continue
                st=cluster_stats(g,col,SEED+50000+len(horizon_records)*19,
                                 test_kind="difference")
                rec={"split":split,"variant":variant,"friction_ticks":ticks,
                     "total_paired_difference":float(g[col].sum()),
                     "fraction_sessions_overnight_better":float((g[col]>0).mean()),
                     "test_id":f"horizon:{variant}:{ticks}tick"}
                rec.update(st)
                rec["p_holm_60"]=np.nan
                horizon_records.append(rec)
                if split=="validation":
                    tests.append({"test_id":rec["test_id"],"family":"horizon_difference",
                                  "hypothesis":"two-sided mean expiry-cluster overnight-minus-intraday difference",
                                  "p_raw":float(st["p_raw"]),"source_index":len(horizon_records)-1,
                                  "target":"horizon"})
    horizon=pd.DataFrame(horizon_records)
    # One 60-test family, across validation P&L and horizon hypotheses, controlling family-wise error.
    tests=holm_adjust(tests)
    adjusted=pd.DataFrame(tests)
    adj_map={r["test_id"]:r["p_holm_60"] for r in tests}
    for i,row in pnl.iterrows():
        if row["split"]=="validation":
            pnl.loc[i,"p_holm_60"]=adj_map.get(row["test_id"],np.nan)
    for i,row in horizon.iterrows():
        if row["split"]=="validation":
            horizon.loc[i,"p_holm_60"]=adj_map.get(row["test_id"],np.nan)
    pnl.to_csv(OUT/"net_profitability_inference.csv",index=False)
    horizon.to_csv(OUT/"horizon_difference_inference.csv",index=False)
    adjusted.to_csv(OUT/"validation_adjusted_test_ledger.csv",index=False)

    # Candidate gate: defined-risk only, stress net positive, 100+ trades, 50+ expiries,
    # cluster bootstrap lower bound >0 and Holm-adjusted p < .05 for the stress outcome.
    val=pnl[(pnl["split"]=="validation")&(pnl["friction_ticks"]==2)&(~pnl["variant"].isin(UNBOUNDED))].copy()
    passed=val[(val["total_net"]>0)&(val["trades"]>=100)&(val["n_expiry_clusters"]>=50)&
               (val["ci95_lo"]>0)&(val["p_holm_60"]<0.05)]
    candidate_records=passed[["variant","window","trades","n_expiry_clusters","total_net","mean_expiry_cluster","ci95_lo","ci95_hi","p_raw","p_holm_60"]].to_dict("records")
    decision="NO_CANDIDATE_GATE_PASS_HOLDOUT_REMAINS_SEALED" if not candidate_records else "DEFINED_RISK_CANDIDATE_FROZEN_FOR_SEPARATE_HOLDOUT_PHASE"

    # Primary validation summary stats; these are decision-support descriptive facts, not live claims.
    valp=pnl[pnl["split"]=="validation"]
    valh=horizon[horizon["split"]=="validation"]
    counts={"trades_rows":int(len(ledger)),"paired_difference_rows":int(len(pairs)),
            "validation_net_tests":int((pnl["split"]=="validation").sum()),
            "validation_horizon_tests":int((horizon["split"]=="validation").sum()),
            "validation_total_tests":int(len(tests))}
    summary={
      "phase":82,"decision":decision,"holdout_opened":bool(candidate_records),
      "input_revision":"Phase 81 persisted corrected run 38044579698",
      "temporal_policy":{"development_through":"2023-12-31","validation_through":"2025-12-31",
                         "holdout_2026":"not loaded/read/scored; remains sealed unless a gate passes"},
      "inference":{"cluster_unit":"listed expiry","cluster_estimand":"equal-weight mean of within-expiry daily outcomes",
                   "bootstrap_replicates":BOOTSTRAPS,"bootstrap_seed":SEED,
                   "holm_adjustment":"single family-wise family across 60 validation tests",
                   "pnl_tests_one_sided_positive":int((adjusted.family=="net_profitability").sum()),
                   "horizon_tests_two_sided":int((adjusted.family=="horizon_difference").sum()),
                   "tests_total":int(len(adjusted))},
      "candidate_gate":{"criteria":["defined-risk only","at least 100 complete validation trades",
          "at least 50 expiry clusters","positive total net at two-tick friction",
          "95% expiry-cluster bootstrap lower bound > 0","Holm-adjusted p < 0.05 across the full 60-test family"],
          "passing_candidates":candidate_records},
      "integrity":{"holdout_dates_read":False,
          "unbounded_short_atm_straddle_excluded_from_promotion":True,
          "fills":"option candle opens plus adverse tick; not bid/ask/depth-confirmed"},
      "counts":counts,
      "validation":{"defined_risk_candidates_total":int(val[val["risk_class"]=="defined_risk"].shape[0]),
          "defined_risk_positive_stress_totals":int((val[val["risk_class"]=="defined_risk"]["total_net"]>0).sum()),
          "net_positive_unbounded_diagnostic_rows":int(((val["risk_class"]=="unbounded_diagnostic_only")&(val["total_net"]>0)).sum()),
          "horizon_test_ci_include_zero":int(((valh["ci95_lo"]<=0)&(valh["ci95_hi"]>=0)).sum()),
          "horizon_test_count":int(len(valh))},
      "limits":["Inference corrects Phase 82's registered family but not every experiment attempted in earlier phases.",
          "Expiry clusters may remain correlated across time, particularly through persistent regimes.",
          "The data have OHLC but no historical bid/ask/depth; fee and tick assumptions do not prove executable prices.",
          "Phase 81 strategy set is broad but not all possible combinations."]}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False)+"\n")

    # Figures: default Matplotlib palette, no hand-chosen colors.
    hv=valh[valh["friction_ticks"]==1].sort_values("mean_expiry_cluster")
    fig,ax=plt.subplots(figsize=(10,6))
    y=np.arange(len(hv))
    ax.hlines(y, hv["ci95_lo"], hv["ci95_hi"])
    ax.plot(hv["mean_expiry_cluster"], y, "o")
    ax.axvline(0,linestyle="--")
    ax.set_yticks(y); ax.set_yticklabels(hv["variant"])
    ax.set_xlabel("Overnight minus intraday net P&L (₹ / expiry-cluster average)")
    ax.set_title("Validation horizon difference with 95% expiry-cluster bootstrap intervals")
    fig.tight_layout(); fig.savefig(FIG/"validation_horizon_difference.png",dpi=160); plt.close(fig)

    pv=valp.copy()
    pv["label"]=pv["variant"]+" | "+pv["window"]+" | "+pv["friction_ticks"].astype(int).astype(str)+" tick"
    pv=pv.sort_values(["window","friction_ticks","variant"])
    fig,ax=plt.subplots(figsize=(14,7))
    x=np.arange(len(pv))
    ax.bar(x,pv["total_net"])
    ax.axhline(0,linestyle="--")
    ax.set_xticks(x); ax.set_xticklabels(pv["label"],rotation=90,fontsize=7)
    ax.set_ylabel("Total validation net P&L (₹, 1-lot assumptions)")
    ax.set_title("Validation net P&L by structure, window and friction")
    fig.tight_layout(); fig.savefig(FIG/"validation_net_pnl.png",dpi=160); plt.close(fig)

    # Write report; include full table of Validation P&L and paired-window tests.
    lines=["# Phase 82 — Expiry-clustered inference and promotion gate","",
      f"**Decision: {decision}.**",
      "The 2026 holdout was not read because no defined-risk validation candidate passed the pre-registered two-tick promotion gate." if not candidate_records else "A candidate was frozen for a separately controlled holdout phase; no result is yet confirmed.",
      "",
      "## Integrity and inferential design",
      f"- Phase 81 source: thetrademarkk/india-index-options-1m pinned to 0f4800e43e6f96cec0794369d78eb4d3c4211ef5; corrected Phase 81 workflow run 38044579698.",
      f"- Input rows: {len(ledger):,} trade rows and {len(pairs):,} paired date×variant differences. No 2026 dates or non-DEV/VAL split was accepted.",
      f"- {len(tests)} validation hypotheses were Holm-adjusted as one family: 40 profitability tests and 20 two-sided horizon differences.",
      f"- Bootstrap resamples expiry clusters ({BOOTSTRAPS:,} iterations; fixed seed {SEED}); the estimand gives each expiry cluster equal weight.",
      "- Brokerage is assumed ₹10 per executed order, with modeled historical statutory charges and adverse ₹0.05/tick and ₹0.10/two-tick fills. OHLC is not quote/depth evidence.",
      "",
      "## Validation profitability result",
      "| Structure | Window | Friction | Trades | Expiries | Total net (₹) | Mean per trade (₹) | 95% cluster-bootstrap CI for equal-expiry mean (₹) | Raw p | Holm p |",
      "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for _,r in valp.sort_values(["variant","window","friction_ticks"]).iterrows():
        lines.append(f"| {r['variant']} | {r['window']} | {int(r['friction_ticks'])} tick | {int(r['trades'])} | {int(r['n_expiry_clusters'])} | {r['total_net']:.2f} | {r['mean_per_trade']:.2f} | [{r['ci95_lo']:.2f}, {r['ci95_hi']:.2f}] | {r['p_raw']:.4g} | {r['p_holm_60']:.4g} |")
    lines += ["","## Paired overnight-minus-intraday result (primary one-tick scenario)",
      "| Structure | Daily pairs | Expiries | Total paired difference (₹) | Mean daily diff (₹) | Equal-expiry mean (₹) | 95% cluster-bootstrap CI (₹) | Raw p | Holm p | Fraction of daily pairs with overnight better |",
      "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for _,r in valh[valh["friction_ticks"]==1].sort_values("variant").iterrows():
        lines.append(f"| {r['variant']} | {int(r['n_trades'])} | {int(r['n_expiry_clusters'])} | {r['total_paired_difference']:.2f} | {r['mean_per_trade']:.2f} | {r['mean_expiry_cluster']:.2f} | [{r['ci95_lo']:.2f}, {r['ci95_hi']:.2f}] | {r['p_raw']:.4g} | {r['p_holm_60']:.4g} | {r['fraction_sessions_overnight_better']:.3f} |")
    lines += ["","## Candidate gate",
      f"- Defined-risk candidate/window rows assessed at two-tick stress: {len(val)}.",
      f"- Defined-risk rows with positive total validation net P&L at two-tick stress: {summary['validation']['defined_risk_positive_stress_totals']}.",
      f"- Candidates passing the full frozen gate: {len(candidate_records)}.",
      "- Naked short ATM straddle is always excluded from promotion, even if its intraday net summary is positive.",
      "",
      "## Figures",
      "- ![Validation horizon differences](figures/validation_horizon_difference.png)",
      "- ![Validation P&L by structure, window and costs](figures/validation_net_pnl.png)",
      "",
      "## Interpretation and next step",
      "A statistically different holding window is not the same as a profitable strategy. The promotion gate requires positive stress-net outcome, a positive lower bootstrap bound and Holm-adjusted significance, in addition to defined risk and coverage. If no candidate passes, move to the final manuscript phase without opening the holdout; do not expand the strategy universe after looking at the results.",
      "",
      "## Limitations",
      "- Tests address the registered 60-hypothesis Phase 82 family, not every prior project experiment.",
      "- Expiry clustering does not eliminate correlation across expiries caused by long-lived market regimes.",
      "- Price references are OHLC opens with adverse ticks; there is no historical bid/ask/depth or market impact model.",
      "- Phase 81 tested ten frozen variants, not every possible strategy combination.",
      "- Bhat et al. (2024) studied delta-hedged returns; this experiment tested static structures."]
    (OUT/"report.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"phase":82,"decision":decision,"tests":len(tests),
        "candidate_rows":len(candidate_records),"defined_risk_positive_two_tick_validation_totals":summary["validation"]["defined_risk_positive_stress_totals"],
        "holdout_opened":bool(candidate_records)},indent=2))

if __name__=="__main__":
    main()
