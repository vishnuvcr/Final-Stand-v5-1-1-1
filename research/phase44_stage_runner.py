import json, os
from pathlib import Path
import numpy as np
import pandas as pd

from phase44_vix_tuning import (
    TZ, DEV_END, VAL_END, OUT, ENTRY_TIMES,
    load_index, load_vix, list_expiries, load_option_expiry,
    entry_ts_for, family_specs, make_legs, lot_size_for_expiry,
    modal_step, exec_px, charges, profile_defs, profile_active,
    paired_stats, max_dd
)

def process_expiries(idx, expiries, stage):
    rows=[]; errors=[]; specs=family_specs()
    needed={(typ,int(off)) for fam,g in specs for typ,off,_q in make_legs(fam,g)}
    for oi,ex in enumerate(expiries):
        try:
            ets_map={tm:entry_ts_for(idx,ex,tm) for tm in ENTRY_TIMES}
            entry_days=[x.normalize() for x in ets_map.values() if x is not None]
            cur=load_option_expiry(ex,entry_days)
            lot=lot_size_for_expiry(ex)
            cutoff=ex.normalize()+pd.Timedelta(hours=15,minutes=29)
            day=cur[(cur.timestamp>=ex.normalize())&(cur.timestamp<=cutoff)]
            day_series={}
            for (typ,strike),z in day.groupby(["option_type","strike"],sort=False):
                day_series[(str(typ).upper(),float(strike))]=z.drop_duplicates("timestamp").set_index("timestamp")["close"]
            for tm,ets in ets_map.items():
                if ets is None: continue
                spotrow=idx[idx.timestamp==ets]
                if spotrow.empty: continue
                snap=cur[cur.timestamp==ets]
                step=modal_step(snap)
                if step is None or step<=0:
                    errors.append({"expiry":str(ex.date()),"entry_time":tm,"reason":"missing_modal_step"}); continue
                strikes=snap.strike.unique()
                atm=float(min(strikes,key=lambda k:abs(float(k)-float(spotrow.iloc[-1].spot))))
                entry={}
                for typ,off in needed:
                    k=float(atm+off*step)
                    x=snap[(snap.option_type==typ)&(snap.strike==k)]
                    if not x.empty: entry[(typ,off)]=float(x.iloc[-1].close)
                for fam,g in specs:
                    legs=make_legs(fam,g)
                    if any((typ,int(off)) not in entry for typ,off,_q in legs): continue
                    series=[]; bad=False
                    for typ,off,_q in legs:
                        ss=day_series.get((typ,float(atm+off*step)))
                        if ss is None or ss.empty: bad=True; break
                        series.append(ss)
                    if bad: continue
                    common=series[0].index
                    for ss in series[1:]:
                        common=common.intersection(ss.index)
                        if len(common)==0: break
                    if len(common)==0: continue
                    exit_ts=common.max(); gross=0.0; orders=[]
                    for (typ,off,q),ss in zip(legs,series):
                        ep=entry[(typ,int(off))]; xp=float(ss.loc[exit_ts])
                        epx=exec_px(ep,"buy" if q>0 else "sell")
                        xpx=exec_px(xp,"buy" if q<0 else "sell")
                        gross += q*(xpx-epx)*lot
                        orders += [(ets,"buy" if q>0 else "sell",epx*abs(q)),
                                   (exit_ts,"buy" if q<0 else "sell",xpx*abs(q))]
                    rows.append({
                        "expiry":str(ex.date()),"entry_time":tm,"entry_ts":str(ets),
                        "split":stage,"family":fam,
                        "geom":json.dumps(g,sort_keys=True,separators=(",",":")),
                        "net":gross-charges(orders,lot,1.0),
                        "net50":gross-charges(orders,lot,1.5)
                    })
        except Exception as exc:
            errors.append({"expiry":str(ex.date()),"reason":repr(exc)})
        if oi%10==0:
            pd.DataFrame(rows).to_csv(OUT/f"progress_{stage}.csv",index=False)
    return pd.DataFrame(rows),pd.DataFrame(errors)

