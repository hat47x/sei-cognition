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
STRICT_ENTRYPOINT = INTEGRATION_DIR / "run_runtime_version_exchange_strict.py"
EVIDENCE_VERIFIER = INTEGRATION_DIR / "verify_runtime_version_exchange_evidence.py"


def _reject_forwarded_options(arguments: list[str]) -> None:
    forbidden = {
        "--kj-atlas-dir",
        "--kj-atlas-backend-bundle",
        "--model-dir",
        "--evidence-dir",
    }
    for argument in arguments:
        if argument in forbidden or any(argument.startswith(name + "=") for name in forbidden):
            raise ValueError(
                "strict identity / Evidence optionはこのentrypoint側で確定します。"
                f"下位entrypointへ直接渡せません: {argument}"
            )


def _prepare_new_path(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve(strict=False)
    if resolved.exists():
        raise ValueError(f"{label} already exists: {resolved}")
    return resolved


def _default_verification_output(evidence_dir: Path) -> Path:
    return evidence_dir.parent / f"{evidence_dir.name}-verification.json"


def _build_command(
    *,
    kj_atlas_dir: Path | None,
    kj_atlas_backend_bundle: Path | None,
    model_dir: Path | None,
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

    if model_dir is not None:
        command.extend(["--model-dir", str(model_dir)])
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


def _preserve_runner_observation(
    evidence_dir: Path,
    *,
    log_path: Path,
    output_sha256: str,
    output_bytes: int,
    exit_code: int,
    source_preparation: str,
) -> None:
    if not evidence_dir.is_dir():
        return

    target_log = evidence_dir / "runtime-exchange-runner.log"
    target_observation = evidence_dir / "runtime-exchange-runner-observation.json"
    if target_log.exists() or target_observation.exists():
        raise ValueError("runner observation path already exists in Evidence directory")

    os.replace(log_path, target_log)
    observation = {
        "schema": "soza.runtime-version-exchange-runner-observation/v1",
        "completed": exit_code == 0,
        "exitCode": exit_code,
        "sourcePreparation": source_preparation,
        "combinedOutputSha256": output_sha256,
        "combinedOutputBytes": output_bytes,
        "qualityJudgement": "not_evaluated",
    }
    target_observation.write_text(
        json.dumps(observation, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def run(
    *,
    kj_atlas_dir: Path | None,
    kj_atlas_backend_bundle: Path | None,
    model_dir: Path | None,
    evidence_dir: Path,
    verification_output: Path,
    forwarded: list[str],
) -> int:
    _reject_forwarded_options(forwarded)
    evidence_dir = _prepare_new_path(evidence_dir, "Evidence directory")
    verification_output = _prepare_new_path(verification_output, "verification output")
    if verification_output == evidence_dir or evidence_dir in verification_output.parents:
        raise ValueError(
            "verification outputはEvidence directoryの外へ保存してください: "
            f"{verification_output}"
        )

    command, source_preparation = _build_command(
        kj_atlas_dir=kj_atlas_dir,
        kj_atlas_backend_bundle=kj_atlas_backend_bundle,
        model_dir=model_dir,
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
            "ISSUE-000070のstrict runtime version exchangeを実行し、"
            "harness observationとEvidence検証結果を保存します。"
        ),
        allow_abbrev=False,
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--kj-atlas-dir", type=Path)
    source.add_argument("--kj-atlas-backend-bundle", type=Path)
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--evidence-dir", required=True, type=Path)
    parser.add_argument(
        "--verification-output",
        type=Path,
        help="Evidence検証結果を保存する新規JSON path。省略時はEvidence directoryの隣へ保存します。",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args, forwarded = parser.parse_known_args()
    if forwarded and forwarded[0] == "--":
        forwarded = forwarded[1:]

    evidence_dir = args.evidence_dir.expanduser().resolve(strict=False)
    verification_output = (
        args.verification_output.expanduser().resolve(strict=False)
        if args.verification_output is not None
        else _default_verification_output(evidence_dir)
    )
    try:
        return run(
            kj_atlas_dir=args.kj_atlas_dir,
            kj_atlas_backend_bundle=args.kj_atlas_backend_bundle,
            model_dir=args.model_dir,
            evidence_dir=evidence_dir,
            verification_output=verification_output,
            forwarded=forwarded,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"runtime version exchange verified runner failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
