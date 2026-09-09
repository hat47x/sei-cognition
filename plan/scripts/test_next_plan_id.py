#!/usr/bin/env python3
"""Self-tests for next_plan_id.py using only the Python stdlib."""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("next_plan_id.py")
SPEC = importlib.util.spec_from_file_location("next_plan_id", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

ADR_PATTERN = re.compile(r"ADR-(\d{4})-[^.]+\.md")
ISSUE_PATTERN = re.compile(r"ISSUE-(\d{6})-[^.]+\.md")


class NextPlanIdTest(unittest.TestCase):
    def make_dir(self, names: list[str]) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        for name in names:
            path = root / name
            if name.endswith("/"):
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")
        return root

    def make_repo(
        self,
        adr_names: list[str],
        issue_names: list[str],
    ) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        script = root / "plan" / "scripts" / "next_plan_id.py"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text(MODULE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        adr_dir = root / "plan" / "adr"
        issue_dir = root / "plan" / "issue"
        adr_dir.mkdir(parents=True, exist_ok=True)
        issue_dir.mkdir(parents=True, exist_ok=True)
        for directory, names in ((adr_dir, adr_names), (issue_dir, issue_names)):
            for name in names:
                (directory / name).write_text("", encoding="utf-8")
        return root

    def run_cli(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(root / "plan" / "scripts" / "next_plan_id.py"), *args],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_empty_directory_starts_at_one(self) -> None:
        directory = self.make_dir([])
        self.assertEqual(1, MODULE.next_number(directory, ADR_PATTERN))
        self.assertEqual(1, MODULE.next_number(directory, ISSUE_PATTERN))

    def test_next_number_uses_maximum_not_first_gap(self) -> None:
        directory = self.make_dir([
            "ISSUE-000001-a.md",
            "ISSUE-000003-c.md",
            "ISSUE-000002-b.md",
        ])
        self.assertEqual(4, MODULE.next_number(directory, ISSUE_PATTERN))

    def test_templates_unrelated_files_and_directories_are_ignored(self) -> None:
        directory = self.make_dir([
            "ISSUE-000007-valid.md",
            "ISSUE_TEMPLATE.md",
            "ISSUE-000099-invalid.txt",
            "ISSUE-000100-dir/",
            "notes.md",
        ])
        self.assertEqual(8, MODULE.next_number(directory, ISSUE_PATTERN))

    def test_cli_all_prints_both_candidates(self) -> None:
        root = self.make_repo(
            ["ADR-0001-a.md", "ADR-0030-current.md"],
            ["ISSUE-000001-a.md", "ISSUE-000072-current.md"],
        )
        result = self.run_cli(root)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("ADR-0031\nISSUE-000073\n", result.stdout)

    def test_cli_kind_filters_output(self) -> None:
        root = self.make_repo(["ADR-0005-a.md"], ["ISSUE-000009-a.md"])
        adr = self.run_cli(root, "adr")
        issue = self.run_cli(root, "issue")
        self.assertEqual(0, adr.returncode, adr.stdout + adr.stderr)
        self.assertEqual("ADR-0006\n", adr.stdout)
        self.assertEqual(0, issue.returncode, issue.stdout + issue.stderr)
        self.assertEqual("ISSUE-000010\n", issue.stdout)

    def test_adr_id_space_exhaustion_fails(self) -> None:
        root = self.make_repo(["ADR-9999-last.md"], ["ISSUE-000001-a.md"])
        result = self.run_cli(root, "adr")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("ADR ID空間を使い切っています。", result.stderr)

    def test_issue_id_space_exhaustion_fails(self) -> None:
        root = self.make_repo(["ADR-0001-a.md"], ["ISSUE-999999-last.md"])
        result = self.run_cli(root, "issue")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Issue ID空間を使い切っています。", result.stderr)


if __name__ == "__main__":
    unittest.main()
