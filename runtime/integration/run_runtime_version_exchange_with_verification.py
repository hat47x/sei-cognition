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


def _reject_forwarded_options(arguments: list[str]) -> None:
    forbidden = {
        "--kj-atlas-dir",
        "--kj-atlas-backend-bundle",
        "--model-dir",
        "--prepare-model-dir",
        "--evidence-dir",
        "--work-dir",
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


def _default_verification_output(evidence_dir: Path) -> Path:
    return evidence_dir.parent / f"{evidence_dir.name}-verification.json"


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
    command.append("--json")
    return command


def _run_preflight(command: list[str]) -> dict[str, object]:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        detail = completed.stderr.strip() or completed.stdout.strip() or "no output"
        raise ValueError(f"runtime exchange preflightのJSONを読めません: {detail}") from exc
    if not isinstance(payload, dict):
        raise ValueError("runtime exchange preflightはJSON objectを返す必要があります")
    if completed.returncode != 0 or payload.get("result") != "ready":
        blockers = payload.get("blockers")
        raise ValueError(f"runtime exchange preflight blocked: blockers={blockers!r}")
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


def _run_and_capture(command: list[str]) -> tuple[int, Path, str, int]:
    temporary = tempfile.NamedTemporaryFile(
        prefix="soza-runtime-exchange-runner-",
        suffix=".log",
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
    if path.exists():
        raise ValueError(f"Evidence path already exists: {path}")
    path.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _preserve_runner_observation(
    evidence_dir: Path,
    *,
    log_path: Path,
    output_sha256: str,
    output_bytes: int,
    exit_code: int,
    source_preparation: str,
    preflight_report: dict[str, object],
) -> None:
    if not evidence_dir.is_dir():
        return

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
) -> int:
    _reject_forwarded_options(forwarded)
    evidence_dir = _prepare_new_path(evidence_dir, "Evidence directory")
    verification_output = _prepare_new_path(verification_output, "verification output")
    _protect_verification_output(
        verification_output,
        evidence_dir=evidence_dir,
        kj_atlas_dir=kj_atlas_dir,
        kj_atlas_backend_bundle=kj_atlas_backend_bundle,
        model_dir=model_dir,
        prepare_model_dir=prepare_model_dir,
        work_dir=work_dir,
    )

    preflight_command = _build_preflight_command(
        kj_atlas_dir=kj_atlas_dir,
        kj_atlas_backend_bundle=kj_atlas_backend_bundle,
        model_dir=model_dir,
        work_dir=work_dir,
        evidence_dir=evidence_dir,
        forwarded=forwarded,
    )
    preflight_report = _run_preflight(preflight_command)

    command, source_preparation = _build_command(
        kj_atlas_dir=kj_atlas_dir,
        kj_atlas_backend_bundle=kj_atlas_backend_bundle,
        model_dir=model_dir,
        prepare_model_dir=prepare_model_dir,
        work_dir=work_dir,
        evidence_dir=evidence_dir,
        forwarded=forwarded,
    )
    exit_code, log_path, output_sha256, output_bytes = _run_and_capture(command)
    try:
        _preserve_runner_observation(
            evidence_dir,
            log_path=log_path,
            output_sha256=output_sha256,
            output_bytes=output_bytes,
            exit_code=exit_code,
            source_preparation=source_preparation,
            preflight_report=preflight_report,
        )
        if log_path.exists():
            # strict entrypointがEvidence directory作成前に失敗した場合は、一時logを残さない。
            log_path.unlink()

        if evidence_dir.is_dir():
            verifier = subprocess.run(
                [
                    sys.executable,
                    str(EVIDENCE_VERIFIER),
                    "--evidence-dir",
                    str(evidence_dir),
                    "--output",
                    str(verification_output),
                ],
                check=False,
            )
            if exit_code == 0:
                return verifier.returncode
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
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"runtime version exchange verified runner failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
