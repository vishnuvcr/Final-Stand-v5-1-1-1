import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(".")
OUT = ROOT / "results/phase41_regime_policy"
SEL = json.load(open(OUT / "selection.json"))
SEQ = pd.read_csv(OUT / "sequential_summary.csv")
top = SEL["top3_frozen_before_holdout"]

def row(rank, period):
    x = SEQ[(SEQ["rank"] == rank) & (SEQ["period"] == period)]
    return x.iloc[0].to_dict() if len(x) else {}

def diagnostics(split):
    p = OUT / f"diagnostics_{split}.json"
    return json.load(open(p)) if p.exists() else {}

def concentration(rank):
    f = OUT / f"sequential_candidate_{rank}.csv"
    if not f.exists():
        return {"available": False}
    x = pd.read_csv(f)
    x = x[x["period"].isin(["validation","holdout"])].copy()
    if x.empty:
        return {"available": False}
    by = x.groupby(["period","expiry"])["policy_net_rupees"].sum()
    ctl = pd.concat([
        pd.read_csv("results/phase39_data/development_control_trades_2021_2023.csv"),
        pd.read_csv("results/phase39_data/frozen_control_trades_2024_2026-06-30.csv")
    ], ignore_index=True)
    ctl["period"] = np.where(pd.to_datetime(ctl["expiry"]).dt.year <= 2023, "development",
                             np.where(pd.to_datetime(ctl["expiry"]).dt.year <= 2025, "validation", "holdout"))
    byc = ctl[ctl["period"].isin(["validation","holdout"])].groupby(["period","expiry"])["net_rupees"].sum()
    d = by - byc.reindex(by.index).fillna(0.0)
    out = {}
    for per in ["validation","holdout"]:
        z = d[d.index.get_level_values(0) == per].to_numpy(float)
        total_pos = float(z[z > 0].sum()) if np.any(z > 0) else 0.0
        out[per] = {
            "max_abs_expiry_uplift": float(np.max(np.abs(z))) if len(z) else 0.0,
            "positive_uplift_sum": total_pos,
            "max_abs_share_of_positive_uplift": float(np.max(np.abs(z)) / total_pos) if total_pos > 0 else float("inf")
        }
    return {"available": True, **out}

def action_asymmetry(rank):
    f = OUT / f"sequential_candidate_{rank}.csv"
    if not f.exists():
        return {}
    x = pd.read_csv(f)
    out = {}
    for per in ["validation","holdout"]:
        z = x[x["period"] == per]
        out[per] = {
            "call_trades": int((z["action"] == "CALL").sum()),
            "put_trades": int((z["action"] == "PUT").sum()),
            "call_net": float(z.loc[z["action"] == "CALL", "policy_net_rupees"].sum()),
            "put_net": float(z.loc[z["action"] == "PUT", "policy_net_rupees"].sum())
        }
    return out