def development_stage():
    idx=load_index(); vix=load_vix()
    ex=[d for d in list_expiries() if d<=DEV_END]
    base,errors=process_expiries(idx,ex,"development")
    if base.empty: raise RuntimeError("no development rows")
    base.to_csv(OUT/"stage1_structure_time_matrix.csv",index=False)
    errors.to_csv(OUT/"stage1_data_errors.csv",index=False)
    dev_candidates=[]
    for pid,mode,par in profile_defs():
        for (fam,geom,tm),g in base.groupby(["family","geom","entry_time"]):
            if len(g)<15: continue
            mask=[profile_active(vix,pd.Timestamp(x),par,mode) for x in g.entry_ts]
            gz=g.loc[mask]
            if len(gz)<10: continue
            common=g[["expiry","net"]].merge(gz[["expiry","net"]],on="expiry",suffixes=("_base","_cand"))
            upl=common.net_cand-common.net_base
            st=paired_stats(upl)
            dev_candidates.append({
                "family":fam,"geom":geom,"entry_time":int(tm),"profile_id":pid,"mode":mode,
                "dev_n":len(gz),"dev_net":float(gz.net.sum()),"dev_net50":float(gz.net50.sum()),
                "dev_dd":max_dd(gz.sort_values("expiry").net.to_numpy()),
                "dev_uplift":float(upl.sum()),"dev_uplift_mean":st["mean"],
                "dev_ci_lo":st["ci_lo"],"dev_ci_hi":st["ci_hi"]
            })
    all_dc=pd.DataFrame(dev_candidates)
    if all_dc.empty: raise RuntimeError("no development profile rows")
    all_dc.to_csv(OUT/"stage1_all_dev_profiles.csv",index=False)
    dc=all_dc[(all_dc.dev_net>=0)&(all_dc.dev_net50>0)&(all_dc.dev_uplift>0)].sort_values(["dev_uplift_mean","dev_net"],ascending=False)
    picked=[]; counts={}
    for r in dc.itertuples(index=False):
        if counts.get(r.family,0)>=5: continue
        picked.append(r._asdict()); counts[r.family]=counts.get(r.family,0)+1
        if len(picked)>=30: break
    frozen=pd.DataFrame(picked,columns=dc.columns)
    frozen.to_csv(OUT/"frozen_dev_shortlist.csv",index=False)
    frozen.to_csv(OUT/"stage1_candidates.csv",index=False)
    frozen.to_csv(OUT/"frozen_stage1.csv",index=False)
    summary={
        "status":"COMPLETE_STAGE1_DEVELOPMENT","stage1_rows":len(base),
        "development_profile_rows":len(all_dc),"candidate_rows":len(dc),
        "frozen_candidates":len(frozen),"holm_survivors":0,
        "holdout_opened_after_validation_freeze":False,
        "decision":"DEVELOPMENT_FROZEN_VALIDATION_PENDING"
    }
    (OUT/"stage1_summary.json").write_text(json.dumps(summary,indent=2))
    return summary

def validation_stage():
    idx=load_index(); vix=load_vix()
    frozen=pd.read_csv(OUT/"frozen_stage1.csv")
    if frozen.empty: raise RuntimeError("empty development freeze")
    ex=[d for d in list_expiries() if DEV_END<d<=VAL_END]
    base,errors=process_expiries(idx,ex,"validation")
    base.to_csv(OUT/"validation_structure_time_matrix.csv",index=False)
    errors.to_csv(OUT/"validation_data_errors.csv",index=False)
    rows=[]; profiles=profile_defs()
    for r in frozen.itertuples(index=False):
        g=base[(base.family==r.family)&(base.geom==r.geom)&(base.entry_time==r.entry_time)]
        par=next(par for pid,mm,par in profiles if pid==r.profile_id and mm==r.mode)
        mask=[profile_active(vix,pd.Timestamp(x),par,r.mode) for x in g.entry_ts]
        gz=g.loc[mask]
        common=g[["expiry","net","net50"]].merge(gz[["expiry","net"]],on="expiry",suffixes=("_base","_cand"))
        diff=(common.net_cand-common.net_base).to_numpy(float)
        st=paired_stats(diff)
        pos=diff[diff>0]
        conc=float(pos.max()/pos.sum()) if len(pos) and pos.sum()>0 else np.nan
        bdd=max_dd(g.sort_values("expiry").net.to_numpy()) if len(g) else np.nan
        rows.append({**r._asdict(),"val_n":len(gz),"val_net":float(gz.net.sum()) if len(gz) else np.nan,
            "val_net50":float(gz.net50.sum()) if len(gz) else np.nan,
            "val_dd":max_dd(gz.sort_values("expiry").net.to_numpy()) if len(gz) else np.nan,
            "base_val_net":float(g.net.sum()) if len(g) else np.nan,"base_val_dd":bdd,
            "val_uplift":float(diff.sum()) if len(diff) else np.nan,"val_uplift_mean":st["mean"],
            "val_ci_lo":st["ci_lo"],"val_ci_hi":st["ci_hi"],"val_p":st["p"],
            "common_n":len(common),"max_positive_uplift_share":conc})
    vd=pd.DataFrame(rows)
    if len(vd):
        vd["validation_gate"]=(vd.val_n>=20)&(vd.val_net>0)&(vd.val_net50>0)&(vd.val_uplift>0)&(vd.val_ci_lo>0)&(vd.val_dd<=1.25*vd.base_val_dd)&(vd.max_positive_uplift_share<=0.40)
        from phase44_vix_tuning import holm
        vd["val_p_holm"]=holm(vd.val_p.fillna(1).to_numpy())
        vd["inference_survivor"]=vd.validation_gate&(vd.val_p_holm<0.05)
    vd.to_csv(OUT/"validation_confirmation.csv",index=False)
    summary={
        "status":"COMPLETE_STAGE2_VALIDATION","stage1_rows":len(base),
        "candidate_rows":len(vd),"frozen_candidates":int(vd.validation_gate.sum()) if len(vd) else 0,
        "holm_survivors":int(vd.inference_survivor.sum()) if len(vd) else 0,
        "holdout_opened_after_validation_freeze":False,
        "decision":"VALIDATION_PASS_HOLDOUT_PENDING" if len(vd) and vd.inference_survivor.any() else "NO_STAGE2_SURVIVOR"
    }
    (OUT/"validation_summary.json").write_text(json.dumps(summary,indent=2))
    return summary

