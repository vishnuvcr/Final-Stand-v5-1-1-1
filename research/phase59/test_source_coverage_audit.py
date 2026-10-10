import importlib.util
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
        self.assertEqual(report["authorized_exact_intraday_oi_sources"],0)
        self.assertEqual(report["authorized_exact_quote_depth_sources"],0)
        self.assertFalse(report["purchase_made"])
        self.assertFalse(report["data_downloaded"])
        self.assertFalse(report["holdout_used"])

    def test_missing_permission_cannot_be_overridden_by_data_fields(self):
        registry=mod.load_registry()
        candidates=[]
        for i, source in enumerate(registry["sources"][:8]):
            candidate=dict(source)
            candidate["id"]=f"test_candidate_{i}"
            if i==0:
                candidate.update({
                    "has_intraday_oi":True,
                    "has_expiry_and_strike":True,
                    "has_bid_ask_depth":True,
                    "exact_target_contract_coverage_verified":True,
                    "license_clear_for_automation":False,
                })
            candidates.append(candidate)
        custom=dict(registry)
        custom["sources"]=candidates
        out=mod.audit(custom)
        first=next(row for row in out["sources"] if row["id"]=="test_candidate_0")
        self.assertFalse(first["eligible_for_prior_minute_oi_replay"])
        self.assertFalse(first["eligible_for_quote_depth_replay"])
        self.assertNotIn("test_candidate_0",out["accepted_for_automated_replay"])

    def test_missing_required_schema_fails_closed(self):
        registry=mod.load_registry()
        bad=dict(registry)
        bad["sources"]=[dict(registry["sources"][0])]
        bad["sources"][0].pop("evidence_limit")
        with self.assertRaises(ValueError):
            mod.audit(bad)


if __name__=="__main__":
    unittest.main()
