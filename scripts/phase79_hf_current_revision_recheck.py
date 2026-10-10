#!/usr/bin/env python3
"""Aggregate-only current-revision audit; raw market files stay in ephemeral runner."""
import os, json, hashlib
from pathlib import Path
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download
REPO='thetrademarkk/india-index-options-1m'; TARGETS=['2026-07-28','2026-08-04']; OUT=Path('results/phase79_hf_current_revision')
def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def main():
 token=os.environ.get('HF_TOKEN')
 if not token: raise RuntimeError('HF_TOKEN secret is required; token value will not be printed')
 api=HfApi(token=token); info=api.dataset_info(REPO); revision=info.sha
 outputs={}; errors=[]
 for day in TARGETS:
  name=f'options/NIFTY/{day}.parquet'
  try:
   path=hf_hub_download(repo_id=REPO,filename=name,repo_type='dataset',revision=revision,token=token)
   digest=sha256(path); frame=pd.read_parquet(path)
   required={'timestamp','expiry','strike','option_type','open','high','low','close'}
   missing=sorted(required-set(frame.columns))
   if missing:
    errors.append(f'{day}: missing columns {missing}')
    outputs[day]={'file':name,'sha256':digest,'rows':int(len(frame)),'missing_columns':missing}; continue
   ts=pd.to_datetime(frame['timestamp'],errors='coerce',utc=True).dt.tz_convert('Asia/Kolkata')
   exp=pd.to_datetime(frame['expiry'],errors='coerce').dt.strftime('%Y-%m-%d')
   expiry_rows=frame.loc[exp.eq(day)].copy(); ets=ts.loc[exp.eq(day)]
   expiry_days=ets.dt.strftime('%Y-%m-%d')
   target=expiry_rows.loc[expiry_days.eq(day)].copy(); tts=ets.loc[expiry_days.eq(day)]
   hhmm=tts.dt.strftime('%H:%M')
   regular=hhmm.ge('09:15') & hhmm.le('15:29')
   regular_rows=target.loc[regular].copy(); regular_ts=tts.loc[regular]
   identity_ok=regular_rows[['strike','option_type']].notna().all(axis=1)
   groups=[]
   if len(regular_rows):
    temp=regular_rows.copy(); temp['_ts']=regular_ts.to_numpy()
    temp['_expiry']=pd.to_datetime(temp['expiry'],errors='coerce').dt.strftime('%Y-%m-%d')
    for (strike,side),g in temp.groupby(['strike','option_type'],dropna=True):
     unique=int(pd.to_datetime(g['_ts'],utc=True).nunique())
     groups.append({'strike':str(strike),'option_type':str(side),'rows':int(len(g)),'unique_minutes':unique,'complete_375':unique==375})
   valid_ohlc=bool((regular_rows['high']>=regular_rows[['open','close','low']].max(axis=1)).all() and (regular_rows['low']<=regular_rows[['open','close','high']].min(axis=1)).all())
   outputs[day]={'file':name,'sha256':digest,'rows':int(len(frame)),'columns':list(frame.columns),'file_timestamp_min':ts.min().isoformat() if ts.notna().any() else None,'file_timestamp_max':ts.max().isoformat() if ts.notna().any() else None,
    'explicit_expiry_rows':int(exp.eq(day).sum()),'expiry_session_rows':int(len(target)),'regular_session_rows':int(len(regular_rows)),
    'unique_regular_timestamps':int(regular_ts.nunique()),'first_regular_timestamp':regular_ts.min().isoformat() if regular_ts.notna().any() else None,'last_regular_timestamp':regular_ts.max().isoformat() if regular_ts.notna().any() else None,
    'rows_with_missing_strike_or_side':int((~identity_ok).sum()),'contract_side_strike_groups':len(groups),'complete_375_groups':sum(x['complete_375'] for x in groups),'valid_ohlc':valid_ohlc,
    'contract_groups':groups}
  except Exception as e:
   errors.append(f'{day}: {type(e).__name__}: {e}'); outputs[day]={'file':name,'error_type':type(e).__name__,'error':str(e)[:400]}
 pass_gate=not errors and all(outputs.get(d,{}).get('expiry_session_rows',0)>0 and outputs[d].get('complete_375_groups',0)>0 and outputs[d].get('valid_ohlc') is True and outputs[d].get('rows_with_missing_strike_or_side',1)==0 for d in TARGETS)
 decision='CURRENT_SOURCE_COVERS_TARGETS' if pass_gate else ('BLOCKED_SOURCE_ACCESS_OR_SCHEMA' if errors else 'BLOCKED_CURRENT_SOURCE_INCOMPLETE')
 result={'phase':79,'dataset':REPO,'revision':revision,'decision':decision,'targets':TARGETS,'errors':errors,'files':outputs,'raw_data_committed':False,'license':'CC-BY-NC-4.0 (as listed on dataset card); non-commercial use only; educational/as-is disclaimer','caveat':'A complete OHLC bar set is data coverage only, not proof of executable fills, spread, or depth. Expiry/strike/side mapping must be validated before replay.'}
 OUT.mkdir(parents=True,exist_ok=True); (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
 lines=['# Phase 79 — Current Hugging Face revision recheck','',f'**Decision: {decision}**','',f'Dataset revision: `{revision}`','', '## Target expiry-session coverage','', '| Expiry | File rows | Explicit expiry rows | Expiry-session rows | Regular rows | Complete 375-bar groups | OHLC valid | SHA-256 |','|---|---:|---:|---:|---:|---:|---|---|']
 for d,x in outputs.items(): lines.append(f"| {d} | {x.get('rows','NA')} | {x.get('explicit_expiry_rows','NA')} | {x.get('expiry_session_rows','NA')} | {x.get('regular_session_rows','NA')} | {x.get('complete_375_groups','NA')} | {x.get('valid_ohlc','NA')} | `{x.get('sha256','NA')}` |")
 lines += ['', '## Interpretation','','This audit checks the current dataset revision rather than Phase 76’s older pinned revision. Only aggregate diagnostics are retained; raw Parquet files remain ephemeral. Even if coverage passes, OHLC bars do not prove executable fills or spread/depth quality. The dataset is marked CC-BY-NC-4.0 and must not be treated as cleared for commercial use.','','## Errors','']+([f'- {e}' for e in errors] if errors else ['- None.'])
 (OUT/'report.md').write_text('\n'.join(lines)+'\n'); print(json.dumps({'decision':decision,'revision':revision,'errors':errors,'files':{d:{k:v for k,v in x.items() if k!='contract_groups' and k!='columns'} for d,x in outputs.items()}},indent=2))
 if errors: raise SystemExit(2)
if __name__=='__main__': main()
