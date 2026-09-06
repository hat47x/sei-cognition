#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

INTEGRATION_DIR = Path(__file__).resolve().parent
SOZA_ROOT = INTEGRATION_DIR.parents[1]
PREFLIGHT = INTEGRATION_DIR / "check_runtime_version_exchange_preflight.py"
STRICT_ENTRYPOINT = INTEGRATION_DIR / "run_runtime_version_exchange_strict.py"
EVIDENCE_VERIFIER = INTEGRATION_DIR / "verify_runtime_version_exchange_provenance.py"
RUNTIME_ARCHIVE_OPTIONS = ("--runtime-a-archive", "--runtime-b-archive")
VERIFIED_CHILD_PYTHON_ENVIRONMENT_KEYS = (
    "PYTHONPATH",
    "PYTHONHOME",
    "PYTHONSTARTUP",
    "PYTHONUSERBASE",
)
VERIFIED_CHILD_TEMP_ENVIRONMENT_KEYS = ("TMPDIR", "TMP", "TEMP")


class PreflightBlocked(ValueError):
    def __init__(self, report: dict[str, object], returncode: int) -> None:
        self.report = report
        self.returncode = returncode
        super().__init__(
            "runtime exchange preflight blocked: "
            f"blockers={report.get('blockers')!r}"
        )


