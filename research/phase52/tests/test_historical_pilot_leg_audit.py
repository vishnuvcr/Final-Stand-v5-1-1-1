import importlib.util
import json
import unittest
from pathlib import Path

RUNNER = Path(__file__).resolve().parents[1] / "historical_pilot_runner.py"
spec = importlib.util.spec_from_file_location("phase55_runner", RUNNER)
runner = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(runner)

class LegAuditPayloadTests(unittest.TestCase):
    def test_skeleton_contains_every_selected_leg_before_gates(self):
        legs = [
            {"leg_id":"L1","side":"SELL","option_type":"CE","strike":22000,"expiry":"2025-03-13","quantity_lots":1},
            {"leg_id":"L2","side":"BUY","option_type":"CE","strike":22100,"expiry":"2025-03-13","quantity_lots":1},
        ]
        rows = runner.initial_leg_audit_rows(legs, 75)
        self.assertEqual([x["leg_id"] for x in rows], ["L1", "L2"])
        self.assertTrue(all(x["entry_status"] == "NOT_TESTED" for x in rows))
        self.assertTrue(all(x["prior_oi_status"] == "NOT_TESTED" for x in rows))
        self.assertTrue(all(x["range_proxy_status"] == "NOT_TESTED" for x in rows))
        self.assertTrue(all(x["exit_status"] == "NOT_TESTED" for x in rows))

    def test_event_record_preserves_all_leg_payloads(self):
        event = {"split":"development","event_id":"e1","expiry":"2025-03-13","entry_ts":"2025-03-13T09:45:00+05:30"}
        conf = {
            "grid_version":"phase52-grid-v1.3","configuration_id":"cfg1","candidate_id":"PH52-043",
            "family_id":"BEAR_CALL_SPREAD","selector_mode":"BASELINE",
            "configuration":{"entry_time_ist":"09:45","entry_dte_calendar_days":0},
            "canonical_configuration_json":"{}",
        }
        legs = runner.initial_leg_audit_rows([
            {"leg_id":"L1","side":"SELL","option_type":"CE","strike":22000,"expiry":"2025-03-13","quantity_lots":1},
            {"leg_id":"L2","side":"BUY","option_type":"CE","strike":22100,"expiry":"2025-03-13","quantity_lots":1},
        ], 75)
        row = runner.event_record(event, conf, "EXCLUDED_OHLC_RANGE_PROXY", "L1 range failed",
                                  22000, 75, legs, "hash", "2025-03-13T15:15:00+05:30")
        parsed = json.loads(row["resolved_legs_json"])
        self.assertEqual(len(parsed), 2)
        self.assertEqual({x["leg_id"] for x in parsed}, {"L1","L2"})
        self.assertFalse(row["promotable"])

if __name__ == "__main__":
    unittest.main()