def holdout_stage():
    idx=load_index(); vix=load_vix()
    vd=pd.read_csv(OUT/"validation_confirmation.csv")
    hs=vd[vd.inference_survivor==True] if not vd.empty else vd
    ex=[d for d in list_expiries() if d>VAL_END]
    base,errors=process_expiries(idx,ex,"holdout")
    base.to_csv(OUT/"holdout_structure_time_matrix.csv",index=False)
    errors.to_csv(OUT/"holdout_data_errors.csv",index=False)
    profiles=profile_defs(); rows=[]
    for r in hs.itertuples(index=False):
        g=base[(base.family==r.family)&(base.geom==r.geom)&(base.entry_time==r.entry_time)]
        par=next(par for pid,mm,par in profiles if pid==r.profile_id and mm==r.mode)
        mask=[profile_active(vix,pd.Timestamp(x),par,r.mode) for x in g.entry_ts]
        hz=g.loc[mask]
        if hz.empty: continue
        common=g[["expiry","net","net50"]].merge(hz[["expiry","net"]],on="expiry",suffixes=("_base","_cand"))
        diff=(common.net_cand-common.net_base).to_numpy(float); st=paired_stats(diff)
        rows.append({**r._asdict(),"hold_n":len(hz),"hold_net":float(hz.net.sum()),
            "hold_net50":float(hz.net50.sum()),"hold_dd":max_dd(hz.sort_values("expiry").net.to_numpy()),
            "hold_uplift":float(diff.sum()) if len(diff) else np.nan,"hold_uplift_mean":st["mean"],
            "hold_ci_lo":st["ci_lo"],"hold_ci_hi":st["ci_hi"],"hold_p":st["p"],"hold_common_n":len(common)})
    hd=pd.DataFrame(rows)
    if len(hd):
        from phase44_vix_tuning import holm
        hd["hold_p_holm"]=holm(hd.hold_p.fillna(1).to_numpy())
        hd["promotion_gate"]=(hd.hold_n>=10)&(hd.hold_net>0)&(hd.hold_net50>0)&(hd.hold_uplift>0)&(hd.hold_ci_lo>0)&(hd.hold_p_holm<0.05)
    hd.to_csv(OUT/"frozen_holdout_confirmation.csv",index=False)
    hd.to_csv(OUT/"frozen_stage1_holdout.csv",index=False)
    summary={
        "status":"COMPLETE_STAGE3_HOLDOUT","stage1_rows":len(base),
        "candidate_rows":len(hd),"frozen_candidates":len(hs),
        "holm_survivors":int(hd.promotion_gate.sum()) if len(hd) else 0,
        "holdout_opened_after_validation_freeze":True,
        "decision":"PROMOTION_CANDIDATE" if len(hd) and hd.promotion_gate.any() else "NO_HOLDOUT_PROMOTION"
    }
    (OUT/"holdout_summary.json").write_text(json.dumps(summary,indent=2))
    return summary

def main():
    stage=os.getenv("PHASE44_STAGE","development").lower()
    if stage=="development": s=development_stage()
    elif stage=="validation": s=validation_stage()
    elif stage=="holdout": s=holdout_stage()
    else: raise ValueError(stage)
    print(json.dumps(s,indent=2))

if __name__=="__main__":
    main()
