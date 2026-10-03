import json, math, os, re, sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.inspection import permutation_importance

OUT = Path("results/dynamic_n_corrected/phase23_entry_state")
FEATURES = OUT / "phase23_entry_features.csv"
CAN = OUT / "canonical_trade_ledger.csv"
REV = OUT / "reverse_trade_ledger.csv"
RNG = np.random.default_rng(20261003)
BOOTSTRAP_B = 5000

TRAIN_END = pd.Timestamp("2023-12-31")
VALIDATION_END = pd.Timestamp("2025-12-31")
HOLDOUT_START = pd.Timestamp("2026-01-01")

SKIP_THRESHOLDS = [0.55,0.60,0.65,0.70,0.75,0.80]
REVERSE_THRESHOLDS = [0.55,0.60,0.65,0.70,0.75,0.80]

GROUPS = {
    "vix_volatility": [
        "india_vix_prev","india_vix_change1","nifty_rv5","nifty_rv10","nifty_rv20","us_vix_ret1"
    ],
    "cross_market": [
        "sp500_ret1","nasdaq_ret1","dow_ret1","nikkei_ret1","hangseng_ret1",
        "kospi_ret1","shanghai_ret1","usd_inr_ret1","gold_ret1","brent_ret1","us10y_ret1"
    ],
    "opening_regime": [
        "overnight_gap_pct","ret_10am_pct","range_to_10am_pct","nifty_ret1"
    ],
    "direction_confidence": [
        "direction_margin"
    ],
    "option_geometry": [
        "selected_x","selected_x_over_long_premium"
    ],
    "payoff_geometry": [
        "boundary_z","boundary_distance"
    ],
    "oi_volume": [
        "put_call_oi_ratio"
    ],
    "iv_skew_structure": [
        "iv_proxy_call_minus_put","selected_x_over_xmax","selected_n"
    ],
}

# Group definitions are preregistered; component transformations are fixed.
LOG_COMPONENTS = {
    "india_vix_prev","nifty_rv5","nifty_rv10","nifty_rv20",
    "selected_x","selected_x_over_long_premium","boundary_distance",
    "put_call_oi_ratio","selected_n"
}


def max_dd(vals):
    running=peak=dd=0.0
    for x in vals:
        running += float(x)
        peak=max(peak,running)
        dd=max(dd,peak-running)
    return float(dd)


def bootstrap_ci(x, b=BOOTSTRAP_B):
    x=np.asarray(x,dtype=float)
    x=x[np.isfinite(x)]
    if len(x)==0:
        return [np.nan,np.nan,np.nan]
    means=np.empty(b)
    for i in range(b):
        means[i]=x[RNG.integers(0,len(x),len(x))].mean()
    return [float(np.mean(x)),float(np.quantile(means,0.025)),float(np.quantile(means,0.975))]


def safe_auc(y,p):
    y=np.asarray(y); p=np.asarray(p)
    if len(np.unique(y))<2: return np.nan
    return float(roc_auc_score(y,p))


def transform_component(s,name):
    x=pd.to_numeric(s,errors="coerce").astype(float)
    if name in LOG_COMPONENTS:
        if name in {"selected_n"}:
            return np.log1p(np.clip(x,0,None))
        if name in {"iv_proxy_call_minus_put"}:
            return x
        # signed features get asinh-style compression when negative values are possible
        if (x.dropna()<0).any():
            return np.sign(x)*np.log1p(np.abs(x))
        return np.log1p(np.clip(x,0,None))
    return x


