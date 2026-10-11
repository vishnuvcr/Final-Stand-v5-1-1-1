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
          ["2024-07-08","OPTIDX","NIFTY","2024-07-25","24000","CE","10","12","9","11","1000","50","25"],
          ["2024-07-08","OPTIDX","NIFTY","2024-07-25","24000","PE","9","10","8","8","800","30","25"],
          ["2024-07-08","FUTIDX","NIFTY","2024-07-25","0","XX","24000","24100","23900","24050","5000","100","25"],
          ["2024-07-08","OPTIDX","RELIANCE","2024-07-25","3000","CE","20","22","19","21","800","20","250"],
        ]
        payload=zipped_csv(fields,rows,"udiff.csv")
        result=nse_backfill.read_archive(payload,date(2024,7,8))
        self.assertEqual(result["schema"],"UDiFF")
        self.assertEqual(result["selected_index_option_rows"],2)
        self.assertEqual(result["identity_complete_rows"],2)
        self.assertEqual(result["positive_volume_rows"],2)
        self.assertEqual(result["invalid_ohlc_positive_volume_rows"],0)
        self.assertEqual(result["duplicate_daily_contract_keys"],0)

    def test_duplicate_daily_contract_key_is_counted(self):
        fields=["BizDt","FinInstrmTp","TckrSymb","FininstrmActlXpryDt","StrkPric","OptnTp",
                "OpnPric","HghPric","LwPric","ClsPric","OpnIntrst","TtlTradgVol","NewBrdLotQty"]
        row=["2024-07-08","OPTIDX","NIFTY","2024-07-25","24000","CE","10","12","9","11","1000","50","25"]
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
            self.assertLessEqual((left[1]-left[0]).days,363)

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


if __name__=="__main__":
    unittest.main()