checks = []
for rank in range(1, len(top) + 1):
    d = row(rank, "development")
    v = row(rank, "validation")
    h = row(rank, "holdout")
    ci_low = float(v.get("boot_ci_mean_low", np.nan))
    hold_ci_low = float(h.get("boot_ci_mean_low", np.nan))
    validation_dd = float(v.get("policy_drawdown_rupees", np.nan))
    validation_control_dd = float(v.get("control_drawdown_rupees", np.nan))
    hold_dd = float(h.get("policy_drawdown_rupees", np.nan))
    hold_control_dd = float(h.get("control_drawdown_rupees", np.nan))
    stress = float(v.get("cost_stress_150pct_uplift", np.nan))
    hold_stress = float(h.get("cost_stress_150pct_uplift", np.nan))
    conc = concentration(rank)
    hold_overrides = int(h.get("overrides", 0))
    primary = {
        "positive_validation": float(v.get("uplift_rupees", 0)) > 0,
        "positive_holdout": float(h.get("uplift_rupees", 0)) > 0,
        "validation_drawdown_ok": validation_dd <= 1.25 * validation_control_dd if np.isfinite(validation_dd) and validation_control_dd > 0 else False,
        "holdout_drawdown_ok": hold_dd <= 1.25 * hold_control_dd if np.isfinite(hold_dd) and hold_control_dd > 0 else False,
        "validation_bootstrap_lower_nonnegative": np.isfinite(ci_low) and ci_low >= 0,
        "holdout_bootstrap_lower_nonnegative": np.isfinite(hold_ci_low) and hold_ci_low >= 0,
        "validation_plus50_cost_stress_positive": np.isfinite(stress) and stress > 0,
        "holdout_plus50_cost_stress_positive": np.isfinite(hold_stress) and hold_stress > 0,
        "holdout_overrides_at_least_5": hold_overrides >= 5,
        "expiry_concentration_validation_ok": conc.get("validation", {}).get("max_abs_share_of_positive_uplift", np.inf) <= 0.40,
        "expiry_concentration_holdout_ok": conc.get("holdout", {}).get("max_abs_share_of_positive_uplift", np.inf) <= 0.40,
    }
    checks.append({
        "rank": rank,
        "model": v.get("model"),
        "margin": v.get("margin"),
        "gate": v.get("gate"),
        "promotion_pass": all(primary.values()),
        "checks": primary,
        "concentration": conc,
        "action_asymmetry": action_asymmetry(rank)
    })

diag_v = diagnostics("validation")
diag_h = diagnostics("holdout")

grid = pd.read_csv(OUT / "fixed_grid_validation.csv")
grid["label"] = grid["model"].str.replace("_VIX", "", regex=False) + " | " + grid["margin"].astype(int).astype(str) + " | " + grid["gate"]
g = grid.sort_values("validation_uplift", ascending=True)
plt.figure(figsize=(10, 7))
plt.barh(g["label"], g["validation_uplift"])
plt.axvline(0, linewidth=1)
plt.title("Phase 41 fixed-opportunity validation uplift: all 24 preregistered variants")
plt.xlabel("Validation uplift vs canonical control (rupees)")
plt.tight_layout()
plt.savefig(OUT / "phase41_validation_grid.png", dpi=160)
plt.close()

rows = []
for r in range(1, len(top) + 1):
    v = row(r, "validation")
    h = row(r, "holdout")
    rows.append({
        "label": f"Rank {r} {v.get('model','')} / {int(v.get('margin',0))} / {v.get('gate','')}",
        "Validation": float(v.get("uplift_rupees", 0)),
        "Holdout": float(h.get("uplift_rupees", 0))
    })
plotdf = pd.DataFrame(rows).set_index("label")
ax = plotdf.plot(kind="bar", figsize=(10, 6))
ax.axhline(0, linewidth=1)
ax.set_ylabel("Sequential uplift vs canonical control (rupees)")
ax.set_title("Phase 41 frozen top-3 exact sequential replay")
plt.tight_layout()
plt.savefig(OUT / "phase41_top3_sequential.png", dpi=160)
plt.close()

