import os, json, math, subprocess, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

TZ = "Asia/Kolkata"
DATA = Path("data/phase33")
OUT = Path("results/phase33_nifty_prediction")
DATA.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

START = pd.Timestamp(os.getenv("SAMPLE_START", "2021-05-27"), tz=TZ)
END = pd.Timestamp(os.getenv("SAMPLE_END", "2026-09-30"), tz=TZ)
TRAIN_END = pd.Timestamp("2023-12-31 23:59:59", tz=TZ)
VAL_END = pd.Timestamp("2025-12-31 23:59:59", tz=TZ)
HOLD_START = pd.Timestamp("2026-01-01", tz=TZ)
HOLD_END = pd.Timestamp("2026-09-30 23:59:59", tz=TZ)

NIFTY_REPO = "thetrademarkk/india-index-options-1m"
SENTIMENT_REPO = "dixitdharmansh07/indic-finance"
SEED = 1337

def ensure(pkg, import_name=None):
    try:
        __import__(import_name or pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])


def normalize_ist_series(x):
    y = pd.to_datetime(x, errors="coerce")
    if getattr(y.dt, "tz", None) is None:
        y = y.dt.tz_localize(TZ)
    else:
        y = y.dt.tz_convert(TZ)
    return y.astype(f"datetime64[ns, {TZ}]")

def as_ist(x):
    x = pd.to_datetime(x)
    if getattr(x.dt, "tz", None) is None:
        return x.dt.tz_localize(TZ)
    return x.dt.tz_convert(TZ)

def load_nifty_batches():
    from huggingface_hub import hf_hub_download
    import pyarrow.parquet as pq
    fn = hf_hub_download(
        repo_id=NIFTY_REPO,
        filename="index/NIFTY.parquet",
        repo_type="dataset",
        token=os.getenv("HF_TOKEN") or None,
    )
    pf = pq.ParquetFile(fn)
    day_parts, ref_parts = [], []
    for batch in pf.iter_batches(
        columns=["timestamp", "open", "high", "low", "close", "volume"],
        batch_size=600000,
    ):
        d = batch.to_pandas()
        ts = pd.to_datetime(d["timestamp"])
        if ts.dt.tz is None:
            ts = ts.dt.tz_localize(TZ)
        else:
            ts = ts.dt.tz_convert(TZ)
        d["timestamp"] = ts
        d["date"] = ts.dt.normalize().astype(f"datetime64[ns, {TZ}]")
        day_parts.append(
            d.groupby("date", as_index=False).agg(
                open=("open", "first"),
                high=("high", "max"),
                low=("low", "min"),
                close=("close", "last"),
                volume=("volume", "sum"),
            )
        )
        ref = d[(ts.dt.hour == 10) & (ts.dt.minute == 0)][["timestamp", "close"]].copy()
        if not ref.empty:
            ref = ref.rename(columns={"timestamp": "ref_ts", "close": "ref_spot"})
            ref["date"] = ref["ref_ts"].dt.normalize()
            ref_parts.append(ref)
    daily = (
        pd.concat(day_parts, ignore_index=True)
        .groupby("date", as_index=False)
        .agg(
            open=("open", "first"),
            high=("high", "max"),
            low=("low", "min"),
            close=("close", "last"),
            volume=("volume", "sum"),
        )
        .sort_values("date")
    )
    refs = (
        pd.concat(ref_parts, ignore_index=True)
        .drop_duplicates("ref_ts")
        .sort_values("ref_ts")
    )
    daily["date"] = normalize_ist_series(daily["date"]).dt.normalize()
    refs["ref_ts"] = normalize_ist_series(refs["ref_ts"])
    refs["date"] = normalize_ist_series(refs["date"]).dt.normalize()
    daily.to_parquet(DATA / "nifty_daily.parquet", index=False)
    refs.to_parquet(DATA / "nifty_10am.parquet", index=False)
    return daily, refs

def load_or_build_nifty():
    dpath, rpath = DATA / "nifty_daily.parquet", DATA / "nifty_10am.parquet"
    if dpath.exists() and rpath.exists():
        d = pd.read_parquet(dpath); r = pd.read_parquet(rpath)
        d["date"] = normalize_ist_series(d["date"]).dt.normalize()
        r["ref_ts"] = normalize_ist_series(r["ref_ts"])
        r["date"] = normalize_ist_series(r["date"]).dt.normalize() if "date" in r else r["ref_ts"].dt.normalize()
        return d, r
    return load_nifty_batches()

