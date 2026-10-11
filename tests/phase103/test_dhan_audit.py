import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"research"/"phase103_stock_options"))
from dhan_data_audit import ALLOWED_STRIKES, CONTRACT_IDENTITY_STATUS, DEFAULT_PANELS, EXPIRY_CODE, check_window, map_underlyings, normalize_strike, parse_panels, parse_strikes, provider_to_date, safe_error_details, summarize, summarize_surface

class DhanDataAuditTests(unittest.TestCase):
    def test_relative_strike_parser_validates_and_preserves_order(self):
        self.assertEqual(parse_strikes("ATM,ATM+1,ATM-1"),["ATM","ATM+1","ATM-1"])
        with self.assertRaises(ValueError): parse_strikes("ATM,ATM")
        with self.assertRaises(ValueError): parse_strikes("ATM+4")
        self.assertEqual(len(ALLOWED_STRIKES),7)
        self.assertEqual(normalize_strike(125.0),"125")

    def test_surface_gate_rejects_duplicate_timestamp_strike_keys(self):
        requested=["ATM","ATM+1","ATM-1"]
        blocks=[
          {"symbol":"HDFCBANK","option_type":"CALL","relative_strike":"ATM","timestamps":[1,2],"strikes":[100,101]},
          {"symbol":"HDFCBANK","option_type":"CALL","relative_strike":"ATM+1","timestamps":[1,2],"strikes":[101,102]},
          {"symbol":"HDFCBANK","option_type":"CALL","relative_strike":"ATM-1","timestamps":[1,2],"strikes":[99,98]}]
        result=summarize_surface(blocks,requested)[0]
        self.assertEqual(result["common_timestamp_count_across_offsets"],2)
        self.assertEqual(result["duplicate_timestamp_actual_strike_keys_across_offsets"],1)
        self.assertEqual(result["relative_surface_alignment_gate"],"FAIL")

    def test_exact_strike_coverage_is_reported_even_when_offset_timestamps_differ(self):
        requested=["ATM","ATM+1","ATM-1"]
        blocks=[
          {"symbol":"SBIN","option_type":"CALL","relative_strike":"ATM","timestamps":[100,160,220],"strikes":[100,100,110]},
          {"symbol":"SBIN","option_type":"CALL","relative_strike":"ATM+1","timestamps":[100,160],"strikes":[110,120]},
          {"symbol":"SBIN","option_type":"CALL","relative_strike":"ATM-1","timestamps":[100,220],"strikes":[90,100]}]
        result=summarize_surface(blocks,requested)[0]
        self.assertEqual(result["relative_surface_alignment_gate"],"FAIL")
        self.assertEqual(result["exact_strike_diagnostic"],"PASS_UNIQUE_TIMESTAMP_STRIKE_KEYS")
        coverage={row["actual_strike"]:row for row in result["actual_strike_coverage"]}
        self.assertEqual(coverage["100"]["observed_minutes"],3)
        self.assertEqual(coverage["110"]["observed_minutes"],2)
        self.assertEqual(coverage["100"]["union_timestamp_coverage_pct"],100.0)

    def test_surface_gate_passes_aligned_distinct_offsets(self):
        requested=["ATM","ATM+1","ATM-1"]
        blocks=[
          {"symbol":"HDFCBANK","option_type":"CALL","relative_strike":"ATM","timestamps":[1,2],"strikes":[100,101]},
          {"symbol":"HDFCBANK","option_type":"CALL","relative_strike":"ATM+1","timestamps":[1,2],"strikes":[102,103]},
          {"symbol":"HDFCBANK","option_type":"CALL","relative_strike":"ATM-1","timestamps":[1,2],"strikes":[98,99]}]
        result=summarize_surface(blocks,requested)[0]
        self.assertEqual(result["relative_surface_alignment_gate"],"PASS")
        self.assertEqual(result["distinct_actual_strikes_in_surface"],6)

    def test_relative_strike_parser_validates_and_preserves_order(self):
        self.assertEqual(parse_strikes("ATM,ATM+1,ATM-1"),["ATM","ATM+1","ATM-1"])
        with self.assertRaises(ValueError): parse_strikes("ATM,ATM")
        with self.assertRaises(ValueError): parse_strikes("ATM+4")
        self.assertEqual(len(ALLOWED_STRIKES),7)
        self.assertEqual(normalize_strike(125.0),"125")

    def test_surface_gate_rejects_duplicate_timestamp_strike_keys(self):
        requested=["ATM","ATM+1","ATM-1"]
        blocks=[
          {"symbol":"HDFCBANK","option_type":"CALL","relative_strike":"ATM","timestamps":[1,2],"strikes":[100,101]},
          {"symbol":"HDFCBANK","option_type":"CALL","relative_strike":"ATM+1","timestamps":[1,2],"strikes":[100,102]},
          {"symbol":"HDFCBANK","option_type":"CALL","relative_strike":"ATM-1","timestamps":[1,2],"strikes":[99,98]}]
        result=summarize_surface(blocks,requested)[0]
        self.assertEqual(result["common_timestamp_count_across_offsets"],2)
        self.assertEqual(result["duplicate_timestamp_actual_strike_keys_across_offsets"],1)
        self.assertEqual(result["relative_surface_alignment_gate"],"FAIL")

    def test_surface_gate_passes_aligned_distinct_offsets(self):
        requested=["ATM","ATM+1","ATM-1"]
        blocks=[
          {"symbol":"HDFCBANK","option_type":"CALL","relative_strike":"ATM","timestamps":[1,2],"strikes":[100,101]},
          {"symbol":"HDFCBANK","option_type":"CALL","relative_strike":"ATM+1","timestamps":[1,2],"strikes":[102,103]},
          {"symbol":"HDFCBANK","option_type":"CALL","relative_strike":"ATM-1","timestamps":[1,2],"strikes":[98,99]}]
        result=summarize_surface(blocks,requested)[0]
        self.assertEqual(result["relative_surface_alignment_gate"],"PASS")
        self.assertEqual(result["distinct_actual_strikes_in_surface"],6)

    def test_selected_panels_are_validated_and_preserve_order(self):
        self.assertEqual(parse_panels("RELIANCE:CALL,RELIANCE:PUT"),
                         [("RELIANCE","CALL"),("RELIANCE","PUT")])
        self.assertEqual(len(DEFAULT_PANELS),4)
        with self.assertRaises(ValueError):
            parse_panels("INFY:CALL,INFY:CALL")
        with self.assertRaises(ValueError):
            parse_panels("NIFTY:CALL")
        with self.assertRaises(ValueError):
            parse_panels("RELIANCE:CE")

    def test_unrecognized_empty_response_is_classified_with_shape_only(self):
        obj={"data":{"ce":None,"pe":{"close":[1,2],"timestamp":[123,456]}}}
        result=summarize("INFY","CALL","ATM+3",200,obj)
        self.assertEqual(result["status"],"REQUESTED_SIDE_PAYLOAD_MISSING")
        envelope=result["response_envelope"]
        self.assertEqual(envelope["requested_side_type"],"null")
        self.assertTrue(envelope["requested_side_key_present"])
        self.assertEqual(envelope["field_shapes"],{})
        self.assertNotIn("123",str(envelope))

    def test_next_expiry_value_matches_dhan_request_sample(self):
        self.assertEqual(EXPIRY_CODE, 1)

    def test_exact_contract_identity_remains_blocked_without_returned_expiry(self):
        self.assertEqual(CONTRACT_IDENTITY_STATUS, "BLOCKED_EXPIRY_NOT_RETURNED")
        # expiryCode=1 is only a request selector; this endpoint response does not supply the actual expiry date.
        self.assertEqual(EXPIRY_CODE, 1)

    def test_window_and_provider_end_date_adapter(self):
        self.assertEqual(check_window("2026-08-02","2026-09-01"),30)
        self.assertEqual(provider_to_date("2026-08-03","2026-08-04"),"2026-08-03")
        self.assertEqual(provider_to_date("2026-08-03","2026-09-02"),"2026-09-01")
        with self.assertRaises(ValueError):
            check_window("2026-08-03","2026-08-03")
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

    def test_summary_counts_rows_by_ist_date_and_flags_out_of_window(self):
        import datetime
        # 2026-08-03 03:45 UTC = 09:15 IST; 2026-08-04 03:45 UTC is next IST session.
        stamps=[
            int(datetime.datetime(2026,8,3,3,45,tzinfo=datetime.timezone.utc).timestamp()),
            int(datetime.datetime(2026,8,4,3,45,tzinfo=datetime.timezone.utc).timestamp())
        ]
        block={"open":[10,11],"high":[11,12],"low":[9,10],"close":[10.5,11.5],
          "iv":[20,21],"volume":[100,120],"strike":[800,800],"oi":[200,220],"spot":[805,806],
          "timestamp":stamps}
        result=summarize("HDFCBANK","CALL","ATM",200,{"status":"success","data":{"ce":block}},
                         None,"2026-08-03","2026-08-04")
        self.assertEqual(result["timestamp_counts_by_ist_date"],{"2026-08-03":1,"2026-08-04":1})
        self.assertEqual(result["outside_requested_date_window_rows"],1)

    def test_payload_summary_checks_arrays(self):
        block={"open":[10,11],"high":[11,12],"low":[9,10],"close":[10.5,11.5],
          "iv":[20,21],"volume":[100,120],"strike":[800,800],"oi":[200,220],"spot":[805,806],
          "timestamp":[1754000000,1754000060]}
        result=summarize("HDFCBANK","CALL","ATM",200,{"status":"success","data":{"ce":block,"pe":None}})
        self.assertEqual(result["rows"],2)
        self.assertTrue(result["array_lengths_consistent"])
        self.assertEqual(result["status"],"DATA_RETURNED")

    def test_http_error_parser_allowlists_message_and_redacts_token(self):
        raw=b'{"errorCode":"DH-905","message":"Invalid request tokenSecret"}'
        result=safe_error_details(raw,"tokenSecret")
        self.assertEqual(result["api_error_code"],"DH-905")
        self.assertIn("[REDACTED]",result["api_error_message"])
        self.assertNotIn("tokenSecret",str(result))

    def test_auth_error_maps_to_safe_status(self):
        result=summarize("INFY","PUT","ATM",401,None)
        self.assertEqual(result["status"],"AUTH_401")
        self.assertEqual(result["rows"],0)

    def test_requested_side_missing_is_not_reported_as_data(self):
        result=summarize("SBIN","PUT","ATM",200,{"status":"success","data":{"ce":{"close":[10],"timestamp":[1754000000]},"pe":None}})
        self.assertEqual(result["rows"],0)
        self.assertEqual(result["status"],"SUCCESS_EMPTY_FOR_REQUESTED_SIDE")
        self.assertNotEqual(result["status"],"DATA_RETURNED")

    def test_summary_does_not_contain_api_secret_or_raw_rows(self):
        # The summarizer only accepts one decoded response and emits counts/timestamps.
        block={"close":[9.0,10.0],"timestamp":[1754000000,1754000060]}
        result=summarize("INFY","CALL","ATM",200,{"status":"success","data":{"ce":block}})
        encoded=__import__("json").dumps(result)
        self.assertNotIn("access-token",encoded.lower())
        self.assertNotIn("9.0",encoded)

