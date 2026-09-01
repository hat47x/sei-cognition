#!/usr/bin/env python3
"""Negative and positive self-tests for document review registry integrity."""

from __future__ import annotations

import pathlib
import tempfile

import check_document_review_registry as checker


def write(root: pathlib.Path, path: str, content: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def registry(reviewed: str, pending: str = "[]") -> str:
    return f"""schema: soza.document-review-registry/v1
updated: 2026-09-01

reviewed:
{reviewed}
pending: {pending}

exclusions:
"""


def run_case(name: str, setup, expected_fragment: str | None) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        setup(root)
        errors, _, _ = checker.check_registry(root)
        if expected_fragment is None:
            if errors:
                raise AssertionError(f"{name}: expected PASS, got {errors}")
            return
        if not any(expected_fragment in error for error in errors):
            raise AssertionError(
                f"{name}: expected error containing {expected_fragment!r}, got {errors}"
            )


def main() -> int:
    run_case(
        "valid",
        lambda root: (
            write(root, "README.md", "# root\n"),
            write(
                root,
                "plan/document_review_registry.yaml",
                registry("  - scope: README.md\n    status: revised\n"),
            ),
        ),
        None,
    )

    run_case(
        "invalid-status",
        lambda root: (
            write(root, "README.md", "# root\n"),
            write(
                root,
                "plan/document_review_registry.yaml",
                registry("  - scope: README.md\n    status: pending\n"),
            ),
        ),
        "invalid reviewed status",
    )

    run_case(
        "stale-scope",
        lambda root: (
            write(root, "README.md", "# root\n"),
            write(
                root,
                "plan/document_review_registry.yaml",
                registry("  - scope: missing.md\n    status: revised\n"),
            ),
        ),
        "reviewed scope matches no Markdown file",
    )

    run_case(
        "uncovered-markdown",
        lambda root: (
            write(root, "README.md", "# root\n"),
            write(root, "docs/new.md", "# new\n"),
            write(
                root,
                "plan/document_review_registry.yaml",
                registry("  - scope: README.md\n    status: revised\n"),
            ),
        ),
        "current Markdown is not covered by reviewed scope: docs/new.md",
    )

    run_case(
        "duplicate-scope",
        lambda root: (
            write(root, "README.md", "# root\n"),
            write(
                root,
                "plan/document_review_registry.yaml",
                registry(
                    "  - scope: README.md\n    status: revised\n"
                    "  - scope: README.md\n    status: reviewed-no-change\n"
                ),
            ),
        ),
        "duplicate reviewed scope",
    )

    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        write(root, "README.md", "# root\n")
        write(root, "docs/pending.md", "# pending\n")
        write(
            root,
            "plan/document_review_registry.yaml",
            """schema: soza.document-review-registry/v1
updated: 2026-09-01

reviewed:
  - scope: README.md
    status: revised
pending:
  - scope: docs/pending.md
    status: pending

exclusions:
""",
        )
        errors, _, _ = checker.check_registry(root)
        if not any("pending must be an explicit empty list" in error for error in errors):
            raise AssertionError(f"pending: expected explicit-empty-list failure, got {errors}")
        if not any("pending scope remains: docs/pending.md" in error for error in errors):
            raise AssertionError(f"pending: expected pending-scope failure, got {errors}")

    print("Document review registry checker self-tests: PASS")
    print("- valid registry accepted")
    print("- invalid status rejected")
    print("- stale scope rejected")
    print("- uncovered Markdown rejected")
    print("- duplicate scope rejected")
    print("- pending review rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
