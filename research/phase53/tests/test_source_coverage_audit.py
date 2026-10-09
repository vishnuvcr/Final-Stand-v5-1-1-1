#!/usr/bin/env python3
"""Offline tests for the Phase 53 metadata audit."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "source_coverage_audit.py"
spec = importlib.util.spec_from_file_location("phase53_source_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(audit)


class SourceRegistryTests(unittest.TestCase):
    def test_registry_is_version_pinned_and_has_unique_sources(self) -> None:
        registry = audit.load_registry()
        ids = [source["id"] for source in registry["sources"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(registry["parent_dataset"]["revision"], "0f4800e43e6f96cec0794369d78eb4d3c4211ef5")
        self.assertEqual(len(registry["parent_dataset"]["required_files"]), 13)

    def test_inventory_reports_exact_files_without_imputation(self) -> None:
        items = [
            {"path": "options/NIFTY/2021-05-27.parquet", "size": 100, "lfs": {"oid": "a" * 40}},
            {"path": "index/NIFTY.parquet", "size": 500},
        ]
        required = ["options/NIFTY/2021-05-27.parquet", "index/NIFTY.parquet"]
        result = audit.assess_inventory(items, required)
        self.assertEqual(result["present_count"], 2)
        self.assertEqual(result["missing_count"], 0)
        self.assertEqual(result["file_metadata"][0]["size_bytes"], 100)

    def test_missing_metadata_listing_is_not_conflated_with_no_files(self) -> None:
        # assess_inventory is only used after a successful API listing. Its result
        # explicitly marks a known listing; unknown API failure is represented as null.
        known_empty = audit.assess_inventory([], ["index/NIFTY.parquet"])
        self.assertTrue(known_empty["listing_complete"])
        self.assertEqual(known_empty["missing_count"], 1)
        unknown_listing = None
        self.assertIsNone(unknown_listing)

    def test_duplicate_listing_paths_are_detected(self) -> None:
        items = [
            {"path": "index/NIFTY.parquet", "size": 1},
            {"path": "index/NIFTY.parquet", "size": 2},
        ]
        result = audit.assess_inventory(items, ["index/NIFTY.parquet"])
        self.assertEqual(result["duplicate_list_entries"], ["index/NIFTY.parquet"])


if __name__ == "__main__":
    unittest.main()
