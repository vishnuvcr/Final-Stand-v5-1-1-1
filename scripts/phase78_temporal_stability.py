#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P50=ROOT/'results/phase50b'; P51=ROOT/'results/phase51/available_oos'; OUT=ROOT/'results/phase78_temporal_stability'
FILES={'TT-04':(P50/'tt04_premium_match_replay/summary.json',P51/'tt04/summary.json'),'TT-05':(P50/'tt05_short_straddle_replay/summary.json',P51/'tt05/summary.json'),'TT-02':(P50/'tt02_calendar_replay/summary.json',P51/'tt02/summary.json')}
CASES=['net','net50','net20','net20_50']
def load(p):
 if not p.is_file(): raise FileNotFoundError(str(p))
 return json.loads(p.read_text())
def get_cases(d): return {k:float(d[k]) for k in CASES if k in d and isinstance(d[k],(int,float))}
def main():
 out={}; errors=[]
 for strategy,(oldp,newp) in FILES.items():
  try: old=load(oldp); new=load(newp)
  except Exception as e: errors.append(f'{strategy}: {e}'); continue
  if old.get('strategy') not in (strategy,strategy.replace('-','')): errors.append(f'{strategy}: unexpected historical strategy identity {old.get("strategy")}')
  oldsplits={x.get('split'):x for x in old.get('splits',[])}
  hold=oldsplits.get('HOLD',{})
  hist={split:get_cases(v) for split,v in oldsplits.items()}
  partial=get_cases(new)
  for key in CASES:
   if key not in partial: errors.append(f'{strategy}: partial summary missing {key}')
  holdcases=get_cases(hold)
  out[strategy]={'historical_engine_revision':old.get('engine_revision'),'partial_engine_revision':new.get('engine_revision'),
   'historical_total':get_cases(old),'historical_splits':hist,'partial_oos':partial,
   'historical_hold_trades':hold.get('trades'),'partial_oos_trades':new.get('trades'),
   'partial_window':new.get('phase51_3_window'),'partial_oos_only':new.get('partial_oos_only'),
   'hold_negative_all_cases':all(holdcases.get(k,0)>=0 for k in [] ) if False else all(k in holdcases and holdcases[k]<0 for k in CASES),
   'partial_positive_all_cases':all(k in partial and partial[k]>0 for k in CASES),
   'temporal_sign_disagreement':bool(holdcases and partial and any(holdcases.get(k,0)<0 and partial.get(k,0)>0 for k in CASES))}
 decision='AUDIT_FAILED' if errors or set(out)!=set(FILES) else 'NO_PROMOTION_TEMPORAL_STABILITY_FAIL' if any(out[s]['temporal_sign_disagreement'] for s in ['TT-04','TT-05'] if s in out) else 'DESCRIPTIVE_RECONCILIATION'
 result={'phase':78,'decision':decision,'errors':errors,'strategies':out,'excluded_expiries':['2026-07-28','2026-08-04'],'interpretation':'The historical split and partial-OOS window are not independent confirmation. A short positive interval does not erase a negative frozen HOLD result. No strategy promotion.'}
 OUT.mkdir(parents=True,exist_ok=True); (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
 lines=['# Phase 78 — Temporal stability reconciliation','',f'**Decision: {decision}**','','## Results','','| Strategy | Historical HOLD trades | Historical HOLD net ₹10/order | HOLD +50% friction | HOLD ₹20/order | HOLD ₹20/order +50% | Partial trades | Partial net ₹10/order | Partial +50% friction | Partial ₹20/order | Partial ₹20/order +50% |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
 for s,d in out.items():
  h=d['historical_splits'].get('HOLD',{}); p=d['partial_oos']; lines.append(f"| {s} | {d['historical_hold_trades']} | {h.get('net') if h.get('net') is not None else 'NA'} | {h.get('net50') if h.get('net50') is not None else 'NA'} | {h.get('net20') if h.get('net20') is not None else 'NA'} | {h.get('net20_50') if h.get('net20_50') is not None else 'NA'} | {d['partial_oos_trades']} | {p.get('net') if p.get('net') is not None else 'NA'} | {p.get('net50') if p.get('net50') is not None else 'NA'} | {p.get('net20') if p.get('net20') is not None else 'NA'} | {p.get('net20_50') if p.get('net20_50') is not None else 'NA'} |")
 lines += ['', '## Interpretation','','This is a reconciliation of previously committed summaries, not a new independent test. The partial window is short and does not supersede the frozen historical HOLD split. Where historical HOLD and partial results disagree, the discrepancy is treated as temporal instability, not an invitation to retune. The two missing expiry dates remain excluded. No strategy is promoted.','','## Audit errors','']+([f'- {e}' for e in errors] if errors else ['- None.'])
 (OUT/'report.md').write_text('\n'.join(lines)+'\n'); print(json.dumps({'decision':decision,'errors':errors,'strategies':{s:{'hold':d['historical_splits'].get('HOLD',{}),'partial':d['partial_oos'],'disagreement':d['temporal_sign_disagreement']} for s,d in out.items()}},indent=2))
 if errors: raise SystemExit(2)
if __name__=='__main__': main()
