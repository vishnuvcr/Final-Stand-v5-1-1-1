import json, math
from pathlib import Path
import numpy as np
import pandas as pd

OUT=Path('results/dynamic_n_corrected/phase25_direction_chooser'); OUT.mkdir(parents=True,exist_ok=True)
FEATURES=Path('results/dynamic_n_corrected/phase23_entry_state/phase23_entry_features.csv')
CAN=Path('results/dynamic_n_corrected/phase23_entry_state/canonical_trade_ledger.csv')
REV=Path('results/dynamic_n_corrected/phase23_entry_state/reverse_trade_ledger.csv')
TRAIN_END=pd.Timestamp('2023-12-31'); VAL_END=pd.Timestamp('2025-12-31'); HOLD_START=pd.Timestamp('2026-01-01')
RNG=np.random.default_rng(20261005); B=5000

def metrics(frame, dirs):
    c=frame.canonical_net.to_numpy(float); r=frame.reverse_net.to_numpy(float)
    base_dir=frame.canonical_direction.to_numpy()
    action=[]; pol=[]
    for i,d in enumerate(dirs):
        if d is None or (d=='BEARISH' and base_dir[i]=='BEARISH') or (d=='BULLISH' and base_dir[i]=='BULLISH'):
            if d is None: action.append('SKIP'); pol.append(0.0)
            else: action.append('BASE'); pol.append(c[i])
        else:
            if np.isfinite(r[i]): action.append('SWITCH'); pol.append(r[i])
            else: action.append('SKIP_REVERSE_UNAVAILABLE'); pol.append(0.0)
    p=np.asarray(pol); win=c>0; winner_ret=float(np.mean(p[win]>0)) if win.any() else np.nan
    switches=np.array(action)=='SWITCH'; skips=np.array([a.startswith('SKIP') for a in action])
    improved=(switches)&np.isfinite(r)&(r>c)
    worsened=(switches)&(r<c)
    w_to_loss=(win)&(p<0)
    cov=1.0-float(skips.mean())
    pnl_diff=p-c
    run=np.cumsum(p); peak=np.maximum.accumulate(np.r_[0.0,run]); dd=float(np.max(peak[1:]-run)) if len(run) else 0.0
    pf=float(p[p>0].sum()/(-p[p<0].sum())) if np.any(p<0) else np.inf
    return {'trades':len(frame),'policy_net':float(p.sum()),'canonical_net':float(c.sum()),'uplift':float(p.sum()-c.sum()),
            'winner_retention':winner_ret,'winner_to_loss_count':int(w_to_loss.sum()),'switch_count':int(switches.sum()),
            'skip_count':int(skips.sum()),'coverage':cov,'switches_improving':int(improved.sum()),'switches_worsening':int(worsened.sum()),
            'losses_reversed':int(((c<0)&switches&(r>c)).sum()),'winning_trades_switched':int((win&switches).sum()),
            'winning_pnl_sacrificed':float(c[(win&switches)].sum()),'profit_factor':pf,'max_dd':dd,'worst_trade':float(p.min())}

def maxdd(a):
    a=np.asarray(a,float); run=np.cumsum(a); peak=np.maximum.accumulate(np.r_[0.0,run]); return float(np.max(peak[1:]-run)) if len(run) else 0.0

def bootstrap(diff):
    diff=np.asarray(diff,float);
    vals=np.empty(B)
    for i in range(B): vals[i]=diff[RNG.integers(0,len(diff),len(diff))].mean()
    return float(diff.mean()),float(np.quantile(vals,.025)),float(np.quantile(vals,.975))

def direction_from_sign(x, positive='BULLISH'):
    if not np.isfinite(x) or x==0: return None
    return positive if x>0 else ('BEARISH' if positive=='BULLISH' else 'BULLISH')