def expected_expiries(daily):
    trading = sorted(set(pd.to_datetime(daily["date"])))
    if not trading:
        return []
    first, last = min(trading), max(trading)
    out = []
    mondays = pd.date_range(
        first - pd.Timedelta(days=14),
        last + pd.Timedelta(days=14),
        freq="W-MON",
        tz=TZ,
    )
    for m in mondays:
        if m >= pd.Timestamp("2025-09-01", tz=TZ):
            scheduled = m + pd.Timedelta(days=1)
        elif m >= pd.Timestamp("2025-04-04", tz=TZ):
            scheduled = m
        else:
            scheduled = m + pd.Timedelta(days=3)
        candidates = [d for d in trading if m.normalize() <= d <= scheduled.normalize()]
        if not candidates:
            continue
        e = max(candidates).normalize()
        if START.normalize() <= e <= END.normalize():
            out.append(e)
    return sorted(set(out))

def load_or_build_sentiment():
    path = DATA / "sentiment_daily.parquet"
    if path.exists():
        out = pd.read_parquet(path)
        out["date"] = normalize_ist_series(out["date"]).dt.normalize()
        return out
    ensure("datasets")
    from datasets import load_dataset
    ds = load_dataset(SENTIMENT_REPO, split="train").to_pandas()
    if "date" not in ds.columns:
        return pd.DataFrame(columns=["date", "sent_mean", "sent_std", "sent_count", "sent_pos", "sent_neg"])
    ds["date"] = pd.to_datetime(ds["date"], errors="coerce")
    ds = ds.dropna(subset=["date"])
    ds["date"] = ds["date"].dt.tz_localize(TZ) if ds["date"].dt.tz is None else ds["date"].dt.tz_convert(TZ)
    # forward-return columns are intentionally ignored.
    p = pd.to_numeric(ds["sentiment_positive"], errors="coerce")
    n = pd.to_numeric(ds["sentiment_negative"], errors="coerce")
    ds["sent_score"] = p - n
    out = (
        ds.groupby(ds["date"].dt.normalize(), as_index=False)
        .agg(
            sent_mean=("sent_score", "mean"),
            sent_std=("sent_score", "std"),
            sent_count=("sent_score", "size"),
            sent_pos=("sent_score", lambda x: float((x > 0).mean())),
            sent_neg=("sent_score", lambda x: float((x < 0).mean())),
        )
        .rename(columns={"date": "date"})
    )
    out["date"] = normalize_ist_series(out["date"]).dt.normalize()
    out.to_parquet(path, index=False)
    return out



def load_or_build_fii_dii():
    path = DATA / "fii_dii_daily.parquet"
    if path.exists():
        out = pd.read_parquet(path)
        out["date"] = normalize_ist_series(out["date"]).dt.normalize()
        return out
    import urllib.request
    url = "https://raw.githubusercontent.com/MrChartist/fii-dii-data/main/data/history.json"
    raw_path = DATA / "fii_dii_history.json"
    urllib.request.urlretrieve(url, raw_path)
    with open(raw_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    rows = []
    for r in raw:
        d = pd.to_datetime(r.get("date"), dayfirst=True, errors="coerce")
        if pd.isna(d):
            continue
        rows.append({
            "date": d.tz_localize(TZ) if d.tzinfo is None else d.tz_convert(TZ),
            "fii_net": pd.to_numeric(r.get("fii_net"), errors="coerce"),
            "dii_net": pd.to_numeric(r.get("dii_net"), errors="coerce"),
            "fii_idx_fut_net": pd.to_numeric(r.get("fii_idx_fut_net"), errors="coerce"),
            "fii_idx_call_net": pd.to_numeric(r.get("fii_idx_call_net"), errors="coerce"),
            "fii_idx_put_net": pd.to_numeric(r.get("fii_idx_put_net"), errors="coerce"),
            "flow_pcr": pd.to_numeric(r.get("pcr"), errors="coerce"),
            "flow_sentiment": pd.to_numeric(r.get("sentiment_score"), errors="coerce"),
        })
    out = pd.DataFrame(rows).drop_duplicates("date").sort_values("date")
    if not out.empty:
        out["date"] = normalize_ist_series(out["date"]).dt.normalize()
    if not out.empty:
        for c in ["fii_net","dii_net","fii_idx_fut_net","fii_idx_call_net","fii_idx_put_net"]:
            out[c + "_z20"] = (out[c] - out[c].rolling(20).mean()) / out[c].rolling(20).std()
    out.to_parquet(path, index=False)
    return out


def load_or_build_global():
    path = DATA / "global_daily.parquet"
    if path.exists():
        out = pd.read_parquet(path)
        out["date"] = normalize_ist_series(out["date"]).dt.normalize()
        return out
    ensure("yfinance", "yfinance")
    import yfinance as yf
    tickers = {
        "SP500": "^GSPC", "NASDAQ": "^IXIC", "DOW": "^DJI", "VIX": "^VIX",
        "NIKKEI": "^N225", "SENSEX": "^BSESN", "USDINR": "INR=X",
        "GOLD": "GC=F", "CRUDE": "CL=F",
    }
    pieces = []
    for name, ticker in tickers.items():
        try:
            z = yf.download(
                ticker, start="2018-01-01", end="2026-10-01",
                auto_adjust=False, progress=False, threads=False,
            )
            if z is None or z.empty:
                continue
            close = z["Close"]
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]
            dd = pd.DataFrame({"date": pd.to_datetime(close.index), name: pd.to_numeric(close, errors="coerce")}).dropna()
            dd["date"] = normalize_ist_series(dd["date"])
            pieces.append(dd)
        except Exception as exc:
            print("GLOBAL_SOURCE_ERROR", name, repr(exc), flush=True)
    if not pieces:
        g = pd.DataFrame({"date": pd.Series(dtype=f"datetime64[ns,{TZ}]")})
    else:
        g = pieces[0]
        for p in pieces[1:]:
            g = g.merge(p, on="date", how="outer")
        g = g.sort_values("date")
        for c in [c for c in g.columns if c != "date"]:
            g[c + "_ret1"] = np.log(g[c] / g[c].shift(1))
    g.to_parquet(path, index=False)
    return g

