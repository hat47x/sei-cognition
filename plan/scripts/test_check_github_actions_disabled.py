#!/usr/bin/env python3
"""Self-tests for check_github_actions_disabled.py using only the Python stdlib."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("check_github_actions_disabled.py")
SPEC = importlib.util.spec_from_file_location("check_github_actions_disabled", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class GitHubActionsDisabledCheckerTest(unittest.TestCase):
    def make_repo(self, files: dict[str, str] | None = None) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        if files:
            for relative, content in files.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
        return root

    def test_absent_workflows_directory_passes(self) -> None:
        self.assertEqual([], MODULE.check_repo(self.make_repo()))

    def test_empty_workflows_directory_passes(self) -> None:
        root = self.make_repo()
        (root / ".github" / "workflows").mkdir(parents=True)
        self.assertEqual([], MODULE.check_repo(root))

    def test_workflow_file_fails(self) -> None:
        root = self.make_repo({".github/workflows/ci.yml": "name: ci\n"})
        errors = MODULE.check_repo(root)
        self.assertEqual(
            ["GitHub Actions workflowがcurrent baselineに存在します: .github/workflows/ci.yml"],
            errors,
        )

    def test_any_tracked_file_under_workflows_fails(self) -> None:
        root = self.make_repo({".github/workflows/README.txt": "disabled\n"})
        errors = MODULE.check_repo(root)
        self.assertEqual(
            ["GitHub Actions workflowがcurrent baselineに存在します: .github/workflows/README.txt"],
            errors,
        )

    def test_multiple_files_are_reported_in_stable_order(self) -> None:
        root = self.make_repo(
            {
                ".github/workflows/z.yml": "name: z\n",
                ".github/workflows/nested/a.yaml": "name: a\n",
            }
        )
        self.assertEqual(
            [
                "GitHub Actions workflowがcurrent baselineに存在します: .github/workflows/nested/a.yaml",
                "GitHub Actions workflowがcurrent baselineに存在します: .github/workflows/z.yml",
            ],
            MODULE.check_repo(root),
        )


if __name__ == "__main__":
    unittest.main()