def make_candidates(df):
    out={}
    # A: raw and normalized curvature at every available starting moneyness.
    for k in range(6,16):
        xc=df[f'CE_p{k+2}']+df[f'CE_p{k+1}']-df[f'CE_p{k}']
        xp=df[f'PE_p{k+2}']+df[f'PE_p{k+1}']-df[f'PE_p{k}']
        out[f'curvature_raw_k{k}']=np.where((xc.notna())&(xp.notna()),np.where(xc>xp,'BEARISH',np.where(xp>xc,'BULLISH',None)),None)
        nc=xc/df[f'CE_p{k}']; np_=xp/df[f'PE_p{k}']
        out[f'curvature_norm_k{k}']=np.where((nc.notna())&(np_.notna()),np.where(nc>np_,'BEARISH',np.where(np_>nc,'BULLISH',None)),None)
    # B: relative OTM call/put price; literature-sign convention is positive => bullish.
    ratios={}
    for k in range(6,16):
        z=np.log(df[f'CE_p{k}']/df[f'PE_p{k}'])
        ratios[k]=z; out[f'premium_ratio_k{k}']=np.where(z.notna(),np.where(z>0,'BULLISH',np.where(z<0,'BEARISH',None)),None)
    # C: same-moneyness call-put IV spread.
    ivs={}
    for k in range(6,11):
        z=df[f'CE_iv{k}']-df[f'PE_iv{k}']; ivs[k]=z
        out[f'iv_spread_k{k}']=np.where(z.notna(),np.where(z>0,'BULLISH',np.where(z<0,'BEARISH',None)),None)
    # D: PCR; test both momentum and contrarian signs.
    for k in range(6,11):
        oi=np.log(df[f'PE_oi{k}']/df[f'CE_oi{k}']); vo=np.log(df[f'PE_vol{k}']/df[f'CE_vol{k}'])
        for name,z in [('oi_pcr',oi),('vol_pcr',vo)]:
            out[f'{name}_momentum_k{k}']=np.where(z.notna(),np.where(z>0,'BEARISH',np.where(z<0,'BULLISH',None)),None)
            out[f'{name}_contrarian_k{k}']=np.where(z.notna(),np.where(z>0,'BULLISH',np.where(z<0,'BEARISH',None)),None)
    # E: direct market/cross-market signals.
    out['nifty_ret1']=np.where(df.nifty_ret1.notna(),np.where(df.nifty_ret1>0,'BULLISH',np.where(df.nifty_ret1<0,'BEARISH',None)),None)
    out['ret_10am_pct']=np.where(df.ret_10am_pct.notna(),np.where(df.ret_10am_pct>0,'BULLISH',np.where(df.ret_10am_pct<0,'BEARISH',None)),None)
    out['overnight_gap']=np.where(df.overnight_gap_pct.notna(),np.where(df.overnight_gap_pct>0,'BULLISH',np.where(df.overnight_gap_pct<0,'BEARISH',None)),None)
    gcols=['sp500_ret1','nasdaq_ret1','dow_ret1','nikkei_ret1','hangseng_ret1','kospi_ret1','shanghai_ret1']
    g=df[gcols].median(axis=1,skipna=True); out['global_equity_median']=np.where(g.notna(),np.where(g>0,'BULLISH',np.where(g<0,'BEARISH',None)),None)
    # F: fixed aggregate signals.
    R=pd.DataFrame(ratios); mr=R[[6,7,8,9,10]].median(axis=1,skipna=True)
    S=pd.DataFrame(ivs); ms=S[[6,7,8,9,10]].median(axis=1,skipna=True)
    out['median_premium_ratio']=np.where(mr.notna(),np.where(mr>0,'BULLISH',np.where(mr<0,'BEARISH',None)),None)
    out['median_iv_spread']=np.where(ms.notna(),np.where(ms>0,'BULLISH',np.where(ms<0,'BEARISH',None)),None)
    vote_cols=['median_premium_ratio','median_iv_spread','global_equity_median','ret_10am_pct']
    # Add PCR-OI contrarian as the fifth vote.
    z=np.log(df['total_pe_oi']/df['total_ce_oi']); pcr=np.where(z.notna(),np.where(z>0,'BULLISH',np.where(z<0,'BEARISH',None)),None); out['pcr_oi_contrarian']=pcr
    votes=[]
    for i in range(len(df)):
        vv=[out[c][i] for c in vote_cols+['pcr_oi_contrarian'] if out[c][i] is not None]
        b=sum(v=='BULLISH' for v in vv); s=sum(v=='BEARISH' for v in vv)
        votes.append('BULLISH' if b>s else ('BEARISH' if s>b else None))
    out['majority_vote']=np.array(votes,dtype=object)
    return out

