#!/usr/bin/env python3
"""Build Phase-64 paper-style report and charts from aggregate strategy outputs."""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "phase64_paper_strategy_tests"
VARIANTS = ["CCI_BASE", "CCI_EMA_FILTER"]

def fmt(v):
    if v is None or pd.isna(v):
        return "NA"
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    if isinstance(v, (float, np.floating)):
        return f"{float(v):,.2f}"
    return str(v)

def main():
    summary = pd.read_csv(OUT / "summary.csv")
    audit = pd.read_csv(OUT / "opportunity_audit.csv")
    ledger = pd.read_csv(OUT / "trade_ledger.csv")
    manifest = json.loads((OUT / "source_manifest.json").read_text())
    decision = json.loads((OUT / "decision.json").read_text())

    lines = [
        "# Phase 64 — Paper-derived CCI NIFTY options strategy test",
        "",
        "**Decision: RESEARCH ONLY / NO PROMOTION.** A successful numerical run does not itself establish a tradable edge.",
        "",
        "## Research question",
        "Does the published daily CCI breakout rule on monthly NIFTY in-the-money long options produce net-positive performance in the available modern sample, and does a fixed EMA(50)/EMA(200) trend filter improve it?",
        "",
        "## Data and chronology",
        f"- Dataset: {manifest['dataset']}, revision {manifest['revision']}; published license CC-BY-NC-4.0. Raw option data is not included in this artifact.",
        f"- Index data SHA-256: {manifest['index_file']['sha256']}; size {manifest['index_file']['bytes']:,} bytes.",
        f"- Monthly-expiry proxy files loaded: {manifest['monthly_expiry_proxy_count']}; underlying minute rows: {manifest.get('index_rows_used', 'see source manifest')}.",
        f"- Latest underlying timestamp actually used: {manifest['features_max_timestamp_used']}. 2026 option files downloaded: {manifest['explicit_2026_option_files_downloaded']}.",
        "- Development period: 2021-05-27 to 2023-12-31. Validation period: 2024-01-01 to 2025-12-31. The 2026 holdout is excluded from outcomes, feature calculation, parameter selection, and statistical tests.",
        "- The source paper's original 2008–2018 period is outside the selected dataset. This is an independent modern-sample rule test, not a direct historical replication.",
        "",
        "## Frozen candidate definitions",
        "1. **CCI_BASE:** daily CCI(20) crosses above -100 for calls or below +100 for puts. Signal day must be on calendar day 3–15. A later minute close must break the signal day's high/low. Entry is at the next exact observed minute's option close using the nearest strictly ITM strike.",
        "2. **CCI_EMA_FILTER:** identical rules, but calls additionally require signal-day close > EMA50 > EMA200 and puts require close < EMA50 < EMA200. This is a new fixed hypothesis, not a direct reproduction of the moving-average article.",
        "- At most one entry per monthly-expiry proxy; earliest breakout wins; simultaneous call/put triggers are excluded as ambiguous.",
        "- CCI signal becomes known only at signal-day close. No same-day breakout, same-bar fill, interpolation, or forward-fill is allowed.",
        "- Target: option close at least 2× entry; stop: option close at or below 0.5× entry; exit at next exact minute after the target/stop trigger or at a reliable close on the last trading session before expiry.",
        "",
        "## Results by split",
        "| Variant | Split | Expiry files | Signal months | Breakout triggers | Completed trades | Trigger coverage | Win rate | Net ₹10/order | Net ₹10 +50% | Net ₹20/order | Net ₹20 +50% | Net 10% price-slip |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for row in summary.to_dict(orient="records"):
        cols = [row["variant"], row["split"], row["monthly_expiries_with_files"],
            row["qualified_signal_months"], row["breakout_months"], row["completed_trades"],
            fmt(row["entry_or_exit_coverage"]), fmt(row["win_rate"]),
            fmt(row["net_10_per_order_rupees"]), fmt(row["net_10_order_50pct_stress_rupees"]),
            fmt(row["net_20_per_order_rupees"]), fmt(row["net_20_order_50pct_stress_rupees"]),
            fmt(row["net_10_order_paper_10pct_slippage_rupees"])]
        lines.append("| " + " | ".join(map(str, cols)) + " |")
    lines += [
        "",
        "## Descriptive risk and trade statistics",
        "| Variant | Split | Mean net/trade | Median net/trade | Profit factor | Max trade-P&L drawdown | Median holding (minutes) |",
        "|---|---|---:|---:|---:|---:|---:|"
    ]
    for row in summary.to_dict(orient="records"):
        lines.append("| " + " | ".join(map(str, [
            row["variant"], row["split"], fmt(row["mean_net_per_trade"]),
            fmt(row["median_net_per_trade"]), fmt(row["profit_factor"]),
            fmt(row["max_cumulative_trade_pnl_drawdown_rupees"]),
            fmt(row["median_holding_minutes"])
        ])) + " |")
    lines += [
        "",
        "## Statistical inference",
        "Only the two frozen variants form the candidate family. For validation, a three-month moving-block bootstrap CI for mean net per trade and a block sign-flip test are attempted only with at least 20 completed trades. Holm correction is applied across computable validation p-values. Underpowered samples report SKIPPED rather than a fabricated p-value.",
        "",
        "| Variant | Validation trades | Inference status | Mean net/trade | 95% block CI | Two-sided p | Holm p |",
        "|---|---:|---|---:|---|---:|---:|"
    ]
    for variant in VARIANTS:
        v = summary.loc[(summary.variant == variant) & (summary.split == "VAL")].iloc[0]
        inf = manifest.get("statistics", {}).get(variant, {})
        ci = "NA" if inf.get("ci_low") is None else f"{fmt(inf.get('ci_low'))} to {fmt(inf.get('ci_high'))}"
        lines.append("| " + " | ".join(map(str, [variant, int(v.completed_trades),
            inf.get("status", "NOT_COMPUTED"), fmt(inf.get("mean_net_per_trade")), ci,
            fmt(inf.get("p_two_sided")), fmt(inf.get("p_holm_2_candidates"))])) + " |")
    counts = audit.groupby(["variant", "status"]).size().to_dict()
    lines += [
        "",
        "## Opportunity and data-quality audit",
        "See opportunity_audit.csv for monthly expiry, signal counts, breakout status, and exact failure reason. Coverage is completed trades divided by monthly expiries with a breakout trigger. No-strike, missing-entry, target/stop-without-next-minute-fill, and missing terminal close cases are not imputed.",
        "",
        "Audit counts: " + "; ".join(f"{k[0]} / {k[1]}: {v}" for k, v in sorted(counts.items())) + ".",
        "",
        "## Execution-cost specification",
        "- Primary execution uses observed option close plus one adverse ₹0.05 tick for entry and minus one tick for exit. Existing Phase-43 historical lot size and date-aware statutory cost helper is reused.",
        "- ₹20/order adds ₹10 per order to the accepted ₹10/order base scenario. In +50% stress, the ₹10 brokerage becomes ₹15 per order and the ₹20 brokerage becomes ₹30 per order; other monetary fees/charges are also stressed 1.5×.",
        "- Separate paper-comparability stress applies 10% adverse option-price slippage: entry price ×1.10 and exit price ×0.90, then recomputes charges. This is a sensitivity and does not replace the one-tick primary model.",
        "- Input is OHLC, not historical bid/ask/depth. These are OHLC-close proxy returns, not guaranteed or quote-faithful fills.",
        "",
        "## Interpretation",
        "Shaha (2019) reports ₹145,362 net, a 63.25% win rate and 232.16% average annual ROI for 68 trades. However, the supplied paper's chi-square table labels the total as 80 despite the body and 43 wins + 25 losses implying 68. Its two-sample test of mean winning trade versus mean loss magnitude does not directly test positive strategy expectancy. We do not import those outcomes as expected returns.",
        "The original study's 2008–2018 data are unavailable here. The selected modern source starts in 2021, has incomplete observations in less liquid options, and its CC-BY-NC-4.0 non-commercial license applies. The monthly expiry date is proxied by a late-month option file, not independently proven from exchange calendars.",
        "",
        "## Strengths",
        "- Directly specified CCI rule and one separately frozen EMA adaptation; no parameter grid.",
        "- Fixed dataset revision, SHA-256 file manifest, timezone normalization, duplicate/conflict checks, no-look-ahead and exact next-minute fill gates.",
        "- Separate DEV and VAL reporting; 2026 excluded.",
        "- Primary and stressed ₹10/₹20 costs, adverse tick slippage and separate 10% price-slippage stress.",
        "",
        "## Limitations",
        "- No direct replication of 2008–2018 data; only the available 2021–2025 interval is tested.",
        "- Monthly expiry file is a proxy and incomplete source coverage can omit a month.",
        "- OHLC does not contain bid/ask/depth, so execution realism remains limited.",
        "- One trade maximum per expiry makes the validation sample potentially small; fewer than 20 trades or <95% trigger coverage means insufficient evidence.",
        "- CCI+EMA is a new hypothesis and has not been supported by a prior options backtest.",
        "",
        "## Conclusion",
        "Phase 64 is research-only. Inspect the summary table and machine-readable decisions: positive point-estimate P&L is not confirmation. No live strategy is promoted from this phase. If the validation trade-count, coverage, all-cost and Holm-adjusted statistical gates fail, the correct result is NO-GO / INSUFFICIENT EVIDENCE.",
        "",
        "## Future research",
        "1. Acquire authorized older, longer option data if a true replication of the 2008–2018 source paper is necessary.",
        "2. If a frozen variant survives validation, pre-register a separate independent confirmation before opening a new holdout.",
        "3. Only add option Greeks, OI, bid/ask/depth or ML features after the separate Phase-52 data-rights and exact-sample gates are met.",
        "",
        "## Reproducibility files",
        "- trade_ledger.csv — completed trade outcomes only.",
        "- opportunity_audit.csv — monthly signals, breakouts and coverage failures.",
        "- summary.csv, decision.json, source_manifest.json — aggregate output and lineage.",
        "- validation_net_pnl.png and validation_equity.png — figures from this run."
    ]
    (OUT / "PHASE64_REPORT.md").write_text("\n".join(lines) + "\n")

    val = summary.loc[summary.split == "VAL"]
    metrics = ["net_10_per_order_rupees", "net_10_order_50pct_stress_rupees",
        "net_20_per_order_rupees", "net_20_order_50pct_stress_rupees"]
    labels = ["₹10/order", "₹10 +50%", "₹20/order", "₹20 +50%"]
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(VARIANTS))
    width = 0.18
    for i, metric in enumerate(metrics):
        values = [float(val.loc[val.variant == v, metric].iloc[0]) for v in VARIANTS]
        ax.bar(x + (i-1.5)*width, values, width, label=labels[i])
    ax.axhline(0, linewidth=0.8)
    ax.set_xticks(x, VARIANTS)
    ax.set_ylabel("Validation net P&L (₹)")
    ax.set_title("Phase 64 validation net P&L by cost scenario")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "validation_net_pnl.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    for variant in VARIANTS:
        z = ledger.loc[(ledger.variant == variant) & (ledger.split == "VAL")].copy()
        if not z.empty:
            z["exit_ts"] = pd.to_datetime(z.exit_ts)
            z = z.sort_values("exit_ts")
            ax.plot(np.arange(1, len(z)+1), z.net_10_per_order.cumsum(), marker="o", label=variant)
    ax.axhline(0, linewidth=0.8)
    ax.set_xlabel("Completed validation trade")
    ax.set_ylabel("Cumulative net P&L (₹10/order)")
    ax.set_title("Phase 64 validation trade-order P&L proxy")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "validation_equity.png", dpi=160)
    plt.close(fig)

if __name__ == "__main__":
    main()
