import importlib.util
import json
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("source_delta_audit.py")
spec = importlib.util.spec_from_file_location("phase61", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
REGISTRY = json.loads((Path(__file__).with_name("source_registry.json")).read_text())


class Phase61Tests(unittest.TestCase):
    def test_registry_has_five_unique_candidates_and_no_accepted_source(self):
        report = mod.evaluate(REGISTRY)
        self.assertEqual(report["candidate_count"], 5)
        self.assertEqual(len({x["id"] for x in report["candidates"]}), 5)
        self.assertEqual(report["status"], "NO_GO_NO_NEW_SOURCE_MEETS_RESTART_GATE")
        self.assertEqual(report["accepted_source_ids"], [])
        self.assertFalse(report["frozen_rules"]["holdout_used"])
        self.assertFalse(report["frozen_rules"]["data_downloaded"])

    def test_acceptance_requires_rights_and_validated_sample(self):
        registry = json.loads(json.dumps(REGISTRY))
        registry["candidates"][0]["decision"] = "ACCEPT_FOR_SAMPLE_VALIDATION"
        with self.assertRaises(AssertionError):
            mod.evaluate(registry)

    def test_duplicate_ids_fail(self):
        registry = json.loads(json.dumps(REGISTRY))
        registry["candidates"][1]["id"] = registry["candidates"][0]["id"]
        with self.assertRaises(ValueError):
            mod.evaluate(registry)


if __name__ == "__main__":
    unittest.main()
