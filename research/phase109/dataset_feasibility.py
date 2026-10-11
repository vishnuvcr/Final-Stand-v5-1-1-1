#!/usr/bin/env python3
"""Build a provenance-aware inventory for Phase 109 data sources.

A dataset-card license field is not treated as proof that underlying exchange or
broker data may be redistributed. Discovery does not make a source backtest-ready.
"""
import csv, json
from datetime import datetime, timezone
from pathlib import Path

OUT=Path("results/phase109")
HF="https://huggingface.co/datasets/"
NSE_REPORT="https://www.nseindia.com/all-reports-derivatives"

BASE=[
{"source_id":"NSE_FO_UDIFF","source":"Official NSE F&O UDiFF daily bhavcopy","data_domain":"Index/stock options daily OHLC, expiry, strike, CE/PE, volume and OI","reported_coverage":"Current UDiFF format from 2024-07-08 onward","source_url":NSE_REPORT,"license_or_terms":"Official exchange archive; redistribution/use terms require review","preferred_role":"Primary exact-contract EOD source","status":"PENDING_ARCHIVE_PROBE","blocking_gate":"Boundary/recent date probes must pass, followed by full-session and contract-identity coverage audit","key_risks":"EOD OHLC is not bid/ask/depth; zero-volume rows and schema transitions must be explicitly handled"},
{"source_id":"NSE_FO_LEGACY","source":"Official NSE F&O legacy bhavcopy","data_domain":"Index/stock options daily OHLC, expiry, strike, CE/PE, volume and OI","reported_coverage":"Through 2024-07-05; legacy columns and file names differ from UDiFF","source_url":"https://archives.nseindia.com/content/historical/DERIVATIVES/{YYYY}/{MON}/fo{DDMONYYYY}bhav.csv.zip","license_or_terms":"Official exchange archive; redistribution/use terms require review","preferred_role":"Historical exact-contract EOD source","status":"PENDING_ARCHIVE_PROBE","blocking_gate":"Legacy schema probe and history coverage/continuity audit must pass","key_risks":"Do not concatenate formats before schema normalization, contract-identity and duplicate/date checks"},
{"source_id":"DHAN_ROLLING_OPTIONS","source":"DhanHQ rolling expired-options API","data_domain":"Intraday OHLC, IV, OI, volume, spot, strike-relative option observations","reported_coverage":"API description reports up to five years and up to 30 calendar days per request","source_url":"https://dhanhq.co/docs/v2/expired-options-data/","license_or_terms":"Account/subscription terms; credentials are workflow secrets","preferred_role":"Supplementary IV/OI/flow features; not assumed fixed-contract exit pricing","status":"ACCESS_SCHEMA_PROBE_PENDING","blocking_gate":"Authenticated response must prove expiry/strike-selector semantics and reconcile with official fixed-contract data","key_risks":"Rolling ATM-relative series can change contracts; initial probe does not establish fixed-expiry history"},
{"source_id":"HF_RISSIN_OPTIONS","source":"rissin/nse-options-intraday","data_domain":"Publisher-described daily index options 2001 onward plus 1-minute index options roughly 2024 onward","reported_coverage":"Publisher describes NIFTY/BANKNIFTY daily and NIFTY/BANKNIFTY/SENSEX intraday; schema has expiry/strike/type/OHLC/volume/OI","source_url":HF+"rissin/nse-options-intraday","license_or_terms":"HF card declares license=other; intraday data are derived from Upstox and provider terms apply","preferred_role":"Potential cross-check only after rights and data-quality verification","status":"BLOCKED_RIGHTS_AND_QUALITY_REVIEW","blocking_gate":"Clarify license/provider terms and audit zero rows, invalid OHLC, dates, duplicates and source labels","key_risks":"Public availability is not a usable license; visible sample rows include zero price/volume records"},
{"source_id":"HF_TRADEMARKK_OPTIONS","source":"thetrademarkk/india-index-options-1m","data_domain":"Publisher-described 1-minute index spot and options OHLCV/OI","reported_coverage":"Approx. 2021-2026; card metadata shows 3,337 files and partial contract/strike coverage","source_url":HF+"thetrademarkk/india-index-options-1m","license_or_terms":"CC BY-NC 4.0; compatibility must be checked before use/publication","preferred_role":"Independent intraday robustness check only if rights cleared","status":"BLOCKED_PENDING_LICENSE_AND_COVERAGE_REVIEW","blocking_gate":"Confirm intended-use rights, exact coverage/missing strikes and official price reconciliation","key_risks":"Publisher notes partial coverage and sparse far/illiquid strikes; no raw data republished absent rights"},
{"source_id":"HF_TEJHQ_EQUITY","source":"tejhq/indian-markets","data_domain":"EOD NSE/BSE equities, symbol history, corporate actions, derived metrics and point-in-time liquidity universe","reported_coverage":"Publisher card reports NSE since 2010 and BSE since 2024-07; daily equities, not option contracts","source_url":HF+"tejhq/indian-markets","license_or_terms":"MIT declared on card; publisher advises verifying exchange terms for commercial use","preferred_role":"Candidate for breadth, sector, constituent, corporate-action and equity cross-check features","status":"CANDIDATE_SCHEMA_AUDIT_PENDING","blocking_gate":"Check schema, point-in-time membership/action timestamps, provenance and exchange terms","key_risks":"Not an option-premium source; avoid revised constituent membership/back-adjusted-price look-ahead"},
{"source_id":"HF_AADEVLOPER_VIX","source":"AAdevloper/nifty50-market-regime","data_domain":"Small CSV claiming date, India VIX, RSI, MA and regime label","reported_coverage":"Publisher page shows about 2.24k rows and MIT tag","source_url":HF+"AAdevloper/nifty50-market-regime","license_or_terms":"MIT is declared on card; data provenance is unverified","preferred_role":"Reject unless original source and schema are corrected/verified","status":"REJECTED_SUSPECT_FIELD_LABEL","blocking_gate":"Displayed india_vix value around 8,295 on 2015-10-23 is inconsistent with usual VIX-point units","key_risks":"Do not use as implied volatility or silently rescale a mislabeled field"},
{"source_id":"HF_AVERAGEDEV_VIX","source":"average-developer/stocks-INDIAVIX-1D-candles","data_domain":"Publisher-labelled India VIX daily candles","reported_coverage":"HF file names suggest annual files 2009-2026; rows/schema not validated","source_url":HF+"average-developer/stocks-INDIAVIX-1D-candles","license_or_terms":"No license declared in API card metadata","preferred_role":"Not used until license and schema verification","status":"BLOCKED_LICENSE_MISSING","blocking_gate":"License, source, India VIX OHLC units, date range, integrity and duplicate checks","key_risks":"Do not infer usability from dataset name or file names"},
{"source_id":"HF_VISHNUN_OHLCV","source":"vishnun0027/indian-market-historical-ohlcv","data_domain":"Publisher-reported NSE/BSE stocks, indices, ETFs, commodities/FX daily OHLCV","reported_coverage":"Page reports 2,690 files, daily OHLCV and refresh through 2026-10-10; Yahoo Finance via yfinance","source_url":HF+"vishnun0027/indian-market-historical-ohlcv","license_or_terms":"MIT declared on card; data source is Yahoo Finance/yfinance","preferred_role":"Secondary spot/market-context cross-check, not primary option fill data","status":"CANDIDATE_SOURCE_AND_SYMBOL_AUDIT_PENDING","blocking_gate":"Verify exact index symbols, timezone, adjusted/raw prices and point-in-time revisions","key_risks":"Unofficial endpoint and revised adjusted prices; no fixed option-chain identity"},
{"source_id":"HF_RAHULKRRAJ_INTRADAY","source":"rahulkrraj/indian-stock-market-minute-data","data_domain":"Publisher-reported minute/daily stock and index OHLCV/OI","reported_coverage":"Page claims 2000-2026 daily and 2022-2026 minute, about 715M rows and multi-GB parquet","source_url":HF+"rahulkrraj/indian-stock-market-minute-data","license_or_terms":"MIT declared on card; raw-source provenance not verified","preferred_role":"Only after bounded download/schema and point-in-time checks","status":"BLOCKED_PROVENANCE_AND_SCALE_AUDIT","blocking_gate":"Verify source, instruments, timezone, missingness, license and reproducible partition manifest","key_risks":"High download/compute cost; schema is not a substitute for exact option contracts"},
{"source_id":"HF_GENAI_FEATURES","source":"GenAIDevTOProd/NIFTY-feature-enhanced","data_domain":"Small NIFTY feature dataset with news, technical indicators and sentiment fields","reported_coverage":"HF card shows about 1.48k rows with train/validation/test splits","source_url":HF+"GenAIDevTOProd/NIFTY-feature-enhanced","license_or_terms":"MIT declared on card; news origin/timestamps/rights not verified","preferred_role":"Excluded from primary testing until leakage review","status":"BLOCKED_LOOKAHEAD_AND_PROVENANCE_AUDIT","blocking_gate":"Prove news/features were public before every decision; recompute rolling indicators from raw data","key_risks":"Precomputed indicators and sentiment-aligned returns risk leakage and selection bias"},
{"source_id":"NSE_HISTORICAL_INDEX_VIX","source":"NSE official historical index and India VIX reports","data_domain":"Daily index OHLC and India VIX OHLC/close/change","reported_coverage":"Official NSE reports expose historical index data and separate historical India VIX exports","source_url":"https://www.nseindia.com/reports-indices-historical-vix","license_or_terms":"Official exchange report; retain provenance and review usage terms","preferred_role":"Primary India VIX/regime and index-level series","status":"ACCESS_AND_BULK_COVERAGE_PENDING","blocking_gate":"Automate historical date-range capture and validate VIX range, dates and duplicate rows","key_risks":"Never infer VIX from spot returns; publication timing must be explicit"},
{"source_id":"NSE_FII_PARTICIPANT_STATS","source":"NSE FII derivatives and participant statistics","data_domain":"Participant-wise OI/volume, FII derivatives statistics, daily volatility and related reports","reported_coverage":"Official reports page lists daily and participant files; historical bulk acquisition not yet tested","source_url":NSE_REPORT,"license_or_terms":"Official exchange reports; preserve report date/publication timestamp","preferred_role":"Flows/positioning feature only after release-time alignment","status":"ACCESS_AND_PUBLICATION_LAG_PENDING","blocking_gate":"Acquire dated files and map publication time to the next eligible observation","key_risks":"Same-day close data can leak if only published after the entry decision"},
{"source_id":"GLOBAL_INDEX_CONTEXT","source":"Free global-index and macro time-series sources to be compared","data_domain":"S&P 500, Nasdaq, Dow, volatility, global index futures, gold and rates","reported_coverage":"Candidate set; exact providers/coverage must be frozen in source registration","source_url":"https://stooq.com/ ; https://fred.stlouisfed.org/ ; https://finance.yahoo.com/","license_or_terms":"Provider-specific terms/attribution require review","preferred_role":"Lagged previous-session cross-market context only","status":"SOURCE_CATALOGUE_PENDING","blocking_gate":"Freeze no-look-ahead timestamp map, timezone/holiday calendar, provenance and release lags","key_risks":"Cross-market closes and macro releases have different timestamps and publication delays"},
]

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    ap=OUT/"source_access_audit.csv"
    hp=OUT/"huggingface_dataset_candidates.json"
    np=OUT/"nse_archive_source_feasibility.json"
    audits=list(csv.DictReader(ap.open(encoding="utf-8"))) if ap.exists() else []
    hf=json.loads(hp.read_text(encoding="utf-8")) if hp.exists() else {}
    nse=json.loads(np.read_text(encoding="utf-8")) if np.exists() else {}
    cards=hf.get("known_dataset_cards",{})
    seen={}
    for term,res in hf.get("terms",{}).items():
        for ds in res.get("datasets",[]):
            if ds.get("id"): seen.setdefault(ds["id"],[]).append(term)
    mapping={"HF_RISSIN_OPTIONS":"rissin/nse-options-intraday","HF_TRADEMARKK_OPTIONS":"thetrademarkk/india-index-options-1m","HF_TEJHQ_EQUITY":"tejhq/indian-markets","HF_AADEVLOPER_VIX":"AAdevloper/nifty50-market-regime","HF_AVERAGEDEV_VIX":"average-developer/stocks-INDIAVIX-1D-candles","HF_VISHNUN_OHLCV":"vishnun0027/indian-market-historical-ohlcv","HF_RAHULKRRAJ_INTRADAY":"rahulkrraj/indian-stock-market-minute-data","HF_GENAI_FEATURES":"GenAIDevTOProd/NIFTY-feature-enhanced"}
    rows=[]
    for base in BASE:
        row=dict(base)
        if base["source_id"] in mapping:
            dsid=mapping[base["source_id"]]
            card=cards.get(dsid,{})
            row["discovered_license"]=card.get("license") or "NOT_DECLARED"
            row["last_modified_utc"]=card.get("lastModified","")
            row["hf_file_count"]=card.get("file_count","")
            row["hf_discovery_queries"]=";".join(seen.get(dsid,[]))
        if base["source_id"] in {"NSE_FO_UDIFF","NSE_FO_LEGACY"}:
            probes=nse.get("probes",[])
            if base["source_id"]=="NSE_FO_UDIFF":
                match=[p for p in probes if p.get("format")=="UDiFF"]
            else:
                match=[p for p in probes if p.get("format")=="LEGACY" or p.get("expected_date")=="2024-07-05"]
            success=any(p.get("status")=="SCHEMA_AND_ROWS_PROBED" and (base["source_id"]!="NSE_FO_UDIFF" or p.get("format")=="UDiFF") and (base["source_id"]!="NSE_FO_LEGACY" or p.get("format")=="LEGACY") for p in match)
            row["status"]="SCHEMA_PROBE_PASS_BULK_COVERAGE_PENDING" if success else "BLOCKED_SCHEMA_PROBE"
            row["probe_dates"]=";".join(p.get("expected_date","")+":"+p.get("status","") for p in match)
        if base["source_id"]=="DHAN_ROLLING_OPTIONS":
            a=next((a for a in audits if a.get("source")=="DhanHQ rolling expired-options API"),{})
            row["status"]="ACCESS_SCHEMA_PROBE_PASS_FIXED_CONTRACT_GATE_PENDING" if a.get("status")=="AUTH_AND_SCHEMA_PROBE_OK" else "BLOCKED_ACCESS_SCHEMA"
            row["probe_observed_rows"]=a.get("bar_count","")
            row["probe_fields"]=a.get("data_fields_returned","")
        rows.append(row)
    fields=sorted({k for row in rows for k in row})
    with (OUT/"source_feasibility_matrix.csv").open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields,extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    good=sum(1 for p in nse.get("probes",[]) if p.get("status")=="SCHEMA_AND_ROWS_PROBED")
    total=len(nse.get("probes",[]))
    lines=[
      "# Phase 109 source-feasibility report","",
      "Generated: "+datetime.now(timezone.utc).isoformat(),"",
      "This records candidate sources and their current gates; it does not claim that they are approved, downloaded, or used in a backtest.","",
      "## Runtime checks","",
      f"- Official NSE legacy/UDiFF probe: {good}/{total} dates passed; report status {nse.get('overall_status','NOT_RUN')}.",
      "- Dhan: initial authenticated schema probe is a short rolling strike-relative sample; fixed expiry/contract use remains blocked pending reconciliation.",
      "- Hugging Face: eight dataset cards inspected for declared license, update time and file listing. Metadata and publisher claims are not independent data-quality proof.","",
      "## Source decisions","",
      "- Use NSE official legacy/UDiFF archives as the primary exact-contract daily options source only after bulk trading-session, identity, expiry, lot-size, positive-volume and OHLC audits.",
      "- Use Dhan as a supplementary IV/OI/flow source, not fixed-contract fills, until strike/expiry transitions and executable price mapping are proven.",
      "- rissin/nse-options-intraday is blocked for now: license=other; intraday source is Upstox and provider terms apply; visible examples include zero-price/zero-volume rows.",
      "- thetrademarkk/india-index-options-1m has CC BY-NC 4.0 and publisher-described partial coverage; block pending license compatibility and official reconciliation.",
      "- tejhq/indian-markets is a promising MIT-declared EOD equity/corporate-action/symbol-history candidate, not an option-price source; validate point-in-time membership and exchange terms.",
      "- AAdevloper/nifty50-market-regime is rejected for India VIX use until corrected: the displayed 2015-10-23 value is about 8,295, inconsistent with VIX-point units.",
      "- average-developer/stocks-INDIAVIX-1D-candles is blocked because no license is declared and rows/schema are not independently validated.",
      "- News/feature-enhanced datasets are excluded until publication-time alignment and look-ahead checks pass.",
      "- Official NSE historical index and India VIX reports and FII/participant files exist; automated historical acquisition, coverage and publication-lag audits remain pending.",
      "- Global indices, volatility, gold and rates must be timestamp-aligned so only information available before each Indian decision can be used.","",
      "## Registered source URLs","",
    ]
    for row in rows: lines.append("- ["+row["source"]+"]("+row["source_url"]+") — "+row.get("status","")+".")
    lines.extend(["","See source_feasibility_matrix.csv, source_access_audit.csv, NSE archive probe output and Hugging Face metadata for machine-readable evidence."])
    (OUT/"SOURCE_FEASIBILITY_REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"candidate_rows":len(rows),"nse_probe_passes":f"{good}/{total}","report":"results/phase109/SOURCE_FEASIBILITY_REPORT.md"},sort_keys=True))

if __name__=="__main__": main()
