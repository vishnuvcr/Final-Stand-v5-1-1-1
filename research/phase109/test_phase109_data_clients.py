"""Network-free regression tests for Phase 109 source parsing and manifest dates."""
import csv
import io
import sys
import unittest
import zipfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nse_backfill
import niftyindices_history
import dhan_rolling_options
import futures_eod_extract
import options_greeks_extract
import strategy_evaluator
import family_grid
import selection_audit
import tempfile


def zipped_csv(headers, rows, filename="sample.csv"):
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
        text=io.StringIO()
        w=csv.writer(text)
        w.writerow(headers)
        w.writerows(rows)
        z.writestr(filename,text.getvalue())
    return buf.getvalue()


class TestNseBackfill(unittest.TestCase):
    def test_schema_boundary_urls(self):
        self.assertIn("/historical/DERIVATIVES/2024/JUL/", nse_backfill.get_url(date(2024,7,5))[0])
        self.assertIn("BhavCopy_NSE_FO_0_0_0_20240708", nse_backfill.get_url(date(2024,7,8))[0])

    def test_date_formats(self):
        self.assertEqual(nse_backfill.parse_date("05-JUL-2024"),"2024-07-05")
        self.assertEqual(nse_backfill.parse_date("2024-07-08"),"2024-07-08")
        self.assertIsNone(nse_backfill.parse_date("not-a-date"))

    def test_weekday_generator_excludes_weekends(self):
        dates=list(nse_backfill.expected_weekdays(date(2024,7,5),date(2024,7,10)))
        self.assertEqual([d.isoformat() for d in dates],["2024-07-05","2024-07-08","2024-07-09"])

    def test_udiff_contract_filter_and_integrity_metrics(self):
        fields=["BizDt","FinInstrmTp","TckrSymb","FininstrmActlXpryDt","StrkPric","OptnTp",
                "OpnPric","HghPric","LwPric","ClsPric","OpnIntrst","TtlTradgVol","NewBrdLotQty"]
        rows=[
          ["2024-07-08","IDO","NIFTY","2024-07-25","24000","CE","10","12","9","11","1000","50","25"],
          ["2024-07-08","IDO","NIFTY","2024-07-25","24000","PE","9","10","8","8","800","30","25"],
          ["2024-07-08","IDF","NIFTY","2024-07-25","0","XX","24000","24100","23900","24050","5000","100","25"],
          ["2024-07-08","STO","RELIANCE","2024-07-25","3000","CE","20","22","19","21","800","20","250"],
        ]
        payload=zipped_csv(fields,rows,"udiff.csv")
        result=nse_backfill.read_archive(payload,date(2024,7,8))
        self.assertEqual(result["schema"],"UDiFF")
        self.assertEqual(result["selected_index_option_rows"],2)
        self.assertEqual(result["identity_complete_rows"],2)
        self.assertEqual(result["positive_volume_rows"],2)
        self.assertEqual(result["invalid_ohlc_positive_volume_rows"],0)
        self.assertEqual(result["duplicate_daily_contract_keys"],0)
        self.assertEqual(result["missing_lot_size_rows"],0)

    def test_duplicate_daily_contract_key_is_counted(self):
        fields=["BizDt","FinInstrmTp","TckrSymb","FininstrmActlXpryDt","StrkPric","OptnTp",
                "OpnPric","HghPric","LwPric","ClsPric","OpnIntrst","TtlTradgVol","NewBrdLotQty"]
        row=["2024-07-08","IDO","NIFTY","2024-07-25","24000","CE","10","12","9","11","1000","50","25"]
        payload=zipped_csv(fields,[row,row],"dup.csv")
        result=nse_backfill.read_archive(payload,date(2024,7,8))
        self.assertEqual(result["selected_index_option_rows"],2)
        self.assertEqual(result["duplicate_daily_contract_keys"],1)


