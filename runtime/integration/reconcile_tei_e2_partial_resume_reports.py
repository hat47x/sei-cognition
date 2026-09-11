#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import run_tei_version_exchange_evidence as version_exchange
import run_tei_version_exchange_from_github as github_runner
import run_tei_version_exchange_resume_from_e2_partial as resume_runner
from runtime_path_safety import reject_symlink_path_or_ancestors

SCHEMA = "sei.tei-version-exchange-e2-partial-resume-reconcile/v1"
STOP_LINE = (
    "resume report pair reconciled without E3 rerun "
    "!= revision B actual E2 newly executed != E3 newly executed "
    "!= ISSUE-000072 Resolved"
)


def _read_json(path: Path, label: str) -> tuple[Path, dict[str, Any]]:
    requested = path.expanduser()
    reject_symlink_path_or_ancestors(requested, label)
    resolved = requested.resolve(strict=True)
    if not resolved.is_file():
        raise ValueError(f"{label}がfileではありません: {resolved}")
    try:
        value = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label}をJSONとして読めません: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label}のrootはobjectである必要があります")
    return resolved, value


def _same_resolved_path(value: object, expected: Path, label: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label}がありません")
    requested = Path(value).expanduser()
    reject_symlink_path_or_ancestors(requested, label)
    actual = requested.resolve(strict=True)
    if actual != expected:
        raise ValueError(
            f"{label}がreconcile入力と一致しません: expected={expected} actual={actual}"
        )


def _validate_canonical(
    canonical: dict[str, Any],
    *,
    canonical_path: Path,
    partial: dict[str, object],
) -> tuple[str, dict[str, object] | None]:
    if canonical.get("schema") != version_exchange.SCHEMA:
        raise ValueError(
            "canonical report schemaが期待値と一致しません: "
            f"expected={version_exchange.SCHEMA} actual={canonical.get('schema')!r}"
        )
    result = canonical.get("result")
    if result not in {"fixed_scope_e2_e3_verified", "e2_verified_e3_failed"}:
        raise ValueError(f"resume reconcile対象外のcanonical resultです: {result!r}")
    if canonical.get("qualityJudgement") != "not_evaluated":
        raise ValueError("canonical reportのqualityJudgementがnot_evaluatedではありません")

    expected_bundle = Path(str(partial["bundleArchive"])).resolve(strict=True)
    _same_resolved_path(
        canonical.get("bundleArchive"),
        expected_bundle,
        "canonical bundleArchive",
    )

    if canonical.get("e2") != partial.get("e2"):
        raise ValueError("canonical reportのE2がpartial Evidenceと一致しません")

    axis = canonical.get("comparisonAxis")
    if not isinstance(axis, dict):
        raise ValueError("canonical reportにcomparisonAxisがありません")
    partial_axis = partial.get("axis")
    if not isinstance(partial_axis, dict):
        raise ValueError("partial Evidenceにcomparison axisがありません")
    for key, expected in partial_axis.items():
        if axis.get(key) != expected:
            raise ValueError(
                "canonical comparison axisがpartial Evidenceと一致しません: "
                f"field={key} expected={expected!r} actual={axis.get(key)!r}"
            )

    provenance = canonical.get("executionProvenance")
    if not isinstance(provenance, dict):
        raise ValueError("canonical reportにresume executionProvenanceがありません")
    if provenance.get("mode") != resume_runner.EXECUTION_MODE:
        raise ValueError(
            "canonical executionProvenance modeがresumeではありません: "
            f"actual={provenance.get('mode')!r}"
        )
    _same_resolved_path(
        provenance.get("partialEvidenceReport"),
        Path(str(partial["partialReport"])).resolve(strict=True),
        "canonical partialEvidenceReport",
    )
    _same_resolved_path(
        provenance.get("bundleArchive"),
        expected_bundle,
        "canonical executionProvenance bundleArchive",
    )

    failure_summary: dict[str, object] | None = None
    if result == "fixed_scope_e2_e3_verified":
        if not isinstance(canonical.get("e3"), dict):
            raise ValueError("successful canonical reportにE3 resultがありません")
        if "failure" in canonical:
            raise ValueError("successful canonical reportにfailureが含まれています")
    else:
        if canonical.get("e3") is not None:
            raise ValueError("E3 failure canonical reportでe3がNoneではありません")
        failure = canonical.get("failure")
        if not isinstance(failure, dict) or failure.get("stage") != "E3":
            raise ValueError("E3 failure canonical reportにfailure.stage=E3がありません")
        failure_type = failure.get("type")
        failure_message = failure.get("message")
        if not isinstance(failure_type, str) or not isinstance(failure_message, str):
            raise ValueError("canonical E3 failureのtype/messageがありません")
        failure_summary = {
            "stage": "E3",
            "type": failure_type,
            "message": failure_message,
        }

    if canonical_path.name != version_exchange.REPORT_NAME:
        raise ValueError(
            "canonical report filenameが標準名ではありません: "
            f"expected={version_exchange.REPORT_NAME} actual={canonical_path.name}"
        )
    return str(result), failure_summary


