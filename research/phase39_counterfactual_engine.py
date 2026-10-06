# Phase 39 Step 1 — fixed-opportunity economic counterfactual engine
import json, os, io, zipfile, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from huggingface_hub import hf_hub_download

HF_REPO = 'thetrademarkk/india-index-options-1m'
TZ = 'Asia/Kolkata'
ROOT = Path('.')
DATA_DIR = ROOT / 'results/phase39_data'
OUT = ROOT / 'results/phase39_counterfactual'
DEV_CONTROL = DATA_DIR / 'development_control_trades_2021_2023.csv'
CONTROL = DATA_DIR / 'frozen_control_trades_2024_2026-06-30.csv'
PROVENANCE = DATA_DIR / 'frozen_control_provenance.json'
DEV_START = pd.Timestamp('2021-05-27', tz=TZ)
DEV_END = pd.Timestamp('2023-12-31', tz=TZ)
OUT.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ID = 11380124540
ARTIFACT_RUN = 37388261915
CONTROL_START = pd.Timestamp('2024-01-11', tz=TZ)
CONTROL_END = pd.Timestamp('2026-06-30', tz=TZ)
TICK = 0.05
SLIPPAGE_TICKS = 1.0
LOTS = 6
WIDTH = 50.0
BROKERAGE_PER_ORDER = 10.0

def norm_cdf(x):
    x = np.asarray(x, float)
    ax = np.abs(x)
    t = 1.0 / (1.0 + 0.2316419 * ax)
    poly = ((((1.330274429*t - 1.821255978)*t + 1.781477937)*t - 0.356563782)*t + 0.319381530)*t
    pdf = np.exp(-0.5*ax*ax) / np.sqrt(2*np.pi)
    cdf = 1 - pdf*poly
    return np.where(x >= 0, cdf, 1-cdf)

def bs_price(S, K, T, sig, typ):
    S=np.asarray(S,float); K=np.asarray(K,float); T=np.maximum(np.asarray(T,float),1e-10); sig=np.maximum(np.asarray(sig,float),1e-8)
    d1=(np.log(S/K)+0.5*sig*sig*T)/(sig*np.sqrt(T)); d2=d1-sig*np.sqrt(T)
    if typ=='CE': return S*norm_cdf(d1)-K*norm_cdf(d2)
    return K*norm_cdf(-d2)-S*norm_cdf(-d1)

def bs_delta(S,K,T,sig,typ):
    S=np.asarray(S,float); K=np.asarray(K,float); T=np.maximum(np.asarray(T,float),1e-10); sig=np.maximum(np.asarray(sig,float),1e-8)
    d1=(np.log(S/K)+0.5*sig*sig*T)/(sig*np.sqrt(T)); n=norm_cdf(d1)
    return n if typ=='CE' else n-1

def implied_delta(price,S,K,T,typ):
    p=np.asarray(price,float); s=np.asarray(S,float); t=np.asarray(T,float); k=np.asarray(K,float)
    intrinsic=np.maximum(s-k,0) if typ=='CE' else np.maximum(k-s,0)
    valid=np.isfinite(p)&np.isfinite(s)&np.isfinite(t)&(t>0)&(s>0)&(p>=intrinsic-1e-7)&(p>1e-8)
    out=np.full(p.shape,np.nan)
    if not valid.any(): return out
    idx=np.where(valid)[0]; pp=p[idx]; ss=s[idx]; tt=t[idx]; kk=k[idx]
    lo=np.full_like(pp,1e-5); hi=np.full_like(pp,5.0); x=np.full_like(pp,0.30)
    for _ in range(16):
        d1=(np.log(ss/kk)+0.5*x*x*tt)/(x*np.sqrt(tt))
        px=bs_price(ss,kk,tt,x,typ)
        v=ss*np.exp(-0.5*d1*d1)/np.sqrt(2*np.pi)*np.sqrt(tt)
        xn=np.clip(x-(px-pp)/np.maximum(v,1e-10),lo,hi)
        bad=~np.isfinite(xn)|(v<1e-10); xn[bad]=(lo[bad]+hi[bad])/2
        pxn=bs_price(ss,kk,tt,xn,typ); low=pxn<pp
        lo=np.where(low,xn,lo); hi=np.where(low,hi,xn); x=xn
    residual=np.abs(bs_price(ss,kk,tt,x,typ)-pp)
    good=residual<=0.03
    out[idx[good]]=bs_delta(ss[good],kk[good],tt[good],x[good],typ)
    return out

