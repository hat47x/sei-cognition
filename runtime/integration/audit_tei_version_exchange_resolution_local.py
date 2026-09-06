#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

import audit_tei_version_exchange_resolution as base_audit
import verify_tei_execution_source_identity as source_identity

SCHEMA = "soza.tei-version-exchange-local-resolution-audit/v1"
CHECKOUT_PREPARATION_SCHEMA = "soza.tei-revision-b-checkout-preparation/v1"
LOCAL_ACQUISITION_MODE = "prepositioned_local_checkout"
STOP_LINE = (
    "local acquisition boundary verified + resolution audit candidate "
    "!= ISSUE-000072 automatically Resolved "
    "!= Stable Requirement change != Universal Contract change"
)


def _read_preparation_report(
    report_path: Path | None,
    revision_b_source_repo: Path,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    if report_path is None:
        return None, {
            "observed": False,
            "note": (
                "checkout preparation reportは未指定です。current exact-B checkout identityは"
                "独立再検証しますが、checkout生成履歴そのものは主張しません。"
            ),
        }

    try:
        resolved, report = base_audit._read_json(
            report_path,
            "TEI revision B checkout preparation report",
        )
    except Exception as exc:
        raise ValueError(
            f"checkout preparation reportを検証できません: {exc}"
        ) from exc

    mismatches: dict[str, Any] = {}
    expected_pairs = {
        "schema": CHECKOUT_PREPARATION_SCHEMA,
        "result": "prepared_verified",
        "revision": source_identity.REVISION_B,
        "detachedHead": True,
        "sourceHeadAndStatusUnchanged": True,
        "sourceObjectDatabaseSelfContained": True,
        "outputObjectDatabaseSelfContained": True,
        "prePublishIdentityVerified": True,
    }
    for key, expected in expected_pairs.items():
        if report.get(key) != expected:
            mismatches[key] = {"expected": expected, "actual": report.get(key)}

    output_repository = report.get("outputRepository")
    try:
        observed_output = (
            Path(str(output_repository)).expanduser().resolve(strict=True)
            if output_repository is not None
            else None
        )
    except OSError as exc:
        mismatches["outputRepository"] = {
            "expected": str(revision_b_source_repo),
            "actual": output_repository,
            "error": str(exc),
        }
        observed_output = None

    if observed_output != revision_b_source_repo:
        mismatches["outputRepository"] = {
            "expected": str(revision_b_source_repo),
            "actual": None if observed_output is None else str(observed_output),
        }

    verification = report.get("verification")
    if not isinstance(verification, dict):
        mismatches["verification"] = {
            "expected": "object",
            "actual": type(verification).__name__,
        }
    else:
        if verification.get("head") != source_identity.REVISION_B:
            mismatches["verification.head"] = {
                "expected": source_identity.REVISION_B,
                "actual": verification.get("head"),
            }
        for key in ("revisionBExactHead", "worktreeCleanWithinBoundary"):
            if verification.get(key) is not True:
                mismatches[f"verification.{key}"] = {
                    "expected": True,
                    "actual": verification.get(key),
                }

    if mismatches:
        raise ValueError(
            "checkout preparation provenanceがfixed local acquisition境界と一致しません: "
            + json.dumps(mismatches, ensure_ascii=False, sort_keys=True)
        )

    return report, {
        "observed": True,
        "report": str(resolved),
        "schema": report.get("schema"),
        "cloneMode": report.get("cloneMode"),
        "sourceObjectDatabaseSelfContained": report.get(
            "sourceObjectDatabaseSelfContained"
        ),
        "outputObjectDatabaseSelfContained": report.get(
            "outputObjectDatabaseSelfContained"
        ),
    }


def _local_boundary_criterion(
    axis: dict[str, Any],
    revision_b_source_repo: Path,
    checkout_preparation_report: Path | None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    try:
        source_repo = revision_b_source_repo.expanduser().resolve(strict=True)
        verification = source_identity.verify_repository(
            source_repo,
            expected_head=source_identity.REVISION_B,
        )
        preparation_report, preparation = _read_preparation_report(
            checkout_preparation_report,
            source_repo,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return base_audit._criterion(
            6,
            base_audit.BLOCKED,
            "local prepositioned revision B acquisition境界を再検証できません",
            acquisitionMode=LOCAL_ACQUISITION_MODE,
            credentialRequirement="not_applicable",
            error=str(exc),
        ), None

    return base_audit._criterion(
        6,
        base_audit.SATISFIED,
        (
            "prepositioned local checkout acquisition / credential非依存 / "
            "exact-B artifact identityとexact-A fixed input acquisitionを分離して追跡できます"
        ),
        sourceAcquisition={
            "mode": LOCAL_ACQUISITION_MODE,
            "repositoryRoot": str(source_repo),
            "sourceCommit": verification.get("head"),
            "credentialRequirement": "not_applicable",
            "currentCanonicalSourceVerification": {
                "revisionBExactHead": verification.get("revisionBExactHead"),
                "worktreeCleanWithinBoundary": verification.get(
                    "worktreeCleanWithinBoundary"
                ),
                "executionSourceObjects": verification.get(
                    "executionSourceObjects"
                ),
            },
            "checkoutPreparationProvenance": preparation,
        },
        referenceInputAcquisition=axis["referenceInputAcquisition"],
    ), preparation_report


def _recompute_resolution(result: dict[str, Any]) -> dict[str, Any]:
    criteria = result.get("criteria")
    if not isinstance(criteria, dict):
        raise ValueError("base resolution audit criteriaがありません")

    automated: list[dict[str, Any]] = []
    for number in range(1, 7):
        item = criteria.get(str(number))
        if not isinstance(item, dict):
            raise ValueError(f"base resolution audit criterion {number}がありません")
        automated.append(item)

    blocked = [
        item["criterion"]
        for item in automated
        if item.get("status") != base_audit.SATISFIED
    ]
    candidate = not blocked
    result["result"] = "manual_review_required" if candidate else "blocked"
    result["resolutionCandidate"] = candidate
    result["autoResolvePermitted"] = False
    result["automatedCriteria"] = {
        "scope": [1, 2, 3, 4, 5, 6],
        "satisfied": [
            item["criterion"]
            for item in automated
            if item.get("status") == base_audit.SATISFIED
        ],
        "blockedOrManual": blocked,
    }
    return result


def audit_local_resolution(
    canonical_report: Path,
    *,
    revision_b_source_repo: Path,
    soza_repo_root: Path,
    historical_a_bundle: Path | None = None,
    checkout_preparation_report: Path | None = None,
    expected_soza_head: str | None = None,
) -> dict[str, Any]:
    result = base_audit.audit_resolution(
        canonical_report,
        soza_repo_root=soza_repo_root,
        historical_a_bundle=historical_a_bundle,
        github_wrapper_report=None,
        expected_soza_head=expected_soza_head,
    )

    canonical = result.get("canonicalReport")
    if not isinstance(canonical, dict):
        raise ValueError("base resolution audit canonicalReportがありません")
    axis = canonical.get("comparisonAxis")
    if not isinstance(axis, dict):
        raise ValueError("base resolution audit comparisonAxisがありません")

    criterion6, preparation_report = _local_boundary_criterion(
        axis,
        revision_b_source_repo,
        checkout_preparation_report,
    )
    criteria = result.get("criteria")
    if not isinstance(criteria, dict):
        raise ValueError("base resolution audit criteriaがありません")
    criteria["6"] = criterion6

    result = _recompute_resolution(result)
    result["schema"] = SCHEMA
    result["baseResolutionAuditSchema"] = base_audit.SCHEMA
    result["githubAcquisitionWrapperObserved"] = False
    result["localPrepositionedSourceObserved"] = True
    result["localAcquisitionMode"] = LOCAL_ACQUISITION_MODE
    result["checkoutPreparationReportObserved"] = preparation_report is not None
    result["stopLine"] = STOP_LINE
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "local Git object database等からprepositionedされたexact revision B checkoutを"
            "canonical version-exchange runnerへ渡したactual runについて、既存Resolution auditへ"
            "local acquisition boundaryを差し込みます。credentialはnot applicableとして分離し、"
            "Issueを自動closeしません。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--canonical-report", required=True, type=Path)
    parser.add_argument("--revision-b-source-repo", required=True, type=Path)
    parser.add_argument("--historical-a-bundle", type=Path)
    parser.add_argument("--checkout-preparation-report", type=Path)
    parser.add_argument(
        "--soza-repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--expected-soza-head")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = audit_local_resolution(
            args.canonical_report,
            revision_b_source_repo=args.revision_b_source_repo,
            soza_repo_root=args.soza_repo_root,
            historical_a_bundle=args.historical_a_bundle,
            checkout_preparation_report=args.checkout_preparation_report,
            expected_soza_head=args.expected_soza_head,
        )
        output = None
        if args.output is not None:
            output = base_audit._prepare_output(args.output, args.soza_repo_root)
            base_audit._write_json_atomic(output, result)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"TEI local version exchange resolution audit rejected: {exc}")
        return 1

    if args.json or output is None:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print(f"TEI local version exchange resolution audit: {result['result']}")
        print(
            f"- resolution candidate: "
            f"{str(result['resolutionCandidate']).lower()}"
        )
        print(f"- local acquisition mode: {result['localAcquisitionMode']}")
        print(f"- output: {output}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