lines = [
"# Phase 41 Manuscript — Regime-Conditional Counterfactual Policy Learning",
"",
"## Abstract",
"",
"Phase 41 tested a bounded regime-conditional economic-margin policy family after Phase 39 showed the promise of counterfactual learning and Phase 40 showed that India VIX was more useful as a routing variable than as a direct direction signal. Twenty-four pre-registered variants were evaluated with expanding-window chronology on a 477-opportunity fixed counterfactual panel. The canonical stateful strategy remained the default action. The top three validation policies were frozen before the 2026 holdout was evaluated, then replayed through the exact sequential trading engine with the repository one-tick adverse slippage, brokerage and statutory-cost model.",
"",
"## Research questions",
"",
"1. Does explicit India-VIX regime state improve control-relative economic-margin prediction?",
"2. Does the policy concentrate positive CALL-versus-PUT counterfactual value in its highest-scored states?",
"3. Does the apparent override value persist under matched-state diagnostics?",
"4. Does it survive exact sequential replay, the untouched 2026 holdout and cost stress?",
"5. Is India VIX more useful as a regime/router than as a direct directional predictor?",
"",
"## Aims and objectives",
"",
"The primary aim was to identify a small, pre-registered regime-conditional override policy that improves the canonical strategy without materially worsening risk. Secondary objectives were to quantify India-VIX routing value, test ranking concentration, examine treatment-overlap diagnostics and preserve strict chronology.",
"",
"## Scientific methodology",
"",
"### Data",
"Accepted fixed-opportunity panel: 477 opportunities; 271 development / 172 validation / 34 untouched holdout. Both hypothetical CALL and PUT spread outcomes were already available in the accepted Phase-39 ledger. The feature layer contains point-in-time NIFTY, option, global-market, FII/DII, sentiment and volatility variables. India VIX was aligned using the prior available session and development-only thresholds.",
"",
"### Candidate family",
"Two learners were registered: a low-capacity spline-Ridge economic-margin model with explicit VIX interactions and a shallow ExtraTrees margin learner. Each was crossed with four override margins (0/250/500/1000 rupees) and three VIX routing gates (ALL/HIGH_VIX/HIGH_VIX_RISING), giving exactly 24 declared variants.",
"",
"### Chronology and execution",
"Each prediction used only earlier observations, with a 100-opportunity warm-up. The economic target was DeltaP&L = CALL net P&L minus PUT net P&L. Overrides were scored as the model predicted improvement over the current canonical direction minus one uncertainty unit. Exact sequential replay allowed the selected direction to change the exit timestamp and therefore future entries. One adverse tick of slippage, four order executions per spread, historical lot sizes, brokerage and date-aware statutory charges were retained.",
"",
"### Selection discipline",
"The top three candidates were selected using development/validation results only. The 2026 holdout was not used to tune model, margin or routing gate. Propensity matching used only pre-evaluation history for propensity fitting and was treated strictly as a selection-overlap diagnostic. Ranking diagnostics examined the observed counterfactual DeltaP&L concentration in the top 10%, 20% and 30% model-score groups.",
"",
"## Pre-registered hypotheses",
"",
"H1: explicit volatility-regime context improves economic-margin prediction and override quality.",
"H2: the best regime-conditional policy yields positive sequential validation and untouched-holdout incremental P&L with acceptable drawdown and execution-cost robustness.",
"",
"## Results",
"",
"### Fixed-opportunity screen",
"Twenty-four declared variants were completed. The validation ranking and complete grid are stored in results/phase41_regime_policy/fixed_grid_validation.csv. The top-three freeze is stored in results/phase41_regime_policy/selection.json.",
"",
"![Validation grid](results/phase41_regime_policy/phase41_validation_grid.png)",
"",
"### Frozen candidates",
"",
"| Rank | Model | Margin | Gate | Validation uplift | Holdout uplift | Holdout overrides |",
"|---:|---|---:|---|---:|---:|---:|"
]
for r in range(1, len(top) + 1):
    v = row(r, "validation")
    h = row(r, "holdout")
    lines.append(f"| {r} | {v.get('model','')} | {float(v.get('margin',0)):.0f} | {v.get('gate','')} | {float(v.get('uplift_rupees',0)):,.2f} | {float(h.get('uplift_rupees',0)):,.2f} | {int(h.get('overrides',0))} |")

lines += [
"",
"![Top three sequential results](results/phase41_regime_policy/phase41_top3_sequential.png)",
"",
"### Paired-expiry inference",
"",
"Results below use 10,000 paired-expiry bootstrap resamples and paired sign-flip inference. The 95% interval is reported for the mean expiry-level incremental P&L; the holdout is the principal generalization test.",
"",
"| Rank | Period | Mean uplift/expiry | 95% CI low | 95% CI high | One-sided p | Positive expiry share |",
"|---:|---|---:|---:|---:|---:|---:|"
]
for r in range(1, len(top) + 1):
    for per in ["validation", "holdout"]:
        z = row(r, per)
        lines.append(f"| {r} | {per} | {float(z.get('boot_mean_uplift_per_expiry',np.nan)):,.2f} | {float(z.get('boot_ci_mean_low',np.nan)):,.2f} | {float(z.get('boot_ci_mean_high',np.nan)):,.2f} | {float(z.get('boot_p_one_sided',np.nan)):.4f} | {float(z.get('boot_positive_expiry_share',np.nan)):.1%} |")

