#!/usr/bin/env python3
"""Self-tests for check_plan_registry.py using only the Python stdlib."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECKER_PATH = Path(__file__).with_name("check_plan_registry.py")
CHECKER_SOURCE = CHECKER_PATH.read_text(encoding="utf-8")

VALID_REGISTRY = """schema: sei.plan-registry/v1
updated: 2026-09-09

adr:
  - id: ADR-0001
    file: plan/adr/ADR-0001-sample.md
    status: Accepted
    related_issues: [ISSUE-000001]

issue:
  - {id: ISSUE-000001, file: plan/issue/ISSUE-000001-sample.md, status: Resolved, priority: 1, related_adrs: [ADR-0001]}
"""

VALID_FILES = {
    "plan/adr/ADR-0001-sample.md": "# ADR-0001: sample\n\nStatus: **Accepted**\n",
    "plan/issue/ISSUE-000001-sample.md": "# ISSUE-000001: sample\n\nStatus: **Resolved**\n",
}


class PlanRegistryCheckerTest(unittest.TestCase):
    def make_repo(
        self,
        registry: str = VALID_REGISTRY,
        extra_files: dict[str, str] | None = None,
    ) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)

        script_path = root / "plan" / "scripts" / "check_plan_registry.py"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(CHECKER_SOURCE, encoding="utf-8")
        (root / "plan" / "registry.yaml").write_text(registry, encoding="utf-8")

        files = dict(VALID_FILES)
        if extra_files:
            files.update(extra_files)
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return root

    def run_checker(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(root / "plan" / "scripts" / "check_plan_registry.py")],
            cwd=root,
            text=True,
            encoding="utf-8",
            env={**os.environ, "PYTHONUTF8": "1"},
            capture_output=True,
            check=False,
        )

    def assert_failed_with(
        self,
        expected: str,
        *,
        registry: str = VALID_REGISTRY,
        extra_files: dict[str, str] | None = None,
    ) -> None:
        result = self.run_checker(self.make_repo(registry, extra_files))
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(expected, result.stderr)

    def test_valid_minimal_registry_passes(self) -> None:
        result = self.run_checker(self.make_repo())
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("plan registry integrity check: PASS", result.stdout)

    def test_duplicate_issue_id_fails(self) -> None:
        registry = VALID_REGISTRY + (
            "  - {id: ISSUE-000001, file: plan/issue/ISSUE-000001-duplicate.md, "
            "status: Resolved, priority: 1, related_adrs: [ADR-0001]}\n"
        )
        self.assert_failed_with(
            "Issue IDが重複しています: ISSUE-000001",
            registry=registry,
            extra_files={
                "plan/issue/ISSUE-000001-duplicate.md":
                    "# ISSUE-000001: duplicate\n\nStatus: **Resolved**\n",
            },
        )

    def test_unregistered_same_id_issue_file_fails(self) -> None:
        self.assert_failed_with(
            "Issueファイルがregistryにありません: plan/issue/ISSUE-000001-stale.md",
            extra_files={
                "plan/issue/ISSUE-000001-stale.md":
                    "# ISSUE-000001: stale\n\nStatus: **Resolved**\n",
            },
        )

    def test_duplicate_issue_file_binding_fails(self) -> None:
        registry = VALID_REGISTRY + (
            "  - {id: ISSUE-000002, file: plan/issue/ISSUE-000001-sample.md, "
            "status: Resolved, priority: 1, related_adrs: [ADR-0001]}\n"
        )
        self.assert_failed_with(
            "Issue fileが重複しています: plan/issue/ISSUE-000001-sample.md",
            registry=registry,
        )

    def test_registry_file_missing_from_tree_fails(self) -> None:
        registry = VALID_REGISTRY.replace(
            "plan/issue/ISSUE-000001-sample.md",
            "plan/issue/ISSUE-000001-missing.md",
        )
        self.assert_failed_with(
            "registryのIssueファイルがactual treeにありません: "
            "plan/issue/ISSUE-000001-missing.md",
            registry=registry,
        )

    def test_document_status_mismatch_fails(self) -> None:
        registry = VALID_REGISTRY.replace("status: Resolved", "status: Open")
        self.assert_failed_with(
            "Issue Statusとregistryが一致しません: ISSUE-000001: "
            "document='Resolved', registry='Open'",
            registry=registry,
        )

    def test_missing_related_adr_fails(self) -> None:
        registry = VALID_REGISTRY.replace(
            "related_adrs: [ADR-0001]",
            "related_adrs: [ADR-9999]",
        )
        self.assert_failed_with(
            "Issueが存在しないADRを参照しています: ISSUE-000001 -> ADR-9999",
            registry=registry,
        )

    def test_templates_are_ignored(self) -> None:
        result = self.run_checker(
            self.make_repo(
                extra_files={
                    "plan/adr/ADR_TEMPLATE.md": "# ADR template\n",
                    "plan/issue/ISSUE_TEMPLATE.md": "# Issue template\n",
                },
            )
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
