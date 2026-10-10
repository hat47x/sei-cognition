#!/usr/bin/env python3
"""SEIのDocument Review Registry coverageを検査する。

このcheckerは文書内容の意味品質を評価しない。actual tree上のMarkdown開発文書が
plan/document_review_registry.yaml のreviewed scopeまたは明示的なexclusionに
包含され、pendingが残っていないことだけを検査する。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REVIEWED_STATUS = {"revised", "reviewed-no-change", "excluded-historical"}
EXCLUSION_STATUS = {"excluded-historical"}


def _section(text: str, start: str, end: str | None) -> str:
    marker = f"\n{start}:"
    if not text.startswith(f"{start}:") and marker not in text:
        return ""
    _, tail = text.split(f"{start}:", 1)
    if end is None:
        return tail
    end_marker = f"\n{end}:"
    return tail.split(end_marker, 1)[0] if end_marker in tail else tail


def _parse_scope_status_pairs(section: str) -> list[tuple[str, str]]:
    pattern = re.compile(
        r"^  - scope:\s*([^\n]+)\n"
        r"    status:\s*([^\n]+)$",
        re.MULTILINE,
    )
    return [(m.group(1).strip(), m.group(2).strip()) for m in pattern.finditer(section)]


def _expand_markdown_scope(repo_root: Path, scope: str) -> set[str]:
    matches: set[str] = set()
    try:
        candidates = repo_root.glob(scope)
    except (NotImplementedError, ValueError):
        return matches
    for path in candidates:
        if path.is_file() and path.suffix.lower() == ".md":
            matches.add(path.relative_to(repo_root).as_posix())
    return matches


def check_registry(repo_root: Path) -> list[str]:
    registry_path = repo_root / "plan" / "document_review_registry.yaml"
    errors: list[str] = []

    if not registry_path.is_file():
        return ["plan/document_review_registry.yaml が見つかりません。"]

    text = registry_path.read_text(encoding="utf-8")
    reviewed_section = _section(text, "reviewed", "pending")
    exclusion_section = _section(text, "exclusions", "closure_rule")

    reviewed = _parse_scope_status_pairs(reviewed_section)
    exclusions = _parse_scope_status_pairs(exclusion_section)

    if not reviewed:
        errors.append("reviewed scopeを1件も読み取れません。台帳書式を確認してください。")

    scopes = [scope for scope, _ in reviewed]
    duplicate_scopes = sorted({scope for scope in scopes if scopes.count(scope) > 1})
    for scope in duplicate_scopes:
        errors.append(f"reviewed scopeが重複しています: {scope}")

    covered: set[str] = set()
    for scope, status in reviewed:
        if status not in REVIEWED_STATUS:
            errors.append(f"reviewed statusが規定値ではありません: {scope}: {status}")
        matched = _expand_markdown_scope(repo_root, scope)
        if not matched:
            errors.append(f"reviewed scopeがactual Markdownに一致しません: {scope}")
        covered.update(matched)

    excluded: set[str] = set()
    for scope, status in exclusions:
        if status not in EXCLUSION_STATUS:
            errors.append(f"exclusion statusが規定値ではありません: {scope}: {status}")
        excluded.update(_expand_markdown_scope(repo_root, scope))

    pending_empty = bool(re.search(r"^pending:\s*\[\]\s*$", text, re.MULTILINE))
    if not pending_empty:
        errors.append("pendingが空ではありません。文書監査を完了してからmergeしてください。")

    actual_markdown = {
        path.relative_to(repo_root).as_posix()
        for path in repo_root.rglob("*.md")
        if path.is_file() and ".git" not in path.parts
    }

    for path in sorted((covered | excluded) - actual_markdown):
        if path.endswith(".md"):
            errors.append(f"Document Review Registryが存在しないMarkdownを参照しています: {path}")

    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    errors = check_registry(repo_root)
    if errors:
        print("document review registry check: FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    markdown_count = sum(1 for path in repo_root.rglob("*.md") if path.is_file())
    print(f"document review registry check: PASS ({markdown_count} Markdown files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