def load_hf(path):
    p=hf_hub_download(repo_id=HF_REPO,filename=path,repo_type='dataset',token=os.getenv('HF_TOKEN') or None)
    df=pd.read_parquet(p)
    df['timestamp']=pd.to_datetime(df['timestamp'])
    if df['timestamp'].dt.tz is None: df['timestamp']=df['timestamp'].dt.tz_localize(TZ)
    else: df['timestamp']=df['timestamp'].dt.tz_convert(TZ)
    return df

def fee_rates(d):
    if d>=pd.Timestamp('2026-04-01',tz=TZ): stt=0.0015
    elif d>=pd.Timestamp('2024-10-01',tz=TZ): stt=0.0010
    else: stt=0.000625
    if d>=pd.Timestamp('2026-03-01',tz=TZ): txn,ipft=0.000355299,0.000000001
    elif d>=pd.Timestamp('2024-10-01',tz=TZ): txn,ipft=0.0003503,0.000005
    else: txn,ipft=0.000495,0.000005
    return stt,txn,0.000001,ipft,0.00003

def exec_px(px,action):
    s=SLIPPAGE_TICKS*TICK
    return max(0.0,float(px)+s) if action=='buy' else max(0.0,float(px)-s)

def charges(orders,lot):
    brokerage=BROKERAGE_PER_ORDER*len(orders); exchange=sebi=ipft=stt=stamp=0.0; qty=lot*LOTS
    for d,side,px in orders:
        sr,tx,se,ip,st=fee_rates(d); turnover=float(px)*qty
        exchange+=tx*turnover; sebi+=se*turnover; ipft+=ip*turnover
        if side=='sell': stt+=sr*turnover
        else: stamp+=st*turnover
    gst=.18*(brokerage+exchange+sebi+ipft)
    return brokerage+exchange+sebi+ipft+stt+stamp+gst

def bootstrap_control_ledger():
    if DEV_CONTROL.exists() and CONTROL.exists() and PROVENANCE.exists():
        return
    token=os.getenv('GITHUB_TOKEN')
    repo=os.getenv('GITHUB_REPOSITORY','vishnuvcr/Final-Stand-v5-1-1-1')
    if not token: raise RuntimeError('GITHUB_TOKEN is required to bootstrap the frozen control ledger')
    url=f'https://api.github.com/repos/{repo}/actions/artifacts/{ARTIFACT_ID}/zip'
    r=requests.get(url,headers={'Authorization':f'Bearer {token}','Accept':'application/vnd.github+json'},timeout=120)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        names=z.namelist(); match=[n for n in names if n.endswith('results/dynamic_strategy_phase32/trades.csv')]
        if not match: raise RuntimeError('Phase-32 artifact did not contain trades.csv')
        raw=z.read(match[0])
    all_trades=pd.read_csv(io.BytesIO(raw))
    exp=pd.to_datetime(all_trades['expiry'],errors='coerce').dt.tz_localize(TZ)
    dev=all_trades.loc[(exp>=DEV_START)&(exp<=DEV_END)].copy()
    frozen=all_trades.loc[(exp>=CONTROL_START)&(exp<=CONTROL_END)].copy()
    excluded=all_trades.loc[(exp>DEV_END)&(exp<CONTROL_START)].copy()
    dev.to_csv(DEV_CONTROL,index=False)
    frozen.to_csv(CONTROL,index=False)
    digest=hashlib.sha256(CONTROL.read_bytes()).hexdigest()
    dev_digest=hashlib.sha256(DEV_CONTROL.read_bytes()).hexdigest()
    prov={'source_artifact_id':ARTIFACT_ID,'source_run_id':ARTIFACT_RUN,'source_repo':repo,'source_member':match[0],
          'development':{'derived_sha256':dev_digest,'trades':int(len(dev)),'expiries':int(dev['expiry'].nunique()),'net_rupees':float(dev['net_rupees'].sum()),'first_expiry':str(dev['expiry'].min()),'last_expiry':str(dev['expiry'].max())},
          'frozen':{'derived_sha256':digest,'trades':int(len(frozen)),'expiries':int(frozen['expiry'].nunique()),'net_rupees':float(frozen['net_rupees'].sum()),'first_expiry':str(frozen['expiry'].min()),'last_expiry':str(frozen['expiry'].max())},
          'excluded_between_dev_and_frozen':{'trades':int(len(excluded)),'expiries':int(excluded['expiry'].nunique()),'net_rupees':float(excluded['net_rupees'].sum()),'reason':'2024-01-04 trade intentionally excluded so validation uses the frozen Phase-38 comparator exactly'}}
    PROVENANCE.write_text(json.dumps(prov,indent=2))

