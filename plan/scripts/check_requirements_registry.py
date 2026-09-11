#!/usr/bin/env python3
"""SEI current Requirements / Acceptance Scenario registry checker.

This checker validates the current Markdown registries without treating Markdown
or this script as semantic authority. The normative rules come from ADR-0020
and the current Requirements documents.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

REQ_ID_RE = re.compile(r"REQ-\d{4}")
SCN_ID_RE = re.compile(r"SCN-\d{4}")
REQ_HEADING_RE = re.compile(r"^##\s+(REQ-\d{4})\b", re.MULTILINE)
SCN_HEADING_RE = re.compile(r"^##\s+(SCN-\d{4})\b", re.MULTILINE)
REQ_TABLE_RE = re.compile(r"^\|\s*(REQ-\d{4})\s*\|", re.MULTILINE)
SCN_TABLE_ROW_RE = re.compile(
    r"^\|\s*(SCN-\d{4})\s*\|([^\n]*)$", re.MULTILINE
)
HISTORICAL_ID_RE = re.compile(r"SEI-(?:PR|NFR|AS)-\d+")
MILESTONE_ID_RE = re.compile(r"(?:M\d+[-_/])?(?:REQ|SCN)-\d{4}")

ALLOWED_REQUIREMENT_STATUS = {
    "Proposed",
    "Accepted",
    "Rejected",
    "Superseded",
    "Deprecated",
}
ALLOWED_ACCEPTANCE_STATE = {
    "Satisfied",
    "Partially Satisfied",
    "Not Satisfied",
    "Not Yet Verified",
    "Not Applicable",
}
ALLOWED_VALUE_AXES = {f"V{i}" for i in range(1, 9)}


@dataclass
class Finding:
    code: str
    message: str


@dataclass
class Report:
    schema: str
    passed: bool
    requirement_count: int
    scenario_count: int
    findings: list[Finding]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["findings"] = [asdict(item) for item in self.findings]
        return data


def _duplicates(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    dup: set[str] = set()
    for value in values:
        if value in seen:
            dup.add(value)
        seen.add(value)
    return dup


def _split_sections(text: str, heading_re: re.Pattern[str]) -> dict[str, str]:
    matches = list(heading_re.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1)] = text[start:end]
    return sections


def _parse_axes(value: str) -> set[str]:
    return set(re.findall(r"\bV\d+\b", value))


def _expand_requirement_cell(cell: str) -> set[str]:
    """Expand `REQ-0002, 0006, 0010` style references from a scenario table cell."""
    refs = set(REQ_ID_RE.findall(cell))
    if not refs:
        return refs
    for digits in re.findall(r"(?<!REQ-)(?<!\d)(\d{4})(?!\d)", cell):
        refs.add(f"REQ-{digits}")
    return refs


def validate(requirements_text: str, scenarios_text: str) -> Report:
    findings: list[Finding] = []

    req_headings = REQ_HEADING_RE.findall(requirements_text)
    scn_headings = SCN_HEADING_RE.findall(scenarios_text)
    req_table = REQ_TABLE_RE.findall(requirements_text)

    scn_table_rows = SCN_TABLE_ROW_RE.findall(scenarios_text)
    scn_table = [row[0] for row in scn_table_rows]

    for duplicate in sorted(_duplicates(req_headings)):
        findings.append(Finding("duplicate-requirement-id", f"Requirement heading is duplicated: {duplicate}"))
    for duplicate in sorted(_duplicates(scn_headings)):
        findings.append(Finding("duplicate-scenario-id", f"Scenario heading is duplicated: {duplicate}"))
    for duplicate in sorted(_duplicates(req_table)):
        findings.append(Finding("duplicate-requirement-table-id", f"Requirement table ID is duplicated: {duplicate}"))
    for duplicate in sorted(_duplicates(scn_table)):
        findings.append(Finding("duplicate-scenario-table-id", f"Scenario table ID is duplicated: {duplicate}"))

    req_ids = set(req_headings)
    scn_ids = set(scn_headings)

    if set(req_table) != req_ids:
        missing_in_table = sorted(req_ids - set(req_table))
        missing_in_body = sorted(set(req_table) - req_ids)
        if missing_in_table:
            findings.append(Finding("requirement-table-missing", f"Requirement IDs missing from summary table: {', '.join(missing_in_table)}"))
        if missing_in_body:
            findings.append(Finding("requirement-body-missing", f"Requirement table IDs missing from body: {', '.join(missing_in_body)}"))

    if set(scn_table) != scn_ids:
        missing_in_table = sorted(scn_ids - set(scn_table))
        missing_in_body = sorted(set(scn_table) - scn_ids)
        if missing_in_table:
            findings.append(Finding("scenario-table-missing", f"Scenario IDs missing from summary table: {', '.join(missing_in_table)}"))
        if missing_in_body:
            findings.append(Finding("scenario-body-missing", f"Scenario table IDs missing from body: {', '.join(missing_in_body)}"))

    req_sections = _split_sections(requirements_text, REQ_HEADING_RE)
    for req_id, section in req_sections.items():
        status_match = re.search(r"^\*\*Status:\*\*\s*([^\n]+?)\s*$", section, re.MULTILINE)
        if not status_match:
            findings.append(Finding("requirement-status-missing", f"{req_id} has no Status metadata"))
        else:
            status = status_match.group(1).strip()
            if status not in ALLOWED_REQUIREMENT_STATUS:
                findings.append(Finding("requirement-status-invalid", f"{req_id} uses unsupported status: {status}"))

        value_match = re.search(r"^\*\*Value:\*\*\s*([^\n]+?)\s*$", section, re.MULTILINE)
        if value_match:
            axes = _parse_axes(value_match.group(1))
            invalid = sorted(axis for axis in axes if axis not in ALLOWED_VALUE_AXES)
            if invalid:
                findings.append(Finding("requirement-value-axis-invalid", f"{req_id} uses invalid Value Axis: {', '.join(invalid)}"))
        else:
            findings.append(Finding("requirement-value-missing", f"{req_id} has no Value metadata"))

        related_match = re.search(r"^\*\*Related Scenarios:\*\*\s*([^\n]+?)\s*$", section, re.MULTILINE)
        if related_match:
            for scn_id in sorted(set(SCN_ID_RE.findall(related_match.group(1)))):
                if scn_id not in scn_ids:
                    findings.append(Finding("requirement-scenario-reference-missing", f"{req_id} refers to missing scenario {scn_id}"))

        for line in section.splitlines():
            if re.match(r"^-\s*(?:Design|Executable|Release|Operational)(?:\s*/[^:]+)?:", line):
                states = re.findall(r"\*\*([^*]+)\*\*", line)
                for state in states:
                    if state.strip() not in ALLOWED_ACCEPTANCE_STATE:
                        findings.append(Finding("requirement-acceptance-state-invalid", f"{req_id} uses unsupported Acceptance state: {state.strip()}"))

    for scn_id, row_text in scn_table_rows:
        columns = [part.strip() for part in row_text.split("|")]
        if len(columns) >= 3:
            axes = _parse_axes(columns[1])
            invalid = sorted(axis for axis in axes if axis not in ALLOWED_VALUE_AXES)
            if invalid:
                findings.append(Finding("scenario-value-axis-invalid", f"{scn_id} uses invalid Value Axis: {', '.join(invalid)}"))
            for req_id in sorted(_expand_requirement_cell(columns[2])):
                if req_id not in req_ids:
                    findings.append(Finding("scenario-requirement-reference-missing", f"{scn_id} refers to missing requirement {req_id}"))

    scn_sections = _split_sections(scenarios_text, SCN_HEADING_RE)
    for scn_id, section in scn_sections.items():
        for req_id in sorted(set(REQ_ID_RE.findall(section))):
            if req_id not in req_ids:
                findings.append(Finding("scenario-requirement-reference-missing", f"{scn_id} refers to missing requirement {req_id}"))
        for line in section.splitlines():
            if re.match(r"^-\s*(?:Design|Executable|Release|Operational)(?:\s*/[^:]+)?:", line):
                states = re.findall(r"\*\*([^*]+)\*\*", line)
                for state in states:
                    if state.strip() not in ALLOWED_ACCEPTANCE_STATE:
                        findings.append(Finding("scenario-acceptance-state-invalid", f"{scn_id} uses unsupported Acceptance state: {state.strip()}"))

    # Historical IDs may appear in explanatory prose, but they must not be used as
    # current canonical table or heading IDs.
    for line in requirements_text.splitlines():
        if line.startswith("|") and HISTORICAL_ID_RE.search(line):
            findings.append(Finding("historical-id-in-current-requirement-table", f"Historical ID appears in current Requirement table: {line.strip()}"))
    for line in scenarios_text.splitlines():
        if line.startswith("|") and HISTORICAL_ID_RE.search(line):
            findings.append(Finding("historical-id-in-current-scenario-table", f"Historical ID appears in current Scenario table: {line.strip()}"))

    return Report(
        schema="sei.requirements-registry-conformance/v1",
        passed=not findings,
        requirement_count=len(req_ids),
        scenario_count=len(scn_ids),
        findings=findings,
    )


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check SEI current Requirements / Scenario registry consistency")
    parser.add_argument("--requirements", type=Path, help="Path to PRODUCT_REQUIREMENTS.md")
    parser.add_argument("--scenarios", type=Path, help="Path to ACCEPTANCE_SCENARIOS.md")
    parser.add_argument("--json-out", type=Path, help="Optional path for a JSON report")
    args = parser.parse_args()

    root = _default_repo_root()
    requirements_path = args.requirements or root / "requirements" / "PRODUCT_REQUIREMENTS.md"
    scenarios_path = args.scenarios or root / "requirements" / "ACCEPTANCE_SCENARIOS.md"

    report = validate(
        requirements_path.read_text(encoding="utf-8"),
        scenarios_path.read_text(encoding="utf-8"),
    )

    payload = report.to_dict()
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if report.passed:
        print(f"PASS: {report.requirement_count} requirements / {report.scenario_count} scenarios")
        return 0

    print(f"FAIL: {len(report.findings)} finding(s)", file=sys.stderr)
    for finding in report.findings:
        print(f"- [{finding.code}] {finding.message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