lines += [
"",
"### Cost stress",
"",
"| Rank | Period | +25% cost uplift | +50% cost uplift | +100% cost uplift |",
"|---:|---|---:|---:|---:|"
]
for r in range(1, len(top) + 1):
    for per in ["validation", "holdout"]:
        z = row(r, per)
        lines.append(f"| {r} | {per} | {float(z.get('cost_stress_125pct_uplift',np.nan)):,.2f} | {float(z.get('cost_stress_150pct_uplift',np.nan)):,.2f} | {float(z.get('cost_stress_200pct_uplift',np.nan)):,.2f} |")

lines += [
"",
"### Selection-overlap diagnostics",
"",
"Validation propensity diagnostic: " + json.dumps(diag_v.get("propensity", {}), sort_keys=True) + ".",
"Holdout propensity diagnostic: " + json.dumps(diag_h.get("propensity", {}), sort_keys=True) + ".",
"",
"These matched-state calculations do not establish causal efficacy. They diagnose whether override opportunities have usable common-support analogues.",
"",
"### Ranking diagnostics",
"",
"Validation ranking: " + json.dumps(diag_v.get("ranking", {}), sort_keys=True) + ".",
"Holdout ranking: " + json.dumps(diag_h.get("ranking", {}), sort_keys=True) + ".",
"",
"## Statistical inference and decision",
"",
"Promotion was evaluated against the pre-registered quantitative gates. A policy must simultaneously show positive sequential validation and holdout uplift, acceptable drawdown in both periods, non-negative paired-expiry confidence lower bounds, positive +50% cost-stress uplift, at least five holdout overrides, and no expiry-level concentration above 40% of total positive OOS uplift.",
"",
"| Rank | Promotion gate result |",
"|---:|---|"
]
for c in checks:
    lines.append(f"| {c['rank']} | {'PASS' if c['promotion_pass'] else 'FAIL'} |")

lines += [
"",
"## Discussion",
"",
"The primary scientific question is not whether a point estimate is positive but whether the result is stable under chronology, control-relative inference and the untouched holdout. The phase therefore treats the fixed-opportunity oracle and raw validation ranking as exploratory and uses sequential replay for the trading claim.",
"",
"India VIX remains scientifically interesting as a state variable. This phase was intentionally narrow: it did not add another unrestricted classifier family. The result is interpreted together with Phase 40, where high-VIX routing was the strongest validation cluster but remained statistically inconclusive on holdout.",
"",
"## Strengths",
"",
"- Explicit counterfactual action target rather than indirect market-direction classification.",
"- Frozen 24-variant universe and holdout discipline.",
"- Strict expanding-window chronology and deterministic point-in-time VIX alignment.",
"- Exact sequential replay with the established one-tick adverse slippage, brokerage, statutory charges and lot-size schedule.",
"- Matched-state and ranking diagnostics in addition to P&L.",
"",
"## Limitations",
"",
"- Only 20 holdout expiry blocks are present in the accepted counterfactual panel.",
"- The policy is learned from a small number of independent expiry-level states.",
"- Propensity matching is not causal identification because treatment is policy-generated and both counterfactual arms are available in the historical panel.",
"- Historical one-minute data do not fully reproduce live bid/ask fill probability, latency or queue position.",
"- The base historical execution model uses one adverse slippage tick; larger slippage was not re-optimized because the research goal was fixed-policy robustness rather than threshold retuning.",
"",
"## Conclusion",
"",
"The Phase-41 registered research phase is closed. The canonical stateful strategy remains unchanged unless an accepted candidate satisfies the complete promotion screen. India VIX is retained as a regime/routing research variable rather than a promoted direct direction predictor.",
"",
"## Future direction",
"",
"The next scientifically valuable step is prospective and paper validation using broker-quality bid/ask and fill data, together with a longer untouched sample. Another unrestricted classifier sweep is not justified by the present evidence.",
"",
"## Reproducibility artifacts",
"",
"- PHASE41_RESEARCH_PLAN.md",
"- PHASE41_PRE_REGISTRATION.md",
"- PHASE41_LITERATURE_REVIEW.md",
"- results/phase41_regime_policy/fixed_grid_validation.csv",
"- results/phase41_regime_policy/selection.json",
"- results/phase41_regime_policy/frozen_top3_fixed_results.csv",
"- results/phase41_regime_policy/sequential_summary.csv",
"- results/phase41_regime_policy/sequential_candidate_*.csv",
"- results/phase41_regime_policy/diagnostics_validation.json",
"- results/phase41_regime_policy/diagnostics_holdout.json",
"- results/phase41_regime_policy/phase41_validation_grid.png",
"- results/phase41_regime_policy/phase41_top3_sequential.png",
"- ERROR_LOG.md and RESEARCH_LOG.md"
]