class GroupTransformer:
    def __init__(self):
        self.component_stats={}
        self.group_medians={}
        self.group_scales={}
    def fit(self, df):
        zparts={}
        for g,cols in GROUPS.items():
            for col in cols:
                x=transform_component(df[col] if col in df else pd.Series(index=df.index,dtype=float),col)
                med=float(x.median()) if x.notna().any() else 0.0
                mad=float((x-med).abs().median()) if x.notna().any() else 1.0
                scale=max(1.4826*mad, 1e-8)
                self.component_stats[col]=(med,scale)
            vals=[]
            for col in cols:
                x=transform_component(df[col] if col in df else pd.Series(index=df.index,dtype=float),col)
                med,scale=self.component_stats[col]
                vals.append(((x-med)/scale).rename(col))
            gscore=pd.concat(vals,axis=1).mean(axis=1,skipna=True)
            med=float(gscore.median()) if gscore.notna().any() else 0.0
            scale=float(gscore.std(ddof=0)) if gscore.notna().sum()>1 else 1.0
            if not np.isfinite(scale) or scale<1e-8: scale=1.0
            self.group_medians[g]=med
            self.group_scales[g]=scale
        return self
    def transform(self,df):
        out=pd.DataFrame(index=df.index)
        for g,cols in GROUPS.items():
            vals=[]
            for col in cols:
                x=transform_component(df[col] if col in df else pd.Series(index=df.index,dtype=float),col)
                med,scale=self.component_stats[col]
                vals.append(((x-med)/scale).rename(col))
            z=pd.concat(vals,axis=1).mean(axis=1,skipna=True)
            z=z.fillna(self.group_medians[g])
            out[g]=(z-self.group_medians[g])/self.group_scales[g]
        return out


def build_derived(df):
    x=df.copy()
    dsign=np.where(x.selected_direction.eq("BULLISH"),1.0,-1.0)
    x["directional_cross_market"]=dsign*x[["sp500_ret1","nasdaq_ret1","dow_ret1","nikkei_ret1","hangseng_ret1","kospi_ret1","shanghai_ret1"]].mean(axis=1,skipna=True)
    x["directional_open"]=dsign*x["ret_10am_pct"]
    x["directional_gap"]=dsign*x["overnight_gap_pct"]
    # Add selected-side OI/volume shares using entry-time strike snapshot.
    oi_share=[]; vol_share=[]
    for _,r in x.iterrows():
        side="CE" if r.selected_direction=="BEARISH" else "PE"
        n=r.selected_n
        if pd.isna(n):
            oi_share.append(np.nan); vol_share.append(np.nan); continue
        n=int(n)
        oi=float(r.get(f"{side}_oi{n}",np.nan))
        vol=float(r.get(f"{side}_vol{n}",np.nan))
        side_oi=np.nansum([r.get(f"{side}_oi{k}",np.nan) for k in range(6,18)])
        side_vol=np.nansum([r.get(f"{side}_vol{k}",np.nan) for k in range(6,18)])
        oi_share.append(oi/side_oi if np.isfinite(oi) and side_oi>0 else np.nan)
        vol_share.append(vol/side_vol if np.isfinite(vol) and side_vol>0 else np.nan)
    x["selected_oi_share"]=oi_share
    x["selected_volume_share"]=vol_share
    x["directional_iv_skew"]=np.where(
        x.selected_direction.eq("BEARISH"), x["CE_iv_skew_6_17"], x["PE_iv_skew_6_17"]
    )
    # Replace the fixed group component with aligned variables where useful.
    GROUPS["cross_market"] = [
        "directional_cross_market","usd_inr_ret1","gold_ret1","brent_ret1","us10y_ret1"
    ]
    GROUPS["opening_regime"] = [
        "directional_gap","directional_open","range_to_10am_pct"
    ]
    GROUPS["oi_volume"] = [
        "put_call_oi_ratio","selected_oi_share","selected_volume_share"
    ]
    GROUPS["iv_skew_structure"] = [
        "directional_iv_skew","iv_proxy_call_minus_put","selected_x_over_xmax","selected_n"
    ]
    return x