def validate_control_ledger():
    bootstrap_control_ledger()
    dev=pd.read_csv(DEV_CONTROL); z=pd.read_csv(CONTROL)
    required={'expiry','entry_ts','exit_ts','direction','short_strike','long_strike','lot_size','net_rupees'}
    for name,frame in [('development',dev),('frozen',z)]:
        missing=required-set(frame.columns)
        if missing: raise AssertionError(f'{name} control ledger missing columns: {sorted(missing)}')
    if len(dev)!=271 or dev['expiry'].nunique()!=135: raise AssertionError(f'Development control shape mismatch: {len(dev)} trades / {dev.expiry.nunique()} expiries')
    if len(z)!=206 or z['expiry'].nunique()!=102: raise AssertionError(f'Frozen control ledger shape mismatch: {len(z)} trades / {z.expiry.nunique()} expiries')
    if abs(float(z.net_rupees.sum())-63672.57530171223)>1e-6: raise AssertionError('Frozen control P&L does not match authoritative benchmark')
    dev['entry_ts']=pd.to_datetime(dev.entry_ts).dt.tz_convert(TZ); dev['expiry']=pd.to_datetime(dev.expiry).dt.strftime('%Y-%m-%d')
    z['entry_ts']=pd.to_datetime(z.entry_ts).dt.tz_convert(TZ); z['expiry']=pd.to_datetime(z.expiry).dt.strftime('%Y-%m-%d')
    dev['split']='development'
    z['split']=np.where(pd.to_datetime(z.expiry).dt.year<=2025,'validation','holdout')
    panel=pd.concat([dev,z],ignore_index=True)
    return panel.sort_values(['entry_ts','expiry']).reset_index(drop=True)

def nearest_delta_strike(snap,spot,ts,typ,target):
    sub=snap[snap.option_type==typ].copy()
    if sub.empty: return None
    expiry_ts=pd.Timestamp(str(sub.expiry_ts.iloc[0])).tz_localize(TZ) if pd.Timestamp(str(sub.expiry_ts.iloc[0])).tzinfo is None else pd.Timestamp(sub.expiry_ts.iloc[0])
    T=max((expiry_ts-ts).total_seconds()/31557600.0,1e-10)
    ds=implied_delta(sub.close.to_numpy(float),np.full(len(sub),spot),sub.strike.to_numpy(float),np.full(len(sub),T),typ)
    ok=np.isfinite(ds)
    if not ok.any(): return None
    zz=sub.loc[ok].copy(); zz['delta']=ds[ok]; i=(zz.delta-target).abs().idxmin()
    return float(zz.loc[i,'strike']),float(zz.loc[i,'delta'])

