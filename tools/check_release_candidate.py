#!/usr/bin/env python3
"""SEIのversion別Release Candidate policyを検査し、候補commitへ結び付いたreportを生成する。

このcheckerが確認するのはrelease candidateの準備条件であり、actual Release Evidenceではない。
versionごとのsupported scope、required path、Plan snapshot、required gate、非主張範囲は独立policyとして扱い、
共通checkerを使うことを理由に異なるversionのrelease境界を混同しない。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "release" / "v0.1.0" / "release-candidate.json"
EXPECTED_SCHEMA = "sei.release-candidate/v1"
EXPECTED_REPOSITORY = "hat47x/sei-cognition"
# ADR-0031の3および5。改名前に記録されたEvidenceは旧identityと旧repository名を
# 持つため、読み取り側は双方を受け付ける。emit側は常に新しい名前だけを書く。
# これは暫定措置ではなく、記録済みEvidenceが存在する限り必要な恒久措置である。
LEGACY_SCHEMA = "soza.release-candidate/v1"
LEGACY_REPOSITORY = "hat47x/soza"
EXPECTED_PROHIBITED_STATUSES = {"Open", "In Progress", "Blocked"}

ISSUE_ROW = re.compile(
    r"^\s*- \{id: (?P<id>ISSUE-\d{6}), file: (?P<file>[^,]+), "
    r"status: (?P<status>[^,]+), priority: (?P<priority>\d+), "
    r"related_adrs: \[(?P<adrs>[^\]]*)\]\}\s*$"
)
ISSUE_ID = re.compile(r"^ISSUE-\d{6}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class VersionPolicy:
    release_scope: str
    required_gates: frozenset[str]
    required_path_anchors: frozenset[str]
    mandatory_false_claims: frozenset[str]


COMMON_GATES = frozenset({
    "plan-integrity",
    "requirements-registry",
    "contract-conformance",
    "representation-profile-fixtures",
    "jcs-go-probe",
    "semantic-runtime-conformance",
    "v6-v7-projection-evaluation",
    "release-candidate-policy",
})

COMMON_FALSE_CLAIMS = frozenset({
    "release_evidence",
    "operational_evidence",
    "adoption_outcome_evidence",
    "production_provider_integration",
    "production_storage_integration",
})

VERSION_POLICIES: dict[str, VersionPolicy] = {
    "0.1.0": VersionPolicy(
        release_scope="semantic-development-baseline-source-release",
        required_gates=COMMON_GATES,
        required_path_anchors=frozenset({
            "README.md",
            "product/value/SEI_PRODUCT_VALUE.md",
            "product/value/SEI_VALUE_ACCEPTANCE.md",
            "requirements/PRODUCT_REQUIREMENTS.md",
            "requirements/ACCEPTANCE_SCENARIOS.md",
            "architecture/SEI_REFERENCE_ARCHITECTURE.md",
            "contracts/CONTRACT_CATALOG.md",
            "contracts/profiles/SEI_JCS_SHA256_PROFILE_v1alpha1.md",
            "contracts/profiles/SEI_RAW_BYTES_SHA256_PROFILE_v1alpha1.md",
            "contracts/schemas/v1alpha1",
            "fixtures/contracts/v1alpha1",
            "runtime/go",
            "evaluation/v6-v7",
            "plan/registry.yaml",
            "release/v0.1.0/RELEASE_ACCEPTANCE.md",
        }),
        mandatory_false_claims=COMMON_FALSE_CLAIMS | {"historical_m47_profile_verified"},
    ),
    "0.2.0": VersionPolicy(
        release_scope="local-reference-product-baseline",
        required_gates=COMMON_GATES | {"local-reference-package"},
        required_path_anchors=frozenset({
            "README.md",
            "product/value/SEI_PRODUCT_VALUE.md",
            "product/value/SEI_VALUE_ACCEPTANCE.md",
            "product/value/SEI_VALUE_TRACEABILITY.md",
            "product/definition/SEI_PRODUCT_SHAPE.md",
            "product/definition/SEI_REALIZATION_PROVIDER_EXCHANGE.md",
            "product/interaction/SEI_PRODUCT_INTERACTION.md",
            "product/packaging/SEI_PRODUCT_PACKAGING.md",
            "product/security/SEI_PRODUCT_IDENTITY_ACCESS_COLLABORATION.md",
            "product/roadmap/SEI_PRODUCT_MILESTONES.md",
            "requirements/PRODUCT_REQUIREMENTS.md",
            "requirements/ACCEPTANCE_SCENARIOS.md",
            "requirements/PRODUCT_JOURNEY_COMPOSITION.md",
            "architecture/SEI_REFERENCE_ARCHITECTURE.md",
            "architecture/SEI_DEPLOYMENT_ARCHITECTURE.md",
            "architecture/SEI_PRODUCT_ACCESS_ARCHITECTURE.md",
            "contracts/CONTRACT_CATALOG.md",
            "contracts/cognitive-method/SEI_COGNITIVE_METHOD_v1alpha1.md",
            "contracts/schemas/v1alpha1",
            "fixtures/contracts/v1alpha1",
            "fixtures/external/e3a",
            "runtime/go",
            "runtime/package/reference",
            "evaluation/v6-v7",
            "plan/registry.yaml",
            "release/v0.2.0/RELEASE_ACCEPTANCE.md",
        }),
        mandatory_false_claims=COMMON_FALSE_CLAIMS | {
            "production_identity_security",
            "e3b_live_external_integration",
            "e4_operational_portability",
            "formal_platform_support_matrix",
        },
    ),
}


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


def require_string(config: dict[str, Any], key: str) -> str:
    value = config.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(f"{key} must be a non-empty string")
    return value


def require_exact_string(config: dict[str, Any], key: str, expected: str) -> None:
    value = config.get(key)
    if value != expected:
        fail(f"{key} = {value!r}, want {expected!r}")


def require_renamed_string(config: dict[str, Any], key: str, expected: str, legacy: str) -> None:
    """ADR-0031の改名を跨いで読む。新旧どちらのidentityでも受け付ける。"""
    value = config.get(key)
    if value not in (expected, legacy):
        fail(f"{key} = {value!r}, want {expected!r} (or pre-rename {legacy!r})")


def require_string_list(config: dict[str, Any], key: str) -> list[str]:
    value = config.get(key)
    if not isinstance(value, list) or not value or not all(isinstance(x, str) and x.strip() for x in value):
        fail(f"{key} must be a non-empty string array")
    if len(value) != len(set(value)):
        fail(f"{key} contains duplicates")
    return value


def version_policy(config: dict[str, Any]) -> tuple[str, VersionPolicy]:
    version = require_string(config, "version")
    policy = VERSION_POLICIES.get(version)
    if policy is None:
        fail(f"unsupported release candidate version: {version!r}")
    require_exact_string(config, "release_scope", policy.release_scope)
    return version, policy


def _swap_filename_prefix(path: str, before: str, after: str) -> str:
    head, _, tail = path.rpartition("/")
    if not tail.startswith(before):
        return path
    renamed = f"{after}{tail[len(before):]}"
    return f"{head}/{renamed}" if head else renamed


def pre_rename_path(path: str) -> str:
    """ADR-0031の文書filename mappingを逆向きにたどる。

    改名前に記録されたrelease candidateは`SOZA_`接頭辞のpathを宣言している。
    当時のrecordを書き換えないため、読み取り側で当時のpathへ戻して照合する。
    """
    return _swap_filename_prefix(path, "SEI_", "SOZA_")


def post_rename_path(path: str) -> str:
    """ADR-0031の文書filename mappingを順方向にたどる。

    改名前のrecordが宣言するpathを、current treeに実在するpathへ解決する。
    """
    return _swap_filename_prefix(path, "SOZA_", "SEI_")


def check_required_paths(paths: list[str], policy: VersionPolicy) -> None:
    declared = set(paths)
    missing_anchors = sorted(
        anchor
        for anchor in policy.required_path_anchors
        if anchor not in declared and pre_rename_path(anchor) not in declared
    )
    if missing_anchors:
        fail(f"required_paths dropped mandatory anchors: {missing_anchors}")

    missing_on_disk = [
        path
        for path in paths
        if not (ROOT / path).exists() and not (ROOT / post_rename_path(path)).exists()
    ]
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


def check_plan_policy(config: dict[str, Any]) -> tuple[list[str], str]:
    prohibited = set(require_string_list(config, "prohibited_plan_statuses"))
    if prohibited != EXPECTED_PROHIBITED_STATUSES:
        fail(
            "prohibited_plan_statuses must remain exactly "
            f"{sorted(EXPECTED_PROHIBITED_STATUSES)}, got {sorted(prohibited)}"
        )

    scope_max = require_string(config, "plan_issue_scope_max")
    if not ISSUE_ID.fullmatch(scope_max):
        fail(f"plan_issue_scope_max must be an ISSUE-###### id, got {scope_max!r}")

    allowed_deferred = set(require_string_list(config, "allowed_deferred_issues"))
    issues = parse_issue_statuses()
    if scope_max not in issues:
        fail(f"plan_issue_scope_max is not present in plan registry: {scope_max}")

    scoped_issues = {
        issue_id: status
        for issue_id, status in issues.items()
        if issue_id <= scope_max
    }

    out_of_scope_allowed = sorted(issue_id for issue_id in allowed_deferred if issue_id > scope_max)
    if out_of_scope_allowed:
        fail(f"allowed_deferred_issues exceed plan_issue_scope_max: {out_of_scope_allowed}")

    blockers = sorted(
        issue_id
        for issue_id, status in scoped_issues.items()
        if status in prohibited
    )
    if blockers:
        fail(f"release candidate has blocking Plan issues within {scope_max}: {blockers}")

    unknown_statuses = sorted(
        (issue_id, status)
        for issue_id, status in scoped_issues.items()
        if status not in {"Resolved", "Deferred"}
    )
    if unknown_statuses:
        fail(f"release candidate has unsupported Plan statuses within {scope_max}: {unknown_statuses}")

    observed_deferred = {
        issue_id
        for issue_id, status in scoped_issues.items()
        if status == "Deferred"
    }
    unapproved = sorted(observed_deferred - allowed_deferred)
    if unapproved:
        fail(f"Deferred issues are not approved by candidate policy: {unapproved}")

    stale_allowlist = sorted(allowed_deferred - observed_deferred)
    if stale_allowlist:
        fail(f"allowed_deferred_issues are not currently Deferred: {stale_allowlist}")

    return sorted(observed_deferred), scope_max


def check_gates(config: dict[str, Any], policy: VersionPolicy) -> list[str]:
    gates = require_string_list(config, "required_gates")
    gate_set = set(gates)
    if gate_set != policy.required_gates:
        missing = sorted(policy.required_gates - gate_set)
        unexpected = sorted(gate_set - policy.required_gates)
        fail(f"required_gates mismatch; missing={missing}, unexpected={unexpected}")
    return gates


def check_non_claims(config: dict[str, Any], policy: VersionPolicy) -> dict[str, bool]:
    claims = config.get("explicit_non_claims")
    if not isinstance(claims, dict):
        fail("explicit_non_claims must be an object")
    missing = sorted(policy.mandatory_false_claims - set(claims))
    if missing:
        fail(f"explicit_non_claims missing mandatory keys: {missing}")
    wrongly_true = sorted(key for key in policy.mandatory_false_claims if claims.get(key) is not False)
    if wrongly_true:
        fail(f"candidate must not claim these Evidence states: {wrongly_true}")
    if not all(isinstance(value, bool) for value in claims.values()):
        fail("explicit_non_claims values must be booleans")
    return {str(key): bool(value) for key, value in claims.items()}


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


def build_report(
    *,
    version: str,
    policy: VersionPolicy,
    gates: list[str],
    deferred: list[str],
    plan_issue_scope_max: str,
    non_claims: dict[str, bool],
) -> dict[str, Any]:
    return {
        "schema": "sei.release-candidate-report/v1",
        "version": version,
        "repository": EXPECTED_REPOSITORY,
        "release_scope": policy.release_scope,
        "source_commit_sha": git_rev("HEAD"),
        "source_tree_sha": git_rev("HEAD^{tree}"),
        "plan_issue_scope_max": plan_issue_scope_max,
        "executed_gates": gates,
        "observed_allowed_deferred_issues": deferred,
        "candidate_gate_passed": True,
        "explicit_non_claims": non_claims,
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
        require_renamed_string(config, "schema", EXPECTED_SCHEMA, LEGACY_SCHEMA)
        require_renamed_string(config, "repository", EXPECTED_REPOSITORY, LEGACY_REPOSITORY)
        version, policy = version_policy(config)

        github_repo = os.environ.get("GITHUB_REPOSITORY")
        if github_repo and github_repo != EXPECTED_REPOSITORY:
            fail(f"GITHUB_REPOSITORY = {github_repo!r}, want {EXPECTED_REPOSITORY!r}")

        paths = require_string_list(config, "required_paths")
        check_required_paths(paths, policy)
        gates = check_gates(config, policy)
        non_claims = check_non_claims(config, policy)
        deferred, plan_issue_scope_max = check_plan_policy(config)
        report = build_report(
            version=version,
            policy=policy,
            gates=gates,
            deferred=deferred,
            plan_issue_scope_max=plan_issue_scope_max,
            non_claims=non_claims,
        )

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
            f"PASS: SEI v{version} release candidate policy; "
            f"commit={report['source_commit_sha']} tree={report['source_tree_sha']} "
            f"plan_scope<={plan_issue_scope_max} deferred={deferred}"
        )
        print("Release Evidence remains NOT VERIFIED until an actual release is created and bound.")
        return 0
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
