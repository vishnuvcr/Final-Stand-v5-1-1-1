#!/usr/bin/env python3
"""Offline tests for the Phase 53 metadata audit."""
from __future__ import annotations

import importlib.util
import unittest
from unittest.mock import patch
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
        self.assertEqual(result["listed_matching_count"], 2)
        self.assertEqual(result["not_listed_in_returned_metadata_count"], 0)
        self.assertTrue(result["metadata_listing_proves_missing"])
        self.assertEqual(result["file_metadata"][0]["size_bytes"], 100)

    def test_missing_metadata_listing_is_not_conflated_with_no_files(self) -> None:
        # assess_inventory is only used after a successful API listing. Its result
        # explicitly marks a known listing; unknown API failure is represented as null.
        partial = audit.assess_inventory([], ["index/NIFTY.parquet"], listing_complete=False)
        self.assertFalse(partial["listing_complete"])
        self.assertEqual(partial["not_listed_in_returned_metadata_count"], 1)
        self.assertFalse(partial["metadata_listing_proves_missing"])
        self.assertIn("UNKNOWN", partial["interpretation"])
        # Only a known complete listing can establish an unlisted path.
        complete = audit.assess_inventory([], ["index/NIFTY.parquet"], listing_complete=True)
        self.assertTrue(complete["metadata_listing_proves_missing"])

    def test_duplicate_listing_paths_are_detected(self) -> None:
        items = [
            {"path": "index/NIFTY.parquet", "size": 1},
            {"path": "index/NIFTY.parquet", "size": 2},
        ]
        result = audit.assess_inventory(items, ["index/NIFTY.parquet"])
        self.assertEqual(result["duplicate_list_entries"], ["index/NIFTY.parquet"])


    def test_hf_tree_listing_follows_next_page_and_merges_directories(self) -> None:
        option_first = [
            {"path": "options/NIFTY/2021-05-27.parquet", "size": 100},
            {"path": "options/NIFTY/2021-12-09.parquet", "size": 120},
        ]
        option_second = [{"path": "options/NIFTY/2022-06-16.parquet", "size": 150}]
        index_rows = [{"path": "index/NIFTY.parquet", "size": 500}]
        meta_first = {"http_status": 200, "link_header": '<https://next.example/page2>; rel="next"'}
        meta_last = {"http_status": 200, "link_header": None}
        with patch.object(audit, "json_request", side_effect=[
            (meta_first, option_first),
            (meta_last, option_second),
            (meta_last, index_rows),
        ]):
            meta, items = audit.listed_tree("owner/repo", "abc123", None)
        self.assertTrue(meta["listing_complete"])
        self.assertEqual(len(items or []), 4)
        inventory = audit.assess_inventory(
            items or [],
            ["options/NIFTY/2021-05-27.parquet", "options/NIFTY/2021-12-09.parquet",
             "options/NIFTY/2022-06-16.parquet", "index/NIFTY.parquet"],
            listing_complete=meta["listing_complete"],
        )
        self.assertEqual(inventory["listed_matching_count"], 4)
        self.assertEqual(inventory["not_listed_in_returned_metadata_count"], 0)

    def test_policy_skips_nse_live_option_chain_network_probe(self) -> None:
        source = {
            "id": "nse_live_option_chain", "name": "NSE current option chain",
            "class": "official_current_snapshot_not_historical", "url": "https://example.invalid",
            "probe_allowed": False, "expected_granularity": "current snapshot only",
        }
        with patch.object(audit, "request_url") as mocked:
            result = audit.source_probe(source, None)
        mocked.assert_not_called()
        self.assertEqual(result["probe_status"], "SKIPPED_BY_POLICY")


if __name__ == "__main__":
    unittest.main()
