#!/usr/bin/env python3
"""Data-availability matrix for every registered strategy-family architecture.

A source may be discoverable but not legally/technically usable. This report only
counts candidate configurations for which declared inputs are present in the
audited source inventory; it never claims strategies were backtested.
"""
import csv, json
from datetime import datetime, timezone
from itertools import product
from pathlib import Path

OUT=Path("results/phase109")


def read_json(name):
    p=OUT/name
    if not p.exists(): return {}
    try: return json.loads(p.read_text(encoding="utf-8"))
    except Exception: return {}


def read_csv(name):
    p=OUT/name
    return list(csv.DictReader(p.open(encoding="utf-8"))) if p.exists() else []


def get_num(d,key):
    try: return int(float(d.get(key,0) or 0))
    except (TypeError,ValueError): return 0


def required_inputs(fam):
    raw=fam.get("required_inputs_json",fam.get("required_inputs", "[]"))
    if isinstance(raw,list): return raw
    try:
        v=json.loads(raw)
        return v if isinstance(v,list) else []
    except Exception:
        return []


def axes_of(row):
    raw=row.get("axes_json","{}")
    if isinstance(raw,dict): return raw
    try:
        v=json.loads(raw)
        return v if isinstance(v,dict) else {}
    except Exception:
        return {}


def first_field(row,*names):
    for name in names:
        if row.get(name) not in (None,""):
            return row[name]
    return ""


