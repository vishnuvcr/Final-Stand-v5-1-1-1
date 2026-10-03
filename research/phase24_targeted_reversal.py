import os, sys, json, math
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from research.phase23_model import (
    GROUPS, GroupTransformer, build_derived, fit_model, max_dd,
    safe_auc, bootstrap_ci, TRAIN_END, VALIDATION_END, HOLDOUT_START
)

OUT = Path("results/dynamic_n_corrected/phase24_targeted_reversal")
OUT.mkdir(parents=True, exist_ok=True)
FEATURES = Path("results/dynamic_n_corrected/phase23_entry_state/phase23_entry_features.csv")
CAN = Path("results/dynamic_n_corrected/phase23_entry_state/canonical_trade_ledger.csv")
REV = Path("results/dynamic_n_corrected/phase23_entry_state/reverse_trade_ledger.csv")

LOSS_THRESHOLDS = [0.65,0.70,0.75,0.80,0.85,0.90,0.95]
REV_THRESHOLDS = [0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95]
MARGIN_THRESHOLDS = [-0.10,0.00,0.05,0.10,0.15,0.20,0.25,0.30]
BOOTSTRAP_B = 5000
RNG = np.random.default_rng(20261004)


def metrics(frame, action):
    ctrl=frame.canonical_net.to_numpy(dtype=float)
    policy=np.where(action=="REVERSE",frame.reverse_net.to_numpy(dtype=float),ctrl)
    winners=ctrl>0
    reversed_loss=(ctrl<0)&(action=="REVERSE")
    reversed_win=(ctrl>0)&(action=="REVERSE")
    winner_to_loss=(winners)&(policy<0)
    pos_pnl=float(ctrl[ctrl>0].sum())
    sacrificed=float(ctrl[reversed_win].sum())
    return {
        "trades":len(frame),
        "canonical_net":float(ctrl.sum()),
        "policy_net":float(policy.sum()),
        "uplift":float(policy.sum()-ctrl.sum()),
        "winner_retention":float(np.mean(policy[winners]>0)) if winners.any() else np.nan,
        "canonical_winners":int(winners.sum()),
        "policy_winners":int((policy>0).sum()),
        "canonical_losses":int((ctrl<0).sum()),
        "losses_reversed":int(reversed_loss.sum()),
        "winning_trades_reversed":int(reversed_win.sum()),
        "winner_to_loss_count":int(winner_to_loss.sum()),
        "winner_pnl_sacrificed":sacrificed,
        "winner_pnl_sacrificed_pct":float(sacrificed/pos_pnl) if pos_pnl>0 else np.nan,
        "reverse_count":int((action=="REVERSE").sum()),
        "canonical_count":int((action!="REVERSE").sum()),
        "profit_factor":float(policy[policy>0].sum()/(-policy[policy<0].sum())) if np.any(policy<0) else np.inf,
        "max_dd":max_dd(policy),
        "worst_trade":float(policy.min()),
        "cvar5":float(np.mean(np.sort(policy)[:max(1,int(math.ceil(0.05*len(policy))))])),
    }


def eval_rule(frame, p_loss, p_rev, family, L, R, M):
    action=np.full(len(frame),"CANONICAL",dtype=object)
    gate=(p_loss>=L)&(p_rev>=R)&frame.reverse_available.to_numpy()
    if family=="B":
        gate=gate & ((p_rev-p_loss)>=M)
    action[gate]="REVERSE"
    out=metrics(frame,action)
    return action,out


