#!/usr/bin/env python3
"""Write reproducible static Phase 80 registry; no data downloads."""
import json
from pathlib import Path
OUT=Path("results/phase80_universe_audit")
OUT.mkdir(parents=True,exist_ok=True)
sources=[
 {"name":"Bhat et al. (2024), Journal of Futures Markets","type":"peer-reviewed literature","url":"https://doi.org/10.1002/fut.22512","scope":"Delta-hedged short NIFTY options; overnight/intraday return asymmetry","status":"hypothesis source; static structures differ"},
 {"name":"Zenodo 10899828","type":"minute OHLC dataset","url":"https://zenodo.org/records/10899828","scope":"NIFTY spot, futures and options, 2017-2020","status":"license unclear; no raw data retained"},
 {"name":"artist-23/nifty-options-data","type":"HF dataset","url":"https://huggingface.co/datasets/artist-23/nifty-options-data","scope":"OHLC, IV, OI, spot and strike labels, 2020-2025","status":"license and exact expiry identity need validation"},
 {"name":"rissin/nse-options-intraday","type":"HF dataset","url":"https://huggingface.co/datasets/rissin/nse-options-intraday","scope":"explicit contract OHLC; 1m Upstox data 2024-2026 plus EOD history","status":"license other; source terms/retention review needed; intraday OI absent"},
 {"name":"thetrademarkk/india-index-options-1m","type":"HF dataset","url":"https://huggingface.co/datasets/thetrademarkk/india-index-options-1m","scope":"existing primary 1-minute OHLCV(+OI), 2021-2026","status":"CC-BY-NC-4.0; partial coverage; no quotes/depth"},
 {"name":"QuantDev-stack/OptionVault","type":"code and dataset samples","url":"https://github.com/QuantDev-stack/OptionVault","scope":"sample options/Greeks/futures/depth files","status":"full coverage requires separately licensed data"},
 {"name":"sahilempire/nifty-options-research-lab","type":"open code/literature corpus","url":"https://github.com/sahilempire/nifty-options-research-lab","scope":"strategy structures, realistic costs, backtest methods","status":"MIT repo; third-party empirical claims not independently verified"},
 {"name":"Bailey & López de Prado (2014) — Deflated Sharpe Ratio","type":"statistical methodology","url":"https://doi.org/10.3905/jpm.2014.40.5.094","scope":"selection bias/multiple testing/non-normality","status":"include multiplicity and non-normal returns in inference"}
]
families=[
 {"family":"short_atm_straddle","legs":"-1 CE ATM, -1 PE ATM","risk":"unbounded; diagnostic-only"},
 {"family":"short_iron_fly_w100","legs":"-1 CE ATM, -1 PE ATM, +1 CE ATM+100, +1 PE ATM-100","risk":"defined"},
 {"family":"short_iron_fly_w200","legs":"same with 200-point wings","risk":"defined"},
 {"family":"short_iron_fly_w300","legs":"same with 300-point wings","risk":"defined"},
 {"family":"long_iron_fly_w100_200_300","legs":"+1 CE ATM, +1 PE ATM, -1 CE ATM+W, -1 PE ATM-W","risk":"debit-limited"},
 {"family":"short_iron_condor_100_300","legs":"+1 PE ATM-300, -1 PE ATM-100, -1 CE ATM+100, +1 CE ATM+300","risk":"defined"},
 {"family":"bull_put_credit_100_300","legs":"-1 PE ATM-100, +1 PE ATM-300","risk":"defined"},
 {"family":"bear_call_credit_100_300","legs":"-1 CE ATM+100, +1 CE ATM+300","risk":"defined"}
]
payload={"phase":80,"as_of":"2026-10-10","completeness":"not exhaustive; finite registry is explicit and reproducible","prior_coverage":{"phase45_new_structures":20,"phase45_reused_phase43_families":22,"other_axes":["VIX regime","feature/symbolic/ensemble selectors","direction polarity","ratio geometry","entry filter","stop/conditional exit","temporal inference"]},"new_test_axis":"paired intraday versus overnight window for same structure/date and exact contracts","temporal_splits":{"development_end":"2023-12-31","validation_end":"2025-12-31","holdout_start":"2026-01-01","holdout_end":"2026-09-30"},"families":families,"sources":sources,"declared structure variants":16,"rights_rule":"unclear/other license means metadata-only; do not cache or republish raw data","execution_rule":"Paytm Money ₹10 per order assumption, historical statutory charges, ₹0.05 adverse per leg per fill; prices based on candle opens; not proof of executable fills"}
(OUT/"source_strategy_registry.json").write_text(json.dumps(payload,indent=2)+"\n")
lines=["# Phase 80 — Expanded strategy and source audit","","> **Decision: the prior search did not test every possible combination. The finite, registered next experiment is same-structure intraday vs overnight exposure.**","","## What is already covered","", "- Phase 45 explicitly tested 20 previously uncovered ready-made structures and combined them with 22 Phase-43 families.", "- Earlier work covered VIX regime/candidate sweeps, selector/features/symbolic/ensemble policies, ratio geometry, entry filters and stop exits.", "- The main Phase-45 entry/exit geometry (10:00 four sessions before expiry to expiry-day last common bar) does not answer how the same structure behaves when held intraday versus overnight.","","## New leads and rights boundary",""]
for s in sources: lines.append(f"- **{s['name']}** — [{s['type']}]({s['url']}). {s['scope']}. Decision: {s['status']}.")
lines += ["", "## Frozen Phase 81 basket","", "| Family | Variants | Risk/use |","|---|---:|---|"]
for f in families: lines.append(f"| {f['family']} | 1 | {f['risk']} |")
lines += ["","Primary paired contrast: 09:20 open to 15:20 open versus 15:20 open to next eligible 09:20 open; derive ATM using prior minute close and keep exact contracts fixed. Do not trade expiry dates or carry contracts into expiry. Require positive prices and nonzero volume at each leg's entry/exit timestamps; no forward filling or synthetic prices.","","## Costs and inference","","Frozen cost model: assumed Paytm Money ₹10 per executed order, statutory/transaction fees per date and one adverse ₹0.05 tick per leg per fill. This is an OHLC reference model, not proof of actual fills due to missing historical bid/ask/depth. Use lagged VIX only. Freeze shortlist from DEV/VAL; keep 2026 holdout sealed until confirmation. Use paired session/expiry-cluster inference, Holm correction, drawdown and tail risk; report all exclusions and the number of tested variants.","","## Core literature","","- Bhat et al. (2024), DOI 10.1002/fut.22512: delta-hedged option-return asymmetry motivates separating clock exposures but is not evidence static spreads will profit. [Wiley/DOI](https://doi.org/10.1002/fut.22512).","- Bailey & López de Prado (2014), Deflated Sharpe Ratio: selection bias grows with the number of tried variants; the full historical trial count is imperfectly enumerated and must remain a limitation. [DOI](https://doi.org/10.3905/jpm.2014.40.5.094).","","## Finite end","","Phase 80: inventory and source audit. Phase 81: registered DEV/VAL temporal sweep. Phase 82: frozen shortlist, inference and holdout confirmation only if data/coverage passes. Phase 83: complete manuscript with figures/tables/appendices and limitations. No rolling parameter search."]
(OUT/"report.md").write_text("\n".join(lines)+"\n")
print(json.dumps({"sources":len(sources),"families":len(families),"phase45_new_structures":20,"phase45_reused_families":22,"decision":"REGISTERED_NEW_HOLDING_WINDOW_AXIS"},indent=2))
if __name__=="__main__": pass
