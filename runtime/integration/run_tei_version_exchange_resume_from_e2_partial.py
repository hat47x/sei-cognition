#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tarfile
from pathlib import Path
from typing import Any

import prepare_tei_fixed_reference_input as fixed_reference
import prepare_tei_revision_b_source as source_acquisition
import run_tei_bundle_adapter_compatibility as adapter_runner
import run_tei_revision_b_e2_from_github as partial_runner
import run_tei_version_exchange_evidence as version_exchange
import run_tei_version_exchange_from_github as github_runner
import verify_tei_evidence_bundle as bundle_verifier
import verify_tei_execution_source_identity as source_identity
from runtime_path_safety import reject_symlink_path_or_ancestors

SCHEMA = "sei.tei-version-exchange-e2-partial-resume/v1"
EXECUTION_MODE = "e2_partial_then_e3_resume"
SOURCE_ACQUISITION_MODE = "github-git-data-api-content-addressed"
ACCEPTED_CREDENTIAL_PROVENANCE = {"environment", "GITHUB_TOKEN", "GH_TOKEN"}
STOP_LINE = (
    "persisted E2 partial Evidence + resumed E3 verified "
    "!= arbitrary TEI version compatibility != Release Evidence "
    "!= Operational Evidence != ISSUE-000072 Resolved"
)
EXPECTED_ERRORS = (
    OSError,
    ValueError,
    RuntimeError,
    subprocess.SubprocessError,
    tarfile.TarError,
)


def legacy_schema(schema: str) -> str:
    """ADR-0031の3。改名前に記録されたEvidenceが持つ旧identityを返す。

    emit側は常に`sei.*`だけを書く。読み取り側だけが双方を受け付ける。
    記録済みEvidenceが存在する限り必要な恒久措置であり、期限は切らない。
    """
    return "soza." + schema[len("sei."):] if schema.startswith("sei.") else schema


class ResumeE3Failed(RuntimeError):
    def __init__(
        self,
        canonical_report: Path,
        wrapper_report: Path,
        cause: Exception,
    ) -> None:
        super().__init__(f"E3 resume failed: {cause}")
        self.canonical_report = canonical_report
        self.wrapper_report = wrapper_report
        self.cause = cause


def _is_within(candidate: Path, root: Path) -> bool:
    return candidate == root or root in candidate.parents


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


def _prepare_bundle(path: Path) -> Path:
    requested = path.expanduser()
    reject_symlink_path_or_ancestors(
        requested,
        "TEI revision B E2 partial Evidence bundle",
    )
    resolved = requested.resolve(strict=True)
    if not resolved.is_file():
        raise ValueError(f"E2 partial Evidence bundleがfileではありません: {resolved}")
    return resolved


