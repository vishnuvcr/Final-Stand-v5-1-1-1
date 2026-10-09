#!/usr/bin/env python3
"""Regression tests for safe Phase 52 checkpoint persistence."""
from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "persist_historical_pilot.py"
spec = importlib.util.spec_from_file_location("persist_historical_pilot", SCRIPT)
persist = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(persist)


def run_git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=True)
    return result.stdout.strip()


class ConflictMergeTests(unittest.TestCase):
    def test_unions_both_sides_and_deduplicates_shared_lines(self) -> None:
        lines = [
            "heading",
            "<<<<<<< HEAD",
            "remote checkpoint",
            "shared line",
            "=======",
            "local checkpoint",
            "shared line",
            ">>>>>>> local",
            "footer",
        ]
        self.assertEqual(
            persist.merge_conflict_markers(lines, "PHASE52_STATUS.md"),
            ["heading", "remote checkpoint", "shared line", "local checkpoint", "footer"],
        )

    def test_rejects_malformed_conflict(self) -> None:
        with self.assertRaises(RuntimeError):
            persist.merge_conflict_markers(["<<<<<<< HEAD", "missing separator"], "x.md")

    def test_real_rebase_preserves_remote_and_local_checkpoints(self) -> None:
        with tempfile.TemporaryDirectory(prefix="phase52-persist-test-") as td:
            root = Path(td)
            bare = root / "origin.git"
            seed = root / "seed"
            clone_remote = root / "remote-writer"
            clone_local = root / "local-writer"
            subprocess.run(["git", "init", "--bare", str(bare)], check=True, capture_output=True)
            seed.mkdir()
            run_git(seed, "init", "-b", "phase-test")
            run_git(seed, "config", "user.name", "test")
            run_git(seed, "config", "user.email", "test@example.invalid")
            (seed / "PHASE52_STATUS.md").write_text("## Base\n", encoding="utf-8")
            run_git(seed, "add", "PHASE52_STATUS.md")
            run_git(seed, "commit", "-m", "base")
            run_git(seed, "remote", "add", "origin", str(bare))
            run_git(seed, "push", "-u", "origin", "phase-test")
            run_git(root, "clone", str(bare), str(clone_remote))
            run_git(root, "clone", str(bare), str(clone_local))
            for clone in (clone_remote, clone_local):
                run_git(clone, "checkout", "-b", "phase-test", "origin/phase-test")
                run_git(clone, "config", "user.name", "test")
                run_git(clone, "config", "user.email", "test@example.invalid")

            remote_file = clone_remote / "PHASE52_STATUS.md"
            remote_file.write_text(remote_file.read_text(encoding="utf-8") + "\n## Remote run\n", encoding="utf-8")
            run_git(clone_remote, "add", "PHASE52_STATUS.md")
            run_git(clone_remote, "commit", "-m", "remote checkpoint")
            run_git(clone_remote, "push", "origin", "phase-test")

            local_file = clone_local / "PHASE52_STATUS.md"
            local_file.write_text(local_file.read_text(encoding="utf-8") + "\n## Local run\n", encoding="utf-8")
            sha = persist.persist_repo(
                clone_local, "phase-test", ["PHASE52_STATUS.md"], "local checkpoint"
            )
            self.assertTrue(len(sha) == 40)
            final = run_git(clone_local, "show", "origin/phase-test:PHASE52_STATUS.md")
            self.assertIn("## Remote run", final)
            self.assertIn("## Local run", final)
            self.assertIn("## Base", final)


if __name__ == "__main__":
    unittest.main()
