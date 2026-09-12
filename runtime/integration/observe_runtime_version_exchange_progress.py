#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

import verify_runtime_version_exchange_evidence as core

SCHEMA = "sei.runtime-version-exchange-progress/v1"
RUNNER_SCHEMA = "sei.runtime-version-exchange-runner-observation/v1"
PREFLIGHT_SCHEMA = "sei.runtime-version-exchange-preflight/v1"
PREFLIGHT_OBSERVATION_SCHEMA = "sei.runtime-version-exchange-preflight-observation/v1"
IDENTITY_SCHEMA = "sei.runtime-version-exchange-evidence-identity/v1"
SOURCE_IDENTITY_SCHEMA = "sei.kj-atlas-runtime-source-identity/v1"
MODEL_STORE_VERIFICATION_SCHEMA = "sei.runtime-version-exchange-model-store-verification/v1"
STOP_LINE = (
    "observed Evidence milestone boundary != exact failing command or internal root cause "
    "!= canonical Evidence + Provenance verification PASS "
    "!= runtime compatibility judgement != outcome quality judgement != ISSUE-000070 Resolved"
)


@dataclass(frozen=True)
class Milestone:
    id: str
    observed: bool
    detail: str


def _read_json(path: Path) -> dict[str, Any] | None:
    if path.is_symlink() or not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _read_text(path: Path) -> str | None:
    if path.is_symlink() or not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _sha_file_matches(path: Path, expected_sha: str) -> bool:
    text = _read_text(path)
    if text is None:
        return False
    fields = text.strip().split()
    return bool(fields) and fields[0] == expected_sha


def _version_matches(path: Path, expected_version: str) -> bool:
    text = _read_text(path)
    return text is not None and core._exact_version_token(text, expected_version)


def _tags_match(path: Path, model_name: str, model_sha: str) -> bool:
    payload = _read_json(path)
    return payload is not None and core._model_digest_from_tags(payload, model_name) == model_sha


def _request_matches(payload: dict[str, Any] | None) -> bool:
    if payload is None:
        return False
    verification = core.Verification()
    core._verify_request(payload, verification)
    return verification.ready


def _inference_matches(
    evidence_path: Path,
    result_path: Path,
    *,
    label: str,
    model_name: str,
) -> tuple[bool, str | None]:
    evidence = _read_json(evidence_path)
    result = _read_json(result_path)
    if evidence is None or result is None:
        return False, None
    verification = core.Verification()
    prompt_sha = core._verify_model_evidence(label, evidence, model_name, verification)
    core._verify_result(label, result, verification)
    return verification.ready, prompt_sha if verification.ready else None


def _source_identity_matches(payload: dict[str, Any] | None) -> bool:
    if payload is None:
        return False
    return (
        payload.get("schema") == SOURCE_IDENTITY_SCHEMA
        and payload.get("verified") is True
        and payload.get("sourceMode") == core.EXPECTED_SOURCE_MODE
        and payload.get("repository") == "hat47x/kj-atlas"
        and payload.get("sourceCommit") == core.EXPECTED_SOURCE_COMMIT
        and payload.get("pinnedBackendTree") == core.EXPECTED_PARENT_BACKEND_TREE
        and payload.get("runtimeSurfaceTree") == core.EXPECTED_RUNTIME_SURFACE_TREE
        and payload.get("verificationBasis") == core.EXPECTED_SOURCE_VERIFICATION_BASIS
    )


def _model_store_verification_matches(
    payload: dict[str, Any] | None,
    model: dict[str, Any],
) -> bool:
    if payload is None:
        return False
    return (
        payload.get("schema") == MODEL_STORE_VERIFICATION_SCHEMA
        and payload.get("verified") is True
        and payload.get("model") == model["name"]
        and payload.get("manifestSha256") == model["sha256"]
        and payload.get("digestBasis") == model["digestBasis"]
        and payload.get("blobVerification") == "declared-size+actual-sha256"
    )