(OUT / "PHASE41_MANUSCRIPT_GENERATED.md").write_text("\n".join(lines) + "\n")
(ROOT / "PHASE41_MANUSCRIPT.md").write_text("\n".join(lines) + "\n")

status = {
    "phase":"41",
    "status":"COMPLETE",
    "declared_variants":24,
    "eligible_count":int(SEL.get("eligible_count",0)),
    "decision":"PROMOTED" if checks and checks[0]["promotion_pass"] else "NO PROMOTION — CANONICAL STRATEGY UNCHANGED",
    "top3_frozen":top,
    "promotion_checks":checks,
    "validation_diagnostics":diag_v,
    "holdout_diagnostics":diag_h
}
(OUT / "final_decision.json").write_text(json.dumps(status, indent=2, default=str))

decision = status["decision"]
(ROOT / "PHASE41_STATUS.md").write_text(
    "# Phase 41 Status — Regime-Conditional Counterfactual Policy Learning\n\n"
    f"**COMPLETE — {decision}**\n\n"
    "The registered 24-variant regime-conditional economic-margin phase was executed. "
    "The top three policies were frozen from development/validation before the untouched 2026 holdout was evaluated. "
    "Exact sequential replay, paired-expiry inference, cost stress, propensity-overlap diagnostics and ranking diagnostics were completed.\n\n"
    f"Declared variants: **24**\n\nValidation-eligible variants: **{int(SEL.get('eligible_count',0))}**\n\n"
    "The canonical Phase-32 stateful strategy remains unchanged unless an accepted candidate satisfies every registered promotion gate.\n\n"
    "See PHASE41_MANUSCRIPT.md and results/phase41_regime_policy/final_decision.json for the complete evidence package.\n"
)
log = ROOT / "RESEARCH_LOG.md"
lc = log.read_text()
lc += "\n\n## 2026-10-06 — Phase 41 closeout\n- Completed the preregistered 24-variant regime-conditional economic-margin screen, top-three freeze, exact sequential replay, paired-expiry inference, cost stress, propensity-overlap and ranking diagnostics.\n- Promotion decision is recorded in results/phase41_regime_policy/final_decision.json; no change is made to the canonical strategy unless every registered gate passes.\n"
log.write_text(lc)
err = ROOT / "ERROR_LOG.md"
ec = err.read_text()
ec += "\n\n## 2026-10-06 — Phase 41 implementation correction before numerical execution\n- Propensity-score fitting in the first draft was incorrectly fit inside each evaluation split. The code was corrected before any accepted numerical run: validation matching now fits propensity on development history only; holdout matching fits on development+validation history only.\n- This was a methodology-chronology correction only; no research parameter, outcome definition or trading rule changed.\n\n## 2026-10-06 — Phase 41 accepted execution status\n- Numerical evidence is accepted only from the GitHub Actions run that completes preflight, the frozen 24-variant screen, exact sequential replay and closeout without protocol changes.\n"
err.write_text(ec)
print(json.dumps(status, indent=2, default=str))