def policy_metrics(x, action_col="action"):
    returns=[]
    actions=[]
    for _,r in x.sort_values("entry_date").iterrows():
        a=r[action_col]
        if a=="REVERSE" and pd.notna(r.reverse_net):
            v=float(r.reverse_net)
        elif a=="SKIP":
            v=0.0
        else:
            v=float(r.canonical_net)
        returns.append(v); actions.append(a)
    arr=np.asarray(returns,float)
    control=np.asarray(x.sort_values("entry_date").canonical_net,float)
    winner_mask=control>0
    winners_retained=float(np.mean(arr[winner_mask]>0)) if winner_mask.any() else np.nan
    losers_removed=int(np.sum((control<0)&(arr>control)))
    baseline_loss_abs=float(-control[control<0].sum())
    policy_loss_abs=float(-arr[arr<0].sum())
    gains_removed=float(control[(control>0)&(arr<=control)] .sum()) if winner_mask.any() else 0.0
    out={
        "trades":len(arr),
        "net_pnl":float(arr.sum()),
        "control_net_pnl":float(control.sum()),
        "uplift":float(arr.sum()-control.sum()),
        "win_count":int(np.sum(arr>0)),
        "winner_retention":winners_retained,
        "control_winners":int(winner_mask.sum()),
        "losses":int(np.sum(arr<0)),
        "profit_factor":float(arr[arr>0].sum() / (-arr[arr<0].sum())) if np.any(arr<0) else np.inf,
        "max_dd":max_dd(arr),
        "worst_trade":float(arr.min()),
        "cvar5":float(np.mean(np.sort(arr)[:max(1,int(math.ceil(0.05*len(arr))))])),
        "skip_count":actions.count("SKIP"),
        "reverse_count":actions.count("REVERSE"),
        "canonical_count":actions.count("CANONICAL"),
        "losing_pnl_removed":float(baseline_loss_abs - (-arr[(control<0)&(arr<0)].sum())),
        "winner_pnl_sacrificed":float(gains_removed),
        "top_trade_uplift_share":float(np.max(np.abs(arr-control))/max(abs(float(arr.sum()-control.sum())),1e-9)) if len(arr) else np.nan,
    }
    return out, np.asarray(actions)


def fit_model(X, y):
    model=LogisticRegression(C=0.5,solver="liblinear",class_weight="balanced",random_state=20261003,max_iter=2000)
    model.fit(X,y)
    return model


def evaluate_policy(df,p_loss,p_rev,t_skip,t_rev):
    out=df.copy()
    out["p_loss"]=p_loss
    out["p_reverse"]=p_rev
    action=np.full(len(out),"CANONICAL",dtype=object)
    reverse_ok=out.reverse_available.astype(bool).to_numpy()
    action[(reverse_ok)&(p_rev>=t_rev)]="REVERSE"
    action[(action=="CANONICAL")&(p_loss>=t_skip)]="SKIP"
    out["action"]=action
    return out


