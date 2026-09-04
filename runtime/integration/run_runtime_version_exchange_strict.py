#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

from export_kj_atlas_runtime_source import export_runtime_bundle
from prepare_runtime_version_exchange_archives import load_manifest as load_artifact_manifest
from prepare_runtime_version_exchange_archives import verify_archive
from prepare_runtime_version_exchange_model_store import prepare_model_store
from verify_kj_atlas_runtime_source import verify_runtime_bundle
from verify_runtime_version_exchange_model_store import verify_model_store


INTEGRATION_DIR = Path(__file__).resolve().parent
SOZA_ROOT = INTEGRATION_DIR.parents[1]
HARNESS = INTEGRATION_DIR / "run_runtime_version_exchange.sh"
RUNTIME_ARCHIVE_OPTIONS = ("--runtime-a-archive", "--runtime-b-archive")
RUNTIME_ARCHIVE_MANIFEST_LABELS = {
    "--runtime-a-archive": "a",
    "--runtime-b-archive": "b",
}
STRICT_CHILD_ENVIRONMENT_KEYS = (
    "SOZA_RUNTIME_EXCHANGE_KJ_ATLAS_BACKEND_BUNDLE",
    "SOZA_RUNTIME_EXCHANGE_WORK_DIR",
    "SOZA_RUNTIME_EXCHANGE_EVIDENCE_DIR",
    "SOZA_RUNTIME_EXCHANGE_PREPOSITIONED_ARCHIVE_A",
    "SOZA_RUNTIME_EXCHANGE_PREPOSITIONED_ARCHIVE_B",
    "SOZA_RUNTIME_EXCHANGE_MODEL_DIR",
)


def _reject_forwarded_identity_options(arguments: list[str]) -> None:
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
                "strict Evidenceのidentity / safety optionはこのentrypoint側で確定します。"
                f"harnessへ直接渡せません: {argument}"
            )


def _forwarded_runtime_archives(arguments: list[str]) -> dict[str, Path]:
    """low-level harnessへ渡す事前配置runtime archiveを曖昧さなく抽出する。"""

    selected: dict[str, Path] = {}
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        matched = False
        for option in RUNTIME_ARCHIVE_OPTIONS:
            value: str | None = None
            if argument == option:
                if index + 1 >= len(arguments):
                    raise ValueError(f"{option} requires PATH")
                value = arguments[index + 1]
                index += 2
                matched = True
            elif argument.startswith(option + "="):
                value = argument.split("=", 1)[1]
                index += 1
                matched = True

            if matched:
                if not value:
                    raise ValueError(f"{option} requires PATH")
                if option in selected:
                    raise ValueError(f"runtime archive optionを重複指定できません: {option}")
                selected[option] = Path(value)
                break

        if not matched:
            index += 1
    return selected