def build_price_features(daily):
    d = daily.copy().sort_values("date").set_index("date")
    r = np.log(d["close"] / d["close"].shift(1))
    for n in [1, 3, 5, 10, 20, 30]:
        d[f"ret{n}"] = np.log(d["close"] / d["close"].shift(n))
    for n in [5, 10, 20, 30]:
        d[f"vol{n}"] = r.rolling(n).std()
        d[f"range{n}"] = np.log(d["high"] / d["low"]).rolling(n).mean()
        d[f"dd{n}"] = d["close"] / d["close"].rolling(n).max() - 1
    up = d["close"].diff().clip(lower=0).rolling(14).mean()
    dn = (-d["close"].diff().clip(upper=0)).rolling(14).mean()
    rs = up / dn.replace(0, np.nan)
    d["rsi14"] = 100 - 100 / (1 + rs)
    ema12 = d["close"].ewm(span=12, adjust=False).mean()
    ema26 = d["close"].ewm(span=26, adjust=False).mean()
    d["macd"] = ema12 - ema26
    d["ma_gap20"] = d["close"] / d["close"].rolling(20).mean() - 1
    d["ret_over_vol20"] = d["ret5"] / d["vol20"].replace(0, np.nan)
    return d.reset_index()

def add_option_event_features(events):
    from huggingface_hub import hf_hub_download
    out = []
    for _, row in events.iterrows():
        expiry = pd.Timestamp(row["expiry"])
        ts = pd.Timestamp(row["ref_ts"])
        try:
            fn = hf_hub_download(
                repo_id=NIFTY_REPO,
                filename=f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet",
                repo_type="dataset",
                token=os.getenv("HF_TOKEN") or None,
            )
            q = pd.read_parquet(fn)
            q["timestamp"] = normalize_ist_series(q["timestamp"])
            if q["timestamp"].dt.tz is None:
                q["timestamp"] = q["timestamp"].dt.tz_localize(TZ)
            else:
                q["timestamp"] = q["timestamp"].dt.tz_convert(TZ)
            q = q[q["timestamp"] == ts].copy()
            if q.empty:
                out.append({"expiry": expiry, "ref_ts": ts})
                continue
            q["strike"] = pd.to_numeric(q["strike"], errors="coerce")
            q["close"] = pd.to_numeric(q["close"], errors="coerce")
            for c in ["volume", "open_interest"]:
                if c not in q.columns:
                    q[c] = np.nan
                q[c] = pd.to_numeric(q[c], errors="coerce")
            atm = float(q.iloc[(q["strike"] - float(row["ref_spot"])).abs().argsort()[:1]]["strike"].iloc[0])
            z = q[(q["strike"] >= atm - 300) & (q["strike"] <= atm + 300)]
            ce = z[z["option_type"].astype(str).str.upper() == "CE"]
            pe = z[z["option_type"].astype(str).str.upper() == "PE"]
            if ce.empty or pe.empty:
                out.append({"expiry": expiry, "ref_ts": ts})
                continue
            ce_atm = ce.iloc[(ce["strike"] - atm).abs().argsort()[:1]].iloc[0]
            pe_atm = pe.iloc[(pe["strike"] - atm).abs().argsort()[:1]].iloc[0]
            out.append({
                "expiry": expiry,
                "ref_ts": ts,
                "opt_call_oi": float(ce_atm["open_interest"]),
                "opt_put_oi": float(pe_atm["open_interest"]),
                "opt_call_vol": float(ce_atm["volume"]),
                "opt_put_vol": float(pe_atm["volume"]),
                "opt_pcr_oi": float(pe_atm["open_interest"] / max(ce_atm["open_interest"], 1.0)),
                "opt_pcr_vol": float(pe_atm["volume"] / max(ce_atm["volume"], 1.0)),
                "opt_atm_straddle": float(ce_atm["close"] + pe_atm["close"]),
                "opt_atm_straddle_pct_spot": float((ce_atm["close"] + pe_atm["close"]) / max(float(row["ref_spot"]), 1.0)),
            })
        except Exception as exc:
            print("OPTION_FEATURE_ERROR", expiry.date(), repr(exc), flush=True)
            out.append({"expiry": expiry, "ref_ts": ts})
    return pd.DataFrame(out)