def _verified_child_environment() -> dict[str, str]:
    """preflight / strict / verifier childを親shellのPython/Git/temp指定から分離する。"""

    environment = os.environ.copy()
    for key in tuple(environment):
        if key in VERIFIED_CHILD_PYTHON_ENVIRONMENT_KEYS:
            environment.pop(key, None)
        elif key in VERIFIED_CHILD_TEMP_ENVIRONMENT_KEYS:
            environment.pop(key, None)
        elif key.startswith("GIT_"):
            environment.pop(key, None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONNOUSERSITE"] = "1"
    return environment


def _reject_forwarded_options(arguments: list[str]) -> None:
    forbidden = {
        "--kj-atlas-dir",
        "--kj-atlas-backend-bundle",
        "--model-dir",
        "--prepare-model-dir",
        "--evidence-dir",
        "--work-dir",
        "--require-prepositioned-artifacts",
    }
    for argument in arguments:
        if argument in forbidden or any(argument.startswith(name + "=") for name in forbidden):
            raise ValueError(
                "strict identity / Evidence optionはこのentrypoint側で確定します。"
                f"下位entrypointへ直接渡せません: {argument}"
            )


def _canonical_path(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def _prepare_new_path(path: Path, label: str) -> Path:
    resolved = _canonical_path(path)
    if resolved.exists():
        raise ValueError(f"{label} already exists: {resolved}")
    return resolved


def _paths_overlap(left: Path, right: Path) -> bool:
    left = _canonical_path(left)
    right = _canonical_path(right)
    return left == right or left in right.parents or right in left.parents


def _protect_verification_output(
    output: Path,
    *,
    evidence_dir: Path,
    kj_atlas_dir: Path | None,
    kj_atlas_backend_bundle: Path | None,
    model_dir: Path | None,
    prepare_model_dir: Path | None,
    work_dir: Path | None,
) -> None:
    protected: list[tuple[str, Path]] = [
        ("SOZA repository", SOZA_ROOT),
        ("Evidence directory", evidence_dir),
    ]
    for label, path in (
        ("KJ Atlas checkout", kj_atlas_dir),
        ("KJ Atlas verified runtime bundle", kj_atlas_backend_bundle),
        ("model directory", model_dir),
        ("prepared model directory", prepare_model_dir),
        ("work directory", work_dir),
    ):
        if path is not None:
            protected.append((label, path))

    for label, path in protected:
        if _paths_overlap(output, path):
            raise ValueError(
                "verification outputは入力資産・作業領域・Evidenceから分離してください: "
                f"output={output} overlaps={label}:{_canonical_path(path)}"
            )


def _protect_runner_output_paths(
    *,
    evidence_dir: Path,
    work_dir: Path,
    verification_output: Path,
    kj_atlas_dir: Path | None,
    kj_atlas_backend_bundle: Path | None,
    model_dir: Path | None,
    prepare_model_dir: Path | None,
) -> None:
    """preflight失敗時も含め、runnerが入力資産をEvidence等で変更しないようにする。"""

    inputs: list[tuple[str, Path]] = [("SOZA repository", SOZA_ROOT)]
    for label, path in (
        ("KJ Atlas checkout", kj_atlas_dir),
        ("KJ Atlas verified runtime bundle", kj_atlas_backend_bundle),
        ("model directory", model_dir),
    ):
        if path is not None:
            inputs.append((label, _canonical_path(path)))

    outputs: list[tuple[str, Path]] = [
        ("Evidence directory", _canonical_path(evidence_dir)),
        ("work directory", _canonical_path(work_dir)),
        ("verification output", _canonical_path(verification_output)),
    ]
    if prepare_model_dir is not None:
        outputs.append(("prepared model directory", _canonical_path(prepare_model_dir)))

    for output_label, output_path in outputs:
        for input_label, input_path in inputs:
            if _paths_overlap(output_path, input_path):
                raise ValueError(
                    f"{output_label}を{input_label}と重ねられません: "
                    f"output={output_path} input={input_path}"
                )

    for index, (left_label, left_path) in enumerate(outputs):
        for right_label, right_path in outputs[index + 1 :]:
            if _paths_overlap(left_path, right_path):
                raise ValueError(
                    f"runner出力pathを相互に重ねられません: "
                    f"{left_label}={left_path} {right_label}={right_path}"
                )


def _default_verification_output(evidence_dir: Path) -> Path:
    return evidence_dir.parent / f"{evidence_dir.name}-verification.json"


def _effective_work_dir(evidence_dir: Path, requested_work_dir: Path | None) -> Path:
    """preflightとstrict entrypointが同じwork pathを診断・利用するよう一度だけ確定する。"""

    if requested_work_dir is not None:
        return _canonical_path(requested_work_dir)
    return evidence_dir.parent / f"{evidence_dir.name}-work"


def _runtime_archive_preflight_arguments(arguments: list[str]) -> list[str]:
    selected: list[str] = []
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        matched = False
        for option in RUNTIME_ARCHIVE_OPTIONS:
            if argument == option:
                if index + 1 >= len(arguments):
                    raise ValueError(f"{option} requires PATH")
                selected.extend([option, arguments[index + 1]])
                index += 2
                matched = True
                break
            if argument.startswith(option + "="):
                selected.append(argument)
                index += 1
                matched = True
                break
        if not matched:
            index += 1
    return selected


def _build_preflight_command(
    *,
    kj_atlas_dir: Path | None,
    kj_atlas_backend_bundle: Path | None,
    model_dir: Path | None,
    work_dir: Path | None,
    evidence_dir: Path,
    forwarded: list[str],
    require_prepositioned_artifacts: bool = False,
) -> list[str]:
    command = [sys.executable, str(PREFLIGHT)]
    if kj_atlas_dir is not None:
        command.extend(["--kj-atlas-dir", str(kj_atlas_dir)])
    elif kj_atlas_backend_bundle is not None:
        command.extend(["--kj-atlas-backend-bundle", str(kj_atlas_backend_bundle)])
    else:
        raise ValueError("KJ Atlas sourceを指定してください")
    if model_dir is not None:
        command.extend(["--model-dir", str(model_dir)])
    if work_dir is not None:
        command.extend(["--work-dir", str(work_dir)])
    command.extend(["--evidence-dir", str(evidence_dir)])
    command.extend(_runtime_archive_preflight_arguments(forwarded))
    if require_prepositioned_artifacts:
        command.append("--require-prepositioned-artifacts")
    command.append("--json")
    return command


def _run_preflight(command: list[str]) -> dict[str, object]:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=_verified_child_environment(),
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        detail = completed.stderr.strip() or completed.stdout.strip() or "no output"
        raise ValueError(f"runtime exchange preflightのJSONを読めません: {detail}") from exc
    if not isinstance(payload, dict):
        raise ValueError("runtime exchange preflightはJSON objectを返す必要があります")
    if completed.returncode != 0 or payload.get("result") != "ready":
        raise PreflightBlocked(payload, completed.returncode)
    return payload


def _build_command(
    *,
    kj_atlas_dir: Path | None,
    kj_atlas_backend_bundle: Path | None,
    model_dir: Path | None,
    prepare_model_dir: Path | None,
    work_dir: Path | None,
    evidence_dir: Path,
    forwarded: list[str],
) -> tuple[list[str], str]:
    command = [sys.executable, str(STRICT_ENTRYPOINT)]
    if kj_atlas_dir is not None:
        command.extend(["--kj-atlas-dir", str(kj_atlas_dir)])
        source_preparation = "checkout-to-verified-runtime-bundle"
    elif kj_atlas_backend_bundle is not None:
        command.extend(["--kj-atlas-backend-bundle", str(kj_atlas_backend_bundle)])
        source_preparation = "verified-runtime-bundle"
    else:
        raise ValueError("KJ Atlas sourceを指定してください")

    if model_dir is not None and prepare_model_dir is not None:
        raise ValueError("--model-dirと--prepare-model-dirは同時に指定できません")
    if model_dir is not None:
        command.extend(["--model-dir", str(model_dir)])
    elif prepare_model_dir is not None:
        command.extend(["--prepare-model-dir", str(prepare_model_dir)])
    if work_dir is not None:
        command.extend(["--work-dir", str(work_dir)])
    command.extend(["--evidence-dir", str(evidence_dir), "--", *forwarded])
    return command, source_preparation


def _run_and_capture(
    command: list[str],
    *,
    log_dir: Path,
) -> tuple[int, Path, str, int]:
    temporary = tempfile.NamedTemporaryFile(
        prefix="soza-runtime-exchange-runner-",
        suffix=".log",
        dir=log_dir,
        delete=False,
    )
    log_path = Path(temporary.name)
    digest = hashlib.sha256()
    total = 0
    try:
        with temporary:
            with subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=_verified_child_environment(),
            ) as process:
                assert process.stdout is not None
                for chunk in iter(lambda: process.stdout.read(64 * 1024), b""):
                    temporary.write(chunk)
                    temporary.flush()
                    digest.update(chunk)
                    total += len(chunk)
                    try:
                        sys.stdout.buffer.write(chunk)
                        sys.stdout.buffer.flush()
                    except BrokenPipeError:
                        pass
                returncode = process.wait()
        return returncode, log_path, digest.hexdigest(), total
    except Exception:
        log_path.unlink(missing_ok=True)
        raise


def _write_json_once(path: Path, payload: dict[str, object]) -> None:
    try:
        with path.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise ValueError(f"Evidence path already exists: {path}") from exc


def _prepare_evidence_directory_after_run(evidence_dir: Path, exit_code: int) -> str:
    """strict実行後のEvidence directoryを確定し、失敗観測を失わないようにする。"""

    if evidence_dir.is_symlink():
        raise ValueError(f"Evidence directoryはsymlinkを許可しません: {evidence_dir}")
    if evidence_dir.exists():
        if not evidence_dir.is_dir():
            raise ValueError(f"Evidence directoryではありません: {evidence_dir}")
        return "strict-entrypoint"
    if exit_code == 0:
        raise ValueError(
            "strict entrypointが成功終了しましたがEvidence directoryを作成しませんでした: "
            f"{evidence_dir}"
        )

    evidence_dir.mkdir(parents=True, exist_ok=False)
    return "verified-runner-after-failure"


def _run_verifier(evidence_dir: Path, verification_output: Path) -> int:
    completed = subprocess.run(
        [
            sys.executable,
            str(EVIDENCE_VERIFIER),
            "--evidence-dir",
            str(evidence_dir),
            "--output",
            str(verification_output),
        ],
        check=False,
        env=_verified_child_environment(),
    )
    return completed.returncode


def _preserve_blocked_preflight(
    evidence_dir: Path,
    *,
    verification_output: Path,
    blocked: PreflightBlocked,
) -> None:
    if evidence_dir.is_symlink() or evidence_dir.exists():
        raise ValueError(
            "blocked preflightのEvidence保存先は新しい通常directoryである必要があります: "
            f"{evidence_dir}"
        )
    evidence_dir.mkdir(parents=True, exist_ok=False)
    _write_json_once(
        evidence_dir / "runtime-exchange-preflight.json",
        blocked.report,
    )
    _write_json_once(
        evidence_dir / "runtime-exchange-preflight-observation.json",
        {
            "schema": "soza.runtime-version-exchange-preflight-observation/v1",
            "completed": True,
            "exitCode": blocked.returncode,
            "preflightResult": blocked.report.get("result"),
            "blockers": blocked.report.get("blockers"),
            "strictStarted": False,
            "qualityJudgement": "not_evaluated",
        },
    )
    _run_verifier(evidence_dir, verification_output)


def _preserve_runner_observation(
    evidence_dir: Path,
    *,
    log_path: Path,
    output_sha256: str,
    output_bytes: int,
    exit_code: int,
    source_preparation: str,
    preflight_report: dict[str, object],
    evidence_directory_created_by: str,
) -> None:
    if not evidence_dir.is_dir():
        raise ValueError(f"runner observationの保存先がEvidence directoryではありません: {evidence_dir}")

    target_log = evidence_dir / "runtime-exchange-runner.log"
    target_observation = evidence_dir / "runtime-exchange-runner-observation.json"
    target_preflight = evidence_dir / "runtime-exchange-preflight.json"
    if target_log.exists():
        raise ValueError("runner log path already exists in Evidence directory")

    os.replace(log_path, target_log)
    observation = {
        "schema": "soza.runtime-version-exchange-runner-observation/v1",
        "completed": exit_code == 0,
        "exitCode": exit_code,
        "sourcePreparation": source_preparation,
        "preflightResult": preflight_report.get("result"),
        "evidenceDirectoryCreatedBy": evidence_directory_created_by,
        "combinedOutputSha256": output_sha256,
        "combinedOutputBytes": output_bytes,
        "qualityJudgement": "not_evaluated",
    }
    _write_json_once(target_preflight, preflight_report)
    _write_json_once(target_observation, observation)


def run(
    *,
    kj_atlas_dir: Path | None,
    kj_atlas_backend_bundle: Path | None,
    model_dir: Path | None,
    prepare_model_dir: Path | None,
    work_dir: Path | None,
    evidence_dir: Path,
    verification_output: Path,
    forwarded: list[str],
    require_prepositioned_artifacts: bool = False,
) -> int:
    _reject_forwarded_options(forwarded)
    if require_prepositioned_artifacts and prepare_model_dir is not None:
        raise ValueError(
            "--require-prepositioned-artifactsでは--prepare-model-dirを使用できません。"
            "固定model storeを--model-dirで事前配置してください"
        )

    evidence_dir = _prepare_new_path(evidence_dir, "Evidence directory")
    effective_work_dir = _effective_work_dir(evidence_dir, work_dir)
    verification_output = _prepare_new_path(verification_output, "verification output")
    _protect_runner_output_paths(
        evidence_dir=evidence_dir,
        work_dir=effective_work_dir,
        verification_output=verification_output,
        kj_atlas_dir=kj_atlas_dir,
        kj_atlas_backend_bundle=kj_atlas_backend_bundle,
        model_dir=model_dir,
        prepare_model_dir=prepare_model_dir,
    )
    _protect_verification_output(
        verification_output,
        evidence_dir=evidence_dir,
        kj_atlas_dir=kj_atlas_dir,
        kj_atlas_backend_bundle=kj_atlas_backend_bundle,
        model_dir=model_dir,
        prepare_model_dir=prepare_model_dir,
        work_dir=effective_work_dir,
    )
    if not evidence_dir.parent.is_dir():
        raise ValueError(
            "Evidence directoryのparent directoryが存在しません: "
            f"{evidence_dir.parent}"
        )
    if not verification_output.parent.is_dir():
        raise ValueError(
            "verification outputのparent directoryが存在しません: "
            f"{verification_output.parent}"
        )

    preflight_command = _build_preflight_command(
        kj_atlas_dir=kj_atlas_dir,
        kj_atlas_backend_bundle=kj_atlas_backend_bundle,
        model_dir=model_dir,
        work_dir=effective_work_dir,
        evidence_dir=evidence_dir,
        forwarded=forwarded,
        require_prepositioned_artifacts=require_prepositioned_artifacts,
    )
    try:
        preflight_report = _run_preflight(preflight_command)
    except PreflightBlocked as blocked:
        _preserve_blocked_preflight(
            evidence_dir,
            verification_output=verification_output,
            blocked=blocked,
        )
        return 2

    command, source_preparation = _build_command(
        kj_atlas_dir=kj_atlas_dir,
        kj_atlas_backend_bundle=kj_atlas_backend_bundle,
        model_dir=model_dir,
        prepare_model_dir=prepare_model_dir,
        work_dir=effective_work_dir,
        evidence_dir=evidence_dir,
        forwarded=forwarded,
    )
    exit_code, log_path, output_sha256, output_bytes = _run_and_capture(
        command,
        log_dir=verification_output.parent,
    )
    try:
        evidence_directory_created_by = _prepare_evidence_directory_after_run(
            evidence_dir,
            exit_code,
        )
        _preserve_runner_observation(
            evidence_dir,
            log_path=log_path,
            output_sha256=output_sha256,
            output_bytes=output_bytes,
            exit_code=exit_code,
            source_preparation=source_preparation,
            preflight_report=preflight_report,
            evidence_directory_created_by=evidence_directory_created_by,
        )

        verifier_returncode = _run_verifier(evidence_dir, verification_output)
        if exit_code == 0:
            return verifier_returncode
        return exit_code
    finally:
        log_path.unlink(missing_ok=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000070のruntime version exchangeを副作用なしpreflightから開始し、"
            "strict実行、runner observation、Evidence再検証まで一続きに行います。"
        ),
        allow_abbrev=False,
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--kj-atlas-dir", type=Path)
    source.add_argument("--kj-atlas-backend-bundle", type=Path)
    model = parser.add_mutually_exclusive_group()
    model.add_argument("--model-dir", type=Path)
    model.add_argument("--prepare-model-dir", type=Path)
    parser.add_argument("--evidence-dir", required=True, type=Path)
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument(
        "--require-prepositioned-artifacts",
        action="store_true",
        help=(
            "network fallbackを許可せず、runtime A/B archiveと固定model storeが"
            "すべて事前配置済みであることをpreflightで要求します。"
        ),
    )
    parser.add_argument(
        "--verification-output",
        type=Path,
        help=(
            "Evidence検証結果を保存する新規JSON path。省略時はEvidence directoryの隣へ保存します。"
            "SOZA/KJ Atlas source、model、work、Evidenceとは重ならないpathが必要です。"
        ),
    )
    return parser


def main() -> int:
    parser = build_parser()
    args, forwarded = parser.parse_known_args()
    if forwarded and forwarded[0] == "--":
        forwarded = forwarded[1:]

    evidence_dir = _canonical_path(args.evidence_dir)
    verification_output = (
        _canonical_path(args.verification_output)
        if args.verification_output is not None
        else _default_verification_output(evidence_dir)
    )
    try:
        return run(
            kj_atlas_dir=args.kj_atlas_dir,
            kj_atlas_backend_bundle=args.kj_atlas_backend_bundle,
            model_dir=args.model_dir,
            prepare_model_dir=args.prepare_model_dir,
            work_dir=args.work_dir,
            evidence_dir=evidence_dir,
            verification_output=verification_output,
            forwarded=forwarded,
            require_prepositioned_artifacts=args.require_prepositioned_artifacts,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"runtime version exchange verified runner failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
