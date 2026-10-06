import json, math
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr

ROOT=Path(".")
FEATURE=ROOT/"results/phase39_features/point_in_time_features.csv"
LEDGER=ROOT/"results/phase39_counterfactual/fixed_opportunity_ledger.csv"
OUT=ROOT/"results/phase39_symbolic"
OUT.mkdir(parents=True,exist_ok=True)

MARGINS=[0.0,250.0,500.0]
TOPK=8
COMPLEXITY_PENALTY=250.0
LABELS={"control_direction","control_net_rupees","delta_pnl_call_minus_put","call_net_rupees","put_net_rupees","expiry","entry_ts","split"}

def load():
    x=pd.read_csv(FEATURE)
    y=pd.read_csv(LEDGER,usecols=["entry_ts","expiry","split","call_net_rupees","put_net_rupees"])
    z=x.merge(y,on=["entry_ts","expiry","split"],how="inner",validate="one_to_one").sort_values("entry_ts").reset_index(drop=True)
    assert len(z)==477
    return z

def feature_candidates(train):
    scores=[]
    y=train.delta_pnl_call_minus_put.to_numpy(float)
    for c in train.columns:
        if c in LABELS or not pd.api.types.is_numeric_dtype(train[c]): continue
        if train[c].isna().mean()>0.50 or train[c].nunique(dropna=True)<5: continue
        x=train[c].to_numpy(float)
        m=np.isfinite(x)&np.isfinite(y)
        if m.sum()<30: continue
        sc=abs(float(spearmanr(x[m],y[m]).statistic))
        if np.isfinite(sc): scores.append((sc,c))
    return [c for _,c in sorted(scores,reverse=True)[:TOPK]]

def transform(series,op):
    x=series.to_numpy(float)
    if op=="x": return x
    if op=="abs": return np.abs(x)
    if op=="sqrt_signed": return np.sign(x)*np.sqrt(np.abs(x))
    if op=="log_signed": return np.sign(x)*np.log1p(np.abs(x))
    return x

def build_exprs(cols):
    out=[]
    ops=["x","abs","sqrt_signed","log_signed"]
    for c in cols:
        for op in ops:
            out.append((f"{op}({c})",[(c,op)]))
    # A small, explicit binary grammar.
    for i,c1 in enumerate(cols):
        for c2 in cols[i+1:]:
            out.append((f"{c1}-{c2}",[(c1,"x",c2,"x","sub")]))
            out.append((f"{c1}+{c2}",[(c1,"x",c2,"x","add")]))
    return out

def fit_expr(train,expr):
    if len(expr)==1:
        c,op=expr[0]
        a=transform(train[c],op).astype(float)
    else:
        c1,o1,c2,o2,bop=expr[0]
        x1=transform(train[c1],o1); x2=transform(train[c2],o2)
        a=x1-x2 if bop=="sub" else x1+x2
    imp=np.nanmedian(a)
    a=np.where(np.isfinite(a),a,imp)
    sc=StandardScaler().fit(a.reshape(-1,1))
    z=sc.transform(a.reshape(-1,1)).ravel()
    y=train.delta_pnl_call_minus_put.to_numpy(float)
    b0=float(np.nanmedian(y))
    v=np.isfinite(z)&np.isfinite(y)
    if v.sum()<30: return None
    X=np.column_stack([np.ones(v.sum()),z[v]])
    coef=np.linalg.lstsq(X,y[v],rcond=None)[0]
    resid=y[v]-(coef[0]+coef[1]*z[v])
    unc=max(float(np.std(resid,ddof=1)),1.0)
    return {"imp":imp,"sc_mean":float(sc.mean_[0]),"sc_scale":float(sc.scale_[0]),"coef0":float(coef[0]),"coef1":float(coef[1]),"unc":unc}

def predict(df,expr,fit):
    if len(expr)==1:
        c,op=expr[0]; a=transform(df[c],op).astype(float)
    else:
        c1,o1,c2,o2,bop=expr[0]; x1=transform(df[c1],o1); x2=transform(df[c2],o2)
        a=x1-x2 if bop=="sub" else x1+x2
    a=np.where(np.isfinite(a),a,fit["imp"])
    z=(a-fit["sc_mean"])/max(fit["sc_scale"],1e-9)
    return fit["coef0"]+fit["coef1"]*z

def policy_uplift(df,pred,unc,margin):
    ctl=df.control_direction.to_numpy()
    imp=np.where(ctl=="CALL",-pred,pred)
    ov=(imp-unc)>margin
    act=ctl.copy()
    act[ov]=np.where(act[ov]=="CALL","PUT","CALL")
    pnl=np.asarray(np.where(act=="CALL",df.call_net_rupees,df.put_net_rupees))
    return float((pnl-df.control_net_rupees.to_numpy()).sum()),ov,act

def main():
    z=load()
    dev=z[z.split=="development"].reset_index(drop=True)
    val=z[z.split=="validation"].reset_index(drop=True)
    cut=int(len(dev)*0.80)
    tr=dev.iloc[:cut].reset_index(drop=True)
    iv=dev.iloc[cut:].reset_index(drop=True)
    cols=feature_candidates(tr)
    exprs=build_exprs(cols)

    rows=[]
    for expr_str,expr in exprs:
        fit=fit_expr(tr,expr)
        if fit is None: continue
        pred=predict(iv,expr,fit)
        for margin in MARGINS:
            uplift,ov,_=policy_uplift(iv,pred,fit["unc"],margin)
            complexity=1 if len(expr)==1 else 2
            score=uplift-COMPLEXITY_PENALTY*complexity
            rows.append({"expr":expr_str,"margin":margin,"inner_validation_uplift":uplift,
                         "inner_override_share":float(ov.mean()),"complexity":complexity,
                         "selection_score":score})
    grid=pd.DataFrame(rows).sort_values(["selection_score","inner_validation_uplift"],ascending=False).reset_index(drop=True)
    best=grid.iloc[0]
    expr_str=str(best.expr)
    # reconstruct selected expression
    expr=None
    for s,e in exprs:
        if s==expr_str: expr=e; break
    fit_full=fit_expr(dev,expr)
    pred_val=predict(val,expr,fit_full)
    uplift,ov,act=policy_uplift(val,pred_val,fit_full["unc"],float(best.margin))
    summary={
      "status":"COMPLETE",
      "selected_expression":expr_str,
      "selected_margin":float(best.margin),
      "inner_train_rows":len(tr),
      "inner_validation_rows":len(iv),
      "validation_rows":len(val),
      "validation_uplift_rupees":uplift,
      "validation_override_share":float(ov.mean()),
      "validation_net_rupees":float(np.asarray(np.where(act=="CALL",val.call_net_rupees,val.put_net_rupees)).sum()),
      "validation_control_rupees":float(val.control_net_rupees.sum()),
      "holdout_evaluated":False,
      "expression_complexity":int(best.complexity)
    }
    grid.to_csv(OUT/"symbolic_grammar_grid.csv",index=False)
    pd.DataFrame({"entry_ts":val.entry_ts,"expression_score":pred_val,"override":ov,"action":act,
                  "control":val.control_direction,"control_net":val.control_net_rupees,
                  "chosen_net":np.asarray(np.where(act=="CALL",val.call_net_rupees,val.put_net_rupees))}).to_csv(OUT/"validation_predictions.csv",index=False)
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2))
    (OUT/"status.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
    print(grid.head(15).to_string(index=False))

if __name__=="__main__":
    main()