def _source_provenance(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("E2 partial reportにsourceAcquisition Provenanceがありません")

    expected = {
        "mode": SOURCE_ACQUISITION_MODE,
        "repository": source_acquisition.GITHUB_REPOSITORY,
        "sourceCommit": source_identity.REVISION_B,
        "rootTree": source_acquisition.REVISION_B_ROOT_TREE,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            raise ValueError(
                "E2 partial source acquisition identityが固定値と一致しません: "
                f"field={key} expected={expected_value!r} actual={value.get(key)!r}"
            )

    credential = value.get("credentialSource")
    if credential not in ACCEPTED_CREDENTIAL_PROVENANCE:
        raise ValueError(
            f"E2 partial credential provenanceが未対応です: {credential!r}"
        )

    canonical = value.get("canonicalSourceVerification")
    if not isinstance(canonical, dict):
        raise ValueError("E2 partial canonical source verificationがありません")
    if canonical.get("head") != source_identity.REVISION_B:
        raise ValueError("E2 partial canonical source HEADがrevision Bではありません")
    for key in (
        "expectedHeadMatched",
        "revisionBExactHead",
        "worktreeCleanWithinBoundary",
    ):
        if canonical.get(key) is not True:
            raise ValueError(
                "E2 partial canonical source verificationが成立していません: "
                f"field={key} actual={canonical.get(key)!r}"
            )

    # Preserve only the same bounded provenance surface used by the existing
    # GitHub wrapper. The bundle verifier below remains authoritative for actual
    # executable / Provider Plan / fixed-reference bytes.
    return {
        "mode": value.get("mode"),
        "repository": value.get("repository"),
        "sourceCommit": value.get("sourceCommit"),
        "rootTree": value.get("rootTree"),
        "credentialSource": credential,
        "objectAcquisition": value.get("objectAcquisition"),
        "canonicalSourceVerification": {
            key: canonical.get(key)
            for key in (
                "head",
                "expectedHead",
                "expectedHeadMatched",
                "revisionBExactHead",
                "executionSourceObjects",
                "worktreeCleanWithinBoundary",
            )
            if key in canonical
        },
    }


def _validate_partial_report(
    report: dict[str, Any],
    bundle_verification: dict[str, object],
) -> dict[str, object]:
    if report.get("schema") not in (partial_runner.SCHEMA, legacy_schema(partial_runner.SCHEMA)):
        raise ValueError(
            "E2 partial report schemaが期待値と一致しません: "
            f"expected={partial_runner.SCHEMA} actual={report.get('schema')!r}"
        )
    if report.get("result") != "e2_bundle_verified_e3_not_run":
        raise ValueError(
            "E2 partial reportがresume可能な成功状態ではありません: "
            f"result={report.get('result')!r}"
        )
    if report.get("e3") is not None:
        raise ValueError("E2 partial reportでE3が未実行ではありません")
    if report.get("qualityJudgement") != "not_evaluated":
        raise ValueError("E2 partial reportのqualityJudgementがnot_evaluatedではありません")

    axis = report.get("comparisonAxis")
    if not isinstance(axis, dict):
        raise ValueError("E2 partial reportにcomparisonAxisがありません")
    expected_axis = {
        "buildSourceCommit": source_identity.REVISION_B,
        "referenceInputSourceCommit": source_identity.REVISION_A,
        "teiGoRequirement": partial_runner.e2_runner.EXPECTED_GO_VERSION,
        "e3IntentionallyNotRun": True,
    }
    for key, expected_value in expected_axis.items():
        if axis.get(key) != expected_value:
            raise ValueError(
                "E2 partial comparison axisが固定値と一致しません: "
                f"field={key} expected={expected_value!r} actual={axis.get(key)!r}"
            )
    acquisition = axis.get("referenceInputAcquisition")
    if acquisition not in {"git_checkout", "historical_evidence_bundle"}:
        raise ValueError(f"referenceInputAcquisitionが未対応です: {acquisition!r}")
    reference_bundle = axis.get("referenceInputBundle")
    if acquisition == "historical_evidence_bundle":
        if not isinstance(reference_bundle, str) or not reference_bundle:
            raise ValueError("historical fixed input acquisitionにreferenceInputBundleがありません")
    elif reference_bundle is not None:
        raise ValueError("git checkout fixed input acquisitionでreferenceInputBundleが設定されています")

    tei_go = axis.get("teiGoExecutable")
    if not isinstance(tei_go, str) or not tei_go:
        raise ValueError("E2 partial reportにTEI Go executable provenanceがありません")

    e2 = report.get("e2")
    if not isinstance(e2, dict) or e2.get("result") != "bundle_produced":
        raise ValueError("E2 partial reportにverified E2 resultがありません")
    reported_bundle = e2.get("bundle")
    if not isinstance(reported_bundle, dict):
        raise ValueError("E2 partial reportにbundle verificationがありません")
    reported_observation = reported_bundle.get("observation")
    actual_observation = bundle_verification.get("observation")
    if not isinstance(reported_observation, dict) or not isinstance(actual_observation, dict):
        raise ValueError("E2 partial bundle observationを比較できません")
    for key in (
        "source_commit",
        "binary_sha256",
        "provider_plan_sha256",
        "archive_sha256",
    ):
        if reported_observation.get(key) != actual_observation.get(key):
            raise ValueError(
                "E2 partial reportとresume bundleのidentityが一致しません: "
                f"field={key} report={reported_observation.get(key)!r} "
                f"bundle={actual_observation.get(key)!r}"
            )

    return {
        "axis": {
            "buildSourceCommit": source_identity.REVISION_B,
            "referenceInputSourceCommit": source_identity.REVISION_A,
            "referenceInputAcquisition": acquisition,
            "referenceInputBundle": reference_bundle,
            "teiGoRequirement": partial_runner.e2_runner.EXPECTED_GO_VERSION,
            "teiGoExecutable": tei_go,
        },
        "sourceAcquisition": _source_provenance(report.get("sourceAcquisition")),
        "e2": e2,
    }


def _load_partial_evidence(
    partial_report: Path,
    bundle: Path,
) -> dict[str, object]:
    report_path, report = _read_json(
        partial_report,
        "TEI revision B E2 partial Evidence report",
    )
    bundle_path = _prepare_bundle(bundle)
    verification = bundle_verifier.verify_bundle(
        bundle_path,
        expected_source_commit=source_identity.REVISION_B,
        expected_reference_input=fixed_reference.EXPECTED_REFERENCE,
    )
    validated = _validate_partial_report(report, verification)
    return {
        **validated,
        "partialReport": str(report_path),
        "bundleArchive": str(bundle_path),
    }


def _prepare_output_reports(
    output_dir: Path,
    *,
    sei_repo_root: Path,
    partial_report: Path,
    bundle: Path,
    overwrite: bool,
) -> tuple[Path, Path]:
    requested = output_dir.expanduser()
    reject_symlink_path_or_ancestors(
        requested,
        "TEI E2 partial resume Evidence directory",
    )
    resolved = requested.resolve(strict=False)
    if resolved.exists() and not resolved.is_dir():
        raise ValueError(f"resume Evidence出力先がdirectoryではありません: {resolved}")

    sei_root = sei_repo_root.expanduser().resolve(strict=True)
    if _is_within(resolved, sei_root) or _is_within(sei_root, resolved):
        raise ValueError(
            "resume Evidence directoryをSEI repositoryと重ねられません: "
            f"output={resolved} sei={sei_root}"
        )

    inputs: set[Path] = set()
    for path, label in (
        (partial_report, "TEI revision B E2 partial Evidence report"),
        (bundle, "TEI revision B E2 partial Evidence bundle"),
    ):
        requested_input = path.expanduser()
        reject_symlink_path_or_ancestors(requested_input, label)
        inputs.add(requested_input.resolve(strict=True))

    canonical = resolved / version_exchange.REPORT_NAME
    wrapper = resolved / github_runner.REPORT_NAME
    for path in (canonical, wrapper):
        reject_symlink_path_or_ancestors(path, "TEI E2 partial resume report")
        if path.resolve(strict=False) in inputs:
            raise ValueError(f"resume outputで入力Evidenceを上書きできません: {path}")

    existing = [path for path in (canonical, wrapper) if os.path.lexists(path)]
    if existing and not overwrite:
        raise ValueError(
            "既存resume Evidence reportを無言で上書きしません。"
            "--overwriteを明示してください: "
            + ", ".join(str(path) for path in existing)
        )
    for path in existing:
        if not path.is_file():
            raise ValueError(f"resume Evidence report出力先がfileではありません: {path}")
    return canonical, wrapper


def _wrapper_report(
    *,
    result: str,
    source: dict[str, object],
    canonical_path: Path,
    partial_report: str,
    bundle_archive: str,
    comparison_axis: dict[str, object],
    failure: dict[str, object] | None = None,
) -> dict[str, object]:
    value: dict[str, object] = {
        "schema": github_runner.SCHEMA,
        "result": result,
        "sourceAcquisition": source,
        "canonicalVersionExchangeReport": str(canonical_path),
        "executionMode": EXECUTION_MODE,
        "resumeFromPartialEvidence": {
            "partialReport": partial_report,
            "bundleArchive": bundle_archive,
        },
        "versionExchange": {
            "result": (
                "fixed_scope_e2_e3_verified"
                if result == "fixed_scope_e2_e3_verified"
                else "e2_verified_e3_failed"
            ),
            "comparisonAxis": comparison_axis,
            "bundleArchive": bundle_archive,
        },
        "qualityJudgement": "not_evaluated",
        "stopLine": github_runner.STOP_LINE,
    }
    if failure is not None:
        value["failure"] = failure
    return value


def _write_pair(
    canonical_path: Path,
    wrapper_path: Path,
    canonical: dict[str, object],
    wrapper: dict[str, object],
    *,
    overwrite: bool,
) -> None:
    github_runner._write_report(canonical_path, canonical, overwrite=overwrite)
    github_runner._write_report(wrapper_path, wrapper, overwrite=overwrite)


def resume_e3(
    partial_report: Path,
    bundle: Path,
    sei_repo_root: Path,
    output_dir: Path,
    *,
    sei_go_executable: Path,
    expected_sei_head: str | None = None,
    overwrite: bool = False,
) -> dict[str, object]:
    sei_repo_root = sei_repo_root.expanduser().resolve(strict=True)
    canonical_path, wrapper_path = _prepare_output_reports(
        output_dir,
        sei_repo_root=sei_repo_root,
        partial_report=partial_report,
        bundle=bundle,
        overwrite=overwrite,
    )
    partial = _load_partial_evidence(partial_report, bundle)
    comparison_axis = {
        **partial["axis"],
        "seiGoRequirement": "runtime/go go.mod with GOTOOLCHAIN=local",
        "seiGoExecutable": str(sei_go_executable.expanduser()),
        "expectedSeiHead": expected_sei_head,
    }
    provenance = {
        "mode": EXECUTION_MODE,
        "partialEvidenceReport": partial["partialReport"],
        "bundleArchive": partial["bundleArchive"],
    }

    e3_toolchain_entered = False
    try:
        with version_exchange._go_on_path(sei_go_executable) as sei_go:
            e3_toolchain_entered = True
            comparison_axis["seiGoExecutable"] = str(sei_go)
            e3 = adapter_runner.run_compatibility(
                Path(str(partial["bundleArchive"])),
                sei_repo_root=sei_repo_root,
                expected_source_commit=source_identity.REVISION_B,
                expected_sei_head=expected_sei_head,
            )
            comparison_axis["seiGoRequirement"] = e3["seiGoRequirement"]
            comparison_axis["seiGoObserved"] = e3["seiGoVersion"]
    except EXPECTED_ERRORS as exc:
        if not e3_toolchain_entered and not isinstance(
            exc, adapter_runner.TEIAdapterStageError
        ):
            exc = adapter_runner.TEIAdapterStageError("sei_go_toolchain", str(exc))
        failure = version_exchange._failure("E3", exc)
        canonical = {
            "schema": version_exchange.SCHEMA,
            "result": "e2_verified_e3_failed",
            "comparisonAxis": comparison_axis,
            "bundleArchive": partial["bundleArchive"],
            "e2": partial["e2"],
            "e3": None,
            "failure": failure,
            "executionProvenance": provenance,
            "qualityJudgement": "not_evaluated",
            "stopLine": version_exchange.STOP_LINE,
        }
        wrapper = _wrapper_report(
            result="version_exchange_failed",
            source=partial["sourceAcquisition"],
            canonical_path=canonical_path,
            partial_report=str(partial["partialReport"]),
            bundle_archive=str(partial["bundleArchive"]),
            comparison_axis=comparison_axis,
            failure={
                "stage": "E3",
                "type": type(exc).__name__,
                "message": str(exc),
            },
        )
        _write_pair(canonical_path, wrapper_path, canonical, wrapper, overwrite=overwrite)
        raise ResumeE3Failed(canonical_path, wrapper_path, exc) from exc

    canonical = {
        "schema": version_exchange.SCHEMA,
        "result": "fixed_scope_e2_e3_verified",
        "comparisonAxis": comparison_axis,
        "bundleArchive": partial["bundleArchive"],
        "e2": partial["e2"],
        "e3": e3,
        "executionProvenance": provenance,
        "qualityJudgement": "not_evaluated",
        "stopLine": version_exchange.STOP_LINE,
    }
    wrapper = _wrapper_report(
        result="fixed_scope_e2_e3_verified",
        source=partial["sourceAcquisition"],
        canonical_path=canonical_path,
        partial_report=str(partial["partialReport"]),
        bundle_archive=str(partial["bundleArchive"]),
        comparison_axis=comparison_axis,
    )
    _write_pair(canonical_path, wrapper_path, canonical, wrapper, overwrite=overwrite)
    return {
        "schema": SCHEMA,
        "result": "fixed_scope_e2_e3_verified",
        "canonicalReport": str(canonical_path),
        "githubWrapperReport": str(wrapper_path),
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "GitHub E2 partial Evidence reportと同一identityのrevision B bundleを再検証し、"
            "E2を再実行せずcurrent SEI Adapter E3だけを再開します。結果は既存canonical "
            "version-exchange reportとGitHub acquisition wrapper reportへ戻します。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--partial-report", required=True, type=Path)
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument(
        "--sei-repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--sei-go-executable", required=True, type=Path)
    parser.add_argument("--expected-sei-head")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = resume_e3(
            args.partial_report,
            args.bundle,
            args.sei_repo_root,
            args.output_dir,
            sei_go_executable=args.sei_go_executable,
            expected_sei_head=args.expected_sei_head,
            overwrite=args.overwrite,
        )
    except ResumeE3Failed as exc:
        print(f"TEI E2 partial resume failed at E3: {exc.cause}")
        print(f"- canonical report: {exc.canonical_report}")
        print(f"- GitHub wrapper report: {exc.wrapper_report}")
        return 1
    except EXPECTED_ERRORS as exc:
        print(f"TEI E2 partial resume rejected: {exc}")
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print("TEI E2 partial -> E3 resume: verified")
        print(f"- canonical report: {result['canonicalReport']}")
        print(f"- GitHub wrapper report: {result['githubWrapperReport']}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