def main():
    feat=pd.read_csv(FEATURES)
    can=pd.read_csv(CAN)
    rev=pd.read_csv(REV)

    feat["entry_date"]=pd.to_datetime(feat.entry_date,errors="coerce").dt.normalize()
    can["entry_date"]=pd.to_datetime(can.entry_date,errors="coerce").dt.normalize()
    rev["entry_date"]=pd.to_datetime(rev.entry_date,errors="coerce").dt.normalize()

    can=can[["expiry","entry_date","net","mfe","exit_reason"]].rename(columns={"net":"canonical_net"})
    rev=rev[["expiry","net"]].rename(columns={"net":"reverse_net"})
    x=feat.merge(can,on=["expiry","entry_date"],how="inner").merge(rev,on="expiry",how="left")
    expected_keys=set(can["expiry"].astype(str)+"|"+can["entry_date"].dt.strftime("%Y-%m-%d"))
    actual_keys=set(x["expiry"].astype(str)+"|"+x["entry_date"].dt.strftime("%Y-%m-%d"))
    missing_keys=sorted(expected_keys-actual_keys)
    extra_keys=sorted(actual_keys-expected_keys)
    pd.DataFrame([{
        "expected_canonical_trades":len(expected_keys),
        "merged_trades":len(actual_keys),
        "missing_keys":";".join(missing_keys),
        "extra_keys":";".join(extra_keys),
    }]).to_csv(OUT/"phase23_universe_alignment.csv",index=False)
    if missing_keys or extra_keys or len(x)!=len(can):
        raise RuntimeError(f"Phase 23 universe misalignment: expected {len(can)}, merged {len(x)}, missing={missing_keys}, extra={extra_keys}")
    x["reverse_available"]=x.reverse_net.notna()
    x["canonical_loss"]=(x.canonical_net<0).astype(int)
    x["reverse_better"]=np.where(x.reverse_available,(x.reverse_net>x.canonical_net).astype(int),np.nan)
    x=build_derived(x).copy()

    # Keep only the 190-trade canonical universe.
    x=x.sort_values("entry_date").reset_index(drop=True)

    train=x[x.entry_date<=TRAIN_END].copy()
    val=x[(x.entry_date>TRAIN_END)&(x.entry_date<=VALIDATION_END)].copy()
    hold=x[x.entry_date>=HOLDOUT_START].copy()

    period_total=len(train)+len(val)+len(hold)
    if period_total != len(x):
        raise RuntimeError(f"Phase 23 temporal split lost trades: merged={len(x)}, split_sum={period_total}")

    if train.canonical_loss.nunique()<2:
        raise RuntimeError("Training canonical-loss label lacks both classes")
    rev_train=train[train.reverse_available].copy()
    if rev_train.reverse_better.nunique()<2:
        raise RuntimeError("Training reverse-better label lacks both classes")

    gt=GroupTransformer().fit(train)
    Xtr=gt.transform(train)
    Xva=gt.transform(val)
    Xho=gt.transform(hold)

    loss_model=fit_model(Xtr,train.canonical_loss.to_numpy())
    rev_model=fit_model(gt.transform(rev_train),rev_train.reverse_better.to_numpy())

    p_loss_tr=loss_model.predict_proba(Xtr)[:,1]
    p_loss_va=loss_model.predict_proba(Xva)[:,1]
    p_loss_ho=loss_model.predict_proba(Xho)[:,1]

    p_rev_tr=np.zeros(len(train))
    p_rev_va=np.zeros(len(val)); p_rev_ho=np.zeros(len(hold))
    idx=rev_train.index
    p_rev_tr[idx.to_numpy()-train.index.min() if False else 0:0]=0
    # map by expiry/row index for robustness
    rev_map_train=dict(zip(rev_train.expiry,rev_model.predict_proba(gt.transform(rev_train))[:,1]))
    rev_map_val={}
    rev_map_hold={}
    rev_val=val[val.reverse_available].copy(); rev_hold=hold[hold.reverse_available].copy()
    if len(rev_val): rev_map_val=dict(zip(rev_val.expiry,rev_model.predict_proba(gt.transform(rev_val))[:,1]))
    if len(rev_hold): rev_map_hold=dict(zip(rev_hold.expiry,rev_model.predict_proba(gt.transform(rev_hold))[:,1]))
    p_rev_tr=np.array([rev_map_train.get(e,0.0) for e in train.expiry])
    p_rev_va=np.array([rev_map_val.get(e,0.0) for e in val.expiry])
    p_rev_ho=np.array([rev_map_hold.get(e,0.0) for e in hold.expiry])

    # Training threshold selection under the preregistered safety screen.
    candidate_rows=[]
    for ts in SKIP_THRESHOLDS:
        for trv in REVERSE_THRESHOLDS:
            pol=evaluate_policy(train,p_loss_tr,p_rev_tr,ts,trv)
            m,_=policy_metrics(pol)
            eligible=(m["winner_retention"]>=0.95 and m["uplift"]>0)
            candidate_rows.append({"mode":"combined","skip_threshold":ts,"reverse_threshold":trv,"eligible_training":eligible,**m})
    for ts in SKIP_THRESHOLDS:
        pol=train.copy()
        pol["action"]=np.where(p_loss_tr>=ts,"SKIP","CANONICAL")
        m,_=policy_metrics(pol)
        eligible=(m["winner_retention"]>=0.95 and m["uplift"]>0)
        candidate_rows.append({"mode":"skip_only","skip_threshold":ts,"reverse_threshold":np.nan,"eligible_training":eligible,**m})
    for trv in REVERSE_THRESHOLDS:
        pol=train.copy()
        pol["action"]=np.where((p_rev_tr>=trv)&train.reverse_available.to_numpy(),"REVERSE","CANONICAL")
        m,_=policy_metrics(pol)
        eligible=(m["winner_retention"]>=0.95 and m["uplift"]>0)
        candidate_rows.append({"mode":"reverse_only","skip_threshold":np.nan,"reverse_threshold":trv,"eligible_training":eligible,**m})
    grid=pd.DataFrame(candidate_rows)
    choices={}
    for mode in ["combined","skip_only","reverse_only"]:
        sub=grid[grid["mode"].eq(mode)]
        elig=sub[sub.eligible_training]
        choices[mode]=(elig.sort_values(["uplift","winner_retention","reverse_count"],ascending=[False,False,True]).iloc[0]
                       if len(elig) else sub.sort_values(["uplift","winner_retention"],ascending=[False,False]).iloc[0])
    chosen=choices["combined"]
    ts=float(chosen.skip_threshold)
    trv=float(chosen.reverse_threshold)
    pol_train=evaluate_policy(train,p_loss_tr,p_rev_tr,ts,trv)
    pol_val=evaluate_policy(val,p_loss_va,p_rev_va,ts,trv)
    pol_hold=evaluate_policy(hold,p_loss_ho,p_rev_ho,ts,trv)
    metrics_train,_=policy_metrics(pol_train); metrics_validation,_=policy_metrics(pol_val); metrics_holdout,_=policy_metrics(pol_hold)

    # Bootstrap P&L uplift CIs on frozen validation/holdout policy.
    for frame,name in [(pol_val,"validation"),(pol_hold,"holdout")]:
        ctrl=frame.canonical_net.to_numpy(dtype=float)
        pol=[]
        for _,r in frame.iterrows():
            if r.action=="SKIP": pol.append(0.0)
            elif r.action=="REVERSE" and pd.notna(r.reverse_net): pol.append(float(r.reverse_net))
            else: pol.append(float(r.canonical_net))
        diff=np.asarray(pol)-ctrl
        ci=bootstrap_ci(diff)
        if name=="validation": metrics_validation["uplift_bootstrap_mean"],metrics_validation["uplift_ci_low"],metrics_validation["uplift_ci_high"]=ci
        else: metrics_holdout["uplift_bootstrap_mean"],metrics_holdout["uplift_ci_low"],metrics_holdout["uplift_ci_high"]=ci

    # Year / regime breakdown of frozen policy.
    pol_all=pd.concat([
        pol_train.assign(period="training"),
        pol_val.assign(period="validation"),
        pol_hold.assign(period="holdout")
    ],ignore_index=True)
    pol_all["policy_net"]=np.where(pol_all.action.eq("SKIP"),0.0,
                                    np.where(pol_all.action.eq("REVERSE"),pol_all.reverse_net,pol_all.canonical_net))
    pol_all["year"]=pd.to_datetime(pol_all.entry_date).dt.year
    yearly=pol_all.groupby(["period","year"]).agg(
        trades=("expiry","count"),canonical_net=("canonical_net","sum"),policy_net=("policy_net","sum"),
        uplift=("policy_net","sum")
    ).reset_index()
    yearly["uplift"]=yearly["policy_net"]-yearly["canonical_net"]

    # Feature diagnostics on training; no diagnostic is used to expand the model.
    diag=[]
    for g,cols in GROUPS.items():
        for col in cols:
            if col not in train: continue
            for period,frame in [("training",train),("validation",val),("holdout",hold)]:
                y=frame.canonical_loss.to_numpy()
                z=pd.to_numeric(frame[col],errors="coerce")
                mask=z.notna() & np.isfinite(z)
                if mask.sum()>=5 and len(np.unique(y[mask]))==2:
                    auc=safe_auc(y[mask],z[mask])
                else: auc=np.nan
                rho=spearmanr(z[mask],frame.canonical_net.to_numpy()[mask]).statistic if mask.sum()>=5 else np.nan
                diag.append({"group":g,"feature":col,"period":period,"n":int(mask.sum()),"loss_auc":auc,"spearman_net":rho})
    diag=pd.DataFrame(diag)

    # Model calibration / AUC.
    model_stats=[]
    for name,frame,p,model in [
        ("loss_validation",val,p_loss_va,loss_model),
        ("loss_holdout",hold,p_loss_ho,loss_model),
    ]:
        y=frame.canonical_loss.to_numpy()
        model_stats.append({"model":name,"n":len(y),"auc":safe_auc(y,p) if len(np.unique(y))==2 else np.nan,
                            "brier":float(brier_score_loss(y,p)) if len(y) else np.nan})
    for name,frame,p in [("reverse_validation",rev_val,None),("reverse_holdout",rev_hold,None)]:
        if len(frame):
            pp=np.array([rev_map_val.get(e,np.nan) for e in frame.expiry]) if "validation" in name else np.array([rev_map_hold.get(e,np.nan) for e in frame.expiry])
            yy=frame.reverse_better.to_numpy()
            model_stats.append({"model":name,"n":len(yy),"auc":safe_auc(yy,pp) if len(np.unique(yy))==2 else np.nan,
                                "brier":float(brier_score_loss(yy,pp)) if len(yy) else np.nan})

    # Permutation sensitivity of validation classification probability to the 8 compact group scores.
    perm_rows=[]
    for group in GROUPS:
        Xperm=Xva.copy()
        base=loss_model.predict_proba(Xva)[:,1].mean() if len(Xva) else np.nan
        drops=[]
        for b in range(100):
            if len(Xperm)==0: break
            arr=Xperm[group].to_numpy().copy(); RNG.shuffle(arr); Xperm[group]=arr
            drops.append(abs(float(loss_model.predict_proba(Xperm)[:,1].mean())-base))
        perm_rows.append({"feature_group":group,"mean_probability_shift":float(np.mean(drops)) if drops else np.nan})

    # Out-of-sample comparison for each action family using thresholds selected on training only.
    mode_period_rows=[]
    for mode,row in choices.items():
        mode_skip_threshold=float(row.skip_threshold) if pd.notna(row.skip_threshold) else None
        mode_reverse_threshold=float(row.reverse_threshold) if pd.notna(row.reverse_threshold) else None
        for period,frame,pl,pr in [("training",train,p_loss_tr,p_rev_tr),("validation",val,p_loss_va,p_rev_va),("holdout",hold,p_loss_ho,p_rev_ho)]:
            if mode=="skip_only":
                pol=frame.copy()
                pol["action"]=np.where(pl>=mode_skip_threshold,"SKIP","CANONICAL")
            elif mode=="reverse_only":
                pol=frame.copy()
                pol["action"]=np.where((pr>=mode_reverse_threshold)&frame.reverse_available.to_numpy(),"REVERSE","CANONICAL")
            else:
                pol=evaluate_policy(frame,pl,pr,mode_skip_threshold,mode_reverse_threshold)
            mm,_=policy_metrics(pol)
            mm.update({"mode":mode,"period":period,"skip_threshold":mode_skip_threshold,"reverse_threshold":mode_reverse_threshold})
            mode_period_rows.append(mm)
    pd.DataFrame(mode_period_rows).to_csv(OUT/"phase23_mode_walkforward_summary.csv",index=False)

    # Reproducibility: persist fitted transforms and model coefficients.
    def model_params(model):
        return {"coef":model.coef_.tolist(),"intercept":model.intercept_.tolist(),"classes":model.classes_.tolist()}
    (OUT/"phase23_model_parameters.json").write_text(json.dumps({
        "group_component_stats":gt.component_stats,
        "group_medians":gt.group_medians,
        "group_scales":gt.group_scales,
        "loss_model":model_params(loss_model),
        "reverse_model":model_params(rev_model),
        "selected_thresholds":{"skip":ts,"reverse":trv}
    },indent=2,default=str))

    # Full output ledger.
    pol_all["p_loss"]=np.nan
    pol_all["p_reverse"]=np.nan
    # recompute score columns through expiry maps
    p_loss_map=dict(zip(train.expiry,p_loss_tr)) | dict(zip(val.expiry,p_loss_va)) | dict(zip(hold.expiry,p_loss_ho))
    p_rev_map=rev_map_train | rev_map_val | rev_map_hold
    pol_all["p_loss"]=pol_all.expiry.map(p_loss_map)
    pol_all["p_reverse"]=pol_all.expiry.map(p_rev_map).fillna(0.0)

    promotion = {
        "chosen_skip_threshold":ts,
        "chosen_reverse_threshold":trv,
        "training_uplift_positive":bool(metrics_train["uplift"]>0),
        "training_winner_retention_ge_95pct":bool(metrics_train["winner_retention"]>=0.95),
        "validation_uplift_positive":bool(metrics_validation["uplift"]>0),
        "holdout_uplift_positive":bool(metrics_holdout["uplift"]>0),
        "validation_winner_retention_ge_90pct":bool(metrics_validation["winner_retention"]>=0.90),
        "holdout_winner_retention_ge_90pct":bool(metrics_holdout["winner_retention"]>=0.90),
        "validation_dd_ok":bool(metrics_validation["max_dd"]<=1.05*max_dd(val.canonical_net)),
        "holdout_dd_ok":bool(metrics_holdout["max_dd"]<=1.05*max_dd(hold.canonical_net)),
        "promotion_pass":bool(
            metrics_train["uplift"]>0 and metrics_train["winner_retention"]>=0.95 and
            metrics_validation["uplift"]>0 and metrics_holdout["uplift"]>0 and
            metrics_validation["winner_retention"]>=0.90 and metrics_holdout["winner_retention"]>=0.90 and
            metrics_validation["max_dd"]<=1.05*max_dd(val.canonical_net) and
            metrics_holdout["max_dd"]<=1.05*max_dd(hold.canonical_net)
        )
    }

    mode_rows=[]
    for mode,row in choices.items():
        mode_rows.append({"mode":mode,**{k:(None if pd.isna(row.get(k,np.nan)) else row[k]) for k in row.index if k!="mode"}})
    pd.DataFrame(mode_rows).to_csv(OUT/"phase23_mode_comparison.csv",index=False)
    grid.to_csv(OUT/"phase23_action_threshold_grid.csv",index=False)
    diag.to_csv(OUT/"phase23_univariate_diagnostics.csv",index=False)
    pd.DataFrame(model_stats).to_csv(OUT/"phase23_model_diagnostics.csv",index=False)
    pd.DataFrame(perm_rows).to_csv(OUT/"phase23_permutation_sensitivity.csv",index=False)
    yearly.to_csv(OUT/"phase23_yearly_policy_breakdown.csv",index=False)
    pol_all.sort_values("entry_date").to_csv(OUT/"phase23_selected_policy_trade_level.csv",index=False)
    pd.DataFrame([metrics_train,metrics_validation,metrics_holdout],index=["training","validation","holdout"]).to_csv(OUT/"phase23_selected_policy_summary.csv")
    (OUT/"phase23_promotion_gate.json").write_text(json.dumps(promotion,indent=2,default=str))
    (OUT/"phase23_model_spec.json").write_text(json.dumps({
        "groups":GROUPS,
        "skip_thresholds":SKIP_THRESHOLDS,
        "reverse_thresholds":REVERSE_THRESHOLDS,
        "log_components":sorted(LOG_COMPONENTS),
        "logistic_C":0.5,
        "class_weight":"balanced",
        "bootstrap_B":BOOTSTRAP_B
    },indent=2,default=str))

    print(json.dumps({
        "training":mtr,
        "validation":mva,
        "holdout":mho,
        "promotion":promotion
    },indent=2,default=str))


if __name__=="__main__":
    main()

# Phase 23 rerun marker: consume latest persisted audit feature table.
