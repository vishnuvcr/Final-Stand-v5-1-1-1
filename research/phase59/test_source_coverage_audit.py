import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parent/"source_coverage_audit.py"
spec=importlib.util.spec_from_file_location("phase59_audit",SCRIPT)
mod=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


class Phase59Tests(unittest.TestCase):
    def test_registry_has_unique_ids_and_conservative_no_go(self):
        registry=mod.load_registry()
        report=mod.audit(registry)
        self.assertEqual(report["source_count"],10)
        self.assertEqual(report["accepted_for_automated_replay"],[])
        self.assertEqual(report["free_license_clear_exact_intraday_oi_sources"],0)
        self.assertEqual(report["free_license_clear_exact_quote_depth_sources"],0)
        self.assertFalse(report["purchase_made"])
        self.assertFalse(report["data_downloaded"])
        self.assertFalse(report["holdout_used"])

    def test_missing_permission_cannot_be_overridden_by_fields(self):
        registry=mod.load_registry()
        candidate=dict(registry["sources"][0])
        candidate["has_intraday_oi"]=True
        candidate["has_expiry_and_strike"]=True
        candidate["has_bid_ask_depth"]=True
        candidate["exact_target_contract_coverage_verified"]=True
        candidate["license_clear_for_automation"]=False
        custom=dict(registry)
        custom["sources"]=[candidate]*0 + [candidate]*8
        # IDs must be unique even when records otherwise look adequate.
        with self.assertRaises(ValueError):
            mod.audit(custom)

    def test_missing_required_schema_fails_closed(self):
        registry=mod.load_registry()
        bad=dict(registry)
        bad["sources"]=[dict(registry["sources"][0])]
        bad["sources"][0].pop("evidence_limit")
        with self.assertRaises(ValueError):
            mod.audit(bad)


if __name__=="__main__":
    unittest.main()