def _new_path(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve(strict=False)
    if resolved.exists():
        raise ValueError(f"{label}は新しいpathを指定してください: {resolved}")
    return resolved


def _is_within(candidate: Path, root: Path) -> bool:
    return candidate == root or root in candidate.parents


def _reject_overlap(candidate: Path, candidate_label: str, roots: tuple[tuple[str, Path], ...]) -> None:
    for root_label, root in roots:
        if _is_within(candidate, root):
            raise ValueError(
                f"{candidate_label}を{root_label}配下には置けません: "
                f"candidate={candidate} root={root}"
            )
        if _is_within(root, candidate):
            raise ValueError(
                f"{candidate_label}で{root_label}を包含できません: "
                f"candidate={candidate} root={root}"
            )


def _validate_runtime_archives(
    arguments: list[str],
    *,
    source_input: Path,
    source_label: str,
) -> dict[str, Path]:
    roots = (("SOZA repository", SOZA_ROOT), (source_label, source_input))
    validated: dict[str, Path] = {}
    for option, requested in _forwarded_runtime_archives(arguments).items():
        expanded = requested.expanduser()
        if expanded.is_symlink():
            raise ValueError(f"{option}にsymlinkは利用できません: {expanded}")
        try:
            resolved = expanded.resolve(strict=True)
        except FileNotFoundError as exc:
            raise ValueError(f"{option}のarchive fileが存在しません: {expanded}") from exc
        if not resolved.is_file():
            raise ValueError(f"{option}はregular fileを指定してください: {resolved}")
        _reject_overlap(resolved, f"{option} runtime archive", roots)
        if resolved in validated.values():
            raise ValueError(
                "runtime A / Bへ同じarchive pathを指定できません: "
                f"option={option} path={resolved}"
            )
        validated[option] = resolved
    return validated


def _verify_runtime_archive_identities(runtime_archives: dict[str, Path]) -> None:
    """事前配置archiveのactual bytesを固定manifestへ照合する。"""

    if not runtime_archives:
        return

    manifest = load_artifact_manifest()
    archives = manifest.get("runtimeArchives")
    if not isinstance(archives, dict):
        raise ValueError("runtime artifact manifestにruntimeArchivesがありません")

    for option, resolved in runtime_archives.items():
        label = RUNTIME_ARCHIVE_MANIFEST_LABELS[option]
        metadata = archives.get(label)
        if not isinstance(metadata, dict):
            raise ValueError(f"runtime artifact manifestにruntimeArchives.{label}がありません")
        expected_size = metadata.get("sizeBytes")
        expected_sha256 = metadata.get("sha256")
        if not isinstance(expected_size, int) or isinstance(expected_size, bool):
            raise ValueError(f"runtimeArchives.{label}.sizeBytesが不正です")
        if not isinstance(expected_sha256, str):
            raise ValueError(f"runtimeArchives.{label}.sha256が不正です")
        verify_archive(resolved, expected_size, expected_sha256)


def _strict_child_environment() -> dict[str, str]:
    """strict入口が確定するidentity / safety値を親環境から継承させない。"""

    environment = os.environ.copy()
    for key in STRICT_CHILD_ENVIRONMENT_KEYS:
        environment.pop(key, None)
    return environment


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def run_strict_probe(
    *,
    checkout_dir: Path | None,
    backend_bundle: Path | None,
    model_dir: Path | None,
    evidence_dir: Path,
    harness_arguments: list[str],
    work_dir: Path | None = None,
    prepare_model_dir: Path | None = None,
) -> int:
    _reject_forwarded_identity_options(harness_arguments)

    if (checkout_dir is None) == (backend_bundle is None):
        raise ValueError("--kj-atlas-dirまたは--kj-atlas-backend-bundleのどちらか一方を指定してください")
    if model_dir is not None and prepare_model_dir is not None:
        raise ValueError("--model-dirと--prepare-model-dirは同時に指定できません")

    if checkout_dir is not None:
        source_input = checkout_dir.expanduser().resolve(strict=True)
        source_label = "KJ Atlas checkout"
    else:
        assert backend_bundle is not None
        source_input = backend_bundle.expanduser().resolve(strict=True)
        source_label = "KJ Atlas verified runtime bundle"

    _reject_overlap(
        source_input,
        source_label,
        (("SOZA repository", SOZA_ROOT),),
    )
    strict_input_roots = (
        ("SOZA repository", SOZA_ROOT),
        (source_label, source_input),
    )

    # 事前配置runtime archiveは、source/model準備やharness起動より前にpath境界を固定する。
    runtime_archives = _validate_runtime_archives(
        harness_arguments,
        source_input=source_input,
        source_label=source_label,
    )

    resolved_model_dir: Path | None = None
    model_will_be_prepared = prepare_model_dir is not None
    if model_dir is not None:
        resolved_model_dir = model_dir.expanduser().resolve(strict=True)
    elif prepare_model_dir is not None:
        resolved_model_dir = _new_path(prepare_model_dir, "Prepared model directory")
    if resolved_model_dir is not None:
        _reject_overlap(resolved_model_dir, "model directory", strict_input_roots)
        for option, archive in runtime_archives.items():
            _reject_overlap(
                archive,
                f"{option} runtime archive",
                (("model directory", resolved_model_dir),),
            )

    evidence_dir = _new_path(evidence_dir, "Evidence directory")
    evidence_roots: list[tuple[str, Path]] = list(strict_input_roots)
    if resolved_model_dir is not None:
        evidence_roots.append(("model directory", resolved_model_dir))
    _reject_overlap(evidence_dir, "Evidence directory", tuple(evidence_roots))

    resolved_work_dir: Path | None = None
    if work_dir is not None:
        resolved_work_dir = _new_path(work_dir, "Work directory")
        work_roots = list(evidence_roots)
        work_roots.append(("Evidence directory", evidence_dir))
        _reject_overlap(resolved_work_dir, "Work directory", tuple(work_roots))

    # 明白なpath blockerをすべて除いた後、重いsource exportやmodel準備より前にactual archive bytesを固定する。
    _verify_runtime_archive_identities(runtime_archives)

    model_verification: dict[str, object] | None = None
    model_preparation: dict[str, object] | None = None
    if resolved_model_dir is not None and not model_will_be_prepared:
        model_verification = verify_model_store(resolved_model_dir)

    temporary: tempfile.TemporaryDirectory[str] | None = None
    source_export: dict[str, object] | None = None
    completed: subprocess.CompletedProcess[bytes] | subprocess.CompletedProcess[str] | None = None
    try:
        if checkout_dir is not None:
            temporary = tempfile.TemporaryDirectory(prefix="soza-runtime-exchange-strict-source-")
            verified_bundle = Path(temporary.name) / "backend"
            source_export = export_runtime_bundle(source_input, verified_bundle)
        else:
            verified_bundle = source_input
            verify_runtime_bundle(verified_bundle)

        if resolved_model_dir is not None and model_will_be_prepared:
            model_preparation = prepare_model_store(resolved_model_dir)
            model_verification = verify_model_store(resolved_model_dir)

        command = [
            "bash",
            str(HARNESS),
            "--kj-atlas-backend-bundle",
            str(verified_bundle),
            "--evidence-dir",
            str(evidence_dir),
        ]
        if resolved_model_dir is not None:
            command.extend(["--model-dir", str(resolved_model_dir)])
        if resolved_work_dir is not None:
            command.extend(["--work-dir", str(resolved_work_dir)])
        command.extend(harness_arguments)

        completed = subprocess.run(
            command,
            check=False,
            env=_strict_child_environment(),
        )
    finally:
        if evidence_dir.is_dir():
            if model_preparation is not None:
                _write_json(
                    evidence_dir / "runtime-exchange-model-store-preparation.json",
                    model_preparation,
                )
            if model_verification is not None:
                _write_json(
                    evidence_dir / "runtime-exchange-model-store-static-verification.json",
                    model_verification,
                )
            if source_export is not None:
                _write_json(
                    evidence_dir / "runtime-exchange-source-export.json",
                    source_export,
                )
        if temporary is not None:
            temporary.cleanup()

    if completed is None:
        raise RuntimeError("runtime exchange harnessが開始されませんでした")
    return completed.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000070のstrict runtime交換を開始します。KJ Atlas sourceをverified runtime "
            "bundleへ固定し、事前配置runtime archiveはharness起動前に固定size / SHA-256を再検証し、"
            "事前配置model storeはOllama起動前にmanifest / blob bytesを静的検証します。"
            "--prepare-model-dirを指定した場合は固定model storeをregistryから新規に準備し、"
            "再検証してからrepository-local harnessへ委譲します。"
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
    return parser


def main() -> int:
    parser = build_parser()
    args, harness_arguments = parser.parse_known_args()
    if harness_arguments and harness_arguments[0] == "--":
        harness_arguments = harness_arguments[1:]

    try:
        return run_strict_probe(
            checkout_dir=args.kj_atlas_dir,
            backend_bundle=args.kj_atlas_backend_bundle,
            model_dir=args.model_dir,
            evidence_dir=args.evidence_dir,
            harness_arguments=harness_arguments,
            work_dir=args.work_dir,
            prepare_model_dir=args.prepare_model_dir,
        )
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"strict runtime version exchange entrypoint failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