def build_events():
    ep = DATA / "events.parquet"
    if ep.exists():
        ev = pd.read_parquet(ep)
        ev["expiry"] = normalize_ist_series(ev["expiry"]).dt.normalize()
        ev["ref_ts"] = normalize_ist_series(ev["ref_ts"])
        return ev
    daily, refs = load_or_build_nifty()
    price = build_price_features(daily)
    exps = expected_expiries(daily)
    event_rows = []
    for e in exps:
        ref_date = (e - pd.Timedelta(days=6)).normalize()
        ref_ts = ref_date + pd.Timedelta(hours=10)
        q = refs[refs["ref_ts"] == ref_ts]
        close = daily[daily["date"] == e]
        if q.empty or close.empty:
            continue
        event_rows.append({
            "expiry": e,
            "ref_ts": ref_ts,
            "ref_spot": float(q["ref_spot"].iloc[0]),
            "expiry_close": float(close["close"].iloc[-1]),
        })
    events = pd.DataFrame(event_rows).sort_values("ref_ts")
    if events.empty:
        raise RuntimeError("No D-6 10:00 events available")
    price_cols = [c for c in price.columns if c not in ["date","close","open","high","low","volume"]]
    events = events.merge(price[["date"] + price_cols], left_on="ref_ts", right_on="date", how="left").drop(columns=["date"])
    # Current-session 10:00 return uses the prior trading day's close only.
    prior = daily[["date", "close"]].copy()
    prior["date"] = prior["date"] + pd.Timedelta(days=1)
    prior = prior.rename(columns={"close": "prev_close"})
    events = events.merge(prior, left_on=events["ref_ts"].dt.normalize(), right_on="date", how="left").drop(columns=["key_0", "date"], errors="ignore")
    events["intraday_ret_10"] = np.log(events["ref_spot"] / events["prev_close"])
    sent = load_or_build_sentiment().sort_values("date")
    # Conservative: use only sentiment dates strictly before the reference date.
    sent["join_date"] = normalize_ist_series(sent["date"]).dt.normalize().astype(f"datetime64[ns, {TZ}]")
    events["join_date"] = (normalize_ist_series(events["ref_ts"]).dt.normalize() - pd.Timedelta(seconds=1)).astype(f"datetime64[ns, {TZ}]")
    events = pd.merge_asof(
        events.sort_values("join_date"),
        sent.sort_values("join_date"),
        on="join_date",
        direction="backward",
        tolerance=pd.Timedelta(days=7),
    ).drop(columns=["join_date"], errors="ignore")
    g = load_or_build_global().sort_values("date")
    g["date"] = normalize_ist_series(g["date"]).dt.normalize()
    gc = g.copy()
    # Previous global session only; avoids using values that may still be trading at Indian 10:00.
    for c in [x for x in gc.columns if x != "date"]:
        gc[c] = gc[c].shift(1)
    gcols = [c for c in gc.columns if c != "date"]
    events["ref_ts"] = normalize_ist_series(events["ref_ts"])
    gc["date"] = normalize_ist_series(gc["date"]).dt.normalize()
    events = pd.merge_asof(
        events.sort_values("ref_ts"),
        gc[["date"] + gcols].sort_values("date"),
        left_on="ref_ts",
        right_on="date",
        direction="backward",
        tolerance=pd.Timedelta(days=5),
    ).drop(columns=["date"], errors="ignore")

    flows = load_or_build_fii_dii().sort_values("date")
    fc = flows.copy()
    events["flow_join_date"] = (normalize_ist_series(events["ref_ts"]).dt.normalize() - pd.Timedelta(seconds=1)).astype(f"datetime64[ns, {TZ}]")
    events = pd.merge_asof(
        events.sort_values("flow_join_date"),
        fc[["date"] + [c for c in fc.columns if c != "date"]].sort_values("date"),
        left_on="flow_join_date", right_on="date",
        direction="backward", tolerance=pd.Timedelta(days=7),
    ).drop(columns=["flow_join_date","date"], errors="ignore")

    opt = add_option_event_features(events[["expiry", "ref_ts", "ref_spot"]].copy())
    events = events.merge(opt, on=["expiry", "ref_ts"], how="left")
    events["target_return"] = np.log(events["expiry_close"] / events["ref_spot"])
    events["target_direction"] = (events["target_return"] > 0).astype(int)
    events["expiry"] = normalize_ist_series(events["expiry"]).dt.normalize()
    events["ref_ts"] = normalize_ist_series(events["ref_ts"])
    events.to_parquet(ep, index=False)
    return events