def reconcile(
    partial_report: Path,
    bundle: Path,
    canonical_report: Path,
) -> dict[str, object]:
    partial = resume_runner._load_partial_evidence(partial_report, bundle)
    canonical_path, canonical = _read_json(
        canonical_report,
        "TEI canonical resumed version-exchange report",
    )
    canonical_result, failure = _validate_canonical(
        canonical,
        canonical_path=canonical_path,
        partial=partial,
    )

    wrapper_path = canonical_path.parent / github_runner.REPORT_NAME
    expected_wrapper = resume_runner._wrapper_report(
        result=(
            "fixed_scope_e2_e3_verified"
            if canonical_result == "fixed_scope_e2_e3_verified"
            else "version_exchange_failed"
        ),
        source=partial["sourceAcquisition"],
        canonical_path=canonical_path,
        partial_report=str(partial["partialReport"]),
        bundle_archive=str(partial["bundleArchive"]),
        comparison_axis=canonical["comparisonAxis"],
        failure=failure,
    )

    if wrapper_path.exists() or wrapper_path.is_symlink():
        existing_path, existing = _read_json(
            wrapper_path,
            "TEI GitHub acquisition wrapper report",
        )
        if existing != expected_wrapper:
            raise ValueError(
                "既存GitHub wrapper reportがcanonical/partial Evidenceと一致しません。"
                "reconcileは既存Evidenceを上書きしません: "
                f"{existing_path}"
            )
        return {
            "schema": SCHEMA,
            "result": "already_consistent",
            "canonicalReport": str(canonical_path),
            "githubWrapperReport": str(existing_path),
            "canonicalResult": canonical_result,
            "qualityJudgement": "not_evaluated",
            "stopLine": STOP_LINE,
        }

    github_runner._write_report(wrapper_path, expected_wrapper, overwrite=False)
    return {
        "schema": SCHEMA,
        "result": "wrapper_reconstructed_without_e3_rerun",
        "canonicalReport": str(canonical_path),
        "githubWrapperReport": str(wrapper_path),
        "canonicalResult": canonical_result,
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "E2 partial -> E3 resume後にcanonical reportだけがpublishされ、GitHub wrapper "
            "reportのpublishだけが失敗した場合に、partial/bundle/canonical identityを"
            "再検証してwrapperだけをE3再実行なしで補完します。既存wrapperは上書きしません。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--partial-report", required=True, type=Path)
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--canonical-report", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = reconcile(
            args.partial_report,
            args.bundle,
            args.canonical_report,
        )
    except resume_runner.EXPECTED_ERRORS as exc:
        print(f"TEI E2 partial resume report reconcile rejected: {exc}")
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print("TEI E2 partial resume report reconcile: " + str(result["result"]))
        print(f"- canonical report: {result['canonicalReport']}")
        print(f"- GitHub wrapper report: {result['githubWrapperReport']}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
