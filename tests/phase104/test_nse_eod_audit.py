import csv
import io
import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "phase104_eod_stock_options"))
from nse_eod_audit import check_window, parse_nse_archive, summarize_rows


class NseEodAuditTests(unittest.TestCase):
    def make_zip(self, rows, fields=None):
        import csv, io, zipfile
        fields = fields or [
            "BizDt", "FinInstrmTp", "TckrSymb", "XpryDt", "FininstrmActlXpryDt",
            "StrkPric", "OptnTp", "OpnPric", "HghPric", "LwPric", "ClsPric",
            "TtlTradgVol", "OpnIntrst", "UndrlygPric", "NewBrdLotQty"
        ]
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        zipped = io.BytesIO()
        with zipfile.ZipFile(zipped, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("daily.csv", buf.getvalue())
        return zipped.getvalue()

    def row(self, symbol="SBIN", instrument="STO", side="CE", expiry="25-Aug-2026", strike="1040", volume="100"):
        return {
            "BizDt":"2026-08-03", "FinInstrmTp":instrument, "TckrSymb":symbol,
            "XpryDt":expiry, "FininstrmActlXpryDt":expiry, "StrkPric":strike,
            "OptnTp":side, "OpnPric":"10.0", "HghPric":"11.0", "LwPric":"9.5",
            "ClsPric":"10.5", "TtlTradgVol":volume, "OpnIntrst":"1000",
            "UndrlygPric":"1045.0", "NewBrdLotQty":"150"
        }

    def test_window_is_bounded_and_end_exclusive(self):
        self.assertEqual(check_window("2026-08-03", "2026-09-02"), 30)
        with self.assertRaises(ValueError):
            check_window("2026-08-03", "2026-09-03")
        with self.assertRaises(ValueError):
            check_window("2026-08-03", "2026-08-03")

    def test_parser_keeps_exact_contract_identity_and_filters_other_instruments(self):
        rows = [
            self.row("SBIN"),
            self.row("RELIANCE", side="PE", strike="1300"),
            self.row("NIFTY", side="CE", strike="25000"),
            self.row("INFY", instrument="FST", side="CE", strike="1500"),
        ]
        parsed = parse_nse_archive(self.make_zip(rows), "2026-08-03")
        self.assertEqual(parsed["selected_rows"], 2)
        self.assertEqual(len(parsed["rows"]), 2)
        self.assertTrue(all(row["identity_complete"] for row in parsed["rows"]))
        self.assertEqual({row["symbol"] for row in parsed["rows"]}, {"SBIN", "RELIANCE"})
        self.assertEqual({row["option_type"] for row in parsed["rows"]}, {"CE", "PE"})

    def test_parser_flags_wrong_trade_date_and_incomplete_identity(self):
        rows = [self.row()]
        rows[0]["BizDt"] = "2026-08-04"
        rows[0]["StrkPric"] = ""
        parsed = parse_nse_archive(self.make_zip(rows), "2026-08-03")
        self.assertEqual(parsed["date_mismatch_rows"], 1)
        self.assertFalse(parsed["rows"][0]["identity_complete"])

    def test_duplicate_daily_contract_identity_is_counted(self):
        rows = [self.row(), self.row()]
        parsed = parse_nse_archive(self.make_zip(rows), "2026-08-03")
        summary = summarize_rows(parsed["rows"], parsed["selected_rows"], parsed["date_mismatch_rows"])
        self.assertEqual(summary["parsed_rows"], 2)
        self.assertEqual(summary["unique_contract_keys"], 1)
        self.assertEqual(summary["duplicate_daily_contract_keys"], 1)

    def test_zero_volume_is_distinct_from_missing_volume(self):
        rows = [self.row(volume="0"), self.row(strike="1050", volume="")]
        parsed = parse_nse_archive(self.make_zip(rows), "2026-08-03")
        summary = summarize_rows(parsed["rows"])
        self.assertEqual(summary["zero_volume_rows"], 1)
        self.assertEqual(summary["missing_volume_rows"], 1)
        self.assertEqual(summary["positive_volume_rows"], 0)

    def test_aggregate_summary_does_not_publish_price_values(self):
        parsed = parse_nse_archive(self.make_zip([self.row()]), "2026-08-03")
        summary = summarize_rows(parsed["rows"])
        encoded = __import__("json").dumps(summary)
        self.assertNotIn('"10.5"', encoded)
        self.assertNotIn('"1040"', encoded)
        self.assertNotIn('"1045', encoded)
        self.assertNotIn("OpnPric", encoded)


if __name__ == "__main__":
    unittest.main()