def _identity_matches(
    payload: dict[str, Any] | None,
    manifest: dict[str, Any],
    source_identity: dict[str, Any] | None,
) -> bool:
    if payload is None or payload.get("schema") != IDENTITY_SCHEMA:
        return False
    runtime_a = manifest["runtimeArchives"]["a"]
    runtime_b = manifest["runtimeArchives"]["b"]
    model = manifest["model"]
    actual_a = payload.get("runtimeA")
    actual_b = payload.get("runtimeB")
    actual_model = payload.get("model")
    acquisition_a = actual_a.get("archiveAcquisition") if isinstance(actual_a, dict) else None
    acquisition_b = actual_b.get("archiveAcquisition") if isinstance(actual_b, dict) else None
    storage_mode = actual_model.get("storageMode") if isinstance(actual_model, dict) else None
    return (
        _source_identity_matches(source_identity)
        and payload.get("methodSource") == source_identity
        and isinstance(actual_a, dict)
        and actual_a.get("name") == "ollama"
        and actual_a.get("version") == runtime_a["version"]
        and actual_a.get("archiveSha256") == runtime_a["sha256"]
        and acquisition_a in {"downloaded", "prepositioned"}
        and isinstance(actual_b, dict)
        and actual_b.get("name") == "ollama"
        and actual_b.get("version") == runtime_b["version"]
        and actual_b.get("archiveSha256") == runtime_b["sha256"]
        and acquisition_b in {"downloaded", "prepositioned"}
        and isinstance(actual_model, dict)
        and actual_model.get("name") == model["name"]
        and actual_model.get("expectedDigest") == model["sha256"]
        and storage_mode in {"work-local", "prepositioned"}
        and payload.get("qualityJudgement") == "not_evaluated"
    )


def _runner_observation_matches(
    root: Path,
    runner: dict[str, Any] | None,
) -> bool:
    if runner is None:
        return False
    completed = runner.get("completed")
    exit_code = runner.get("exitCode")
    output_sha = runner.get("combinedOutputSha256")
    output_bytes = runner.get("combinedOutputBytes")
    if not (
        runner.get("schema") == RUNNER_SCHEMA
        and runner.get("qualityJudgement") == "not_evaluated"
        and isinstance(completed, bool)
        and isinstance(exit_code, int)
        and not isinstance(exit_code, bool)
        and isinstance(output_sha, str)
        and re.fullmatch(r"[0-9a-f]{64}", output_sha) is not None
        and isinstance(output_bytes, int)
        and not isinstance(output_bytes, bool)
        and output_bytes >= 0
    ):
        return False

    log_path = root / "runtime-exchange-runner.log"
    if log_path.is_symlink() or not log_path.is_file():
        return False
    try:
        payload = log_path.read_bytes()
    except OSError:
        return False
    if hashlib.sha256(payload).hexdigest() != output_sha or len(payload) != output_bytes:
        return False
    if completed is True and exit_code == 0 and core.EXPECTED_COMPLETION_MARKER not in payload:
        return False
    return True


def _milestone(
    milestone_id: str,
    predicate: Callable[[], bool],
    observed_detail: str,
    missing_detail: str,
) -> Milestone:
    try:
        observed = bool(predicate())
    except (OSError, ValueError, KeyError, TypeError):
        observed = False
    return Milestone(
        id=milestone_id,
        observed=observed,
        detail=observed_detail if observed else missing_detail,
    )


