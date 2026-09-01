#!/usr/bin/env python3
"""Check structural integrity of plan/document_review_registry.yaml.

This checker does not score prose quality. It verifies that current Markdown
files are covered by reviewed scopes and that no pending review remains.
"""

from __future__ import annotations

import argparse
import fnmatch
import pathlib
import re
import sys
from dataclasses import dataclass

DEFAULT_ROOT = pathlib.Path(__file__).resolve().parents[2]
EXPECTED_SCHEMA = "soza.document-review-registry/v1"
REVIEWED_STATUSES = {"revised", "reviewed-no-change"}
EXCLUDED_STATUSES = {"excluded-historical"}


@dataclass(frozen=True)
class Entry:
    scope: str
    status: str
    section: str


def parse_entries(text: str) -> tuple[list[Entry], str]:
    entries: list[Entry] = []
    section = ""
    pending_value = ""
    current_scope: str | None = None
    current_section: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        if line == "reviewed:":
            section = "reviewed"
            current_scope = None
            continue
        if line.startswith("pending:"):
            section = "pending"
            pending_value = line.split(":", 1)[1].strip()
            current_scope = None
            continue
        if line == "exclusions:":
            section = "exclusions"
            current_scope = None
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:", line) and not line.startswith("  "):
            section = "other"
            current_scope = None
            continue

        scope_match = re.match(r"^  - scope:\s*(.+?)\s*$", line)
        if scope_match and section in {"reviewed", "exclusions", "pending"}:
            if current_scope is not None:
                raise ValueError(f"missing status for scope: {current_scope}")
            current_scope = scope_match.group(1).strip().strip('"\'')
            current_section = section
            continue

        status_match = re.match(r"^    status:\s*([^#]+?)\s*$", line)
        if status_match and current_scope is not None and current_section is not None:
            status = status_match.group(1).strip().strip('"\'')
            entries.append(Entry(current_scope, status, current_section))
            current_scope = None
            current_section = None

    if current_scope is not None:
        raise ValueError(f"missing status for scope: {current_scope}")

    return entries, pending_value


def markdown_files(root: pathlib.Path) -> list[str]:
    files: list[str] = []
    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        files.append(path.relative_to(root).as_posix())
    return sorted(files)


def matches(scope: str, path: str) -> bool:
    return fnmatch.fnmatchcase(path, scope)


def check_registry(root: pathlib.Path) -> tuple[list[str], int, int]:
    errors: list[str] = []
    registry = root / "plan" / "document_review_registry.yaml"

    if not registry.exists():
        return [f"missing registry: {registry.relative_to(root)}"], 0, 0

    text = registry.read_text(encoding="utf-8")

    schema_match = re.search(r"^schema:\s*(\S+)\s*$", text, re.MULTILINE)
    if not schema_match:
        errors.append("registry schema is missing")
    elif schema_match.group(1) != EXPECTED_SCHEMA:
        errors.append(
            f"unexpected registry schema: {schema_match.group(1)} != {EXPECTED_SCHEMA}"
        )

    try:
        entries, pending_value = parse_entries(text)
    except ValueError as exc:
        errors.append(str(exc))
        entries, pending_value = [], ""

    if pending_value != "[]":
        errors.append("pending must be an explicit empty list: pending: []")

    seen_scopes: set[tuple[str, str]] = set()
    reviewed: list[Entry] = []

    for entry in entries:
        key = (entry.section, entry.scope)
        if key in seen_scopes:
            errors.append(f"duplicate {entry.section} scope: {entry.scope}")
        seen_scopes.add(key)

        if entry.section == "reviewed":
            reviewed.append(entry)
            if entry.status not in REVIEWED_STATUSES:
                errors.append(
                    f"invalid reviewed status for {entry.scope}: {entry.status}"
                )
        elif entry.section == "exclusions":
            if entry.status not in EXCLUDED_STATUSES:
                errors.append(
                    f"invalid exclusion status for {entry.scope}: {entry.status}"
                )
        elif entry.section == "pending":
            errors.append(f"pending scope remains: {entry.scope}")

    all_markdown = markdown_files(root)

    for entry in reviewed:
        matched = [path for path in all_markdown if matches(entry.scope, path)]
        if not matched:
            errors.append(f"reviewed scope matches no Markdown file: {entry.scope}")

    uncovered = [
        path
        for path in all_markdown
        if not any(matches(entry.scope, path) for entry in reviewed)
    ]
    for path in uncovered:
        errors.append(f"current Markdown is not covered by reviewed scope: {path}")

    return errors, len(reviewed), len(all_markdown)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=pathlib.Path,
        default=DEFAULT_ROOT,
        help="repository root to inspect (default: actual repository root)",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()

    errors, reviewed_count, markdown_count = check_registry(root)
    if errors:
        print("Document review registry integrity: FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Document review registry integrity: PASS")
    print(f"- reviewed scopes: {reviewed_count}")
    print(f"- current Markdown files covered: {markdown_count}")
    print("- pending scopes: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
