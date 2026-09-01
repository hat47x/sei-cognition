#!/usr/bin/env python3
"""Validate SOZA v0.1.0 release-candidate policy and emit a bound report.

This checker does not create or prove Release Evidence. It runs last in the
integrated candidate workflow after the semantic/executable sub-gates have
already succeeded, then binds that candidate result to the checked Git commit
and tree.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "release" / "v0.1.0" / "release-candidate.json"

EXPECTED_SCHEMA = "soza.release-candidate/v1"
EXPECTED_VERSION = "0.1.0"
EXPECTED_REPOSITORY = "hat47x/soza"
EXPECTED_SCOPE = "semantic-development-baseline-source-release"

REQUIRED_GATE_SET = {
    "plan-integrity",
    "requirements-registry",
    "contract-conformance",
    "representation-profile-fixtures",
    "jcs-go-probe",
    "semantic-runtime-conformance",
    "v6-v7-projection-evaluation",
    "release-candidate-policy",
}

REQUIRED_PATH_ANCHORS = {
    "README.md",
    "product/value/SOZA_PRODUCT_VALUE.md",
    "product/value/SOZA_VALUE_ACCEPTANCE.md",
    "requirements/PRODUCT_REQUIREMENTS.md",
    "requirements/ACCEPTANCE_SCENARIOS.md",
    "architecture/SOZA_REFERENCE_ARCHITECTURE.md",
    "contracts/CONTRACT_CATALOG.md",
    "contracts/profiles/SOZA_JCS_SHA256_PROFILE_v1alpha1.md",
    "contracts/profiles/SOZA_RAW_BYTES_SHA256_PROFILE_v1alpha1.md",
    "contracts/schemas/v1alpha1",
    "fixtures/contracts/v1alpha1",
    "runtime/go",
    "evaluation/v6-v7",
    "plan/registry.yaml",
    "release/v0.1.0/RELEASE_ACCEPTANCE.md",
}

EXPECTED_PROHIBITED_STATUSES = {"Open", "In Progress", "Blocked"}
EXPECTED_FALSE_CLAIMS = {
    "release_evidence",
    "operational_evidence",
    "adoption_outcome_evidence",
    "production_provider_integration",
    "production_storage_integration",
    "historical_m47_profile_verified",
}

ISSUE_ROW = re.compile(
    r"^\s*- \{id: (?P<id>ISSUE-\d{6}), file: (?P<file>[^,]+), "
    r"status: (?P<status>[^,]+), priority: (?P<priority>\d+), "
    r"related_adrs: \[(?P<adrs>[^\]]*)\]\}\s*$"
)
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"candidate configuration not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"candidate configuration is invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        fail("candidate configuration root must be an object")
    return value


def require_string(config: dict[str, Any], key: str, expected: str) -> None:
    value = config.get(key)
    if value != expected:
        fail(f"{key} = {value!r}, want {expected!r}")


def require_string_list(config: dict[str, Any], key: str) -> list[str]:
    value = config.get(key)
    if not isinstance(value, list) or not value or not all(isinstance(x, str) and x.strip() for x in value):
        fail(f"{key} must be a non-empty string array")
    if len(value) != len(set(value)):
        fail(f"{key} contains duplicates")
    return value


def check_required_paths(paths: list[str]) -> None:
    declared = set(paths)
    missing_anchors = sorted(REQUIRED_PATH_ANCHORS - declared)
    if missing_anchors:
        fail(f"required_paths dropped mandatory anchors: {missing_anchors}")

    missing_on_disk = [path for path in paths if not (ROOT / path).exists()]
    if missing_on_disk:
        fail(f"required_paths do not exist in candidate tree: {missing_on_disk}")


def parse_issue_statuses() -> dict[str, str]:
    registry = ROOT / "plan" / "registry.yaml"
    issues: dict[str, str] = {}
    for raw_line in registry.read_text(encoding="utf-8").splitlines():
        match = ISSUE_ROW.match(raw_line)
        if not match:
            continue
        issue_id = match.group("id")
        if issue_id in issues:
            fail(f"duplicate issue row in registry: {issue_id}")
        issues[issue_id] = match.group("status").strip()
    if not issues:
        fail("no issue rows parsed from plan/registry.yaml")
    return issues


def check_plan_policy(config: dict[str, Any]) -> list[str]:
    prohibited = set(require_string_list(config, "prohibited_plan_statuses"))
    if prohibited != EXPECTED_PROHIBITED_STATUSES:
        fail(
            "prohibited_plan_statuses must remain exactly "
            f"{sorted(EXPECTED_PROHIBITED_STATUSES)}, got {sorted(prohibited)}"
        )

    allowed_deferred = set(require_string_list(config, "allowed_deferred_issues"))
    issues = parse_issue_statuses()

    blockers = sorted(issue_id for issue_id, status in issues.items() if status in prohibited)
    if blockers:
        fail(f"release candidate has blocking Plan issues: {blockers}")

    unknown_statuses = sorted(
        (issue_id, status)
        for issue_id, status in issues.items()
        if status not in {"Resolved", "Deferred"}
    )
    if unknown_statuses:
        fail(f"release candidate has unsupported Plan statuses: {unknown_statuses}")

    observed_deferred = {issue_id for issue_id, status in issues.items() if status == "Deferred"}
    unapproved = sorted(observed_deferred - allowed_deferred)
    if unapproved:
        fail(f"Deferred issues are not approved by candidate policy: {unapproved}")

    stale_allowlist = sorted(allowed_deferred - observed_deferred)
    if stale_allowlist:
        fail(f"allowed_deferred_issues are not currently Deferred: {stale_allowlist}")

    return sorted(observed_deferred)


def check_gates(config: dict[str, Any]) -> list[str]:
    gates = require_string_list(config, "required_gates")
    gate_set = set(gates)
    if gate_set != REQUIRED_GATE_SET:
        missing = sorted(REQUIRED_GATE_SET - gate_set)
        unexpected = sorted(gate_set - REQUIRED_GATE_SET)
        fail(f"required_gates mismatch; missing={missing}, unexpected={unexpected}")
    return gates


def check_non_claims(config: dict[str, Any]) -> dict[str, bool]:
    claims = config.get("explicit_non_claims")
    if not isinstance(claims, dict):
        fail("explicit_non_claims must be an object")
    missing = sorted(EXPECTED_FALSE_CLAIMS - set(claims))
    if missing:
        fail(f"explicit_non_claims missing mandatory keys: {missing}")
    wrongly_true = sorted(key for key in EXPECTED_FALSE_CLAIMS if claims.get(key) is not False)
    if wrongly_true:
        fail(f"candidate must not claim these Evidence states: {wrongly_true}")
    if not all(isinstance(v, bool) for v in claims.values()):
        fail("explicit_non_claims values must be booleans")
    return {str(k): bool(v) for k, v in claims.items()}


def git_rev(spec: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", spec],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    value = result.stdout.strip()
    if not HEX40.fullmatch(value):
        fail(f"git rev-parse {spec!r} returned unexpected value {value!r}")
    return value


def build_report(config: dict[str, Any], gates: list[str], deferred: list[str]) -> dict[str, Any]:
    commit_sha = git_rev("HEAD")
    tree_sha = git_rev("HEAD^{tree}")
    return {
        "schema": "soza.release-candidate-report/v1",
        "version": EXPECTED_VERSION,
        "repository": EXPECTED_REPOSITORY,
        "release_scope": EXPECTED_SCOPE,
        "source_commit_sha": commit_sha,
        "source_tree_sha": tree_sha,
        "executed_gates": gates,
        "observed_allowed_deferred_issues": deferred,
        "candidate_gate_passed": True,
        "release_evidence": False,
        "operational_evidence": False,
        "adoption_outcome_evidence": False,
        "note": "Candidate gate PASS is release-preparation Executable Evidence, not Release Evidence.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    try:
        config = load_json(args.config)
        require_string(config, "schema", EXPECTED_SCHEMA)
        require_string(config, "version", EXPECTED_VERSION)
        require_string(config, "repository", EXPECTED_REPOSITORY)
        require_string(config, "release_scope", EXPECTED_SCOPE)

        github_repo = os.environ.get("GITHUB_REPOSITORY")
        if github_repo and github_repo != EXPECTED_REPOSITORY:
            fail(f"GITHUB_REPOSITORY = {github_repo!r}, want {EXPECTED_REPOSITORY!r}")

        required_paths = require_string_list(config, "required_paths")
        check_required_paths(required_paths)
        gates = check_gates(config)
        check_non_claims(config)
        deferred = check_plan_policy(config)
        report = build_report(config, gates, deferred)

        if args.report:
            report_path = args.report
            if not report_path.is_absolute():
                report_path = ROOT / report_path
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            print(f"release candidate report: {report_path}")

        print(
            "PASS: SOZA v0.1.0 release candidate policy; "
            f"commit={report['source_commit_sha']} tree={report['source_tree_sha']} "
            f"deferred={deferred}"
        )
        print("Release Evidence remains NOT VERIFIED until an actual release is created and bound.")
        return 0
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