def observe_progress(
    evidence_dir: Path,
    *,
    manifest_path: Path = core.ARTIFACT_MANIFEST,
) -> dict[str, Any]:
    root = evidence_dir.expanduser()
    if root.is_symlink():
        raise ValueError(f"Evidence directoryはsymlinkを許可しません: {root}")
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"Evidence directoryではありません: {root}")

    manifest = core._load_manifest(manifest_path)
    runtime_a = manifest["runtimeArchives"]["a"]
    runtime_b = manifest["runtimeArchives"]["b"]
    model = manifest["model"]
    model_name = model["name"]
    model_sha = model["sha256"]

    preflight = _read_json(root / "runtime-exchange-preflight.json")
    preflight_observation = _read_json(
        root / "runtime-exchange-preflight-observation.json"
    )
    runner = _read_json(root / "runtime-exchange-runner-observation.json")
    source_identity = _read_json(root / "kj-atlas-source-identity.json")
    model_store_verification = _read_json(
        root / "runtime-exchange-model-store-static-verification.json"
    )
    identity = _read_json(root / "runtime-exchange-identity.json")
    request = _read_json(root / "kj-atlas-runtime-exchange-request.json")

    preflight_blocked = (
        preflight is not None
        and preflight.get("schema") == PREFLIGHT_SCHEMA
        and preflight.get("result") == "blocked"
        and preflight_observation is not None
        and preflight_observation.get("schema") == PREFLIGHT_OBSERVATION_SCHEMA
        and preflight_observation.get("strictStarted") is False
    )
    preflight_ready = (
        preflight is not None
        and preflight.get("schema") == PREFLIGHT_SCHEMA
        and preflight.get("result") == "ready"
        and preflight.get("blockers") == []
    )

    inference_a, prompt_a = _inference_matches(
        root / "runtime-exchange-a-evidence.json",
        root / "runtime-exchange-a-result.json",
        label="a",
        model_name=model_name,
    )
    inference_b, prompt_b = _inference_matches(
        root / "runtime-exchange-b-evidence.json",
        root / "runtime-exchange-b-result.json",
        label="b",
        model_name=model_name,
    )

    milestones = [
        Milestone(
            "preflight_ready",
            preflight_ready,
            "保存済みpreflightがready / blockers=[]です",
            "readyな保存済みpreflightを確認できません",
        ),
        _milestone(
            "model_store_static_identity_verified",
            lambda: _model_store_verification_matches(model_store_verification, model),
            "固定model storeのmanifest / blob静的identityをEvidenceから確認できます",
            "固定model storeの静的identity Evidenceを確認できません",
        ),
        _milestone(
            "kj_atlas_source_identity_verified",
            lambda: _source_identity_matches(source_identity),
            "verified KJ Atlas runtime source identityをEvidenceから確認できます",
            "verified KJ Atlas runtime source identityを確認できません",
        ),
        _milestone(
            "fixed_identity_recorded",
            lambda: _identity_matches(identity, manifest, source_identity),
            "source・runtime A/B・modelの固定identityがEvidenceへ記録されています",
            "固定identity Evidenceを確認できません",
        ),
        _milestone(
            "runtime_a_archive_digest_observed",
            lambda: _sha_file_matches(
                root / "runtime-exchange-a-archive-sha256.txt",
                runtime_a["sha256"],
            ),
            "runtime A actual archive SHA-256の一致を確認できます",
            "runtime A actual archive SHA-256一致を確認できません",
        ),
        _milestone(
            "runtime_b_archive_digest_observed",
            lambda: _sha_file_matches(
                root / "runtime-exchange-b-archive-sha256.txt",
                runtime_b["sha256"],
            ),
            "runtime B actual archive SHA-256の一致を確認できます",
            "runtime B actual archive SHA-256一致を確認できません",
        ),
        _milestone(
            "fixed_method_input_recorded",
            lambda: _request_matches(request),
            "固定3-card Method inputとheld card条件をEvidenceから確認できます",
            "固定Method input Evidenceを確認できません",
        ),
        _milestone(
            "runtime_a_version_observed",
            lambda: _version_matches(
                root / "runtime-exchange-a-version.txt", runtime_a["version"]
            ),
            f"runtime A version {runtime_a['version']} をactual logから確認できます",
            "runtime A versionの一致を確認できません",
        ),
        _milestone(
            "runtime_a_model_identity_observed",
            lambda: _tags_match(
                root / "runtime-exchange-a-tags.json", model_name, model_sha
            ),
            "runtime A /api/tagsで固定model digestを確認できます",
            "runtime Aの固定model digestを確認できません",
        ),
        Milestone(
            "runtime_a_inference_observed",
            inference_a,
            "runtime Aのactual model EvidenceとKJ Atlas resultが成立しています"
            if inference_a
            else "runtime Aのactual inference成立を確認できません",
        ),
        _milestone(
            "runtime_b_version_observed",
            lambda: _version_matches(
                root / "runtime-exchange-b-version.txt", runtime_b["version"]
            ),
            f"runtime B version {runtime_b['version']} をactual logから確認できます",
            "runtime B versionの一致を確認できません",
        ),
        _milestone(
            "runtime_b_model_identity_observed",
            lambda: _tags_match(
                root / "runtime-exchange-b-tags.json", model_name, model_sha
            ),
            "runtime B /api/tagsで固定model digestを確認できます",
            "runtime Bの固定model digestを確認できません",
        ),
        Milestone(
            "runtime_b_inference_observed",
            inference_b,
            "runtime Bのactual model EvidenceとKJ Atlas resultが成立しています"
            if inference_b
            else "runtime Bのactual inference成立を確認できません",
        ),
        Milestone(
            "cross_runtime_prompt_identity_observed",
            bool(inference_a and inference_b and prompt_a and prompt_a == prompt_b),
            "A/B actual inferenceのprompt SHA-256一致を確認できます"
            if inference_a and inference_b and prompt_a and prompt_a == prompt_b
            else "A/B prompt identity一致を確認できません",
        ),
    ]

    first_missing_index = next(
        (index for index, item in enumerate(milestones) if not item.observed),
        len(milestones),
    )
    later_observed = [
        item.id for item in milestones[first_missing_index + 1 :] if item.observed
    ]
    monotonic = not later_observed

    observed_prefix = milestones[:first_missing_index]
    last_observed = observed_prefix[-1].id if observed_prefix else None
    next_unobserved = (
        milestones[first_missing_index].id
        if first_missing_index < len(milestones)
        else None
    )

    runner_present = runner is not None
    runner_recognized = _runner_observation_matches(root, runner)
    runner_completed = (
        runner_recognized
        and runner is not None
        and runner.get("completed") is True
        and runner.get("exitCode") == 0
    )
    runner_failed = (
        runner_recognized
        and runner is not None
        and runner.get("completed") is False
        and runner.get("exitCode") != 0
    )

    if not monotonic:
        state = "inconsistent_evidence_order"
        boundary = (
            "前段milestoneが未観測なのに後段milestoneが観測されています: "
            + ", ".join(later_observed)
        )
    elif preflight_blocked:
        state = "preflight_blocked"
        boundary = "strict entrypointは開始されていません"
    elif next_unobserved is None and runner_completed:
        state = "all_observed_milestones_completed"
        boundary = (
            "定義したA/B actual milestoneとrunner log identityをすべて観測しました。"
            "canonical Evidence + Provenance verifierは別途必要です"
        )
    elif runner_failed:
        state = "partial_after_strict_failure"
        boundary = (
            f"last observed={last_observed!r}; next unobserved={next_unobserved!r}. "
            "この区間より細かいfailure原因は、このprogress観測だけから特定しません"
        )
    elif not runner_recognized:
        state = "partial_without_valid_runner_observation"
        boundary = (
            f"last observed={last_observed!r}; next unobserved={next_unobserved!r}. "
            "runner observationとrunner logの整合を確認できません"
        )
    else:
        state = "partial_or_unverified"
        boundary = (
            f"last observed={last_observed!r}; next unobserved={next_unobserved!r}"
        )

    return {
        "schema": SCHEMA,
        "evidenceDirectory": str(root),
        "state": state,
        "preflightBlocked": preflight_blocked,
        "runner": {
            "present": runner_present,
            "recognized": runner_recognized,
            "completed": runner.get("completed") if runner is not None else None,
            "exitCode": runner.get("exitCode") if runner is not None else None,
        },
        "milestones": [asdict(item) for item in milestones],
        "lastObservedMilestone": last_observed,
        "nextUnobservedMilestone": next_unobserved,
        "monotonicEvidenceOrder": monotonic,
        "unexpectedLaterObservedMilestones": later_observed,
        "canonicalEvidenceVerification": "required_separately",
        "boundary": boundary,
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000070の保存済みEvidenceから、stderrを解析せず、"
            "固定artifactの存在と内容identityだけでA/B runtime交換の観測済みmilestoneを整理します。"
        )
    )
    parser.add_argument("--evidence-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        output = (
            core._prepare_output_path(args.output, args.evidence_dir)
            if args.output is not None
            else None
        )
        report = observe_progress(args.evidence_dir)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(2, f"runtime version exchange progress observation failed: {exc}\n")

    rendered = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    if args.json or output is None:
        print(rendered, end="")
    else:
        print(f"Runtime version exchange progress: {report['state']}")
        print(f"- last observed: {report['lastObservedMilestone']}")
        print(f"- next unobserved: {report['nextUnobservedMilestone']}")
        print(report["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
