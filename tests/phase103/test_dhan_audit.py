import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"research"/"phase103_stock_options"))
from dhan_data_audit import check_window, map_underlyings, summarize

class DhanDataAuditTests(unittest.TestCase):
    def test_window_maximum_is_30_days(self):
        self.assertEqual(check_window("2026-08-02","2026-09-01"),30)
        with self.assertRaises(ValueError):
            check_window("2026-08-01","2026-09-01")

    def test_underlying_map_uses_nse_equity_and_eq_series(self):
        import io,csv
        rows=[
          {"SEM_EXM_EXCH_ID":"NSE","SEM_SEGMENT":"E","SEM_SMST_SECURITY_ID":"1333",
           "SEM_INSTRUMENT_NAME":"EQUITY","SEM_TRADING_SYMBOL":"HDFCBANK","SEM_SERIES":"EQ","SEM_LOT_UNITS":"1"},
          {"SEM_EXM_EXCH_ID":"NSE","SEM_SEGMENT":"D","SEM_SMST_SECURITY_ID":"55555",
           "SEM_INSTRUMENT_NAME":"OPTSTK","SEM_TRADING_SYMBOL":"HDFCBANK","SEM_SERIES":"","SEM_LOT_UNITS":"550"}]
        output=io.StringIO(); fields=list(rows[0]); w=csv.DictWriter(output,fieldnames=fields)
        w.writeheader(); w.writerows(rows)
        result=map_underlyings(output.getvalue().encode())
        self.assertEqual(result["HDFCBANK"]["security_id"],"1333")
        self.assertEqual(result["HDFCBANK"]["status"],"MATCHED")

    def test_payload_summary_checks_arrays(self):
        block={"open":[10,11],"high":[11,12],"low":[9,10],"close":[10.5,11.5],
          "iv":[20,21],"volume":[100,120],"strike":[800,800],"oi":[200,220],"spot":[805,806],
          "timestamp":[1754000000,1754000060]}
        result=summarize("HDFCBANK","CALL",200,{"status":"success","data":{"ce":block,"pe":None}})
        self.assertEqual(result["rows"],2)
        self.assertTrue(result["array_lengths_consistent"])
        self.assertEqual(result["status"],"DATA_RETURNED")

    def test_auth_error_maps_to_safe_status(self):
        result=summarize("INFY","PUT",401,None)
        self.assertEqual(result["status"],"AUTH_401")
        self.assertEqual(result["rows"],0)

    def test_requested_side_missing_is_not_reported_as_data(self):
        result=summarize("SBIN","PUT",200,{"status":"success","data":{"ce":{"close":[10],"timestamp":[1754000000]},"pe":None}})
        self.assertEqual(result["rows"],0)
        self.assertNotEqual(result["status"],"DATA_RETURNED")

    def test_summary_does_not_contain_api_secret_or_raw_rows(self):
        # The summarizer only accepts one decoded response and emits counts/timestamps.
        block={"close":[9.0,10.0],"timestamp":[1754000000,1754000060]}
        result=summarize("INFY","CALL",200,{"status":"success","data":{"ce":block}})
        encoded=__import__("json").dumps(result)
        self.assertNotIn("access-token",encoded.lower())
        self.assertNotIn("9.0",encoded)

if __name__=="__main__":
    unittest.main()