def split_of(ts):
    if ts <= TRAIN_END: return "train"
    if ts <= VAL_END: return "validation"
    if HOLD_START <= ts <= HOLD_END: return "holdout"
    return "other"

def numeric_features(events):
    drop = {
        "expiry", "ref_ts", "ref_spot", "expiry_close",
        "target_return", "target_direction", "split",
    }
    cols = [c for c in events.columns if c not in drop and pd.api.types.is_numeric_dtype(events[c])]
    return cols

def metric_block(y, p):
    from sklearn.metrics import accuracy_score, balanced_accuracy_score, roc_auc_score, log_loss, brier_score_loss
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    out = {
        "n": int(len(y)),
        "accuracy": float(accuracy_score(y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, np.c_[1-p, p], labels=[0,1])),
    }
    out["roc_auc"] = float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else np.nan
    out["hit_rate"] = out["accuracy"]
    return out

def fit_rf(train_df, test_df, cols):
    ensure("scikit-learn", "sklearn")
    from sklearn.impute import SimpleImputer
    from sklearn.ensemble import RandomForestClassifier
    imp = SimpleImputer(strategy="median").fit(train_df[cols])
    m = RandomForestClassifier(
        n_estimators=300, max_depth=5, min_samples_leaf=4,
        class_weight="balanced_subsample", random_state=SEED, n_jobs=-1,
    )
    m.fit(imp.transform(train_df[cols]), train_df["target_direction"].astype(int))
    return m.predict_proba(imp.transform(test_df[cols]))[:, 1]

