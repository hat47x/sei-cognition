#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from prepare_runtime_version_exchange_inputs import RESULT_SCHEMA, prepare_prepositioned_inputs


INTEGRATION_DIR = Path(__file__).resolve().parent
VERIFIED_RUNNER = INTEGRATION_DIR / "run_runtime_version_exchange_with_verification.py"


def _prepared_artifact_path(value: object, *, name: str, root: Path) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"verifiedRunnerInputs.{name}のartifact pathが不正です")

    requested = Path(value).expanduser()
    if not requested.is_absolute():
        raise ValueError(f"verifiedRunnerInputs.{name}は絶対pathである必要があります")

    resolved = requested.resolve(strict=False)
    if root not in resolved.parents:
        raise ValueError(
            f"verifiedRunnerInputs.{name}がprepositioned input root配下ではありません: "
            f"path={resolved} root={root}"
        )
    return str(resolved)


def _validate_preparation_result(
    prepared: dict[str, object], artifact_root: Path
) -> tuple[str, str, str]:
    if prepared.get("schema") != RESULT_SCHEMA:
        raise ValueError(
            "prepositioned input preparation resultのschemaが未対応です: "
            f"{prepared.get('schema')!r}"
        )
    if prepared.get("result") != "ok":
        raise ValueError(
            "prepositioned input preparation resultがokではありません: "
            f"{prepared.get('result')!r}"
        )

    prepared_root = prepared.get("root")
    if not isinstance(prepared_root, str) or not prepared_root:
        raise ValueError("prepositioned input preparation resultにrootがありません")

    expected_root = artifact_root.expanduser().resolve(strict=False)
    observed_root = Path(prepared_root).expanduser().resolve(strict=False)
    if observed_root != expected_root:
        raise ValueError(
            "prepositioned input preparation resultのrootが要求したartifact rootと一致しません: "
            f"actual={observed_root} expected={expected_root}"
        )

    runner_inputs = prepared.get("verifiedRunnerInputs")
    if not isinstance(runner_inputs, dict):
        raise ValueError("prepositioned input preparation resultにverifiedRunnerInputsがありません")

    require_prepositioned = runner_inputs.get("requirePrepositionedArtifacts")
    if require_prepositioned is not True:
        raise ValueError("verifiedRunnerInputsはrequirePrepositionedArtifacts=trueである必要があります")

    model_dir = _prepared_artifact_path(
        runner_inputs.get("modelDir"), name="modelDir", root=observed_root
    )
    runtime_a = _prepared_artifact_path(
        runner_inputs.get("runtimeAArchive"), name="runtimeAArchive", root=observed_root
    )
    runtime_b = _prepared_artifact_path(
        runner_inputs.get("runtimeBArchive"), name="runtimeBArchive", root=observed_root
    )
    if runtime_a == runtime_b:
        raise ValueError("verifiedRunnerInputsのruntime A / B archive pathが同一です")

    return model_dir, runtime_a, runtime_b


def build_verified_runner_command(
    *,
    artifact_root: Path,
    kj_atlas_dir: Path | None,
    kj_atlas_backend_bundle: Path | None,
    evidence_dir: Path,
    verification_output: Path | None,
    work_dir: Path | None,
) -> tuple[list[str], dict[str, object]]:
    if (kj_atlas_dir is None) == (kj_atlas_backend_bundle is None):
        raise ValueError(
            "--kj-atlas-dirまたは--kj-atlas-backend-bundleのどちらか一方を指定してください"
        )

    prepared = prepare_prepositioned_inputs(artifact_root, verify_only=True)
    model_dir, runtime_a, runtime_b = _validate_preparation_result(prepared, artifact_root)

    command = [sys.executable, str(VERIFIED_RUNNER)]
    if kj_atlas_dir is not None:
        command.extend(["--kj-atlas-dir", str(kj_atlas_dir)])
    else:
        assert kj_atlas_backend_bundle is not None
        command.extend(["--kj-atlas-backend-bundle", str(kj_atlas_backend_bundle)])

    command.extend(
        [
            "--model-dir",
            model_dir,
            "--evidence-dir",
            str(evidence_dir),
            "--require-prepositioned-artifacts",
        ]
    )
    if verification_output is not None:
        command.extend(["--verification-output", str(verification_output)])
    if work_dir is not None:
        command.extend(["--work-dir", str(work_dir)])

    command.extend(
        [
            "--",
            "--runtime-a-archive",
            runtime_a,
            "--runtime-b-archive",
            runtime_b,
        ]
    )
    return command, prepared


def run(
    *,
    artifact_root: Path,
    kj_atlas_dir: Path | None,
    kj_atlas_backend_bundle: Path | None,
    evidence_dir: Path,
    verification_output: Path | None = None,
    work_dir: Path | None = None,
) -> int:
    command, prepared = build_verified_runner_command(
        artifact_root=artifact_root,
        kj_atlas_dir=kj_atlas_dir,
        kj_atlas_backend_bundle=kj_atlas_backend_bundle,
        evidence_dir=evidence_dir,
        verification_output=verification_output,
        work_dir=work_dir,
    )

    print(
        json.dumps(
            {
                "prepositionedInputs": prepared["verifiedRunnerInputs"],
                "next": "verified-runtime-exchange-runner",
                "qualityJudgement": "not_evaluated",
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
        flush=True,
    )
    completed = subprocess.run(command, check=False)
    return completed.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000070の事前配置済み固定artifact rootをnetworkなしで再検証し、"
            "A/B archiveとmodel storeのpathを手入力せず標準verified runnerへ接続します。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--artifact-root", required=True, type=Path)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--kj-atlas-dir", type=Path)
    source.add_argument("--kj-atlas-backend-bundle", type=Path)
    parser.add_argument("--evidence-dir", required=True, type=Path)
    parser.add_argument("--verification-output", type=Path)
    parser.add_argument("--work-dir", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run(
            artifact_root=args.artifact_root,
            kj_atlas_dir=args.kj_atlas_dir,
            kj_atlas_backend_bundle=args.kj_atlas_backend_bundle,
            evidence_dir=args.evidence_dir,
            verification_output=args.verification_output,
            work_dir=args.work_dir,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"prepositioned runtime exchange runner failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
