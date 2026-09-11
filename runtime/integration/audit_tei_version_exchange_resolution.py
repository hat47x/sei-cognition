#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import prepare_tei_fixed_reference_input as fixed_reference
import prepare_tei_revision_b_source as github_source
import verify_tei_evidence_bundle as bundle_verifier
import verify_tei_execution_source_identity as source_identity
from runtime_path_safety import reject_symlink_path_or_ancestors

SCHEMA = "sei.tei-version-exchange-resolution-audit/v1"
CANONICAL_SCHEMA = "sei.tei-version-exchange-evidence-run/v1"
WRAPPER_SCHEMA = "sei.tei-version-exchange-github-acquisition-run/v1"
CURRENT_GITHUB_ACQUISITION_MODE = "github-git-data-api-content-addressed"
ACCEPTED_CREDENTIAL_PROVENANCE = {"environment", "GITHUB_TOKEN", "GH_TOKEN"}
BASELINE_PATHS = [
    "plan/issue/ISSUE-000072-verify-tei-executable-version-exchange.md",
    "runtime/TEI_VERSION_EXCHANGE_REQUIREMENT_PREAUDIT_2026-09-05.md",
    "requirements/PRODUCT_REQUIREMENTS.md",
    "requirements/ACCEPTANCE_SCENARIOS.md",
]
STOP_LINE = (
    "resolution audit candidate != ISSUE-000072 automatically Resolved "
    "!= Stable Requirement change != Universal Contract change"
)
SATISFIED = "satisfied"
BLOCKED = "blocked"
MANUAL = "manual_review"


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


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        raise ValueError(
            f"Git command failed: {' '.join(args)}: {result.stderr.strip()}"
        )
    return result


def _verify_sei_baseline(repo: Path, expected_head: str | None) -> dict[str, Any]:
    repo = repo.expanduser().resolve(strict=True)
    inside = _git(repo, "rev-parse", "--is-inside-work-tree", check=False)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        raise ValueError(f"SEI Git repositoryではありません: {repo}")
    head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    if expected_head is not None and head != expected_head:
        raise ValueError(
            f"SEI HEADが期待値と一致しません: expected={expected_head} actual={head}"
        )
    dirty = _git(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--ignored=matching",
        "--",
        *BASELINE_PATHS,
    ).stdout.splitlines()
    dirty = [line for line in dirty if line.strip()]
    if dirty:
        raise ValueError(
            "Resolution audit baselineに未commit変更、untracked file、またはignored entryがあります: "
            + " | ".join(dirty)
        )
    objects: dict[str, str] = {}
    for relative in BASELINE_PATHS:
        observed = _git(repo, "rev-parse", f"HEAD:{relative}", check=False)
        if observed.returncode != 0:
            raise ValueError(
                f"Resolution audit baseline Git objectを取得できません: {relative}"
            )
        objects[relative] = observed.stdout.strip()
    return {
        "head": head,
        "expectedHead": expected_head,
        "expectedHeadMatched": expected_head is None or head == expected_head,
        "objects": objects,
        "worktreeCleanWithinBoundary": True,
    }


def _validate_canonical(report: dict[str, Any]) -> dict[str, Any]:
    if report.get("schema") != CANONICAL_SCHEMA:
        raise ValueError(
            "canonical report schemaが期待値と一致しません: "
            f"expected={CANONICAL_SCHEMA} actual={report.get('schema')!r}"
        )
    result = report.get("result")
    if result not in {
        "fixed_scope_e2_e3_verified",
        "e2_failed",
        "e2_verified_e3_failed",
        "e2_bundle_verified_e3_not_run",
    }:
        raise ValueError(f"canonical report resultが未対応です: {result!r}")
    axis = report.get("comparisonAxis")
    if not isinstance(axis, dict):
        raise ValueError("canonical report comparisonAxisがありません")
    expected = {
        "buildSourceCommit": source_identity.REVISION_B,
        "referenceInputSourceCommit": source_identity.REVISION_A,
    }
    for key, value in expected.items():
        if axis.get(key) != value:
            raise ValueError(
                "version-exchange comparison axisが固定値と一致しません: "
                f"field={key} expected={value} actual={axis.get(key)!r}"
            )
    acquisition = axis.get("referenceInputAcquisition")
    if acquisition not in {"git_checkout", "historical_evidence_bundle"}:
        raise ValueError(f"referenceInputAcquisitionが未対応です: {acquisition!r}")
    return {
        "result": result,
        "buildSourceCommit": axis["buildSourceCommit"],
        "referenceInputSourceCommit": axis["referenceInputSourceCommit"],
        "referenceInputAcquisition": acquisition,
        "teiGoRequirement": axis.get("teiGoRequirement"),
        "seiGoRequirement": axis.get("seiGoRequirement"),
        "expectedSeiHead": axis.get("expectedSeiHead"),
    }