class TestNiftyIndicesHistory(unittest.TestCase):
    def test_api_chunk_boundaries_cover_requested_days_once(self):
        start=date(2023,10,1); end=date(2026,10,9)
        chunks=list(niftyindices_history.intervals(start,end))
        self.assertGreater(len(chunks),1)
        self.assertEqual(chunks[0][0],start)
        self.assertEqual(chunks[-1][1]+niftyindices_history.timedelta(days=1),end)
        for left,right in zip(chunks,chunks[1:]):
            self.assertEqual(left[1]+niftyindices_history.timedelta(days=1),right[0])
            self.assertLessEqual((left[1]-left[0]).days,59)

    def test_minimum_expected_observation_gate_rejects_short_api_responses(self):
        start=date(2023,10,1); end=date(2026,10,9)
        minimum=niftyindices_history.minimum_expected_observations(start,end)
        self.assertGreater(minimum,218)
        self.assertGreaterEqual(
            minimum,
            int(niftyindices_history.expected_weekdays(start,end)*0.90),
        )

    def test_index_date_parsing(self):
        self.assertEqual(niftyindices_history.parse_d("01 Jan 2024"),"2024-01-01")
        self.assertEqual(niftyindices_history.parse_d("2024-01-01"),"2024-01-01")
        self.assertIsNone(niftyindices_history.parse_d("bad"))

    def test_rows_audit_flags_missing_ohlc(self):
        rows=[{"date":"01 Jan 2024","open":"13.1","high":"14.0","low":"12.4","close":"13.7"},
              {"date":"02 Jan 2024","open":"12.0","high":"","low":"11.5","close":"11.7"}]
        result=niftyindices_history.rows_audit("INDIA_VIX",rows,"abc",date(2024,1,1),date(2024,1,3))
        self.assertEqual(result["row_count"],2)
        self.assertEqual(result["rows_with_missing_OHLC"],1)
        self.assertEqual(result["invalid_OHLC_rows"],0)

class TestDhanRollingOptions(unittest.TestCase):
    def test_chunk_windows_are_disjoint_and_at_most_30_days_inclusive(self):
        start=date(2024,10,1); end=date(2025,1,1)
        windows=list(dhan_rolling_options.chunks(start,end))
        self.assertEqual(windows[0][0],start)
        self.assertEqual(windows[-1][1]+dhan_rolling_options.timedelta(days=1),end)
        for left,right in windows:
            self.assertLessEqual((right-left).days,29)
        for first,second in zip(windows,windows[1:]):
            self.assertEqual(first[1]+dhan_rolling_options.timedelta(days=1),second[0])

    def test_dhan_rolling_series_quality_and_strike_changes(self):
        rows=[
          {"timestamp":"2024-10-01 09:15:00","strike":25000,"open":100,"high":105,"low":95,"close":101,"iv":18.2,"volume":25,"oi":1000,"spot":25010},
          {"timestamp":"2024-10-01 09:20:00","strike":25000,"open":101,"high":108,"low":98,"close":104,"iv":18.4,"volume":30,"oi":1100,"spot":25025},
          {"timestamp":"2024-10-01 09:25:00","strike":25050,"open":104,"high":109,"low":100,"close":106,"iv":18.1,"volume":35,"oi":1200,"spot":25048},
        ]
        result=dhan_rolling_options.audit_rows(rows)
        self.assertEqual(result["rows"],3)
        self.assertEqual(result["unique_observed_dates"],1)
        self.assertEqual(result["positive_unique_strikes"],2)
        self.assertEqual(result["strike_transition_count"],1)
        self.assertEqual(result["invalid_ohlc_rows"],0)
        self.assertEqual(result["invalid_or_missing_iv_rows"],0)
        self.assertEqual(result["invalid_or_missing_volume_rows"],0)

