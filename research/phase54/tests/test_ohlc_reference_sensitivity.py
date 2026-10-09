import importlib.util
import json
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "ohlc_reference_sensitivity.py"
spec = importlib.util.spec_from_file_location("phase54_sensitivity", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

class Phase54Tests(unittest.TestCase):
    def test_threshold_only_changes_range_gate_and_not_prior_oi(self):
        rows = [
            {"configuration_id":"a","event_id":"e","status":"EXCLUDED_OHLC_RANGE_PROXY","split":"development",
             "family_id":"BUY_CALL","resolved_legs_json":json.dumps([
                 {"prior_oi_status":"PASS","prior_oi":500,"entry_status":"PASS","entry_range_proxy_pct":5.5}])},
            {"configuration_id":"b","event_id":"e","status":"BLOCKED_LEG_ELIGIBILITY","split":"development",
             "family_id":"BUY_PUT","resolved_legs_json":json.dumps([
                 {"prior_oi_status":"FAIL","prior_oi":0,"entry_status":"PASS","entry_range_proxy_pct":1.0}])},
        ]
        out = mod.analyze(rows)
        self.assertEqual(out["threshold_sensitivity"][0]["rows_meeting_prior_oi_entry_data_and_range_gate"], 0)
        at_six = next(x for x in out["threshold_sensitivity"] if x["threshold_pct"] == 6)
        self.assertEqual(at_six["rows_meeting_prior_oi_entry_data_and_range_gate"], 1)
        self.assertEqual(at_six["rejected_for_prior_oi"], 1)
        self.assertFalse(out["frozen_rules"]["historical_pnl_recalculated"])
        self.assertFalse(out["frozen_rules"]["live_execution_or_promotion_allowed"])

    def test_empty_or_bad_schema_is_rejected(self):
        with self.assertRaises(ValueError):
            mod.analyze([])
        with self.assertRaises(ValueError):
            mod.analyze([{"status":"PASS"}])

if __name__ == "__main__":
    unittest.main()

# Trigger validation after workflow persistence fix; test logic unchanged.