def main():
    feat=pd.read_csv(FEATURES)
    can=pd.read_csv(CAN)
    rev=pd.read_csv(REV)

    for df in (feat,can,rev):
        df["entry_date"]=pd.to_datetime(df["entry_date"],errors="coerce").dt.normalize()
    can=can[["expiry","entry_date","net"]].rename(columns={"net":"canonical_net"})
    rev=rev[["expiry","net"]].rename(columns={"net":"reverse_net"})

    x=feat.merge(can,on=["expiry","entry_date"],how="inner").merge(rev,on="expiry",how="left")
    expected=set(can["expiry"].astype(str)+"|"+can["entry_date"].dt.strftime("%Y-%m-%d"))
    actual=set(x["expiry"].astype(str)+"|"+x["entry_date"].dt.strftime("%Y-%m-%d"))
    if expected!=actual or len(x)!=len(can):
        raise RuntimeError(f"Universe mismatch: canonical={len(can)} merged={len(x)} missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    x["reverse_available"]=x.reverse_net.notna()
    x["canonical_loss"]=(x.canonical_net<0).astype(int)
    x["reverse_better"]=np.where(x.reverse_available,(x.reverse_net>x.canonical_net).astype(int),np.nan)
    x=build_derived(x).copy().sort_values("entry_date").reset_index(drop=True)

    train=x[x.entry_date<=TRAIN_END].copy()
    val=x[(x.entry_date>TRAIN_END)&(x.entry_date<=VALIDATION_END)].copy()
    hold=x[x.entry_date>=HOLDOUT_START].copy()
    if len(train)+len(val)+len(hold)!=len(x):
        raise RuntimeError("Temporal split does not conserve trades")
    if train.canonical_loss.nunique()<2 or train[train.reverse_available].reverse_better.nunique()<2:
        raise RuntimeError("Training model labels lack two classes")

    gt=GroupTransformer().fit(train)
    loss_model=fit_model(gt.transform(train),train.canonical_loss.to_numpy())
    rev_train=train[train.reverse_available].copy()
    rev_model=fit_model(gt.transform(rev_train),rev_train.reverse_better.to_numpy())

    p_loss_all=loss_model.predict_proba(gt.transform(x))[:,1]
    rev_map=dict(zip(rev_train.expiry,rev_model.predict_proba(gt.transform(rev_train))[:,1]))
    p_rev_all=np.array([rev_map.get(e,0.0) for e in x.expiry])

    idx_train=np.where(x.entry_date.to_numpy()<=TRAIN_END.to_datetime64())[0]
    idx_val=np.where((x.entry_date.to_numpy()>TRAIN_END.to_datetime64())&(x.entry_date.to_numpy()<=VALIDATION_END.to_datetime64()))[0]
    idx_hold=np.where(x.entry_date.to_numpy()>=HOLDOUT_START.to_datetime64())[0]

    candidates=[]
    for family in ["A","B"]:
        for L in LOSS_THRESHOLDS:
            for R in REV_THRESHOLDS:
                margins=MARGIN_THRESHOLDS if family=="B" else [-np.inf]
                for M in margins:
                    acts,mm=eval_rule(train,p_loss_all[idx_train],p_rev_all[idx_train],family,L,R,M)
                    eligible=(
                        mm["uplift"]>0 and
                        mm["losses_reversed"]>=1 and
                        mm["winner_retention"]>=0.95 and
                        mm["winner_to_loss_count"]==0 and
                        mm["winner_pnl_sacrificed_pct"]<=0.05
                    )
                    candidates.append({
                        "family":family,"L":L,"R":R,"M":M,"eligible_training":eligible,**mm
                    })
    grid=pd.DataFrame(candidates)

    elig=grid[grid.eligible_training].copy()
    if len(elig):
        # Highest thresholds and margin define sparsity / least-aggressive selection.
        elig["M_sort"]=elig["M"].replace(-np.inf,-999.0)
        selected=elig.sort_values(["L","R","M_sort","uplift"],ascending=[False,False,False,False]).iloc[0]
        selection_basis="least-aggressive qualifying rule"
    else:
        grid["M_sort"]=grid["M"].replace(-np.inf,-999.0)
        selected=grid.sort_values(["uplift","L","R","M_sort"],ascending=[False,False,False,False]).iloc[0]
        selection_basis="no training-eligible rule; diagnostic closest candidate only"

    family=str(selected.family); L=float(selected.L); R=float(selected.R); M=float(selected.M)

    results=[]
    ledgers=[]
    for period,ix in [("training",idx_train),("validation",idx_val),("holdout",idx_hold)]:
        frame=x.iloc[ix].copy().reset_index(drop=True)
        pl=p_loss_all[ix]; pr=p_rev_all[ix]
        act,mm=eval_rule(frame,pl,pr,family,L,R,M)
        mm.update({"period":period,"family":family,"L":L,"R":R,"M":M})
        results.append(mm)
        led=frame[["expiry","entry_date","selected_direction","canonical_net","reverse_net","reverse_available"]].copy()
        led["p_loss"]=pl
        led["p_reverse"]=pr
        led["reverse_margin"]=pr-pl
        led["action"]=act
        led["policy_net"]=np.where(act=="REVERSE",led.reverse_net,led.canonical_net)
        led["period"]=period
        ledgers.append(led)

    summary=pd.DataFrame(results)

    # Bootstrap uplift confidence intervals for OOS periods.
    boot=[]
    for period,ix in [("validation",idx_val),("holdout",idx_hold)]:
        frame=x.iloc[ix].copy().reset_index(drop=True)
        pl=p_loss_all[ix]; pr=p_rev_all[ix]
        act,_=eval_rule(frame,pl,pr,family,L,R,M)
        diff=np.where(act=="REVERSE",frame.reverse_net.to_numpy()-frame.canonical_net.to_numpy(),0.0)
        mean,lo,hi=bootstrap_ci(diff,b=BOOTSTRAP_B)
        boot.append({"period":period,"uplift_mean":mean,"uplift_ci_low":lo,"uplift_ci_high":hi})
    boot_df=pd.DataFrame(boot)

    # OOS promotion screen.
    tr,va,ho=[summary[summary.period.eq(p)].iloc[0].to_dict() for p in ["training","validation","holdout"]]
    dd_val=float(va["max_dd"]); dd_hold=float(ho["max_dd"])
    baseline_val=max_dd(val.canonical_net); baseline_hold=max_dd(hold.canonical_net)
    promotion={
        "selected_family":family,"L":L,"R":R,"M":M,
        "selection_basis":selection_basis,
        "training_gate_pass":bool(selected.eligible_training),
        "validation_uplift_positive":bool(va["uplift"]>0),
        "holdout_uplift_positive":bool(ho["uplift"]>0),
        "validation_winner_retention_ge_90":bool(va["winner_retention"]>=0.90),
        "holdout_winner_retention_ge_90":bool(ho["winner_retention"]>=0.90),
        "validation_no_winner_to_loss":bool(va["winner_to_loss_count"]==0),
        "holdout_no_winner_to_loss":bool(ho["winner_to_loss_count"]==0),
        "validation_dd_ok":bool(dd_val<=1.05*baseline_val),
        "holdout_dd_ok":bool(dd_hold<=1.05*baseline_hold),
        "oos_loss_reversed":bool((va["losses_reversed"]+ho["losses_reversed"])>=1),
        "promotion_pass":bool(
            selected.eligible_training and
            va["uplift"]>0 and ho["uplift"]>0 and
            va["winner_retention"]>=0.90 and ho["winner_retention"]>=0.90 and
            va["winner_to_loss_count"]==0 and ho["winner_to_loss_count"]==0 and
            dd_val<=1.05*baseline_val and dd_hold<=1.05*baseline_hold and
            (va["losses_reversed"]+ho["losses_reversed"])>=1
        )
    }

    grid.to_csv(OUT/"phase24_training_grid.csv",index=False)
    summary.to_csv(OUT/"phase24_selected_rule_walkforward.csv",index=False)
    pd.concat(ledgers,ignore_index=True).sort_values("entry_date").to_csv(OUT/"phase24_trade_level.csv",index=False)
    boot_df.to_csv(OUT/"phase24_bootstrap.csv",index=False)
    (OUT/"phase24_selected_rule.json").write_text(json.dumps({
        "family":family,"L":L,"R":R,"M":M,"selection_basis":selection_basis
    },indent=2))
    (OUT/"phase24_promotion_gate.json").write_text(json.dumps(promotion,indent=2))
    print(json.dumps({"selection":selection_basis,"selected":{"family":family,"L":L,"R":R,"M":M},"promotion":promotion,"summary":results},indent=2))

if __name__=="__main__":
    main()
