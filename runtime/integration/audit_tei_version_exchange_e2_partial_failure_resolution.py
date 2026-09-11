#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import audit_tei_version_exchange_resolution as base_audit
import prepare_tei_revision_b_source as github_source
import prepare_tei_revision_b_source_from_snapshot as snapshot_source
import run_tei_revision_b_e2_from_github as e2_partial
import verify_tei_execution_source_identity as source_identity

SCHEMA = "soza.tei-version-exchange-e2-partial-failure-resolution-audit/v1"
STOP_LINE = (
    "E2 partial failure resolution audit != ISSUE-000072 Resolved "
    "!= revision B replacement != Stable Requirement change != Universal Contract change"
)


def _validate_partial_failure(report: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if report.get("schema") != e2_partial.SCHEMA:
        raise ValueError(
            "E2 partial report schemaが期待値と一致しません: "
            f"expected={e2_partial.SCHEMA} actual={report.get('schema')!r}"
        )
    if report.get("result") != "e2_failed":
        raise ValueError(
            "このauditはactual E2 partial failure report専用です: "
            f"actualResult={report.get('result')!r}"
        )
    if report.get("e2") is not None or report.get("e3") is not None:
        raise ValueError("E2 failure reportでe2/e3 payloadを成功扱いできません")

    axis = report.get("comparisonAxis")
    if not isinstance(axis, dict):
        raise ValueError("E2 partial report comparisonAxisがありません")
    expected_axis = {
        "buildSourceCommit": source_identity.REVISION_B,
        "referenceInputSourceCommit": source_identity.REVISION_A,
    }
    for key, value in expected_axis.items():
        if axis.get(key) != value:
            raise ValueError(
                "E2 partial comparison axisが固定値と一致しません: "
                f"field={key} expected={value} actual={axis.get(key)!r}"
            )
    acquisition = axis.get("referenceInputAcquisition")
    if acquisition not in {"git_checkout", "historical_evidence_bundle"}:
        raise ValueError(f"referenceInputAcquisitionが未対応です: {acquisition!r}")
    if axis.get("e3IntentionallyNotRun") is not True:
        raise ValueError("E2 partial failure reportでE3 intentional non-run境界を確認できません")

    failure = report.get("failure")
    if not isinstance(failure, dict) or failure.get("stage") != "E2":
        raise ValueError("E2 partial failure reportのfailure.stageがE2ではありません")
    return axis, failure


def _source_boundary_criterion(
    report: dict[str, Any],
    axis: dict[str, Any],
) -> dict[str, Any]:
    source = report.get("sourceAcquisition")
    if not isinstance(source, dict):
        return base_audit._criterion(
            6,
            base_audit.BLOCKED,
            "E2 partial failure reportにsource acquisition Provenanceがありません",
        )

    mismatches: dict[str, Any] = {}
    expected = {
        "repository": github_source.GITHUB_REPOSITORY,
        "sourceCommit": source_identity.REVISION_B,
        "rootTree": github_source.REVISION_B_ROOT_TREE,
    }
    for key, value in expected.items():
        if source.get(key) != value:
            mismatches[key] = {"expected": value, "actual": source.get(key)}

    acquisition_mode = source.get("mode")
    if acquisition_mode not in {
        base_audit.CURRENT_GITHUB_ACQUISITION_MODE,
        "github_git_data_api",
    }:
        mismatches["sourceAcquisitionMode"] = {
            "expected": base_audit.CURRENT_GITHUB_ACQUISITION_MODE,
            "actual": acquisition_mode,
        }

    credential_source = source.get("credentialSource")
    if credential_source not in base_audit.ACCEPTED_CREDENTIAL_PROVENANCE:
        mismatches["credentialSource"] = {
            "expected": "environment provenance without credential value",
            "actual": credential_source,
        }

    canonical_source = source.get("canonicalSourceVerification")
    if not isinstance(canonical_source, dict):
        mismatches["canonicalSourceVerification"] = {
            "expected": "object",
            "actual": type(canonical_source).__name__,
        }
    else:
        for key in ("revisionBExactHead", "worktreeCleanWithinBoundary"):
            if canonical_source.get(key) is not True:
                mismatches[key] = {
                    "expected": True,
                    "actual": canonical_source.get(key),
                }

    transport = source.get("sourceTransport")
    transport_summary: dict[str, Any] | None = None
    if transport is not None:
        if not isinstance(transport, dict):
            mismatches["sourceTransport"] = {
                "expected": "object when present",
                "actual": type(transport).__name__,
            }
        else:
            transport_summary = {
                "mode": transport.get("mode"),
                "schema": transport.get("schema"),
                "sha256": transport.get("sha256"),
                "runtimeCredentialUsed": transport.get("runtimeCredentialUsed"),
            }
            if transport.get("mode") != snapshot_source.SNAPSHOT_TRANSPORT_MODE:
                mismatches["sourceTransport.mode"] = {
                    "expected": snapshot_source.SNAPSHOT_TRANSPORT_MODE,
                    "actual": transport.get("mode"),
                }
            if transport.get("runtimeCredentialUsed") is not False:
                mismatches["sourceTransport.runtimeCredentialUsed"] = {
                    "expected": False,
                    "actual": transport.get("runtimeCredentialUsed"),
                }

    if mismatches:
        return base_audit._criterion(
            6,
            base_audit.BLOCKED,
            "E2 partial failureのacquisition / credential / fixed-input Provenanceが固定境界と一致しません",
            mismatches=mismatches,
        )

    return base_audit._criterion(
        6,
        base_audit.BLOCKED,
        "source acquisition / credential / exact-B source / exact-A fixed-input境界は観測できましたが、actual executable / Evidence bundle identityが成立していないためcriterion 6は未完了です",
        observedSourceBoundaries={
            "mode": acquisition_mode,
            "repository": source.get("repository"),
            "sourceCommit": source.get("sourceCommit"),
            "rootTree": source.get("rootTree"),
            "credentialSource": credential_source,
            "sourceTransport": transport_summary,
            "referenceInputAcquisition": axis.get("referenceInputAcquisition"),
        },
        missingBoundary="actual_artifact_identity",
    )


def audit_partial_failure(
    partial_report: Path,
    *,
    soza_repo_root: Path,
    historical_a_bundle: Path | None = None,
    expected_soza_head: str | None = None,
) -> dict[str, Any]:
    report_path, report = base_audit._read_json(
        partial_report,
        "TEI revision B E2 partial failure report",
    )
    axis, failure = _validate_partial_failure(report)
    baseline = base_audit._verify_soza_baseline(soza_repo_root, expected_soza_head)

    c1, historical = base_audit._historical_a(historical_a_bundle)
    c2 = base_audit._criterion(
        2,
        base_audit.BLOCKED,
        "revision B actual E2がbundle生成前に停止しており、actual executable / fixed Evidence bundleのbinary / Provider Plan identityを記録できません",
        partialResult=report.get("result"),
        bundleArchive=report.get("bundleArchive"),
    )
    substage = failure.get("substage")
    if isinstance(substage, str) and substage:
        c3 = base_audit._criterion(
            3,
            base_audit.SATISFIED,
            "E2は不成立でしたがrepository-local external stageまで停止位置を判別できました",
            outcome="failed",
            substage=substage,
            failureType=failure.get("type"),
        )
    else:
        c3 = base_audit._criterion(
            3,
            base_audit.BLOCKED,
            "E2不成立の停止位置をrepository-local substageまで判別できません",
        )
    c4 = base_audit._criterion(
        4,
        base_audit.BLOCKED,
        "revision B actual E2が成立していないためE3 SEI Adapter compatibilityへ到達していません",
        e3IntentionallyNotRun=axis.get("e3IntentionallyNotRun"),
    )
    c5 = base_audit._a_unchanged(historical)
    c6 = _source_boundary_criterion(report, axis)
    c7 = base_audit._criterion(
        7,
        base_audit.MANUAL,
        "REQ-0001 / REQ-0007 / REQ-0021 / SCN-0014 / SCN-0018をpre-audit基準で最終再照合してください",
        hint=base_audit._reaudit_hint(report),
    )
    c8 = base_audit._criterion(
        8,
        base_audit.MANUAL,
        "自然な日本語を最重要視した最終意味監査が必要です",
    )

    criteria = [c1, c2, c3, c4, c5, c6, c7, c8]
    automated = criteria[:6]
    blocked = [
        item["criterion"]
        for item in automated
        if item["status"] != base_audit.SATISFIED
    ]
    candidate = not blocked
    return {
        "schema": SCHEMA,
        "result": "manual_review_required" if candidate else "blocked",
        "resolutionCandidate": candidate,
        "autoResolvePermitted": False,
        "partialE2FailureReport": {
            "path": str(report_path),
            "schema": report.get("schema"),
            "result": report.get("result"),
            "comparisonAxis": axis,
            "failure": {
                "stage": failure.get("stage"),
                "substage": failure.get("substage"),
                "type": failure.get("type"),
            },
        },
        "historicalAReverification": None if historical is None else {
            "sourceCommit": historical.get("sourceCommit"),
            "archive": historical.get("archive"),
            "archiveSha256": historical.get("archiveSha256"),
            "referenceInput": historical.get("referenceInput"),
        },
        "sozaAuditBaseline": baseline,
        "criteria": {str(item["criterion"]): item for item in criteria},
        "automatedCriteria": {
            "scope": [1, 2, 3, 4, 5, 6],
            "satisfied": [
                item["criterion"]
                for item in automated
                if item["status"] == base_audit.SATISFIED
            ],
            "blockedOrManual": blocked,
        },
        "manualReviewRequired": [7, 8],
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "actual revision B E2 partial failure reportをISSUE-000072 Resolution 1〜8へ対応付けます。"
            "build failureをResolved候補やSEI Adapter incompatibilityへ昇格させません。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--partial-report", required=True, type=Path)
    parser.add_argument("--historical-a-bundle", type=Path)
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
        result = audit_partial_failure(
            args.partial_report,
            soza_repo_root=args.soza_repo_root,
            historical_a_bundle=args.historical_a_bundle,
            expected_soza_head=args.expected_soza_head,
        )
        if args.output is not None:
            output = base_audit._prepare_output(args.output, args.soza_repo_root)
            base_audit._write_json_atomic(output, result)
    except (OSError, ValueError) as exc:
        print(f"TEI E2 partial failure Resolution audit failed: {exc}")
        return 1

    if args.json:
        import json

        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print(f"TEI E2 partial failure Resolution audit: {result['result']}")
        print(f"- resolutionCandidate: {result['resolutionCandidate']}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