class TestPhase109ManifestAndSelection(unittest.TestCase):
    def test_evaluator_normalizes_udiff_index_options(self):
        fields=["BizDt","FinInstrmTp","TckrSymb","FininstrmActlXpryDt","StrkPric","OptnTp",
                "OpnPric","HghPric","LwPric","ClsPric","OpnIntrst","TtlTradgVol","NewBrdLotQty","UndrlygPric"]
        row=["2024-10-01","IDO","NIFTY","2024-10-31","25000","CE","100","110","90","105","1000","50","25","25010"]
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"sample.zip"
            path.write_bytes(zipped_csv(fields,[row],"udiff.csv"))
            parsed=strategy_evaluator.read_archive(path,date(2024,10,1))
        self.assertEqual(len(parsed),1)
        self.assertEqual(parsed[0]["instrument"],"OPTIDX")
        self.assertEqual(parsed[0]["lot"],25)

    def test_base_family_has_1080_unique_applicable_configs(self):
        axes=family_grid.axes_for_family({"regime_id":"NONE","confirmation_id":"NONE"})
        count=1
        for values in axes.values(): count*=len(values)
        self.assertEqual(count,1080)
        self.assertNotIn("vol_lookback_sessions",axes)
        self.assertNotIn("regime_definition",axes)
        self.assertNotIn("oi_confirmation_method",axes)

    def test_regime_and_oi_axes_are_only_attached_when_applicable(self):
        vol=family_grid.axes_for_family({"regime_id":"REALIZED_VOL_LOW_HIGH","confirmation_id":"NONE"})
        flow=family_grid.axes_for_family({"regime_id":"NONE","confirmation_id":"OPTIONS_FLOW"})
        self.assertIn("vol_lookback_sessions",vol)
        self.assertIn("regime_definition",vol)
        self.assertIn("oi_confirmation_method",flow)
        self.assertNotIn("vol_lookback_sessions",flow)

    def test_holm_adjustment_is_monotonic_and_keyed_to_test_identity(self):
        adjusted, rejected, count=selection_audit.holm([(("a",),0.01),(("b",),0.04),(("c",),0.03)])
        self.assertEqual(count,3)
        self.assertAlmostEqual(adjusted[("a",)],0.03)
        self.assertAlmostEqual(adjusted[("c",)],0.06)
        self.assertAlmostEqual(adjusted[("b",)],0.06)

    def test_exact_24_cost_scenarios_are_required(self):
        import csv, itertools
        old_out=str(strategy_evaluator.OUT)
        with tempfile.TemporaryDirectory() as td:
            strategy_evaluator.OUT=Path(td)
            path=Path(td)/"cost_scenarios.csv"
            with path.open("w",newline="",encoding="utf-8") as fh:
                w=csv.DictWriter(fh,fieldnames=["cost_case_id","brokerage_per_order","slippage_per_unit_per_side","fee_multiplier"])
                w.writeheader()
                for b,s,m in itertools.product((10,15,20),(0,0.05,0.25,0.50),(1,1.5)):
                    w.writerow({"cost_case_id":f"{b}-{s}-{m}","brokerage_per_order":b,"slippage_per_unit_per_side":s,"fee_multiplier":m})
            result=strategy_evaluator.load_cost_cases()
            self.assertEqual(len(result),24)
            self.assertEqual(len({(x["brokerage_per_order"],x["slippage_per_unit_per_side"],x["fee_multiplier"]) for x in result}),24)
        strategy_evaluator.OUT=Path(old_out)


class TestStrategyEvaluator(unittest.TestCase):
    def test_momentum_signal_is_lagged_and_thresholded(self):
        rising=[100.0,100.1,100.2,100.8,101.0,102.0]
        self.assertEqual(strategy_evaluator.compute_signal("ROC_MOMENTUM",rising,5,3,0.5),1)
        falling=[102.0,101.9,101.5,101.0,100.5,100.0]
        self.assertEqual(strategy_evaluator.compute_signal("ROC_MOMENTUM",falling,5,3,0.5),-1)
        flat=[100.0]*10
        self.assertEqual(strategy_evaluator.compute_signal("ROC_MOMENTUM",flat,9,3,0.5),0)

    def test_cost_model_adapter_exposes_canonical_fee_calculation(self):
        model=strategy_evaluator.load_cost_model()
        name,fn=strategy_evaluator.find_cost_function(model)
        self.assertIsNotNone(name)
        self.assertTrue(callable(fn))
        fee,detail=strategy_evaluator.call_cost_model(
            model,date(2024,10,1),100.0,105.0,25,20.0,1.0
        )
        self.assertGreaterEqual(fee,0.0)
        self.assertIn("model_callable",detail)