def fit_sofnn(train_df, test_df, cols):
    ensure("scikit-learn", "sklearn")
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.linear_model import LogisticRegression
    imp = SimpleImputer(strategy="median").fit(train_df[cols])
    sc = StandardScaler().fit(imp.transform(train_df[cols]))
    a, b = sc.transform(imp.transform(train_df[cols])), sc.transform(imp.transform(test_df[cols]))
    k = min(12, max(2, len(a)//8))
    km = KMeans(n_clusters=k, n_init=10, random_state=SEED).fit(a)
    da = ((a[:,None,:] - km.cluster_centers_[None,:,:])**2).mean(axis=2)
    db = ((b[:,None,:] - km.cluster_centers_[None,:,:])**2).mean(axis=2)
    scale = max(float(np.median(np.sqrt(da)) if np.isfinite(da).any() else 1.0), 0.5)
    phi_a = np.exp(-da/(2*scale**2))
    phi_b = np.exp(-db/(2*scale**2))
    clf = LogisticRegression(max_iter=2000, C=1.0, random_state=SEED).fit(phi_a, train_df["target_direction"].astype(int))
    return clf.predict_proba(phi_b)[:,1]


def fit_sentiment_sofnn(train_df, test_df, cols):
    return fit_sofnn(train_df, test_df, cols)


def garch_one(train_ret, horizon, model_kind):
    ensure("arch")
    from arch import arch_model
    r = pd.Series(train_ret).dropna().astype(float) * 100
    if len(r) < 100:
        return np.nan, np.nan
    if model_kind == "GARCH":
        am = arch_model(r, mean="AR", lags=1, vol="GARCH", p=1, o=0, q=1, dist="t")
    elif model_kind == "EGARCH":
        am = arch_model(r, mean="AR", lags=1, vol="EGARCH", p=1, o=1, q=1, dist="t")
    else:
        am = arch_model(r, mean="AR", lags=1, vol="GARCH", p=1, o=1, q=1, dist="t")
    fit = am.fit(disp="off")
    fc = fit.forecast(horizon=max(1, int(horizon)), reindex=False)
    mu = float(np.nansum(fc.mean.values[-1])) / 100.0
    var = float(np.nansum(fc.variance.values[-1])) / (100.0**2)
    return mu, math.sqrt(max(var, 0.0))

def run_garch(events, daily):
    daily = daily.sort_values("date").copy()
    daily["ret"] = np.log(daily["close"] / daily["close"].shift(1))
    rows = []
    for _, row in events[events["split"].isin(["validation","holdout"])].iterrows():
        tr = daily[daily["date"] < row["ref_ts"].normalize()]["ret"].dropna()
        horizon = max(1, len(daily[(daily["date"] >= row["ref_ts"].normalize()) & (daily["date"] <= row["expiry"])]))
        vals = []
        for kind in ["GARCH","EGARCH","GJR-GARCH"]:
            try:
                vals.append(garch_one(tr, horizon, kind))
            except Exception as exc:
                print("GARCH_ERROR", row["expiry"], kind, repr(exc), flush=True)
        mu = float(np.nanmean([x[0] for x in vals])) if vals else np.nan
        sig = float(np.nanmean([x[1] for x in vals])) if vals else np.nan
        # Pre-registered conditional Normal mapping, no tuned threshold.
        p_up = 0.5 if not np.isfinite(sig) else float(0.5*(1 + math.erf((mu/max(sig,1e-6))/math.sqrt(2))))
        rows.append({
            "split": row["split"], "expiry": row["expiry"], "ref_ts": row["ref_ts"],
            "garch_mu": mu, "garch_sigma": sig, "garch_prob": p_up,
            "realized_abs_return": abs(float(row["target_return"])),
            "realized_sq_return": float(row["target_return"]**2),
        })
    return pd.DataFrame(rows)

def lstm_fit_predict(train_events, test_events, daily, seq_cols):
    ensure("torch")
    import torch
    from torch import nn
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler
    torch.manual_seed(SEED); np.random.seed(SEED)

    # The registered LSTM input is the 30 most recent completed trading
    # sessions strictly before the D-6 reference date. No reference-day close
    # or any future intraday observation is included.
    daily_feat = build_price_features(daily).sort_values("date").copy()
    imp = SimpleImputer(strategy="median").fit(train_events[seq_cols].copy())
    sc = StandardScaler().fit(imp.transform(train_events[seq_cols].copy()))

    Xs, ys = [], []
    lookback = 30
    for _, row in train_events.sort_values("ref_ts").iterrows():
        ref_day = pd.Timestamp(row["ref_ts"]).normalize()
        prior = daily_feat[daily_feat["date"] < ref_day].tail(lookback)
        if len(prior) < lookback:
            continue
        Xs.append(sc.transform(imp.transform(prior[seq_cols])))
        ys.append(float(row["target_return"]))

    if len(Xs) < 25:
        raise RuntimeError("Insufficient LSTM training sequences")

    xx = torch.tensor(np.stack(Xs), dtype=torch.float32)
    yy = torch.tensor(np.asarray(ys), dtype=torch.float32).view(-1,1)

    class Net(nn.Module):
        def __init__(self, n):
            super().__init__()
            self.lstm = nn.LSTM(n, 16, batch_first=True)
            self.drop = nn.Dropout(0.10)
            self.fc = nn.Linear(16,1)
        def forward(self, x):
            z,_ = self.lstm(x)
            return self.fc(self.drop(z[:,-1,:]))

    net = Net(len(seq_cols))
    opt = torch.optim.Adam(net.parameters(), lr=0.003)
    loss = nn.MSELoss()
    net.train()
    for _ in range(35):
        opt.zero_grad()
        pred = net(xx)
        l = loss(pred, yy)
        l.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0)
        opt.step()

    train_std = max(float(np.std(ys, ddof=1)), 1e-4)
    probs, pred_ret = [], []
    net.eval()
    for _, row in test_events.sort_values("ref_ts").iterrows():
        ref_day = pd.Timestamp(row["ref_ts"]).normalize()
        prior = daily_feat[daily_feat["date"] < ref_day].tail(lookback)
        if len(prior) < lookback:
            raise RuntimeError(f"Insufficient 30-session LSTM history at {row['ref_ts']}")
        z = sc.transform(imp.transform(prior[seq_cols]))
        with torch.no_grad():
            mu = float(net(torch.tensor(z[None,:,:], dtype=torch.float32)).item())
        p = 0.5*(1 + math.erf((mu/train_std)/math.sqrt(2)))
        probs.append(p); pred_ret.append(mu)

    return np.asarray(probs), np.asarray(pred_ret)

def bootstrap_mean(x, n=3000):
    x = np.asarray(x, float)
    rng = np.random.default_rng(SEED)
    if len(x) == 0: return [np.nan, np.nan]
    means = [float(np.mean(rng.choice(x, len(x), replace=True))) for _ in range(n)]
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]

