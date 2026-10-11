import io
import zipfile
import unittest
from datetime import date

from research.phase108_eod_ohlc_strategy_pilot import (
    bootstrap_mean_daily_ci, oi_increased, parse_strategy_archive, select_contract,
    signal_side, simulate_trade, valid_ohlc,
)


def row(trade_date="2026-08-03", expiry="2026-08-20", strike=100.0, side="CE",
        volume=50.0, oi=100.0, underlying=101.0, lot_size=25.0,
        open_=5.0, high=6.0, low=4.5, close=5.5):
    return {
        "trade_date": trade_date, "symbol": "INFY", "expiry": expiry, "strike": strike,
        "option_type": side, "identity_complete": True, "prices_complete": True,
        "volume": volume, "oi": oi, "underlying": underlying, "lot_size": lot_size,
        "open": open_, "high": high, "low": low, "close": close,
    }


class Phase108PilotTests(unittest.TestCase):
    def test_signal_direction_is_frozen_and_zero_skips(self):
        self.assertEqual(signal_side("MOMENTUM_ATM", 0.01), "CE")
        self.assertEqual(signal_side("MOMENTUM_ATM", -0.01), "PE")
        self.assertEqual(signal_side("REVERSAL_ATM", 0.01), "PE")
        self.assertEqual(signal_side("REVERSAL_ATM", -0.01), "CE")
        self.assertEqual(signal_side("MOMENTUM_OI_CONFIRM", 0.01), "CE")
        self.assertIsNone(signal_side("MOMENTUM_ATM", 0.0))
        self.assertEqual(signal_side("LOW_VOL_MOMENTUM", 0.01, "LOW"), "CE")
        self.assertIsNone(signal_side("LOW_VOL_MOMENTUM", 0.01, "HIGH"))
        self.assertEqual(signal_side("HIGH_VOL_REVERSAL", 0.01, "HIGH"), "PE")
        self.assertIsNone(signal_side("HIGH_VOL_REVERSAL", 0.01, "LOW"))
        self.assertEqual(signal_side("LARGE_MOVE_MOMENTUM", 0.006), "CE")
        self.assertIsNone(signal_side("LARGE_MOVE_MOMENTUM", 0.004))
        self.assertEqual(signal_side("SMALL_MOVE_REVERSAL", 0.004), "PE")
        self.assertIsNone(signal_side("SMALL_MOVE_REVERSAL", 0.006))
        self.assertEqual(signal_side("LARGE_MOVE_REVERSAL", -0.006), "CE")
        self.assertIsNone(signal_side("LARGE_MOVE_REVERSAL", -0.004))

    def test_selector_uses_earliest_eligible_expiry_then_nearest_strike(self):
        rows = [
            row(expiry="2026-08-27", strike=101),
            row(expiry="2026-08-20", strike=105),
            row(expiry="2026-08-20", strike=100),
            row(expiry="2026-08-20", strike=100, oi=200, volume=20),
        ]
        selected = select_contract(rows, "2026-08-03", "CE", 101.0)
        self.assertEqual(selected["expiry"], "2026-08-20")
        self.assertEqual(selected["strike"], 100)
        self.assertEqual(selected["oi"], 200)

    def test_selector_rejects_near_expiry_zero_volume_and_invalid_prices(self):
        rows = [
            row(expiry="2026-08-05", strike=100),
            row(expiry="2026-08-20", strike=100, volume=0),
            row(expiry="2026-08-20", strike=101, open_=0),
        ]
        self.assertIsNone(select_contract(rows, "2026-08-03", "CE", 101.0))

    def test_oi_confirmation_requires_same_side_same_expiry_near_atm_increase(self):
        current = [row(oi=150), row(strike=110, oi=500)]
        prior = [row(trade_date="2026-07-31", oi=100), row(strike=110, oi=500)]
        self.assertTrue(oi_increased(current, prior, "CE", "2026-08-20", 101.0))
        self.assertFalse(oi_increased(prior, current, "CE", "2026-08-20", 101.0))
        self.assertFalse(oi_increased(current, prior, "PE", "2026-08-20", 101.0))

    def test_ohlc_invariants(self):
        self.assertTrue(valid_ohlc(row()))
        self.assertFalse(valid_ohlc(row(open_=0)))
        self.assertFalse(valid_ohlc(row(high=4.0)))
        self.assertFalse(valid_ohlc(row(low=5.6)))

    def test_net_accounting_reconciles_and_adverse_slippage_lowers_pnl(self):
        trade = {"entry_date": "2026-08-03", "symbol": "INFY", "open": 10.0, "close": 11.0, "lot_size": 25}
        ideal = simulate_trade(trade, 20.0, 0.0, 1.0)
        stressed = simulate_trade(trade, 20.0, 0.5, 1.5)
        self.assertGreater(ideal["net_pnl_rupees"], stressed["net_pnl_rupees"])
        expected = (trade["close"] - trade["open"]) * trade["lot_size"]
        self.assertAlmostEqual(
            expected - stressed["slippage_cost_rupees"] - stressed["fees_rupees"],
            stressed["net_pnl_rupees"], places=2
        )

    def test_bootstrap_is_deterministic_and_includes_session_clusters(self):
        vals = [100, -50, 20, -10, 40]
        a = bootstrap_mean_daily_ci(vals, seed=105, draws=100)
        b = bootstrap_mean_daily_ci(vals, seed=105, draws=100)
        self.assertEqual(a, b)
        self.assertEqual(a["n_sessions"], 5)
        self.assertLessEqual(a["ci95_low_rupees"], a["ci95_high_rupees"])

    def test_archive_parser_keeps_price_fields_in_memory_and_counts_mismatches(self):
        header = [
            "FinInstrmTp", "TckrSymb", "BizDt", "FininstrmActlXpryDt", "XpryDt",
            "StrkPric", "OptnTp", "OpnPric", "HghPric", "LwPric", "ClsPric",
            "TtlTradgVol", "OpnIntrst", "UndrlygPric", "NewBrdLotQty"
        ]
        line = ["OPTSTK", "INFY", "2026-08-03", "2026-08-20", "2026-08-20",
                "100", "CE", "5", "6", "4.5", "5.5", "50", "100", "101", "25"]
        payload = io.StringIO()
        payload.write(",".join(header) + "\n" + ",".join(line) + "\n")
        data = io.BytesIO()
        with zipfile.ZipFile(data, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("test.csv", payload.getvalue())
        parsed = parse_strategy_archive(data.getvalue(), "2026-08-03")
        self.assertEqual(parsed["selected_count"], 1)
        self.assertEqual(parsed["date_mismatch_count"], 0)
        self.assertEqual(parsed["rows"][0]["open"], 5.0)
        self.assertEqual(parsed["rows"][0]["close"], 5.5)
        self.assertTrue(parsed["rows"][0]["identity_complete"])
        self.assertTrue(parsed["rows"][0]["prices_complete"])


if __name__ == "__main__":
    unittest.main()