class EmptySideContinuationTests(unittest.TestCase):
    def test_success_response_without_requested_side_is_explicit_empty_coverage(self):
        result=summarize("INFY","CALL","ATM+3",200,{"status":"success","data":{"ce":None,"pe":{"close":[1],"timestamp":[1754000000]}}})
        self.assertEqual(result["status"],"SUCCESS_EMPTY_FOR_REQUESTED_SIDE")
        self.assertEqual(result["rows"],0)
        self.assertFalse(result["array_lengths_consistent"])


class ExpiryCrosscheckTests(unittest.TestCase):
    def _nse_zip_for_date(self, day):
        import csv, io, zipfile
        symbols = [("SBIN", "CE", "1040"), ("RELIANCE", "CE", "1300"), ("ICICIBANK", "CE", "1430")]
        fields = ["FinInstrmTp","TckrSymb","XpryDt","FininstrmActlXpryDt","StrkPric","OptnTp",
                  "OpnPric","HghPric","LwPric","ClsPric","TtlTradgVol","OpnIntrst"]
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=fields)
        writer.writeheader()
        for symbol, side, strike in symbols:
            for expiry, prices in [
                ("25-Aug-2026", (10.0, 12.0, 8.0, 11.0)),
                ("29-Sep-2026", (20.0, 21.0, 19.0, 20.0)),
                ("27-Oct-2026", (30.0, 33.0, 29.0, 32.0)),
            ]:
                writer.writerow({
                    "FinInstrmTp":"STO","TckrSymb":symbol,"XpryDt":expiry,"FininstrmActlXpryDt":expiry,
                    "StrkPric":strike,"OptnTp":side,"OpnPric":prices[0],"HghPric":prices[1],
                    "LwPric":prices[2],"ClsPric":prices[3],"TtlTradgVol":385,"OpnIntrst":1000
                })
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("sample.csv", out.getvalue())
        return buffer.getvalue()

    def _profiles(self, prices=(20.0, 21.0, 19.0, 20.0)):
        import datetime
        blocks = []
        for day in ["2026-08-03", "2026-08-04", "2026-08-05"]:
            base = datetime.datetime.fromisoformat(day + "T03:45:00+00:00")
            for symbol, side, strike in [("SBIN","CALL",1040),("RELIANCE","CALL",1300),("ICICIBANK","CALL",1430)]:
                timestamps = [int((base + datetime.timedelta(minutes=i)).timestamp()) for i in range(385)]
                opn, high, low, close = prices
                blocks.append({"symbol":symbol,"option_type":side,"relative_strike":"ATM",
                    "timestamps":timestamps,"strikes":[strike]*385,
                    "bars":{"timestamp":timestamps,"strike":[strike]*385,"open":[opn]*385,
                            "high":[high]*385,"low":[low]*385,"close":[close]*385,
                            "volume":[1]*385,"oi":[1000]*385}})
        return blocks

    def _run(self, prices=(20.0,21.0,19.0,20.0)):
        from expiry_crosscheck import audit_expiry_identity
        payload = self._nse_zip_for_date("2026-08-03")
        def fetch_bytes(url, timeout=30):
            import re
            match = re.search(r"BhavCopy_NSE_FO_0_0_0_(\\d{8})_F_0000", url)
            self.assertIsNotNone(match)
            return payload
        return audit_expiry_identity(self._profiles(prices), fetch_bytes)

    def test_expiry_crosscheck_matches_exact_contract_and_second_future_expiry(self):
        result = self._run()
        self.assertEqual(result["status"], "PASS_EOD_RECONCILED_EXPIRY_CODE_1")
        self.assertEqual(result["eligible_full_session_profiles"], 9)
        self.assertEqual(result["unique_exact_contract_matches"], 9)
        self.assertEqual(result["expiry_code_matches"], 9)
        self.assertEqual(result["expiry_selector_mismatches"], 0)
        self.assertFalse(result["raw_rows_persisted"])
        self.assertEqual(result["matched_expiry_counts"], {"2026-09-29": 9})

    def test_expiry_crosscheck_blocks_when_minute_ohlc_does_not_match_eod(self):
        result = self._run((99.0,100.0,98.0,99.0))
        self.assertEqual(result["status"], "BLOCKED_EOD_EXPIRY_RECONCILIATION_INSUFFICIENT")
        self.assertEqual(result["unique_exact_contract_matches"], 0)
        self.assertEqual(result["unmatched_profile_count"], 9)

if __name__=="__main__":
    unittest.main()