def main():
    families=read_csv("strategy_families.csv")
    spaces={first_field(r,"family_id","family_key","id"):r for r in read_csv("family_configuration_space.csv")}
    option=read_json("nse_index_options_backfill_summary.json")
    index=read_json("niftyindices_context_summary.json")
    fut=read_json("nse_index_futures_summary.json")
    dhan=read_json("dhan_rolling_options_audit.json")
    model_greeks=read_json("options_model_greeks_summary.json")
    grid=read_json("phase109_grid_summary.json")
    index_summary={r.get("series"):r for r in index.get("merged_series_summary",[])}
    nse_rows=get_num(option,"archive_dates_parsed")
    nse_pos=get_num(option,"positive_volume_rows")
    nse_id=get_num(option,"identity_complete_rows")
    nse_prices=get_num(option,"price_complete_rows")
    nifty=index_summary.get("NIFTY 50",{})
    bank=index_summary.get("NIFTY BANK",{})
    vix=index_summary.get("INDIA_VIX",{})
    option_ok=bool(nse_rows and nse_pos and nse_id and nse_prices)
    index_ok=bool(nifty.get("unique_date_count",0) and bank.get("unique_date_count",0))
    vix_ok=bool(vix.get("unique_date_count",0) and not vix.get("invalid_OHLC_rows",0))
    future_ok=bool(get_num(fut,"dates_with_selected_index_futures") and not get_num(fut,"invalid_ohlc_positive_volume_rows"))
    dhan_ok=bool(dhan.get("summary",{}).get("rows",0) and dhan.get("summary",{}).get("invalid_ohlc_rows",0)==0)
    model_greeks_ok=bool(model_greeks.get("valid_model_greek_rows",0) and model_greeks.get("udiff_dates_parsed",0))
    caps={
      "underlying_close":(option_ok,"Official option archive/underlying observations present; per-symbol coverage still required"),
      "underlying_ohlc":(index_ok,"Official NIFTY 50/NIFTY BANK daily OHLC only; not all underlying indices"),
      "daily_timestamp":(option_ok,"Daily archive dates present"),
      "timestamp":(option_ok,"Daily timestamps present; this does not satisfy intraday execution"),
      "spot_price":(option_ok,"Spot/underlying close available in UDiFF for eligible dates and official index context for NIFTY/BANK"),
      "strike":(option_ok,"Exact strike identity in official option archives"),
      "expiry":(option_ok,"Exact expiry identity in official option archives"),
      "option_type":(option_ok,"CE/PE identity present"),
      "option_price":(option_ok,"EOD option OHLC present; not bid/ask/depth"),
      "contract_identity":(option_ok,"Daily symbol/expiry/strike/side identity present; contiguous contract coverage must still pass"),
      "open_interest":(option_ok,"End-of-day OI field present; positive/valid value audits remain per date"),
      "option_volume":(option_ok,"End-of-day contract volume present; zero-volume contracts are ineligible"),
      "option_chain_oi":(option_ok,"Can be aggregated from audited exact option contracts; aggregation definition must be frozen"),
      "option_chain_volume":(option_ok,"Can be aggregated from audited exact option contracts; aggregation definition must be frozen"),
      "future_price":(future_ok,"Official daily index-futures extraction present; spot sync/expiry and lot-size checks still required"),
      "future_contract_identity":(future_ok,"Future symbol/expiry identity present; date-level duplicate/coverage gates remain"),
      "index_context":(index_ok,"Official NIFTY 50 and NIFTY BANK context series present"),
      "india_vix":(vix_ok,"Official NSE Indices VIX series only; timestamp/release lag still required"),
      "option_iv":(dhan_ok or model_greeks_ok,"Dhan rolling ATM IV and/or exact-contract Black-Scholes implied-vol estimates are present; both require separate model/proxy sensitivity gates"),
      "model_iv_estimate":(model_greeks_ok,"Exact-contract EOD premium-implied volatility estimated using flat 6.5% rate, zero dividend, European Black-Scholes; not exchange-published IV"),
      "rolling_atm_iv":(dhan_ok,"Dhan rolling ATM IV feature series present; use only as lagged market feature"),
      "rolling_atm_oi":(dhan_ok,"Dhan rolling ATM OI feature series present; rolling contract transitions limit interpretation"),
      "underlying_volume":(False,"No synchronized underlying-index volume series has passed source audit"),
      "intraday_ohlcv":(False,"No verified underlying intraday OHLCV execution dataset is approved"),
      "intraday_timestamp":(False,"Option ATM timestamps alone do not provide a full underlying intraday bar/chain"),
      "intraday_option_chain":(False,"Dhan rolling ATM is not a historical complete strike/expiry option chain"),
      "futures_intraday":(False,"Current futures source is EOD archive only"),
      "fii_flow":(False,"Official historical FII series has not yet passed bulk coverage/publication-lag audit"),
      "dii_flow":(False,"Official historical DII series has not yet passed bulk coverage/publication-lag audit"),
      "participant_positioning":(False,"Participant statistics have not yet been acquired and release-time aligned"),
      "global_index_return":(False,"Point-in-time global index source/calendar has not passed audit"),
      "global_volatility":(False,"Point-in-time global VIX/volatility source has not passed audit"),
      "global_gold":(False,"Gold series/time-zone/contract method not yet audited"),
      "rates":(False,"No historical risk-free/rate curve has been validated for carry pricing"),
      "interest_rate":(False,"No historical risk-free/rate curve has been validated for carry pricing"),
      "dividend_schedule":(False,"No date-effective dividend/corporate-action schedule has been audited for index carry"),
      "corporate_action":(False,"Corporate-action source and publication timing not yet validated"),
      "event_calendar":(False,"No date-aligned earnings/macro/news event calendar has passed audit"),
      "news_sentiment":(False,"No timestamped news-source dataset has passed point-in-time/right checks"),
      "breadth":(False,"Historical point-in-time breadth/constituent data not yet ingested"),
      "sector_rotation":(False,"Historical sector constituents/weights not yet verified point-in-time"),
      "greeks":(model_greeks_ok,"Model-derived delta/gamma/vega/theta from exact-contract EOD close; r=6.5%, q=0%, model and stale-mark sensitivities pending"),
      "delta_model":(model_greeks_ok,"Model-derived Black-Scholes delta; not exchange-published"),
      "gamma_model":(model_greeks_ok,"Model-derived Black-Scholes gamma; not exchange-published"),
      "vega_per_vol_point_model":(model_greeks_ok,"Model-derived vega; not exchange-published"),
      "theta_per_calendar_day_model":(model_greeks_ok,"Model-derived theta; not exchange-published"),
      "option_skew":(False,"Exact-expiry matched IV smile/skew is not available from the rolling ATM source"),
      "synthetic_future":(future_ok and option_ok,"Synthetic-forward can be computed from matched call/put and future closes; carry/exit realism still required"),
      "basis":(future_ok and option_ok,"EOD spot/futures basis candidate; exact timestamp alignment and dated costs remain"),
      "expiry_calendar":(option_ok,"Option/futures expiry field present; holiday/roll rules remain"),
      "volatility":(bool(nifty.get("unique_date_count",0)),"Realized volatility may be calculated from audited close history"),
      "volatility_lookback":(True,"Registered parameter axis; not an external data dependency"),
      "signal_lookback_sessions":(True,"Registered parameter axis; not an external data dependency"),
      "signal_threshold":(True,"Registered parameter axis; not an external data dependency"),
      "move_or_signal_threshold_pct":(True,"Registered parameter axis; not an external data dependency"),
      "strike_target":(True,"Registered option-selection parameter axis"),
      "holding_exit":(True,"Registered exit-horizon parameter axis"),
      "risk_profile":(True,"Registered exit/risk parameter axis"),
      "oi_confirmation_method":(True,"Registered OI configuration axis; source data checked separately"),
    }
    # Header aliases allow the generator's different field names without silently
    # treating an unknown input as available.
    aliases={
      "underlying_open":"underlying_ohlc","underlying_high":"underlying_ohlc","underlying_low":"underlying_ohlc",
      "prior_close":"underlying_ohlc","volatility_lookback_sessions":"volatility_lookback",
      "lookback_sessions":"signal_lookback_sessions","move_threshold_pct":"move_or_signal_threshold_pct",
      "cross_index_or_global_return":"index_context",
      "nifty_close":"index_context","banknifty_close":"index_context",
      "futures_close":"future_price","future_expiry":"future_contract_identity",
      "synthetic_future":"synthetic_future","basis":"basis",
      "open_gap":"underlying_ohlc","realized_volatility":"volatility",
      "volatility_regime":"volatility","event_timestamp":"event_calendar",
      "news":"news_sentiment","sentiment":"news_sentiment","macro_event":"event_calendar",
      "put_call_ratio":"option_chain_oi","options_flow":"option_chain_volume",
      "option_oi":"open_interest","oi_change":"open_interest",
      "vix":"india_vix","india_vix_close":"india_vix",
      "option_greeks":"greeks","delta":"greeks","gamma":"greeks","vega":"greeks","theta":"greeks",
      "global_index":"global_index_return","cross_asset_return":"global_index_return",
      "institutional_flow":"participant_positioning","fii":"fii_flow","dii":"dii_flow",
    }
    rows=[]; family_counts={}
    for fam in families:
        fid=first_field(fam,"family_id","family_key","id")
        space=spaces.get(fid,{})
        axes=axes_of(space)
        try: total=int(float(first_field(space,"configurations","configuration_count","total_configurations") or 0))
        except (ValueError,TypeError): total=0
        if total==0:
            try: total=int(first_field(fam,"configuration_count","configurations") or 0)
            except (ValueError,TypeError): total=0
        req=required_inputs(fam)
        missing=[]; partial=[]
        for raw in req:
            key=str(raw).strip().lower()
            cap=aliases.get(key,key)
            if cap not in caps:
                missing.append((key,"Unregistered/unverified input; default block"))
            elif not caps[cap][0]:
                missing.append((key,caps[cap][1]))
            elif cap in {"option_iv","model_iv_estimate","delta_model","gamma_model","vega_per_vol_point_model","theta_per_calendar_day_model","greeks","rolling_atm_iv","rolling_atm_oi","basis","synthetic_future","future_price","future_contract_identity"}:
                partial.append((key,caps[cap][1]))
        eligible=total if not missing else 0
        why="; ".join(f"{x}: {y}" for x,y in missing)
        if missing:
            state="BLOCKED_MISSING_INPUTS"
        elif partial:
            state="INPUTS_PRESENT_WITH_PROXY_OR_EXECUTION_GATES"
            why="; ".join(f"{x}: {y}" for x,y in partial)
        else:
            state="INPUTS_PRESENT_EXECUTION_AND_SPLIT_GATES_PENDING"
            why="Source fields exist; contiguous date coverage, positive-volume selection, lot size, costs, timing and OOS must pass before a backtest."
        rows.append({
          "family_id":fid,
          "family_name":first_field(fam,"family_name","name","label","family_id"),
          "core_id":first_field(fam,"core_id","core","signal_core","core_name"),
          "confirmation_id":first_field(fam,"confirmation_id","confirmation","confirm_id"),
          "regime_id":first_field(fam,"regime_id","regime","regime_gate"),
          "registered_configurations":total,
          "declared_inputs_json":json.dumps(req,separators=(",",":")),
          "source_feasibility_status":state,
          "candidate_configurations_by_input_presence":eligible,
          "missing_inputs_json":json.dumps([{"input":x,"reason":y} for x,y in missing],separators=(",",":")),
          "execution_and_method_gates_json":json.dumps([{"input":x,"gate":y} for x,y in partial],separators=(",",":")),
          "interpretation":"Input availability status only; registered/configurable does not mean attempted or backtested.",
        })
        family_counts[state]=family_counts.get(state,0)+1
    path=OUT/"family_data_feasibility.csv"
    fields=sorted({k for r in rows for k in r})
    with path.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)
    summary={
      "generated_utc":datetime.now(timezone.utc).isoformat(),
      "registered_families":len(rows),
      "grid_summary_family_count":grid.get("family_count",0),
      "family_counts_by_status":dict(sorted(family_counts.items())),
      "registered_configurations_total":sum(r["registered_configurations"] for r in rows),
      "candidate_configs_with_all_inputs_present":sum(r["candidate_configurations_by_input_presence"] for r in rows),
      "families_with_missing_inputs":sum(1 for r in rows if r["source_feasibility_status"]=="BLOCKED_MISSING_INPUTS"),
      "families_with_proxy_or_execution_gates":sum(1 for r in rows if r["source_feasibility_status"]=="INPUTS_PRESENT_WITH_PROXY_OR_EXECUTION_GATES"),
      "families_with_inputs_present":sum(1 for r in rows if r["source_feasibility_status"]=="INPUTS_PRESENT_EXECUTION_AND_SPLIT_GATES_PENDING"),
      "known_data_presence":{
        "option_archive_dates_parsed":nse_rows,"positive_volume_option_rows":nse_pos,
        "index_context_series":{k:v.get("unique_date_count",0) for k,v in index_summary.items()},
        "dhan_rolling_rows":get_num(dhan.get("summary",{}),"rows"),
        "valid_model_greek_rows":get_num(model_greeks,"valid_model_greek_rows"),
        "model_greeks_rate_assumption":model_greeks.get("risk_free_rate_assumption"),
        "model_greeks_dividend_assumption":model_greeks.get("dividend_yield_assumption"),
        "futures_dates":get_num(fut,"dates_with_selected_index_futures"),
      },
      "note":"This matrix uses declared input fields and audited source presence only; it does not run a strategy, verify complete chronological holdout coverage, or promote a family.",
    }
    (OUT/"family_data_feasibility_summary.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    lines=[
      "# Phase 109 family-by-family data-feasibility gate","",
      "Generated: "+summary["generated_utc"],"",
      "**This is an input availability gate, not a backtest.** Family counts and candidate configurations are not performance-tested observations.","",
      "| State | Families |",
      "|---|---:|",
    ]
    for key,val in sorted(family_counts.items()): lines.append(f"| {key} | {val:,} |")
    lines.extend(["","## Aggregate",
      f"- Registered architecture combinations: {len(rows):,}.",
      f"- Total registered configurations under current grid: {summary['registered_configurations_total']:,}.",
      f"- Candidate configurations whose declared fields are present (before date, symbol and execution gates): {summary['candidate_configs_with_all_inputs_present']:,}.",
      f"- Data-gated families: {summary['families_with_missing_inputs']:,}.",
      f"- Families with proxy or execution conditions: {summary['families_with_proxy_or_execution_gates']:,}.",
      f"- Families with source fields present but execution/split gates pending: {summary['families_with_inputs_present']:,}.","",
      "## Interpretation",
      "- Official NSE EOD index-option archives support exact symbol/expiry/strike/side, OHLC, volume and OI, subject to session coverage and positive-volume filters.",
      "- Dhan historical rolling ATM IV/OI is a feature candidate only; rolling contracts are not fixed-contract entries/exits.",
      "- Futures EOD may support a basis feature after spot/expiry/lot-size checks, not intraday fills.",
      "- India VIX is usable only if official NSE Indices series passes range/schema/time alignment checks.",
      "- Greek-dependent families may use the separately labelled exact-contract Black-Scholes estimates only as model-derived features with explicit r=6.5%/q=0% sensitivity gates; directly observed Greeks and matched IV skew remain unavailable. Global-, FII/DII-, event-, news-, breadth- and corporate-action-dependent families stay blocked until their respective audited sources are present. Never substitute unlabeled or unverified proxies.",
      "- All P&L rows before 2024-10-01 remain blocked under the currently verified transaction-cost model. Earlier price history may serve as indicator warm-up, not as a net-return sample, until an approved pre-October-2024 cost schedule is implemented.",
      "",
      "See family_data_feasibility.csv and family_data_feasibility_summary.json for the full list of missing inputs and eligibility decisions.")
    (OUT/"FAMILY_DATA_FEASIBILITY_REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(summary,sort_keys=True))


if __name__=="__main__": main()
