#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("check_document_review_registry.py")
SPEC = importlib.util.spec_from_file_location("check_document_review_registry", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
check_registry = MODULE.check_registry


class DocumentReviewRegistryTest(unittest.TestCase):
    def make_repo(self, registry: str, files: dict[str, str]) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        (root / "plan").mkdir(parents=True, exist_ok=True)
        (root / "plan" / "document_review_registry.yaml").write_text(registry, encoding="utf-8")
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return root

    def test_registered_markdown_and_empty_pending_pass(self) -> None:
        root = self.make_repo(
            """schema: sei.document-review-registry/v1
reviewed:
  - scope: README.md
    status: revised
  - scope: docs/*.md
    status: reviewed-no-change
pending: []
exclusions:
closure_rule: done
""",
            {"README.md": "# root\n", "docs/a.md": "# a\n"},
        )
        self.assertEqual([], check_registry(root))

    def test_unregistered_markdown_fails(self) -> None:
        root = self.make_repo(
            """schema: sei.document-review-registry/v1
reviewed:
  - scope: README.md
    status: revised
pending: []
exclusions:
closure_rule: done
""",
            {"README.md": "# root\n", "docs/new.md": "# new\n"},
        )
        errors = check_registry(root)
        self.assertTrue(any("docs/new.md" in error and "covered" in error for error in errors))

    def test_nonempty_pending_fails(self) -> None:
        root = self.make_repo(
            """schema: sei.document-review-registry/v1
reviewed:
  - scope: README.md
    status: revised
pending:
  - scope: docs/new.md
    status: pending
exclusions:
closure_rule: done
""",
            {"README.md": "# root\n", "docs/new.md": "# new\n"},
        )
        errors = check_registry(root)
        self.assertTrue(any("pendingが空ではありません" in error for error in errors))

    def test_historical_markdown_exclusion_passes(self) -> None:
        root = self.make_repo(
            """schema: sei.document-review-registry/v1
reviewed:
  - scope: README.md
    status: revised
pending: []
exclusions:
  - scope: history/*.md
    status: excluded-historical
    reason: source evidence
closure_rule: done
""",
            {"README.md": "# root\n", "history/source.md": "# source\n"},
        )
        self.assertEqual([], check_registry(root))

    def test_stale_reviewed_scope_fails(self) -> None:
        root = self.make_repo(
            """schema: sei.document-review-registry/v1
reviewed:
  - scope: README.md
    status: revised
  - scope: docs/*.md
    status: revised
pending: []
exclusions:
closure_rule: done
""",
            {"README.md": "# root\n"},
        )
        errors = check_registry(root)
        self.assertTrue(any("reviewed scopeがactual Markdownに一致しません: docs/*.md" == error for error in errors))


if __name__ == "__main__":
    unittest.main()