def main():
    daily, refs = load_or_build_nifty()
    events = build_events()
    events = events[(events["ref_ts"] >= START) & (events["ref_ts"] <= HOLD_END)].copy()
    events["split"] = events["ref_ts"].map(split_of)
    train = events[events["split"]=="train"].copy()
    val = events[events["split"]=="validation"].copy()
    hold = events[events["split"]=="holdout"].copy()
    if len(train) < 60 or len(val) < 20 or len(hold) < 10:
        raise RuntimeError(f"Insufficient events train={len(train)} val={len(val)} hold={len(hold)}")
    cols = numeric_features(events)

    pred_parts = []
    for split, test in [("validation",val),("holdout",hold)]:
        fit = train if split == "validation" else pd.concat([train,val]).sort_values("ref_ts")
        rf = fit_rf(fit, test, cols)
        sof = fit_sofnn(fit, test, cols)
        row = test[["expiry","ref_ts","target_return","target_direction"]].copy()
        row["rf_prob"] = rf
        row["sofnn_prob"] = sof
        pred_parts.append(row)

    sent_start = pd.Timestamp("2024-01-01", tz=TZ)
    sent_train_end = pd.Timestamp("2024-12-31 23:59:59", tz=TZ)
    sent_train = events[(events["ref_ts"] >= sent_start) & (events["ref_ts"] <= sent_train_end)].copy()
    sent_val = events[(events["ref_ts"] > sent_train_end) & (events["ref_ts"] <= VAL_END)].copy()
    sent_hold = events[(events["ref_ts"] >= HOLD_START) & (events["ref_ts"] <= HOLD_END)].copy()
    sent_cols_primary = [c for c in cols if c.startswith("sent_")]
    if len(sent_cols_primary) and len(sent_train) >= 20:
        for key, test in [("validation", sent_val), ("holdout", sent_hold)]:
            if test.empty:
                continue
            fit = sent_train if key == "validation" else pd.concat([sent_train, sent_val]).sort_values("ref_ts")
            p = fit_sentiment_sofnn(fit, test, cols)
            for i, part in enumerate(pred_parts):
                if not part.empty and part["ref_ts"].min() == test["ref_ts"].min():
                    pred_parts[i]["sofnn_sent_prob"] = p
    for part in pred_parts:
        if "sofnn_sent_prob" not in part:
            part["sofnn_sent_prob"] = part["sofnn_prob"]

    try:
        seq_cols = [c for c in cols if c.startswith(("ret","vol","range","dd")) or c in ["rsi14","macd","ma_gap20","ret_over_vol20"]]
        pred_parts = [p.reset_index(drop=True) for p in pred_parts]
        for split, test in [("validation",val),("holdout",hold)]:
            fit = train if split == "validation" else pd.concat([train,val]).sort_values("ref_ts")
            p, mu = lstm_fit_predict(fit, test, daily, seq_cols)
            for i, part in enumerate(pred_parts):
                if part["ref_ts"].iloc[0] == test["ref_ts"].iloc[0]:
                    pred_parts[i]["lstm_prob"] = p
                    pred_parts[i]["lstm_pred_return"] = mu
    except Exception as exc:
        print("LSTM_ERROR", repr(exc), flush=True)
        for part in pred_parts:
            part["lstm_prob"] = 0.5
            part["lstm_pred_return"] = np.nan

    pred = pd.concat(pred_parts, ignore_index=True).sort_values("ref_ts")
    pred["ensemble_prob"] = pred[["rf_prob","sofnn_sent_prob","lstm_prob"]].mean(axis=1)
    pred["split"] = pred["ref_ts"].map(split_of)
    pred.to_csv(OUT/"model_predictions.csv", index=False)

    metrics = []
    for split in ["validation","holdout"]:
        q = pred[pred["split"]==split]
        for model in ["rf","sofnn","sofnn_sent","lstm","ensemble"]:
            m = metric_block(q["target_direction"].astype(int), q[f"{model}_prob"])
            m.update({"split":split,"model":model})
            metrics.append(m)
    # Price-only control over the sentiment window to quantify incremental SOFNN value.
    sent_cols = [c for c in cols if c.startswith("sent_")]
    if sent_cols:
        base_cols = [c for c in cols if c not in sent_cols]
        m2 = []
        for split, test in [("validation",val),("holdout",hold)]:
            fit = train if split == "validation" else pd.concat([train,val]).sort_values("ref_ts")
            p = fit_rf(fit, test, base_cols)
            mm = metric_block(test["target_direction"].astype(int), p)
            mm.update({"split":split,"model":"RF_price_only_control"})
            m2.append(mm)
        metrics.extend(m2)
    pd.DataFrame(metrics).to_csv(OUT/"model_metrics.csv", index=False)

    # Baselines and simple economic direction diagnostic.
    base_rows = []
    for split, test in [("validation",val),("holdout",hold)]:
        majority = float(train["target_direction"].mean() if split=="validation" else pd.concat([train,val])["target_direction"].mean())
        for name, p in [
            ("constant", np.full(len(test), majority)),
            ("always_up", np.ones(len(test))),
            ("always_down", np.zeros(len(test))),
        ]:
            base_rows.append({"split":split,"model":name,**metric_block(test["target_direction"],p)})
    pd.DataFrame(base_rows).to_csv(OUT/"baseline_metrics.csv", index=False)

    econ = []
    for split in ["validation","holdout"]:
        q = pred[pred["split"]==split].copy()
        for model in ["rf","sofnn","sofnn_sent","lstm","ensemble"]:
            prob_col = "sofnn_sent_prob" if model == "sofnn_sent" else f"{model}_prob"
            sign = np.where(q[prob_col] >= 0.5, 1.0, -1.0)
            sr = sign * q["target_return"].to_numpy(float)
            lo, hi = bootstrap_mean(sr)
            econ.append({
                "split":split,"model":model,"hit_rate":float((sr>0).mean()),
                "mean_signed_log_return":float(np.mean(sr)),
                "sum_signed_log_return":float(np.sum(sr)),
                "bootstrap_ci_low":lo,"bootstrap_ci_high":hi,
            })
    pd.DataFrame(econ).to_csv(OUT/"directional_economic_diagnostic.csv", index=False)

    g = run_garch(events, daily)
    g.to_csv(OUT/"garch_predictions.csv", index=False)
    if not g.empty:
        gstat = {
            "garch_sigma_mae": float(np.mean(np.abs(g["garch_sigma"] - g["realized_abs_return"]))),
            "garch_sigma_rmse": float(np.sqrt(np.mean((g["garch_sigma"] - g["realized_abs_return"])**2))),
            "garch_direction_accuracy": float(((g["garch_prob"] >= 0.5).astype(int) == events[events["split"].isin(["validation","holdout"])]["target_direction"].to_numpy()).mean())
        }
    else:
        gstat = {}

    coverage = {
        "reference_rule":"expiry minus 6 calendar days at exactly 10:00 IST",
        "target_rule":"expiry-day latest complete NIFTY close at or before 15:29 IST",
        "events_total":int(len(events)),
        "train_events":int(len(train)),
        "validation_events":int(len(val)),
        "holdout_events":int(len(hold)),
        "feature_count":int(len(cols)),
        "sentiment_feature_count":int(len(sent_cols)),
        "events_with_sentiment":int(events[sent_cols_primary].notna().any(axis=1).sum()) if sent_cols_primary else 0,
        "events_with_fii_dii":int(events[[c for c in cols if c.startswith("fii_") or c.startswith("dii_") or c.startswith("flow_")]].notna().any(axis=1).sum()) if any(c.startswith("fii_") or c.startswith("dii_") or c.startswith("flow_") for c in cols) else 0,
        "models":["LSTM","GARCH","EGARCH","GJR-GARCH","SOFNN-inspired","Random Forest","equal-weight ensemble"],
        "garch_stats":gstat,
        "data_note":"D-6 reference events with missing exact 10:00 observations are excluded, not shifted."
    }
    with open(OUT/"coverage_and_metadata.json","w") as f:
        json.dump(coverage, f, indent=2, default=str)

    # High-level result summary.
    summary = {
        "phase":"33",
        "status":"NUMERICAL RUN COMPLETE",
        "reference":"D-6 calendar days, 10:00 IST",
        "validation_best_model": min(
            [x for x in metrics if x["split"]=="validation" and x["model"] in ["rf","sofnn","sofnn_sent","lstm","ensemble"]],
            key=lambda x:x["log_loss"]
        )["model"],
        "holdout_best_model": min(
            [x for x in metrics if x["split"]=="holdout" and x["model"] in ["rf","sofnn","sofnn_sent","lstm","ensemble"]],
            key=lambda x:x["log_loss"]
        )["model"],
    }
    with open(OUT/"PHASE33_SUMMARY.json","w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(coverage, indent=2, default=str))
    print(pd.DataFrame(metrics).to_string(index=False))

if __name__ == "__main__":
    main()
