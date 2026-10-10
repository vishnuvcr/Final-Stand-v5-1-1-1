#!/usr/bin/env python3
"""Descriptive expiry-cluster bootstrap of frozen Phase 51-3 trade ledgers."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'results/phase51/available_oos'; OUT=ROOT/'results/phase77_partial_oos_inference'
CASES=['net','net50','net20','net20_50']; EXPECTED={'tt02':13,'tt04':62,'tt05':62}; SEED=771026; N_BOOT=10000

def q(x): return [float(v) for v in np.quantile(x,[.025,.5,.975])]
def max_dd(s):
    c=np.cumsum(np.asarray(s,dtype=float)); peak=np.maximum.accumulate(np.r_[0.0,c]); return float(np.max(peak-np.r_[0.0,c]))

def main():
    rng=np.random.default_rng(SEED); ledger_results={}; errors=[]
    for name in ['tt02','tt04','tt05']:
        file={'tt02':'tt02_trades.csv','tt04':'tt04_trades.csv','tt05':'tt05_trades.csv'}[name]
        frame=pd.read_csv(BASE/name/file); needed={'net','net50','net20','net20_50','expiry'}; missing=sorted(needed-set(frame.columns))
        if missing: errors.append(f'{name}: missing columns {missing}'); continue
        frame['expiry']=pd.to_datetime(frame['expiry'],errors='coerce').dt.strftime('%Y-%m-%d')
        if frame['expiry'].isna().any(): errors.append(f'{name}: null expiry values')
        if len(frame)!=EXPECTED[name]: errors.append(f'{name}: trade count {len(frame)} != expected {EXPECTED[name]}')
        summary=json.loads((BASE/name/'summary.json').read_text()); published=summary.get('net'); ledger=float(frame['net'].sum())
        if published is None or abs(ledger-float(published))>0.02: errors.append(f'{name}: net ledger {ledger:.4f} != summary {published}')
        grouped=frame.groupby('expiry',dropna=False); keys=list(grouped.groups.keys()); counts=np.array([len(grouped.groups[k]) for k in keys],dtype=int)
        case_results={}
        for case in CASES:
            values=frame[case].astype(float).to_numpy(); cluster_totals=np.array([float(grouped[case].sum().loc[k]) for k in keys])
            # Vectorized cluster resampling, deterministic seed; rows are bootstrap replicates.
            indices=rng.integers(0,len(cluster_totals),size=(N_BOOT,len(cluster_totals)))
            boot_totals=cluster_totals[indices].sum(axis=1); boot_counts=counts[indices].sum(axis=1)
            boot_means=boot_totals/np.maximum(boot_counts,1)
            case_results[case]={'ledger_total_net':float(values.sum()),'mean_per_trade':float(values.mean()),'median_per_trade':float(np.median(values)),
              'win_rate':float((values>0).mean()),'max_cumulative_trade_pnl_drawdown':max_dd(values),
              'bootstrap_total_net_ci95_percentile':q(boot_totals),'bootstrap_mean_trade_net_ci95_percentile':q(boot_means),
              'bootstrap_fraction_total_net_positive':float((boot_totals>0).mean())}
        ledger_results[name]={'trade_count':int(len(frame)),'expiry_cluster_count':int(frame['expiry'].nunique()),
          'first_entry_date':str(pd.to_datetime(frame['entry_ts'],errors='coerce').min()) if 'entry_ts' in frame else None,
          'last_entry_date':str(pd.to_datetime(frame['entry_ts'],errors='coerce').max()) if 'entry_ts' in frame else None,
          'published_summary_net':float(published) if published is not None else None,'ledger_net_sum':ledger,
          'ledger_summary_abs_difference':abs(ledger-float(published)) if published is not None else None,'cases':case_results}
    decision='AUDIT_PASS_DESCRIPTIVE_ONLY' if not errors and set(ledger_results)==set(EXPECTED) else 'AUDIT_FAILED_RECONCILIATION'
    result={'phase':77,'decision':decision,'window':['2026-04-21','2026-07-21'],'missing_expiries_excluded':['2026-07-28','2026-08-04'],
      'source':'Frozen Phase 51-3 trade CSVs and summaries; no new price downloads','bootstrap':{'unit':'expiry cluster','replicates':N_BOOT,'seed':SEED,'interval':'95% percentile','interpretation':'descriptive only; not a confirmatory p-value or posterior probability'},
      'errors':errors,'strategies':ledger_results,'promotion':'NONE','caveat':'Only 14 expiry dates exist in the source interval. The two missing later expiries are excluded. The short sample and strategy selection mean bootstrap outputs cannot establish a persistent edge.'}
    OUT.mkdir(parents=True,exist_ok=True); (OUT/'summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    lines=['# Phase 77 — Partial-OOS expiry-cluster inference audit','',f"Decision: **{decision}**",'','## Coverage and exclusions','','Validated interval: 2026-04-21 through 2026-07-21. Missing expiry dates 2026-07-28 and 2026-08-04 are explicitly excluded; no synthetic data are used.','','## Results','','| Strategy | Trades | Expiry clusters | Net ₹10/order | Net +50% friction | Net ₹20/order | Net ₹20/order +50% | Bootstrap fraction total > 0, base | Bootstrap fraction total > 0, max friction |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name,d in ledger_results.items():
        c=d['cases']; lines.append(f"| {name.upper()} | {d['trade_count']} | {d['expiry_cluster_count']} | ₹{c['net']['ledger_total_net']:.2f} | ₹{c['net50']['ledger_total_net']:.2f} | ₹{c['net20']['ledger_total_net']:.2f} | ₹{c['net20_50']['ledger_total_net']:.2f} | {c['net']['bootstrap_fraction_total_net_positive']:.3f} | {c['net20_50']['bootstrap_fraction_total_net_positive']:.3f} |")
    lines += ['', '## Uncertainty','','For each cost scenario, 10,000 expiry-cluster bootstrap replicates resample expiry clusters rather than individual trades. Percentile intervals are reported for total net P&L and mean net per trade in `summary.json`. With only 14 expiry clusters, these intervals are unstable and descriptive only.','','## Audit and interpretation','',f"Ledger reconciliation errors: {len(errors)}.",'No strategy is promoted. Positive bootstrap fractions do not mean the strategy has that probability of being profitable in the future. The data interval is short and excludes the two later missing expiries. All published net values retain the frozen Paytm Money cost/friction model; no new costs or execution assumptions were added.','','## Errors','']
    lines += [f'- {e}' for e in errors] if errors else ['- None detected in count/net reconciliation.']
    (OUT/'report.md').write_text('\n'.join(lines)+'\n'); print(json.dumps({'decision':decision,'errors':errors,'strategies':{k:{'trades':v['trade_count'],'clusters':v['expiry_cluster_count'],'base_net':v['cases']['net']['ledger_total_net'],'max_friction_net':v['cases']['net20_50']['ledger_total_net']} for k,v in ledger_results.items()}},indent=2))
    if errors: raise SystemExit(2)
if __name__=='__main__': main()