class TestPhase109CostSchedule(unittest.TestCase):
    def test_paytm_money_order_brokerage_and_2026_nse_rates(self):
        model = strategy_evaluator.load_cost_model()
        self.assertAlmostEqual(model.exchange_transaction_rate(date(2026, 2, 28)), 0.0003503)
        self.assertAlmostEqual(model.exchange_transaction_rate(date(2026, 3, 1)), 0.0003552)
        self.assertAlmostEqual(model.STT_SELL_RATE_BEFORE_2026_04_01, 0.0010)
        self.assertAlmostEqual(model.STT_SELL_RATE_FROM_2026_04_01, 0.0015)
        result = model.round_trip_cost(
            buy_premium=100.0,
            sell_premium=110.0,
            quantity=25,
            trade_date=date(2026, 4, 1),
            brokerage_per_order=10.0,
        )
        self.assertEqual(result["brokerage"], 20.0)
        self.assertAlmostEqual(result["stt_sell_rate"], 0.0015)
        self.assertAlmostEqual(result["exchange_rate_per_side"], 0.0003552)


class TestModelGreeks(unittest.TestCase):
    def test_black_scholes_implied_volatility_round_trip(self):
        premium=options_greeks_extract.bs_price(25000,25000,30/365,0.065,0.2,"CE")
        iv,status=options_greeks_extract.implied_vol(premium,25000,25000,30/365,0.065,"CE")
        self.assertEqual(status,"OK")
        self.assertAlmostEqual(iv,0.2,places=5)
        metrics=options_greeks_extract.greeks(25000,25000,30/365,0.065,iv,"CE")
        self.assertTrue(all(abs(v)<1e6 for v in metrics.values()))
        self.assertGreater(metrics["delta"],0)
        self.assertGreater(metrics["gamma"],0)

    def test_contract_price_below_model_bound_is_not_forced_to_iv(self):
        iv,status=options_greeks_extract.implied_vol(1,25000,20000,5/365,0.065,"CE")
        self.assertIsNone(iv)
        self.assertEqual(status,"PREMIUM_BELOW_MODEL_LOWER_BOUND")


class TestIndexFuturesExtractor(unittest.TestCase):
    def test_extract_udiff_futures_and_ignore_options(self):
        headers=["BizDt","FinInstrmTp","TckrSymb","FininstrmActlXpryDt","OpnPric","HghPric","LwPric","ClsPric",
                 "TtlTradgVol","OpnIntrst","NewBrdLotQty","UndrlygPric"]
        rows=[
          ["2024-10-01","IDF","NIFTY","2024-10-31","25000","25100","24950","25080","100000","500000","25","25010"],
          ["2024-10-01","IDO","NIFTY","2024-10-10","100","125","90","110","12000","80000","25","25010"],
        ]
        payload=zipped_csv(headers,rows,"future.csv")
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"20241001.zip"; p.write_bytes(payload)
            summary,extracted=futures_eod_extract.extract_zip(p,"2024-10-01")
        self.assertEqual(summary["schema"],"UDiFF")
        self.assertEqual(summary["selected_futures_rows"],1)
        self.assertEqual(extracted[0]["symbol"],"NIFTY")
        self.assertEqual(extracted[0]["expiry"],"2024-10-31")
        self.assertEqual(extracted[0]["lot_size"],25)
        self.assertEqual(extracted[0]["close"],25080.0)
        self.assertEqual(summary["invalid_ohlc_positive_volume_rows"],0)



if __name__=="__main__":
    unittest.main()
