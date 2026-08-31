#!/usr/bin/env python3
"""SOZA plan/ のADR / Issue / registry整合を検査する。

外部YAMLライブラリへ依存せず、plan/registry.yaml の現在の制約された書式を読む。
このcheckerは関連の完全対称性までは要求しない。ADR側とIssue側では関連を記録する
観点が異なり得るためである。ただし、記載された関連IDが実在することは検査する。
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ADR_ID_RE = re.compile(r"ADR-\d{4}$")
ISSUE_ID_RE = re.compile(r"ISSUE-\d{6}$")
ADR_FILE_RE = re.compile(r"ADR-(\d{4})-[^.]+\.md$")
ISSUE_FILE_RE = re.compile(r"ISSUE-(\d{6})-[^.]+\.md$")
STATUS_RE = re.compile(r"^Status:\s*\*\*(.+?)\*\*\s*$", re.MULTILINE)
HEADING_ID_RE = re.compile(r"^#\s+((?:ADR-\d{4})|(?:ISSUE-\d{6})):", re.MULTILINE)

ALLOWED_ADR_STATUSES = {
    "Proposed", "Decision Deferred", "Accepted", "Rejected", "Superseded", "Deprecated",
}
ALLOWED_ISSUE_STATUSES = {
    "Open", "In Progress", "Blocked", "Resolved", "Deferred", "Closed — No Change",
}


@dataclass(frozen=True)
class AdrEntry:
    id: str
    file: str
    status: str
    related_issues: tuple[str, ...]


@dataclass(frozen=True)
class IssueEntry:
    id: str
    file: str
    status: str
    priority: int
    related_adrs: tuple[str, ...]


def split_ids(raw: str) -> tuple[str, ...]:
    raw = raw.strip()
    return tuple(part.strip() for part in raw.split(",") if part.strip()) if raw else ()


def parse_registry(text: str) -> tuple[list[AdrEntry], list[IssueEntry]]:
    adr_pattern = re.compile(
        r"^  - id: (ADR-\d{4})\n"
        r"    file: ([^\n]+)\n"
        r"    status: ([^\n]+)\n"
        r"    related_issues: \[([^\]]*)\]$", re.MULTILINE,
    )
    issue_pattern = re.compile(
        r"^  - \{id: (ISSUE-\d{6}), file: ([^,]+), status: ([^,]+), "
        r"priority: (\d+), related_adrs: \[([^\]]*)\]\}$", re.MULTILINE,
    )
    adrs = [AdrEntry(m.group(1), m.group(2).strip(), m.group(3).strip(), split_ids(m.group(4)))
            for m in adr_pattern.finditer(text)]
    issues = [IssueEntry(m.group(1), m.group(2).strip(), m.group(3).strip(), int(m.group(4)), split_ids(m.group(5)))
              for m in issue_pattern.finditer(text)]
    return adrs, issues


def markdown_meta(path: Path) -> tuple[str | None, str | None]:
    text = path.read_text(encoding="utf-8")
    heading = HEADING_ID_RE.search(text)
    status = STATUS_RE.search(text)
    return (heading.group(1) if heading else None, status.group(1).strip() if status else None)


def add_duplicate_errors(values: list[str], label: str, errors: list[str]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    for value in sorted(duplicates):
        errors.append(f"{label}が重複しています: {value}")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    adr_dir = repo_root / "plan" / "adr"
    issue_dir = repo_root / "plan" / "issue"
    registry_path = repo_root / "plan" / "registry.yaml"
    errors: list[str] = []

    if not registry_path.is_file():
        print("ERROR: plan/registry.yaml が見つかりません。", file=sys.stderr)
        return 1

    adrs, issues = parse_registry(registry_path.read_text(encoding="utf-8"))
    if not adrs:
        errors.append("registryからADRを1件も読み取れません。書式を確認してください。")
    if not issues:
        errors.append("registryからIssueを1件も読み取れません。書式を確認してください。")

    add_duplicate_errors([e.id for e in adrs], "ADR ID", errors)
    add_duplicate_errors([e.id for e in issues], "Issue ID", errors)
    add_duplicate_errors([e.file for e in adrs], "ADR file", errors)
    add_duplicate_errors([e.file for e in issues], "Issue file", errors)

    adr_by_id = {e.id: e for e in adrs}
    issue_by_id = {e.id: e for e in issues}
    actual_adr_files = {p.relative_to(repo_root).as_posix(): p for p in adr_dir.glob("ADR-*.md") if p.name != "ADR_TEMPLATE.md"}
    actual_issue_files = {p.relative_to(repo_root).as_posix(): p for p in issue_dir.glob("ISSUE-*.md") if p.name != "ISSUE_TEMPLATE.md"}
    registry_adr_files = {e.file for e in adrs}
    registry_issue_files = {e.file for e in issues}

    for missing in sorted(set(actual_adr_files) - registry_adr_files):
        errors.append(f"ADRファイルがregistryにありません: {missing}")
    for missing in sorted(registry_adr_files - set(actual_adr_files)):
        errors.append(f"registryのADRファイルがactual treeにありません: {missing}")
    for missing in sorted(set(actual_issue_files) - registry_issue_files):
        errors.append(f"Issueファイルがregistryにありません: {missing}")
    for missing in sorted(registry_issue_files - set(actual_issue_files)):
        errors.append(f"registryのIssueファイルがactual treeにありません: {missing}")

    for entry in adrs:
        if not ADR_ID_RE.fullmatch(entry.id):
            errors.append(f"ADR IDが4桁規則に違反しています: {entry.id}")
        if entry.status not in ALLOWED_ADR_STATUSES:
            errors.append(f"ADR Statusが規定値ではありません: {entry.id}: {entry.status}")
        path = repo_root / entry.file
        if not path.is_file():
            continue
        match = ADR_FILE_RE.fullmatch(path.name)
        if not match:
            errors.append(f"ADRファイル名が規則に違反しています: {entry.file}")
        elif f"ADR-{match.group(1)}" != entry.id:
            errors.append(f"ADRファイル名とIDが一致しません: {entry.id}: {entry.file}")
        heading_id, document_status = markdown_meta(path)
        if heading_id != entry.id:
            errors.append(f"ADR本文IDとregistryが一致しません: {entry.file}: heading={heading_id!r}, registry={entry.id}")
        if document_status != entry.status:
            errors.append(f"ADR Statusとregistryが一致しません: {entry.id}: document={document_status!r}, registry={entry.status!r}")
        for issue_id in entry.related_issues:
            if not ISSUE_ID_RE.fullmatch(issue_id):
                errors.append(f"ADRのrelated_issuesが6桁Issue IDではありません: {entry.id}: {issue_id}")
            elif issue_id not in issue_by_id:
                errors.append(f"ADRが存在しないIssueを参照しています: {entry.id} -> {issue_id}")

    for entry in issues:
        if not ISSUE_ID_RE.fullmatch(entry.id):
            errors.append(f"Issue IDが6桁規則に違反しています: {entry.id}")
        if entry.status not in ALLOWED_ISSUE_STATUSES:
            errors.append(f"Issue Statusが規定値ではありません: {entry.id}: {entry.status}")
        if entry.priority < 1:
            errors.append(f"Issue Priorityは1以上である必要があります: {entry.id}: {entry.priority}")
        path = repo_root / entry.file
        if not path.is_file():
            continue
        match = ISSUE_FILE_RE.fullmatch(path.name)
        if not match:
            errors.append(f"Issueファイル名が規則に違反しています: {entry.file}")
        elif f"ISSUE-{match.group(1)}" != entry.id:
            errors.append(f"Issueファイル名とIDが一致しません: {entry.id}: {entry.file}")
        heading_id, document_status = markdown_meta(path)
        if heading_id != entry.id:
            errors.append(f"Issue本文IDとregistryが一致しません: {entry.file}: heading={heading_id!r}, registry={entry.id}")
        if document_status != entry.status:
            errors.append(f"Issue Statusとregistryが一致しません: {entry.id}: document={document_status!r}, registry={entry.status!r}")
        for adr_id in entry.related_adrs:
            if not ADR_ID_RE.fullmatch(adr_id):
                errors.append(f"Issueのrelated_adrsが4桁ADR IDではありません: {entry.id}: {adr_id}")
            elif adr_id not in adr_by_id:
                errors.append(f"Issueが存在しないADRを参照しています: {entry.id} -> {adr_id}")

    if errors:
        print("plan registry integrity check: FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"plan registry integrity check: PASS ({len(adrs)} ADRs, {len(issues)} Issues)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
