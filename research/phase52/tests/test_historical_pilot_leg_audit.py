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

    def test_validator_fails_closed_on_dropped_leg(self):
        row = {
            "configuration_id":"cfg", "event_id":"e", "family_id":"BEAR_CALL_SPREAD",
            "status":"EXCLUDED_OHLC_RANGE_PROXY",
            "resolved_legs_json":json.dumps([{"leg_id":"L1"}]),
        }
        with self.assertRaises(RuntimeError):
            runner.validate_leg_audit_payloads([row])

    def test_validator_accepts_complete_spread_leg_ids(self):
        row = {
            "configuration_id":"cfg", "event_id":"e", "family_id":"BEAR_CALL_SPREAD",
            "status":"EXCLUDED_OHLC_RANGE_PROXY",
            "resolved_legs_json":json.dumps([{"leg_id":"L1"},{"leg_id":"L2"}]),
        }
        runner.validate_leg_audit_payloads([row])

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


    def test_prior_oi_block_records_every_selected_leg(self):
        entry, prior, event, expiries = runner.resolver.synthetic_fixture()
        specs = runner.resolver.load_csv(runner.resolver.SPECS_PATH)
        manifest = runner.resolver.load_source_manifest()
        config = {
            "strike_selection": "ATM_OFFSET",
            "atm_offset_steps": 2,
            "wing_width_steps": 3,
            "reference_lots_per_leg": 1,
            "exit_rule": "15:15_IST",
            "hedge_mode": "NONE",
            "liquidity_max_spread_pct": 2.0,
            "expiry_pairing": "WEEKLY_WEEKLY",
        }
        baseline = runner.resolver.resolve_template(
            "BEAR_CALL_SPREAD", config, event, entry, prior, expiries, specs, manifest
        )
        self.assertEqual(baseline["status"], "TEMPLATE_RESOLVED_ENTRY_GATES_PASS")
        self.assertEqual(len(baseline["legs"]), 2)

        first = baseline["legs"][0]
        failed_prior = prior.copy()
        times = runner.resolver.pd.to_datetime(failed_prior["timestamp"], errors="coerce")
        mask = (
            times.eq(runner.resolver.as_ist(event["entry_ts"]) - runner.resolver.pd.Timedelta(minutes=1))
            & failed_prior["expiry"].astype(str).eq(first["expiry"])
            & failed_prior["option_type"].astype(str).str.upper().eq(first["option_type"])
            & runner.resolver.pd.to_numeric(failed_prior["strike"], errors="coerce").eq(float(first["strike"]))
        )
        self.assertEqual(int(mask.sum()), 1)
        failed_prior.loc[mask, "open_interest"] = 50.0

        blocked = runner.resolver.resolve_template(
            "BEAR_CALL_SPREAD", config, event, entry, failed_prior, expiries, specs, manifest
        )
        self.assertEqual(blocked["status"], "BLOCKED_LEG_ELIGIBILITY")
        audits = blocked["audit_legs"]
        self.assertEqual(len(audits), 2)
        self.assertEqual({x["leg_id"] for x in audits}, {"L1", "L2"})
        self.assertTrue(all(k in x for x in audits for k in (
            "entry_status", "prior_oi_status", "range_proxy_status", "exit_status"
        )))
        first_audit = next(x for x in audits if x["leg_id"] == first["leg_id"])
        second_audit = next(x for x in audits if x["leg_id"] != first["leg_id"])
        self.assertEqual(first_audit["status"], "PRIOR_OI_MISSING_OR_BELOW_GATE")
        self.assertEqual(first_audit["prior_oi"], 50.0)
        self.assertEqual(first_audit["prior_oi_status"], "FAIL")
        self.assertEqual(second_audit["prior_oi_status"], "PASS")
        self.assertEqual(blocked["promotable"], False)

if __name__ == "__main__":
    unittest.main()