def run_arm(option_df,spot_df,entry_ts,expiry,typ,short_k,long_k,lot):
    expiry_ts=expiry+pd.Timedelta(hours=15,minutes=30)
    snap=option_df[option_df.timestamp==entry_ts]
    legs=option_df[(option_df.timestamp==entry_ts)&(option_df.option_type==typ)&(option_df.strike.isin([short_k,long_k]))]
    if len(legs)<2: raise RuntimeError(f'missing entry legs {entry_ts} {typ} {short_k} {long_k}')
    q={float(x.strike):float(x.close) for _,x in legs.iterrows()}
    short_entry=q[float(short_k)]; long_entry=q[float(long_k)]
    path=option_df[(option_df.timestamp>entry_ts)&(option_df.timestamp<=expiry+pd.Timedelta(hours=15,minutes=29))&(option_df.option_type==typ)&(option_df.strike.isin([short_k,long_k]))].pivot_table(index='timestamp',columns='strike',values='close',aggfunc='last').dropna(subset=[short_k,long_k])
    if path.empty: raise RuntimeError(f'no future path {entry_ts} {typ}')
    path=path.reset_index().merge(spot_df[['timestamp','spot']],on='timestamp',how='inner').sort_values('timestamp').reset_index(drop=True)
    tleft=np.maximum((expiry_ts-pd.to_datetime(path.timestamp)).dt.total_seconds().to_numpy(float)/31557600.0,1e-10)
    deltas=implied_delta(path[short_k].to_numpy(float),path.spot.to_numpy(float),np.full(len(path),short_k,float),tleft,typ)
    hit=(deltas>=.50)|(deltas<=.04) if typ=='CE' else (deltas<=-.50)|(deltas>=-.04)
    hit_idx=np.flatnonzero(np.isfinite(deltas)&hit)
    if len(hit_idx):
        row=path.iloc[int(hit_idx[0])]; exit_delta=float(deltas[int(hit_idx[0])]); reason='DELTA_EXIT'
    else:
        row=path.iloc[-1]; exit_delta=np.nan; reason='CONTRACT_EXPIRY'
    exit_ts=pd.Timestamp(row.timestamp)
    ep_long=exec_px(long_entry,'buy'); ep_short=exec_px(short_entry,'sell')
    xp_short=exec_px(float(row[short_k]),'buy'); xp_long=exec_px(float(row[long_k]),'sell')
    gross=((ep_short-xp_short)+(xp_long-ep_long))*lot*LOTS
    orders=[(entry_ts,'sell',ep_short),(entry_ts,'buy',ep_long),(exit_ts,'buy',xp_short),(exit_ts,'sell',xp_long)]
    cost=charges(orders,lot); net=gross-cost
    return {'entry_ts':str(entry_ts),'exit_ts':str(exit_ts),'direction':'CALL' if typ=='CE' else 'PUT','short_strike':short_k,'long_strike':long_k,'gross_rupees':gross,'cost_rupees':cost,'net_rupees':net,'short_delta_exit':exit_delta,'exit_reason':reason}