def main():
    f=pd.read_csv(FEATURES); c=pd.read_csv(CAN); r=pd.read_csv(REV)
    f['entry_date']=pd.to_datetime(f.entry_date).dt.normalize(); c['entry_date']=pd.to_datetime(c.entry_date).dt.normalize()
    c=c[['expiry','entry_date','net','canonical_direction']].rename(columns={'net':'canonical_net'})
    r=r[['expiry','net']].rename(columns={'net':'reverse_net'})
    x=f.merge(c,on=['expiry','entry_date'],how='inner').merge(r,on='expiry',how='left')
    if len(x)!=len(c): raise RuntimeError(f'Universe mismatch: {len(x)} vs {len(c)}')
    x=x.sort_values('entry_date').reset_index(drop=True)
    x['baseline_positive']=x.canonical_net>0
    candidates=make_candidates(x)
    records=[]; ledgers=[]
    for name,dirs in candidates.items():
        for period,mask in [('training',x.entry_date<=TRAIN_END),('validation',(x.entry_date>TRAIN_END)&(x.entry_date<=VAL_END)),('holdout',x.entry_date>=HOLD_START)]:
            fr=x.loc[mask].copy().reset_index(drop=True); dd=np.asarray(dirs)[mask.to_numpy()]
            mm=metrics(fr,dd); mm.update({'candidate':name,'period':period})
            # Retrospective directional hit rate, diagnostic only.
            better=np.where(fr.reverse_net.notna(),np.where(fr.reverse_net>fr.canonical_net,'REVERSE',np.where(fr.reverse_net<fr.canonical_net,'CANONICAL','TIE')), 'CANONICAL')
            chosen=np.where(dd=='BULLISH','REVERSE',np.where(dd=='BEARISH','CANONICAL','SKIP'))
            valid=chosen!='SKIP'; mm['retrospective_accuracy']=float(np.mean(chosen[valid]==better[valid])) if valid.any() else np.nan
            records.append(mm)
            led=pd.DataFrame({'expiry':fr.expiry,'entry_date':fr.entry_date,'baseline_direction':fr.canonical_direction,'candidate':name,'candidate_direction':dd,'canonical_net':fr.canonical_net,'reverse_net':fr.reverse_net,'period':period})
            led['action']=np.where(dd==fr.canonical_direction,'BASE',np.where(dd==('BULLISH'),'SWITCH_TO_PUT',np.where(dd==('BEARISH'),'SWITCH_TO_CALL','SKIP')))
            led['policy_net']=np.where(led.action=='BASE',led.canonical_net,np.where(led.action.str.startswith('SWITCH')&led.reverse_net.notna(),led.reverse_net,0.0))
            ledgers.append(led)
    grid=pd.DataFrame(records)
    tr=grid[grid.period=='training'].copy()
    elig=tr[(tr.uplift>0)&(tr.winner_retention>=.95)&(tr.winner_to_loss_count==0)&(tr.coverage>=.95)&(tr.switches_improving>=2)].copy()
    if len(elig):
        elig=elig.sort_values(['winner_retention','switch_count','uplift','coverage'],ascending=[False,True,False,False])
        selected=str(elig.iloc[0].candidate); basis='least-disruptive training-eligible candidate'
    else:
        selected='baseline_otm678'; basis='no alternative passed training eligibility; baseline retained'
    # Baseline metrics are explicitly added.
    base_dirs=x.canonical_direction.to_numpy(dtype=object)
    base_rows=[]
    for period,mask in [('training',x.entry_date<=TRAIN_END),('validation',(x.entry_date>TRAIN_END)&(x.entry_date<=VAL_END)),('holdout',x.entry_date>=HOLD_START)]:
        fr=x.loc[mask].copy().reset_index(drop=True); mm=metrics(fr,fr.canonical_direction.to_numpy(dtype=object)); mm.update({'candidate':'baseline_otm678','period':period}); base_rows.append(mm)
    grid=pd.concat([grid,pd.DataFrame(base_rows)],ignore_index=True)
    sel_rows=grid[(grid.candidate==selected)&(grid.period.isin(['training','validation','holdout']))].copy()
    trm=sel_rows[sel_rows.period=='training'].iloc[0]; vam=sel_rows[sel_rows.period=='validation'].iloc[0]; hom=sel_rows[sel_rows.period=='holdout'].iloc[0]
    basev=grid[(grid.candidate=='baseline_otm678')&(grid.period=='validation')].iloc[0]; baseh=grid[(grid.candidate=='baseline_otm678')&(grid.period=='holdout')].iloc[0]
    promotion=bool(selected!='baseline_otm678' and trm.uplift>0 and trm.winner_retention>=.95 and trm.winner_to_loss_count==0 and trm.coverage>=.95 and trm.switches_improving>=2 and vam.uplift>0 and hom.uplift>0 and vam.winner_retention>=.90 and hom.winner_retention>=.90 and vam.winner_to_loss_count==0 and hom.winner_to_loss_count==0 and vam.coverage>=.95 and hom.coverage>=.95 and vam.max_dd<=1.05*basev.max_dd and hom.max_dd<=1.05*baseh.max_dd and (vam.switches_improving+hom.switches_improving)>=2)
    # Bootstrap selected-candidate OOS uplift.
    boots=[]
    for period,mask in [('validation',x.entry_date>TRAIN_END)&(x.entry_date<=VAL_END),('holdout',x.entry_date>=HOLD_START)]:
        fr=x.loc[mask].copy().reset_index(drop=True); dd=np.asarray(candidates[selected])[mask.to_numpy()] if selected!='baseline_otm678' else fr.canonical_direction.to_numpy(dtype=object)
        pol=np.where(dd==fr.canonical_direction,fr.canonical_net,np.where(dd=='BULLISH',fr.reverse_net,np.where(dd=='BEARISH',fr.reverse_net,0.0)))
        diff=np.nan_to_num(pol-fr.canonical_net,nan=-fr.canonical_net.to_numpy())
        m,lo,hi=bootstrap(diff); boots.append({'period':period,'uplift_mean':m,'ci_low':lo,'ci_high':hi})
    grid.to_csv(OUT/'phase25_direction_chooser_grid.csv',index=False)
    pd.concat(ledgers,ignore_index=True).sort_values(['candidate','entry_date']).to_csv(OUT/'phase25_direction_chooser_trade_level.csv',index=False)
    pd.DataFrame(boots).to_csv(OUT/'phase25_selected_bootstrap.csv',index=False)
    (OUT/'phase25_selection.json').write_text(json.dumps({'selected_candidate':selected,'selection_basis':basis,'promotion_pass':promotion},indent=2))
    summary=sel_rows[['candidate','period','policy_net','canonical_net','uplift','winner_retention','coverage','switch_count','switches_improving','losses_reversed','max_dd','worst_trade','profit_factor']].copy()
    summary.to_csv(OUT/'phase25_selected_walkforward.csv',index=False)
    print(json.dumps({'selected':selected,'basis':basis,'promotion_pass':promotion,'summary':summary.to_dict('records')},indent=2))

if __name__=='__main__': main()