def _criterion(number: int, status: str, summary: str, **detail: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "criterion": number,
        "status": status,
        "summary": summary,
    }
    if detail:
        value["detail"] = detail
    return value


def _historical_a(bundle: Path | None) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if bundle is None:
        return _criterion(
            1,
            MANUAL,
            "historical revision A artifactはこのaudit invocationでは再検証していません",
        ), None
    try:
        verification = fixed_reference.verify_fixed_reference_input_bundle(bundle)
    except Exception as exc:
        return _criterion(
            1,
            BLOCKED,
            "historical revision A artifactのcurrent verifier再検証に失敗しました",
            error=str(exc),
        ), None
    return _criterion(
        1,
        SATISFIED,
        "historical revision A artifactをcurrent verifierで固定identityへ再検証しました",
        archive=verification.get("archive"),
        archiveSha256=verification.get("archiveSha256"),
        sourceCommit=verification.get("sourceCommit"),
        referenceInput=verification.get("referenceInput"),
    ), verification


def _revision_b_bundle(
    report: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    e2 = report.get("e2")
    if not isinstance(e2, dict) or e2.get("result") != "bundle_produced":
        return _criterion(
            2,
            BLOCKED,
            "revision Bのactual fixed Evidence bundleがcanonical reportで成立していません",
        ), None
    archive_value = report.get("bundleArchive")
    if not isinstance(archive_value, str) or not archive_value:
        return _criterion(
            2,
            BLOCKED,
            "canonical reportにrevision B bundleArchiveがありません",
        ), None
    try:
        archive = Path(archive_value).expanduser().resolve(strict=True)
        verification = bundle_verifier.verify_bundle(
            archive,
            expected_source_commit=source_identity.REVISION_B,
            expected_reference_input=fixed_reference.EXPECTED_REFERENCE,
        )
    except Exception as exc:
        return _criterion(
            2,
            BLOCKED,
            "revision B Evidence bundleの独立再検証に失敗しました",
            error=str(exc),
            bundleArchive=archive_value,
        ), None
    observation = verification.get("observation")
    if not isinstance(observation, dict):
        return _criterion(
            2,
            BLOCKED,
            "revision B bundle verification observationがありません",
        ), None
    identities = {
        "sourceCommit": observation.get("source_commit"),
        "binarySha256": observation.get("binary_sha256"),
        "providerPlanSha256": observation.get("provider_plan_sha256"),
        "archiveSha256": observation.get("archive_sha256"),
    }
    if identities["sourceCommit"] != source_identity.REVISION_B:
        return _criterion(
            2,
            BLOCKED,
            "revision B bundle source identityが固定revisionと一致しません",
            identities=identities,
        ), None
    if not all(
        isinstance(identities[key], str) and identities[key]
        for key in ("binarySha256", "providerPlanSha256", "archiveSha256")
    ):
        return _criterion(
            2,
            BLOCKED,
            "revision B bundleでbinary / Provider Plan / archive identityを記録できません",
            identities=identities,
        ), None
    return _criterion(
        2,
        SATISFIED,
        "revision B actual bundleのsource / binary / Provider Plan identityを再検証しました",
        identities=identities,
    ), verification


def _e2_criterion(report: dict[str, Any]) -> dict[str, Any]:
    result = report.get("result")
    if result in {
        "fixed_scope_e2_e3_verified",
        "e2_verified_e3_failed",
        "e2_bundle_verified_e3_not_run",
    } and isinstance(report.get("e2"), dict):
        e2 = report["e2"]
        return _criterion(
            3,
            SATISFIED,
            "exact-B executable + exact-A fixed inputのE2がProvider Plan Evidence bundleまで到達しました",
            outcome="verified",
            result=e2.get("result"),
            completedStages=e2.get("completedStages"),
        )
    if result == "e2_failed":
        failure = report.get("failure")
        if isinstance(failure, dict) and isinstance(failure.get("substage"), str):
            return _criterion(
                3,
                SATISFIED,
                "E2は不成立でしたがrepository-local external stageまで停止位置を判別できました",
                outcome="failed",
                substage=failure.get("substage"),
                failureType=failure.get("type"),
            )
        return _criterion(
            3,
            BLOCKED,
            "E2不成立の停止位置をrepository-local substageまで判別できません",
        )
    return _criterion(
        3,
        BLOCKED,
        "E2のactual結果を判定できません",
        canonicalResult=result,
    )


def _e3_criterion(report: dict[str, Any]) -> dict[str, Any]:
    result = report.get("result")
    if result == "fixed_scope_e2_e3_verified" and isinstance(report.get("e3"), dict):
        e3 = report["e3"]
        return _criterion(
            4,
            SATISFIED,
            "current SEI Adapterでrevision Bのlive compatibilityをactualに確認しました",
            outcome="verified",
            result=e3.get("result"),
            seiSource=e3.get("seiSource"),
            postLiveTestSeiSource=e3.get("postLiveTestSeiSource"),
        )
    if result == "e2_verified_e3_failed":
        failure = report.get("failure")
        if isinstance(failure, dict) and isinstance(failure.get("substage"), str):
            return _criterion(
                4,
                SATISFIED,
                "E3は不成立でしたがrepository-local external stageまで停止位置を判別できました",
                outcome="failed",
                substage=failure.get("substage"),
                failureType=failure.get("type"),
            )
        return _criterion(
            4,
            BLOCKED,
            "E3不成立の停止位置をrepository-local substageまで判別できません",
        )
    return _criterion(
        4,
        BLOCKED,
        "E3 actual Adapter compatibilityまで到達していません",
        canonicalResult=result,
    )


def _a_unchanged(historical: dict[str, Any] | None) -> dict[str, Any]:
    if historical is None:
        return _criterion(
            5,
            MANUAL,
            "revision A Evidence不変性はこのaudit invocationでは固定bundle再検証から確認できません",
        )
    return _criterion(
        5,
        SATISFIED,
        "revision A historical Evidenceは固定source / binary / Provider Plan / reference identityへ引き続き一致します",
        sourceCommit=historical.get("sourceCommit"),
        archiveSha256=historical.get("archiveSha256"),
    )


def _wrapper_expected_result(canonical_result: str) -> tuple[str, str | None]:
    if canonical_result == "fixed_scope_e2_e3_verified":
        return canonical_result, None
    if canonical_result == "e2_failed":
        return "version_exchange_failed", "E2"
    if canonical_result == "e2_verified_e3_failed":
        return "version_exchange_failed", "E3"
    return "version_exchange_failed", None


def _boundary_criterion(
    axis: dict[str, Any],
    canonical: dict[str, Any],
    wrapper_path: Path | None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if wrapper_path is None:
        return _criterion(
            6,
            MANUAL,
            "canonical reportはfixed input acquisitionを保持していますがrevision B acquisition / credential Provenanceのwrapper reportがありません",
            referenceInputAcquisition=axis["referenceInputAcquisition"],
        ), None
    try:
        resolved, wrapper = _read_json(
            wrapper_path,
            "TEI GitHub acquisition wrapper report",
        )
    except Exception as exc:
        return _criterion(
            6,
            BLOCKED,
            "GitHub acquisition wrapper reportを検証できません",
            error=str(exc),
        ), None
    if wrapper.get("schema") != WRAPPER_SCHEMA:
        return _criterion(
            6,
            BLOCKED,
            "GitHub acquisition wrapper schemaが期待値と一致しません",
            actualSchema=wrapper.get("schema"),
        ), wrapper
    source = wrapper.get("sourceAcquisition")
    if not isinstance(source, dict):
        return _criterion(
            6,
            BLOCKED,
            "wrapper reportにsourceAcquisition Provenanceがありません",
        ), wrapper

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
        CURRENT_GITHUB_ACQUISITION_MODE,
        "github_git_data_api",
    }:
        mismatches["sourceAcquisitionMode"] = {
            "expected": CURRENT_GITHUB_ACQUISITION_MODE,
            "actual": acquisition_mode,
        }

    credential_source = source.get("credentialSource")
    if credential_source not in ACCEPTED_CREDENTIAL_PROVENANCE:
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

    expected_result, expected_stage = _wrapper_expected_result(str(canonical.get("result")))
    if wrapper.get("result") != expected_result:
        mismatches["wrapperResult"] = {
            "expected": expected_result,
            "actual": wrapper.get("result"),
        }
    if expected_stage is not None:
        failure = wrapper.get("failure")
        actual_stage = failure.get("stage") if isinstance(failure, dict) else None
        if actual_stage != expected_stage:
            mismatches["wrapperFailureStage"] = {
                "expected": expected_stage,
                "actual": actual_stage,
            }
    if mismatches:
        return _criterion(
            6,
            BLOCKED,
            "acquisition / credential / artifact identity境界のProvenanceが固定値と一致しません",
            mismatches=mismatches,
        ), wrapper
    return _criterion(
        6,
        SATISFIED,
        "GitHub acquisition / environment credential provenance / exact-B artifact identityとexact-A fixed input acquisitionを分離して追跡できます",
        wrapperReport=str(resolved),
        sourceAcquisition={
            "mode": acquisition_mode,
            "repository": source.get("repository"),
            "sourceCommit": source.get("sourceCommit"),
            "rootTree": source.get("rootTree"),
            "credentialSource": credential_source,
        },
        referenceInputAcquisition=axis["referenceInputAcquisition"],
    ), wrapper


def _reaudit_hint(report: dict[str, Any]) -> dict[str, Any]:
    result = report.get("result")
    failure = report.get("failure") if isinstance(report.get("failure"), dict) else {}
    substage = failure.get("substage") if isinstance(failure, dict) else None
    if result == "fixed_scope_e2_e3_verified":
        classification = "evidence_strengthened_no_requirement_change_expected"
        note = (
            "REQ-0001 / 0007 / 0021は原則No Change。"
            "REQ-0022を含むProvider-neutral Observation Evidence強化を確認する。"
        )
    elif result == "e2_failed":
        classification = "no_semantic_inference_from_e2_failure"
        note = (
            "build / toolchain / Provider Plan boundaryの不成立だけから"
            "Stable Requirement changeを推定しない。"
        )
    elif result == "e2_verified_e3_failed":
        classification = "adapter_local_compatibility_review_first"
        note = (
            "まずProvider surface / Adapter-local compatibilityとして評価し、"
            "Universal Requirement化は独立した意味上の必要性が確認された場合だけ検討する。"
        )
    else:
        classification = "manual_interpretation_required"
        note = "pre-audit判定表へ戻ってactual Evidenceの高さを再確認する。"
    return {
        "classification": classification,
        "canonicalResult": result,
        "observedSubstage": substage,
        "note": note,
        "requirements": {
            "REQ-0001": "No Change | Evidence strengthened | Candidate Requirement needed",
            "REQ-0007": "No Change | Evidence strengthened | Candidate Requirement needed",
            "REQ-0021": "No Change | Evidence strengthened | Candidate Requirement needed",
            "REQ-0022": "adjacent; add formally only if actual Product failure requires it",
        },
        "scenarios": {
            "SCN-0014": "do not mark Satisfied from TEI executable version exchange alone",
            "SCN-0018": "review fixture-scoped Evidence strengthening only",
        },
    }


def audit_resolution(
    canonical_report: Path,
    *,
    sei_repo_root: Path,
    historical_a_bundle: Path | None = None,
    github_wrapper_report: Path | None = None,
    expected_sei_head: str | None = None,
) -> dict[str, Any]:
    canonical_path, canonical = _read_json(
        canonical_report,
        "TEI canonical version exchange report",
    )
    axis = _validate_canonical(canonical)
    if expected_sei_head is None and isinstance(axis.get("expectedSeiHead"), str):
        expected_sei_head = axis["expectedSeiHead"]
    baseline = _verify_sei_baseline(sei_repo_root, expected_sei_head)

    c1, historical = _historical_a(historical_a_bundle)
    c2, b_bundle = _revision_b_bundle(canonical)
    c3 = _e2_criterion(canonical)
    c4 = _e3_criterion(canonical)
    c5 = _a_unchanged(historical)
    c6, wrapper = _boundary_criterion(axis, canonical, github_wrapper_report)
    c7 = _criterion(
        7,
        MANUAL,
        "REQ-0001 / REQ-0007 / REQ-0021 / SCN-0014 / SCN-0018をpre-audit基準で最終再照合してください",
        hint=_reaudit_hint(canonical),
    )
    c8 = _criterion(
        8,
        MANUAL,
        "自然な日本語を最重要視した最終意味監査が必要です",
    )

    criteria = [c1, c2, c3, c4, c5, c6, c7, c8]
    automated = criteria[:6]
    blocked = [
        item["criterion"]
        for item in automated
        if item["status"] != SATISFIED
    ]
    candidate = not blocked
    return {
        "schema": SCHEMA,
        "result": "manual_review_required" if candidate else "blocked",
        "resolutionCandidate": candidate,
        "autoResolvePermitted": False,
        "canonicalReport": {
            "path": str(canonical_path),
            "result": canonical.get("result"),
            "comparisonAxis": axis,
        },
        "historicalAReverification": None if historical is None else {
            "sourceCommit": historical.get("sourceCommit"),
            "archive": historical.get("archive"),
            "archiveSha256": historical.get("archiveSha256"),
            "referenceInput": historical.get("referenceInput"),
        },
        "revisionBBundleVerification": None if b_bundle is None else {
            "observation": b_bundle.get("observation"),
            "referenceInput": b_bundle.get("referenceInput"),
        },
        "githubAcquisitionWrapperObserved": wrapper is not None,
        "seiAuditBaseline": baseline,
        "criteria": {str(item["criterion"]): item for item in criteria},
        "automatedCriteria": {
            "scope": [1, 2, 3, 4, 5, 6],
            "satisfied": [
                item["criterion"]
                for item in automated
                if item["status"] == SATISFIED
            ],
            "blockedOrManual": blocked,
        },
        "manualReviewRequired": [7, 8],
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }


def _prepare_output(output: Path, sei_repo_root: Path) -> Path:
    requested = output.expanduser()
    reject_symlink_path_or_ancestors(
        requested,
        "TEI version exchange resolution audit output",
    )
    resolved = requested.resolve(strict=False)
    sei_root = sei_repo_root.expanduser().resolve(strict=True)
    if resolved == sei_root or sei_root in resolved.parents:
        raise ValueError(
            "Resolution audit outputをSEI repository配下へ置けません: "
            f"output={resolved} sei={sei_root}"
        )
    if resolved.exists():
        raise ValueError(
            f"既存Resolution audit outputを無言で上書きしません: {resolved}"
        )
    return resolved


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    reject_symlink_path_or_ancestors(
        path,
        "TEI version exchange resolution audit output",
    )
    candidate: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            candidate = Path(handle.name)
            json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        reject_symlink_path_or_ancestors(
            path,
            "TEI version exchange resolution audit output",
        )
        if path.exists():
            raise ValueError(
                "Resolution audit outputがpublish直前に作成されました。暗黙上書きしません: "
                f"{path}"
            )
        os.replace(candidate, path)
        candidate = None
    finally:
        if candidate is not None and candidate.exists() and not candidate.is_symlink():
            candidate.unlink()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "actual TEI version exchange canonical reportをISSUE-000072 Resolution 1〜8へ対応付け、"
            "1〜6の自動検査と7〜8のmanual review境界を分離します。"
            "Issueを自動closeせず、Requirement / Universal Contractも変更しません。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--canonical-report", required=True, type=Path)
    parser.add_argument("--historical-a-bundle", type=Path)
    parser.add_argument("--github-wrapper-report", type=Path)
    parser.add_argument(
        "--sei-repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--expected-sei-head")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = audit_resolution(
            args.canonical_report,
            sei_repo_root=args.sei_repo_root,
            historical_a_bundle=args.historical_a_bundle,
            github_wrapper_report=args.github_wrapper_report,
            expected_sei_head=args.expected_sei_head,
        )
        output = None
        if args.output is not None:
            output = _prepare_output(args.output, args.sei_repo_root)
            _write_json_atomic(output, result)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"TEI version exchange resolution audit rejected: {exc}")
        return 1
    if args.json or output is None:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print(f"TEI version exchange resolution audit: {result['result']}")
        print(f"- resolution candidate: {str(result['resolutionCandidate']).lower()}")
        print(f"- output: {output}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