def main():
    ctl=validate_control_ledger()
    spot=load_hf('index/NIFTY.parquet')[['timestamp','close']].rename(columns={'close':'spot'}).drop_duplicates('timestamp').sort_values('timestamp')
    cache={}; rows=[]; audit=[]
    for i,r in ctl.iterrows():
        expiry=pd.Timestamp(r.expiry,tz=TZ); entry_ts=pd.Timestamp(r.entry_ts)
        if expiry not in cache:
            od=load_hf(f'options/NIFTY/{expiry.strftime("%Y-%m-%d")}.parquet')
            od['option_type']=od.option_type.astype(str).str.upper(); od['strike']=pd.to_numeric(od.strike,errors='coerce'); od=od.dropna(subset=['timestamp','strike','close']); od=od.sort_values(['timestamp','option_type','strike'],kind='stable').drop_duplicates(['timestamp','option_type','strike'],keep='last'); od['expiry_ts']=expiry+pd.Timedelta(hours=15,minutes=30); cache[expiry]=od
        od=cache[expiry]; srow=spot[spot.timestamp==entry_ts]
        if srow.empty: raise RuntimeError(f'missing spot at {entry_ts}')
        s=float(srow.iloc[0].spot)
        out={}
        for typ in ['CE','PE']:
            if (r.direction=='CALL' and typ=='CE') or (r.direction=='PUT' and typ=='PE'):
                sk=float(r.short_strike); lk=float(r.long_strike); sel='ledger'
            else:
                found=nearest_delta_strike(od[od.timestamp==entry_ts],s,entry_ts,typ,0.25 if typ=='CE' else -0.25)
                if found is None: raise RuntimeError(f'cannot select counterfactual delta strike at {entry_ts} {typ}')
                sk,entry_delta=found; lk=sk+WIDTH if typ=='CE' else sk-WIDTH; sel='nearest_delta'
            out[typ]=run_arm(od,spot,entry_ts,expiry,typ,sk,lk,int(r.lot_size)); out[typ]['strike_selection']=sel
        control_net=float(r.net_rupees); control_arm=out['CE' if r.direction=='CALL' else 'PE']['net_rupees']
        recon_err=control_arm-control_net
        if abs(recon_err)>0.75: raise AssertionError(f'Control arm P&L mismatch at row {i}: recalculated={control_arm}, frozen={control_net}, err={recon_err}')
        rows.append({
            'split':str(r.split),'expiry':str(expiry.date()),'entry_ts':str(entry_ts),'control_direction':r.direction,'entry_spot':s,'lot_size':int(r.lot_size),
            'call_net_rupees':out['CE']['net_rupees'],'put_net_rupees':out['PE']['net_rupees'],
            'delta_pnl_call_minus_put':out['CE']['net_rupees']-out['PE']['net_rupees'],
            'control_net_rupees':control_net,'recalculated_control_net_rupees':control_arm,'control_reconstruction_error':recon_err,
            'oracle_net_rupees':max(out['CE']['net_rupees'],out['PE']['net_rupees']),
            'control_regret_rupees':max(out['CE']['net_rupees'],out['PE']['net_rupees'])-control_net,
            'call_exit_ts':out['CE']['exit_ts'],'put_exit_ts':out['PE']['exit_ts'],
            'call_short_strike':out['CE']['short_strike'],'put_short_strike':out['PE']['short_strike'],
            'call_long_strike':out['CE']['long_strike'],'put_long_strike':out['PE']['long_strike'],
            'call_exit_reason':out['CE']['exit_reason'],'put_exit_reason':out['PE']['exit_reason']
        })
    df=pd.DataFrame(rows).sort_values('entry_ts').reset_index(drop=True)
    df.to_csv(OUT/'fixed_opportunity_ledger.csv',index=False)
    exp=df.groupby(['split','expiry'],as_index=False).agg(control_net_rupees=('control_net_rupees','sum'),call_net_rupees=('call_net_rupees','sum'),put_net_rupees=('put_net_rupees','sum'),delta_pnl_call_minus_put=('delta_pnl_call_minus_put','sum'),control_regret_rupees=('control_regret_rupees','sum'))
    exp.to_csv(OUT/'fixed_opportunity_expiry_summary.csv',index=False)
    def split_summary(g):
        return {'rows':int(len(g)),'expiries':int(g.expiry.nunique()),'control_net_rupees':float(g.control_net_rupees.sum()),'call_net_rupees':float(g.call_net_rupees.sum()),'put_net_rupees':float(g.put_net_rupees.sum()),'mean_delta_pnl_rupees':float(g.delta_pnl_call_minus_put.mean()),'median_delta_pnl_rupees':float(g.delta_pnl_call_minus_put.median()),'positive_delta_share':float((g.delta_pnl_call_minus_put>0).mean()),'oracle_net_rupees':float(g.oracle_net_rupees.sum()),'oracle_uplift_vs_control_rupees':float(g.control_regret_rupees.sum()),'control_reconstruction_max_abs_error':float(g.control_reconstruction_error.abs().max()),'control_reconstruction_mean_abs_error':float(g.control_reconstruction_error.abs().mean())}
    stats={'status':'PASS','panel_rows':int(len(df)),'development':split_summary(df[df.split=='development']),'validation':split_summary(df[df.split=='validation']),'holdout':split_summary(df[df.split=='holdout']),'frozen_control_net_rupees':float(df[df.split!='development'].control_net_rupees.sum()),'control_direction_counts':{k:int(v) for k,v in df.control_direction.value_counts().to_dict().items()},'counterfactual_arm_win_counts':{'CALL':int((df.call_net_rupees>df.put_net_rupees).sum()),'PUT':int((df.put_net_rupees>df.call_net_rupees).sum()),'TIE':int((df.put_net_rupees==df.call_net_rupees).sum())}
    (OUT/'summary.json').write_text(json.dumps(stats,indent=2))
    (OUT/'status.json').write_text(json.dumps({'step':'fixed_opportunity_counterfactual_engine','status':'COMPLETE','panel_rows':len(df),'development_rows':int((df.split=='development').sum()),'validation_rows':int((df.split=='validation').sum()),'holdout_rows':int((df.split=='holdout').sum()),'validation_holdout_frozen_net_rupees':float(df[df.split!='development'].control_net_rupees.sum()),'control_reconstruction_max_abs_error':float(df.control_reconstruction_error.abs().max()),'deterministic_quote_dedup':'stable timestamp/type/strike last-row selection'},indent=2))
    print(json.dumps(stats,indent=2))

if __name__=='__main__': main()