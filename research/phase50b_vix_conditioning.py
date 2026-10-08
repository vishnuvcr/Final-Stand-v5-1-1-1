import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'research'
for p in (ROOT, RESEARCH):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from phase43_vix_strategy_sweep import load_vix, vix_state

OUT = ROOT / 'results/phase50b/vix_conditioning'
OUT.mkdir(parents=True, exist_ok=True)

STRATEGIES = {
    'TT02': ROOT / 'results/phase50b/tt02_calendar_replay/tt02_trades.csv',
    'TT03': ROOT / 'results/phase50b/tt03_dynamic_n_replay/tt03_trades.csv',
    'TT04': ROOT / 'results/phase50b/tt04_premium_match_replay/tt04_trades.csv',
    'TT05': ROOT / 'results/phase50b/tt05_short_straddle_replay/tt05_trades.csv',
}
MODES = ['LOW','NORMAL','HIGH','SPIKE','FALLING','RISING','HIGH_RISING']
SPLITS = {
    'DEV': (pd.Timestamp('1900-01-01'), pd.Timestamp('2023-12-31 23:59:59')),
    'VAL': (pd.Timestamp('2024-01-01'), pd.Timestamp('2025-12-31 23:59:59')),
    'HOLD': (pd.Timestamp('2026-01-01'), pd.Timestamp('2100-01-01')),
}

def split_for(ts):
    t = pd.Timestamp(ts)
    if t.tzinfo is not None: t = t.tz_localize(None)
    for name, (lo, hi) in SPLITS.items():
        if lo <= t <= hi: return name
    return None

def active_modes(v):
    out = {v['level_state']}
    if v['SPIKE']: out.add('SPIKE')
    if v['RISING']: out.add('RISING')
    if v['FALLING']: out.add('FALLING')
    if v['level_state'] == 'HIGH' and v['RISING']: out.add('HIGH_RISING')
    return out

def max_drawdown(values):
    if len(values) == 0: return 0.0
    x=np.asarray(values,dtype=float); eq=np.cumsum(x); peak=np.maximum.accumulate(eq)
    return float(np.max(peak-eq))

def load_feasible(strategy,path):
    d=json.loads((path.parent/'summary.json').read_text())
    if float(d.get('coverage_rate',0)) < 0.95: raise RuntimeError(f'{strategy}: coverage gate failed')
    errors=pd.read_csv(path.parent/'data_errors.csv')
    if len(errors): raise RuntimeError(f'{strategy}: non-empty data_errors.csv')
    z=pd.read_csv(path)
    req={'entry_ts','net','net50','net20','net20_50'}; missing=req-set(z.columns)
    if missing: raise RuntimeError(f'{strategy}: missing columns {sorted(missing)}')
    z['entry_ts']=pd.to_datetime(z['entry_ts'],errors='coerce')
    z=z.dropna(subset=['entry_ts','net','net50','net20','net20_50']).copy()
    z['_split']=z['entry_ts'].map(split_for)
    return z,d

def main():
    vix=load_vix(); rows=[]; audit=[]; hypotheses=[]
    for strategy,path in STRATEGIES.items():
        z,summary=load_feasible(strategy,path); mode_sets=[]
        for _,row in z.iterrows():
            ts=pd.Timestamp(row['entry_ts'])
            if ts.tzinfo is None: ts=ts.tz_localize('Asia/Kolkata')
            state=vix_state(vix,ts)
            mode_sets.append(set() if state is None else active_modes(state))
        z['_modes']=mode_sets; z['_vix_observable']=z['_modes'].map(bool)
        audit.append({'strategy':strategy,'source_trades':len(z),'vix_observable':int(z['_vix_observable'].sum()),'vix_unobservable':int((~z['_vix_observable']).sum()),'coverage_rate':float(summary['coverage_rate'])})
        for mode in MODES:
            hypotheses.append({'strategy':strategy,'vix_mode':mode,'hypothesis_id':f'{strategy}__{mode}'})
            for split in SPLITS:
                q=z[(z['_split']==split)&z['_vix_observable']&z['_modes'].map(lambda s: mode in s)].sort_values('entry_ts',kind='stable')
                comp=z[(z['_split']==split)&z['_vix_observable']&~z['_modes'].map(lambda s: mode in s)]
                rows.append({'strategy':strategy,'vix_mode':mode,'split':split,'trades':len(q),'complement_trades':len(comp),'net':float(q.net.sum()) if len(q) else 0.0,'net50':float(q.net50.sum()) if len(q) else 0.0,'net20':float(q.net20.sum()) if len(q) else 0.0,'net20_50':float(q.net20_50.sum()) if len(q) else 0.0,'mean_net':float(q.net.mean()) if len(q) else np.nan,'median_net':float(q.net.median()) if len(q) else np.nan,'win_rate':float((q.net>0).mean()) if len(q) else np.nan,'worst_trade':float(q.net.min()) if len(q) else np.nan,'max_drawdown':max_drawdown(q.net.tolist()),'complement_net':float(comp.net.sum()) if len(comp) else 0.0,'complement_mean_net':float(comp.net.mean()) if len(comp) else np.nan})
    pd.DataFrame(rows).to_csv(OUT/'vix_conditioning_by_split.csv',index=False)
    pd.DataFrame(audit).to_csv(OUT/'vix_observability_audit.csv',index=False)
    pd.DataFrame(hypotheses).to_csv(OUT/'registered_hypotheses.csv',index=False)
    meta={'status':'PASS','strategies':list(STRATEGIES),'modes':MODES,'hypotheses':len(hypotheses),'holdout_used_for_selection':False,'holdout_used_for_inference':False,'selection_rule':'NONE — all 28 registered strategy×VIX hypotheses retained','source_of_vix_state':'entry_timestamp_only','coverage_threshold':0.95}
    (OUT/'phase50b_3_manifest.json').write_text(json.dumps(meta,indent=2)); print(json.dumps(meta,indent=2))

if __name__ == '__main__': main()